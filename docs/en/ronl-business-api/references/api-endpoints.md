# API Endpoints

All current endpoints use the `/v1/` prefix. Legacy `/api/*` endpoints are deprecated and will be removed in v2.0.0. They return `Deprecation: true` and `Link: <successor>; rel="successor-version"` headers.

---

## Root & Health

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/` | None | API name, version, status, endpoint map |
| `GET` | `/v1/health` | None | Health check with service latencies (Keycloak + Operaton) |
| `GET` | `/v1/health/live` | None | Liveness probe — returns `{ status: "alive" }` |
| `GET` | `/v1/health/ready` | None | Readiness probe — checks Operaton availability |
| `GET` | `/v1/health/external` | None | Reachability check for CPRMV API, TriplyDB, and LDE. Performs server-side HEAD requests (5-second timeout) to avoid CORS. Returns `{ status: "up"|"down", latency: number }` per service. |
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
| `GET` | `/v1/process/:key/variable-hints` | Bearer JWT | Fetch deduplicated variable names and their inferred types from the historic variable store for a given process definition key. Used by the caseworker dashboard to pre-populate form fields. |
---

## Public content
 
These endpoints require no authentication and are accessible before login. They are used by both the MijnOmgeving landing page and the caseworker dashboard Home tab.
 
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/v1/public/nieuws` | None | National news from the Government.nl RSS feed. Supports `?limit=` (max 20) and `?offset=`. Cached 10 minutes server-side; stale cache returned on feed unavailability. |
| `GET` | `/v1/public/berichten` | None | Returns announcements from the Provincie Flevoland news RSS feed. |
| `GET` | `/v1/public/berichten/:id` | None | Returns a single bericht by its RSS `<guid>`. Reads from the in-memory cache populated by the list endpoint; returns `404 BERICHT_NOT_FOUND` if the cache is empty or the id is not present. |
| `GET` | `/v1/public/producten-diensten` | None | Returns the Provincie Flevoland product and services catalogue. No authentication required. Currently only populated for the Flevoland tenant; other tenants receive an empty list. |
| `GET` | `/v1/public/regelcatalogus` | None | RONL knowledge graph data: services, organisations, NL-SBB concepts, and implementation rules. Five parallel SPARQL queries against TriplyDB. Each data slice cached 5 minutes in-memory; stale cache returned on TriplyDB failure. |
| `POST` | `/v1/public/use-case` | None | Submit a use-case scenario as a GitLab issue in the IOU Architecture project. Returns the created issue's `iid` and `web_url`. |
| `GET` | `/v1/public/use-cases` | None | List GitLab issues for the IOU Architecture project. Query: `?state=opened` (default) or `?state=closed`. Returns up to 100 items sorted by `created_at` descending. |
| `POST` | `/v1/public/feedback` | None | Submit feedback with optional screenshot attachments as a GitLab issue. Accepts `multipart/form-data`. Images are uploaded to the GitLab project uploads API and embedded as markdown references in the issue body. |
| `POST` | `/v1/public/upload-file` | None | Upload a single file of any type to the GitLab project and receive its markdown reference. Used by the use-case form to pre-upload attachments before JSON submission. Accepts `multipart/form-data` with a single file under the field name `file`. |
 
**`GET /v1/public/nieuws` response shape:**
 
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "guid-from-rss",
        "title": "Titel van het bericht",
        "summary": "Samenvatting...",
        "category": null,
        "publishedAt": "2026-03-12T08:00:00.000Z",
        "url": "https://www.government.nl/...",
        "source": { "id": "government", "name": "Government.nl" }
      }
    ],
    "pagination": { "limit": 10, "offset": 0, "total": 40, "hasMore": true }
  },
  "meta": { "generatedAt": "2026-03-12T12:00:00.000Z" }
}
```

**`GET /v1/public/berichten` response shape:**

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "https://flevoland.nl/actueel/nieuws/2026/...",
        "subject": "Titel van het bericht",
        "preview": "Korte beschrijving...",
        "content": "<p>Korte beschrijving...</p>",
        "type": "announcement",
        "status": "published",
        "audience": "all",
        "sender": { "id": "flevoland", "name": "Provincie Flevoland" },
        "publishedAt": "2026-03-12T08:00:00.000Z",
        "expiresAt": null,
        "priority": "normal",
        "isRead": false,
        "action": { "label": "Lees meer", "url": "https://flevoland.nl/actueel/nieuws/2026/..." }
      }
    ],
    "pagination": { "limit": 10, "offset": 0, "total": 25, "hasMore": true }
  },
  "meta": { "generatedAt": "2026-03-12T12:00:00.000Z" }
}
```

