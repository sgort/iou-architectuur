# cprmv:Dataset Generation

---

## Architecture

```
User edits CPRMV rules in CPRMVTab
        ↓
On TTL export or publish, TTLGenerator.generate() in ttlGenerator.js:
    ...
    Service section                     (cpsv:PublicService)
    Organization section                (cv:PublicOrganisation)
    Legal Resource section              (eli:LegalResource)
    CPRMV Dataset section                ← one Dataset per unique rulesetId
    CPRMV Rules section                  ← per-rule cprmv:implements URI
    ...
        ↓
generateDatasetsSection():
    rulesetIds = unique values of cprmv:rulesetId across all rules
    For each rulesetId:
        isPrimary = (rulesetId matches legalResource.bwbId)
        legalUri  = buildLegalUriForRulesetId(rulesetId, isPrimary ? version : '')
        Emit Dataset block (DCAT-aligned)
        ↓
generateCprmvRulesSection():
    For each rule:
        isPrimary  = (rule.rulesetId matches legalResource.bwbId)
        legalUri   = buildLegalUriForRulesetId(rule.rulesetId, isPrimary ? version : '')
        Emit Rule block, including:
            cprmv:rulesetId  "{rule.rulesetId}"
            cprmv:implements <{legalUri}>
```

---

## Files

```
src/
├── utils/
│   ├── ttlGenerator.js         # generateDatasetsSection, generateCprmvRulesSection,
│   │                             buildLegalUriForRulesetId, buildLegalResourceUri
│   ├── constants.js            # TTL_NAMESPACES (cprmv, dcat, dct, xsd prefixes)
│   └── index.js                # encodeURIComponentTTL, escapeTTLString utilities
└── config/
    └── vocabularies.config.js  # entityTypes.cprmvDataset (acceptedTypes, canonicalType)
```

---

## API functions

### `generateDatasetsSection()`

Generates the `cprmv:Dataset` section of the TTL document. One Dataset is emitted per unique `cprmv:rulesetId` found in the CPRMV Rules collection.

```javascript
// inside TTLGenerator.generate():
if (this.hasCprmvRules()) {
  ttl += this.generateSectionHeader('CPRMV Dataset');
  ttl += this.generateDatasetsSection();
}
```

**Behaviour:**

- Returns `''` when there are no CPRMV rules
- Emits one Dataset per distinct rulesetId
- `dcat:version`, versioned `cprmv:implements`, versioned `dcat:landingPage` and `dct:title` are applied only to the Dataset matching the service's primary `legalResource.bwbId`; other rulesets get un-versioned URIs and no title (see "Version confidence")

### `buildLegalUriForRulesetId(rulesetId, version)`

Builds a canonical legal-resource URI from a BWB/CVDR identifier or full URI. Used by both the Rule and Dataset emitters so they produce symmetric URIs.

```javascript
buildLegalUriForRulesetId('BWBR0015703', '2026-01-01');
// → 'https://wetten.overheid.nl/BWBR0015703/2026-01-01'

buildLegalUriForRulesetId('BWBR0044894', '');
// → 'https://wetten.overheid.nl/BWBR0044894'

buildLegalUriForRulesetId('CVDR123456', '');
// → 'https://lokaleregelgeving.overheid.nl/CVDR123456/1'

buildLegalUriForRulesetId('https://wetten.overheid.nl/BWBR0015703/2026-01-01/0', '2026-01-01');
// → 'https://wetten.overheid.nl/BWBR0015703/2026-01-01'
//   (trailing /YYYY-MM-DD[/N] is stripped before version is re-appended,
//    preventing doubled-version URIs from already-versioned input)
```

**Parameters:**

- `rulesetId` — bare ID (`BWBR…` / `CVDR…`) or full URI
- `version` — date string (`YYYY-MM-DD`); appended to the base URI when truthy

### `buildLegalResourceUri()`

Thin wrapper that delegates to `buildLegalUriForRulesetId` using the service's primary legal resource (`this.legalResource.bwbId` and `this.legalResource.version`). Used as the defensive fallback path when a Rule lacks a `rulesetId`.

