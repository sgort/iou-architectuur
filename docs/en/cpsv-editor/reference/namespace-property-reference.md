# Namespace & Property Reference

**Editor version:** 1.10.x  
**CPSV-AP version:** 3.2.0  
**CPRMV version:** 0.4.1

---

## Namespace prefix table

These prefixes are emitted verbatim in every exported file (see `TTL_NAMESPACES`
in `src/utils/constants.js`).

| Prefix | Namespace URI | Standard |
|---|---|---|
| `cpsv` | `http://purl.org/vocab/cpsv#` | CPSV-AP |
| `cv` | `http://data.europa.eu/m8g/` | Core Vocabulary |
| `dct` | `http://purl.org/dc/terms/` | Dublin Core Terms |
| `dcat` | `http://www.w3.org/ns/dcat#` | DCAT |
| `eli` | `http://data.europa.eu/eli/ontology#` | ELI |
| `foaf` | `http://xmlns.com/foaf/0.1/` | FOAF |
| `org` | `http://www.w3.org/ns/org#` | W3C Org |
| `ronl` | `https://regels.overheid.nl/ontology#` | RONL |
| `skos` | `http://www.w3.org/2004/02/skos/core#` | SKOS |
| `schema` | `http://schema.org/` | Schema.org |
| `xsd` | `http://www.w3.org/2001/XMLSchema#` | XML Schema |
| `prov` | `http://www.w3.org/ns/prov#` | PROV-O |
| `cprmv` | `https://standaarden.open-regels.nl/standards/cprmv/0.4.1#` | CPRMV |

!!! note "CPRMV namespace bump (v1.10.0)"
    The canonical CPRMV namespace changed from `https://cprmv.open-regels.nl/0.3.0/`
    to `https://standaarden.open-regels.nl/standards/cprmv/0.4.1#`. The importer still
    accepts the old namespace and the parser normalises it; only the 0.4.1 namespace
    is written on export.

