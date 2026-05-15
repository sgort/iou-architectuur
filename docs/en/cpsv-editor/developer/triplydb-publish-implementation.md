# TriplyDB Publish Implementation

---

## Architecture

```
User clicks Publish
        ↓
PublishDialog.jsx opens
        ↓
User enters credentials → optional Test Connection
        ↓
handlePublish() in App.js:
    10%  — Validate form
    30%  — Generate TTL (ttlGenerator.js)
    50%  — Compute graph IRI (buildGraphIRI)
    50%  — Upload TTL to TriplyDB targeting that graph
    85%  — Notify backend to re-sync service (graphName included)
   100%  — Show result + auto-close
        ↓
publishToTriplyDB() in triplydbHelper.js:
    PUT  /datasets/{account}/{dataset}/assets             (logo, if present)
    POST /datasets/{account}/{dataset}/jobs               (TTL data,
                       ?defaultGraphName=<URL-encoded IRI>)
        ↓
updateTriplyDBService() in triplydbHelper.js:
    POST {backendUrl}/v1/triplydb/update-service
    body: { config, serviceName, graphName }
```

---

## Files

```
src/
├── App.js                      # handlePublish() with progress state management
├── components/
│   └── PublishDialog.jsx       # Dialog UI: form, progress, success/error states
└── utils/
    ├── triplydbHelper.js       # TriplyDB API integration, buildGraphIRI
    └── dmnHelpers.js           # sanitizeServiceIdentifier (used by buildGraphIRI)
```

---

## API functions

### `buildGraphIRI({ organizationIdentifier, serviceIdentifier })`

Computes the deterministic graph IRI for a publish.

```javascript
const graphIRI = buildGraphIRI({
  organizationIdentifier: organization.identifier,
  serviceIdentifier: service.identifier,
});
// → 'https://regels.overheid.nl/graphs/Sociale_Verzekeringsbank/aow-leeftijd'
```

**Parameters:**

- `organizationIdentifier` — Full URI (e.g. `https://organisaties.overheid.nl/28212263/Sociale_Verzekeringsbank`) or local identifier. The helper extracts the last path segment as the local org name.
- `serviceIdentifier` — Service identifier (e.g. `aow-leeftijd`). Sanitised via `sanitizeServiceIdentifier` from `dmnHelpers.js`.

**Fallback:** Returns `https://regels.overheid.nl/graphs/default` when either argument is missing. The editor's publish form requires both fields, so the fallback is defensive only.

### `publishToTriplyDB(ttlContent, config, filename, graphIRI)`

Uploads TTL content to TriplyDB, targeting a specific graph.

```javascript
const result = await publishToTriplyDB(
  ttlContent,
  config,
  filename,
  graphIRI,
);
// Returns: { success: true, message: "Published successfully! View at: ...", url: "..." }
```

**Parameters:**

- `ttlContent` — Generated Turtle string
- `config.baseUrl` — TriplyDB API base URL
- `config.account` — Account/organisation name
- `config.dataset` — Target dataset name
- `config.apiToken` — API token (transmitted via Authorization header over HTTPS only)
- `filename` — Filename for the upload job (e.g. `aow-leeftijd.ttl`)
- `graphIRI` — Target graph IRI from `buildGraphIRI`; defaults to `https://regels.overheid.nl/graphs/default`

**Network:** A single POST to the TriplyDB jobs endpoint with `defaultGraphName=<URL-encoded IRI>` in the query string. The dataset must already exist; create it manually in TriplyDB before first use. A `publishToTriplyDB_SPARQL` variant exists for SPARQL UPDATE flows and accepts the same `graphIRI` parameter with the same default.

### `updateTriplyDBService(config, serviceName, graphName)`

Notifies the LDE backend to re-sync the dataset's SPARQL service after a publish.

```javascript
await updateTriplyDBService(config, config.dataset, graphIRI);
```

**Parameters:**

- `config` — Same shape as for `publishToTriplyDB`
- `serviceName` — Target service to sync (defaults to `config.dataset`)
- `graphName` — IRI of the graph that just received data; logged by the backend as `triggeredByGraph` for traceability

The TriplyDB sync API the backend wraps (`POST /datasets/{account}/{dataset}/services/{serviceName}` with body `{"sync":"true"}`) has no graph-scoping mechanism — `graphName` is observability metadata only. The sync re-indexes all graphs the service is configured for.

### `testTriplyDBConnection(config)`

Verifies credentials without uploading data.

```javascript
const result = await testTriplyDBConnection(config);
// Returns: { success: true, message: "Successfully connected to TriplyDB" }
```

---

## Token storage

The API token is stored in `localStorage` under a namespaced key. It is read when the dialog opens and cleared when the user explicitly removes it. It is transmitted only to the configured TriplyDB base URL over HTTPS — never logged or sent elsewhere.

---

## Graph naming

Each publish writes the TTL to a graph whose IRI is computed deterministically from the organisation and service identifiers:

```
https://regels.overheid.nl/graphs/{org-local}/{service-id}
```

For example, publishing the SVB AOW-leeftijd service yields:

```
https://regels.overheid.nl/graphs/Sociale_Verzekeringsbank/aow-leeftijd
```

The IRI is computed by `buildGraphIRI` and passed to `publishToTriplyDB` from `handlePublish` in `App.js`. The same IRI is forwarded to the backend as the `graphName` field on `/v1/triplydb/update-service`, where it surfaces in logs as `triggeredByGraph`.

**Effect on republishing.** Because the graph IRI is deterministic, republishing the same service overwrites the previous graph rather than creating an incremented `graph:default-N`. The TriplyDB UI shows one graph per service, named after the service.

**Effect on multi-service datasets.** A single TriplyDB dataset (e.g. `DMN-discovery`) can host many services, each in its own graph. The dataset's SPARQL service spans all of them, so cross-service queries continue to work without additional configuration.

**Legacy graphs.** Services published before the `buildGraphIRI` feature were all written to the auto-numbered `graph:default-N` series. These are harmless but can be removed manually from the TriplyDB UI when convenient.

---

## Backend proxy

The proxy endpoint is `{backendUrl}/v1/triplydb/update-service`. Request body:

```json
{
  "config": {
    "baseUrl": "https://api.open-regels.triply.cc",
    "account": "stevengort",
    "dataset": "DMN-discovery",
    "apiToken": "..."
  },
  "serviceName": "DMN-discovery",
  "graphName": "https://regels.overheid.nl/graphs/Sociale_Verzekeringsbank/aow-leeftijd"
}
```

`graphName` is the IRI just written to. The backend logs it for traceability and echoes it in the response when supplied. The actual TriplyDB sync re-indexes all graphs the service spans.

If the proxy is unavailable, the upload still succeeds. A warning is shown: "Service update failed — data is accessible in TriplyDB but the SPARQL endpoint may not reflect the latest state." The proxy is optional; the upload itself does not depend on it.

---

## Backend proxy deployment checklist

- [ ] Deploy Node.js backend (linked-data-explorer repository)
- [ ] Set `TRIPLYDB_TOKEN` environment variable
- [ ] Configure CORS to allow the editor's domain
- [ ] Verify: `curl {backendUrl}/v1/triplydb/health` returns 200
- [ ] Verify TriplyDB connectivity from the backend host