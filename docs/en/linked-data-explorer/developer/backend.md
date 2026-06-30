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

### Norms

```
GET /v1/norms?endpoint={url}&rulesetid={ruleset}&applicable_date={YYYY-MM-DD}&cprmv_version={0.3.0|0.3.2|0.4.1}
```

Returns all `cprmv:Rule` paths and norms from the configured TriplyDB endpoint in the publish format consumed by the SPARQL editor's norm publisher. Each rule object mirrors the `cprmv-example.json` shape exactly: fully-qualified RDF/CPRMV keys for `type`, `id`, `definition`, and `contains`; short keys for `situatie`, `norm`, `per`, `rulesetid`, `applicable_date`, and `rule_id_path`. The fully-qualified keys carry the namespace of the **selected `cprmv_version`** (see below).

Parent rules and their `cprmv:contains` children are aggregated into a single nested object per parent. Key insertion order is preserved across runs:

```
type, id, definition, contains?, situatie?, norm?, per?, rulesetid, applicable_date, rulesetid_index, rule_id_path, rule_id_path_key
```

Three fields are derived from `rule_id_path` and emit JSON `null` when the path does not match the canonical `<rulesetid>_<YYYY-MM-DD>_<index>[, <rest>]` shape:

| Field              | Source from `rule_id_path`                                 | Example                              |
| ------------------ | ---------------------------------------------------------- | ------------------------------------ |
| `applicable_date`  | The `_YYYY-MM-DD_` segment                                 | `"2025-07-01"`                       |
| `rulesetid_index`  | The integer after the date                                 | `0`                                  |
| `rule_id_path_key` | Path with date and index removed; stable across versions   | `"BWBR0002471, Artikel 2, lid 6"`   |

The response envelope also carries an `aggregations` block alongside `rules`:

```
data: {
  total: <number>,
  aggregations: { norms_per_rulesetid: { "<rulesetid>": <count>, ... } },
  rules: [...]
}
```

Counts are over the filtered result set, so `total` equals the sum of all `norms_per_rulesetid` values. Use this to render ruleset-level summaries without re-counting on the client.

**Dataset versioning and HTTP cache headers**

Each BWB ruleset (BWBR0002471, BWBR0015703, …) carries per-ruleset version metadata, published by the CPSV editor (see [CPRMV RuleSet / Dataset Generation](../../cpsv-editor/developer/cprmv-dataset-generation.md)). **Where that metadata lives depends on `cprmv_version`:** for `0.3.0`/`0.3.2` it is a `cprmv:Dataset` resource (with `dct:issued` + `dcat:version`); for `0.4.1` there is no `cprmv:Dataset` and it is read from the `cprmv:RuleSet` instead (`cprmv:validFrom`, which also serves as `published_at` — see the table below). A single ruleset can have multiple records — different applicable periods of the same law (e.g. BWBR0015703 at `2025-01-01` and `2026-01-01`) are **concurrent and equally authoritative**, not competing versions. A single `/v1/norms` response can span multiple rulesets, each carrying multiple records; the envelope therefore carries a `dataset_versions` map keyed by `cprmv:rulesetId`, where each value is a **list** of records:

```json
"dataset_versions": {
  "BWBR0015703": [
    {
      "version": "2026-01-01",
      "published_at": "2026-05-15T06:57:21Z",
      "title": "Participatiewet"
    },
    {
      "version": "2025-01-01",
      "published_at": "2026-05-15T07:45:36Z",
      "title": "Participatiewet"
    }
  ],
  "BWBR0044894": [
    { "version": null, "published_at": "2026-05-15T07:45:36Z", "title": null }
  ]
}
```

The list is pre-sorted: **`version` descending with nulls at the end, ties broken by `published_at` descending**. Element `[0]` is the most-recent applicable version of that ruleset.

Three per-entry fields:

