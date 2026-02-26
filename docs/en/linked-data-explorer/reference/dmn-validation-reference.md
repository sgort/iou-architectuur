# DMN Validation Reference

This reference documents every validation code produced by the RONL DMN+ syntactic validator, the rule each code enforces, and the rationale for why that rule exists. The validator runs on the shared backend at `POST /v1/dmns/validate` and is used both by the Linked Data Explorer's standalone DMN Validator view and by the CPSV Editor's inline validation in the DMN tab.

---

## How to read this reference

Each entry follows this structure:

| Field | Meaning |
|---|---|
| **Code** | The short typed identifier included in every issue object (e.g. `BIZ-002`) |
| **Severity** | `error` — must fix; `warning` — should fix for RONL publishing; `info` — quality suggestion |
| **Trigger** | The condition that causes this issue to be emitted |
| **Rationale** | Why this rule exists and what goes wrong if it is violated |
| **Fix** | What to change in your DMN file |

---

## Layer 1 — Base DMN (BASE-*)

Layer 1 checks that the file is a structurally sound XML document with the correct root element and namespace. These checks run first; if they fail, layers 2–5 are skipped entirely because a broken document cannot be safely traversed.

---

### BASE-PARSE

| | |
|---|---|
| **Severity** | error |
| **Trigger** | `libxmljs2.parseXml()` throws a `SyntaxError` — the file is not well-formed XML |
| **Rationale** | DMN files are XML documents. A parser error means the file cannot be read at all — not by the validator, not by Operaton, not by any other DMN tooling. This is the most fundamental failure mode. |
| **Fix** | Open the file in a text editor or XML validator. Common causes: unclosed tags, illegal characters in attribute values, missing XML declaration encoding, byte-order mark (BOM) at the start of the file. The `line` and `column` fields on the issue pinpoint the exact location. |

---

### BASE-ROOT

| | |
|---|---|
| **Severity** | error |
| **Trigger** | The root element is not named `definitions` |
| **Rationale** | The DMN 1.x specification mandates `<definitions>` as the document root. A different root element means the file is either not a DMN file, is a fragment, or has been corrupted. |
| **Fix** | Ensure the file starts with `<definitions xmlns="https://www.omg.org/spec/DMN/20191111/MODEL/" ...>`. |

---

### BASE-NS

| | |
|---|---|
| **Severity** | error |
| **Trigger** | The namespace URI on `<definitions>` is not one of the recognised DMN namespaces |
| **Rationale** | Each DMN version uses a distinct namespace URI. The validator recognises: DMN 1.3 (`https://www.omg.org/spec/DMN/20191111/MODEL/`), DMN 1.2 (`http://www.omg.org/spec/DMN/20180521/MODEL/`), DMN 1.1 (`http://www.omg.org/spec/DMN/20151101/dmn.xsd`), and the Camunda legacy namespace (`https://www.camunda.org/schema/1.0/dmn`). An unrecognised namespace causes XPath queries in layers 2–5 to fail silently, producing incomplete validation results and unexpected Operaton behaviour. |
| **Fix** | Update `xmlns` on `<definitions>` to a recognised namespace. For new files, use the DMN 1.3 namespace. |

---

### BASE-NAME

| | |
|---|---|
| **Severity** | warning |
| **Trigger** | `<definitions>` is missing the `name` attribute or its value is empty |
| **Rationale** | The DMN specification requires a `name` on `<definitions>`. Operaton uses this name in its deployment UI. A missing name makes it harder to identify a model in the engine and in TriplyDB metadata. |
| **Fix** | Add `name="YourModelName"` to the `<definitions>` element. |

---

### BASE-NSATTR

| | |
|---|---|
| **Severity** | warning |
| **Trigger** | `<definitions>` is missing the `namespace` attribute or its value is empty |
| **Rationale** | The `namespace` attribute defines the target namespace for the model's identifiers. Without it, URIs generated from decision IDs are ambiguous. For RONL publishing, this value is used as the base URI for the decision model's linked data identity. |
| **Fix** | Add `namespace="https://regels.overheid.nl/services/{your-service-id}/dmn"` to `<definitions>`. |

---

### BASE-EMPTY

