# CPRMV RuleSet Generation

!!! note "Renamed in v1.10.0"
    This page previously documented `cprmv:Dataset` generation. As of CPRMV 0.4.1
    conformance (v1.10.0) the editor emits a `cprmv:RuleSet` (with a `cprmv:RuleMethod`)
    per legal source instead of a `cprmv:Dataset` (`+ dcat:Dataset`) block. The 0.4.1
    ontology models a RuleSet as *part of* a `dcat:Dataset` (`cprmv:is_part_of`), not as
    one, so the RuleSet is typed `cprmv:RuleSet` only.

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
    CPRMV RuleSet section                ← one RuleSet (+ RuleMethod) per unique rulesetId
    CPRMV Rules section                  ← per-rule cprmv:implements URI + cprmv:id
    ...
        ↓
generateRuleSetsSection():
    Group rules by rulesetId (rules with no rulesetId attach to the primary RuleSet)
    For each rulesetId:
        isPrimary = (rulesetId matches legalResource.bwbId)
        version   = isPrimary ? legalResource.version : ''
        Emit RuleMethod node  (cprmv:RuleMethod, cprmv:CodificationMethod)
        Emit RuleSet node     (cprmv:RuleSet) with an ordered cprmv:hasPart list
        ↓
generateCprmvRulesSection():
    For each rule:
        Emit cprmv:Rule with cprmv:id (required), rulesetId, definition, situatie,
        norm, ruleIdPath, and cprmv:implements <{legalUri}>
```

---

## Files

```
src/
├── utils/
│   ├── ttlGenerator.js         # generateRuleSetsSection, generateCprmvRulesSection,
│   │                             cprmvRuleUri, primaryRulesetId, cprmvValidFrom,
│   │                             buildLegalUriForRulesetId, buildLegalResourceUri
│   ├── cprmvImport.js          # flattenCprmvRules — CPRMV 0.4.1 Rules API → flat model
│   ├── constants.js            # TTL_NAMESPACES (cprmv 0.4.1, dcat, prov, dct, xsd)
│   └── ttlHelpers.js           # encodeURIComponentTTL, escapeTTLString, sanitizeRuleIdPath
└── config/
    └── vocabularies.config.js  # entityTypes.ruleSet / ruleMethod / cprmvRule
```

---

## API functions

### `generateRuleSetsSection()`

Emits one `cprmv:RuleSet` (and its `cprmv:RuleMethod`) per unique `cprmv:rulesetId`
found across the CPRMV Rules collection. Rules that carry no `rulesetId` of their own
attach to the **primary** RuleSet (derived from the service's `legalResource.bwbId`).

**Behaviour:**

- Returns `''` when there are no CPRMV rules.
- The `RuleMethod` is dual-typed `cprmv:RuleMethod, cprmv:CodificationMethod` so the
  `sh:class cprmv:RuleMethod` check passes without subclass entailment (the validator
  performs none).
- The `RuleSet` carries the RuleSetShape-required `cprmv:id`, `cprmv:validFrom`^^`xsd:date`,
  `cprmv:isOutputOf` → the `cpsv:PublicService`, `cprmv:hasMethod` → the RuleMethod, an
  ordered `cprmv:hasPart` RDF list of its rule URIs, a `prov:wasDerivedFrom` link to the
  legal source, and `cprmv:rulesetId`. The primary RuleSet additionally carries the
  legal resource's `dct:title`.
- `cprmv:validFrom` resolves to the legal resource's `version` when that is an ISO date,
  else today's date (it is required by the 0.4.1 RuleSetShape).

### `cprmvRuleUri(rule)`

Deterministic subject URI shared by the RuleSet emitter (to build the `hasPart` list) and
the Rule emitter (to emit matching subjects), so the list members always resolve to real
`cprmv:Rule` nodes. Uses `sanitizeRuleIdPath(rule.ruleIdPath)` when available, else
`{rulesetId}_{ruleId}`. Pattern: `https://cprmv.open-regels.nl/rules/{identifier}`.

### `buildLegalUriForRulesetId(rulesetId, version)`

Builds a canonical legal-resource URI from a BWB/CVDR identifier or full URI. Used by both
the Rule emitter and the RuleSet emitter so they produce symmetric URIs.

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

---

## Schema design

### RuleSet + RuleMethod (primary ruleset)

