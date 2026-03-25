# Document Composer

The Document Composer lets you author formal government decision documents (*beschikkingen*) as structured templates inside the Linked Data Explorer. Templates are zone-based, block-driven, and bound to Operaton process variables — so a document authored here can be rendered at runtime by MijnOmgeving for any completed process instance.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Document Composer three-panel layout — document list on the left, zone canvas in the centre, and the Bindings panel on the right with the Kapvergunning Beschikking example open](../../assets/screenshots/linked-data-explorer-document-composer-overview.png)
  <figcaption>Document Composer: document list (left), zone canvas (centre), Bindings panel (right)</figcaption>
</figure>

---

## Three-panel layout

The Composer uses the same three-panel layout convention as the BPMN Modeler and Chain Builder.

- **Left panel** — Document list. Shows all documents stored in `localStorage` with create, rename, delete, and **Save as…** actions. An **EXAMPLE** badge marks the read-only seed document; user-created documents carry a **WIP** badge.
- **Centre panel** — Zone canvas. Renders the document zones in A4-style layout. Blocks are dragged onto zones from the left panel's Content library, and can be reordered or moved between zones by dragging.
- **Right panel** — Bindings. Links `{{placeholder}}` tokens in rich-text blocks to Operaton process variable keys. Only visible when a document is active.

---

## Document zones

Every document follows a fixed zone structure that matches Dutch administrative letter conventions:

| Zone | Label | Required | Purpose |
|---|---|---|---|
| `letterhead` | Letterhead | Yes | Logo, organisation name, house style elements |
| `contactInformation` | Contact Information | Yes | Address, phone, email, website |
| `reference` | Reference | Yes | File number, date, subject, case handler |
| `body` | Body | Yes | Decision, motivation, considerations (Awb art. 3:46) |
| `closing` | Closing | Yes | Appeal options, deadlines, next steps |
| `signOff` | Sign-off | Yes | Name, role, signature of signatory |
| `annex` | Annex | No | Optional annexes; toggled via **Add annex / Remove annex** |

The Letterhead and Contact Information zones render side-by-side at the top of the canvas to reflect standard letter layout.

---

## Block types

The Content library in the left panel provides five block types that can be dragged onto any zone:

| Block | Icon | Description |
|---|---|---|
| **Rich text** | `T` | TipTap editor with bold, italic, headings (H1–H3), and lists. Supports `{{placeholder}}` tokens for variable interpolation. |
| **Variable** | `{}` | Standalone display of a single Operaton process variable value. |
| **Image** | 🖼 | Fetches and renders an asset from the active TriplyDB dataset. |
| **Separator** | `—` | Horizontal rule for visual separation between sections. |
| **Spacer** | ↕ | Vertical whitespace block for layout control. |

Blocks can be reordered within a zone by dragging, or moved to a different zone by dragging across zone boundaries.

---

## Variable Bindings panel

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Bindings panel showing the process key field, Discover Variables button, discovered variable chips with type labels, and a filled binding form](../../assets/screenshots/linked-data-explorer-document-composer-bindings.png)
  <figcaption>Bindings panel: process key, discovered variable chips, and the manual binding form</figcaption>
</figure>

The Bindings panel maps `{{placeholder}}` tokens in document text to Operaton process variable keys.

**Discover Variables** — enter a process definition key (e.g. `AwbShellProcess`) and click the button to query the Operaton history API for all variables used by completed instances of that process. Discovered variables appear as clickable chips labelled with their type (`String`, `Boolean`, `Double`, etc.). Clicking a chip pre-fills the binding form.

Each binding records:

| Field | Description |
|---|---|
| Placeholder | `{{variableName}}` token used in rich-text blocks |
| Variable key | Operaton process variable name |
| Source | `process` (live variable) or `dmn_output` (DMN result variable) |
| Label | Optional human-readable label for the binding panel |

---

## Storage

Document templates are stored in PostgreSQL via the LDE backend, cached locally in `localStorage` for instant synchronous access. On editor load, the service fetches the authoritative list from `GET /v1/assets/documents` and replaces the local cache.

Example templates (`readonly: true`) are seeded from `defaultTemplates.ts` on the frontend and are never written to the database.

See [Asset Storage](../developer/asset-storage.md) for the full architecture.

---

## BPMN Modeler integration

A **Link decision template** selector is injected into the BPMN properties panel for every `UserTask` element. Selecting a document template writes `camunda:documentRef` to the BPMN XML. A purple badge appears below the element on the canvas, distinct from the green form badge (📝) and the amber DMN badge.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: BPMN canvas showing a UserTask with all three badges: amber DMN badge, green form badge, and purple document badge stacked below the element](../../assets/screenshots/linked-data-explorer-bpmn-document-badge.png)
  <figcaption>UserTask with DMN (amber), form (green), and document template (purple) badges</figcaption>
</figure>

See [BPMN Modeler — Document template linking](bpmn-modeler.md#document-template-linking) for details.

---

## Related documentation

- [Document Composer user guide](../user-guide/document-composer.md) — step-by-step authoring workflow
- [Document Composer developer docs](../developer/document-composer.md) — type model, storage, backend endpoint
- [BPMN Modeler — Document template linking](bpmn-modeler.md#document-template-linking)
- [RONL Business API — Dynamic Forms](../../../ronl-business-api/features/dynamic-forms.md) — citizen-side document rendering in MijnOmgeving
