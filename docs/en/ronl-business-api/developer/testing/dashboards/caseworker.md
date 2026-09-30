---
component: RONL Business API
---

# Caseworker — tests

The caseworker portal is the oldest and largest board, and the one whose
end-to-end journeys exercise the full Operaton stack.

**Frontend: 52 files · 571 tests**, including the shared process view.
**E2E: 3 specs** — 2 tests measured, and `thuisbatterij-journey` not yet.

---

## Frontend

Re-derived on **30 September 2026** at `ae06c9e` (v2026.09.15). The frontend
package was measured the same day — 120 files, 1318 tests, all passing — but
Vitest's console reports only that total, so the per-file and per-area counts
below are taken from the source, each test file parsed with its `.each`
tables expanded. Summed over the whole package the method gives exactly the
runner's 1318. The figures this page carried before were derived on
30 August.

The `CaseworkerDashboard/` directory is not only this board's: it is the
**shared section-component library**, reused across three of the four V2
dashboards. Changes there ripple, which is why it carries 231 tests across 26
files on its own. `components/process/` is shared the same way: the
caseworker's process view is built from it, and the Infra-board's project
detail draws its phase stepper and swimlane with the same components.

| Area | Files | Tests |
|---|---:|---:|
| `components/CaseworkerDashboard` (shared section library) | 26 | 231 |
| `components/CaseworkerDashboardV2` (including `regelsimulatie/`) | 16 | 186 |
| **`components/process`** (the process view, shared with the Infra-board) | 8 | 119 |
| `pages/caseworker-v2` (`modes.config`) | 1 | 21 |
| `pages/CaseworkerDashboardV2.test.tsx` | 1 | 14 |

Largest files outside `components/process/`:

| File | Tests | Covers |
|---|---:|---|
| `CaseworkerDashboardV2/SectionRouter.test.tsx` | 28 | Section routing and the shell's state machine |
| `CaseworkerDashboardV2/TakenInbox.test.tsx` | 28 | The task list — filters, the Awb-phase hint, the *Procesgegevens* bar and the process view a selected task opens (19 on 28 September) |
| `CaseworkerDashboardV2/regelsimulatie/simEngine.test.ts` | 22 | The deterministic budget-exhaustion simulator |
| `pages/caseworker-v2/modes.config.test.ts` | 21 | Mode configuration, a pure data module |
| `CaseworkerDashboard/McpChatSection.test.tsx` | 20 | The MCP chat surface |
| `CaseworkerDashboard/IouGebruiksscenarioSection.test.tsx` | 16 | Usage-scenario section |
| `CaseworkerDashboard/RegelCatalogus.test.tsx` | 16 | The rule catalogue |
| `CaseworkerDashboardV2/RegelSimulatie.test.tsx` | 16 | The rule-simulation section |
| `CaseworkerDashboard/GereedschapSection.test.tsx` | 15 | Tools section |
| `CaseworkerDashboardV2/regelsimulatie/SimTweak.test.tsx` | 15 | Adjusting the simulation's parameters |
| `CaseworkerDashboard/TaskFormViewer.test.tsx` | 14 | Rendering and submitting an Operaton task form |
| `pages/CaseworkerDashboardV2.test.tsx` | 14 | The page container |

**The process view** — new in v2026.09.14, all but one file new:

| File | Tests | Covers |
|---|---:|---|
| `process/PhaseSwimlane.test.tsx` | 38 | The swimlane renderer, moved here from `InfraBoardDashboard/` (22 tests there): collision stacking, the caseworker additions, readable gateway labels (`edgeLabelText`) and the roomier density |
| `process/laneSteps.test.ts` | 19 | Pure step-list logic: lane metadata, which lanes are the user's, the trail and the hand-overs between lanes |
| `process/ProcessLaneSteps.test.tsx` | 13 | *Processtappen per rol* — the steps grouped by role |
| `process/ProcessOverlay.test.tsx` | 13 | The whole-process overlay with its stepper and swimlane |
| `process/useTaskProcessContext.test.ts` | 11 | Loading a task's process context across the call chain |
| `process/ProcessWhere.test.tsx` | 9 | *Waar sta ik* — the Awb phase and the step on the stepper |
| `process/processContext.test.ts` | 9 | `buildProcessContext` — splicing a sub-process's history into its parent's, in engine order |
| `process/PhaseStepper.test.tsx` | 7 | The phase stepper, shared with the Infra-board |

