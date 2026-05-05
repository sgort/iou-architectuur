# Backend Architecture

The backend is a Node.js/Express TypeScript API. It sits between the React frontend and two external services: TriplyDB (SPARQL knowledge graph) and Operaton (DMN execution engine). Its responsibilities are SPARQL querying, DMN chain orchestration, variable mapping between chain steps, and proxying dynamic TriplyDB endpoint calls.

---

## API versioning

All endpoints follow `/v1/*`. Legacy `/api/*` endpoints exist with `Deprecation` response headers for backward compatibility. The version is included in every response via the `API-Version` header, following Dutch Government API Design Rules API-20 and API-57.

---

## Endpoints

### Health

```
GET /v1/health
```

Returns service health including TriplyDB and Operaton latency checks. Used by CI/CD pipelines and the frontend status indicator.

```json
{
  "name": "Linked Data Explorer Backend",
  "version": "0.4.0",
  "environment": "production",
  "status": "healthy",
  "uptime": 3600,
  "services": {
    "triplydb": { "status": "up", "latency": 145 },
    "operaton": { "status": "up", "latency": 98 }
  }
}
```

### DMN discovery

```
GET /v1/dmns?endpoint={sparql_endpoint_url}
```

Queries TriplyDB for all `cprmv:DecisionModel` resources at the given endpoint. Returns models with full variable lists and governance/vendor metadata. Cached per endpoint for 5 minutes.

```
GET /v1/dmns/:identifier?endpoint={url}
```

Returns full metadata for a single DMN by its `dct:identifier` value.

```
GET /v1/dmns/enhanced-chain-links?endpoint={url}
```

Returns all chain links including both exact identifier matches and semantic `skos:exactMatch` matches. Each link includes a `matchType` field: `"exact"`, `"semantic"`, or `"both"`.

```
GET /v1/dmns/semantic-equivalences?endpoint={url}
```

Returns all variable pairs from different DMNs that share a `skos:exactMatch` concept URI.

```
GET /v1/dmns/cycles?endpoint={url}
```

Returns circular dependencies detected via semantic links (3-hop traversal).

### Chain discovery

```
GET /v1/chains?endpoint={url}
```

Returns all DMN pairs where an output variable of one model matches an input variable of another by exact identifier.

### Chain execution

```
POST /v1/chains/execute
```

Request body:

```json
{
  "chain": ["SVB_LeeftijdsInformatie", "SZW_BijstandsnormInformatie"],
  "inputs": { "geboortedatum": "1960-01-01" },
  "endpoint": "https://api.open-regels.triply.cc/..."
}
```

Executes the chain sequentially, flattening outputs into inputs between steps. Returns per-step results and combined final output.

```
POST /v1/chains/execute/heusdenpas
```

Convenience endpoint for the fixed three-step Heusdenpas chain with production test data. Target execution time: <1000ms. See [API Reference](../reference/api-reference.md) for the full request/response.

```
POST /v1/chains/export
```

Generates a DRD XML file from a chain and deploys it to Operaton. See [DRD Generation](drd-generation.md).

### eDOCS

```
GET  /v1/edocs/status
POST /v1/edocs/workspaces/ensure
POST /v1/edocs/documents
GET  /v1/edocs/workspaces/:workspaceId/documents
```

Integrates with the OpenText eDOCS document management system. Used by the RIP Phase 1 process to create project workspaces and file documents. In stub mode (`EDOCS_STUB_MODE=true`, default) all methods return realistic fake responses so the process runs end-to-end before a live eDOCS server is available.

