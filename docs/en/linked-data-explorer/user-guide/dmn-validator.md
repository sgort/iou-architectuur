# Using the DMN Validator

This guide explains how to validate DMN files before publishing them to TriplyDB.

---

## Opening the validator

Click the **shield icon** (🛡) in the left sidebar. The validator opens as a full-panel view. Any files you have loaded remain in place when you switch to other views and return.

---

## Loading files

**Drag and drop** one or more `.dmn` or `.xml` files directly onto the drop zone.

**Browse** by clicking anywhere on the drop zone to open a file picker. The picker accepts multiple file selection.

Files are read client-side — no content is sent to any server until you click **Validate**.

!!! note
    Only `.dmn` and `.xml` extensions are accepted. Other file types are skipped with a brief warning toast.

---

## Running validation

**Single file.** Click the **Validate** button on an individual file card.

**All files at once.** Click **Validate all** in the header. This runs all pending files concurrently — each card updates independently as results arrive.

Validation calls `POST /v1/dmns/validate` on the shared backend. The file content is sent as a JSON string. Results typically return within a few hundred milliseconds.

---

## Reading the results

### Summary badge

The top of each card shows either:

- 🟢 **Valid** — no errors (warnings and info may still be present)
- 🔴 **Invalid** — one or more errors detected

Alongside the badge, count pills show the total number of errors (E), warnings (W), and informational messages (I).

### Layer sections

Below the summary, five collapsible layer rows show the per-layer status:

- A green ✓ and **OK** means the layer found no issues.
- A coloured badge (e.g. **2W**, **1E**) means issues were found — click the row to expand them.

### Issue rows

Each issue shows:

- A severity icon (🔴 error / 🟡 warning / 🔵 info)
- A typed code (e.g. `INT-005`, `EXEC-001`)
- A human-readable message
- Where applicable: an element reference (e.g. `<inputData id="InputData_ingezetene_requirement">`) and a line number

Use the code to look up the detailed rationale in the [DMN Validation Reference](../reference/dmn-validation-reference.md).

---

## Acting on results

### Errors

Errors must be resolved in your DMN authoring tool (Camunda Modeler, VS Code DMN plugin, etc.) before the file is ready for deployment or publishing. Common errors:

- **BASE-PARSE** — the file is not valid XML. Open it in a text editor to locate the syntax problem.
- **BASE-NS** — the namespace does not match a known DMN version. Update the `xmlns` attribute on `<definitions>`.
- **INT-005** — an `<inputData>` element exists but is not wired to any decision. Either connect it or remove it in your modeler.

### Warnings

Warnings are advisory. The most common ones for RONL publishing:

- **BIZ-002 / BIZ-004** — `typeRef` is missing on an input expression or output column. Add the FEEL type (e.g. `boolean`, `string`, `integer`) in the modeler.
- **EXEC-001** — the CPRMV namespace is not declared. CPRMV attributes are optional but recommended for RONL-compliant publishing.

### Informational messages

Info messages flag quality improvements with no functional impact — for example, missing `<textAnnotation>` content or absent CPRMV descriptive attributes.

---

## Removing files

Click **×** on a file card to remove that file. Click **Clear all** in the header to remove all files and reset the panel.

---

## Next steps

Once all files are valid (or warnings have been reviewed and accepted):

1. Open the **CPSV Editor** and upload the DMN via the DMN tab.
2. The editor will re-run validation inline — results should match.
3. Deploy to Operaton and publish to TriplyDB.
