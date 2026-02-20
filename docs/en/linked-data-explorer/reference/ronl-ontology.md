# RONL Ontology

The Linked Data Explorer uses a subset of the RONL Ontology v1.0 for two features: governance validation badges and vendor service discovery.

For the full ontology specification — all 9 governance properties, the vendor vocabulary, namespace definitions, parser configuration, and UI validation rules — see:

**[CPSV Editor → References → RONL Ontology](../../cpsv-editor/reference/ronl-ontology.md)**

---

## Properties used in the Linked Data Explorer

### Governance badges

| Property | Type | Used for |
|---|---|---|
| `ronl:validationStatus` | `xsd:string` | Badge state: `"validated"`, `"in-review"`, `"not-validated"` |
| `ronl:validatedBy` | URI | Organisation that performed validation (resolved to name via `skos:prefLabel`) |
| `ronl:validatedAt` | `xsd:date` | Validation date shown in badge tooltip |
| `ronl:validationNote` | `rdf:langString` | Optional note shown in badge tooltip |

Applied to: `cprmv:DecisionModel`

### Vendor services

| Property | Type | Used for |
|---|---|---|
| `ronl:VendorService` | Class | A commercial implementation of a government decision model |
| `ronl:basedOn` | URI | Links vendor service to the reference `cprmv:DecisionModel` |
| `ronl:implementedBy` | URI | Platform URI (e.g., `<https://regels.overheid.nl/termen/Blueriq>`) |
| `ronl:accessType` | `xsd:string` | `"iam-required"`, `"public"`, `"api-key"` |

Combined with `schema:provider`, `schema:url`, `schema:license`, `foaf:homepage` for contact and service details.

---

## Namespace

```turtle
@prefix ronl: <https://regels.overheid.nl/ontology#> .
```
