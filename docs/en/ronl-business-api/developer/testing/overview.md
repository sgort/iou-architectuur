---
component: RONL Business API
---

# Testing

RONL Business API is an npm-workspaces monorepo with five tested packages: the
Express/TypeScript backend on **Jest**, and four on **Vitest** — the caseworker
portal (`packages/frontend`) with React Testing Library, the Public Affairs
cockpit (`packages/pa-cockpit`), the public cockpit demo
(`packages/pa-demo`) and the public search site (`packages/public-site`) with
jsdom. All five run with coverage by default.

!!! info "Figures on this page are measured, not estimated"
    Every count and percentage below was produced by running
    `npm run test:serial` against **v2026.09.5** on **5 September 2026**, on
    `acc` at `66940d9`, after a clean `npm ci`. Rerun the commands in
    [Running the tests](#running-the-tests) to reproduce them.

    **The Playwright suites were _not_ re-run for this release** — their figures
    on [E2E & live smoke](e2e.md) remain those measured on 30 August. The spec
    inventory was verified unchanged against `acc` (ten frontend specs, one
    each in pa-demo and public-site), and this release added unit tests only,
    but the counts themselves are older than the rest of this page. The four
    live-smoke shell scripts remain described from their configuration only.

**At a glance:**

| Package | Runner | Files | Tests | Result | Wall time¹ | Statements | Branches | Functions | Lines |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|
| `packages/backend` | Jest + ts-jest | 86 | 2011² | all passing | ~119s | 98.40% | 92.28% | 97.28% | 98.83% |
| `packages/frontend` | Vitest + RTL | 110 | 1104 | all passing | ~444s | 93.11% | 89.76% | 87.75% | 93.97% |
| `packages/pa-cockpit` | Vitest + RTL | 43 | 476 | all passing | ~111s | 90.07% | 88.52% | 86.39% | 91.33% |
| `packages/pa-demo` | Vitest + jsdom | 19 | 106 | all passing | ~37s | 93.47% | 95.65% | 85.00% | 92.85% |
| `packages/public-site` | Vitest + jsdom | 30 | 204 | all passing | ~47s | 96.09% | 96.92% | 94.62% | 96.16% |

**288 files · 3901 tests**, plus one performance spec run separately — 3902 in
total. See [Coverage](coverage.md) for what those percentages mean and where
the remaining gaps are.

² Backend reports 2011 total, of which **2008 pass and 3 are skipped**. The other
four workspaces skip nothing.

!!! note "A coverage campaign, and every workspace moved at once"
    v2026.09.2 extended the backend-only coverage push to **all five workspaces
    that have a test runner**, against a per-file 80% branch floor: 53 files were
    below it, and none are now. Every package gained on every measure, which is
    unusual — the previous release's figures moved in one package and held to the
    decimal in the others.

    Branches moved furthest, which is the point of a *branch* floor:
    public-site **70.39% → 96.92%**, pa-cockpit **75.55% → 88.52%**, frontend
    **80.33% → 89.76%**, backend **90.01% → 92.28%**, pa-demo
    **86.95% → 95.65%**.

    The floor is a **convention, not a gate** — no coverage threshold is
    configured in any runner config and no workflow measures coverage at all.
    See [Code Standards](../../../contributing/code-standards.md#the-80-branch-floor-is-a-convention-not-a-gate).

¹ These are **serial** wall times, measured with `test:serial`, and are much
longer than a parallel run — the frontend suite measures ~61s parallel on an
idle machine. Treat them as an order of magnitude rather than a figure to match,
and compare like with like.

---

## Where to look

| Page | Covers |
|---|---|
| [Coverage](coverage.md) | Headline and per-area coverage for all five packages, and why the last two decimals are noise |
| [Backend suite](backend.md) | The 86 files and 2011 tests in `packages/backend`, by area |
| [Public site suite](public-site.md) | The 30 files and 204 tests in `packages/public-site`, plus its own Playwright suite |
| [PA-demo suite](pa-demo.md) | The 19 files and 106 tests in `packages/pa-demo`, and the one Playwright suite that runs in CI |
| [Caseworker](dashboards/caseworker.md) · [PA cockpit](dashboards/pa-cockpit.md) · [Infra-board](dashboards/infra-board.md) · [Woo-dashboard](dashboards/woo-dashboard.md) | The frontend and cockpit suites, split the way the product is — one page per board |
| [E2E & live smoke](e2e.md) | The Playwright suites, what they need running, and the four cross-app shell scripts |
| [Writing tests](writing-tests.md) | Conventions for adding tests here, and the traps that have already cost time |

!!! note "The four board pages do not add up to the frontend total, by design"
    They account for **841 of the 1155** frontend tests. The other 314 are not
    board-specific and so have no board page to live on:

    - **223** in `src/services` (211), `App.test.tsx` (5), `src/hooks` (4) and
      `src/test` (3)
    - **49** in shared widgets reused across boards — `ProcessStartFormViewer`,
      `TimeLine`, `DecisionViewer`, `LoginChoice`, `AltchaWidget`,
      `SessionExpiryWarning`, `PersonalDataPanel`
    - **42** in pages that belong to no board — `AuthCallback`, `Dashboard`,
      `ChangelogPanel`, `LoginChoice`

    Note also that `components/CaseworkerDashboard/` is counted under
    [Caseworker](dashboards/caseworker.md) but is the **shared section-component
    library**, reused across three of the four V2 dashboards. Its 185 tests
    protect more than that one board.

---

## Running the tests

Run from the repository root after `npm install` (`node_modules` must already
be installed in every workspace).

| Command | Scope | Files | Tests |
|---|---|---:|---:|
| `npm test` | Every workspace with a `test` script (see below) | 288 | 3901 |
| `npm run test:serial` | The same, without file parallelism | 288 | 3901 |
| `npm test --workspace=@ronl/backend` | Backend only (Jest, coverage on by default) | 86 | 2011 |
| `npm test --workspace=@ronl/frontend` | Frontend only (Vitest, coverage on by default) | 110 | 1104 |
| `npm test --workspace=@ronl/pa-cockpit` | The cockpit package | 43 | 476 |
| `npm test --workspace=@ronl/pa-demo` | The public demo | 19 | 106 |
| `npm test --workspace=@ronl/public-site` | Public site only (Vitest, coverage on by default) | 30 | 204 |
| `npm run test:perf --workspace=@ronl/frontend` | The wall-clock budget, run without file parallelism | 1 | 1 |

```bash
# Everything
npm test

# Everything, serially — see the warning below
npm run test:serial

# One workspace
npm test --workspace=@ronl/backend
npm test --workspace=@ronl/pa-cockpit

# Single file / pattern
npx jest --config packages/backend/jest.config.js --no-coverage --testPathPattern=rules
npx vitest run --config packages/frontend/vite.config.ts session
npx vitest run --config packages/public-site/vite.config.ts SectionIndex
```

!!! warning "Reach for `test:serial`, not for a flag"
    This repository runs **two test runners behind one command shape** — the
    backend on Jest, the other four on Vitest. Any serial flag you reach for is
    right in four places and wrong in the fifth: `--no-file-parallelism` is
    Vitest's, `--runInBand` is Jest's, and Jest rejects the Vitest flags
    outright. Every workspace defines a `test:serial` script for exactly this
    reason, so the runner's identity stops being something the caller has to
    know.

    Note that a **parallel-run failure is not a finding until it fails
    serially.** The flakiness chased through August turned out to be timeouts at
    Vitest's 5000ms default under machine load, not a defect in the code under
    test; `testTimeout` is now 20s in all four Vitest workspaces.

**What `npm test` at the root actually runs.** The root script is
`npm run test --workspaces --if-present`, fanning out over every package under
`packages/*`. Five of the six have a `test` script — `@ronl/backend`,
`@ronl/frontend`, `@ronl/pa-cockpit`, `@ronl/pa-demo`, `@ronl/public-site` — and
`--if-present` silently skips the sixth, `@ronl/shared`, which has no `test`
script at all (only `build`, `prepare`, `clean`, `type-check`). That is
expected, not a gap: `shared` is a types-only package with nothing to unit test.

!!! warning "Clear the Jest cache before trusting a green backend run"
    ts-jest caches type diagnostics per file, so a warm cache can skip
    re-checking a file that no longer compiles and report the suite green. That
    is not hypothetical: nine backend test files were latently broken for
    weeks — every top-level declaration landing in the global scope, colliding
    across files — while `npm test` passed locally every time. The first CI run
    on a cold runner failed immediately.

    ```bash
    npx jest --config packages/backend/jest.config.js --clearCache
    ```

    Which files fail also varies between runs, because it depends on the order
    the type program reaches them. See
    [Writing tests](writing-tests.md#make-every-test-file-a-module).

### The performance budget

`simEngine.ts` carries a real budget: `run(cfg)` must process the default
3,150-application population in under **250ms**. Its source comment is emphatic
that if the assertion ever fails the threshold must not be loosened — the
intended remedy is a web worker, not a bigger number.

The problem was never the threshold. A single `performance.now()` call measures
the machine as much as the engine: on a contended host the assertion was
observed at 302ms, then 837ms, then 1297ms across three consecutive runs, and
inside a full `npm test` — where Vitest saturates every core with 133 parallel
test files — even the fastest of three CPU-time samples came out at 468ms,
against ~100ms in isolation. Wiring the CI test gate would have made that a
permanently red pipeline.

So the budget moved rather than moved up:

- The assertion lives in `simEngine.perf.test.ts`, still asserting `< 250ms`,
  now with a warm-up run and the fastest of three samples so a JIT pause or a
  stray GC cannot decide it.
- `vite.config.ts` excludes `src/**/*.perf.test.ts` from the default run.
- `vitest.perf.config.ts` mirrors it — same plugins, aliases and setup, but the
  perf specs are the only thing *included*, and `fileParallelism` is off. It
  spreads and overrides the base test block rather than using `mergeConfig`,
  which concatenates arrays and would have kept the base `exclude`, hiding the
  perf specs from their own run.
- `npm run test:perf` runs it, and both frontend workflows run that as their
  own blocking CI step.

`ChangelogPanel.test.tsx` was the other casualty of the same contention: its
15-second timeout sufficed in isolation but not inside a full run, where it was
observed taking 22s. `changelog-data.ts` renders every real version entry, so
the test is genuinely slow rather than unreliable — and a timeout exists to
catch a hang, not to assert a speed. It was raised to 60s, which costs no
coverage; the perf spec remains the one place a real budget is asserted.

---

## Linting, formatting, git hooks, and CI

| Command | What it does | Result (measured) |
|---|---|---|
| `npm run lint` | `npm run lint --workspaces --if-present` — `eslint .` in backend, frontend, public-site | exit 0, no errors |
| `npm run check-format` | `prettier --check "**/*.{ts,tsx,json,md}" --ignore-path .gitignore` — **one repo-wide glob, not a per-workspace fan-out** | exit 0, no violations |

`npm run lint` skips `@ronl/shared` the same way `test` does — no `lint` script
there. `npm run check-format`, by contrast, is **not** scoped by workspace
scripts at all: it is a single Prettier invocation over the whole tree (minus
`.gitignore`d paths), so it reaches `packages/shared` too even though `shared`
defines no format-check script of its own.

### Git hooks

| Hook | Runs | Scope |
|---|---|---|
| `pre-commit` | `npx lint-staged` | Staged files only |
| `pre-push` | build `@ronl/shared` → `npm run type-check` → `npm run lint` → `npm run check-format` | All workspaces (type-check, lint) / whole tree (check-format) |

!!! important "The hooks do not run the tests"
    Neither `pre-commit` nor `pre-push` invokes any `test` script, so nothing
    client-side stops a push that breaks a suite — run `npm test` yourself
    before pushing anything nontrivial. Since 20 August 2026 every pipeline
    does run them, so a broken push no longer reaches acceptance; the
    client-side gap is now a matter of feedback speed rather than of what
    ships.

### CI

**Nine** workflows under `.github/workflows/` on `acc` — an acc/prod pair per
package, plus the supply-chain `audit` gate:

| Workflow | Lint | Type-check | **Tests** | E2E | Perf budget | Build | Deploys? |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| `azure-backend-acc.yml` / `-prod.yml` | ✅ | – | **✅** | – | – | ✅ | **No** — packages and uploads an artifact |
| `azure-frontend-acc.yml` / `-prod.yml` | ✅ | – | **✅** | – | **✅** | ✅ | Yes |
| `azure-pa-demo-acc.yml` / `-prod.yml` | ✅ | ✅ | **✅** | **✅ (acc only)** | – | ✅ | Yes |
| `azure-publicsite-acc.yml` / `-prod.yml` | ✅ | ✅ | **✅** | – | – | ✅ | Yes |
| `zizmor.yml` | – | – | – | – | – | – | No — blocking `audit` gate |

**Every package has a real CI test gate**, as of 20 August 2026 — a failing test
blocks the pipeline in all eight Azure workflows. Public-site had one already.
Backend CI now runs Jest alongside its existing lint step; frontend CI previously
ran neither lint nor test, going straight from `npm ci` to `vite build`.

**`azure-pa-demo-acc.yml` is the only workflow that runs an end-to-end suite** —
the first Playwright in CI anywhere in this repository. See
[PA-demo suite](pa-demo.md#the-playwright-suite).

The backend workflows are the exception to "deploy": they end at *Create
deployment zip* → *Upload deployment artifact*. Nothing in them calls a deploy
action, and there is no post-deployment health check — the artifact is
deployed separately, from a developer machine. See
[CI/CD](../cicd.md) and the [supply-chain gate](../../../contributing/supply-chain.md).

The gap was deliberate while it lasted: gating on coverage that was still
climbing was judged theatre, the same call the
[Linked Data Explorer](../../../linked-data-explorer/developer/testing.md#ci-the-test-gate)
made and has since reversed for the same reason.

---

## Roadmap

**E2E CI wiring is done for one of the three Playwright suites.** The
[PA-demo suite](pa-demo.md#the-playwright-suite) runs as a blocking step of
`azure-pa-demo-acc.yml`, which was possible because that demo needs no backend,
database or Keycloak — Playwright starts its own dev server and that is the whole
environment.

The other two still run locally only. The frontend suite needs a
`webServer`-style auto-boot for Keycloak/Postgres/Redis/backend/LDE-backend —
there is no human to start the stack manually in CI — plus a known Node
v24-on-Windows exit crash in `globalSetup` and an unbounded
local-Operaton-history-growth gap to close first. The public-site suite has no
such blocker and is the obvious next candidate.

**One board has no end-to-end coverage.** [Woo-dashboard](dashboards/woo-dashboard.md)
is well covered by unit tests and has no Playwright spec at all. That is a gap
rather than a decision — the PA cockpit work showed exactly which class of
defect unit tests cannot see, and the Woo-dashboard has the same shape.

The [Infra-board](dashboards/infra-board.md) **was** in that sentence and should
not have been: two specs driving it landed on 24 August 2026, and this roadmap
item kept naming it through two subsequent syncs. E2E coverage per board is now
tabulated on [E2E & live smoke](e2e.md#coverage-per-board), which is the place
to check it rather than this paragraph.

**Doccle has no live-tested results yet.** `test-doccle-live.sh` exists and is
ready to run, but every run so far has been in `DOCCLE_STUB_MODE=true` — see
[Doccle — Live Testing](doccle-live-testing.md).

**Branch-coverage depth** is the natural next target across the frontend and
public site: defensive guards and catch-block edges inside already-tested
files, not new files to reach.

**Deliberately out of scope for now:** visual regression and screenshot
diffing, a cross-browser matrix (Chromium only in both Playwright suites), and
parallel or sharded E2E execution tuning — none are blockers at current suite
size.