!!! note "Selectable export namespace (v1.10.5)"
    A **CPRMV version selector** lets the editor emit the `0.3.2` versioned-path
    namespace `https://cprmv.open-regels.nl/0.3.2/` instead of the default `0.4.1`
    namespace above. This is the namespace the Linked Data Explorer
    `/v1/norms?cprmv_version=0.3.2` query reads. The two targets also differ in
    shape — see the [conformance changes (v1.10.5)](#cprmv-version-selector-changes-v1105)
    below.

---

## CPSV-AP (`cpsv:`)

### Classes

| Class | Description |
|---|---|
| `cpsv:PublicService` | A public-sector service |
| `cpsv:Rule` | Base class for all rules |
| `cpsv:Input` | Input variable to a decision model |

### Properties

| Property | Domain | Range | Cardinality | Notes |
|---|---|---|---|---|
| `cpsv:implements` | DecisionModel | PublicService | 0..1 | DMN implements service |
| `cpsv:isRequiredBy` | Input | DecisionModel | 1..1 | Links input to model |

---

## Core Vocabulary (`cv:`)

### Classes

| Class | Description |
|---|---|
| `cv:PublicOrganisation` | ✅ v1.4.0+ — replaces `org:Organization` |
| `cv:Cost` | Service cost |
| `cv:Output` | Service output |

### Properties

| Property | Domain | Range | Cardinality | Notes |
|---|---|---|---|---|
| `cv:hasCompetentAuthority` | PublicService | PublicOrganisation | 1..* | Mandatory |
| `cv:hasLegalResource` | PublicService | LegalResource | 0..* | ✅ v1.4.0+ — replaces `cpsv:follows` |
| `cv:thematicArea` | PublicService | URI | 0..* | Referenced node typed `skos:Concept` in-graph |
| `cv:sector` | PublicService | URI | 1..* | Mandatory; referenced node typed `skos:Concept` in-graph |
| `cv:hasCost` | PublicService | Cost | 0..* | |
| `cv:hasOutput` | PublicService | Output | 0..* | |

---

## Dublin Core Terms (`dct:`)

| Property | Domain | Range | Cardinality | Notes |
|---|---|---|---|---|
| `dct:identifier` | Any | Literal | 1..n | Mandatory for all entities (v1.4.0+) |
| `dct:title` | Any | Literal | 1..n | Language-tagged (`@nl`) |
| `dct:description` | Any | Literal | 0..n | Language-tagged (`@nl`) |
| `dct:language` | PublicService | URI | 0..n | LinguisticSystem URI; the referenced node is typed `dct:LinguisticSystem` in-graph |
| `dct:spatial` | PublicOrganisation | URI | 1..* | ✅ v1.10.0 — **Mandatory** (replaces `cv:spatial`); the referenced node is typed `dct:Location` in-graph to satisfy `PublicOrganisationShape` without entailment |
| `dct:type` | Output | URI | 0..1 | Classification |

!!! note "`cv:spatial` → `dct:spatial` (v1.10.0)"
    For CPSV-AP 3.2.0 SHACL conformance the organisation's geographic jurisdiction is
    now emitted as `dct:spatial` pointing at a `dct:Location`-typed node. The importer
    reads **both** `dct:spatial` (current output) and `cv:spatial` (legacy files), so
    older files round-trip cleanly.

---

## RONL (`ronl:`) — Governance

**Namespace URI:** `https://regels.overheid.nl/ontology#`

### Classes

| Class | Description |
|---|---|
| `ronl:VendorService` | Vendor implementation of a reference service |

!!! warning "Rule & parameter classes moved to `cprmv:` (v2.0.0 vocabulary)"
    Temporal rules and parameter values are no longer typed in the `ronl:` namespace.
    The generator now emits `a cpsv:Rule, cprmv:TemporalRule` and `a cprmv:ParameterWaarde`,
    with their temporal/confidence properties under `cprmv:` (see the CPRMV section below).
    The `ronl:` namespace is now reserved for governance (validation, certification, vendor).
    The parser still accepts the legacy `ronl:TemporalRule` / `ronl:ParameterWaarde` types and
    `ronl:validFrom`/`ronl:validUntil`/`ronl:confidenceLevel`/`ronl:extends` properties on import.

### Properties

| Property | Domain | Range | Cardinality |
|---|---|---|---|
| `ronl:validatedBy` | DecisionModel, Service | URI | 0..1 |
| `ronl:validationStatus` | DecisionModel, Service | Literal | 0..1 |
| `ronl:validatedAt` | DecisionModel, Service | `xsd:date` | 0..1 |
| `ronl:validationNote` | DecisionModel, Service | Literal | 0..1 |
| `ronl:certifiedBy` | Service | URI | 0..1 |
| `ronl:certificationStatus` | Service | Literal | 0..1 |
| `ronl:certifiedAt` | Service | `xsd:date` | 0..1 |
| `ronl:certificationNote` | Service | Literal | 0..1 |
| `ronl:basedOn` | Service | URI | 0..1 |
| `ronl:vendorType` | Organisation | Literal | 0..1 |

---

## CPRMV (`cprmv:`) — Rule Management

**Namespace URI:** `https://standaarden.open-regels.nl/standards/cprmv/0.4.1#`

### Classes

| Class | Description |
|---|---|
| `cprmv:Rule` | Normative rule from legislation |
| `cprmv:RuleSet` | ✅ v1.10.0 — a set of `cprmv:Rule`s derived from one legal source (replaces the v1.9.4 `cprmv:Dataset`) |
| `cprmv:RuleMethod` | ✅ v1.10.0 — the codification method for a RuleSet (dual-typed with `cprmv:CodificationMethod`) |
| `cprmv:CodificationMethod` | ✅ v1.10.0 — co-type of the RuleMethod node |
| `cprmv:TemporalRule` | ✅ v2.0.0 — time-bounded business rule (dual-typed with `cpsv:Rule`); replaces `ronl:TemporalRule` |
| `cprmv:ParameterWaarde` | ✅ v2.0.0 — parameter value (constant); replaces `ronl:ParameterWaarde` |
| `cprmv:DecisionModel` | Deployed DMN decision model |
| `cprmv:DecisionRule` | Individual rule extracted from a DMN (dual-typed with `cpsv:Rule`) |

### Properties

| Property | Domain | Range | Cardinality | Notes |
|---|---|---|---|---|
| `cprmv:definition` | Rule | Literal | 1..1 | `@nl` |
| `cprmv:situatie` | Rule | Literal | 1..1 | `@nl` |
| `cprmv:norm` | Rule | Literal | 1..1 | |
| `cprmv:ruleIdPath` | Rule | Literal | 1..1 | |
| `cprmv:id` | Rule, RuleSet, RuleMethod | Literal | 1..1 | ✅ v1.10.0 — required by RuleShape/RuleSetShape |
| `cprmv:rulesetId` | Rule, RuleSet | Literal | 0..1 | |
| `cprmv:implements` | Rule | LegalResource | 0..1 | Uses the rule's own `rulesetId` |
| `cprmv:validFrom` | RuleSet, TemporalRule, ParameterWaarde | `xsd:date` | 0..1 | ✅ v2.0.0 (replaces `ronl:validFrom`) |
| `cprmv:validUntil` | TemporalRule, ParameterWaarde | `xsd:date` | 0..1 | ✅ v2.0.0 (replaces `ronl:validUntil`) |
| `cprmv:confidenceLevel` | TemporalRule | Literal | 0..1 | ✅ v2.0.0 (replaces `ronl:confidenceLevel`) |
| `cprmv:isBasedOn` | TemporalRule, DecisionRule | URI | 0..1 | ✅ v1.10.0 — renamed from `cprmv:extends` |
| `cprmv:isOutputOf` | RuleSet | PublicService | 0..1 | ✅ v1.10.0 |
| `cprmv:hasMethod` | RuleSet | RuleMethod | 0..1 | ✅ v1.10.0 |
| `cprmv:hasPart` | RuleSet | RDF list of Rule | 0..1 | ✅ v1.10.0 — ordered list |
| `cprmv:hasAnalysis` | LegalResource | URI | 0..1 | Analysis method concept (replaces `ronl:hasAnalysis`) |
| `cprmv:hasMethod` (Legal) | LegalResource | URI | 0..1 | Rule-management method concept (replaces `ronl:hasMethod`) |
| `cprmv:hasDecisionModel` | PublicService | DecisionModel | 0..1 | |
| `cprmv:deploymentId` | DecisionModel | `xsd:string` | 0..1 | |
| `cprmv:deployedAt` | DecisionModel | `xsd:dateTime` | 0..1 | |
| `cprmv:implementedBy` | DecisionModel | URI | 0..1 | API endpoint executing the model |
| `cprmv:lastTested` | DecisionModel | `xsd:dateTime` | 0..1 | |
| `cprmv:testStatus` | DecisionModel | `xsd:string` | 0..1 | |
| `cprmv:ruleType` | DecisionRule | `xsd:string` | 0..1 | |
| `cprmv:confidence` | DecisionRule | `xsd:string` | 0..1 | |
| `cprmv:decisionTable` | DecisionRule | `xsd:string` | 0..1 | |
| `cprmv:rulesetType` | DecisionRule | `xsd:string` | 0..1 | |
| `cprmv:note` | DecisionRule | Literal | 0..1 | `@nl` |

`cprmv:RuleSet` nodes also carry a `prov:wasDerivedFrom` link to their legal source.

---

## SKOS (`skos:`)

| Property | Domain | Range | Cardinality | Notes |
|---|---|---|---|---|
| `skos:prefLabel` | Organisation, ParameterWaarde | Literal | 1..1 | ParameterWaarde: required by `cprmv:ParameterWaardeShape` (v1.10.4) |
| `skos:notation` | ParameterWaarde | Literal | 1..1 | Machine-readable identifier; required by `cprmv:ParameterWaardeShape` (v1.10.4) |

---

## Schema.org (`schema:`)

| Property | Domain | Range | Cardinality |
|---|---|---|---|
| `schema:value` | ParameterWaarde | Literal | 0..1 |
| `schema:unitCode` | ParameterWaarde | Literal | 0..1 |
| `schema:image` | Organisation, VendorService | URI | 0..1 |
| `schema:url` | VendorService | URI | 0..1 |
| `schema:license` | VendorService | Literal | 0..1 |
| `schema:provider` | VendorService | BlankNode | 0..1 |
| `schema:contactPoint` | Organisation/Provider | BlankNode | 0..1 |

---

## CPSV-AP 3.2.0 compliance changes (v1.4.0)

| Change | Before | After |
|---|---|---|
| Organisation class | `org:Organization` | `cv:PublicOrganisation` |
| Legal resource link | `cpsv:follows` | `cv:hasLegalResource` |
| Rule typing | `a ronl:TemporalRule` | `a cpsv:Rule, cprmv:TemporalRule` |
| Language format | Plain string | LinguisticSystem URI |
| Identifier output | Implicit | Explicit `dct:identifier` for all entities |

---

## CPSV-AP 3.2.0 / CPRMV 0.4.1 conformance changes (v1.10.0)

| Change | Before | After |
|---|---|---|
| CPRMV namespace | `…/cprmv/0.3.0/` | `…/standards/cprmv/0.4.1#` |
| Organisation jurisdiction | `cv:spatial` | `dct:spatial` → `dct:Location`-typed node |
| Rule grouping | `cprmv:Dataset` (+ `dcat:Dataset`) | `cprmv:RuleSet` (+ `cprmv:RuleMethod`) |
| Rule extension predicate | `cprmv:extends` | `cprmv:isBasedOn` |
| DMN/temporal rule typing | `a cpsv:Rule` only | `a cpsv:Rule, cprmv:DecisionRule` / `cprmv:TemporalRule` with required `dct:title`/`dct:description` |
| `cpsv:implements` target | the `cpsv:PublicService` | the `eli:LegalResource` (or omitted when none) |
| Controlled-vocab references | untyped | `dct:LinguisticSystem` / `skos:Concept` typed in-graph |

All editor-generated TTL validates clean (0 violations) against both the CPSV-AP
3.2.0 and CPRMV 0.4.1 SHACL shapes.

---

## Parameter validation (v1.10.4)

The `cprmv:ParameterWaardeShape` (added in Linked Data Explorer v1.9.8) makes both
`skos:notation` and `skos:prefLabel` mandatory `[1,n]` on every `cprmv:ParameterWaarde`.
The editor's client-side `validateParameter` mirrors this: both fields are required
regardless of whether a `schema:value` is set, and a missing one is surfaced in the
Parameters-tab form and the pre-publish validation panel rather than only at back-end
publish time.

---

## CPRMV version selector changes (v1.10.5)

The editor can emit either of two CPRMV targets, selected in the toolbar. They differ
in namespace **and** in shape:

| | `0.4.1` (default) | `0.3.2` |
|---|---|---|
| `cprmv:` namespace | `…/standards/cprmv/0.4.1#` | `https://cprmv.open-regels.nl/0.3.2/` |
| Ruleset grouping | `cprmv:RuleSet` (+ `cprmv:hasPart`) | `cprmv:Dataset` per ruleset |
| Dataset node typing | — | `cprmv:Dataset` **only** (not co-typed `dcat:Dataset`, so the CPSV-AP `DatasetShape` is not triggered) |
| Flat `cprmv:Rule` resources | emitted | emitted |
| LDE query | `dataset_versions` via `cprmv:RuleSet` | `/v1/norms?cprmv_version=0.3.2` |

Independent of the selected version:

| Behaviour | Effect |
|---|---|
| Rules-derived consolidation date | `eli:is_realized_by` and each ruleset's `cprmv:validFrom`/versioned `cprmv:id` come from the BWB in-force date in the rules' `ruleIdPath`; the manual date field is a fallback only |
| Unique rule subject URIs | Rules sharing a legal path get an `_N` suffix (`_2`, `_3`, …) instead of collapsing onto one subject; duplicates share a `rule_id_path_key` dedup key |
| Nested sub-clause folding | Import folds `rule_id_path`-less nested members into the parent `cprmv:definition` rather than creating norm-less rules |

---

## Data types

| xsd type | Used for | Example |
|---|---|---|
| `xsd:date` | Validity dates, certification dates | `"2024-01-01"^^xsd:date` |
| `xsd:dateTime` | Test timestamps | `"2024-01-01T12:00:00Z"^^xsd:dateTime` |
| `xsd:string` | Status values, type codes | `"validated"^^xsd:string` |
| `xsd:decimal` | Parameter values | `"1234.56"^^xsd:decimal` |
| `xsd:nonNegativeInteger` | Counts | `"123"^^xsd:nonNegativeInteger` |
