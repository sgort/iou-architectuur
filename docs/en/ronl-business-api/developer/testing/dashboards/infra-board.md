---
component: RONL Business API
---

# Infra-board — tests

**Frontend: 17 files · 188 tests. E2E: 2 specs · 8 tests.**

The infra-board is well covered at the unit level — `src/pages/infra-board` is
the single best-covered area in the frontend at **99.64%** statements — and it
is the **only board with two Playwright specs**: one driving the shell, one
driving the work that happens inside it.

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

**Two specs, eight tests.** Measured 30 August 2026 against `acc` at `15dfbf9`
as part of the full frontend run: 27 tests, all passing, 1.9m.

| Spec | Tests | Covers |
|---|---:|---|
| `infra-board-journey.spec.ts` | 7 | The shell |
| `rip-r21-journey.spec.ts` | 1 | The work |

These eight are the largest per-board share of the frontend suite — see
[Coverage per board](../e2e.md#coverage-per-board) for how they sit against the
other nineteen.

**`infra-board-journey.spec.ts`** drives the board itself: opening on Mijn dag
with all three werkmodi available, each werkmodus reaching its own surface and
back, the rail carrying all twelve RIP phases with each opening its own detail,
every account/IOU/hulpmiddelen section rendering real content, the RIP archive
opening from its own rail entry rather than the IOU one, and the command palette
jumping straight to a section. One test is a full sweep asserting **no failed
request and no console error** across the board.

**`rip-r21-journey.spec.ts`** starts a RIP R2.1 process, works every user task,
and completes the phase. Its own header puts the division plainly: the first
spec covers the shell, this one covers the work. It signs in as
`test-infra-flevoland`, navigates the Faseladder rail to R2.1, and drives all
twelve tasks — the last of which now renders the
[signing panel](../../validsign-signing.md) rather than a form.

It carries a `test.skip(true, reason)` **inside** the test body, which skips the
run when its preconditions are not met and logs the reason first. It did not
skip in this measurement.

!!! warning "This page said *none* for six days"
    Both specs landed on **24 August 2026**. This page, its at-a-glance line and
    the testing overview's roadmap all continued to say the board had no
    end-to-end coverage through two subsequent documentation syncs. The specs
    were visible the whole time in `packages/frontend/e2e/`; nothing in a
    changelog-driven sync pointed at them, because neither release that added
    them was the one being documented.

    The lesson is narrow and worth stating: **a per-board page's E2E section
    cannot be derived from the release being synced.** It has to be re-derived
    from the spec directory, every time.
