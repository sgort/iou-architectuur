# Changelog & Roadmap

---

## Changelog

### v2.5.1 — Enhancement (March 12, 2026)

**Caseworker Dashboard — Changelog Panel** 📋

- Changelog panel button added to the caseworker dashboard header, mirroring the button already present on the login page.
- Button positioned to the right of the authenticated user block for consistent right-side placement.
- Accessible without login — visible to unauthenticated visitors alongside the public sections.

**Nieuws — Government.nl RSS Feed** 📰

- Nieuws endpoint switched from the Rijksoverheid JSON API to the Government.nl RSS feed (`feeds.rijksoverheid.nl/nieuws.rss`).
- RSS parsed server-side with no additional dependency — `axios` `responseType: text` with regex-based item extraction.
- Source attribution updated to Government.nl; CDATA and plain-text description fields both handled correctly.
- 10-minute cache TTL retained; stale cache returned on feed unavailability to prevent blank UI.

---

### v2.5.0 — Feature Release (March 12, 2026)

**Caseworker Dashboard — Regelcatalogus** 🔍

- New public section "Regelcatalogus" added to the Home tab — accessible without caseworker login.
- **Diensten tab:** Public services from the RONL knowledge graph displayed as expandable cards with full description and URI link; clicking "Toon concepten" navigates to the Concepten tab pre-filtered by that service.
- **Organisaties tab:** Implementing organisations with logo (TriplyDB assets API), homepage, and linked services.
- **Concepten tab:** NL-SBB concepts searchable by label, filterable by service; each concept has a direct link to the `skos:exactMatch` URI.
- **Regels tab:** Implementation rules grouped by service; searchable by rule name and description; groups expand automatically when searching; description expandable per rule.

**Backend — Regelcatalogus Endpoint** ⚙️

- `GET /v1/public/regelcatalogus` — no authentication required; returns services, organisations, concepts, and rules in a single response.
- Five parallel SPARQL queries against the RONL TriplyDB endpoint: `PublicService`, `PublicOrganisation`, competent authority links, NL-SBB concept traversal, and `cpsv:Rule` implementations.
- Organisation logos resolved via TriplyDB assets API to versioned CDN URLs.
- 5-minute in-memory cache per data slice; stale cache returned on TriplyDB failure to prevent blank UI.
- `RONL_SPARQL_ENDPOINT` environment variable added for overriding the default endpoint per deployment.

---

### v2.4.1 — Feature Release (March 11, 2026)

**Multi-Tenant Architecture — Organisation Types** 🏛️

- Platform extended beyond municipalities: provinces and national government agencies now supported as first-class tenant categories.
- New `OrganisationType` union type: `municipality | province | national` — shared across frontend, backend, and Keycloak (`@ronl/shared`).
- `organisationType` JWT claim added to all tokens via Keycloak protocol mapper (`organisation_type` user attribute).
- `organisationType` propagated through `AuthenticatedUser`, `JWTPayload`, and BPMN process variables.
- `TenantConfig` gains `organisationType` (required) and `organisationCode` (optional, for CBS PV codes, OIN, etc.); `municipalityCode` made optional.
- `tenants.json` extended with Provincie Flevoland (`province`, `PV24`) and UWV (`national`) as reference tenants.
- Backend error messages generalised: "municipality mismatch" → "organisation mismatch".
- PostgreSQL `tenants` table gains `organisation_type` and `organisation_code` columns.
- Keycloak realm: `organisation_type` attribute and protocol mapper added; test users for `flevoland` and `uwv` added.

---

### v2.4.0 — Feature Release (March 11, 2026)

**HR Onboarding Process** 👤

