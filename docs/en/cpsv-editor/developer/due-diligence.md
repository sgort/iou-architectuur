---
component: CPSV Editor
---

# CPSV Editor — Product & Architecture Overview

**Repository:** `ttl-editor` (public, GitLab — mirrored to GitHub)
**Purpose:** A browser-based editor for creating, importing, and exporting Dutch government service descriptions as RDF/Turtle files, compliant with the EU CPSV-AP 3.2.0 standard.
**Part of:** The RONL (Regels Open Nederland) initiative — tooling for machine-readable government regulation metadata.

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
| Service | Identifier, name, description, sector, thematic area, keywords, required services (`dct:requires`) | CPSV-AP, DCAT |
| Organization | Competent authority, homepage, geographic jurisdiction, logo | CV, FOAF, ORG |
| Legal | BWB/CVDR legislation reference, version, RONL analysis & method concepts | ELI, SKOS, RONL vocabulary |
| Rules | Temporal business rules with validity periods and confidence levels | CPRMV 0.4.1 |
| CPRMV (Policy) | Normative rules with ruleId, rulesetId, situatie, norm, definition; grouped into `cprmv:RuleSet`s | CPRMV 0.4.1 |
| Parameters | Named parameter values (amounts, percentages, durations) with temporal validity | CPRMV, SKOS |
| Concepts | NL-SBB compliant SKOS concepts with labels, definitions, notations | SKOS, NL-SBB |
| Cost / Output | Service cost and output descriptions (embedded in Service tab) | CV |
| Changelog | Version history tracking | Custom |

Additional capabilities: TTL import with full round-trip fidelity (`parseTTL.enhanced.js`, ~840 lines), TTL export with live preview, form validation, CPRMV JSON import, and a "clear all" reset.

### 2 — Vendor Integration

The Vendor tab is a multi-vendor architecture that lets organizations associate vendor-specific implementations with a service description. Two vendor integration types currently exist:

**Blueriq** — Captures contact information, technical service URL, license type, access model, and certification status. Vendors are selected from the RONL vocabulary dropdown (fetched via SPARQL from TriplyDB at startup). Serialized as `ronl:VendorService` triples in the output.

**iKnow** — Imports Cognitatie/iKnow XML annotation exports, mapping knowledge domain concepts to the editor's data model via configurable mapping files. A one-directional import pathway that populates the Service, Organization, Legal, Rules, and Parameters tabs from the iKnow XML structure.

Both integrations live within the same Vendor tab, demonstrating the pattern for onboarding additional vendor toolchains in the future.

**Coupling to core editor:** Low. Consumes the RONL vocabulary concepts (shared with the Legal tab) and the service identifier for URI generation.

### 3 — Publishing to TriplyDB

A PublishDialog component publishes the generated TTL to a TriplyDB triple store — since v2026.11.1 through the shared Express backend, as the signed-in author, in one call (`publishToTriplyDB` → `POST /v1/triplydb/publish`). The backend holds the TriplyDB account and token, uploads the Turtle into a graph IRI built from the organization and service identifiers, uploads the organization and vendor logos, re-indexes the dataset's SPARQL service and logs who published. The dialog tracks progress (validate → generate TTL → publish), checks the dataset through the backend on request, and keeps only the dataset name in localStorage. Publishing needs the realm role `lde-author`.

When the dialog opens it also runs an **advisory pre-publish SHACL validation** (`shaclHelper.js` → `POST /v1/shacl/validate`), rendering a layered CPRMV 0.4.1 / CPSV-AP 3.2.0 / RONL result. It never blocks publishing and degrades to a neutral amber state when the backend is unreachable. It validates the editor's *regenerated* output, which can differ from an imported source file because import normalises legacy terms to the 0.4.1 vocabulary.

**Coupling to core editor:** Low. Consumes only the generated TTL string and service/organization identifiers for graph naming. The Express backend (`VITE_BACKEND_URL`) is shared with the Linked Data Explorer.

### 4 — DMN Integration & Operaton Deployment

The DMN Tab (`DMNTab.jsx`, ~1840 lines) handles the full lifecycle of decision model integration. The workflow proceeds through four stages: validate → deploy → test → generate concepts.

**Upload & Validate.** Upload a `.dmn` file or load a built-in example. On upload, the editor parses the DMN XML client-side (DOMParser) to extract the primary decision key (skipping `p_*` constant parameters), detect all testable decisions in a DRD, and auto-generate a request body from `<inputData>` elements with smart type inference (dates get random birth dates, numerics default to 0, booleans to false). Simultaneously, the editor calls the shared LDE backend's `POST /v1/dmns/validate` endpoint for five-layer syntactic validation (`dmn-validation.service.ts`, ~950 lines, using libxmljs2):

