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

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: BPMN properties panel with the Link to DMN/DRD dropdown open showing DRD and single DMN options](../../assets/screenshots/linked-data-explorer-bpmn-dmn-dropdown.png)
  <figcaption>BPMN properties panel with the Link to DMN/DRD dropdown open showing DRD and single DMN options</figcaption>
</figure>

1. Click **Link to DMN/DRD** to open the dropdown.
2. The dropdown shows two groups:
   - **🔗 DRDs (Unified Chains)** — DRD templates saved from the Chain Builder
   - **📋 Single DMNs** — individual decision models from the active TriplyDB endpoint
3. Select an option. The `camunda:decisionRef` field auto-populates with the correct identifier and a suggested `camunda:resultVariable` value appears.
4. An info card confirms your selection. DRD cards show the constituent DMNs the DRD combines; single DMN cards show the decision identifier.

---

## Linking a UserTask or StartEvent to a form

`UserTask` and `StartEvent` elements can be linked to Camunda Forms authored in the [Form Editor](form-editor.md). Once linked, Operaton renders the form at runtime for the citizen or caseworker assigned to that task.

Select a **UserTask** or **StartEvent** on the canvas. The properties panel shows a **Link to Form** section beneath the standard element fields.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: BPMN properties panel open for a UserTask showing the Link to Form dropdown with a list of available forms](../../assets/screenshots/linked-data-explorer-bpmn-form-link-dropdown.png)
  <figcaption>Link to Form dropdown in the properties panel for a UserTask</figcaption>
</figure>

1. Click the **Link to Form** dropdown. It lists all forms currently saved in the Form Editor.
2. Select the form you want to link.
3. A confirmation card appears below the dropdown showing the form name and the resulting `camunda:formRef` value.
4. A **green badge** appears below the element on the canvas, confirming the link.

The dropdown writes `camunda:formRef` and `camunda:formRefBinding="latest"` into the BPMN XML. `binding: latest` means Operaton always uses the most recently deployed version of that form — you do not need to pin a specific version.

To unlink a form, open the dropdown and select the blank option at the top.

!!! tip "Form not in the list?"
    Open the **Form Editor** view and create or save the form first. Forms appear in the dropdown immediately after saving — no page reload required.

---

## Deploying to Operaton

The Modeler can deploy your process — including subprocess BPMNs and linked forms — to Operaton in a single step.

Click the **Deploy** button in the canvas toolbar. The deploy modal opens and lists:

  - The current BPMN file
  - Any subprocess BPMNs it calls via `calledElement` (resolved from your saved processes)
  - All `.form` files whose IDs match `camunda:formRef` references in the bundle
  - All `.document` files whose IDs match `ronl:documentRef` references in the bundle
 
!!! note "DMNs are not part of the deploy bundle"
    Decision models referenced via `camunda:decisionRef` on `BusinessRuleTask` elements are **not** included in this deployment. DMNs reach Operaton through a separate path: they are published to TriplyDB by the [CPSV Editor](../../cpsv-editor/index.md) and deployed to Operaton from there. The BPMN process resolves `camunda:decisionRef` at runtime against whatever is already deployed — as long as the DMN key matches, no additional action is needed here.
 
<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Deploy modal showing three sections — BPMN file, subprocess BPMNs, and form files — with the Operaton endpoint field pre-filled and a Deploy button at the bottom](../../assets/screenshots/linked-data-explorer-bpmn-deploy-modal.png)
  <figcaption>Deploy modal showing the complete bundle before committing to Operaton</figcaption>
</figure>

1. Review the resource list. If a referenced form ID is shown as unmatched, open the Form Editor and save a form with that ID before deploying.
2. Confirm or edit the **Operaton endpoint** URL. It is pre-filled from the environment configuration.
3. If your Operaton instance requires authentication, enter the **Username** and **Password**.
4. Click **Deploy**. All resources are sent in one multipart request.
5. On success, a deployment ID is shown and the Deploy button is disabled to prevent accidental re-deploy.

Because the BPMN and all its forms land in the same Operaton deployment, `camunda:formRef` resolves correctly at runtime with no additional steps.

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

## Storage

Processes are stored in PostgreSQL via the LDE backend and cached in browser `localStorage` for instant access. On editor load, the service fetches the authoritative list from the server and replaces the local cache. If the backend is unreachable, the local cache is used as a fallback without any error surfaced to the user.

Example processes (`readonly: true`) are seeded from `public/examples/` on the frontend and are never written to the database.

See [Asset Storage](../developer/asset-storage.md) for the full architecture.

Click **Export** to download a `.bpmn` file for deployment to Operaton. You can also deploy directly from the Modeler using the **Deploy** button. See [Deploying to Operaton](#deploying-to-operaton) above.

---

## The Tree Felling Permit example

The example process cannot be deleted. It demonstrates:

- `UserTask` for application submission
- `BusinessRuleTask` (Assess Felling Permit) linked to `TreeFellingDecision`
- `ExclusiveGateway` routing on the decision outcome
- `BusinessRuleTask` (Assess Replacement Requirement) linked to `ReplacementTreeDecision`
- Two end events: Permit Granted and Permit Rejected

To use it as a starting point, export it, create a new process, and paste the exported XML.

---

## AWB shell and subprocess examples

The process library ships with two AWB shell processes and their subprocesses:

**AWB Generic Process** (`SHELL`) — the universal eight-phase AWB procedural shell for the Kapvergunning (tree felling permit). Calls `TreeFellingPermitSubProcess` via a Call Activity at Phase 4+5.

└── **Tree Felling Permit** (`SUB`) — evaluates the substantive tree felling decision and routes to caseworker review.

**AWB Zorgtoeslag — Provisional Entitlement** (`SHELL`) — AWB shell wired for the Zorgtoeslag provisional entitlement subprocess.

└── **Zorgtoeslag — Provisional Entitlement** (`SUB`) — validates application, retrieves income data, evaluates the `resultaat_zorgtoeslag` DMN, and routes to caseworker review.

└── **Zorgtoeslag — Final Settlement** (`SUB`) — started via the `FinalIncomeReceived` message event once final annual income data arrives from Belastingdienst. Evaluates confirmed income and sets the settlement outcome.

All example processes are protected (`EXAMPLE` badge, delete disabled). To use one as a starting point, export it and import the copy as a new process.