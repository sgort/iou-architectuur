# Changelog & Roadmap

---

## Changelog
 
### v1.2.0 — RIP Phase 1 Bundle & eDOCS Integration (March 2026)
 
**v1.2.0 — New Feature (March 14, 2026)**
 
#### RIP Phase 1 Bundle
 
New deployment bundle for the Regular Infrastructure Projects (RIP) Phase 1 workflow — Provincie Flevoland.
 
- 20-step BPMN process (`RipPhase1Process.bpmn`) covering project definition and preliminary design preparation: intake form, intake meeting, intake report, PSU organisation, PSU execution, PSU report, risk file preparation, preliminary design principles, and two approval gateways with rejection loops
- `RipProjectTypeAssignment.dmn` — assigns `candidateGroups` and `assignedRoles` from `projectType` and `department`; all rules resolve to `infra-projectteam` / `infra-medewerker`; designed for granular RBAC extension without BPMN changes
- 7 forms: `rip-intake`, `rip-intake-meeting`, `rip-intake-report`, `rip-psu-organize`, `rip-psu-execution`, `rip-risk-file`, `rip-approval` (reusable at both approval gateways)
- 3 document templates: `rip-intake-report.document` (column 2), `rip-psu-report.document` (column 3), `rip-pdp.document` (column 4)
- Bundle deployed to `examples/organizations/flevoland/rip-phase1/`
 
**Files:** `examples/organizations/flevoland/rip-phase1/`
 
#### eDOCS Integration
 
New backend service and external task worker for OpenText eDOCS document management.
 
- `EdocsService` wraps the eDOCS REST API: `connect` (session token caching with auto re-authentication on 401/403), `ensureWorkspace`, `uploadDocument`, `getWorkspaceDocuments`, `healthCheck`
- `ExternalTaskWorker` polls Operaton via `fetchAndLock` (long-polling, 20s timeout) for two topics: `rip-edocs-workspace` (create/retrieve project workspace, write `edocsWorkspaceId`) and `rip-edocs-document` (render and upload document, write named output variable)
- Stub mode (`EDOCS_STUB_MODE=true`, default) — all methods return realistic fake responses; full process runs end-to-end without a live eDOCS server; no code changes needed when switching to live
- Worker started in `app.listen()` callback; stopped cleanly on `SIGTERM`/`SIGINT`
- 4 new REST endpoints: `GET /v1/edocs/status`, `POST /v1/edocs/workspaces/ensure`, `POST /v1/edocs/documents`, `GET /v1/edocs/workspaces/:id/documents`
- New environment variables: `EDOCS_BASE_URL`, `EDOCS_LIBRARY`, `EDOCS_USER_ID`, `EDOCS_PASSWORD`, `EDOCS_STUB_MODE`
 
**Files:** `packages/backend/src/services/edocs.service.ts`, `packages/backend/src/services/externalTaskWorker.service.ts`, `packages/backend/src/routes/edocs.routes.ts`
 
#### DMN Validator — Interaction Rules
 
- **INT-005** scoped to DRDs only — no longer fires on standalone single-decision DMNs; `<inputData>` elements on standalone models serve as input contract declarations for CPSV publishing and do not require `<informationRequirement>` wiring
- **INT-007** (new) — warns when an `<inputExpression>` references a variable name with no matching top-level `<inputData>` declaration; without this, the CPSV Editor generates an empty request body on deploy
 
**File:** `packages/backend/src/services/dmn-validation.service.ts`
 
**v1.1.2 — Bug Fix (March 11, 2026)**
 
#### Form Editor
 
- **Save** now correctly persists the current schema. `saveSchema()` in form-js 1.20.x returns the schema object directly — not wrapped in `{ schema }`. Destructuring assumption caused `undefined` to be written to `localStorage`, making the active form disappear on the next render.
- **Export .form** fixed for the same reason.
- Vite `dedupe` config added for `preact` / `preact/hooks` / `preact/compat` to prevent duplicate Preact instances after npm version round-trips involving `@bpmn-io/*` packages; fixes `TypeError: Cannot read properties of undefined (reading 'context')` on the form canvas.
 
**Known issue:** Typing in a properties panel field (label, key, etc.) loses focus after the first character. Upstream form-js 1.20.x issue — Preact re-renders the properties panel internally on every change event. Will be resolved when an upstream fix is available.
 
**File:** `packages/frontend/vite.config.ts`, `packages/frontend/src/components/FormEditor/FormCanvas.tsx`
 