| Layer | Scope | Example checks |
|---|---|---|
| 1 — Base DMN | XML well-formedness, root element, DMN namespace | BASE-PARSE, BASE-ROOT, BASE-NS |
| 2 — Business Rules | Decision table structure, hit policies, type refs, input/output entries | BIZ-001 through BIZ-008+ |
| 3 — Execution Rules | CPRMV extension attributes (ruleType, confidence, validFrom/Until, BWB IDs) | EXEC-001 through EXEC-006+ |
| 4 — Interaction Rules | DRD wiring, informationRequirement integrity, orphaned inputData, self-references | INT-001 through INT-007 |
| 5 — Content | Metadata quality — empty descriptions, missing typeRefs, empty text annotations | CON-001 through CON-005 |

Validation results (errors, warnings, infos per layer) are displayed inline with collapsible detail per layer. This is the same validation engine used by the Linked Data Explorer's multi-file drag-and-drop DMN validator. If the backend is unreachable, the panel renders a distinct amber *"Syntax validation result not available"* state (v1.9.5) rather than failing silently — deployment and testing still work; only the syntactic pre-check is skipped.

**Deploy.** One-click deployment to the Operaton rule engine, routed through the shared LDE backend's `POST /v1/dmns/deploy` rather than the browser calling Operaton directly (v2026.08.0 — the direct call hit CORS in local development). Stores the deployment ID and timestamp in editor state.

**Test.** Three levels of testing, all routed through the shared LDE backend's `POST /v1/dmns/evaluate/{key}` (v2026.08.0), which calls Operaton server-to-server:

| Test mode | What it does |
|---|---|
| Single Evaluate (Postman-style) | Editable JSON request body, evaluate the primary decision, see the full response inline. The request body is auto-generated from DMN inputData but fully editable. |
| Intermediate Decision Tests | For DRDs with multiple decisions: evaluates each sub-decision individually using the same request body. Shows progressive results (ok / error / unexpected) per decision. Constant parameter decisions (`p_*`) are automatically filtered. |
| Test Cases | Upload a `test-cases.json` file (supports two formats: Toeslagen `{name, expected, requestBody}` and DUO `{testName, testResult, variables}`). Runs all cases sequentially against the primary decision. Shows pass/fail per case with expandable detail. |

**Concept generation.** After any successful test, the tab auto-generates NL-SBB compliant SKOS concepts from the DMN input/output variables — including URI, prefLabel, definition, notation, and `skos:exactMatch` — and pushes them to the Concepts tab. Test case runs derive input concepts from the union of every uploaded case's request-body variables (so all inputs are covered even without a successful evaluate) and add output concepts from the last successful case (v1.10.2). Generated concept URIs, `dct:subject` and `skos:exactMatch` values are IRI-sanitised (whitespace → `_`, illegal chars percent-encoded) so the export parses under a strict SHACL parser and re-imports cleanly.

The DMN content is embedded in the TTL output as `cprmv:DecisionModel` triples, and the Organization tab supports validation status tracking (not-validated / in-review / validated / rejected) with metadata about who validated and when.

**Coupling to core editor:** Medium. DMN metadata (deployment status, test results, validation) is part of the editor state. The auto-generated concepts feed into the Concepts tab. The TTL export includes DMN blocks. The syntactic validation depends on the shared LDE backend (`POST /v1/dmns/validate`). Deploy and evaluate also go through that backend (`/v1/dmns/deploy`, `/v1/dmns/evaluate/{key}`), so the tab no longer talks to Operaton directly. DMN XML parsing (`dmnHelpers.js`) remains a self-contained utility.

### 5 — DSO → DMN deep-link import

The `useDsoImport` hook (`src/hooks/useDsoImport.js`) consumes a deep-link handoff from the Linked Data Explorer: `/?dsoImport=dmn&dmnId=…&env=…&activityName=…&authority=…&activityUrn=…&fsRef=…`. On mount it fetches the standalone DMN XML from the shared backend (`GET /v1/dso/toepasbare-regels/{dmnId}/dmn`, with `?env=prod` only when `env=prod`) and prefills the DMN tab (keeping it interactive — *not* the imported-preserved mode), the Service tab (from the DSO activity) and the Organization tab (from the resolved authority). The import params are then stripped via `history.replaceState`, and a `consumedRef` guard prevents a StrictMode double-invoke. Deploy/test/publish proceed through the normal DMNTab + PublishDialog flow.

