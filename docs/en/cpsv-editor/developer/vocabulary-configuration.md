# Vocabulary Configuration

The `src/config/vocabularies_config.js` file is the central configuration for all RDF vocabulary handling in the editor. It controls how the parser recognises entities and properties in imported Turtle files. Adding support for a new vocabulary requires only configuration changes — no parser code modifications.

---

## File structure

```javascript
export const VOCABULARY_CONFIG = {
  version: '2.1.0',
  lastUpdated: '2026-06-11',

  namespaces: { /* URI → prefix mappings */ },
  entityTypes: { /* RDF type → editor section mappings */ },
  propertyAliases: { /* alternative property → canonical property */ },
};
```

!!! note "v2.0.0 vocabulary migration"
    Rule properties moved from `ronl:` to `cprmv:`; `ronl:` is now used exclusively for
    validation/certification governance. Backward compatibility is provided via a
    `ronl-legacy` import-only alias. The CPRMV namespace is `…/cprmv/0.4.1#`.

---

## Namespaces

Maps namespace URIs to the prefix(es) accepted in Turtle files.

**Current configuration:**

```javascript
namespaces: {
  'http://purl.org/vocab/cpsv#':                              ['cpsv'],
  'http://data.europa.eu/m8g/':                               ['cv', 'cpsv-ap'],
  'http://www.w3.org/ns/org#':                                ['org'],
  'http://xmlns.com/foaf/0.1/':                               ['foaf'],
  'http://data.europa.eu/eli/ontology#':                      ['eli'],
  'https://regels.overheid.nl/ontology#':                     ['ronl'],          // governance only
  'https://regels.overheid.nl/termen/':                       ['ronl-legacy'],   // import-only, never exported
  'https://standaarden.open-regels.nl/standards/cprmv/0.4.1#':['cprmv'],
  'http://www.w3.org/ns/prov#':                               ['prov'],
  'http://purl.org/dc/terms/':                                ['dct'],
  'http://www.w3.org/ns/dcat#':                               ['dcat'],
  'http://www.w3.org/2004/02/skos/core#':                     ['skos'],
  'http://www.w3.org/2001/XMLSchema#':                        ['xsd'],
  'http://schema.org/':                                       ['schema'],
}
```

**Adding a namespace:**

```javascript
namespaces: {
  // existing entries...
  'http://www.w3.org/ns/prov#': ['prov'],
}
```

---

## Entity types

Defines which RDF types are recognised and which editor section they map to.

**Current configuration:**

```javascript
entityTypes: {
  service: {
    acceptedTypes: ['cpsv:PublicService', 'cpsv-ap:PublicService'],
    canonicalType: 'cpsv:PublicService'
  },
  organization: {
    acceptedTypes: ['cv:PublicOrganisation'],
    canonicalType: 'cv:PublicOrganisation'
  },
  concept:       { acceptedTypes: ['skos:Concept'], canonicalType: 'skos:Concept' },
  cost:          { acceptedTypes: ['cv:Cost'],      canonicalType: 'cv:Cost' },
  output:        { acceptedTypes: ['cv:Output'],    canonicalType: 'cv:Output' },
  legalResource: { acceptedTypes: ['eli:LegalResource'], canonicalType: 'eli:LegalResource' },
  temporalRule: {
    acceptedTypes: ['cprmv:TemporalRule', 'cpsv:Rule', 'ronl:TemporalRule'], // ronl = legacy
    canonicalType: 'cprmv:TemporalRule'
  },
  parameter: {
    acceptedTypes: ['cprmv:ParameterWaarde', 'skos:Concept', 'ronl:ParameterWaarde'],
    canonicalType: 'cprmv:ParameterWaarde'
  },
  ruleSet:    { acceptedTypes: ['cprmv:RuleSet'],    canonicalType: 'cprmv:RuleSet' },
  ruleMethod: { acceptedTypes: ['cprmv:RuleMethod'], canonicalType: 'cprmv:RuleMethod' },
  cprmvRule:  { acceptedTypes: ['cprmv:Rule'],       canonicalType: 'cprmv:Rule' },
  vendorService: { acceptedTypes: ['ronl:VendorService'], canonicalType: 'ronl:VendorService' },
}
```

**Adding a type to an existing section:**

