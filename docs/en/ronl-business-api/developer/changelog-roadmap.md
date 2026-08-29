---
component: RONL Business API
---

# Changelog & Roadmap

---

## Changelog

## v2026.08.33 — The Action Majors, Verified by the Gate They Upgrade (August 2026)

> Pipeline detail: [Supply-chain gate](../../contributing/supply-chain.md).

Three Renovate pull requests, each held for the full 14-day cooldown, moved the pinned first-party actions to their current majors: `actions/checkout` to `3d3c42e5` (v7.0.1) across nine workflows, `actions/setup-node` to `820762786` (v7.0.0) across eight, and `actions/upload-artifact` to `043fb46d` (v7.0.1) in the two backend workflows. Each digest moved together with its `# vX.Y.Z` comment, which is what makes a pin readable rather than merely immutable.

This closes the Node-runtime deprecation. The pinned v4 actions targeted a Node version the runner had begun force-upgrading; v7 declares node24 natively. Pinning had deliberately frozen those versions in place, and upgrading them was kept as separate work so that a broken deploy would be attributable to one change or the other rather than to both at once.

The `checkout` upgrade also covers `zizmor.yml`, which made it the one upgrade whose failure would have been self-obscuring — a broken checkout inside the audit gate breaks the mechanism that would otherwise report it. The gate passed on all three merges, so the upgrade is verified by the thing it upgrades.

---

## v2026.08.32 — CI Work Gets Its Own Changelog Type (August 2026)

Pipeline and supply-chain work had no home in the changelog, so it landed as a chore, filed next to housekeeping — when it is the one category whose commits change how everything else is built and shipped. `ci` is now a changelog type in its own right.

It is also a release scope, and deliberately **not** a deployable one: a CI-scoped release bumps the root version only. Bumping a package version for pipeline work would trip that package's path-filtered workflow and deploy code that had not changed.

---

## v2026.08.31 — The Gate Gets Teeth: 49 Findings to Zero (August 2026)

> Pipeline detail: [Supply-chain gate](../../contributing/supply-chain.md) · [CI/CD](cicd.md).

**Every action reference is now an immutable commit digest.** All 27 `uses:` references across eight workflows were pinned, each at its then-current major so the change stayed behaviour-preserving. A tag can be moved; a digest cannot — and the Static Web Apps deploy action referenced here publishes one ref as *both* a 2021 tag and a 2024 branch head, 3.5 years apart, across nine references in four deploy pipelines.

**Credentials are no longer left in the workspace.** Before this, `actions/checkout` wrote a live `GITHUB_TOKEN` into `.git/config`, which was then mounted into a closed-source third-party container. `persist-credentials: false` is now set everywhere. Token scope drops to read-only by default, with write granted only to the six jobs that comment on pull requests, and none at all to the three that only tear down a preview environment.

**A blocking audit gate enforces it.** The `audit` job runs zizmor on every pull request and on pushes to `acc` and `main`, pinned to an exact tool version rather than the action's default of `latest` — a supply-chain gate that pulled an unpinned tool would defeat itself. Together with an `acc` ruleset requiring a pull request and a passing check, the workflow became enforcement rather than advice: the check alone would still have let a direct push bypass it.

**Renovate keeps the pins alive.** Its configuration had to land *before* the app was installed, because Renovate reads configuration only from the default branch. Updates are held for fourteen days so vendors and researchers have time to find problems, with one deliberate exception — security advisories bypass the wait entirely, which is the clause most cooldown policies omit and the reason such policies get switched off mid-incident.

**The register was corrected on one important point.** It had implied CI deploys the backend. It does not: the backend workflows build, test and upload an artifact with no deploy step at all.

Squash and rebase merging were disabled repo-wide, leaving merge commits only — changelog entries name commits by SHA, and both alternatives rewrite those hashes, rebase deceptively so since it preserves the commit count while replacing every hash. Releases consequently land through a pull request rather than a local fast-forward. The lockfile's `engines` were brought into line with `package.json`, committed as its own change rather than riding along in an unrelated one.

---

## v2026.08.30 — Guards for the Duplication the Extraction Did Not Reach (August 2026)

The investigation changed its own framing twice. Three of the four listed duplications turned out to be **required copies rather than decay**: the demo never imports the caseworker stylesheet, so the package must carry its own rule for every class its components render, or the demo renders unstyled. The answer was therefore to make divergence detectable, not to remove it.

**The five brand colours are pinned across all four files** — two stylesheet root blocks and two build-config fallbacks. One fact, four hand-maintained copies, previously with nothing keeping them in step. **Every rendered class must be styled in both sheets**, so a package-owned component that grows a new class fails the guard rather than letting the demo silently render unstyled. Both guards strip CSS comments before matching, because a class named only inside a comment would otherwise count as defined — a hole that a later task in the same plan would have opened by adding prose comments naming real selectors.

**The demo's auth adapter is pinned, including where it correctly differs** from the frontend's. The two differ in exactly two places and both differences are right, so the test pins the differences too rather than asserting a false equivalence.

Stylesheet citations now cite by anchor rather than line number, after an eleven-line comment inserted near the top of a shared stylesheet shifted every citation below it — one of them landing mid-declaration inside an unrelated rule.

---

## v2026.08.29 — The Session Seam Goes Back to the Host (August 2026)

> Test detail: [PA cockpit — tests](testing/dashboards/pa-cockpit.md).

The package had hardcoded five facts belonging to a host application: two session-storage key names, an identity-provider literal and two router paths. That protocol is a house convention shared by five files in the caseworker frontend — the cockpit was its sixth participant, and extraction had stranded it outside the app that owns the convention. Session controls are now handed back: optional login and logout callbacks are added to the host contract and both hosts wired to supply them, the cockpit's three control sites key off those callbacks, and `logout` leaves the auth contract once nothing calls it. Each step leaves all five workspaces green.

**The parallel-run flakiness was timeouts, not shared state.** The frontend suite is green in five consecutive parallel runs on an idle machine and produces 8–16 failures under concurrent load — every one of them a timeout at Vitest's 5000ms default, which none of the four Vitest workspaces had overridden. The affected file set tracks machine load rather than any property of the tests, which is what ruled out contention. `testTimeout` is now 20s in all four.

**Every workspace gained a `test:serial` script.** The repo runs two test runners behind one command shape — the backend on Jest, the other four on Vitest — so any serial flag a caller reaches for is right in four places and wrong in the fifth, and Jest rejects the Vitest ones outright. A named script per workspace means the runner's identity stops being something the caller has to know.

Two guard residuals closed: a decoy function declared in an inner scope could disarm the modes rule for a whole file while compiling with zero type and lint errors, and the auth-path guard's needle was quote-wrapped so a double-quoted path or a template literal walked straight past it.

---

## v2026.08.28 — The Fork Is Deleted (August 2026)

**The demo renders from the package, and the vendored copy is gone** — 44 files and 1.1 MB of byte-identical cockpit, together with the manifest, sync script, byte-level drift checker and the workflow that ran it. That deletion is what the whole extraction was for. The demo now supplies its own host adapter rather than overlaying files, which is the seam the vendored fork existed to discover.

**The bundle gate had silently no-opped on Windows.** Both bundle-check scripts guarded their entry point by comparing a module URL against the process argument; on Windows that argument is a drive-letter path with backslashes, so the comparison never held. The gate exited zero having checked nothing, and the build passed. Both scripts run as the last step of every build for two public, unauthenticated sites, checking for auth libraries, telemetry and backend origins — on Windows, none of that had ever been checked.

`pa-cockpit` was wired into the CI path filters and the release scoping, without which a change to the cockpit would trigger nothing and version nothing. The demo now starts alongside the other dev servers, which matters once a cockpit change affects both apps. Deny-by-default section filtering and the user forward were pinned by regression tests, and the demo gained its own changelog panel rather than a vendored stand-in.

---

## v2026.08.27 — The Cockpit Becomes `@ronl/pa-cockpit` (August 2026)

> Developer detail: [PA-Cockpit package](pa-cockpit-package.md).

Thirteen tasks against an approved design, in an order that is load-bearing: pure data and mode config first so later tasks have something to import, the API services next because they carry the auth seam and nothing else, then the views, then the modes context, and the shell last since it carries all five seams.

**The host declares what it provides.** The package publishes the interface a host must satisfy to mount the cockpit — auth and tenant services, plus the components the shell renders but does not own. The shell takes those seams as a **required** prop rather than an optional one, so a host cannot silently omit a seam and discover it at runtime. Auth and tenant resolve through configured getters inside functions, so a refreshed token is never captured by value and left stale.

**One `PaSectionsRouter` replaces a fourteen-export surface.** The frontend's section router and the demo's carried byte-identical id groupings, an identical panel dispatch and an identical remount branch — section-id grammar about the package's own ids, not host knowledge. Exporting fourteen components and asking every host to hand-maintain that grammar would have kept the vendored fork's most-duplicated behaviour, merely formalised.

The rail and command palette now derive from the mode set the host injects, which is what lets the demo present a curated subset without the package knowing anything about curation. The notifications panel dropped Tailwind for scoped `pac-*` rules, using the literal Tailwind-computed values rather than the nearest design token so the rendered result stays pixel-identical.

The frontend deliberately does not type-check between two of these tasks. That was stated up front in the plan so an implementer would not try to repair it early and fight the migration.

---

## v2026.08.26 — A Social Card, and the Tenant Config That Should Never Have Shipped (August 2026)

**18 KB of internal multi-tenant configuration was being deployed to the public demo.** Because the asset vendor root was the public directory, vendoring the tenant config shipped real contact details, non-public sections, entries explicitly flagged as not public, and the very IOU sections the demo deliberately drops. Nothing in the demo ever fetched it; its only consumer was a drift test, which now reads the frontend copy directly.

**The demo gained an Open Graph social card** — 1200×630, with a full OG and Twitter meta block and a description tag it never had. The part needing care is the origin: a static `index.html` cannot know its own deploy target, and the OG specification requires absolute URLs because scrapers do not resolve relative paths. The page is authored against production and a build plugin rewrites the URL and image to whichever origin is being built; without it, an acceptance deploy would advertise production assets.

**The E2E suite runs in the acceptance deploy workflow** — the first Playwright suite in this repository to run in CI at all. It is the only proof of two of the four no-Live layers: that the live toggle is actually hidden in a real browser's cascade, and that the page issues no network request. The demo needs no backend, database or Keycloak; Playwright starts its own dev server and that is the whole environment.