---

## Schema design

Each Dataset is dual-typed `cprmv:Dataset` and `dcat:Dataset`, with DCAT-aligned properties for catalogue interoperability.

### Primary Dataset (matches the service's `legalResource.bwbId`)

```turtle
<https://cprmv.open-regels.nl/datasets/BWBR0015703_2026-01-01> a cprmv:Dataset, dcat:Dataset ;
    dct:identifier "BWBR0015703_2026-01-01" ;
    dct:title "Participatiewet"@nl ;
    cprmv:rulesetId "BWBR0015703" ;
    cprmv:implements <https://wetten.overheid.nl/BWBR0015703/2026-01-01> ;
    dcat:version "2026-01-01" ;
    dct:issued "2026-05-15T06:57:11Z"^^xsd:dateTime ;
    dcat:landingPage <https://wetten.overheid.nl/BWBR0015703/2026-01-01> .
```

### Non-primary Dataset (any other rulesetId referenced by rules in this service)

```turtle
<https://cprmv.open-regels.nl/datasets/BWBR0044894_2026-01-01> a cprmv:Dataset, dcat:Dataset ;
    dct:identifier "BWBR0044894_2026-01-01" ;
    cprmv:rulesetId "BWBR0044894" ;
    cprmv:implements <https://wetten.overheid.nl/BWBR0044894> ;
    dct:issued "2026-05-15T06:57:11Z"^^xsd:dateTime ;
    dcat:landingPage <https://wetten.overheid.nl/BWBR0044894> .
```

The Dataset URI suffix carries the version (`BWBR0044894_2026-01-01`), inherited from the service's `legalResource.version`. This makes Dataset URIs sortable by publication batch even when the individual BWB's version is unknown to the editor.

---

## CPRMV Rule companion

Rules emit `cprmv:implements` using their own `rulesetId`, not the service's primary legal resource. This is what makes the Rule ↔ Dataset URI symmetry possible.

```turtle
<https://cprmv.open-regels.nl/rules/BWBR0044894_2026-01-01_0_Artikel-7a_onderdeel-c> a cprmv:Rule ;
    cprmv:id "onderdeel c." ;
    cprmv:rulesetId "BWBR0044894" ;
    cprmv:definition "19-jarigen: € 231,09;"@nl ;
    cprmv:situatie "19-jarigen"@nl ;
    cprmv:norm "231,09" ;
    cprmv:ruleIdPath "BWBR0044894_2026-01-01_0, Artikel 7a., onderdeel c." ;
    cprmv:implements <https://wetten.overheid.nl/BWBR0044894> .
```

A rule from Article 7a of BWBR0044894 implements BWBR0044894 — not the service's primary law (here, BWBR0015703). When a rule has no `rulesetId` (defensive fallback path), the emitter calls `buildLegalResourceUri()` and emits the service's primary URI. In practice the editor enforces `rulesetId` as a mandatory field, so this path is not normally taken.

---

## Join semantics

Datasets connect to Rules through two predicates — both work, and both return identical record sets in both single-BWB and multi-BWB services. They are interchangeable; use whichever fits the query style.

### Loose join — by `cprmv:rulesetId`

Rule-level granularity. Joins on the literal `cprmv:rulesetId` shared between a Rule and its Dataset.

```sparql
PREFIX cprmv: <https://cprmv.open-regels.nl/0.3.0/>

SELECT ?rule ?dataset WHERE {
  ?rule a cprmv:Rule ; cprmv:rulesetId ?id .
  ?dataset a cprmv:Dataset ; cprmv:rulesetId ?id .
}
```

### Tight join — by `cprmv:implements`

URI-level granularity. Joins via the shared legal-resource URI. The version suffix is present for the primary ruleset and absent for non-primary ones — both sides agree by construction (see "Version confidence").

```sparql
PREFIX cprmv: <https://cprmv.open-regels.nl/0.3.0/>

SELECT ?rule ?dataset WHERE {
  ?rule a cprmv:Rule ; cprmv:implements ?legal .
  ?dataset a cprmv:Dataset ; cprmv:implements ?legal .
}
```