- `HrOnboardingProcess` BPMN deployed: collect employee data → DMN role assignment → HR review → notify employee.
- `EmployeeRoleAssignment` DMN maps `department` + `jobFunction` to `assignedRoles`, `candidateGroups`, and `accessLevel`.
- All user tasks use `candidateGroups="hr-medewerker"` — claim-first workflow identical to Kapvergunning.
- Process started with empty variables; first task (Collect employee data) appears in the task queue immediately.
- `hr-medewerker` realm role added; `test-hr-denhaag` and `test-onboarded-denhaag` test users added for Den Haag.
- `employeeId` protocol mapper added to `ronl-business-api-dedicated` client scope — injects `employee_id` user attribute as `employeeId` JWT claim.

**IT Handover Document** 📄

- `hr-it-handover.document` authored and bundled in `HrOnboardingProcess` deployment.
- Document linked via `ronl:documentRef` on `Task_NotifyEmployee` in `HrOnboardingProcess.bpmn`.
- Template includes medewerkergegevens, toegangsspecificaties, and step-by-step Keycloak account creation instructions for IT.
- Bindings cover `employeeId`, `firstName`, `lastName`, `municipality`, `department`, `jobFunction`, `assignedRoles`, `candidateGroups`, `accessLevel`, `startDate`.

**Caseworker Dashboard — HR Sections** 🏛️

- **Persoonlijke info → Profiel:** JWT identity card + onboarding data auto-fetched via `employeeId` claim; manual input fallback when claim absent.
- **Persoonlijke info → Rollen & rechten:** Assigned roles from completed onboarding process with access level description card.
- **Persoonlijke info → Medewerker onboarden:** Role-gated to `hr-medewerker`; starts `HrOnboardingProcess` with a single button; success state directs to task queue.
- **Persoonlijke info → Afgeronde onboardingen:** Role-gated to `hr-medewerker`; lists all completed `HrOnboardingProcess` instances for the municipality with name, employee ID, and completion date; expand to render IT handover document via `DecisionViewer`.
- `GET /v1/hr/onboarding/profile` — returns flattened historic variables for a completed onboarding by `employeeId` + municipality.
- `GET /v1/hr/onboarding/completed` — returns list of all completed onboarding instances enriched with `employeeId`, `firstName`, `lastName`.

**Caseworker Dashboard — UX Fixes** ✨

- Header user block shows `preferred_username`, LoA badge, and all role badges dynamically — supports multiple roles.
- Unauthenticated navigation to any top-nav page now defaults to the first section in the left panel, showing the login prompt immediately without a second click.
- Afgeronde onboardingen access restricted to `hr-medewerker` role — regular caseworkers see access-denied message.

---

### v2.3.0 — Feature Release (March 9, 2026)

**Citizen Dashboard — Document Template Viewer** 📄

- `DecisionViewer` now fetches `GET /v1/process/:id/decision-document` in parallel with historic variables. When a `DocumentTemplate` is bundled in the Operaton deployment, it is rendered as styled HTML — TipTap/ProseMirror JSON blocks converted to React elements, `{{variableKey}}` placeholders substituted from historic process variables. The letter layout (letterhead + contact information side-by-side, body, closing, sign-off, optional annex) mirrors the Document Composer canvas.
- Falls back to the v2.2.0 form-js readonly schema for process instances deployed before document templates were introduced.

**Backend — Decision Document Endpoint** ⚙️

- `GET /v1/process/:id/decision-document` — reads the `ronl:documentRef` attribute from the BPMN `UserTask` element via the process definition XML, fetches the named `.document` resource from the Operaton deployment bundle, and returns `{ success: true, template: DocumentTemplate }`.
- Tenant isolation applied via `municipality` variable — same pattern as `historic-variables`.
- Returns 404 `DOCUMENT_NOT_FOUND` when no `ronl:documentRef` is present or the `.document` resource is absent from the deployment bundle.
- Route ordering in `process.routes.ts` corrected: literal `/history` route and instance-ID sub-routes registered before definition-key sub-routes.

**LDE — BPMN Document Linking** 🔗

