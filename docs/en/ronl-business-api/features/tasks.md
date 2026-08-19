---
component: RONL Business API
---

# Tasks

A **task** is a unit of human work produced by a running process. Where a process definition describes an entire workflow, a task represents the single step in it that requires a person to act before the process can continue. Tasks are the point where the platform hands control from the engine to a person, and back again.

---

## Visibility

A task becomes visible to the people entitled to see it, not to everyone. Operaton scopes a task to one or more **candidate groups**, defined in the BPMN model, which the platform maps onto a signed-in user's roles: a user only sees a task in their list if at least one of their roles matches one of the task's candidate groups.

A task list is also scoped to the tenant its underlying process instance belongs to, so a task only appears to people working within that tenant. This scoping is covered by an automated end-to-end test — see [Testing](../developer/testing/overview.md#frontend-playwright-suite).

Once a task has been claimed, it does not disappear from view — it stays visible, so the person who claimed it (and anyone else entitled to see it) can find it again, including through a filtered view of "my claimed work".

---

## Claiming

**Claiming** a task assigns it to the person who claims it, taking ownership of it. Before it is claimed, a task is open to anyone in its candidate groups; once claimed, it is that person's to handle. A claim can be made on any task the caller is entitled to see, subject to the same tenant check that governs visibility.

---

## Handling

A claimed task is typically handled through a **task form** — a schema deployed alongside the BPMN and bound to that specific task, fetched and rendered at the moment the task is opened. The form determines what information the task requires and what the person handling it can enter or review. Handling a task can also mean reading the process instance's variables accumulated so far, giving the person the context needed to act.

---

## Completing

**Completing** a task submits the outcome — whatever variables the task form collected — back to the process instance and returns control to the engine. Completion is what allows the process to continue past the point the task represented; the engine resumes execution from there, which may produce further automated steps, another task for someone else, or the end of the process.

A completed task leaves a record: it can be retrieved afterwards as part of the tenant's history of finished work, separate from the list of currently open tasks.

---

## Related

- [Processes](processes.md) — what produces a task in the first place, and how tenancy scopes it
- [Dynamic Forms](dynamic-forms.md) — how task forms are rendered
- [Authentication & IAM](authentication-iam.md) — how roles determine which candidate groups a user belongs to
