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
  ![Screenshot: The publish dialog for an imported service: the pre-publish SHACL panel reporting 2 errors and 0 warnings, with the remark that you can still publish; the note that you publish as yourself; the Dataset Name field set to RONL; Test Connection, answered by Dataset RONL is available; and Publish to TriplyDB](../../assets/screenshots/cpsv-editor-publish-dialog.png)
  <figcaption>The TriplyDB publish dialog: the SHACL check found two errors, and Publish to TriplyDB stays available</figcaption>
</figure>

---

## Publishing

1. Click the **Publish** button in the bottom-right of the application (purple).
2. Review the **Pre-publish SHACL validation** panel at the top of the dialog. It validates the Turtle that will actually be published against the CPRMV 0.4.1 / CPSV-AP 3.2.0 / RONL shapes. This is advisory — a non-conformant result (or an unreachable validation backend, shown in amber) does **not** stop you from publishing. Click **Validate now** to re-run it.
3. Check the **Dataset Name**: the dataset to publish into, `DMN-discovery` unless you chose another before. A name is 1 to 40 letters, digits and hyphens. There is nothing else to fill in — the backend holds the TriplyDB instance, the account and the token.
4. Optionally click **Test Connection** to check, through the backend, that the dataset exists.
5. Click **Publish to TriplyDB**.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: The publish dialog while publishing: a spinner beside Publishing to TriplyDB..., the progress bar a little over half full, ticks beside Validating form and Generating TTL, Publishing to TriplyDB in bold blue with a filled dot, and the Publishing... button disabled](../../assets/screenshots/cpsv-editor-publish-progress.png)
  <figcaption>While the backend publishes, the first two steps are ticked and Publishing to TriplyDB is the step under way</figcaption>
</figure>

---

## Progress tracking

The dialog lists three steps:

1. Validating form
2. Generating TTL
3. Publishing to TriplyDB

The editor validates the form and generates the Turtle itself. The third step is one call to the backend, which uploads the Turtle and any logos and syncs the dataset's service. The step under way is shown in bold with a filled dot, finished steps get a tick, and steps still to come an open circle.

On success the dialog says **Published successfully!** and closes after two seconds. A green message under the page title gives the dataset's URL and disappears after ten seconds.

If the Turtle reached TriplyDB but something around it did not, the dialog ends in an orange **Published with warning** that names each part: *Service update failed:* with the reason when the dataset's service could not be synced, and *Logo not uploaded:* with the file name for each logo the backend could not upload. It closes after three seconds, and the message under the page title says the same. The data is in TriplyDB, so publishing again would not help: only the dataset's SPARQL service may lag behind it, or a logo be missing.

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
