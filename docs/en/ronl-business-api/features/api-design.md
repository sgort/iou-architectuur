---
component: RONL Business API
---

# API Design

The HTTP surface is deliberately small and consistent: every route sits under a versioned prefix, almost every response follows the same envelope, and errors are reported the same way regardless of which endpoint produced them.

---

## Versioning

Every route is served under a `/v1/` prefix — the major version lives in the path, not in a header or a query parameter. Every response also carries an `API-Version` header reporting the deployed API's own version number, independent of the route version, so a caller can tell exactly which build answered a request.

---

## Naming

Resource paths use a singular noun for a resource type regardless of whether the request addresses the collection or a single member of it — `/v1/process`, `/v1/task`, `/v1/decision` — rather than pluralising collection endpoints. A resource's own identifier, not an internal Operaton identifier, is what appears in the path once a specific instance is addressed.

---

## The response envelope

Almost every response — across both the authenticated API and the public, unauthenticated endpoints — follows the same shape:

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

An error always carries a stable, machine-readable `code` alongside a human-readable `message`, so a caller can branch on the code without parsing the message text. Some endpoints add further fields alongside `data` — pagination details, or a generation timestamp — without changing the envelope's basic shape.

**Where the envelope deliberately does not apply**: the service's own root endpoint, which reports the API's name, version, and a map of its mounted routes as a plain object, is not wrapped in the envelope — it identifies the service itself rather than the result of an API call, and is meant to be readable by a human landing on the base URL directly rather than parsed as API output.

---

## Error handling

Every error response carries a `code` drawn from a small, consistent vocabulary — `UNAUTHORIZED` and `FORBIDDEN` for identity and authorization failures, `VALIDATION_ERROR` for a malformed request, resource-specific `*_NOT_FOUND` codes, and so on — alongside an HTTP status that matches the failure: `401` for a missing or invalid token, `403` for a role, tenant, or assurance-level check that failed, `404` for a resource that doesn't exist or isn't visible to the caller, `429` for a rate limit, `500` for anything unexpected. An unhandled error is caught centrally rather than crashing the request, and in production its message is replaced with a generic one so internal detail is not leaked to the caller.

---

## Public versus authenticated surface

Not every endpoint requires a token. A set of routes is deliberately public — reachable with no login — publishing read-only information for anyone to consult; see [Regelcatalogus](regelcatalogus.md) and [Procesbibliotheek](procesbibliotheek.md) for what that surface exposes. The public surface still follows the same response envelope and the same versioned prefix as the authenticated one, and the handful of public endpoints that accept a write are held to a stricter rate limit and a proof-of-work check rather than a login — see [Security & Compliance](security-compliance.md).

Every other endpoint requires a valid token, checked as described in [Authentication & IAM](authentication-iam.md), before any request data is processed.

---

## Related

- [Authentication & IAM](authentication-iam.md) — the validation every non-public request passes through
- [Security & Compliance](security-compliance.md) — rate limiting and the audit trail this surface produces
- [Tasks](tasks.md) and [Processes](processes.md) — the resources most of this surface addresses
