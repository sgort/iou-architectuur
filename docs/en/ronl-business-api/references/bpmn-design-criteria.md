# BPMN Design Criteria

This page documents design constraints and conventions that apply when authoring BPMN processes and DMN decisions for deployment in the RONL Business API platform. Following these criteria ensures correct runtime behaviour and prevents issues in the citizen portal and caseworker interface.

---

## BusinessRuleTask: `camunda:mapDecisionResult`

A `BusinessRuleTask` that calls a DMN decision must declare how the engine maps the decision output into a process variable. This is controlled by the `camunda:mapDecisionResult` attribute.

Operaton supports four mapping modes:

| Value | Returns | Use when |
|---|---|---|
| `singleEntry` | The value of a single output column from a single matched rule | The decision has one output column and a hit policy that guarantees at most one result (`UNIQUE`, `FIRST`, `ANY`) |
| `singleResult` | All output columns of a single matched rule as a `Map` object | The decision has multiple output columns and you need all of them as a structured object |
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

### `singleResult` — structured multi-output decisions

For decisions with multiple output columns (for example a completeness check returning `isComplete`, `missingFields`, and `legalArticle`), use `singleResult`. This stores a `Map` as the result variable.

```xml
<bpmn:businessRuleTask
  id="Task_CompletenessCheck"
  name="Phase 3: Admissibility check"
  camunda:resultVariable="completenessResult"
  camunda:decisionRef="AwbCompletenessCheck"
  camunda:mapDecisionResult="singleResult">
```

The process variable `completenessResult` will be a `Map`. To use individual fields in downstream tasks, access them by key:

```javascript
// In a script task (Groovy / JavaScript):
var isComplete = completenessResult.get("isComplete");
var missingFields = completenessResult.get("missingFields");
```

!!! warning "Frontend display"
    When `singleResult` is used, the process variable is stored as a `Map` object. Rendering it via `String(value)` in a JavaScript frontend produces `[object Object]`. The caseworker interface handles this by detecting object-type values and serialising them with `JSON.stringify`. However, to keep process data readable, prefer extracting the specific sub-values you need into separate scalar variables using a script task immediately after the business rule task.

### Known issue in `AwbShellProcess`

The `Task_Phase3_Completeness` task in `awb-process.bpmn` uses `singleResult` because `AwbCompletenessCheck.dmn` has three output columns. This causes `completenessResult` to be stored as a `Map` and to appear as `[object Object]` in raw variable displays.

**Workaround (frontend):** The caseworker variables panel serialises object values with `JSON.stringify` before display.

**Proper fix (BPMN):** Add a script task after `Task_Phase3_Completeness` that extracts `completenessResult.get("isComplete")` into a plain `Boolean` variable, then use that variable in the `Gateway_Complete` condition:

```xml
<bpmn:scriptTask id="Task_ExtractCompleteness" name="Extract completeness flag" scriptFormat="javascript">
  <bpmn:script>
    var result = execution.getVariable("completenessResult");
    execution.setVariable("isComplete", result.get("isComplete"));
    execution.setVariable("missingFieldsDescription", result.get("missingFields"));
  </bpmn:script>
</bpmn:scriptTask>
```

---

## Gateway conditions and variable types

Gateway `conditionExpression` values must match the actual type of the process variable being tested.

| Variable type | Correct expression | Incorrect |
|---|---|---|
| `String` | `${permitDecision == "Permit"}` | `${permitDecision == true}` |
| `Boolean` | `${isComplete == true}` or `${isComplete}` | `${isComplete == "true"}` |
| `Integer` | `${treeDiameter > 30}` | `${treeDiameter > "30"}` |
| `Map` (singleResult) | `${completenessResult.get("isComplete") == true}` | `${completenessResult == true}` |

When `singleResult` is used, the gateway must call `.get("columnName")` on the map variable. Comparing the map object directly to a primitive always evaluates to `false` without throwing an error, making this class of bug difficult to detect at design time.

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

## Related pages

- [Business Rules Execution](../features/business-rules-execution.md) — BPMN/DMN execution via Operaton
- [Operaton DMN Compatibility](../../linked-data-explorer/reference/operaton-dmn-compatibility.md) — DMN authoring constraints for the Linked Data Explorer
- [API Endpoints Reference](../references/api-endpoints.md) — `/v1/process` and `/v1/task` endpoints
