# API Endpoints

All current endpoints use the `/v1/` prefix. Legacy `/api/*` endpoints are deprecated and will be removed in v2.0.0. They return `Deprecation: true` and `Link: <successor>; rel="successor-version"` headers.

## Root & Health

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/` | None | API name, version, status, endpoint map |
| `GET` | `/v1/health` | None | Health check with service latencies |
| `GET` | `/api/health` | None | ⚠ Deprecated |

**`GET /v1/health` response:**

```json
{
  "name": "RONL Business API",
  "version": "1.0.0",
  "environment": "production",
  "status": "healthy",
  "uptime": 3600.0,
  "timestamp": "2026-02-20T10:00:00.000Z",
  "services": {
    "keycloak": { "status": "up", "latency": 45 },
    "operaton": { "status": "up", "latency": 112 }
  }
}
```

Health status values: `healthy` (HTTP 200), `degraded` (HTTP 503), `unhealthy` (HTTP 503).

## Decision evaluation

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/v1/decision/:key/evaluate` | Bearer JWT | Evaluate a DMN decision table by key |
| `GET` | `/api/decision` | Bearer JWT | ⚠ Deprecated |

**Request body:**
```json
{
  "variables": {
    "ingezeteneVanNederland": true,
    "inkomenEnVermogen": 24000
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "eligible": true,
    "amount": 1150
  },
  "timestamp": "2026-02-20T10:00:00.000Z"
}
```

## Process management

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/v1/process/:key/start` | Bearer JWT | Start a BPMN process instance |
| `GET` | `/v1/process/:id/status` | Bearer JWT | Get process instance status |
| `GET` | `/v1/process/:id/variables` | Bearer JWT | Get process instance output variables |
| `DELETE` | `/v1/process/:id` | Bearer JWT | Cancel a process instance |

## Response headers

All responses include:

```http
API-Version: 1.0.0
Content-Type: application/json
```

Deprecated endpoints additionally include:

```http
Deprecation: true
Link: </v1/health>; rel="successor-version"
```

## Error codes

| Code | HTTP status | Meaning |
|---|---|---|
| `UNAUTHORIZED` | 401 | Missing or invalid JWT |
| `FORBIDDEN` | 403 | Valid JWT but insufficient role or LoA |
| `LOA_INSUFFICIENT` | 403 | Required assurance level not met |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `VALIDATION_ERROR` | 400 | Request body failed validation |
| `PROCESS_NOT_FOUND` | 404 | Process key or instance ID not found |
| `OPERATON_ERROR` | 502 | Upstream Operaton call failed |
| `QUERY_ERROR` | 500 | Internal error |
