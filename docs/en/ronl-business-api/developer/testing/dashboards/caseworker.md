---
component: RONL Business API
---

# Caseworker — tests

The caseworker portal is the oldest and largest board, and the one whose
end-to-end journeys exercise the full Operaton stack.

**Frontend: 43 files · 329 tests. E2E: 5 specs · 12 tests.**

---

## Frontend

The `CaseworkerDashboard/` directory is not only this board's: it is the
**shared section-component library**, reused across three of the four V2
dashboards. Changes there ripple, which is why it carries 185 tests across 26
files on its own.

| Area | Files | Tests |
|---|---:|---:|
| `components/CaseworkerDashboard` (shared section library) | 26 | 185 |
| `components/CaseworkerDashboardV2` | 15 | 116 |
| `pages/caseworker-v2` (`modes.config`) | 1 | 21 |
| `pages/CaseworkerDashboardV2.test.tsx` | 1 | 7 |

Largest files:

| File | Tests | Covers |
|---|---:|---|
| `CaseworkerDashboardV2/SectionRouter.test.tsx` | 28 | Section routing and the shell's state machine |
| `CaseworkerDashboardV2/regelsimulatie/simEngine.test.ts` | 22 | The deterministic budget-exhaustion simulator |
| `pages/caseworker-v2/modes.config.test.ts` | 21 | Mode configuration, a pure data module |
| `CaseworkerDashboard/TaskFormViewer.test.tsx` | 14 | Rendering and submitting an Operaton task form |
| `CaseworkerDashboard/IouFeedbackSection.test.tsx` | 10 | Feedback capture |
| `CaseworkerDashboard/IouGebruiksscenarioSection.test.tsx` | 10 | Usage-scenario section |
| `CaseworkerDashboard/ProfielSection.test.tsx` | 10 | Profile data |
| `CaseworkerDashboard/McpChatSection.test.tsx` | 9 | The MCP chat surface |
| `CaseworkerDashboard/ProcessStepsTimeline.test.tsx` | 9 | Process step timeline |

Coverage: `components/CaseworkerDashboard` 86.33%,
`components/CaseworkerDashboardV2` 81.27%, and the `regelsimulatie`
sub-directory 97.66%.

!!! note "The simulator carries a real performance budget"
    `simEngine.ts` must process the default 3,150-application population in
    under 250ms. That assertion does **not** run in the default suite — it
    lives in `simEngine.perf.test.ts` and runs via `npm run test:perf`, without
    file parallelism, as its own CI step. The reasoning is on
    [Overview](../overview.md#the-performance-budget).

---

## E2E

**Two specs, two tests** drive this board specifically:
`caseworker-journey.spec.ts` (the Kapvergunning roundtrip) and
`zorgtoeslag-journey.spec.ts` (a citizen submitting through a commercial
organisation, handled by the competent authority's caseworker).

Measured 30 August 2026 against `acc` at `15dfbf9`, as part of the full frontend
run: 27 tests, all passing, 1.9m.

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
| `tenant-isolation.spec.ts` | A real cross-tenant fixture — confirms a wrong-tenant caseworker does **not** see a task, and the right one does |

`tenant-isolation.spec.ts` is the empirical proof of the tenancy-scoping
behaviour described in
[Processes → Tenancy](../../../features/processes.md#tenancy) and
[Tasks → Visibility](../../../features/tasks.md#visibility): a task raised under
one tenant is visible only to that tenant's caseworker.

What the suite needs running, and why it fails fast rather than starting
anything itself, is on [E2E & live smoke](../e2e.md).
