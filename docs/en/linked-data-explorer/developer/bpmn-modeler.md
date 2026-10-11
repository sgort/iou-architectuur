---
component: Linked Data Explorer
---

# BPMN Modeler Implementation

The BPMN Modeler wraps the `bpmn-js` library in a three-panel React component. This page covers the component structure, the canvas setup decisions, and known rendering issues with their fixes.

---

## Component structure

```
packages/frontend/src/components/BpmnModeler/
├── BpmnModeler.tsx            main orchestrator, manages selected process state
├── BpmnCanvas.tsx             bpmn-js canvas wrapper (modeler lifecycle, badge overlays, deploy trigger)
├── BpmnProperties.tsx         properties panel (right), includes DmnTemplateSelector
├── ProcessList.tsx            process list (left), CRUD operations
├── DmnTemplateSelector.tsx    DMN/DRD dropdown for BusinessRuleTask linking
├── FormTemplateSelector.tsx   Form dropdown for UserTask / StartEvent linking
├── DocumentTemplateSelector.tsx  document template chips and "add" select for UserTask linking
├── RopaSelector.tsx           RoPA record selector, in the footer pinned below the process list
├── DsoActiviteitSelector.tsx  DSO activiteit URN selector, in the same footer
├── ProcessPhasesEditor.tsx    the process's phase scheme and own phases, for RBA's stepper
├── PhaseMarkerSelector.tsx    "Start van fase": the phase a node starts
├── ronlModdleDescriptor.json  registers the ronl: attributes bpmn-js reads as properties
└── BpmnModeler.css            custom styles for canvas rendering fixes and badge overlays

packages/frontend/src/
├── services/
│   ├── bpmnService.ts         localStorage CRUD for BpmnProcess records
│   └── formService.ts         localStorage CRUD for FormSchema records (shared with FormEditor)
└── utils/
    ├── bpmnLinks.ts           extractCallActivityTargets, shared with the RoPA editor
    ├── bpmnTemplates.ts       default BPMN XML templates (new process, example)
    ├── deployBundle.ts        findProcessId, resolveSubProcesses, collectBundleRefs: the deploy bundle
    ├── documentRefs.ts        parse and format the comma-separated ronl:documentRef list
    ├── exampleVersions.ts     EXAMPLE_VERSIONS, the seed version registry
    ├── processIdentity.ts     isValidProcessId, renameProcessId, freshProcessId
    └── phases/                phase model, RBA's phase inheritance, deploy checks, edit commands
```

---

## Canvas initialisation

`BpmnCanvas.tsx` manages the bpmn-js modeler instance lifecycle:

```typescript
const modeler = new BpmnModeler({
  container: containerRef.current,
  additionalModules: [
    BpmnPropertiesPanelModule,
    BpmnPropertiesProviderModule,
    CamundaPlatformPropertiesProviderModule,
  ],
  moddleExtensions: {
    camunda: camundaModdleDescriptor,
    ronl: ronlModdleDescriptor,
  },
});

await modeler.importXML(xml);
const canvas = modeler.get('canvas');
canvas.zoom('fit-viewport');
refreshDmnOverlays();
```

The badge overlays are drawn by `refreshDmnOverlays()`, which runs after the import and again on every `commandStack.changed` event.

`camunda-bpmn-moddle` is used instead of an Operaton equivalent because no `operaton-bpmn-moddle` package exists. Operaton accepts both `camunda:` and `operaton:` namespace attributes, so `camunda:` is safe to use and ensures compatibility with the broader Camunda 7 tooling ecosystem.

---

## Scroll-to-zoom override

The bpmn-js default requires `Ctrl+Scroll` to zoom. This was overridden to plain scroll for consistency with the rest of the application:

```typescript
const handleWheel = (e: WheelEvent) => {
  e.preventDefault();
  const canvas = modelerRef.current?.get('canvas') as any;
  const currentZoom = canvas.zoom();
  const delta = e.deltaY > 0 ? -0.1 : 0.1;
  canvas.zoom(Math.max(0.2, Math.min(4, currentZoom + delta)));
};

container.addEventListener('wheel', handleWheel, { passive: false });
```

`passive: false` is required so `preventDefault()` is effective on wheel events.

---

## Rendering artifact fix

bpmn-js produces black circles and stray lines during drag operations when SVG layer pointer events conflict. The fix in `BpmnModeler.css`:

```css
.bpmn-container .djs-overlay-container,
.bpmn-container .djs-hit-container,
.bpmn-container .djs-outline-container {
  pointer-events: none;
}

.bpmn-container .djs-element {
  pointer-events: all;
}
```

This separates hit detection (on elements) from overlay rendering (no pointer events), eliminating the visual artifacts.

---

## FormTemplateSelector — form linking for UserTask and StartEvent

`FormTemplateSelector` is a React component injected into the bpmn-js properties panel when a `UserTask` or `StartEvent` is selected. It reads available forms from `FormService` and writes `camunda:formRef` / `camunda:formRefBinding` to the element's BPMN extension attributes via the bpmn-js `modeling` API.

### Injection

The injection follows the same pattern as `DmnTemplateSelector`. Inside `BpmnCanvas.tsx`, the `selectionChanged` listener distinguishes element type and mounts the appropriate selector:

```typescript
} else if (elementType === 'bpmn:UserTask' || elementType === 'bpmn:StartEvent') {
  const selectorContainer = document.createElement('div');
  selectorContainer.id = `form-template-custom-${selectedElement.id}`;
  propertiesPanel.appendChild(selectorContainer);

  const root = ReactDOM.createRoot(selectorContainer);
  root.render(
    <FormTemplateSelector
      element={selectedElement}
      modeling={modeling}
      selectedFormRef={businessObject.get('camunda:formRef')}
    />
  );
}
```

