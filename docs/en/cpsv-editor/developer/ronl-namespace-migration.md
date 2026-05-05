# RONL Namespace Migration

This page documents the reorganisation of the RONL namespace that took effect with v1.9.x and explains what the parser does to maintain backward compatibility.

---

## Background

The original RONL namespace (`https://regels.overheid.nl/termen/`) was used for both governance properties (validation, certification) and rule management properties. These concerns have been separated into two distinct namespaces:

| Namespace | Prefix | Purpose |
|---|---|---|
| `https://regels.overheid.nl/ontology#` | `ronl:` | Organisational governance (validation, certification, vendor) |
| `https://cprmv.open-regels.nl/0.3.0/` | `cprmv:` | Rule management (decision models, rules, parameters) |

The old namespace is deprecated but still accepted by the parser for backward compatibility.

---

## What changed

**Old (deprecated):**

```turtle
@prefix ronl: <https://regels.overheid.nl/termen/> .

<something>
    ronl:hasAnalysis <...> ;
    ronl:hasMethod <...> ;
    ronl:implements <...> .
```

**New (current):**

```turtle
@prefix ronl:  <https://regels.overheid.nl/ontology#> .
@prefix cprmv: <https://cprmv.open-regels.nl/0.3.0/> .

<something>
    cprmv:hasAnalysis <...> ;
    cprmv:hasMethod <...> ;
    cprmv:implements <...> .
```

---

## Parser configuration

The parser registers both namespaces:

```javascript
// src/config/vocabularies.config.js
namespaces: {
  'https://regels.overheid.nl/ontology#':  ['ronl'],
  'https://cprmv.open-regels.nl/0.3.0/':  ['cprmv'],
  'https://regels.overheid.nl/termen/':   ['ronl-legacy'],  // never exported
}
```

And maps legacy properties to their current equivalents:

```javascript
propertyAliases: {
  'ronl-legacy:hasAnalysis':     'cprmv:hasAnalysis',
  'ronl-legacy:hasMethod':       'cprmv:hasMethod',
  'ronl-legacy:implements':      'cprmv:implements',
  'ronl-legacy:implementedBy':   'cprmv:implementedBy',
  'ronl-legacy:confidenceLevel': 'cprmv:confidenceLevel',
  'ronl-legacy:validFrom':       'ronl:validFrom',
  'ronl-legacy:validUntil':      'ronl:validUntil',
  'ronl-legacy:extends':         'ronl:extends',
}
```

The `ronl-legacy` prefix is an internal alias only — it never appears in exported Turtle. Files imported with the old namespace are silently normalised and re-exported with the current namespaces.

---

## SPARQL query migration

When querying across both old and new data, use `OPTIONAL` to handle both namespaces:

```sparql
PREFIX cprmv: <https://cprmv.open-regels.nl/0.3.0/>
PREFIX ronl-old: <https://regels.overheid.nl/termen/>

SELECT ?service ?analysis WHERE {
  ?service a cpsv:PublicService .
  OPTIONAL { ?service cprmv:hasAnalysis ?analysis }
  OPTIONAL { ?service ronl-old:hasAnalysis ?analysis }
}
```

---

## RONL governance properties (current)

The `ronl:` prefix now exclusively covers organisational governance properties. These are defined in the [RONL Ontology](../reference/ronl-ontology.md) and apply to `cprmv:DecisionModel` and `cpsv:PublicService` subjects:

| Property | Purpose |
|---|---|
| `ronl:validatedBy` | Organisation that validated the model |
| `ronl:validationStatus` | Validation state (`validated`, `pending`, etc.) |
| `ronl:validatedAt` | Validation date |
| `ronl:validationNote` | Free-text validation notes |
| `ronl:certifiedBy` | Organisation that certified the implementation |
| `ronl:certificationStatus` | Certification state (`certified`, `self-assessed`, etc.) |
| `ronl:certifiedAt` | Certification date |
| `ronl:certificationNote` | Free-text certification notes |
| `ronl:basedOn` | Reference implementation URI |
| `ronl:vendorType` | Vendor classification |
