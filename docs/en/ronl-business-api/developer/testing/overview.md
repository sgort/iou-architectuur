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
    Every count and percentage below was produced on **24 September 2026**
    against **v2026.09.11**, on `main` at `86af73e`, after a clean `npm ci` in a
    separate clone on **Node 24.14.1 / npm 11.11.0**. Each workspace was run on
    its own, one after another, with its own `npm test`; all five of those
    scripts already include coverage. Rerun the commands in
    [Running the tests](#running-the-tests) to reproduce them.

    **The Playwright suites were _not_ re-run in this pass** — their figures on
    [E2E & live smoke](e2e.md) remain those measured on 30 August 2026, and they
    are now further out of date than a stale figure usually is: the spec
    inventory has **grown to eleven frontend specs**, one each in pa-demo and
    public-site, and the 27-test frontend figure predates
    `thuisbatterij-journey.spec.ts` entirely. Read those counts as a floor, not
    a total. The four live-smoke shell scripts remain described from their
    configuration only.

    **The root gates and the branch rulesets were also not re-run or re-read in
    this pass.** Everything under
    [Linting, formatting, git hooks, and CI](#linting-formatting-git-hooks-and-ci)
    still carries its 20 September result unless the text says otherwise; what
    *was* re-read at `86af73e` is the workflow tree itself.

**At a glance:**

| Package | Runner | Files | Tests | Result | Duration¹ | Statements | Branches | Functions | Lines |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|
| `packages/backend` | Jest + ts-jest | 89 | 2072² | all passing | 118.06s | 98.44% | 92.44% | 97.44% | 98.86% |
| `packages/frontend` | Vitest + RTL | 110 | 1117 | all passing³ | 176.97s | 93.23% | 89.92% | 87.96% | 94.06% |
| `packages/pa-cockpit` | Vitest + RTL | 43 | 476 | all passing | 37.58s | 90.11% | 88.52% | 86.52% | 91.33% |
| `packages/pa-demo` | Vitest + jsdom | 19 | 106 | all passing | 19.62s | 93.47% | 95.65% | 85.00% | 92.85% |
| `packages/public-site` | Vitest + jsdom | 32 | 235 | all passing | 29.21s | 95.92% | 96.31% | 95.07% | 96.41% |

**293 files · 4006 tests**, all passing, **nothing failed and nothing skipped**,
in about **6 minutes 21 seconds** of runner-reported time across the five runs
(about 7 minutes 15 seconds of wall clock, counting npm's own start-up). One
performance spec runs separately — 4007 in total. See
[Coverage](coverage.md) for what those percentages mean and where the remaining
gaps are.

Against v2026.09.9 that is **+3 files and +51 tests**: the backend gained three
files and 44 tests, the frontend three tests, the public site four, and
pa-cockpit and pa-demo neither.

² The backend reported **2011** for several releases, of which 2008 ran and
three were permanently skipped; those three went with the unreachable
`PHASE_NOT_MODELLED` branch they guarded (issue #85). The 2072 measured here is
growth on top of that 2008 — **no workspace skips anything**.

³ The frontend was **1117/1117 green run serially**. Its default parallel run
showed five contention-only failures, all in
`ChangelogPanel.variants.test.tsx`, which passes in isolation — see
[A parallel failure is not a finding](#a-parallel-failure-is-not-a-finding) and
[issue #199](https://github.com/sgort/ronl-business-api/issues/199), which is
open on it. The coverage figures in that row are from the serial run, the only
green one.

!!! note "A coverage campaign, and every workspace moved at once"
    v2026.09.2 extended the backend-only coverage push to **all five workspaces
    that have a test runner**, against a per-file 80% branch floor: 53 files were
    below it, and none are now. Every package gained on every measure, which is
    unusual — the previous release's figures moved in one package and held to the
    decimal in the others.

    Branches moved furthest, which is the point of a *branch* floor, and the
    24 September figures hold the gain: public-site **70.39% → 96.31%**,
    pa-cockpit **75.55% → 88.52%**, frontend **80.33% → 89.92%**, backend
    **90.01% → 92.44%**, pa-demo **86.95% → 95.65%**.

    **The floor is now a gate, and it is per file.** v2026.09.6 configured it in
    all five runner configs — a glob key `'./src/**/*.ts': { branches: 80 }` in
    `packages/backend/jest.config.js`, and
    `thresholds: { branches: 80, perFile: true }` in the four Vitest configs —
    so one file dropping below 80% branches exits the run non-zero and names
    that file. **All five configurations are still in place on 24 September
    2026, and no run named a file**; scanning every file entry in the five
    `coverage-summary.json` reports independently finds **zero of 299 files
    below 80% branches** in any workspace. The floor is **branches only**,
    deliberately: measured the same way, a functions floor at 80 would fail
    **26 files** (frontend 10, pa-cockpit 8, pa-demo 5, public-site 3,
    backend 0) — while the configs' own comments still say 31. See
    [Coverage Floor](../../../contributing/coverage-floor.md) and
    [Coverage](coverage.md).

¹ These are **elapsed** times for one `npm test` per workspace, each runner's
own file parallelism left on, run one workspace at a time. Treat them as an
order of magnitude rather than a figure to match, and compare like with like —
the frontend suite that reports 176.97s here takes **408.71s** under
`test:serial`, about 2.3 times longer. They are also machine-dependent to a
degree worth keeping in mind: every one of these five is slower than its
20 September counterpart while three of the five packages did not change at
all, which says more about the host than about the suites.

!!! warning "Vitest's `tests` line is not elapsed time"
    The frontend run takes **176.97 seconds** by Vitest's own `Duration`, and
    the same summary block prints `tests 334.13s` beside it — and
    `environment 915.56s`, which is larger still. Those figures sum per-worker
    time across parallel workers; nobody ever waited for either. Read as
    elapsed, they turn a three-minute suite into a claimed quarter-hour one —
    which is the most likely origin of the ~444s this table carried for
    v2026.09.5. Quote `Duration` from Vitest and `Time:` from Jest, and quote
    nothing else.

    The same trap has a second form in the JSON reporters. Vitest's
    `numTotalTestSuites` counts **`describe` blocks, not files** — public-site
    reports 88 against its 32 files. The file count is `testResults.length`,
    which is what the console's `Test Files` line shows.

---

## Where to look

| Page | Covers |
|---|---|
| [Coverage](coverage.md) | Headline and per-area coverage for all five packages, and why the last two decimals are noise |
| [Backend suite](backend.md) | The 89 files and 2072 tests in `packages/backend`, by area |
| [Public site suite](public-site.md) | The 32 files and 235 tests in `packages/public-site`, plus its own Playwright suite |
| [PA-demo suite](pa-demo.md) | The 19 files and 106 tests in `packages/pa-demo`, and the one Playwright suite that runs in CI |
| [Caseworker](dashboards/caseworker.md) · [PA cockpit](dashboards/pa-cockpit.md) · [Infra-board](dashboards/infra-board.md) · [Woo-dashboard](dashboards/woo-dashboard.md) | The frontend and cockpit suites, split the way the product is — one page per board |
| [E2E & live smoke](e2e.md) | The Playwright suites, what they need running, and the four cross-app shell scripts |
| [Writing tests](writing-tests.md) | Conventions for adding tests here, and the traps that have already cost time |

!!! note "The four board pages do not add up to the frontend total, by design"
    They account for **841 of the 1155** frontend tests *as the split was last
    derived, on 30 August 2026*. It was **not** re-derived on 24 September,
    when the frontend measured 1117 tests with the cockpit's 476 living in
    their own package — so read the shares below as proportions rather than as
    current counts. The other 314 were not board-specific and so had no board
    page to live on:

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
| `npm test` | Every workspace with a `test` script (see below) | 293 | 4006 |
| `npm run test:serial` | The same, without file parallelism | 293 | 4006 |
| `npm test --workspace=@ronl/backend` | Backend only (Jest, coverage on by default) | 89 | 2072 |
| `npm test --workspace=@ronl/frontend` | Frontend only (Vitest, coverage on by default) | 110 | 1117 |
| `npm test --workspace=@ronl/pa-cockpit` | The cockpit package | 43 | 476 |
| `npm test --workspace=@ronl/pa-demo` | The public demo | 19 | 106 |
| `npm test --workspace=@ronl/public-site` | Public site only (Vitest, coverage on by default) | 32 | 235 |
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

### A parallel failure is not a finding

The 24 September pass is a worked example of the rule above, and the reason the
frontend row in the table carries a footnote rather than a red result. It is
also the second pass running in which the same file has been the one to go red
under load — **one test on 20 September, five today** — which is what finally
made the mechanism worth publishing rather than merely noting.

The frontend's default `npm test` — file parallelism on, as CI runs it — came
back **1112 passed, 5 failed**, every one of them in the same file:

```text
FAIL  src/pages/ChangelogPanel.variants.test.tsx >
      ChangelogPanel with an empty changelog >
      opens without expanding anything, rather than throwing on a missing first entry
TestingLibraryElementError: Unable to find role="dialog"
```

Two checks, in this order, before drawing any conclusion from that:

1. **The file on its own**, run from `packages/frontend`:
   `npx vitest run --config vite.config.ts --coverage.enabled=false src/pages/ChangelogPanel.variants.test.tsx`
   → exit 0, **1 file · 7 tests · passing**, twice in a row, in 5.32s and 3.70s.
   From the repository root the same run is
   `npx vitest run --config packages/frontend/vite.config.ts ChangelogPanel.variants`;
   `setupFiles` resolves against the config rather than the cwd, so both work.
2. **The whole suite serially.** `npm run test:serial --workspace=@ronl/frontend`
   → exit 0, **110 files · 1117 tests · passing · 408.71s**. Inside that run the
   file took **654ms**; inside the parallel run it took **7225ms** and failed
   five of its seven tests.

So the failure is contention under parallel load, not a defect in the code under
test, and the honest way to publish the frontend is **all green — 1117/1117
serially, with five contention-only failures in the default parallel run in a
file that passes in isolation**.

#### Why this file, and why five instead of one

!!! info "Open work — [issue #199](https://github.com/sgort/ronl-business-api/issues/199)"
    Opened 24 September 2026 on the evidence below. What follows is a diagnosis
    with a fix still to choose, not a closed explanation: nothing in the
    repository yet stops this recurring, and the trend line says it will.

The mechanism is worth stating, because it is not the timeout most people reach
for and because it explains the growth from one failure to five without any
change to the test:

- `ChangelogPanel` is a **`lazy()` + `Suspense` shim**, split so the changelog
  data does not ship in the entry chunk. Its content therefore resolves
  *asynchronously*, and every test in `ChangelogPanel.variants.test.tsx` opens
  with `await screen.findByRole('dialog')` for exactly that reason — the file's
  own comment says so, and warns that dropping those awaits would make the
  negative assertions pass against an empty DOM.
- **`findBy*` does not use `testTimeout`.** It uses testing-library's own
  async-util timeout, which defaults to **1000 ms** and is configured nowhere in
  this package. So the config's `testTimeout: 20000` — the setting that fixed
  the August flakiness — has no bearing on this failure at all. A dynamic import
  slower than one second fails the assertion rather than extending it, and the
  error reads *"Unable to find role=dialog"* against an empty body rather than
  as a timeout.
- **The module it waits on keeps growing.** `changelog-data.ts` is
  **612,980 bytes** at v2026.09.11, up **7.1%** from 572,299 at v2026.09.9,
  while `ChangelogPanel.variants.test.tsx` and `ChangelogPanel.tsx` are both
  untouched between the two releases.

The test did not get worse. The module it waits on got bigger, and the
one-second budget it is measured against did not move. That is also the
prediction, and the reason [#199](https://github.com/sgort/ronl-business-api/issues/199)
is open rather than this being a footnote: left alone, this will fail in more of
the file's seven tests each release, because the changelog only grows.

**Whatever the fix turns out to be, it belongs at the file's own boundary** —
and **not** at a parallelism flag. CI runs `npm test` parallel and should keep
doing so. The issue carries three candidates, none yet chosen:

- an explicit `findByRole('dialog', { timeout })` in that file;
- a `configure({ asyncUtilTimeout })` in the frontend's `src/test/setup.ts`,
  which would cover every `findBy*` in the package rather than this one file;
- decoupling the variants test from the real 600 KB module altogether, with a
  fixture — the option that removes the trend line instead of raising the
  budget ahead of it. The file already mocks `./changelog-data`; what it waits
  on is the lazy chunk behind the panel itself.

The first two buy time proportional to the number chosen. The third is the only
one that stops the clock.

This class of failure is not a surprise here; `packages/frontend/vite.config.ts`
already documents it in the comment above `testTimeout: 20000`, which records
the suite as green in five consecutive parallel runs on an idle machine and
producing 8–16 timeout failures under concurrent load, across a file set that
changes with how busy the machine is. `ChangelogPanel.test.tsx` is named in that
same comment as a file needing more headroom still. What that comment does not
cover, and what the five failures above are, is the *other* timeout — the one
testing-library owns rather than Vitest.

!!! danger "The fix is not to turn parallelism off"
    Disabling file parallelism globally would make the symptom go away and take
    the signal with it. It diverges local runs from CI, where the gating suites
    still run parallel; it costs real time on every later run — 408.71s against
    176.97s on this suite alone; and flakiness under parallelism is usually a genuine
    defect worth finding, in shared module state, an unisolated temp directory
    or a port collision. `test:serial` exists to *diagnose* a suspect failure,
    not to become the default. Where a suite really is parallelism-sensitive,
    fix it at its own boundary — the `*.perf.test.ts` convention and the
    per-file timeouts below are both that pattern.

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
  own blocking CI step. **Not re-run on 24 September 2026 either** — its last
  measured result is still from **12 September 2026: 1 file · 1 test · passing ·
  1.04s**, with coverage off. Because `vite.config.ts` excludes
  `src/**/*.perf.test.ts`, the frontend's 110 files and 1117 tests above do
  **not** include it — it is the one test in the repository that has to be
  counted separately, and the one unit-test figure on this page that was
  carried over rather than re-measured.

`ChangelogPanel.test.tsx` was the other casualty of the same contention: its
15-second timeout sufficed in isolation but not inside a full run, where it was
observed taking 22s. `changelog-data.ts` renders every real version entry, so
the test is genuinely slow rather than unreliable — and a timeout exists to
catch a hang, not to assert a speed. It was raised to 60s, which costs no
coverage; the perf spec remains the one place a real budget is asserted. It was
green in the 24 September serial run at **22.66s**, which is the same figure
that prompted the raise and a reminder of how little headroom 15s left.

Its sibling `ChangelogPanel.variants.test.tsx` is the file that failed under
parallel load on 20 September and again, five times over, on 24 September —
same component, same root cause, still the variants file rather than this one
that has yet to be given headroom. The headroom it needs is **not**
`testTimeout`, which is what was raised for this file. That is
[issue #199](https://github.com/sgort/ronl-business-api/issues/199); see
[Why this file, and why five instead of one](#why-this-file-and-why-five-instead-of-one).

---

## Linting, formatting, git hooks, and CI

All four root gates were run on 20 September 2026 and all four passed. **They
were not re-run on 24 September** — that pass measured the test suites only —
so the results below are carried over rather than re-measured.

| Command | What it does | Result (measured) |
|---|---|---|
| `npm run lint` | `npm run lint --workspaces --if-present` — `eslint .` in backend, frontend, public-site | exit 0, no errors, 68s |
| `npm run check-format` | `prettier --check "**/*.{ts,tsx,json,md}" --ignore-path .gitignore` — **one repo-wide glob, not a per-workspace fan-out** | *All matched files use Prettier code style!*, 15s |
| `npm run check-shared` | `node scripts/check-shared-declarations.mjs` — what stands in for tests in `packages/shared` | `check-shared-declarations: 11 file(s) in packages/shared/src/ — declarations and constant data only.`, 1s |
| `npm run check-supply-chain` | `node scripts/check-supply-chain.mjs` — every action pin against its version comment and the register | `31 pinned reference(s) across 5 action(s) in .github/workflows/` … `OK — digests, version comments and the register all agree.`, 4s |

`npm run lint` skips `@ronl/shared` the same way `test` does — no `lint` script
there. `npm run check-format`, by contrast, is **not** scoped by workspace
scripts at all: it is a single Prettier invocation over the whole tree (minus
`.gitignore`d paths), so it reaches `packages/shared` too even though `shared`
defines no format-check script of its own.

!!! note "`packages/shared` has no test script, and that is the design"
    It defines `build`, `prepare`, `clean` and `type-check` and nothing else,
    so `--if-present` skips it. What polices it instead is `check-shared`,
    which asserts that every file under `packages/shared/src/` holds
    declarations and constant data only — no runtime behaviour, hence nothing
    to unit test. It runs in the `audit` job, which is the one required check,
    so the package with no tests is in fact the one whose rule is enforced on
    every pull request.

### Git hooks

| Hook | Runs | Scope |
|---|---|---|
| `pre-commit` | `npx lint-staged` | Staged files only |
| `pre-push` | `npm run deps:check` → build `@ronl/shared` → `npm run type-check` → `npm run lint` → `npm run check-format` | All workspaces (type-check, lint) / whole tree (check-format) |

!!! important "The hooks do not run the tests"
    Re-read against `.husky/` on 20 September 2026 and still true: `pre-commit`
    runs `npx lint-staged` and nothing else, and `pre-push` runs the five
    commands above in that order. Neither invokes any `test` script, so nothing
    client-side stops a push that breaks a suite — run `npm test` yourself
    before pushing anything nontrivial.

    **`deps:check` is new at the front of `pre-push`**, and it is there for a
    reason the hook file records: on 14 September 2026 a clone still on Prettier
    3.8.1, after the lockfile had moved to 3.9.6, failed `check-format` on seven
    correctly-formatted files and nothing said why. Running it first means a
    push from an install that no longer matches `package-lock.json` stops with
    the fix named — `npm ci` — rather than the later checks running against the
    wrong tool versions.

    What has changed is on the server. Since 20 August 2026 each deploy
    workflow runs the suite of the package it ships; since v2026.09.6 the
    frontend workflows also run `@ronl/pa-cockpit`'s; and since v2026.09.7 the
    backend suite runs on the pull request rather than only on the merge. As of
    19 September 2026 those runs also **gate** on `acc` — see
    [What actually gates a merge](#what-actually-gates-a-merge).

### CI

**Eleven** workflows under `.github/workflows/`, read at `86af73e` — an acc/prod
pair per deployable package, the supply-chain `audit` gate, the Semgrep `scan`
job added in v2026.09.7, and the promotion orchestrator added since v2026.09.9:

| Workflow | Lint | Type-check | **Tests** | E2E | Perf budget | Build | Deploys? |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| `azure-backend-acc.yml` / `-prod.yml` | ✅ | – | **✅** | – | – | ✅ | **No** — packages and uploads an artifact |
| `azure-frontend-acc.yml` / `-prod.yml` | ✅ | – | **✅ ×2** — pa-cockpit, then frontend | – | **✅** | ✅ | Yes |
| `azure-pa-demo-acc.yml` / `-prod.yml` | ✅ | ✅ | **✅** | **✅ (acc only)** | – | ✅ | Yes |
| `azure-publicsite-acc.yml` / `-prod.yml` | ✅ | ✅ | **✅** | – | – | ✅ | Yes |
| `promote-to-production.yml` | – | – | – | – | – | – | Orchestrates the four `-prod` workflows in order |
| `zizmor.yml` | – | – | – | – | – | – | No — the required `audit` gate |
| `semgrep.yml` | – | – | – | – | – | – | No — `scan`, reporting and not required |

!!! note "The four `-prod.yml` workflows no longer trigger themselves"
    Read at `86af73e`: all four now declare `on: workflow_call` and
    `workflow_dispatch` **only**. A push to `main` no longer starts them — it
    starts `promote-to-production.yml`, which decides what changed and calls
    them in order, backend first so the three sites never deploy against a
    backend that has not been promoted yet. The test steps inside each of them
    are unchanged; what moved is who invokes them. See [CI/CD](../cicd.md).

**Every deployable package has had a real CI test step since 20 August 2026** —
a failing test fails the pipeline in all eight Azure workflows. Public-site had
one already. Backend CI runs Jest alongside its existing lint step; frontend CI
before that ran neither lint nor test, going straight from `npm ci` to
`vite build`.

**`@ronl/pa-cockpit` was the package that phrasing missed.** It is a library
with no deploy workflow of its own, so until v2026.09.6 nothing triggered its
suite and **its 476 tests ran nowhere in CI** — a count third only to the
backend's and the frontend's, covered locally and only locally. Both frontend
workflows now run it, as a step placed *before* the frontend's own, because the
frontend imports it: there is no point testing the consumer while the library
is broken. The pa-demo workflows consume the cockpit too, and watch
`packages/pa-cockpit/**` in their path filters, but run only pa-demo's own
suite.

**The backend suite now runs before a merge, not only after one.** Both backend
workflows triggered on `push` alone, so a backend pull request reached `acc`
with `audit` as its only check and the backend suite ran retrospectively —
including, after v2026.09.6, the per-file branch floor it carries. A
`pull_request` trigger on `azure-backend-acc.yml` closed that in v2026.09.7
(issue #87), and both path filters gained `package-lock.json` and
`package.json`, so a lockfile-only change — Renovate's above all — is
no longer built and tested by nothing. A concurrency group keyed on the
pull-request number keeps a twice-pushed branch from running the suite twice. It
paid for
itself immediately: an `axios` 1.18 security bump broke the backend build *on
the pull request*, 1859 tests passing and one suite failing to compile against a
widened header type. `azure-backend-prod.yml` keeps `push` only, deliberately —
`main` is promoted from `acc`, where that same suite has already run.

### What actually gates a merge

**This changed on 19 September 2026, and the two branches are deliberately
different.** Read from the repository rulesets
(`gh api repos/sgort/ronl-business-api/rulesets`) on 20 September 2026 and
**not re-read on 24 September** — a gating claim is only as current as the last
time somebody ran that command:

| Branch | Ruleset | Required status checks |
|---|---|---|
| `acc` | *acc supply-chain gate* | `audit`, `scan`, `build`, `Build and Deploy ACC Frontend`, `Build and Deploy ACC PA Demo`, `Build and Deploy ACC Public Site` |
| `main` | *main promotion gate* | `audit` |

So on `acc` a red suite now **does** block the merge. `build` is
`azure-backend-acc.yml`'s build job, which runs the backend's `npm test`; the
three `Build and Deploy ACC …` contexts are the frontend, pa-demo and
public-site deploy jobs, each of which runs its package's suite — and the
frontend's runs `@ronl/pa-cockpit`'s first. Between them, every one of the five
suites is now a required check on `acc`. `scan` — Semgrep — became required in
the same change; test files remain excluded from its Code scanning, a fixture
credential not being a leaked one. Both rulesets also forbid deletion and
non-fast-forward pushes, and require a pull request to change the branch at all.

!!! note "`main` requiring only `audit` is not an oversight"
    **No production workflow has a `pull_request` trigger.** A check that never
    runs on the pull request cannot be required of it: adding one would block
    every promotion forever. `main` is promoted from `acc`, where those same
    suites have already run and now also gate. `audit` and `scan` are the two
    workflows that do trigger on any pull request, which is what makes `audit`
    requirable there.

    This is now doubly true. Read at `86af73e`, the four `-prod.yml` files have
    no `push` trigger either — they are `workflow_call` and `workflow_dispatch`
    only, invoked by `promote-to-production.yml`. Through v2026.09.9 they fired
    on `push` to `main`, which is what this note used to say.

!!! warning "This page said the opposite until 20 September 2026"
    Through v2026.09.7 these pages stated that `audit` was the only required
    check on **both** branches and that "a suite that runs is not a suite that
    gates". That was true when written and is now false for `acc`. The claim
    outlived the ruleset by a day; a gating claim is only as current as the last
    time somebody read the rulesets, which is why the command to do so is quoted
    above rather than described.

**`azure-pa-demo-acc.yml` is the only workflow that runs an end-to-end suite** —
the first Playwright in CI anywhere in this repository. See
[PA-demo suite](pa-demo.md#the-playwright-suite).

The backend workflows are the exception to "deploy": they end at *Create
deployment zip* → *Upload deployment artifact*. Nothing in them calls a deploy
action, and there is no post-deployment health check — the artifact is
deployed separately, from a developer machine. See
[CI/CD](../cicd.md) and the [supply-chain gate](../../../contributing/supply-chain.md).

**The coverage gap closed differently from the test gap.** Gating on coverage
while it was still climbing was judged theatre — the same call the
[Linked Data Explorer](../../../linked-data-explorer/developer/testing.md#ci-the-test-gate)
made and has since reversed for the same reason — so there is still no coverage
job in any workflow, and there does not need to be.

It closed from the other direction rather than by adding a coverage job. Since
v2026.09.6 the per-file branch floor lives in the five runner configs and
`npm test` already runs with coverage, so coverage is checked wherever the
suites run — in CI and on a developer's machine, by the same command, with no
separate step to keep in step.

---

## Roadmap

**E2E CI wiring is done for one of the three Playwright suites.** The
[PA-demo suite](pa-demo.md#the-playwright-suite) runs as a blocking step of
`azure-pa-demo-acc.yml`, which was possible because that demo needs no backend,
database or Keycloak — Playwright starts its own dev server and that is the whole
environment.

The other two still run locally only. The frontend suite needs a
`webServer`-style auto-boot for Keycloak/Postgres/Redis/backend/LDE-backend —
its `playwright.config.ts` declares **no `webServer` at all**, and there is no
human to start the stack manually in CI — plus an unbounded
local-Operaton-history-growth gap to close first. The public-site suite has no
such blocker and is the obvious next candidate: it already declares its own
`webServer` and needs only the backend.

The Node v24-on-Windows exit crash that used to be listed here as a third
blocker is **fixed**, and `e2e/global-setup.ts` records how: `AbortSignal.timeout()`
left its internal timer uncleaned before the fetch settled, tripping a libuv
`UV_HANDLE_CLOSING` assertion on process exit. A manually managed
`AbortController` with an explicit `clearTimeout` replaced it.

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
