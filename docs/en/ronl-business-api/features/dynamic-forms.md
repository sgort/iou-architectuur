---
component: RONL Business API
---

# Dynamic Forms

A **form** is a JSON schema, not a hardcoded screen. No form fields live in the frontend application; a schema is fetched from the deployment and rendered at runtime, each time the form is opened. This is the rendering counterpart to a task's [Handling](tasks.md#handling) step — it describes what actually appears when a start event or a user task needs input.

---

## Authoring and deployment

A form is a **Camunda Form** — a JSON schema, not a BPMN diagram — deployed to Operaton as a resource alongside the BPMN process it belongs to. Deployment happens in the same bundle and shares the same deployment id, which is what lets a BPMN element resolve its bound form at runtime. A deployed process can also carry no forms at all: nothing requires a start event or a user task to have one.

---

## Binding

A BPMN element is bound to a form by referencing the form's id — the `camunda:formRef` attribute — rather than embedding the form inline. Because the reference is by id, redeploying a new version of the form updates every start event or user task bound to it without touching the BPMN itself; the platform resolves the reference to the most recently deployed version at fetch time, not a version pinned when the BPMN was authored.

Binding is optional. A process definition can expose no start form, in which case starting it is a matter of supplying variables directly. A task without a bound form falls back to a plain completion with no form-driven fields — see [Tasks — Completing](tasks.md#completing).

Only Camunda Forms — JSON schemas — are rendered. If the resource deployed for a given element is an embedded HTML form instead, fetching it returns `415 UNSUPPORTED_FORM_TYPE`: the platform does not render that format.

---

## Fetching a schema

The schema is fetched, not pushed. A start form is retrieved when a process's start screen is opened; a task form is retrieved when a claimed task is opened. Both requests carry tenant checks — a task form fetch is rejected if the task does not belong to the caller's tenant — matching the visibility rules described in [Tasks](tasks.md).

---

## Rendering

The fetched schema is rendered by a form-rendering runtime that interprets the JSON directly — nothing about the fields is known to the application in advance. Rendering also takes an initial-data object to pre-fill parts of the form:

- A **start form** is pre-filled with context the caller doesn't need to type — for example values drawn from the caller's own identity and tenant, attached automatically when the process is started.
- A **task form** is pre-filled with the process instance's current variables, so the person handling the task sees the state the process has accumulated so far rather than a blank form.

---

## Submitting

Submitting a start form forwards its variables directly to the process-start request; submitting a task form completes the task with its variables, handing control back to the engine exactly as described in [Tasks — Completing](tasks.md#completing). In both cases the form only ever produces process variables — it has no side effects of its own outside that submission.

---

## Document templates

A process can also bundle a **document template** instead of, or alongside, a form — a schema for rendering a process's outcome as a formatted document rather than collecting input. A document template is organised into zones (for example a letterhead, a body, a closing) and can reference process variables by key, substituting each reference with the corresponding resolved value when rendered. Fetching a document template is scoped by the same tenant check as any other process resource; a process instance that has no document template bound simply has none to fetch.

---

## Related

- [Tasks](tasks.md) — the lifecycle a task form fits into
- [Processes](processes.md) — how a start form fits into starting an instance
- [Business Rules Execution](business-rules-execution.md) — decisions whose outcomes a task or document form displays
- [API Design](api-design.md) — the conventions the form-fetching endpoints follow
