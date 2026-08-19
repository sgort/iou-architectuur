---
component: RONL Business API
---

# Processes

A **process** is a BPMN 2.0 workflow deployed to the Operaton engine that RONL Business API sits in front of. The Business API never executes process logic itself — it validates the caller, resolves tenancy, and forwards the request to Operaton, hiding the engine's own REST API behind a smaller, versioned surface.

---

## Process definitions and keys

A deployed BPMN workflow becomes a **process definition** in Operaton, identified by a **process definition key** — a short, stable name taken from the BPMN model. Deploying a new version of the same workflow does not replace the key; Operaton keeps prior versions available so that instances already in flight keep running against the definition they started under.

---

## Starting an instance

Starting a process creates a **process instance** — a running copy of the workflow, addressed by its own instance id. A start request carries:

- the **process definition key** identifying which workflow to start,
- an optional **business key**, a caller-chosen identifier for the instance (used to correlate it with a case elsewhere), and
- a set of **input variables**, which seed the process instance's variable scope and are typically supplied by a **start form** — a schema deployed alongside the BPMN and bound to the process's start event.

The response reports the new instance's id, business key, and status (`active`, `suspended`, or `ended`).

A process definition can also expose no start form at all, in which case starting it is a matter of supplying variables directly.

Once running, an instance can be queried for its status and variables, cancelled outright, or — once it has produced history — inspected for its final variable state and the sequence of steps the engine executed between user tasks.

---

## Tenancy

Operaton has a native **tenant-id** concept, independent of any variable carried inside the process. A deployment can be made under a specific tenant-id, restricting who can see or start it, or it can be deployed **untenanted** — with no tenant-id at all — in which case it is visible and startable regardless of tenant.

When a process is started or queried, the request resolves against a tenant:

- If the process definition's own deployed tenant-id can be determined, that tenant scopes the request — not necessarily the tenant of the caller. A process can deliberately be deployed under a fixed tenant so that every instance of it, regardless of who starts it, is handled by that one tenant.
- If no tenant-scoped deployment of that key can be found, the platform falls back to starting it untenanted — the behaviour a process gets when it has deliberately been deployed shared, without a tenant-id, and is meant to be startable across tenants.

This makes multi-tenancy a property of the deployment, not of the caller: the same process definition key can be deployed once, shared across every tenant, or deployed separately per tenant, and the platform resolves which applies without the caller needing to know which case it is.

Every running instance also carries its own tenant as a process variable, separate from Operaton's native tenant-id, which is what scopes later access to that instance's status, variables, and history to the tenant it belongs to.

This tenant scoping is covered by an automated end-to-end test — see [Testing](../developer/testing/overview.md#frontend-playwright-suite).

---

## Related

- [Tasks](tasks.md) — what happens once a running process produces work for a person to do
- [Dynamic Forms](dynamic-forms.md) — how start forms and task forms are rendered
- [API Design](api-design.md) — the versioned REST conventions the process endpoints follow
