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
    Every count and percentage below was produced on **20 September 2026**
    against **v2026.09.9**, on `main` at `10bcf8b`, after a clean `npm ci` in a
    separate clone on **Node 24.14.1 / npm 11.11.0**. Each workspace was run on
    its own, one after another, with its own `npm test`; all five of those
    scripts already include coverage. Rerun the commands in
    [Running the tests](#running-the-tests) to reproduce them.

    **The Playwright suites were _not_ re-run in this pass** — their figures on
    [E2E & live smoke](e2e.md) remain those measured on 30 August 2026. The
    spec inventory was verified unchanged against `main` (ten frontend specs,
    one each in pa-demo and public-site), but the counts themselves are older
    than the rest of this page. The four live-smoke shell scripts remain
    described from their configuration only.

**At a glance:**

| Package | Runner | Files | Tests | Result | Duration¹ | Statements | Branches | Functions | Lines |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|
| `packages/backend` | Jest + ts-jest | 86 | 2028² | all passing | 73.06s | 98.37% | 92.35% | 97.29% | 98.79% |
| `packages/frontend` | Vitest + RTL | 110 | 1114 | all passing³ | 84.86s | 93.23% | 89.92% | 87.96% | 94.06% |
| `packages/pa-cockpit` | Vitest + RTL | 43 | 476 | all passing | 23.91s | 90.07% | 88.52% | 86.39% | 91.33% |
| `packages/pa-demo` | Vitest + jsdom | 19 | 106 | all passing | 8.57s | 93.47% | 95.65% | 85.00% | 92.85% |
| `packages/public-site` | Vitest + jsdom | 32 | 231 | all passing | 15.67s | 95.82% | 96.45% | 94.89% | 96.33% |

**290 files · 3955 tests**, all passing, **nothing failed and nothing skipped**,
in about **3 minutes 26 seconds** of runner-reported time across the five runs
(a little over 4 minutes of wall clock, counting npm's own start-up). One
performance spec runs separately — 3956 in total. See
[Coverage](coverage.md) for what those percentages mean and where the remaining
gaps are.

² The backend reported **2011** for several releases, of which 2008 ran and
three were permanently skipped; those three went with the unreachable
`PHASE_NOT_MODELLED` branch they guarded (issue #85). The 2028 measured here is
growth on top of that 2008 — **no workspace skips anything**.

³ The frontend was **1114/1114 green run serially**. Its default parallel run
showed one contention-only failure, in `ChangelogPanel.variants.test.tsx`,
which passes in isolation — see
[A parallel failure is not a finding](#a-parallel-failure-is-not-a-finding).

!!! note "A coverage campaign, and every workspace moved at once"
    v2026.09.2 extended the backend-only coverage push to **all five workspaces
    that have a test runner**, against a per-file 80% branch floor: 53 files were
    below it, and none are now. Every package gained on every measure, which is
    unusual — the previous release's figures moved in one package and held to the
    decimal in the others.

    Branches moved furthest, which is the point of a *branch* floor, and the
    20 September figures hold the gain: public-site **70.39% → 96.45%**,
    pa-cockpit **75.55% → 88.52%**, frontend **80.33% → 89.92%**, backend
    **90.01% → 92.35%**, pa-demo **86.95% → 95.65%**.

    **The floor is now a gate, and it is per file.** v2026.09.6 configured it in
    all five runner configs — a glob key `'./src/**/*.ts': { branches: 80 }` in
    `packages/backend/jest.config.js`, and
    `thresholds: { branches: 80, perFile: true }` in the four Vitest configs —
    so one file dropping below 80% branches exits the run non-zero and names
    that file. **All five passed on 20 September 2026 and nothing was named**;
    scanning every file entry in the five `coverage-summary.json` reports
    independently finds **zero files below 80% branches** in any workspace. The
    floor is **branches only**, deliberately: measured the same way, a
    functions floor at 80 would fail **26 files** (frontend 10, pa-cockpit 8,
    pa-demo 5, public-site 3, backend 0). See
    [Coverage Floor](../../../contributing/coverage-floor.md) and
    [Coverage](coverage.md).

¹ These are **elapsed** times for one `npm test` per workspace, each runner's
own file parallelism left on, run one workspace at a time on an otherwise idle
machine. Treat them as an order of magnitude rather than a figure to match, and
compare like with like — the frontend suite that reports 84.86s here takes
**266.92s** under `test:serial`, a little over three times longer.

!!! warning "Vitest's `tests` line is not elapsed time"
    The frontend run takes **84.86 seconds** by Vitest's own `Duration`, and the
    same summary block prints `tests 202.89s` beside it. That second figure sums
    per-worker time across parallel workers; nobody ever waited for it. Read as
    elapsed, it turns a ninety-second suite into a claimed three-and-a-half
    minute one — which is the most likely origin of the ~444s this table carried
    for v2026.09.5. Quote `Duration` from Vitest and `Time:` from Jest, and
    quote nothing else.

    The same trap has a second form in the JSON reporters. Vitest's
    `numTotalTestSuites` counts **`describe` blocks, not files** — public-site
    reports 88 against its 32 files. The file count is `testResults.length`,
    which is what the console's `Test Files` line shows.

---

## Where to look

| Page | Covers |
|---|---|
| [Coverage](coverage.md) | Headline and per-area coverage for all five packages, and why the last two decimals are noise |
| [Backend suite](backend.md) | The 86 files and 2028 tests in `packages/backend`, by area |
| [Public site suite](public-site.md) | The 32 files and 231 tests in `packages/public-site`, plus its own Playwright suite |
| [PA-demo suite](pa-demo.md) | The 19 files and 106 tests in `packages/pa-demo`, and the one Playwright suite that runs in CI |
| [Caseworker](dashboards/caseworker.md) · [PA cockpit](dashboards/pa-cockpit.md) · [Infra-board](dashboards/infra-board.md) · [Woo-dashboard](dashboards/woo-dashboard.md) | The frontend and cockpit suites, split the way the product is — one page per board |
| [E2E & live smoke](e2e.md) | The Playwright suites, what they need running, and the four cross-app shell scripts |
| [Writing tests](writing-tests.md) | Conventions for adding tests here, and the traps that have already cost time |

!!! note "The four board pages do not add up to the frontend total, by design"
    They account for **841 of the 1155** frontend tests *as the split was last
    derived, on 30 August 2026*. It was **not** re-derived on 20 September,
    when the frontend measured 1114 tests with the cockpit's 476 living in
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
| `npm test` | Every workspace with a `test` script (see below) | 290 | 3955 |
| `npm run test:serial` | The same, without file parallelism | 290 | 3955 |
| `npm test --workspace=@ronl/backend` | Backend only (Jest, coverage on by default) | 86 | 2028 |
| `npm test --workspace=@ronl/frontend` | Frontend only (Vitest, coverage on by default) | 110 | 1114 |
| `npm test --workspace=@ronl/pa-cockpit` | The cockpit package | 43 | 476 |
| `npm test --workspace=@ronl/pa-demo` | The public demo | 19 | 106 |
| `npm test --workspace=@ronl/public-site` | Public site only (Vitest, coverage on by default) | 32 | 231 |
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

The 20 September pass is a worked example of the rule above, and the reason the
frontend row in the table carries a footnote rather than a red result.

The frontend's default `npm test` — file parallelism on, as CI runs it — came
back **1113 passed, 1 failed**:

```text
FAIL  src/pages/ChangelogPanel.variants.test.tsx >
      ChangelogPanel with an empty changelog >
      opens without expanding anything, rather than throwing on a missing first entry
TestingLibraryElementError: Unable to find role="dialog"
```

Two checks, in this order, before drawing any conclusion from that:

1. **The file on its own.**
   `npx vitest run src/pages/ChangelogPanel.variants.test.tsx --coverage.enabled=false`
   → exit 0, **1 file · 7 tests · passing · 2.37s**.
2. **The whole suite serially.** `npm run test:serial --workspace=@ronl/frontend`
   → exit 0, **110 files · 1114 tests · passing · 266.92s**.

So the failure is contention under parallel load, not a defect in the code under
test, and the honest way to publish the frontend is **all green — 1114/1114
serially, with one contention-only failure in the default parallel run that
passes in isolation**.

This class of failure is not a surprise here; `packages/frontend/vite.config.ts`
already documents it in the comment above `testTimeout: 20000`, which records
the suite as green in five consecutive parallel runs on an idle machine and
producing 8–16 timeout failures under concurrent load, across a file set that
changes with how busy the machine is. `ChangelogPanel.test.tsx` is named in that
same comment as a file needing more headroom still.

!!! danger "The fix is not to turn parallelism off"
    Disabling file parallelism globally would make the symptom go away and take
    the signal with it. It diverges local runs from CI, where the gating suites
    still run parallel; it costs real time on every later run — three times over
    on this suite alone; and flakiness under parallelism is usually a genuine
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
  own blocking CI step. **Not re-run on 20 September 2026** — its last measured
  result is from **12 September 2026: 1 file · 1 test · passing · 1.04s**, with
  coverage off. Because `vite.config.ts` excludes `src/**/*.perf.test.ts`, the
  frontend's 110 files and 1114 tests above do **not** include it — it is the
  one test in the repository that has to be counted separately, and the one
  figure on this page that was carried over rather than re-measured.

`ChangelogPanel.test.tsx` was the other casualty of the same contention: its
15-second timeout sufficed in isolation but not inside a full run, where it was
observed taking 22s. `changelog-data.ts` renders every real version entry, so
the test is genuinely slow rather than unreliable — and a timeout exists to
catch a hang, not to assert a speed. It was raised to 60s, which costs no
coverage; the perf spec remains the one place a real budget is asserted. Its
sibling `ChangelogPanel.variants.test.tsx` is the file that failed under
parallel load on 20 September — same component, same cause, and it is the
variants file rather than this one that has yet to be given headroom.

---

## Linting, formatting, git hooks, and CI

All four root gates were run on 20 September 2026 and all four passed.

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

**Ten** workflows under `.github/workflows/`, read at `10bcf8b` — an acc/prod
pair per deployable package, the supply-chain `audit` gate, and the Semgrep
`scan` job added in v2026.09.7:

| Workflow | Lint | Type-check | **Tests** | E2E | Perf budget | Build | Deploys? |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| `azure-backend-acc.yml` / `-prod.yml` | ✅ | – | **✅** | – | – | ✅ | **No** — packages and uploads an artifact |
| `azure-frontend-acc.yml` / `-prod.yml` | ✅ | – | **✅ ×2** — pa-cockpit, then frontend | – | **✅** | ✅ | Yes |
| `azure-pa-demo-acc.yml` / `-prod.yml` | ✅ | ✅ | **✅** | **✅ (acc only)** | – | ✅ | Yes |
| `azure-publicsite-acc.yml` / `-prod.yml` | ✅ | ✅ | **✅** | – | – | ✅ | Yes |
| `zizmor.yml` | – | – | – | – | – | – | No — the required `audit` gate |
| `semgrep.yml` | – | – | – | – | – | – | No — `scan`, reporting and not required |

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
(`gh api repos/sgort/ronl-business-api/rulesets`) on 20 September 2026:

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
    **No production workflow has a `pull_request` trigger** — all four
    `-prod.yml` files fire on `push` to `main` and on `workflow_dispatch`, and
    `azure-backend-prod.yml` says so in a comment answering issue #87. A check
    that never runs on the pull request cannot be required of it: adding one
    would block every promotion forever. `main` is promoted from `acc`, where
    those same suites have already run and now also gate. `audit` and `scan`
    are the two workflows that do trigger on any pull request, which is what
    makes `audit` requirable there.

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
