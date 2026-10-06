---
component: Linked Data Explorer
---

# BPMN Modeler

The BPMN Modeler is a full BPMN 2.0 process editor integrated into the Linked Data Explorer. It lets you design government service workflows visually, link `BusinessRuleTask` elements to DMN decision models or DRD chains, link `UserTask` and `StartEvent` elements to Camunda Forms authored in the Form Editor, link `UserTask` elements to document templates authored in the Document Composer, and deploy the complete bundle — BPMN, subprocess BPMNs, forms and document templates — to Operaton in a single operation.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: BPMN Modeler showing the Tree Felling Permit example — the Kapvergunning subprocess drawn in the pool Kapvergunning - Behandeling en besluit, with the lanes Behandelaar and Systeem and Dutch element names such as Kapvergunning beoordelen (APV) and Herplantplicht beoordelen — with the properties panel open](../../assets/screenshots/linked-data-explorer-bpmn-modeler.png)
  <figcaption>BPMN Modeler showing the Kapvergunning subprocess in its Behandelaar and Systeem lanes, with the properties panel open</figcaption>
</figure>

---

## Three-panel layout

The Modeler uses the same three-panel layout as the Chain Builder:

- **Left panel** — Process list. Shows all saved processes with create, rename, and delete actions. An EXAMPLE badge marks protected processes that cannot be deleted.
- **Centre panel** — Canvas. Interactive BPMN 2.0 canvas powered by bpmn-js, with drag-and-drop palette, zoom controls, and scroll-to-zoom.
- **Right panel** — Properties. Shows element type, ID, name field, and — for `BusinessRuleTask` elements — the DMN/DRD decision reference section.

---

## Process library

The left panel lists all processes grouped by their role in the AWB shell pattern.

### Shell / subprocess hierarchy

The Linked Data Explorer models government service workflows as two-layer BPMN compositions: a universal **AWB shell** process handles the eight statutory procedural phases, and a product-specific **subprocess** delivers the substantive decision via a Call Activity. The process list reflects this structure visually.

Shell processes are top-level entries. Their subprocesses are indented beneath them with a tree connector. Standalone processes — those with no parent-child relationship — appear as top-level entries without indentation.

!!! note "Automatic shell/subprocess linking"
    Uploaded BPMN processes that form a shell/subprocess pair are linked automatically: a process containing Call Activity elements is classified as a **shell**, and any process whose BPMN process ID is targeted by a shell's call-activity becomes its **subprocess**. Classification runs both on fresh imports and on startup, so a process stored as standalone is reclassified without needing a re-upload.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: BPMN Modeler process list showing AWB Generic Process with Tree Felling Permit indented below it as a subprocess, and AWB Zorgtoeslag with its two subprocesses indented below it](../../assets/screenshots/linked-data-explorer-bpmn-process-hierarchy.png)
  <figcaption>Process list showing shell/subprocess hierarchy: AWB shells with their subprocesses indented</figcaption>
</figure>

### Role badges

Each process card carries one or more badges:

| Badge | Colour | Meaning |
|---|---|---|
| `EXAMPLE` | Blue | Seeded example — editable, but cannot be deleted |
| `WIP` | Amber | Work in progress, such as the seeded Migration & Asylum Procedure |
| `SHELL` | Violet | AWB shell process — calls one or more subprocesses via a Call Activity |
| `SUB` | Teal | Subprocess — called by a shell via its `calledElement` attribute |

### Process roles

Every `BpmnProcess` record carries three relationship fields:

| Field | Type | Description |
|---|---|---|
| `bpmnProcessId` | `string` | The `<process id="...">` value from the BPMN XML |
| `processRole` | `'shell' \| 'subprocess' \| 'standalone'` | How this process relates to others |
| `calledElement` | `string?` | For subprocesses: the `bpmnProcessId` of the parent shell |

User-created and imported processes default to `standalone`. The BPMN `<process id="...">` value is extracted automatically from the XML on save.

