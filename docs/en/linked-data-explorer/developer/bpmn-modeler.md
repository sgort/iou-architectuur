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
├── FormTemplateSelector.tsx   Form dropdown for UserTask / StartEvent linking  ← new in v1.0.0
└── BpmnModeler.css            custom styles for canvas rendering fixes and badge overlays

packages/frontend/src/
├── services/
│   ├── bpmnService.ts         localStorage CRUD for BpmnProcess records
│   └── formService.ts         localStorage CRUD for FormSchema records (shared with FormEditor)
└── utils/
    └── bpmnTemplates.ts       default BPMN XML templates (new process, example)
```

---

## Canvas initialisation

`BpmnCanvas.tsx` manages the bpmn-js modeler instance lifecycle:

```typescript
const modeler = new Modeler({
  container: containerRef.current,
  moddleExtensions: {
    camunda: camundaModdleDescriptor,
  },
});

await modeler.importXML(xml);
const canvas = modeler.get('canvas');
canvas.zoom('fit-viewport');
```

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
  'camunda:formRefBinding': 'latest',
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

When any `UserTask` or `StartEvent` has `camunda:formRef` set, `BpmnCanvas.tsx` renders a green badge overlay below the element using the bpmn-js `overlays` service. This is applied on `import.done` and on every `element.changed` event.

```typescript
overlays.add(element.id, 'form-linked', {
  position: { bottom: -22, left: leftOffset },
  html: `<div class="form-linked-badge" title="${formRef}">📝 ${formRef}</div>`,
});
```

The badge offset uses `leftOffset = Math.round((element.width - badgeWidth) / 2)` to centre the badge horizontally beneath the element. A separate CSS class `form-linked-badge--start` applies smaller font/padding for `StartEvent` elements, which have a narrower default width.

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

## Deploy modal

The deploy modal is triggered by the **Deploy** button in the canvas toolbar. `BpmnCanvas.tsx` assembles the resource bundle before opening the modal:

### Resource collection

```typescript
// 1. Save current BPMN to get latest XML
const { xml } = await modelerRef.current.saveXML({ format: true });

// 2. Extract subprocess calledElement references (recursive)
const calledElements = extractCalledElements(xml);
// → match against saved BpmnProcess records by process/@id

// 3. Extract all camunda:formRef values from main + subprocess XMLs
const allFormRefs = new Set([
  ...extractFormRefs(xml),
  ...subProcessXmls.flatMap(sp => extractFormRefs(sp.xml)),
]);

// 4. Match form refs against FormService.getForms() by schema.id
const forms = allFormRefs → matched FormSchema records
```

Unmatched form refs (referenced in BPMN but not in localStorage) are passed to the modal as `unmatchedForms` for display.

### API call

On **Deploy**, `BpmnCanvas.tsx` sends a JSON body to the backend:

```typescript
await fetch(`${API_BASE_URL}/api/dmns/process/deploy`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    bpmnXml: xml,
    deploymentName: processKey,   // from BPMN process/@id
    forms,                        // [{ id, schema }]
    subProcesses,                 // [{ filename, xml }]
    operatonUrl,                  // from modal field
    operatonUsername,
    operatonPassword,
  }),
});
```

### Backend endpoint

`POST /api/dmns/process/deploy` (in `dmn.routes.ts`) delegates to `operatonService.deployProcess()`. That method builds a `multipart/form-data` request with each resource appended as a named field matching Camunda Modeler behaviour:

- Main BPMN: field name = `${processKey}.bpmn`
- Subprocess BPMNs: field name = the subprocess filename
- Forms: field name = `${formId}.form`

A custom Operaton URL in the request body causes `deployProcess()` to construct a new Axios client targeting that URL, with optional Basic Auth credentials, instead of using the default `OPERATON_BASE_URL` from the backend environment.

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

### DmnTemplateSelector pre-selection fix

Before v1.0.0, opening the properties panel for a `BusinessRuleTask` that already had `camunda:decisionRef` set would show an empty dropdown. The fix reads `currentDecisionRef` from `businessObject.get('camunda:decisionRef')` and passes it as `selectedDecisionRef` to `DmnTemplateSelector`, which initialises its `useState` from that prop.

---

## Process persistence (localStorage)

`bpmnService.ts` stores processes as `BpmnProcess` records:

```typescript
interface BpmnProcess {
  id: string;
  name: string;
  xml: string;
  createdAt: string;
  updatedAt: string;
  linkedDmnTemplates: string[];
  readonly?: boolean;
}
```

`readonly: true` marks the Tree Felling Permit example; its delete button is disabled in `ProcessList.tsx`.

---

## Tree Felling Permit example auto-loading

On first mount (empty localStorage), `bpmnService.ts` calls `seedExampleProcess()` which writes the example process using the template from `bpmnTemplates.ts`. The example is always protected by `readonly: true`.

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
- [ ] Scroll to zoom — wheel event zooms without requiring Ctrl
- [ ] Fit to viewport — canvas centres diagram
- [ ] No rendering artifacts during drag — no black circles or stray lines