See [eDOCS Integration](edocs-integration.md) and the [API Reference](../reference/api-reference.md#edocs) for request/response details.

### TriplyDB proxy

```
POST /v1/triplydb/query
```

Request body:

```json
{
  "endpoint": "https://api.open-regels.triply.cc/...",
  "query": "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 5"
}
```

Proxies a SPARQL query to any TriplyDB endpoint, bypassing CORS restrictions. Used by the frontend Query Editor for dynamic endpoint support.

---

### Asset storage
```
GET    /v1/assets/bpmn
POST   /v1/assets/bpmn
DELETE /v1/assets/bpmn/:id
GET    /v1/assets/bpmn/by-bpmn-id/:bpmnProcessId

GET    /v1/assets/forms
POST   /v1/assets/forms
DELETE /v1/assets/forms/:id

GET    /v1/assets/documents
POST   /v1/assets/documents
DELETE /v1/assets/documents/:id
```

Persists BPMN processes, form schemas, and document templates to PostgreSQL. All routes return `503 DB_NOT_CONFIGURED` when `DATABASE_URL` is absent. See [Asset Storage](asset-storage.md) for the service architecture and [API Reference](../reference/api-reference.md#asset-storage) for full request/response documentation.

---

## Database

The backend connects to a PostgreSQL database via a `pg.Pool`. The pool is initialised in `src/db/pool.ts` when `DATABASE_URL` is present in the environment. If the variable is absent, `pool` is `null` and all asset endpoints respond with `503`.

Schema migrations run automatically on startup via `migrate()` in `src/db/migrate.ts`, called from `startServer()` before `app.listen()`. The migration is idempotent (`CREATE TABLE IF NOT EXISTS`).
```
src/db/
├── pool.ts       — pg.Pool initialisation, error listener, null-if-unconfigured guard
└── migrate.ts    — idempotent DDL: process_definitions, form_schemas, document_templates
```

See [PostgreSQL Deployment](deployment-postgresql.md) for Azure provisioning.

---

## SPARQL service

`sparql.service.ts` builds and executes all SPARQL queries against TriplyDB. Key functions:

```typescript
findAllDmns(endpoint: string): Promise<DmnModel[]>
findEnhancedChainLinks(endpoint: string): Promise<EnhancedChainLink[]>
findSemanticEquivalences(endpoint: string): Promise<SemanticEquivalence[]>
```

The `findEnhancedChainLinks` query uses a `BIND(IF(...))` pattern to categorise each link as `exact`, `semantic`, or `both`, then expands `both` entries into two separate records post-query. This is the mechanism described in [Enhanced Validation](enhanced-validation.md).

---

## Orchestration service

`orchestration.service.ts` executes sequential chains:

1. Fetch DMN metadata for each step from the SPARQL service (cached)
2. For the first step, use the user-supplied inputs
3. For each subsequent step, build inputs by:
   - Flattening all previous step outputs into a single map
   - For semantic matches: rename output variable keys to match the expected input identifiers
   - Merge with any additional user-supplied inputs
4. Call `operaton.service.ts` for each step
5. Accumulate results

Variable flattening means a semantic chain like `heeftJuisteLeeftijd → leeftijd_requirement` is transparently bridged — the output value is passed under the input's expected key.

---

## Operaton service

`operaton.service.ts` calls the Operaton REST API:

```
POST {OPERATON_BASE_URL}/decision-definition/key/{decisionRef}/evaluate
```

Request payload maps to Operaton's variable format:

```json
{
  "variables": {
    "geboortedatum": { "value": "1960-01-01", "type": "String" }
  }
}
```

For DRD execution, the same endpoint is used with the DRD entry-point identifier. Operaton handles internal decision dependency evaluation.

---

## eDOCS service

`edocs.service.ts` wraps the OpenText eDOCS REST API. It authenticates once via `POST /connect`, caches the `X-DM-DST` session token, and re-authenticates automatically on `401`/`403`. Key methods:

```typescript
ensureWorkspace(projectNumber: string, projectName: string): Promise<EdocsWorkspaceResult>
uploadDocument(workspaceId: string, filename: string, contentBase64: string, metadata: EdocsDocumentMetadata): Promise<EdocsDocumentResult>
getWorkspaceDocuments(workspaceId: string): Promise<...>
healthCheck(): Promise<{ status: 'up' | 'down' | 'stub' }>
```

When `EDOCS_STUB_MODE=true`, all methods return realistic fake data and log what they would have done. The stub is transparent to all callers.

---

## External task worker

`externalTaskWorker.service.ts` polls Operaton's external task API (`POST /external-task/fetchAndLock`) using long-polling (`asyncResponseTimeout: 20 000 ms`). It handles two topics:

| Topic                 | Reads                                                                                       | Writes                                                            |
| --------------------- | ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| `rip-edocs-workspace` | `projectNumber`, `projectName`                                                              | `edocsWorkspaceId`, `edocsWorkspaceName`, `edocsWorkspaceCreated` |
| `rip-edocs-document`  | `edocsWorkspaceId`, `documentTemplateId`, `edocsDocumentVariableName`, + template variables | `<edocsDocumentVariableName>` (e.g. `edocsIntakeReportId`)        |

`documentTemplateId` and `edocsDocumentVariableName` are injected per ServiceTask via `camunda:inputParameter` in the BPMN, making the single topic handler reusable across all three document upload steps in the RIP Phase 1 process.

The worker starts inside the `app.listen()` callback and stops in both `SIGTERM` and `SIGINT` handlers.

---

## Logging

Winston structured logging with JSON output. All service calls log at `[INFO]` level with context (endpoint, query length, result count, latency). Errors log at `[ERROR]` with stack traces. Log level is configurable via `LOG_LEVEL` environment variable.

---

## Error handling

A central `errorHandler.ts` middleware catches unhandled errors and returns standardised JSON error responses with appropriate HTTP status codes. SPARQL and Operaton errors are wrapped with descriptive messages before being returned to the frontend. No sensitive data is included in error responses.

---

## Performance

**Targets:**

| Operation               | Target   |
| ----------------------- | -------- |
| Chain execution         | < 1000ms |
| Health check response   | < 100ms  |
| DMN list query          | < 500ms  |
| API response time (p95) | < 200ms  |

**Production baselines (Heusdenpas chain, 3 DMNs):**

| Measurement                              | Observed  |
| ---------------------------------------- | --------- |
| Full chain execution                     | ~827ms    |
| Health check (incl. TriplyDB + Operaton) | ~180ms    |
| DMN discovery (SPARQL + parsing)         | ~350ms    |
| TriplyDB round-trip latency              | 150–200ms |
| Operaton per-DMN execution               | 80–120ms  |

---

## Security

**HTTP headers** — [Helmet](https://helmetjs.github.io/) is configured to set comprehensive security headers on all responses, including `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`, and `Strict-Transport-Security`.

**CORS** — only origins listed in `CORS_ORIGIN` are permitted. In production this is restricted to `https://linkeddata.open-regels.nl` and `https://cpsv.open-regels.nl`. All other origins receive a CORS rejection.

**Input validation** — type checking is applied to all request inputs. Variable names, DMN identifiers, and SPARQL endpoint URLs are validated before any service call is made. Request body size is limited to 10 MB.

**Environment variables** — all sensitive configuration (TriplyDB endpoint URLs, Operaton API URLs, CORS origins, eDOCS credentials) is stored in environment variables and never hardcoded. eDOCS-specific variables: `EDOCS_BASE_URL`, `EDOCS_LIBRARY`, `EDOCS_USER_ID`, `EDOCS_PASSWORD`, `EDOCS_STUB_MODE`.

**Error responses** — the central error handler scrubs stack traces and internal context before returning responses to clients, ensuring no implementation details are exposed.

---

## Dutch Government API Design Rules compliance

The API follows the [Dutch Government API Design Rules](https://publicatie.centrumvoorstandaarden.nl/api/adr/) for interoperability and standardisation.

**Implemented rules:**

| Rule   | Description                 | Implementation                         |
| ------ | --------------------------- | -------------------------------------- |
| API-20 | Major version in URI        | `/v1/*` endpoints                      |
| API-57 | Version header in responses | `API-Version: 0.4.0` on every response |
| API-05 | Use nouns for resources     | `dmns`, `chains`, `health`             |
| API-54 | Plural/singular naming      | Correct usage throughout               |
| API-48 | No trailing slashes         | Enforced in routing                    |
| API-53 | Hide implementation details | Clean service abstractions             |

**Language note (API-04)** — technical endpoint names (`health`, `version`) follow international convention in English. Business resource names (`dmns`, `chains`) follow the source data. Dutch variable names (e.g., `geboortedatum`) are preserved as-is from the DMN definitions.

**Planned:**

| Rule           | Description                            | Target version |
| -------------- | -------------------------------------- | -------------- |
| API-16, API-51 | OpenAPI 3.0 spec at `/v1/openapi.json` | v0.5.0         |
| API-02         | Standard error response format         | v0.5.0         |
| API-10         | Resource collections with pagination   | v1.0.0         |
