---
component: RONL Business API
---

# BPMN Design Criteria

This page documents design constraints and conventions that apply when authoring BPMN processes and DMN decisions for deployment in the RONL Business API platform. Following these criteria ensures correct runtime behaviour and prevents issues in the citizen portal and caseworker interface.

---

## BusinessRuleTask: `camunda:mapDecisionResult`

A `BusinessRuleTask` that calls a DMN decision must declare how the engine hands the decision output to the process. For a decision with one output column that is the `camunda:mapDecisionResult` attribute together with `camunda:resultVariable`; for a decision with several output columns it is one `camunda:outputParameter` per column, and no result variable at all.

Operaton supports four mapping modes:

| Value | Returns | Use when |
|---|---|---|
| `singleEntry` | The value of a single output column from a single matched rule | The decision has one output column and a hit policy that guarantees at most one result (`UNIQUE`, `FIRST`, `ANY`) |
| `singleResult` | All output columns of a single matched rule as a `Map` object | Not with a result variable — read a multi-output decision through [output parameters](#multi-output-decisions-one-output-parameter-per-column) instead |
| `collectEntries` | A `List` of values from a single output column across all matched rules | The decision uses `COLLECT` and you need all values from one column |
| `resultList` | A `List` of `Map` objects, one per matched rule | The decision uses `COLLECT` and you need all columns of all matched rules |

### Why this matters

The mapping mode determines the Java type stored in the process variable. If the wrong mode is used, the value stored is not a primitive (`String`, `Integer`, `Boolean`) but a complex object (`Map`, `List`). Any downstream expression, script task, or UI component that expects a simple value will fail silently or display `[object Object]`.

### `singleEntry` — the default for single-output decisions

For decisions with one output column and a `UNIQUE` hit policy, always use `singleEntry`. This stores the raw value directly in the result variable.

```xml
<bpmn:businessRuleTask
  id="Task_AssessPermit"
  name="Assess tree felling permit"
  camunda:resultVariable="permitDecision"
  camunda:decisionRef="TreeFellingDecision"
  camunda:mapDecisionResult="singleEntry">
```

The process variable `permitDecision` will contain the string `"Permit"` or `"Reject"` directly, usable in gateway conditions and script tasks without any unwrapping.

### Multi-output decisions: one output parameter per column

For a decision with several output columns, leave out `camunda:resultVariable` and `camunda:mapDecisionResult`, and give the task one `camunda:outputParameter` per output column that the process needs. Each reads its column from the decision result. `HrOnboardingProcess` (`examples/organizations/flevoland/HrOnboardingProcess.bpmn`) does this for the three outputs of `EmployeeRoleAssignment`:

```xml
<bpmn:businessRuleTask id="Task_DetermineRoles" name="Determine roles" camunda:decisionRef="EmployeeRoleAssignment">
  <bpmn:extensionElements>
    <camunda:inputOutput>
      <camunda:outputParameter name="assignedRoles">${decisionResult.getSingleResult().getEntry("assignedRoles")}</camunda:outputParameter>
      <camunda:outputParameter name="candidateGroups">${decisionResult.getSingleResult().getEntry("candidateGroups")}</camunda:outputParameter>
      <camunda:outputParameter name="accessLevel">${decisionResult.getSingleResult().getEntry("accessLevel")}</camunda:outputParameter>
    </camunda:inputOutput>
  </bpmn:extensionElements>
  ...
</bpmn:businessRuleTask>
```

Each output is then a plain `String`, `Boolean` or `Integer` process variable, usable directly in gateway conditions, forms and script tasks. The variable may be named differently from its column: `AwbShellProcess` maps the `legalBasis` column of `ArchivesActRetention` to `archivingLegalBasis`. As with `singleEntry`, the decision needs a hit policy that yields a single result.

`AwbShellProcess` maps only the column it branches on: `Task_Phase3_Completeness` calls `AwbCompletenessCheck` and maps `isComplete` through an output parameter, and `Gateway_Complete` tests `${isComplete == true}` and `${isComplete == false}`.

### Why not `singleResult` with a result variable

`camunda:mapDecisionResult="singleResult"` with a `camunda:resultVariable` stores the whole matched rule as one variable: a Java-serialised `java.util.HashMap`. A REST read that deserialises the process variables can write that object back, so concurrent reads of the same instance collide with `ENGINE-03005`, Operaton's optimistic-locking failure ([sgort/linked-data-explorer#273](https://github.com/sgort/linked-data-explorer/issues/273)). The example processes were rewritten to output parameters for that reason (`f3117dd`). The map is also no use where a simple value is expected: a gateway has to reach into it by key, and a frontend that renders it with `String(value)` shows `[object Object]`.

A script task that only copies entries out of the map into separate variables is unnecessary: the output parameters produce those variables directly, without the map ever being stored.

---

## Gateway conditions and variable types

Gateway `conditionExpression` values must match the actual type of the process variable being tested.

| Variable type | Correct expression | Incorrect |
|---|---|---|
| `String` | `${permitDecision == "Permit"}` | `${permitDecision == true}` |
| `Boolean` | `${isComplete == true}` or `${isComplete}` | `${isComplete == "true"}` |
| `Integer` | `${treeDiameter > 30}` | `${treeDiameter > "30"}` |

An output of a multi-output decision, mapped through an output parameter, is one of these types and is tested the same way. Do not branch on a field of a `Map` variable (`${completenessResult.isComplete == true}`): it needs the map stored, which is the pattern to avoid — see [Why not `singleResult` with a result variable](#why-not-singleresult-with-a-result-variable).

---

## Process variable naming conventions

All process variables set by the RONL Business API platform follow these conventions:

| Convention | Example | Reason |
|---|---|---|
| camelCase | `permitDecision`, `treeDiameter` | Consistent with JavaScript and Java conventions |
| No underscores in names used for `processVariables` filtering | `municipality` not `tenant_id` | Operaton's `processVariables` query filter uses `_` as a separator: `municipality_eq_utrecht` |
| Tenant context variables reserved | `municipality`, `initiator`, `assuranceLevel`, `applicantId` | Injected automatically by `tenant.middleware.ts`; do not reuse these names in DMN outputs |

---

## Tenant context variables

The backend middleware automatically injects the following variables into every process instance at start time. These must not be overwritten by DMN outputs or script tasks.

| Variable | Type | Source | Value |
|---|---|---|---|
| `municipality` | `String` | JWT `municipality` claim | e.g. `utrecht` |
| `initiator` | `String` | JWT `sub` claim | Keycloak user ID |
| `applicantId` | `String` | JWT `sub` claim | Same as `initiator`; used for history queries |
| `assuranceLevel` | `String` | JWT `loa` claim | `laag`, `midden`, or `hoog` |

These variables are available in all process expressions and DMN input columns. The `municipality` variable is used by the task queue to filter tasks to the correct tenant.

Two more variables are stamped by the backend, never by a process: `edocsAuthor` (the employee's e-mail, or username) and `edocsAuthorName` (display name), set from the caller's token when a staff member starts a process or completes a task. Background eDOCS archiving reads them to title documents "namens …". Together with `municipality`, `originTenantId` and `applicantId` they are reserved (`RESERVED_PROCESS_VARIABLES` in `auth/tenant-access.ts`): a task completion that carries one is refused, a `/v1` start drops a sent `edocsAuthor`/`edocsAuthorName`, and an M2M start that carries one is refused. Do not use these names for your own variables.

---

## `camunda:historyTimeToLive`

Every process definition must declare `camunda:historyTimeToLive` on the `<bpmn:process>` element. Without it, Operaton logs a warning on deployment and may refuse deployment depending on engine configuration.

```xml
<bpmn:process
  id="AwbShellProcess"
  name="AWB General Administrative Law Act - Generic Process"
  isExecutable="true"
  camunda:historyTimeToLive="365">
```

Recommended values:

| Context | Value | Rationale |
|---|---|---|
| AWB citizen processes | `365` | One year; aligns with Awb appeal and audit requirements |
| Short-lived subprocess | `180` | Six months for intermediate processes with no independent legal value |
| Development / test | `30` | Avoids accumulation of test instances in Operaton Cockpit |

---

## Lanes and phase markers: the caseworker process view

The caseworker board shows where an open task stands in its process — the phase stepper ("Waar sta ik"), the steps per role, and the whole process as a swimlane — only for processes whose deployed BPMN carries the information. The backend reads it with `parseSwimlane()` in `packages/backend/src/rip-swimlane/bpmn-swimlane.ts`, served by `GET /v1/process/definition/key/:key/swimlane`; nothing about a process is configured anywhere else.

The stepper shows one of two phase schemes, and a process uses exactly one: the Awb phases, marked with [`ronl:awbPhase`](#ronlawbphase), or phases the process declares itself, marked with [`ronl:phase`](#a-processs-own-phases-ronlphases-ronlphaselabel-ronlphase). The model the endpoint returns carries the scheme as `phaseSet` (`scheme` `awb` or `bpmn`, a `label`, and the ordered `phases`) and every node's phase code as `phase`; both are absent when the process has no valid marker.

### Lanes

- **Without a `laneSet`, there is no process view.** The task keeps the flat list of steps it had before.
- **Put the user tasks in the lanes.** A lane's roles are derived from the `candidateGroups` of the user tasks drawn in it (its `flowNodeRef`s), never configured. A lane with no user task has no roles, so it cannot be recognised as the caseworker's.
- **`candidateGroups` must be literals.** Comma-separated group names are read; an expression (`${…}` or `#{…}`) names no group until runtime and is dropped.
- Lanes are ordered by the `y` of their shape in the diagram; node positions are recomputed, not read from the diagram.

### `ronl:awbPhase`

Declare the namespace on `<bpmn:definitions>` and mark the nodes where a phase begins:

```xml
<bpmn:definitions
  xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
  xmlns:ronl="http://ronl.nl/schema/1.0"
  ...>
  <bpmn:process id="AwbShellProcess" ...>
    <bpmn:userTask id="Task_Phase6_Notify"
      name="Fase 6: Aanvrager informeren over besluit (Awb 3:6)"
      camunda:formRef="awb-notify-applicant"
      camunda:candidateGroups="caseworker"
      ronl:documentRef="example_treefelling_beschikking"
      ronl:awbPhase="6">
```

Any element in the list of flow-node types below can carry a marker — in `AwbShellProcess` they sit on the start event, a script task, business-rule tasks, the call activity, a user task and two gateways.

| Value | Stepper label |
|---|---|
| `1` | Rechtsbetrekking |
| `2` | Ontvangst |
| `3` | Ontvankelijkheid |
| `4+5` | Behandeling en besluit |
| `6` | Bekendmaking |
| `7` | Betaling |
| `8` | Ketenproces |
| `archivering` | Archivering |

The values are exactly those of `AWB_PHASES` in `@ronl/shared`. Phases 4 and 5 are one step, because the kapvergunning subprocess handles treatment and decision together. **Any other value is ignored without a warning**, so a typo such as `4-5` or `Archivering` leaves the node unmarked.

- **An unmarked node inherits.** It takes the latest phase among its forward predecessors, so a join after an optional step (payment) lands in the later phase. Back edges — the flows that close a rework loop — are excluded, so a loop cannot pull an earlier step into a later phase. Marking the first node of each phase is therefore enough.
- **No markers, no stepper.** A process with no valid marker gets no phases, and the board hides the stepper. A task in an unmarked subprocess takes the phase of the call activity that started it, walking up the call chain.

On the board the eyebrow names the legal phase number, *Waar sta ik · Awb-fase 4+5 · stap 4 van 8*, and the caption under the stepper reads *Fase 4+5 · Behandeling en besluit*. Archiving has no phase number: the eyebrow names it (*Awb-fase Archivering*) and the caption reads *Archiefwet · Archivering*.

### A process's own phases: `ronl:phases`, `ronl:phaseLabel`, `ronl:phase`

A process that does not follow the Awb declares its phases on `<bpmn:process>` and marks nodes with `ronl:phase`. *Besluitvorming onder gedelegeerde bevoegdheid* does this:

```xml
<bpmn:process id="GedelegeerdBesluitProcess"
  name="Besluitvorming onder gedelegeerde bevoegdheid"
  ronl:phases="voorbereiding:Voorbereiding;toetsing:Advies en toetsing;memorandum:Memorandum;ondertekening:Ondertekening;escalatie:Escalatie;registratie:Registratie en archivering"
  ronl:phaseLabel="Fase"
  ...>
  <bpmn:startEvent id="StartEvent_Besluit" name="Besluit voorbereiden" ronl:phase="voorbereiding">
  ...
  <bpmn:userTask id="Task_AdviesToetsing" name="Advies en toetsing" ronl:phase="toetsing" ...>
```

| Attribute | On | Meaning |
|---|---|---|
| `ronl:phases` | `<bpmn:process>` | The phases in order, as `code:Name` entries separated by `;` |
| `ronl:phaseLabel` | `<bpmn:process>` | The word before a phase's position, `Fase` when absent |
| `ronl:phase` | a flow node | The code of the phase that begins at this node |

- **The order of `ronl:phases` is the stepper's order**, and a phase is referred to by its position: the stepper labels the second phase *Fase 2*, the eyebrow reads *Waar sta ik · Fase 2 · stap 2 van 6*, and the caption *Fase 2 · Advies en toetsing*. The codes are identifiers and never appear on screen.
- **An unusable entry is skipped, not guessed at**: one without a code or a name, or one repeating an earlier code. Only the first `:` separates code from name, so a name may itself contain a colon. When no usable entry remains, the process is read as an Awb process.
- **A marker must name a declared code.** A `ronl:phase` value that is not in `ronl:phases` is ignored without a warning, like an unknown `ronl:awbPhase` value.
- **The two schemes never mix.** Once `ronl:phases` declares a usable phase, `ronl:awbPhase` is not read anywhere in the process; without it, `ronl:phase` is not read.
- Inheritance, rework loops, subprocesses and "no markers, no stepper" work as for `ronl:awbPhase` above, so marking the first node of each phase is enough.

### Other attributes the view reads

| Element or attribute | Shown as |
|---|---|
| `scriptTask` | A step of its own kind (script) |
| `businessRuleTask` with `camunda:decisionRef` | A decision step carrying its DMN key |
| `callActivity` with `calledElement` | A subprocess step; the view can open the called process |
| `camunda:formRef` | The form a step uses, per node |
| `ronl:documentRef` | The documents a step produces; a comma-separated list for several |

Only the first `<bpmn:process>` in a file is read, and only these flow-node types become nodes: start, end and intermediate events, user, manual, receive, script, business-rule, service and send tasks, call activities, subprocesses, and exclusive, inclusive, event-based and parallel gateways.

---

## Related pages

- [Business Rules Execution](../features/business-rules-execution.md) — BPMN/DMN execution via Operaton
- [Operaton DMN Compatibility](../../linked-data-explorer/reference/operaton-dmn-compatibility.md) — DMN authoring constraints for the Linked Data Explorer
- [API Specification](../reference/api-specification.md) — `/v1/process` and `/v1/task` endpoints
