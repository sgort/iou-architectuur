# Namespace & Property Reference

**Editor version:** 1.9.x  
**CPSV-AP version:** 3.2.0

---

## Namespace prefix table

| Prefix | Namespace URI | Standard |
|---|---|---|
| `cpsv` | `http://purl.org/vocab/cpsv#` | CPSV-AP |
| `cv` | `http://data.europa.eu/m8g/` | Core Vocabulary |
| `dct` | `http://purl.org/dc/terms/` | Dublin Core Terms |
| `eli` | `http://data.europa.eu/eli/ontology#` | ELI |
| `ronl` | `https://regels.overheid.nl/ontology#` | RONL |
| `cprmv` | `https://cprmv.open-regels.nl/0.3.0/` | CPRMV |
| `skos` | `http://www.w3.org/2004/02/skos/core#` | SKOS |
| `schema` | `http://schema.org/` | Schema.org |
| `foaf` | `http://xmlns.com/foaf/0.1/` | FOAF |
| `org` | `http://www.w3.org/ns/org#` | W3C Org |
| `dcat` | `http://www.w3.org/ns/dcat#` | DCAT |
| `xsd` | `http://www.w3.org/2001/XMLSchema#` | XML Schema |

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
| `cv:thematicArea` | PublicService | URI | 0..* | |
| `cv:sector` | PublicService | URI | 1..* | Mandatory |
| `cv:spatial` | PublicOrganisation | URI | 1..* | Mandatory |
| `cv:hasCost` | PublicService | Cost | 0..* | |
| `cv:hasOutput` | PublicService | Output | 0..* | |

---

## Dublin Core Terms (`dct:`)

| Property | Domain | Range | Cardinality | Notes |
|---|---|---|---|---|
| `dct:identifier` | Any | Literal | 1..n | Mandatory for all entities (v1.4.0+) |
| `dct:title` | Any | Literal | 1..n | Language-tagged (`@nl`) |
| `dct:description` | Any | Literal | 0..n | Language-tagged (`@nl`) |
| `dct:language` | PublicService | URI | 0..n | LinguisticSystem URI format |
| `dct:type` | Output | URI | 0..1 | Classification |

---

## RONL (`ronl:`) — Governance

**Namespace URI:** `https://regels.overheid.nl/ontology#`

### Classes

| Class | Description |
|---|---|
| `ronl:TemporalRule` | Time-bounded business rule (dual-typed with `cpsv:Rule`) |
| `ronl:ParameterWaarde` | Parameter value (constant) |
| `ronl:VendorService` | Vendor implementation of a reference service |

### Properties

| Property | Domain | Range | Cardinality |
|---|---|---|---|
| `ronl:validFrom` | TemporalRule, ParameterWaarde | `xsd:date` | 0..1 |
| `ronl:validUntil` | TemporalRule, ParameterWaarde | `xsd:date` | 0..1 |
| `ronl:confidenceLevel` | TemporalRule | Literal | 0..1 |
| `ronl:extends` | TemporalRule | URI | 0..1 |
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

**Namespace URI:** `https://cprmv.open-regels.nl/0.3.0/`

### Classes

| Class | Description |
|---|---|
| `cprmv:Rule` | Normative rule from legislation |
| `cprmv:DecisionModel` | Deployed DMN decision model |
| `cprmv:DecisionRule` | Individual rule extracted from a DMN |

### Properties

| Property | Domain | Range | Cardinality |
|---|---|---|---|
| `cprmv:definition` | Rule | Literal | 1..1 |
| `cprmv:situatie` | Rule | Literal | 1..1 |
| `cprmv:norm` | Rule | Literal | 1..1 |
| `cprmv:ruleIdPath` | Rule | Literal | 1..1 |
| `cprmv:implements` | Rule | LegalResource | 0..1 |
| `cprmv:hasDecisionModel` | PublicService | DecisionModel | 0..1 |
| `cprmv:deploymentId` | DecisionModel | `xsd:string` | 0..1 |
| `cprmv:lastTested` | DecisionModel | `xsd:dateTime` | 0..1 |
| `cprmv:testStatus` | DecisionModel | `xsd:string` | 0..1 |
| `cprmv:extends` | DecisionRule | URI | 0..1 |
| `cprmv:ruleType` | DecisionRule | `xsd:string` | 0..1 |
| `cprmv:confidence` | DecisionRule | `xsd:string` | 0..1 |
| `cprmv:decisionTable` | DecisionRule | `xsd:string` | 0..1 |

---

## SKOS (`skos:`)

| Property | Domain | Range | Cardinality | Notes |
|---|---|---|---|---|
| `skos:prefLabel` | Organisation, ParameterWaarde | Literal | 1..1 | |
| `skos:notation` | ParameterWaarde | Literal | 0..1 | Machine-readable identifier |

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
| Rule typing | `a ronl:TemporalRule` | `a cpsv:Rule, ronl:TemporalRule` |
| Language format | Plain string | LinguisticSystem URI |
| Identifier output | Implicit | Explicit `dct:identifier` for all entities |

---

## Data types

| xsd type | Used for | Example |
|---|---|---|
| `xsd:date` | Validity dates, certification dates | `"2024-01-01"^^xsd:date` |
| `xsd:dateTime` | Test timestamps | `"2024-01-01T12:00:00Z"^^xsd:dateTime` |
| `xsd:string` | Status values, type codes | `"validated"^^xsd:string` |
| `xsd:decimal` | Parameter values | `"1234.56"^^xsd:decimal` |
| `xsd:nonNegativeInteger` | Counts | `"123"^^xsd:nonNegativeInteger` |
