# Changelog & Roadmap

---

## Changelog

### v0.9.x — DMN Syntactic Validation (February 2026)

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