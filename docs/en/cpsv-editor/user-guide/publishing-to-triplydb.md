---
component: CPSV Editor
---

# Publishing to TriplyDB

---

## Before you publish

Ensure:

- You are signed in with an account that has the `lde-author` role — see [Signing in](getting-started.md#signing-in). Without it the **Publish** button is locked, with *Sign in to publish* or *You need permission to publish* beside it
- The service identifier is filled in (it is used to construct the graph IRI)
- The **Validate** button shows no errors
- The **CPRMV version selector** (`0.4.1` / `0.3.2`) is set to the version your consumer expects — it drives the published Turtle just as it drives the preview and download (v1.10.5). See [CPRMV vocabulary version](../features/import-export.md#cprmv-vocabulary-version-041-032).

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Publish modal with the pre-publish SHACL panel, the note that you publish as yourself, and the Dataset Name field](../../assets/screenshots/cpsv-editor-publish-dialog.png)
  <figcaption>The TriplyDB publish dialog</figcaption>
</figure>

---

## Publishing

1. Click the **Publish** button in the bottom-right of the application (purple).
2. Review the **Pre-publish SHACL validation** panel at the top of the dialog. It validates the Turtle that will actually be published against the CPRMV 0.4.1 / CPSV-AP 3.2.0 / RONL shapes. This is advisory — a non-conformant result (or an unreachable validation backend, shown in amber) does **not** stop you from publishing. Click **Validate now** to re-run it.
3. Check the **Dataset Name**: the dataset to publish into, `DMN-discovery` unless you chose another before. A name is 1 to 40 letters, digits and hyphens. There is nothing else to fill in — the backend holds the TriplyDB instance, the account and the token.
4. Optionally click **Test Connection** to check, through the backend, that the dataset exists.
5. Click **Publish to TriplyDB**.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Publish dialog in "publishing" state showing the progress bar, four step indicators (Validating, Generating TTL, Uploading, Updating service) with the first three showing ✓ and the fourth showing a spinner](../../assets/screenshots/cpsv-editor-publish-progress.png)
  <figcaption>Publish dialog in "publishing" state showing the progress bar, four step indicators (Validating, Generating TTL, Uploading to TriplyDB, Updating service)</figcaption>
</figure>

---

## Progress tracking

The dialog lists four steps:

1. Validating form
2. Generating TTL
3. Uploading to TriplyDB
4. Updating service

Since v2026.11.1 the last two happen inside one call to the backend. The editor validates the form and generates the Turtle, then shows **Publishing to TriplyDB...** while the backend uploads the Turtle and any logos and syncs the dataset's service. The indicators for that call do not follow it yet: *Uploading to TriplyDB* shows a tick as soon as the call starts, and *Updating service* never gets one.

On success, a direct link to the published dataset appears and the dialog closes automatically after two seconds. A green message with the dataset URL appears under the page title and auto-dismisses after ten seconds.

If the Turtle reached TriplyDB but the dataset's service could not be synced, the dialog ends in an orange **Published with warning** with the reason, and closes after three seconds; the message under the page title says the same. The data is in TriplyDB — only the dataset's SPARQL service may lag behind it.

---

## Error handling

Errors are displayed inside the dialog with details. The dialog closes after five seconds and an inline red message appears under the page title. Common causes:

- *Sign in as an author to publish.* — the session has run out, or the account lacks `lde-author`.
- A dataset that does not exist in the publishing account. **Test Connection** says so before you publish: *Dataset not found. Please check the dataset name.*
- *Publishing is not configured on this backend* — the backend has no TriplyDB account set.
- *Network error: Could not connect to backend.*

---

## Who can publish

You publish as yourself. The editor sends your sign-in token, never a TriplyDB token: the Linked Data Explorer backend holds the TriplyDB account and token, accepts a publish only from an account with the `lde-author` role, and writes a log line for every attempt — who, which organisation and service, which graph and dataset, and the outcome.

The only TriplyDB setting the browser keeps is the dataset name. Versions before v2026.11.1 stored a base URL, an account and an API token in `localStorage`; the token is removed the first time the current version loads.

The role says that you may publish, not on whose behalf: an author can publish a description for any organisation into any dataset of the backend's TriplyDB account.

---

## Per-service graphs

Each service is published to its own stable named graph (`…/graphs/{org-local}/{service-id}`). Republishing the same service **overwrites** that graph, so it always holds the latest version — no auto-numbered duplicates accumulate. Different services live in separate graphs within the same dataset, and the backend's unified SPARQL endpoint reflects the current state across all of them.
