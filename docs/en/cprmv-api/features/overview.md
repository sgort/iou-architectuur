# Features Overview

The CPRMV API delivers the following core capabilities, derived directly from the `serve_api/src/serve.py` implementation and the `data/cprmvmethods.ttl` methods registry.

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

Four official publication sources are supported, each with its own XSLT transform and ID format logic:

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

The `unformat` query parameter accepts a [`parse`](https://pypi.org/project/parse/) pattern string to extract structured values from a rule's `cprmv:definition` literal. The parsed named fields are added as triples on the rule and merged into the response. As of v0.4.1 this works with **any** output format (not only `cprmv-json`):

```
unformat={situatie:param_value}: € {norm:param_value}
```

This enables structured extraction of domain values (e.g. income limits, thresholds) directly from natural-language rule definitions without additional post-processing.

---

## Reference resolution

The `/ref` endpoint accepts a single `reference` query parameter, **auto-detects** the reference method, and redirects to the corresponding CPRMV API path or source (v0.4.1 — the earlier `/ref/{referencemethod}/{reference}` path form is gone):

- **Juriconnect** (`jci1.3` and `jci1.31`) — maps BWB identifiers and locatie-strings to `/rules/` paths. Supported locatie types: `artikel`, `hoofdstuk`, `paragraaf`, `onderdeel`, `lid`. Sighting date is accepted in the URI but ignored (defaults to today).
- **ELI → Formex 4 on EU CELLAR** — queries CELLAR and redirects to the matching item (defaults to language `NLD`, format `fmx4`).
- **ELI for BWB / CVDR** (experimental) — accepts a forward-slash-delimited path after the base URI and maps it to a `/rules/` path.
- **CPRMV API rule id path** — a `/rules/` URL is accepted and re-issued on this instance.

See [Reference Resolution](reference-resolution.md) for details and examples.

---

## MCP server

The API is also exposed as a basic **Model Context Protocol** server (mounted at `/mcp` via `fastapi-mcp`, v0.4.1), so MCP-capable clients can invoke its endpoints as tools.

---

## CPRMV Specification hosting

The API serves the CPRMV specification in ReSpec format as static files under `/respec/`. This makes the canonical specification directly co-located with the API that implements it:

- [acc.cprmv.open-regels.nl/respec/](https://acc.cprmv.open-regels.nl/respec/) — acceptance environment
