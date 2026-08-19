---
component: CPSV Editor
---

# External Standards & Links

---

## Standards implemented

| Standard | Version | Specification |
|---|---|---|
| CPSV-AP | 3.2.0 | <https://semiceu.github.io/CPSV-AP/> |
| CPRMV | 0.4.1 | <https://standaarden.open-regels.nl/standards/cprmv/0.4.1/> |
| RONL Vocabulary | — | <https://regels.overheid.nl/termen/> |
| ELI | — | <http://data.europa.eu/eli/ontology> |
| Dublin Core Terms | — | <https://www.dublincore.org/specifications/dublin-core/dcmi-terms/> |
| SKOS | — | <https://www.w3.org/2004/02/skos/> |
| Schema.org | — | <https://schema.org/> |
| FOAF | — | <http://xmlns.com/foaf/0.1/> |
| W3C ORG | — | <https://www.w3.org/TR/vocab-org/> |
| W3C Turtle | — | <https://www.w3.org/TR/turtle/> |
| DMN | 1.3 | <https://www.omg.org/spec/DMN/1.3/> |

### CPRMV — in flight

Two CPRMV developments affect what the editor emits, neither of them shipped
in the 0.4.1 target it currently writes:

**Cell-level legislative linking.** A proposal to link legislation at
decision-table cell granularity, finer than DMN's decision-level
`knowledgeSource` or CPRMV's rule-level `extends`/`ruleType`/`confidence`. It
was prototyped against a real rule and cross-referenced against annotation
data, and the editor implements it today using only existing CPRMV terms
(`cprmv:hasPart`, `cprmv:isBasedOn`, `cprmv:sourceQuote`, `cprmv:id`) — no new
classes or shapes. See [Cell-Level Legislative Grounding](../developer/cell-level-grounding.md).

**`ReferenceMethod` (CPRMV 0.4.2).** JuriConnect is *not* being mandated as
the citation grammar. 0.4.2 introduces `ReferenceMethod` as a pluggable
concept, with JCI and ELI as known methods alongside an internal rule-id-path
method for citing minted `cprmv:Rule`s. The editor's current emission predates
this and resolves JCI references directly; aligning with `ReferenceMethod` is
a future change.

Note also that `cprmv:implements` does not exist — the correct relation is
`cpsv:implements`.

---

## Dutch government resources

| Resource | URL |
|---|---|
| Dutch legislation (BWB) | <https://wetten.overheid.nl> |
| Government organisations | <https://organisaties.overheid.nl> |
| RONL Initiative | <https://regels.overheid.nl> |
| CPRMV documentation | <https://standaarden.open-regels.nl/standards/cprmv/0.4.1/> |

---

## Infrastructure

| Service | URL |
|---|---|
| Operaton rule engine | <https://operaton.open-regels.nl> |
| Operaton documentation | <https://docs.operaton.org> |
| TriplyDB instance | <https://open-regels.triply.cc> |

---

## Application environments

| Environment | URL |
|---|---|
| CPSV Editor (production) | <https://cpsv-editor.open-regels.nl> |
| CPSV Editor (acceptance) | <https://acc.cpsv-editor.open-regels.nl> |
| Linked Data Explorer (production) | <https://linkeddata.open-regels.nl> |
| Linked Data Explorer (acceptance) | <https://acc.linkeddata.open-regels.nl> |

---

## License

This project is licensed under the **EUPL v1.2** (European Union Public License, version 1.2 or later).