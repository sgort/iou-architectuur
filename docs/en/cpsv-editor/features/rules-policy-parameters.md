# Rules, Policy & Parameters

The editor implements the **Rules–Policy–Parameters (RPP)** architectural pattern for structuring government business rule management. Three separate tabs map to the three layers of this pattern, each visually distinguished by colour and labelled with its RPP role.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Tab navigation bar showing the Rules (blue) with RPP layer badges](../../assets/screenshots/cpsv-editor-rpp-tabs-rules.png)
  <figcaption>Tab navigation bar showing the Rules (blue) with RPP layer badges</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Tab navigation bar showing the CPRMV/Policy (purple) with RPP layer badges](../../assets/screenshots/cpsv-editor-rpp-tabs-policy.png)
  <figcaption>Tab navigation bar showing the CPRMV/Policy (purple) with RPP layer badges</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Tab navigation bar showing the Parameters (green) tabs with RPP layer badges](../../assets/screenshots/cpsv-editor-rpp-tabs-parameters.png)
  <figcaption>Tab navigation bar showing the Parameters (green) tabs with RPP layer badges</figcaption>
</figure>

---

## The three layers

| Layer          | Tab        | Colour    | RDF class                       | Description                                           |
| -------------- | ---------- | --------- | ------------------------------- | ----------------------------------------------------- |
| **Rules**      | Rules      | 🔵 Blue   | `cpsv:Rule, cprmv:TemporalRule` | Executable decision logic that operationalises policy |
| **Policy**     | CPRMV      | 🟣 Purple | `cprmv:Rule` (grouped in `cprmv:RuleSet`) | Normative values derived directly from legislation    |
| **Parameters** | Parameters | 🟢 Green  | `cprmv:ParameterWaarde`         | Configurable values that tune rule behaviour          |

---

## Rules layer

Rules are time-bounded (`cprmv:TemporalRule`) business rules that implement policy decisions. Each rule carries a mandatory identifier, title and description, an optional URI, temporal validity dates (`cprmv:validFrom`, `cprmv:validUntil`), a confidence level (`cprmv:confidenceLevel`), and an extension reference (`cprmv:isBasedOn`) that links the rule to a specific article or version of the legal resource. When a legal resource is set, the rule's `cpsv:implements` points at the `eli:LegalResource` (as CPSV-AP's RuleShape requires), not the service.

The dual typing `a cpsv:Rule, cprmv:TemporalRule` ensures both CPSV-AP 3.2.0 compliance and compatibility with the Dutch CPRMV extensions.

!!! note "Vocabulary migration (v2.0.0)"
    Temporal-rule typing and properties moved from the `ronl:` namespace to `cprmv:`
    (`ronl:TemporalRule` → `cprmv:TemporalRule`, `ronl:validFrom`/`validUntil`/`confidenceLevel`
    → `cprmv:…`, `ronl:extends` → `cprmv:isBasedOn`). The `ronl:` namespace is now reserved
    for governance (validation, certification, vendor). Legacy files still import correctly.

---

## Policy layer (CPRMV)

The CPRMV tab captures normative rules extracted directly from legislation — the values mandated by law rather than the computational logic that applies them. These are modelled as `cprmv:Rule` and imported either by loading JSON or by filling in individual fields.

Each CPRMV rule has six fields: rule id (`cprmv:id`), ruleset id (`cprmv:rulesetId`), definition (full legal text, `cprmv:definition`), situational context (`cprmv:situatie`), the normative value itself (`cprmv:norm`), and the legal source path (`cprmv:ruleIdPath`).

**CPRMV 0.4.1 RuleSets.** On export, every unique `rulesetId` produces a conformant `cprmv:RuleSet` — carrying `cprmv:id`, `cprmv:validFrom`, `cprmv:isOutputOf` (→ the public service), a dual-typed `cprmv:RuleMethod`, an ordered `cprmv:hasPart` list of its rules, and a `prov:wasDerivedFrom` link to the legal source. This replaces the v1.9.4 `cprmv:Dataset` block. See [CPRMV RuleSet Generation](../developer/cprmv-dataset-generation.md).

**Importing the CPRMV Rules API output.** The **Import JSON** button (and the CPRMV tab's **Load Example**) accept the CPRMV 0.4.1 Rules API shape — an array of `cprmv:RuleSet` objects with nested `…#hasPart` maps — as well as legacy 0.3.0 and flat-array exports. `flattenCprmvRules` (`src/utils/cprmvImport.js`) walks and flattens nested sub-rules into the editor's flat model, with nested rules inheriting their parent's `rulesetId`.

An informational banner in the CPRMV tab shows the currently linked legal resource and the `cprmv:implements` property that creates an explicit semantic link between a policy rule and the versioned legislation it implements — enabling clean SPARQL queries without fragile string parsing.

---

## Parameters layer

Parameters are configurable constants that tune rule behaviour without changing the rules themselves — for example, income thresholds, age limits, or regional rates. Modelled as `cprmv:ParameterWaarde` (was `ronl:ParameterWaarde` before v2.0.0), each parameter carries a machine-readable notation (`skos:notation`), a numeric value and unit (`schema:value`, `schema:unitCode`), and optional temporal validity (`cprmv:validFrom`, `cprmv:validUntil`).

---

## Why this separation matters

The RPP pattern creates a clear chain of traceability: **Law → Policy → Rule → Parameter → Decision**. The practical benefits are:

**Legal traceability.** Every decision can be traced back to the specific article of legislation that mandates it. When legislation changes, the affected layer is immediately identifiable.

**Organisational agility.** Parameters can be adjusted (e.g. a regional pilot rate) without touching the rules or redeploying decision models. Rules can be versioned without touching the underlying policy statements.

**Governance clarity.** Each layer has distinct ownership. Policy rules are owned by legal teams, computational rules by analysts, and parameters by operational teams. Approval workflows can be scoped to the layer that actually changed.

See [RPP Architecture Reference](../reference/rpp-architecture.md) for the formal specification.
