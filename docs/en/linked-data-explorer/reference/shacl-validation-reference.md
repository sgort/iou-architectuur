# SHACL Validation Reference

This reference documents the shape layers used by the SHACL Validator, the constraint codes it emits, and the rationale for the RONL-specific shapes. The validator runs on the shared backend at `POST /v1/shacl/validate` (file-local) and `POST /v1/shacl/validate-merged` (merge-simulated), and is used by the Linked Data Explorer's standalone SHACL Validator view.

---

## How to read this reference

Issues are grouped into two layers. Each issue carries a severity, a typed code, the focus node and property path it applies to, and — for cardinality and uniqueness constraints — the offending values.

| Field | Meaning |
|---|---|
| **Layer** | `CPSV-AP 3.2.0` (canonical, vendored) or `RONL Custom` (RONL-authored) |
| **Code** | Derived from the SHACL `sh:sourceConstraintComponent` local name (e.g. `SHACL-MAXCOUNT`) |
| **Severity** | `error` (`sh:Violation`), `warning` (`sh:Warning`), `info` (`sh:Info`) |
| **Focus node** | The subject the constraint was evaluated against |
| **Path** | The property the constraint applies to |

---

## Validation modes

| Mode | Endpoint | Behaviour |
|---|---|---|
| File-local | `POST /v1/shacl/validate` | Validates the uploaded Turtle exactly as written. |
| Merge-simulated | `POST /v1/shacl/validate-merged` | Fetches the already-published triples for the file's subjects via a read-only SPARQL `CONSTRUCT`, unions them with the file, then validates. Catches collisions that only emerge once the file is added to the store. |

Merge-simulated mode never writes to the endpoint.

---

## Layer 1 — CPSV-AP 3.2.0

This layer is the canonical SHACL shapes file from the SEMIC CPSV-AP 3.2.0 release, vendored verbatim into `packages/backend/shapes/cpsv-ap/3.2.0/cpsv-ap-SHACL.ttl`. It contains 32 `sh:NodeShape` definitions (pure SHACL Core — no SPARQL constraints) targeting the full CPSV-AP model:

`cpsv:PublicService`, `cpsv:Rule`, `m8g:PublicOrganisation`, `m8g:ContactPoint`, `m8g:Channel`, `m8g:Cost`, `m8g:Evidence`, `m8g:Requirement`, `m8g:Output`, `locn:Address`, `dcat:Dataset`, `foaf:Agent`, `org:Organization`, `skos:Concept`, and related classes.

The constraints most relevant to RONL publishing:

| Class | Constraint | Code |
|---|---|---|
| `cpsv:Rule` | `dct:identifier` is required (`sh:minCount 1`) | `SHACL-MINCOUNT` |
| `cpsv:Rule` | `dct:title` / `dct:description` must be `rdf:langString` | `SHACL-DATATYPE` |
| `m8g:PublicOrganisation` | `dct:spatial` is required (`sh:minCount 1`) | `SHACL-MINCOUNT` |

!!! note
    The CPSV-AP `Rule` shape constrains `dct:title` / `dct:description` only by datatype — it does **not** cap their cardinality. The single-value-per-language rule is supplied by the RONL Custom layer, so the two layers complement rather than duplicate each other.

---

## Layer 2 — RONL Custom

RONL-authored shapes in `packages/backend/shapes/ronl/`, layered on top of CPSV-AP. They encode publishing invariants that are stricter than (or orthogonal to) the canonical profile, chosen specifically to prevent merge-time fan-out and subject-URI collisions in TriplyDB.

These shapes prefer `sh:uniqueLang true` over `sh:maxCount 1` for human-readable labels, so a record carrying one `@nl` and one `@en` value passes, while two values sharing a language tag are flagged.

---

### PublicOrganisationUniquenessShape

**Target:** `m8g:PublicOrganisation`

| Path | Constraint | Code |
|---|---|---|
| `foaf:homepage` | `sh:maxCount 1` | `SHACL-MAXCOUNT` |
| `dct:identifier` | `sh:maxCount 1` | `SHACL-MAXCOUNT` |
| `cv:spatial` | `sh:maxCount 1` | `SHACL-MAXCOUNT` |
| `skos:prefLabel` | `sh:uniqueLang true` | `SHACL-UNIQUELANG` |

