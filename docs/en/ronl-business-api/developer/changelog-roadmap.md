# Changelog & Roadmap

---

## Changelog

## v2.9.5 — Enhancement (April 2, 2026)

### IOU — Gebruiksscenario indienen — UX improvements

Sub-step number badges in step 6 (Concrete Example) changed from filled blue circles (`bg-blue-600 rounded-full`) to slate rounded squares (`bg-slate-500 rounded-md`), eliminating the visual collision with the section header badges which share the same shape and colour. The size was reduced from `w-6 h-6` to `w-5 h-5` to keep them visually subordinate to the section headers, and `font-mono` applied so the counter numerals read as distinct from section numbers.

Step 6 now has a remove button per row — only rendered when more than one step is present to prevent accidental full deletion. The button turns red on hover to signal destructive intent.

Step 9 (Existing Materials) gains an optional file attachment zone below the existing material checkboxes — drag-and-drop or file picker, any file type, up to 5 files at 10 MB each.

### Backend — new endpoint

`POST /v1/public/upload-file` added to `public.routes.ts`. Accepts a single file of any type via `multipart/form-data` (field name `file`), uploads it to the GitLab project uploads API using `GITLAB_TOKEN`, and returns the GitLab-generated markdown reference (`{ success: true, data: { markdown } }`). Uses a dedicated `uploadAny` multer instance without the image-only `fileFilter` used by the `/feedback` route.

The `/use-case` submission remains plain JSON (`Content-Type: application/json`). Attachments are pre-uploaded one-by-one via `POST /v1/public/upload-file` before the issue is created; the returned markdown references are appended as a `## Bijlagen · Attachments` section in the issue body. This avoids a multer v2 `req.body` field-parsing failure that occurred when text fields were submitted alongside files in `multipart/form-data` — text fields arrived as `undefined` regardless of file presence.

### Backend — development noise fix

`ExternalTaskWorker.asyncResponseTimeout` reduced to 5 000 ms when `NODE_ENV !== 'production'` (was 20 000 ms). The long-poll window exceeded the TCP keep-alive timeout on the network path between the local dev machine and the remote Operaton VM, causing repeated `ECONNRESET` poll errors in the development log. The worker still runs locally; only the poll window is shortened.

---

## v2.9.4 — Feature Release (April 1, 2026)

### Caseworker Dashboard — IOU tab (Flevoland)

New **IOU** top-nav tab added, tenant-scoped to the `flevoland` tenant via `tenants.json → leftPanelSections.iou`. The tab is visible without authentication; submission sections require login. Four sections:

| Section | Auth required | Description |
|---|---|---|
| Gebruiksscenario indienen | Yes | 10-section submission form (title, submitter, description, current situation, desired outcome, concrete example, legislation, affected parties, existing materials, priority). POSTs to `POST /v1/public/use-case`; organisation pre-filled as "Provincie Flevoland". |
| Feedback geven | Yes | Feedback form with submitter info, description, and screenshot upload — paste (Ctrl+V), drag-and-drop, or file picker; up to 5 images at 10 MB each. POSTs to `POST /v1/public/feedback`. |
| Actieve zaken | No | Read-only list of open GitLab issues via `GET /v1/public/use-cases?state=opened`. Expandable cards rendered with `react-markdown` + `remark-gfm`; parsed sections: Indiener table, Beschrijving, and Gewenst resultaat. |
| Archief | No | Same component as Actieve zaken with `state=closed`. |

The IOU badge count on the top-nav **IOU** tab is populated by `IouZakenSection` via an `onCountChange` callback — identical pattern to the task count badge on the **Projecten** tab.

`IouZakenSection` is shared by both list views; the `WORK_ITEM_FIELDS` constant controls which markdown sections are extracted and displayed per card. Main content area overflow corrected from `flex-col` to `block` so all long-form sections scroll correctly.

To enable the IOU tab for another tenant, add an `iou` key with the four section entries to that tenant's `leftPanelSections` in `tenants.json`. No code changes are required.

### Backend — IOU public endpoints

