# Frontend

The frontend (`regel-gui`) is a **Vue 3** application built with the **Quasar** framework as a
plain **SPA** — `src-ssr/` was removed in v2026.07.0 (see
[Changelog & Roadmap](changelog-roadmap.md)). State is held mainly in a **Pinia** `regel`
store (plus a small `layout` store for UI-only state), the domain is modelled as plain
JavaScript classes, and the network view is drawn with **D3**.

---

## Directory layout

```
gui/src/
├── router/routes.js             # task, sources, interpretation, visualization,
│                                 # executable, execute — client-side routes
├── pages/                       # Thin <q-page> wrappers, one per route, each
│   ├── TaskDefinitionPage.vue    # rendering the matching view below
│   ├── SourceCollectionPage.vue
│   ├── InterpretationPage.vue
│   ├── VisualizationPage.vue
│   ├── ExecutablePage.vue       # "Coming soon" — see Roadmap
│   ├── ExecutePage.vue          # "Coming soon" — see Roadmap
│   └── ErrorNotFound.vue
├── views/                       # The actual step UIs; unaffected by the routing rework
│   ├── TaskDefinitionView.vue
│   ├── SourceCollectionView.vue
│   ├── InterpretationView.vue
│   ├── SourceView.vue           # interpretation pane
│   ├── FramesView.vue           # interpretation pane
│   └── visualization/           # VisualizationView.vue, VisualizationPanel.vue
├── components/                  # Editor panels, forms, lists, network, dialogs
├── model/                       # Domain classes (see below)
├── stores/                      # regel.js (domain state), layout.js (UI state)
├── services/ApiServices.js      # All calls to the backend / Python services
├── helpers/                     # annotating, underlining, importExport, config, ...
└── i18n/                        # vue-i18n message catalogue (en-US)
```

Routing replaced a single `IndexPage.vue` stepper that swapped views by client-side step
state; the same `views/*.vue` step UIs are now reached through the router instead.

---

## The domain model

The `model/` classes are the source of truth for what an interpretation *is*. They are plain
classes (not Vue reactive objects) with `toFlatObject()` / `fromFlatObject()` methods for
serialisation.

```mermaid
classDiagram
    class Task
    class SourceDocument
    class Sentence
    class Snippet
    class Annotation
    class Fact
    class Act
    class Claimduty
    class BooleanConstruct
    class Comment

    SourceDocument "1" --> "*" Sentence
    Sentence "1" --> "*" Snippet
    Snippet "1" --> "*" Annotation
    Annotation --> Fact : frame
    Annotation --> Act : frame
    Annotation --> Claimduty : frame
    Act --> Fact : action/actor/object/recipient
    Act --> BooleanConstruct : precondition
    Claimduty --> Fact : duty/claimant/holder
    Fact --> BooleanConstruct : subdivision
    BooleanConstruct --> BooleanConstruct : children
    Fact "1" --> "*" Comment
```

| Class | Responsibility |
|---|---|
| `Task` | Task and interpretation IRIs, editor, label, description |
| `SourceDocument` | Parses Choppr JSON-LD into a sentence tree; owns annotation lookup/cleanup helpers |
| `Sentence` | A node in the document tree: text, children, selected/collapsed/visible flags, snippets |
| `Snippet` | A character range within a sentence; holds the annotations covering it |
| `Annotation` | Links one or more snippets to one frame |
| `Fact` | A fact frame: short/full name, subtypes, subdivision, comments |
| `Act` | An act relation: action, actor, object, recipient, precondition, creates, terminates |
| `Claimduty` | A claim-duty relation: duty, claimant, holder |
| `BooleanConstruct` | AND/OR/NOT tree used for preconditions and fact subdivisions |
| `Comment` | A note on a frame: content, author, created/edited timestamps |
| `frame.js` | `frameTypes` — the catalogue of frame types and fact subtypes |

!!! note "Refactoring note in the code"
    `Fact`, `Act`, and `Claimduty` share several methods (`deleteReferencesToFrame`, role
    handling, `toFlatObject`/`fromFlatObject`). The code contains a `Frame` base class stub
    and TODOs to unify them; today each frame type implements these independently.

---

## State management

A single Pinia store, `useRegelStore` (in `stores/regel.js`), holds the entire editor state:
the current step, the list of frames, which frame and boolean-construct node are being edited,
the loaded source documents, the current annotation, and the available sources/tasks from
TriplyDB.

Its actions cover the full lifecycle:

- **Frame management** — `addNewFrame`, `setFrameBeingEdited`, `removeFrame` (which also strips
  every reference to the deleted frame and its annotations), `createNewFrameViaNlp`.
- **Sources** — `addSource`, `addSourceFromTriply`, `createSourceDocFromJsonLD`,
  `readAvailableSourcesInTripleStore`.
- **Tasks** — `addTaskFromTriply`, `readAvailableTasksInTripleStore`,
  `saveInterpretationTriply`.
- **Import/export** — `saveInterpretationAsJson`, `saveInterpretationAsTrig`,
  `loadInterpretation`, `loadInterpretationFromRDF`.

When saving, the store merges the persisted frames with those still open in the editor, dedupes
by id, and hands the result to `convertInterpretationToJson`.

---

## Annotation internals

Two helpers carry the annotation logic:

- `helpers/annotating.js` turns a raw browser `Selection` (or a character range) into the set
  of snippets it covers, handling right-to-left selections and cross-sentence spans, and
  splits snippets so a highlight becomes its own snippet (`splitAndReturnSelectedSnippets`).
- `helpers/underlining.js` computes the vertical position of each annotation's underline so
  overlapping annotations stack without colliding.

`helpers/importExport.js` holds `convertInterpretationToJson` and
`parseJsonToInterpretation`, which translate between the model classes and the on-disk JSON,
re-linking frame references by id and reconstructing snippets and comments on load.

---

## Calling the services

`services/ApiServices.js` is the only place the frontend talks to the network. Its functions
map one-to-one onto the routed endpoints:

| Function | Endpoint | Purpose |
|---|---|---|
| `fetchNlpPrediction` | `POST /api/predict` | NLP suggestions |
| `convertToRDF` | `POST /api/process_and_save` | JSON → RDF (wrap-up) |
| `convertRDFToJSON` | `POST /api/process_graph` | RDF → JSON (unwrap) |
| `getSourceList` | `GET /api/getSources` | List sources |
| `getSourceFromTriply` | `POST /api/getSource` | Fetch one source |
| `getTasksFromTriply` | `POST /api/getTasksFromTriply` | List tasks |
| `getTaskFromTriply` | `POST /api/getTask` | Fetch one task |
| `saveTask` | `POST /api/saveTaskAtTriply` | Save a task |

See [API Endpoints](../reference/api-endpoints.md) for request/response details.