**Rationale.** When two publications describe the same organisation with divergent single-valued properties (most commonly `foaf:homepage`), the union in TriplyDB produces multiple values on one subject, which fan out into duplicate rows in downstream queries. Capping these at one surfaces the divergence at validation time — especially in merge-simulated mode, where the conflicting value lives in the already-published graph rather than the uploaded file.

---

### RuleUniquenessShape

**Target:** `cpsv:Rule`

| Path | Constraint | Code |
|---|---|---|
| `dct:title` | `sh:uniqueLang true` | `SHACL-UNIQUELANG` |
| `dct:description` | `sh:uniqueLang true` | `SHACL-UNIQUELANG` |

**Rationale.** Publishing several distinct rules under one subject URI is a common authoring error: the subject accumulates several same-language titles and descriptions. `sh:uniqueLang` detects this while still allowing a single rule to carry one title/description per language. The fix is to give each rule its own subject URI.

---

## Constraint codes

Codes are generic — any SHACL Core constraint component can appear, named `SHACL-<COMPONENT>`. The ones the RONL data exercises in practice:

### SHACL-MINCOUNT

| | |
|---|---|
| **Severity** | 🔴 error |
| **Trigger** | A focus node has fewer values for a path than `sh:minCount` requires |
| **Rationale** | A required property is absent. For `cpsv:Rule` this is almost always a missing `dct:identifier`; for `m8g:PublicOrganisation` it can be a missing `dct:spatial`. |
| **Fix** | Add the missing property to the subject in your Turtle. |

### SHACL-MAXCOUNT

| | |
|---|---|
| **Severity** | 🔴 error |
| **Trigger** | A focus node has more values for a path than `sh:maxCount` permits |
| **Rationale** | A property that must be single-valued for RONL publishing has several values. In merge-simulated mode this usually means your value differs from the one already published. |
| **Fix** | Reconcile the values so only one remains — either in your file, or by correcting the published record. |

### SHACL-UNIQUELANG

| | |
|---|---|
| **Severity** | 🔴 error |
| **Trigger** | Two or more values of a path share the same language tag while `sh:uniqueLang true` is set |
| **Rationale** | Typically several `cpsv:Rule` blocks were published under one subject URI, so the subject carries multiple same-language titles/descriptions. |
| **Fix** | Give each rule its own subject URI so each carries at most one title and description per language. |

---

## Severity summary by component

| Code | Layer(s) | Severity |
|---|---|---|
| `SHACL-MINCOUNT` | CPSV-AP 3.2.0 | error |
| `SHACL-MAXCOUNT` | RONL Custom | error |
| `SHACL-UNIQUELANG` | RONL Custom, CPSV-AP 3.2.0 | error |
| `SHACL-DATATYPE` | CPSV-AP 3.2.0 | error |

---

## Known divergence — `dct:spatial` vs `cv:spatial`

The canonical CPSV-AP 3.2.0 `PublicOrganisation` shape requires `dct:spatial` (`http://purl.org/dc/terms/spatial`), while RONL data — and the RONL `PublicOrganisationUniquenessShape` — use `cv:spatial` (`http://data.europa.eu/m8g/spatial`). As a result the CPSV-AP layer reports a `SHACL-MINCOUNT` on `dct:spatial` for RONL organisations.

This is **not a validator defect** — it is the validator correctly surfacing a modelling difference between the RONL profile and the canonical profile. The decision on whether to align RONL to `dct:spatial` or accept the divergence is deferred to a dedicated data-modelling pass.

---

## API contract

Both endpoints accept a JSON body and return the standard envelope.

**Request:**

```json
{ "content": "<turtle>", "endpoint": "https://…/sparql" }
```

`endpoint` applies to `validate-merged` only and is optional (the configured default is used when omitted).

**Response:**

```json
{
  "success": true,
  "data": {
    "valid": false,
    "parseError": null,
    "layers": {
      "cpsv-ap":     { "label": "CPSV-AP 3.2.0", "loaded": true, "issues": [ ... ] },
      "ronl-custom": { "label": "RONL Custom",   "loaded": true, "issues": [ ... ] }
    },
    "summary": { "errors": 2, "warnings": 0, "infos": 0 }
  },
  "timestamp": "2026-06-05T00:00:00.000Z"
}
```

Each issue has the shape `{ severity, code, message, location? }`, where `location` is the focus node and property path. A layer with `loaded: false` had no shape files present and was not evaluated.
