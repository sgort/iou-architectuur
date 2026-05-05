# RoPA Records

This guide walks through creating a complete RoPA record for a deployed process bundle — from opening the editor to activating the record for public publication.

---

## Prerequisites

- A process bundle must already exist in the BPMN Modeler with at least one linked form (so the **Hydrate from forms** button has something to read).
- The LDE backend must be connected to PostgreSQL — the RoPA feature requires database access.

---

## Step 1 — Open the RoPA Records view

Click the **ScrollText** icon (🗒) in the left sidebar. If no records exist yet the right panel shows an empty state. Click the **+** button in the panel header to create a new record.

---

## Step 2 — Fill in the Record tab

Start with the two identifier fields at the top:

1. **Title** — a clear, human-readable name for the processing activity, e.g. *Tree Felling Permit — material law assessment*.
2. **BPMN process ID** — copy the exact `id` attribute from the `<bpmn:process>` element, e.g. `TreeFellingPermitSubProcess`. This is the value shown on the process card in the BPMN Modeler.
3. **Process level** — select `Shell` if this record covers the AWB procedural shell, or `Subprocess` if it covers a product-specific subprocess.

Then complete all GDPR Art. 30 mandatory fields: controller name and contact, purpose, GDPR article, data subjects, recipients, retention period, and security measures.

### Looking up the legal basis

Click **Lookup from knowledge graph** next to the Legal basis field. The LDE queries the RONL TriplyDB endpoint and returns a list of `eli:LegalResource` entries linked to public services. Click the correct entry — both the URI and label fields are populated automatically.

If the service is not yet registered in the knowledge graph, type the label and URI manually.

---

## Step 3 — Hydrate personal data fields

Switch to the **Personal Data Fields** tab. Click **Hydrate from forms**.

The LDE reads the BPMN XML for the process ID you entered on the Record tab, extracts all `camunda:formRef` values, loads those form schemas, and creates one table row per field that has a `key` property. Fields without a `key` (headings, text blocks, submit buttons) are skipped automatically.

For each row:

- Confirm the **Label** — it is pre-filled from the form schema but can be edited.
- Set the **Category** dropdown to the most appropriate data category.
- Tick **Art. 9/10** for any field that collects health data (Art. 9 GDPR) or criminal data (Art. 10 GDPR). The zorgtoeslag form fields `statusZorgverzekerd` (health insurance status) and `gedetineerd` (detained) are examples.

Remove any rows that represent routing variables or computed outputs that do not constitute personal data by clicking the × on that row.

---

## Step 4 — Save the record

Click **Save** in the top bar. The record is persisted to PostgreSQL and appears in the left panel list with a **DRAFT** badge. The record now has a UUID which is needed for the next step.

---

## Step 5 — Link to the BPMN process

Switch to the **BPMN Link** tab. You will see the BPMN process ID, the record's UUID, and the current value of `ronl:ropaRef` in the process XML.

Click **Write ronl:ropaRef to BPMN**. The UUID is injected into the BPMN XML and the status indicator changes to green with a **✓ Linked** label.

!!! tip
    You can also link the record from the BPMN Modeler directly — open the process there and use the **RoPA Record** dropdown panel at the bottom of the process list. Both methods produce the same result.

---

## Step 6 — Activate the record

Switch to the **Status** tab. The current status is **Draft**. Click **Set Active**. Confirm the dialog — *"Activating this record will make it publicly visible. Continue?"*

Click **Save** again. The badge in the left panel changes to **ACTIVE** and the record is now returned by `GET /v1/ropa/public` and visible on the public site.

---

## Editing an existing record

Click any record in the left panel to open it. Edit the fields as needed and click **Save**. Changes to personal data fields (adding, removing, reclassifying) take effect immediately after saving.

!!! note
    Changing the **BPMN process ID** on an existing record does not automatically update the `ronl:ropaRef` in the old process XML. If you change the process ID, go to the BPMN Link tab and write the link again.

---

## Archiving a record

When a process bundle is retired, switch the record to **Archived** on the Status tab and save. Archived records are removed from the public site but remain in the database for audit purposes.

---

## Related documentation

- [RoPA Records features](../features/ropa-records.md) — full feature reference
- [RoPA Records developer docs](../developer/ropa-records.md) — database schema and API
- [BPMN Modeler user guide](bpmn-modeler.md) — linking forms and document templates