The `cleanupReactRoots()` helper unmounts the previous React root whenever the selection changes, preventing stale instances.

### Writing attributes

When the user selects a form:

```typescript
modeling.updateProperties(element, {
  'camunda:formRef': schemaId,        // the schema.id from the FormSchema JSON
  'camunda:formRefBinding': 'deployment', // the process's own deployment; 'latest' fails with ENGINE-03109 across tenants
  'camunda:formKey': undefined,       // clears any legacy HTML formKey
});
```

`schemaId` is `(form.schema as Record<string, unknown>).id` — the ID embedded in the form's JSON schema, not the outer `FormSchema.id` used as the localStorage record key.

### Clearing a link

Selecting the blank option calls:

```typescript
modeling.updateProperties(element, {
  'camunda:formRef': undefined,
  'camunda:formRefBinding': undefined,
});
```

---

## Form badge overlay

When any `UserTask` or `StartEvent` has `camunda:formRef` set, `BpmnCanvas.tsx` renders a green badge overlay using the bpmn-js `overlays` service, in `refreshDmnOverlays()` — after the import and on every `commandStack.changed` event.

```typescript
// UserTask: on the task's bottom edge
overlays.add(element.id, 'form-linked', {
  position: { bottom: 8, left: leftOffset },
  html: `<div class="form-linked-badge" title="${formRef}">📝 ${formRef}</div>`,
});

// StartEvent: below the event, with the narrower --start variant
overlays.add(element.id, 'form-linked', {
  position: { bottom: -22, left: leftOffset },
  html: `<div class="form-linked-badge form-linked-badge--start" title="${formRef}">📝 ${formRef}</div>`,
});
```

The badge offset uses `leftOffset = Math.round((element.width - badgeWidth) / 2)` to centre the badge horizontally on the element, with a badge width of 130 for a task and 110 for a start event. The CSS class `form-linked-badge--start` applies a smaller font, padding and maximum width for `StartEvent` elements, which have a narrower default width.

Styles are defined in `BpmnModeler.css`:

```css
.form-linked-badge {
  background: #16a34a;   /* green-600 */
  color: white;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  max-width: 130px;
  overflow: hidden;
  text-overflow: ellipsis;
  pointer-events: none;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}
```

`pointer-events: none` prevents the badge from interfering with element selection on the canvas.

---

## DocumentTemplateSelector — document template linking for UserTask

`DocumentTemplateSelector` is a React component injected into the bpmn-js properties panel when a `UserTask` is selected (not `StartEvent`). It reads available document templates from `DocumentService` and writes `ronl:documentRef` to the element via the bpmn-js `modeling` API. It follows the identical injection pattern as `FormTemplateSelector`.

`ronl:documentRef` holds a **list**: one template id, or several separated by commas, because a task can produce more than one deliverable. `utils/documentRefs.ts` reads and writes it:

- `parseDocumentRefs(value)` splits on commas, trims each id and drops blanks, so a hand-edited `"a, b"` reads the same as `"a,b"`;
- `formatDocumentRefs(ids)` joins the cleaned ids with a comma, or returns `undefined` for an empty list, which makes `modeling.updateProperties` remove the attribute rather than write an empty string.

A BPMN with a single id needs no migration: it is a list of one.

### Injection

In `BpmnCanvas.tsx`, when the selection changes to a `UserTask`, the document selector is appended to the properties panel immediately below the `FormTemplateSelector`:

```typescript
// UserTask only — not StartEvent
if (elementType === 'bpmn:UserTask') {
  const docSelectorContainer = document.createElement('div');
  docSelectorContainer.id = `document-template-custom-${selectedElement.id}`;
  propertiesPanel.appendChild(docSelectorContainer);

  const currentDocumentRef = businessObject.get('ronl:documentRef');

  const docRoot = ReactDOM.createRoot(docSelectorContainer);
  docRoot.render(
    <DocumentTemplateSelector
      element={selectedElement}
      modeling={modeling}
      selectedDocumentRef={currentDocumentRef}
    />
  );
}
```

`cleanupReactRoots()` unmounts all injected React roots (form and document) when the selection changes.

### Attaching and removing templates

The control is headed **Link decision templates**. Each attached template is a chip showing its name, its description and `processKey` where the template has them, and its id, with a **✕** button that removes it. An id that matches no template in this browser — a BPMN that references a template this browser has not been seeded with — shows as its bare id rather than being hidden.

Below the chips, a select adds a template. It offers only the templates not yet attached, under the placeholder **-- Add a template --**; once every template is attached it reads **-- All templates attached --** and is disabled. The select is an add action rather than the state itself, so removing one of three templates is a click on its chip rather than a ctrl-click in a multi-select.

Both actions write the whole list back:

```typescript
const write = (ids: string[]) => {
  setSelectedIds(ids);
  modeling.updateProperties(element, {
    'ronl:documentRef': formatDocumentRefs(ids), // undefined when the list is empty
  });
};
```

When no templates exist at all, the control shows *No documents available — create one in the Document Composer.* instead.

---

## Document badge overlay

When a `UserTask` has `ronl:documentRef` set, `BpmnCanvas.tsx` renders a purple badge below the element. This is applied in `refreshDmnOverlays()` alongside the DMN and form badges:

```typescript
overlays.remove({ type: 'document-linked' });

// ...inside the elementRegistry.forEach loop, after the form badge check:
if (element.type === 'bpmn:UserTask') {
  const documentRefs = parseDocumentRefs(element.businessObject.get('ronl:documentRef'));
  if (documentRefs.length === 0) return;
  const badgeWidth = 130;
  const leftOffset = Math.round((element.width - badgeWidth) / 2);
  const label =
    documentRefs.length === 1 ? documentRefs[0] : `${documentRefs.length} documents`;
  overlays.add(element.id, 'document-linked', {
    position: { bottom: -36, left: leftOffset }, // below the form badge
    html: `<div class="document-linked-badge" title="${documentRefs.join(', ')}">📄 ${label}</div>`,
  });
}
```

One document is named on the badge. Several would not fit, so the badge reads **N documents** and its `title` tooltip lists every id.

The badge offset is `bottom: -36`, below the form badge, so both badges show without overlapping. The form badge's block runs first and returns from the loop callback when the task has no `camunda:formRef`, so a user task shows a document badge only when it also has a form.

### CSS

Defined in `BpmnModeler.css`:

```css
.document-linked-badge {
  background: #7c3aed;   /* violet-700 */
  color: white;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  white-space: nowrap;
  max-width: 130px;
  overflow: hidden;
  text-overflow: ellipsis;
  pointer-events: none;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}
```

### Badge stacking order

