# Rules, Policy & Parameters

The editor implements the **Rules–Policy–Parameters (RPP)** architectural pattern for structuring government business rule management. Three separate tabs map to the three layers of this pattern, each visually distinguished by colour and labelled with its RPP role.

<figure markdown>
  ![Screenshot: Tab navigation bar showing the Rules (blue) with RPP layer badges](../../assets/screenshots/cpsv-editor-rpp-tabs-rules.png)
  <figcaption>Tab navigation bar showing the Rules (blue) with RPP layer badges</figcaption>
</figure>

<figure markdown>
  ![Screenshot: Tab navigation bar showing the CPRMV/Policy (purple) with RPP layer badges](../../assets/screenshots/cpsv-editor-rpp-tabs-policy.png)
  <figcaption>Tab navigation bar showing the CPRMV/Policy (purple) with RPP layer badges</figcaption>
</figure>

<figure markdown>
  ![Screenshot: Tab navigation bar showing the Parameters (green) tabs with RPP layer badges](../../assets/screenshots/cpsv-editor-rpp-tabs-parameters.png)
  <figcaption>Tab navigation bar showing the Parameters (green) tabs with RPP layer badges</figcaption>
</figure>

---

## The three layers

| Layer          | Tab        | Colour    | RDF class                      | Description                                           |
| -------------- | ---------- | --------- | ------------------------------ | ----------------------------------------------------- |
| **Rules**      | Rules      | 🔵 Blue   | `cpsv:Rule, ronl:TemporalRule` | Executable decision logic that operationalises policy |
| **Policy**     | CPRMV      | 🟣 Purple | `cprmv:Rule`                   | Normative values derived directly from legislation    |
| **Parameters** | Parameters | 🟢 Green  | `ronl:ParameterWaarde`         | Configurable values that tune rule behaviour          |

---

## Rules layer

Rules are time-bounded (`ronl:TemporalRule`) business rules that implement policy decisions. Each rule carries a mandatory identifier and title, an optional URI, temporal validity dates (`ronl:validFrom`, `ronl:validUntil`), a confidence level, and an extension reference (`ronl:extends`) that links the rule to a specific article or version of the legal resource.

The dual typing `a cpsv:Rule, ronl:TemporalRule` ensures both CPSV-AP 3.2.0 compliance and compatibility with Dutch RONL extensions.

---

## Policy layer (CPRMV)

The CPRMV tab captures normative rules extracted directly from legislation — the values mandated by law rather than the computational logic that applies them. These are modelled as `cprmv:Rule` and imported either by pasting JSON (normenbrief format) or by filling in individual fields.

Each CPRMV rule has six mandatory fields: identifier, title, definition (full legal text), situational context, the normative value itself, and the legal source path (`cprmv:ruleIdPath`).

An informational banner in the CPRMV tab shows the currently linked legal resource and the `cprmv:implements` property that creates an explicit semantic link between a policy rule and the versioned legislation it implements — enabling clean SPARQL queries without fragile string parsing.

---

## Parameters layer

Parameters are configurable constants that tune rule behaviour without changing the rules themselves — for example, income thresholds, age limits, or regional rates. Modelled as `ronl:ParameterWaarde`, each parameter carries a machine-readable notation (`skos:notation`), a numeric value and unit (`schema:value`, `schema:unitCode`), and optional temporal validity.

---

## Why this separation matters

The RPP pattern creates a clear chain of traceability: **Law → Policy → Rule → Parameter → Decision**. The practical benefits are:

**Legal traceability.** Every decision can be traced back to the specific article of legislation that mandates it. When legislation changes, the affected layer is immediately identifiable.

**Organisational agility.** Parameters can be adjusted (e.g. a regional pilot rate) without touching the rules or redeploying decision models. Rules can be versioned without touching the underlying policy statements.

**Governance clarity.** Each layer has distinct ownership. Policy rules are owned by legal teams, computational rules by analysts, and parameters by operational teams. Approval workflows can be scoped to the layer that actually changed.

See [RPP Architecture Reference](../reference/rpp-architecture.md) for the formal specification.
