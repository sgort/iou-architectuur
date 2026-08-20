---
component: RONL Business API
---

# Testing

RONL Business API is an npm-workspaces monorepo with three tested packages:
the Express/TypeScript backend on **Jest**, the caseworker portal
(`packages/frontend`) on **Vitest** + React Testing Library, and the public
search site (`packages/public-site`) on **Vitest** + jsdom. All three run
with coverage by default. Each also has a Playwright **E2E** suite; the
frontend and public-site E2E suites are measured below, run by the
maintainer against a live dev stack — see
[E2E and live smoke suites](#e2e-and-live-smoke-suites).

!!! info "Figures on this page are measured, not estimated"
    Every count, command and coverage percentage below — including the
    frontend Playwright E2E suite — was produced by running the suites against
    **v2026.08.20** on **20 August 2026**. The frontend E2E suite was run by
    the maintainer, who owns the dev stack and local Operaton container it
    needs; its figures come from that run's Playwright HTML report, which
    embeds the same result data (the report itself is not committed to this
    repo). Rerun the commands in [Running the tests](#running-the-tests) to
    reproduce the unit figures. Two things on this page were **not** re-run
    for this release: the public-site E2E suite, whose figures still date
    from v2026.08.19, and the four live-smoke shell scripts, which remain
    described from source only — see
    [E2E and live smoke suites](#e2e-and-live-smoke-suites).

**At a glance:**

| Package | Runner | Files | Tests | Result | Wall time | Statements | Branches | Functions | Lines |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|
| `packages/backend` | Jest + ts-jest | 71 | 1145 | all passing | ~23s | 94.28% | 73.54% | 94.13% | 95.69% |
| `packages/frontend` | Vitest + RTL | 130 | 1064 | all passing | ~61s¹ | 85.04% | 76.51% | 80.16% | 86.40% |
| `packages/public-site` | Vitest + jsdom | 28 | 134 | all passing | ~12s | 86.82% | 70.39% | 87.63% | 88.76% |

¹ Wall time varies with machine load, so treat it as an order of magnitude
rather than a figure to match. The ~61s above is from a full `npm test` root run
on 20 August 2026; the same suite measured 88.28s earlier the same day on a
contended machine. That contention used to make two tests **fail**, not merely
run slow; both were fixed on 20 August rather than left as known flakes, and the
wall-clock budget that was one of them now runs separately as
`npm run test:perf` (1 test, making 1065 in total). See
[The performance budget](#the-performance-budget).

---

## Running the tests

Run from the repository root after `npm install` (`node_modules` must
already be installed in every workspace).

| Command | Scope | Files | Tests |
|---|---|---:|---:|
| `npm test` | Every workspace with a `test` script (see below) | 229 | 2343 |
| `npm test --workspace=@ronl/backend` | Backend only (Jest, coverage on by default) | 71 | 1145 |
| `npm test --workspace=@ronl/frontend` | Frontend only (Vitest, coverage on by default) | 130 | 1064 |
| `npm run test:perf --workspace=@ronl/frontend` | The wall-clock budget, run without file parallelism | 1 | 1 |
| `npm test --workspace=@ronl/public-site` | Public site only (Vitest, coverage on by default) | 28 | 134 |

```bash
# Everything
npm test

# One workspace
npm test --workspace=@ronl/backend
npm test --workspace=@ronl/frontend
npm test --workspace=@ronl/public-site

# Watch mode
npm run test:watch --workspace=@ronl/backend
npm run test:watch --workspace=@ronl/frontend
npm run test:watch --workspace=@ronl/public-site

# Single file / pattern
npx jest --config packages/backend/jest.config.js --no-coverage --testPathPattern=rules
npx vitest run --config packages/frontend/vite.config.ts session
npx vitest run --config packages/public-site/vite.config.ts SectionIndex
```

**What `npm test` at the root actually runs.** The root script is
`npm run test --workspaces --if-present`, fanning out over every package
under `packages/*`. Three of the four have a `test` script — `@ronl/backend`,
`@ronl/frontend`, `@ronl/public-site` — and `--if-present` silently skips the
fourth, `@ronl/shared`, which has no `test` script at all (only `build`,
`prepare`, `clean`, `type-check`). That's expected, not a gap: `shared` is a
types-only package with nothing to unit test.

### The performance budget

`simEngine.ts` carries a real budget: `run(cfg)` must process the default
3,150-application population in under **250ms**. Its source comment is
emphatic that if the assertion ever fails, the threshold must not be
loosened — the intended remedy is a web worker, not a bigger number.

The problem was never the threshold. It was that a single `performance.now()`
call measures the machine as much as it measures the engine. On a machine
contended by another process starting, the assertion was observed degrading to
**302ms, then 837ms, then 1297ms** across three consecutive runs; inside a full
`npm test`, where Vitest saturates every core with 130 parallel test files, even
the fastest of three CPU-time samples came out at **468ms**. Against ~100ms in
isolation. Wiring the CI test gate would have made that a permanently red
pipeline.

So on 20 August 2026 the budget moved rather than moved up:

- The assertion lives in `simEngine.perf.test.ts`, still asserting `< 250ms`,
  now with a warm-up run and the fastest of three samples so a JIT pause or a
  stray GC cannot decide it.
- `vite.config.ts` excludes `src/**/*.perf.test.ts` from the default run.
- `vitest.perf.config.ts` mirrors it — same plugins, aliases and setup, but the
  perf specs are the only thing *included*, and `fileParallelism` is off. It
  spreads and overrides the base test block rather than using `mergeConfig`,
  which concatenates arrays and would have kept the base `exclude`, hiding the
  perf specs from their own run.
- `npm run test:perf` runs it, and both frontend workflows run that as their own
  blocking CI step.

`ChangelogPanel.test.tsx` was the other casualty of the same contention: its
15-second timeout was enough in isolation but not inside a full run, where it was
observed taking 22s. `changelog-data.ts` renders 60+ real version entries, so the
test is genuinely slow rather than unreliable — and a timeout exists to catch a
hang, not to assert a speed, so it was raised to 60s. That costs no coverage;
`simEngine.perf.test.ts` remains the one place a real budget is asserted.

!!! note "Coverage report on failure"
    Vitest's default is to skip writing a coverage report when any test fails,
    so a red run loses its coverage figures exactly when you want them. Both the
    frontend and public-site configs now set `coverage.reportOnFailure: true`,
    rather than relying on anyone remembering the CLI flag.

---

## Linting, formatting, git hooks, and CI

| Command | What it does | Result (measured) |
|---|---|---|
| `npm run lint` | `npm run lint --workspaces --if-present` — `eslint .` in backend, frontend, public-site | exit 0, no errors |
| `npm run check-format` | `prettier --check "**/*.{ts,tsx,json,md}" --ignore-path .gitignore` — **one repo-wide glob, not a per-workspace fan-out** | exit 0, no violations |

`npm run lint` skips `@ronl/shared` the same way `test` does — no `lint`
script there. `npm run check-format`, by contrast, is **not** scoped by
workspace scripts at all: it's a single Prettier invocation over the whole
tree (minus `.gitignore`d paths — `node_modules/`, `dist/`, `coverage/`,
etc.), so it reaches `packages/shared` too even though `shared` defines no
format-check script of its own — confirmed directly:
`npx prettier --check "packages/shared/**/*.{ts,tsx,json,md}" --ignore-path
.gitignore` passes. This is the same class of check a sibling component in
this documentation set got wrong (a root `check-format --workspaces
--if-present` silently skipped a package that named its script
differently) — this repo's root script avoids that failure mode by not
fanning out over workspace scripts in the first place.

### Git hooks

| Hook | Runs | Scope |
|---|---|---|
| `pre-commit` | `npx lint-staged` | Staged files only, per the `lint-staged` config below |
| `pre-push` | build `@ronl/shared` → `npm run type-check` → `npm run lint` → `npm run check-format` | All workspaces (type-check, lint) / whole tree (check-format) |

`lint-staged` (in the root `package.json`):

```json
{
  "packages/frontend/**/*.{ts,tsx}": ["npm run lint:fix --workspace=@ronl/frontend", "prettier --write"],
  "packages/public-site/**/*.{ts,tsx}": ["npm run lint:fix --workspace=@ronl/public-site", "prettier --write"],
  "packages/backend/**/*.ts": ["npm run lint:fix --workspace=@ronl/backend", "prettier --write"],
  "packages/shared/**/*.ts": ["prettier --write"],
  "*.{json,md}": ["prettier --write"]
}
```

!!! note "`public-site` had no `lint-staged` entry until 20 August 2026"
    A staged public-site source file got no ESLint pass and no Prettier pass at
    commit time — only the generic `*.{json,md}` rule applied, and that doesn't
    match `.ts`/`.tsx`. It was never uncaught for long, since `pre-push`'s
    `npm run lint` and `npm run check-format` both cover public-site in full and
    neither is scoped by the `lint-staged` glob, but a local commit alone could
    carry an unformatted or unlinted public-site change. The glob above closes
    it; the package already passed both checks, so there was no fallout.

!!! important "The hooks do not run the tests"
    Neither `pre-commit` nor `pre-push` invokes any `test` script, so nothing
    client-side stops a push that breaks the backend, frontend, or public-site
    suite — run `npm test` yourself before pushing anything nontrivial. Since
    20 August 2026 every deploy pipeline does run them, so a broken push no
    longer reaches acceptance; the client-side gap is now a matter of feedback
    speed rather than of what ships.

### CI

Six Azure workflows under `.github/workflows/`, one acc/prod pair per
package:

| Workflow | Lint | Type-check | **Tests** | Perf budget | Build | Deploy |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `azure-backend-acc.yml` / `-prod.yml` | ✅ | – | **✅** | – | ✅ | ✅ |
| `azure-frontend-acc.yml` / `-prod.yml` | ✅ | – | **✅** | **✅** | ✅ | ✅ |
| `azure-publicsite-acc.yml` / `-prod.yml` | ✅ | ✅ | **✅** | – | ✅ | ✅ |

**Every package now has a real CI test gate**, as of 20 August 2026 — a failing
test blocks the deploy in all six workflows. Public-site had one already: both
`azure-publicsite-*.yml` workflows run `npm run lint`, `npm run type-check`, then
`npm test` before building. Backend CI lints and builds, and now runs Jest
alongside the existing lint step. Frontend CI previously ran neither lint nor
test — straight from `npm ci` to `vite build` to deploy — and now runs
`npm run lint`, `npm test`, and `npm run test:perf` before the build. A
post-deployment health check (backend only: 5 retries, 10s apart, against
`/v1/health`) confirms the deployed instance responds before a backend
deployment is marked successful.

The gap was deliberate while it lasted: gating on coverage that was still
climbing was judged theatre, the same call the
[Linked Data Explorer](../../../linked-data-explorer/developer/testing.md#ci-the-test-gate)
made and has since reversed for the same reason. All three RONL packages have
been through their coverage campaigns; there is nothing left for the deferral to
wait on.

---

## Test inventory

All three packages colocate test files with the source they cover
(`foo.ts(x)` → `foo.test.ts(x)`) and pick them up automatically — no separate
`tests/` directory in any package.

### Backend (Jest) — 71 files, 1145 tests

| Area | Files | Tests | Covers |
|---|---:|---:|---|
| `src/services` | 21 | 325 | Every service — `operaton`, `edocs`, `doccle`, `audit`, `berichten`, `nieuws`, `search`, `regelcatalogus`, `productenDiensten`, `mcpChat`, `externalTaskWorker`, `lde`, the `llm/` providers (Anthropic, OpenAI) and `mcp/` provider wrappers (Cprmv, Lde, Operaton, TriplyDb) |
| `src/pa-monitoring` | 16 | 368 | Public Affairs monitoring — `pa.routes` (88 tests, the full route surface), `pa-dossiers.routes`/`.db` (dossier authoring), `curation.service`, `rules` (pure scoring), the TK/OB/EU/agenda/media source clients, `pa-cache`, `query-match`, `rss`, `notifications.service` |
| `src/routes` | 15 | 253 | Every route module mounted with the service layer and auth mocked, supertest driving requests — `edocs` (27), `m2m` (33), `process` (34), `task` (22), `public.routes` + `public.routes.security` (59 combined), `doccle`, `rip`, `mcp`, `health`, `hr`, `capacity`, `decision`, `brp`, `admin` |
| `src/mcp-servers` | 3 | 46 | The standalone stdio MCP servers (`lde`, `triplydb`, `edocs`) — each mocks the MCP SDK to capture and drive its `ListTools`/`CallTool` handlers directly |
| `src/media-aggregator` | 8 | 95 | `net-guard` (35 tests — the SSRF guard: IPv4/IPv6 rules, every DNS path), `ingest`, `search`, `store`, `sanitize`, `stable-id`, plus the aggregator's own route module |
| `src/middleware` | 2 | 24 | `jwt`/`tenant`/`audit` gates sit in `auth/` and `middleware/` — `tenant.middleware` and `audit.middleware` here |
| `src/auth` | 1 | 13 | `jwt.middleware` — token validation, role/assurance gates |
| `src/utils` | 5 | 21 | `env` (parsers extracted from `config.ts` so they're testable without triggering its import-time `dotenv` side effect), `errors`, `altcha`, `slug`, `logger` |

This is real growth since the last narrative count of "829 tests" — 1145
tests now, +316, from areas added or expanded after that count: the eDOCS
and Doccle live-switch paths, the standalone `mcp-servers/edocs` server, the
PA dossier-authoring routes/db, `search.service`, `slug`, `notifications.service`,
`query-match`, and `rss`.

### Frontend (Vitest + RTL) — 130 files, 1064 tests

| Area | Files | Tests | Covers |
|---|---:|---:|---|
| `src/components` | 90 | 597 | Every dashboard's shared section-component library (`CaseworkerDashboard/`, reused across three of the four V2 dashboards), each dashboard's own components (`CaseworkerDashboardV2`, `PADashboardV2`, `WooDashboard`, `InfraBoardDashboard`), the `*SectionRouter*`/`*Dock*`/`*CommandPalette*`/`*NoAccessPanel*` shells, and reusable widgets (`DecisionViewer`, `AltchaWidget`, `SessionExpiryWarning`, `PersonalDataPanel`, `ProcessStartFormViewer`, `TimeLine`) |
| `src/pages` | 28 | 278 | Top-level pages/containers — `Dashboard`, `LoginChoice`, `AuthCallback`, `ChangelogPanel` — plus pure data/config modules (`infra-board/*.data.ts`, `woo/woo.data.ts`, `caseworker-v2/modes.config.ts`, `public-affairs-v2/kompas.ts`) |
| `src/services` | 10 | 180 | `api.ts` (46 tests — the typed client, `chatStream`'s SSE parsing counted separately at 11), `pa.api` (45), `infra.api`, `dossierbeheer.api`, `brp.api`/`brp.timeline`, `keycloak`, `tenant`, `bsn.mapping` |
| `src/hooks` | 1 | 4 | `useProfielData` — the manual loading/error/data hook pattern |
| `src/App.test.tsx` | 1 | 5 | `ProtectedRoute`'s SSO-check-on-mount behavior, exported and tested in isolation |

Mocking style throughout: `msw` at the network boundary for API/service
modules (not `axios` stubbing directly, so the auth-interceptor chain is
exercised too); `vi.mock` for module-level singletons (`keycloak.ts`) and for
heavyweight libraries (`@bpmn-io/form-js`, mocked as a plain-function
constructor); container/router tests mock every child one level below rather
than re-running already-tested children; pure data/logic modules run
unmocked. Environment defaults to `node`, opting into `jsdom` per file with
a `// @vitest-environment jsdom` first line only where a component or
DOM-touching hook needs it.

### Public site (Vitest + jsdom) — 28 files, 134 tests

| Area | Files | Tests | Covers |
|---|---:|---:|---|
| `src/pages` | 14 | 71 | Includes a full `herkomst/` provenance-explorer sub-area (`HerkomstExplorer`, `HerkomstTrace`, `HerkomstChip`, `HerkomstBackground`, `herkomstConcepts`, `herkomstData`, `herkomstTrail` — 7 files, 39 tests) plus the generic `SectionIndex`/`Regelcatalogus`/`Results`/`Detail`/`Woordenboek`/static pages |
| `src/lib` | 6 | 26 | `slug` (kept identical to the backend's slugifier by design), `useQueryState` (URL-backed filters), `search` (`highlight()`), `api` (the typed `/v1/public/*` client), `sectionHits` (`mapToHits()`), `prerenderedData` (the seeded-render reader) |
| `scripts/` | 2 | 15 | `prerender.test.ts` (11 — `escapeHtml`, `buildSitemap`, `injectIntoShell`), `check-bundle.test.ts` (4 — the build-time gate that fails if any auth/telemetry string ships in the bundle) |
| `src/components` | 3 | 13 | Presentational chrome, `Footer`, `TechDetails` |
| `src/App.test.tsx` | 1 | 5 | Routing shell — every route registered, `<html lang>` synced to the language switch |
| `src/i18n` | 1 | 3 | NL/EN dictionary key parity |
| `src/staticwebapp-csp.test.ts` | 1 | 1 | Guards the shipped CSP header — a regression here silently breaks the org-logo host |

This is substantially more than the "79 tests across 18 files" figure from
this package's own earlier narrative doc — the `herkomst/` area alone (7
files, 39 tests) didn't exist at that count, along with `Footer.test.tsx`
and `TechDetails.test.tsx`.

For eDOCS-specific live results, see
[eDOCS — Live Testing](edocs-live-testing.md); for Doccle,
[Doccle — Live Testing](doccle-live-testing.md).

---

## Coverage

Measured with `npm test --workspace=<pkg>` per package against v2026.08.20
on 20 August 2026.

| Package | Statements | Branches | Functions | Lines |
|---|---:|---:|---:|---:|
| Backend | 94.28% | 73.54% | 94.13% | 95.69% |
| Frontend | 85.04% | 76.51% | 80.16% | 86.40% |
| Public site | 86.82% | 70.39% | 87.63% | 88.76% |

The backend figures are unchanged from v2026.08.19 — no file it counts was
touched. The frontend moved slightly because `src/**/*.perf.test.ts` is now
excluded from the default run, taking the coverage that spec contributed to
`simEngine.ts` with it. The public-site figures are a **correction**: no file
under `packages/public-site/src/` has changed since v2026.08.19, yet the
previously published numbers do not come out of the command. Re-measured three
times, including once against the pre-release `vite.config.ts` to rule out this
release's own change, the result was identical every time.

All three configure `collectCoverageFrom`/`coverage.include` to span the
whole `src` tree rather than only the files a test happens to import, so an
untested file shows as 0% instead of silently disappearing from the report —
each package's own testing doc, before this page, called out that this
wasn't always true and had to be fixed.

**What the headline numbers mean here.** Unlike a package where the
statement total is dominated by a large untested UI layer, all three RONL
packages have been through a dedicated coverage campaign that closed
*breadth* gaps deliberately — every backend feature area, every frontend
component/page, and every public-site module now has at least a test file.
The consistent pattern across all three is **branches trail statements by
15–20 points** (backend 94→74, frontend 85→77, public-site 86→70) — the
remaining gap is *depth*, not missing files: defensive `if (!req.user)`
guards behind real middleware, `?? null` fallbacks, catch blocks unreachable
through a legal input, and a handful of deliberately-scoped "critical
interactions only" passes on the largest components (documented per-file, not
silently absent).

### Backend by area

These are the rows Jest prints, verbatim, so each one can be matched against
the output of `npm test --workspace=@ronl/backend -- --coverageReporters=text`.
Sub-directories report separately rather than rolling up into their parent, and
istanbul truncates to two decimals rather than rounding.

| Area | Statements | Branches | Functions | Lines |
|---|---:|---:|---:|---:|
| `middleware` | 100 | 95.83 | 92.3 | 100 |
| `mcp-servers/edocs` | 100 | 78.12 | 100 | 100 |
| `mcp-servers/triplydb` | 100 | 90.9 | 100 | 100 |
| `services/llm` | 99.02 | 92.3 | 100 | 98.95 |
| `pa-monitoring/sources` | 96.64 | 75.1 | 91.04 | 98.4 |
| `mcp-servers/lde` | 96.07 | 82.14 | 100 | 97.95 |
| `services/mcp` | 96 | 71.62 | 93.9 | 97.84 |
| `media-aggregator` | 95.75 | 85.63 | 98.21 | 96.87 |
| `services` | 95.68 | 77.56 | 96.27 | 96.78 |
| `pa-monitoring` | 94.52 | 76.32 | 92.66 | 97 |
| `routes` | 93.43 | 68.62 | 93.04 | 95.05 |
| `auth` | 88.88 | 85.71 | 84.61 | 88.05 |
| `utils` | 43.47 | 6.54 | 73.33 | 40.47 |

`utils/` is the one deliberately-low area, and it's a known, documented
artifact, not a gap: `utils/config.ts` sits at 0% because it self-runs
`dotenv` + `validateConfig` on import (its pure parsers were extracted to
`utils/env.ts`, which is at 100%), and `utils/logger.ts` is fully mocked in
every test that touches it, so its real transport-wiring lines never
execute under test.

### Frontend by area

| Area | Statements | Branches | Functions | Lines |
|---|---:|---:|---:|---:|
| `src/hooks` | 100.00% | 75.00% | 100.00% | 100.00% |
| `src/services` | 93.01% | 79.35% | 96.29% | 93.56% |
| `src/components` | 86.45% | 70.11% | 94.73% | 90.62% |
| `src/pages` | 72.40% | 69.87% | 61.56% | 73.43% |
| `src/utils` | 66.66% | 50.00% | 100.00% | 100.00% |

`src/pages` is the lowest of the five because it's where the largest,
most-recently-added containers live (dashboard shells, `ChangelogPanel`'s
60+ real version entries) — the same "critical interactions only" scoping
used throughout the frontend's own P5/P8/P9 coverage phases, not an
oversight.

### Public site by area

| Area | Statements | Branches | Functions | Lines |
|---|---:|---:|---:|---:|
| `src/components` | 96.77% | 100.00% | 96.15% | 96.66% |
| `src/lib` | 84.90% | 73.17% | 88.88% | 86.20% |
| `src/pages` | 82 | 61.51 | 79.06 | 84.26 |

---

## E2E and live smoke suites

The frontend and public-site Playwright suites below were **measured** on
19 August 2026 against v2026.08.19 — run by the maintainer, who owns the
dev stack and local Operaton container both suites need. Figures come from
their Playwright JSON reporter output; the reports themselves are
deliberately not committed to this repo, only the figures below. The four
live-smoke shell scripts at the end of this section were **not run** and
remain described from their configuration and specs only.

### Frontend Playwright suite

`packages/frontend/e2e/`, its own `playwright.config.ts`
(`npm run test:e2e --workspace=@ronl/frontend`). Chromium only,
`workers: 1` (two specs race to claim an identically-named task for the
same caseworker against the shared local Operaton engine, so the suite
trades parallelism for correctness).

**Measured 20 August 2026 against v2026.08.20: 12 tests, 12 passed, 0
failed, 0 flaky, 0 skipped, 54.1s.** Run against the corrected `e2e-fixtures`
BPMNs redeployed from the Linked Data Explorer, confirming that chain end to
end.

| Spec | Covers |
|---|---|
| `smoke.spec.ts` | App loads at `/`, `LoginChoice` renders, no console errors |
| `login-redirect.spec.ts` | One test per role (citizen/caseworker/infra/woo/PA) against the Flevoland tenant, driving the real Keycloak hosted login — 5 tests |
| `protected-route.spec.ts` | Cross-role `ProtectedRoute` redirect behavior — 2 tests |
| `caseworker-journey.spec.ts` | Citizen submits a real Kapvergunning request via Operaton/DMN; caseworker claims and completes both resulting tasks; a genuinely finalized roundtrip |
| `zorgtoeslag-journey.spec.ts` | Second deep journey — a commercial-org citizen submits a Zorgtoeslag claim, the `toeslagen` caseworker completes both steps |
| `tenant-isolation.spec.ts` | A real cross-tenant fixture — confirms a wrong-tenant caseworker does **not** see a task, and the right one does |

`tenant-isolation.spec.ts` is the empirical proof of the tenancy-scoping
behaviour described in
[Processes → Tenancy](../../features/processes.md#tenancy) and
[Tasks → Visibility](../../features/tasks.md#visibility): a task raised
under one tenant is visible only to that tenant's caseworker.

Requires: `docker compose up -d` (Keycloak + Postgres + Redis) at the repo
root, the backend and frontend dev servers running, and a sibling
`linked-data-explorer` repo's backend running on `:3001` (required for the
Procesbibliotheek journey). `e2e/global-setup.ts` checks all of these before
any test runs and fails fast with the exact start commands if one is down —
it does not start anything itself.

### Public-site Playwright suite

`packages/public-site/e2e/publiek.spec.ts`
(`npm run test:e2e --workspace=@ronl/public-site`) against real
`/v1/public/*` data (no mocks) — search→filter→detail→back URL
preservation, a deep link with pre-applied filters, keyboard-only
navigation, plus three axe-core accessibility scans (home, results, a detail
page) asserting no critical/serious violations.

**Measured 19 August 2026 against v2026.08.19: 6 tests, 6 passed, 0 failed,
0 flaky, 0 skipped, 8.9s.** Unlike every other figure on this page, this one was
not re-measured for v2026.08.20 — nothing under `packages/public-site/src/`
changed between the two releases, but the suite was not re-run to confirm it.

Unlike the frontend suite, Playwright starts its own dev server for this
package (`webServer` in `playwright.config.ts`) — only the backend needs to
already be running. Setting `E2E_BASE_URL` points the suite at an
already-deployed site instead (used for post-deploy verification against
ACC).

### Live smoke suite (shell scripts, cross-app)

Four gated shell scripts under `scripts/`, deliberately kept out of `npm
test` — they hit real running services over the network, mutate real data
in two cases, and need real credentials for some tiers.

| Script | Covers | Mutates? |
|---|---|---|
| `test-smoke-live.sh` | Cross-app health: Operaton, Keycloak, LDE, TriplyDB, CPRMV, media store, eDOCS reach/status, MCP layer | No |
| `test-edocs-live.sh` | eDOCS workspace + document lifecycle — see [eDOCS — Live Testing](edocs-live-testing.md) | Yes |
| `test-doccle-live.sh` | Doccle sender API — see [Doccle — Live Testing](doccle-live-testing.md) | Yes — not yet live-tested, still `DOCCLE_STUB_MODE=true` in every run so far |
| `test-m2m-routes.sh` | M2M decision-evaluation routes against ACC | No |

```bash
bash scripts/test-smoke-live.sh                                    # local, full run
CLIENT_SECRET=<secret> TARGET=acc bash scripts/test-smoke-live.sh   # against ACC
bash scripts/test-edocs-live.sh                                    # eDOCS, mutating
CLIENT_SECRET=<secret> bash scripts/test-doccle-live.sh             # Doccle, mutating
CLIENT_SECRET=<secret> bash scripts/test-m2m-routes.sh              # M2M routes vs ACC
```

Exit `0` when nothing failed, `1` on any real failure — a dependency that's
intentionally off (stub mode, no `CLIENT_SECRET`) skips with a `~` note,
never a red fail. `curl http://localhost:3002/v1/health | jq .` (or the ACC
equivalent) is the fastest single check of a running instance's dependency
status, independent of the smoke scripts.

---

## Adding tests

- **Colocate.** `foo.ts(x)` → `foo.test.ts(x)`, next to the source, in all
  three packages — no `__tests__` or `tests/` directories.
- **Backend**: mock at the service boundary (axios, pg-promise, the MCP SDK)
  and drive routes with supertest through a real `jwtMiddleware` test stub
  reading an `x-test-roles` header. Path aliases (`@utils/`, `@services/`,
  `@auth/`, `@middleware/`, `@routes/`, `@models/`, `@ronl/shared`) are
  mapped in `packages/backend/jest.config.js` and work inside test files.
- **Frontend & public site**: default to the `node` Vitest environment,
  opt into `jsdom` per file with `// @vitest-environment jsdom` only when a
  component or DOM-touching hook needs it. Mock at the network boundary with
  `msw`, not by stubbing `axios` methods directly. Use `vi.hoisted` for any
  mock referenced inside a `vi.mock` factory.
- **Shared mocks/fixtures** used by more than one test file in a directory go
  in a local `__helpers__` subdirectory — don't create one until a second
  file actually needs to share something.
- **Scope large containers to critical interactions**, not exhaustive branch
  coverage — mock every child component/context one level below what the
  container under test actually consumes, since those children have their
  own test files already.
- **Keep wall-clock assertions out of the main suite.** A budget asserted
  against `performance.now()` measures the machine as much as the code once 130
  test files are competing for cores. Name such a spec `*.perf.test.ts`: the
  default run excludes them and `npm run test:perf` executes them without file
  parallelism, as its own CI step.
- **Update the counts on this page** when a phase lands, from a real run
  (`--json --outputFile=...` for Jest, `--reporter=json --outputFile=...`
  for Vitest) rather than an estimate or a grep for `it(`/`test(` — both
  miscount multi-line and parameterised cases.

---

## Roadmap

**E2E CI wiring is deliberately deferred for both Playwright suites.** Both
run locally only today. The frontend suite needs a `webServer`-style
auto-boot for Keycloak/Postgres/Redis/backend/LDE-backend (there's no human
to start the stack manually in CI), plus a known Node v24-on-Windows exit
crash in `globalSetup` and an unbounded local-Operaton-history-growth gap to
close first.

**Doccle has no live-tested results yet.** `test-doccle-live.sh` exists and
is ready to run, but every run so far has been in `DOCCLE_STUB_MODE=true` —
see [Doccle — Live Testing](doccle-live-testing.md).

**Backend `utils/` coverage is a known, accepted artifact**
(`utils/config.ts` 0%, `utils/logger.ts` mocked) — not scheduled for
closure, since closing it would mean testing `dotenv`'s own import-time
side effects or winston's real transport wiring, neither of which is where
the risk lives.

**Frontend/public-site branch-coverage depth** — the 15–20 point gap between
statement and branch coverage across both — is the natural next target once
there's appetite for it: defensive guards and catch-block edges inside
already-tested files, not new files to reach.

**Deliberately out of scope for now:** visual regression / screenshot
diffing, a cross-browser matrix (Chromium only in both Playwright suites),
and parallel/sharded E2E execution tuning — none are blockers at current
suite size.
