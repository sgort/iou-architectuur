# Reference Resolution

The `/ref/{referencemethod}/{reference}` endpoint accepts external legal reference URIs and resolves them to a CPRMV API `/rules/` path, returning an HTTP redirect.

This allows other systems that produce Juriconnect or ELI references to pass them directly to the CPRMV API without needing to understand the internal ID format.

---

## Juriconnect

Both `jci1.3` and `jci1.31` versions are supported. The `referencemethod` path segment should be `Juriconnect` (case-insensitive handling is not guaranteed — use as shown).

**Supported locatie types:** `artikel`, `hoofdstuk`, `paragraaf`, `onderdeel`, `lid`.

**Example reference:**

```
jci1.3:c:BWBR0015703&hoofdstuk=3&paragraaf=3.2&artikel=20&z=2025-07-01&g=2025-07-01
```

The `z` (gezien-op / sighting date) parameter is accepted but currently ignored. The `g` (geldig-op / valid-on date) parameter is used to resolve the correct publication version.

The API constructs a redirect to:

```
/rules/BWBR0015703_{date}_latest/hoofdstuk%203%2Cparagraaf%203.2%2CArtikel%2020
```

**Limitations:**

- Only single-consolidation references are supported; multi-consolidation (`mconsolidatie`) is not.
- The full set of locatie types supported by the Juriconnect standard may not all be implemented in the BWB XSLT transform.
- BWB ID must be exactly 8 characters (`BWBRxxxxxxx`).

---

## ELI

The ELI reference method is registered in the methods KG (`cprmvmethods:referencemethods`) but the transform function (`transform_eli_reference`) returns `None` — not yet implemented.

---

## Reference method configuration

The supported reference methods and their parameter mappings are defined in `data/cprmvmethods.ttl` under the `cprmvmethods:referencemethods` RDF list. Each method entry carries:

- `cprmv-serve:reference-mapping-valid-on` — the query parameter name that carries the valid-on date in the external reference format.
- `cprmv-serve:reference-mapping-seen-on` — the query parameter name for the sighting date.
- Additional key-value mappings that translate external locatie-string keys to CPRMV rule ID path segment labels.
