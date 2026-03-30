# Features Overview

The CPRMV API delivers five core capabilities derived directly from the `serve_api/src/serve.py` implementation and the `data/cprmvmethods.ttl` methods registry.

---

## On-the-fly rule retrieval

Rules are resolved and fetched live from official publication repositories — nothing is pre-loaded or cached between requests. When a request arrives:

1. The rule set identifier is parsed to detect which publication method applies (BWB, CVDR, CELLAR, or DMN 1.3).
2. The publication URL is constructed using the format templates in `cprmvmethods.ttl`.
3. The XML publication is downloaded via HTTPS.
4. An XSLT stylesheet transforms it to CPRMV Turtle.
5. rdflib navigates the resulting RDF graph to the requested rule.

This means the API always serves the authoritative source — no synchronisation or stale data.

---

## Multi-repository support

Three official publication repositories are supported, each with its own XSLT transform and ID format logic:

| Repository | Scope | Identifier prefix |
|---|---|---|
| **BWB** | Dutch national law (Basis Wettenbestand) | `BWBR…` |
| **CVDR** | Dutch municipal and provincial regulations | `CVDR…` |
| **EU CELLAR** | European Union legislation (Formex v4) | `CFMX4…` |
| **Operaton DMN 1.3** | Deployed DMN decision models (experimental) | `DMN1.3_…` |

For BWB and CVDR, "latest version valid on a given date" queries are resolved automatically through SRU search of the repository, so callers do not need to know the exact publication index.

---

## Rule path navigation

Rules within a publication are hierarchically structured (hoofdstuk → paragraaf → artikel → lid → onderdeel). The `/rules/{rule_id_path}` endpoint accepts a comma-separated path of identifiers to navigate directly to any level:

```
BWBR0015703_2025-07-01_0, Artikel 20, lid 1, onderdeel a.
```

The path traversal is **depth-first** and **alphanumeric-only** (all non-alphanumeric characters including whitespace are stripped before matching), so `"onderdeel a."` and `"onderdeel a"` resolve identically. Intermediate identifiers can be omitted when there is no ambiguity.

---

## Multiple output formats

Every response can be serialised in seven formats via the `format` query parameter:

| Format | Description |
|---|---|
| `cprmv-json` *(default)* | Custom JSON with recursive rule tree — human-readable |
| `json-ld` | JSON-LD RDF serialisation |
| `turtle` / `ttl` | Turtle RDF serialisation |
| `turtle2` | Turtle RDF (alternative serialiser) |
| `n3` | N3 RDF serialisation |
| `xml` | RDF/XML serialisation |

The `cprmv-json` format produces a nested dictionary representation of the rule and all its contained sub-rules, with predicate URIs as keys — designed for readability and direct use in downstream processing.

---

## Definition extraction with `unformat`

The `unformat` query parameter accepts a [`parse`](https://pypi.org/project/parse/) pattern string to extract structured values from a rule's `cprmv:definition` literal. When supplied, the format is forced to `cprmv-json` and the parsed named fields are merged into the response alongside the full rule data:

```
unformat={situatie:param_value}: € {norm:param_value}
```

This enables structured extraction of domain values (e.g. income limits, thresholds) directly from natural-language rule definitions without additional post-processing.

---

## Reference resolution

The `/ref/{referencemethod}/{reference}` endpoint accepts external legal reference URIs and redirects to the corresponding CPRMV API path:

- **Juriconnect** (`jci1.3` and `jci1.31`) — maps BWB identifiers and locatie-strings to `/rules/` paths. Supported locatie types: `artikel`, `hoofdstuk`, `paragraaf`, `onderdeel`, `lid`. Sighting date is accepted in the URI but ignored (defaults to today).
- **ELI** — defined in the methods registry; not yet implemented.

---

## CPRMV Specification hosting

The API serves the CPRMV specification in ReSpec format as static files under `/respec/`. This makes the canonical specification directly co-located with the API that implements it:

- [acc.cprmv.open-regels.nl/respec/](https://acc.cprmv.open-regels.nl/respec/) — acceptance environment
