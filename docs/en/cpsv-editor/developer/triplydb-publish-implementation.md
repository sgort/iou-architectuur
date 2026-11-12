---
component: CPSV Editor
---

# TriplyDB Publish Implementation

Since v2026.11.1 the editor never writes to TriplyDB itself and never holds a TriplyDB
token. It sends the signed-in author's token and the dataset name to the Linked Data
Explorer backend, which holds the TriplyDB instance, account and token and does the
writing ([ttl-editor#234](https://github.com/sgort/ttl-editor/issues/234)).

---

## Architecture

```
User clicks Publish   (a LockedAction: disabled without lde-author)
        ↓
PublishDialog.jsx opens
        ↓
On open: validateTtl(ttlContent) → POST /v1/shacl/validate   (advisory, non-blocking)
        ↓
User checks the dataset name → optional Test Connection
        → POST {backendUrl}/v1/triplydb/test-connection   (author's token)
        ↓
handlePublish() in App.jsx:
    10%  — Validate form
    30%  — Generate TTL (ttlGenerator.js)
           Compute graph IRI (buildGraphIRI); collect logos as data URLs
    60%  — publishToTriplyDB(): one call to the backend
   100%  — Show result (success, or warning when only the service sync failed)
        ↓
publishToTriplyDB() in triplydbHelper.js:
    POST {backendUrl}/v1/triplydb/publish
         Authorization: Bearer <author's token>
         { dataset, graph, filename, ttl, organization, service, logos[] }
        ↓
LDE backend (requireAuthor, requirePublishTarget):
    upload the TTL into the graph → upload each logo as an asset
    → sync the dataset's service → log who published what, and the outcome
```

---

## Files

```
src/
├── App.jsx                     # handlePublish() with progress state management
├── components/
│   ├── LockedAction.jsx        # The Publish button: locked without lde-author
│   └── PublishDialog.jsx       # Dialog UI: dataset name, progress, result, SHACL panel
├── hooks/
│   └── useEditorState.js       # triplyDBConfig ({ dataset }); publish target for the picker
└── utils/
    ├── auth.js                 # authHeaders(): the author's bearer token
    ├── triplydbHelper.js       # Backend calls, buildGraphIRI, the stored dataset name
    ├── shaclHelper.js          # validateTtl — advisory pre-publish SHACL validation
    └── dmnHelpers.js           # sanitizeServiceIdentifier (used by buildGraphIRI)
```

---

## Pre-publish SHACL validation

When the dialog opens (and via a **Validate now** button), `PublishDialog` calls
`validateTtl(ttlContent)` from `src/utils/shaclHelper.js`, which POSTs the generated Turtle
to `VITE_BACKEND_URL/v1/shacl/validate` and returns a layered result
(`{ valid, parseError, layers: { cprmv, 'cpsv-ap', 'ronl-custom' }, summary, unavailable? }`).

It mirrors `DMNTab.runBackendValidation`: it **never throws**. An unreachable backend yields a
neutral `{ unavailable: true }` shape and the panel shows a distinct amber state. The check is
**advisory only** — it never blocks `handlePublish`. Because it validates the editor's
*regenerated* output, an imported legacy file that fails on its own may pass here (import
normalises to CPRMV 0.4.1 / CPSV-AP 3.2.0).

---

## API functions

`triplydbHelper.js` exports seven functions.

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

**Fallback:** Returns `https://regels.overheid.nl/graphs/default` when the service identifier is missing, and `…/graphs/{service-id}` without an organisation. The editor's publish form requires both fields, so the fallbacks are defensive only. The backend accepts only a graph under `https://regels.overheid.nl/graphs/`.

### `publishToTriplyDB(publish)`

Publishes a service description as the signed-in author, in one call.

```javascript
const result = await publishToTriplyDB({
  dataset: config.dataset,
  graph: graphIRI,
  filename,
  ttl: ttlContent,
  organization: organization.identifier,
  service: service.identifier,
  logos, // [{ fileName: 'Org_logo.png', dataUrl: 'data:image/png;base64,…' }]
});
// → { url, graph, serviceUpdated, serviceError?, logos: [{ fileName, ok }] }
```

It sends `POST {backendUrl}/v1/triplydb/publish` with the author's bearer token from
`authHeaders()` in `src/utils/auth.js`. The backend checks the input — a dataset name of 1
to 40 letters, digits and hyphens, a graph under `https://regels.overheid.nl/graphs/`, a
file name, non-empty Turtle, and logos with a plain file name and an image data URL —
then uploads the Turtle into the graph, uploads each logo as an asset, and syncs the
dataset's service. A failed logo is reported in `logos` with `ok: false` and does not fail
the publish; a failed service sync is reported as `serviceUpdated: false` with
`serviceError`, and the editor shows it as a warning.

Errors thrown, for the dialog to show:

- 401 or 403 — *Sign in as an author to publish.*
- any other failure — the backend's RFC 9457 `detail` (for example *Publishing is not configured on this backend*, a 503), or *Publishing failed: HTTP {status}*
- no connection — *Network error: Could not connect to backend.*

### `fetchPublishTarget()`

`GET {backendUrl}/v1/triplydb/publish-target` — the non-secret part of where the backend
publishes, `{ baseUrl, account }`, never the token. `useEditorState` calls it once on mount;
the Service tab's required-services picker combines it with the dataset name to build its
SPARQL URL. It answers `null` when publishing is not configured on the backend, the backend
cannot be reached, or the answer lacks either field — and the picker then shows as
unconfigured.

### `testTriplyDBConnection(config)`

Checks, through the backend and as the signed-in author, that the dataset exists in the
publishing account: `POST {backendUrl}/v1/triplydb/test-connection` with `{ dataset }`. An
invalid name is refused without a request. It answers
`{ success: true, message: 'Dataset … is available' }`, or `success: false` with an error for
a 404 (*Dataset not found*), a 401 or 403 (*Sign in as an author to check the dataset.*), any
other status, or a network failure.

### `validateTriplyDBConfig`, `loadTriplyDBConfig`, `saveTriplyDBConfig`

`validateTriplyDBConfig` checks the dataset name, the only TriplyDB setting the user keeps.
`loadTriplyDBConfig` and `saveTriplyDBConfig` read and write it in `localStorage`; see the next
section.

---

## What the browser keeps

The key `triplydb_config` in `localStorage` holds `{ dataset }` and nothing else, defaulting to
`DMN-discovery`. `saveTriplyDBConfig` writes only the dataset, and `App.jsx` saves it only after
a publish succeeds. Versions before v2026.11.1 stored a base URL, an account and an API token
under the same key: `loadTriplyDBConfig` reduces such a value to `{ dataset }` and writes it
back, so the old token leaves the browser the first time the current version loads.

The sign-in session itself is held by `keycloak-js` in memory. The only sign-in state in
`localStorage` is a flag, `ttl.auth.wasSignedIn`, that makes the next page load restore the
session with a silent check.

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

The IRI is computed by `buildGraphIRI` in `handlePublish` and sent as `graph` in the publish call. The backend uploads the Turtle into that graph and names it when it syncs the dataset's service, and its publish log line records it.

**Effect on republishing.** Because the graph IRI is deterministic, republishing the same service overwrites the previous graph rather than creating an incremented `graph:default-N`. The TriplyDB UI shows one graph per service, named after the service.

**Effect on multi-service datasets.** A single TriplyDB dataset (e.g. `DMN-discovery`) can host many services, each in its own graph. The dataset's SPARQL service spans all of them, so cross-service queries continue to work without additional configuration.

**Legacy graphs.** Services published before the `buildGraphIRI` feature were all written to the auto-numbered `graph:default-N` series. These are harmless but can be removed manually from the TriplyDB UI when convenient.

---

## The backend's publish route

`POST /v1/triplydb/publish` in the Linked Data Explorer backend
(`packages/backend/src/routes/triplydb.routes.ts`) is guarded twice: `requireAuthor` accepts
only a Keycloak token carrying the realm role `lde-author`, and `requirePublishTarget`
answers 503 when the backend has no TriplyDB account configured. The TriplyDB token is the
server's; the caller never sends or sees one.

Every attempt writes one log line, `triplydb.publish`, with the user, the organisation and
service, the graph and dataset, and the outcome: `published`, `published-with-warning` or
`failed`. That records who published what; it is a log line, not an audit store with a
retention period.

The service sync wraps TriplyDB's `POST /datasets/{account}/{dataset}/services/{serviceName}`
with `{"sync":"true"}`, which re-indexes all graphs the service spans; the graph IRI is
observability metadata there, not a scope. If the sync fails, the upload still stands, and
the editor shows *Published with warning* with the reason.

The same backend also serves `update-service`, `list-graphs` and `test-connection`, all with
`lde-author` and its own token. A `config` an older client still sends with a base URL,
account or token is ignored: only its dataset name is read.

---

## Backend deployment checklist

- [ ] Deploy the Node.js backend (linked-data-explorer repository)
- [ ] Set `TRIPLYDB_BASE_URL`, `TRIPLYDB_ACCOUNT` and `TRIPLYDB_API_TOKEN`; without an account and token the publish routes answer 503
- [ ] Set the Keycloak realm the backend verifies tokens against, and keep `ttl-editor` in `AUTH_CLIENTS` (the default is `linked-data-explorer,ttl-editor,lde-e2e`)
- [ ] Give the authors the realm role `lde-author`
- [ ] Configure CORS to allow the editor's domain
- [ ] Verify: `curl {backendUrl}/v1/triplydb/publish-target` returns the base URL and account
- [ ] Verify TriplyDB connectivity from the backend host