`GET /v1/public/use-cases` added to `public.routes.ts`. Lists GitLab issues for `GITLAB_PROJECT_PATH`; supports `?state=opened` (default) or `?state=closed`; returns up to 100 items sorted by `created_at` descending. Returns `iid`, `title`, `state`, `created_at`, `updated_at`, `web_url`, `labels`, `assignees`, and `description` per item. No authentication required.

`POST /v1/public/feedback` added to `public.routes.ts`. Accepts `multipart/form-data` with fields `name`, `org`, `role`, `contact`, `description`, and up to 5 image files under the field name `screenshots`. Each image is first uploaded to the GitLab project uploads API; the returned markdown references are embedded in the issue body. Uses `multer` in-memory storage with a per-file 10 MB limit and an image-only `fileFilter`. No authentication required.

Both endpoints require `GITLAB_TOKEN`, `GITLAB_BASE_URL`, and `GITLAB_PROJECT_PATH` to be set. Missing configuration returns `503 GITLAB_NOT_CONFIGURED`.

See [IOU GitLab Integration](iou-gitlab-integration.md) for full setup instructions, environment variable reference, and the curl verification steps.

---

## v2.9.3 — Feature Release (March 26, 2026)

### Caseworker Dashboard — Berichten & Regelcatalogus

- Berichten endpoint switched from hardcoded seed data to the Provincie Flevoland RSS feed (`flevoland.nl/Content/Pages/Loket?rss=news`) — same axios/regex pattern as the Nieuws service, 10-minute cache TTL.
- HTML entities decoded server-side (`nbsp`, `amp`, `euro`, `lt`, `gt`, `quot`); action link populated from RSS `<link>` element as "Lees meer".
- `getBerichtById()` now reads from the live cache instead of the removed `SEED` constant; `/berichten` and `/berichten/:id` routes made async.
- `BerichtenSection` footer row now renders `item.action` as a "Lees meer →" anchor, matching the `NieuwsSection` pattern.
- Berichten section moved above Nieuws in `leftPanelSections.home` for all tenants in `tenants.json`.
- Regelcatalogus default active tab changed from `diensten` to `organisaties`.

### Caseworker Dashboard — Producten & Diensten Catalogus

- New "Producten & Diensten" section added to the Flevoland tenant home panel — publicly accessible without login.
- Backend service fetches the Provincie Flevoland SC4.0 product feed (`flevoland.nl/loket/loketoverview?sc40=true`) — XML parsed server-side with no additional dependency, 30-minute cache TTL.
- New `GET /v1/public/producten-diensten` endpoint; returns `id`, `title`, `description`, `url`, `audience`, `onlineAanvragen`, and `modified` per item.
- `ProductenDienstenCatalogus` component: expandable 2-column card grid styled after `RegelCatalogus`, with free-text search and audience filter (Alle / Ondernemer / Particulier).
- Cards show audience badges and an "Online aanvragen" badge where applicable; expanded card links directly to the product page on flevoland.nl.
- Stats row shows total visible product count and number of online-aanvraagbare items.
- Main content area overflow corrected from `overflow-hidden` to `overflow-y-auto` — all sections with long content lists are now fully scrollable.

### AI Assistant — SSE Streaming

- `POST /v1/mcp/chat` replaced with SSE streaming — `Content-Type: text/event-stream`, headers flushed immediately, `X-Accel-Buffering: no` set for Caddy; three event types: `status` (tool call starting), `delta` (text token), `done` (loop complete).
- `client.messages.stream()` used in place of `messages.create()`; text deltas emitted immediately on all rounds so the user sees tokens arrive in real time.
- Tool result payloads capped at 12,000 characters before being added to the messages array — prevents prompt-too-long errors on multi-round queries that return large Operaton JSON responses.
- Timeout raised to 240s for the SSE endpoint.
- `POST /v1/mcp/chat` excluded from audit log middleware alongside `GET /v1/admin/audit`.
- `AbortController` threaded through the streaming loop and tool execution: fires on client disconnect and on timeout.
- `businessApi.mcp.chatStream()` async generator in `api.ts` replaces the axios POST — refreshes Keycloak token first, then consumes the SSE `ReadableStream` line-by-line and yields typed `McpChatStreamEvent` objects.
- `McpChatSection`: in-progress assistant bubble updates token-by-token on `delta` events with a blinking cursor; status line above the typing dots shows the active tool name (e.g. `Calling deployment_list…`) between rounds; Clear chat aborts any in-flight stream; `AbortController` cancelled on unmount.

