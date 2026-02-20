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
    50%  — Upload to TriplyDB (triplydbHelper.js)
    85%  — Update service via backend proxy
   100%  — Show result + auto-close
        ↓
publishToTriplyDB() in triplydbHelper.js:
    PUT /datasets/{account}/{dataset}/assets (logo, if present)
    POST /datasets/{account}/{dataset}/graphs (TTL data)
        ↓
updateServiceViaProxy() (optional backend proxy):
    POST {backendUrl}/v1/services/update
```

---

## Files

```
src/
├── App.js                     # handlePublish() with progress state management
├── components/
│   └── PublishDialog.jsx       # Dialog UI: form, progress, success/error states
└── utils/
    └── triplydbHelper.js       # TriplyDB API integration
```

---

## API functions

### `publishToTriplyDB(config, ttlContent, logoData?)`

Uploads TTL content (and optionally a logo asset) to TriplyDB.

```javascript
const result = await publishToTriplyDB(config, ttlContent, logoData);
// Returns: { success: true, message: "Published successfully! View at: ...", url: "..." }
```

**Parameters:**

- `config.baseUrl` — TriplyDB API base URL
- `config.account` — Account/organisation name
- `config.dataset` — Target dataset name
- `config.token` — API token (transmitted via Authorization header over HTTPS only)
- `ttlContent` — Generated Turtle string
- `logoData` — Optional base64-encoded logo with filename

**Network:** Retries up to 3 times on transient failures.

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

## Graph accumulation

TriplyDB auto-numbers graphs on each upload (graph1, graph2, ...). Direct SPARQL UPDATE and HTTP PUT approaches to accumulate into a single graph both return 403 or 405. The current solution is a backend proxy that queries all graphs and presents a unified view.

The proxy endpoint: `{backendUrl}/v1/services/update`

If the proxy is unavailable, the upload still succeeds. A warning is shown: "Service update failed — data is accessible in TriplyDB but the SPARQL endpoint may not reflect the latest state." The proxy is optional; the upload itself does not depend on it.

---

## Backend proxy deployment checklist

- [ ] Deploy Node.js backend (linked-data-explorer repository)
- [ ] Set `TRIPLYDB_TOKEN` environment variable
- [ ] Configure CORS to allow the editor's domain
- [ ] Verify: `curl {backendUrl}/v1/health` returns 200
- [ ] Verify TriplyDB connectivity from the backend host
