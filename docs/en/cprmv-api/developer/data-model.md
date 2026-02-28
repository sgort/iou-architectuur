# Data Model

The CPRMV API produces and consumes data conforming to the CPRMV OWL vocabulary (`rdf/cprmv.ttl`) validated by the SHACL shapes in `rdf/cprmv.shacl.ttl`.

---

## Namespace

```
https://standaarden.open-regels.nl/standards/cprmv/0.4.0/#
```

Prefix: `cprmv:`

---

## Core classes

### cprmv:RuleSet

A set of rules that is the output of a public service. Subclass of `eli:LegalResource` and `cv:Output`.

| Property | Type | Cardinality | Notes |
|---|---|---|---|
| `cprmv:id` | literal | 1..1 | Unique identifier |
| `cprmv:validFrom` | `xsd:date` | 1..1 | |
| `cprmv:validUntil` | `xsd:date` | 0..1 | |
| `cprmv:publishedOn` | `xsd:date` | 0..1 | |
| `cprmv:isOutputOf` | `cpsv:PublicService` | 1..1 | Links to the service that produced this rule set |
| `cprmv:hasMethod` | `cprmv:RuleMethod` | 1..* | |
| `cprmv:hasPart` | RDF list of `cprmv:Rule`/`cprmv:RuleSet` | 1..1 | |
| `cprmv:isBasedOn` | `cprmv:RuleSet` or `cprmv:Rule` | 0..* | |
| `cprmv:comment` | `xsd:string` | 0..1 | |

### cprmv:Analysis

Subclass of `cprmv:RuleSet`. A rule set produced by following an analysis method (e.g. Wetsanalyse/JAS).

### cprmv:DecisionModel

Subclass of `cprmv:RuleSet`. A rule set produced by following a formalisation method (e.g. DMN 1.3).

| Property | Type | Cardinality |
|---|---|---|
| `cprmv:hasAnalysis` | `cprmv:Analysis` | 0..* |

### cprmv:Rule

An individual rule within a rule set.

| Property | Type | Cardinality | Notes |
|---|---|---|---|
| `cprmv:id` | literal (lang-tagged) | 1..1 | Used for path navigation |
| `cprmv:definition` | literal | 0..1 | Natural language definition |
| `cprmv:postDefinition` | literal | 0..1 | |
| `cprmv:sourceQuote` | `xsd:string` | 0..1 | |
| `cprmv:comment` | `xsd:string` | 0..1 | |
| `cprmv:isBasedOn` | `cprmv:Rule` | 0..* | |
| `cprmv:hasPart` | RDF list | 0..1 | Sub-rules |

### cprmv:Parameter

Subclass of `cprmv:Rule`. A rule that represents a parameter value (e.g. income limit, threshold percentage).

---

## RuleMethod hierarchy

| Class | Description |
|---|---|
| `cprmv:RuleMethod` | Base class |
| `cprmv:AnalysisMethod` | Methods for analysing legislation (e.g. Wetsanalyse) |
| `cprmv:FormalisationMethod` | Methods for formalising rules (e.g. DMN 1.3) |
| `cprmv:CodificationMethod` | Methods for codifying rules |
| `cprmv:ExecutionMethod` | Methods for executing rules |
| `cprmv:ExplanationMethod` | Methods for explaining rules |
| `cprmv:TestMethod` | Methods for testing rules |
| `cprmv:PublicationMethod` | Methods tied to a publication repository |
| `cprmv:ReferenceMethod` | Methods for referencing rules externally |

---

## RDF list structure for hasPart

`cprmv:hasPart` uses standard RDF lists (`rdf:first` / `rdf:rest` / `rdf:nil`). The Python traversal in `get_rule` and `get_first_rule_by_Id_path_split_from_rule_as_root` walks these lists explicitly. Each list item is a blank node `[ a cprmv:Rule; cprmv:id "..."; ... ]`.

---

## Methods namespace

```
https://cprmv.open-regels.nl/0.4.0/serve-api/
```

Prefix: `cprmv-serve:`

Key serve-API properties on method nodes:

| Property | Purpose |
|---|---|
| `cprmv-serve:publication-id-format` | Format template for the publication identifier |
| `cprmv-serve:normalized-id-format` | Normalised format used for parsing incoming IDs |
| `cprmv-serve:repository-publication-location-format` | URL template for downloading the publication XML |
| `cprmv-serve:frbr-repository-sru-url` | SRU URL for resolving `latest` versions |
| `cprmv-serve:xslt` | Relative path to the XSLT file |

---

## SHACL shapes

`rdf/cprmv.shacl.ttl` defines shapes for `cprmv:RuleSet`, `cprmv:DecisionModel`, `cprmv:Rule`, and `cprmv:RuleMethod`. The shapes enforce mandatory properties and cardinality constraints as listed in the tables above. They can be used to validate TTL files produced by the CLI tool (`tools/bwb2cprmv/`) or the API's own output before ingestion into TriplyDB.