---

## v2.9.2 — Refactor (March 23, 2026)

### Regelcatalogus — tab order

Tab order changed to **Organisaties → Diensten → Regels → Concepten**. The `TABS` array in `RegelCatalogus.tsx` was reordered; no data or API changes.

### Caseworker Dashboard — component extraction

`CaseworkerDashboard.tsx` reduced from ~2 500 lines to a pure shell responsible for auth state, tenant config, navigation state, and layout only — no domain logic remains in the page file. All sections extracted to `src/components/CaseworkerDashboard/`:

- `NieuwsSection`, `BerichtenSection` — own their fetch lifecycle; `PRIORITY_STYLES` and `TYPE_LABELS` moved into `BerichtenSection`
- `ArchiefSection` — owns task history fetch, grouping logic, variable cache, and expand state
- `OnboardingArchiefSection` — role-gated to `hr-medewerker`; owns completed onboarding list fetch and `DecisionViewer` expand state
- `RipFase1WipSection`, `RipFase1GereedSection` — role-gated to `infra-projectteam`; each owns its own project list fetch and viewer expand state
- `GereedschapSection` — owns all three status API calls (eDOCS, Operaton, external); `PLATFORM_TOOLS` constant moved out of the page file
- `TakenSection` — owns full task queue lifecycle including list fetch, select, claim, `TaskFormViewer` integration, and `onCountChange` callback for the top nav badge
- `HrOnboardingSection`, `RipFase1Section` — each owns its started/error state, eliminating the last uses of shared `actionMessage` state
- `AuditSection` — handles both `audit-overzicht` and `audit-details` tabs via `activeTab` prop, owns paginated fetch and load-more state
- `ProfielSection` — consumes `useProfielData` hook; owns `employeeIdInput` for manual ID lookup fallback
- `RollenSection` — consumes `useProfielData` independently; derives onboarding roles and access level display
- `useProfielData` hook introduced in `src/hooks/useProfielData.ts` — shared by `ProfielSection` and `RollenSection`
- `formatDate` extracted to `src/utils/formatDate.ts` and shared across components

---

## v2.9.1 — Feature Release (March 21, 2026)

### Archive — Completed tasks

**Archief** section added to the Projecten tab. Completed tasks are fetched from the Operaton historic task API (`GET /history/task?finished=true`) via the new `GET /v1/task/history` backend endpoint. The endpoint is tenant-scoped via the `municipality` process variable and registered before `/:id` to prevent route shadowing.

`OperatonService.getCompletedTasks(tenantId)` fetches up to 200 completed tasks sorted by `endTime` descending.

In the frontend, tasks are grouped by `processDefinitionKey` — identical to the active task queue: mono uppercase group headers, groups sorted by most recent `endTime`. Each task card shows name, completion date, and assignee. Expanding a card loads historic process variables via the existing `historicVariables` endpoint; variables are cached per `processInstanceId`.

`businessApi.task.history()` added to `api.ts` with `HistoricTask` type from `@ronl/shared`.

---

## v2.9.0 — Feature Release (March 20, 2026)

### Caseworker Dashboard — Gereedschap

New **Gereedschap** top-nav page added as a platform-scoped tab — not tenant-configured, visible to all authenticated caseworkers regardless of organisation.

Eight tool cards: CPSV Editor, CPRMV API, TriplyDB, Linked Data Explorer, Operaton Cockpit, eDOCS, SAP, KMS. Each active tool opens in a new browser tab; placeholder tools (eDOCS, SAP, KMS) show an orange **Binnenkort** badge with no open button. Operaton Cockpit and SAP are only visible to users with the `admin` role.

Live status widgets:

| Tool | Source |
|---|---|
| Operaton Cockpit | `GET /v1/health` — existing health endpoint |
| eDOCS | `GET /v1/edocs/status` — stub/live/offline |
| CPRMV API, TriplyDB, LDE | `GET /v1/health/external` — server-side HEAD requests to avoid CORS |

