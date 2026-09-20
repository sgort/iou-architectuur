---
component: RONL Business API
---

# Coverage

Measured on **20 September 2026** against **v2026.09.9**, on `main` at
`10bcf8b`, after a clean `npm ci` in a separate clone on **Node 24.14.1 /
npm 11.11.0**. Each package was measured by its own `npm test`, run one
workspace at a time; all five of those scripts collect coverage already.

| Package | Statements | Branches | Functions | Lines | Δ branches since v2026.08.36 |
|---|---:|---:|---:|---:|---|
| Backend | 98.37% | 92.35% | 97.29% | 98.79% | +2.34 |
| Frontend | 93.23% | 89.92% | 87.96% | 94.06% | **+9.59** |
| pa-cockpit | 90.07% | 88.52% | 86.39% | 91.33% | **+12.97** |
| pa-demo | 93.47% | 95.65% | 85.00% | 92.85% | **+8.70** |
| Public site | 95.82% | 96.45% | 94.89% | 96.33% | **+26.06** |

!!! info "The repository-wide figure, and why it is not an average of that column"
    Across all five workspaces together: **95.08% statements · 90.86% branches ·
    90.49% functions · 95.84% lines**.

    Those come from **summing the covered and total counts** across the five
    `coverage-summary.json` reports and dividing once — 12923/13591 statements,
    8119/8936 branches, 2987/3301 functions, 11740/12249 lines — not from
    averaging the five percentages in the table. Averaging the column would
    weight pa-demo's 92 statements exactly as heavily as the backend's 5977 and
    give a repository-wide branch figure of 92.58% instead of 90.86%: nearly two
    points of pure arithmetic error, in the flattering direction. The
    denominators differ by two orders of magnitude here, so the distinction is
    not academic.

    The frontend contributes its **serial** branch count (3408/3790) for the
    reason given on [Overview](overview.md#a-parallel-failure-is-not-a-finding);
    its parallel run, one test short, gives 3407 and moves the repository-wide
    branch figure to 90.85%.

!!! note "Every package moved, and branches moved most"
    v2026.09.2 extended the backend-only coverage campaign to all five
    workspaces with a test runner, against a **per-file 80% branch floor**:
    53 files were below it, none are now. That is why the branch column moved
    furthest and why public-site — which started lowest at 70.39% — moved most.

    That was unusual and worth noting as a check that the run was sound: the
    pass before it had three packages reproducing their figures to the decimal,
    while in the campaign pass every package gained on every measure — which is
    what a campaign targeting *all* of them should look like. The table above
    is two releases further on, and has moved only in decimals since; what
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
    so nothing needed a separate coverage job. **All five passed on
    20 September 2026 and no file was named**, and scanning every file entry in
    the five `coverage-summary.json` reports confirms it independently: **zero
    files below 80% branches**, out of 88 in backend, 111 in frontend, 38 in
    pa-cockpit, 16 in pa-demo and 43 in public-site.

    Per file is the whole point: against a package average, one file falling to
    40% barely moves 92%, and the regression the floor exists to catch would
    pass. **Branches only is equally deliberate.** Measured the same way on
    20 September, a functions floor at 80 would fail **26 files** — frontend 10,
    pa-cockpit 8, pa-demo 5, public-site 3, backend 0 — so the symmetry is a
    trap for whoever adds `functions: 80` on the assumption that it is free.

    `public-site/src/components/TopBar.tsx` is the example the configs
    themselves reach for, and it still holds: **100% branches, 66.66%
    functions**. The two metrics are not interchangeable, and a file can be
    exemplary on one while failing the other.

    See [Coverage Floor](../../../contributing/coverage-floor.md).

!!! note "The configs' own comments say 31, not 26"
    All five runner configs carry a comment claiming a functions floor would
    fail 31 files (frontend 11, pa-cockpit 10, pa-demo 7, public-site 3,
    backend 0). Re-derived from the 20 September reports the figure is **26**,
    distributed as above. The comments were accurate when written and have not
    been updated since; the number here is the measured one. Where the two
    disagree, re-run the suites rather than trusting either.

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

**What moved between 12 and 20 September** is small, and `git diff --stat
311d732 10bcf8b -- packages/` accounts for all of it.

- **pa-demo and pa-cockpit reproduced all four figures to the decimal** except
  pa-cockpit's functions, 0.13 of a point down. Neither package had a single
  `src/` change in the window — only `package.json` — so both rows are a
  straight repeat measurement, and the pa-cockpit move is the ordinary
  run-to-run noise described below rather than a regression.
- **The backend gained 20 tests without gaining a file** (2008 → 2028, still
  86). Almost all of that is `routes/validsign.routes.test.ts`, which grew by
  173 lines alongside a 73-line change to the route it covers; `lde.service`,
  `operaton.service`, `search.service` and `config` moved too. Statements and
  lines each gave up a few hundredths while branches rose 0.04 — which is what
  adding branch cases to an already well-covered file does.
- **The frontend gained 11 tests, also without a new file** (1103 → 1114, still
  110), spread across `InfraCommandPalette`, `PhaseDetail`,
  `InfraBoardDashboard`, `infra-board.data` and `infra.api`. Every measure rose
  slightly; branches moved most, 89.78% → 89.92%.
- **The public site is the only package that gained a file** (31 → 32, 225 →
  231 tests): `src/components/StatusTag.test.tsx`, arriving with the
  `StatusTag.tsx` it covers, plus new cases in `Results.test.tsx`. The new
  component is at **100% on all four measures**, which is why a package this
  small gained on all four rather than trading one against another — the
  opposite of what `buildInfo` did to it in the previous window.

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
| Backend | 98.37 → 92.35 | 6.0 | 7.5 |
| Frontend | 93.23 → 89.92 | 3.3 | 8.0 |
| pa-cockpit | 90.07 → 88.52 | 1.6 | 10.6 |
| pa-demo | 93.47 → 95.65 | **−2.2** | 4.4 |
| Public site | 95.82 → 96.45 | **−0.6** | 16.4 |

Every gap narrowed, and two went **negative** — branches now sit above
statements. That is what a campaign aimed at branch edges produces once it
reaches the guards inside files whose plain statements nobody had a reason to
execute. The public site, whose 16.4-point gap was the widest in the repository
a month ago, is one of the two. pa-demo's position is a property of what it
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

**Re-derived on 20 September 2026** from the run's own
`coverage/coverage-summary.json`, grouped per directory the way istanbul's text
reporter groups them. The rows reconcile to the package total in the table at
the top of this page, which is the check that they are current.

| Area | Files | Statements | Branches | Functions | Lines |
|---|---:|---:|---:|---:|---:|
| `mcp-servers/edocs` | 1 | 100 | 100 | 100 | 100 |
| `mcp-servers/triplydb` | 1 | 100 | 90.9 | 100 | 100 |
| `middleware` | 2 | 100 | 95.91 | 92.3 | 100 |
| `services/document` | 4 | 100 | 100 | 100 | 100 |
| `rip-swimlane` | 2 | 99.3 | 98.52 | 96 | 100 |
| `routes` | 15 | 99.14 | 94.65 | 100 | 99.11 |
| `services/llm` | 4 | 99.02 | 92.3 | 100 | 98.95 |
| `services` | 15 | 98.77 | 91.4 | 98.47 | 99.25 |
| `utils` | 10 | 98.47 | 98.66 | 100 | 98.3 |
| `pa-monitoring` | 10 | 98.38 | 88.1 | 95.93 | 98.53 |
| `pa-monitoring/sources` | 6 | 97.58 | 91.57 | 93.24 | 98.5 |
| `media-aggregator` | 10 | 96.96 | 92.26 | 98.21 | 98.26 |
| `services/mcp` | 6 | 96.33 | 100 | 93.9 | 97.84 |
| `mcp-servers/lde` | 1 | 96.07 | 82.14 | 100 | 97.95 |
| `auth` | 1 | 88.23 | 82.75 | 86.66 | 89.61 |

Two rows are new to this table rather than newly measured. **`rip-swimlane`**
had never appeared here at all — the area that derives an Infra-board phase
swimlane from deployed BPMN, and it enters at 99.3% statements. **`services/document`**
is likewise a first appearance, at 100 across the board.

!!! success "`utils/` is no longer the exception"
    Through v2026.08.20 this table's lowest row by a wide margin was `utils/`
    at 43.47% statements and **6.54% branches**, documented as an accepted
    artifact: `config.ts` sat at 0% because it self-runs `dotenv` and
    `validateConfig` on import, and `logger.ts` was mocked in every test that
    touched it.

    Both are closed. Of the ten source files in `utils/` on 20 September, nine
    report **100 / 100 / 100 / 100** — `altcha`, `client-ip`, `dutch-datetime`,
    `env`, `errors`, `logger`, `operaton-variables`, `slug`, `tls-bootstrap`.
    The tenth is `config.ts` at 93.75% statements and **98.26% branches**
    (113 of 115), which is what pulls the area row off 100 and is comfortably
    the largest branch surface in the area. `tls-bootstrap.ts` was also at 0%
    and is now fully covered. The area that was the standing excuse is now
    among the best in the package.

`auth/` is the lowest row, at 88.23% statements and **82.75% branches** — one
file, `jwt.middleware.ts`, and the only area in the backend within three points
of the 80% branch floor.

---

## Frontend by area

**Re-derived on 20 September 2026**, from the serial run's
`coverage/coverage-summary.json`. The rows reconcile to the 93.23 / 89.92 /
87.96 / 94.06 package total above.

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
| `src/pages/infra-board` | 6 | 99.6 | 97.7 | 100 | 99.49 |
| `src/components/…/regelsimulatie` | 8 | 98.33 | 88.59 | 96.38 | 98.89 |
| `src/components/WooDashboard` | 12 | 98.26 | 94.78 | 98.52 | 98.57 |
| `src/components` | 6 | 97.6 | 93.1 | 98.24 | 100 |
| `src/services` | 7 | 97.53 | 89.26 | 97.27 | 97.69 |
| `src/pages/woo` | 2 | 96.55 | 84.12 | 94.44 | 98.01 |
| `src/components/InfraBoardDashboard` | 13 | 94.05 | 88.47 | 90.2 | 95.11 |
| `src/components/CaseworkerDashboardV2` | 8 | 92.46 | 92.28 | 82.44 | 93.1 |
| `src/components/CaseworkerDashboard` | 26 | 90.16 | 89.33 | 86.08 | 91.67 |
| `src/pages` | 11 | 83.33 | 87.47 | 73.06 | 84.09 |

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
largest, most-recently-added containers live — and at 73.06% functions it is
also where most of the 26 files that a functions floor would fail are
concentrated. Its branches, at 87.47%, are comfortably clear of the floor;
this is a functions gap, not a branch gap. Per-board detail is on the board
pages: [Caseworker](dashboards/caseworker.md),
[PA cockpit](dashboards/pa-cockpit.md),
[Infra-board](dashboards/infra-board.md),
[Woo-dashboard](dashboards/woo-dashboard.md).

---

## pa-cockpit by area

**Re-derived on 20 September 2026.** These rows reconcile to the 90.07 / 88.52 /
86.39 / 91.33 package total above.

| Area | Files | Statements | Branches | Functions | Lines |
|---|---:|---:|---:|---:|---:|
| `src/` (root files) | 2 | 100 | 100 | 100 | 100 |
| `src/modes` | 1 | 95.65 | 100 | 100 | 95 |
| `src/services` | 3 | 94.54 | 84.98 | 98.19 | 95.28 |
| `src/components/PADashboardV2` | 10 | 91.88 | 89.44 | 86.3 | 93.73 |
| `src/pages/public-affairs-v2` | 13 | 90.35 | 88.2 | 86.4 | 92.08 |
| `src/pages` | 1 | 86.87 | 95.57 | 79.03 | 86.76 |
| `src/components/PADashboardV2/dossierbeheer` | 8 | 81.35 | 89.12 | 77.96 | 82.89 |

`dossierbeheer` is the lowest area on statements and the lowest on functions,
but at 89.12% branches it clears the floor by nine points — the same pattern as
the frontend's `src/pages`. This package holds 8 of the 26 files that an 80%
functions floor would fail.

---

## Public site by area

**Re-derived on 20 September 2026.** These rows reconcile to the 95.82 / 96.45 /
94.89 / 96.33 package total above.

| Area | Files | Statements | Branches | Functions | Lines |
|---|---:|---:|---:|---:|---:|
| `src/` (root files) | 1 | 100 | 100 | 100 | 100 |
| `src/i18n` | 3 | 100 | 100 | 100 | 100 |
| `src/pages/herkomst` | 8 | 100 | 97.05 | 100 | 100 |
| `src/components` | 13 | 97.14 | 100 | 96.29 | 97.05 |
| `src/pages` | 10 | 95.21 | 97.55 | 91.39 | 95.65 |
| `src/lib` | 8 | 93.85 | 91.11 | 97.36 | 94.68 |

!!! success "The pre-campaign rows are gone, and the difference is the point"
    This table used to carry three rows derived on 22 August 2026 —
    `src/components` 96.77, `src/lib` 84.9 / **73.17 branches**, `src/pages` 82 /
    **61.51 branches** — which sat visibly below a package total of 96.41% and
    carried a warning saying so. They are now re-measured: `src/lib` branches
    have gone **73.17 → 91.11**, and `src/pages` branches **61.51 → 97.55**.
    Nothing in the package is below the 80% branch floor, and `src/components`
    is at 100% branches outright.

    The whole-tree `src/pages` row covers the ten files directly in that
    directory; the eight-file `herkomst/` provenance explorer reports as its own
    row, at 100% statements.

See [Public site suite](public-site.md) for what these files are and what is
deliberately not covered.

---

## pa-demo by area

**Re-derived on 20 September 2026**, and every row below now reconciles to the
**All files** row rather than predating it.

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
    This package contributes 5 of the 26 files an 80% functions floor would
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
