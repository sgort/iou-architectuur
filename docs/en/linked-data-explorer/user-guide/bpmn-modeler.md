---
component: Linked Data Explorer
---

# BPMN Modeler

The BPMN Modeler lets you design government service workflows and link decision model references directly to DMNs and DRDs you have discovered or saved in the Chain Builder.

---

## Opening the Modeler

Click the Workflow icon in the left sidebar. The Modeler opens with the process list on the left, the canvas in the centre, and the properties panel on the right.

On your first visit, the Modeler seeds its example processes and opens the first of them, the **AWB Generic Process**. The examples demonstrate complete government workflows and serve as a reference — examine them before creating your own processes.

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

!!! warning "Under an organization, `latest` can be ambiguous"
    `latest` looks the form key up across the whole engine. Once the same form is
    deployed under more than one organization (tenant), Operaton cannot choose and
    refuses with `ENGINE-03109`. The seeded examples therefore use
    `camunda:formRefBinding="deployment"`, which takes the form from the process's
    own deployment. The dropdown always writes `latest`; to use `deployment`, edit
    the attribute in the BPMN XML by hand.

To unlink a form, open the dropdown and select the blank option at the top.

---

## Linking a UserTask to document templates

Select a **UserTask**. Below the form selector, the properties panel shows **Link decision templates**.

1. Pick a template from **-- Add a template --**. It appears as a chip above the select, and the select stops offering it.
2. Add more templates the same way when the task produces several documents.
3. Remove one with the **✕** on its chip.