`GET /v1/health/external` added to `health.routes.ts`. It performs parallel HEAD requests (5-second timeout) to `acc.cprmv.open-regels.nl`, `api.open-regels.triply.cc`, and `acc.linkeddata.open-regels.nl`, returning `{ status: "up"|"down", latency: number }` per service.

Adding a new tool requires a single entry in the `PLATFORM_TOOLS` constant in `GereedschapSection.tsx`. No other code changes are required.

`businessApi.externalStatus()` added to `api.ts`. `businessApi.health()` error handling hardened to extract dependency data from axios 503 responses.

---

## v2.8.2 — March 19, 2026

### Audit log — database persistence fixes

`persistAuditLog()` in `audit.service.ts` refactored to pass an explicit named-parameter object to pg-promise instead of spreading `AuditLogEntry`. The spread caused pg-promise to throw `Property 'resourceType' doesn't exist` for any field not referenced in the SQL template (specifically `azp` added in v2.8.1), silently suppressing all audit log writes to the database on ACC.

`ipAddress` port stripping now applied in the explicit object — Azure App Service appends the port to `req.ip`, which is invalid for PostgreSQL `inet` type. This error was masked by the spread error and is now also fixed.

---

## v2.8.1 — March 19, 2026

### Audit log — M2M tenant fallback

`persistAuditLog()` now falls back to the `azp` claim when `tenantId` is absent, preventing a NOT NULL violation on `tenant_id` for service account tokens. The fallback is applied only at the point of DB persistence — `req.user.tenantId` is unchanged.

`jwt.middleware.ts` reverted: `tenantId` is set exclusively from the `municipality` claim. The earlier `azp` fallback on `req.user` caused `tenantMiddleware` to pass M2M tokens through to tenant-scoped routes, returning empty data instead of `MISSING_TENANT`.

`azp?: string` added to `AuditLogEntry` in `audit.types.ts` and to `AuthContext` in `auth.types.ts`. `azp` populated on `req.auth` in `jwt.middleware.ts` and passed through `createAuditLog()` — eliminates type casts in `audit.middleware.ts`.

---

## v2.8.0 — March 19, 2026
 
### M2M API — Operaton access
 
New `/v1/m2m/*` route group in `m2m.routes.ts` applies `jwtMiddleware` only — no `tenantMiddleware`. M2M clients are system actors not scoped to a single organisation, so tenant isolation is intentionally absent.
 
The full Operaton surface is exposed: process (list, start, status, variables, historic-variables, history, decision-document, start-form, variable-hints, delete), task (list, get, variables, form-schema, claim, complete), and decision (evaluate, get).
 
A `M2M_ALLOWED_OPERATIONS` constant at the top of `m2m.routes.ts` acts as a curation gate — comment out any entry to disable that operation with no other code changes required.
 
Dedicated Operaton instance supported via `OPERATON_M2M_BASE_URL`, `OPERATON_M2M_USERNAME`, `OPERATON_M2M_PASSWORD` — falls back to the shared instance when unset. On ACC, the M2M routes point at `operaton-doc.open-regels.nl`.
 
See [Operaton MCP Client](operaton-mcp-client.md) for the full setup, curl verification steps, and curation instructions.
 
### OperatonService — new public methods and constructor
 
`getUserTasks()` parameters made optional — `tenantId` omitted returns an unfiltered task list; existing callers with `tenantId` are unaffected.
 
`getTaskVariables(taskId)` added: resolves `processInstanceId` via `getTask()`, returns flattened process variables.
 
`listProcessInstances(params?)`, `queryProcessHistory(body)`, and `getDecisionDefinition(key)` added as thin pass-throughs to Operaton with no tenant filter, intended for M2M callers.
 
`OperatonService` constructor updated to accept optional `baseUrl`, `username`, and `password` parameters — the existing singleton instantiation is unchanged.
 
### Keycloak — operaton-mcp-client
 
