# Governance Implementation

This page covers the backend SPARQL query, TypeScript interfaces, and frontend components that implement the DMN validation badge system.

---

## Backend — SPARQL query

Validation metadata is fetched alongside DMN data in `findAllDmns` using `OPTIONAL` blocks that do not break when governance data is absent:

```sparql
PREFIX ronl: <https://regels.overheid.nl/ontology#>

SELECT ...
WHERE {
  ?dmn a cprmv:DecisionModel ;
       dct:identifier ?identifier ;
       dct:title ?title .

  # Governance metadata (all optional)
  OPTIONAL { ?dmn ronl:validationStatus ?validationStatus }
  OPTIONAL {
    ?dmn ronl:validatedBy ?validatedBy .
    OPTIONAL { ?validatedBy skos:prefLabel ?validatedByName . }
  }
  OPTIONAL { ?dmn ronl:validatedAt ?validatedAt }
  OPTIONAL { ?dmn ronl:validationNote ?validationNote }
}
```

The `validatedByName` is resolved via `skos:prefLabel` on the organisation URI (`ronl:validatedBy` points to a URI, not a literal). If the organisation resource has no `skos:prefLabel`, the badge renders without the organisation name — graceful degradation.

---

## Backend — TypeScript interface

```typescript
// In sparql.service.ts DmnModel interface
interface DmnModel {
  id: string;
  identifier: string;
  title: string;
  // ... core fields ...

  // Governance fields
  validationStatus?: 'validated' | 'in-review' | 'not-validated';
  validatedBy?: string;        // Organisation URI
  validatedByName?: string;    // Resolved skos:prefLabel
  validatedAt?: string;        // ISO 8601 date string
  validationNote?: string;
}
```

---

## Frontend — ValidationBadge component

`ValidationBadge.tsx` renders conditionally based on `validationStatus`. No badge renders for `"not-validated"` or when `validationStatus` is absent:

```typescript
interface ValidationBadgeProps {
  status: 'validated' | 'in-review' | 'not-validated' | undefined;
  validatedByName?: string;
  validatedAt?: string;
  compact?: boolean;
}

const ValidationBadge: React.FC<ValidationBadgeProps> = ({
  status, validatedByName, validatedAt, compact
}) => {
  if (!status || status === 'not-validated') return null;

  const isValidated = status === 'validated';

  return (
    <span
      className={`badge ${isValidated ? 'badge-green' : 'badge-amber'}`}
      title={`${validatedByName ?? ''} ${validatedAt ?? ''}`}
    >
      {isValidated ? '✓ Gevalideerd' : '⏱ In Review'}
    </span>
  );
};
```

The `compact` prop reduces the badge to a small indicator for use on Chain Composer cards where space is limited.

---

## Frontend — integration points

- `DmnList.tsx` — badge appears on each card in the Available DMNs panel
- `ChainComposer.tsx` — badge persists on cards after they are dropped into the chain

---

## RDF data structure

The canonical RDF for a validated DMN:

```turtle
@prefix ronl:  <https://regels.overheid.nl/ontology#> .
@prefix cprmv: <https://cprmv.open-regels.nl/0.3.0/> .
@prefix dct:   <http://purl.org/dc/terms/> .
@prefix skos:  <http://www.w3.org/2004/02/skos/core#> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
@prefix org:   <http://www.w3.org/ns/org#> .

<https://organisaties.overheid.nl/28212263/Sociale_Verzekeringsbank>
  a org:Organization ;
  skos:prefLabel "Sociale Verzekeringsbank"@nl .

<https://regels.overheid.nl/services/aow-leeftijd/dmn>
  a cprmv:DecisionModel ;
  dct:identifier "SVB_LeeftijdsInformatie" ;
  ronl:validationStatus "validated"^^xsd:string ;
  ronl:validatedBy <https://organisaties.overheid.nl/28212263/Sociale_Verzekeringsbank> ;
  ronl:validatedAt "2026-02-14"^^xsd:date ;
  ronl:validationNote "Validated against AOW legislation Article 7a"@nl .
```

This data is published from the CPSV Editor. See the [CPSV Editor — Publishing to TriplyDB](../../cpsv-editor/user-guide/publishing-to-triplydb.md) guide for the publisher workflow.

---

## RONL Ontology reference

For the full property specification, see [CPSV Editor — RONL Ontology](../../cpsv-editor/reference/ronl-ontology.md). The properties used by the governance badge system are `ronl:validationStatus`, `ronl:validatedBy`, `ronl:validatedAt`, and `ronl:validationNote`.
