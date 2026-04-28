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

## Process library

The left panel lists all processes grouped by their role in the AWB shell pattern.

### Shell / subprocess hierarchy

The Linked Data Explorer models government service workflows as two-layer BPMN compositions: a universal **AWB shell** process handles the eight statutory procedural phases, and a product-specific **subprocess** delivers the substantive decision via a Call Activity. The process list reflects this structure visually.

Shell processes are top-level entries. Their subprocesses are indented beneath them with a tree connector. Standalone processes — those with no parent-child relationship — appear as top-level entries without indentation.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: BPMN Modeler process list showing AWB Generic Process with Tree Felling Permit indented below it as a subprocess, and AWB Zorgtoeslag with its two subprocesses indented below it](../../assets/screenshots/linked-data-explorer-bpmn-process-hierarchy.png)
  <figcaption>Process list showing shell/subprocess hierarchy: AWB shells with their subprocesses indented</figcaption>
</figure>

### Role badges

Each process card carries one or more badges:

| Badge | Colour | Meaning |
|---|---|---|
| `EXAMPLE` | Blue | Seeded read-only example — cannot be deleted |
| `WIP` | Amber | Work in progress — user-authored |
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
| Migration & Asylum Procedure | `standalone` | — |

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

## Document template linking

When a `UserTask` is selected, the properties panel shows a **Link decision template** dropdown below the form selector. The dropdown lists every document template saved in the Document Composer's `localStorage`.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: BPMN properties panel for a UserTask showing the Link decision template dropdown with the Kapvergunning Beschikking template selected, and the purple info card below confirming the selection](../../assets/screenshots/linked-data-explorer-bpmn-document-template-selector.png)
  <figcaption>Link decision template dropdown in the UserTask properties panel</figcaption>
</figure>

Selecting a template writes `camunda:documentRef` to the BPMN XML and renders a **purple badge** (📄) beneath the element on the canvas. The badge is positioned below the green form badge so all three linked artefacts are visible simultaneously:

| Badge colour | Artefact type | Attribute written |
|---|---|---|
| Amber | DMN / DRD decision | `camunda:decisionRef` |
| Green | Camunda Form | `camunda:formRef` |
| **Purple** | **Document template** | **`camunda:documentRef`** |

Document template linking is only available for `UserTask` elements (not `StartEvent`).

See [Document Composer](document-composer.md) for how to create and manage document templates.

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

## RoPA record linkage

Every process in the LDE can be linked to a RoPA record via `ronl:ropaRef`. Two mechanisms are available:

**RoPA Record selector in the process list** — when a process is open, a **RoPA Record** panel is pinned to the bottom of the left panel below the scrollable process list. A dropdown shows all available records; selecting one writes `ronl:ropaRef` into the process XML immediately.

**BPMN Link tab in the RoPA Editor** — the RoPA Editor's BPMN Link tab writes the same attribute and shows whether the current record ID matches the value already in the XML.

Both mechanisms produce identical results. The attribute is registered in `ronlModdleDescriptor.json` under the `http://ronl.nl/schema/1.0` namespace so it survives `saveXML()` serialisation.

### Deploy warning

The deploy modal checks for the presence of `ronl:ropaRef` on the process element. If absent, an amber warning appears between the resource list and the resource count line. The warning is non-blocking — the bundle can still be deployed — but is intended to prevent deploying to production without a linked RoPA record.

See [RoPA Records](ropa-records.md) for the full feature description.

---

## DSO activiteit linkage

The BPMN Modeler footer panel includes a **DSO Activity** selector for linking a process to a DSO activiteit URN. Pasting a URN and clicking **Verify** queries the live DSO RTR; on success the panel shows the activity's omschrijving, authority block, and a link to the public RTR viewer. The URN is persisted on `<bpmn:process>` as the `ronl:dsoActiviteitUrn` attribute and survives `saveXML` round-trips.

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

---

## Tree Felling Permit example

On first launch, the Modeler auto-creates the **Tree Felling Permit** example process, demonstrating a complete municipal workflow: application submission, two `BusinessRuleTask` elements linked to DMN decision models (`TreeFellingDecision`, `ReplacementTreeDecision`), an exclusive gateway routing to permit granted or rejected outcomes. The example is protected from deletion and serves as a reference for process designers.

---

## Engine compatibility

The Modeler targets Operaton, the open-source fork of Camunda 7 CE. It uses `camunda-bpmn-moddle` for namespace support since no `operaton-bpmn-moddle` package exists yet. Operaton accepts both `camunda:` and `operaton:` namespace attributes, ensuring compatibility.

The Modeler targets Operaton, the open-source fork of Camunda 7 CE. It uses `camunda-bpmn-moddle` for namespace support since no `operaton-bpmn-moddle` package exists yet. The `camunda:formRef` and `camunda:formRefBinding` attributes used for form linking are also accepted by Operaton under the `camunda:` namespace.

---

## Related documentation

- [Form Editor](form-editor.md) — creating and managing Camunda Forms in the LDE
- [RONL Business API — Dynamic Forms](../../../ronl-business-api/features/dynamic-forms.md) — how deployed forms are fetched and rendered at runtime in MijnOmgeving
- [RONL API Endpoints — Process definition deployment](../../../ronl-business-api/references/api-endpoints.md#process-definition-deployment) — the `POST /api/dmns/process/deploy` endpoint this button calls
- [Document Composer](document-composer.md) — authoring decision document templates
- [Document Composer user guide](../user-guide/document-composer.md) — step-by-step workflow
