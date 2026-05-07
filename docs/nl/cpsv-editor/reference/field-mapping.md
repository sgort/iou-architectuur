# Field Mapping: CPSV-AP 3.2.0

This page maps each UI field in the editor to its corresponding RDF property and
CPSV-AP 3.2.0 compliance status.

**Legend:** ✅ Implemented and compliant · 🎯 Phase 1 (v1.4.0) · ⭐ New in
v1.5.0/v1.9.0 · 📋 Phase 2 planned · ℹ️ RONL/CPRMV extension

---

## Service tab — `cpsv:PublicService`

| UI field           | State property         | TTL property                        | CPSV-AP 3.2.0     | Status       |
| ------------------ | ---------------------- | ----------------------------------- | ----------------- | ------------ |
| Unique identifier  | `service.identifier`   | `dct:identifier`                    | `dct:identifier`  | ⭐ Mandatory  |
| Official name      | `service.name`         | `dct:title`                         | `dct:title`       | ✅            |
| Description        | `service.description`  | `dct:description`                   | `dct:description` | ✅            |
| Thematic area      | `service.thematicArea` | `cv:thematicArea`                   | `cv:thematicArea` | ✅            |
| Government level   | `service.sector`       | `cv:sector`                         | `cv:sector`       | 🎯 Mandatory  |
| Keywords           | `service.keywords`     | `dcat:keyword`                      | `dct:subject`     | ✅            |
| Language           | `service.language`     | `dct:language`                      | `dct:language`    | 🎯 URI format |
| Cost amount        | `cost.amount`          | `cv:hasCost / schema:price`         | `cv:hasCost`      | 🎯            |
| Cost currency      | `cost.currency`        | `cv:hasCost / schema:priceCurrency` | `cv:hasCost`      | 🎯            |
| Output title       | `output.title`         | `cv:hasOutput / dct:title`          | `cv:hasOutput`    | 🎯            |
| Output description | `output.description`   | `cv:hasOutput / dct:description`    | `cv:hasOutput`    | 🎯            |

---

## Organisation tab — `cv:PublicOrganisation`

| UI field                | State property            | TTL property                | CPSV-AP 3.2.0    | Status      |
| ----------------------- | ------------------------- | --------------------------- | ---------------- | ----------- |
| Organisation identifier | `organization.identifier` | `dct:identifier`            | `dct:identifier` | ⭐           |
| Organisation name       | `organization.name`       | `skos:prefLabel`            | `skos:prefLabel` | ✅           |
| Geographic jurisdiction | `organization.spatial`    | `cv:spatial`                | `cv:spatial`     | 🎯 Mandatory |
| Homepage                | `organization.homepage`   | `foaf:homepage`             | `foaf:homepage`  | ✅           |
| Logo                    | `organization.logo`       | `foaf:logo`, `schema:image` | —                | ℹ️          |

---

## Legal tab — `eli:LegalResource`

| UI field    | State property              | TTL property      | CPSV-AP 3.2.0         | Status |
| ----------- | --------------------------- | ----------------- | --------------------- | ------ |
| BWB ID      | `legalResource.bwbId`       | URI construction  | `cv:hasLegalResource` | ✅      |
| Version     | `legalResource.version`     | `eli:version`     | `eli:version`         | ✅      |
| Title       | `legalResource.title`       | `dct:title`       | `dct:title`           | ✅      |
| Description | `legalResource.description` | `dct:description` | `dct:description`     | ✅      |

---

## Rules tab — `cpsv:Rule, ronl:TemporalRule`

| UI field         | State property         | TTL property           | CPSV-AP 3.2.0    | Status      |
| ---------------- | ---------------------- | ---------------------- | ---------------- | ----------- |
| Rule identifier  | `rule.identifier`      | `dct:identifier`       | `dct:identifier` | 🎯 Mandatory |
| Rule title       | `rule.title`           | `dct:title`            | `dct:title`      | 🎯 Mandatory |
| Rule URI         | `rule.uri`             | Subject URI            | —                | ℹ️          |
| Extends          | `rule.extends`         | `ronl:extends`         | —                | ℹ️          |
| Valid from       | `rule.validFrom`       | `ronl:validFrom`       | —                | ℹ️          |
| Valid until      | `rule.validUntil`      | `ronl:validUntil`      | —                | ℹ️          |
| Confidence level | `rule.confidenceLevel` | `ronl:confidenceLevel` | —                | ℹ️          |

---

## Parameters tab — `ronl:ParameterWaarde`

| UI field    | State property         | TTL property      | Notes               |
| ----------- | ---------------------- | ----------------- | ------------------- |
| Notation    | `parameter.notation`   | `skos:notation`   | Machine-readable ID |
| Label       | `parameter.label`      | `skos:prefLabel`  | Human-readable name |
| Value       | `parameter.value`      | `schema:value`    |                     |
| Unit        | `parameter.unit`       | `schema:unitCode` |                     |
| Valid from  | `parameter.validFrom`  | `ronl:validFrom`  |                     |
| Valid until | `parameter.validUntil` | `ronl:validUntil` |                     |

---

## CPRMV tab — `cprmv:Rule`

| UI field     | State property         | TTL property       | Status               |
| ------------ | ---------------------- | ------------------ | -------------------- |
| Identifier   | `cprmvRule.identifier` | `dct:identifier`   | ✅ Mandatory          |
| Title        | `cprmvRule.title`      | `dct:title`        | ✅ Mandatory          |
| Definition   | `cprmvRule.definition` | `cprmv:definition` | ✅ Mandatory          |
| Situation    | `cprmvRule.situation`  | `cprmv:situatie`   | ✅ Mandatory          |
| Norm         | `cprmvRule.norm`       | `cprmv:norm`       | ✅ Mandatory          |
| Rule ID path | `cprmvRule.ruleIdPath` | `cprmv:ruleIdPath` | ✅ Mandatory          |
| Implements   | auto-linked            | `cprmv:implements` | ⭐ v1.9.0 auto-linked |

---

## DMN tab — `cprmv:DecisionModel`

| UI field        | State property         | TTL property                  | Notes                 |
| --------------- | ---------------------- | ----------------------------- | --------------------- |
| DMN filename    | `dmnData.fileName`     | `dct:source`                  |                       |
| Decision key    | `dmnData.decisionKey`  | `dct:identifier`              |                       |
| Deployment ID   | `dmnData.deploymentId` | `cprmv:deploymentId`          |                       |
| Deployed at     | `dmnData.deployedAt`   | `dct:issued`                  |                       |
| API endpoint    | `dmnData.apiEndpoint`  | `schema:url`                  |                       |
| Input variables | extracted              | `cpsv:Input` entities         | One per `<inputData>` |
| Decision rules  | extracted              | `cprmv:DecisionRule` entities | One per `<decision>`  |

---

## Future phases

**Phase 2 (planned):**

- `cv:Channel` — service delivery channel
- `cv:ContactPoint` — contact information
- `cv:Criterion` — eligibility criteria

**Phase 3 (planned):**

- `cv:Requirement` — prerequisite requirements
- `cv:Evidence` — supporting evidence
- `cv:Event` — life events triggering the service
- `cpov:Participation` — participation information