- `BpmnCanvas` properties panel writes `ronl:documentRef="<templateId>"` into the BPMN XML when a document template is linked to a `UserTask`.
- The `ronl` namespace (`http://ronl.nl/schema/1.0`) is declared on the BPMN `definitions` element.
- The linked document template is bundled as a `.document` JSON file in the one-click deployment alongside BPMN and `.form` files.

### v2.2.0 — Feature Release (March 5, 2026)

**Citizen Dashboard — Dynamic Start Form** 🌳

- Kapvergunning form replaced by `@bpmn-io/form-js` viewer — schema fetched live from the deployed process via `GET /v1/process/:key/start-form`.
- Form renders with `applicantId` and `productType` pre-populated as hidden initial data.
- On submit, form variables are passed directly to `POST /v1/process/:key/start` — no hardcoded field mapping.
- Falls back gracefully when no form is deployed (404/415).

**Caseworker Dashboard — Dynamic Task Forms** 🏛️

- `CaseReviewForm` and `NotifyApplicantForm` replaced by a single `TaskFormViewer` component.
- Form schema fetched per task via `GET /v1/task/:id/form-schema` with tenant isolation.
- Process variables pre-populated into the form at import time — caseworker sees current DMN decisions immediately.
- FEEL conditional visibility on the `tree-felling-review` form hides override fields unless caseworker selects Wijzigen.
- Falls back to a generic "Taak voltooien" button when no form is deployed (`status === 'no-form'`).

**Citizen Dashboard — Decision Viewer** 📋

- Completed applications in **Mijn aanvragen** show a **Bekijk beslissing** toggle.
- `DecisionViewer` fetches final variable state via `GET /v1/process/:id/historic-variables`.
- Readonly form renders `status`, `permitDecision`, `finalMessage`, `replacementInfo`, and `dossierReference` — caseworker-only fields excluded.
- Historic variables available immediately after process completion — no polling required.

**Backend — Form Schema Endpoints** ⚙️

- `GET /v1/process/:key/start-form` — fetches deployed start form schema; returns 415 `UNSUPPORTED_FORM_TYPE` for legacy HTML `formKey` deployments.
- `GET /v1/task/:id/form-schema` — fetches deployed task form schema with tenant isolation; treats Operaton 400 (no `formRef` set) as 404 `FORM_NOT_FOUND`.
- `POST /api/dmns/process/deploy` — deploys BPMN + subprocess BPMNs + Camunda Forms in one multipart request.

### v2.1.0 — Feature Release (March 3, 2026)

**AWB Kapvergunning Process** 🌳

- Full two-layer AWB process implementation. `AwbShellProcess` manages the procedural framework (Awb phases 1–6): identity recording, receipt acknowledgement with `dossierReference` and statutory 8-week deadline (Awb 4:13), admissibility check via `AwbCompletenessCheck` DMN (Awb 2:3), and citizen notification confirmation.
- `TreeFellingPermitSubProcess` handles the substantive decision: both `TreeFellingDecision` and `ReplacementTreeDecision` DMNs are always evaluated before the caseworker review task, giving the caseworker full context.
- `Sub_ResolveDecision` applies overrides when `reviewAction = "change"`. `camunda:historyTimeToLive` set to 365 days (shell) and 180 days (subprocess).

**Caseworker Task Queue — Claim-First Workflow** 🏛️

- All user tasks (`Sub_CaseReview`, `Task_Phase6_Notify`, `Task_RequestMissingInfo`) now use `camunda:candidateGroups="caseworker"` instead of `camunda:assignee`.
- Tasks appear as **Openstaand** in the task queue and require an explicit claim before the action form is displayed.
- Removed dead `Task_ExtractCompleteness` scriptTask from `AwbShellProcess` (had no incoming or outgoing flows, was never executed).

**Backend — Tenant Variable Serialisation** ⚙️