**v1.1.1 — Enhancement (March 10, 2026)**
 
#### Import from file
 
- **BPMN Modeler** — import `.bpmn` files via the Upload button in the process list header; process name derived from the `name` attribute on the `<process>` element, falling back to filename
- **Form Editor** — import `.form` files; name derived from the schema `id` field, falling back to filename
- **Document Composer** — import `.document` files; receives a fresh `id` and timestamps on import to avoid collisions with existing templates
- All imported items open immediately in their respective editor and are persisted to `localStorage`
 
**Files:** `BpmnModeler/BpmnModeler.tsx`, `FormEditor/FormEditor.tsx`, `DocumentComposer/DocumentComposer.tsx`
 
---

### v1.1.0 — Document Composer (March 2026)

**v1.1.0 — New Feature (March 8, 2026)**

#### Document Composer

New **Document Composer** view for authoring formal government decision document templates (*beschikkingen*).

- Three-panel layout matching BPMN Modeler and Chain Builder conventions: document list (left), zone canvas (centre), Bindings panel (right)
- Fixed-zone document structure: Letterhead, Contact Information, Reference, Body, Closing, Sign-off, and optional Annex
- Five draggable block types: rich text (TipTap with bold, italic, headings, lists), variable placeholder, image (from TriplyDB), separator, horizontal rule, and spacer
- Blocks dragged from the Content library onto zones; reordering within and across zones by drag
- Image library tab fetches assets from the active TriplyDB dataset
- Documents stored in `localStorage` under `linkedDataExplorer_documentTemplates`; create, rename, delete, and **Save as…** actions
- Export document template as a `.document` JSON file
- Read-only example document pre-loaded: **Kapvergunning Beschikking** (linked to `AwbShellProcess`)

**Files:** `DocumentComposer.tsx`, `DocumentCanvas.tsx`, `DocumentList.tsx`, `ZonePanel.tsx`, `TextBlockEditor.tsx`, `ImageBlock.tsx`, `VariableBlock.tsx`, `BindingPanel.tsx`, `document.types.ts`, `documentService.ts`

#### Variable Bindings

- Bindings panel maps `{{placeholder}}` tokens in rich-text blocks to Operaton process variable keys
- **Discover Variables** button queries `GET /v1/process/:key/variable-hints` for all variables used by completed instances of a given process definition key
- Discovered variables shown as clickable chips labelled with type (`String`, `Boolean`, `Double`, etc.)
- Each binding records placeholder, variable key, source (`process` or `dmn_output`), and optional label

**File:** `BindingPanel.tsx`

#### BPMN Modeler integration

- **Link decision template** dropdown injected into the bpmn-js properties panel for `UserTask` elements (not `StartEvent`)
- Selecting a template writes `camunda:documentRef` to the BPMN XML
- Purple badge (📄) rendered on the canvas below the element, below the existing green form badge
- Badge positioned at `bottom: -36` (vs. `bottom: -22` for the form badge) so both badges are visible simultaneously
- `DocumentTemplateSelector.tsx` follows the identical injection pattern as `FormTemplateSelector.tsx`

**Files:** `BpmnModeler/DocumentTemplateSelector.tsx`, `BpmnCanvas.tsx`

---

### v1.0.1 — Bug Fix & Internal (March 2026)

**v1.0.1 — Bug Fix (March 7, 2026)**

#### Bug fix

Fixed `Task_Phase6_Notify` and `Task_RequestMissingInfo` appearing pre-claimed in the caseworker dashboard. `camunda:assignee="demo"` removed; `camunda:candidateGroups="caseworker"` added to both tasks so they are correctly visible in the task queue.

#### Internal — example file migration and version registry

- Example `.bpmn` and `.form` files moved to `public/examples/flevoland/` as the single source of truth. Inline schemas removed from `bpmnTemplates.ts` and `FormEditor.tsx`.
- Added `exampleVersions.ts` with `EXAMPLE_VERSIONS` record (keyed by example name, value is an integer version). The app compares stored versions in `localStorage` key `linkedDataExplorer_exampleVersions` against `EXAMPLE_VERSIONS` and re-fetches any example whose version has been incremented.
- **Developer workflow:** edit the file in `public/examples/`, mirror the change to `examples/organizations/`, increment the version in `exampleVersions.ts`, commit. Existing users receive the updated example without clearing `localStorage`.

