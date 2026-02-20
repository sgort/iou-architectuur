# Vendor Tab Implementation

---

## Architecture

```
VendorTab.jsx
  ├── Vendor dropdown (SPARQL → TriplyDB)
  ├── IKnowMappingTab.jsx  (conditional on vendor = iKnow URI)
  └── {VendorSpecificForm} (conditional on selected vendor URI)
        e.g. BlueriqVendorForm (inline in VendorTab for now)

src/utils/
  ├── ronlHelper.js        # fetchAllRonlConcepts() — loads vendor dropdown
  ├── iknowParser.js       # iKnow XML parser
  └── ttlGenerator.js      # generateVendorServiceSection()
```

---

## Vendor list source

Vendors are loaded from TriplyDB via SPARQL:

```sparql
PREFIX ronl: <https://regels.overheid.nl/termen/>
SELECT ?vendor ?label WHERE {
  ?vendor a ronl:MethodConcept ;
          skos:prefLabel ?label .
}
```

Endpoint: `https://api.open-regels.triply.cc/datasets/stevengort/ronl/services/ronl/sparql`

Vendor URIs follow the pattern `https://regels.overheid.nl/termen/{VendorName}`.

---

## Vendor state shape

```javascript
vendorService: {
  selectedVendor: string,         // Vendor URI
  serviceTitle: string,
  contact: {
    contactPerson: string,
    email: string,
    phone: string,
    website: string,
    logo: string | null,          // Base64 encoded image
  },
  technical: {
    serviceUrl: string,
    license: string,
    accessType: string,
  },
  serviceNotes: string,
  certification: {
    status: string,               // 'not-certified' | 'self-assessed' | 'certified'
    certifiedBy: string,          // Organisation URI
    certifiedAt: string,          // ISO date
    certificationNote: string,
  }
}
```

---

## TTL output

The generated Turtle for a vendor service:

```turtle
<https://regels.overheid.nl/vendor-services/{vendor}/{serviceId}>
    a ronl:VendorService ;
    dct:title "{serviceTitle}"@nl ;
    ronl:basedOn <https://regels.overheid.nl/services/{serviceId}> ;
    ronl:implementedBy <{vendorUri}> ;
    schema:provider [
        a schema:Organization ;
        schema:name "{vendorName}" ;
        schema:image <./assets/{VendorName}_vendor_logo.png> ;
        schema:contactPoint [
            schema:name "{contactPerson}" ;
            schema:email "{email}" ;
            schema:telephone "{phone}"
        ] ;
        foaf:homepage <{website}>
    ] ;
    schema:url <{serviceUrl}> ;
    schema:license "{license}" ;
    ronl:certificationStatus "{status}"^^xsd:string ;
    ronl:certifiedBy <{certifiedByUri}> ;
    ronl:certifiedAt "{date}"^^xsd:date .
```

---

## Adding a new vendor integration

1. Create `src/components/tabs/vendors/{VendorName}VendorForm.jsx` with the vendor-specific form fields.
2. Add conditional rendering in `VendorTab.jsx`:

```javascript
{selectedVendor === 'https://regels.overheid.nl/termen/YourVendor' && (
  <YourVendorForm vendorService={vendorService} setVendorService={setVendorService} />
)}
```

3. Implement a data parser in `src/utils/{vendorName}Parser.js` if the vendor provides an importable data format.
4. Add state management for any vendor-specific configuration fields.
5. Add the vendor's URI to the RONL vocabulary in TriplyDB so it appears in the dropdown.

---

## Certification auto-population

The Vendor tab watches the Organisation tab's identifier and automatically populates `vendorService.certification.certifiedBy` with the competent authority URI:

```javascript
useEffect(() => {
  if (organization.identifier) {
    const orgUri = organization.identifier.startsWith('http')
      ? organization.identifier
      : `https://regels.overheid.nl/organizations/${organization.identifier}`;
    setVendorService(prev => ({
      ...prev,
      certification: { ...prev.certification, certifiedBy: orgUri }
    }));
  }
}, [organization.identifier]);
```

---

## Planned enhancements

- **v1.9.1** — Import support: parse `ronl:VendorService` entities from imported Turtle files, enabling full round-trip for vendor metadata.
- **v1.10.0** — Additional vendor form components (Oracle Policy Automation, IBM ODM).
- **v2.0.0** — Logo upload integration in the TriplyDB publish flow; currently logos generate an asset path but are not uploaded.
- **v2.1.0** — Public certification registry: SPARQL query across all `ronl:VendorService` instances with certified status, displayed as a searchable table.
