---
component: RONL Business API
---

# Coverage

Measured with `npm test --workspace=<pkg>` per package against **v2026.08.23**
on **22 August 2026**, from a cold cache. `packages/pa-demo` was measured
separately, on **25 August 2026** on branch `feat/public-pa-cockpit` at
`a59a0a7` — it has not merged to `acc` yet, so its row carries a different
date and commit than the other three.

| Package | Statements | Branches | Functions | Lines | Δ since v2026.08.20 |
|---|---:|---:|---:|---:|---|
| Backend | 98.35% | 91.49% | 96.65% | 98.75% | +4.07 / +17.95 / +2.52 / +3.06 |
| Frontend | 87.47% | 78.68% | 83.35% | 88.87% | +2.43 / +2.17 / +3.19 / +2.47 |
| Public site | 86.82% | 70.39% | 87.63% | 88.76% | unchanged |
| pa-demo | 73.94% | 63.41% | 72.22% | 73.87% | new package |

Public site is unchanged because nothing under `packages/public-site/src/` was
touched in this window; its figures reproduced the 20 August numbers exactly.
pa-demo is new to this table and excludes `src/vendor/**` from every figure —
see [pa-demo by area](#pa-demo-by-area) below.

The backend branch figure moved most — **73.54% → 91.49%**, nearly eighteen
points — from the coverage campaign and the PA route work. On the frontend the
gain came from four surfaces that had little or nothing: `NotificationsPanel`
(previously 0%), `Issuekaart`, `Monitoring`, and `PaDataProvider`.

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

All four configure `collectCoverageFrom` / `coverage.include` to span the whole
`src` tree rather than only the files a test happens to import, so an untested
file shows as 0% instead of silently disappearing from the report. pa-demo's
`coverage.include` is `src/**/*.{ts,tsx}` with `src/vendor/**` explicitly
excluded — see [pa-demo by area](#pa-demo-by-area).

**What the headline numbers mean here.** The first three packages have been
through a dedicated coverage campaign that closed *breadth* gaps
deliberately — every backend feature area, every frontend component and
page, and every public-site module now has at least a test file. What
remains there is *depth*, and it is no longer uniform across the three.
pa-demo has not had that campaign yet — it is a new package, and its
lower headline figures reflect breadth gaps rather than depth ones (see
[pa-demo by area](#pa-demo-by-area)):

| Package | Statements → branches | Gap |
|---|---|---:|
| Backend | 98.35 → 91.49 | 6.9 |
| Frontend | 87.47 → 78.68 | 8.8 |
| Public site | 86.82 → 70.39 | 16.4 |
| pa-demo | 73.94 → 63.41 | 10.5 |

The backend's gap has largely closed; the public site's has not moved, because
nothing there changed. pa-demo is new and has not been through a coverage
campaign at all yet — its gap is closer to the backend's than to public
site's, but at a much lower base. What is left in the first three is the same
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
| `src/` (root) | 75.00 | 100 | 50.00 | 75.00 |
| `src/demo` | 76.08 | 61.53 | 95.45 | 76.19 |
| `src/demo/shims` | 65.21 | 100 | 33.33 | 65.21 |

**`src/vendor/**` is excluded from every figure on this page and this table.**
Those 39 files are the same ones already exercised by the 1155 tests counted
under Frontend above — measuring them again here would double-count that
work and let pa-demo's own, much smaller, demo-owned surface
(`src/demo/**`, `src/main-helpers.ts`, `src/App.tsx`) hide behind an
inflated package total. A reader comparing this table to that 39-file
vendored tree should not expect it to appear here at all; it is covered,
just not by this package's suite. See
[pa-demo suite → Coverage excludes `src/vendor/**`](pa-demo.md#coverage-excludes-srcvendor)
for the full rationale.

Two more files are excluded from coverage entirely, by config rather than by
this table's rounding: `src/main.tsx` (it calls `createRoot`; its one
meaningful line, `forceMockMode()`, is tested separately via the extracted,
fully-covered `src/main-helpers.ts`) and `src/vite-env.d.ts` (a type-only
ambient declaration file, nothing to execute). The `src/` row above is just
these two remaining root files, `App.tsx` and `main-helpers.ts` — 100% on
`main-helpers.ts` (3/3 statements) pulled down by 0% on `App.tsx` (0/1) gives
the row's 75%. `App.tsx` is the lowest-covered file in the package — its one
statement, the route shell itself, has no test rendering it.