Returns announcements from the Provincie Flevoland news RSS feed. No authentication required.

**Query parameters:** `limit` (default 10, max 20), `offset` (default 0)

**Data source:** `https://flevoland.nl/Content/Pages/Loket?rss=news` — parsed server-side, cached 10 minutes. Stale cache is returned on feed unavailability.

**Response:** `application/json`

Each item contains: `id` (RSS `<guid>`), `subject`, `preview`, `content`, `type`, (`announcement`), `sender` (`{ id: "flevoland", name: "Provincie Flevoland" }`), `publishedAt`, `priority` (`normal`), `isRead` (`false`), `action` (`{ label: "Lees meer", url: "<link>" }` when the RSS item carries a `<link>` element, otherwise `null`).

**`GET /v1/public/berichten/:id`**

No authentication required.

**`GET /v1/public/producten-diensten` response shape**

```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": "12345",
        "title": "Kapvergunning aanvragen",
        "description": "Wilt u een boom kappen? Dan heeft u mogelijk een omgevingsvergunning nodig...",
        "url": "https://flevoland.nl/loket/producten/kapvergunning",
        "audience": ["particulier", "ondernemer"],
        "onlineAanvragen": true,
        "modified": "2026-01-15"
      }
    ],
    "pagination": { "limit": 50, "offset": 0, "total": 142, "hasMore": true }
  },
  "meta": { "generatedAt": "2026-03-12T12:00:00.000Z" }
}
```

**Query parameters:** `limit` (default 50, max 200), `offset` (default 0)

**Data source:** `https://flevoland.nl/loket/loketoverview?sc40=true` — SC4.0 XML feed parsed server-side using regex, cached 30 minutes. Stale cache is returned on feed unavailability.

**Response:** `application/json`

Each item contains: `id` (`productID` element), `title` (`dcterms:title`), `description`, (`dcterms:abstract`), `url` (`dcterms:identifier`), `audience` (array of `"ondernemer"` | `"particulier"`), `onlineAanvragen` (boolean, `true` when the `<onlineAanvragen>` element is `"ja"`), `modified` (`dcterms:modified` or `null`). HTML entities are decoded server-side.

Items with no title are filtered out.

**`GET /v1/public/regelcatalogus` response shape:**
 
```json
{
  "success": true,
  "data": {
    "services": [
      {
        "uri": "https://example.org/service/zorgtoeslag",
        "title": "Zorgtoeslag",
        "description": "Healthcare allowance for low-income households.",
        "organisationUri": "https://example.org/org/belastingdienst"
      }
    ],
    "organisations": [
      {
        "uri": "https://example.org/org/belastingdienst",
        "name": "Belastingdienst",
        "homepage": "https://belastingdienst.nl",
        "logo": "https://api.triplydb.com/assets/..."
      }
    ],
    "concepts": [
      {
        "uri": "https://example.org/concept/toetsingsinkomen",
        "prefLabel": "Toetsingsinkomen",
        "serviceTitle": "Zorgtoeslag",
        "exactMatch": "https://wetten.overheid.nl/..."
      }
    ],
    "rules": [
      {
        "uri": "https://example.org/rule/zorgtoeslag-artikel-1",
        "ruleTitle": "Zorgtoeslag artikel 1",
        "description": "Beschrijving van de regel...",
        "serviceTitle": "Zorgtoeslag",
        "validFrom": "2026-01-01",
        "confidence": "high"
      }
    ]
  },
  "meta": { "generatedAt": "2026-03-12T12:00:00.000Z" }
}
```
 
---
 
**`POST /v1/public/use-case` request body:**
```json
{
  "title": "Subsidietoets voor Flevolandse inwoners",
  "description": "## 1. Submitter · Indiener\n\n| Veld | Waarde |\n|---|---|\n| Naam | Jan de Vries |"
}
```

**`POST /v1/public/use-case` response:**
```json
{
  "success": true,
  "data": {
    "iid": 42,
    "web_url": "https://git.open-regels.nl/showcases/iou-architectuur/-/issues/42"
  },
  "meta": { "generatedAt": "2026-04-01T10:00:00.000Z" }
}
```