| | |
|---|---|
| **Severity** | warning |
| **Trigger** | The document contains no `<decision>` elements |
| **Rationale** | A DMN file with no decisions contains no executable logic. This typically indicates an empty template, a partially authored file, or a file that only contains `<inputData>` definitions without the associated decisions. |
| **Fix** | Add at least one `<decision>` element, or verify that the correct file was uploaded. |

---

## Layer 2 — Business Rules (BIZ-*)

Layer 2 checks the structural correctness of decision table definitions: that enumerations are valid, that type declarations are present, and that rule rows are internally consistent.

---

### BIZ-001

| | |
|---|---|
| **Severity** | error |
| **Trigger** | A `<decisionTable>` has a `hitPolicy` attribute whose value is not in the allowed set: `UNIQUE`, `FIRST`, `ANY`, `COLLECT`, `RULE ORDER`, `OUTPUT ORDER`, `PRIORITY` |
| **Rationale** | Operaton implements the full DMN 1.3 hit policy set but will reject unknown values at deployment time with a cryptic parse error. Catching this before deployment saves a round-trip to the engine. |
| **Fix** | Correct the `hitPolicy` value on the `<decisionTable>` element. If no hit policy is specified, `UNIQUE` is the default. |

---

### BIZ-002

| | |
|---|---|
| **Severity** | warning |
| **Trigger** | An `<inputExpression>` inside a decision table is missing a `typeRef` attribute |
| **Rationale** | `typeRef` declares the FEEL type of the input column. Without it, Operaton performs no type coercion — a string `"true"` is not automatically cast to `boolean true`, which causes rules to never match if the FEEL type does not align with the runtime variable type. For RONL publishing, typed inputs are required for semantic interoperability. |
| **Fix** | Add `typeRef="boolean"` (or `string`, `integer`, `date`, etc.) to the `<inputExpression>`. |

---

### BIZ-003

| | |
|---|---|
| **Severity** | warning |
| **Trigger** | An `<inputExpression>` has a `typeRef` value that is not a known DMN FEEL type |
| **Rationale** | Known types are: `string`, `boolean`, `integer`, `long`, `double`, `number`, `date`, and their capitalised variants. An unknown type (e.g. a misspelling such as `Boolean` when the file expects `boolean`, or a custom type name) means the type declaration is present but non-functional. |
| **Fix** | Replace the custom or misspelled type with the correct FEEL type name. |

---

### BIZ-004