| Overlay type | CSS class | Colour | `bottom` offset |
|---|---|---|---|
| `dmn-linked` | `.dmn-linked-badge` | Blue (`#2563eb`) | `8` (on the business rule task's bottom edge) |
| `form-linked` on a `UserTask` | `.form-linked-badge` | Green (`#16a34a`) | `8` (on the task's bottom edge) |
| `form-linked` on a `StartEvent` | `.form-linked-badge` + `.form-linked-badge--start` | Green (`#16a34a`) | `-22` (below the event) |
| `document-linked` | `.document-linked-badge` | Violet (`#7c3aed`) | `-36` (below the form badge) |

`refreshDmnOverlays()` removes all three overlay types before re-adding them, so stale badges are cleared on every `commandStack.changed` event.

---

## Deploy modal

The deploy modal is triggered by the **Deploy** button in the canvas toolbar. `BpmnCanvas.tsx` assembles the resource bundle before opening the modal:

### Resource collection

The bundle is computed in `utils/deployBundle.ts`. Its three helpers are shared by both handlers in `BpmnCanvas.tsx` — `handleOpenDeployModal`, which lists the bundle, and `handleDeploy`, which sends it — so the two cannot drift apart:

```typescript
// 1. Save current BPMN to get latest XML
const { xml } = await modelerRef.current.saveXML({ format: true });

// 2. The process key: the <process> id, under any namespace prefix
const processKey = findProcessId(xml) ?? 'process';

// 3. One level of subprocesses: each calledElement in the open process,
//    matched against saved BpmnProcess records by process id
const subProcessXmls = resolveSubProcesses(xml, BpmnService.getProcesses());

// 4. camunda:formRef ids, and document ids from ronl:documentRef (split on
//    commas) AND ronl:signatureRef, across the open process and its
//    subprocesses, once each
const { formRefs, documentRefs } = collectBundleRefs(xml, subProcessXmls);

// 5. Match form refs against FormService.getForms() by schema.id,
//    document ids against DocumentService.getTemplates() by id
```

`findProcessId` looks the process element up with `getElementsByTagNameNS('*', 'process')`, so it matches the prefixed `<bpmn:process>` that bpmn-js emits. `resolveSubProcesses` ignores a stored record's status; that is safe because an `e2e-fixtures` subprocess carries its own `…E2E` key that no example shell names, which `public-example-fixture-parity.test.ts` enforces. A called element no stored process provides is left out, and the engine reports it at start. `deployBundle.test.ts` covers the three helpers.

`ronl:signatureRef` is read alongside `ronl:documentRef` because a signature task can bind its template through `signatureRef` alone; the template must still travel with the deployment. A `documentRef` list is split rather than matched whole, so a task with two documents contributes two ids.

References that match nothing in local storage are passed to the modal as `unmatchedForms` and `unmatchedDocuments`. The modal lists them by name under **⛔ Referenced resources are missing from local storage** and **disables Deploy** while any remain, alongside the board-owner and organization guards: a bundle without them is one the engine cannot resolve at runtime.

`handleOpenDeployModal` also runs `checkPhases(xml)` (`utils/phases/phaseChecks.ts`) on the open process and passes the result as `phaseFindings`. Each finding renders as its own banner, red for an error and amber for a warning, and an error **disables Deploy** too. There is one error, `MIXED_SCHEMES` — declared phases and Awb markers in one process — and five warnings: `NO_MARKERS`, `UNKNOWN_CODE`, `EMPTY_PHASE`, `SKIPPED_ENTRIES` and `IGNORED_NODE_KIND`. See [Phases](#phases).

### Stacking

The modal's overlay sits at `z-[1100]`, not the `z-50` the app's other dialogs use. It is the only dialog that opens over a bpmn-js canvas, and bpmn-js brings its own stacking: `diagram-js.css` puts the context pad at 100, the popup menu at 200 and the hover tooltip at 1000, and `properties-panel.css` puts its tooltip and FEEL editor popup at 1001. At `z-50` a selected task's context pad sat on top of the modal and stayed clickable through the backdrop; 1100 clears them all. `BpmnCanvas.test.tsx` pins the class.

### API call

On **Deploy**, `BpmnCanvas.tsx` sends one JSON request to the backend:

```typescript
await fetch(`${API_BASE_URL}/api/dmns/process/deploy`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    bpmnXml: xml,
    deploymentName: processKey,       // from BPMN process/@id
    forms,                            // [{ id, schema }]
    documents,                        // [{ id, template }]
    subProcesses: subProcessXmls,     // [{ filename, xml }]
    boardOwner,
    organization: deployOrganization,
  }),
});
```

The request names **no Operaton target and no credentials**. The modal offers no Operaton URL, username or password; it names the Operaton the backend deploys to instead.

The call still uses the legacy `/api/dmns/...` alias, which the backend serves through the `/v1` handler with a `Deprecation` header.

**The backend records the bundle in the same request.** The response's `data` carries `deploymentId` and a `bundleRecorded` flag, with `bundleRecordingError` when the write did not land. A deploy Operaton has accepted is a success either way — it cannot be undone — so a failed recording shows as a **warning**, saying the process will not appear on the dashboard or the public site until it is saved and deployed again. The browser makes no second write of its own. An error response is read with `getProblemDetail()`, since errors are RFC 9457 problem details.

### Backend endpoint

`POST /api/dmns/process/deploy` (in `dmn.routes.ts`) delegates to `operatonService.deployProcess()`. That method builds a `multipart/form-data` request with each resource appended as a named field matching Camunda Modeler behaviour:

- Main BPMN: field name = `${processKey}.bpmn`
- Subprocess BPMNs: field name = the subprocess filename
- Forms: field name = `${formId}.form`
- Document templates: field name = `${documentId}.document`

The organization goes in Operaton's native `tenant-id` field.

Processes deploy **only to the configured Operaton**. `deployProcess()` always uses the shared client, built from `OPERATON_BASE_URL` and carrying `OPERATON_API_KEY`, so Operaton credentials stay on the backend. For older frontends, an `operatonUrl` equal to the configured one is still accepted; any other answers `400`, and `operatonUsername` and `operatonPassword` are ignored. All three fields are deprecated.

After Operaton accepts the deployment, the route finds the stored process by the id in the BPMN within the deploy's organisation — or creates a minimal row when none exists — and stamps it as deployed, recording the Operaton actually used. A minimal row's `lde_id` is `${organization}:${bpmnProcessId}` (the bare process id without an organisation), so one organisation's deploy can neither find nor overwrite another's row with the same process id. Saving a process takes `bpmnProcessId` from the saved XML, so renaming the process id no longer leaves a stale value that makes the next deploy create a second row.

---

## DmnTemplateSelector

`DmnTemplateSelector.tsx` loads from two sources in parallel when mounted for a `BusinessRuleTask`:

```typescript
const loadOptions = async () => {
  // Remote: regular DMNs from backend
  const response = await fetch(`${API_BASE_URL}/v1/dmns?endpoint=${endpoint}`);
  const dmnArray: DmnModel[] = data.data.dmns;

  // Local: DRD templates from localStorage
  const userTemplates = getUserTemplates(endpoint);
  const drdOptions = userTemplates
    .filter(t => t.isDrd && t.drdEntryPointId)
    .map(t => ({
      identifier: t.drdEntryPointId!,
      title: `${t.name} (DRD)`,
      isDrd: true,
      originalChain: t.drdOriginalChain,
    }));

  setOptions({ drds: drdOptions, dmns: dmnArray });
};
```

The dropdown renders two `<optgroup>` elements: "🔗 DRDs (Unified Chains)" and "📋 Single DMNs". Selection auto-populates `camunda:decisionRef` and suggests a `camunda:resultVariable` value (derived from the decision title, camelCased).

### DmnTemplateSelector pre-selection

Opening the properties panel for a `BusinessRuleTask` that already has `camunda:decisionRef` set shows that decision selected. `BpmnCanvas.tsx` reads `currentDecisionRef` from `businessObject.get('camunda:decisionRef')` and passes it as `selectedDecisionRef` to `DmnTemplateSelector`, which initialises its `useState` from that prop.

---

## Process persistence

`bpmnService.ts` stores processes as `BpmnProcess` records in PostgreSQL via the backend, using `localStorage` as a synchronous read cache. See [Asset Storage](asset-storage.md) for the full write-through cache and hydration architecture.

The `BpmnProcess` type includes three relationship fields:
```typescript
interface BpmnProcess {
  // ... existing fields ...
  bpmnProcessId?: string;                               // <process id="..."> from XML
  processRole?: 'shell' | 'subprocess' | 'standalone';
  calledElement?: string;                               // parent shell's bpmnProcessId
}
```

`bpmnProcessId` is extracted from the XML on save using:
```typescript
const extractBpmnProcessId = (xml: string): string => {
  const match = xml.match(/<(?:bpmn:)?process[^>]+\bid="([^"]+)"/);
  return match?.[1] ?? 'unknown';
};
```

`ProcessList.tsx` uses `calledElement === shell.bpmnProcessId` to group subprocesses under their parent shell in the hierarchical view.

### One process id per organisation

The backend keeps one stored process per organisation and process id, and answers a save that would break that with `409 PROCESS_ID_TAKEN`, naming the row that holds the id (see [Asset Storage](asset-storage.md)). `BpmnService.saveProcessDetailed` returns `{ saved, conflict? }`, with `conflict` set only for that refusal; `saveProcess` still returns the plain boolean. The Modeler handles the conflict in three places:

- **`handleCreateProcess`** gives every new process a fresh process id — `freshProcessId(templateId)`, the template's id plus a timestamp, written with `renameProcessId` — since every new process would otherwise share the template's id.
- **An import** whose id is taken is dropped from the local cache with `BpmnService.forgetLocal` (the server never stored it), and `resolveImportConflict` asks: replace the holder's content with the import, keeping its LDE id, record, status and deploy stamp, or give the import another id, prompted with a fresh one and checked with `isValidProcessId`.
- **A save** whose process id was renamed to a taken one shows an error naming the holder.

`renameProcessId` rewrites only the `<process>` id, a participant's `processRef` and the diagram plane's `bpmnElement`.

### Bundle assembly after migration

`BpmnCanvas.tsx` resolves subprocess XMLs for deployment by matching `calledElement` values from the active BPMN against stored `BpmnProcess` records. After the PostgreSQL migration the lookup continues to work identically — `hydrateFromServer()` ensures the local cache reflects the database state on mount, so the in-memory lookup in `BpmnService.getProcesses()` always has current data.

The backend additionally exposes `GET /v1/assets/bpmn/by-bpmn-id/:bpmnProcessId` for direct server-side subprocess lookup by BPMN process id. An optional `?organization=` scopes the lookup to one organisation, an empty value meaning none; without it, every organisation's rows count.

---

## RoPA linkage — moddleDescriptor and ProcessList

### ronlModdleDescriptor.json

`ronlModdleDescriptor.json` registers `ronl:` extensions against bpmn-js, under the namespace `http://ronl.nl/schema/1.0`, so bpmn-js reads and writes them as typed properties of the element — which is what lets `businessObject.get('ronl:documentRef')` and `modeling.updateProperties` work on them.

The descriptor declares seven type entries:

| Type | Extends | Attribute |
|---|---|---|
| `DocumentRefMixin` | `bpmn:UserTask` | `documentRef` — one or more template ids, comma-separated; `signatureRef` — the one template a signature task signs |
| `RopaRefMixin` | `bpmn:Process` | `ropaRef` |
| `DsoActiviteitMixin` | `bpmn:Process` | `dsoActiviteitUrn` |
| `LanguageMixin` | `bpmn:Process` | `language` |
| `OrganizationMixin` | `bpmn:Process` | `organization` |
| `PhasesMixin` | `bpmn:Process` | `phases` — the process's own phases, `code:Name` pairs separated by `;`; `phaseLabel` — the word before a phase's number, `Fase` when absent |
| `PhaseMarkerMixin` | `bpmn:FlowNode` | `phase` — the declared phase a node starts; `awbPhase` — the Awb phase it starts |

`ronl:signatureRef` is registered, but the Modeler offers no control for it: it is written by hand in the BPMN. `ronlModdleDescriptor.test.ts` reads `documentRef` and `signatureRef` on a user task as typed properties, because an unregistered attribute still round-trips, parked in `$attrs`, and a missing registration would otherwise fail silently.

The phase attributes are registered so the phase editors can write them with `modeling.updateModdleProperties`; the test also reads them as typed properties and round-trips them through a save.

Each entry has the same shape, e.g. for `LanguageMixin`:
```json
{
  "name": "LanguageMixin",
  "extends": ["bpmn:Process"],
  "properties": [
    { "name": "language", "isAttr": true, "type": "String" }
  ]
}
```

When adding a new attribute on `bpmn:Process` or `bpmn:UserTask`, append a new mixin entry rather than altering existing ones — each entry is self-contained.

### RopaSelector placement

`RopaSelector.tsx` is rendered as a sibling of the scrollable list container inside `ProcessList.tsx`, not as a child. The JSX structure is:
```
<div className="w-80 bg-white border-r ...">   ← outer wrapper
  <div className="h-14 ...">                   ← header
  <div className="flex-1 overflow-y-auto ..."> ← scrollable list
  </div>
  {activeProcess && (                          ← RopaSelector — outside scroll container
    <div className="border-t ... shrink-0">
      <RopaSelector ... />
    </div>
  )}
</div>
```

Placing the panel inside the scroll container caused it to scroll away with the list — it must be a sibling to stay pinned.

### handleRopaRefChange

`handleRopaRefChange` in `BpmnModeler.tsx` handles three cases:

- `ropaRef` is a non-empty string and `ronl:ropaRef` already exists → regex replace the existing value
- `ropaRef` is a non-empty string and `ronl:ropaRef` is absent → inject into the `<bpmn:process>` opening tag before its `>` or `/>`
- `ropaRef` is `undefined` → remove the attribute entirely with a regex that also strips the preceding whitespace

In all cases it first checks for `xmlns:ronl=` in the XML and injects the namespace declaration on the `<definitions>` element if absent.

---

## Phases

The phase editors set the attributes the RONL Business API reads to draw a caseworker's phase stepper. RBA is the reference for every rule: the code in `utils/phases/` copies its parsing and its inheritance so that the canvas cannot show something the stepper does not.

```
packages/frontend/src/utils/phases/
├── phaseSet.ts        Phase, PhaseSet, the Awb table; parse and serialise ronl:phases, derive a code from a name
├── phaseGraph.ts      graphFromXml: the first <process>, its direct children of RBA's counted kinds
├── assignPhases.ts    findBackEdges, assignColumns, computePhaseView: RBA's inheritance, ported line for line
├── phaseChecks.ts     checkPhases: the deploy modal's findings
└── phaseCommands.ts   the ronl.phases.update command, process and node targeting, marker rewrites
```

- **`phaseSet.ts`** — `parseDeclaredPhases` follows RBA's `declaredPhaseSet`: entries split on `;`, each at its first `:`, both parts trimmed; an entry without a code or a name, or repeating a code, is skipped and reported. `AWB_PHASES` is copied from RBA's `awb-phases.ts`. `phaseCodeLabel` gives the label RBA shows: `Fase 4+5` or `Archiefwet` for Awb, `<label> <n>` for declared phases.
- **`phaseGraph.ts`** — reads the XML the way RBA's `parseSwimlane` does: only the first `<process>`, only its direct children of the counted kinds, attributes by local name, blank as absent. Nodes are sorted kind by kind in RBA's order, because that order decides the seed when there is no start event. A marker on an element of another kind, such as a boundary event, is collected as ignored.
- **`assignPhases.ts`** — `computePhaseView` decides the scheme (`declared` when `ronl:phases` yields a set, `awb` when an `ronl:awbPhase` marker exists, `none` otherwise), drops back edges, orders nodes by longest path, and gives an unmarked node the latest phase among its forward predecessors. The result, a `PhaseView`, holds every node's phase with an `inherited` flag, plus the unknown markers and skipped entries the checks report.
- **`phaseCommands.ts`** — every phase edit is one `ronl.phases.update` command, whose handler applies its updates as nested `updateModdleProperties` calls in `preExecute`. diagram-js records nested commands under the outer one, so a code rename that rewrites eight markers is one undo step. `updateModdleProperties` rather than `updateProperties`, because the phase list lives on the process while the selected element in a collaboration is its participant. `resolveProcessTarget` picks the process to edit, and `isCountedNode` mirrors RBA's counted kinds for bpmn-js elements.

### The panel

`BpmnCanvas.tsx` renders the panel into the properties panel's scroll container, below the other selectors: `ProcessPhasesEditor` when the process is the target — nothing selected, or a participant — and `PhaseMarkerSelector` for a flow node. The panel keeps one React root across edits and only re-renders it with the new phase view, so typing in a field survives the recompute; it re-mounts only when the selection or the process changes. Both components take `readByRba`: a pool other than the first process RBA reads gets an explanation instead of controls.

Awb phases have no process attribute — RBA recognises them by their markers — so a fresh **Awb phases** choice lives in the canvas's `schemeIntent` state until the first marker exists.

### Badges

`schedulePhaseRefresh` runs on import and on every `commandStack.changed`. After 150 ms it serialises the diagram with `saveXML`, computes the view with `phaseViewFromXml` and redraws the `phase-marker` overlays in `refreshPhaseOverlays`: `phase-badge--start` (solid) where a node carries its own marker, `phase-badge--inherited` (outlined) where it inherits, one colour per position in the set from `PHASE_COLOURS`. Phase names and codes are user text, so the overlay HTML is escaped. A failed save or parse keeps the last view.

---

## Example process seeding

On mount, `BpmnModeler.tsx` runs a versioned seed effect. For each example defined in `EXAMPLE_VERSIONS` (`utils/exampleVersions.ts`), if the stored version is lower than the current version the file is re-fetched from `public/examples/` and the record is overwritten in `localStorage`. The Migration & Asylum record is the exception: it is inline XML, written only when no record with its id exists, and has no version.

The seed effect writes **eleven** records. Ten carry `status: 'example'`, which is what the **EXAMPLE** badge and the disabled delete button key on; `wip_asylum_migration` carries `status: 'wip'`. **Status is not read-only.** Exactly one record — `example_dvtp_toestemming` — sets `readonly: true`; the other ten, `wip_asylum_migration` among them, set `readonly: false`.

That distinction is load-bearing, because `readonly` — not `status` — is what gates the backend write: `BpmnService.saveProcess` persists to `localStorage` first and then returns early for a readonly record without ever POSTing to `/v1/assets/bpmn`. So ten of the eleven seeded records *are* written to the backend when saved, and `hydrateFromServer` merges the readonly DvTP record back from local storage rather than from the server. A user's edit to a seeded example also survives only until the next version bump: the seed overwrites the stored record whenever `EXAMPLE_VERSIONS` moves past it.

The current example processes and their roles:

| Seed ID | `processRole` | `bpmnProcessId` | `calledElement` | Organization | Version |
|---|---|---|---|---|---|
| `example_awb_process` | `shell` | `AwbShellProcess` | — | `flevoland` | 9 |
| `example_tree_felling` | `subprocess` | `TreeFellingPermitSubProcess` | `AwbShellProcess` | `flevoland` | 11 |
| `example_awb_zorgtoeslag` | `shell` | `AwbZorgtoeslagProcess` | — | `toeslagen` | 7 |
| `example_zorgtoeslag_provisional` | `subprocess` | `ZorgtoeslagProvisionalSubProcess` | `AwbZorgtoeslagProcess` | `toeslagen` | 9 |
| `example_zorgtoeslag_final` | `subprocess` | `ZorgtoeslagFinalSubProcess` | `AwbZorgtoeslagProcess` | `toeslagen` | 7 |
| `example_thuisbatterij_aanvraag` | `shell` | `ThuisbatterijSubsidieAanvraagProcess` | — | `flevoland` | 4 |
| `example_thuisbatterij_decision` | `subprocess` | `ThuisbatterijSubsidieDecisionSubProcess` | `ThuisbatterijSubsidieAanvraagProcess` | `flevoland` | 3 |
| `example_dvtp_toestemming` | `standalone` | `DvtpToestemmingGevenProcess` | — | `bzk` | 4 |
| `example_hr_capacity_nl` | `standalone` | `ManagementCapacityClaimProcess` | — | `flevoland` | 5 |
| `example_besluit_gb` | `standalone` | `GedelegeerdBesluitProcess` | — | `flevoland` | 3 |
| `wip_asylum_migration` | `standalone` | `Process_Migratie_en_Asiel` | — | `ind` | — |

Every subprocess record declares `shellId` alongside `calledElement`. `example_besluit_gb` lists `GedelegeerdBesluitRoute` as its linked DMN; see [Besluitvorming onder gedelegeerde bevoegdheid](../features/besluitvorming-gedelegeerd-bundle.md) for the bundle.

### Lanes and Dutch names

Every Awb process is drawn as a pool with lanes and carries Dutch element names. Their element ids are the ones they always had, so nothing that references them by id changes.

| Process | Pool | Lanes |
|---|---|---|
| `AwbShellProcess` | *Awb Algemene wet bestuursrecht - Generiek proces* | Aanvrager, Behandelaar, Systeem |
| `TreeFellingPermitSubProcess` | *Kapvergunning - Behandeling en besluit* | Behandelaar, Systeem |
| `AwbZorgtoeslagProcess` | *Awb Zorgtoeslag - Voorlopige toekenning* | Aanvrager, Behandelaar, Systeem |
| `ZorgtoeslagProvisionalSubProcess` | *Zorgtoeslag — Beoordeling voorlopige aanspraak* | Behandelaar, Systeem |
| `ZorgtoeslagFinalSubProcess` | *Zorgtoeslag — Definitieve vaststelling* | Behandelaar, Systeem |
| `ThuisbatterijSubsidieAanvraagProcess` | *Subsidie Thuisbatterij Flevoland - Hoofdproces* | Aanvrager, Behandelaar, Systeem |
| `ThuisbatterijSubsidieDecisionSubProcess` | *Thuisbatterijsubsidie - Beoordeling recht en hoogte* | Behandelaar, Systeem |

A subprocess has no applicant-facing step, so it has no Aanvrager lane.

### DMN results as plain variables

A business rule task with `mapDecisionResult="singleResult"` stored a multi-output result as one serialised Java map, and two concurrent REST reads of it could collide with `ENGINE-03005`. The examples' business rule tasks that did so now map each output straight into a plain variable with a `camunda:outputParameter` on the transient `decisionResult` — for instance `${decisionResult.getSingleResult().getEntry("isComplete")}` — and the script tasks that only copied map values are gone. Gateways and scripts read the plain variables. Instances already running keep their old definition until they finish.

### Missing information

In each of the three Awb shells — kapvergunning, zorgtoeslag and Thuisbatterij — the user task *Aanvullende gegevens opvragen (Awb 4:5)* (`Task_RequestMissingInfo`) opens a form-js form with `camunda:formRefBinding="deployment"`. The form carries the `supplementReceived` checkbox the next gateway, *Aanvulling ontvangen?*, branches on.

| Shell | Form | Form Editor seed |
|---|---|---|
| `AwbShellProcess` | `kapvergunning-aanvullende-gegevens` | `example_kapvergunning_missing_info` |
| `AwbZorgtoeslagProcess` | `zorgtoeslag-aanvullende-gegevens` | `example_zorgtoeslag_missing_info` |
| `ThuisbatterijSubsidieAanvraagProcess` | `thuisbatterij-aanvullende-gegevens` | `example_thuisbatterij_missing_info` |

The `e2e-fixtures/manifest.json` entry for each shell lists its missing-information form beside the start and notification forms.

The Thuisbatterij shell checks completeness with its own `ThuisbatterijCompletenessCheck` decision, whose outputs `isComplete` and `missingFields` become plain variables. Its gateway *Aanvraag volledig?* has three exits: complete to the assessment; incomplete with no recovery asked yet to `Task_RequestMissingInfo`, whose end listener sets `herstelVerzocht`; and incomplete after recovery to *Aanvraag buiten behandeling stellen (Awb 4:5 lid 2)*. A supplement received sends the case back through the completeness check. The form shows `missingFields` and records the supplied values.

### Phase markers

The examples carry the phase attributes the RONL Business API reads to draw the caseworker's phase stepper; the [phase editors](#phases) show and edit them.

- **The Awb shells** mark the node that starts each Awb phase with `ronl:awbPhase` — `1`, `2`, `3`, `4+5`, `6`, `7`, `8` and `archivering` — and each Awb subprocess marks its start event with `4+5`. See [`ronl:awbPhase`](../../ronl-business-api/reference/bpmn-design-criteria.md#ronlawbphase).
- **The Dutch HR capacity claim** (`HR-capacity/ManagementCapacityClaimProcess.bpmn`) declares its own eight phases with `ronl:phases` and `ronl:phaseLabel`, marks the node that starts each with `ronl:phase`, and is drawn in eight lanes. Its business rule task `Task_DetermineRouting` carries `decisionRefTenantId="${null}"`, so it resolves the shared `CapacityClaimRouting` DMN untenanted.
- **Besluitvorming onder gedelegeerde bevoegdheid** declares six phases the same way.

See [A process's own phases](../../ronl-business-api/reference/bpmn-design-criteria.md#a-processs-own-phases-ronlphases-ronlphaselabel-ronlphase) and [Lanes and phase markers](../../ronl-business-api/reference/bpmn-design-criteria.md#lanes-and-phase-markers-the-caseworker-process-view) for how the RONL Business API reads them.

!!! warning "A tenanted process cannot see an untenanted DMN"
    Operaton resolves a business rule task's `decisionRef` **inside the process instance's own
    tenant**. A process deployed under tenant-id `flevoland` therefore cannot reach a DMN
    deployed without one, and the engine refuses to instantiate it at all — surfacing as a 500
    from process start and an unexplained *"De aanvraag kon niet worden ingediend"* on the ACC
    citizen dashboard. `decisionRefTenantId="${null}"` points a business rule task back at the
    shared untenanted DMN. Every business rule task in the kapvergunning, Zorgtoeslag provisional,
    Thuisbatterij, HR capacity and besluitvorming examples carries it; those in
    `ZorgtoeslagFinalSubProcess` and the DvTP process do not.

    A change to a seeded file reaches existing users only when its `EXAMPLE_VERSIONS` entry is
    bumped with it — without the bump the seed skips re-saving, and every existing user keeps
    the old copy.

After the seed effect, a separate hydration effect runs `BpmnService.hydrateFromServer()` to merge any user-authored processes stored in PostgreSQL into the local list.

---

## Pending-until-Save editing model

Footer edits — `language`, `organization`, `ropaRef`, `dsoActiviteitUrn` — accumulate in a draft on `BpmnModeler.tsx` rather than persisting immediately. The pattern:

```typescript
type FooterDraft = {
  language?: BpmnProcess['language'];
  organization?: string;
  ropaRef?: string;
  dsoActiviteitUrn?: string;
};

const [draft, setDraft] = useState<FooterDraft>({});
const [hasFooterChanges, setHasFooterChanges] = useState(false);
const [hasCanvasChanges, setHasCanvasChanges] = useState(false);
```

Footer handlers update only the draft:

```typescript
const handleLanguageChange = (language: string | undefined) => {
  if (!activeProcessId) return;
  setDraft((d) => ({ ...d, language: language as BpmnProcess['language'] }));
  setHasFooterChanges(true);
};
```

`handleSaveProcess` flushes the draft into both the in-memory `BpmnProcess` object and the BPMN XML's `ronl:` attributes, then resets the draft. Distinguishing "user touched the field" from "user explicitly cleared it" matters — the `'language' in draft` idiom preserves the difference between *unset* and *cleared*:

```typescript
language: 'language' in draft ? draft.language : process.language,
```

The list panel reads from committed `processes` state so visible grouping doesn't shift while the user is typing in the footer. The footer reads its display value via a `readEffective()` helper: draft wins when the field has been touched, else the committed `BpmnProcess` field, else the `ronl:` attribute extracted from the XML.

Navigation guards (`handleCreateProcess`, `handleLoadProcess`, `handleCloseProcess`) check the combined `hasUnsavedChanges = hasCanvasChanges || hasFooterChanges` and prompt the user to confirm before discarding. `BpmnCanvas` exposes its own dirty state via `onDirtyChange?: (dirty: boolean) => void` so the parent can combine canvas content edits with footer edits into a single guard.

### `applyRonlAttr` helper

A single helper consolidates the four duplicated XML-mutation snippets that previously lived in each footer handler. It ensures the `xmlns:ronl=` namespace is declared on `<definitions>`, then either rewrites an existing `ronl:<attr>=` value, injects a new attribute on the `<bpmn:process>` opening tag, or strips the attribute when the value is `undefined`:

```typescript
function applyRonlAttr(xml: string, attr: string, value: string | undefined): string;
```

`handleSaveProcess` calls it once per draft field present (`language`, `organization`, `ropaRef`, `dsoActiviteitUrn`).

### Shell → subprocess atomic save

After saving a shell, `handleSaveProcess` walks `processes` for subprocesses where `processRole === 'subprocess'` and the record links back to this shell. The link is matched on **`shellId` where the record has one**, falling back to `calledElement === shell.bpmnProcessId` for records saved before `shellId` existed — two shell records can share a `bpmnProcessId` (an `e2e-fixtures` copy deliberately keeps a seeded example's production Operaton key), so matching on that string alone would cascade one shell's `language` and `organization` onto an unrelated shell's subprocess. For each match, the shell's `language` and `organization` are applied to the subprocess XML (via `applyRonlAttr`) and to the in-memory `BpmnProcess` fields, then persisted via `BpmnService.saveProcess` in sequence. The propagation triggers on every shell save when the shell has either field set, regardless of whether the user touched the footer in this session — the architectural rule "shell wins" must hold across editing sessions.

Idempotent: subprocesses already aligned on both fields are skipped (no `updatedAt` bump, no backend write). Records marked `readonly` are skipped. The only seeded readonly record is `example_dvtp_toestemming`, a standalone process, so in practice no seeded subprocess is skipped: the seeded example subprocesses are **not** read-only and do receive the propagation. RoPA and DSO are NOT propagated — each subprocess has its own RoPA record and DSO context.

---

## Testing checklist

After changes to any BPMN Modeler component:

- [ ] Create new process — process appears in list, empty canvas with start event
- [ ] Rename process — double-click list item, save on blur
- [ ] Delete process — confirmation dialog, list updates
- [ ] Cannot delete example — delete button disabled with tooltip
- [ ] Save — process persists across hard refresh
- [ ] Export — `.bpmn` file downloads with valid XML
- [ ] Drag element from palette — element appears on canvas
- [ ] Connect elements — arrow tool works
- [ ] Select element — properties panel updates
- [ ] BusinessRuleTask selected — DMN/DRD dropdown appears and loads
- [ ] DRD selected — purple info card shows chain composition
- [ ] Single DMN selected — blue info card shows identifier
- [ ] UserTask with a form — attach two document templates: two chips, the badge reads **2 documents**, removing a chip updates the badge
- [ ] Deploy modal — lists every `.document` named by `ronl:documentRef` and `ronl:signatureRef`; a missing form or document disables Deploy
- [ ] Process selected — **Own phases**: add, rename, recode, reorder and remove a phase; one undo takes back each edit
- [ ] Node selected — **Start van fase** sets and clears a marker; the canvas badge turns solid or outlined within a moment
- [ ] Deploy modal — own phases plus an `ronl:awbPhase` marker shows the red finding and disables Deploy
- [ ] New process — gets a process id of its own; importing a BPMN whose id the organisation already uses asks to replace or rename
- [ ] Scroll to zoom — wheel event zooms without requiring Ctrl
- [ ] Fit to viewport — canvas centres diagram
- [ ] No rendering artifacts during drag — no black circles or stray lines