Coverage on 30 September (statements / branches):
`components/CaseworkerDashboard` **93.83 / 94.93**,
`components/CaseworkerDashboardV2` **93.03 / 93.1**, the `regelsimulatie`
sub-directory 98.33 / 88.59, and `components/process` **99.56 / 91.96**. The
first two rose by several points in v2026.09.15's branch-margin work; see
[Coverage](../coverage.md#frontend-by-area).

!!! note "The simulator carries a real performance budget"
    `simEngine.ts` must process the default 3,150-application population in
    under 250ms. That assertion does **not** run in the default suite — it
    lives in `simEngine.perf.test.ts` and runs via `npm run test:perf`, without
    file parallelism, as its own CI step. The reasoning is on
    [Overview](../overview.md#the-performance-budget).

---

## E2E

**Three specs** drive this board specifically:
`caseworker-journey.spec.ts` (the Kapvergunning roundtrip),
`zorgtoeslag-journey.spec.ts` (a citizen submitting through a commercial
organisation, handled by the competent authority's caseworker) and
`thuisbatterij-journey.spec.ts` (a Thuisbatterij subsidy application reviewed
by a caseworker, new in v2026.09.11).

The first two were measured on 30 August 2026 against `acc` at `15dfbf9`, as
part of the full frontend run: 27 tests, all passing, 1.9m — one test each.
`thuisbatterij-journey` arrived after that run and has not been measured by
these pages; the suite was not re-run on 30 September. See
[E2E & live smoke](../e2e.md#coverage-per-board).

All three now accept the task names linked-data-explorer's swimlane redesign
introduced — *Beoordeling behandelaar: …* and *Fase 6: Aanvrager informeren
over besluit* — as well as the old English ones, so they pass against either
deployment: `thuisbatterij-journey` since v2026.09.12, the other two since
v2026.09.14. Read from the specs at `ae06c9e`, not run.

!!! note "The other three specs measured here before are cross-cutting, not caseworker"
    This section used to read *"five specs, twelve tests"*, counting
    `login-redirect`, `protected-route`, `tenant-isolation` and `smoke` towards
    this board. Those four cut across every board and belong to none — they are
    now attributed as such in
    [Coverage per board](../e2e.md#coverage-per-board), which is why this figure
    dropped without any test being removed.

That run was against the corrected `e2e-fixtures` BPMNs redeployed from the
Linked Data Explorer, which confirms that chain end to end.

| Spec | Covers |
|---|---|
| `smoke.spec.ts` | App loads at `/`, `LoginChoice` renders, no console errors |
| `login-redirect.spec.ts` | One test per role (citizen / caseworker / infra / woo / PA) against the Flevoland tenant, driving the real Keycloak hosted login — 5 tests |
| `protected-route.spec.ts` | Cross-role `ProtectedRoute` redirect behaviour — 2 tests |
| `caseworker-journey.spec.ts` | A citizen submits a real Kapvergunning request via Operaton/DMN; the caseworker claims and completes both resulting tasks — a genuinely finalised roundtrip |
| `zorgtoeslag-journey.spec.ts` | A second deep journey — a commercial-org citizen submits a Zorgtoeslag claim, and the `toeslagen` caseworker completes both steps |
| `thuisbatterij-journey.spec.ts` | A third deep journey — a citizen applies for a Thuisbatterij subsidy, the six-decision DRD evaluates, and the caseworker reviews the resulting task |
| `tenant-isolation.spec.ts` | A real cross-tenant fixture — confirms a wrong-tenant caseworker does **not** see a task, and the right one does. Since v2026.09.14 it matches the review task by its English or Dutch name, so the negative check cannot pass on a name that no longer exists |

`tenant-isolation.spec.ts` is the empirical proof of the tenancy-scoping
behaviour described in
[Processes → Tenancy](../../../features/processes.md#tenancy) and
[Tasks → Visibility](../../../features/tasks.md#visibility): a task raised under
one tenant is visible only to that tenant's caseworker.

What the suite needs running, and why it fails fast rather than starting
anything itself, is on [E2E & live smoke](../e2e.md).
