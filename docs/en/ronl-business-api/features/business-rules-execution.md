---
component: RONL Business API
---

# Business Rules Execution

A **decision** is a DMN 1.3 decision table deployed to Operaton, the same engine that runs BPMN processes. As with a process, the Business API never evaluates the table itself — it validates the caller and forwards the request, hiding Operaton's own REST API behind a smaller, versioned surface.

---

## Deploying a decision table

A decision table is deployed to Operaton as a resource, identified by a decision key. Deployment follows the same pattern as a process definition: a new version can be deployed under the same key without breaking whatever already depends on the version in place.

---

## Invoking a decision

A decision can be evaluated in two ways:

- **Directly**, by posting the input variables to the decision's evaluate endpoint. This is the path a caller uses to get a decision outcome without running a full process around it.
- **From within a running process**, where a BPMN business rule task evaluates the decision as one step of the workflow, invisible to the Business API — Operaton executes it inline as part of the process, and the result becomes part of that instance's variables like any other step.

---

## Inputs and outputs

A direct evaluation request carries its input variables in the request body. Each variable is transformed into Operaton's own `{ value, type }` format before being sent on: if a caller already supplies that shape it is passed through unchanged, otherwise the platform infers the type — boolean, integer, double, string, or JSON — from the plain value supplied. The decision table's output is returned as Operaton reports it, in the same array-of-results format Operaton itself produces.

Evaluating a decision directly requires the caller to hold at least a minimum level of assurance — the platform will not evaluate a decision on behalf of a caller whose identity has not been established to at least that level.

---

## Decisions shared across tenants

Every caller carries a tenant, and that tenant id is added into the evaluation's variables alongside the caller's own inputs. But the evaluate endpoint itself resolves whatever decision is deployed under the requested key — it does not scope the lookup to the caller's own tenant the way starting a process does. In practice this means a single deployed decision table can serve every tenant that invokes it by key, and any tenant-specific behaviour is left entirely to the table's own rules: a decision table that wants to treat tenants differently does so by branching on the tenant variable it receives, not because the platform routed the request to a tenant-specific deployment.

---

## Errors

When Operaton reports an evaluation failure, the platform recognises a small set of known engine errors — such as a hit policy that allows only one matching rule being violated by a table where several rules match at once — and raises a descriptive message for them instead of surfacing the raw engine exception. Any other engine error is passed through with Operaton's own message rather than hidden behind a generic failure.

---

## Related

- [Processes](processes.md) — how a business rule task fits inside a running process, and how tenancy scopes a process differently from a decision
- [Tasks](tasks.md) — the human step that typically follows a decision inside a process
- [Dynamic Forms](dynamic-forms.md) — how a decision's outcome is shown to the person handling the resulting task
- [API Design](api-design.md) — the versioned conventions the decision endpoints follow