- Tenant middleware now stores plain scalar values.
- Process start routes wrap with `inferType()` before forwarding to Operaton.
- Resolves `Must provide 'null' or String value for value of SerializableValue type 'Json'` 500 error on `AwbShellProcess` start.

---

### Frontend — v2.0.1 — Feature Release (February 27, 2026)

**Caseworker login** 🏢

Added a dedicated caseworker login path to the MijnOmgeving landing page. A slate-coloured "Inloggen als Medewerker" button, visually separated from the three citizen IdP options by a "MEDEWERKERS" section divider, initiates the new flow. `AuthCallback` uses `check-sso` instead of `login-required`, so caseworkers with an active Keycloak SSO session bypass the login screen on subsequent visits. When a new session is required, `keycloak.login({ loginHint: '__medewerker__' })` redirects to Keycloak, where the custom `login.ftl` theme detects the sentinel and renders an indigo "Inloggen als gemeentemedewerker" context banner with "Medewerker portaal" as the page title.

### Frontend — v2.0.0 — Major Release (February 2026)

**Frontend Redesign** 🎨

- New landing page with identity provider selection (DigiD / eHerkenning / eIDAS)
- Custom Keycloak theme matching MijnOmgeving design
- Blue gradient header with rounded modern inputs
- Multi-tenant theming with CSS custom properties for runtime theme switching
- Dutch language support throughout authentication flow
- Mobile-responsive design for all screen sizes

**Authentication Flow** 🔐

- Identity Provider selection before Keycloak authentication
- DigiD, eHerkenning, and eIDAS support (infrastructure ready)
- Seamless redirect flow with `idpHint` parameter
- Session storage for IDP selection persistence
- Enhanced error handling and user feedback

**Infrastructure** 🏗️

- Azure Static Web Apps deployment with SPA fallback routing
- Custom Keycloak theme deployment to VM
- Theme volume mounting for ACC and PROD environments
- Version-controlled deployment configurations
- Manual deployment process for VM-hosted services

---

### Frontend — v1.5.0 — Feature Release (February 2026)

**Multi-Tenant Support** 🏛️

- Four municipalities supported: Utrecht, Amsterdam, Rotterdam, Den Haag
- Municipality-specific theming with custom colours and logos
- Tenant configuration via JSON for runtime theme switching
- Municipality claim in JWT tokens for backend tenant isolation
- Test users for each municipality with proper attributes

**Zorgtoeslag Calculator** 💰

- DMN-based zorgtoeslag (healthcare allowance) calculation
- Integration with Operaton BPMN/DMN engine
- Business rules evaluation via REST API
- Result display with matched rules and annotations
- Support for multiple requirement checks and income thresholds

**Security & Compliance** 🔒

- JWT audience validation for API security
- Role-based access control (citizen, caseworker, admin)
- Assurance level (LoA) claims for DigiD compliance
- Audit logging with 7-year retention
- BIO (Baseline Information Security) compliance ready

---

### Backend / Frontend — v1.0.0 — Initial Release (January–February 2026)

**Status:** Production  
**Released:** February 2026

**Backend Core**

- Secure Business API Layer for Dutch municipality government services
- OIDC Authorization Code Flow + PKCE via Keycloak 23
- Multi-tenant isolation for Utrecht, Amsterdam, Rotterdam, Den Haag
- JWT validation with JWKS caching (Redis)
- Zorgtoeslag calculation via Operaton BPMN/DMN
- Compliance-grade audit logging (PostgreSQL, 7-year retention)
- Rate limiting per IP and per tenant
- Helmet security headers (CSP, HSTS)
- Versioned REST API (`/v1/*`) following Dutch API Design Rules
- Deprecated `/api/*` routes with `Deprecation` headers

**Frontend Core** 🏗️

- Monorepo structure with frontend, backend, and shared packages
- React 18 + TypeScript frontend with Vite build
- Express + TypeScript backend with PostgreSQL
- Keycloak 23.0 for authentication and authorisation
- Operaton integration for BPMN/DMN execution

