# Document Composer

This guide walks through the complete workflow for creating a government decision document (*beschikking*) template in the Document Composer, binding it to process variables, and linking it to a BPMN process in the BPMN Modeler.

---

## Opening the Composer

Click **Document Composer** in the left sidebar (📄 icon). If no document has been created yet, the canvas shows an empty state with a **Create New Document** button. Click it, or use the **+** button in the left panel header, to create your first document.

---

## Creating a document

1. Click **+** in the document list header. A new document named `New document` is created with all mandatory zones empty.
2. Double-click the document name to rename it (e.g. `Kapvergunning — Beschikking`).
3. The canvas opens automatically with the six mandatory zones visible. The **Annex** zone is hidden by default.

---

## Adding blocks to zones

The left panel has two tabs: **Documents** (the list) and **Content** (the block library). Switch to **Content** to access the draggable block types.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Left panel showing the Content library tab with the five block types — Rich text, Variable, Image, Separator, and Spacer — ready to be dragged](../../assets/screenshots/linked-data-explorer-document-composer-content-library.png)
  <figcaption>Content library showing the five available block types</figcaption>
</figure>

1. Drag a **Rich text** block onto the **Body** zone. A TipTap editor appears inline.
2. Type your decision text. Use the toolbar for bold, italic, headings, and lists.
3. To reference a process variable, type `{{variableName}}` directly in the text. The token is resolved at render time when MijnOmgeving fills in the document.
4. Drag a **Variable** block onto the **Reference** zone for a standalone display of a single variable (e.g. the file reference number).
5. Drag an **Image** block to add a TriplyDB-hosted asset such as a municipality logo into the **Letterhead** zone.

### Reordering and moving blocks

- **Within a zone** — drag a block up or down to reorder it within the same zone.
- **Between zones** — drag a block across zone boundaries to move it. The target zone highlights when the block is over it.
- **Delete a block** — click the trash icon on the block toolbar.

---

## Enabling the Annex zone

At the bottom of the canvas, click **Add annex**. A seventh zone appears. Remove it with **Remove annex**. Blocks in the annex are not lost when the zone is toggled off and back on during the same session — but if you save while the annex is off, its blocks are not persisted.

---

## Binding variables

Open the right panel by clicking the **Bindings** tab (visible when a document is active).

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Bindings panel with AwbShellProcess entered in the process key field and several discovered variable chips displayed below the Discover Variables button](../../assets/screenshots/linked-data-explorer-document-composer-discover-variables.png)
  <figcaption>Discover Variables in action: chips for each process variable with type labels</figcaption>
</figure>

1. Enter the **process key** in the field at the top (e.g. `AwbShellProcess`).
2. Click **Discover Variables**. The panel queries the Operaton history API and shows a chip for every variable found in completed process instances.
3. Click a chip to pre-fill the binding form. Adjust the **placeholder** field if the token name in your text differs from the variable key.
4. Set **Source** to `process` for a live process variable, or `dmn_output` for a DMN result variable.
5. Click **Add binding**. The binding appears in the list.

You can also add bindings manually without using Discover Variables — fill in the placeholder and variable key fields directly.

---

## Saving and exporting

- **Save** (canvas toolbar) — persists the document to `localStorage`. The button is disabled when there are no unsaved changes.
- **Save as…** — creates a copy of the current document with a new name. Useful for creating variant templates.
- **Export .document** — downloads the template as a JSON file. The exported file can be imported into another LDE instance by copying it to `public/examples/` (developer workflow only).

---

## Working with the example document

The **Kapvergunning Beschikking** example is read-only (EXAMPLE badge). It demonstrates a complete, production-style beschikking template linked to the `AwbShellProcess` process key. To customise it:

1. Open the example document.
2. Click **Save as…** and give the copy a name.
3. Edit the copy freely.

The example document cannot be renamed or deleted.

---

## Linking to a BPMN process

Once your document is saved, switch to the **BPMN Modeler**:

1. Open or create a process.
2. Click a `UserTask` element to open its properties.
3. Scroll down to **Link decision template**. Your saved document appears in the dropdown.
4. Select it. A purple badge (📄) appears below the `UserTask` on the canvas, and `camunda:documentRef` is written to the BPMN XML.

The badge is distinct from the green form badge (📝) and the amber DMN badge so you can confirm all three links at a glance.

---

## Next steps

- [Document Composer features](../features/document-composer.md) — full feature reference
- [BPMN Modeler — Document template linking](../features/bpmn-modeler.md#document-template-linking)
- [Developer docs — Document Composer](../developer/document-composer.md) — type model and storage internals
