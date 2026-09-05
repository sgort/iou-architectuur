---
component: RONL Business API
---

# Coverage

Measured with `npm run test:serial` against **v2026.09.5** on **5 September
2026**, on `acc` at `66940d9`, after a clean `npm ci`. All five packages were
measured in the same run.

| Package | Statements | Branches | Functions | Lines | Δ branches since v2026.08.36 |
|---|---:|---:|---:|---:|---|
| Backend | 98.40% | 92.28% | 97.28% | 98.83% | +2.27 |
| Frontend | 93.11% | 89.76% | 87.75% | 93.97% | **+9.43** |
| pa-cockpit | 90.07% | 88.52% | 86.39% | 91.33% | **+12.97** |
| pa-demo | 93.47% | 95.65% | 85.00% | 92.85% | **+8.70** |
| Public site | 96.09% | 96.92% | 94.62% | 96.16% | **+26.53** |

!!! note "Every package moved, and branches moved most"
    v2026.09.2 extended the backend-only coverage campaign to all five
    workspaces with a test runner, against a **per-file 80% branch floor**:
    53 files were below it, none are now. That is why the branch column moved
    furthest and why public-site — which started lowest at 70.39% — moved most.

    This is unusual and worth noting as a check that the run is sound: the
    previous pass had three packages reproducing their figures to the decimal.
    Here every package gained on every measure, which is what a campaign
    targeting *all* of them should look like.