**Coupling to core editor:** Low. The hook only calls the existing `setDmnData`/`setService`/`setOrganization` setters and the shared message banner.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 19, Vite, Tailwind CSS, Lucide icons, `keycloak-js` (sign-in) |
| State management | React hooks (`useEditorState`, `useArrayHandlers`), no external state library |
| Build & lint | Vite, ESLint, Prettier, Husky (pre-commit/pre-push), lint-staged |
| Testing | Vitest 5, `@testing-library/react`, Playwright — 858 tests across 70 files, all passing (measured 12 November 2026), at 91.35% statements, 89.29% branches, 82.15% functions and 92.03% lines; plus 4 end-to-end journeys ([Testing](testing.md)) |
| TTL parsing | Custom hand-written parser (no RDF library dependency) |
| DMN parsing | Browser DOMParser (XML) |
| External APIs | Keycloak (OIDC sign-in, realm `ronl`) directly from the browser; TriplyDB, Operaton (Camunda-compatible REST), the RONL SPARQL vocabulary and the DSO APIs only through the shared backend |
| Backend dependency | Shared Express server (Linked Data Explorer repo) for CORS-proxied SPARQL queries (the RONL vocabulary and the published-services list), TriplyDB publishing as the signed-in author, DMN syntactic validation (libxmljs2), DMN deploy and evaluate, pre-publish SHACL validation and the DSO import |
| Hosting | Azure Static Web Apps (acc branch → acceptance, main → production) |
| CI/CD | GitHub Actions: lint, tests and the production build on the runner (Node 24.22.2 from `.nvmrc`), uploaded to Azure Static Web Apps with `skip_app_build`; on every pull request a required lockfile review and verification of registry signatures and provenance attestations; a daily dependency audit, a quarterly dependency review, and an SBOM per release of every production package ([Deployment](deployment.md)) |

---

## Advice for the DevOps Team

**The good:** The application works, is in active use, has real-world TTL examples for 12+ organizations, and covers a complex EU standard. The vocabulary configuration is well-structured, the validation layer is solid, and the TTL round-trip import/export is mature.

**What to assess:**

- **No RDF library.** TTL parsing and generation are entirely hand-written (a ~840-line parser and a ~1,660-line generator). This works but is fragile for edge cases. Evaluate whether introducing a lightweight RDF/JS library (e.g. N3.js) would reduce maintenance burden vs. the cost of migration.

- **App.jsx orchestration.** The main `App.jsx` (1,190 lines) has been partially modularized: data state lives in `useEditorState`, array CRUD operations in `useArrayHandlers`, TTL import logic in `importHandler.js`, and TTL generation in `ttlGenerator.js`. What remains in App.jsx is UI orchestration (tab rendering, message/status management), the publish workflow (~230 lines: form validation, TTL generation and one backend call, with its progress and result states), and glue code wiring state to child components. Further extraction targets: the publish handler could become a custom hook (`usePublishWorkflow`), and the tab navigation + message system could be separated from the data wiring.

- **Automated tests — addressed.** This was originally raised here as *"no automated tests for TTL output"*: the only test file was a CRA stub and validation happened manually against example files. A phased suite landed in v2026.07.0, including the high-value round-trip coverage suggested here — parse a real reference export, regenerate, re-parse, compare — and found two genuine defects immediately, one of which had been silently dropping data on re-import since a predicate rename. All eight phases, P0–P7, are complete: at v2026.09.4 the suite stands at **751 tests across 61 files**, plus three Playwright journeys against a live stack, and every file is held to an **80% branch floor enforced by the runner**. The UI layer this bullet once named as untested is covered: `DMNTab.jsx` 98.34% branches, `importHandler.js` 100% statements, `ttlGenerator.js` 94.89% and `parseTTL.enhanced.js` 94.50% statements. The remaining weakness is narrower and specific: `App.jsx` clears the branch floor at 81.48% but reads **53.70% functions** — whole handlers no test calls, which a branch floor does not see. See [Testing](testing.md).

- **localStorage for config — resolved.** TriplyDB credentials used to be stored in localStorage. Since v2026.11.1 the browser keeps only the dataset name; the token lives in the Linked Data Explorer backend, and one an older version stored is removed on first load.

