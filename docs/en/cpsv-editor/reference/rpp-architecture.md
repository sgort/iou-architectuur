# RPP Architecture

The **Rules–Policy–Parameters (RPP)** pattern is the architectural framework for separating government business rule concerns into three distinct, independently governable layers.

---

## The three layers

```
LAW (legislation)
  ↓
POLICY — Normative values extracted from the law (cprmv:Rule)
  ↓  implements
RULES — Executable decision logic that operationalises policy (cpsv:Rule, ronl:TemporalRule)
  ↓  configured by
PARAMETERS — Tunable constants that adjust rule behaviour (ronl:ParameterWaarde)
  ↓
DECISION — Computed outcome for a citizen or case
```

### Policy layer

Policy captures what the law **mandates** — the normative values that must be implemented. It is expressed as `cprmv:Rule` and sourced from legal analysis. Policy is owned by legal and policy teams and changes when legislation changes.

Examples: the legal definition of "eligible for zorgtoeslag", the statutory AOW retirement age formula.

### Rules layer

Rules capture **how** policy is implemented computationally — the executable decision logic. Expressed as `cpsv:Rule, ronl:TemporalRule`, rules are time-bounded and link back to their policy source via `ronl:extends`. Rules are owned by business analysts and are versioned independently of the underlying policy.

Examples: an eligibility check function, a benefit calculation algorithm.

### Parameters layer

Parameters are **configurable constants** that tune rule behaviour without requiring rule changes. Expressed as `ronl:ParameterWaarde`, parameters carry a machine-readable notation, a value, a unit, and temporal validity. They are owned by operational teams who can update them within authorised ranges.

Examples: an income threshold, a regional pilot adjustment factor, a standard premium amount.

---

## Semantic linking

The RPP layers are connected through explicit RDF properties:

```turtle
# Policy rule — linked to legislation
<.../rules/aow-leeftijd-policy>
    a cprmv:Rule ;
    cprmv:implements <https://wetten.overheid.nl/BWBR0002221> .

# Temporal rule — links to policy via ronl:extends
<.../rules/aow-leeftijd-2024>
    a cpsv:Rule, ronl:TemporalRule ;
    ronl:extends <https://wetten.overheid.nl/BWBR0002221/2024-01-01/0/artikel/7a> ;
    ronl:validFrom "2024-01-01"^^xsd:date ;
    ronl:validUntil "2024-12-31"^^xsd:date .

# Parameter — used by the rule
<.../parameters/aow-standaard-leeftijd>
    a ronl:ParameterWaarde ;
    skos:notation "AOW_LEEFTIJD_STANDAARD" ;
    schema:value "67" ;
    schema:unitCode "ANN" .
```

---

## Governance benefits

**Legal traceability.** Every decision can be traced from output back to the specific legal article that mandates it. When a SPARQL query links `cprmv:DecisionRule → cprmv:extends → eli:LegalResource`, the chain from decision to law is explicit and machine-verifiable.

**Organisational agility.** Parameters can be updated by operational teams within their authorised scope, without touching rules (which require analyst approval) or policy (which requires legal approval). This reduces the cost and risk of routine maintenance.

**Governance clarity.** Each layer has a distinct approval workflow and ownership. Changes to policy require legal sign-off. Changes to rules require analyst review. Changes to parameters are self-service within defined bounds.

**Version control compatibility.** Because each layer is expressed as separate entities in the Turtle file, git diffs are scoped to the layer that actually changed — a parameter update does not create noise in the rules or policy sections.

---

## Implementation in the editor

The three RPP tabs are visually differentiated with colour coding and explanatory banners. Each tab displays its RPP layer label and a brief explanation of how that layer relates to the others.

The `cprmv:implements` property (v1.9.0) creates automatic semantic linking between CPRMV policy rules and their legal resource, without requiring manual user configuration.
