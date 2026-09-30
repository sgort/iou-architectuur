---
component: RONL Business API
---

# Infra-board — tests

**Frontend: 18 files · 252 tests. E2E: 2 specs · 8 tests.**

The infra-board is well covered at the unit level — `src/pages/infra-board` is
at **100%** statements, functions and lines and 98.47% branches, the
best-covered substantial area in the frontend — and it is the **only board with
two Playwright specs**: one driving the shell, one driving the work that
happens inside it.

---

## Frontend

Re-derived on **30 September 2026** at `ae06c9e` (v2026.09.15). The frontend
package was measured the same day — 120 files, 1318 tests, all passing — but
Vitest's console reports only that total, so the counts below are taken from
the source, each test file parsed with its `.each` tables expanded; summed
over the whole package the method gives exactly the runner's 1318. The figures
this page carried before were derived on 30 August.

| Area | Files | Tests |
|---|---:|---:|
| `pages/infra-board` (data and pure logic) | 6 | 108 |
| `components/InfraBoardDashboard` | 11 | 126 |
| `pages/InfraBoardDashboard.test.tsx` | 1 | 18 |

!!! note "The phase swimlane's tests moved to `components/process/`"
    `PhaseSwimlane.test.tsx` lived in `components/InfraBoardDashboard/` until
    v2026.09.14, with 22 tests on 28 September. The caseworker's process view
    needed the same swimlane and the same phase stepper, so both components
    and their tests moved to the shared `components/process/` directory, where
    `PhaseSwimlane.test.tsx` now holds 38 and `PhaseStepper.test.tsx` 7. This
    board still uses both — `ProjectDetail` imports them from there — but they
    are counted once, on the [Caseworker](caseworker.md) page, rather than on
    both.

| File | Tests | Covers |
|---|---:|---|
| `pages/infra-board/infra-board.data.test.ts` | 34 | The board's data module |
| `components/InfraBoardDashboard/PhaseDetail.test.tsx` | 31 | Phase detail view |
| `pages/infra-board/rip-model.test.ts` | 26 | The RIP phase model |
| `components/InfraBoardDashboard/ProjectDetail.test.tsx` | 20 | Project detail, with the shared phase stepper and swimlane |
| `pages/InfraBoardDashboard.test.tsx` | 18 | The page container |
| `pages/infra-board/rail-stats.test.ts` | 15 | Rail statistics |
| `components/InfraBoardDashboard/SigningPanel.test.tsx` | 15 | The [signing panel](../../validsign-signing.md) an approval task renders |
| `components/InfraBoardDashboard/InfraSectionRouter.test.tsx` | 14 | Section routing |
| `pages/infra-board/rip-phases.catalog.test.ts` | 14 | The twelve-phase catalogue |
| `components/InfraBoardDashboard/FaseladderOverview.test.tsx` | 11 | Faseladder overview |
| `components/InfraBoardDashboard/Portfolio.test.tsx` | 11 | Portfolio view |
| `pages/infra-board/rip-phase-counts.test.ts` | 10 | Phase counts |
| `components/InfraBoardDashboard/InfraCommandPalette.test.tsx` | 9 | Command palette |
| `pages/infra-board/modes.config.test.ts` | 9 | Mode configuration |
| `components/InfraBoardDashboard/MijnDag.test.tsx` | 6 | The "Mijn Dag" section |
| `components/InfraBoardDashboard/InfraDock.test.tsx` | 4 | The dock |
| `components/InfraBoardDashboard/resolveSigningUrl.test.ts` | 4 | Resolving the signing ceremony's URL |
| `components/InfraBoardDashboard/InfraNoAccessPanel.test.tsx` | 1 | The no-access panel |

Coverage on 30 September: `pages/infra-board` **100 / 98.47 / 100 / 100**, and
`components/InfraBoardDashboard` 95.06 / 89.37 / 93.71 / 96.14 — up from
94.06 / 88.43 / 90.25 / 95.12 on 28 September, over twelve source files now
that `PhaseSwimlane.tsx` has moved out.

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