**Files:** `exampleVersions.ts`, `bpmnTemplates.ts`, `FormEditor.tsx`, `public/examples/flevoland/`

---

### v1.0.0 — Form Editor & One-Click Deploy (March 2026)

**v1.0.0 — Major Release**

#### Form Editor

New **Form Editor** view powered by `@bpmn-io/form-js` (schemaVersion 16, MIT licensed). Forms are authored as JSON schema, stored in `localStorage`, and available immediately to the BPMN Modeler.

- Two-panel layout: form list (left) and `@bpmn-io/form-js` editor canvas (right)
- Create, rename, and delete WIP forms; three seed EXAMPLE forms are read-only
- Three built-in examples: `kapvergunning-start` (citizen-facing), `tree-felling-review` (caseworker review), `awb-notify-applicant` (caseworker notification)
- Export individual forms as `.form` JSON files compatible with Camunda Modeler and Operaton
- `FormService` localStorage CRUD shared with the BPMN Modeler — no sync step required

**Files:** `FormEditor.tsx`, `FormCanvas.tsx`, `FormList.tsx`, `formService.ts`

#### BPMN Modeler — Form integration

- **Link to Form** dropdown in the properties panel for `UserTask` and `StartEvent` elements
- Writes `camunda:formRef` and `camunda:formRefBinding="latest"` to the BPMN XML
- `camunda:formRefBinding="latest"` means Operaton always resolves the most recent deployment of that form ID — no version pinning needed
- Green badge overlay on `UserTask` and `StartEvent` elements when a form is linked
- `DmnTemplateSelector` pre-selection bug fixed — dropdown now correctly reflects an existing `camunda:decisionRef` when opening properties for an already-linked element

**Files:** `BpmnCanvas.tsx`, `FormTemplateSelector.tsx`

#### BPMN Modeler — One-click deploy

- **Deploy** button opens a modal listing all resources to be bundled: main BPMN, subprocess BPMNs (resolved via `calledElement` attributes), and all `.form` files referenced by `camunda:formRef`
- All resources deployed in a single multipart `POST /api/dmns/process/deploy` to Operaton — `camunda:formRef` resolves at runtime because BPMN and forms share the same deployment ID
- Configurable Operaton endpoint field pre-filled from `VITE_OPERATON_BASE_URL`
- Optional HTTP Basic Auth credentials per deployment
- Unmatched form references (in BPMN but not in localStorage) shown in modal before deploying
- Deploy button disabled after a successful deployment to prevent accidental re-deploy

**Files:** `BpmnCanvas.tsx` (frontend), `dmn.routes.ts` + `operaton.service.ts` (backend)

---

### v0.9.x — DMN Syntactic Validation (February 2026)

**v0.9.1 — Date Input Validation Fix**

Fixed a false "Missing 1 required input(s)" error in the Chain Composer when a DMN contains an optional `Date` input whose test value is intentionally `null` (e.g. `overlijdensdatum` in `zorgtoeslag_resultaat`).

The root cause was a two-part gap between how RDF stores test data and how the validator tracks input state. In TriplyDB, a `null` value cannot be represented as a `schema:value` triple, so optional date variables have no `testValue` property at all on the `DmnVariable` object returned by the backend. The Fill with test data button in `InputForm.tsx` only wrote a key into the `inputs` state object when `testValue` was defined — silently skipping `null`-default dates. The validator in `ChainBuilder.tsx` then checked `input.identifier in inputs`, found the key absent, and pushed the variable into `missingInputs`.

Two fixes were applied:

- **`InputForm.tsx`** — the Fill button now explicitly sets `Date` inputs to `null` when `testValue` is `undefined`, ensuring the key is always registered in state after filling.
- **`ChainBuilder.tsx`** — the validator now exempts `Date` inputs from the missing-input check when no value is present, consistent with the existing exemption for `Boolean` inputs (which default to `false` without user action). An unset date is a valid input state, not an authoring error.

**v0.9.0 — DMN Validator**

Added DMN Validator feature. The DMN Validator lets you validate one or more DMN files against the RONL DMN+ syntactic layers. It is accessible from the shield icon (🛡) in the sidebar. You can drop any number of .dmn or .xml files onto the validator at once, or add files incrementally — the drop zone remains visible at the top of the panel whenever files are loaded. Files are validated independently and displayed side-by-side for easy comparison.

The validator runs on the shared backend at `POST /v1/dmns/validate` and is used both by this Linked Data Explorer's standalone DMN Validator view and by the CPSV Editor's inline validation in the [DMN tab](../../cpsv-editor/features/dmn-orchestration.md).

