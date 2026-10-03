---
component: RONL Business API
---

# Woo-dashboard — tests

**Frontend: 15 files · 77 tests. E2E: none yet.**

The Woo dashboard is the most thinly tested of the four boards by test count,
while reporting high coverage percentages. Both things are true at once, and
the combination is worth understanding before reading the numbers as
reassurance.

---

## Frontend

Re-derived on **3 October 2026** at `0625d48` (v2026.10.0), where every count
and coverage figure below is the same as on 30 September — v2026.10.0 did not
touch this board. The frontend package was measured the same day — 124 files,
1378 tests, all passing — but Vitest's console reports only that total, so the
counts below are taken from the source, each test file parsed with its `.each`
tables expanded; summed over the whole package the method gives exactly the
runner's 1378.

| Area | Files | Tests |
|---|---:|---:|
| `components/WooDashboard` | 12 | 43 |
| `pages/woo` (data and config) | 2 | 22 |
| `pages/WooDashboard.test.tsx` | 1 | 12 |

| File | Tests | Covers |
|---|---:|---|
| `pages/woo/woo.data.test.ts` | 19 | The board's data module |
| `pages/WooDashboard.test.tsx` | 12 | The page container |
| `components/WooDashboard/Register.test.tsx` | 8 | The register section |
| `components/WooDashboard/WooCommandPalette.test.tsx` | 8 | Command palette |
| `components/WooDashboard/charts.test.tsx` | 7 | Chart rendering |
| `components/WooDashboard/WooSectionRouter.test.tsx` | 7 | Section routing |
| `pages/woo/modes.config.test.ts` | 3 | Mode configuration |
| `components/WooDashboard/Bezwaar.test.tsx` | 2 | Objections |
| `components/WooDashboard/Proces.test.tsx` | 2 | Process view |
| `components/WooDashboard/Publicatie.test.tsx` | 2 | Publication |
| `components/WooDashboard/Verzoeken.test.tsx` | 2 | Requests |
| `components/WooDashboard/WooDock.test.tsx` | 2 | The dock |
| `components/WooDashboard/Overzicht.test.tsx` | 1 | Overview |
| `components/WooDashboard/Tijdigheid.test.tsx` | 1 | Timeliness |
| `components/WooDashboard/WooNoAccessPanel.test.tsx` | 1 | The no-access panel |

`woo.data.test.ts` (+4) and `WooDashboard.test.tsx` (+3) grew in v2026.09.15's
branch-margin work; the other counts are as they were on 28 September.

Coverage on 3 October, as on 30 September: `components/WooDashboard`
**98.26 / 94.78 / 98.52 / 98.57** and `pages/woo` **99.13 / 100 / 100 / 99** —
the latter up from 96.55 / 84.12 / 94.44 / 98.01.

!!! note "High coverage, few assertions"
    Eight of the twelve component files carry one or two tests each. Those
    render the section and assert it renders — which executes nearly every line
    in a presentational component and so scores 98%, without asserting much
    about what it renders.

    That is a legitimate scoping choice for presentational sections, and it is
    the same "critical interactions only" approach used across the frontend.
    But it means this board's coverage percentage is a weaker signal than the
    identical percentage on, say, `pages/infra-board`, where 108 tests across
    six files are asserting real behaviour. Read the test count alongside the
    percentage.

---

## E2E

**None.** There is no Playwright spec that drives this board — verified against
`packages/frontend/e2e/` on 30 August 2026, at `ae06c9e` on 30 September and
in the full frontend run of 3 October, whose 28 tests include none that
drives this board (`login-redirect` only checks that `test-woo-flevoland`
lands on it) — not inferred from a changelog. It is
now the only board in that position; see
[Coverage per board](../e2e.md#coverage-per-board).

As with [Infra-board](infra-board.md), this is a gap rather than a decision, and
the case for closing it is a little stronger here: the combination of few
assertions and no end-to-end coverage means a broken write path or an empty
panel would pass everything currently in place.

The PA cockpit suite is the model — mock mode driven against the real store, no
mocking, deterministic fixtures. See
[PA cockpit → Why mock mode is worth an E2E suite](pa-cockpit.md#why-mock-mode-is-worth-an-e2e-suite).