### Example processes

| Process | `processRole` | `calledElement` |
|---|---|---|
| AWB Generic Process | `shell` | — |
| Tree Felling Permit | `subprocess` | `AwbShellProcess` |
| AWB Zorgtoeslag — Provisional Entitlement | `shell` | — |
| Zorgtoeslag — Provisional Entitlement | `subprocess` | `AwbZorgtoeslagProcess` |
| Zorgtoeslag — Final Settlement | `subprocess` | `AwbZorgtoeslagProcess` |
| Subsidie Thuisbatterij Flevoland | `shell` | — |
| Thuisbatterijsubsidie — Beoordeling recht en hoogte | `subprocess` | `ThuisbatterijSubsidieAanvraagProcess` |
| DvTP — Flow A: Toestemming geven | `standalone` | — |
| Beheer capaciteitsclaim — proces (NL) | `standalone` | — |
| Besluitvorming onder gedelegeerde bevoegdheid (NL) | `standalone` | — |
| Migration & Asylum Procedure | `standalone` | — |

The list shows each seeded example with the suffix *(Example)*, or *(Voorbeeld, NL)* for the two Dutch ones. The Awb shells and subprocesses are drawn as pools with lanes — **Aanvrager**, **Behandelaar** and **Systeem** in a shell, **Behandelaar** and **Systeem** in a subprocess — and carry Dutch element names. The Dutch HR capacity claim has eight lanes; *Besluitvorming onder gedelegeerde bevoegdheid* has six and is described on its own page, [Besluitvorming onder gedelegeerde bevoegdheid](besluitvorming-gedelegeerd-bundle.md).

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
camunda:formRefBinding="deployment"
```

`camunda:formRefBinding="deployment"` resolves the form from the process definition's own deployment, which is unambiguous because the deploy modal ships the BPMN and its forms together. Every seeded example uses the same binding. The alternative, `latest`, looks the form key up across the whole engine, so once the same form is deployed under more than one tenant Operaton cannot choose and fails with `ENGINE-03109`.

A **green badge** appears below the element on the canvas once a form is linked, showing the form ID. The badge colour distinguishes form links (green) from DMN decision links (blue).

To remove a form link, open the **Link to Form** dropdown and select the blank option at the top.

---

## Document template linking

When a `UserTask` is selected, the properties panel shows a **Link decision templates** section below the form selector. A task can carry **several** document templates, because one step can produce more than one deliverable.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: BPMN properties panel for a UserTask under Link decision templates, showing two attached templates as purple chips, each with its name, documentRef and a remove button, the select below reading -- Add a template --, and on the canvas the task's purple badge reading 2 documents](../../assets/screenshots/linked-data-explorer-bpmn-document-template-selector.png)
  <figcaption>A task with two document templates attached: two chips, the "-- Add a template --" select, and a "2 documents" badge on the canvas</figcaption>
</figure>

- **Attached templates** appear as chips, each showing the template's name and id, with a **✕** button that removes it. A template id this browser does not know is shown as its bare id rather than hidden.
- **The select below the chips adds a template.** It lists only the templates saved in the Document Composer that are not yet attached, under **-- Add a template --**, and reads **-- All templates attached --** once none are left.

The Modeler writes the attached ids to `ronl:documentRef` as a comma-separated list — `ronl:documentRef="rip-ontwerptoelichting,rip-objectenboom"` — and removes the attribute when the last chip is removed. A BPMN with a single id is a list of one, so existing processes need no change.

A **purple badge** (📄) appears beneath the element on the canvas, below the green form badge. With one template it shows the template id; with several it reads **N documents**, and hovering it lists every id. Each badge colour stands for one kind of link:

| Badge colour | Artefact type | Attribute written |
|---|---|---|
| Blue | DMN / DRD decision | `camunda:decisionRef` |
| Green | Camunda Form | `camunda:formRef` |
| **Purple** | **Document templates** | **`ronl:documentRef`** |

Document template linking is only available for `UserTask` elements (not `StartEvent`). The purple badge is drawn only on a user task that also has a form linked.

!!! note "Hand-authored `ronl:*` attributes"
    Several `ronl:*` attributes are set by hand in the BPMN: the Modeler keeps
    them through a save but offers no control for them and shows no badge for
    them.

    - **`ronl:signatureRef`** on a user task names a document template. For
      that task the RONL Business API offers a ValidSign signing ceremony for
      the document in place of the task's plain form. The deploy modal bundles
      that template like any other. See [ValidSign signing](../../ronl-business-api/developer/validsign-signing.md)
      and [RIP R2.1 Bundle](rip-phase1-bundle.md#the-phase-exit-approval-is-signed).
    - **`ronl:awbPhase`**, **`ronl:phases`**, **`ronl:phaseLabel`** and
      **`ronl:phase`** declare a process's phases and mark the node that starts
      each one. The RONL Business API reads them to draw the caseworker's phase
      stepper — see [Lanes and phase markers](../../ronl-business-api/reference/bpmn-design-criteria.md#lanes-and-phase-markers-the-caseworker-process-view).
      A Modeler control for them is [LDE issue #242](https://github.com/sgort/linked-data-explorer/issues/242).

See [Document Composer](document-composer.md) for how to create and manage document templates.

---

## One-click deploy

The **Deploy** button in the Modeler toolbar opens a deploy modal that collects all resources needed for a complete Operaton deployment:

1. The currently open BPMN file
2. The subprocess BPMNs the open process calls through a `calledElement` attribute, matched against saved processes by their BPMN process id. A called element that no saved process provides is left out, and Operaton reports it when the process starts
3. All `.form` files whose `id` matches a `camunda:formRef` found anywhere in the bundle
4. All `.document` files whose id is named by a `ronl:documentRef` — which can list several per task — or by a `ronl:signatureRef`, anywhere in the bundle

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Deploy modal over the Kapvergunning swimlane canvas, listing seven resources — two BPMN files, four .form files and one .document file — with the Board ownership and Organization sections, an amber warning that the bundle mixes the languages en and nl, the line naming the Operaton it deploys to, and the Deploy button. Captured at v2026.10.0, when the Kapvergunning bundle still mixed en and nl; its forms and beschikking are all tagged nl now, so that warning no longer appears for it](../../assets/screenshots/linked-data-explorer-bpmn-deploy-modal.png)
  <figcaption>Deploy modal listing the seven resources of the Kapvergunning bundle, captured at v2026.10.0, when the bundle still mixed en and nl</figcaption>
</figure>

The browser sends the bundle in one request to the Linked Data Explorer backend, which posts every resource to Operaton in a single multipart deployment. Because the BPMN, its forms and its document templates share one deployment, `camunda:formRef` resolves correctly at runtime — no separate form deployment step is needed.

The modal provides:

- **Board ownership** *(required)* — the owning board, auto-detected from the process's candidate groups (infra/rip → Infra-board, caseworker/hr → Caseworker) and overridable. The choice is stamped onto the deployed BPMN as a process-level `camunda:property boardOwner`, persisted on the `process_definitions` record (`board_owner` column), and exposed via `/bundles/public` for downstream consumers (ronl-business-api Procesbibliotheek and archive split)
- **Operaton target** — *named, not chosen*. A line reading *Deploys to …* says which Operaton the process will reach. The backend always deploys to its own configured Operaton with its own credentials, so the modal offers no endpoint URL, username or password
- **Resource list** — shows exactly what will be included before you commit
- **Organization** *(required)* — taken from the process's `ronl:organization`, set in the sidebar's **Organization** field; the deploy will not submit without one. It is sent to Operaton as its native **tenant-id** (`POST /deployment/create`'s `tenant-id` field), so no process is deployed without a tenant and left invisible to tenant-scoped lookups
- **Deploy button** — disabled after a successful deployment to prevent accidental re-deploy
- **Recording result** — the backend records the deployed process in the same request, so it appears on the caseworker dashboard and the public site. If that record could not be written, the result shows as a **warning** rather than a tick: the deployment itself succeeded and cannot be undone, but the process will not appear on the dashboard or the public site until it is saved and deployed again

If a `camunda:formRef`, `ronl:documentRef` or `ronl:signatureRef` names a form or document template that is not in local storage, the modal lists it under **⛔ Referenced resources are missing from local storage** and **Deploy stays disabled** until it is imported in the Form Editor or the Document Composer: a bundle without it is one the engine cannot resolve at runtime.

!!! note "Board-owner injection preserves BPMN schema order"
    When a `<bpmn:process>` already carries a `<bpmn:documentation>` child, the `boardOwner` property is inserted **after** it — `injectBoardOwner` skips past any leading `<documentation>` element(s) before locating or creating `extensionElements`, so the resulting XML stays schema-valid (documentation must precede extensionElements). A failed deploy shows the error the backend reports rather than a generic message.

---

## RoPA record linkage

Every process in the LDE can be linked to a RoPA record via `ronl:ropaRef`. Two mechanisms are available:

**RoPA Record selector in the process list** — when a process is open, a **RoPA Record** panel is pinned to the bottom of the left panel below the scrollable process list. A dropdown shows all available records; selecting one writes `ronl:ropaRef` into the process XML immediately.

**BPMN Link tab in the RoPA Editor** — the RoPA Editor's BPMN Link tab writes the same attribute and shows whether the current record ID matches the value already in the XML.

Both mechanisms produce identical results. The attribute is registered in `ronlModdleDescriptor.json` under the `http://ronl.nl/schema/1.0` namespace so it survives `saveXML()` serialisation.

