---
component: CPRMV
---

# Data Model

The CPRMV API produces and consumes data conforming to the CPRMV OWL vocabulary (`rdf/0.4.3/cprmv.ttl`), validated by the SHACL shapes in `rdf/0.4.3/cprmv.shacl.ttl`. The `rdf/` folder keeps one subfolder per version (`0.4.0/` … `0.4.3/`).

---

## Namespace

```
https://standaarden.open-regels.nl/standards/cprmv/0.4.3#
```

Prefix: `cprmv:`

---

## Core classes

Cardinalities are those of the SHACL shapes.

### cprmv:RuleSet

A bundle of rules that is the output of a deliberation in a public service's delivery. Subclass of `frbr:Endeavor` — so a Work, Expression, Manifestation or Item —, `cv:Output` and `prov:Bundle`; not an `eli:LegalResource`. A RuleSet, being a `cv:Output`, is `cprmv:is_part_of` a `dcat:Dataset`.

| Property | Type | Cardinality | Notes |
|---|---|---|---|
| `cprmv:id` | `xsd:string` or `rdf:langString` | 1..* | Identifier |
| `cprmv:validFrom` | `xsd:date` | 1..1 | |
| `cprmv:validUntil` | `xsd:date` | 0..1 | |
| `cprmv:publishedOn` | `xsd:date` | 0..1 | |
| `cprmv:isOutputOf` | `cpsv:PublicService` | 1..* | Links to the service that produced this rule set |
| `cprmv:hasMethod` | `cprmv:RuleMethod` | 1..* | |
| `cprmv:hasPart` | RDF list of `cprmv:Rule` | 1..* items | Checked by `cprmv:hasPartShape` |
| `cprmv:isBasedOn` | `cprmv:RuleSet` | 0..* | Subproperty of `frbr:relatedEndeavour` and `prov:wasDerivedFrom` |
| `cprmv:comment` | `xsd:string` or `rdf:langString` | 0..* | |

!!! note "Source provenance"
    A RuleSet from `/rules` does not name its source with `prov:wasDerivedFrom`: the
    original publication is available from `/raw` with the same rule set id, and its
    source URL follows from the method's configuration. The API no longer hands the
    stylesheets a `puburl`. Two exceptions: a RuleSet read from JSON (IOU Norms, ROO)
    points at the publication URL with `cprmv:isBasedOn`, and the STTR stylesheet (DSO)
    still writes a `prov:wasDerivedFrom`, which, left without a URL, resolves to its
    base address `https://cprmv.open-regels.nl/0.4.3/methods/dso/`.

### cprmv:Analysis

Subclass of `cprmv:RuleSet`. A rule set produced by following an analysis method (e.g. Wetsanalyse/JAS).

### cprmv:DecisionModel

Subclass of `cprmv:RuleSet`. A rule set produced by following a formalisation method (e.g. DMN 1.3).

| Property | Type | Cardinality |
|---|---|---|
| `cprmv:hasAnalysis` | `cprmv:Analysis` | 0..* |

### cprmv:Rule

An individual rule within a rule set. Subclass of `prov:Entity`.

| Property | Type | Cardinality | Notes |
|---|---|---|---|
| `cprmv:id` | literal (lang-tagged in API output) | 1..* | Used for path navigation |
| `cprmv:definition` | literal | 0..1 | Natural language definition |
| `cprmv:postDefinition` | literal | 0..1 | |
| `cprmv:sourcequote` | `xsd:string` or `rdf:langString` | 0..* | |
| `cprmv:comment` | `xsd:string` or `rdf:langString` | 0..* | |
| `cprmv:isBasedOn` | `cprmv:Rule` | 0..* | |
| `cprmv:hasPart` | RDF list | 0..* | Sub-rules |

### cprmv:Parameter

Subclass of `cprmv:Rule`. A rule that represents a parameter value (e.g. income limit, threshold percentage).

### Other classes

`cprmv:Explanation`, `cprmv:Decision` and `cprmv:Case` are subclasses of `cprmv:Rule`; `cprmv:TestCase` is a subclass of `cprmv:Case`; `cprmv:TestSet` is a subclass of `cprmv:RuleSet`. The API does not produce them.

---

## RuleMethod hierarchy

| Class | Subclass of | Description |
|---|---|---|
| `cprmv:RuleMethod` | `cprmv:Method` | Base class of the rule methods |
| `cprmv:AnalysisMethod` | `cprmv:RuleMethod` | Methods for analysing legislation (e.g. JAS, FLINT) |
| `cprmv:FormalisationMethod` | `cprmv:RuleMethod` | Methods for formalising rules (e.g. DMN 1.3) |
| `cprmv:SerialisationMethod` | `cprmv:RuleMethod` | How a publication is serialised (e.g. BWB XML, Formex 4) |
| `cprmv:CodificationMethod` | `cprmv:RuleMethod` | Methods for codifying rules |
| `cprmv:ExecutionMethod` | `cprmv:RuleMethod` | Methods for executing rules |
| `cprmv:ExplanationMethod` | `cprmv:RuleMethod` | Methods for explaining rules |
| `cprmv:TestMethod` | `cprmv:RuleMethod` | Methods for testing rules |
| `cprmv:PublicationMethod` | `cprmv:RuleMethod` | Methods tied to a publication repository |
| `cprmv:ReferenceMethod` | `cprmv:PublicationMethod` | Methods for referencing rules |
| `cprmv:OrganisationRegister` | `cprmv:PublicationMethod` | Register of acknowledged organisations |
| `cprmv:ServiceRegister` | `cprmv:PublicationMethod` | Register of acknowledged services |

