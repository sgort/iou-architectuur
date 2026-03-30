# CPRMV Vocabulary Reference

The CPRMV vocabulary is defined in `rdf/cprmv.ttl` and published as the CPRMV specification at [acc.cprmv.open-regels.nl/respec/](https://acc.cprmv.open-regels.nl/respec/). This page provides a compact reference of the classes and properties relevant to the API's output.

**Vocabulary namespace:** `https://standaarden.open-regels.nl/standards/cprmv/0.4.0/#`  
**Prefix:** `cprmv:`  
**Version:** 0.4.0 (published 2026-02-09)  

---

## Classes

| Class                       | Subclass of                      | Description                                          |
| --------------------------- | -------------------------------- | ---------------------------------------------------- |
| `cprmv:RuleSet`             | `eli:LegalResource`, `cv:Output` | A versioned set of rules, output of a public service |
| `cprmv:Analysis`            | `cprmv:RuleSet`                  | Rule set produced by an analysis method              |
| `cprmv:DecisionModel`       | `cprmv:RuleSet`                  | Rule set produced by a formalisation method          |
| `cprmv:Rule`                | —                                | An individual rule within a rule set                 |
| `cprmv:Parameter`           | `cprmv:Rule`                     | A rule representing a parameter value                |
| `cprmv:RuleMethod`          | —                                | Base class for all method types                      |
| `cprmv:AnalysisMethod`      | `cprmv:RuleMethod`               |                                                      |
| `cprmv:FormalisationMethod` | `cprmv:RuleMethod`               |                                                      |
| `cprmv:CodificationMethod`  | `cprmv:RuleMethod`               |                                                      |
| `cprmv:ExecutionMethod`     | `cprmv:RuleMethod`               |                                                      |
| `cprmv:ExplanationMethod`   | `cprmv:RuleMethod`               |                                                      |
| `cprmv:TestMethod`          | `cprmv:RuleMethod`               |                                                      |
| `cprmv:PublicationMethod`   | `cprmv:RuleMethod`               | Tied to an official publication repository           |
| `cprmv:ReferenceMethod`     | `cprmv:RuleMethod`               |                                                      |
| `cprmv:Explanation`         | —                                | Explains a rule set or rule                          |
| `cprmv:TestCase`            | —                                |                                                      |
| `cprmv:TestSet`             | —                                |                                                      |
| `cprmv:Decision`            | —                                |                                                      |
| `cprmv:Case`                | —                                |                                                      |

---

## Properties

### On cprmv:RuleSet and cprmv:Rule

| Property          | Domain                                              | Range                          | Description                                               |
| ----------------- | --------------------------------------------------- | ------------------------------ | --------------------------------------------------------- |
| `cprmv:id`        | `cprmv:Rule` ∪ `cprmv:RuleSet` ∪ `cprmv:RuleMethod` | literal                        | Unique identifier (lang-tagged, used for path navigation) |
| `cprmv:hasPart`   | `cprmv:RuleSet` ∪ `cprmv:Rule`                      | RDF list                       | Ordered list of contained rules or rule sets              |
| `cprmv:isBasedOn` | `cprmv:RuleSet` ∪ `cprmv:Rule`                      | `cprmv:RuleSet` ∪ `cprmv:Rule` | Subproperty of `eli:based_on` and `prov:wasDerivedFrom`   |
| `cprmv:comment`   | —                                                   | `xsd:string`                   |                                                           |

### On cprmv:RuleSet only

| Property            | Range                | Description                       |
| ------------------- | -------------------- | --------------------------------- |
| `cprmv:validFrom`   | `xsd:date`           |                                   |
| `cprmv:validUntil`  | `xsd:date`           |                                   |
| `cprmv:publishedOn` | `xsd:date`           |                                   |
| `cprmv:isOutputOf`  | `cpsv:PublicService` | Inverse of `schema:serviceOutput` |
| `cprmv:hasMethod`   | `cprmv:RuleMethod`   |                                   |

### On cprmv:Rule only

| Property               | Range        | Description                      |
| ---------------------- | ------------ | -------------------------------- |
| `cprmv:definition`     | literal      | Natural language definition text |
| `cprmv:postDefinition` | literal      | Continuation of definition       |
| `cprmv:sourceQuote`    | `xsd:string` | Verbatim source text             |

### On cprmv:DecisionModel

| Property            | Range            | Description                      |
| ------------------- | ---------------- | -------------------------------- |
| `cprmv:hasAnalysis` | `cprmv:Analysis` | Subproperty of `cprmv:isBasedOn` |

---

## External standards alignment

| CPRMV class/property | Aligned standard                                         |
| -------------------- | -------------------------------------------------------- |
| `cprmv:RuleSet`      | `eli:LegalResource`, `cv:Output`, `dcat:Dataset` member  |
| `cprmv:isBasedOn`    | `eli:based_on`, `prov:wasDerivedFrom`                    |
| `cprmv:isOutputOf`   | inverse of `schema:serviceOutput`, `prov:wasGeneratedBy` |

The full alignment table and rationale are in the [CPRMV specification](https://acc.cprmv.open-regels.nl/respec/).