### v0.8.x — Governance & Vendor Integration (February 2026)

**v0.8.4 — Vendor Services**

Added vendor service discovery: `ronl:VendorService` resources are queried alongside DMN metadata, surfaced as blue count badges on DMN cards, and displayed in a detail modal with full provider information.

**v0.8.3 — DMN Governance Badges**

Three-state validation badge system using RONL Ontology v1.0 properties (`ronl:validationStatus`, `ronl:validatedBy`, `ronl:validatedAt`). Badges visible in both the DMN list and the Chain Composer. Organisation names resolved via `skos:prefLabel`.

**v0.8.1 — BPMN DRD/DMN Selector**

`DmnTemplateSelector` now loads both locally-saved DRD templates and regular DMNs from the backend, displayed in grouped options. Purple info card for DRDs shows chain composition. Auto-populates `camunda:decisionRef` with prefixed DRD entry-point identifier.

---

### v0.7.x — BPMN Modeler & DRD Templates (February 2026)

**v0.7.3 — DRD Template Linking (partial)**

DMN template dropdown in BPMN properties panel implemented. Exact identifier auto-population working; variable compatibility validation planned for a future release.

**v0.7.2 — DRD Template System**

Users can save DRD-compatible chains as named templates stored in localStorage. Templates are endpoint-scoped. DRD templates load via the new "My Templates" panel.

**v0.7.1 — Semantic Variable Matching Fix**

Fixed `findEnhancedChainLinks` SPARQL query to correctly detect both exact and semantic matches. Heusdenpas chain now shows all 10 variable relationships across 3 DMNs.

**v0.7.0 — BPMN Modeler Foundation**

Full BPMN 2.0 editor using bpmn-js v18.12.0 with official Camunda/Operaton properties panel (`bpmn-js-properties-panel`). Three-panel layout: process list, canvas, properties. Tree Felling Permit example auto-loaded on first visit. localStorage persistence and `.bpmn` export.

---

### v0.6.x — DRD Generation & Enhanced Validation (February 2026)

**v0.6.2 — Semantic Analysis Tab**

Semantic Analysis tab added to Chain Builder. Displays cross-agency variable equivalences and chain suggestions. Backend endpoints: `/api/dmns/semantic-equivalences`, `/api/dmns/enhanced-chain-links`, `/api/dmns/cycles`.

**v0.6.1 — DRD Generation**

Save DRD-compatible chains as single executable DRD files deployed to Operaton. Automatic `<informationRequirement>` wiring, entry-point detection, and deployment ID tracking.

**v0.6.0 — Enhanced Validation**

Validation engine distinguishes DRD-compatible chains (all exact matches) from sequential chains (semantic matches present). Clear UI states: green (DRD), amber (sequential), red (invalid). Separate save paths.

---

### v0.5.x — Multi-Endpoint & Test Data (January 2026)

**v0.5.5 — SPARQL & Export Improvements**

Added "Service Rules Metadata" query (`cprmv:Rule → eli:LegalResource → cpsv:PublicService`). CSV export with timestamped filenames and proper escaping. RDF URI collision fix for `cprmv:Rule` instances.

**v0.5.4 — Multi-Endpoint Chain Execution**

Chain execution now correctly uses the selected endpoint throughout the full execution flow. Automatic test data population from `schema:value` in TriplyDB TTL files. Fallback to `testData.json` for legacy DMNs.

**v0.5.3 — Dynamic Endpoint Selection**

Switch between TriplyDB datasets in real time without page reload. Backend caches DMN metadata per endpoint (5-minute TTL). Connection indicator shows direct vs proxied connection status.

---

### v0.4.x — API Versioning & Export (January 2026)

**v0.4.0 — Backend API v1**

Migrated all endpoints to `/v1/*` following Dutch Government API Design Rules. Legacy `/api/*` endpoints retained with `Deprecation` headers. `API-Version` header in all responses. Chain export as JSON or BPMN 2.0 diagram.

---

### v0.3.x — Chain Builder UI (January 2026)

**v0.3.1 — Bug Fixes**

Enhanced error messages for Operaton failures. Synchronized test data between preset and manual chain. Fixed execution progress visibility on first run.

**v0.3.0 — Chain Builder UI**

Visual drag-and-drop chain builder. Real-time validation with input requirements. Dynamic form generation for DMN inputs. Chain execution with step-by-step progress tracking. In-app tutorial (accessible via ? icon). Deployment metadata display.

