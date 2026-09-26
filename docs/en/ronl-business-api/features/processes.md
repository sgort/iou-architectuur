---
component: RONL Business API
---

# Processes

A **process** is a BPMN 2.0 workflow deployed to the Operaton engine that RONL Business API sits in front of. The Business API never executes process logic itself — it validates the caller, resolves tenancy, and forwards the request to Operaton, hiding the engine's own REST API behind a smaller, versioned surface.

---

## Process definitions and keys

A deployed BPMN workflow becomes a **process definition** in Operaton, identified by a **process definition key** — a short, stable name taken from the BPMN model. Deploying a new version of the same workflow does not replace the key; Operaton keeps prior versions available so that instances already in flight keep running against the definition they started under.

---

## A phase catalogue cannot name a process it does not have

Where a sequence of phases is driven by one process per phase — as the RIP ladder is, with twelve — the mapping from phase code to process definition key lives in a single place that backend and frontend both read, so neither authors it separately.

The process definition key on a catalogue entry is **required**. While the ladder was still being built it was optional, and a known phase with no process yet was a real state the platform had to answer for: a request naming one was refused with a status of its own, distinct from a request naming a phase that does not exist at all. Once every phase carried a process, that state stopped being reachable — and rather than leave a branch answering for something no input could produce, the field was made required. A phase with no deployed process is now a compile error rather than a runtime answer, which fixes the order of work: model and deploy the process, then add the catalogue entry.

One failure mode is left, and it is a client error: a phase code the catalogue does not carry at all.

---

## Starting an instance

Starting a process creates a **process instance** — a running copy of the workflow, addressed by its own instance id. A start request carries:

- the **process definition key** identifying which workflow to start,
- an optional **business key**, the case's human-facing handle. A key the caller supplies is kept verbatim — a RIP phase started for a project passes the key its first phase minted, so every phase of one project shares it. Without one, the backend mints `<owning organisation>-<timestamp>`, naming the organisation that owns the case rather than the caller's; and
- a set of **input variables**, which seed the process instance's variable scope and are typically supplied by a **start form** — a schema deployed alongside the BPMN and bound to the process's start event.

The response reports the new instance's id, business key, and status (`active`, `suspended`, or `ended`).

A process definition can also expose no start form at all, in which case starting it is a matter of supplying variables directly.

Once running, an instance can be queried for its status and variables, cancelled outright, or — once it has produced history — inspected for its final variable state and the sequence of steps the engine executed between user tasks.

---

## Tenancy

Operaton has a native **tenant-id** concept, independent of any variable carried inside the process. A deployment can be made under a specific tenant-id, or it can be deployed **untenanted** — with no tenant-id at all.

### Which deployment a start resolves to

Before starting, the backend asks Operaton which tenants deploy the latest version of the process definition key, and picks one:

1. The caller's own tenant, if it deploys the key.
2. Otherwise the single tenant that deploys it.
3. If several other tenants deploy it and none of them is the caller's, there is no basis for choosing: the start is refused with `409 AMBIGUOUS_DEPLOYMENT` and nothing is started. The start-form lookup answers the same way.
4. If no tenant-scoped deployment exists (or the lookup itself fails), the process starts untenanted — the behaviour of a process deliberately deployed shared, without a tenant-id.

The choice never depends on the order in which Operaton lists its definitions.

### Who owns the case

The resolved deployment then decides whether the caller may start it and which organisation owns the resulting case:

- An untenanted deployment, or one under the caller's own tenant: the case belongs to the caller's tenant.
- A deployment under another tenant, started by a citizen: the case goes to the deploying tenant, and `originTenantId` records the tenant the citizen came in through. A citizen of one municipality applying for a benefit handled by a national organisation is this case.
- A deployment under another tenant, started by staff: refused with `403 TENANT_MISMATCH`; no instance is created.

The owning tenant is written into the instance's `municipality` process variable, so it always agrees with the tenant Operaton runs the instance under. That variable is the only tenant label any access check reads, and the checks fail closed: an instance without it is refused to everyone. The five reads — status, variables, historic variables, activity history and decision document — are open to the owning tenant and to the case's own applicant; cancelling the instance is open to the owning tenant only. See [Authentication & IAM — Tenancy](authentication-iam.md#tenancy) for the full rule set.

This tenant scoping is covered by an automated end-to-end test — see [Testing](../developer/testing/dashboards/caseworker.md#e2e).

---

## Related

- [Tasks](tasks.md) — what happens once a running process produces work for a person to do
- [Dynamic Forms](dynamic-forms.md) — how start forms and task forms are rendered
- [API Design](api-design.md) — the versioned REST conventions the process endpoints follow