!!! warning "The floor is a convention, not a gate"
    Nothing mechanical enforces it. No `coverageThreshold` is configured in any
    of the five runner configs, and **no workflow measures coverage at all** —
    so a file dropping below 80% branches fails neither a local run nor CI. The
    floor is recorded in an implementation plan and held by review. See
    [Code Standards](../../../contributing/code-standards.md#the-80-branch-floor-is-a-convention-not-a-gate).

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

Backend and public site are unchanged because nothing under their `src/` trees
was touched in this window; both reproduced the 22 August figures exactly.

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

| Package | Statements → branches | Gap |
|---|---|---:|
| Backend | 97.52 → 90.01 | 7.5 |
| Frontend | 88.32 → 80.33 | 8.0 |
| pa-cockpit | 86.16 → 75.55 | 10.6 |
| pa-demo | 91.30 → 86.95 | 4.4 |
| Public site | 86.82 → 70.39 | 16.4 |

The backend's gap has largely closed; the public site's has not moved, because
nothing there changed. **pa-demo now has the narrowest gap of the five**, which
is a property of what it became rather than of effort spent: a thin host adapter
over a package that carries its own tests. What is left elsewhere is the same
kind of thing:
defensive `if (!req.user)` guards behind real middleware, `?? null` fallbacks,
catch blocks unreachable through a legal input, and deliberately-scoped
"critical interactions only" passes on the largest components — documented
per-file rather than silently absent.

---

## Backend by area

These are the rows Jest prints, verbatim, so each can be matched against the
output of `npm test --workspace=@ronl/backend -- --coverageReporters=text`.
Sub-directories report separately rather than rolling up into their parent, and
istanbul truncates to two decimals rather than rounding.

| Area | Statements | Branches | Functions | Lines |
|---|---:|---:|---:|---:|
| `mcp-servers/edocs` | 100 | 100 | 100 | 100 |
| `mcp-servers/triplydb` | 100 | 90.9 | 100 | 100 |
| `middleware` | 100 | 95.83 | 92.3 | 100 |
| `utils` | 100 | 100 | 100 | 100 |
| `routes` | 99.55 | 93.86 | 100 | 99.53 |
| `services/llm` | 99.02 | 92.3 | 100 | 98.95 |
| `services` | 98.87 | 91.26 | 98.13 | 99.24 |
| `pa-monitoring` | 98.32 | 88.01 | 94.82 | 98.37 |
| `pa-monitoring/sources` | 97.07 | 88.6 | 92.2 | 98.1 |
| `media-aggregator` | 96.96 | 92.26 | 98.21 | 98.26 |
| `services/mcp` | 96.33 | 100 | 93.9 | 97.84 |
| `mcp-servers/lde` | 96.07 | 82.14 | 100 | 97.95 |
| `auth` | 88.88 | 85.71 | 84.61 | 88.05 |

!!! success "`utils/` is no longer the exception"
    Through v2026.08.20 this table's lowest row by a wide margin was `utils/`
    at 43.47% statements and **6.54% branches**, documented as an accepted
    artifact: `config.ts` sat at 0% because it self-runs `dotenv` and
    `validateConfig` on import, and `logger.ts` was mocked in every test that
    touched it.

    Both are now closed. Every file in `utils/` — `altcha`, `config`, `env`,
    `errors`, `logger`, `operaton-variables`, `slug`, `tls-bootstrap` — reports
    **100 / 100 / 100 / 100**. `tls-bootstrap.ts` was also at 0% and is now
    fully covered. The area that was the standing excuse is now the best in the
    package.

`auth/` is now the lowest row, at 88.88% statements — the uncovered lines are
`jwt.middleware.ts:23-33`.

---

## Frontend by area

| Area | Statements | Branches | Functions | Lines |
|---|---:|---:|---:|---:|
| `src/hooks` | 100 | 75 | 100 | 100 |
| `src/pages/infra-board` | 99.64 | 97.2 | 100 | 100 |
| `src/components/WooDashboard` | 97.68 | 89.56 | 98.52 | 97.85 |
| `src/components/…/regelsimulatie` | 97.66 | 81.43 | 95.18 | 98.15 |
| `src/pages/woo` | 96.55 | 84.12 | 94.44 | 98.01 |
| `src/services` | 93.48 | 81.14 | 96.55 | 94.02 |
| `src/components/InfraBoardDashboard` | 90.96 | 84.54 | 87.87 | 91.68 |
| `src/` (root files) | 88.23 | 72.22 | 60 | 88.23 |
| `src/pages/public-affairs-v2` | 86.67 | 69.69 | 83.83 | 90.28 |
| `src/components` | 86.45 | 70.11 | 94.73 | 90.62 |
| `src/components/CaseworkerDashboard` | 86.33 | 81.37 | 84.53 | 88.19 |
| `src/components/PADashboardV2` | 84.77 | 73.2 | 81.87 | 87.41 |
| `src/components/…/dossierbeheer` | 81.35 | 89.12 | 77.96 | 82.89 |
| `src/components/CaseworkerDashboardV2` | 81.27 | 74.57 | 72.51 | 81.96 |
| `src/pages` | 72.4 | 69.87 | 61.56 | 73.43 |
| `src/utils` | 66.66 | 50 | 100 | 100 |

Two rows moved substantially in this window: `src/pages/public-affairs-v2` from
67.83% to **86.67%**, and `src/components/…/dossierbeheer` from 79.29% to
**81.35%** — both from the PA cockpit work. `src/services` rose from 93.01% to
93.48%.

`src/pages` is the lowest of the top-level areas because it is where the
largest, most-recently-added containers live. Per-board detail is on the board
pages: [Caseworker](dashboards/caseworker.md),
[PA cockpit](dashboards/pa-cockpit.md),
[Infra-board](dashboards/infra-board.md),
[Woo-dashboard](dashboards/woo-dashboard.md).

---

## Public site by area

| Area | Statements | Branches | Functions | Lines |
|---|---:|---:|---:|---:|
| `src/components` | 96.77 | 100 | 96.15 | 96.66 |
| `src/lib` | 84.9 | 73.17 | 88.88 | 86.2 |
| `src/pages` | 82 | 61.51 | 79.06 | 84.26 |

Unchanged since v2026.08.20 — see [Public site suite](public-site.md) for what
these files are and what is deliberately not covered.

---

## pa-demo by area

| Area | Statements | Branches | Functions | Lines |
|---|---:|---:|---:|---:|
| **All files** | **93.47** | **95.65** | **85.00** | **92.85** |
| `src/demo` | 95.91 | 84.61 | 100 | 97.72 |
| `src/demo/changelog` | 100 | 87.50 | 100 | 100 |
| `src/demo/shims` | 75.00 | 100 | 44.44 | 75.00 |
| `src/` (root) | 75.00 | 100 | 50.00 | 75.00 |

!!! note "The **All files** row is measured; the per-area rows below it are not"
    The package total was re-measured against v2026.09.5 on 5 September 2026.
    The per-area rows were last derived on 30 August and have not been
    re-generated, so they will not sum to the new total — v2026.09.2's coverage
    campaign added tests across the package. Treat the per-area breakdown as
    indicative of *where* the gaps are, not of their current size.

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
