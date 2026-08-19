---
component: RONL Business API
---

# Testing

RONL Business API is an npm-workspaces monorepo with three tested packages:
the Express/TypeScript backend on **Jest**, the caseworker portal
(`packages/frontend`) on **Vitest** + React Testing Library, and the public
search site (`packages/public-site`) on **Vitest** + jsdom. All three run
with coverage by default. Each also has a Playwright **E2E** suite, described
from source later on this page — see [E2E and live smoke suites](#e2e-and-live-smoke-suites-described-from-source-not-measured).

!!! info "Figures on this page are measured, not estimated"
    Every count, command and coverage percentage below was produced by
    running the suites against **v2026.08.19** on **19 August 2026**. Rerun
    the commands in [Running the tests](#running-the-tests) to reproduce
    them.

**At a glance:**

| Package | Runner | Files | Tests | Result | Wall time | Statements | Branches | Functions | Lines |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|
| `packages/backend` | Jest + ts-jest | 71 | 1145 | all passing | ~40s | 94.28% | 73.54% | 94.13% | 95.69% |
| `packages/frontend` | Vitest + RTL | 130 | 1065 | 1063 passing, 2 flaky¹ | ~60–100s | 85.18% | 76.63% | 80.21% | 86.55% |
| `packages/public-site` | Vitest + jsdom | 28 | 134 | all passing | ~15s | 86.34% | 70.17% | 87.09% | 88.49% |

¹ Two frontend tests are timing-sensitive and fail intermittently only under
the CPU load of a full coverage run — see the note in
[Running the tests](#running-the-tests). Both pass reliably in isolation.

---

## Running the tests

Run from the repository root after `npm install` (`node_modules` must
already be installed in every workspace).

| Command | Scope | Files | Tests |
|---|---|---:|---:|
| `npm test` | Every workspace with a `test` script (see below) | 229 | 2344 |
| `npm test --workspace=@ronl/backend` | Backend only (Jest, coverage on by default) | 71 | 1145 |
| `npm test --workspace=@ronl/frontend` | Frontend only (Vitest, coverage on by default) | 130 | 1065 |
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

!!! warning "Two frontend tests are flaky under a full coverage run"
    `ChangelogPanel.test.tsx` (a 15s timeout that a CPU-contended full run can
    exceed — `changelog-data.ts` renders 60+ real version entries) and
    `simEngine.test.ts`'s performance assertion (`run(cfg)` must complete
    under 250ms; measured **302ms, 837ms, and 1297ms** on this machine across
    three consecutive full coverage runs, worsening each time as other work
    competed for CPU) both failed in every full-suite coverage run taken for
    this page. Both pass cleanly — 31/31 — when run alone
    (`npx vitest run src/pages/ChangelogPanel.test.tsx
    src/components/CaseworkerDashboardV2/regelsimulatie/simEngine.test.ts`).
    This is a known, previously-documented trade-off (both tests carry source
    comments explaining the budget/timeout), not a regression — but it means
    a red `npm test --workspace=@ronl/frontend` on a busy machine does not by
    itself mean something broke. Re-run the two files in isolation before
    treating a frontend failure as real.

!!! note "Coverage report on failure"
    Vitest's default is to skip writing a coverage report when any test
    fails. The frontend figures on this page were captured with
    `--coverage.reportOnFailure=true` so the two flaky tests above didn't
    blank the report; a plain `npm test --workspace=@ronl/frontend` on a
    contended machine may finish red with no `coverage/` output at all.

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
  "packages/backend/**/*.ts": ["npm run lint:fix --workspace=@ronl/backend", "prettier --write"],
  "packages/shared/**/*.ts": ["prettier --write"],
  "*.{json,md}": ["prettier --write"]
}
```

**`packages/public-site/**/*.{ts,tsx}` has no entry.** A staged public-site
source file gets no ESLint pass and no Prettier pass at commit time — only
the generic `*.{json,md}` rule applies, and that doesn't match `.ts`/`.tsx`.
It isn't uncaught for long: `pre-push`'s `npm run lint` and
`npm run check-format` both cover public-site in full before anything
reaches the remote, since neither is scoped by the `lint-staged` glob. But a
local commit alone can carry an unformatted or unlinted public-site change.

!!! important "The hooks do not run the tests"
    Neither `pre-commit` nor `pre-push` invokes any `test` script. Nothing
    client-side stops a push that breaks the backend, frontend, or
    public-site suite — run `npm test` yourself before pushing anything
    nontrivial.

### CI

Six Azure workflows under `.github/workflows/`, one acc/prod pair per
package:

| Workflow | Lint | Type-check | **Tests** | Build | Deploy |
|---|:---:|:---:|:---:|:---:|:---:|
| `azure-backend-acc.yml` / `-prod.yml` | ✅ | – | – | ✅ | ✅ |
| `azure-frontend-acc.yml` / `-prod.yml` | – | – | – | ✅ | ✅ |
| `azure-publicsite-acc.yml` / `-prod.yml` | ✅ | ✅ | **✅** | ✅ | ✅ |

**Public-site is the one package with a real CI test gate.** Both
`azure-publicsite-*.yml` workflows run `npm run lint`, `npm run type-check`,
then `npm test` (Vitest, with coverage) inside `packages/public-site` before
building and deploying — a failing test blocks the deploy. Backend CI lints
and builds but never runs Jest. Frontend CI does neither lint nor test — it
goes straight from `npm ci` to `vite build` to deploy. For backend and
frontend, `npm test` is a manual discipline enforced by review, not an
automated gate; for public-site it's enforced by the pipeline itself. A
post-deployment health check (backend only: 5 retries, 10s apart, against
`/v1/health`) confirms the deployed instance responds before a backend
deployment is marked successful.

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

### Frontend (Vitest + RTL) — 130 files, 1065 tests

| Area | Files | Tests | Covers |
|---|---:|---:|---|
| `src/components` | 90 | 598 | Every dashboard's shared section-component library (`CaseworkerDashboard/`, reused across three of the four V2 dashboards), each dashboard's own components (`CaseworkerDashboardV2`, `PADashboardV2`, `WooDashboard`, `InfraBoardDashboard`), the `*SectionRouter*`/`*Dock*`/`*CommandPalette*`/`*NoAccessPanel*` shells, and reusable widgets (`DecisionViewer`, `AltchaWidget`, `SessionExpiryWarning`, `PersonalDataPanel`, `ProcessStartFormViewer`, `TimeLine`) |
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

Measured with `npm test --workspace=<pkg>` per package against v2026.08.19
on 19 August 2026.

| Package | Statements | Branches | Functions | Lines |
|---|---:|---:|---:|---:|
| Backend | 94.28% | 73.54% | 94.13% | 95.69% |
| Frontend | 85.18% | 76.63% | 80.21% | 86.55% |
| Public site | 86.34% | 70.17% | 87.09% | 88.49% |

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

| Area | Statements | Branches | Functions | Lines |
|---|---:|---:|---:|---:|
| `middleware/` | 100.00% | 95.83% | 92.31% | 100.00% |
| `mcp-servers/` | 98.94% | 83.87% | 100.00% | 99.45% |
| `services/` | 95.97% | 77.73% | 95.95% | 97.14% |
| `media-aggregator/` | 95.76% | 85.64% | 98.21% | 96.88% |
| `pa-monitoring/` | 95.26% | 75.99% | 92.05% | 97.48% |
| `routes/` | 93.44% | 68.62% | 93.04% | 95.05% |
| `auth/` | 88.89% | 85.71% | 84.62% | 88.06% |
| `utils/` | 43.48% | 6.54% | 73.33% | 40.48% |

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
| `src/pages` | 81.00% | 61.15% | 77.90% | 83.70% |

---

## E2E and live smoke suites (described from source, not measured)

Everything in this section was **not run in this session** — the frontend
suite needs a live dev stack (Keycloak, Postgres, Redis, the backend, and a
sibling repo's LDE backend all running) and a local Operaton instance, and
the live smoke shell scripts hit real running services. This section
describes them from their configuration and specs only.

### Frontend Playwright suite

`packages/frontend/e2e/`, its own `playwright.config.ts`
(`npm run test:e2e --workspace=@ronl/frontend`). Per the source's own
tracked tally: **12 tests across 6 spec files**, Chromium only, `workers: 1`
(two specs race to claim an identically-named task for the same caseworker
against the shared local Operaton engine, so the suite trades parallelism
for correctness).

| Spec | Covers |
|---|---|
| `smoke.spec.ts` | App loads at `/`, `LoginChoice` renders, no console errors |
| `login-redirect.spec.ts` | One test per role (citizen/caseworker/infra/woo/PA) against the Flevoland tenant, driving the real Keycloak hosted login — 5 tests |
| `protected-route.spec.ts` | Cross-role `ProtectedRoute` redirect behavior — 2 tests |
| `caseworker-journey.spec.ts` | Citizen submits a real Kapvergunning request via Operaton/DMN; caseworker claims and completes both resulting tasks; a genuinely finalized roundtrip |
| `zorgtoeslag-journey.spec.ts` | Second deep journey — a commercial-org citizen submits a Zorgtoeslag claim, the `toeslagen` caseworker completes both steps |
| `tenant-isolation.spec.ts` | A real cross-tenant fixture — confirms a wrong-tenant caseworker does **not** see a task, and the right one does |

Requires: `docker compose up -d` (Keycloak + Postgres + Redis) at the repo
root, the backend and frontend dev servers running, and a sibling
`linked-data-explorer` repo's backend running on `:3001` (required for the
Procesbibliotheek journey). `e2e/global-setup.ts` checks all of these before
any test runs and fails fast with the exact start commands if one is down —
it does not start anything itself.

### Public-site Playwright suite

`packages/public-site/e2e/publiek.spec.ts`
(`npm run test:e2e --workspace=@ronl/public-site`). Per source: **6 tests**
against real `/v1/public/*` data (no mocks) — search→filter→detail→back URL
preservation, a deep link with pre-applied filters, keyboard-only
navigation, plus three axe-core accessibility scans (home, results, a detail
page) asserting no critical/serious violations.

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
- **Update the counts on this page** when a phase lands, from a real run
  (`--json --outputFile=...` for Jest, `--reporter=json --outputFile=...`
  for Vitest) rather than an estimate or a grep for `it(`/`test(` — both
  miscount multi-line and parameterised cases.

---

## Roadmap

**No CI test gate for backend or frontend.** Public-site is the only package
where a failing test blocks a deploy. Backend CI lints and builds but never
runs Jest; frontend CI does neither lint nor test. Wiring a test step into
`azure-backend-*.yml` (mirroring its existing `npm run lint` step) and into
`azure-frontend-*.yml` are both open items, not scheduled.

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
