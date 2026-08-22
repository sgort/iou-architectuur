---
component: RONL Business API
---

# Infra-board — tests

**Frontend: 17 files · 188 tests. E2E: none yet.**

The infra-board is well covered at the unit level — `src/pages/infra-board` is
the single best-covered area in the frontend at **99.64%** statements — and has
no end-to-end coverage at all.

---

## Frontend

| Area | Files | Tests |
|---|---:|---:|
| `pages/infra-board` (data and pure logic) | 6 | 88 |
| `components/InfraBoardDashboard` | 10 | 86 |
| `pages/InfraBoardDashboard.test.tsx` | 1 | 14 |

| File | Tests | Covers |
|---|---:|---|
| `components/InfraBoardDashboard/PhaseDetail.test.tsx` | 26 | Phase detail view |
| `pages/infra-board/infra-board.data.test.ts` | 26 | The board's data module |
| `pages/infra-board/rip-model.test.ts` | 20 | The RIP phase model |
| `pages/infra-board/rail-stats.test.ts` | 15 | Rail statistics |
| `pages/InfraBoardDashboard.test.tsx` | 14 | The page container |
| `components/InfraBoardDashboard/InfraSectionRouter.test.tsx` | 14 | Section routing |
| `pages/infra-board/rip-phases.catalog.test.ts` | 11 | The twelve-phase catalogue |
| `components/InfraBoardDashboard/FaseladderOverview.test.tsx` | 9 | Faseladder overview |
| `components/InfraBoardDashboard/Portfolio.test.tsx` | 9 | Portfolio view |
| `pages/infra-board/modes.config.test.ts` | 9 | Mode configuration |
| `components/InfraBoardDashboard/InfraCommandPalette.test.tsx` | 8 | Command palette |
| `pages/infra-board/rip-phase-counts.test.ts` | 7 | Phase counts |
| `components/InfraBoardDashboard/ProjectDetail.test.tsx` | 6 | Project detail |
| `components/InfraBoardDashboard/MijnDag.test.tsx` | 5 | The "Mijn Dag" section |

Coverage: `pages/infra-board` **99.64 / 97.2 / 100 / 100** —
the highest in the frontend — and `components/InfraBoardDashboard`
90.96 / 84.54 / 87.87 / 91.68.

The gap between those two rows is the usual one: the pure data and model
modules are exhaustively covered, while the components carry the
"critical interactions only" scoping used across the frontend.

---

## E2E

**None.** There is no Playwright spec that drives this board.

This is a gap rather than a decision. The PA cockpit work in the 21–22 August
window demonstrated concretely what unit tests cannot see on a board like this
one: a saved write that was a bare `return;`, a confirm that built an object and
discarded it, a panel hardcoded to empty, a resource fetched once at mount and
never again. Every one of those passed its component tests, because a component
test mocks the very seam that was broken.

The infra-board has the same shape — a section router, a command palette, data
panels reading through a provider — so it is exposed to the same class of
defect, and nothing currently would catch it.

If a spec is added, the PA cockpit's structure is the model to copy: drive mock
mode against the real store with no mocking, which is affordable precisely
because the fixtures are deterministic. See
[PA cockpit → Why mock mode is worth an E2E suite](pa-cockpit.md#why-mock-mode-is-worth-an-e2e-suite).
