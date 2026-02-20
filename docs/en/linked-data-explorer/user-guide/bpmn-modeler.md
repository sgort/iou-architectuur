# BPMN Modeler

The BPMN Modeler lets you design government service workflows and link decision model references directly to DMNs and DRDs you have discovered or saved in the Chain Builder.

---

## Opening the Modeler

Click the Workflow icon in the left sidebar. The Modeler opens with the process list on the left, the canvas in the centre, and the properties panel on the right.

On your first visit, the **Tree Felling Permit** example process loads automatically. It demonstrates a complete municipal workflow and serves as a reference — examine it before creating your own processes.

---

## Creating a process

1. Click the blue **+** button at the top of the process list.
2. A new process named "New Process" appears in the list and the canvas shows an empty diagram with a start event.
3. Double-click the process name in the list to rename it.

---

## Building a diagram

Drag elements from the palette on the left edge of the canvas onto the diagram area. Connect elements by clicking the source element and dragging the blue arrow handle that appears on hover to the target element.

Available element types: start events, intermediate events, end events, tasks (user, service, business rule), gateways (exclusive, parallel, inclusive, event-based), sub-processes, data objects, pools, and text annotations.

---

## Linking a BusinessRuleTask to a decision

Select a **BusinessRuleTask** on the canvas. The properties panel on the right shows the element details, including a **DMN/DRD Decision Reference** section.

![Screenshot: BPMN properties panel with the Link to DMN/DRD dropdown open showing DRD and single DMN options](../../assets/screenshots/linked-data-explorer-bpmn-dmn-dropdown.png)

1. Click **Link to DMN/DRD** to open the dropdown.
2. The dropdown shows two groups:
   - **🔗 DRDs (Unified Chains)** — DRD templates saved from the Chain Builder
   - **📋 Single DMNs** — individual decision models from the active TriplyDB endpoint
3. Select an option. The `camunda:decisionRef` field auto-populates with the correct identifier and a suggested `camunda:resultVariable` value appears.
4. An info card confirms your selection. DRD cards show the constituent DMNs the DRD combines; single DMN cards show the decision identifier.

---

## Editing element properties

- **Name**: editable in the right properties panel for any selected element
- **Element ID**: shown read-only (managed by bpmn-js)
- **BusinessRuleTask specific**: `camunda:decisionRef`, `camunda:resultVariable`, `camunda:mapDecisionResult`

---

## Zoom and navigation

- **Scroll wheel** — zoom in and out
- **+ / − buttons** in the toolbar — zoom in/out in steps
- **Fit to viewport** button — centres and scales the diagram to fill the canvas
- **Click and drag** on empty canvas — pan

---

## Saving and exporting

Click **Save** in the canvas toolbar to persist the current process to browser local storage. Click **Export** to download a `.bpmn` file for deployment to Operaton.

!!! note
    Processes are stored in browser `localStorage`. They are not shared between browsers or users. Export processes you want to keep before clearing browser storage.

---

## The Tree Felling Permit example

The example process cannot be deleted. It demonstrates:

- `UserTask` for application submission
- `BusinessRuleTask` (Assess Felling Permit) linked to `TreeFellingDecision`
- `ExclusiveGateway` routing on the decision outcome
- `BusinessRuleTask` (Assess Replacement Requirement) linked to `ReplacementTreeDecision`
- Two end events: Permit Granted and Permit Rejected

To use it as a starting point, export it, create a new process, and paste the exported XML.
