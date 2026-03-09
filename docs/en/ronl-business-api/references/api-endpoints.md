# API Endpoints

All current endpoints use the `/v1/` prefix. Legacy `/api/*` endpoints are deprecated and will be removed in v2.0.0. They return `Deprecation: true` and `Link: <successor>; rel="successor-version"` headers.

---

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

---

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

---

## Process management

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/v1/process/:key/start` | Bearer JWT | Start a BPMN process instance |
| `GET` | `/v1/process/:id/status` | Bearer JWT | Get process instance status |
| `GET` | `/v1/process/:id/variables` | Bearer JWT | Get process instance output variables |
| `DELETE` | `/v1/process/:id` | Bearer JWT | Cancel a process instance |
| `GET` | `/v1/process/history` | Bearer JWT | List completed and active process instances for the authenticated citizen (`?applicantId=`) |
| `GET` | `/v1/process/:key/start-form` | Bearer JWT | Fetch the deployed Camunda Form schema for a process start event. Returns 404 `FORM_NOT_FOUND` if no form is linked; 415 `UNSUPPORTED_FORM_TYPE` if an embedded HTML form is linked. |
| `GET` | `/v1/process/:id/historic-variables` | Bearer JWT | Fetch the final variable state of a completed process instance from Operaton history. Applies tenant isolation via the `municipality` variable. |
| `GET` | `/v1/process/:id/decision-document` | Bearer JWT | Fetch the `DocumentTemplate` bundled in the Operaton deployment for a completed process instance. Reads `ronl:documentRef` from the BPMN `UserTask` element and returns the named `.document` resource. Returns 404 `DOCUMENT_NOT_FOUND` when no `ronl:documentRef` is present or the resource is absent. Applies tenant isolation via the `municipality` variable. |

---

## Task management

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/v1/task` | Bearer JWT (caseworker) | List all open tasks for the caseworker's municipality |
| `GET` | `/v1/task/:id` | Bearer JWT (caseworker) | Get a single task by ID |
| `GET` | `/v1/task/:id/variables` | Bearer JWT (caseworker) | Get all process variables for a task |
| `POST` | `/v1/task/:id/claim` | Bearer JWT (caseworker) | Claim a task for the authenticated caseworker |
| `POST` | `/v1/task/:id/complete` | Bearer JWT (caseworker) | Complete a task with submitted variables |
| `GET` | `/v1/task/:id/form-schema` | Bearer JWT (caseworker) | Fetch the deployed Camunda Form schema for a task. Returns 404 `FORM_NOT_FOUND` if no `camunda:formRef` is set; treats Operaton 400 responses as 404. |

**`POST /v1/task/:id/complete` request body:**
```json
{
  "variables": {
    "reviewAction": "confirm",
    "notificationMethod": "email"
  }
}
```

Tasks are filtered to the caseworker's municipality via the `municipality` process variable. A caseworker from Utrecht cannot see Amsterdam's tasks.

---

## Process definition deployment

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/api/dmns/process/deploy` | Bearer JWT | Deploy a BPMN process bundle to Operaton in a single multipart request |

This endpoint accepts an `application/json` request body and deploys all provided resources as one named Operaton deployment. It is used by the LDE BPMN Modeler one-click deploy feature.

**Request body fields:**

| Field | Type | Required | Description |
|---|---|---|---|
| `bpmnXml` | `string` | Yes | The primary BPMN XML content |
| `deploymentName` | `string` | Yes | Name for the Operaton deployment (typically the BPMN process ID) |
| `forms` | `{ id: string, schema: object }[]` | No | Camunda Form schemas to include in the deployment. Defaults to `[]`. |
| `documents` | `{ id: string, template: object }[]` | No | Document template JSON files to include in the deployment. Each `template` is a `DocumentTemplate` object authored in the LDE Document Composer. Defaults to `[]`. |
| `subProcesses` | `{ filename: string, xml: string }[]` | No | Subprocess BPMN XML content. Defaults to `[]`. |
| `operatonUrl` | `string` | No | Override the default Operaton base URL |
| `operatonUsername` | `string` | No | Override Operaton basic-auth username |
| `operatonPassword` | `string` | No | Override Operaton basic-auth password |

See [Dynamic Forms — Deployment](../features/dynamic-forms.md#deployment) for the full deploy workflow.

---

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

---

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
| `TASK_NOT_FOUND` | 404 | Task ID does not exist |
| `TASK_CLAIM_FAILED` | 500 | Operaton rejected the claim request |
| `TASK_COMPLETE_FAILED` | 500 | Operaton rejected the complete request |
| `TASK_VARIABLES_FAILED` | 500 | Could not retrieve process variables for task |