**The mock-only environment invariant is now actually guarded.** The existing lock test only ever proved the test environment file, because Vitest's mode is always `test` — nothing read the production or acceptance files, so deleting a mock flag from either would have left every check green. A new test asserts across all four environment files that the three mock flags are true and the API URL absent, verified red then green.

The floating assistant toggle turned out to be a one-way trap rather than a dead control: clicking it set the open flag, which both hid the button and rendered a null shim, leaving nothing able to unset it. The backend-request guard now compares against the run's own origin instead of hardcoding localhost, which had produced two false failures against the acceptance site. A curated executive-summary changelog replaced the placeholder, covering the CalVer releases in eight themed entries rather than re-listing every commit.

---

## v2026.08.25 — The Demo Bar Retired, the Theme Applied at Runtime (August 2026)

The role selector had existed in three places — the demo bar, Beheer → Rollen & rechten, and Dossierbeheer's inert vendored role bar — plus two separate resets. Role switching now lives only on Rollen & rechten, and reset only in Dossierbeheer's own mock banner.

**The cockpit was silently rebranding itself orange.** Its stylesheets read theme custom properties with Flevoland blue and magenta as *fallbacks*, which apply only while those properties are undefined — and the vendored global stylesheet set them to generic RONL blue and orange at the root, satisfying the fallback. The theme is now applied at runtime on the document element, which is how the real tenant service solves it for every tenant, and wins the cascade over an inherited value.

**Every monitor icon 404ed on two sections.** A vendored component reads 14 icons from a hard-coded path rather than an import, so a manifest that discovers files by following imports could never find them. A second asset root now sits alongside the source manifest. Tailwind, PostCSS and Autoprefixer were vendored at the exact versions the frontend pins, fixing three visual bugs caused by utility classes never being processed at all, and a double scrollbar was removed by capping the root to the viewport in a column flexbox.

Deploy workflows for `acc.plato.open-regels.nl` and `plato.open-regels.nl` landed alongside a vendor-drift workflow, triggered on frontend source pushes rather than demo ones since the deploy workflows are path-filtered to the demo package and would never see an edit to the origin the copy tracks.

---

## v2026.08.24 — A Public, Mock-Only PA Cockpit (August 2026)

> User guide: [PA-Cockpit demo](../user-guide/pa-demo.md) · Test detail: [PA-demo suite](testing/pa-demo.md).

A showcase instance of the Public Affairs cockpit on an unauthenticated public site, with no option to switch to Live. Mock mode was already a working demo driven by the same mutation actions live uses, so the work was packaging and severing auth rather than building demo behaviour.

**It shipped as a vendored copy deliberately ahead of extracting the package, not after it.** An extraction has to commit to an interface, and nothing outside `packages/frontend` had ever consumed the cockpit — so building a real second consumer first made that boundary empirical instead of imagined, and left the shipping cockpit alone during a 342-commit promotion.

**Sections are curated by a deny-by-default allow-list**: 21 static ids plus the data-driven dossiers sentinel, with five dropped ids, reconciled one-to-one against the real modes config's 26 rail items. The filter is applied at the data source rather than at the router, because the command palette calls the section list directly with no props — filtering anywhere else would have missed it.

**No-Live is enforced twice over.** `staticwebapp.config.json` ships a CSP with `connect-src 'self'`, so the browser refuses any outbound request the demo's code might someday make. The stronger layer is a build-time bundle gate that scans every built `.js` file for auth libraries, telemetry and the real backend origins and fails the build if any appear — proving the URL is not in the bundle to be requested at all. Dossierbeheer's own switch-to-live button is suppressed separately: a visitor clicking it mid-demo would have flipped the cockpit to live against a backend that does not exist, in front of the audience the demo exists to persuade.

Selecting a role rewrites the shim's synthetic Keycloak roles array and derives capabilities through the product's own `deriveDossierRole`, so capability chips, editor lock hints and every disabled action follow, with no vendored file touched. Four positions are offered with the broadest as the default — a visitor should see the whole product before being shown what a narrower role loses. Profiel and Rollen & rechten are demo-owned pages rather than reused caseworker ones, and five Playwright tests drive the journey end to end with no backend, database or Keycloak.

---

## v2026.08.23 — Mock Mode Made Real, and the Throttle That Looked Like an Outage (August 2026)

> Test detail: [PA cockpit — tests](testing/dashboards/pa-cockpit.md).

### Mock mode becomes a working demo, driven end to end

Mock mode stopped being a read-only snapshot: curating a signal moves the rail badges and the move survives a reload, an ignored signal stays ignored, and *Reset demodata* restores every source to its fixture baseline. Every signaalbron now carries a watchlist orphan that can be linked to a dossier, and the demo counts are no longer identical across sources. `PA_USE_MOCK` was dropped — nothing read it.

Two Playwright specs now drive the cockpit: `pa-mock-journey.spec.ts` against the real store with no mocking, and `pa-live-authoring.spec.ts` against the live backend and a real database. Every mock-mode defect fixed in this window was invisible to the unit suites by construction — a saved-search write that was a bare `return;`, a confirm that built an object and discarded it, notifications hardcoded to empty — because a component test mocks the very seam that was broken.

### The shipped rate limit was below what the cockpit costs to use

One short authoring journey measures 21 requests to `/v1/pa/*` against a 100/minute per-IP budget, so two specs back to back exhausted it, and the UI rendered the resulting 429 as *"Kon dossiers niet laden"* — indistinguishable from a backend that is down. The default is now 1000/minute, and `e2e/helpers/rate-limit.ts` fails a test with a message naming the throttle rather than retrying past it.

### Mocks that could not pass vacuously

`expectMockNamesRealExports` originally compared a mocked path against the mock — itself — and would have passed no matter what; it was caught by injecting a bogus export and noticing the assertion failed to fail. Both `mockModule` helpers now require `importActual`/`requireActual`, the PA mocks are built on the real modules rather than replacing them, and a parity-checked stub for the `usePaData` context fails loudly when a member is added to one side and not the other.

### Data-integrity and feed fixes

Deleting a dossier now takes its signals and zoekcriteria with it. A created dossier is on the overview by the time you arrive there. TK is fetched one term at a time so multi-term criteria stop aborting, an empty cached feed is no longer served for the rest of its TTL, and the rail's confirmed counter no longer freezes at mount.

---

## v2026.08.22 — EU Feed Recovery and One Switch for the Cockpit (August 2026)

**The mock/live toggle is now one switch for the whole cockpit**, and demo data stopped leaking into the live database — neither the demo taxonomy nor demo dossiers are seeded there any more.

**Half the plenary feed was missing.** EU refs are now recovered from the guid, restoring it. Europarl receives a `User-Agent` and an empty `202` is no longer read as a feed; EP motions that arrive once per political group are collapsed into a single signal; EP press releases are surfaced and `commissie` is populated for EU items. The raw EU feed can now be searched from the cockpit directly.

**Inbox badges stay current** instead of freezing at page load, and every badge is populated on mount from a single counts request.

M2M decision checks became environment-aware, and the local client secret is read from the realm export rather than from `.env`.

---

## v2026.08.21 — Backend Coverage, and Nine Test Files That Never Compiled (August 2026)

> Test detail: [Backend suite](testing/backend.md) · [Writing tests](testing/writing-tests.md).

**Backend test files made modules so their globals stop colliding.** Nine test files had no top-level `import` or `export`, which makes each a global script to TypeScript, so every top-level declaration landed in the global scope: `mockAxios` collided across five files, `Mod` and `freshModule` across six each. The suite passed locally for weeks because ts-jest caches type diagnostics per file; the first CI run on a cold runner failed immediately. Adding `export {};` to each scopes them.

**Backend branch and function coverage lifted above 80% for every file.** This is the release that took `utils/` from 43.47% statements and 6.54% branches — long documented as an accepted artifact, with `config.ts` at 0% and `logger.ts` mocked everywhere — to **100% across all four metrics**, `tls-bootstrap.ts` included. Backend coverage overall moved from 94.28/73.54/94.13/95.69 to 98.35/91.49/96.65/98.75.

**Required-env checks now actually fire**, and `/v1/health` reports the deployment tier. A seed dossier without an owner is now a compile error, `inferType` was extracted from four routers into one tested helper, and local M2M targets the Docker Operaton so its route script runs locally.

---

## v2026.08.20 — Every Deploy Gated on Its Tests (August 2026)

### Backend and frontend deploys now run the suites

Public-site was the only package whose pipeline could block a deploy. Backend CI linted and built but never ran its 1145 Jest tests; frontend CI ran neither lint nor test, going straight from `npm ci` to `vite build` to deploy. For those two, `npm test` was a manual discipline enforced by review rather than an automated gate. The backend workflows gain a Jest step beside their existing linter, and the frontend workflows gain a linter, the Vitest suite, and the performance budget as a step of its own.

### The simEngine budget moved rather than moved up

`simEngine.ts` carries a real budget: `run(cfg)` must process the default 3,150-application population in under 250ms, and its source comment is emphatic that the threshold must not be loosened — the intended remedy is a web worker, not a bigger number. The problem was never the threshold but what the assertion measured. On a contended host it was observed at 302ms, then 837ms, then 1297ms; inside a full `npm test`, where Vitest saturates every core with 130 parallel files, even the fastest of three CPU-time samples came out at 468ms, against ~100ms in isolation. Wiring the CI gate would have made that a permanently red pipeline. The assertion now lives in `simEngine.perf.test.ts`, still asserting `< 250ms`, run by `npm run test:perf` with file parallelism disabled and gated as its own CI step. `ChangelogPanel.test.tsx` was the other casualty of the same contention — 15s timeout, observed at 22s — raised to 60s, since a timeout catches a hang rather than asserting a speed.

### Two Vitest config defects, and a lint-staged blind spot

`setupFiles` resolved against the process cwd rather than the config file, so the single-file command documented on the [Testing](testing/overview.md) page failed from the repo root and worked only from inside the package. `coverage.reportOnFailure` is now set in both frontend and public-site, so a red run keeps its coverage figures instead of discarding them exactly when they are wanted. And `lint-staged` had globs for frontend, backend and shared but none for `packages/public-site`, so a staged public-site source file got neither ESLint nor Prettier at commit time — `pre-push` always caught it, but a local commit could carry it.

---

## v2026.08.19 — DMN Downloads + Tenant-Mandatory Deployment Closed Out (August 2026)

### DMN source files downloadable from the public rule catalogue

