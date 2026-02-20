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
GET /v1/dmns/chains?endpoint={url}
```

Returns all DMN pairs where an output variable of one model matches an input variable of another by exact identifier.

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
POST /v1/chains/export
```

Generates a DRD XML file from a chain for deployment. See [DRD Generation](drd-generation.md).

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

## Logging

Winston structured logging with JSON output. All service calls log at `[INFO]` level with context (endpoint, query length, result count, latency). Errors log at `[ERROR]` with stack traces. Log level is configurable via `LOG_LEVEL` environment variable.

---

## Error handling

A central `errorHandler.ts` middleware catches unhandled errors and returns standardised JSON error responses with appropriate HTTP status codes. SPARQL and Operaton errors are wrapped with descriptive messages before being returned to the frontend.
