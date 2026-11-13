---
component: CPSV Editor
---

# TriplyDB Publishing

The editor can publish service metadata directly to a TriplyDB knowledge graph without any manual file handling. The publish feature is available via the **Publish** button in the bottom-right of the application. It needs a signed-in account with the `lde-author` role; without one the button is locked.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: The publish dialog for an imported service: the pre-publish SHACL panel reporting 2 errors and 0 warnings, with the remark that you can still publish; the note that you publish as yourself; the Dataset Name field set to RONL; Test Connection, answered by Dataset RONL is available; and Publish to TriplyDB](../../assets/screenshots/cpsv-editor-publish-dialog.png)
  <figcaption>The TriplyDB publish dialog: the SHACL check found two errors, and Publish to TriplyDB stays available</figcaption>
</figure>

---

## What publishing does

When you publish, the editor generates the complete Turtle output for the current service definition and sends it, with the dataset name and your sign-in token, to the Linked Data Explorer backend's `POST /v1/triplydb/publish`. The backend uploads it to TriplyDB with its own account and token (v2026.11.1). Each service is written to its own deterministic, per-service named graph at `https://regels.overheid.nl/graphs/{org-local}/{service-id}` (v1.9.4), derived by `buildGraphIRI()` from the organisation and service identifiers. Republishing the same service overwrites that graph rather than creating an auto-numbered copy, so each service corresponds to a single, stable graph IRI; different services accumulate side by side in the dataset.

Organisation logos (and vendor logos), when present, travel in the same call, and the backend uploads them as named assets alongside the Turtle data, making them available as linked resources in the knowledge graph.

The published Turtle honours the **CPRMV version selector** (`0.4.1` / `0.3.2`) — the same selection that drives the live preview and **Download TTL** — so you can publish data shaped for a `0.3.x` consumer as well as the default `0.4.1`. See [CPRMV vocabulary version](import-export.md#cprmv-vocabulary-version-041-032) for how the two targets differ (v1.10.5).

---

## Pre-publish SHACL validation (advisory)

When the publish dialog opens it runs the generated Turtle through the shared backend's SHACL validator (`POST /v1/shacl/validate`, `src/utils/shaclHelper.js`) and shows a layered **CPRMV 0.4.1 / CPSV-AP 3.2.0 / RONL Custom** result panel with per-layer issues. A **Validate now** button re-runs the check.

The check is **purely advisory and never blocks publishing**. It validates the Turtle that will *actually* be published — the editor's current, regenerated output — which can differ from an originally-imported file, because import normalises legacy CPRMV/CPSV-AP terms to the CPRMV 0.4.1 / CPSV-AP 3.2.0 vocabulary. An imported file that fails validation on its own may therefore still publish as conformant here (v1.10.0–v1.10.1).

If the validation backend is unreachable, the panel shows a distinct amber "result not available" state and publishing continues unaffected.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: The publish dialog's "Pre-publish SHACL validation" panel showing a green "Conformant — 0 violations" result with the CPRMV/CPSV-AP/RONL layers, the "Validate now" button, and the explanatory note about regenerated output](../../assets/screenshots/cpsv-editor-publish-shacl-validation.png)
  <figcaption>The advisory pre-publish SHACL validation panel in the publish dialog</figcaption>
</figure>

---

## Progress tracking

The publish dialog lists four steps:

1. Validating form
2. Generating TTL
3. Uploading to TriplyDB
4. Updating service

The editor does the first two itself. The last two happen inside the one call to the backend, which uploads the Turtle and the logos and then syncs the dataset's SPARQL service; while it runs the dialog shows **Publishing to TriplyDB...**, and the indicators for those two steps do not follow it. When the upload succeeds but the service sync fails, the result is a warning, not an error: the data is in TriplyDB. On success, the dialog displays a direct link to the published dataset and closes automatically after two seconds. Errors are surfaced inside the dialog with details, and an inline message appears under the page title after the dialog closes.

---

## Configuration

Publishing needs two things: a signed-in account with the `lde-author` role, and a dataset name — 1 to 40 letters, digits and hyphens, `DMN-discovery` by default. The dataset name is the only TriplyDB setting the editor keeps, in browser `localStorage`. The TriplyDB instance, account and token belong to the Linked Data Explorer backend, which publishes with them on the author's behalf and logs every attempt. Before v2026.11.1 the user entered a base URL, an account and an API token here, and the token was kept in the browser; the current version removes such a token the first time it loads.

The Service tab's **Required services** picker lists the public services already published to the same dataset. It takes the base URL and account from the backend's `GET /v1/triplydb/publish-target`, which never returns the token, and queries through the backend's SPARQL proxy without credentials, so a private dataset lists nothing there and a URI has to be pasted instead. When the backend has no publish target, the picker shows as unconfigured.

An optional **Test Connection** button checks, through the backend, that the dataset exists in the publishing account, without uploading any data.

---

## Per-service graphs

TriplyDB's default behaviour creates auto-numbered graphs on each upload. The editor avoids this by writing each service to a deterministic, per-service named graph (`buildGraphIRI()` → `…/graphs/{org-local}/{service-id}`). Republishing a service overwrites its own graph, so it always has exactly one current version, while distinct services coexist in the dataset. The graph IRI travels with the publish call, and the backend names it when it syncs the dataset's SPARQL service, so the cumulative service stays in sync across multi-publish flows.
