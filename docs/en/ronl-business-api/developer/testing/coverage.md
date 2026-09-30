---
component: RONL Business API
---

# Coverage

Measured on **30 September 2026** against **v2026.09.15**, the release in
production (`main` at `ae06c9e`), in the working checkout on `acc` at
`142d909` — a tree identical to `ae06c9e` — after `npm run deps:check`
reported the install in sync with the lockfile, on **Node 24.14.1 /
npm 11.11.0** (`.nvmrc` names 22.23.2). Each package was measured by its own
`npm test`, run one workspace at a time; all five of those scripts collect
coverage already.

| Package | Statements | Branches | Functions | Lines | Δ branches since v2026.08.36 |
|---|---:|---:|---:|---:|---|
| Backend | 98.90% | 95.14% | 97.98% | 99.20% | **+5.13** |
| Frontend | 95.36% | 93.09% | 91.41% | 95.89% | **+12.76** |
| pa-cockpit | 92.61% | 93.89% | 89.56% | 93.13% | **+18.34** |
| pa-demo | 93.47% | 95.65% | 85.00% | 92.85% | **+8.70** |
| Public site | 96.60% | 97.34% | 95.07% | 97.17% | **+26.95** |

Against the 28 September reading of v2026.09.13, **four of the five packages
rose on every measure they moved on, and none fell**: backend branches
92.57 → 95.14, frontend 89.91 → 93.09, pa-cockpit 88.52 → 93.89, public site
96.31 → 97.34. pa-demo reproduced all four figures to the decimal, and public
site's functions held at 95.07. Most of the branch gain is `391b1a8` and
`73a6764` — the margin work set out below — and the rest is new code arriving
well covered.

!!! info "The repository-wide figure, and why it is not an average of that column"
    Across all five workspaces together: **96.54% statements · 94.13% branches ·
    92.92% functions · 97.01% lines**.

    Those come from **summing the covered and total counts** across the five
    workspaces' coverage reports and dividing once — 13924/14423 statements,
    8984/9544 branches, 3268/3517 functions, 12558/12945 lines — not from
    averaging the five percentages in the table. Averaging the column would
    weight pa-demo's 92 statements exactly as heavily as the backend's 6327 and
    give a repository-wide branch figure of 95.02% instead of 94.13%: nearly a
    point of pure arithmetic error, in the flattering direction. The
    denominators differ by two orders of magnitude here, so the distinction is
    not academic. On 30 September the counts were summed from each workspace's
    `coverage/coverage-final.json`, which every one of the five runs writes;
    each workspace's own total reproduces the table row above exactly.

    All four repository-wide measures rose against the 28 September
    measurement of v2026.09.13 — statements 95.20 → 96.54, branches
    90.94 → 94.13, functions 90.65 → 92.92, lines 95.94 → 97.01 — on a body of
    code that grew by 599 statements and 553 branches. That is the largest
    move since the v2026.09.2 campaign, and for the same reason: a deliberate
    push, this time for margin above the floor rather than for the floor
    itself.

!!! note "Which frontend run the aggregate uses"
    The frontend contributes the figures of its **default parallel** run — the
    one CI makes, and the one every pass since 24 September has used, so the
    four numbers stay comparable across passes. On 30 September that run was
    green, 1318/1318, and no serial run was made.

    On 28 September, when the parallel run carried one contention-only failure,
    the green serial run of the same suite reported slightly *lower* frontend
    coverage — 93.16 / 89.88 / 87.84 / 93.98 against 93.24 / 89.91 / 87.98 /
    94.07, four statements and two functions out of 4971 and 1423. That is v8
    worker-attribution noise, the same phenomenon the *last two decimals*
    warning below describes. Anyone reproducing these figures serially should
    expect a difference of that size.

!!! note "Every package moved, and branches moved most"
    v2026.09.2 extended the backend-only coverage campaign to all five
    workspaces with a test runner, against a **per-file 80% branch floor**:
    53 files were below it, none are now. That is why the branch column moved
    furthest and why public-site — which started lowest at 70.39% — moved most.

    That was unusual and worth noting as a check that the run was sound: the
    pass before it had three packages reproducing their figures to the decimal,
    while in the campaign pass every package gained on every measure — which is
    what a campaign targeting *all* of them should look like. The table above
    is several releases further on. It moved only in decimals until
    v2026.09.14, and then by whole points again on the margin work; what
    changed is set out below.

