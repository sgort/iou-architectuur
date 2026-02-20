# RONL Ontology

**Namespace URI:** `https://regels.overheid.nl/ontology#`  
**Prefix:** `ronl:`  
**Version:** 1.0.0  
**Status:** Draft  
**Maintainer:** RONL Initiative / VWS

---

## Purpose

The RONL Ontology defines a vocabulary for organisational governance of Dutch government rules and decision models. It provides properties for tracking validation, certification, and vendor relationships — enabling transparent, auditable governance of government decision logic.

The ontology defines **properties** only. It reuses existing classes from CPSV-AP (`cpsv:PublicService`, `cv:PublicOrganisation`), CPRMV (`cprmv:DecisionModel`), and W3C ORG (`org:Organization`).

---

## Validation properties

Applied to `cprmv:DecisionModel` and `cpsv:PublicService`:

| Property | Range | Cardinality | Description |
|---|---|---|---|
| `ronl:validatedBy` | URI | 0..1 | Organisation that performed validation |
| `ronl:validationStatus` | `xsd:string` | 0..1 | Validation state (e.g. `"validated"`, `"pending"`) |
| `ronl:validatedAt` | `xsd:date` | 0..1 | Date of validation |
| `ronl:validationNote` | Literal | 0..1 | Free-text notes on the validation process |

---

## Certification properties

Applied to `cpsv:PublicService` (typically a vendor service):

| Property | Range | Cardinality | Description |
|---|---|---|---|
| `ronl:certifiedBy` | URI | 0..1 | Organisation that issued certification |
| `ronl:certificationStatus` | `xsd:string` | 0..1 | Certification state (e.g. `"certified"`, `"self-assessed"`) |
| `ronl:certifiedAt` | `xsd:date` | 0..1 | Date of certification |
| `ronl:certificationNote` | Literal | 0..1 | Free-text notes on the certification scope |

---

## Vendor integration properties

| Property | Domain | Range | Cardinality | Description |
|---|---|---|---|---|
| `ronl:basedOn` | VendorService | URI | 0..1 | Reference service this implementation is based on |
| `ronl:vendorType` | Organisation | `xsd:string` | 0..1 | Vendor classification (e.g. `"commercial"`) |

---

## Property constraints

The following rules apply when producing or validating Turtle using these properties:

If `ronl:validationStatus` is `"validated"`, then `ronl:validatedBy` and `ronl:validatedAt` must be present.

If `ronl:certificationStatus` is `"certified"`, then `ronl:certifiedBy` and `ronl:certifiedAt` must be present, and `ronl:certifiedAt` must be on or after `ronl:validatedAt`.

If a subject has `ronl:certifiedBy`, it must also have `ronl:basedOn` (certified vendor services must reference a canonical service for traceability).

---

## Example: Reference DMN validation

```turtle
@prefix ronl:  <https://regels.overheid.nl/ontology#> .
@prefix cprmv: <https://cprmv.open-regels.nl/0.3.0/> .
@prefix dct:   <http://purl.org/dc/terms/> .

<https://regels.overheid.nl/services/aow-leeftijd/dmn>
    a cprmv:DecisionModel ;
    dct:identifier "SVB_LeeftijdsInformatie" ;
    dct:title "SVB Leeftijdsinformatie DMN"@nl ;
    cprmv:implements <https://regels.overheid.nl/services/aow-leeftijd> ;
    ronl:validatedBy <https://organisaties.overheid.nl/28212263/Sociale_Verzekeringsbank> ;
    ronl:validationStatus "validated"^^xsd:string ;
    ronl:validatedAt "2026-02-15"^^xsd:date ;
    ronl:validationNote "Validated against AOW legislation Article 7a. 127 test cases passed."@nl .
```

---

## Example: Vendor service certification

```turtle
@prefix ronl:   <https://regels.overheid.nl/ontology#> .
@prefix cpsv:   <http://purl.org/vocab/cpsv#> .
@prefix dct:    <http://purl.org/dc/terms/> .

<https://regels.overheid.nl/vendor-services/blueriq/aow-leeftijd>
    a cpsv:PublicService ;
    dct:identifier "blueriq-aow-leeftijd" ;
    dct:title "AOW Leeftijd - Blueriq Implementation"@nl ;
    ronl:basedOn <https://regels.overheid.nl/services/aow-leeftijd> ;
    ronl:validatedBy <https://regels.overheid.nl/vendors/blueriq> ;
    ronl:validationStatus "validated"^^xsd:string ;
    ronl:validatedAt "2026-02-10"^^xsd:date ;
    ronl:certifiedBy <https://organisaties.overheid.nl/28212263/Sociale_Verzekeringsbank> ;
    ronl:certificationStatus "certified"^^xsd:string ;
    ronl:certifiedAt "2026-02-15"^^xsd:date ;
    ronl:certificationNote "Meets SVB implementation requirements v2.1. Annual recertification required."@nl .
```
