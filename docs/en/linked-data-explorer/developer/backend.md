---
component: Linked Data Explorer
---

# Backend Architecture

The backend is a Node.js/Express TypeScript API. It sits between the React frontend and two external services: TriplyDB (SPARQL knowledge graph) and Operaton (DMN execution engine). Its responsibilities are SPARQL querying, DMN chain orchestration, variable mapping between chain steps, and proxying dynamic TriplyDB endpoint calls.

---

## API versioning

| Environment | Base URL |
|---|---|
| Production | `https://backend.linkeddata.open-regels.nl/v1` |
| Acceptance | `https://acc.backend.linkeddata.open-regels.nl/v1` |

All endpoints follow `/v1/*`. The release version is included in every response via the `API-Version` header — `API-Version: 2026.09.6` on acceptance and `2026.09.5` on production at the time of writing, since the two environments can be a release apart — following Dutch Government API Design Rules API-20 and API-57.

**The contract is published.** `GET /v1/openapi.json` serves an OpenAPI 3.1 description of every `/v1` route, built from `packages/backend/openapi/openapi.yaml`. It is the reference for request and response shapes; the [API Specification](../reference/api-specification.md) page renders it. `/v1/openapi.json` is one of three public mounts served to any origin (see [Security](#security)), so any client can read it.

**Legacy `/api/*` aliases** still answer for backward compatibility, and carry a `Deprecation` header and a `Link` header naming the `/v1` successor. They are to be removed in v2.0.0.

**`GET /`**, outside `/v1`, returns API metadata and a directory of the current and legacy endpoint paths, including the `documentation` pointer to `/v1/openapi.json`.

---

## Endpoints

### Health

```
GET /v1/health
```

Returns service health: TriplyDB and Operaton latency checks, the SHACL shape layers the validator loaded, and **which build is running**. Used by the deploy workflows' post-deployment verification and by the frontend status indicator. Production's response on 19 September 2026:

```json
{
  "name": "Linked Data Explorer Backend",
  "version": "2026.09.5",
  "environment": "production",
  "build": {
    "sha": "ec4792f09c289f8fee6c68da5184fd775a27ccc9",
    "shortSha": "ec4792f",
    "run": "19",
    "isTracked": true,
    "label": "build ec4792f · #19"
  },
  "status": "healthy",
  "services": {
    "triplydb": { "status": "up", "latency": 98 },
    "operaton": { "status": "up", "latency": 105 }
  },
  "shacl": {
    "complete": true,
    "layers": {
      "cpsv-ap": { "label": "CPSV-AP 3.2.0", "loaded": true },
      "ronl-custom": { "label": "RONL Custom", "loaded": true },
      "cprmv": { "label": "CPRMV 0.4.1", "loaded": true }
    }
  },
  "documentation": "/v1/openapi.json"
}
```

`version` names the release; `build` names the commit and workflow run, read from the `deploy/build-info.json` the deploy workflow writes into the artifact. `build` is tracked only when both `sha` and `run` are present — a missing or malformed file reports a local build and never affects `status`.

`utils/buildInfo.ts` reads `build-info.json` **once, at module load**, the same moment `version` is bound from `package.json`, so the two cannot disagree: a stale process can only report the build it started with. The read is deliberately not lazy. A zip deploy overwrites `build-info.json` while the previous process is still serving and restarts it afterwards, so a read on first use let the old process report the new `build.sha` — a false pass in the deploy gate, seen on the v2026.09.6 production promotion, where `build.sha` showed the new commit while `version` still read 2026.09.5. Eager reading closes that since v2026.09.7. `/v1/openapi.json` stays lazy on purpose: it reads its document on the first request and caches it, but does not cache a failed read, so a document that is not built yet is retried and surfaces as a `500` rather than being remembered as broken.

The deploy workflows wait until `build.sha` equals the commit they deployed and `shacl.complete` is `true` before they pass; see [Post-deployment verification](deployment.md#post-deployment-verification).

### DMN deploy and evaluate (v2026.08.2)

```
POST /v1/dmns/deploy
POST /v1/dmns/evaluate/:decisionKey
```

Two routes added for the CPSV Editor's DMN tab, which used to call Operaton
directly from the browser — blocked by CORS for a local dev origin. The browser
posts here; the backend talks to Operaton server-to-server.

`deploy` takes raw DMN XML and requires no pre-registered norm identifier, so an
uploaded or generated file with no registry entry can still be deployed. It wraps
`operatonService.deployDrd()`.

`evaluate/:decisionKey` is a **raw passthrough**: it forwards Operaton's response
byte-for-byte and status-for-status — the success array or the exception object —
rather than the usual `{ success, data }` envelope, because the calling tab
reads Operaton's own JSON. `evaluateRaw()` also passes the request body through
untouched, skipping the type inference `evaluateDecision()` applies for its
different caller contract; the DMN tab already builds Operaton-shaped bodies, so
re-wrapping would double-wrap them.

Both are described in the [API Specification](../reference/api-specification.md).

### Deploy target (v2026.09.6)

```
GET /v1/dmns/process/deploy-target
```

Answers which Operaton the backend deploys BPMN processes to, as
`{ operatonUrl }`. The deploy modal and the exported README ask this route
instead of reading the frontend's build-time `VITE_OPERATON_BASE_URL`, which is
**removed** — a build-time copy of the target can drift from the backend's
configured `OPERATON_BASE_URL`, and only the backend's value decides where a
process actually lands. The frontend caches a successful answer for the session;
a failure is **not** cached, so the modal names the target as soon as the backend
is reachable again.

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

Executes the chain sequentially, flattening outputs into inputs between steps. Returns per-step results and combined final output. A chain that fails part-way answers with a problem-details error **and** keeps its partial result under `data`, so the steps that ran and their outputs are not lost.

```
POST /v1/dmns/drd/deploy
```

Assembles deployed DMNs into a single DRD and deploys it to Operaton. See [DRD Generation](drd-generation.md).

### eDOCS

```
GET  /v1/edocs/status
POST /v1/edocs/workspaces/ensure
POST /v1/edocs/documents
GET  /v1/edocs/workspaces/:workspaceId/documents
```

Integrates with the OpenText eDOCS document management system. Used by the RIP Phase 1 process to create project workspaces and file documents. In stub mode (`EDOCS_STUB_MODE=true`, default) all methods return realistic fake responses so the process runs end-to-end before a live eDOCS server is available.

See [eDOCS Integration](edocs-integration.md), and the [API Specification](../reference/api-specification.md) for request and response details.

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

Runs a SPARQL query against a caller-supplied endpoint. **Every query the frontend's Query Editor sends comes through here** — the editor no longer fetches endpoints from the browser, and its former `api.allorigins.win` fallback proxy is gone. The endpoint passes the [outbound guard](#outbound-guard) first: it must be `https:`, carry no credentials and resolve to a public address, or the route answers `400 INVALID_INPUT` before any request is made.

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

Persists BPMN processes, form schemas, and document templates to PostgreSQL. All routes return `503 DB_NOT_CONFIGURED` when `DATABASE_URL` is absent. The upserts, the deploy mark and the ROPA delete validate their input before it reaches Postgres and answer `400 INVALID_INPUT` with a detail naming every field that failed; the checks follow the database's own constraints, and a blank title, id or name is refused on the fields that identify a record. See [Asset Storage](asset-storage.md) for the service architecture and the [API Specification](../reference/api-specification.md) for request and response shapes.

---

## Database

The backend connects to a PostgreSQL database via a `pg.Pool`. The pool is initialised in `src/db/pool.ts` when `DATABASE_URL` is present in the environment. If the variable is absent, `pool` is `null` and all asset endpoints respond with `503`.

Schema migrations run automatically on startup via `migrate()` in `src/db/migrate.ts`, called from `startServer()` before `app.listen()`. The migration is idempotent (`CREATE TABLE IF NOT EXISTS`).
```
src/db/
├── pool.ts       — pg.Pool initialisation, error listener, null-if-unconfigured guard
└── migrate.ts    — idempotent DDL: process_definitions, form_schemas, document_templates
```

As of v1.9.9, `process_definitions` carries a `board_owner` column that records the owning board chosen (or auto-derived from candidate groups) at deploy time. It is set from the deployed BPMN's process-level `camunda:property boardOwner` and surfaced through `/bundles/public`, so downstream consumers (the ronl-business-api Procesbibliotheek and archive split) can group processes by board.

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

Every error the API produces itself is an **RFC 9457 problem details** response, `application/problem+json`:

```json
{
  "type": "about:blank",
  "title": "Bad Request",
  "status": 400,
  "detail": "…",
  "instance": "/v1/dmns",
  "code": "INVALID_INPUT"
}
```

`code` is an extension member and the field callers branch on — `INVALID_INPUT`, `MALFORMED_BODY`, `PAYLOAD_TOO_LARGE`, `DB_NOT_CONFIGURED` and so on. `type` is `about:blank`, because there is no documentation page per kind of problem and a URL that does not resolve would be worse than none. `instance` is the request path without its query string. Success responses are unchanged and keep `{ success: true, data }`.

This replaced five different envelopes in v2026.09.5. `POST /v1/dmns/evaluate/:decisionKey` is the one exception: it passes Operaton's own errors through unchanged, because its caller reads Operaton's JSON.

`middleware/error.middleware.ts` is the central handler. It answers a body that does not parse with **400 `MALFORMED_BODY`**, a body over the 10 MB limit with **413 `PAYLOAD_TOO_LARGE`** naming that limit, and other body-parser failures with the parser's own status as `INVALID_BODY` — recognising parser errors by type, so an arbitrary thrown error carrying a `status` property still answers 500 rather than choosing its own response. Stack traces and internal context never reach the client.

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

### Caching — one utility, a named registry

Since v2026.09.6 the hand-rolled caches are replaced by one TTL utility
(`utils/ttl-cache.ts`) whose instances **register themselves by name**. The cache
routes therefore report and clear across every cache rather than a hardcoded
list:

| Route | Does |
|---|---|
| `GET /v1/cache/stats` | Cache age and entry count, per named cache. Expired entries are not counted |
| `DELETE /v1/cache/clear` | Clears every registered cache |

| Cache | TTL | Why |
|---|---|---|
| `dso-activiteit` | 5 minutes | Activity detail is the hottest DSO read — the DSO Explorer's child-activity fan-out calls it once per child and discards the names on every re-render |
| DMN caches | 5 minutes | The existing per-endpoint SPARQL discovery caches |

Entries that are never read again are now evicted rather than retained for the
process lifetime; before v2026.09.6 an 8.7 MB annotation graph per municipality
could sit in memory indefinitely. DSO activity data does change, so the staleness
a five-minute TTL admits is deliberate and `DELETE /v1/cache/clear` is the escape
hatch.

The frontend keeps a separate, smaller cache for the activity dossier, keyed
`env|datum|urn`. It stores the **promise** rather than the resolved value, so
concurrent calls for one key dedupe, and it evicts on failure so one bad response
cannot permanently block a retry.

---

## Security

**HTTP headers** — [Helmet](https://helmetjs.github.io/) is configured to set comprehensive security headers on all responses, including `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`, and `Strict-Transport-Security`.

**CORS** — only origins listed in `CORS_ORIGIN` are permitted. In production this is restricted to `https://linkeddata.open-regels.nl` and `https://cpsv.open-regels.nl`; acceptance also admits both tiers of the IOU architecture documentation site. Any other origin gets an ordinary response with no `Access-Control-Allow-Origin` header, which the browser then refuses — **except on the three public read-only mounts**, `/v1/ropa/public`, `/v1/bundles/public` and `/v1/openapi.json`, which answer any origin for `GET` and `OPTIONS` by design. `isPublicPath` matches those mounts or a path below them, never a sibling route that shares the prefix; see [RoPA Records — the public routes](ropa-records.md#public-route-v1ropapublic).

**Input validation** — request inputs are checked before any service call, and a failure answers `400 INVALID_INPUT` naming the fields at fault rather than surfacing as a 500 from a downstream system. Request body size is limited to 10 MB.

<a id="outbound-guard"></a>**Outbound guard** — the backend never requests a host a caller named without checking it (v2026.09.5, [#142](https://github.com/sgort/linked-data-explorer/issues/142)). There are two layers:

- **At the route**, `utils/outboundUrl.ts` checks every caller-supplied SPARQL endpoint — on `GET /norms`, the DMN reads, chain execution, the vendor reads, merged SHACL validation and `POST /triplydb/query` — and refuses it with `400 INVALID_INPUT` when it is not `https:`, carries credentials, or points to an internal address. Internal addresses are recognised in every textual IPv4 and IPv6 form, including IPv6 forms that embed an IPv4 address.
- **At connect time**, `utils/outboundHttp.ts` provides the axios client every caller-chosen request uses. Its agents refuse a name that *resolves* to an internal address, redirects are re-checked, and it pins `proxy: false`, because axios otherwise honours `HTTP(S)_PROXY` with a tunnelling agent that skips the lookup.

The connect-time layer was finished in v2026.09.6: the client now pins the http adapter and HTTP/1 on **every** request rather than relying on the default, and a refused redirect surfaces as `EOUTBOUNDREFUSED` instead of a generic connection error. The unreachable `::/128` and `::1/128` entries were dropped from the internal-address list, `test-connection` gained its own request schema with `apiToken` optional, and the credential-leak test now searches the whole call rather than part of it.

TriplyDB calls that forward the caller's token go only to `https:` hosts in `TRIPLYDB_ALLOWED_HOSTS`. Processes deploy only to the configured Operaton, through the shared client that carries `OPERATON_API_KEY` — a request can no longer name the Operaton URL or supply credentials. `ALLOW_LOCAL_ENDPOINTS=true` admits `http:` and local addresses for local development, and is never set on ACC or production.

**CSP reports** — `POST /v1/csp-reports` receives the frontend's Content-Security-Policy violation reports in both formats (`application/csp-report` and `application/reports+json`, up to 64 KB) and logs one warning line per violation. It stores nothing.

**Environment variables** — all sensitive configuration (TriplyDB endpoint URLs, Operaton API URLs, CORS origins, eDOCS credentials) is stored in environment variables and never hardcoded. eDOCS-specific variables: `EDOCS_BASE_URL`, `EDOCS_LIBRARY`, `EDOCS_USER_ID`, `EDOCS_PASSWORD`, `EDOCS_STUB_MODE`.

**Error responses** — the central error handler scrubs stack traces and internal context before returning responses to clients, ensuring no implementation details are exposed.

---

## Dutch Government API Design Rules compliance

The API follows the [Dutch Government API Design Rules](https://publicatie.centrumvoorstandaarden.nl/api/adr/) for interoperability and standardisation.

**Implemented rules:**

| Rule   | Description                 | Implementation                         |
| ------ | --------------------------- | -------------------------------------- |
| API-20 | Major version in URI        | `/v1/*` endpoints                      |
| API-57 | Version header in responses | `API-Version: <release>` on every response |
| API-16 | Use OpenAPI for documentation | OpenAPI 3.1 description (v2026.09.5) |
| API-51 | Publish the OpenAPI document at a standard location | `/v1/openapi.json` (v2026.09.5) |
| API-05 | Use nouns for resources     | `dmns`, `chains`, `health`             |
| API-54 | Plural/singular naming      | Correct usage throughout               |
| API-48 | No trailing slashes         | Enforced in routing                    |
| API-53 | Hide implementation details | Clean service abstractions             |

**Language note (API-04)** — technical endpoint names (`health`, `version`) follow international convention in English. Business resource names (`dmns`, `chains`) follow the source data. Dutch variable names (e.g., `geboortedatum`) are preserved as-is from the DMN definitions.

**Checked in CI.** `npm run lint:openapi` lints the published description with Spectral against the NL API Design Rules 2.2.1 in both backend deploy workflows. Errors follow the rules' problem-details requirements (`nlgov:problem-*`). Where the API departs from a rule, the exception is recorded per path in `openapi/.spectral.yaml` rather than switched off globally.
| API-10         | Resource collections with pagination   | v1.0.0         |