`cprmv:Method` is one of three **instruments**: `cprmv:Instrument` — something used in relation to rules — has the subclasses `cprmv:Standard`, `cprmv:Tool` and `cprmv:Method`.

The concrete methods are defined in `rdf/0.4.3/methods/<module>/method.ttl`, grouped into method modules (`cprmvmethods:module`, listing its methods with `cprmvmethods:hasMethods`), each method with a `cprmv:id` equal to its local name. The API loads only those that have a Python module (see [Architecture](architecture.md#method-plugins)).

---

## Echelons

`cprmv:Echelon` categorises rule sets in the context of service delivery. It has six subclasses: `cprmv:NaturalEchelon`, `cprmv:SemanticEchelon`, `cprmv:OntologicEchelon`, `cprmv:LogicEchelon`, `cprmv:OperableEchelon` and `cprmv:SupportEchelon`.

A rule method states which echelons it refines between with `cprmv:refinesFrom` and `cprmv:refinesTowards` (domain `cprmv:RuleMethod`, range `cprmv:Echelon`). The SHACL shapes for each method class limit which echelons are allowed — a `cprmv:TestMethod`, for example, refines from `cprmv:OperableEchelon` towards `cprmv:SupportEchelon`.

---

## Registers and catalogs

| Class | Subclass of | Notes |
|---|---|---|
| `cprmv:OrganisationCatalog` | `cprmv:RuleSet` | Its `cprmv:hasMethod` must be a `cprmv:OrganisationRegister` |
| `cprmv:AcknowledgedOrganisation` | `cprmv:Rule` | `cprmv:acknowledges` at least one `cv:PublicOrganisation` |
| `cprmv:ServiceCatalog` | `cprmv:RuleSet` | Its `cprmv:hasMethod` must be a `cprmv:ServiceRegister` |
| `cprmv:AcknowledgedService` | `cprmv:Rule` | `cprmv:acknowledges` at least one `cpsv:PublicService` |

---

## RDF list structure for hasPart

`cprmv:hasPart` uses standard RDF lists (`rdf:first` / `rdf:rest` / `rdf:nil`). The Python traversal in `get_rule` and `get_first_rule_by_Id_path_split_from_rule_as_root` walks these lists explicitly. The SHACL shape follows the same structure with a sequence path, `( cprmv:hasPart [ sh:zeroOrMorePath rdf:rest ] rdf:first )`, so every list item is checked to be a `cprmv:Rule` without a recursive list shape.

---

## Methods namespace

The methods registry uses four namespaces:

| Prefix | Namespace | Holds |
|---|---|---|
| `cprmvmethods:` | `https://cprmv.open-regels.nl/0.4.3/methods/` | Method definitions, modules and the value lists (`rulemethods`, `publicationmethods`, `referencemethods`, …) |
| `cprmv-serve:` | `https://cprmv.open-regels.nl/0.4.3/serve-api/` | API settings on method nodes, and the `core-*` base methods |
| `core-api:` | `https://cprmv.open-regels.nl/0.4.3/methods/core-api#` | Settings of API sources: `api-base-url`, `api-headers`, `http-method` |
| `frbr-sru:` | `https://cprmv.open-regels.nl/0.4.3/methods/frbr-sru/` | Settings of the FRBR SRU version lookup |

Key properties on method nodes:

| Property | Purpose |
|---|---|
| `cprmv-serve:publication-id-format` | Format of the official publication identifier |
| `cprmv-serve:normalized-id-format` | Normalised format used for parsing incoming ids |
| `cprmv-serve:repository-publication-location-format` | URL template for downloading the publication |
| `cprmv-serve:xslt` | File name of the XSLT in `serve_api/data/` |
| `cprmv-serve:utilizes` | The service or organisation register a method consults (DSO → DSO service register → ROO) |
| `cprmv-serve:reference-format` | Pattern a reference method parses references with |
| `cprmv-serve:reference-mapping` | List of key/label pairs for Juriconnect location strings, including `cprmv-serve:reference-mapping-valid-on` (`g`) and `cprmv-serve:reference-mapping-seen-on` (`z`) |
| `frbr-sru:url` | SRU search URL for resolving `latest` versions |
| `frbr-sru:response-from-date-term`, `frbr-sru:response-from-date-term-namespace` | Element in the SRU response holding the valid-from date |
| `frbr-sru:response-publication-location-term`, `frbr-sru:response-publication-location-term-namespace` | Element in the SRU response holding the publication location |

Settings defined on a parent method are copied onto the method that inherits them when the API loads it, so they are defined once per hierarchy.

---

## SHACL shapes

`rdf/0.4.3/cprmv.shacl.ttl` defines node shapes for `cprmv:RuleSet`, `cprmv:DecisionModel`, `cprmv:Rule`, `cprmv:RuleMethod`, the analysis, formalisation, codification, execution, explanation, test and publication method classes (each with its echelon constraints), `cprmv:ReferenceMethod`, the two catalogs, `cprmv:Echelon`, `cprmv:Explanation`, and the test, case and decision classes, plus the property shapes `cprmv:hasPartShape` and the two `cprmv:acknowledges` shapes. They enforce the cardinalities listed above.

`rdf/0.4.3/test.sh` validates the example data, every method definition and sample API output for BWB, CVDR, DMN 1.3 and Formex 4 against them with pyshacl; see [Testing](testing.md#shacl-validation).