The public site now joins the Linked Data Explorer's published-DMN list onto Regelcatalogus services and offers the DMN 1.3 XML as a download row in each rule's Technical details. A new `getPublicDmnsByService()` in `lde.service` fetches `/v1/dmns` for the RONL graph, groups the result by service URI, caches for five minutes, and returns an empty map on failure so the catalogue still renders when LDE is unreachable; the relative `xmlUrl` is resolved against the configured API URL rather than concatenated, which is what keeps `/v1` from doubling. `SPARQL_ENDPOINT` is now exported from `regelcatalogus.service` so LDE is queried against the same graph instead of a second copy of the URL. Regel items carry `dmns` only when LDE knows the service, so unmatched services simply render no download row; `TechDetails` takes an optional `downloads` prop rendering a "download DMN (xml)" row inside the existing key/value table, with several DMNs for one service stacking under one key. Because the link points straight at LDE, the saved filename comes from its `Content-Disposition`, which uses the Operaton decision key — where that key is a generated GUID (the HvA export) the download name differs from the displayed title, an accepted gap since the real fix belongs at the source deployment rather than here.

### Tenant-mandatory deployment: the design plan executed against a real two-tenant Operaton

The release that motivated all of this: starting `RipR21Process` (at the time still named `RipPhase1Process`) from Beheer → R2.1 → Starten failed with "is niet gevonden", even though the Faseladder's own deploy-status check correctly showed it as deployed. The root cause was `startProcess` calling only Operaton's untenanted `/process-definition/key/{key}/start` shorthand, which Operaton only resolves against definitions deployed with no tenant-id — but this process is now deployed with a native tenant-id. The fix tries the tenant-scoped start endpoint first and falls back to the untenanted one only on Operaton's specific "no matching process definition" response, so every process deployed before this point keeps working unchanged.

That fix was followed by a full design and implementation plan (all 53 `OperatonService` Operaton calls read and categorized) for closing the two remaining tenant-scoping gaps, redeploying the five active process bundles under their correct tenants, and standing up a single-source-of-truth E2E test bundle at `linked-data-explorer/e2e-fixtures/<tenant>/`, replacing two pre-existing, already-diverged "examples" locations. Executed against a real, live, two-tenant Operaton instance rather than unit mocks alone, it surfaced two further genuine regressions only once real cross-tenant traffic was exercised for the first time: a cross-tenant process-start lookup bug, and Operaton's DMN business-rule-task tenant resolution requiring an explicit `camunda:decisionRefTenantId` override for shared decision tables once the calling process itself becomes tenant-scoped — both confirmed via a live, throwaway empirical spike before being applied for real.

Concretely, this release also: renamed the process key from `RipPhase1Process` to the self-describing `RipR21Process`, matching the Faseladder's own R2.1 stage code, end to end across the shared `RIP_PHASE_KEYS` catalog, both backend query filters, the frontend's start action, and every asserting test; fixed `startProcess` and `getDeployedStartForm` to discover a process's actual deployed tenant via Operaton's unscoped list endpoint rather than assuming it matches the caller's own tenant, which broke `AwbZorgtoeslagProcess` — always handled under the toeslagen tenant by design, callable by citizens of any tenant; closed a cross-tenant data leak in `GET /v1/rip/phases/deployment-status` and `/v1/rip/phases/counts`, which queried Operaton with no tenant filter at all — `getPhaseInstanceCounts` in particular counted every running instance of a process-definition key globally, almost certainly the mechanism behind an earlier-observed Portfolio/Faseladder discrepancy, fixed by threading the caseworker's tenant through Operaton's native `tenantIdIn` filter; and fixed two more untenanted-key lookups, `getBoardOwner` (degraded silently to "untagged" via a try/catch, quietly breaking the Beheer archive's board split) and `getDeployedStartForm` (threw outright, breaking the citizen-facing "start a new case" flow), both now sharing the tenant-scoped-then-fallback helper `startProcess` established.

### E2E hardening, reporting UX, and an accessibility correction

`global-setup.ts` now queries Operaton directly for the five processes the E2E suite requires and fails fast with a specific message — which key, which tenant, what to do — before any test runs, rather than a mismatch surfacing as a confusing failure deep inside an unrelated spec; it verifies only, never deploys. Separately, the Operaton-history cleanup prompt is consolidated from one confirmation per business key (a dozen instances meant a dozen `[y/N]` prompts) to a single prompt covering all pending keys at once, and Playwright's HTML report now opens automatically after every run instead of relying on a `show-report` hint that could resolve to the wrong path (it's computed relative to the npm workspace's internal working directory, not the shell the command was typed in). `linked-data-explorer`'s E2E fixture sub-processes were also renamed with an `E2E` suffix to give them their own process-definition keys, distinct from the general-purpose seeded examples sharing the same BPMN process id.

Finally, the accessibility statement's claim that every interactive element gets a 2px black-and-yellow focus indicator was corrected — an earlier release (`2026.08.1`) had already changed form-field focus to black-and-blue on request, but the statement was never updated to match; confirmed directly against the shipped CSS and reworded rather than reverted, since the blue was a deliberate change.

## v2026.08.18 — Regelsimulatie: a Deterministic Budget-Exhaustion Simulator (August 2026)

### The simulation engine

A new, deterministic, pure-TypeScript engine ports the Flevoland home-battery subsidy's budget-exhaustion simulation: entitlement rules, amount calculation, split/merged budget pools with a 1 October boundary and year-to-year carry-over, first-come-first-served allocation with no back-fill once a pool seals, and two counterfactual re-runs isolating how much of the unpaid total is attributable to an information-request delay versus a successful appeal. Twenty-two tests cover determinism, amount boundaries, entitlement precedence, resolver sealing and priority ordering, full-run bookkeeping invariants, the budget-year-is-submission-year rule, both counterfactuals, and a performance budget (under 250ms for the default 3,150-application population). A review found the port's appeal-displacement attribution logic — which appeal "displaced" a given application — actually diverges from the reference implementation: the reference compares against a field that's never set on the object type involved, making that branch permanently dead code there, while the port's version can correctly pick the nearest-preceding appeal winner instead of always the pool's overall minimum. Confirmed with the project owner as intended behaviour rather than a bug to revert; it only affects which application id is shown in one caption, not totals or payment outcomes, and is now disclosed in a code comment with a test proving the two strategies diverge.

### UI: RegelSimulatie section, chart, and presentational primitives

