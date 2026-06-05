# Changelog & Roadmap

---

## Changelog

### v1.9.5 — DMN Workflow Polish (May 2026)

**Request Body Generation Reads `<inputValues>` Constraints**

`generateRequestBodyFromDMN` in `DMNTab.jsx` now consults every decisionTable input column for an `<inputValues>` FEEL allowed-values list and uses the first allowed value as the starter for the corresponding inputData. DMNs that constrain string inputs (e.g., normbedragen descriptions, status codes, enum-style domain values) no longer produce empty strings that would fail at Operaton evaluate time — the generated starter body is runnable as-is.

Two helper closures added: `parseFirstFeelListItem` (unwraps quoted strings, coerces booleans, parses numbers from a comma-separated FEEL list) and `findInputValuesExample` (scans `decisionTable > input` elements for a constraint whose `inputExpression` matches the given inputData name). When no constraint exists, the inputData falls through to the existing `typeRef` switch and name-based heuristics unchanged — every existing project DMN keeps generating the same starter body as before.

**Validation Backend Unreachability Surfaced**

`runBackendValidation` no longer fails silently when the Linked Data Explorer backend at `REACT_APP_BACKEND_URL` cannot be reached. The validation panel renders a third, distinct visual state — amber *"Syntax validation result not available"* — with a short explanation that DMN deployment and testing still work; only the syntactic pre-check is skipped. The amber state is kept visually separate from the existing red *"Syntax issues found"* state so a network failure cannot be mistaken for an actual DMN problem. A new `validationResult.unavailable` flag drives the third branch in the validation pill header; the `parseError` bubble switches between amber and red styling to match the meaning of the message.

**DMN Modelling Reference Updates**

Patterns surfaced while building the Den Haag *Beslissing Levensonderhoud (ALO)* and SZW *normbedragen* deployable DMNs have been folded back as standing guidance: every `<inputData>` element requires a `<variable>` child with `name` and `typeRef` so sub-decision evaluation by key can resolve `requiredInput` references; the primary decision must be listed first in the file because Operaton selects the first `<decision>` as the primary key; and decisions that aggregate output from required decisions should declare passthrough output columns (e.g., `redenAfwijzing`, `informatiebehoefte`) so the response from a primary-decision evaluate call carries the full verdict shape rather than just the headline output.

---

### v1.9.4 — Dataset Catalog & Stable Graph Publishing (May 2026)

**Legal Resource URI Cleanup**

Parser normalises `legalResource.bwbId` to its canonical un-versioned form on import — trailing `/YYYY-MM-DD` and `/YYYY-MM-DD/<index>` segments are stripped so the version is captured exclusively in `legalResource.version`. The `generateLegalResourceSection` emitter refactored to route both the subject URI and `eli:is_realized_by` through `buildLegalUriForRulesetId`, producing a clean un-versioned `eli:LegalResource` subject (e.g., `https://wetten.overheid.nl/BWBR0015703`) and a single-versioned manifestation URI (`.../BWBR0015703/2026-01-01`), regardless of whether `bwbId` arrived clean or in a legacy already-versioned form. `cv:hasLegalResource` in the Service section automatically points to the same un-versioned URI as the LegalResource block, closing the loop between Service, LegalResource, and versioned manifestation. Resolves the doubled-version URIs (e.g., `.../BWBR0015703/2026-01-01/0/2026-01-01`) that previously appeared in `eli:is_realized_by` and propagated through to `cprmv:implements` on rules.

**cprmv:Dataset Generation**

TTL export now emits a `cprmv:Dataset` block per unique `cprmv:rulesetId` across the CPRMV Rules collection — one Dataset per legal source, dual-typed `cprmv:Dataset` and `dcat:Dataset` for DCAT catalogue interoperability. Dataset properties include `dct:identifier`, optional `dct:title` (primary ruleset only), `cprmv:rulesetId`, `cprmv:implements` pointing to the legal manifestation URI, optional `dcat:version`, `dct:issued`, and `dcat:landingPage`.