The `title` is automatically prefixed with `[Use Case]` before creation. Requires `GITLAB_TOKEN`, `GITLAB_BASE_URL`, and `GITLAB_PROJECT_PATH` to be set on the backend. Returns `503 GITLAB_NOT_CONFIGURED` when any of these are missing.

**`GET /v1/public/use-cases` response shape:**
```json
{
  "success": true,
  "data": [
    {
      "iid": 42,
      "title": "[Use Case] Subsidietoets voor Flevolandse inwoners",
      "state": "opened",
      "created_at": "2026-04-01T10:00:00.000Z",
      "updated_at": "2026-04-01T10:00:00.000Z",
      "web_url": "https://git.open-regels.nl/showcases/iou-architectuur/-/issues/42",
      "labels": ["Submitted"],
      "assignees": [],
      "description": "## 1. Submitter · Indiener\n\n..."
    }
  ]
}
```

**`POST /v1/public/feedback` request (multipart/form-data fields):**

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Submitter name |
| `org` | string | No | Organisation |
| `role` | string | No | Function / role |
| `contact` | string | Yes | Contact e-mail address |
| `description` | string | Yes | Feedback description |
| `screenshots` | file[] | No | Up to 5 image files, max 10 MB each |

**`POST /v1/public/feedback` response:**
```json
{
  "success": true,
  "data": {
    "iid": 43,
    "web_url": "https://git.open-regels.nl/showcases/iou-architectuur/-/issues/43"
  }
}
```

**`POST /v1/public/upload-file` request (multipart/form-data fields):**

| Field | Type | Required | Description |
|---|---|---|---|
| `file` | file | Yes | Any file type, max 10 MB |

**`POST /v1/public/upload-file` response:**
```json
{
  "success": true,
  "data": {
    "markdown": "![filename](/uploads/abc123/filename.pdf)"
  }
}
```

The returned `markdown` string is the GitLab-hosted reference. The use-case form collects these references for all attachments and appends them as a `## Bijlagen · Attachments` section to the issue body before calling `POST /v1/public/use-case`.

---

## HR Onboarding
 
These endpoints require a valid JWT with the `caseworker` or `hr-medewerker` role. Tenant isolation is applied via the `municipality` JWT claim — a caseworker from Utrecht cannot retrieve Den Haag's onboarding records.
 
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/v1/hr/onboarding/profile` | Bearer JWT (caseworker) | Returns the flattened historic variables for a completed `HrOnboardingProcess` instance identified by `?employeeId=`. Any caseworker may look up their own record; `hr-medewerker` may look up any employee's record within the same municipality. Returns 500 `HR_PROFILE_FAILED` when no completed instance is found. |
| `GET` | `/v1/hr/onboarding/completed` | Bearer JWT (caseworker) | Returns all completed `HrOnboardingProcess` instances for the caseworker's municipality, enriched with `employeeId`, `firstName`, `lastName`, `startTime`, and `endTime`. |
 
**`GET /v1/hr/onboarding/profile` request:**
 
```
GET /v1/hr/onboarding/profile?employeeId=emp-001
Authorization: Bearer <token>
```
 
**`GET /v1/hr/onboarding/completed` response shape:**
 
```json
{
  "success": true,
  "data": [
    {
      "id": "process-instance-uuid",
      "startTime": "2026-03-11T09:00:00.000Z",
      "endTime": "2026-03-11T10:30:00.000Z",
      "employeeId": "emp-001",
      "firstName": "Jan",
      "lastName": "de Vries"
    }
  ]
}
```
 
---

## RIP Phase 1

These endpoints require a valid JWT with the `caseworker` role. Tenant isolation is applied via the `municipality` process variable compared to the JWT `municipality` claim.

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/v1/rip/phase1/active` | Bearer JWT (caseworker) | Lists all active `RipPhase1Process` instances for the authenticated user's municipality, enriched with `projectNumber`, `projectName`, and `edocsWorkspaceId`. |
| `GET` | `/v1/rip/phase1/:instanceId/documents` | Bearer JWT (caseworker) | Returns all three document templates bundled in the deployment for a given process instance, together with current process variables. Documents not yet produced return `null`. Applies tenant isolation via the `municipality` process variable. |
| `GET` | `/v1/rip/phase1/completed` | Bearer JWT (caseworker) | Lists all completed `RipPhase1Process` instances for the authenticated user's municipality, enriched with `projectNumber`, `projectName`, `edocsWorkspaceId`, and `endTime`. |

