---
component: Linked Data Explorer
---

# Document Composer Implementation

The Document Composer is a React feature for authoring structured government decision document templates (*beschikkingen*). It follows the same component, storage, and DnD patterns established by the BPMN Modeler and Form Editor.

---

## Component structure

```
DocumentComposer/
├── DocumentComposer.tsx       # Root — owns template list state, DnD context, panel layout
├── DocumentList.tsx           # Left panel — document CRUD and Content library tab
├── DocumentCanvas.tsx         # Centre panel — zone rendering, block operations, toolbar
├── ZonePanel.tsx              # Individual zone — droppable container + block list
├── TextBlockEditor.tsx        # TipTap rich-text block (inline editor)
├── ImageBlock.tsx             # TriplyDB asset block
├── VariableBlock.tsx          # Standalone variable-display block
└── BindingPanel.tsx           # Right panel — {{placeholder}} → variableKey bindings
```

`BpmnModeler/DocumentTemplateSelector.tsx` is injected into the bpmn-js properties panel for `UserTask` elements (separate from the Composer itself).

---

## Type model

Defined in `packages/frontend/src/types/document.types.ts`. Key interfaces:

```typescript
interface DocumentTemplate {
  id: string;
  name: string;
  description?: string;
  processKey?: string;       // Operaton process definition key
  serviceId?: string;        // Chain Composer service identifier (informational)
  schemaVersion: number;     // currently 1
  zones: DocumentZones;
  bindings: VariableBinding[];
  assets: string[];          // TriplyDB asset URLs for dependency tracking
  createdAt: string;
  updatedAt: string;
  readonly?: boolean;
  status?: 'example' | 'wip' | 'e2e';
  language?: 'en' | 'nl' | 'de';
  organization?: string;
}

interface DocumentZones {
  letterhead: DocumentZone;
  contactInformation: DocumentZone;
  reference: DocumentZone;
  body: DocumentZone;
  closing: DocumentZone;
  signOff: DocumentZone;
  annex?: DocumentZone | null;
}

interface DocumentZone {
  blocks: DocumentBlock[];
}

type BlockType = 'text' | 'image' | 'variable' | 'separator' | 'spacer';

interface DocumentBlock {
  id: string;
  type: BlockType;
  content?: TipTapDoc;       // ProseMirror JSON — for type === 'text'
  assetUrl?: string;         // for type === 'image'
  variableKey?: string;      // for type === 'variable'
  label?: string;
}

interface VariableBinding {
  id: string;
  placeholder: string;       // e.g. "{{permitDecision}}"
  variableKey: string;       // Operaton variable name
  source: 'process' | 'dmn_output';
  label?: string;
}
```

`ZONE_META` (also in `document.types.ts`) maps each `ZoneId` to a display label, English internal name, required flag, and description. `ZONE_ORDER` defines the fixed rendering sequence (annex always last).

---

## Storage

`DocumentService` (`services/documentService.ts`) provides synchronous CRUD over `localStorage`. The storage key is `linkedDataExplorer_documentTemplates`.

```typescript
DocumentService.getTemplates(): DocumentTemplate[]
DocumentService.getTemplate(id: string): DocumentTemplate | null
DocumentService.saveTemplate(template: DocumentTemplate): void
DocumentService.deleteTemplate(id: string): void
```

---

## Example document seeding

The example templates are defined inline in `DocumentComposer/defaultTemplates.ts` and listed in `DEFAULT_TEMPLATES`, eight in all:

| Template id | Name |
|---|---|
| `example_treefelling_beschikking` | Kapvergunning Beschikking (Example) |
| `example_zorgtoeslag_provisional_beschikking` | Zorgtoeslag Voorlopige Beschikking (Example) |
| `example_zorgtoeslag_final_beschikking` | Zorgtoeslag Definitieve Beschikking (Example) |
| `example_dvtp_consent_receipt` | DvTP Toestemmingsbewijs (Example) |
| `board-decision-notification-nl` | HR — Directiebesluit-notificatie (Voorbeeld, NL) |
| `capacity-claim-handover-nl` | HR — Overdracht capaciteitsclaim (Voorbeeld, NL) |
| `thuisbatterij_subsidie_beschikking` | Subsidie Thuisbatterij Beschikking |
| `besluit-gb-besluit` | Besluit onder gedelegeerde bevoegdheid |

On mount, `DocumentComposer.tsx` saves every entry of `DEFAULT_TEMPLATES` whose id is not yet in `localStorage`. Seeding goes by presence, not by version: `exampleVersions.ts` plays no part here, and a template already stored in a browser is never overwritten by a newer default.

Every example carries `status: 'example'`, which blocks deletion. All of them are `readonly: false` except `example_dvtp_consent_receipt`, which is `readonly: true`: **Save** is disabled for it, and **Save As** creates an editable copy.

Some templates mirror a `.document` file that is deployed with a bundle. `thuisbatterij_subsidie_beschikking` is kept in step with `public/examples/flevoland/thuisbatterij_subsidie_beschikking.document`, and `besluit-gb-besluit` with `public/examples/flevoland/besluitvorming-gedelegeerd/besluit-gb-besluit.document` — the copy the LDE deploys and the RONL Business API renders for signing. The copy is inline because the Vite dev server rejects imports from `public/`; `defaultTemplates.test.ts` pins the inline copy and the file as identical.