!!! warning "Shared DMN decisions and tenancy"
    Now that deployed processes always carry a tenant-id, a `businessRuleTask`'s
    `camunda:decisionRef` resolves against a decision definition under the
    **exact same tenant** — with no fallback to a shared, untenanted decision
    even when one exists. This was confirmed empirically against a live engine.

    To call a genuinely shared decision from a tenant-scoped process, set
    `camunda:decisionRefTenantId` to an EL expression evaluating to null
    (`${null}`). A literal empty string is silently ignored.

### Deploy warning

The deploy modal checks for the presence of `ronl:ropaRef` on the process element. If absent, an amber warning appears between the resource list and the resource count line. The warning is non-blocking — the bundle can still be deployed — but is intended to prevent deploying to production without a linked RoPA record.

See [RoPA Records](ropa-records.md) for the full feature description.

---

## DSO activiteit linkage

The BPMN Modeler footer panel includes a **DSO Activity** selector for linking a process to a DSO activiteit URN. Pasting a URN and clicking **Verify** queries the live DSO RTR; on success the panel shows the activity's omschrijving, authority block, and a link to the public RTR viewer. The URN is persisted on `<bpmn:process>` as the `ronl:dsoActiviteitUrn` attribute and survives `saveXML` round-trips.

Verification always runs against the **pre-production** DSO — the selector passes no `env`
argument, so the Settings toggle does not apply here. Production-only URNs will not verify in
this panel.

