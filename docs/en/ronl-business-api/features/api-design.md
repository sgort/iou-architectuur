---
component: RONL Business API
---

# API Design

The HTTP surface sits under one versioned prefix, describes itself in a published OpenAPI document, and reports errors with a stable, machine-readable code. Its response shapes are not uniform: most operations share one envelope, and the exceptions are recorded below rather than smoothed over.

---

## Versioning

Every route is served under a `/v1/` prefix — the major version lives in the path, not in a header or a query parameter. Every response also carries an `API-Version` header with the release version — a calendar version such as `2026.09.12`, the same string `/v1/health` and the root banner report — so a caller can tell exactly which release answered a request.

---

## Naming

The execution core uses a singular noun for a resource type, whether the request addresses the collection or one member of it: `/v1/process`, `/v1/task`, `/v1/decision`. Other mounts name their collections in the plural — `/v1/edocs/documents`, `/v1/pa/dossiers`, `/v1/pa/searches`, `/v1/public/processen` — so naming is not uniform across the API. Process instances and tasks are addressed by their Operaton ids.

---

## Response shapes

Most responses — across both the authenticated API and the public, unauthenticated endpoints — follow one envelope:

**Success:**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "..."
  }
}
```

The public endpoints add a `meta` block beside `data` — `meta.generatedAt` is when the response was built, not when upstream data was fetched — and their lists put `items` and `pagination` inside `data`.

These operations answer differently, and the published description records each as it is:

| Where | Shape |
|---|---|
| `/v1/edocs`, `/v1/doccle` | `{ success, data, timestamp }`, with `timestamp` on success only |
| `GET /v1/process/{key}/variable-hints` | `{ success, variables }` |
| Several `/v1/pa` writes | a bare `{ success }` |
| `/v1/media-aggregator` | `{ articles }` and `{ ok, cached }` on success; a bare `{ error }` on failure |
| `GET /v1/pa/signals.rss` | an RSS document; its refusals are plain text |
| ValidSign ceremony routes | `text/html` |
| `POST /v1/mcp/chat` | a `text/event-stream` of `delta` and `done` events; its refusals are ordinary JSON sent before the stream opens |
| `GET /v1/openapi.json` | the OpenAPI document itself |

**The root endpoint** (`/`) is not wrapped either. It reports the service's name, version, status and environment, and an `endpoints` map built from the same route registry that mounts the routes — so it cannot advertise a path that is not served. The map includes a `documentation` key pointing at `/v1/openapi.json`.

---

## Error handling

Apart from the media aggregator's bare `{ error }`, every JSON error carries a stable `code` alongside a human-readable `message`, so a caller can branch on the code without parsing the message text. The HTTP status matches the failure:

| Status | Meaning | Codes include |
|---|---|---|
| `400` | A malformed request, or a task completion that sets a variable fixed at process start | `VALIDATION_ERROR`, `RESERVED_VARIABLE` |
| `401` | A missing or invalid token | `MISSING_TOKEN`, `INVALID_TOKEN`, `UNAUTHORIZED` |
| `403` | A role, tenant or assurance-level check that failed | `FORBIDDEN`, `TENANT_MISMATCH`, `MISSING_TENANT`, `INSUFFICIENT_ASSURANCE` |
| `404` | A resource that does not exist or is not visible to the caller | resource-specific `*_NOT_FOUND`, `NOT_FOUND` |
| `409` | A process start whose key several other organisations deploy | `AMBIGUOUS_DEPLOYMENT` |
| `429` | A rate limit | `RATE_LIMIT_EXCEEDED` |
| `500` | Anything unexpected | `INTERNAL_ERROR` and operation-specific `*_FAILED` codes |
| `502` | A fault in an upstream system, such as eDOCS or Doccle | `EDOCS_ERROR`, `DOCCLE_ERROR` |

The tenant codes are explained in [Authentication & IAM — Tenancy](authentication-iam.md#tenancy). An unhandled error is caught centrally rather than crashing the request, and in production its message is replaced with a generic one.

---

## Published description

The API describes itself at **`GET /v1/openapi.json`**, an OpenAPI 3.1 document served at the location the NL API Design Rules prescribe (`/core/publish-openapi`) and open to every origin, so a browser-based viewer can load it. Its `info.version` is set from the release at build time, so the document and the release cannot disagree. See the [API Specification](../reference/api-specification.md) for the reference built from it.

The document is linted with Spectral against a vendored copy of the NL API Design Rules 2.2.1 ruleset, in both backend workflows. Every rule gates except these recorded deviations:

- `nlgov:semver` is off, because releases are CalVer and a zero-padded month is not valid semver.
- The three problem-details rules (`nlgov:use-problem-schema`, `nlgov:problem-schema-members`, `nlgov:problem-invalid-input`) are off, because the API answers its own `{ success, error }` envelope rather than RFC 9457 `application/problem+json`. Every error response in the document refers to one shared component, so a later migration is one change.
- Two date-named properties that carry full timestamps are exempt from the date-instead-of-datetime rule.

A coverage test compares the document with the route registry: it fails when a served operation is neither documented nor listed as pending, when a documented operation is not served, or when the pending list grows. The machine-to-machine routes under `/v1/m2m` are the operations still pending.

---

## Public versus authenticated surface

Not every endpoint requires a token. A set of routes is deliberately public — reachable with no login — publishing read-only information for anyone to consult; see [Regelcatalogus](regelcatalogus.md) and [Procesbibliotheek](procesbibliotheek.md) for what that surface exposes. The `/v1/public` routes follow the same envelope and versioned prefix as the authenticated ones, and the handful of public endpoints that accept a write are held to a stricter rate limit, and most of them to a proof-of-work check, rather than a login — see [Security & Compliance](security-compliance.md).

Every other endpoint requires a valid token, checked as described in [Authentication & IAM](authentication-iam.md), before any request data is processed. Three exceptions authenticate differently: the ValidSign callback, which ValidSign calls without a token; `/v1/pa/signals.rss`, which takes a token in its query string because RSS readers cannot send headers; and `/v1/media-aggregator/search`, which requires a shared bearer key when one is configured and is open otherwise.

---

## Related

- [Authentication & IAM](authentication-iam.md) — the validation every non-public request passes through
- [Security & Compliance](security-compliance.md) — rate limiting and the audit trail this surface produces
- [API Specification](../reference/api-specification.md) — the published OpenAPI description
- [Tasks](tasks.md) and [Processes](processes.md) — the resources most of this surface addresses
