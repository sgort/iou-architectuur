---
component: RONL Business API
---

# Coverage

Measured on **3 October 2026** against **v2026.10.0**, the release in
production (`main` at `0625d48`), in the working checkout on `acc` at
`0e3eed8` — a tree identical to `0625d48` — after `npm run deps:check`
reported the install in sync with the lockfile, on **Node 22.23.2**, the
version `.nvmrc` names. Each package was measured by its own
`npm run test:serial`, run one workspace at a time; all five of those scripts
collect coverage, as their `npm test` counterparts do. Every figure on this
page is read from those runs' coverage tables and from the
`coverage/coverage-final.json` each of them wrote.

| Package | Statements | Branches | Functions | Lines | Δ branches since v2026.08.36 |
|---|---:|---:|---:|---:|---|
| Backend | 98.91% | 95.21% | 97.92% | 99.18% | **+5.20** |
| Frontend | 95.23% | 93.02% | 91.21% | 95.76% | **+12.69** |
| pa-cockpit | 92.61% | 93.89% | 89.56% | 93.13% | **+18.34** |
| pa-demo | 93.47% | 95.65% | 85.00% | 92.85% | **+8.70** |
| Public site | 96.68% | 97.40% | 95.09% | 97.23% | **+27.01** |

Against the 30 September reading of v2026.09.15, **pa-cockpit and pa-demo
reproduced all four figures to the decimal**, on packages v2026.10.0 did not
touch; the **public site rose on all four**, on `lib/problem.ts` arriving at
100; the **backend** moved in the second decimal, branches 95.14 → 95.21; and
the **frontend fell by a tenth or two on every measure** — 95.36 → 95.23,
93.09 → 93.02, 91.41 → 91.21, 95.89 → 95.76. That last is mostly new code
arriving less than fully covered — `BesluitOverzichtSection.tsx` at 80.43%
branches and `BesluitStartSection.tsx` at 66.66% functions above all — and
partly a change of run, set out in the next note.

!!! info "The repository-wide figure, and why it is not an average of that column"
    Across all five workspaces together: **96.51% statements · 94.13% branches ·
    92.83% functions · 96.97% lines**.

    Those come from **summing the covered and total counts** across the five
    workspaces' coverage reports and dividing once — 14204/14717 statements,
    9195/9768 branches, 3316/3572 functions, 12837/13238 lines — not from
    averaging the five percentages in the table. Averaging the column would
    weight pa-demo's 92 statements exactly as heavily as the backend's 6481 and
    give a repository-wide branch figure of 95.03% instead of 94.13%: nearly a
    point of pure arithmetic error, in the flattering direction. The
    denominators differ by two orders of magnitude here, so the distinction is
    not academic. On 3 October the counts were summed from each workspace's
    `coverage/coverage-final.json`, which every one of the five runs writes;
    each workspace's own total reproduces the table row above exactly, and the
    four Vitest totals match the covered/total counts in the run's own
    *Coverage summary* block.

    Against the 30 September measurement of v2026.09.15 the repository-wide
    figures held or moved in the second decimal — statements 96.54 → 96.51,
    branches 94.13 → 94.13, functions 92.92 → 92.83, lines 97.01 → 96.97 — on
    a body of code that grew by 294 statements and 224 branches. That is the
    shape of a feature release: new code arriving roughly as well covered as
    the old.