New confidential client `operaton-mcp-client` registered in the `ronl` realm: service accounts enabled, Client Credentials grant only, audience mapper targeting `ronl-business-api`. No `municipality` or `organisation_type` claims — M2M client has no tenant context by design.
 
### Audit log — M2M tenant fallback
 
`extractUser()` in `jwt.middleware.ts` falls back to the `azp` claim when `municipality` is absent, preventing a NOT NULL violation on `tenant_id` for service account tokens. M2M audit entries record `tenant_id` as the Keycloak client ID (e.g. `operaton-mcp-client`).
 
---

## v2.7.0 — March 14, 2026
 
### eDOCS Service — Live Mode
 
`EdocsService` ported to `packages/backend/src/services/edocs.service.ts`: session token caching via `POST /connect`, automatic re-authentication on 401/403, `ensureWorkspace`, `uploadDocument`, `getWorkspaceDocuments`, and `healthCheck`. When `EDOCS_STUB_MODE=true` (default) all methods return realistic fake responses — the stub is fully transparent to callers.
 
`ExternalTaskWorker` ported to `packages/backend/src/services/externalTaskWorker.service.ts`: long-polling Operaton's external task API on topics `rip-edocs-workspace` and `rip-edocs-document`. The worker starts inside the `app.listen()` callback and stops cleanly on `SIGTERM`/`SIGINT`.
 
`edocs.routes.ts` rewritten to delegate to `EdocsService` — all four endpoints (`/status`, `/workspaces/ensure`, `/documents`, `/workspaces/:id/documents`) are now backed by the service rather than hardcoded stub responses.
 
`config.ts` extended with an `edocs` block reading `EDOCS_BASE_URL`, `EDOCS_LIBRARY`, `EDOCS_USER_ID`, `EDOCS_PASSWORD`, and `EDOCS_STUB_MODE`. `utils/errors.ts` added with the `getErrorMessage()` helper.
 
### Copilot Studio — eDOCS OAuth Connection
 
Keycloak client `copilot-studio-edocs` registered in `ronl-realm`: confidential, service accounts enabled, Client Credentials grant only, audience mapper targeting `ronl-business-api`. The OAuth 2.0 connection was verified end-to-end on ACC.
 
See [Copilot Studio — eDOCS OAuth Integration](copilot-studio-edocs.md) for the full setup, curl verification steps and Live Mode switch.

---

### v2.6.0 — Feature Release (March 13, 2026)

**RIP Phase 1 — Process Bundle (Flevoland)** 🏗️

- `RipPhase1Process` BPMN deployed: 17-step process covering intake → eDOCS workspace → intake meeting → intake report → approval loop → PSU → PSU report → risk file → PDP → approval loop → end.
- `RipProjectTypeAssignment` DMN maps `department` + `projectType` to `candidateGroups` (`infra-projectteam`) and `assignedRoles` (`infra-medewerker`). Hit policy FIRST; structured for per-role granularity in future iterations.
- Seven task forms: `rip-intake`, `rip-intake-meeting`, `rip-intake-report`, `rip-psu-organize`, `rip-psu-execution`, `rip-risk-file`, `rip-approval` (reusable at both approval gateways).
- Three document templates bundled in deployment: `rip-intake-report.document` (Column 2), `rip-psu-report.document` (Column 3), `rip-pdp.document` (Column 4).
- eDOCS integration via Operaton external task pattern — LDE backend worker polls topics `rip-edocs-workspace` (writes `edocsWorkspaceId`) and `rip-edocs-document` (writes `edocsIntakeReportId`, `edocsPsuReportId`, `edocsPdpId`). Stub mode (`EDOCS_STUB_MODE=true`) active by default.
- `EmployeeRoleAssignment` DMN updated: all `infrastructuur` department rules prepend `infra-projectteam` to `candidateGroups` so onboarded infrastructure employees can claim RIP tasks without a separate configuration step.

**RIP Phase 1 — Caseworker Dashboard** 🏛️

