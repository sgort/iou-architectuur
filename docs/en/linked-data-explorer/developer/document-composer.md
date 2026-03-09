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
  processKey?: string;       // Operaton process definition key
  serviceId?: string;        // Chain Composer service identifier (informational)
  schemaVersion: number;     // currently 1
  zones: DocumentZones;
  bindings: VariableBinding[];
  assets: string[];          // TriplyDB asset URLs for dependency tracking
  createdAt: string;
  updatedAt: string;
  readonly?: boolean;
  status?: 'example' | 'wip';
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

The seed document (`Kapvergunning Beschikking`) is stored at `public/examples/flevoland/kapvergunning-beschikking.document` and loaded on first launch via `exampleVersions.ts`:

```typescript
export const EXAMPLE_VERSIONS: Record<string, number> = {
  'kapvergunning-beschikking': 1,
  // ...
};
```

The app checks `localStorage` key `linkedDataExplorer_exampleVersions`. If the stored version for a key is lower than `EXAMPLE_VERSIONS[key]`, the example file is re-fetched and written (as `readonly: true`, `status: 'example'`). This allows updating example content for existing users by incrementing the version number — no `localStorage` clear required.

**Developer workflow:** edit the example in `public/examples/flevoland/`, mirror the change to `examples/organizations/flevoland/`, increment the version in `exampleVersions.ts`, commit.

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

`DocumentTemplateSelector` (`BpmnModeler/DocumentTemplateSelector.tsx`) is injected into the bpmn-js properties panel alongside `FormTemplateSelector` whenever a `UserTask` is selected. It follows the identical injection pattern (see [BPMN Modeler developer docs](bpmn-modeler.md#formtemplateselector--form-linking-for-usertask-and-startevent)):

```typescript
// BpmnCanvas.tsx — inside selectionChanged, after FormTemplateSelector injection
if (elementType === 'bpmn:UserTask') {
  const docRoot = ReactDOM.createRoot(docSelectorContainer);
  docRoot.render(
    <DocumentTemplateSelector
      element={selectedElement}
      modeling={modeling}
      selectedDocumentRef={businessObject.get('camunda:documentRef')}
    />
  );
}
```

Selecting a template writes:

```typescript
modeling.updateProperties(element, {
  'camunda:documentRef': templateId,
});
```

Selecting the blank option sets `camunda:documentRef` to `undefined` (removes the attribute).

### Document badge overlay

The purple document badge is rendered in `BpmnCanvas.tsx` in the `element.changed` handler, immediately after the green form badge:

```typescript
const documentRef = element.businessObject.get('camunda:documentRef');
if (documentRef) {
  overlays.add(element.id, 'document-linked', {
    position: { bottom: -36, left: leftOffset }, // below the form badge
    html: `<div class="document-linked-badge" title="${documentRef}">📄 ${documentRef}</div>`,
  });
}
```

The badge is positioned 36px below the element (vs. 22px for the form badge), so both badges are visible simultaneously without overlapping.

---

## Export format

Clicking **Export .document** serialises the `DocumentTemplate` object to JSON and downloads it with a `.document` extension. The file is identical to what is stored in `localStorage` and can be used as a seed in `public/examples/`.

---

## Related pages

- [Document Composer features](../features/document-composer.md)
- [Document Composer user guide](../user-guide/document-composer.md)
- [BPMN Modeler developer docs — FormTemplateSelector](bpmn-modeler.md#formtemplateselector--form-linking-for-usertask-and-startevent)
- [Frontend Architecture](frontend.md) — ViewMode enum, localStorage key conventions
