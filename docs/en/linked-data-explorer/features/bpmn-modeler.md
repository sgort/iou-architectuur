# BPMN Modeler

The BPMN Modeler is a full BPMN 2.0 process editor integrated into the Linked Data Explorer. It lets you design government service workflows visually and link `BusinessRuleTask` elements directly to DMN decision models or DRD chains discovered from TriplyDB.

<figure markdown>
  ![Screenshot: BPMN Modeler showing the Tree Felling Permit example with properties panel open](../../assets/screenshots/linked-data-explorer-bpmn-modeler.png)
  <figcaption>BPMN Modeler showing the Tree Felling Permit example with properties panel open</figcaption>
</figure>

---

## Three-panel layout

The Modeler uses the same three-panel layout as the Chain Builder:

- **Left panel** — Process list. Shows all saved processes with create, rename, and delete actions. An EXAMPLE badge marks protected processes that cannot be deleted.
- **Centre panel** — Canvas. Interactive BPMN 2.0 canvas powered by bpmn-js, with drag-and-drop palette, zoom controls, and scroll-to-zoom.
- **Right panel** — Properties. Shows element type, ID, name field, and — for `BusinessRuleTask` elements — the DMN/DRD decision reference section.

---

## BPMN palette

The palette provides all standard BPMN 2.0 elements: start, intermediate, and end events; tasks (including business rule tasks); gateways (exclusive, parallel, inclusive, event-based); sub-processes; data objects; pools; and text annotations.

---

## DMN/DRD linking

When a `BusinessRuleTask` is selected in the properties panel, a **Link to DMN/DRD** dropdown appears. It loads options from two sources simultaneously:

- **DRDs (Unified Chains)** — DRD templates saved locally from the Chain Builder
- **Single DMNs** — individual decision models from the active TriplyDB endpoint

Selecting an option auto-populates `camunda:decisionRef` with the correct identifier and suggests a value for `camunda:resultVariable`. A visual info card below the dropdown confirms the selection, with purple styling for DRDs and blue for single DMNs. DRD cards also show the chain composition (which DMNs the DRD combines).

---

## Export

Processes can be exported as `.bpmn` files for deployment to Operaton. The XML uses `camunda:` namespace attributes, which Operaton accepts for compatibility with the Camunda 7 ecosystem.

---

## Tree Felling Permit example

On first launch, the Modeler auto-creates the **Tree Felling Permit** example process, demonstrating a complete municipal workflow: application submission, two `BusinessRuleTask` elements linked to DMN decision models (`TreeFellingDecision`, `ReplacementTreeDecision`), an exclusive gateway routing to permit granted or rejected outcomes. The example is protected from deletion and serves as a reference for process designers.

---

## Engine compatibility

The Modeler targets Operaton, the open-source fork of Camunda 7 CE. It uses `camunda-bpmn-moddle` for namespace support since no `operaton-bpmn-moddle` package exists yet. Operaton accepts both `camunda:` and `operaton:` namespace attributes, ensuring compatibility.
