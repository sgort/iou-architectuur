---
component: RONL Business API
---

# Infra-board — tests

**Frontend: 19 files · 278 tests**, including the shared signing panel.
**E2E: 2 specs · 8 tests** — 7 passed and 1 skipped on 7 November 2026, as on 3 and 9 October.

The infra-board is well covered at the unit level — `src/pages/infra-board` is
at **100%** statements, functions and lines and 98.74% branches, the
best-covered substantial area in the frontend — and its **two Playwright
specs** divide the board between them: one driving the shell, one driving the
work that happens inside it.

---

## Frontend

Measured on **12 November 2026** at `4e28ed7`, a tree identical to `main`
at `ad0fd62` (v2026.11.2): the frontend package ran 143 files and 1738 tests,
all passing, every per-file count the same as on 7 November for v2026.11.1, and the counts below are read from Vitest's JSON report of that
run.

**v2026.10.3 added 19 tests to this board and no file.** The project page
now draws its process through the shared ProcessView, with the legend, the
viewer's lanes and the task marks (`ProjectDetail.test.tsx` 21 → **27**), and
the portfolio keeps projects waiting between phases, from the finished
instances of every phase (`infra-board.data.test.ts` 34 → **45**,
`Portfolio.test.tsx` 11 → **12**, `pages/InfraBoardDashboard.test.tsx`
18 → **19**). The client for `GET /v1/rip/phases/completed` is tested in
`services/infra.api.test.ts`, which belongs to no board.

| Area | Files | Tests |
|---|---:|---:|
| `pages/infra-board` (data and pure logic) | 6 | 119 |
| `components/InfraBoardDashboard` | 9 | 115 |
| `pages/InfraBoardDashboard.test.tsx` | 1 | 19 |
| **`components/signing`** (the signing panel, shared with the caseworker inbox) | 3 | 25 |

!!! note "The signing panel moved to `components/signing/`, and is counted here once"
    Until v2026.10.0 `SigningPanel` and its tests lived in
    `components/InfraBoardDashboard/`. v2026.10.0 moved them to the shared
    `components/signing/`, behind a `useTaskSignature` hook that every task
    view asks whether a task signs through ValidSign, so the caseworker inbox
    renders the same panel — see the
    [signing feature](../../validsign-signing.md). The directory's tests are
    counted **once, on this page**, where the panel started, and not on the
    [Caseworker](caseworker.md) page as well:

    | File | Tests | Covers |
    |---|---:|---|
    | `signing/SigningPanel.test.tsx` | 16 | The panel an approval task renders in place of a form; since v2026.10.0 it tells its host once about a decline, so the task list can move on (15 on 30 September, in `InfraBoardDashboard/`) |
    | `signing/useTaskSignature.test.ts` | 5 | **New.** Loading until the signing spec arrives; no fetch without a task; no spec when the fetch fails or answers `success: false`, so the caller falls back to the form; and never the previous task's spec after switching tasks |
    | `signing/resolveSigningUrl.test.ts` | 4 | Resolving the signing ceremony's URL — moved unchanged |

    Coverage on 7 November, unchanged since 3 October: `components/signing`
    **93.1 / 88.75 / 95.65 / 96.11**, with `SigningPanel.tsx` at 85.93%
    branches and the other two files at 100 on all four.

!!! note "The phase swimlane's tests moved to `components/process/`"
    `PhaseSwimlane.test.tsx` lived in `components/InfraBoardDashboard/` until
    v2026.09.14, with 22 tests on 28 September. The caseworker's process view
    needed the same swimlane and the same phase stepper, so both components
    and their tests moved to the shared `components/process/` directory, where
    `PhaseSwimlane.test.tsx` now holds 48 and `PhaseStepper.test.tsx` 7. Since
    v2026.10.3 this board draws its process through `ProcessView`, which wraps
    both, and `process-view-guard.test.ts` keeps any board from importing the
    swimlane directly. The directory is counted once, on the
    [Caseworker](caseworker.md) page, rather than on both.