!!! note "Which frontend run the aggregate uses — and why 3 October is not quite like for like"
    Every pass from 24 to 30 September took the frontend's figures from its
    **default parallel** run, the one CI makes. **The 3 October pass ran every
    workspace with `test:serial`**, the frontend included, so its frontend row
    comes from a serial run. Serial and parallel runs of the same code do not
    report identical v8 coverage.

    The size of that effect is on record. On 28 September, when the parallel
    run carried one contention-only failure, the green serial run of the same
    suite reported slightly *lower* frontend coverage — 93.16 / 89.88 / 87.84 /
    93.98 against 93.24 / 89.91 / 87.98 / 94.07, four statements and two
    functions out of 4971 and 1423. That is v8 worker-attribution noise, the
    same phenomenon the *last two decimals* warning below describes. So part
    of the frontend's tenth-of-a-point fall is the change of run, not the
    code, and a frontend difference of that size against 30 September should
    not be read as a regression. The backend's figures have a sensitivity of
    their own — see that warning.

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
    v2026.09.14, then by whole points again on the margin work, and in
    v2026.10.0 by decimals once more; what changed is set out below.

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
    unchanged at `0625d48`, and no file was named in any of the five runs of
    this pass**; reading every file entry in the five workspaces' coverage
    reports confirms it independently: **zero of 327 files below 80%
    branches** — 101 in backend, 128 in frontend, 38 in pa-cockpit, 16 in
    pa-demo and 44 in public-site. (Since 30 September the backend gained three
    source files, `middleware/error.middleware.ts`, `utils/problem.ts` and
    `routes/besluitvorming.routes.ts`, all at 100 on all four measures; the
    frontend four, `CaseworkerDashboard/BesluitOverzichtSection.tsx` and
    `BesluitStartSection.tsx`, `components/signing/useTaskSignature.ts` and
    `utils/problem.ts`; and the public site one, `lib/problem.ts`.
    `SigningPanel.tsx` and `resolveSigningUrl.ts` moved from
    `InfraBoardDashboard/` to `components/signing/` and are not counted as new,
    and in `components/process/` `phaseSet.ts` took the place of
    `awbStepper.ts` — see the frontend table below.)

    !!! warning "Zero below the line — but since v2026.10.0, two frontend files within five points of it"
        On 30 September every file in the repository cleared 85% branches.
        On 3 October two do not, both new or rewritten in this release and
        both in the frontend:

        | File | Branches | |
        |---|---:|---|
        | `components/CaseworkerDashboard/BesluitOverzichtSection.tsx` | **80.43** (37/46) | New: the *Lopende* and *Afgeronde besluiten* list. One more uncovered branch fails the gate |
        | `components/process/phaseSet.ts` | 83.33 (10/12) | New in place of `awbStepper.ts`: the phase set a process declares, or the Awb set |

        **85 is a margin, not a floor**, and v2026.10.0 is the first release
        since the margin was reached to arrive below it. The two are the
        obvious next targets; `BesluitOverzichtSection.tsx` is the urgent one,
        because the next uncovered edge added to it fails a required check.

        History. On 28 September the margin was thinner than the headline sounded:
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
          80.00% before it, read 98.67% on 30 September.
          It needed one production change: public-site's `lib/api.ts` now
          reads `import.meta.env` directly, so `vi.stubEnv` can reach it, and
          went from 83.78% branches to **97.29%** (96.55% on 3 October, after
          v2026.10.0 taught it to read a problem's `detail`). The arms left
          there cannot occur in Node and are tracked in #294.

        Measured on 3 October, the lowest file in each workspace:

        | Workspace | Lowest file by branches | Branches |
        |---|---|---:|
        | backend | `src/pa-monitoring/pa-cache.ts` and `src/services/llm/OpenAILlmProvider.ts` | 86.36 |
        | frontend | `src/components/CaseworkerDashboard/BesluitOverzichtSection.tsx` | **80.43** |
        | pa-cockpit | `src/services/dossierbeheer.api.ts` | 85.10 |
        | pa-demo | `src/demo/changelog/DemoChangelogPanel.tsx` | 87.50 |
        | public-site | `src/lib/useQueryState.ts` and `src/pages/herkomst/HerkomstTrace.tsx` | 87.50 |

        Four of the five are as on 30 September. `IouFeedbackSection.tsx`,
        which then sat exactly on the 85 line at 51 of 60 branches, now reads
        86.21% — 50 of 58, after a change in this release that came with a
        test.

    Per file is the whole point: against a package average, one file falling to
    40% barely moves 95%, and the regression the floor exists to catch would
    pass. **Branches only is equally deliberate.** Measured the same way on
    3 October, a functions floor at 80 would fail **24 files** — frontend 9,
    pa-cockpit 7, pa-demo 5, public-site 3, backend 0 — so the symmetry is a
    trap for whoever adds `functions: 80` on the assumption that it is free.

    `public-site/src/components/TopBar.tsx` is the example the configs
    themselves reach for, and it still holds: **100% branches, 66.66%
    functions**. The two metrics are not interchangeable, and a file can be
    exemplary on one while failing the other — though note that `TopBar.tsx`
    has no branches at all, so its 100% is the reporter's default for an empty
    denominator rather than anything a test achieved.

    See [Coverage Floor](../../../contributing/coverage-floor.md).

!!! note "The configs' own comments say 26 — corrected on 28 September, and two high on 3 October"
    Through v2026.09.13 all five runner configs claimed a functions floor would
    fail 31 files, a figure the reports had contradicted on 20, 24, 26 and
    28 September, which each measured 26. `391b1a8` (v2026.09.14) corrected the
    comments to **26** and dated the measurement 28 September. Measured since,
    the figure was **23** on 30 September and is **24** on 3 October:

    | Workspace | Comment until v2026.09.13 | Comment since `391b1a8` | Measured, 30 Sep | Measured, 3 Oct |
    |---|---:|---:|---:|---:|
    | `frontend` | 11 | 10 | 8 | **9** |
    | `pa-cockpit` | 10 | 8 | 7 | **7** |
    | `pa-demo` | 7 | 5 | 5 | **5** |
    | `public-site` | 3 | 3 | 3 | **3** |
    | `backend` | 0 | 0 | 0 | **0** |
    | **Total** | **31** | **26** | **23** | **24** |

    The comments are not wrong so much as dated: each says when it was
    measured, which is the fix that matters, since a count like this moves
    with every release that touches a container — v2026.10.0 added one,
    `BesluitStartSection.tsx` at 2 of 3 functions. Where the two disagree,
    re-run the suites rather than trusting either.

    The 24 are concentrated where the largest containers live: in the
    frontend, the four board page containers (`CaseworkerDashboardV2`,
    `Dashboard`, `InfraBoardDashboard`, `WooDashboard`), four
    `CaseworkerDashboard` sections — `BesluitStartSection`, `DvtpTakenSection`,
    `IouFeedbackSection` and `IouGebruiksscenarioSection` — and
    `RegelSimulatie` at 60%; in pa-cockpit,
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

**What moved in v2026.10.0** — measured 3 October, against the 30 September
reading of v2026.09.15. `git diff --name-status ae06c9e 0625d48 --
'packages/*/src/**'` is the whole window.

- **Backend: +3 files, +87 tests, 2370 → 2457.** Package figures:
  statements 98.90 → **98.91**, branches 95.14 → **95.21**, functions
  97.98 → **97.92**, lines 99.20 → **99.18**. The three new source files —
  `middleware/error.middleware.ts`, `utils/problem.ts` and
  `routes/besluitvorming.routes.ts` — arrived at 100 on all four measures;
  `operaton.service.ts`, `validsignCompletion.service.ts`, `validsign.routes.ts`,
  `m2m.routes.ts` and `bpmn-swimlane.ts` each rose a little. The one file that
  fell is `routes/public.routes.ts`, from 100% functions to **96.66%** and
  98.59 → 98.14 statements, after the problem-details change. See
  [Backend by area](#backend-by-area).
- **Frontend: +4 files, +60 tests, 1318 → 1378**, and four new source files.
  Package figures: 95.36 → **95.23**, 93.09 → **93.02**, 91.41 → **91.21**,
  95.89 → **95.76** — measured serially this time; see *Which frontend run
  the aggregate uses* above. The new code is uneven: `utils/problem.ts` and
  `useTaskSignature.ts` at 100, `BesluitStartSection.tsx` at 66.66% functions,
  and `BesluitOverzichtSection.tsx` at 80.43% branches. `components/process/`
  fell from 91.96 to **91.18** branches on the declared-phases work, with
  `ProcessWhere.tsx` 91.66 → 85.71 and the new `phaseSet.ts` at 83.33; and
  `TakenInbox.tsx`, which now hosts the signing panel, went from 96.02 to
  94.9 statements while its branches rose, 93.24 → 94.11.
- **Public site: +1 file, +10 tests, 265 → 275** — `lib/problem.test.ts` (9)
  and one more case in `lib/api.test.ts`. Package figures: 96.60 → **96.68**,
  97.34 → **97.40**, 95.07 → **95.09**, 97.17 → **97.23**, all of the
  movement in `src/lib`.
- **pa-cockpit and pa-demo reproduced all four package figures and every
  per-area row to the decimal**, on source that did not change — pa-demo for
  the eighth release running.

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
    invocation. Through 30 September they came from
    `npm test --workspace=@ronl/backend`; the 3 October figures come from
    `npm run test:serial`, the same Jest command with `--runInBand`, so a
    second-decimal difference against earlier passes may be the invocation
    rather than the code.

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
| Backend | 98.91 → 95.21 | 3.7 | 7.5 |
| Frontend | 95.23 → 93.02 | 2.2 | 8.0 |
| pa-cockpit | 92.61 → 93.89 | **−1.3** | 10.6 |
| pa-demo | 93.47 → 95.65 | **−2.2** | 4.4 |
| Public site | 96.68 → 97.40 | **−0.7** | 16.4 |

Every gap narrowed, and three have gone **negative** — branches now sit above
statements, pa-cockpit joining pa-demo and the public site on 30 September,
and all three still there on 3 October.
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

**Re-derived on 3 October 2026** from the run's own coverage report, grouped
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
| `rip-swimlane` | 2 | 100 | 99.26 | 100 | 100 |
| `middleware` | 4 | 100 | 96.66 | 94.11 | 100 |
| `mcp-servers/triplydb` | 1 | 100 | 90.9 | 100 | 100 |
| `routes` | 19 | 99.3 | 98.3 | 99.39 | 99.27 |
| `services/llm` | 4 | 99.02 | 92.3 | 100 | 98.95 |
| `services` | 15 | 99.02 | 95.54 | 98.55 | 99.28 |
| `pa-monitoring` | 10 | 98.95 | 89.35 | 95.93 | 98.99 |
| `utils` | 13 | 98.89 | 98.85 | 100 | 98.75 |
| `pa-monitoring/sources` | 6 | 98.13 | 93.05 | 94.52 | 99.13 |
| `mcp-servers/lde` | 1 | 98.03 | 100 | 100 | 97.95 |
| `media-aggregator` | 10 | 97.58 | 93.37 | 100 | 98.61 |
| `services/mcp` | 6 | 96.33 | 100 | 93.9 | 97.84 |

**Seven rows moved in v2026.10.0, and ten are unchanged to the decimal.**
Three gained a file at 100 on all four — **`middleware`**
(`error.middleware.ts`; branches 95.83 → **96.66**, functions 92.85 →
**94.11**), **`utils`** (`problem.ts`; 98.82 → **98.89** statements) and
**`routes`** (`besluitvorming.routes.ts`). `routes` is also the one row that
fell on a measure: functions 100 → **99.39**, every bit of it
`public.routes.ts` at 96.66%. **`rip-swimlane`** rose to 99.26 branches with
the declared-phases parser, **`services`** moved in the second decimal
(`operaton.service.ts` and `validsignCompletion.service.ts` up, branches
95.61 → 95.54 on the larger denominator), and **`pa-monitoring`** lost a
little on lines, 99.16 → **98.99**, in `pa.routes.ts` and
`pa-dossiers.routes.ts` after their errors became problems.
`media-aggregator` moved by one hundredth on statements.

**History: nine rows moved between v2026.09.13 and v2026.09.15, and eight were unchanged
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

    Both are closed. Of the thirteen source files in `utils/` on 3 October,
    **twelve report 100 / 100 / 100 / 100** — `altcha`, `build-info`,
    `client-ip`, `cors-origin`, `dutch-datetime`, `env`, `errors`, `logger`,
    `operaton-variables`, `problem` (new in v2026.10.0), `slug`,
    `tls-bootstrap`. The thirteenth is `config.ts` at
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
**100 on all four**. The lowest rows on 3 October are `services/mcp` on
statements, functions and lines (96.33%, 93.9% and 97.84%) — `middleware`,
lowest on functions through 30 September, rose past it with
`error.middleware.ts` — and `pa-monitoring` on branches at **89.35%**, more
than nine points clear of the floor. At file level the closest are `pa-monitoring/pa-cache.ts` and
`services/llm/OpenAILlmProvider.ts`, both at **86.36%** branches.

---

## Frontend by area

**Re-derived on 3 October 2026**, from the serial run — the one this pass
made, for the reason given in *Which frontend run the aggregate uses* at the
top of this page. The rows reconcile to the 95.23 / 93.02 / 91.21 / 95.76
package total above. Vitest's text table omits fully covered files, so the
rows are grouped from the run's `coverage-final.json`; every row the text
table does print matches.

**Five rows moved, one is new and fifteen reproduced to the decimal** —
`src/utils` among them, at 100 with one more file.
`src/components/signing` is new — `SigningPanel.tsx` and `resolveSigningUrl.ts`
moved in from `InfraBoardDashboard`, which drops from 12 files to 10, and
`useTaskSignature.ts` is new. `CaseworkerDashboard` gains
`BesluitOverzichtSection.tsx` and `BesluitStartSection.tsx` (26 → **28**) and
`src/utils` gains `problem.ts` at 100 (2 → **3**). The moves are small and
mostly downward on new or reworked code: `CaseworkerDashboard` 94.93 →
**94.45** branches, `components/process` 91.96 → **91.18** branches,
`CaseworkerDashboardV2` 84.66 → **84.24** functions, and `src/services`
97.81 → **96.9** statements and 97.32 → **95.65** functions on the new
response interceptor in `api.ts`. `InfraBoardDashboard` rose on branches,
89.37 → **89.91**, once the signing panel left it.

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
| `src/utils` | 3 | 100 | 100 | 100 | 100 |
| `src/pages/infra-board` | 6 | 100 | 98.47 | 100 | 100 |
| `src/components/process` | 10 | 99.16 | 91.18 | 100 | 99.74 |
| `src/pages/woo` | 2 | 99.13 | 100 | 100 | 99 |
| `src/components/…/regelsimulatie` | 8 | 98.33 | 88.59 | 96.38 | 98.89 |
| `src/components/WooDashboard` | 12 | 98.26 | 94.78 | 98.52 | 98.57 |
| `src/components` | 7 | 97.65 | 93.47 | 98.3 | 100 |
| `src/services` | 8 | 96.9 | 91.07 | 95.65 | 97.03 |
| `src/components/InfraBoardDashboard` | 10 | 95.34 | 89.91 | 92.59 | 95.85 |
| `src/components/CaseworkerDashboard` | 28 | 93.86 | 94.45 | 90 | 94.7 |
| `src/components/signing` | 3 | 93.1 | 88.75 | 95.65 | 96.11 |
| `src/components/CaseworkerDashboardV2` | 10 | 92.81 | 93.52 | 84.24 | 93.3 |
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
    is gone entirely. Nothing in the frontend is below the 80% branch floor,
    though since v2026.10.0 two files are below 85 — see the floor note at the
    top of this page.

`src/pages` is the lowest of the top-level areas because it is where the
largest containers live — and at 78.68% functions it holds four of the nine
frontend files that a functions floor would fail. Its branches, at 94.77%, are
well clear of the floor; this is a functions gap, not a branch gap. Per-board detail is on the board
pages: [Caseworker](dashboards/caseworker.md),
[PA cockpit](dashboards/pa-cockpit.md),
[Infra-board](dashboards/infra-board.md),
[Woo-dashboard](dashboards/woo-dashboard.md).

---

## pa-cockpit by area

**Re-derived on 3 October 2026, and every row is identical to 30 September**,
on a package v2026.10.0 did not touch. These rows reconcile to the 92.61 /
93.89 / 89.56 / 93.13 package total above. The account below is of the
28 → 30 September window. The package's only changes in it were tests —
`391b1a8`'s four in `DossierRow.test.tsx` and `73a6764`'s 35 across six files — plus the small `DossierRow.tsx` fix the
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
pattern as the frontend's `src/pages`. This package holds 7 of the 24 files
that an 80% functions floor would fail.

---

## Public site by area

**Re-derived on 3 October 2026.** These rows reconcile to the 96.68 / 97.40 /
95.09 / 97.23 package total above. **Five of the six are identical to 24, 26,
28 and 30 September**; the sixth is `src/lib` again, this time on v2026.10.0's
problem details: `lib/problem.ts` is new, at 100 on all four, and `lib/api.ts`
now reads a problem's `detail` through it.

| Area | Files | Statements | Branches | Functions | Lines |
|---|---:|---:|---:|---:|---:|
| `src/` (root files) | 1 | 100 | 100 | 100 | 100 |
| `src/i18n` | 3 | 100 | 100 | 100 | 100 |
| `src/pages/herkomst` | 8 | 100 | 97.05 | 100 | 100 |
| `src/components` | 13 | 97.14 | 100 | 96.29 | 97.05 |
| `src/lib` | 9 | 96.8 | 97.05 | 97.43 | 98.03 |
| `src/pages` | 10 | 95.45 | 97.29 | 92 | 95.83 |

`src/lib` went 96.49 → **96.8** statements, 96.66 → **97.05** branches,
97.36 → **97.43** functions and 97.87 → **98.03** lines. Before that, the
v2026.09.15 window took it from 93.85 / 91.11 to 96.49 / 96.66, on the one
production change `73a6764` made anywhere: `lib/api.ts` reads
`import.meta.env` directly, so its base-URL fallbacks can be tested with
`vi.stubEnv`. `lib/api.ts` itself went from 83.78% branches — the lowest file
in the package from v2026.09.11 to v2026.09.13 — to 97.29% then, and reads
**96.55%** on 3 October; the arms left cannot occur in Node and are tracked in
#294. The lowest files by branches are `lib/useQueryState.ts` and
`pages/herkomst/HerkomstTrace.tsx`, both at 87.50%.

The new `src/indexHtml.test.ts` adds no row: it tests `index.html`'s
link-preview tags, filled from each mode's `.env` file, and `index.html` is
not a source file under coverage.

!!! success "The pre-campaign rows are gone, and the difference is the point"
    This table used to carry three rows derived on 22 August 2026 —
    `src/components` 96.77, `src/lib` 84.9 / **73.17 branches**, `src/pages` 82 /
    **61.51 branches** — which sat visibly below a package total of 96.41% and
    carried a warning saying so. They are now re-measured: `src/lib` branches
    have gone **73.17 → 97.05**, and `src/pages` branches **61.51 → 97.29**.
    Nothing in the package is below the 80% branch floor, and `src/components`
    is at 100% branches outright.

    The whole-tree `src/pages` row covers the ten files directly in that
    directory; the eight-file `herkomst/` provenance explorer reports as its own
    row, at 100% statements.

See [Public site suite](public-site.md) for what these files are and what is
deliberately not covered.

---

## pa-demo by area

**Re-derived on 3 October 2026**, and every row below reconciles to the
**All files** row rather than predating it. All five rows reproduced to the
decimal against 24, 26, 28 and 30 September, on a package whose `src/` tree
has not changed since v2026.09.5.

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
    This package contributes 5 of the 24 files an 80% functions floor would
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