**Developer workflow:** edit the template in `defaultTemplates.ts`; where it mirrors a deployed `.document` file, change that file in the same commit.

---

## Drag-and-drop

Drag-and-drop is implemented with `@dnd-kit/core` and `@dnd-kit/sortable`. The `DndContext` lives in `DocumentComposer.tsx` and passes `dragEndEvent` down to `DocumentCanvas.tsx` via props (to keep business logic in the canvas component while the context wraps the full three-panel layout).

Two drag types are distinguished via `DragData.type`:

- `'new-block'` — dragged from the Content library. Resolved in `DocumentCanvas` by calling `createBlock(dragData)` and appending to the target zone.
- `'existing-block'` — dragged from an existing block within a zone. Resolved by either reordering within the zone (`arrayMove`) or moving to a different zone.

Zone droppable IDs use the prefix `zone-{zoneId}` so that `DocumentCanvas` can distinguish a drop onto a zone (append to end) from a drop onto a specific block (insert at position).

---

## TextBlockEditor and TipTap readonly sync

`TextBlockEditor` wraps `@tiptap/react`. TipTap only reads the `editable` option at initialisation and does not react to prop changes. A `useEffect` syncs the `readonly` prop after mount:

```typescript
useEffect(() => {
  editor?.setEditable(!readonly);
}, [editor, readonly]);
```

This mirrors the pattern in the BPMN Modeler's form editors.

---

## BindingPanel — variable discovery

`BindingPanel` calls `fetchVariableHints(processKey)` from `assetService.ts`, which hits:

```
GET /v1/process/:key/variable-hints
```

The backend queries the Operaton history API for all variables present in completed instances of the given process definition key, deduplicates by name, and returns an array of `{ name, type }` objects. The response is typed as `ProcessVariableHint[]`.

---

## DocumentTemplateSelector — BPMN integration

`DocumentTemplateSelector` (`BpmnModeler/DocumentTemplateSelector.tsx`) is injected into the bpmn-js properties panel alongside `FormTemplateSelector` whenever a `UserTask` is selected. It follows the identical injection pattern (see [BPMN Modeler developer docs](bpmn-modeler.md#formtemplateselector-form-linking-for-usertask-and-startevent)):

```typescript
// BpmnCanvas.tsx — inside selectionChanged, after FormTemplateSelector injection
if (elementType === 'bpmn:UserTask') {
  const docRoot = ReactDOM.createRoot(docSelectorContainer);
  docRoot.render(
    <DocumentTemplateSelector
      element={selectedElement}
      modeling={modeling}
      selectedDocumentRef={businessObject.get('ronl:documentRef')}
    />
  );
}
```

`ronl:documentRef` holds a comma-separated list of template ids, because one task can produce several documents. `utils/documentRefs.ts` reads and writes it: `parseDocumentRefs` splits on commas, trims whitespace and drops blanks; `formatDocumentRefs` joins the ids with a comma, or returns `undefined` for an empty list so that the attribute is removed rather than left empty. A BPMN with a single id needs no migration.

The selector, labelled **Link decision templates**, shows each attached template as a removable chip. The select below it is an add action: choosing a template appends its id (`-- Add a template --`), and once every template is attached the select is disabled (`-- All templates attached --`). Every change writes the whole list:

```typescript
modeling.updateProperties(element, {
  'ronl:documentRef': formatDocumentRefs(ids),
});
```

A chip for an id that has no template in this browser shows the id instead of a name, so an attachment from an imported BPMN stays visible.

### Document badge overlay

The purple document badge is rendered in `BpmnCanvas.tsx` in the `element.changed` handler, immediately after the green form badge:

```typescript
const documentRefs = parseDocumentRefs(element.businessObject.get('ronl:documentRef'));
if (documentRefs.length === 0) return;
const label =
  documentRefs.length === 1 ? documentRefs[0] : `${documentRefs.length} documents`;
overlays.add(element.id, 'document-linked', {
  position: { bottom: -36, left: leftOffset }, // below the form badge
  html: `<div class="document-linked-badge" title="${documentRefs.join(', ')}">📄 ${label}</div>`,
});
```

With one document the badge names it; with several it reads **N documents** and the tooltip lists every id. The badge is positioned 36px below the element (vs. 22px for the form badge), so both badges are visible simultaneously without overlapping.

When a process is deployed, the bundle collects document ids from both `ronl:documentRef` and `ronl:signatureRef`, splitting each list, and includes the matching templates from local storage as `.document` resources. A referenced template that is not in local storage is reported in the deploy dialog and blocks the deploy.

---

## Export format

Clicking **Export .document** serialises the `DocumentTemplate` object to JSON and downloads it with a `.document` extension. The file is identical to what is stored in `localStorage` and can be used as a seed in `public/examples/`.

---

## Related pages

- [Document Composer features](../features/document-composer.md)
- [Document Composer user guide](../user-guide/document-composer.md)
- [BPMN Modeler developer docs — FormTemplateSelector](bpmn-modeler.md#formtemplateselector-form-linking-for-usertask-and-startevent)
- [Frontend Architecture](frontend.md) — ViewMode enum, localStorage key conventions
