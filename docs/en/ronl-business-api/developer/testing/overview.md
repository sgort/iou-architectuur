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
    Every count and percentage below was produced on **3 October 2026**
    against **v2026.10.0**, the release in production: `main` is at
    `0625d48`. The runs were made in the working checkout on `acc` at
    `0e3eed8`, whose tree is identical to `0625d48`, after
    `npm run deps:check` reported the installed dependencies in sync with the
    lockfile. Each workspace was run on its own, one after another, with its
    own **`npm run test:serial`**; all five of those scripts include coverage,
    as their `npm test` counterparts do. Rerun the commands in
    [Running the tests](#running-the-tests) to reproduce them.

    **The method differs from the 30 September pass in one respect**, and it is
    stated rather than assumed away: that pass ran each workspace's default
    `npm test`, with each runner's file parallelism on; this one ran
    `test:serial`, which is the same command with `--runInBand` (Jest) or
    `--no-file-parallelism` (Vitest) added. The counts do not depend on that.
    The durations do, heavily — see the footnote under the table — and the
    frontend's coverage can move in the second decimal with it, which
    [Coverage](coverage.md) explains. Where this page compares against an
    earlier release it names the date that figure was taken, because not every
    figure here has been re-measured on every pass.

    **The runtime was Node 22.23.2, the version `.nvmrc` names.** Every pass
    before this one ran on Node 24.14.1 and said so; this is the first set of
    figures on these pages taken on the Node the repository pins.

    **The Playwright suites _were_ re-run in this pass**, for the first time
    since 30 August, against a full local stack the developer already had
    running: frontend **27 passed, 1 skipped**, pa-demo **11 passed**, and
    public-site **6/6 serially, after two timeouts in its parallel run** — see
    [E2E & live smoke](e2e.md). The inventory is still **thirteen specs** —
    eleven frontend, `pa-demo/e2e/plato-demo` and `public-site/e2e/publiek` —
    and no spec changed between v2026.09.15 and v2026.10.0. The four live-smoke
    shell scripts remain described from their configuration only.

    **`npm run test:perf` was re-run too: 1 file · 1 test · passing**, its first
    measurement since 12 September. Because `vite.config.ts` excludes
    `src/**/*.perf.test.ts`, that one test is **not** part of the 124 frontend
    files or the repository-wide 320 / 4731 below. Wherever this page states a
    repository-wide file count, that count excludes the performance spec.

    **The root gates were re-run in this pass; the branch rulesets were not
    re-read.** `lint`, `check-format`, `lint:openapi`, `check-shared`,
    `check-supply-chain` and `check-swimlane-fixtures` all exited 0 on
    3 October — see
    [Linting, formatting, git hooks, and CI](#linting-formatting-git-hooks-and-ci).
    The backend's `test:contract` and `test:openapi-coverage` were not run on
    their own this time; their scope is contained in the full backend run. The
    rulesets were last read on 30 September — see
    [What actually gates a merge](#what-actually-gates-a-merge).

**At a glance:**

| Package | Runner | Files | Tests | Result | Duration¹ | Statements | Branches | Functions | Lines |
|---|---|---:|---:|---|---:|---:|---:|---:|---:|
| `packages/backend` | Jest + ts-jest | 100 | 2457² | all passing | 176.94s | 98.91% | 95.21% | 97.92% | 99.18% |
| `packages/frontend` | Vitest + RTL | 124 | 1378 | all passing³ | 589.43s | 95.23% | 93.02% | 91.21% | 95.76% |
| `packages/pa-cockpit` | Vitest + RTL | 43 | 515 | all passing | 133.53s | 92.61% | 93.89% | 89.56% | 93.13% |
| `packages/pa-demo` | Vitest + jsdom | 19 | 106 | all passing | 35.65s | 93.47% | 95.65% | 85.00% | 92.85% |
| `packages/public-site` | Vitest + jsdom | 34 | 275 | all passing | 76.58s | 96.68% | 97.40% | 95.09% | 97.23% |

**320 files · 4731 tests**, all passing, **nothing skipped**, in about
**16 minutes 52 seconds** of runner-reported time across the five serial runs
(about 18 minutes of wall clock — 199s, 616s, 140s, 49s and 79s — counting
npm's own start-up and, for the backend, the conformance-coverage step). One
performance spec runs separately and is excluded from both the 124 and the
320 — 4732 in total. See [Coverage](coverage.md) for what those percentages
mean and where the remaining gaps are.

**Against the 30 September measurement of v2026.09.15 — the previous
release — that is +8 files and +157 tests.** Three of the five workspaces
grew; pa-cockpit and pa-demo reproduced their counts and all four of their
percentages exactly, on packages whose source did not change. Written out:

| | 28 Sep · v2026.09.13 | 30 Sep · v2026.09.15 | 3 Oct · v2026.10.0 | Δ since 30 Sep |
|---|---:|---:|---:|---:|
| `packages/backend` | 96 files · 2202 | 97 · 2370 | **100 · 2457** | +3 · +87 |
| `packages/frontend` | 110 files · 1122 | 120 · 1318 | **124 · 1378** | +4 · +60 |
| `packages/pa-cockpit` | 43 files · 476 | 43 · 515 | **43 · 515** | — |
| `packages/pa-demo` | 19 files · 106 | 19 · 106 | **19 · 106** | — |
| `packages/public-site` | 32 files · 235 | 33 · 265 | **34 · 275** | +1 · +10 |
| **Total** | **300 · 4141** | **312 · 4574** | **320 · 4731** | **+8 · +157** |

The eight new files, by workspace:

- **Backend, three:** `middleware/error.middleware.test.ts` (8) for the 404,
  catch-all and rate-limit handlers that now answer
  [RFC 9457 problem details](../../features/api-design.md),
  `utils/problem.test.ts` (13) for `sendProblem` and the title derived from a
  code, and `routes/besluitvorming.routes.test.ts` (10) for
  `GET /v1/besluitvorming/active` and `/completed`. The other +56 went into
  existing files: `rip-swimlane/bpmn-swimlane.test.ts` +27 (process-declared
  phases, and the Gedelegeerd besluit and HR capacity claim BPMNs as
  fixtures), `services/operaton.service.test.ts` +11,
  `routes/m2m.routes.test.ts` +10 (the reserved-variable refusals, `POST`
  history and the deprecated `GET`), and +4 each in
  `routes/validsign.routes.test.ts` and
  `services/validsignCompletion.service.test.ts` (signing state per task,
  archive names). See [Backend suite](backend.md).
- **Frontend, four:** `CaseworkerDashboard/BesluitOverzichtSection.test.tsx`
  (7) and `BesluitStartSection.test.tsx` (3) for Besluitvorming,
  `components/signing/useTaskSignature.test.ts` (5), and
  `src/utils/problem.test.ts` (23), the response interceptor's mapping of a
  problem back onto `ApiResponse`. `SigningPanel.test.tsx` (15 → 16) and
  `resolveSigningUrl.test.ts` (4) are not new: they moved from
  `InfraBoardDashboard/` to the shared `components/signing/`. The largest
  growth in existing files is `TakenInbox.test.tsx` +4 — the signing panel in
  the caseworker inbox — and `modes.config.test.ts`, `SectionRouter.test.tsx`
  and `ProcessWhere.test.tsx` +3 each.
- **Public site, one:** `src/lib/problem.test.ts` (9), which reads a problem's
  `detail`; `lib/api.test.ts` gained one.

Vitest's console reports only package totals, and Jest's default reporter
prints no per-file counts either, so every per-file figure above is counted
from the source by parsing each test file with its `.each` tables expanded.
For the four Vitest workspaces that method reproduces the runner's totals
exactly — 1378, 515 and 275 at `0625d48`, and 1318 at `ae06c9e`. For the
backend, whose six files with `.each` over a named table the parser cannot
expand, the per-file figures are the 30 September run's own JSON counts plus
the parsed change in each of the eight files the release touched, with the
one non-literal table that changed (`bpmn-swimlane`'s twelve fixtures)
expanded by hand; the sum is the runner's **2457** exactly.

**History, 30 September: the twelve files v2026.09.14 and v2026.09.15
added**, by workspace:

- **Backend, one:** `openapi/testing/conformance.test.ts` (20 tests), for the
  helper that checks a real response against the documented schema (#269) —
  see [Backend suite](backend.md). The other +148 backend tests went into
  existing files, most of them in the route suites (+46), `rip-swimlane`
  (+56, the parser that now reads any laned process and its Awb phases) and
  `services` (+29); `openapi/coverage.test.ts` *shrank* from 7 tests to 3
  when the pending list it policed was emptied and deleted.
- **Frontend, ten:** seven in the new `components/process/` directory — the
  caseworker's process view — plus `PaletteActions.test.tsx`,
  `StartFailureNotice.test.tsx` and `src/indexHtml.test.ts`, the link-preview
  tags per build mode. An eighth file in `components/process/`,
  `PhaseSwimlane.test.tsx`, is not new: it moved there from
  `InfraBoardDashboard/` and grew from 22 tests to 38. The directory holds
  119 tests across those eight. Vitest's console reports only the package
  total, so these per-file figures are counted from the source by parsing
  every test file with `.each` tables expanded — a method that reproduces the
  runner's total exactly, 1318 at `ae06c9e` and 1122 at `963fe24`.
- **Public site, one:** `src/indexHtml.test.ts`, its own link-preview check,
  23 tests across four build modes.

**pa-cockpit gained 39 tests and no file** in that window, all from the two
branch-margin commits (see [Coverage](coverage.md)): `391b1a8` added four to
`DossierRow.test.tsx`, and `73a6764` the other 35 —
`pages/public-affairs-v2/Monitoring.test.tsx` (+16) and
`services/pa.api.test.ts` (+13) above all.

² The backend reported **2011** for several releases, of which 2008 ran and
three were permanently skipped; those three went with the unreachable
`PHASE_NOT_MODELLED` branch they guarded (issue #85). The 2457 measured here is
growth on top of that 2008 — **2011 → 2008 → 2028 → 2072 → 2198 → 2202 →
2370 → 2457** — and **no workspace skips anything**. The same run ended with
*"✓ all 136 documented operations were checked against a real response"*,
the conformance-coverage step `npm test` and `test:serial` carry after Jest —
three more operations than on 30 September, the two Besluitvorming lists and
`POST /v1/m2m/process/history`. See [Backend suite](backend.md).

³ The frontend is **1378/1378 green in its serial run**, the one this pass
made. No default parallel run — the one CI makes — was made on 3 October, so
this pass says nothing new about the frontend under parallel load; the last
such run, on 30 September, was 1318/1318 green. The file that failed under
load in four of the five passes before that, `ChangelogPanel.variants.test.tsx`,
was fixed at its own boundary in `afc2001`, which closed
[issue #199](https://github.com/sgort/ronl-business-api/issues/199) on
28 September — see
[A parallel failure is not a finding](#a-parallel-failure-is-not-a-finding).

!!! note "A coverage campaign, and every workspace moved at once"
    v2026.09.2 extended the backend-only coverage push to **all five workspaces
    that have a test runner**, against a per-file 80% branch floor: 53 files were
    below it, and none are now. Every package gained on every measure, which is
    unusual — the previous release's figures moved in one package and held to the
    decimal in the others.

    Branches moved furthest, which is the point of a *branch* floor, and the
    3 October figures hold the gain: public-site **70.39% → 97.40%**,
    pa-cockpit **75.55% → 93.89%**, frontend **80.33% → 93.02%**, backend
    **90.01% → 95.21%**, pa-demo **86.95% → 95.65%**.

    **The floor is a gate, and it is per file.** v2026.09.6 configured it in
    all five runner configs — a glob key `'./src/**/*.ts': { branches: 80 }` in
    `packages/backend/jest.config.js`, and
    `thresholds: { branches: 80, perFile: true }` in the four Vitest configs —
    so one file dropping below 80% branches exits the run non-zero and names
    that file. **All five configurations are unchanged at `0625d48`, and no
    run named a file**; reading every file entry in the five workspaces'
    coverage reports independently finds **zero of 327 files below 80%
    branches** in any workspace.

    **The floor is still 80, and the 85 margin no longer holds everywhere.**
    On 30 September every file cleared 85, after `391b1a8` (#256) and
    `73a6764` had lifted the files at or near the line. v2026.10.0 brought two
    new frontend files in below it, both well covered on statements but not
    yet on every branch. Measured on 3 October, the lowest file per workspace:

    | Workspace | Lowest file by branches | Branches |
    |---|---|---:|
    | backend | `pa-monitoring/pa-cache.ts`, `services/llm/OpenAILlmProvider.ts` | 86.36 |
    | frontend | `components/CaseworkerDashboard/BesluitOverzichtSection.tsx` | **80.43** |
    | pa-cockpit | `services/dossierbeheer.api.ts` | 85.10 |
    | pa-demo | `demo/changelog/DemoChangelogPanel.tsx` | 87.50 |
    | public-site | `lib/useQueryState.ts`, `pages/herkomst/HerkomstTrace.tsx` | 87.50 |

    The frontend's second file under 85 is `components/process/phaseSet.ts`,
    at 83.33% (10 of 12 branches). `BesluitOverzichtSection.tsx` — the
    *Lopende* and *Afgeronde besluiten* list, new in this release — passes the
    gate with 37 of 46 branches, half a point clear: one more uncovered branch
    there fails a required check. `IouFeedbackSection.tsx`, which sat exactly
    on the 85 line on 30 September, reads 86.21% now, on a test added with
    this release. It is a margin, not a floor; the configs say 80.

    The floor is **branches only**, deliberately: measured the same way, a
    functions floor at 80 would now fail **24 files** (frontend 9, pa-cockpit 7,
    pa-demo 5, public-site 3, backend 0) — one more than on 30 September,
    `BesluitStartSection.tsx` at 2 of 3 functions. The configs' own comments
    were corrected from 31 to 26 in `391b1a8`, dated 28 September, and are two
    high today. See
    [Coverage Floor](../../../contributing/coverage-floor.md) and
    [Coverage](coverage.md).

¹ These are **elapsed** times for one `npm run test:serial` per workspace —
Jest's `Time:` and Vitest's `Duration` — run one workspace at a time, with
**file parallelism off**. They are not comparable with the parallel figures
earlier passes published, and they are not slow suites: on 28 September the
frontend took **133.15s** parallel and **372.31s** under `test:serial`, about
2.8 times longer, and the 3 October serial run, at **589.43s** on 1378 tests,
is the same shape. Treat them as an order of magnitude rather than a figure
to match, and compare like with like.

They are machine-dependent to a degree worth keeping in mind even within one
mode: the same parallel backend suite was measured at **118.06s** (24 Sep),
**59.86s** (26 Sep), **94.98s** (28 Sep) and **54.67s** (30 Sep), and the
parallel frontend at 176.97s, 119.31s, 133.15s and 114.82s across the same
dates. Spread like that says more about the host than about the suites, which
is why nothing on this page is compared on time alone.

!!! warning "Vitest's `tests` line is not elapsed time"
    On 30 September the parallel frontend run took **114.82 seconds** by
    Vitest's own `Duration`, and the same summary block printed
    `tests 286.64s` beside it — and `environment 588.41s`, which is larger
    still. Those figures sum per-worker time across parallel workers; nobody
    ever waited for either. Read as elapsed, they turn a two-minute suite into
    a claimed ten-minute one — which is the most likely origin of the ~444s
    this table carried for v2026.09.5. (In the 3 October serial run, with one
    file at a time, they read `tests 151.56s` and `environment 241.45s`
    against a `Duration` of 589.43s — smaller than elapsed, the other way
    round, and no more quotable.) Quote `Duration` from Vitest and `Time:`
    from Jest, and quote nothing else.

    The same trap has a second form in the JSON reporters. Vitest's
    `numTotalTestSuites` counts **`describe` blocks, not files** — public-site
    reported 88 against its 32 files on 28 September. The file count is `testResults.length`,
    which is what the console's `Test Files` line shows.

---

## Where to look

| Page | Covers |
|---|---|
| [Coverage](coverage.md) | Headline and per-area coverage for all five packages, and why the last two decimals are noise |
| [Backend suite](backend.md) | The 100 files and 2457 tests in `packages/backend`, by area |
| [Public site suite](public-site.md) | The 34 files and 275 tests in `packages/public-site`, plus its own Playwright suite |
| [PA-demo suite](pa-demo.md) | The 19 files and 106 tests in `packages/pa-demo`, and the one Playwright suite that runs in CI |
| [Caseworker](dashboards/caseworker.md) · [PA cockpit](dashboards/pa-cockpit.md) · [Infra-board](dashboards/infra-board.md) · [Woo-dashboard](dashboards/woo-dashboard.md) | The frontend and cockpit suites, split the way the product is — one page per board |
| [E2E & live smoke](e2e.md) | The Playwright suites, what they need running, and the four cross-app shell scripts |
| [Writing tests](writing-tests.md) | Conventions for adding tests here, and the traps that have already cost time |

!!! note "The four board pages do not add up to the frontend total, by design"
    Re-derived on **3 October 2026** at `0625d48`, they account for
    **934 of the 1378** frontend tests: Caseworker 475, the shared process view
    in `components/process/` 123 (listed on the Caseworker page), Infra-board
    234, the shared signing panel in `components/signing/` 25 (listed on the
    Infra-board page) and Woo-dashboard 77. The PA cockpit's 515 live in their
    own package and are not part of the 1378. Per-file frontend counts are
    taken from the source, with `.each` tables expanded, because Vitest's
    console reports only the package total; summed, they reproduce that total
    exactly. The other 444 are not board-specific and so have no board page to
    live on:

    - **239** in `src/services` (162), the three root test files (38 —
      `App.test.tsx`, `indexHtml.test.ts`, `pa-cockpit-class-coverage.test.ts`),
      `src/hooks` (5) and `src/utils` (34, of which `problem.test.ts` is 23)
    - **70** in shared widgets reused across boards — `ProcessStartFormViewer`,
      `TimeLine`, `DecisionViewer`, `StartFailureNotice`, `AltchaWidget`,
      `SessionExpiryWarning`, `PersonalDataPanel` and the two `LoginChoice`
      components
    - **40** in the frontend's host side of the PA cockpit —
      `components/PADashboardV2` (30), `PaCockpitRoute` and
      `pa-cockpit-host` (5 each)
    - **95** in pages that belong to no board — `AuthCallback`, `Dashboard`,
      `ChangelogPanel` and its variants, `LoginChoice`, `no-eager-changelog`
      and `pages/login-choice`

    Note also that `components/CaseworkerDashboard/` is counted under
    [Caseworker](dashboards/caseworker.md) but is the **shared section-component
    library**, reused across three of the four V2 dashboards. Its 244 tests
    protect more than that one board — and `components/process/` is shared the
    same way, since the Infra-board's `ProjectDetail` draws its phase stepper
    and swimlane with the same `PhaseStepper` and `PhaseSwimlane` the
    caseworker's process overview uses. Since v2026.10.0 so is
    `components/signing/`: the caseworker inbox and the Infra-board both render
    the same `SigningPanel` through `useTaskSignature`.

---

## Running the tests

Run from the repository root after `npm install` (`node_modules` must already
be installed in every workspace).

| Command | Scope | Files | Tests |
|---|---|---:|---:|
| `npm test` | Every workspace with a `test` script (see below) | 320 | 4731 |
| `npm run test:serial` | The same, without file parallelism — what the 3 October figures were measured with, one workspace at a time | 320 | 4731 |
| `npm test --workspace=@ronl/backend` | Backend only (Jest, coverage on by default), then the conformance-coverage check | 100 | 2457 |
| `npm run test:contract --workspace=@ronl/backend` | `src/openapi` and `src/routes` — the OpenAPI gates plus every route suite, coverage off | 24 | 692 |
| `npm run test:openapi-coverage --workspace=@ronl/backend` | `src/openapi` only — the coverage gate, the conformance helper and their helpers, coverage off | 4 | 43 |
| `npm run lint:openapi --workspace=@ronl/backend` | Builds `openapi/openapi.json` and lints it with Spectral against the NL API Design Rules 2.2.1 ruleset, failing on `error` | — | — |
| `npm test --workspace=@ronl/frontend` | Frontend only (Vitest, coverage on by default) | 124 | 1378 |
| `npm test --workspace=@ronl/pa-cockpit` | The cockpit package | 43 | 515 |
| `npm test --workspace=@ronl/pa-demo` | The public demo | 19 | 106 |
| `npm test --workspace=@ronl/public-site` | Public site only (Vitest, coverage on by default) | 34 | 275 |
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

**To reproduce the figures in the table above**, rather than just run the
suites, ask each runner for machine-readable output and read the counts from
that instead of from the console:

```bash
# Backend — Jest
npm test --workspace=@ronl/backend -- --json --outputFile=<OUT>/backend.json \
  --coverageReporters=json-summary --coverageReporters=text-summary

# Each Vitest workspace: frontend, pa-cockpit, pa-demo, public-site
npm test --workspace=@ronl/<pkg> -- --reporter=default --reporter=json \
  --outputFile.json=<OUT>/<pkg>.json \
  --coverage.reporter=json-summary --coverage.reporter=text
```

!!! warning "`--outputFile.json` resolves against the workspace, not the repo root"
    `npm test --workspace=…` runs with the cwd set to the package directory, so
    a relative `--outputFile.json=../out/frontend.json` lands in `packages/`
    rather than where you meant. **Give it an absolute path.** Jest's
    `--outputFile` has the same behaviour. This cost a stray directory inside
    the clone during the 28 September pass, which is why it is written down.

    Read the file count from `testResults.length` and the coverage figures from
    each workspace's `coverage/coverage-summary.json` — never by grepping the
    console output, and never from `numTotalTestSuites`, which counts
    `describe` blocks (see the warning above).

`lint:openapi` was run on its own on 3 October and passed, with *"No results
with a severity of 'error' found!"*. The two contract test scripts were not:
their counts in the table are the full run's `src/routes` (20 files,
649 tests) and `src/openapi` (4 and 43), which is exactly what they select.
When they were last run on their own, on 30 September, they reported
**23 suites · 668 tests** and **4 suites · 43 tests**, reconciling with that
day's full run the same way. The two test scripts are subsets of the backend's own `npm test`, which runs the same
files with coverage on — they exist to check the contract quickly, not as
extra gates — and, being filtered Jest runs, **neither ends with the
conformance-coverage check** that `npm test` runs after Jest; see
[Backend suite](backend.md). `lint:openapi` is the one that is not covered by
`npm test`: both backend workflows run it as its own step, before the tests.

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

The 24 September pass is the worked example of the rule above. The same file
was the one to go red under load in four of five passes — **one test on
20 September, five on 24 September, none on 26 September, one again on
28 September** — which is what made the mechanism worth publishing rather than
merely noting. **On 30 September, at v2026.09.15, the frontend's default
parallel run was 1318/1318 green**, the first measured pass since the file was
fixed at its own boundary in `afc2001`, which closed
[issue #199](https://github.com/sgort/ronl-business-api/issues/199) on
28 September. One green run does not prove a fix; what the fix changed, and why
it removes the cause rather than widening a timeout, is set out
[below](#why-this-file-and-why-the-count-moves). The 3 October pass ran every
unit suite serially, so it adds no parallel evidence either way. The accounts
that follow are history, kept as they were measured.

!!! note "3 October: the rule applied to a Playwright suite"
    The same rule decided the one red result of the 3 October pass. The
    public-site Playwright suite, run with its config's default parallel
    workers (six on that machine), came back **4 passed, 2 failed**: both
    search-journey tests (`publiek.spec.ts:6` and `:27`) timed out after 10s
    waiting for the search-result filter checkbox. Re-run serially with
    `--workers=1`, against the same running backend, it passed
    **6/6 in 7.8s**. Recorded as *6/6 serially; 2 timeouts in the parallel
    run* — not as a defect. See
    [E2E & live smoke](e2e.md#public-site-playwright-suite).

!!! note "History, 28 September: one failure, and it is contention — established, not assumed"
    The v2026.09.13 pass ran the frontend's default parallel `npm test` and got
    **110 files · 1122 tests · 1121 passed · 1 failed · 133.15s**. The failure
    was in `ChangelogPanel.variants.test.tsx` again, and again on
    `findByRole('dialog')`:

    ```text
    FAIL  src/pages/ChangelogPanel.variants.test.tsx >
          ChangelogPanel with an empty changelog >
          opens without expanding anything, rather than throwing on a missing first entry
    TestingLibraryElementError: Unable to find role="dialog"
    ```

    Two checks before drawing any conclusion, in this order, exactly as the
    rule requires:

    1. **The file on its own** —
       `npx vitest run --config packages/frontend/vite.config.ts --coverage.enabled=false src/pages/ChangelogPanel.variants.test.tsx`
       → exit 0, **1 file · 7 tests · passing · 2.55s**.
    2. **The whole suite serially** — `npm run test:serial --workspace=@ronl/frontend`
       → exit 0, **110 files · 1122 tests · passing · 372.31s**.

    Then, for good measure, **two further parallel runs of the whole suite**,
    one with coverage off and one with it on: **1122/1122 green** both times, in
    69.40s and 45.02s, with the variants file taking 930ms in the second.

    So it is contention, not a defect — and the circumstance is worth recording
    because it is the same one every time. The failing run was the **first of
    the five workspace runs after the backend's Jest suite**, on a machine that
    had not yet quietened down; the three green runs came later, on a host with
    less on it. A contention failure needs contention.

    That run did not close
    [issue #199](https://github.com/sgort/ronl-business-api/issues/199), and
    was not meant to. The fix landed the same evening, in `afc2001` — see
    [Why this file](#why-this-file-and-why-the-count-moves).

**The 24 September account, kept as it was measured.** The frontend's default
`npm test` came back **1112 passed, 5 failed**, every one of them in the same
file and with the same `Unable to find role="dialog"` error. The file on its
own passed **7/7** twice in a row, in 5.32s and 3.70s; run from
`packages/frontend` the command is
`npx vitest run --config vite.config.ts --coverage.enabled=false src/pages/ChangelogPanel.variants.test.tsx`,
and from the repository root
`npx vitest run --config packages/frontend/vite.config.ts ChangelogPanel.variants`
— `setupFiles` resolves against the config rather than the cwd, so both work.
The whole suite serially was **110 files · 1117 tests · passing · 408.71s**,
with the file taking **654ms** inside that run against **7225ms** inside the
parallel one.

So the honest way to publish the frontend, through 28 September, was **all
green serially, with contention-only failures in the default parallel run in a
file that passes in isolation**. On 30 September it was simply all green, and
on 3 October, run serially, it was again.

#### Why this file, and why the count moves

!!! success "Closed — [issue #199](https://github.com/sgort/ronl-business-api/issues/199), fixed in `afc2001`"
    Opened 24 September 2026 on the evidence below and **closed on
    28 September** by `afc2001`, *"stop the changelog variants test loading the
    real history"*, which reached production with v2026.09.14. The diagnosis
    below is kept as history, because the mechanism is not the one most people
    reach for and the same shape can recur in any test that awaits a lazy
    chunk.

    **What four passes showed was the shape of the symptom.** One failing
    test, then five, then none, then one again — and on 28 September two of the
    three parallel runs of the same suite on the same commit were green. The
    failure was **intermittent and load-dependent**, not the reliable, worsening
    one the 24 September reading suggested: the kind of check CI teaches people
    to re-run rather than read, which is why it was fixed rather than lived
    with.

The mechanism, as diagnosed before the fix:

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
- **The module it waits on keeps growing.** `changelog-data.ts` was
  **572,299 bytes** at v2026.09.9, **612,980** at v2026.09.11 (+7.1%),
  **648,881** at v2026.09.12, and **659,684 bytes** at v2026.09.13 — up
  **46,704 bytes, +7.6%, in the four days** since v2026.09.11. Over the same
  window neither the test nor the component moved at all:
  `git diff --name-status 86af73e 963fe24 -- 'packages/frontend/src/pages/ChangelogPanel*'`
  returns nothing. It has kept growing since: **689,070 bytes** at
  v2026.09.15 and **701,168** at v2026.10.0.

The test did not get worse. The module it waited on got bigger, and the
one-second budget it was measured against did not move — though four passes
showed not a clean upward trend in failures, but an intermittent one whose
count tracked how busy the machine was. The growth was real and monotonic; the
failure count was not.

**The fix was at the file's own boundary, and it stopped the clock rather than
widening the budget.** The issue had carried three candidates: an explicit
`findByRole('dialog', { timeout })` in that file, a package-wide
`configure({ asyncUtilTimeout })` in `src/test/setup.ts`, or decoupling the
test from the real module. `afc2001` took the third, and in doing so corrected
the diagnosis above in one respect. This page had said the file *"already mocks
`./changelog-data`"*; it did, but through `importActual`, spreading the real
module before overriding `changelog`, its only runtime export — so every run
loaded the whole release history inside the `lazy()` import the first
`findByRole` waited on, only to throw the data away. The commit:

- mocks `./changelog-data` **without** `importActual`, so the real history is
  never loaded by this file at all; and
- resolves the lazy `ChangelogPanelContent` chunk once in a `beforeAll`, under
  the hook timeout, so no `findBy*` pays for an import.

By the commit's own measurement the first test dropped from 409–662 ms to
99–125 ms on an idle machine, and it no longer grows with the changelog.
Neither timeout was raised, and parallelism was not touched.

!!! note "Its sibling was left as it is, deliberately"
    `ChangelogPanel.test.tsx` renders every real version entry and does **not**
    fail — but on 28 September it took **44.1 seconds** in the measured parallel
    run, and 30.4s in another run of the same suite on the same commit. It
    passes because `testTimeout` was raised to 20s package-wide and this file
    was given 60s on top of that. `afc2001` left it alone on purpose: it imports
    the data and the content module statically, so its `findBy*` never waits on
    an import, and its real-history rendering is what its own 60s timeout is
    for. It still carries the changelog's growth; its time was not re-measured
    on 30 September or 3 October, because Vitest's console does not print
    per-file times.

This class of failure is not a surprise here; `packages/frontend/vite.config.ts`
already documents it in the comment above `testTimeout: 20000`, which records
the suite as green in five consecutive parallel runs on an idle machine and
producing 8–16 timeout failures under concurrent load, across a file set that
changes with how busy the machine is. `ChangelogPanel.test.tsx` is named in that
same comment as a file needing more headroom still. What that comment does not
cover, and what every one of the variants file's failures was, is the *other*
timeout — the one testing-library owns rather than Vitest.

!!! danger "The fix is not to turn parallelism off"
    Disabling file parallelism globally would make the symptom go away and take
    the signal with it. It diverges local runs from CI, where the gating suites
    still run parallel; it costs real time on every later run — **372.31s against
    133.15s** on this suite alone, as measured on 28 September, and 408.71s
    against 176.97s on 24 September; and flakiness under parallelism is usually a genuine
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
  own blocking CI step. **Re-run on 3 October 2026, for the first time since
  12 September: 1 file · 1 test · passing · `Duration 1.18s`**, with coverage
  off (12 September: 1.04s). Because `vite.config.ts` excludes
  `src/**/*.perf.test.ts`, the frontend's 124 files and 1378 tests above do
  **not** include it, and neither does the repository-wide
  **320 files / 4731 tests** — it is the one test in the repository that has
  to be counted separately.

`ChangelogPanel.test.tsx` was the other casualty of the same contention: its
15-second timeout sufficed in isolation but not inside a full run, where it was
observed taking 22s. `changelog-data.ts` renders every real version entry, so
the test is genuinely slow rather than unreliable — and a timeout exists to
catch a hang, not to assert a speed. It was raised to 60s, which costs no
coverage; the perf spec remains the one place a real budget is asserted. It was
green in the 24 September serial run at **22.66s**, which is the same figure
that prompted the raise and a reminder of how little headroom 15s left.

**On 28 September it took 44.1 seconds** in the measured parallel run, and
30.4s in another parallel run of the same suite on the same commit. That is
double the 24 September figure and three quarters of the 60s ceiling, on a
file whose only input that changed is `changelog-data.ts`. It still passes, and
it is the clearest quantity on this page for how fast that module is growing.
It was not timed on 30 September or 3 October: the suite was run with
Vitest's default console reporter, which prints no per-file times.

Its sibling `ChangelogPanel.variants.test.tsx` is the file that failed under
parallel load on 20 September, five times over on 24 September, not at all on
26 September and once again on 28 September — same component, same growth,
but a different timeout. What it needed was **not** `testTimeout`, which is
what was raised for this file, and it did not get a bigger budget of any kind:
`afc2001` stopped it loading the real history at all, closing
[issue #199](https://github.com/sgort/ronl-business-api/issues/199). See
[Why this file, and why the count moves](#why-this-file-and-why-the-count-moves).

---

## Linting, formatting, git hooks, and CI

All the root gates were run again on **3 October 2026**, at the same tree
as the suites above, and all exited 0, printing what the table shows — the
same output as on 30 September. The timings are from 20 September; later
runs did not record any.

| Command | What it does | Result (measured 3 Oct) |
|---|---|---|
| `npm run lint` | `npm run lint --workspaces --if-present` — `eslint .` in backend, frontend, public-site | exit 0, no errors (68s on 20 Sep) |
| `npm run check-format` | `prettier --check "**/*.{ts,tsx,json,md}" --ignore-path .gitignore --ignore-path .prettierignore` — **one repo-wide glob, not a per-workspace fan-out** | *All matched files use Prettier code style!* (15s on 20 Sep) |
| `npm run lint:openapi --workspace=@ronl/backend` | Builds `openapi/openapi.json`, then `spectral lint` against the NL API Design Rules 2.2.1 ruleset with `--fail-severity error` — new in v2026.09.12 | *No results with a severity of 'error' found!* |
| `npm run check-shared` | `node scripts/check-shared-declarations.mjs` — what stands in for tests in `packages/shared` | `check-shared-declarations: 12 file(s) in packages/shared/src/ — declarations and constant data only.` (11 on 20 Sep) |
| `npm run check-supply-chain` | `node scripts/check-supply-chain.mjs` — every action pin against its version comment and the register | `39 pinned reference(s) across 6 action(s) in .github/workflows/` … `OK — digests, version comments and the register all agree.` (31 across 5 on 20 Sep, before the two workflows added in v2026.09.12) |
| `npm run check-swimlane-fixtures` | `node scripts/check-swimlane-fixtures.mjs` — the parser's RIP fixtures against their fingerprints (see [Git hooks](#git-hooks)) | `✓ 12 swimlane fixtures match their fingerprints; 12 compared against ..\linked-data-explorer.` |

`npm run lint` skips `@ronl/shared` the same way `test` does — no `lint` script
there. `npm run check-format`, by contrast, is **not** scoped by workspace
scripts at all: it is a single Prettier invocation over the whole tree (minus
`.gitignore`d paths), so it reaches `packages/shared` too even though `shared`
defines no format-check script of its own. The second ignore file is new in
v2026.09.14 (`96fabb6`): `.prettierignore` holds one pattern, `*-handoff/`,
keeping design handoff folders — scratch input that is never committed — out
of the check.

!!! note "`packages/shared` has no test script, and that is the design"
    It defines `build`, `prepare`, `clean` and `type-check` and nothing else,
    so `--if-present` skips it. What polices it instead is `check-shared`,
    which asserts that every file under `packages/shared/src/` holds
    declarations and constant data only — no runtime behaviour, hence nothing
    to unit test. It runs in the `audit` job, a required check on both `acc`
    and `main`, so the package with no tests is in fact the one whose rule is
    enforced on every pull request.

### Git hooks

| Hook | Runs | Scope |
|---|---|---|
| `pre-commit` | `npx lint-staged` | Staged files only |
| `pre-push` | `npm run deps:check` → build `@ronl/shared` → **`npm run check-swimlane-fixtures`** → `npm run type-check` → `npm run lint` → `npm run check-format` | All workspaces (type-check, lint) / whole tree (check-format) / the twelve BPMN fixtures (check-swimlane-fixtures) |

!!! important "The hooks do not run the tests"
    Re-read against `.husky/pre-push` at `ae06c9e` on 30 September 2026, and
    `.husky/` is unchanged at `0625d48`, so still true: `pre-commit` runs `npx lint-staged` and nothing else, and
    `pre-push` runs the **six** commands above in that order. Neither invokes
    any `test` script, so nothing client-side stops a push that breaks a suite
    — run `npm test` yourself before pushing anything nontrivial.

    **`check-swimlane-fixtures` is the sixth, and it is third in the order** —
    between the `@ronl/shared` build and the type check. These pages said five
    until 28 September 2026; the step was added without this table following.
    It does not weaken the claim above: it compares
    `packages/backend/src/rip-swimlane/__fixtures__/`'s twelve RIP phase BPMNs
    against sha256 fingerprints committed identically in this repository and in
    linked-data-explorer, and byte-for-byte against the real files when that
    checkout is alongside. A fixture edited here fails it, because the edit
    belongs upstream. That is a file comparison, not a suite. Since
    v2026.09.14 (`97e0534`, #268) the check tells the two directions of drift
    apart from the fingerprint file: a fixture that disagrees with its
    fingerprint is stale and `--sync` fixes it, while one that agrees but
    differs from the linked-data-explorer checkout means *that checkout* is out
    of step — and `--sync` now refuses to copy from it unless `--force` is
    given. The seven Awb fixtures added under
    `__fixtures__/awb/` in the same release are **not** part of it: the check
    matches only the RIP phase files, so those seven are exercised by the
    parser's tests but not drift-checked against linked-data-explorer. The
    same holds for the two fixtures v2026.10.0 added under
    `__fixtures__/declared/` — `GedelegeerdBesluitProcess`, copied
    byte-for-byte from linked-data-explorer, and the HR capacity claim — which
    is why the 3 October run still reports twelve.

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

**Thirteen** workflows under `.github/workflows/`, and v2026.10.0 changed
none of them: `git diff ae06c9e 0625d48 -- .github/` is empty. Re-read at
`ae06c9e` on 30 September against `2443adc`, the last full reading: no
workflow was added or removed, and **no test step changed**. What did change is a
`node scripts/check-og.mjs acceptance|production` check of the built
link-preview tags inside the build step of the four frontend and public-site
deploy workflows, and Node 24.21.0 in `dependency-audit.yml` and `sbom.yml`.
The thirteen are an acc/prod pair per deployable package, the supply-chain
`audit` gate, the Semgrep `scan` job added in v2026.09.7, the promotion
orchestrator added since v2026.09.9, and two added in v2026.09.12: a daily
dependency audit and a release SBOM:

| Workflow | Lint | Type-check | **Tests** | E2E | Perf budget | Build | Deploys? |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| `azure-backend-acc.yml` / `-prod.yml` | ✅ + OpenAPI (`lint:openapi`) | – | **✅**, with the conformance-coverage check | – | – | ✅ | Yes — over OIDC since v2026.09.10, then a liveness check and a check that `/v1/health` reports the deployed commit; the acc workflow skips all three on a pull request |
| `azure-frontend-acc.yml` / `-prod.yml` | ✅ | – | **✅ ×2** — pa-cockpit, then frontend | – | **✅** | ✅ | Yes |
| `azure-pa-demo-acc.yml` / `-prod.yml` | ✅ | ✅ | **✅** | **✅ (acc only)** | – | ✅ | Yes |
| `azure-publicsite-acc.yml` / `-prod.yml` | ✅ | ✅ | **✅** | – | – | ✅ | Yes |
| `promote-to-production.yml` | – | – | – | – | – | – | Orchestrates the four `-prod` workflows in order |
| `zizmor.yml` | – | – | – | – | – | – | No — the required `audit` gate, which since v2026.09.12 also checks that the lockfile matches `package.json` |
| `semgrep.yml` | – | – | – | – | – | – | No — `scan`, required on `acc` and, since the end of September, on `main` |
| `dependency-audit.yml` | – | – | – | – | – | – | No — a daily scheduled audit of the dependency tree, the one check here that runs on a clock rather than a commit |
| `sbom.yml` | – | – | – | – | – | – | No — generates and uploads the release SBOM on a push to `main` |

Neither of the two workflows added in v2026.09.12 is a required check in the
rulesets as last read, on 30 September (see
[What actually gates a merge](#what-actually-gates-a-merge)).

**The backend's contract is now linted before its tests run.** Both backend
workflows gained a *Lint the OpenAPI document* step in v2026.09.12, placed
before *Unit tests* so a document that breaks the NL API Design Rules ruleset
fails fast and names the rule. The checks that the document matches the routes
actually served, and that every documented operation's response was compared
against its schema, are not separate steps: they are
`src/openapi/coverage.test.ts` and the conformance-coverage script that the
backend's ordinary `npm test` runs after Jest — see
[Backend suite](backend.md).

!!! note "The four `-prod.yml` workflows no longer trigger themselves"
    Read at `86af73e` and still so at `2443adc`: all four declare `on: workflow_call` and
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
suite and **its tests ran nowhere in CI** — a suite third in size only to the
backend's and the frontend's (515 tests on 3 October), covered locally and
only locally. Both frontend
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
widened header type. `azure-backend-prod.yml` has no `pull_request` trigger,
deliberately — `main` is promoted from `acc`, where that same suite has already
run.

### What actually gates a merge

**This changed on 19 September 2026, and the two branches are deliberately
different.** Read from the repository rulesets
(`gh api repos/sgort/ronl-business-api/rulesets`) on 20 September 2026, not
re-read on 24, 26 or 28 September, **re-read on 30 September**, and not
re-read on 3 October — a gating claim is only as current as the last time
somebody ran that command:

| Branch | Ruleset | Required status checks |
|---|---|---|
| `acc` | *acc supply-chain gate* | `audit`, `scan`, `build`, `Build and Deploy ACC Frontend`, `Build and Deploy ACC PA Demo`, `Build and Deploy ACC Public Site` |
| `main` | *main promotion gate* | `audit`, `scan` |

The `acc` row is unchanged since 20 September. **`main` now requires `scan` as
well as `audit`**, where the 20 September reading had `audit` alone. Both
rulesets are active, and neither branch carries classic branch protection any
more — `gh api repos/sgort/ronl-business-api/branches/<branch>/protection`
answers *Branch not protected* for both, so the rulesets are the whole of the
gate.

So on `acc` a red suite now **does** block the merge. `build` is
`azure-backend-acc.yml`'s build job, which runs the backend's `npm test`; the
three `Build and Deploy ACC …` contexts are the frontend, pa-demo and
public-site deploy jobs, each of which runs its package's suite — and the
frontend's runs `@ronl/pa-cockpit`'s first. Between them, every one of the five
suites is now a required check on `acc`. `scan` — Semgrep — became required in
the same change; test files remain excluded from its Code scanning, a fixture
credential not being a leaked one. Both rulesets also forbid deletion and
non-fast-forward pushes, and require a pull request to change the branch at all.

!!! note "`main` requiring no suite is not an oversight"
    **No production workflow has a `pull_request` trigger.** A check that never
    runs on the pull request cannot be required of it: adding one would block
    every promotion forever. `main` is promoted from `acc`, where those same
    suites have already run and now also gate. `audit` and `scan` are the two
    workflows that do trigger on any pull request, which is what makes them
    requirable there — and both now are.

    This is now doubly true. Read at `86af73e`, at `2443adc` and again at `ae06c9e`, the four `-prod.yml` files have
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

**The backend workflows deploy too, since v2026.09.10.** Until then they ended
at *Create deployment zip* → *Upload deployment artifact*, and the artifact
was deployed separately, from a developer machine — which is what this
paragraph still said through the 28 September pass, although the change
(`e3c7dd6`, 20 September) was already in the `2443adc` reading above. They now
log in to Azure over OIDC, run `az webapp deploy`, poll `/v1/health/live` for
liveness, and then fail the job unless `/v1/health` reports the commit that was
just deployed as its `build.sha` — a liveness check alone passes against the
previous build while Azure starts the new one. On `azure-backend-acc.yml` all
of that is skipped on a pull request, so `build` can stay a required check
without a pull request shipping anything. See
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
`webServer` and needs only the backend. One thing to settle first: on
3 October its two search-journey tests timed out under six parallel workers
and passed serially (see [E2E & live smoke](e2e.md#public-site-playwright-suite)),
so the 10-second wait for the filter checkbox is the first thing a CI run
would test.

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
files, not new files to reach. The two frontend files v2026.10.0 left below
85% branches — `BesluitOverzichtSection.tsx` at 80.43% and `phaseSet.ts` at
83.33% — are the nearest such targets.

**Deliberately out of scope for now:** visual regression and screenshot
diffing, a cross-browser matrix (Chromium only in both Playwright suites), and
parallel or sharded E2E execution tuning — none are blockers at current suite
size.
