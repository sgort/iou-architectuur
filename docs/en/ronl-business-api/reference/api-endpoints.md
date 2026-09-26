---
component: RONL Business API
---

# API Endpoints

The reference for the RONL Business API is its OpenAPI document, rendered on
[API Specification](api-specification.md). It describes every `/v1` operation
except the machine-to-machine surface under `/v1/m2m`, which is not described
yet ([#214](https://github.com/sgort/ronl-business-api/issues/214)) and is
therefore documented here.

This page retires when #214 empties `openapi/pending.json`: at that point the
specification covers everything and nothing here is needed.

---

## M2M — Operaton { #m2m-operaton }

All 18 `/v1/m2m` operations require a Bearer JWT issued by Keycloak
(`aud: ronl-business-api`). Only `jwtMiddleware` is applied — no tenant
middleware — so the surface is deliberately cross-tenant: it lists and acts on
process instances and tasks of every organisation. It is intended for the
`operaton-mcp-client` Keycloak client and other system-level callers. See
[Operaton MCP Client](../developer/operaton-mcp-client.md) for Keycloak setup and
authentication details.

The M2M routes talk to their own Operaton engine, configured by
`OPERATON_M2M_BASE_URL` (default `https://operaton-doc.open-regels.nl/engine-rest`)
with `OPERATON_M2M_USERNAME` / `OPERATON_M2M_PASSWORD` — separate from
`OPERATON_BASE_URL`, which the tenant-scoped routes use.

The exported `M2M_ALLOWED_OPERATIONS` list in `m2m.routes.ts` gates each
operation. All 18 are currently enabled; commenting an entry out makes that
operation answer `403 OPERATION_NOT_PERMITTED`, with no other code change.

Responses use the service's `{ success, data }` envelope, with two exceptions
noted below; errors answer `{ success: false, error: { code, message } }`.

### Process

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/v1/m2m/process` | List active process instances across all organisations. Query parameters are forwarded to Operaton. |
| `POST` | `/v1/m2m/process/:key/start` | Start a process instance by definition key. Body: `{ variables, businessKey? }`; variables may be plain values or typed `{ value, type }`. Returns `processInstanceId` and `businessKey`. |
| `GET` | `/v1/m2m/process/history` | Query process history. The **request body** of this `GET` is forwarded to Operaton unchanged. |
| `GET` | `/v1/m2m/process/:id/status` | Process instance status: `active`, `suspended` or `ended`. `404 PROCESS_NOT_FOUND` if unknown. |
| `GET` | `/v1/m2m/process/:id/variables` | Current process variables, flattened to plain values |
| `GET` | `/v1/m2m/process/:id/historic-variables` | Final variable state of a completed instance |
| `GET` | `/v1/m2m/process/:id/decision-document` | The `DocumentTemplate` linked via `ronl:documentRef`. Answers `{ success, template }` rather than `data`. `404 DOCUMENT_NOT_FOUND` when there is none. |
| `GET` | `/v1/m2m/process/:key/start-form` | Deployed Camunda Form schema for the start event. `404 FORM_NOT_FOUND` if no form is linked; `415 UNSUPPORTED_FORM_TYPE` if the linked form is not JSON. |
| `GET` | `/v1/m2m/process/:key/variable-hints` | Deduplicated variable names and inferred types from history. Answers `{ success, variables }` rather than `data`. |
| `DELETE` | `/v1/m2m/process/:id` | Cancel a process instance. Optional body: `{ reason }`. |

### Task

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/v1/m2m/task` | List all open tasks across all organisations |
| `GET` | `/v1/m2m/task/:id` | A single task by ID. `404 TASK_NOT_FOUND` if unknown. |
| `GET` | `/v1/m2m/task/:id/variables` | All process variables for a task |
| `GET` | `/v1/m2m/task/:id/form-schema` | Deployed Camunda Form schema for a task. `404 FORM_NOT_FOUND` if no form is linked; `415 UNSUPPORTED_FORM_TYPE` if the linked form is not JSON. |
| `POST` | `/v1/m2m/task/:id/claim` | Claim a task. Body: `{ "userId": "..." }` (optional — falls back to the token subject) |
| `POST` | `/v1/m2m/task/:id/complete` | Complete a task. Body: `{ variables }`, plain or typed as for process start. |

### Decision

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/v1/m2m/decision/:key/evaluate` | Evaluate a DMN decision by key |
| `GET` | `/v1/m2m/decision/:key` | Decision definition metadata. `404 DECISION_NOT_FOUND` if unknown. |

**`POST /v1/m2m/decision/:key/evaluate` request body:**
```json
{
  "variables": {
    "treeDiameter": 45,
    "protectedArea": false
  }
}
```

Process start, cancel, task claim and complete, decision evaluation and the
process list are recorded in the audit log. For M2M tokens the audit
`tenant_id` is the Keycloak `azp` claim (for example `operaton-mcp-client`),
because service-account tokens carry no `municipality` claim.

### Test script

`scripts/test-m2m-routes.sh` checks the M2M routes against a running backend.
It obtains a token via Client Credentials, checks its claims, calls the read
operations and the decision evaluation, and verifies that tenant isolation
still holds on the standard caseworker routes. It does not start, cancel, claim
or complete anything.

**Prerequisites:** `curl` and `jq` on `$PATH`.

**Usage:**
```bash
# Local stack (default) — the secret is read from config/keycloak/ronl-realm.json
bash scripts/test-m2m-routes.sh

# Acceptance — the secret must be supplied
TARGET=acc CLIENT_SECRET=<secret> bash scripts/test-m2m-routes.sh
```

**Overridable environment variables:**

| Variable | Default | Description |
|---|---|---|
| `TARGET` | `local` | `local` or `acc`; selects the preset URLs and decision below |
| `BASE_URL` | `http://localhost:3002` (local), `https://acc.api.open-regels.nl` (acc) | RONL Business API base URL |
| `KEYCLOAK_URL` | `http://localhost:8080` (local), `https://acc.keycloak.open-regels.nl` (acc) | Keycloak base URL |
| `CLIENT_ID` | `operaton-mcp-client` | Keycloak client ID |
| `CLIENT_SECRET` | from the realm file (local only) | Keycloak client secret; required for `acc` |
| `DECISION_KEY` | `TreeFellingDecision` (local), `AwbCompletenessCheck` (acc) | DMN key for the decision tests |
| `DECISION_VARS` | matching preset | Request body for the evaluate test |

**What it checks:**

- Token obtained; `azp` is the client ID, `aud` contains `ronl-business-api`, `municipality` is absent
- The read operations return HTTP 200 (404 accepted for `form-schema`, `start-form`, `decision-document` and `historic-variables`, whose resource may not exist in the deployment); a 404 on `GET /v1/m2m/decision/:key` skips both decision checks
- On `local` only, known-fixture assertions: tenant-scoped processes (`AwbShellProcess`, `AwbZorgtoeslagProcess`) still yield their start forms through the untenanted surface, `RipR21Process` has no start form, and its variable hints resolve
- `GET /v1/task` with an M2M token returns `403 MISSING_TENANT` — tenant-scoped routes remain isolated

---

## eDOCS

The `/v1/edocs` operations — status, workspaces, document upload, profile,
versions and deletion — are described on
[API Specification](api-specification.md), under **Documents**. What the
specification does not carry:

- All of them require a Bearer JWT. The primary consumer is Microsoft Copilot
  Studio via the `copilot-studio-edocs` Keycloak client; see
  [Copilot Studio — eDOCS](../developer/copilot-studio-edocs.md).
- `EDOCS_STUB_MODE` defaults to `true`: unless it is set to `false`, every
  operation answers realistic fake responses and no eDOCS server is contacted.
- `POST /v1/edocs/documents` requires `metadata.docName` and
  `metadata.department` (eDOCS `UV_AFD_NAAM`, which the DM server also
  demands). For live-tested behaviour — which upload path works, which version
  value downloads — see [eDOCS — Live Testing](../developer/testing/edocs-live-testing.md).

---

## Process definition deployment

One-click BPMN deployment belongs to the Linked Data Explorer's backend, not to
this API. See the Linked Data Explorer's
[API Specification](../../linked-data-explorer/reference/api-specification.md).
