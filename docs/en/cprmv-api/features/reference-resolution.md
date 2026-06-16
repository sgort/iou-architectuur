# Reference Resolution

The `/ref` endpoint accepts an external reference in its single `reference` query parameter, **auto-detects** which reference method it is, and resolves it — redirecting either to a CPRMV API `/rules/` path or to an external source.

This allows other systems that produce Juriconnect, ELI, or CPRMV-API references to pass them directly without needing to understand the internal ID format.

!!! note "Signature change in v0.4.1"
    Up to v0.4.0 the endpoint took the method in the path: `/ref/{referencemethod}/{reference}`.
    As of v0.4.1 the method is auto-detected and the call is simply `GET /ref?reference=…`.
    Each reference is matched against the `reference-format` patterns in the
    `cprmvmethods:referencemethods` registry.

---

## Juriconnect

Both `jci1.3` and `jci1.31` versions are supported.

**Supported locatie types:** `artikel`, `hoofdstuk`, `paragraaf`, `onderdeel`, `lid`.

**Example reference:**

```
GET /ref?reference=jci1.31:c:BWBR0015703&artikel=20&o=a.
```

The sighting date (`z` / gezien-op) is accepted in the URL but currently ignored (defaults to today). The valid-on date (`g` / geldig-op) is used to resolve the correct publication version; when absent it defaults to today and `latest`.

**Limitations:**

- Only single-consolidation references are supported; multi-consolidation (`mconsolidatie`) is not.
- The full set of locatie types supported by the Juriconnect standard may not all be implemented in the BWB XSLT transform.
- BWB ID must be exactly 8 characters (`BWBRxxxxxxx`).
- Invalid arguments in a Juriconnect reference no longer cause an internal server error (fixed in v0.4.1).

---

## ELI → Formex 4 on EU CELLAR

Implemented in v0.4.1 (`transform_eli_reference`). The endpoint queries the EU CELLAR SPARQL endpoint for the manifestation item matching the ELI work and redirects to it. Language and format default to `NLD` and `fmx4`.

**Example:**

```
GET /ref?reference=http://data.europa.eu/eli/reg/2018/1805/oj
```

See also the [`/cellar-by-eli`](../reference/api-endpoints.md) endpoint for explicit language/format control.

---

## ELI for BWB and CVDR (experimental)

A forward-slash-delimited path appended to a BWB/CVDR base URI is mapped to a CPRMV API `/rules/` path.

**Example:**

```
GET /ref?reference=https://wetten.overheid.nl/BWBR0015703/Artikel%2020/onderdeel%20a.
```

---

## CPRMV API rule id path

A `/rules/` URL (on this or another CPRMV API instance) is accepted and re-issued against this instance.

**Example:**

```
GET /ref?reference=https://cprmv.open-regels.nl/rules/BWBR0015703/Artikel%2020/onderdeel%20a.
```

---

## Reference method configuration

The supported reference methods and their parameter mappings are defined in `data/cprmvmethods.ttl` under the `cprmvmethods:referencemethods` RDF list. Each method entry carries:

- `cprmv-serve:reference-mapping-valid-on` — the query parameter name that carries the valid-on date in the external reference format.
- `cprmv-serve:reference-mapping-seen-on` — the query parameter name for the sighting date.
- Additional key-value mappings that translate external locatie-string keys to CPRMV rule ID path segment labels.