| Field          | Source (0.3.x / 0.4.1)        | Notes |
| -------------- | ----------------------------- | ----- |
| `version`      | `dcat:version` / `cprmv:validFrom` | **Now present for every ruleset.** Since v1.10.5 the editor derives each ruleset's version from the BWB date its own rules carry (their `ruleIdPath`), so non-primary rulesets are versioned too. (`null` only survives for legacy data published before that change.) |
| `published_at` | `dct:issued` / `cprmv:validFrom` | **0.3.x:** the `cprmv:Dataset` publication timestamp — changes on every (re-)publication, the primary cache-validity signal. **0.4.1:** there is no `dct:issued`, so `cprmv:validFrom` doubles as `published_at` (see caveat below). |
| `title`        | `dct:title`                   | Primary ruleset only — the editor only knows the human title of the service's `legalResource`. `null` for non-primary rulesets. |

!!! warning "0.4.1 cache caveat"
    For `cprmv_version=0.4.1`, `published_at` equals `cprmv:validFrom` (the applicable date), not a publication timestamp. Re-publishing a RuleSet **with the same `validFrom`** but changed rule values does **not** change the ETag/`Last-Modified`, so a cached `0.4.1` response can be served for up to `max-age` (1 h) after a same-date correction. `0.3.x` does not have this caveat (`dct:issued` advances on every publish). A future fix is to emit `dct:issued`/`prov:generatedAtTime` on the 0.4.1 RuleSet.

**CPRMV version selection (`?cprmv_version=`)**

The optional `cprmv_version` query parameter selects which CPRMV vocabulary version the endpoint **queries and emits** — one of `0.3.0`, `0.3.2`, or `0.4.1` (anything else → `400 INVALID_PARAM`). It defaults to `0.3.0`, preserving the historical behaviour. The chosen value is echoed back in the `cprmv_version` envelope field, and the fully-qualified rule keys (`type`, `id`, `definition`, `contains`) carry that version's namespace:

| `cprmv_version` | Namespace bound to `cprmv:` | Per-ruleset metadata source |
| --------------- | --------------------------- | --------------------------- |
| `0.3.0` (default) | `https://cprmv.open-regels.nl/0.3.0/` | `cprmv:Dataset` |
| `0.3.2` | `https://cprmv.open-regels.nl/0.3.2/` | `cprmv:Dataset` |
| `0.4.1` | `https://standaarden.open-regels.nl/standards/cprmv/0.4.1#` | `cprmv:RuleSet` |

All three versions carry **flat `cprmv:Rule` resources with identical predicates** (`id`, `definition`, `rulesetId`, `ruleIdPath`, `situatie`, `norm`), so the rules query is one shape with the namespace swapped. The selected version is threaded through the rules query, the dataset-metadata query (cache keyed by endpoint **+ version**), the output keys, the `cprmv_version` field, and the ETag signature — so different versions never share a cache entry.

!!! warning "Changed semantics"
    `cprmv_version` previously described "the vocabulary the backend speaks, independent of the data". It now reflects the **requested** version and therefore the namespace of the data returned. Callers that pinned to `0.3.0` see no change (it is the default).

When **every** rulesetid in the response has at least one `dataset_versions` entry, the response carries strong HTTP cache headers:

```
ETag: "3c899856"
Last-Modified: Fri, 15 May 2026 07:45:36 GMT
Cache-Control: public, max-age=3600
```

The `ETag` is an opaque 8-hex hash over every `(version, published_at)` pair in `dataset_versions` plus all request parameters that affect the response shape. `title` is deliberately excluded — informational only, and a title-only update would arrive as a new `dct:issued` anyway. `Last-Modified` is the maximum `published_at` across *all* records in the response (not just the first per ruleset), so a consumer's `If-Modified-Since` returns `304 Not Modified` only when nothing in their query has been republished.

Conditional requests are honoured via Express's `req.fresh`:

```http
GET /v1/norms HTTP/1.1
If-None-Match: "3c899856"
```