### Example result (Normenbrief, 69 rows from both joins)

| ?rule | ?dataset |
|---|---|
| `…/rules/BWBR0004163_2026-01-01_0_Artikel-5_lid-4_onderdeel-b` | `…/datasets/BWBR0004163_2026-01-01` |
| `…/rules/BWBR0044894_2026-01-01_0_Artikel-7a_onderdeel-c` | `…/datasets/BWBR0044894_2026-01-01` |
| `…/rules/BWBR0015703_2026-01-01_0_Artikel-22a_lid-3_onderdeel-a` | `…/datasets/BWBR0015703_2026-01-01` |
| `…/rules/BWBR0015711_2026-01-01_0_Artikel-25` | `…/datasets/BWBR0015711_2026-01-01` |
| `…/rules/BWBR0004044_2026-01-01_0_Artikel-8_lid-9` | `…/datasets/BWBR0004044_2026-01-01` |
| … | … |

Each rule pairs with the Dataset that represents the same BWB version, whether that BWB is the service's primary law or another ruleset referenced from within the service.

### Projecting Dataset metadata for an API endpoint

For richer responses (e.g. an LDE `/v1/norms` endpoint), project the Dataset's metadata alongside the rule:

```sparql
PREFIX cprmv: <https://cprmv.open-regels.nl/0.3.0/>
PREFIX dct:   <http://purl.org/dc/terms/>
PREFIX dcat:  <http://www.w3.org/ns/dcat#>

SELECT ?rule ?ruleId ?dataset ?title ?version ?landingPage WHERE {
  ?rule a cprmv:Rule ;
        cprmv:rulesetId ?rulesetId ;
        cprmv:id ?ruleId .
  ?dataset a cprmv:Dataset ;
           cprmv:rulesetId ?rulesetId ;
           dcat:landingPage ?landingPage .
  OPTIONAL { ?dataset dct:title ?title }
  OPTIONAL { ?dataset dcat:version ?version }
}
```

`dct:title` and `dcat:version` are `OPTIONAL` because non-primary Datasets omit them.

---

## Version confidence

Only one ruleset's version is known to the editor: the service's primary `legalResource`, which the user explicitly enters in the Legal tab. Other rulesets enter the picture solely via the `cprmv:rulesetId` field on individual CPRMV rules — their versions are unknown.

The generator handles this by emitting versioned URIs only for the primary ruleset. Both the Dataset emitter and the Rule emitter compare each rulesetId against the service's primary, and pass the version through only when they match:

```javascript
const primaryMatch = this.legalResource.bwbId.match(/(BWB[A-Z]?\d+|CVDR\d+)/i);
const primaryRulesetId = primaryMatch ? primaryMatch[0] : '';
const isPrimary = rulesetId === primaryRulesetId;
const versionForUri = isPrimary ? this.legalResource.version : '';
```

Symmetry between Rule and Dataset emitters is essential. If Rules emitted versioned URIs for non-primary rulesets while Datasets emitted un-versioned ones (or vice versa), the tight join would silently degrade for multi-BWB services.

---

## Vocabulary

Required prefixes (already declared in `TTL_NAMESPACES` in `src/utils/constants.js`):

```turtle
@prefix cprmv: <https://cprmv.open-regels.nl/0.3.0/> .
@prefix dcat:  <http://www.w3.org/ns/dcat#> .
@prefix dct:   <http://purl.org/dc/terms/> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
```

The Dataset entity type is registered in `vocabularies.config.js` for round-trip recognition on TTL import:

```javascript
cprmvDataset: {
  acceptedTypes: ['cprmv:Dataset', 'dcat:Dataset'],
  canonicalType: 'cprmv:Dataset',
}
```

Dataset round-trip parsing is not yet implemented in `parseTTL.enhanced.js` — on import, Dataset blocks are ignored. On export they are regenerated deterministically from each rule's `cprmv:rulesetId`, so single-trip round-tripping produces equivalent output. Manual edits to Dataset blocks in TTL files will not survive an import/export cycle.