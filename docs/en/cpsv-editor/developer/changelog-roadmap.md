# Changelog & Roadmap

---

## Changelog

### v1.9.x — DMN Testing Suite & Vendor Services (February 2026)

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