For single-rulesetid queries (`?rulesetid=<id>`), the 304 check happens **before** the expensive rules SPARQL query — only the cheap (cached) metadata query runs for a 304 response. For multi-rulesetid queries the rules query must run first to know which rulesetids appear in the response.

When **any** rulesetid in the response lacks `cprmv:Dataset` records, `Cache-Control: no-cache` is set and `ETag` / `Last-Modified` are omitted. Safe-by-default: consumers must always refetch until every BWB they query has been published with at least one `cprmv:Dataset` record. During the rollout-from-scratch period this means caching kicks in progressively as Datasets are published.

Dataset metadata is cached in-memory for 60 seconds, keyed by endpoint URL **and `cprmv_version`** (so the `cprmv:Dataset` and `cprmv:RuleSet` metadata queries never share a cache entry).

**Query parameters** (all optional, may be combined):

| Parameter         | Description                                                                                                                                                          |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `endpoint`        | SPARQL endpoint URL. Defaults to `config.triplydb.endpoint` (`TRIPLYDB_ENDPOINT`) when omitted, matching the pattern used by `/v1/dmns`.                             |
| `rulesetid`       | Exact-match filter on `cprmv:rulesetId` (e.g. `BWBR0015703`). Must match `/^[A-Za-z0-9_-]+$/` or the request is rejected with `400 INVALID_PARAM`.                   |
| `applicable_date` | Filter on the dated segment of `cprmv:ruleIdPath` (e.g. `2026-01-01` matches paths containing `_2026-01-01_`). Must match `/^\d{4}-\d{2}-\d{2}$/` or `400`.          |
| `cprmv_version`   | CPRMV vocabulary version to query and emit: one of `0.3.0`, `0.3.2`, `0.4.1` (else `400 INVALID_PARAM`). Defaults to `0.3.0`. Selects the `cprmv:` namespace and the metadata model (`cprmv:Dataset` vs `cprmv:RuleSet`) — see the **CPRMV version selection** subsection above. |

Validated filter values are applied as SPARQL `FILTER` clauses server-side: exact-match on `?rulesetId` and `CONTAINS(STR(?ruleIdPath), "_<date>_")`. Filters are interpolated only after passing the regex gate, making SPARQL injection impossible. `cprmv_version` selects a namespace rather than a filter, so it is validated against the supported set rather than a character-class regex.

**Example response — flat rule** (most common; no `contains` key):

```json
{
  "success": true,
  "data": {
    "total": 1,
    "dataset_versions": {
      "BWBR0015703": [
        {
          "version": "2026-01-01",
          "published_at": "2026-05-15T06:57:21Z",
          "title": "Participatiewet"
        },
        {
          "version": "2025-01-01",
          "published_at": "2026-05-15T07:45:36Z",
          "title": "Participatiewet"
        }
      ]
    },
    "cprmv_version": "0.3.0",
    "aggregations": {
      "norms_per_rulesetid": {
        "BWBR0015703": 1
      }
    },
    "rules": [
      {
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "https://cprmv.open-regels.nl/0.3.0/Rule",
        "https://cprmv.open-regels.nl/0.3.0/id": "onderdeel a.",
        "https://cprmv.open-regels.nl/0.3.0/definition": "een alleenstaande van 18, 19 of 20 jaar: € 337,98;",
        "situatie": "een alleenstaande van 18, 19 of 20 jaar",
        "norm": "337,98",
        "rulesetid": "BWBR0015703",
        "applicable_date": "2025-07-01",
        "rulesetid_index": 0,
        "rule_id_path": "BWBR0015703_2025-07-01_0, Artikel 20, lid 1, onderdeel a.",
        "rule_id_path_key": "BWBR0015703, Artikel 20, lid 1, onderdeel a."
      }
    ]
  },
  "timestamp": "2026-05-14T14:00:00.000Z"
}
```

**Example response — rule with nested children** (conditional `contains` map; emitted only when the parent has `cprmv:contains` links to sub-rules):