```turtle
<https://cprmv.open-regels.nl/rulesets/BWBR0015703_2026-01-01/method>
    a cprmv:RuleMethod, cprmv:CodificationMethod ;
    cprmv:id "BWBR0015703-method" .

<https://cprmv.open-regels.nl/rulesets/BWBR0015703_2026-01-01>
    a cprmv:RuleSet ;
    cprmv:id "BWBR0015703_2026-01-01" ;
    cprmv:validFrom "2026-01-01"^^xsd:date ;
    cprmv:isOutputOf <https://regels.overheid.nl/services/aow-leeftijd> ;
    cprmv:hasMethod <https://cprmv.open-regels.nl/rulesets/BWBR0015703_2026-01-01/method> ;
    prov:wasDerivedFrom <https://wetten.overheid.nl/BWBR0015703/2026-01-01> ;
    dct:title "Participatiewet"@nl ;
    cprmv:rulesetId "BWBR0015703" ;
    cprmv:hasPart ( <…/rules/BWBR0015703_2026-01-01_0_Artikel-22a_lid-3_onderdeel-a> … ) .
```

### CPRMV Rule companion

```turtle
<https://cprmv.open-regels.nl/rules/BWBR0044894_2026-01-01_0_Artikel-7a_onderdeel-c>
    a cprmv:Rule ;
    cprmv:id "onderdeel c." ;
    cprmv:rulesetId "BWBR0044894" ;
    cprmv:definition "19-jarigen: € 231,09;"@nl ;
    cprmv:situatie "19-jarigen"@nl ;
    cprmv:norm "231,09" ;
    cprmv:ruleIdPath "BWBR0044894_2026-01-01_0, Artikel 7a., onderdeel c." ;
    cprmv:implements <https://wetten.overheid.nl/BWBR0044894> .
```

`cprmv:id` is always emitted (required by RuleShape, falling back to `ruleIdPath` or a
placeholder). A rule from Article 7a of BWBR0044894 implements BWBR0044894 — not the
service's primary law — making rule-level claims accurate in multi-BWB services.

---

## Version confidence

Only one ruleset's version is known to the editor: the service's primary `legalResource`,
which the user explicitly enters in the Legal tab. Other rulesets enter the picture solely
via the `cprmv:rulesetId` field on individual rules — their versions are unknown. The
generator therefore emits versioned URIs only for the primary ruleset; the Rule and RuleSet
emitters both compare each `rulesetId` against the primary and pass the version through only
when they match. Symmetry between the two emitters keeps tight (`cprmv:implements`) joins
intact for multi-BWB services.

---

## Join semantics

RuleSets connect to Rules in two interchangeable ways — both return identical record sets:

```sparql
PREFIX cprmv: <https://standaarden.open-regels.nl/standards/cprmv/0.4.1#>

# Loose join — by rulesetId literal
SELECT ?rule ?ruleset WHERE {
  ?rule    a cprmv:Rule    ; cprmv:rulesetId ?id .
  ?ruleset a cprmv:RuleSet ; cprmv:rulesetId ?id .
}

# Membership join — via the ordered hasPart list
SELECT ?ruleset ?rule WHERE {
  ?ruleset a cprmv:RuleSet ; cprmv:hasPart/rdf:rest*/rdf:first ?rule .
}
```

---

## Vocabulary

Required prefixes (declared in `TTL_NAMESPACES` in `src/utils/constants.js`):

```turtle
@prefix cprmv: <https://standaarden.open-regels.nl/standards/cprmv/0.4.1#> .
@prefix prov:  <http://www.w3.org/ns/prov#> .
@prefix dcat:  <http://www.w3.org/ns/dcat#> .
@prefix dct:   <http://purl.org/dc/terms/> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
```

The RuleSet/RuleMethod/Rule entity types are registered in `vocabularies.config.js` for
round-trip recognition on TTL import. Detection of `cprmv:RuleSet` / `cprmv:RuleMethod` is
ordered **before** `cprmv:Rule`, since `a cprmv:Rule` is a substring of both.

```javascript
ruleSet:    { acceptedTypes: ['cprmv:RuleSet'],    canonicalType: 'cprmv:RuleSet' },
ruleMethod: { acceptedTypes: ['cprmv:RuleMethod'], canonicalType: 'cprmv:RuleMethod' },
cprmvRule:  { acceptedTypes: ['cprmv:Rule'],       canonicalType: 'cprmv:Rule' },
```

On export the RuleSet/RuleMethod blocks are regenerated deterministically from each rule's
`cprmv:rulesetId`, so single-trip round-tripping produces equivalent output.

---

## Importing the CPRMV 0.4.1 Rules API

`src/utils/cprmvImport.js` `flattenCprmvRules()` walks the CPRMV 0.4.1 Rules API shape — an
array of `cprmv:RuleSet` objects with nested `…#hasPart` object-maps — and recurses,
flattening sub-rules into the editor's flat rule model (nested rules inherit their parent's
`rulesetId`). It reads the 0.4.1 standards keys plus the `http://cprmv.open-regels.nl/`
extension predicates (`situatie`, `norm`, `rulesetid`, `rule_id_path`) and tolerates the
legacy 0.4.1-slash and 0.3.0 namespaces, `contains` instead of `hasPart`, and flat-array
exports. Both `handleImportJSON` (`App.js`) and the CPRMV tab's **Load Example** use it.