CPRMV Rule emitter updated so `cprmv:implements` uses each rule's own `rulesetId` rather than the service's primary legal resource — accurate rule-level claims in multi-BWB services, and identical loose (`cprmv:rulesetId`) and tight (`cprmv:implements`) SPARQL join results. New `buildLegalUriForRulesetId()` helper handles BWB, CVDR, and full-URI inputs; defensively strips already-versioned suffixes before appending the version. `cprmvDataset` entity type registered in `vocabularies.config.js`; `dcat` namespace already present in `TTL_NAMESPACES`. Supports the new `/v1/norms` endpoint in the Linked Data Explorer.

**Deterministic Graph IRI on Publish**

Publishes now land in a per-service graph at `https://regels.overheid.nl/graphs/{org-local}/{service-id}` (e.g., `.../graphs/Sociale_Verzekeringsbank/aow-leeftijd`) instead of the auto-numbered `graph:default-N` series. Republishing the same service overwrites its previous graph rather than creating an incremented copy — each service now corresponds to a single, stable graph IRI in TriplyDB. New `buildGraphIRI()` helper derives the IRI from `organization.identifier` and `service.identifier`, threaded through `publishToTriplyDB` and `publishToTriplyDB_SPARQL` as a `graphIRI` parameter (default fallback: `graphs/default`).

The graph IRI is forwarded to the Linked Data Explorer backend's `/v1/triplydb/update-service` endpoint as `graphName`, logged on the backend as `triggeredByGraph` for end-to-end traceability across multi-publish flows.

**Vendor Tab Polish**

Vendor tab data — selected vendor, contact details, technical fields, certification, service notes — now survives navigation between tabs; the local `selectedVendor` state in `VendorTab.jsx` replaced with a derived alias over lifted `vendorService.selectedVendor`, eliminating the data loss that previously occurred on tab re-entry. RONL concept fetch (analysis, method, and vendor concepts from TriplyDB) lifted from `LegalTab` and `VendorTab` into `useEditorState` — concepts are fetched once on App mount and shared across both tabs, eliminating per-mount network calls and dropdown flicker.

TTL import now restores vendor data: `selectedVendor`, provider organisation name, `contactPoint` (name, email, telephone), `foaf:homepage`, `schema:url`, `schema:license`, `ronl:accessType`, `dct:description`, and `schema:image`. `vendorService` threaded through `parseTTL()` and `applyImportedData()`; `setVendorService` added to the setters object handed to `handleTTLImport`. Round-trip verified against the SVB AOW-leeftijd Vendor example.

---

### v1.9.x — DMN Testing Suite & Vendor Services (February 2026)

**v1.9.3 — DMN Syntactic Validation**

 Immediately after upload, the editor runs the DMN file through the shared backend's five-layer syntactic validator. The result is shown inline in the file card — valid files display a green badge, files with issues display a collapsible panel grouped by layer. Validation covers five layers. Issues are grouped by layer in a collapsible panel. Each issue carries a severity (error, warning, or informational), a typed code, a human-readable message, and — where applicable — an element reference and line number.

**v1.9.2 — DMN Testing Suite**

Intermediate decision tests added, allowing each sub-decision in a DRD to be tested individually. Batch test case upload from JSON files with progressive real-time result display and pass/fail statistics. Smart filtering automatically skips constant `p_*` parameter decisions. NL-SBB concepts auto-generated from last successful test run output. Critical date type fix: date variables now correctly use `type: 'String'` in request bodies, resolving `InvalidRequestException` errors for DMNs with `typeRef='date'`.

**v1.9.1 — Vendor Tab**

Dedicated Vendor tab for publishing `ronl:VendorService` metadata. Dynamic vendor selection dropdown loading RONL Method Concepts from TriplyDB. Full Blueriq implementation: contact information, service URL, licence type, access type (`fair-use` / `iam-required`), logo upload, and certification tracking workflow with pre-populated request email. Generates complete `ronl:VendorService` TTL with `schema:provider` nested structure. Multi-vendor architecture extensible for future platforms. Round-trip import/export support.

**v1.9.0 — Semantic Rule Linking**