```javascript
parameter: {
  acceptedTypes: [
    'cprmv:ParameterWaarde',
    'skos:Concept',
    'ronl:ParameterWaarde',  // legacy
    'custom:Parameter'       // ← add here, never remove existing
  ],
  canonicalType: 'cprmv:ParameterWaarde'
}
```

Always add new types alongside existing ones. Removing an accepted type breaks import of files that use it.

!!! warning "Detection order matters"
    `detectEntityType()` checks DMN entities first, then `cprmv:RuleSet` / `cprmv:RuleMethod`
    **before** `cprmv:Rule` — because `a cprmv:Rule` is a substring of `a cprmv:RuleSet` /
    `a cprmv:RuleMethod` and would otherwise match first. `skos:Concept` detection excludes
    `skos:ConceptScheme`.

---

## Property aliases

Maps alternative property expressions to the canonical form the editor uses internally.

**Current configuration:**

```javascript
propertyAliases: {
  // Organization name variants
  'foaf:name':      'skos:prefLabel',
  'org:name':       'skos:prefLabel',

  // CPSV-AP to CV property mapping
  'cpsv-ap:hasCompetentAuthority': 'cv:hasCompetentAuthority',
  'cpsv-ap:thematicArea':          'cv:thematicArea',
  'cpsv-ap:sector':                'cv:sector',
  'cpsv-ap:hasChannel':            'cv:hasChannel',
  'cpsv-ap:hasContactPoint':       'cv:hasContactPoint',
  'cpsv-ap:hasCost':               'cv:hasCost',
  'cpsv-ap:hasOutput':             'cv:hasOutput',
  'cpsv-ap:hasLegalResource':      'cv:hasLegalResource',

  // v2.0.0: legacy ronl:* (import-only) → current cprmv:* equivalents
  'ronl-legacy:hasAnalysis':     'cprmv:hasAnalysis',
  'ronl-legacy:hasMethod':       'cprmv:hasMethod',
  'ronl-legacy:implements':      'cprmv:implements',
  'ronl-legacy:implementedBy':   'cprmv:implementedBy',
  'ronl-legacy:confidenceLevel': 'cprmv:confidenceLevel',
  'ronl-legacy:validFrom':       'cprmv:validFrom',
  'ronl-legacy:validUntil':      'cprmv:validUntil',
  'ronl-legacy:extends':         'cprmv:extends',

  // CPRMV self-aliases (normalise confidence variants)
  'cprmv:confidence':      'cprmv:confidenceLevel',
  'cprmv:confidenceLevel': 'cprmv:confidenceLevel',
  'cprmv:extends':         'cprmv:extends'
}
```

---

## Helper functions

The config file exports several utility functions used by the parser:

**`detectEntityType(line)`** — Returns the editor section name for a `a <type>` line (DMN and RuleSet/RuleMethod checked first), or `null`.

**`normalizeProperty(property)`** — Maps an alias (e.g. `ronl-legacy:validFrom`) to its canonical form, or returns the property unchanged.

**`getCanonicalType(entityName)`** — Returns the canonical RDF type for a given editor section.

**`extractPrefixMap(ttlContent)`** — Parses all `@prefix` declarations from a Turtle string and returns a `{ prefix: uri }` map.

**`validatePrefixes(ttlContent, { silent })`** — Checks whether essential prefixes are present in the Turtle string. Returns `{ valid: boolean, warnings: string[] }`.

---

## Testing configuration changes

After modifying the configuration:

1. Create a minimal Turtle file using the new vocabulary:

```turtle
@prefix custom: <https://example.org/vocab#> .
@prefix dct: <http://purl.org/dc/terms/> .

<https://example.nl/test/1> a custom:NewType ;
    dct:title "Test Service"@nl .
```

2. Start the editor (`npm start`), click **Import TTL File**, and select the test file.
3. Verify the data appears in the expected tab with no console errors.
4. Export (Download TTL) and import the result to verify round-trip fidelity.

---

## Troubleshooting

**Entity not appearing in any tab** — The RDF type is not in `acceptedTypes` for any section. Add it.

**Property value is empty after import** — The property needs an alias, or it is not handled by the parser. Check `parseTTL.enhanced.js` for the property and add an alias if needed.

**Console warning about missing prefix** — Add the namespace URI to `namespaces`.
