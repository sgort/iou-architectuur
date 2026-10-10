---
component: CPRMV
---

# Features Overview

The CPRMV API delivers the following core capabilities, derived from `serve_api/src/serve.py`, the method modules in `serve_api/methods/`, and the methods registry in `serve_api/data/cprmvmethods.ttl`.

---

## On-the-fly rule retrieval

Rules are resolved and fetched live from official publication repositories — nothing is pre-loaded or cached between requests. When a request arrives:

1. Each acknowledged publication method in turn tries to parse the rule set identifier against its `cprmv-serve:normalized-id-format`; the first match wins (BWB, CVDR, EU CELLAR, Operaton DMN 1.3).
2. For a `latest` request on BWB or CVDR, the method looks up the version valid on the requested date through the repository's SRU service.
3. The publication URL is built from the method's `cprmv-serve:repository-publication-location-format` and the publication is downloaded via HTTPS.
4. The method's XSLT stylesheet transforms it to CPRMV Turtle.
5. rdflib navigates the resulting RDF graph to the requested rule.

This means the API always serves the authoritative source — no synchronisation or stale data.

---

## Multi-repository support

Four publication methods are acknowledged, each a method module with its own XSLT transform and ID format:

| Repository | Method id | Scope | Identifier prefix |
|---|---|---|---|
| **BWB** | `repository-overheid-nl-bwb` | Dutch national law (Basiswettenbestand) | `BWBR…` |
| **CVDR** | `repository-overheid-nl-cvdr` | Dutch municipal, provincial and water-board regulations | `CVDR…` |
| **EU CELLAR** | `eucellar-fmx4` | European Union legislation (Formex v4) | `CFMX4…` |
| **Operaton DMN 1.3** | `operaton.open-regels.nl` | DMN decision models deployed on operaton.open-regels.nl (experimental) | `DMN1.3_…` |

For BWB and CVDR, "latest version valid on a given date" queries are resolved automatically through SRU search of the repository, so callers do not need to know the exact publication index. See [Publication Repositories](publication-repositories.md).

---

## Rule path navigation

Rules within a publication are hierarchically structured (hoofdstuk → paragraaf → artikel → lid → onderdeel). The `/rules/{rule_id_path}` endpoint accepts a comma-separated path of identifiers to navigate directly to any level:

```
BWBR0015703_2025-07-01_0, Artikel 20, lid 1, onderdeel a.
```

The path traversal is **depth-first** and **alphanumeric-only** (all non-alphanumeric characters including whitespace are stripped before matching), so `"onderdeel a."` and `"onderdeel a"` resolve identically. Intermediate identifiers can be omitted when there is no ambiguity.

The response is always the `cprmv:RuleSet`, with the selected rule (and everything it contains) as its only `cprmv:hasPart`.

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

The `cprmv-json` format produces a nested dictionary representation of the rule set and the selected sub-rules, with predicate URIs as keys — designed for readability and direct use in downstream processing. An unrecognised `format` value falls back to `cprmv-json`.

---

## Definition extraction with `unformat`

The `unformat` query parameter accepts a [`parse`](https://pypi.org/project/parse/) pattern string to extract structured values from the selected rule's `cprmv:definition` literal. The parsed named fields are added as triples on the rule, so they appear in every output format:

```
unformat={situatie:param_value}: € {norm:param_value}
```

This enables structured extraction of domain values (e.g. income limits, thresholds) directly from natural-language rule definitions without additional post-processing. See [Definition Extraction](../user-guide/definition-extraction.md).

---

## Reference resolution

The `/ref` endpoint accepts a single `reference` query parameter, **auto-detects** the reference method, and redirects to the corresponding CPRMV API path or source. The acknowledged reference methods are tried in this order:

- **CPRMV API rule id path** (`cprmvapi`) — a `/rules/` URL is accepted and re-issued on this instance.
- **Juriconnect** (`juriconnect`, `jci1.3` and `jci1.31`) — maps BWB identifiers and locatie-strings to `/rules/` paths. A valid-on date (`g`) selects the version; without it the version valid today is used.
- **ELI → Formex 4 on EU CELLAR** (`elifmx4`) — queries CELLAR and redirects to the matching item (language `NLD`, format `fmx4`).
- **ELI for BWB / CVDR** (`elinl`, experimental) — accepts a forward-slash-delimited path after `https://wetten.overheid.nl/` and maps it to a `/rules/` path.

See [Reference Resolution](reference-resolution.md) for details and examples.

---

## MCP server

`serve.py` wires the API into a **Model Context Protocol** server with FastMCP (`FastMCP.from_fastapi`), mounted at `/mcp` on a combined application. In the current deployment `/mcp` is **not reachable** — it returns `404` on production and acceptance. The MCP server is built before the API routes are registered, and the container serves the plain FastAPI `app` rather than the combined one. This is reported in [standards/cprmv#31](https://git.open-regels.nl/standards/cprmv/-/work_items/31).

---

## CPRMV Specification hosting

The API serves the CPRMV specification in ReSpec format as static files under `/respec/`, one folder per version (`/respec/0.4.0/`, `/respec/0.4.1/`, `/respec/0.4.2/`). On the live hosts, `/respec/` itself opens the 0.4.2 specification. This makes the canonical specification directly co-located with the API that implements it:

- [cprmv.open-regels.nl/respec/](https://cprmv.open-regels.nl/respec/) — production
- [acc.cprmv.open-regels.nl/respec/](https://acc.cprmv.open-regels.nl/respec/) — acceptance
