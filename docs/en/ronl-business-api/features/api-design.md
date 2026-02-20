# API Design

RONL Business API follows the **Dutch Government API Design Rules** (Nederlandse API Strategie). The API is versioned, uses standard HTTP semantics, and provides machine-readable metadata via response headers.

## Versioning

All current endpoints are served under the `/v1/` prefix (rule API-20: major version in the URI path). A response header `API-Version` is added to every response (rule API-57):

```http
HTTP/1.1 200 OK
API-Version: 1.0.0
Content-Type: application/json
```

Legacy endpoints under `/api/*` continue to work but are deprecated. They return additional headers (rule API-51):

```http
Deprecation: true
Link: </v1/health>; rel="successor-version"
```

Legacy support will be removed in v2.0.0.

## Naming conventions

| Rule | Applied as |
|---|---|
| API-05: use nouns | `process`, `decision`, `health` |
| API-54: plural/singular | Collections use plural (`/v1/process`), single resource uses singular with ID |
| API-48: no trailing slashes | Enforced in routing configuration |
| API-53: hide implementation | No Operaton-internal identifiers exposed in responses |
| API-04: language | Technical endpoints in English; business variable names follow Dutch source data |

## Request / response format

All endpoints use `application/json`. Request bodies are validated using `express-validator`. Responses follow a consistent envelope:

**Success:**
```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2026-02-20T10:00:00.000Z"
}
```

**Error:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "income must be a positive number"
  },
  "timestamp": "2026-02-20T10:00:00.000Z"
}
```

## Rate limiting headers

Rate limit state is communicated via standard headers (`RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`) when approaching the limit.

## OpenAPI documentation

An OpenAPI 3.0 specification is planned at `/v1/openapi.json` (rule API-16 / API-51). It is currently enabled only in non-production environments via `ENABLE_SWAGGER=true`.

## Route inventory

The full list of registered routes, including legacy `/api/*` equivalents, is documented in [API Endpoints](../references/api-endpoints.md).