See [DSO Integration](dso-integration.md) for the full integration overview and [DSO Explorer user guide](../user-guide/dso-explorer.md) for the verification workflow.

---

## Language and organization

The footer panel includes **Language** and **Organization** selectors:

- **Language** — ISO 639-1 dropdown (Language-agnostic / English / Dutch / German). Persisted as `ronl:language` on `<bpmn:process>` and as the `process_definitions.language` DB column.
- **Organization** — free-text input with autocomplete from existing organization keys. Persisted as `ronl:organization` and as the DB column.

Both fields are pending-until-Save: typing in them updates the editor's draft state but does not regroup the artefact in the list panel until **Save** is clicked. Saving a shell process atomically propagates `language` and `organization` to all linked subprocesses.

The list panel toolbar offers a language filter and a search box; cards are grouped under collapsible organization headers. Subprocesses follow their shell's organization regardless of their own tag.

See [Multilingualism](multilingualism.md) for the full feature description and [Multilingualism user guide](../user-guide/multilingualism.md) for the tagging workflow.

---

## Deploy modal — language consistency check

When the deploy modal opens, LDE walks the bundle resources (shell BPMN + subprocess BPMNs + linked forms + linked documents) and collects all distinct language tags. If more than one is present, an amber warning surfaces inline in the modal listing the offending codes. The warning is non-blocking — Deploy stays enabled. DMNs are excluded from the check (language-agnostic by design).

