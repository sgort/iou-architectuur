---
component: CPRMV
---

# Reference Resolution

The `/ref` endpoint accepts an external reference in its single `reference` query parameter, **auto-detects** which reference method it is, and resolves it — redirecting either to a CPRMV API `/rules/` path or to an external source.

This allows other systems that produce Juriconnect, ELI, or CPRMV-API references to pass them directly without needing to understand the internal ID format.

!!! note "How detection works"
    The endpoint takes no method in its path: the call is simply `GET /ref?reference=…`.
    The reference methods acknowledged in `cprmvmethods:referencemethods` are tried in order —
    `cprmvapi`, `juriconnect`, `elifmx4`, `elinl` — and the first whose method module returns a
    target wins. Each is a class in `serve_api/methods/` (`cprmvapi.py`, `juriconnect.py`, and
    `eli.py` for both ELI methods). A successful match answers with a `307 Temporary Redirect`.

---

## Juriconnect

Both `jci1.3` and `jci1.31` versions are supported. The reference format is `jci1.{subversion}:c:BWB{bwbid}&{locatie-string}`.

**Supported locatie types:** the locatie-string keys are mapped to rule identifiers by `cprmv-serve:reference-mapping` (for example `artikel` → `Artikel`, `o` → `onderdeel`, `lid` → `lid`, `hoofdstuk` → `Hoofdstuk`, `paragraaf` → `Paragraaf`). Whether a mapped rule can be found depends on the BWB XSLT transform; the endpoint description names `artikel`, `hoofdstuk`, `paragraaf`, `onderdeel` and `lid` as supported.

**Example reference:**

```
GET /ref?reference=jci1.31:c:BWBR0015703&artikel=20&o=a.
```

redirects to `/rules/BWBR0015703_{today}_latest%2CArtikel%2020%2Conderdeel%20a.`.

The valid-on date (`g` / geldig-op) becomes the date of the rule set id and the version valid on that date is looked up; when absent the date defaults to today, with index `latest`.

The sighting date (`z` / gezien-op) is not ignored: its value is placed in the **version-index** position of the rule set id instead of `latest`. `…&g=2025-07-01&z=2025-07-01&artikel=20` therefore resolves to `BWBR0015703_2025-07-01_2025-07-01`, which skips the SRU lookup. Whether this is intended is asked in [standards/cprmv#31](https://git.open-regels.nl/standards/cprmv/-/work_items/31).

**Limitations:**

- Only single-consolidation references are supported; multi-consolidation (`mconsolidatie`) is not.
- The full set of locatie types supported by the Juriconnect standard may not all be implemented in the BWB XSLT transform.
- The part of the BWB id after `BWB` must be exactly 8 characters — `BWBR0015703` (`R0015703`) qualifies; the module upper-cases it.
- A malformed Juriconnect reference (a wrong version, a too-short BWB id, or a locatie-string part without `=`) is not recognised by the module and falls through to the ELI → CELLAR method, whose query fails on it: the endpoint answers `500 Internal Server Error`.

---

## ELI → Formex 4 on EU CELLAR

Implemented by `elifmx4.transform_reference` in `eli.py`. The method queries the EU CELLAR SPARQL endpoint for the manifestation item matching the ELI work and redirects to the first item found. Language and format are fixed to `NLD` and `fmx4`.

**Example:**

```
GET /ref?reference=http://data.europa.eu/eli/reg/2018/1805/oj
```

redirects to `http://publications.europa.eu/resource/cellar/83e4752e-f2e5-11e8-9982-01aa75ed71a1.0017.02/DOC_1`.

Because this method queries CELLAR for any reference that reaches it, every reference not handled by `cprmvapi` or `juriconnect` costs a CELLAR round trip before `elinl` is tried.

See also the [`/cellar-by-eli`](../reference/api-endpoints.md) endpoint for explicit language/format control.

---

## ELI for BWB and CVDR (experimental)

A forward-slash-delimited path after `https://wetten.overheid.nl/` is mapped to a CPRMV API `/rules/` path (method `elinl`, reference format `https://wetten.overheid.nl/{path}`).

**Example:**

```
GET /ref?reference=https://wetten.overheid.nl/BWBR0015703/Artikel%2020/onderdeel%20a.
```

---

## CPRMV API rule id path

A `/rules/` URL (on this or another CPRMV API instance) is accepted and re-issued against this instance (method `cprmvapi`, reference format `{baseuri}/rules/{path}`); slashes in the path become comma separators.

**Example:**

```
GET /ref?reference=https://cprmv.open-regels.nl/rules/BWBR0015703/Artikel%2020/onderdeel%20a.
```

---

## Reference method configuration

The supported reference methods are acknowledged in the `cprmvmethods:referencemethods` list in `data/cprmvmethods.ttl`. Each method node carries its own configuration:

- `cprmv-serve:reference-format` — the `parse` pattern the reference must match.
- `cprmv-serve:reference-mapping` (Juriconnect) — a list of key–value pairs that translate locatie-string keys to CPRMV rule ID path segment labels, plus two special entries:
    - `cprmv-serve:reference-mapping-valid-on` — the locatie-string key that carries the valid-on date (`g`).
    - `cprmv-serve:reference-mapping-seen-on` — the locatie-string key for the sighting date (`z`).

`cprmv-serve:` is the namespace `https://cprmv.open-regels.nl/0.4.2/serve-api/`.

If no method matches, the endpoint returns `{"error": "not a valid or supported reference..."}`.