| File | Tests | Covers |
|---|---:|---|
| `pages/infra-board/infra-board.data.test.ts` | 45 | The board's data module — since v2026.10.3 the waiting rows built from finished phases (34 on 9 October) |
| `components/InfraBoardDashboard/PhaseDetail.test.tsx` | 31 | Phase detail view |
| `pages/infra-board/rip-model.test.ts` | 26 | The RIP phase model |
| `components/InfraBoardDashboard/ProjectDetail.test.tsx` | 27 | Project detail, since v2026.10.3 drawn through ProcessView with the viewer's marks, a waiting project's finished phase, a refresh of the open tasks after a claim, and the shared signing panel through `useTaskSignature` (21 on 9 October) |
| `pages/InfraBoardDashboard.test.tsx` | 19 | The page container (18 on 9 October) |
| `pages/infra-board/rail-stats.test.ts` | 15 | Rail statistics |
| `components/InfraBoardDashboard/InfraSectionRouter.test.tsx` | 14 | Section routing |
| `pages/infra-board/rip-phases.catalog.test.ts` | 14 | The twelve-phase catalogue |
| `components/InfraBoardDashboard/FaseladderOverview.test.tsx` | 11 | Faseladder overview |
| `components/InfraBoardDashboard/Portfolio.test.tsx` | 12 | Portfolio view, with waiting projects (11 on 9 October) |
| `pages/infra-board/rip-phase-counts.test.ts` | 10 | Phase counts |
| `components/InfraBoardDashboard/InfraCommandPalette.test.tsx` | 9 | Command palette |
| `pages/infra-board/modes.config.test.ts` | 9 | Mode configuration |
| `components/InfraBoardDashboard/MijnDag.test.tsx` | 6 | The "Mijn Dag" section |
| `components/InfraBoardDashboard/InfraDock.test.tsx` | 4 | The dock |
| `components/InfraBoardDashboard/InfraNoAccessPanel.test.tsx` | 1 | The no-access panel |

Coverage on 7 November: `pages/infra-board` **100 / 98.74 / 100 / 100**
(98.47 branches on 9 October), and `components/InfraBoardDashboard`
95.43 / 90.21 / 92.59 / 95.95 (95.34 / 89.91 / 92.59 / 95.85 on 9 October),
over ten source files. `ProjectDetail.tsx` reads 89.02% branches and 83.33%
functions; `Portfolio.tsx` 100% branches.

The gap between those two rows is the usual one: the pure data and model
modules are exhaustively covered, while the components carry the
"critical interactions only" scoping used across the frontend.

---

## E2E

**Two specs, eight tests.** Measured **7 November 2026** as part of the full
frontend run against the developer's already-running local stack: 56 passed,
5 skipped, 6.4m. Before that, 9 October 2026: 42 passed, 5 skipped, 2.6m;
3 October 2026: 27 passed, 1 skipped, 2.8m; and 30 August 2026 against `acc`
at `15dfbf9`: all 27 passing, 1.9m.

| Spec | Tests | 7 November | Covers |
|---|---:|---|---|
| `infra-board-journey.spec.ts` | 7 | 7 passed | The shell |
| `rip-r21-journey.spec.ts` | 1 | **skipped, by its own guard** | The work |

These eight are still the largest share of any board in the frontend suite —
see [Coverage per board](../e2e.md#coverage-per-board) for how they sit
against the other fifty-three. Two specs new since 9 October also reach this
board without belonging to it alone: `process-view.spec.ts` checks the
project page against the shared ProcessView rules and, on a controlled R2.4
instance, the *jouw taak* / *geclaimd* / open marks and the parallel bars
(two of its three tests, both passing), and `accessibility.spec.ts` scans the
Infra-board for Flevoland (one of its ten, passing).

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

It carries two `test.skip(true, reason)` calls **inside** the test body, which
skip the run when its preconditions are not met and log the reason first. It
did not skip on 30 August, which predates both. **On 3 October it did**, and
again on 9 October, and said why before creating anything:

```text
[rip-r21-journey] SKIPPED — local dev stack signs with the real ValidSign
(VALIDSIGN_STUB_MODE=false), and this journey will not request a binding
signature. Nothing was created — the refusal happens before
POST /task/:id/package. Run it against a target where VALIDSIGN_STUB_MODE=true.
```

**On 7 November it skipped by its other guard**: an R2.1 instance was
already running on the local engine, and the spec cannot tell a foreign
instance from its own — a fallback-started R2.1 carries no project number —
so it refuses rather than risk working someone else's process to completion.

That is the guard doing its job, not a gap in the run: a stack configured for
real signing cannot complete the journey's approval task without a binding
signature, and the spec refuses before it sends a package. So the R2.1 work
has not been driven end to end by these pages since 30 August; that needs a
run against a target in stub mode.

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
