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

## Completing

**Completing** a task submits the outcome — whatever variables the task form collected — back to the process instance and returns control to the engine. Completion is what allows the process to continue past the point the task represented; the engine resumes execution from there, which may produce further automated steps, another task for someone else, or the end of the process.

A completion cannot set the variables that decide access. `municipality`, `originTenantId` and `applicantId` are written once, when the process starts; Operaton stores completion variables on the process instance, so a completion carrying `municipality` would hand the case to another organisation. A completion that includes any of the three is refused with `400 RESERVED_VARIABLE`, after the tenant check and before anything reaches the engine.

A completed task leaves a record: it can be retrieved afterwards as part of the tenant's history of finished work — filtered on the same `municipality` variable — separate from the list of currently open tasks.

---

## Related

- [Processes](processes.md) — what produces a task in the first place, and how tenancy scopes it
- [Dynamic Forms](dynamic-forms.md) — how task forms are rendered
- [Authentication & IAM](authentication-iam.md) — how roles determine which candidate groups a user belongs to
