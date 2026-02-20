# Vendor Services Implementation

This page covers the SPARQL query, TypeScript interfaces, and UI components that implement the vendor badge and detail modal.

---

## Backend — SPARQL query

Vendor data is queried alongside DMN metadata using `OPTIONAL` blocks:

```sparql
PREFIX ronl:   <https://regels.overheid.nl/ontology#>
PREFIX schema: <http://schema.org/> .
PREFIX foaf:   <http://xmlns.com/foaf/0.1/> .

SELECT ?identifier
       ?vendorService ?vendorPlatform
       ?providerName ?providerLogo ?providerHomepage
       ?contactName ?contactEmail ?contactPhone
       ?serviceUrl ?license ?accessType ?description
WHERE {
  ?dmn a cprmv:DecisionModel ;
       dct:identifier ?identifier .

  OPTIONAL {
    ?vendorService a ronl:VendorService ;
                   ronl:basedOn ?dmn ;
                   ronl:implementedBy ?vendorPlatform .
    OPTIONAL {
      ?vendorService schema:provider ?provider .
      OPTIONAL { ?provider schema:name ?providerName . }
      OPTIONAL { ?provider schema:image ?providerLogo . }
      OPTIONAL { ?provider foaf:homepage ?providerHomepage . }
      OPTIONAL {
        ?provider schema:contactPoint ?contact .
        OPTIONAL { ?contact schema:name ?contactName . }
        OPTIONAL { ?contact schema:email ?contactEmail . }
        OPTIONAL { ?contact schema:telephone ?contactPhone . }
      }
    }
    OPTIONAL { ?vendorService schema:url ?serviceUrl . }
    OPTIONAL { ?vendorService schema:license ?license . }
    OPTIONAL { ?vendorService ronl:accessType ?accessType . }
    OPTIONAL { ?vendorService dct:description ?description . }
  }
}
```

The backend groups multiple vendor records per DMN identifier in post-processing, building the `vendors` array on each `DmnModel`.

---

## TypeScript interfaces

```typescript
interface VendorService {
  uri: string;
  platform?: string;          // ronl:implementedBy URI
  providerName?: string;
  providerLogo?: string;      // Image URI
  providerHomepage?: string;
  contactName?: string;
  contactEmail?: string;
  contactPhone?: string;
  serviceUrl?: string;
  license?: 'Commercial' | 'Open Source' | 'Free';
  accessType?: 'iam-required' | 'public' | 'api-key';
  description?: string;
}

// Added to DmnModel
interface DmnModel {
  // ... existing fields ...
  vendorCount: number;
  vendors: VendorService[];
}
```

---

## Frontend — vendor badge

The vendor count badge on a DMN card renders only when `vendorCount > 0`:

```typescript
{dmn.vendorCount > 0 && (
  <button
    className="vendor-badge"
    onClick={(e) => { e.stopPropagation(); openVendorModal(dmn); }}
  >
    🏢 {dmn.vendorCount}
  </button>
)}
```

`e.stopPropagation()` prevents the card expand/collapse from triggering when the badge is clicked.

---

## Frontend — vendor modal

The vendor modal renders a section per vendor in `dmn.vendors`. Key rendering logic for licence and access type badges:

```typescript
const licenceBadge = {
  'Commercial': 'badge-purple',
  'Open Source': 'badge-green',
  'Free': 'badge-blue',
};

const accessBadge = {
  'iam-required': { label: 'IAM Required', style: 'badge-amber' },
  'public': { label: 'Public Access', style: 'badge-green' },
  'api-key': { label: 'API Key Required', style: 'badge-blue' },
};
```

Contact fields render as links: `href="mailto:{email}"`, `href="tel:{phone}"`, `href="{serviceUrl}"` with `target="_blank"`.

---

## RDF data structure

Vendor metadata is published via the CPSV Editor and stored in TriplyDB as:

```turtle
@prefix ronl:   <https://regels.overheid.nl/ontology#> .
@prefix schema: <http://schema.org/> .
@prefix foaf:   <http://xmlns.com/foaf/0.1/> .
@prefix dct:    <http://purl.org/dc/terms/> .

<https://regels.overheid.nl/services/aow-leeftijd/vendor/blueriq>
  a ronl:VendorService ;
  ronl:basedOn <https://regels.overheid.nl/services/aow-leeftijd/dmn> ;
  ronl:implementedBy <https://regels.overheid.nl/termen/Blueriq> ;
  schema:provider [
    a schema:Organization ;
    schema:name "Blueriq B.V." ;
    schema:image <./assets/Blueriq_vendor_logo.png> ;
    foaf:homepage <https://www.blueriq.com> ;
    schema:contactPoint [
      schema:name "John Doe" ;
      schema:email "john.doe@blueriq.com" ;
      schema:telephone "+31 6 12 34 56 78"
    ]
  ] ;
  schema:url <https://regelservices.blueriq.com/shortcut/Doccle> ;
  schema:license "Commercial" ;
  ronl:accessType "iam-required" ;
  dct:description "Pensioen Regelservice voor gebruik in combinatie met Doccle."@nl .
```

---

## RONL Ontology reference

The vendor vocabulary (`ronl:VendorService`, `ronl:basedOn`, `ronl:implementedBy`, `ronl:accessType`) is part of the RONL Ontology v1.0. For the full specification, see [CPSV Editor — RONL Ontology](../../cpsv-editor/reference/ronl-ontology.md).