Critical bug fix: rule URIs now use the full `cprmv:ruleIdPath` for uniqueness (e.g., `BWBR0015703_2026-01-01_0_Artikel-20_lid-1_onderdeel-a`), eliminating RDF triple merging in TriplyDB caused by duplicate short IDs. Added `cprmv:implements` property linking each rule directly to its legal resource URI, removing fragile string-based matching. Versioned URI support: rules link to `eli:is_realized_by` version URI when available. Policy tab now shows an informational banner with the linked legal resource as a clickable link.

---

### v1.8.x — RONL Concepts & Legal Resource Extensions (January 2026)

**v1.8.3 — RONL Concepts Integration**

Legal tab extended with Analysis dropdown (Wetsanalyse JAS, JRM, FLINT) and Method dropdown (16 options: ALEF, Avola, DMN, RuleSpeak, and more), both loading dynamically from TriplyDB via SPARQL. Properties `ronl:hasAnalysis` and `ronl:hasMethod` link legal resources to RONL vocabulary concepts. Full round-trip import/export. iKnow tab refactored into extensible Vendor tab with vendor selection dropdown as the foundation for multi-vendor architecture.

**v1.8.2 — DMN Type Detection & CVDR Support**

DMN files now read `typeRef` from `<variable>` elements for accurate type detection, with intelligent birth date generation (random age 25–68) for demographic variables. Added CVDR (municipal regulations) support alongside BWB national legislation — automatic repository detection with visual badges, smart URI generation, and quick links to the appropriate repository. Compact tab navigation eliminates horizontal scroll across all 10 tabs.

**v1.8.1 — NL-SBB Concept Layer**

Complete three-phase implementation of the NL-SBB concept layer for DMN variables. Phase A: automatic concept generation from DMN test results with Dutch NL-SBB standard compliance. Phase B: full import/export round-trip support. Phase C: editable Concepts tab with add/edit/delete for all concept properties including preferred labels, definitions, notations, and `skos:exactMatch` URIs. Bidirectional linking via `dct:subject` from concepts to technical variables. Foundation for cross-DMN semantic matching and chain validation in the Linked Data Explorer.

---

### v1.7.0 — Organisation Logo Management (January 2026)

Logo upload with automatic resizing to 256×256px, live preview, and direct publishing to TriplyDB as an asset file. TTL generation adds `foaf:logo` and `schema:image` properties. Added `ronl:implements` link from DMN to Service enabling complete RDF graph traversal: DMN → Service → Organisation → Logo.

---

### v1.6.0 — TriplyDB Publishing (January 2026)

Direct publishing to TriplyDB from the editor. Configuration dialog for API URL, account, dataset, and token (stored in `localStorage`, never on server). Test connection functionality and real-time status feedback. Automatic validation before publish. Supports up to 5 MB per upload. Created `triplydbHelper.js` utility and `PublishDialog` component.

---

### v1.5.x — Modularisation & RPP Architecture (January 2026)

**v1.5.2**

TTL generation for DMN fully moved to `ttlGenerator.js`. DMN output variables now extracted (previously only inputs). Fixed auto-generated request body producing empty values, which caused DMN evaluations to return null.

**v1.5.1**

Complete four-phase modularisation: state management extracted to `useEditorState`, TTL generation to `TTLGenerator` class, import logic to `importHandler.js`, array operations to `useArrayHandlers`. Rules–Policy–Parameters (RPP) separation pattern visualised with colour-coded tab badges and explanatory architecture banners. Seven bug fixes including: missing `cprmv:hasDecisionModel` link, DMN section not appearing on TTL import, file input not resettable for re-import, iKnow mappings not surviving Clear All.

**v1.5.0**

DMN integration: upload DMN files, deploy to Operaton, and test decision evaluations. `dct:source` placeholder URI for DMN file location, `ronl:implementedBy` for the executing software system, `cpsv:isRequiredBy` back-link to the DMN model. Baseline iKnow integration: parses CognitatieAnnotation and SemanticsExport XML formats, maps to CPSV-AP fields via configurable mappings.

---

### v1.4.x — CPSV-AP 3.2.0 Compliance (December 2025)

**v1.4.1**