!!! success "The floor is a gate, and it is per file"
    It used to be a convention held by review, with no threshold configured
    anywhere. v2026.09.6 configured it in **all five** runner configs, and the
    two runners express the same rule differently:

    | Workspace | Config | How the per-file floor is written |
    |---|---|---|
    | `backend` | `jest.config.js` | `coverageThreshold: { './src/**/*.ts': { branches: 80 } }` |
    | `frontend` | `vite.config.ts` | `coverage.thresholds: { branches: 80, perFile: true }` |
    | `pa-cockpit` | `vitest.config.ts` | `coverage.thresholds: { branches: 80, perFile: true }` |
    | `pa-demo` | `vite.config.ts` | `coverage.thresholds: { branches: 80, perFile: true }` |
    | `public-site` | `vite.config.ts` | `coverage.thresholds: { branches: 80, perFile: true }` |

    The Jest form is a **glob key rather than `global`**: Jest applies a glob
    threshold to each matching file individually, which is what makes it a
    per-file floor and not a package average. Vitest needs `perFile: true`
    alongside the number to say the same thing. Get either detail wrong and the
    threshold silently becomes an average, which is the one thing it exists not
    to be.

    A file below the line exits the run non-zero and names that file, locally
    and in CI alike — `npm test` already collects coverage in every workspace,
    so nothing needed a separate coverage job. **All five configurations are
    still in place at `ae06c9e`, and no file was named in any of the five runs
    of this pass**; reading every file entry in the five workspaces' coverage
    reports confirms it independently: **zero of 319 files below 80%
    branches** — 98 in backend, 124 in frontend, 38 in pa-cockpit, 16 in
    pa-demo and 43 in public-site. (Since 28 September the backend gained one
    source file, `openapi/testing/conformance.ts`, and the frontend twelve:
    nine new files in `components/process/`, `StartFailureNotice.tsx`, and
    `CaseworkerDashboardV2/PaletteActions.tsx` with its
    `paletteActionsContext.ts`. `PhaseSwimlane.tsx` moved into
    `components/process/` from `InfraBoardDashboard/` and is not counted as
    new — see the frontend table below.)

    !!! success "Zero below the line — and, since v2026.09.15, none within five points of it"
        On 28 September the margin was thinner than the headline sounded:
        **three files sat at exactly 80.00% branches** —
        `backend/src/media-aggregator/sanitize.ts`,
        `frontend/src/components/CaseworkerDashboardV2/NoAccessPanel.tsx` and
        `pa-cockpit/src/components/PADashboardV2/dossierbeheer/DossierRow.tsx` —
        so one uncovered edge added to any of them would have failed a required
        check. Two commits closed that:

        - **`391b1a8`** (#256, v2026.09.14) covered the remaining arms of all
          three, taking each to **100%**. Its missing-kompas test exposed a
          latent crash in `DossierRow`, fixed in the same commit.
        - **`73a6764`** (v2026.09.15) brought **32 files** that sat between
          80.00 and 85 — 11 in the backend, 13 in the frontend, 6 in
          pa-cockpit, 2 in public-site — to 85 or above, most well past 90.
          `services/edocs.service.ts`, which that commit records at exactly
          80.00% before it, is at 98.67% now.
          It needed one production change: public-site's `lib/api.ts` now
          reads `import.meta.env` directly, so `vi.stubEnv` can reach it, and
          went from 83.78% branches to **97.29%**. The two arms left there
          cannot occur in Node and are tracked in #294.

        Measured on 30 September, the lowest file in each workspace:

        | Workspace | Lowest file by branches | Branches |
        |---|---|---:|
        | backend | `src/pa-monitoring/pa-cache.ts` and `src/services/llm/OpenAILlmProvider.ts` | 86.36 |
        | frontend | `src/components/CaseworkerDashboard/IouFeedbackSection.tsx` | **85.00** |
        | pa-cockpit | `src/services/dossierbeheer.api.ts` | 85.10 |
        | pa-demo | `src/demo/changelog/DemoChangelogPanel.tsx` | 87.50 |
        | public-site | `src/lib/useQueryState.ts` and `src/pages/herkomst/HerkomstTrace.tsx` | 87.50 |

        **85 is a margin, not a floor.** The configs still say 80, and
        `IouFeedbackSection.tsx` sits exactly on the 85 line — 51 of 60
        branches — so whoever touches it next should expect to write a test
        with the change if the margin is to hold.

    Per file is the whole point: against a package average, one file falling to
    40% barely moves 95%, and the regression the floor exists to catch would
    pass. **Branches only is equally deliberate.** Measured the same way on
    30 September, a functions floor at 80 would fail **23 files** — frontend 8,
    pa-cockpit 7, pa-demo 5, public-site 3, backend 0 — so the symmetry is a
    trap for whoever adds `functions: 80` on the assumption that it is free.

    `public-site/src/components/TopBar.tsx` is the example the configs
    themselves reach for, and it still holds: **100% branches, 66.66%
    functions**. The two metrics are not interchangeable, and a file can be
    exemplary on one while failing the other — though note that `TopBar.tsx`
    has no branches at all, so its 100% is the reporter's default for an empty
    denominator rather than anything a test achieved.

    See [Coverage Floor](../../../contributing/coverage-floor.md).

!!! note "The configs' own comments say 26 — corrected on 28 September, and already three high"
    Through v2026.09.13 all five runner configs claimed a functions floor would
    fail 31 files, a figure the reports had contradicted on 20, 24, 26 and
    28 September, which each measured 26. `391b1a8` (v2026.09.14) corrected the
    comments to **26** and dated the measurement 28 September. Measured again
    on 30 September the figure is **23**:

    | Workspace | Comment until v2026.09.13 | Comment since `391b1a8` | Measured, 30 Sep |
    |---|---:|---:|---:|
    | `frontend` | 11 | 10 | **8** |
    | `pa-cockpit` | 10 | 8 | **7** |
    | `pa-demo` | 7 | 5 | **5** |
    | `public-site` | 3 | 3 | **3** |
    | `backend` | 0 | 0 | **0** |
    | **Total** | **31** | **26** | **23** |

    This time the comments are not wrong so much as dated: each says when it
    was measured, which is the fix that matters, since a count like this moves
    with every release that touches a container. Where the two disagree,
    re-run the suites rather than trusting either.

    The 23 are concentrated where the largest containers live: in the
    frontend, the four board page containers (`CaseworkerDashboardV2`,
    `Dashboard`, `InfraBoardDashboard`, `WooDashboard`), three
    `CaseworkerDashboard` sections and `RegelSimulatie` at 60%; in pa-cockpit,
    `PADashboardV2`, `Dossierbeheer`, `MdEditor`, `Vandaag`, `pa.data`,
    `CuratieSpecSection` and `ZoekcriteriaSection`; in pa-demo, `App.tsx` and
    four shims, two of which — the dock stand-in and the session-expiry
    warning — render `null` by design; and in public-site,
    `TopBar`, `Herkomst` and `Results`. The backend has none.

!!! note "The frontend row is not comparable to v2026.08.23"
    The Public Affairs cockpit was extracted into `packages/pa-cockpit` in this
    window, taking 41 test files and 368 tests with it. The frontend percentage
    is therefore measured over a **different, smaller** body of code than the
    87.47% recorded last time — it did not simply improve. Read the frontend and
    pa-cockpit rows together.

**pa-demo's jump is the vendored fork leaving**, not a testing campaign. Its
figures previously spanned a byte-identical copy of the cockpit with
`src/vendor/**` excluded by hand; the fork was deleted in v2026.08.28 and the
package is now a thin host adapter over `@ronl/pa-cockpit`. There is nothing
left to exclude — see [pa-demo by area](#pa-demo-by-area) below.

**What moved in v2026.09.14 and v2026.09.15** — measured 30 September, against
the 28 September reading of v2026.09.13; v2026.09.14 was not measured on its
own. `git diff --name-status 963fe24 ae06c9e -- 'packages/*/src/**'` is the
whole window.

- **Backend: +1 file, +168 tests, 2202 → 2370.** Package figures: statements
  98.49 → **98.90**, branches 92.57 → **95.14**, functions 97.51 → **97.98**,
  lines 98.89 → **99.20**. The new file is the conformance helper's own test;
  the branch gain is mostly the margin work in `routes/`, `services/`,
  `auth/` and `mcp-servers/lde` — see [Backend by area](#backend-by-area).
- **Frontend: +10 files, +196 tests, 1122 → 1318**, and twelve new source
  files, nine of them the caseworker's process view. Package figures:
  93.24 → **95.36**, 89.91 → **93.09**, 87.98 → **91.41**,
  94.07 → **95.89**. The new code arrived well covered —
  `components/process/` at 99.56% statements and 91.96% branches — and
  `73a6764` lifted `CaseworkerDashboard/` and `src/pages` by several points
  each.
- **pa-cockpit: no new file, +39 tests, 476 → 515**, all from the two
  margin commits. Package figures: 90.07 → **92.61**, 88.52 → **93.89**,
  86.39 → **89.56**, 91.33 → **93.13** — the largest branch gain of the five.
- **Public site: +1 file, +30 tests, 235 → 265** — the new
  `indexHtml.test.ts` for the link-preview tags (23) and the rest in
  `prerender.test.ts`, `lib/api.test.ts` and `Footer.test.tsx`. Package
  figures: 95.92 → **96.60**, 96.31 → **97.34**, functions unchanged at
  95.07, 96.41 → **97.17**, all of the movement in `src/lib`.
- **pa-demo reproduced all four package figures and every per-area row to the
  decimal**, for the seventh release running.

**What moved in v2026.09.13**, measured 28 September against the 26 September
reading of v2026.09.12, for the record: the backend +4 tests in existing
files, the frontend +5 and one new source file, pa-demo and the public site
unchanged to the decimal, and pa-cockpit moving in the second decimal on
statements and functions with **no `src/` change and no test change at all** —
the nondeterminism this page warns about below, caught in the cleanest
possible conditions.

Two windows further back, for the record: 24 → 26 September was the backend
alone, 89 → 96 files and 2072 → 2198 tests, the seven new files covering six new
source modules all at 100 on all four measures. 20 → 24 September took the
backend 86 → 89 files and 2028 → 2072 tests on `root.routes`, `build-info` and
`cors-origin`; the public site gained four tests in `Detail.test.tsx`, the
frontend three in `infra-board.data.test.ts`.

!!! warning "The last two decimals are noise"
    Frontend coverage is **not deterministic**. Six runs at the same commit,
    with no source change between them, produced 87.34% twice and 87.47% four
    times — the same 6789-statement denominator, nine statements apart.
    Clearing the Vite cache changed nothing. Treat a mismatch in the second
    decimal as expected rather than as something to chase; a difference of a
    whole point is worth investigating.

    The backend has a different sensitivity: its figures depend on the
    invocation. `npm test --workspace=@ronl/backend` is the command these
    numbers come from.

All five configure `collectCoverageFrom` / `coverage.include` to span the whole
`src` tree rather than only the files a test happens to import, so an untested
file shows as 0% instead of silently disappearing from the report. pa-demo no
longer needs a `src/vendor/**` exclusion, because there is no vendored tree left
to exclude — see [pa-demo by area](#pa-demo-by-area).

**What the headline numbers mean here.** Backend, frontend and public site have
been through a dedicated coverage campaign that closed *breadth* gaps
deliberately — every backend feature area, every frontend component and page,
and every public-site module now has at least a test file. What remains there is
*depth*. pa-cockpit inherits the frontend's profile, since it *is* the code that
used to be measured there. pa-demo is the outlier in the other direction (see
[pa-demo by area](#pa-demo-by-area)):

| Package | Statements → branches | Gap | Was, v2026.08.36 |
|---|---|---:|---:|
| Backend | 98.90 → 95.14 | 3.8 | 7.5 |
| Frontend | 95.36 → 93.09 | 2.3 | 8.0 |
| pa-cockpit | 92.61 → 93.89 | **−1.3** | 10.6 |
| pa-demo | 93.47 → 95.65 | **−2.2** | 4.4 |
| Public site | 96.60 → 97.34 | **−0.7** | 16.4 |

Every gap narrowed, and three have gone **negative** — branches now sit above
statements, pa-cockpit joining pa-demo and the public site on 30 September.
That is what a campaign aimed at branch edges produces once it reaches the
guards inside files whose plain statements nobody had a reason to execute. The
public site, whose 16.4-point gap was the widest in the repository at
v2026.08.36, is one of the three. pa-demo's position is a property of what it
became rather than of effort spent: a thin host adapter over a package that
carries its own tests. What is left elsewhere is the same kind of thing:
defensive `if (!req.user)` guards behind real middleware, `?? null` fallbacks,
catch blocks unreachable through a legal input, and deliberately-scoped
"critical interactions only" passes on the largest components — documented
per-file rather than silently absent.

---

## Backend by area

Sub-directories report separately rather than rolling up into their parent, and
istanbul truncates to two decimals rather than rounding. Match these against
`npm test --workspace=@ronl/backend -- --coverageReporters=text`.

**Re-derived on 30 September 2026** from the run's own coverage report, grouped
per directory the way istanbul's text reporter groups them and truncated to two
decimals the same way — and checked against that text table, which the run
printed and which every row below matches. The rows reconcile to the package
total in the table at the top of this page, which is the check that they are
current.

| Area | Files | Statements | Branches | Functions | Lines |
|---|---:|---:|---:|---:|---:|
| `auth` | 2 | 100 | 100 | 100 | 100 |
| `mcp-servers/edocs` | 1 | 100 | 100 | 100 | 100 |
| `openapi` | 1 | 100 | 100 | 100 | 100 |
| `openapi/testing` | 2 | 100 | 100 | 100 | 100 |
| `services/document` | 4 | 100 | 100 | 100 | 100 |
| `rip-swimlane` | 2 | 100 | 99.12 | 100 | 100 |
| `middleware` | 3 | 100 | 95.83 | 92.85 | 100 |
| `mcp-servers/triplydb` | 1 | 100 | 90.9 | 100 | 100 |
| `routes` | 18 | 99.34 | 98.26 | 100 | 99.31 |
| `services/llm` | 4 | 99.02 | 92.3 | 100 | 98.95 |
| `services` | 15 | 99 | 95.61 | 98.51 | 99.27 |
| `pa-monitoring` | 10 | 98.95 | 89.35 | 95.93 | 99.16 |
| `utils` | 12 | 98.82 | 98.76 | 100 | 98.66 |
| `pa-monitoring/sources` | 6 | 98.13 | 93.05 | 94.52 | 99.13 |
| `mcp-servers/lde` | 1 | 98.03 | 100 | 100 | 97.95 |
| `media-aggregator` | 10 | 97.57 | 93.37 | 100 | 98.61 |
| `services/mcp` | 6 | 96.33 | 100 | 93.9 | 97.84 |

**Nine rows moved between v2026.09.13 and v2026.09.15, and eight are unchanged
to the decimal.** The biggest moves are the margin work: **`auth`** from
90.74 / 88.63 / 90.9 / 91.91 to **100 on all four**, `jwt.middleware.ts`
reaching 100 alongside `tenant-access.ts`; **`mcp-servers/lde`** from 82.14%
branches to **100**; **`routes`** 94.6 → **98.26** branches; **`services`**
91.79 → **95.61** branches, `edocs.service.ts`, `lde.service.ts` and
`search.service.ts` above all. **`rip-swimlane`** reached 100 statements,
functions and lines, and 99.12 branches, while its parser grew to read any
laned process. **`openapi/testing`** gained `conformance.ts` at 100 on all
four. `pa-monitoring`, `pa-monitoring/sources` and `media-aggregator` each
moved by about a point on branches. `media-aggregator/sanitize.ts`, one of
the three files at exactly 80.00% on 28 September, is at 100% branches.

The v2026.09.13 window, before that: two rows moved in the second decimal —
`rip-swimlane` on `bpmn-swimlane.ts` reading a list of document references
instead of one, and `services/` on `operaton.service.ts`, where three caches
keyed by process-definition *key* became one keyed by definition *id*.

The v2026.09.12 window, which this table also absorbed: **`openapi`** and
**`openapi/testing`** — `document.ts` and `routeOperations.ts` — arrived at 100
across the board; **`auth/`** gained `tenant-access.ts` at 100 and rose on every
measure; **`middleware/`** gained `version.middleware.ts` at 100, its branch and
function figures moving a fraction (95.91 → 95.83, 92.3 → 92.85) on the larger
denominator; **`routes/`** gained `openapi.routes.ts` and `registry.ts`, both at
100.

!!! success "`utils/` is no longer the exception"
    Through v2026.08.20 this table's lowest row by a wide margin was `utils/`
    at 43.47% statements and **6.54% branches**, documented as an accepted
    artifact: `config.ts` sat at 0% because it self-runs `dotenv` and
    `validateConfig` on import, and `logger.ts` was mocked in every test that
    touched it.

    Both are closed. Of the twelve source files in `utils/` on 30 September,
    **eleven report 100 / 100 / 100 / 100** — `altcha`, `build-info`,
    `client-ip`, `cors-origin`, `dutch-datetime`, `env`, `errors`, `logger`,
    `operaton-variables`, `slug`, `tls-bootstrap`. The twelfth is `config.ts` at
    95.12% statements and **98.31% branches**, which is what pulls the area row
    off 100 and is comfortably the largest branch surface in the area.
    `tls-bootstrap.ts` was also at 0% and is now fully covered. The area that
    was the standing excuse is now the joint-best large area in the package, and
    the one that grew most in v2026.09.11.

`auth/` was the lowest row on statements, functions and lines through the
28 September pass. Through v2026.09.11 it was `jwt.middleware.ts` alone, at
88.23% statements and **82.75% branches**; v2026.09.12 added `tenant-access.ts`
at 100 on all four, lifting the row to 90.74% statements and 88.63% branches;
and `73a6764` took `jwt.middleware.ts` itself to 100, so the row now reads
**100 on all four**. The lowest rows are now `services/mcp` on statements and
lines (96.33% and 97.84%), `middleware` on functions (92.85%), and
`pa-monitoring` on branches at **89.35%** — more than nine points clear of the
floor. At file level the closest are `pa-monitoring/pa-cache.ts` and
`services/llm/OpenAILlmProvider.ts`, both at **86.36%** branches.

---

## Frontend by area

**Re-derived on 30 September 2026**, from the default parallel run — the one
the package total uses, for the reason given in *Which frontend run the
aggregate uses* at the top of this page. The rows reconcile to the
95.36 / 93.09 / 91.41 / 95.89 package total above. Vitest's text table omits
fully covered files, so the rows are grouped from the run's
`coverage-final.json`; every row the text table does print matches.

**Eight rows moved, one is new and eleven reproduced to the decimal.**
`src/components/process` is new — ten source files, nine of them new and
`PhaseSwimlane.tsx` moved in from `InfraBoardDashboard`, which drops from 13
files to 12. `src/components` gains `StartFailureNotice.tsx` (6 → **7**) and
`CaseworkerDashboardV2` gains `PaletteActions.tsx` and its context (8 →
**10**). The biggest moves are `73a6764`'s: `CaseworkerDashboard` 89.33 →
**94.93** branches, `src/pages` 87.42 → **94.77** branches and 73.17 →
**78.68** functions, and `src/pages/woo` 84.12 → **100** branches.

| Area | Files | Statements | Branches | Functions | Lines |
|---|---:|---:|---:|---:|---:|
| `src/` (root files) | 1 | 100 | 100 | 100 | 100 |
| `src/components/…/regelsimulatie/__helpers__` | 1 | 100 | 100 | 100 | 100 |
| `src/components/LoginChoice` | 2 | 100 | 100 | 100 | 100 |
| `src/components/PADashboardV2` | 2 | 100 | 100 | 100 | 100 |
| `src/hooks` | 1 | 100 | 100 | 100 | 100 |
| `src/pages/caseworker-v2` | 1 | 100 | 100 | 100 | 100 |
| `src/pages/login-choice` | 1 | 100 | 100 | 100 | 100 |
| `src/types` | 1 | 100 | 100 | 100 | 100 |
| `src/utils` | 2 | 100 | 100 | 100 | 100 |
| `src/pages/infra-board` | 6 | 100 | 98.47 | 100 | 100 |
| `src/components/process` | 10 | 99.56 | 91.96 | 100 | 99.73 |
| `src/pages/woo` | 2 | 99.13 | 100 | 100 | 99 |
| `src/components/…/regelsimulatie` | 8 | 98.33 | 88.59 | 96.38 | 98.89 |
| `src/components/WooDashboard` | 12 | 98.26 | 94.78 | 98.52 | 98.57 |
| `src/services` | 8 | 97.81 | 90.82 | 97.32 | 97.97 |
| `src/components` | 7 | 97.65 | 93.47 | 98.3 | 100 |
| `src/components/InfraBoardDashboard` | 12 | 95.06 | 89.37 | 93.71 | 96.14 |
| `src/components/CaseworkerDashboard` | 26 | 93.83 | 94.93 | 89.94 | 94.73 |
| `src/components/CaseworkerDashboardV2` | 10 | 93.03 | 93.1 | 84.66 | 93.59 |
| `src/pages` | 11 | 87.56 | 94.77 | 78.68 | 87.76 |

!!! note "This table no longer carries the cockpit's rows"
    Earlier versions listed `src/pages/public-affairs-v2`,
    `src/components/PADashboardV2/dossierbeheer` and a large
    `src/components/PADashboardV2` here. Those directories live in
    **`packages/pa-cockpit`** since the extraction and are measured by that
    package's own suite — see [pa-cockpit by area](#pa-cockpit-by-area) below.
    The two-file `src/components/PADashboardV2` that remains in the frontend is
    what stayed behind, and it is at 100.

    The other reason the shape changed: several areas that were middling are
    now at 100, and the old `src/utils` row of 66.66% statements / 50% branches
    is gone entirely. Nothing in the frontend is below the 80% branch floor.

`src/pages` is the lowest of the top-level areas because it is where the
largest containers live — and at 78.68% functions it holds four of the eight
frontend files that a functions floor would fail. Its branches, at 94.77%, are
well clear of the floor; this is a functions gap, not a branch gap. Per-board detail is on the board
pages: [Caseworker](dashboards/caseworker.md),
[PA cockpit](dashboards/pa-cockpit.md),
[Infra-board](dashboards/infra-board.md),
[Woo-dashboard](dashboards/woo-dashboard.md).

---

## pa-cockpit by area

**Re-derived on 30 September 2026.** These rows reconcile to the 92.61 / 93.89 /
89.56 / 93.13 package total above. The package's only changes since
28 September are tests — `391b1a8`'s four in `DossierRow.test.tsx` and
`73a6764`'s 35 across six files — plus the small `DossierRow.tsx` fix the
first of them exposed, so nearly everything that moved below moved on new
assertions against unchanged code.

| Area | Files | Statements | Branches | Functions | Lines |
|---|---:|---:|---:|---:|---:|
| `src/` (root files) | 2 | 100 | 100 | 100 | 100 |
| `src/services` | 3 | 95.97 | 93.99 | 98.19 | 95.28 |
| `src/modes` | 1 | 95.65 | 100 | 100 | 95 |
| `src/pages/public-affairs-v2` | 13 | 94.73 | 95.04 | 92.55 | 95.53 |
| `src/components/PADashboardV2` | 10 | 92.12 | 91.78 | 86.98 | 93.73 |
| `src/pages` | 1 | 86.87 | 95.57 | 79.03 | 86.76 |
| `src/components/PADashboardV2/dossierbeheer` | 8 | 85.47 | 92.88 | 81.35 | 86.29 |

**Four rows moved and three are identical to 28 September.**
`src/pages/public-affairs-v2` moved most — 88.2 → **95.04** branches, 86.4 →
**92.55** functions — on the 16 new `Monitoring.test.tsx` cases; `src/services`
84.98 → **93.99** branches on 13 new cases in `pa.api.test.ts`;
`dossierbeheer` 89.12 → **92.88** branches, `DossierRow.tsx` now at 100; and
`src/components/PADashboardV2` 89.44 → **91.78**. The 28 September reading had
the second-decimal wobble this page warns about — statements and functions
alternating on identical code — which is why a move that small would not be
worth a sentence, and why these are.

`dossierbeheer` is still the lowest area on statements and functions, but at
92.88% branches it clears the floor by nearly thirteen points — the same
pattern as the frontend's `src/pages`. This package holds 7 of the 23 files
that an 80% functions floor would fail.

---

## Public site by area

**Re-derived on 30 September 2026.** These rows reconcile to the 96.60 / 97.34 /
95.07 / 97.17 package total above. **Five of the six are identical to 24, 26
and 28 September**; the sixth, `src/lib`, moved on the one production change
`73a6764` made anywhere: `lib/api.ts` now reads `import.meta.env` directly, so
its base-URL fallbacks can be tested with `vi.stubEnv`, and three new tests do.

| Area | Files | Statements | Branches | Functions | Lines |
|---|---:|---:|---:|---:|---:|
| `src/` (root files) | 1 | 100 | 100 | 100 | 100 |
| `src/i18n` | 3 | 100 | 100 | 100 | 100 |
| `src/pages/herkomst` | 8 | 100 | 97.05 | 100 | 100 |
| `src/components` | 13 | 97.14 | 100 | 96.29 | 97.05 |
| `src/lib` | 8 | 96.49 | 96.66 | 97.36 | 97.87 |
| `src/pages` | 10 | 95.45 | 97.29 | 92 | 95.83 |

`src/lib` went 93.85 → **96.49** statements, 91.11 → **96.66** branches and
94.68 → **97.87** lines, functions unchanged. `lib/api.ts` itself went from
83.78% branches — the lowest file in the package from v2026.09.11 to
v2026.09.13 — to **97.29%**; the two arms left cannot occur in Node and are
tracked in #294. The lowest files by branches are now `lib/useQueryState.ts`
and `pages/herkomst/HerkomstTrace.tsx`, both at 87.50%.

The new `src/indexHtml.test.ts` adds no row: it tests `index.html`'s
link-preview tags, filled from each mode's `.env` file, and `index.html` is
not a source file under coverage.

!!! success "The pre-campaign rows are gone, and the difference is the point"
    This table used to carry three rows derived on 22 August 2026 —
    `src/components` 96.77, `src/lib` 84.9 / **73.17 branches**, `src/pages` 82 /
    **61.51 branches** — which sat visibly below a package total of 96.41% and
    carried a warning saying so. They are now re-measured: `src/lib` branches
    have gone **73.17 → 96.66**, and `src/pages` branches **61.51 → 97.29**.
    Nothing in the package is below the 80% branch floor, and `src/components`
    is at 100% branches outright.

    The whole-tree `src/pages` row covers the ten files directly in that
    directory; the eight-file `herkomst/` provenance explorer reports as its own
    row, at 100% statements.

See [Public site suite](public-site.md) for what these files are and what is
deliberately not covered.

---

## pa-demo by area

**Re-derived on 30 September 2026**, and every row below reconciles to the
**All files** row rather than predating it. All five rows reproduced to the
decimal against 24, 26 and 28 September, on a package whose `src/` tree has
not changed since v2026.09.5.

| Area | Files | Statements | Branches | Functions | Lines |
|---|---:|---:|---:|---:|---:|
| **All files** | **16** | **93.47** | **95.65** | **85.00** | **92.85** |
| `src/demo` | 8 | 100 | 100 | 100 | 100 |
| `src/demo/changelog` | 2 | 100 | 87.50 | 100 | 100 |
| `src/` (root) | 2 | 75.00 | 100 | 50.00 | 75.00 |
| `src/demo/shims` | 4 | 75.00 | 100 | 44.44 | 75.00 |

!!! note "`src/demo` reached 100 across the board"
    The rows that used to sit here were derived on 30 August and did not sum to
    the total — v2026.09.2's campaign had added tests across the package after
    they were taken. Re-measured, `src/demo` is at **100 / 100 / 100 / 100**
    where it previously read 95.91 / 84.61, and the package's remaining gaps are
    entirely in the two rows at 75%, both of which are at **100% branches**.
    This package contributes 5 of the 23 files an 80% functions floor would
    fail, and none at all to a branch floor.

**The `src/vendor/**` exclusion is gone, because the vendored tree is.** Until
v2026.08.28 this package held a byte-identical copy of the cockpit — 39 files
kept honest by a manifest, a sync script and a drift checker — which had to be
excluded from these figures to avoid double-counting code the frontend suite
already exercised. The extraction into
[`@ronl/pa-cockpit`](../pa-cockpit-package.md) deleted the fork and all of that
machinery, so every figure above is now pa-demo's own demo-owned surface and
nothing else. That is the whole reason the package total jumped from 73.94% to
91.30% without a single test being written for that purpose.

What remains uncovered is almost entirely **shims that deliberately return
nothing**: the dock stand-in and the session-expiry warning both render `null`
by design, because the real components pull in chat machinery and session
handling that a public, unauthenticated page must not have. They depress the
function percentage without representing a gap.

Two more files are excluded from coverage entirely, by config rather than by
this table's rounding: `src/main.tsx` (it calls `createRoot`; its one
meaningful line, `forceMockMode()`, is tested separately via the extracted,
fully-covered `src/main-helpers.ts`) and `src/vite-env.d.ts` (a type-only
ambient declaration file, nothing to execute). The `src/` row above is just
these two remaining root files, `App.tsx` and `main-helpers.ts` — 100% on
`main-helpers.ts` (3/3 statements) pulled down by 0% on `App.tsx` (0/1) gives
the row's 75%. `App.tsx` is the lowest-covered file in the package — its one
statement, the route shell itself, has no test rendering it.
