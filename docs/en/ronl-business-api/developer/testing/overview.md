---
component: RONL Business API
---

# Testing

RONL Business API is an npm-workspaces monorepo with four tested packages:
the Express/TypeScript backend on **Jest**, the caseworker portal
(`packages/frontend`) on **Vitest** + React Testing Library, the public
search site (`packages/public-site`) on **Vitest** + jsdom, and the public
PA Cockpit demo (`packages/pa-demo`) on **Vitest** + jsdom. All four run with
coverage by default.

!!! info "Figures on this page are measured, not estimated"
    Backend, frontend and public-site figures were produced by running the
    suites against **v2026.08.23** on **22 August 2026**, from a cold cache,
    on `acc` at `57ce4c2`. The `packages/pa-demo` row was measured separately,
    on **25 August 2026**, on branch `feat/public-pa-cockpit` at `a59a0a7` —
    that package has not merged to `acc` yet, so its figures carry a
    different date and commit than its three siblings on this page. Rerun the
    commands in [Running the tests](#running-the-tests) to reproduce any of
    them.

    Two things were **not** re-run for this release and say so where they
    appear: the public-site Playwright suite, whose figures date from
    v2026.08.19, and the four live-smoke shell scripts, which remain described
    from their configuration only. See [E2E & live smoke](e2e.md).

**At a glance:**

| Package | Runner | Files | Tests | Result | Wall time | Statements | Branches | Functions | Lines |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|
| `packages/backend` | Jest + ts-jest | 74 | 1576 | all passing | ~23s | 98.35% | 91.49% | 96.65% | 98.75% |
| `packages/frontend` | Vitest + RTL | 133 | 1155 | all passing | ~61s¹ | 87.47% | 78.68% | 83.35% | 88.87% |
| `packages/public-site` | Vitest + jsdom | 28 | 134 | all passing | ~12s | 86.82% | 70.39% | 87.63% | 88.76% |
| `packages/pa-demo` | Vitest + jsdom | 13 | 68 | all passing | ~5s | 73.94% | 63.41% | 72.22% | 73.87% |

**248 files · 2933 tests**, plus one performance spec run separately — 2934 in
total. `packages/pa-demo` also carries its own 9-test Playwright suite (see
[pa-demo suite](pa-demo.md)), not included in that count — same treatment as
the other two Playwright suites on this page. See [Coverage](coverage.md) for
what those percentages mean and where the remaining gaps are.

¹ Wall time varies with machine load; treat it as an order of magnitude rather
than a figure to match. The same frontend suite has measured 61s on an idle
machine and 88s on a contended one. That contention used to make two tests
**fail** rather than merely run slow; both were fixed on 20 August rather than
left as known flakes, and the wall-clock budget that was one of them now runs
separately — see [The performance budget](#the-performance-budget).

---

## Where to look

| Page | Covers |
|---|---|
| [Coverage](coverage.md) | Headline and per-area coverage for all four packages, and why the last two decimals are noise |
| [Backend suite](backend.md) | The 74 files and 1576 tests in `packages/backend`, by area |
| [Public site suite](public-site.md) | The 28 files and 134 tests in `packages/public-site`, plus its own Playwright suite |
| [pa-demo suite](pa-demo.md) | The 13 files and 68 tests in `packages/pa-demo`, the four no-Live layers, the bundle gate, the drift checker, and its own Playwright suite |
| [Caseworker](dashboards/caseworker.md) · [PA cockpit](dashboards/pa-cockpit.md) · [Infra-board](dashboards/infra-board.md) · [Woo-dashboard](dashboards/woo-dashboard.md) | The frontend suite, split the way the product is — one page per board |
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
| `npm test` | Every workspace with a `test` script (see below) | 248 | 2933 |
| `npm test --workspace=@ronl/backend` | Backend only (Jest, coverage on by default) | 74 | 1576 |
| `npm test --workspace=@ronl/frontend` | Frontend only (Vitest, coverage on by default) | 133 | 1155 |
| `npm run test:perf --workspace=@ronl/frontend` | The wall-clock budget, run without file parallelism | 1 | 1 |
| `npm test --workspace=@ronl/public-site` | Public site only (Vitest, coverage on by default) | 28 | 134 |
| `npm test --workspace=@ronl/pa-demo` | PA Cockpit demo only (Vitest, coverage on by default) | 13 | 68 |

```bash
# Everything
npm test

# One workspace
npm test --workspace=@ronl/backend
npm test --workspace=@ronl/frontend
npm test --workspace=@ronl/public-site
npm test --workspace=@ronl/pa-demo

# Watch mode
npm run test:watch --workspace=@ronl/backend
npm run test:watch --workspace=@ronl/frontend
npm run test:watch --workspace=@ronl/public-site
npm run test:watch --workspace=@ronl/pa-demo

# Single file / pattern
npx jest --config packages/backend/jest.config.js --no-coverage --testPathPattern=rules
npx vitest run --config packages/frontend/vite.config.ts session
npx vitest run --config packages/public-site/vite.config.ts SectionIndex
npx vitest run --config packages/pa-demo/vite.config.ts mock-lock
```

**What `npm test` at the root actually runs.** The root script is
`npm run test --workspaces --if-present`, fanning out over every package under
`packages/*`. Four of the five have a `test` script — `@ronl/backend`,
`@ronl/frontend`, `@ronl/public-site`, `@ronl/pa-demo` — and `--if-present`
silently skips the fifth, `@ronl/shared`, which has no `test` script at all
(only `build`, `prepare`, `clean`, `type-check`). That is expected, not a gap:
`shared` is a types-only package with nothing to unit test.

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

Six Azure workflows under `.github/workflows/`, one acc/prod pair per
package — this table covers three of the four packages on this page.
`pa-demo` ships its own CI pipeline once merged; see
[pa-demo suite → CI](pa-demo.md#ci) for its two deploy workflows and the
separate, non-blocking drift-check workflow, none of which are on `acc`
yet.

| Workflow | Lint | Type-check | **Tests** | Perf budget | Build | Deploys? |
|---|:---:|:---:|:---:|:---:|:---:|---|
| `azure-backend-acc.yml` / `-prod.yml` | ✅ | – | **✅** | – | ✅ | **No** — packages and uploads an artifact |
| `azure-frontend-acc.yml` / `-prod.yml` | ✅ | – | **✅** | **✅** | ✅ | Yes |
| `azure-publicsite-acc.yml` / `-prod.yml` | ✅ | ✅ | **✅** | – | ✅ | Yes |

**Every package has a real CI test gate**, as of 20 August 2026 — a failing test
blocks the pipeline in all six workflows. Public-site had one already. Backend
CI now runs Jest alongside its existing lint step; frontend CI previously ran
neither lint nor test, going straight from `npm ci` to `vite build`, and now
runs lint, the suite, and the performance budget before building.

The backend workflows are the exception to "deploy": they end at *Create
deployment zip* → *Upload deployment artifact*. Nothing in them calls a deploy
action, and there is no post-deployment health check — the artifact is
deployed separately.

The gap was deliberate while it lasted: gating on coverage that was still
climbing was judged theatre, the same call the
[Linked Data Explorer](../../../linked-data-explorer/developer/testing.md#ci-the-test-gate)
made and has since reversed for the same reason.

---

## Roadmap

**E2E CI wiring is deliberately deferred for both Playwright suites.** Both run
locally only today. The frontend suite needs a `webServer`-style auto-boot for
Keycloak/Postgres/Redis/backend/LDE-backend — there is no human to start the
stack manually in CI — plus a known Node v24-on-Windows exit crash in
`globalSetup` and an unbounded local-Operaton-history-growth gap to close first.

**Two boards have no end-to-end coverage.** [Infra-board](dashboards/infra-board.md)
and [Woo-dashboard](dashboards/woo-dashboard.md) are well covered by unit tests
and have no Playwright specs at all. That is a gap rather than a decision — the
PA cockpit work showed exactly which class of defect unit tests cannot see.

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
