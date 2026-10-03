---
component: RONL Business API
---

# Tasks

A **task** is a unit of human work produced by a running process. Where a process definition describes an entire workflow, a task represents the single step in it that requires a person to act before the process can continue. Tasks are the point where the platform hands control from the engine to a person, and back again.

---

## Visibility

A task becomes visible to the people entitled to see it, not to everyone. Operaton scopes a task to one or more **candidate groups**, defined in the BPMN model, which the platform maps onto a signed-in user's roles: a user only sees a task in their list if at least one of their roles matches one of the task's candidate groups.

A task belongs to the organisation that owns its process instance: the instance's `municipality` process variable, not Operaton's `task.tenantId` (which names the deployment's tenant). The task list filters on that variable, and opening a task — its detail, its variables, its form schema — as well as claiming and completing it all check the same variable. A task the list offers is therefore one the detail endpoints accept. For a task in a called subprocess, the label is the child instance's copy, inherited from the parent. A task whose instance carries no label, or another organisation's, is refused with `403 TENANT_MISMATCH`; every task operation is open to the owning organisation only. This scoping is covered by an automated end-to-end test — see [Testing](../developer/testing/dashboards/caseworker.md#e2e).

Once a task has been claimed, it does not disappear from view — it stays visible, so the person who claimed it (and anyone else entitled to see it) can find it again, including through a filtered view of "my claimed work".

---

## Claiming

**Claiming** a task assigns it to the person who claims it, taking ownership of it. Before it is claimed, a task is open to anyone in its candidate groups; once claimed, it is that person's to handle. A claim is subject to the same tenant check as opening the task, made before anything is sent to the engine.

---

## Handling

A claimed task is typically handled through a **task form** — a schema deployed alongside the BPMN and bound to that specific task, fetched and rendered at the moment the task is opened. The form determines what information the task requires and what the person handling it can enter or review. Handling a task can also mean reading the process instance's variables accumulated so far, giving the person the context needed to act.

---

## Where a task stands in its process

A task is one step in a larger process, and the working environment can show where. For the task's process it loads the [lineage and activity history](processes.md#lineage) — walking up through any process that called it — and the [swimlane model](processes.md#swimlane-model-of-a-process) of every process involved, then draws the task in that context:

- **Lanes are roles.** Each lane carries the literal candidate groups of the user tasks drawn in it. A lane whose groups meet the user's realm roles is marked as the user's own; a candidate group written as an expression (`${…}`, `#{…}`) names no role and is left out.
- **Phases come from markers.** A process marks its nodes either with `ronl:awbPhase`, against the built-in Awb phases, or with `ronl:phase`, against phases it declares itself in `ronl:phases`; the two schemes never mix in one process. Where there are markers, the task's phase and a phase stepper are shown; a task in a subprocess without markers takes the phase of the call activity that started it. With no markers anywhere in the chain, the task has no phase and no stepper is shown. [BPMN Design Criteria](../reference/bpmn-design-criteria.md) describes both schemes.
- **One history across the chain.** The activity histories of the main process and its subprocesses are merged into one list in engine order, with a subprocess's steps placed directly after the call activity that started it.

Only the task's own lineage and history are required; a calling process the user may not read, or a model that fails to load, leaves the view partial rather than empty. A process whose BPMN has no lanes keeps the flat list of steps. [BPMN Design Criteria](../reference/bpmn-design-criteria.md) describes how to model a process for this view, and the [Caseworker guide](../user-guide/caseworker.md) how it looks.

---

## Completing

**Completing** a task submits the outcome — whatever variables the task form collected — back to the process instance and returns control to the engine. Completion is what allows the process to continue past the point the task represented; the engine resumes execution from there, which may produce further automated steps, another task for someone else, or the end of the process.

A completion cannot set the variables that decide access. `municipality`, `originTenantId` and `applicantId` are written once, when the process starts; Operaton stores completion variables on the process instance, so a completion carrying `municipality` would hand the case to another organisation. A completion that includes any of the three is refused with `400 RESERVED_VARIABLE`, after the tenant check and before anything reaches the engine; the problem's `reserved` member names the variables refused. A completion through the machine-to-machine route, `POST /v1/m2m/task/{id}/complete`, is refused the same way.

A completed task leaves a record: it can be retrieved afterwards as part of the tenant's history of finished work — filtered on the same `municipality` variable — separate from the list of currently open tasks.

---

## Related

- [Processes](processes.md) — what produces a task in the first place, and how tenancy scopes it
- [Dynamic Forms](dynamic-forms.md) — how task forms are rendered
- [Authentication & IAM](authentication-iam.md) — how roles determine which candidate groups a user belongs to
