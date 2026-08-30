---
component: RONL Business API
---

# Woo-dashboard — tests

**Frontend: 15 files · 66 tests. E2E: none yet.**

The Woo dashboard is the most thinly tested of the four boards by test count,
while reporting high coverage percentages. Both things are true at once, and
the combination is worth understanding before reading the numbers as
reassurance.

---

## Frontend

| Area | Files | Tests |
|---|---:|---:|
| `components/WooDashboard` | 12 | 39 |
| `pages/woo` (data and config) | 2 | 18 |
| `pages/WooDashboard.test.tsx` | 1 | 9 |

| File | Tests | Covers |
|---|---:|---|
| `pages/woo/woo.data.test.ts` | 15 | The board's data module |
| `pages/WooDashboard.test.tsx` | 9 | The page container |
| `components/WooDashboard/WooCommandPalette.test.tsx` | 8 | Command palette |
| `components/WooDashboard/charts.test.tsx` | 7 | Chart rendering |
| `components/WooDashboard/WooSectionRouter.test.tsx` | 7 | Section routing |
| `components/WooDashboard/Register.test.tsx` | 4 | The register section |
| `pages/woo/modes.config.test.ts` | 3 | Mode configuration |
| `components/WooDashboard/Bezwaar.test.tsx` | 2 | Objections |
| `components/WooDashboard/Proces.test.tsx` | 2 | Process view |
| `components/WooDashboard/Publicatie.test.tsx` | 2 | Publication |
| `components/WooDashboard/Verzoeken.test.tsx` | 2 | Requests |
| `components/WooDashboard/WooDock.test.tsx` | 2 | The dock |
| `components/WooDashboard/Overzicht.test.tsx` | 1 | Overview |
| `components/WooDashboard/Tijdigheid.test.tsx` | 1 | Timeliness |

Coverage: `components/WooDashboard` **97.68 / 89.56 / 98.52 / 97.85** and
`pages/woo` 96.55 / 84.12 / 94.44 / 98.01.

!!! note "High coverage, few assertions"
    Seven of the twelve component files carry one or two tests each. Those
    render the section and assert it renders — which executes nearly every line
    in a presentational component and so scores 97%, without asserting much
    about what it renders.

    That is a legitimate scoping choice for presentational sections, and it is
    the same "critical interactions only" approach used across the frontend.
    But it means this board's coverage percentage is a weaker signal than the
    identical percentage on, say, `pages/infra-board`, where 88 tests across six
    files are asserting real behaviour. Read the test count alongside the
    percentage.

---

## E2E

**None.** There is no Playwright spec that drives this board — verified against
`packages/frontend/e2e/` on 30 August 2026, not inferred from a changelog. It is
now the only board in that position; see
[Coverage per board](../e2e.md#coverage-per-board).

As with [Infra-board](infra-board.md), this is a gap rather than a decision, and
the case for closing it is a little stronger here: the combination of few
assertions and no end-to-end coverage means a broken write path or an empty
panel would pass everything currently in place.

The PA cockpit suite is the model — mock mode driven against the real store, no
mocking, deterministic fixtures. See
[PA cockpit → Why mock mode is worth an E2E suite](pa-cockpit.md#why-mock-mode-is-worth-an-e2e-suite).