```json
{
  "success": true,
  "data": {
    "total": 1,
    "dataset_versions": {
      "BWBR0015703": [
        {
          "version": "2026-01-01",
          "published_at": "2026-05-15T06:57:21Z",
          "title": "Participatiewet"
        },
        {
          "version": "2025-01-01",
          "published_at": "2026-05-15T07:45:36Z",
          "title": "Participatiewet"
        }
      ]
    },
    "cprmv_version": "0.3.0",
    "aggregations": {
      "norms_per_rulesetid": {
        "BWBR0015703": 1
      }
    },
    "rules": [
      {
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "https://cprmv.open-regels.nl/0.3.0/Rule",
        "https://cprmv.open-regels.nl/0.3.0/id": "onderdeel r.",
        "https://cprmv.open-regels.nl/0.3.0/definition": "inkomsten uit arbeid van een alleenstaande ouder ...",
        "https://cprmv.open-regels.nl/0.3.0/contains": {
          "onderdeel 1°.": {
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "https://cprmv.open-regels.nl/0.3.0/Rule",
            "https://cprmv.open-regels.nl/0.3.0/id": "onderdeel 1°.",
            "https://cprmv.open-regels.nl/0.3.0/definition": "hij de volledige zorg heeft voor een tot zijn last komend kind tot 12 jaar,"
          },
          "onderdeel 2°.": {
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "https://cprmv.open-regels.nl/0.3.0/Rule",
            "https://cprmv.open-regels.nl/0.3.0/id": "onderdeel 2°.",
            "https://cprmv.open-regels.nl/0.3.0/definition": "de periode van zes maanden, bedoeld in onderdeel n, is verstreken, en"
          }
        },
        "situatie": "inkomsten uit arbeid van een alleenstaande ouder ...",
        "norm": "173,87",
        "per": "maand, gedurende een aaneengesloten periode van maximaal 30 maanden, ...",
        "rulesetid": "BWBR0015703",
        "applicable_date": "2025-07-01",
        "rulesetid_index": 0,
        "rule_id_path": "BWBR0015703_2025-07-01_0, Artikel 31, lid 2, onderdeel r.",
        "rule_id_path_key": "BWBR0015703, Artikel 31, lid 2, onderdeel r."
      }
    ]
  },
  "timestamp": "2026-05-14T14:00:00.000Z"
}
```

!!! note "`contains` is not produced by the current editor"
    The nested-children shape above is materialised *only when* `cprmv:contains` triples are
    present in TriplyDB. Since CPSV editor v1.10.5 those are **not** emitted: nested
    sub-clauses (enumeration items such as *"onderdeel 1°./2°./3°."*) are **folded into the
    parent rule's `cprmv:definition`** on import rather than published as `cprmv:contains`
    children. The endpoint keeps the `OPTIONAL { ?rule cprmv:contains … }` branch for
    backward compatibility with any legacy data, but current acceptance/production responses
    are flat (the parent definition carries the full legal text). The `per` field is likewise
    only populated when a `cprmv:per` triple exists.

**Example requests:**

```
GET /v1/norms
GET /v1/norms?rulesetid=BWBR0015703
GET /v1/norms?applicable_date=2026-01-01
GET /v1/norms?rulesetid=BWBR0015703&applicable_date=2026-01-01
GET /v1/norms?cprmv_version=0.4.1
GET /v1/norms?cprmv_version=0.3.2&rulesetid=BWBR0015703
GET /v1/norms?endpoint=https://api.open-regels.triply.cc/datasets/stevengort/RONL/services/RONL/sparql
```

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

A separate `norms.service.ts` handles the `cprmv:Rule` publish-format query backing `/v1/norms`. It builds the query dynamically — filter clauses (rulesetid exact-match, applicable date `CONTAINS`) are injected only after upstream regex validation — then aggregates parent/child rows into nested objects with deterministic key ordering matching `cprmv-example.json`.

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