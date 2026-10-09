---
component: RONL Business API
---

# API Design

The HTTP surface sits under one versioned prefix, describes itself in a published OpenAPI document, and reports every error as RFC 9457 problem details with a stable, machine-readable code. Its success shapes are not uniform: most operations share one envelope, and the exceptions are recorded below rather than smoothed over.

---

## Versioning

Every route is served under a `/v1/` prefix — the major version lives in the path, not in a header or a query parameter. Every response also carries an `API-Version` header with the release version — a calendar version such as `2026.09.12`, the same string `/v1/health` and the root banner report — so a caller can tell exactly which release answered a request.

---

## Naming

The execution core uses a singular noun for a resource type, whether the request addresses the collection or one member of it: `/v1/process`, `/v1/task`, `/v1/decision`. Other mounts name their collections in the plural — `/v1/edocs/documents`, `/v1/pa/dossiers`, `/v1/pa/searches`, `/v1/public/processen` — so naming is not uniform across the API. Process instances and tasks are addressed by their Operaton ids.

---

## Response shapes

Most successful responses — across both the authenticated API and the public, unauthenticated endpoints — follow one envelope:

```json
{
  "success": true,
  "data": { ... }
}
```

Errors do not use it: every 4xx and 5xx is problem details, described under [Error handling](#error-handling).

The public endpoints add a `meta` block beside `data` — `meta.generatedAt` is when the response was built, not when upstream data was fetched — and their lists put `items` and `pagination` inside `data`.

These operations answer success differently, and the published description records each as it is:

| Where | Shape |
|---|---|
| `/v1/edocs`, `/v1/doccle` | `{ success, data, timestamp }` |
| `GET /v1/process/{key}/variable-hints` | `{ success, variables }` |
| Several `/v1/pa` writes | a bare `{ success }` |
| `/v1/media-aggregator` | `{ articles }` and `{ ok, cached }` |
| `GET /v1/pa/signals.rss` | an RSS document |
| ValidSign ceremony routes | `text/html`; a failed signing on the stub ceremony is an HTML page too, the one error that is not problem details |
| `POST /v1/mcp/chat` | a `text/event-stream` of `delta` and `done` events; its refusals are problem details sent before the stream opens |
| `GET /v1/openapi.json` | the OpenAPI document itself |

**The root endpoint** (`/`) is not wrapped either. It reports the service's name, version, status and environment, and an `endpoints` map built from the same route registry that mounts the routes — so it cannot advertise a path that is not served. The map includes a `documentation` key pointing at `/v1/openapi.json`.

---

## Error handling

Every error is [RFC 9457](https://www.rfc-editor.org/rfc/rfc9457) problem details, served as `application/problem+json`. The body carries the RFC's members — `type` (always `about:blank`, since the API has no page per problem kind), `status`, `title`, `detail` and `instance` (the request path, without its query string) — plus a `code` extension member:

```json
{
  "type": "about:blank",
  "status": 403,
  "title": "Tenant mismatch",
  "detail": "Access denied: organisation mismatch",
  "instance": "/v1/task/<task id>/complete",
  "code": "TENANT_MISMATCH"
}
```

`code` is the stable, machine-readable identifier a caller branches on, so it never has to parse `detail`. `title` is derived from it — `PROCESS_START_FAILED` reads "Process start failed" — so the same code always has the same title. Some operations add further extension members, and the published description documents each:

| Operation | Extension members |
|---|---|
| `POST /v1/process/{key}/start` failing with `PROCESS_START_FAILED` | `details` (the engine's own message) and `engine` (the Operaton base URL the start was sent to) |
| A task completion, or a machine-to-machine start, refused with `RESERVED_VARIABLE` | `reserved` (the variable names refused) |
| `GET /v1/health` and `GET /v1/health/ready` answering `503` | `data` (the full health or readiness report) |

Successful responses keep their own shapes, described under [Response shapes](#response-shapes). The HTTP status matches the failure:

| Status | Meaning | Codes include |
|---|---|---|
| `400` | A malformed request, a body that does not parse, or a task completion (or machine-to-machine start) that sets a variable fixed at process start | `VALIDATION_ERROR`, `MALFORMED_BODY`, `INVALID_BODY`, `RESERVED_VARIABLE` |
| `401` | A missing or invalid token, or a person whose eDOCS session can no longer be renewed and must sign in again | `MISSING_TOKEN`, `INVALID_TOKEN`, `UNAUTHORIZED`, `EDOCS_REAUTH_REQUIRED` |
| `403` | A role, tenant, assurance-level or machine-client check that failed, or eDOCS that cannot be reached as the person or refuses them | `FORBIDDEN`, `TENANT_MISMATCH`, `MISSING_TENANT`, `INSUFFICIENT_ASSURANCE`, `M2M_CLIENT_NOT_ALLOWED`, `EDOCS_CLIENT_NOT_ALLOWED`, `EDOCS_USER_TOKEN_UNAVAILABLE`, `EDOCS_ACCESS_DENIED` |
| `404` | A resource that does not exist or is not visible to the caller | resource-specific `*_NOT_FOUND`, `NOT_FOUND` |
| `409` | A process start whose key several other organisations deploy | `AMBIGUOUS_DEPLOYMENT` |
| `413` | A request body over the size limit | `PAYLOAD_TOO_LARGE` |
| `429` | A rate limit | `RATE_LIMIT_EXCEEDED` |
| `500` | Anything unexpected | `INTERNAL_ERROR` and operation-specific `*_FAILED` codes |
| `502` | A fault in an upstream system, such as eDOCS or Doccle | `EDOCS_ERROR`, `DOCCLE_ERROR` |
| `503` | A required dependency or optional subsystem that is unavailable | `SERVICE_DEGRADED`, `NOT_READY`, `MCP_DISABLED`, `SERVICES_UNAVAILABLE` |

The tenant codes are explained in [Authentication & IAM — Tenancy](authentication-iam.md#tenancy); the eDOCS codes in [eDOCS — Live Testing](../developer/testing/edocs-live-testing.md#people-and-the-service-account). A body the JSON parser refuses is a client error, answered before any route runs: `400 MALFORMED_BODY` for one that does not parse, `413 PAYLOAD_TOO_LARGE` for one over the limit. An unhandled error is caught centrally rather than crashing the request, and in production its `detail` is replaced with a generic one.

---

## Published description

The API describes itself at **`GET /v1/openapi.json`**, an OpenAPI 3.1 document served at the location the NL API Design Rules prescribe (`/core/publish-openapi`) and open to every origin, so a browser-based viewer can load it. Its `info.version` is set from the release at build time, so the document and the release cannot disagree. See the [API Specification](../reference/api-specification.md) for the reference built from it.

The document is linted with Spectral against a vendored copy of the NL API Design Rules 2.2.1 ruleset, in both backend workflows. Every rule gates except these recorded deviations:

- `nlgov:semver` is off, because releases are CalVer and a zero-padded month is not valid semver.
- `nlgov:use-problem-schema` is off for one response only: the stub ValidSign ceremony's failed signing, an HTML page shown to the person in the signing frame rather than an error for a client to parse. The three problem-details rules gate everywhere else.
- Two date-named properties that carry full timestamps are exempt from the date-instead-of-datetime rule.

Every served operation is described, the machine-to-machine routes under `/v1/m2m` included. A coverage test compares the document with the route registry and fails when a served operation is not documented or a documented operation is not served. A conformance check goes further: route tests compare real responses against the document's schemas, and `npm test` fails when any documented operation was never compared against a real response.

---

## Public versus authenticated surface

Not every endpoint requires a token. A set of routes is deliberately public — reachable with no login — publishing read-only information for anyone to consult; see [Regelcatalogus](regelcatalogus.md) and [Procesbibliotheek](procesbibliotheek.md) for what that surface exposes. The `/v1/public` routes follow the same envelope and versioned prefix as the authenticated ones, and the handful of public endpoints that accept a write are held to a stricter rate limit, and most of them to a proof-of-work check, rather than a login — see [Security & Compliance](security-compliance.md).

Every other endpoint requires a valid token, checked as described in [Authentication & IAM](authentication-iam.md), before any request data is processed. Four exceptions authenticate differently: the ValidSign callback, which ValidSign calls without a token; `/v1/pa/signals.rss`, which takes a token in its query string because RSS readers cannot send headers; `/v1/media-aggregator/search`, which requires a shared bearer key when one is configured and is open otherwise; and the machine-to-machine routes under `/v1/m2m`, which accept a token only when it was issued to a client on an allow-list — see [Authentication & IAM — Tenancy](authentication-iam.md#tenancy).

---

## Related

- [Authentication & IAM](authentication-iam.md) — the validation every non-public request passes through
- [Security & Compliance](security-compliance.md) — rate limiting and the audit trail this surface produces
- [API Specification](../reference/api-specification.md) — the published OpenAPI description
- [Tasks](tasks.md) and [Processes](processes.md) — the resources most of this surface addresses