- **Shared backend.** The Express backend is owned by the Linked Data Explorer repo. The CPSV Editor depends on it for CORS-proxied SPARQL queries (the RONL vocabulary, and since v2026.11.0 the public services published to the dataset), TriplyDB publishing (as the signed-in author, since v2026.11.1), DMN syntactic validation (the five-layer validator uses libxmljs2, which requires a Node.js runtime), DMN deploy and evaluate against Operaton, pre-publish SHACL validation, and the DSO import. Any changes to the backend affect the CPSV Editor. Clarify ownership, versioning (API v1 header is already in place), and deployment coupling.

- **Separation opportunity.** The four domains (editor, vendor, publishing, DMN) are loosely coupled via the shared editor state. A modular architecture — whether as separate routes/lazy-loaded modules within the SPA, or as independent micro-frontends sharing a TTL data contract — would improve maintainability and allow independent release cycles. A first step in that direction has landed: since v2026.09.2 the four heaviest tabs — `ChangelogTab`, `CPRMVTab`, `DMNTab` and `VendorTab` — are lazy-loaded, taking the entry chunk from 685.71 to 392.74 kB.

- **Create React App — resolved.** This review recommended migrating off CRA, deprecated by the React team on 14 February 2025 and receiving no new features, performance work or active security updates. That **migrated to Vite in v2026.09.1**, in four independently revertable phases with the P0–P4 suite as the regression net exactly as proposed here. `npm audit` dropped from 52 vulnerabilities to 10 and production builds from roughly 30 seconds to under two. See [The Vite migration](testing.md#the-vite-migration).

---

## Authentication & Authorization for Production Publishing

Since v2026.11.1 the editor has sign-in. A user signs in at Keycloak realm `ronl`, the login the Linked Data Explorer and the RONL Business API share — client `ttl-editor`, the authorization code flow with PKCE — either through Flevoland's Entra or with an employee password. Signing in is optional: editing, import, validation and download work without it. The two actions that change shared state need the realm role `lde-author`:

| Integration point | Auth mechanism at v2026.11.1 |
|---|---|
| TriplyDB publishing | The author's bearer token to the Linked Data Explorer backend's `POST /v1/triplydb/publish`, which requires `lde-author` and publishes with its own TriplyDB account and token. The browser keeps only the dataset name |
| Operaton deployment & testing | Deploy sends the author's token to `POST /v1/dmns/deploy`. Without a token the backend makes it a test deploy to the tenant `TestOnly`, removed after 48 hours — enabled on acceptance, not on production. Evaluate is open. The backend reaches the engine with its own optional `OPERATON_API_KEY` |
| Shared Express backend (LDE) | Verifies Keycloak tokens. Every route the editor uses to change shared state requires `lde-author` — publish, test-connection, update-service, list-graphs — except deploy, which without a token is a test deploy where one is enabled. The routes the editor reads stay open: the SPARQL proxy, DMN and SHACL validation, evaluate, `publish-target` and `deploy/options` |
| Azure Static Web Apps | Deployment tokens in GitHub Secrets (CI/CD only, no user auth) |

That establishes **who** the user is and that they may change the shared library. It does not establish **on whose behalf** they publish: the role is a single flag, so any author can publish a description for any organization into any dataset of the backend's TriplyDB account. A publication that carries a competent authority's mandate needs that link.

**Advice for the DevOps team:**

- **Backend-mediated publishing — done.** Since v2026.11.1 the browser never holds a TriplyDB token. The backend holds the service credentials and accepts a publish only from an author, which also removed the localStorage token ([ttl-editor#234](https://github.com/sgort/ttl-editor/issues/234)).

- **Authorization per organization — open.** Map an author to the organizations they may publish for — a token claim or a Keycloak group — and have the backend refuse a publish whose `organization` is not among them, and possibly restrict the datasets as well.

- **Operaton credentials — addressed in part.** The editor holds no Operaton credential: deploy and evaluate are proxied by the Linked Data Explorer backend, which calls the engine server-to-server with its own optional `OPERATON_API_KEY`. A deploy now needs an author, or is confined to the `TestOnly` tenant; evaluate is still open to any caller.

- **Backend authentication — done for writes.** The shared backend verifies Keycloak tokens against the realm's keys and requires `lde-author` on the routes that write. The read routes remain open.

- **Audit trail — a log line, not yet a record.** Every publish attempt writes one log line: who, which organization and service, which graph and dataset, and the outcome (`published`, `published-with-warning` or `failed`). That is the raw material for an audit trail; a store with a retention period, which a mandate would need, does not exist yet.

- **Scope.** The one write a signed-out user can make is the test deploy, and only where the backend's `TEST_DEPLOY_ENABLED` is `true`: on 12 November 2026 acceptance answered `enabled: true` and production `enabled: false` (`GET /v1/dmns/deploy/options`).