A **purple badge** below the task on the canvas names the template, or reads **2 documents** (or more) when several are attached; hover it to see every id. The badge shows only on a task that also has a form linked. See [Document template linking](../features/bpmn-modeler.md#document-template-linking).

!!! tip "Form not in the list?"
    Open the **Form Editor** view and create or save the form first. Forms appear in the dropdown immediately after saving — no page reload required.

---

## Deploying to Operaton

The Modeler can deploy your process — including subprocess BPMNs, linked forms and document templates — to Operaton in a single step.

Click the **Deploy** button in the canvas toolbar. The deploy modal opens and lists:

  - The current BPMN file
  - Any subprocess BPMNs it calls via `calledElement` (resolved from your saved processes)
  - All `.form` files whose IDs match `camunda:formRef` references in the bundle
  - All `.document` files whose IDs match `ronl:documentRef` references — several per task where a task carries several — or `ronl:signatureRef` references in the bundle

The modal also has a required **Board ownership** section. It auto-detects the owning board from the process's candidate groups — infra/rip groups → **Infra-board**, caseworker/hr groups → **Caseworker** — and lets you override the choice. The selected board is stamped onto the deployed BPMN as a process-level `camunda:property boardOwner`, persisted with the process, and exposed via `/bundles/public` so downstream consumers (the ronl-business-api Procesbibliotheek and archive split) can read which board owns the process.

!!! note "DMNs are not part of the deploy bundle"
    Decision models referenced via `camunda:decisionRef` on `BusinessRuleTask` elements are **not** included in this deployment. DMNs reach Operaton through a separate path: they are published to TriplyDB by the [CPSV Editor](../../cpsv-editor/index.md) and deployed to Operaton from there. The BPMN process resolves `camunda:decisionRef` at runtime against whatever is already deployed — as long as the DMN key matches, no additional action is needed here. A process deployed under an organization reaches a shared DMN deployed without one only when its business rule task carries `camunda:decisionRefTenantId="${null}"`, as the seeded examples do.
 
<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Deploy modal showing the bundle's seven resources — two BPMN files, four forms and a document — with an amber warning that the bundle mixes languages, plus the required Board ownership section with the auto-detected board and an override control, the line naming the Operaton it deploys to, and a Deploy button at the bottom](../../assets/screenshots/linked-data-explorer-bpmn-deploy-modal.png)
  <figcaption>Deploy modal showing the complete bundle and the Board ownership section before committing to Operaton</figcaption>
</figure>

1. Review the resource list. A form or document template the process references but this browser does not have is listed under **⛔ Referenced resources are missing from local storage**, and **Deploy** stays disabled until you import it in the Form Editor or the Document Composer.
2. Read any amber warning. **Bundle mixes languages** means the artefacts carry more than one `ronl:language` tag — in the figure, the seeded Kapvergunning bundle, whose new missing-information form is tagged `nl` and the rest `en`. It does not stop the deploy, but a deployed bundle should be one language: retag or untag the odd one out first. A missing `ronl:ropaRef` gets a warning of the same kind.
3. Check the **Board ownership** section — accept the auto-detected board or override it. A board owner is required to deploy.
4. Check the **Organization**. It comes from the sidebar's **Organization** field once the process is saved, and it is **required** — the deploy will not submit without one. It is sent to Operaton as the deployment's tenant-id, so a process deployed without it would be invisible to any tenant-scoped lookup made later.
5. Check the line **Deploys to …**, which names the Operaton the process will reach. You do not choose it here: the backend always deploys to its own configured Operaton, with its own credentials.
6. Click **Deploy**. The Linked Data Explorer backend posts all resources to Operaton in one multipart deployment.
7. On success, a deployment ID is shown and the Deploy button is disabled to prevent accidental re-deploy.

If the result shows as a **warning** rather than a tick, the deployment succeeded but the process could not be recorded, and the message says why. It will not appear on the caseworker dashboard or the public site until you save it and deploy it again.

Because the BPMN and all its forms and document templates land in the same Operaton deployment, `camunda:formRef` resolves correctly at runtime with no additional steps.

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

Seeded example processes are fetched from `public/examples/` on the frontend. They are editable and are written to the database when saved, like your own processes — except the DvTP example, the one seeded record marked `readonly`, which stays in local storage only.

See [Asset Storage](../developer/asset-storage.md) for the full architecture.

Click **Export** to download a `.bpmn` file for deployment to Operaton. You can also deploy directly from the Modeler using the **Deploy** button. See [Deploying to Operaton](#deploying-to-operaton) above.

---

## The Tree Felling Permit example

The **Tree Felling Permit** example is the Kapvergunning subprocess the AWB Generic Process calls in its phase *Fase 4+5: Behandeling en besluit*. It is drawn in the pool *Kapvergunning - Behandeling en besluit* with two lanes, **Behandelaar** and **Systeem**, and demonstrates:

- `BusinessRuleTask` *Kapvergunning beoordelen (APV)*, linked to `TreeFellingDecision`
- `BusinessRuleTask` *Herplantplicht beoordelen*, linked to `ReplacementTreeDecision`
- `UserTask` *Beoordeling behandelaar: besluit kapvergunning* in the Behandelaar lane, with a form and a document template linked
- `ExclusiveGateway` *Vergunning verleend?* routing on the final decision
- One end event, *Besluit gereed*

The application itself is submitted in the shell, through its start form. To use the example as a starting point, export it and import the copy as a new process.

---

## AWB shell and subprocess examples

The process library ships with three AWB shell processes and their subprocesses. Each is drawn as a pool with lanes and carries Dutch element names: a shell has the lanes **Aanvrager**, **Behandelaar** and **Systeem**; a subprocess has only **Behandelaar** and **Systeem**, because it has no step for the applicant.

**AWB Generic Process** (`SHELL`) — the universal eight-phase AWB procedural shell for the Kapvergunning (tree felling permit). Calls `TreeFellingPermitSubProcess` via a Call Activity at Phase 4+5.

└── **Tree Felling Permit** (`SUB`) — evaluates the substantive tree felling decision and routes to caseworker review.

**AWB Zorgtoeslag — Provisional Entitlement** (`SHELL`) — AWB shell wired for the Zorgtoeslag provisional entitlement subprocess.

└── **Zorgtoeslag — Provisional Entitlement** (`SUB`) — evaluates the `resultaat_zorgtoeslag` DMN and routes to caseworker review.

└── **Zorgtoeslag — Final Settlement** (`SUB`) — started via the `FinalIncomeReceived` message event once final annual income data arrives from Belastingdienst. Evaluates confirmed income and sets the settlement outcome.

**Subsidie Thuisbatterij Flevoland** (`SHELL`) — AWB shell for the Provincie Flevoland home-battery subsidy.

└── **Thuisbatterijsubsidie — Beoordeling recht en hoogte** (`SUB`) — evaluates entitlement and amount, and routes to caseworker review.

**Asking for missing information.** When an application is incomplete, each shell opens the task *Aanvullende gegevens opvragen (Awb 4:5)* with its own form — `kapvergunning-aanvullende-gegevens`, `zorgtoeslag-aanvullende-gegevens` or `thuisbatterij-aanvullende-gegevens`. Its **supplementReceived** checkbox decides the next gateway, *Aanvulling ontvangen?*: the case continues, or the application is not processed. The form deploys with the shell like its other forms.

---

## Standalone examples

Three examples are standalone processes, with no shell:

- **Beheer capaciteitsclaim — proces (Voorbeeld, NL)** — the Dutch HR capacity claim, drawn in eight lanes and declaring eight phases of its own. See [Multilingualism](multilingualism.md).
- **Besluitvorming onder gedelegeerde bevoegdheid (Voorbeeld, NL)** — a decision prepared, reviewed, signed through ValidSign or escalated, then registered and archived, in six lanes and six phases. See [Besluitvorming onder gedelegeerde bevoegdheid](../features/besluitvorming-gedelegeerd-bundle.md).
- **DvTP — Flow A: Toestemming geven** — the DvTP consent process.

The lanes and phases are what the RONL Business API shows a caseworker; see [Lanes and phase markers](../../ronl-business-api/reference/bpmn-design-criteria.md#lanes-and-phase-markers-the-caseworker-process-view).

All seeded examples carry the `EXAMPLE` badge and cannot be deleted. They can be edited and saved, but a later example update replaces your edits, so to keep a change, export the process and import the copy as a new process.