The section shell ties the engine to a header, a collapsible scenario-parameter panel of fifteen sliders, a playback control bar, and a two-column card layout, recomputing the simulation only when a parameter actually changes, never while scrubbing the timeline. `SimChart` renders the saw-tooth budget-over-time chart as hand-rolled SVG with no charting library — free vs. reserved budget, split and merged pot phases, exhaustion markers, and the current-day indicator — alongside `SimMissedPanel`, the "Geldige aanvragen die misliepen" panel with three filters (RFI priority-shift, successful appeal, all unpaid) over a per-application timeline. The smaller presentational primitives (`SimPot`, `SimOutcomeRow`, `SimTweak`) and a dedicated `simFormat.ts` module (extracted from `SimPot.tsx` after it broke Vite's react-refresh assumption that a component file exports only components) round out the surface, ported unchanged and scoped under the existing `.cwd-v2` design tokens with no new colours. The feature is wired into the V2 shell as a new Simulatie mode between Zoeken and Beheer, with a Regelsimulatie rail item gated behind both a per-item auth requirement and a separate tenant-visibility gate.

### Review fixes: a slider freeze, persistence scoping, and a rename

The final whole-branch review found a genuine multi-second main-thread freeze while dragging a parameter slider at settings the UI itself exposes (population or RFI chance near their max) — every drag step fired a full engine run synchronously — fixed by decoupling a slider's visual position from when its value actually commits, on release rather than on every step. The review also added a missing `type="button"` attribute and accessible slider labels, corrected a silent trailing-zero formatting divergence and an unclamped restored-from-storage scenario value, and separately fixed the persisted playback day: it had shared one localStorage key with the scenario parameters, so a caseworker could land on a fully-played-through simulation (day 719/719) left behind by an earlier visit. Scenario parameters stay under the shared key — there's no per-user meaning to a set of sliders — but the playback day now lives under a key scoped by the caseworker's stable Keycloak `sub`, so a different caseworker, or the same one on a first visit, always starts at day 0. The rail label was also renamed from the generic "Regelsimulatie" to the specific "Subsidie thuisbatterij," since the Simulatie mode is deliberately built to hold more than one simulation later and needs a name that won't collide with an equally generic sibling.

## v2026.08.17 — Faseladder Content Correction: Rule Sets Per Competent Authority (August 2026)

The public site's "Verifiëren & live" pipeline stage note claimed a citizen always sees one environment behind which sit exactly two rule sets from two competent authorities. Corrected to "one or more rule sets from corresponding competent authorities" — not every deployment involves exactly two authorities.

## v2026.08.16 — Herkomst Polish: Scroll, Citations, and Prerendering (August 2026)

Following the Herkomst provenance page introduced in `2026.08.15`, four fixes tightened it up. Selecting a concept, drilling into a chip, clicking a trail segment, or "Begin opnieuw" could each change which concept's trace is shown without the page scrolling, leaving the new concept's trail bar and header off-screen if the reader was scrolled deep into a long trace; the jump buttons' existing scroll-to-id helper was extracted into a shared `herkomstScroll.ts`, which `HerkomstExplorer` now calls on every concept change. `/herkomst` was in the sitemap `urls` array but, unlike every other content route (berichten, nieuws, producten, regels, processen), had no `writeRoute()` call, so a crawler that doesn't execute JS got the homepage's title and description via Azure's SPA `navigationFallback` instead of Herkomst's own — its title, description, and crawlable summary are now sourced directly from `herkomstData.ts`/`herkomstConcepts.ts`, verified against a real `build:acc` output. Three legal citations were also corrected against the content owner's sources: the Leeftijd concept's Wet op de zorgtoeslag citation (art. 1 lid 1 onder b → onder c), and the BSN and Datum berekening concepts' `wet.tekst` fields, which had been paraphrases and are now exact statutory quotes with corrected `bron` references. Finally, `HerkomstExplorer.tsx`'s plain-function export `nextTrail` — which broke Vite's react-refresh assumption that a component file exports only components — was moved into its own `herkomstTrail.ts` module with its own test.

## v2026.08.15 — Social Card + the Herkomst Provenance Page (August 2026)

### Sitewide Open Graph / Twitter social card

Sitewide `og:*`/`twitter:` meta tags were added to `index.html`, plus a 1200×630 `og-open-regels.png` asset, per the design handoff's social card addition — confirmed sitewide rather than per-page is correct, since the prerender script only ever swaps `<title>`/`<meta name="description">` and never touches `og:*`/`twitter:` tags, so every prerendered route already carries the same card.

### Herkomst: tracing a concept from statute to screen

A new provenance feature, Herkomst, walks a citizen-facing question back to its legal source. `HerkomstTrace` is the core component — an eight-step, two-track grid tracing a concept from quoted legal text (Wet- & Regelgeving) to the question a citizen sees on screen (Gebruikers), row-aligned step for step, handling both chain-end cases (no-DMN concepts render an explanatory fallback line; concepts with nothing left to derive from render "einde van de keten" instead of chips). `HerkomstChip` is the clickable concept chip used throughout — either a button drilling into another concept, or a plain leaf chip carrying its own inline definition — and `HerkomstBackground` renders the grey background band below the trace: the four-stage pipeline, the (a)/(b)/(c) concept chain with its catalogue band, and the open/gesloten standards list. `HerkomstExplorer` ties it together, owning the drill-down trail state: selecting a concept in the list resets it, drilling into a chip pushes onto it (a no-op if already on that concept), trail segments truncate to that depth, and "Begin opnieuw" resets to the first concept. The page itself wires all six components together at `/herkomst`, with a breadcrumb, page head, jump links, a nav item after Gegevenswoordenboek, and a `HERKOMST_PATH` constant mirroring the existing `WOORDENBOEK_PATH` pattern. Content — four concepts (Leeftijd, Geboortedatum, Datumberekening, BSN), each with quoted legal text, annotation, rule, DMN expression and citizen-facing copy — was ported byte-identical from the design handoff's hand-authored reference content, independently verified via a field-by-field deep-equal check rather than visual proofreading alone; styling was ported into `pub.css` with every `.k-` class prefix renamed to `.pub-herkomst-` to match the codebase's convention.

A final whole-branch review caught three gaps a task-scoped review couldn't have: the deliberate accessibility improvement associating track headers with their cells used `aria-labelledby` on plain `<div>`s, which ARIA prohibits on the `role=generic` a bare div computes to — likely never reaching assistive tech, fixed by adding `role="group"` to all eight cells; `/herkomst` was never registered in the sitemap/prerender pipeline, since no single task had that file in scope; and the drill-down trail was a bare div where the spec required a real breadcrumb `nav` landmark. A second CSS-scoping gap slipped through the initial port too: the task brief covered renaming the reference stylesheet's hyphenated component classes but not its space-descendant-combinator rules, so bare global `h1`–`h4`/`p` selectors and a global `.pub-nav a` override (from the reference prototype's own internal preview-shell nav) collided with the real site's styling — fixed by scoping headings/paragraphs under a new `.pub-herkomst-k` page-root class and deleting the four unused nav rules. Separately, a test asserting the trail's no-op guard actually exercised the wrong interaction path (a nav-list click rather than a chip drill-down) and would still pass with the guard deleted; the trail-update logic was extracted as a pure, directly-unit-tested function, `nextTrail`.

## v2026.08.14 — Build Fixes: Rollup CJS Interop and a ChangelogPanel Matcher (August 2026)

Two real build/tooling bugs were fixed. `vite build` goes through Rollup directly rather than `vite dev`'s esbuild pre-bundler, and Rollup by default only runs CommonJS→ESM interop on `node_modules/**`; since `@ronl/shared` resolves to a relative workspace path (`../shared/dist`), Rollup parsed it as plain ESM, found no literal `export` keyword, and reported every named value import (`RIP_PHASE_KEYS`) as not exported. This only ever surfaced once `vite build --mode acceptance` actually ran in CI, since local dev used an already-fixed dev-server path (`optimizeDeps.include`); both `build:acc` and `build:prod` are now verified to succeed with `RIP_PHASE_KEYS` actually present in the emitted bundle. Separately, `ChangelogPanel`'s version-button matcher used a bare `.includes()` check that became ambiguous once double-digit CalVer patches existed — `v2026.08.1` is a string-prefix of `v2026.08.10` through `v2026.08.13`, so clicking one version's button could resolve to the wrong entry. Fixed with a `versionButtonName()` helper using a negative-lookahead regex to require an exact patch-number boundary.

## v2026.08.13 — Faseladder: Rail Stats for Mijn dag, Portfolio, and Beheer (August 2026)

Continuing the twelve-phase RIP ladder work begun in `2026.08.4`, the app shell's left rail now shows real numbers per mode instead of only navigable links: Mijn dag gets Taken vandaag / Urgent-te laat / Mijn projecten counts; Portfolio gets stage-grouped phase counts plus Overgangen (Wacht op start) and Gezondheid (groen/geel/rood) breakdowns; and Beheer's phase items gain WIP/geparkeerd count badges and a muted style for undeployed phases. A new pure-function `rail-stats` module computes each mode's rail content from already-fetched mock and live data, matching the pattern every other Infra-board component already uses. Comparing the deployed app against design screenshots also caught Beheer's rail phase list still rendering as one flat list, missing the R2–R6 stage headers Portfolio's rail already had, and Portfolio's rail still carrying a static "Alle projecten" link the design no longer calls for (the top-nav Portfolio tab already routes there directly) — both were corrected. A more serious gap: the new rail stats were rendering for anonymous visitors, showing live-looking project numbers beside a "please log in" main pane; all four rail-stat blocks are now gated behind login, matching the rest of the shell.

## v2026.08.12 — Faseladder: Numbered-List Styling Restored (August 2026)

Tailwind's Preflight base reset strips list-style and margin/padding from every `ol`/`ul` app-wide. The Beheer phase detail page's "Wat er gebeurt bij starten" side panel never got counter-restoring CSS for its numbered steps and definition list, so it silently rendered as plain unnumbered running text instead of the design's numbered list and label/value rows — fixed with the missing restoration CSS.

## v2026.08.11 — Faseladder: Portfolio, Mijn dag, and the Project Stepper Move onto the Real Ladder (August 2026)

Portfolio's Gantt timeline and per-fase Kanban board now iterate the real twelve-phase catalogue, grouped by stage, instead of the old six-phase mock model — backed by a rebuilt mock Gantt and status model spanning all twelve real phases with stage-grouped durations and a deterministic status generator, replacing the old flags-override mechanism. Mijn dag's "Mijn projecten" cards now show each project's real current RIP phase instead of the old mock label, and the project detail page's phase stepper renders all twelve real RIP phases (R2.1–R6.1) instead of six mock ones. With all three surfaces off the real ladder, the superseded six-phase `PHASES` model and the `phaseLabels` prop threading it through Portfolio, Mijn dag, and the stepper were retired entirely.

## v2026.08.10 — Faseladder: Geparkeerde Projecten Page (August 2026)

The R5.3 "Geparkeerde projecten" placeholder in Beheer, part of the twelve-phase RIP ladder work begun in `2026.08.4`, is now built out: a new `getMockGeparkeerdRows` selector lists the projects currently parked at that phase, each with its health status and a link back to the full project.

## v2026.08.9 — Faseladder: Phase Catalogue Grows to Twelve Phases (August 2026)

Matching an updated design handoff, the RIP phase ladder grew from 9 phases across 4 stages to 12 phases across 5 stages (R2.1–R6.1): R5.2 became a real modelled phase (Directievoering en toezicht), and R5.3 is a new unmodelled placeholder (built out the following release). The frontend/backend-shared `RIP_PHASE_KEYS` list grew to match, mock projects now hash directly across all twelve real phases instead of going through the old legacy-bucket lookup table, and the Faseladder/PhaseDetail test suite was updated for the grown catalogue.

## v2026.08.8 — Faseladder: WIP and Gereed Tabs on the Phase Detail Page (August 2026)

The Beheer phase detail page gained WIP and Gereed tabs showing real R2.1 process instances alongside mock rows, backed by a new `getWipStepInfo`/`countReworkLoops` pair deriving a running instance's current step and rework count from its Operaton activity history, and a `usePhase1Completed` hook feeding the Gereed tab's live rows. Both tabs were then routed through the hook layer with proper loading/error/empty states and a retry option, live "Producten" document-progress computation, a complete Gereed summary line, and automatic refetch after starting a new instance; the mock row selection for both tabs was deduplicated into `infra-board.data.ts` against the existing phase-counts logic so the two can't drift apart. Two real bugs were fixed along the way: the WIP tab could flag a running instance as "blocked" after its very first pass through a step with no rework loop at all, now only flagging blocked once an activity has genuinely executed more than once; and the Gereed tab's live-row map used a shorthand fragment that can't carry a `key` prop, switched to an explicit keyed `Fragment`. The now-superseded `RipFase1WipSection`/`RipFase1GereedSection` sections on the caseworker dashboard were retired.

## v2026.08.7 — Faseladder: the Phase Detail Page (August 2026)

A new PhaseDetail page — header, side panel, and a Starten tab for beginning a new process instance — is now wired into the rail, the section router, and the Faseladder overview, so clicking a phase row opens its detail page; the old `RipFase1Section`, including a dead import, dispatch branch, and rail item still referencing it, was retired. New `getReadyProjects`/`getOutOfSequenceProjects` selectors back the Starten tab's eligibility checks, and each phase in the catalogue now names its `kredietBeslisser` where a krediet decision applies. Comparing against the design handoff's screenshots also caught the Gereed/Klaar KPI logic computing backwards — the "gereed" condition checked for projects *before* a phase instead of past it, feeding wrong figures into every downstream Klaar calculation — fixed and cross-checked phase by phase against the reference for an exact match; "Fasen in uitvoering" now shows total WIP across all phases rather than a phase count capped at 9, "Klaar om te starten" totals Klaar across every non-beyond phase, zero-value Klaar cells render "—" consistently, and the WIP column is relabelled "WIP / Geparkeerd" with geparkeerd counts for beyond phases. A separate runtime bug was also fixed: Vite doesn't apply CJS→ESM interop to workspace-linked packages like `@ronl/shared` unless they're in its dependency optimizer, so the first genuine runtime import from it (`RIP_PHASE_KEYS`) failed silently with no build-time error, producing a blank white page — fixed by adding `@ronl/shared` to `optimizeDeps.include`.

## v2026.08.6 — Faseladder: the Overview Page and Live Phase Counts (August 2026)

A new Faseladder overview — the Beheer landing page, one row per RIP phase grouped by stage, with live/mock combined counts and deploy status — is now wired into the rail, section router, and ⌘K command palette. It's backed by a new backend endpoint, `GET /v1/rip/phases/counts`, and a matching `OperatonService.getPhaseInstanceCounts` for live per-phase WIP/Gereed instance counts, plus a new `rip-phase-counts` module holding the "Klaar" (ready-to-start) formula per phase and a `combinePhaseCounts` helper merging mock and live counts while keeping the live subset alongside for annotation. The mock portfolio also grew to 42 projects and gained the RIP-ladder fields the overview needs.

## v2026.08.5 — Faseladder: Deployment Status and the Phase Catalogue (August 2026)

The first structural piece of the twelve-phase RIP ladder: a new `rip-phases.catalog` module holds the phase/stage data plus a `getPhaseDeployStatus` helper (`gedeployed` / `ontwerp` / `onbekend`) used across the Beheer surface, backed by a new backend endpoint, `GET /v1/rip/phases/deployment-status`, and a matching `OperatonService.getDeployedProcessKeys`. A new shared mapping from RIP phase codes to their Operaton process-definition keys is the single source of truth for which phases have a real process behind them, and a `useDeployedProcessKeys` hook exposes it to the frontend.

## v2026.08.4 — Faseladder: Friendlier Deployment Error (August 2026)

Starting a RIP Fase 1 instance against an environment where the process isn't deployed now shows a clear, specific message instead of a raw engine error — the first fix in what grew into the twelve-phase RIP ladder work carried through `2026.08.13`.

## v2026.08.3 — Public Site: Footer Version/URL and a Facet-Group Border Fix (August 2026)

The footer's site line was hardcoded to `publiek.open-regels.nl` (prod) on every environment; it's now driven by a per-environment `VITE_SITE_URL` (dev shows `localhost:5175`, ACC `acc.publiek.open-regels.nl`, prod `publiek.open-regels.nl`), rendered as a link to that origin, and now also shows the current release — the public-site package version, injected via a Vite `define` (`__APP_VERSION__`) — so the footer always matches the latest public-site changelog entry. Separately, the Verfijn filter groups (Soort / Bron / Voor wie) are `<fieldset>`s whose CSS only set a bottom separator and never reset the browser's default fieldset box border, so each rendered inside a grooved border with a notch around its legend; the fieldset defaults are now reset so only the intended separator shows.

## v2026.08.2 — Public Site: Section Pages Seed from Prerendered Data (August 2026)

The Berichten, Nieuws, Producten & Diensten, and Procesbibliotheek section pages now seed their list from the data the prerender already embeds per route, instead of rendering a "Laden…" placeholder and then fetching — content is present on first client render, removing the loading flash that grows in and shifts the footer, the same layout shift the Regelcatalogus fix in `2026.08.1` removed there. The raw→`PublicHit` mapping is extracted from `SectionIndex` into a shared `mapToHits()` so the prerender and the page produce identical items from one source; a cold load with no embedded blob still falls back to fetching through it.

## v2026.08.1 — Public Site: Focus Ring, Prerendered Seeding, CSP and Deploy Fixes (August 2026)

Following the public site's launch in `2026.08.0`, this release closes out several review and deploy findings. The search boxes and the Regelcatalogus dienst-filter dropdown showed a thick yellow focus ring (the Rijkshuisstijl `--ro-focus` token); swapped for the brand blue (`--ro-link`) on form-field `:focus-visible`, keeping the 2px dark outline plus a 4px ring so WCAG 2.4.7 (Focus Visible) is preserved — link and button focus styling is unchanged. The Regelcatalogus page now seeds from the prerender's embedded per-route JSON (`<script>`, `<`-escaped) via a pure reader instead of showing a "Laden…" placeholder and re-fetching, removing the layout shift behind the page's live CLS. Two deploy-blocking bugs were also fixed: the Regelcatalogus org-card logos are `<img>`s served from the RONL knowledge-graph host (`api.open-regels.triply.cc`), but the site's CSP `img-src` was `'self' data:` only, so the browser silently blocked every logo — the host was added, guarded by a test parsing the shipped SWA config's CSP; and `staticwebapp.config.json` lived at the package root but the deploy workflow uploads only `packages/public-site/dist` with `skip_app_build`, so Azure never saw it — no SPA `navigationFallback` (deep-link refresh 404s), no CSP/security headers, no `mimeTypes` overrides — fixed by moving it into `public/` so Vite copies it into `dist`. The Playwright config now also honours an `E2E_BASE_URL` env var to run the suite against an already-deployed URL (used to verify the public site against live ACC) instead of only the local dev server.

## v2026.08.0 — Public Site Launched: an Unauthenticated Regelcatalogus, Search, and Content Site (August 2026)

### A new package with no auth dependencies

`packages/public-site` is a new Vite/React/TypeScript workspace package with a dev server on `:5175` and, deliberately, no `keycloak-js`, no `@azure/msal`, no `@ronl/shared`, and no Tailwind — a new `scripts/check-bundle.mjs` bundle-cleanliness gate scans every built `.js` file for forbidden strings (Keycloak, MSAL, oidc-client, analytics libraries) and fails the build if any are found, wired into `build`/`build:acc`/`build:prod` as their last step, so the "no auth" boundary is enforced mechanically rather than by convention. See [Public Site](../user-guide/public-site.md) for the reader-facing tour.

### Federated search and the Regelcatalogus

A new backend `search.service` aggregates berichten, nieuws, producten, Regelcatalogus services, and LDE process bundles into one cached, server-side searchable index, replacing the design prototype's browser-side search, which doesn't scale past a few hundred items — proxied through a new `lde.service` that filters the process-bundle list to `status active` and `boardOwner` `caseworker`/`untagged` only, so internal boards and non-active drafts stay caseworker-only. A `slugify` utility generates deterministic slugs for rule-catalogue services (which have no natural short id), used identically on both backend (building the index) and frontend (building matching links) so the two can never disagree. The Results page implements federated search with all filter state (`q`/`soort`/`bron`/`doelgroep`/`sort`) living in the URL via `useQueryState`; facet counts come from the server, computed on the query before that facet's own filter is applied, so checking a box never makes its own count disappear. The Regelcatalogus page mirrors the caseworker version with four tabs — Organisations (with logos), Services, Rules (accordion per service, count and list from the same query, with per-rule drill-down into decision-logic descriptions added during review), and Concepts (every row linking out to Skosmos) — and review also fixed the accordion needing two clicks to switch services (the browser's native `<details open>`/`onToggle` toggling fought the React-driven `open` prop; now fully React-controlled via `onClick`+`preventDefault`) and the tab state resetting on every switch (both the open accordion and the Concepts dienst filter are now lifted into the parent component). A generic `SectionIndex` page covers the four content types with no dedicated page of their own (berichten, nieuws, producten, processen — regel has the Regelcatalogus instead).

### Woordenboek, Toegankelijkheid, Open Data, and content pages

Woordenboek is a pure Skosmos iframe embed (with a `title` attribute, a visible "open in new tab" fallback, and `src` following the language switch) — which required a separate infrastructure fix: `skosmos.open-regels.nl` was importing `basic_security_headers`, setting `X-Frame-Options: DENY` and blocking iframe embedding from every origin, including this page and the caseworker app's Gegevenswoordenboek; replaced with a dedicated `skosmos_security_headers` snippet dropping the blanket header in favour of a CSP `frame-ancestors` allow-list scoped to the origins that actually embed it. Detail is the generic per-type detail page for all five content types, with a collapsed-by-default technical-details section showing the exact `GET /v1/public/...` path for that item; Toegankelijkheid is a static accessibility statement (WCAG 2.1 AA target, stated in both languages), and Open Data lists the real `/v1/public/*` GET endpoints. A typed client for `/v1/public/*` backs every page, with dual-runtime base-URL resolution (browser via `import.meta.env`, the Node prerender script via `process.env`) and a 404-vs-throw split between list and per-item lookups; i18n dictionaries (NL/EN, structurally enforced to declare the same keys) and five section definitions cover everything searchable — the data dictionary is deliberately excluded, since it has no search type or detail route of its own.

### Prerendering, deploy, and end-to-end coverage

A post-build step fetches real content through the same `lib/api.ts` the app itself uses and writes a static, crawlable HTML fragment per section/detail route into `dist/`, plus `sitemap.xml` and `robots.txt` (`/zoeken` and `/woordenboek` are excluded from the sitemap by design); a duplicate `<meta description>` bug from an earlier version of this step, where the per-page description was inserted without removing the shell's generic one, was fixed before it ever shipped. `azure-publicsite-acc.yml`/`-prod.yml` mirror the frontend's branch-triggered Azure Static Web App deploy pattern, with `staticwebapp.config.json` carrying no `routes`/`allowedRoles` block at all — matching every "no auth" requirement elsewhere in this release — and `public-site` was added to the root `npm run dev` alongside backend and frontend. The backend's CORS allow-list and `.env.example` template were also found, via the E2E suite's first live run, to be missing the public-site dev port entirely, which would have blocked every fetch from a fresh checkout. A Playwright suite covers the full search → filter → detail → back journey, a deep link with filters pre-applied, a keyboard-only path, and three axe-core accessibility scans (home/results/detail) — 6/6 passing against real backend data during review — alongside a guard test that introspects the real Express router (not a mock) to assert `/v1/public/*` stays GET-only and unauthenticated, so a future change adding a write verb or auth middleware fails immediately rather than shipping unnoticed. Other review-driven fixes folded into this release: organisation logos on the Regelcatalogus Organisaties tab (the data was already fetched and unused), a fix for `sort:'date'` in the search index only partitioning dated-vs-undated items rather than comparing actual date values, an `ACC`-only `PUBLIC_SHOW_WIP_PROCESSES` escape hatch for previewing `wip` process bundles (still gated on `boardOwner`, off by default, must stay off in production), and a `scrollbar-gutter: stable` fix for horizontal layout jitter between routes of different heights.

## v2026.07.0 — CalVer Adopted + Playwright E2E Harness (July 2026)

### Versioning switches from SemVer to CalVer

`bump-release` now computes the next version as `YYYY.MM.patch` from the current date — patch increments on a same-month follow-up release, resets to 0 on the first release of a new month — matching the scheme already adopted by the CPSV Editor and Linked Data Explorer repos. This is a version-string convention only: no git tags and no other change to the release workflow. Historical SemVer entries (`3.9.6` and earlier are the last of that line — actual releases stopped at `3.9.5`) are left as-is; `2026.07.0` is the first release cut under the new scheme.

### Playwright E2E harness, and two deep journeys against a real Operaton

`@playwright/test` is now wired up under `packages/frontend/e2e/`, with a `globalSetup` that checks the frontend, backend, and the sibling Linked Data Explorer backend are all reachable before any test runs — failing fast with the exact start commands rather than a confusing mid-test connection error. A new `operaton` service in `docker-compose.yml` (H2 file-based DB, host port 8081) gives the suite a real, disposable Process Engine to exercise, and `npm run dev`'s `docker:check` step was extended to verify it alongside Postgres and Keycloak.

Two "deep journey" specs run a full roundtrip against that container rather than mocking the engine: a Kapvergunning request submitted via `AwbShellProcess`, DMN-evaluated, claimed and completed as a caseworker task, advancing to and completing a follow-up caseworker task, leaving zero open tasks or instances in Operaton; and a second journey for a Zorgtoeslag claim via `AwbZorgtoeslagProcess`, which also doubles as a tenant-isolation spot-check — confirming a Flevoland caseworker cannot see a task routed to the toeslagen processing authority while a toeslagen caseworker can, a genuine server-side security boundary rather than an assumption. Optional Operaton history cleanup runs from Playwright's `globalTeardown` rather than the test bodies themselves, since worker child processes don't forward the CLI's real TTY stdin needed for the interactive confirmation prompt.

Two real bugs came out of running these specs for real: parallel Playwright workers creating identically-named tasks for the same caseworker could race and steal each other's task mid-flight, causing a genuine Operaton save conflict (fixed by pinning `workers: 1`); and the pending-cleanup tracking file was being deleted unconditionally after its confirmation prompt regardless of the answer given, so a declined entry lost its tracking entirely while its Operaton history was never actually deleted — three real leftover entries had to be purged manually before the fix, after which only confirmed-and-deleted entries are dropped from the file.

### Login/redirect matrix found two real gaps, and fixing them caused a regression

A new login/redirect matrix spec (one test per Flevoland role) and a `ProtectedRoute` spec surfaced two real gaps: a fresh page load of a protected route — URL bar, bookmark, or refresh — always redirected to `/` even with a live Keycloak SSO session, because `keycloak.init()` was only ever called inside `AuthCallback.tsx` and `ProtectedRoute` checked `keycloak.authenticated` synchronously with no initialization of its own; and `/dashboard/caseworker` was not wrapped in `ProtectedRoute` at all, so a citizen navigating there directly just stayed. Both were fixed: `services/keycloak.ts` now exports `initializeKeycloak()`, an idempotent wrapper memoizing the first `keycloak.init()` call, which `ProtectedRoute` awaits on mount; `/dashboard/caseworker` is now wrapped identically to `/dashboard/citizen` (accepted trade-off: `CaseworkerDashboardV2`'s public "zoeken" mode for unauthenticated visitors is no longer reachable, since the route now redirects before the component mounts).

Fixing that pair introduced a real regression, caught by manual testing rather than by the automated suite: the first version of `initializeKeycloak()` memoized whichever options its first caller passed for the life of the page, so visiting `/dashboard/caseworker` while logged out and then choosing "Login met DigiD" got back the already-resolved `false` from `ProtectedRoute`'s earlier check-SSO call instead of triggering a real login — the DigiD redirect never fired. Fixed by always using a fixed check-SSO init and triggering every real login redirect through an explicit `keycloak.login(...)` call, which carries none of `.init()`'s "only once" restriction.

!!! note "Also shipped in v2026.07.0"
    `TakenInbox`'s success message now actually renders after task completion (a same-render state-batching bug meant the confirmation banner was gated behind a branch that had already flipped away by the time it painted). Dossierbeheer's `actionError` banner now also renders in the edit view, not only the overview. `AuditSection`'s load-on-mount effect is now gated behind the admin role check, so a non-admin user no longer triggers an `/admin/audit` fetch that only the render was previously hiding from them. `scripts/check-deps.sh` now compares `package-lock.json` content against an install-time snapshot instead of mtimes, since `git checkout`/`merge --ff-only` bump a tracked file's mtime on disk even when its content is unchanged.

## v3.9.5 — Frontend Test-Coverage Backlog Closed (July 2026)

### P7–P11: the frontend test-coverage campaign started in v3.9.4 reaches 100% file coverage

Building on the service-layer-through-SSE-chat phases from v3.9.4, this release works through the remaining shared component surface: the full `components/CaseworkerDashboard/` section-component library reused across `CaseworkerDashboardV2`, `InfraBoardDashboard`, and `PADashboardV2` (small/medium files, then the larger ones, closing that folder out entirely); the `dossierbeheer` PA-authoring surface (`DossierEditor`, `TemplateGallery`, `ArchiveDialog`, and the `Dossierbeheer` container); `LoginChoice`, `AuthCallback` (including its medewerker-vs-citizen IdP branches and role-to-dashboard fallback logic), and `ChangelogPanel`; and finally the command-palette/dock/section-router shell components shared across all four dashboards. Statement coverage rises from 46.59% to 83.39% across 888 tests, closing the entire phase-1-through-11 backlog: every component and page in the frontend now has at least a test file. Per-phase detail is intentionally not itemized here; see the dedicated frontend testing page.

Two real, documented-not-fixed gaps came out of this work and were fixed in the following release: `AuditSection`'s load-on-mount effect had no role guard of its own (only the rendered UI was gated), and Dossierbeheer's `actionError` banner only rendered in the overview branch, so a failed save while still in the editor set the error state but never showed it. A genuine test-flakiness issue was fixed along the way too — `ChangelogPanel.test.tsx` renders the full real `changelog-data.ts` dataset (60+ entries), which could cross the 5s default Vitest timeout under full-suite CPU contention; fixed with a per-file `testTimeout: 15000` rather than trimming the fixture.

### Release tooling and line-ending hygiene

The `bump-release` skill now fast-forwards `acc` onto the working branch and deletes it by default once the version-bump commit lands, stopping (rather than forcing) on a diverged `acc` and still asking separately before pushing to origin. A `.gitattributes` file now pins tracked text files to LF: on Windows checkouts with `core.autocrlf=true`, git was silently rewriting committed LF files to CRLF on disk on every checkout, bumping mtimes even with unchanged content, which produced false positives in both `check-deps.sh`'s staleness check and the pre-push hook's `prettier --check`.

## v3.9.4 — Frontend Testing Infrastructure Introduced (July 2026)

### RTL, jsdom, and msw wired up; the P1–P6 coverage backlog closed

The frontend previously had two pure-logic test files and no way to render a component at all. This release adds React Testing Library, jsdom, and msw, fixes Vitest's coverage config to report across the whole `src` tree instead of only executed files, and aligns `npm test` with the backend's coverage-by-default convention. A new `docs/TESTING-FRONTEND.md` documents the conventions, layer-by-layer patterns, and a prioritized coverage backlog.

That backlog is then worked through phase by phase: the service layer (`services/*.ts`, including the largest, `pa.api.ts`, with its ~35 exports across mock and live branches); the `useProfielData` hook and `PaDataProvider`'s write-then-selective-refetch pattern; small reusable components (`AltchaWidget`, `DecisionViewer`, `ProcessStartFormViewer`, `PersonalDataPanel`, `TimeLine`); pure logic and config modules across infra-board, caseworker-v2, woo, and login-choice (including a seeded-PRNG-generated 218-row register in `woo.data.ts`); the five dashboard containers, scoped to auth/access gates and the highest-value form flow per container rather than exhaustive coverage; and finally the SSE streaming chat client, mocked by driving the `ReadableStream` reader directly rather than fighting msw's streamed-response API. Overall statement coverage rises from 1.6% to 26.33% across 303 tests, and a follow-up pass (`P1b`) covers the remaining ~40 `businessApi` methods plus every previously-untested PA/Woo/Caseworker-V2/InfraBoard section component, reaching 46.59% across 466 tests.

Two real findings surfaced along the way and were noted for later fixing: `PADashboardV2`'s `switchMode` restores the last section visited per mode rather than always resetting to a default, and `Dashboard.tsx`'s permit submission is a two-step flow where the child form's own success screen fires before the container's tab switch. A genuine bug was fixed directly: `BronnenSection`'s `PersonalFeedLink` rendered a `<div>` inside a `<p>`, which browsers can't nest — they silently close the paragraph early — caught via `validateDOMNesting` warnings while writing its test file.

## v3.9.3 — Notificaties: Team Watches Fixed, Modal Renamed, Explainer Page Added (July 2026)

### Team-scoped Zoekcriteria watches were silently inert

`computeNotifications`' watch query required `user_id IS NOT NULL`, but the taxonomy seed rows behind team-scoped Zoekcriteria have no `user_id` — they're shared, unowned filters. Toggling their WatchBell persisted `notify=true` but could never produce a Meldingen entry, with nothing in the UI indicating the bell was inert. `PATCH /v1/pa/searches/:id` now detects an unowned row and, instead of writing `notify` on the shared row, finds or creates a personal watch derivative (`source_search_id` pointing at the team row) that `computeNotifications` can actually match against; `GET /v1/pa/searches` reflects the caller's own derivative state for the bell instead of the dead shared flag.

### Meldingen becomes Notificaties, with an explainer page

The slide-over notification panel is renamed from "Meldingen" to "Notificaties" throughout, and its Beheer → Monitoring nav item moved from directly under Zoekcriteria to directly under Curatiepijplijn (order is now Signaalbronnen, Zoekcriteria, Curatiepijplijn, Notificaties). A new read-only Notificaties page, sibling to the existing Curatiepijplijn and Afwegingskader spec pages, documents how the WatchBell &amp; Meldingen layer actually works — trigger points, `matchWatch`, the `UNIQUE(user_id, signal_id)` dedup, and the team-search-to-personal-derivative rule above — and is automatically picked up by the ⌘K command palette. It's purely additive documentation with no change to notification runtime behaviour.

## v3.9.2 — Dossier-Editing Security Fixes + Notification Reliability (July 2026)

### Two privilege-escalation holes closed in dossier editing

The dossier edit endpoint checked the publish flag against a user's publish rights, but never validated or gated a status change at all. A pa-author — who can edit but not publish — could archive any live dossier by sending a status change directly, bypassing the admin-only archive route and its required legal-retention metadata, and could unpublish any already-published dossier, since the publish guard only ever fired in one direction. Both are closed by adding a status whitelist and an archive-permission guard, and by making the publish guard compare against the dossier's *current* value so both publishing and unpublishing now require the same publish rights.

### Editing a published dossier no longer requires re-publish rights

A separate, related bug: a plain edit-only save always resent the dossier's current `gepubliceerd` value. For any already-published dossier this tripped the backend's publish guard for a pa-author, surfacing as a misleading connectivity error — and since every seeded dossier ships published, this locked pa-authors out of editing anything at all. `gepubliceerd` is now omitted from the save payload entirely unless the user is actually publishing, since the backend already treats a missing field as "no change."

### Notifications now recompute on watch toggle, and WatchBell is hardened

Toggling a watch's notify flag — a Zoekcriteria bell, or a dossier's watch-everything bell — never itself recomputed notifications; an already-confirmed signal that newly matched sat silently undelivered until some unrelated later event forced a full rescan and dumped the whole backlog at once. A `watch-toggle` trigger point added to `computeNotifications` in both `PATCH /v1/pa/searches/:id` and `POST /v1/pa/dossiers/:id/watch` now surfaces the backlog the moment the watch actually turns on. On the frontend, both WatchBell call sites had been calling the API client directly instead of going through `PaDataProvider`, so the Meldingen badge never refetched after a toggle even though the backend had already recomputed — fixed by routing all three watch mutations through `PaDataProvider`, mirroring the existing `confirmSignal`/`linkSignalDossier` pattern. WatchBell was also missing an in-flight guard, so a rapid double-click could fire two overlapping requests whose local-state flips canceled out visually while the server converged on a different state than what the bell displayed; it now disables itself via a busy flag (or a per-row busy set on the saved-searches list) while a toggle is in flight.

### Other fixes and coverage

The archive route's metadata guard checked for a missing `reason` before validating its type, so a non-string value passed the missing-value check and then crashed the request — and with no async-error middleware in this backend, the crash never reached the client as an error response, it just hung; an explicit type guard now returns the intended 400. Dossier deletion previously ran two independent, unlinked database statements, so a failure between them could delete a dossier but leave its version history behind — and because dossier IDs are deterministic, a later dossier recreated under the same name could silently inherit that orphaned history as its own; both deletes now run inside a single transaction. The live signal feed's source filter had no branch for `eu` at all, so a personal search scoped to EU alone silently returned zero results; the existing EU feed client is now wired into the live endpoint the same way the curation cycle already uses it. Dossierbeheer's narrative fields (waarom nu / waarover / ons verhaal) are stored as Markdown but were rendered as plain text on the Issuekaart, showing literal `##` headers and `**bold**` asterisks; it now uses the same `react-markdown` + `rehype-sanitize` pipeline as the editor's own preview.

Backend test coverage also rose sharply in this release: `pa-dossiers.db.ts` (table creation, seed-to-Markdown conversion, the relative-time formatter used on every dossier card) went from 43.75% to 98.75% statement coverage; `curation.service.ts`'s notification-age-label and document-reference-lookup helpers, previously only reachable incidentally through the full curation pipeline, are now directly asserted against every branch; and `pa-dossiers.routes.ts` gained coverage for previously-untested error and validation branches across most of its mutation routes.

## v3.9.1 — eDOCS AI Assistant MCP Source (July 2026)

### `EdocsMcpProvider` — a fifth AI Assistant source

`EdocsMcpProvider` added as a fifth AI Assistant source (`edocs`, displayed first — left of Process Engine). Unlike every other MCP source, its subprocess calls this backend's own `/v1/edocs/*` HTTP surface — the same routes `scripts/test-edocs-live.sh` already proves working — rather than the OpenText eDOCS DM server directly, so `EdocsService` stays the single place that knows eDOCS' auth and API quirks. It authenticates via a `client_credentials` flow against Keycloak using a new, dedicated `edocs-mcp-client`, kept separate from the existing `copilot-studio-edocs` client (which has its own unrelated, unresolved custom-connector OAuth constraints).

Four tools exposed, scoped strictly to the routes proven live: `workspace_list`, `workspace_documents`, `document_profile`, `document_versions`. No tool was added on the basis of the OpenAPI spec alone — there is deliberately no `document_list` / browse-by-author tool, since browsing documents outside a workspace has no live-tested backend route yet. See [MCP AI Assistant — eDOCS tools](mcp-ai-assistant.md#edocs-tools-edocs) for the full architecture.

Also: `GET /v1/edocs/status` now includes `baseUrl` alongside the existing `library`/`stubMode`/`reachable`/`authenticated` fields.

!!! note "Also shipped in v3.9.1"
    WatchBell &amp; Meldingen — per-user notifications for watched dossiers and searches. A PA-Cockpit feature with no developer-page surface in this section; see the Features changelog for v3.9.1.

## v3.9.0 — Doccle Integration + eDOCS Live-Fixes (July 2026)

`/v1/doccle` routes added, mirroring the eDOCS integration pattern (stub mode, JWT-gated, reachability-only health check). See [Doccle — Live Testing](testing/doccle-live-testing.md).

Five live-verified eDOCS bugs fixed against a real DM server (multipart upload shape, `APP_ID` default, mandatory `UV_AFD_NAAM`, workspace-search parsing, the `getWorkspaceDocuments` endpoint) — full detail already tracked in [eDOCS — Live Testing](testing/edocs-live-testing.md).

## v3.7.3 — Backend Test-Coverage Campaign (July 2026)

A two-phase coverage campaign (~667 → 829 tests) brought every backend feature area under test for the first time, including the standalone MCP servers (`mcp-servers/lde`, `mcp-servers/triplydb`). See [Testing — Backend unit &amp; integration tests](testing/overview.md).

## v3.5.5 — Dev Tooling: Dependency Preflight Check (July 2026)

`npm run dev` now runs a `deps:check` preflight (`scripts/check-deps.sh`) before the Docker check — fails fast with a clear "run `npm install`" message instead of a `MODULE_NOT_FOUND` crash mid-boot when dependencies drift after a `git pull`. It compares `package-lock.json`'s mtime against the `node_modules/.package-lock.json` install marker npm writes after every install; advisory only, it never installs anything on its own. See [Local Development — Start development servers](local-development.md#start-development-servers).

## v3.4.1 — AI Assistant: Model Retirement Fix (June 2026)

Anthropic retired the dated `claude-sonnet-4-20250514` / `claude-opus-4-20250514` snapshots, which started returning a live `404 not_found_error` from the API on their retirement date. `AnthropicLlmProvider`'s model registry now uses non-expiring aliases (`claude-sonnet-4-6`, `claude-opus-4-8`) instead of dated snapshots. Provider errors (retired model, auth, rate limit, overload) are now translated to a clean, code-driven Dutch message instead of surfacing the raw Anthropic API payload. See [LLM Provider Architecture — Registered providers](llm-provider-architecture.md#registered-providers).

## v3.1.0 — Caseworker Dashboard: V1 Retired (June 2026)

Following the V2 shell's introduction (see v3.0.0–v3.0.6 below), `/dashboard/caseworker` now serves V2 exclusively — the V1 three-zone shell and its now-orphaned section components were deleted, and the temporary `/dashboard/caseworker/v2` redirect route was removed in favour of the canonical `/dashboard/caseworker` path.

## v3.0.8 — Security Hardening: Public Write Endpoints (June 2026)

### ALTCHA proof-of-work + upload/rate-limit hardening

Following [work item #33](https://git.open-regels.nl/showcases/iou-architectuur/-/work_items/33) — public routes `/use-case`, `/upload-file`, and `/feedback` accepted requests with no auth, rate limiting, or CAPTCHA — the gaps were closed:

- **ALTCHA proof-of-work** added to `POST /use-case` and `POST /feedback` — visitors must complete a SHA-256 PoW puzzle (`GET /v1/public/altcha/challenge`, max 50,000 iterations, 10-minute expiry, via `altcha-lib`) before a GitLab work item is created. `ALTCHA_HMAC_KEY` configures the HMAC secret; when unset, the check bypasses gracefully so development environments without the key are not blocked. `/upload-file` is intentionally excluded — it's a pre-upload step, not the final submission gate.
- **Upload type whitelist** tightened on `POST /upload-file`: only images, PDF, plain text, Word/ODT, Excel, and XML are accepted, with MIME type and file extension checked independently to block extension spoofing.
- **Rate limit** on public write endpoints reduced from the global 100 req/min to 10 req per 15 minutes per IP, with standardised `RateLimit-*` response headers.
- **Build:** backend `tsconfig.json` upgraded from CommonJS/Node10 to `module: node16` / `moduleResolution: node16` — enables subpath-exports resolution and aligns TypeScript's module semantics with the Node.js runtime. See [TypeScript path aliases](backend-development.md#typescript-path-aliases).

---

*The following gap versions (v3.1.1–v3.1.2, v3.2.0–v3.2.1, v3.3.0–v3.4.0, v3.4.2, v3.5.0–v3.5.4, v3.6.0–v3.6.1, v3.7.0–v3.7.2, v3.8.0–v3.8.3) shipped PA-Cockpit, Woo-dashboard, or Infra-board feature work only, with no developer-perspective architecture change — see the Features changelog for those versions.*

---

## v3.0.7 — Production Cutover (May 2026)

### Production brought to parity with ACC

PROD (previously v2.9.2) brought up to the ACC line. Operationally notable:

- **PROD backend workflow fix.** `.github/workflows/azure-backend-prod.yml` corrected to delete the `@ronl/shared` workspace dependency from the deploy `package.json` before `npm install --production` (`npm pkg delete dependencies.@ronl/shared`) and to copy `shared/dist` into `node_modules/@ronl/shared/` with the correct nesting — matching the ACC workflow. The previous PROD workflow produced a non-functional zip.
- **New PROD App Service settings.** `ANTHROPIC_API_KEY` (required — the backend aborts at startup without it), plus the MCP/TriplyDB/CPRMV/LDE, GitLab, eDOCS, and `REDIS_URL` settings. See [Environment Variables](../reference/environment-variables.md).
- **PROD Keycloak realm sync.** The nine Management Capacity Claim roles and associated clients/mappers imported into the PROD realm.
- **Frontend env.** `.env.production` / `.env.acceptance` are force-tracked in the repo and travel with the merge; `VITE_LDE_API_URL` points at the standalone LDE backend, not the business API.

!!! warning "LDE backend is a separate deployment"
    The Procesbibliotheek section calls the standalone LDE backend (`backend.linkeddata.open-regels.nl`) directly from the browser, not via the business API. That backend has its own ACC/PROD environment split and its own CORS allowlist. Each new frontend origin (e.g. `https://mijn.open-regels.nl`) must be added to the LDE backend's allowlist or the Procesbibliotheek section fails with a CORS error while the rest of the dashboard works. See [Troubleshooting — Procesbibliotheek CORS](troubleshooting.md#procesbibliotheek-cors-error).

## v3.0.0–v3.0.6 — V2 Caseworker Dashboard cutover (April–May 2026)

### V2 caseworker dashboard becomes the default

`/dashboard/caseworker/v2` now serves the V2 shell. The V1 three-zone shell will be retired; `/dashboard/caseworker/v2` will redirect to the canonical route for one release to catch stale bookmarks. New surface:

- 3-mode information architecture (Werk · Zoeken · Beheer) replacing the flat ~25-item left panel — `pages/caseworker-v2/modes.config.ts`
- ⌘K command palette (`CommandPalette.tsx`) — any section in two keystrokes, filtered by the same visibility gate as the rail
- Right-side assistant dock (`AssistantDock.tsx`) — replaces the full-screen chat tab; conversation persisted to `sessionStorage`
- Single `isRailItemVisible(item, ctx)` predicate used by both rail and palette; `requiredRoles` / `requiredOrgTypes` capability on `RailItem`
- Defence-in-depth gate in `SectionRouter` via `findGateFor()` + `<NoAccessPanel>` — gated sections cannot leak via deep-link or palette
- `SectionErrorBoundary` — a render error in one section no longer takes down the shell

See [Caseworker Dashboard (V2)](../features/archive/caseworker-dashboard-v2.md).

### DvTP consent flow (v3.0.1)

`DvtpStartSection` / `DvtpTakenSection` added under Werk → DVTP, gated to `municipality` org types. Starts the `DvtpToestemmingGevenProcess` BPMN via `ProcessStartFormViewer`. `dvtp` feature flag added to `tenants.json`.

### Management Capacity Claim (v3.0.2)

`ManagementCapacityClaimProcess` BPMN + `/v1/hr-capacity/*` routes (`capacity.routes.ts`). `CapacityClaimSection` (manager-gated), `CapacityClaimArchiefSection`, inline `CapacityClaimDocumentsViewer`. Nine new realm roles. Role-based `candidateGroups` task queue filtering.

### Nieuws RSS feed migration → revert

`nieuws.service.ts` was migrated to the Rijksoverheid `/api/rss?query=` JSON API and then reverted to the legacy `feeds.rijksoverheid.nl/nieuws.rss` subdomain due to upstream technical issues. Cold-cache failure handling hardened: a 200 with zero parsed items is now treated as a failure rather than caching an empty list.

---

## v2.9.7 — Feature Release (April 3, 2026)

### AI Assistant — CPRMV Legislation Provider

`CprmvMcpProvider` added to the MCP registry. Connects to the CPRMV HTTP MCP server at `acc.cprmv.open-regels.nl/mcp` using `StreamableHTTPClientTransport` — a remote HTTP endpoint, not a subprocess. Enabled via `CPRMV_MCP_ENABLED=true`; URL overridable via `CPRMV_URL`.

Three tools exposed: `rules_rules__rule_id_path__get` (retrieve rules from BWB, CVDR, or EU CELLAR by rule ID path), `ref_ref__referencemethod___reference__get` (resolve rules by Juriconnect reference), `celex_cellar_by_celex__celexid___language___format__get` (look up EU CELLAR publications by CELEX id).

`config.cprmv` added to `Config`: `enabled` (`CPRMV_MCP_ENABLED`, default `false`), `url` (`CPRMV_URL`).

### AI Assistant — LDE Process Library Provider

`LdeMcpProvider` added. Spawns a custom `lde-mcp` stdio subprocess (`src/mcp-servers/lde/index.ts` in dev, `dist/mcp-servers/lde/index.js` in prod) that connects directly to the LDE `lde_assets` PostgreSQL database. Enabled via `LDE_MCP_ENABLED=true` and `LDE_DATABASE_URL`.

Six tools: `bundle_list`, `bundle_get` (deployed BPMN bundles with forms, documents, subprocesses, and DMN keys), `form_list`, `form_get` (full Camunda Form JSON schema), `document_list`, `document_get` (zones and bindings).

SSL handled by stripping `sslmode` from the connection URL and passing `ssl: { rejectUnauthorized: true }` to the pg `Pool` constructor directly — avoids the pg-connection-string `sslmode=require` deprecation warning.

`config.lde` added to `Config`: `enabled` (`LDE_MCP_ENABLED`, default `false`), `databaseUrl` (`LDE_DATABASE_URL`).

### AI Assistant — LLM Provider Architecture

`LlmProvider` interface introduced in `src/services/llm/LlmProvider.ts`. Decouples the agentic loop from any specific SDK — `mcpChat.service.ts` has no direct dependency on Anthropic or OpenAI. Provider-agnostic types: `AgentMessage`, `AgentToolUse`, `AgentToolResult`, `LlmStreamParams`, `LlmTurnResult`.

`LlmRegistry` singleton maps model IDs to their owning provider. `getAvailableModels()` returns only models from providers where `isAvailable()` is `true`.

`AnthropicLlmProvider` registered with three models: `claude-sonnet-4-20250514`, `claude-opus-4-20250514`, `claude-haiku-4-5-20251001`. Enabled when `ANTHROPIC_API_KEY` is set.

`OpenAILlmProvider` registered with `gpt-4o` and `gpt-4o-mini`. Enabled when `OPENAI_API_KEY` is set.

`GET /v1/mcp/models` added — returns all available models with `providerId` and `providerDisplayName`. Used by the frontend model selector dropdown.

`POST /v1/mcp/chat` body extended with `modelId: string` — required field; returns `400 INVALID_REQUEST` when absent.

Frontend: model selector dropdown rendered below the subtitle in the AI Assistant header. Hidden when only one model is available. First available model pre-selected on mount.

### Caseworker Dashboard — Procesbibliotheek

New `procesbibliotheek` section added to the Home tab for all tenants whose `leftPanelSections.home` includes the entry (currently Utrecht, Amsterdam, Rotterdam, Den Haag, Flevoland). Publicly accessible (`isPublic: true`).

Fetches deployed BPMN bundles from the LDE public API (`VITE_LDE_API_URL/bundles/public`). A dedicated `ldeApi` Axios instance is used — no Keycloak `Authorization` header is sent. Cards show process name, `bpmnProcessId`, status badge (WIP/Actief/Concept), role badge (Standalone/Subprocess), and deployment date; expand to reveal forms, documents, DMN keys, and deployment ID.

`ProcessBundle`, `BundleDeployedForm`, `BundleDeployedDocument` types exported from `api.ts`. `VITE_LDE_API_URL` added to all env files and `vite-env.d.ts`.

---

## v2.9.6 — Enhancement (April 2, 2026)

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

## v2.9.5 — Feature Release (April 1, 2026)

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

## v2.9.4 — Feature Release (March 30, 2026)

### AI Assistant — Multi-Source MCP Registry

`McpClientService` singleton replaced by `McpRegistry` — a provider registry that manages multiple independent MCP sources. Each provider connects, exposes a curated set of tools, and contributes a section to the composite system prompt independently. A provider failure does not block other providers.

`McpProvider` interface introduced: `id`, `displayName`, `description`, `connect()`, `disconnect()`, `getToolDefinitions()`, `callTool()`, `isConnected()`, `systemPromptContribution()`.

`OperatonMcpProvider` replaces `McpClientService` — identical stdio subprocess behaviour, 15-tool `ALLOWED_TOOLS` curation gate preserved.

`TriplyDbMcpProvider` added — spawns the bundled `triplydb-mcp` stdio server; connects to the RONL SPARQL endpoint (`stevengort/RONL`). Exposes 11 tools: `dmn_list`, `dmn_get`, `dmn_chain_links`, `dmn_enhanced_chain_links`, `dmn_semantic_equivalences`, `organization_list`, `service_list`, `rule_list`, `concept_list`, `service_rules_metadata`, `sparql_query`. Enabled via `TRIPLYDB_MCP_ENABLED=true`.

`McpRegistry.getToolDefinitions(providerIds?)` and `callTool()` accept an optional provider ID filter. `buildSystemPrompt(providerIds?)` assembles a composite prompt from only the selected connected providers. `getProviderMeta()` returns metadata and connection status for all registered providers.

`POST /v1/mcp/chat` extended with `sources: string[]` — provider IDs selected by the user for the session. `GET /v1/mcp/sources` added — returns provider metadata and connection status.

Frontend: source selector toggle buttons rendered below the message history. All connected sources pre-selected by default; offline providers shown greyed-out. Send button and textarea disabled when no sources are selected. Header subtitle shows active source display names dynamically.

Markdown rendering added to assistant bubbles via `react-markdown` + `@tailwindcss/typography` prose classes. In-progress streaming bubble also renders Markdown incrementally.

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
| AI Assistant — Multi-Source MCP Registry (McpRegistry)   | v2.9.4  |
| TriplyDbMcpProvider + Knowledge Graph tools              | v2.9.4  |
| Source selector UI + Markdown rendering in chat bubbles  | v2.9.4  |
| IOU tab — GitLab integration (Flevoland)                 | v2.9.5  |
| `GET /v1/public/use-cases`, `POST /v1/public/feedback`   | v2.9.5  |
| IOU form UX — step badges, add/remove, file attachments  | v2.9.6  |
| `POST /v1/public/upload-file`                            | v2.9.6  |
| CPRMV Legislation Provider                               | v2.9.7  |
| LDE Process Library Provider                             | v2.9.7  |
| LLM Provider Architecture (LlmRegistry, OpenAI support)  | v2.9.7  |
| Procesbibliotheek section                                | v2.9.7  |
| V2 caseworker dashboard (3-mode shell, ⌘K, dock)         | v3.0.0  |
| Section gating (`requiredRoles`/`requiredOrgTypes`)      | v3.0.0  |
| `SectionErrorBoundary` per-section crash isolation       | v3.0.0  |
| DvTP consent flow (`DvtpToestemmingGevenProcess`)        | v3.0.1  |
| `dvtp` tenant feature flag                               | v3.0.1  |
| Management Capacity Claim process + 9 realm roles        | v3.0.2  |
| `/v1/hr-capacity/*` route group                          | v3.0.2  |
| Nieuws RSS feed migration → revert                       | v3.0.x  |
| V1 dashboard retired; V2 is the default route            | v3.0.x  |
| PROD brought to ACC parity (cutover)                     | v3.0.7  |

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