---

### v0.2.0 — DMN Discovery & Orchestration View (January 2026)

SPARQL-based DMN discovery using CPRMV vocabulary. Three-panel orchestration view: DMN list, chain composer placeholder, details panel. Real-time search and filter. Input/output variable inspection. Automatic chain detection by variable matching. SPARQL result parsing for multiple query response formats.

---

### v0.1.0 — Initial Release (January 2026)

React-based SPARQL visualisation and query tool. Interactive D3.js force-directed graph. Multiple endpoint support. Query editor with sample library and CORS proxy fallback. SELECT query results table. TypeScript interfaces and Vite build tooling.

---

## Notable backend bug fixes

These fixes are documented here because they involve non-obvious root causes that are likely to recur.

### TriplyDB health check returning HTTP 400

**Root cause:** The health check was calling `axios.get(triplydbEndpoint)` without a query parameter. SPARQL endpoints reject bare GET requests — they require either a POST with a query body or a GET with a `?query=` parameter.

**Fix:** Updated `health.routes.ts` to call `sparqlService.healthCheck()`, which executes a minimal `SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 1` query.

**File:** `packages/backend/src/routes/health.routes.ts`

---

### `/v1/*` endpoints returning 404 after Azure deployment

**Root cause:** The GitHub Actions deployment step used `cp -r dist/* deploy/`, which flattened the compiled output. The `package.json` start script references `dist/index.js`, and `health.routes.js` inside `dist/routes/` uses `require('../../package.json')` — both paths broke when the `dist/` folder was removed.

**Fix:** Changed the deployment step to `cp -r dist deploy/`, preserving the directory structure.

```yaml
# Before (broken)
cp -r dist/* deploy/

# After (correct)
cp -r dist deploy/
```

**Files:** `.github/workflows/azure-backend-acc.yml`, `.github/workflows/azure-backend-production.yml`

---

### Root endpoint referencing deprecated `/api/*` paths

**Root cause:** The `GET /` root response had not been updated when API versioning was introduced, so it still advertised `/api/health` and `/api/` as the documentation and health URLs.

**Fix:** Updated `index.ts` to reference `/v1/*` endpoints in the root response and added a `legacy` block explicitly marking the old paths as deprecated.

**File:** `packages/backend/src/index.ts`

---

## Roadmap

### Frontend — Phase 2

The following items are planned but not yet scheduled. Phase 1 features (v0.1–v0.8) are complete.

**Database migration**

Move chain templates and BPMN processes from `localStorage` to a server-side database. Enables user authentication and ownership, process versioning with history, and public sharing with access control. PostgreSQL is the planned backend, consistent with the RONL Business API stack.

**Collaborative editing**

Multiple users editing shared process definitions. Real-time or optimistic-update model TBD.

**Advanced BPMN properties panel**

Full editing of all BPMN element properties: form fields, execution listeners, input/output mappings, conditional expressions, timers. Currently only name and DMN reference are editable.

**DRD export and versioning**

Export generated DRD XML for versioning and sharing. Track DRD version history alongside template evolution.

**Certification registry**

A queryable view of all `ronl:VendorService` resources with `ronl:certificationStatus "certified"`, enabling cross-service comparison of certified vendor implementations.

**Multi-hop semantic chains**

The current semantic validation checks only adjacent DMN pairs. Phase 2 will extend this to multi-hop: `DMN1 → DMN2 → DMN3` where the connection between DMN1 and DMN3 is bridged semantically through DMN2.

**Semantic concept browser**

UI to explore the `skos:exactMatch` network: graph view of all concepts and their relationships, filterable by DMN or variable type, with search by concept URI.

---

### Backend API — versioning roadmap

**v0.5.0 (planned)**

OpenAPI 3.0 specification served at `/v1/openapi.json`. Request/response validation against the spec. Rate limiting. Per-endpoint response caching layer.

**v1.0.0 (planned)**

Full Dutch Government API Design Rules compliance (API-16, API-51, API-02, API-10). Production-grade monitoring and alerting. Performance target: <800ms for any chain execution. Comprehensive structured error handling across all services.

**v2.0.0 (future)**

Remove all legacy `/api/*` endpoints. Evaluate Dutch naming for business resources (`/v2/besluitmodellen` etc.) per API-04. Enhanced orchestration: parallel chain execution where dependency graph allows. Batch execution support for multiple input sets.