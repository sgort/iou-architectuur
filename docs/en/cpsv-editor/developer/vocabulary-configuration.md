# Vocabulary Configuration

The `src/config/vocabularies_config.js` file is the central configuration for all RDF vocabulary handling in the editor. It controls how the parser recognises entities and properties in imported Turtle files. Adding support for a new vocabulary requires only configuration changes — no parser code modifications.

---

## File structure

```javascript
export const VOCABULARY_CONFIG = {
  version: '1.0.0',
  lastUpdated: '2025-10-27',

  namespaces: { /* URI → prefix mappings */ },
  entityTypes: { /* RDF type → editor section mappings */ },
  propertyAliases: { /* alternative property → canonical property */ },
};
```

---

## Namespaces

Maps namespace URIs to the prefix(es) accepted in Turtle files.

**Current configuration:**

```javascript
namespaces: {
  'http://purl.org/vocab/cpsv#':               ['cpsv'],
  'http://data.europa.eu/m8g/':                ['cv', 'cpsv-ap'],
  'http://www.w3.org/ns/org#':                 ['org'],
  'http://xmlns.com/foaf/0.1/':                ['foaf'],
  'http://data.europa.eu/eli/ontology#':       ['eli'],
  'https://regels.overheid.nl/termen/':        ['ronl'],
  'https://cprmv.open-regels.nl/0.3.0/':       ['cprmv'],
  'http://purl.org/dc/terms/':                 ['dct'],
  'http://www.w3.org/ns/dcat#':                ['dcat'],
  'http://www.w3.org/2004/02/skos/core#':      ['skos'],
  'http://www.w3.org/2001/XMLSchema#':         ['xsd'],
  'http://schema.org/':                        ['schema'],
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
    acceptedTypes: ['org:Organization', 'foaf:Organization'],
    canonicalType: 'org:Organization'
  },
  legalResource: {
    acceptedTypes: ['eli:LegalResource'],
    canonicalType: 'eli:LegalResource'
  },
  temporalRule: {
    acceptedTypes: ['ronl:TemporalRule'],
    canonicalType: 'ronl:TemporalRule'
  },
  parameter: {
    acceptedTypes: ['skos:Concept', 'ronl:ParameterWaarde'],
    canonicalType: 'skos:Concept'
  }
}
```

**Adding a type to an existing section:**

```javascript
parameter: {
  acceptedTypes: [
    'skos:Concept',
    'ronl:ParameterWaarde',
    'custom:Parameter'       // ← add here, never remove existing
  ],
  canonicalType: 'skos:Concept'
}
```

Always add new types alongside existing ones. Removing an accepted type breaks import of files that use it.

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

  // CPRMV to RONL property mapping
  'cprmv:validFrom':       'ronl:validFrom',
  'cprmv:validUntil':      'ronl:validUntil',
  'cprmv:confidence':      'ronl:confidenceLevel',
  'cprmv:confidenceLevel': 'ronl:confidenceLevel',
  'cprmv:extends':         'ronl:extends'
}
```

---

## Helper functions

The config file exports several utility functions used by the parser:

**`isKnownPrefix(prefix)`** — Returns true if the prefix is registered in `namespaces`.

**`resolveNamespace(prefix)`** — Returns the full URI for a prefix, or null.

**`getCanonicalType(sectionName)`** — Returns the canonical RDF type for a given editor section.

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