**Deployment** 🚀

- Azure Static Web Apps for frontend (ACC + PROD)
- Azure App Service for backend API
- VM-hosted Keycloak with separate ACC/PROD instances
- Caddy reverse proxy for SSL termination
- GitHub Actions for automated deployments
- Multi-tenant frontend theming via CSS custom properties
- Dynamic `tenants.json` configuration (no rebuild needed for theme changes)

**Supported municipalities**

Utrecht, Amsterdam, Rotterdam, Den Haag — each with isolated data, custom theme, role-based access, and dedicated audit logs.

**Technology versions**

| Component  | Version |
| ---------- | ------- |
| Node.js    | 20      |
| React      | 18      |
| TypeScript | 5.3     |
| Keycloak   | 23      |
| Express    | 4.18    |
| Vite       | Latest  |
| Caddy      | 2       |
| PostgreSQL | 16      |

---

## Roadmap

### Completed

| Feature                                                  | Version |
| -------------------------------------------------------- | ------- |
| Monorepo core architecture                               | v1.0.0  |
| Multi-tenant municipality support                        | v1.5.0  |
| Zorgtoeslag DMN calculator                               | v1.5.0  |
| IDP selection landing page                               | v2.0.0  |
| Custom Keycloak MijnOmgeving theme                       | v2.0.0  |
| DigiD / eHerkenning / eIDAS infrastructure               | v2.0.0  |
| Caseworker login with SSO session reuse                  | v2.0.1  |
| CI/CD Vite environment configuration                     | v2.0.2  |
| AWB Kapvergunning process (AwbShellProcess + subprocess) | v2.1.0  |
| Caseworker claim-first task queue                        | v2.1.0  |
| BPMN design criteria reference documentation             | v2.1.0  |
| Dynamic Camunda Forms — citizen start form               | v2.2.0  |
| Dynamic Camunda Forms — caseworker task forms            | v2.2.0  |
| Decision Viewer — citizen-facing historic variables      | v2.2.0  |
| Decision Document Viewer — DocumentTemplate rendering    | v2.3.0  |
| Backend decision-document endpoint                       | v2.3.0  |
| LDE BPMN document linking (`ronl:documentRef`)           | v2.3.0  |
| HR Onboarding Process (BPMN + DMN)                       | v2.4.0  |
| IT Handover Document template                            | v2.4.0  |
| Caseworker Dashboard — HR sections                       | v2.4.0  |
| Multi-tenant organisation types (province, national)     | v2.4.1  |
| `OrganisationType` claim in JWT                          | v2.4.1  |
| Caseworker Dashboard — Regelcatalogus                    | v2.5.0  |
| Backend Regelcatalogus endpoint (SPARQL + cache)         | v2.5.0  |
| Changelog Panel in caseworker dashboard header           | v2.5.1  |
| Nieuws — Government.nl RSS feed                          | v2.5.1  |

---

### Planned

**Phase 2 — Identity Provider Activation (2026 Q2)**

Live DigiD integration with BSN-based citizen authentication. eHerkenning activation for business users. eIDAS support for EU residents. Full SAML federation with Dutch government identity infrastructure.

**Phase 3 — Extended Business Rules (2026 Q2–Q3)**

Additional DMN-based benefit calculations beyond zorgtoeslag. Parameterised rule sets loaded from TriplyDB. Integration with CPSV Editor published service definitions. Case management workflow with caseworker assignment and review.

**Phase 4 — BRP Integration (2026 Q3)**

Real-time citizen data retrieval from BRP (Basisregistratie Personen). Pre-populated forms using authenticated citizen profile. Timeline navigation for historische persoonsgegevens.

**Phase 5 — Audit & Compliance Dashboard (2026 Q4)**

Real-time audit log viewer for municipality administrators. Compliance reporting against BIO baseline. DPIA (Data Protection Impact Assessment) evidence export. Role-based access management UI.
