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

The activity history lists every step in the order the engine executed it — sorted on Operaton's `occurrence`, not start time alone, so steps that start in the same millisecond keep their causal order. Each entry names the process definition it belongs to (`processDefinitionKey`, `processDefinitionId`) and, for a call activity, the instance it started (`calledProcessInstanceId`).

### Lineage

`GET /v1/process/{id}/lineage` places an instance in its call chain: its process definition, and `superProcessInstanceId` — the instance that called it, or `null` for a top-level instance. It reads Operaton's historic instance, so it also answers for an instance that has ended. It is subject to the same tenant check as the activity history. An unknown instance answers `404 PROCESS_NOT_FOUND`; any other failure `500 PROCESS_LINEAGE_FAILED`.

Together, lineage and activity history let a client walk from a task in a subprocess up to its main process and merge the histories of the whole chain — which is what the caseworker's process view does; see [Tasks — Where a task stands in its process](tasks.md#where-a-task-stands-in-its-process).

---

## Swimlane model of a process

`GET /v1/process/definition/key/{key}/swimlane` returns the process a key currently resolves to as a swimlane model, parsed from its deployed BPMN: its lanes (with the literal candidate groups of the user tasks drawn in each), its nodes and flows, and — where the model carries phase markers — the phase of every node (`phase`) and the phases the model moves through (`phaseSet`: its `scheme`, `awb` for the built-in Awb phases marked with `ronl:awbPhase` or `bpmn` for phases the process declares itself in `ronl:phases` and marks with `ronl:phase`; the `label` a phase reference starts with; and the ordered `phases`). The same parser serves the Infra-board's RIP phases; nothing in it is specific to RIP.

- **Tenant-scoped lookup.** The key is resolved under the caller's tenant first, falling back to an untenanted deployment, so another tenant's deployment is never reached.
- **Cached by definition id.** The parsed model is cached per deployed definition, so a redeploy is picked up on the next request.
- **Validated key.** The key must be an XML NCName — a letter or underscore, then letters, digits, `_`, `.` or `-` — or the request is refused with `400 INVALID_PROCESS_KEY` before anything reaches the engine.

A key with no deployment answers `404 PROCESS_DEFINITION_NOT_FOUND`; a model that cannot be built, `500 SWIMLANE_MODEL_FAILED`. How to model a process so the view has lanes and phases to show is described in [BPMN Design Criteria](../reference/bpmn-design-criteria.md).

---

## Tenancy

Operaton has a native **tenant-id** concept, independent of any variable carried inside the process. A deployment can be made under a specific tenant-id, or it can be deployed **untenanted** — with no tenant-id at all.

### Which deployment a start resolves to

Before starting, the backend asks Operaton which tenants deploy the latest version of the process definition key, and picks one:

1. The caller's own tenant, if it deploys the key.
2. Otherwise the single tenant that deploys it.
3. If several other tenants deploy it and none of them is the caller's, there is no basis for choosing: the start is refused with `409 AMBIGUOUS_DEPLOYMENT` and nothing is started. The start-form lookup answers the same way.
4. If no tenant-scoped deployment exists (or the lookup itself fails), there is no deploying tenant. A member of staff starts the process untenanted — the behaviour of a process deliberately deployed shared, without a tenant-id, as HR onboarding still is. A citizen's start is refused: a citizen's case must belong to a tenant (see below).

The choice never depends on the order in which Operaton lists its definitions.

### Who owns the case

The resolved deployment then decides whether the caller may start it and which organisation owns the resulting case:

- A deployment under the caller's own tenant: the case belongs to the caller's tenant.
- No deploying tenant, started by staff: the case belongs to the caller's tenant.
- No deploying tenant, started by a citizen: refused with `403 TENANT_MISMATCH`; no instance is created.
- A deployment under another tenant, started by a citizen for a cross-tenant [citizen service](#citizen-services): the case goes to the deploying tenant, and `originTenantId` records the tenant the citizen came in through. A citizen of a municipality applying for Zorgtoeslag, handled by Dienst Toeslagen, is this case.
- A deployment under another tenant, in any other case — started by staff, or by a citizen for a process that is not a cross-tenant citizen service, such as another organisation's own-tenant service: refused with `403 TENANT_MISMATCH`; no instance is created.

The owning tenant is written into the instance's `municipality` process variable, so it always agrees with the tenant Operaton runs the instance under. That variable is the only tenant label any access check reads, and the checks fail closed: an instance without it is refused to everyone. The six reads — status, variables, historic variables, activity history, lineage and decision document — are open to the owning tenant and to the case's own applicant; cancelling the instance is open to the owning tenant only. See [Authentication & IAM — Tenancy](authentication-iam.md#tenancy) for the full rule set.

This tenant scoping is covered by an automated end-to-end test — see [Testing](../developer/testing/dashboards/caseworker.md#e2e).

---

## Citizen services

The services a citizen can apply for in the [citizen portal](../user-guide/citizen-portal.md) are listed once, in `CITIZEN_SERVICES` in the shared package (`@ronl/shared`): each entry names the service, the process it starts, and its scope.

| Service | Process key | Scope |
|---|---|---|
| `zorgtoeslag` | `AwbZorgtoeslagProcess` | cross-tenant |
| `vergunningen` | `AwbShellProcess` | own-tenant |
| `subsidies` | `ThuisbatterijSubsidieAanvraagProcess` | own-tenant |
| `heusdenpas` | `HeusdenpasAanvraagProcess` | own-tenant |

- **own-tenant**: offered only to citizens of a tenant that deploys the process itself, so the case lands at their own organisation.
- **cross-tenant**: offered to every citizen when exactly one tenant deploys the process; that tenant handles the case for whichever organisation the citizen came in through. Deployed under several tenants, a start would be ambiguous (`409 AMBIGUOUS_DEPLOYMENT`), so the service is not offered at all.

The registry holds data only. The backend derives from it which services a citizen is offered and checks every start against it — the cross-tenant scope is what lets a citizen's start reach another tenant's deployment (see [Who owns the case](#who-owns-the-case)). The labels, icons and forms of the cards are the frontend's.

`GET /v1/process/available` answers which services the signed-in citizen may start, as `data.services`, a list of service ids in registry order. It asks Operaton for the latest deployment of each registry process under every tenant and applies the two scopes; a deployment without a tenant never counts, since a citizen's case must belong to a tenant. The route is for citizens only: anyone else is refused with `403 FORBIDDEN`. When Operaton cannot be asked, it answers `503 SERVICES_UNAVAILABLE`, and the portal shows an error with a retry rather than every card.

Adding a service means a registry entry, a card for it in the frontend, and deploying its process under the tenant — or, for a cross-tenant service, the one tenant — that handles it.

---

## Related

- [Tasks](tasks.md) — what happens once a running process produces work for a person to do
- [Dynamic Forms](dynamic-forms.md) — how start forms and task forms are rendered
- [API Design](api-design.md) — the versioned REST conventions the process endpoints follow
