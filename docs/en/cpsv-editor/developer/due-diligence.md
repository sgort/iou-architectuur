# CPSV Editor — Product & Architecture Overview

**Repository:** `ttl-editor` (public, GitLab — mirrored to GitHub)

**Purpose:** A browser-based editor for creating, importing, and exporting Dutch government service descriptions as RDF/Turtle files, compliant with the EU CPSV-AP 3.2.0 standard.

**Part of:** The RONL (regels.overheid.nl) initiative — tooling for machine-readable government regulation metadata.

---

## What It Does

The editor lets policy analysts and rule modelers describe a public service (e.g. Zorgtoeslag, WW-uitkering) by filling in a structured form. The form captures the service, its responsible organization, the underlying legislation, temporal business rules, parameters, costs, outputs, and linked concepts. The editor generates a standards-compliant Turtle (.ttl) file in real-time via a live preview panel, and can re-import previously exported .ttl files for round-trip editing.

---

## Feature Domains

The current application bundles four distinct functional domains into a single React SPA. Each domain could, in principle, operate as an independent module or product without breaking the others — provided they share the same RDF data model as their integration contract.

### 1 — Core Editor (metadata authoring)

Form-based authoring of CPSV-AP 3.2.0 compliant service descriptions. Ten tabs cover the full data model:

| Tab | What it captures | Key standards |
|---|---|---|
| Service | Identifier, name, description, sector, thematic area, keywords | CPSV-AP, DCAT |
| Organization | Competent authority, homepage, geographic jurisdiction, logo | CV, FOAF, ORG |
| Legal | BWB/CVDR legislation reference, version, RONL analysis & method concepts | ELI, SKOS, RONL vocabulary |
| Rules | Temporal business rules with validity periods and confidence levels | CPRMV 0.3.0 |
| CPRMV (Policy) | Normative rules with ruleId, rulesetId, situatie, norm, definition | CPRMV 0.3.0 |
| Parameters | Named parameter values (amounts, percentages, durations) with temporal validity | CPRMV, SKOS |
| Concepts | NL-SBB compliant SKOS concepts with labels, definitions, notations | SKOS, NL-SBB |
| Cost / Output | Service cost and output descriptions (embedded in Service tab) | CV |
| Changelog | Version history tracking | Custom |

Additional capabilities: TTL import with full round-trip fidelity (parseTTL_enhanced.js, ~770 lines), TTL export with live preview, form validation, CPRMV JSON import, and a "clear all" reset.

### 2 — Vendor Integration

The Vendor tab is a multi-vendor architecture that lets organizations associate vendor-specific implementations with a service description. Two vendor integration types currently exist:

**Blueriq** — Captures contact information, technical service URL, license type, access model, and certification status. Vendors are selected from the RONL vocabulary dropdown (fetched via SPARQL from TriplyDB at startup). Serialized as `ronl:VendorService` triples in the output.

**iKnow** — Imports Cognitatie/iKnow XML annotation exports, mapping knowledge domain concepts to the editor's data model via configurable mapping files. A one-directional import pathway that populates the Service, Organization, Legal, Rules, and Parameters tabs from the iKnow XML structure.

Both integrations live within the same Vendor tab, demonstrating the pattern for onboarding additional vendor toolchains in the future.

**Coupling to core editor:** Low. Consumes the RONL vocabulary concepts (shared with the Legal tab) and the service identifier for URI generation.

### 3 — Publishing to TriplyDB

A PublishDialog component handles uploading the generated TTL content to a TriplyDB triple store. Two upload methods are implemented: FormData-based file upload (`publishToTriplyDB`) and SPARQL UPDATE insertion (`publishToTriplyDB_SPARQL`). The publish workflow is a multi-step process with progress tracking: validate → generate TTL → upload to TriplyDB → upload logos (organization + vendor) → update SPARQL service → confirm. Supports configurable account/dataset/token (persisted in localStorage), connection testing, graph IRI generation based on organization + service identifiers, and SPARQL service re-indexing (via the shared Express backend to avoid CORS).

**Coupling to core editor:** Low. Consumes only the generated TTL string and service/organization identifiers for graph naming. The Express backend (`REACT_APP_BACKEND_URL`) is shared with the Linked Data Explorer.

### 4 — DMN Integration & Operaton Deployment

The DMN Tab (`DMNTab.jsx`, ~1520 lines) handles the full lifecycle of decision model integration. The workflow proceeds through four stages: validate → deploy → test → generate concepts.

**Upload & Validate.** Upload a `.dmn` file or load a built-in example. On upload, the editor parses the DMN XML client-side (DOMParser) to extract the primary decision key (skipping `p_*` constant parameters), detect all testable decisions in a DRD, and auto-generate a request body from `<inputData>` elements with smart type inference (dates get random birth dates, numerics default to 0, booleans to false). Simultaneously, the editor calls the shared LDE backend's `POST /v1/dmns/validate` endpoint for five-layer syntactic validation (`dmn-validation.service.ts`, ~950 lines, using libxmljs2):

| Layer | Scope | Example checks |
|---|---|---|
| 1 — Base DMN | XML well-formedness, root element, DMN namespace | BASE-PARSE, BASE-ROOT, BASE-NS |
| 2 — Business Rules | Decision table structure, hit policies, type refs, input/output entries | BIZ-001 through BIZ-008+ |
| 3 — Execution Rules | CPRMV extension attributes (ruleType, confidence, validFrom/Until, BWB IDs) | EXEC-001 through EXEC-006+ |
| 4 — Interaction Rules | DRD wiring, informationRequirement integrity, orphaned inputData, self-references | INT-001 through INT-007 |
| 5 — Content | Metadata quality — empty descriptions, missing typeRefs, empty text annotations | CON-001 through CON-005 |

