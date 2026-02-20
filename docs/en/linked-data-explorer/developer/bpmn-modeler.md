# BPMN Modeler Implementation

The BPMN Modeler wraps the `bpmn-js` library in a three-panel React component. This page covers the component structure, the canvas setup decisions, and known rendering issues with their fixes.

---

## Component structure

```
packages/frontend/src/components/BpmnModeler/
├── BpmnModeler.tsx           main orchestrator, manages selected process state
├── BpmnCanvas.tsx            bpmn-js canvas wrapper (modeler lifecycle)
├── BpmnProperties.tsx        properties panel (right), includes DmnTemplateSelector
├── ProcessList.tsx           process list (left), CRUD operations
├── DmnTemplateSelector.tsx   DMN/DRD dropdown for BusinessRuleTask linking
└── BpmnModeler.css           custom styles for canvas rendering fixes

packages/frontend/src/
├── services/
│   └── bpmnService.ts        localStorage CRUD for BpmnProcess records
└── utils/
    └── bpmnTemplates.ts      default BPMN XML templates (new process, example)
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