The check sits alongside the existing RoPA-missing warning, both rendered between the resource list and the resource count.

The seeded Thuisbatterij bundle shows it: its two processes are untagged, but `awb-notify-applicant-thuisbatterij` is tagged `en` while the bundle's other forms — `recht-en-hoogte-subsidie-thuisbatterij`, `thuisbatterij-aanvullende-gegevens`, `thuisbatterij-subsidie-review` — and `thuisbatterij_subsidie_beschikking` are tagged `nl`, so the modal warns that the bundle mixes `en, nl`. Untagged artefacts never count, so the warning names exactly the tags that disagree; retagging one side, or untagging it, clears it.

---

## Tree Felling Permit example

The **Tree Felling Permit** example is the Kapvergunning subprocess `TreeFellingPermitSubProcess`, seeded with the other examples on first launch. The AWB Generic Process shell calls it through its Call Activity *Fase 4+5: Behandeling en besluit*, once the application is complete. It is drawn in the pool *Kapvergunning - Behandeling en besluit* with two lanes:

- **Systeem** — the start event *Start behandeling*; two `BusinessRuleTask` elements linked to DMN decision models, *Kapvergunning beoordelen (APV)* (`TreeFellingDecision`) and *Herplantplicht beoordelen* (`ReplacementTreeDecision`); the script task *Definitief besluit kapvergunning vaststellen*; the exclusive gateway *Vergunning verleend?* and the two script tasks that set the decision variables, *Besluitvariabelen zetten: Verleend* and *Besluitvariabelen zetten: Geweigerd*; and the single end event *Besluit gereed*
- **Behandelaar** — the user task *Beoordeling behandelaar: besluit kapvergunning*, with the form `tree-felling-review` and the document template `example_treefelling_beschikking`

The example cannot be deleted and serves as a reference for process designers.

---

## Engine compatibility

The Modeler targets Operaton, the open-source fork of Camunda 7 CE. It uses `camunda-bpmn-moddle` for namespace support since no `operaton-bpmn-moddle` package exists yet. Operaton accepts both `camunda:` and `operaton:` namespace attributes, ensuring compatibility.

---

## Related documentation

- [Form Editor](form-editor.md) — creating and managing Camunda Forms in the LDE
- [RONL Business API — Dynamic Forms](../../ronl-business-api/features/dynamic-forms.md) — how deployed forms are fetched and rendered at runtime in MijnOmgeving
- [API Specification](../reference/api-specification.md) — the Linked Data Explorer's `POST /v1/dmns/process/deploy` endpoint this button calls
- [Document Composer](document-composer.md) — authoring decision document templates
- [Document Composer user guide](../user-guide/document-composer.md) — step-by-step workflow
- [Besluitvorming onder gedelegeerde bevoegdheid](besluitvorming-gedelegeerd-bundle.md) — the example with six lanes, declared phases, a routing DMN and a signed besluit
- [RONL Business API — BPMN Design Criteria](../../ronl-business-api/reference/bpmn-design-criteria.md#lanes-and-phase-markers-the-caseworker-process-view) — how lanes and phase markers drive the caseworker process view