Fixed missing `cpsv:implements` linking each rule directly to the service it implements.

**v1.4.0**

Minimal CPSV-AP 3.2.0 compliance achieved. Key changes: Organisation class corrected to `cv:PublicOrganisation`, mandatory `cv:spatial` added, `cpsv:follows` replaced with `cv:hasLegalResource`, explicit `dct:identifier` outputs for all major entities, mandatory Rule identifiers and titles. Cost and Output sections added to Service tab with full import/export.

---

### v1.3.0 — CPRMV Tab & Modularisation (December 2025)

Dedicated CPRMV tab with JSON import for all mandatory `cprmv:{...}` fields. Component extraction: separate tab components for Service, Organisation, Legal, Rules, Parameters; Preview moved to a side panel. Changelog tab added.

---

### v1.2.2 — Clear All & Import Fixes (November 2025)

Clear All button with confirmation dialog resets all form fields. Four import bug fixes: `ronl:ParameterWaarde` parameters, `skos:prefLabel` organisation name, sequential import clearing, uncontrolled input warnings.

---

### v1.1.x — Parameters Tab (October 2025)

**v1.1.1**

Rules description field expanded to 10 rows; preview panel expanded to ~80 lines.

**v1.1.0**

Dedicated Parameters tab for `ronl:ParameterWaarde`: define income limits, asset thresholds, and percentages with notation, label, value, unit (`EUR`/`PCT`/`NUM`/etc.), description, and temporal validity dates. `schema:value` and `schema:unitCode` added.

---

### v1.0.x — Initial Release (October 2025)

**v1.0.2**

Bug fixes: BWB ID `c_` prefix stripping, TTL string escaping, URI encoding, filename sanitisation.

**v1.0.1**

TTL import: automatic parsing of CPSV-AP/CPRMV structures populates all form fields. Round-trip editing support. W3C Turtle specification compliance.

**v1.0.0**

Initial release. React + Tailwind CSS web application. Five-tab interface: Service, Organisation, Legal, Rules, Preview. Real-time TTL preview. CPSV-AP 3.0 and CPRMV 0.3.0 compliance. Azure Static Web Apps deployment at `ttl.open-regels.nl` with GitHub Actions CI/CD.

---

## Roadmap

### Completed

| Feature | Version |
|---|---|
| CPSV-AP 3.2.0 compliance | v1.4.0 |
| DMN integration (upload, deploy, test) | v1.5.0 |
| iKnow XML import | v1.5.0 |
| Full modularisation (−66% code) | v1.5.1 |
| RPP architecture visualisation | v1.5.1 |
| TriplyDB direct publishing | v1.6.0 |

---

### Planned

**Phase B — RPP Deep Integration (2026 Q1–Q2)**

Cross-references between RPP layers: "This rule implements Policy X", "This parameter is used by Rules Y, Z". Traceability visualisation and impact analysis across the Rules–Policy–Parameters graph.

**Phase 2 — Extended CPSV-AP Support (2026 Q2)**

Add Channel (`cv:Channel`), Contact Points (`cv:ContactPoint`), Criteria requirements, and Evidence requirements to complete full CPSV-AP 3.2.0 coverage.

**Phase 3 — User Experience (2026 Q3)**

Multi-language support beyond Dutch with language-specific fields and translation workflows. Pre-configured service templates for common types (AOW, bijstand, WMO). Real-time collaborative editing with comments, change tracking, and review workflows. Browser `localStorage` auto-save with crash recovery.

**Phase 4 — Technical Enhancements (2026 Q4)**

SHACL-based validation with field-level error messages and real-time compliance checking. Additional export formats: JSON-LD, RDF/XML, N-Triples, YAML. Git integration for service versioning and diff viewing.

**Phase 5 — Advanced Features (2027 Q1)**

Multi-service session management with service catalog, bulk operations, and cross-service references. Completeness scores, compliance metrics, and quality dashboards. Semantic search across services.

**Phase 6 — Enterprise Features (2027 Q2+)**

Automated regression testing and CI/CD integration for service definitions. User accounts, role-based access control, organisational workspaces, and audit logging.