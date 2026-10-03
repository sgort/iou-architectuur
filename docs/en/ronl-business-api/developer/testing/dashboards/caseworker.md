---
component: RONL Business API
---

# Caseworker — tests

The caseworker portal is the oldest and largest board, and the one whose
end-to-end journeys exercise the full Operaton stack.

**Frontend: 54 files · 598 tests**, including the shared process view.
**E2E: 3 specs · 3 tests**, all passing on 3 October 2026.

---

## Frontend

Re-derived on **3 October 2026** at `0625d48` (v2026.10.0). The frontend
package was measured the same day — 124 files, 1378 tests, all passing — but
Vitest's console reports only that total, so the per-file and per-area counts
below are taken from the source, each test file parsed with its `.each`
tables expanded. Summed over the whole package the method gives exactly the
runner's 1378.

The `CaseworkerDashboard/` directory is not only this board's: it is the
**shared section-component library**, reused across three of the four V2
dashboards. Changes there ripple, which is why it carries 244 tests across 28
files on its own. `components/process/` is shared the same way: the
caseworker's process view is built from it, and the Infra-board's project
detail draws its phase stepper and swimlane with the same components.

!!! note "The signing panel is shared too, and counted on the Infra-board page"
    Since v2026.10.0 the caseworker inbox renders the same
    [signing panel](../../validsign-signing.md) as the Infra-board:
    `SigningPanel` and `useTaskSignature` moved to the shared
    `components/signing/`, and `TakenInbox` asks `useTaskSignature` whether a
    claimed task signs through ValidSign before it renders a form. That
    directory's **3 files and 25 tests** are counted once, on
    [Infra-board](infra-board.md#frontend), where the panel started — not
    here as well. What this board adds is in `TakenInbox.test.tsx`, below.

| Area | Files | Tests |
|---|---:|---:|
| `components/CaseworkerDashboard` (shared section library) | 28 | 244 |
| `components/CaseworkerDashboardV2` (including `regelsimulatie/`) | 16 | 193 |
| **`components/process`** (the process view, shared with the Infra-board) | 8 | 123 |
| `pages/caseworker-v2` (`modes.config`) | 1 | 24 |
| `pages/CaseworkerDashboardV2.test.tsx` | 1 | 14 |

**Besluitvorming** — new in v2026.10.0, in the shared section library:

| File | Tests | Covers |
|---|---:|---|
| `CaseworkerDashboard/BesluitOverzichtSection.test.tsx` | 7 | *Lopende* and *Afgeronde besluiten*: refused without a besluit role, running besluiten with their current step, completed ones with their outcome, a besluit opened to its details with the empty ones left out, and a retry when the list cannot be loaded |
| `CaseworkerDashboard/BesluitStartSection.test.tsx` | 3 | *Besluit voorbereiden*: refused without `besluit-indiener`, the process started and confirmed, and a failed start reported |

`pages/caseworker-v2/modes.config.test.ts` gained three with them — the two
besluit lists in the tenant sections, and Flevoland offering the start to its
indieners — and `CaseworkerDashboardV2/SectionRouter.test.tsx` three, one per
besluit section.

Largest files outside `components/process/`:

| File | Tests | Covers |
|---|---:|---|
| `CaseworkerDashboardV2/TakenInbox.test.tsx` | 32 | The task list — filters, the phase hint, the *Procesgegevens* bar, the process view a selected task opens, and since v2026.10.0 the signing panel in place of the form for a task that must be signed, nothing while the signing spec is still loading, the fallback form when it cannot be fetched, and a refreshed list after a decline (28 on 30 September) |
| `CaseworkerDashboardV2/SectionRouter.test.tsx` | 31 | Section routing and the shell's state machine |
| `pages/caseworker-v2/modes.config.test.ts` | 24 | Mode configuration, a pure data module, read against the real `tenants.json` |
| `CaseworkerDashboardV2/regelsimulatie/simEngine.test.ts` | 22 | The deterministic budget-exhaustion simulator |
| `CaseworkerDashboard/McpChatSection.test.tsx` | 20 | The MCP chat surface |
| `CaseworkerDashboard/IouGebruiksscenarioSection.test.tsx` | 17 | Usage-scenario section |
| `CaseworkerDashboard/RegelCatalogus.test.tsx` | 16 | The rule catalogue |
| `CaseworkerDashboardV2/RegelSimulatie.test.tsx` | 16 | The rule-simulation section |
| `CaseworkerDashboard/GereedschapSection.test.tsx` | 15 | Tools section |
| `CaseworkerDashboardV2/regelsimulatie/SimTweak.test.tsx` | 15 | Adjusting the simulation's parameters |
| `CaseworkerDashboard/TaskFormViewer.test.tsx` | 14 | Rendering and submitting an Operaton task form |
| `pages/CaseworkerDashboardV2.test.tsx` | 14 | The page container |

**The process view** — new in v2026.09.14, all but one file new then:

| File | Tests | Covers |
|---|---:|---|
| `process/PhaseSwimlane.test.tsx` | 38 | The swimlane renderer, moved here from `InfraBoardDashboard/` (22 tests there): collision stacking, the caseworker additions, readable gateway labels (`edgeLabelText`) and the roomier density |
| `process/laneSteps.test.ts` | 19 | Pure step-list logic: lane metadata, which lanes are the user's, the trail and the hand-overs between lanes |
| `process/ProcessLaneSteps.test.tsx` | 13 | *Processtappen per rol* — the steps grouped by role |
| `process/ProcessOverlay.test.tsx` | 13 | The whole-process overlay with its stepper and swimlane |
| `process/ProcessWhere.test.tsx` | 12 | *Waar sta ik* — the phase and the step on the stepper; since v2026.10.0 nothing for a process without phases, and a process's own declared phases numbered and captioned under its own label (9 on 30 September) |
| `process/useTaskProcessContext.test.ts` | 11 | Loading a task's process context across the call chain |
| `process/processContext.test.ts` | 10 | `buildProcessContext` — splicing a sub-process's history into its parent's, in engine order, and carrying a declared phase set (9 on 30 September) |
| `process/PhaseStepper.test.tsx` | 7 | The phase stepper, shared with the Infra-board |

Coverage on 3 October (statements / branches):
`components/CaseworkerDashboard` **93.86 / 94.45**,
`components/CaseworkerDashboardV2` **92.81 / 93.52**, the `regelsimulatie`
sub-directory 98.33 / 88.59, and `components/process` **99.16 / 91.18**.
`BesluitOverzichtSection.tsx` is the lowest file in the frontend by branches,
at **80.43%** — half a point above the floor — and `process/phaseSet.ts`, the
phase set a process declares, is at 83.33%; see
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

**All three were measured on 3 October 2026**, as part of the full frontend
run against the developer's already-running local stack (27 passed,
1 skipped, 2.8m): **one test each, all passing** — `caseworker-journey` in 24.5s,
`thuisbatterij-journey` in 8.4s and `zorgtoeslag-journey` in 6.1s. It is the
first measurement of `thuisbatterij-journey` on these pages, which carried
it as *not yet measured* from v2026.09.11 until now. The previous run of the
other two was on 30 August. See
[E2E & live smoke](../e2e.md#coverage-per-board).

All three accept the task names linked-data-explorer's swimlane redesign
introduced — *Beoordeling behandelaar: …* and *Fase 6: Aanvrager informeren
over besluit* — as well as the old English ones, so they pass against either
deployment: `thuisbatterij-journey` since v2026.09.12, the other two since
v2026.09.14. No spec changed in v2026.10.0.

No spec drives **Besluitvorming** yet: the *Besluit voorbereiden* start and
the *Lopende* and *Afgeronde besluiten* lists are covered by the unit tests
above only, and so is the signing panel in the caseworker inbox.

!!! note "The other three specs measured here before are cross-cutting, not caseworker"
    This section used to read *"five specs, twelve tests"*, counting
    `login-redirect`, `protected-route`, `tenant-isolation` and `smoke` towards
    this board. Those four cut across every board and belong to none — they are
    now attributed as such in
    [Coverage per board](../e2e.md#coverage-per-board), which is why this figure
    dropped without any test being removed.

The 30 August run was against the corrected `e2e-fixtures` BPMNs redeployed
from the Linked Data Explorer, which confirmed that chain end to end; the
3 October run passed the same `globalSetup` gates, which refuse to start
unless those fixtures are deployed.

| Spec | Covers |
|---|---|
| `smoke.spec.ts` | App loads at `/`, `LoginChoice` renders, no console errors |
| `login-redirect.spec.ts` | One test per role (citizen / caseworker / infra / woo / PA) against the Flevoland tenant, driving the real Keycloak hosted login — 5 tests |
| `protected-route.spec.ts` | Cross-role `ProtectedRoute` redirect behaviour, and DigiD login still working after an unauthenticated visit to a protected route — 3 tests |
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
