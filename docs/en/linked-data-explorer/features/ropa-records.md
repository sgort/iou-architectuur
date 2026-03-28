# RoPA Records

The RoPA Records feature lets Product Owners author and maintain a **Record of Processing Activities** (RoPA) for every deployed process bundle, fulfilling the mandatory GDPR Article 30 obligation for government processing activities. Records are stored in PostgreSQL, linked to their BPMN process via `ronl:ropaRef`, and published to a public-facing website isolated from the LDE stack.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: RoPA Records view showing the left panel list with four records grouped as two shells and two subprocesses, and the Record tab of the RopaRecordEditor open on the right with all GDPR Art. 30 fields filled in for the Tree Felling Permit subprocess](../../assets/screenshots/linked-data-explorer-ropa-records-overview.png)
  <figcaption>RoPA Records — record list (left) and Record tab editor (right)</figcaption>
</figure>

---

## Two-panel layout

The RoPA Records view follows the same two-panel convention as the Form Editor:

- **Left panel** — Record list. All RoPA records grouped as shell processes first, subprocesses second, each with a DRAFT / ACTIVE / ARCHIVED status badge and a delete control.
- **Right panel** — Record editor. Four tabs covering the full GDPR Art. 30 data model, BPMN linkage, and lifecycle management.

---

## Record list

Each entry in the list shows the record title, the `bpmnProcessId` it covers, and its current status. Shell records are top-level entries; subprocess records are indented beneath their parent shell with a tree connector — mirroring the hierarchy in the BPMN Modeler process list.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: RoPA Records left panel showing two shell records (AWB Shell Tree Felling Permit and AWB Shell Zorgtoeslag) each with two subprocess records indented beneath them, all carrying ACTIVE badges](../../assets/screenshots/linked-data-explorer-ropa-list.png)
  <figcaption>Record list — shell/subprocess hierarchy with status badges</figcaption>
</figure>

Clicking a record opens it in the editor. The **+** button in the panel header creates a new blank record.

---

## Record tab

The Record tab collects all GDPR Article 30 mandatory fields:

| Field | Description |
|---|---|
| Title | Human-readable name for the processing activity |
| BPMN process ID | The `<process id="...">` value from the BPMN XML — used to link the record to its process |
| Process level | `Shell` or `Subprocess` — reflects the AWB two-layer architecture |
| Controller name | Name of the data controller organisation |
| Controller contact | Contact address for the controller |
| DPO contact | Data Protection Officer contact (optional) |
| Purpose | Description of why the personal data is processed |
| GDPR article | Legal basis from the dropdown — Art. 6(1)(a) through (f) |
| Legal basis | `eli:LegalResource` URI and human-readable label |
| Data subjects | Categories of persons whose data is processed |
| Recipients | Who receives the data, including internal and external parties |
| Third country transfers | Toggle — reveals a detail field if transfers exist |
| Retention period | How long data is kept and under which statutory basis |
| Security measures | Technical and organisational measures in place |

### Legal basis lookup

The **Lookup from knowledge graph** button fires a SPARQL query against the TriplyDB RONL endpoint to retrieve all `eli:LegalResource` resources linked to `cpsv:PublicService` entries. Results appear as a pick-list; selecting one populates both the URI and label fields automatically.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Record tab showing the legal basis section with the Lookup button highlighted and a dropdown pick-list of legal resources below it, with Wet op de zorgtoeslag selected](../../assets/screenshots/linked-data-explorer-ropa-legal-lookup.png)
  <figcaption>Legal basis lookup — results from the RONL knowledge graph</figcaption>
</figure>

---

## Personal Data Fields tab

This tab lists every personal data field collected by the forms linked to this process. The **Hydrate from forms** button reads all `camunda:formRef` values from the process XML, loads the matching form schemas from the Form Editor storage, and appends one row per form component that has a `key` property — skipping headings, text blocks, and buttons.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Personal Data Fields tab showing a table with columns for Form, Field key, Label, Category, and Art. 9/10, populated with the zorgtoeslag-provisional-start form fields including statusZorgverzekerd and gedetineerd marked as Art. 9/10 special categories](../../assets/screenshots/linked-data-explorer-ropa-fields-tab.png)
  <figcaption>Personal Data Fields — hydrated from the zorgtoeslag-provisional-start form</figcaption>
</figure>

For each field the Product Owner classifies:

- **Data category** — `identity`, `financial`, `residence`, `health`, `civil status`, `criminal`, or `other`
- **Art. 9/10** — checkbox for health data (Art. 9) and criminal data (Art. 10) — renders as a red badge on the public site