**`GET /v1/rip/phase1/active` response shape:**
```json
{
  "success": true,
  "data": [
    {
      "id": "process-instance-uuid",
      "startTime": "2026-03-13T09:00:00.000Z",
      "projectNumber": "123456789",
      "projectName": "Test",
      "edocsWorkspaceId": "stub-ws-123456789"
    }
  ]
}
```

**`GET /v1/rip/phase1/:instanceId/documents` response shape:**
```json
{
  "success": true,
  "data": {
    "variables": {
      "projectNumber": "123456789",
      "projectName": "Test",
      "municipality": "flevoland"
    },
    "intakeReport": { },
    "psuReport": null,
    "pdp": null
  }
}
```

`intakeReport`, `psuReport`, and `pdp` are `DocumentTemplate` objects when the corresponding ServiceTask has completed, or `null` when not yet produced.

**`GET /v1/rip/phase1/completed` response shape:**
```json
{
  "success": true,
  "data": [
    {
      "id": "process-instance-uuid",
      "startTime": "2026-03-13T09:00:00.000Z",
      "endTime": "2026-03-13T14:30:00.000Z",
      "projectNumber": "123456789",
      "projectName": "Test",
      "edocsWorkspaceId": "stub-ws-123456789"
    }
  ]
}
```

---
 
## eDOCS
 
All `/v1/edocs` endpoints require a Bearer JWT issued by Keycloak (`aud: ronl-business-api`). They are intended for machine-to-machine access — the primary consumer is Microsoft Copilot Studio via the `copilot-studio-edocs` Keycloak client, though they can be called by any authenticated client.
 
When `EDOCS_STUB_MODE=true` (default on ACC), all endpoints return realistic fake responses. No live eDOCS server is contacted.
 
| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/v1/edocs/status` | Bearer JWT | Returns service health: `status` (`stub`, `up`, or `down`), `library`, `stubMode`, and optional `latencyMs` |
| `POST` | `/v1/edocs/workspaces/ensure` | Bearer JWT | Creates or retrieves a project workspace. Returns `workspaceId`, `workspaceName`, `created` |
| `POST` | `/v1/edocs/documents` | Bearer JWT | Uploads a base64-encoded document to a workspace. Returns `documentId`, `documentNumber`, `workspaceId` |
| `GET` | `/v1/edocs/workspaces/:workspaceId/documents` | Bearer JWT | Lists all documents in a workspace |
 
**`GET /v1/edocs/status` response:**
 
```json
{
  "success": true,
  "data": {
    "status": "stub",
    "library": "DOCUVITT",
    "stubMode": true
  },
  "timestamp": "2026-03-14T20:32:47.462Z"
}
```
 
**`POST /v1/edocs/workspaces/ensure` request body:**
 
```json
{
  "projectNumber": "FL-INF-2025-042",
  "projectName": "N308 Reconstructie"
}
```
 
**`POST /v1/edocs/documents` request body:**
 
```json
{
  "workspaceId": "2993896",
  "filename": "rip-intake-report-FL-INF-2025-042.txt",
  "contentBase64": "<base64-encoded content>",
  "metadata": {
    "docName": "FL-INF-2025-042 — Intake Report — N308 Reconstructie",
    "appId": "INFRA"
  }
}
```
 
**`GET /v1/edocs/workspaces/:workspaceId/documents` response:**
 
```json
{
  "success": true,
  "data": {
    "workspaceId": "2993896",
    "documents": [
      {
        "id": "stub-doc-1",
        "name": "rip-intake-report.pdf",
        "documentNumber": "2993898"
      }
    ]
  },
  "timestamp": "2026-03-14T20:32:53.462Z"
}
```
 
For OAuth setup and curl verification, see [Copilot Studio — eDOCS OAuth Integration](../developer/copilot-studio-edocs.md).

---

## Operaton MCP AI Assistant

**`GET /v1/mcp/sources`**

Returns all registered MCP providers with their connection status. Used by the frontend to populate the source selector in the Gereedschap tab. Returns an empty array when `MCP_ENABLED=false`.

**Auth:** JWT required — `caseworker` or `admin` role.

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "operaton",
      "displayName": "Process Engine",
      "description": "Operaton BPMN/DMN — process instances, tasks, decisions, deployments",
      "connected": true
    },
    {
      "id": "triplydb",
      "displayName": "Knowledge Graph",
      "description": "TriplyDB SPARQL — decision models, services, organisations, rules",
      "connected": true
    }
  ]
}
```

