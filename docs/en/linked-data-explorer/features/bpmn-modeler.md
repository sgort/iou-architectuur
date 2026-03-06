# BPMN Modeler

The BPMN Modeler is a full BPMN 2.0 process editor integrated into the Linked Data Explorer. It lets you design government service workflows visually, link `BusinessRuleTask` elements to DMN decision models or DRD chains, link `UserTask` and `StartEvent` elements to Camunda Forms authored in the Form Editor, and deploy the complete bundle — BPMN, subprocess BPMNs, and forms — to Operaton in a single operation.

<figure markdown style="width:100%; margin:0;">
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

## Form linking

When a `UserTask` or `StartEvent` is selected, the properties panel shows a **Link to Form** dropdown in addition to the standard element fields. The dropdown lists every form currently stored in the Form Editor's `localStorage`.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: BPMN canvas showing a StartEvent and a UserTask each with a green form-linked badge displaying the linked form ID](../../assets/screenshots/linked-data-explorer-bpmn-form-badge.png)
  <figcaption>Green badges on StartEvent and UserTask elements indicate a linked Camunda Form</figcaption>
</figure>

Selecting a form writes two attributes to the BPMN XML:

```xml
camunda:formRef="kapvergunning-start"
camunda:formRefBinding="latest"
```

`camunda:formRefBinding="latest"` instructs Operaton to always resolve the most recently deployed version of that form ID, eliminating the need for version pinning.

A **green badge** appears below the element on the canvas once a form is linked, showing the form ID. The badge colour distinguishes form links (green) from DMN decision links (blue).

To remove a form link, open the **Link to Form** dropdown and select the blank option at the top.

---

## One-click deploy

The **Deploy** button in the Modeler toolbar opens a deploy modal that collects all resources needed for a complete Operaton deployment:

1. The currently open BPMN file
2. Any subprocess BPMNs referenced via `calledElement` attributes (resolved recursively from saved processes)
3. All `.form` files whose `id` matches a `camunda:formRef` found anywhere in the bundle

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Deploy modal showing the bundled resources list — main BPMN, two subprocess BPMNs, and three .form files — with the Operaton endpoint field and Deploy button](../../assets/screenshots/linked-data-explorer-bpmn-deploy-modal.png)
  <figcaption>Deploy modal listing the complete bundle before sending to Operaton</figcaption>
</figure>

All resources are sent in a single multipart `POST` to Operaton. Because the BPMN and its forms share one deployment ID, `camunda:formRef` resolves correctly at runtime — no separate form deployment step is needed.

The modal provides:

- **Operaton endpoint** — pre-filled from `VITE_OPERATON_BASE_URL`, editable per deployment
- **Username / Password** — optional HTTP Basic Auth for instances that require it
- **Resource list** — shows exactly what will be included before you commit
- **Deploy button** — disabled after a successful deployment to prevent accidental re-deploy

If a `camunda:formRef` references a form ID that is not found in `localStorage`, it is listed as an unmatched reference. The deployment still proceeds, but that form will not resolve at runtime.

---

## Tree Felling Permit example

On first launch, the Modeler auto-creates the **Tree Felling Permit** example process, demonstrating a complete municipal workflow: application submission, two `BusinessRuleTask` elements linked to DMN decision models (`TreeFellingDecision`, `ReplacementTreeDecision`), an exclusive gateway routing to permit granted or rejected outcomes. The example is protected from deletion and serves as a reference for process designers.

---

## Engine compatibility

The Modeler targets Operaton, the open-source fork of Camunda 7 CE. It uses `camunda-bpmn-moddle` for namespace support since no `operaton-bpmn-moddle` package exists yet. Operaton accepts both `camunda:` and `operaton:` namespace attributes, ensuring compatibility.

The Modeler targets Operaton, the open-source fork of Camunda 7 CE. It uses `camunda-bpmn-moddle` for namespace support since no `operaton-bpmn-moddle` package exists yet. The `camunda:formRef` and `camunda:formRefBinding` attributes used for form linking are also accepted by Operaton under the `camunda:` namespace.