- Projecten → **RIP Fase 1 starten**: role-gated to `infra-projectteam`; starts `RipPhase1Process` with a single button; success state directs to Taken.
- Projecten → **RIP Fase 1 WIP**: lists all active `RipPhase1Process` instances for the municipality, enriched with `projectNumber`, `projectName`, `edocsWorkspaceId`, and start date. Expands to three collapsible document sections (Intakeverslag, PSU-verslag, Voorlopige Ontwerpuitgangspunten); documents not yet produced show "Nog niet beschikbaar".
- Projecten → **RIP Fase 1 gereed**: identical layout to WIP; shows completed instances with completion date via `GET /v1/rip/phase1/completed`.
- Document rendering reuses the TipTap/ProseMirror zone renderer from `DecisionViewer` with zone key normalisation (`signoff`/`signOff`, `contactInfo`/`contactInformation`).

**Backend — RIP Phase 1 Endpoints** ⚙️

- `GET /v1/rip/phase1/active` — lists active `RipPhase1Process` instances for the caseworker's municipality.
- `GET /v1/rip/phase1/:instanceId/documents` — returns all three document templates from the deployment bundle plus current process variables in a single response; absent documents return `null`.
- `GET /v1/rip/phase1/completed` — lists completed `RipPhase1Process` instances enriched with `endTime`.
- All three endpoints apply municipality-based tenant isolation consistent with all other process routes.
- eDOCS endpoints: `GET /v1/edocs/status`, `POST /v1/edocs/workspaces/ensure`, `POST /v1/edocs/documents`, `GET /v1/edocs/workspaces/:id/documents`.

**Keycloak — Flevoland RIP Roles** 🔑

- `infra-projectteam` and `infra-medewerker` realm roles added to `ronl-realm.json`.
- `test-infra-flevoland` test user added with roles `caseworker`, `infra-projectteam`, `infra-medewerker` and attributes `municipality=flevoland`, `employeeId=EMP-FLV-001`.

**Caseworker Dashboard — UX** ✨

- Procesgegevens panel restyled to match RIP WIP document sections — bordered card with consistent ▲/▼ toggle.
- `roleResult` intermediate DMN variable excluded from Procesgegevens display.
- RIP WIP zone key normalisation fixes crash when expanding Intakeverslag.

**Session Expiry Warning** ⏱️

- `SessionExpiryWarning` component mounted in the caseworker dashboard — polls token expiry every 15 seconds and shows a modal when fewer than 2 minutes remain.
- Modal offers **Sessie verlengen** (forces `updateToken`) and **Uitloggen**; unsaved form data is preserved when extending.
- Axios request interceptor upgraded to proactively call `updateToken(30)` before every API request; forces re-login if the SSO session is gone.

---

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
| RIP Phase 1 process bundle (Flevoland)                   | v2.6.0  |
| eDOCS integration — external task worker + stub mode     | v2.6.0  |
| RIP Fase 1 starten / WIP / gereed dashboard sections     | v2.6.0  |
| `infra-projectteam` and `infra-medewerker` realm roles   | v2.6.0  |
| Session expiry warning modal + proactive token refresh   | v2.6.0  |
| Audit log — database persistence (`audit_logs` table)    | v2.7.1  |
| Audit log tab in caseworker dashboard                    | v2.7.1  |
| Commercial organisation type + cross-tenant processing   | v2.7.3  |
| M2M API — `/v1/m2m/*` route group                        | v2.8.0  |
| `operaton-mcp-client` Keycloak client                    | v2.8.0  |
| Audit log — database persistence fixes                   | v2.8.2  |
| Gereedschap platform tools hub                           | v2.9.0  |
| Archief — completed task history                         | v2.9.1  |
| CaseworkerDashboard.tsx component extraction             | v2.9.2  |
| Berichten — live Provincie Flevoland RSS feed            | v2.9.3  |
| Producten & Diensten Catalogus (Flevoland)               | v2.9.3  |
| AI Assistant — SSE streaming + TriplyDB Knowledge Graph  | v2.9.3  |
| IOU tab — GitLab integration (Flevoland)                 | v2.9.4  |
| `POST /v1/public/use-cases`, `POST /v1/public/feedback`  | v2.9.4  |
| IOU form UX — step badges, add/remove, file attachments  | v2.9.5  |
| `POST /v1/public/upload-file`                            | v2.9.5  |

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