---

**`POST /v1/mcp/chat`**

Runs a single agentic chat turn through the MCP loop and streams the response via Server-Sent
Events.

**Auth:** JWT required — `caseworker` or `admin` role.

**Request body:**
```json
{
  "message": "How many active process instances are running?",
  "history": [
    { "role": "user", "content": "..." },
    { "role": "assistant", "content": "..." }
  ],
  "sources": ["operaton", "triplydb"]
}
```

The `sources` array controls which MCP providers are active for this turn. An empty array activates all connected providers. Provider IDs are returned by `GET /v1/mcp/sources`.

**Response:** `Content-Type: text/event-stream`

Headers are flushed immediately. Events arrive as newline-delimited `data:` frames:
```
data: {"type":"status","message":"Calling processInstance_count…"}

data: {"type":"delta","text":"There are currently "}

data: {"type":"delta","text":"42 active process instances."}

data: {"type":"done"}
```

Pre-flight errors (MCP disabled, MCP not connected, missing message) are returned as standard
JSON with the appropriate HTTP status code before the stream is opened.

| Event type | When                                          |
|------------|-----------------------------------------------|
| `status`   | Before each MCP tool call                     |
| `delta`    | Each text token from Claude                   |
| `done`     | Loop completed                                |
| `error`    | Timeout, tool failure, or Anthropic API error |

**Timeout:** 240 seconds. **Not recorded in the audit log.**

---
 
## M2M — Operaton

All `/v1/m2m` endpoints require a Bearer JWT issued by Keycloak (`aud: ronl-business-api`). Only `jwtMiddleware` is applied — no tenant scoping. These endpoints are intended for the `operaton-mcp-client` Keycloak client and other system-level callers.

The `M2M_ALLOWED_OPERATIONS` constant in `m2m.routes.ts` gates which operations are active. Commenting out an entry returns `403 OPERATION_NOT_PERMITTED` for that operation — no other code changes required. See [Operaton MCP Client](../developer/operaton-mcp-client.md) for Keycloak setup and authentication details.

### Process

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/v1/m2m/process` | List active process instances across all organisations. Query params forwarded to Operaton. |
| `POST` | `/v1/m2m/process/:key/start` | Start a process instance by definition key |
| `GET` | `/v1/m2m/process/history` | Query process history. Request body forwarded to Operaton. |
| `GET` | `/v1/m2m/process/:id/status` | Get process instance status |
| `GET` | `/v1/m2m/process/:id/variables` | Get current process variables (plain values) |
| `GET` | `/v1/m2m/process/:id/historic-variables` | Get final variable state of a completed instance |
| `GET` | `/v1/m2m/process/:id/decision-document` | Fetch the DocumentTemplate linked via `ronl:documentRef`. Returns 404 `DOCUMENT_NOT_FOUND` if no `ronl:documentRef` is present. |
| `GET` | `/v1/m2m/process/:key/start-form` | Fetch the deployed Camunda Form schema for a process start event. Returns 404 `FORM_NOT_FOUND` if no form is linked. |
| `GET` | `/v1/m2m/process/:key/variable-hints` | Fetch deduplicated variable names and types from history |
| `DELETE` | `/v1/m2m/process/:id` | Cancel a process instance |

### Task

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/v1/m2m/task` | List all open tasks across all organisations |
| `GET` | `/v1/m2m/task/:id` | Get a single task by ID |
| `GET` | `/v1/m2m/task/:id/variables` | Get all process variables for a task |
| `GET` | `/v1/m2m/task/:id/form-schema` | Fetch the deployed Camunda Form schema for a task. Returns 404 `FORM_NOT_FOUND` if no form is linked. |
| `POST` | `/v1/m2m/task/:id/claim` | Claim a task. Body: `{ "userId": "..." }` (optional — falls back to token subject) |
| `POST` | `/v1/m2m/task/:id/complete` | Complete a task with submitted variables |

