---
component: CPRMV
---

# CPRMV Vocabulary Reference

The CPRMV vocabulary is defined in `rdf/0.4.2/cprmv.ttl`, with SHACL shapes in `rdf/0.4.2/cprmv.shacl.ttl`, and published as the CPRMV specification at [cprmv.open-regels.nl/respec/](https://cprmv.open-regels.nl/respec/). This page provides a compact reference of the classes and properties relevant to the API's output.

**Vocabulary namespace:** `https://standaarden.open-regels.nl/standards/cprmv/0.4.2#`  
**Prefix:** `cprmv:`  
**Version:** 0.4.2  

Related namespaces used by the API: `cprmvmethods:` = `https://cprmv.open-regels.nl/0.4.2/methods/` (method definitions) and `cprmv-serve:` = `https://cprmv.open-regels.nl/0.4.2/serve-api/` (API configuration properties).

!!! note "The copy the API loads"
    The API loads the vocabulary from `serve_api/data/cprmv.ttl`, which `make methods` copies from `rdf/0.4.2/cprmv.ttl`. The committed copy predates the 0.4.2 additions below: it carries the 0.4.2 namespace but lacks `SerialisationMethod`, the registers, catalogs and echelons, and still declares `cprmv:ReferencenMethod` as a subclass of `cprmv:RuleMethod`. `/methods` serves that copy.

---

## Classes

| Class                       | Subclass of                      | Description                                          |
| --------------------------- | -------------------------------- | ---------------------------------------------------- |
| `cprmv:RuleSet`             | `frbroo:F1_Work`, `cv:Output`    | A versioned set of rules, output of a public service. A RuleSet is a FRBR Work, **not** an `eli:LegalResource` — a formalisation (e.g. business rules) is not in itself a legal resource (`eli:LegalResource` is itself a subclass of FRBR Work). |
| `cprmv:Analysis`            | `cprmv:RuleSet`                  | Rule set produced by an analysis method              |
| `cprmv:DecisionModel`       | `cprmv:RuleSet`                  | Rule set produced by a formalisation method          |
| `cprmv:TestSet`             | `cprmv:RuleSet`                  | Rule set of test cases defined following a test method |
| `cprmv:OrganisationCatalog` | `cprmv:RuleSet`                  | Catalog of officially acknowledged organisations that produce rule sets |
| `cprmv:ServiceCatalog`      | `cprmv:RuleSet`                  | Catalog of officially acknowledged public services in which rule sets are produced |
| `cprmv:Rule`                | —                                | An individual rule within a rule set                 |
| `cprmv:Parameter`           | `cprmv:Rule`                     | A rule representing a parameter value                |
| `cprmv:AcknowledgedOrganisation` | `cprmv:Rule`                | The official acknowledgement of a `cv:PublicOrganisation` |
| `cprmv:AcknowledgedService` | `cprmv:Rule`                     | The official acknowledgement of a `cpsv:PublicService` |
| `cprmv:Explanation`         | `cprmv:Rule`                     | Explains a rule set or rule                          |
| `cprmv:Decision`            | `cprmv:Rule`                     | A rule defined following an execution method         |
| `cprmv:Case`                | `cprmv:Rule`                     | A list of decisions defined following an execution method |
| `cprmv:TestCase`            | `cprmv:Case`                     | A case defined for and following a test method       |
| `cprmv:RuleMethod`          | —                                | Base class for all method types                      |
| `cprmv:AnalysisMethod`      | `cprmv:RuleMethod`               |                                                      |
| `cprmv:FormalisationMethod` | `cprmv:RuleMethod`               |                                                      |
| `cprmv:SerialisationMethod` | `cprmv:RuleMethod`               | Meta method: serialising rules as a storable text file (XML, JSON, YAML, Turtle) |
| `cprmv:CodificationMethod`  | `cprmv:RuleMethod`               |                                                      |
| `cprmv:ExecutionMethod`     | `cprmv:RuleMethod`               |                                                      |
| `cprmv:ExplanationMethod`   | `cprmv:RuleMethod`               |                                                      |
| `cprmv:TestMethod`          | `cprmv:RuleMethod`               |                                                      |
| `cprmv:PublicationMethod`   | `cprmv:RuleMethod`               | Publication of rule set definitions, apart from their execution |
| `cprmv:ReferenceMethod`     | `cprmv:PublicationMethod`        | Meta method: referencing rules and rule sets         |
| `cprmv:OrganisationRegister`| `cprmv:PublicationMethod`        | Method for publishing an organisation catalog        |
| `cprmv:ServiceRegister`     | `cprmv:PublicationMethod`        | Method for publishing a service catalog              |
| `cprmv:Echelon`             | —                                | A category of a rule set in service delivery — see [Echelons](#echelons) |

---

## Properties

### On cprmv:RuleSet and cprmv:Rule

| Property          | Domain                                              | Range                          | Description                                               |
| ----------------- | --------------------------------------------------- | ------------------------------ | --------------------------------------------------------- |
| `cprmv:id`        | `cprmv:Rule` ∪ `cprmv:RuleSet` ∪ `cprmv:RuleMethod` | literal                        | Unique identifier (lang-tagged, used for path navigation) |
| `cprmv:hasPart`   | `cprmv:RuleSet` ∪ `cprmv:Rule`                      | RDF list                       | Ordered list of contained rules                           |
| `cprmv:isBasedOn` | `cprmv:RuleSet` ∪ `cprmv:Rule`                      | `cprmv:RuleSet` ∪ `cprmv:Rule` | Subproperty of `frbroo:R2_is_derivative_of` and `prov:wasDerivedFrom` |
| `cprmv:comment`   | `cprmv:Rule` ∪ `cprmv:RuleSet` ∪ `cprmv:RuleMethod` | `xsd:string` or `rdf:langString` (SHACL) |                                                 |

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
| `cprmv:sourcequote`    | `xsd:string` or `rdf:langString` (SHACL) | Replicates (part of) the definition of the rule being extended |

### On cprmv:DecisionModel

| Property            | Range            | Description                      |
| ------------------- | ---------------- | -------------------------------- |
| `cprmv:hasAnalysis` | `cprmv:Analysis` | Subproperty of `cprmv:isBasedOn` |

### On cprmv:Explanation

| Property         | Range                          | Description                      |
| ---------------- | ------------------------------ | -------------------------------- |
| `cprmv:explains` | `cprmv:Rule` ∪ `cprmv:RuleSet` | The rule or rule set explained   |

### On cprmv:AcknowledgedOrganisation and cprmv:AcknowledgedService

| Property             | Range (SHACL)                                   | Description |
| -------------------- | ----------------------------------------------- | ----------- |
| `cprmv:acknowledges` | `cv:PublicOrganisation` / `cpsv:PublicService`  | The organisation or service the rule acknowledges |

### On cprmv:RuleMethod

| Property               | Range           | Description                                     |
| ---------------------- | --------------- | ----------------------------------------------- |
| `cprmv:refinesTowards` | `cprmv:Echelon` | The echelon a method refines rule sets towards  |
| `cprmv:refinesFrom`    | `cprmv:Echelon` | The echelon a method refines rule sets from     |

### Echelons

`cprmv:Echelon` has six subclasses, loosely based on the theory of hierarchical, multilevel systems (Mesarovic, Macko, Takahara):

| Echelon                    | Tied to                                                          |
| -------------------------- | ---------------------------------------------------------------- |
| `cprmv:AgreementEchelon`   | Contract management: solutions as natural-language descriptions  |
| `cprmv:SemanticEchelon`    | Contract management: concepts and norms                          |
| `cprmv:OntologicEchelon`   | Contract management: information models of concepts and norms    |
| `cprmv:LogicEchelon`       | Contract management: logically formalised, operable models (decision and process models) |
| `cprmv:OperableEchelon`    | Operations: operable solutions followed in service delivery      |
| `cprmv:SupportEchelon`     | Support processes: evaluation of solutions                       |

---

## SHACL constraints

`rdf/0.4.2/cprmv.shacl.ttl` constrains the output as follows:

- **`cprmv:RuleSetShape`** — `cprmv:id` (at least one), exactly one `cprmv:validFrom` (`xsd:date`), optional `cprmv:validUntil` / `cprmv:publishedOn`, at least one `cprmv:isOutputOf` (`cpsv:PublicService`) and at least one `cprmv:hasMethod` (`cprmv:RuleMethod`). Through the shared property shape `cprmv:hasPartShape` — the sequence path `cprmv:hasPart / rdf:rest* / rdf:first` — a rule set must contain at least one member, and every member must be a `cprmv:Rule`.
- **`cprmv:RuleShape`** — `cprmv:id` (at least one), at most one `cprmv:definition` and one `cprmv:postDefinition`, `cprmv:hasPart` zero or more.
- **`cprmv:id`, `cprmv:comment` and `cprmv:sourcequote`** accept `xsd:string` or `rdf:langString`, where constrained.
- **Method shapes** — every `cprmv:RuleMethod` needs a `cprmv:id`; `refinesTowards` and `refinesFrom` must point to a `cprmv:Echelon`, and each method subclass narrows which echelons it may refine from and towards (for example, an analysis method refines towards the agreement, semantic or ontologic echelon; a formalisation method towards the logic or operable echelon).
- **Catalogs** — an `OrganisationCatalog` must have an `OrganisationRegister` as method, a `ServiceCatalog` a `ServiceRegister`; `cprmv:acknowledges` is required on `AcknowledgedOrganisation` (`cv:PublicOrganisation`) and `AcknowledgedService` (`cpsv:PublicService`).

`rdf/0.4.2/test.sh` runs pyshacl over the test files and method definitions; it is a manual check.

---

## External standards alignment

| CPRMV class/property | Aligned standard                                         |
| -------------------- | -------------------------------------------------------- |
| `cprmv:RuleSet`      | `frbroo:F1_Work`, `cv:Output`, `dcat:Dataset` member (`cprmv:is_part_of`) |
| `cprmv:isBasedOn`    | `frbroo:R2_is_derivative_of`, `prov:wasDerivedFrom`     |
| `cprmv:isOutputOf`   | inverse of `schema:serviceOutput`, `prov:wasGeneratedBy` |

The full alignment table and rationale are in the [CPRMV specification](https://cprmv.open-regels.nl/respec/).