Non-personal fields (routing variables, computed outputs) can be removed from the table using the × button on each row.

---

## BPMN Link tab

The BPMN Link tab writes `ronl:ropaRef` into the process XML, formally linking the record to its BPMN definition. The record must be saved first so it has a UUID.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: BPMN Link tab showing the BPMN process ID, the RoPA record ID, and the current ronl:ropaRef in BPMN XML field showing a matching UUID with a green tick and Linked label, and the Write ronl:ropaRef to BPMN button below](../../assets/screenshots/linked-data-explorer-ropa-bpmn-link-tab.png)
  <figcaption>BPMN Link tab — record linked, UUID matches</figcaption>
</figure>

Clicking **Write ronl:ropaRef to BPMN** injects the attribute into the process XML and saves via `BpmnService`. If the `xmlns:ronl` namespace declaration is absent from the `<definitions>` element, it is added automatically.

The status indicator shows three states:

- **Not linked** — no `ronl:ropaRef` present in the XML
- **Linked** (green) — `ronl:ropaRef` matches this record's ID
- **Points to a different record** (amber) — the XML has a `ronl:ropaRef` but it references a different record ID

---

## Status tab

The Status tab controls the publication lifecycle of the record.

| Status | Meaning |
|---|---|
| **Draft** | Internal only — not returned by the public endpoint |
| **Active** | Publicly visible via `GET /v1/ropa/public` — appears on the public site |
| **Archived** | Hidden from public site — retained for audit purposes |

Activating a record shows a confirmation dialog: *"Activating this record will make it publicly visible on ropa.flevoland.nl. Continue?"* Status changes take effect after saving the record with the **Save** button in the top bar.

---

## RoPA Selector in the BPMN Modeler

When a process is open in the BPMN Modeler, a **RoPA Record** panel appears pinned to the bottom of the process list — below the scrollable card list. It shows a dropdown of all available RoPA records and writes `ronl:ropaRef` directly into the process XML on selection, without requiring any canvas element to be selected.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: BPMN Modeler process list with the RoPA Record panel visible at the bottom, showing the dropdown with AWB Shell Tree Felling Permit selected and a teal info card below showing the controller name and GDPR article](../../assets/screenshots/linked-data-explorer-ropa-selector-processlist.png)
  <figcaption>RoPA Record selector — pinned to the bottom of the BPMN Modeler process list</figcaption>
</figure>

---

## Deploy modal warning

When deploying a bundle to Operaton, the deploy modal checks whether `ronl:ropaRef` is present on the process element. If absent, an amber warning is shown between the resource list and the resource count:

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Deploy modal showing the resource list with BPMN and form files, followed by an amber warning panel reading No ronl:ropaRef found on the process element. Link a RoPA record in the BPMN properties panel before deploying to production.](../../assets/screenshots/linked-data-explorer-ropa-deploy-warning.png)
  <figcaption>Deploy modal — amber warning when no RoPA record is linked</figcaption>
</figure>

The warning is non-blocking — the **Deploy** button remains active. It is intended to prompt the Product Owner to complete the RoPA record before promoting to production.

---

## Public website

Active RoPA records are served from a CORS-open public endpoint and rendered on a dedicated static site **[ropa.open-regels.nl](https://acc.ropa.open-regels.nl)** deployed separately from the LDE. The site displays collapsible cards — one per record — with all GDPR Art. 30 fields including the personal data fields table with colour-coded data categories and Art. 9/10 flags.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: ropa.flevoland.nl public site showing four collapsible record cards — AWB Shell Zorgtoeslag (Processchil, Actief), AWB Shell Tree Felling Permit (Processchil, Actief), Zorgtoeslag provisional entitlement assessment (Deelproces, Actief), Tree Felling Permit material law assessment (Deelproces, Actief)](../../assets/screenshots/ropa-site-overview.png)
  <figcaption>Public RoPA site — four active records for Provincie Flevoland</figcaption>
</figure>

See [RoPA Records developer docs](../developer/ropa-records.md) for the API endpoint, database schema, and public site deployment.

---

## Related documentation

- [RoPA Records user guide](../user-guide/ropa-records.md) — step-by-step authoring workflow
- [RoPA Records developer docs](../developer/ropa-records.md) — database schema, API routes, public site
- [BPMN Modeler — RoPA linkage](bpmn-modeler.md#ropa-record-linkage)
- [Document Composer](document-composer.md) — authoring decision document templates