### Decision

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/v1/m2m/decision/:key/evaluate` | Evaluate a DMN decision table by key |
| `GET` | `/v1/m2m/decision/:key` | Fetch decision definition metadata |

**`POST /v1/m2m/decision/:key/evaluate` request body:**
```json
{
  "variables": {
    "treeDiameter": 45,
    "protectedArea": false
  }
}
```

### Test script

`scripts/test-m2m-routes.sh` validates all M2M routes against a running instance. It obtains a token via Client Credentials, checks JWT claims, exercises every active operation, and verifies tenant isolation remains intact on the standard caseworker routes.

**Prerequisites:** `curl` and `jq` must be available on `$PATH`. The `operaton-mcp-client` Keycloak client must be configured with `CAMUNDA_BPM_AUTHORIZATION_ENABLED=false` on the target Operaton instance (or equivalent authorization grants in place) — without this, process, history, and deployment endpoints return 404.

**Usage:**
```bash
CLIENT_SECRET=<secret> bash scripts/test-m2m-routes.sh
```

**Overridable environment variables:**

| Variable | Default | Description |
|---|---|---|
| `BASE_URL` | `https://acc.api.open-regels.nl` | RONL Business API base URL |
| `KEYCLOAK_URL` | `https://acc.keycloak.open-regels.nl` | Keycloak base URL |
| `CLIENT_ID` | `operaton-mcp-client` | Keycloak client ID |
| `CLIENT_SECRET` | _(required)_ | Keycloak client secret |
| `DECISION_KEY` | `TreeFellingDecision` | DMN key used for the decision evaluate test |

**What it checks:**

- Token obtained and JWT claims valid (`azp`, `aud`, `municipality` absent)
- All active operations return HTTP 200 (404 accepted for `form-schema`, `start-form`, `decision-document` — resource may not exist in the deployment)
- All disabled operations return `403 OPERATION_NOT_PERMITTED`
- `GET /v1/task` with an M2M token returns `403 MISSING_TENANT` — confirming tenant-scoped routes remain isolated
 
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
| `GET` | `/v1/task/history` | Bearer JWT (caseworker) | List completed tasks for the caseworker's municipality. Tenant-scoped via `municipality` process variable. Returns up to 200 tasks sorted by `endTime` descending. Route registered before `/:id` to prevent shadowing. |

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

## Admin

The `/v1/admin` endpoints require a valid JWT with the `admin` role. Non-admin caseworkers receive `403 FORBIDDEN`.

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/v1/admin/audit` | Bearer JWT (`admin`) | Returns paginated audit log records from PostgreSQL. Query: `?limit=` (default 50, max 200), `?offset=` (default 0). Excluded from its own audit trail. |

**`GET /v1/admin/audit` response shape:**
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "timestamp": "2026-03-19T12:00:00.000Z",
        "tenant_id": "flevoland",
        "user_id": "sub-uuid-from-jwt",
        "action": "task.claim",
        "resource_type": null,
        "resource_id": null,
        "details": { "taskId": "task-uuid" },
        "result": "success",
        "error_message": null,
        "request_id": null
      }
    ],
    "pagination": { "limit": 50, "offset": 0, "total": 312, "hasMore": true }
  }
}
```

For M2M tokens, `tenant_id` is set to the Keycloak `azp` claim (e.g. `operaton-mcp-client`) because service account tokens carry no `municipality` claim.

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
| `MISSING_TENANT` | 403 | M2M token used on a tenant-scoped route — no `municipality` claim present |
| `OPERATION_NOT_PERMITTED` | 403 | M2M operation is disabled in `M2M_ALLOWED_OPERATIONS` |
| `GITLAB_NOT_CONFIGURED` | 503 | Required GitLab env vars (`GITLAB_TOKEN`, `GITLAB_PROJECT_PATH`) are missing |
| `GITLAB_ERROR` | 502 | GitLab API rejected the request |
| `GITLAB_UNREACHABLE` | 502 | GitLab API could not be reached |
| `USE_CASE_INVALID` | 400 | `title` or `description` missing from use-case submission |
| `MISSING_FIELDS` | 400 | Required fields absent from feedback or file upload request |
| `NO_FILE` | 400 | `POST /v1/public/upload-file` called without a file |
| `MCP_DISABLED` | 503 | `MCP_ENABLED=false` — MCP endpoints are inactive |
| `MCP_NOT_CONNECTED` | 503 | No connected MCP providers match the requested `sources` |
| `DB_ERROR` | 500 | PostgreSQL query failed in admin/audit endpoint |