| | |
|---|---|
| **Severity** | warning |
| **Trigger** | An `<output>` column in a decision table is missing a `typeRef` attribute |
| **Rationale** | Without a typed output, consuming systems (including the Linked Data Explorer's chain builder) cannot validate that the output type of one DMN matches the expected input type of the next DMN in a chain. This is a prerequisite for type-safe chain composition. |
| **Fix** | Add `typeRef` to the `<output>` element. |

---

### BIZ-005

| | |
|---|---|
| **Severity** | error |
| **Trigger** | A rule row has a different number of `<inputEntry>` or `<outputEntry>` elements than the number of `<input>` or `<output>` columns declared on the parent `<decisionTable>` |
| **Rationale** | DMN requires that every rule row has exactly one entry per input column and at least one entry per output column. A mismatch means the table is malformed — Operaton will either throw a parse error or silently misalign entries, producing incorrect rule matches. |
| **Fix** | Ensure every `<rule>` in the decision table has the same number of `<inputEntry>` elements as there are `<input>` columns, and the same number of `<outputEntry>` elements as there are `<output>` columns. |

---

## Layer 3 — Execution Rules (EXEC-*)

Layer 3 validates CPRMV extension attributes. The CPRMV namespace (`https://cprmv.open-regels.nl/0.3.0/`) is defined by the RONL initiative to capture the legal provenance and classification of each decision rule. These attributes are required for RONL-compliant publishing but are not enforced by Operaton itself.

---

### EXEC-001

| | |
|---|---|
| **Severity** | info |
| **Trigger** | No element in the document has an attribute in the CPRMV namespace |
| **Rationale** | CPRMV attributes are the mechanism by which a DMN file records its connection to Dutch legislation. Without them, the exported Turtle will contain no legal provenance metadata. The issue is `info` rather than `warning` because a DMN may be published to TriplyDB as a technical artefact before CPRMV metadata has been added. |
| **Fix** | Add CPRMV namespace declaration to `<definitions>`: `xmlns:cprmv="https://cprmv.open-regels.nl/0.3.0/"`, then add attributes such as `cprmv:rulesetType`, `cprmv:ruleType`, and `cprmv:confidence` to your decision elements. |

---

### EXEC-002

| | |
|---|---|
| **Severity** | error |
| **Trigger** | A `cprmv:rulesetType` attribute has a value that is not in the allowed set: `decision-table`, `conditional-calculation`, `constraint-table`, `derivation-table` |
| **Rationale** | `rulesetType` classifies the structural pattern of the ruleset. An invalid value means the classification cannot be interpreted by downstream systems that use this attribute to determine how to present or execute the ruleset. |
| **Fix** | Set `cprmv:rulesetType` to one of the four allowed values. |

---

### EXEC-003

| | |
|---|---|
| **Severity** | error |
| **Trigger** | A `cprmv:ruleType` attribute has a value not in: `temporal-period`, `conditional`, `derivation`, `constraint`, `decision-rule`, `default` |
| **Rationale** | `ruleType` classifies the logical nature of an individual rule. The six types map to distinct patterns in Dutch administrative law: a temporal period rule applies during a date range; a conditional rule applies when certain conditions are met; a derivation computes a value from other values; a constraint checks that a value is within bounds; a decision-rule is a general decision table row; a default applies when no other rule fires. An unknown value cannot be processed by RONL vocabulary services. |
| **Fix** | Set `cprmv:ruleType` to one of the six allowed values. |

---

### EXEC-004

| | |
|---|---|
| **Severity** | error |
| **Trigger** | A `cprmv:confidence` attribute has a value not in: `low`, `medium`, `high` |
| **Rationale** | `confidence` expresses how certain the rule author is that the DMN correctly implements the underlying legislation. An invalid value cannot be interpreted by governance tooling. |
| **Fix** | Set `cprmv:confidence` to `low`, `medium`, or `high`. |

---

### EXEC-005

| | |
|---|---|
| **Severity** | error |
| **Trigger** | A `cprmv:validFrom` or `cprmv:validUntil` attribute has a value that does not match `YYYY-MM-DD` |
| **Rationale** | CPRMV dates are ISO 8601 calendar dates. An incorrectly formatted date cannot be parsed for temporal reasoning — for example, determining whether a rule is currently in effect. Operaton does not validate these attributes, so malformed dates survive deployment but cause silent failures in TriplyDB temporal queries. |
| **Fix** | Use ISO format: `cprmv:validFrom="2026-01-01"`. |

---

### EXEC-006

| | |
|---|---|
| **Severity** | error |
| **Trigger** | A `cprmv:bwbId` attribute has a value that does not match `^[A-Z]{4}\d{7}$` (four uppercase letters followed by seven digits, e.g. `BWBR0011453`) |
| **Rationale** | BWB IDs are the persistent identifiers for Dutch legislation on `wetten.overheid.nl`. A malformed BWB ID cannot be resolved to a legislation page, breaking the link between the DMN rule and its legal source. |
| **Fix** | Use the correct BWB ID format. BWB IDs can be found in the URL of the legislation on `wetten.overheid.nl` (e.g. `https://wetten.overheid.nl/BWBR0011453`). |

---

### EXEC-007

| | |
|---|---|
| **Severity** | error |
| **Trigger** | A rule has `cprmv:ruleType="temporal-period"` but is missing either `cprmv:validFrom` or `cprmv:validUntil` |
| **Rationale** | A temporal-period rule is, by definition, bounded in time. A rule with `ruleType=temporal-period` but no start or end date is semantically incomplete — it is impossible to determine when the rule is in effect. This is the most common CPRMV authoring mistake. |
| **Fix** | Add both `cprmv:validFrom` and `cprmv:validUntil` to any rule with `ruleType="temporal-period"`. |

---

## Layer 4 — Interaction Rules (INT-*)

Layer 4 validates the Decision Requirements Diagram (DRD) — the graph of decisions and information requirements that connects inputs to the final decision output. DRD errors mean the model's internal wiring is broken.

---

### INT-001

| | |
|---|---|
| **Severity** | error |
| **Trigger** | An `<informationRequirement>` element has an `href` attribute that references a decision or input ID that does not exist in the same `<definitions>` document |
| **Rationale** | An `<informationRequirement>` declares that decision A depends on the output of decision B (or the value of an `<inputData>` element). A broken `href` means Operaton cannot locate the dependency at runtime, causing an `NullPointerException` or a silent evaluation failure. This is particularly common after copy-paste from another DMN file, where IDs may not have been updated. |
| **Fix** | Verify that the `href="#some-id"` in every `<informationRequirement>` corresponds to the `id` of an element in the same document. |

---

### INT-002

| | |
|---|---|
| **Severity** | warning |
| **Trigger** | A `<decision>` element has an `<informationRequirement>` that references another `<decision>` but the referenced decision has no corresponding `<inputData>` element feeding into it |
| **Rationale** | This pattern is technically valid but often indicates a partially wired DRD where an intermediate decision has been declared but not connected from the diagram's input side. |
| **Fix** | Review the DRD wiring and either add the missing `<inputData>` connection or verify that the reference is intentional. |

---

### INT-003

| | |
|---|---|
| **Severity** | warning |
| **Trigger** | An `<inputData>` element exists in the document but is not referenced by any `<informationRequirement>` |
| **Rationale** | An orphaned `<inputData>` element declares an input that no decision actually uses. It adds clutter to the DRD, makes the model harder to understand, and will cause the CPSV Editor to generate `cpsv:Input` metadata for an input that has no effect on any decision outcome. |
| **Fix** | Either connect the `<inputData>` element to a decision via `<informationRequirement>`, or remove it from the model. |

---

### INT-004

| | |
|---|---|
| **Severity** | warning |
| **Trigger** | A `<decision>` element has a `<variable>` child whose `name` attribute does not match the `name` attribute of the `<inputData>` element that feeds into it (where an exact name match would be expected) |
| **Rationale** | Operaton resolves inputs to decisions by variable name at runtime. If the variable name declared in `<variable name="...">` does not match the name used in the FEEL expression that consumes it, the input evaluates to null. This is a common source of "my rule never fires" bugs. |
| **Fix** | Align the `<variable name="...">` on `<inputData>` with the name referenced in the decision table's input expressions. |

---

### INT-005

| | |
|---|---|
| **Severity** | warning |
| **Trigger** | An `<inputData>` element is not referenced by any `<informationRequirement>` in the document (duplicate of INT-003, emitted once per orphaned element with its element reference) |
| **Rationale** | See INT-003. This issue is emitted per element to provide actionable location information for each orphan. |
| **Fix** | See INT-003. |

---

## Layer 5 — Content (CON-*)

Layer 5 checks metadata quality: whether descriptive attributes are populated and whether elements that should carry content actually do. These checks have no functional impact on execution but are required for RONL publishing quality.

---

### CON-001

| | |
|---|---|
| **Severity** | info |
| **Trigger** | A CPRMV descriptive attribute (`cprmv:title`, `cprmv:description`, or `cprmv:note`) is present but empty |
| **Rationale** | CPRMV descriptive attributes are used by the Linked Data Explorer and TriplyDB to display human-readable metadata about rules. An empty attribute is functionally equivalent to a missing one but signals that the author added the attribute placeholder without filling it in. |
| **Fix** | Add meaningful text to the attribute, or remove it if it is not applicable. |

---

### CON-002

| | |
|---|---|
| **Severity** | info |
| **Trigger** | A CPRMV descriptive attribute is present but contains only whitespace |
| **Rationale** | Same as CON-001 — whitespace-only content is treated as absent. |
| **Fix** | Add meaningful text or remove the attribute. |

---

### CON-003

| | |
|---|---|
| **Severity** | info |
| **Trigger** | A `<decision>` element has a `<variable>` child that is missing a `typeRef` attribute |
| **Rationale** | The `typeRef` on a decision's `<variable>` declares the FEEL type of the decision's output. Without it, consuming decisions in a DRD cannot perform type-safe input binding, and the chain builder in the Linked Data Explorer cannot verify type compatibility between linked DMNs. |
| **Fix** | Add `typeRef="boolean"` (or the appropriate FEEL type) to the `<variable>` element inside each `<decision>`. |

---

### CON-004

| | |
|---|---|
| **Severity** | info |
| **Trigger** | A `<variable>` element (anywhere in the document) is missing `typeRef` |
| **Rationale** | See CON-003. This check applies to all `<variable>` elements, including those inside `<inputData>` elements. |
| **Fix** | Add `typeRef` to all `<variable>` elements. |

---

### CON-005

| | |
|---|---|
| **Severity** | info |
| **Trigger** | A `<textAnnotation>` element exists but its `<text>` child is empty or missing |
| **Rationale** | Text annotations are author-provided comments in the DRD. An empty annotation is a placeholder that was never filled in. While harmless, it adds noise to the diagram and signals incomplete documentation. |
| **Fix** | Add a meaningful description to the annotation, or remove it. |

---

## Issue severity summary

| Code | Severity |
|---|---|
| BASE-PARSE | 🔴 error |
| BASE-ROOT | 🔴 error |
| BASE-NS | 🔴 error |
| BASE-NAME | 🟡 warning |
| BASE-NSATTR | 🟡 warning |
| BASE-EMPTY | 🟡 warning |
| BIZ-001 | 🔴 error |
| BIZ-002 | 🟡 warning |
| BIZ-003 | 🟡 warning |
| BIZ-004 | 🟡 warning |
| BIZ-005 | 🔴 error |
| EXEC-001 | 🔵 info |
| EXEC-002 | 🔴 error |
| EXEC-003 | 🔴 error |
| EXEC-004 | 🔴 error |
| EXEC-005 | 🔴 error |
| EXEC-006 | 🔴 error |
| EXEC-007 | 🔴 error |
| INT-001 | 🔴 error |
| INT-002 | 🟡 warning |
| INT-003 | 🟡 warning |
| INT-004 | 🟡 warning |
| INT-005 | 🟡 warning |
| CON-001 | 🔵 info |
| CON-002 | 🔵 info |
| CON-003 | 🔵 info |
| CON-004 | 🔵 info |
| CON-005 | 🔵 info |

---

## API contract

**Endpoint:** `POST /v1/dmns/validate`

**Request:**
```json
{ "content": "<xml string — the full DMN file content>" }
```

**Response (success):**
```json
{
  "success": true,
  "data": {
    "valid": true,
    "parseError": null,
    "layers": {
      "base":        { "label": "Base DMN",         "issues": [] },
      "business":    { "label": "Business Rules",   "issues": [] },
      "execution":   { "label": "Execution Rules",  "issues": [] },
      "interaction": { "label": "Interaction Rules","issues": [] },
      "content":     { "label": "Content",          "issues": [] }
    },
    "summary": { "errors": 0, "warnings": 6, "infos": 1 }
  },
  "timestamp": "2026-02-25T14:32:11.000Z"
}
```

**Issue object:**
```json
{
  "severity": "warning",
  "code": "INT-005",
  "message": "<inputData id=\"InputData_ingezetene_requirement\"> is not referenced by any informationRequirement and will be inaccessible to decisions.",
  "location": "<inputData id=\"InputData_ingezetene_requirement\">",
  "line": null,
  "column": null
}
```

**Response (parse error — layers 2–5 skipped):**
```json
{
  "success": true,
  "data": {
    "valid": false,
    "parseError": "XML is not well-formed: ...",
    "layers": {
      "base": { "label": "Base DMN", "issues": [{ "severity": "error", "code": "BASE-PARSE", ... }] },
      "business":    { "label": "Business Rules",   "issues": [] },
      "execution":   { "label": "Execution Rules",  "issues": [] },
      "interaction": { "label": "Interaction Rules","issues": [] },
      "content":     { "label": "Content",          "issues": [] }
    },
    "summary": { "errors": 1, "warnings": 0, "infos": 0 }
  },
  "timestamp": "..."
}
```

**Response (bad request):**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Request body must contain a \"content\" field with the DMN XML as a string."
  },
  "timestamp": "..."
}
```

The endpoint is unauthenticated. Maximum request body size is 10 MB.
