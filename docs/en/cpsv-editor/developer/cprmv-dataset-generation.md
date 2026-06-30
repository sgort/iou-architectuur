# CPRMV RuleSet / Dataset Generation

!!! note "Target version is selectable since v1.10.5"
    The **CPRMV version selector** (next to the preview/export controls) chooses which
    vocabulary version the editor emits, and the two targets differ in **shape**, not just
    namespace:

    - **`0.4.1`** (default) — one `cprmv:RuleSet` (+ `cprmv:RuleMethod`) per legal source,
      under `https://standaarden.open-regels.nl/standards/cprmv/0.4.1#`. The RuleSet is
      typed `cprmv:RuleSet` only (the 0.4.1 ontology models a RuleSet as *part of* a
      `dcat:Dataset`, not as one).
    - **`0.3.2`** — one `cprmv:Dataset` per ruleset under
      `https://cprmv.open-regels.nl/0.3.2/`, for consumers still on the flat 0.3.x model
      (e.g. the Linked Data Explorer `/v1/norms?cprmv_version=0.3.2`). The Dataset is typed
      `cprmv:Dataset` **only** — deliberately *not* co-typed `dcat:Dataset`, see
      [SHACL note](#shacl-no-dcat-dataset) below.

    Both targets emit the same flat `cprmv:Rule` resources; only the wrapper (RuleSet vs
    Dataset) and the `cprmv:` namespace change. The selection applies to the live preview,
    the TTL download and publish-to-TriplyDB alike.

---

## Architecture

```
User edits CPRMV rules in CPRMVTab; picks a target version (0.4.1 | 0.3.2)
        ↓
On TTL export or publish, TTLGenerator.generate() in ttlGenerator.js:
    ...
    Service section                     (cpsv:PublicService)
    Organization section                (cv:PublicOrganisation)
    Legal Resource section              (eli:LegalResource)
    CPRMV wrapper section                ← 0.4.1: generateRuleSetsSection()
                                          ← 0.3.2: generateDatasetsSection()
    CPRMV Rules section                  ← flat cprmv:Rule (both targets)
    ...
        ↓
generateNamespaces():
    Bind the cprmv: prefix to the selected target's namespace
        ↓
generateRuleSetsSection()  /  generateDatasetsSection():
    Group rules by rulesetId (rules with no rulesetId attach to the primary group)
    For each rulesetId:
        date = rulesetDateFromRules(rules)          ← the _YYYY-MM-DD_ from ruleIdPath
               || (isPrimary ? legalResource.version : '')   ← manual fallback
               || today                                       ← last resort
        0.4.1 → Emit RuleMethod + RuleSet (cprmv:hasPart list), cprmv:validFrom = date
        0.3.2 → Emit cprmv:Dataset, dcat:version = date, dct:issued = now
        ↓
generateCprmvRulesSection():
    For each rule:
        Emit cprmv:Rule with cprmv:id (required), rulesetId, definition, situatie,
        norm, ruleIdPath, and cprmv:implements <{legalUri}>.
        Subject URI is unique even when two rules share a ruleIdPath (see cprmvRuleUri).
```

---

## Files

```
src/
├── utils/
│   ├── ttlGenerator.js         # generateRuleSetsSection, generateDatasetsSection,
│   │                             generateCprmvRulesSection, cprmvRuleUri / cprmvRuleUriMap,
│   │                             rulesetDateFromRules, primaryRulesetId / primaryRulesetDate,
│   │                             cprmvValidFrom, buildLegalUriForRulesetId, generateNamespaces
│   ├── cprmvImport.js          # flattenCprmvRules — CPRMV Rules API → flat model
│   │                             (folds sub-clauses into the parent definition)
│   ├── constants.js            # TTL_NAMESPACES; CPRMV_NS_BY_VERSION (0.4.1, 0.3.2)
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
- `cprmv:validFrom` (and the versioned `cprmv:id`/legal URI) is **derived per ruleset** from
  the BWB in-force date the ruleset's own rules carry in their `ruleIdPath` — the
  `_YYYY-MM-DD_` segment, e.g. `BWBR0015703_2026-04-03_0` → `2026-04-03`
  (`rulesetDateFromRules()`). It falls back to the manually-entered `legalResource.version`
  for the **primary** ruleset, then to today. Because the date comes from the rules,
  **every** ruleset — primary and non-primary alike — is now dated correctly and its
  version matches its rules' `applicable_date`. (Before v1.10.5 only the primary ruleset was
  versioned, from the hand-entered date; see [Version confidence](#version-confidence).)

### `generateDatasetsSection()` (0.3.2 target)

The 0.3.2 counterpart of `generateRuleSetsSection()`. Emits one `cprmv:Dataset` per
ruleset — the unit the Linked Data Explorer `/v1/norms` `dataset_versions` map reads —
carrying `dct:identifier`, `cprmv:rulesetId`, `cprmv:implements`, `dcat:version` (the
rules-derived date, see above), `dct:issued` (publication timestamp), `dcat:landingPage`,
and `dct:title` for the primary ruleset. The Dataset is typed `cprmv:Dataset` **only** (see
the [SHACL note](#shacl-no-dcat-dataset)). The flat
`cprmv:Rule` resources are emitted by `generateCprmvRulesSection()` for both targets.

### `cprmvRuleUri(rule)` / `cprmvRuleUriMap()`

Deterministic subject URI shared by the wrapper emitter (to build the `hasPart` list) and
the Rule emitter (to emit matching subjects), so the list members always resolve to real
`cprmv:Rule` nodes. Uses `sanitizeRuleIdPath(rule.ruleIdPath)` when available, else
`{rulesetId}_{ruleId}`. Pattern: `https://cprmv.open-regels.nl/rules/{identifier}`.

When **several rules share a `ruleIdPath`** — a range's bounds (*"meer dan € 59.782, doch
minder dan € 251.233"*) or multiple maxima (*"per maand"* / *"per kalenderjaar"*) — the
path-derived URI would collide and the rules would merge onto a single RDF subject,
silently dropping norm values on publish. `cprmvRuleUriMap()` therefore assigns the first
occurrence the path-derived URI and each subsequent duplicate an `_N` suffix (`_2`, `_3`, …)
in document order. The flat Rule emitter and the `hasPart` list share the map, so all rules
survive; the duplicates still share a `rule_id_path_key` (the LDE dedup key).

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

### Dataset (0.3.2 target)

When the **0.3.2** target is selected, the wrapper is a `cprmv:Dataset` per ruleset instead
of a RuleSet, under the `https://cprmv.open-regels.nl/0.3.2/` namespace:

```turtle
@prefix cprmv: <https://cprmv.open-regels.nl/0.3.2/> .

<https://cprmv.open-regels.nl/datasets/BWBR0015703_2026-04-03>
    a cprmv:Dataset ;
    dct:identifier "BWBR0015703_2026-04-03" ;
    dct:title "Participatiewet"@nl ;          # primary ruleset only
    cprmv:rulesetId "BWBR0015703" ;
    cprmv:implements <https://wetten.overheid.nl/BWBR0015703/2026-04-03> ;
    dcat:version "2026-04-03" ;                # the rules' own date (per ruleset)
    dct:issued "2026-06-30T12:52:36Z"^^xsd:dateTime ;
    dcat:landingPage <https://wetten.overheid.nl/BWBR0015703/2026-04-03> .
```

#### SHACL: the 0.3.2 Dataset is *not* co-typed `dcat:Dataset` { #shacl-no-dcat-dataset }

Earlier 0.3.x output co-typed the Dataset `cprmv:Dataset, dcat:Dataset`. That triggered the
CPSV-AP 3.2.0 `DatasetShape` (`sh:targetClass dcat:Dataset`), which requires `dct:title`,
`dct:description`, `dct:publisher` and a typed `dcat:landingPage` — none of which exist for
non-primary rulesets, producing four pre-publish validation errors per Dataset. The Dataset
is now typed **`cprmv:Dataset` only**: no SHACL shape targets `cprmv:Dataset`, and the LDE
`dataset_versions` query reads `cprmv:Dataset`, so validation passes and the data stays
fully consumable. This mirrors the RuleSet emitter's reason for not co-typing `dcat:Dataset`.

---

## Version confidence

**Changed in v1.10.5.** The version is now derived from the rules themselves, so it no
longer depends on the operator hand-entering a date. Each rule's `ruleIdPath` carries the
exact BWB in-force date the CPRMV API resolved (`…_YYYY-MM-DD_…`), and
`rulesetDateFromRules()` reads it per ruleset. Consequently **every** ruleset is versioned —
not only the service's primary `legalResource` — and a ruleset's version always matches its
rules' `applicable_date` by construction.

The manually-entered `legalResource.version` (Legal tab) remains a **fallback** for the
primary ruleset when no rule carries a dated `ruleIdPath`, with today's date as a last
resort. The wrapper emitter (RuleSet or Dataset) and the Rule emitter share the same derived
date and URI assignment, keeping tight `cprmv:implements` joins intact for multi-BWB
services.

!!! warning "Operator note"
    The hand-entered consolidation date no longer drives the published version. If it
    disagrees with the rules (e.g. a typed `2026-03-04` against `2026-04-03` rules), the
    rules win — which is the intended behaviour, since the rules carry the authoritative BWB
    date.

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

`src/utils/cprmvImport.js` `flattenCprmvRules()` walks the CPRMV Rules API shape — an array
of `cprmv:RuleSet` objects with nested `…#hasPart` object-maps. It reads the 0.4.1 standards
keys plus the `http://cprmv.open-regels.nl/` extension predicates (`situatie`, `norm`,
`rulesetid`, `rule_id_path`) and tolerates the legacy 0.4.1-slash and 0.3.0 namespaces,
`contains` instead of `hasPart`, and flat-array exports. Both `handleImportJSON` (`App.js`)
and the CPRMV tab's **Load Example** use it.

**Sub-clause folding (v1.10.5).** A rule's nested `hasPart` members come in two kinds, and
they are handled differently:

- **Sub-clauses** — members that carry **no `rule_id_path`** (e.g. the
  *"onderdeel 1°./2°./3°."* enumeration under *"Artikel 31, lid 2, onderdeel r."*) are
  **folded, in order and recursively, into the parent rule's `definition`** so the parent
  keeps the complete legal text (`… ingeval: <clause> <clause> …`). They are **not** imported
  as separate, norm-less rules.
- **Genuine nested rules** — members that **do** carry a `rule_id_path` remain their own
  flat entries (inheriting the parent's `rulesetId`).

For the 1 July 2026 0.4.1 normenbrief this turns 81 raw entries into **72** imported rules —
exactly the count `/v1/norms?cprmv_version=0.4.1` returns (the 9 sub-clauses fold into their
3 parents).

!!! note "`cprmv:contains` is no longer produced"
    Because sub-clauses are folded into the parent's `cprmv:definition`, the editor does
    **not** emit `cprmv:contains` / nested child rules. The LDE `/v1/norms` query still has an
    `OPTIONAL { ?rule cprmv:contains … }` for backward compatibility, but current editor
    output never populates it.