Validation results (errors, warnings, infos per layer) are displayed inline with collapsible detail per layer. This is the same validation engine used by the Linked Data Explorer's multi-file drag-and-drop DMN validator. If the backend is unreachable, validation fails silently — it does not block the DMN workflow.

**Deploy.** One-click deployment to the Operaton rule engine (`operaton.open-regels.nl/engine-rest/deployment/create`) via multipart form upload. Stores the deployment ID and timestamp in editor state.

**Test.** Three levels of testing, all calling Operaton's `/engine-rest/decision-definition/key/{key}/evaluate` endpoint directly from the browser:

| Test mode | What it does |
|---|---|
| Single Evaluate (Postman-style) | Editable JSON request body, evaluate the primary decision, see the full response inline. The request body is auto-generated from DMN inputData but fully editable. |
| Intermediate Decision Tests | For DRDs with multiple decisions: evaluates each sub-decision individually using the same request body. Shows progressive results (ok / error / unexpected) per decision. Constant parameter decisions (`p_*`) are automatically filtered. |
| Test Cases | Upload a `test-cases.json` file (supports two formats: Toeslagen `{name, expected, requestBody}` and DUO `{testName, testResult, variables}`). Runs all cases sequentially against the primary decision. Shows pass/fail per case with expandable detail. |

**Concept generation.** After any successful test, the tab auto-generates NL-SBB compliant SKOS concepts from the DMN input/output variables — including URI, prefLabel, definition, notation, and `skos:exactMatch` — and pushes them to the Concepts tab. Test case runs generate concepts from the last successful case.

The DMN content is embedded in the TTL output as `cprmv:DecisionModel` triples, and the Organization tab supports validation status tracking (not-validated / in-review / validated / rejected) with metadata about who validated and when.

**Coupling to core editor:** Medium. DMN metadata (deployment status, test results, validation) is part of the editor state. The auto-generated concepts feed into the Concepts tab. The TTL export includes DMN blocks. The syntactic validation depends on the shared LDE backend (`POST /v1/dmns/validate`). However, the Operaton REST API interaction and DMN XML parsing (`dmnHelpers.js`) are self-contained utilities.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Create React App (deprecated — see below), Tailwind CSS, Lucide icons |
| State management | React hooks (`useEditorState`, `useArrayHandlers`), no external state library |
| Build & lint | CRA, ESLint, Prettier, Husky (pre-commit/pre-push), lint-staged |
| TTL parsing | Custom hand-written parser (no RDF library dependency) |
| DMN parsing | Browser DOMParser (XML) |
| External APIs | TriplyDB REST + SPARQL, Operaton REST (Camunda-compatible), RONL SPARQL vocabulary |
| Backend dependency | Shared Express server (Linked Data Explorer repo) for CORS-proxied SPARQL queries, TriplyDB service updates, and DMN syntactic validation (libxmljs2) |
| Hosting | Azure Static Web Apps (acc branch → acceptance, main → production) |
| CI/CD | GitHub Actions → Azure SWA deploy |

---

## Advice for the DevOps Team

**The good:** The application works, is in active use, has real-world TTL examples for 12+ organizations, and covers a complex EU standard. The vocabulary configuration is well-structured, the validation layer is solid, and the TTL round-trip import/export is mature.

**What to assess:**

- **No RDF library.** TTL parsing and generation are entirely hand-written (~770 + ~200 lines). This works but is fragile for edge cases. Evaluate whether introducing a lightweight RDF/JS library (e.g. N3.js) would reduce maintenance burden vs. the cost of migration.

- **App.js orchestration.** The main `App.js` (1143 lines) has been partially modularized: data state lives in `useEditorState`, array CRUD operations in `useArrayHandlers`, TTL import logic in `importHandler.js`, and TTL generation in `ttlGenerator.js`. What remains in App.js is UI orchestration (tab rendering, message/status management), the publish workflow (~300 lines of step-by-step progress tracking), and glue code wiring state to child components. Further extraction targets: the publish handler could become a custom hook (`usePublishWorkflow`), and the tab navigation + message system could be separated from the data wiring.

- **No automated tests for TTL output.** The test file (`App.test.js`) is a CRA stub. The real validation happens manually via example files. A test suite comparing generated TTL against the reference examples would be high-value.

- **localStorage for config.** TriplyDB credentials are stored in localStorage. Fine for a prototype, but for a production tool used across teams, does need a proper secrets/config management approach.

- **Shared backend.** The Express backend is owned by the Linked Data Explorer repo. The CPSV Editor depends on it for three things: CORS-proxied SPARQL queries (RONL vocabulary), TriplyDB service re-indexing, and DMN syntactic validation (the five-layer validator uses libxmljs2, which requires a Node.js runtime). Any changes to the backend affect the CPSV Editor. Clarify ownership, versioning (API v1 header is already in place), and deployment coupling.

- **Separation opportunity.** The four domains (editor, vendor, publishing, DMN) are loosely coupled via the shared editor state. A modular architecture — whether as separate routes/lazy-loaded modules within the SPA, or as independent micro-frontends sharing a TTL data contract — would improve maintainability and allow independent release cycles.

- **Create React App.** The React team officially deprecated CRA on February 14, 2025. It continues to work in maintenance mode (a final version was published with React 19 support), but it will not receive new features, performance improvements, or active security updates. The React team recommends migrating to a framework (Next.js, React Router) or a modern build tool (Vite, Parcel, Rsbuild). Since the Linked Data Explorer already uses Vite, migrating the CPSV Editor to Vite would align the tooling across the RONL ecosystem and remove the dependency on an unmaintained build tool.