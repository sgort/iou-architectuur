---
component: CPRMV
---

# Features Overview

The CPRMV API delivers the following core capabilities, derived from `serve_api/src/serve.py`, the method modules in `serve_api/methods/`, and the methods registry in `serve_api/data/cprmvmethods.ttl`.

---

## On-the-fly rule retrieval

Rules are resolved and fetched live from official publication repositories — nothing is pre-loaded or cached between requests. When a request arrives:

1. Each acknowledged publication method in turn tries to parse the rule set identifier against its `cprmv-serve:normalized-id-format`; the first match wins (BWB, CVDR, EU CELLAR, Operaton DMN 1.3, IOU Norms, ROO, DSO).
2. For a `latest` request on BWB or CVDR, the method looks up the version valid on the requested date through the repository's SRU service.
3. The publication URL is built from the method's `cprmv-serve:repository-publication-location-format` and the publication is downloaded via HTTPS — for the DSO with the caller's own key, passed on from the `x-api-key` header.
4. An XSLT stylesheet (XML sources) or the JSON method (`core_json`, for ROO and IOU Norms) transforms it to CPRMV.
5. rdflib navigates the resulting RDF graph to the requested rule.

This means the API always serves the authoritative source — no synchronisation or stale data.

---

## Multi-repository support

Ten publication methods can be fetched, each with its own ID format and an XSLT transform or the JSON method:

| Repository | Method id | Scope | Identifier prefix |
|---|---|---|---|
| **BWB** | `repository-overheid-nl-bwb` | Dutch national law (Basiswettenbestand) | `BWBR…` |
| **CVDR** | `repository-overheid-nl-cvdr` | Dutch municipal, provincial and water-board regulations | `CVDR…` |
| **EU CELLAR** | `eucellar-fmx4` | European Union legislation (Formex v4) | `CFMX4…` |
| **Operaton DMN 1.3** | `operaton.open-regels.nl` | DMN decision models deployed on operaton.open-regels.nl (experimental) | `DMN1.3_…` |
| **IOU Norms** | `norms-backend.linkeddata.open-regels.nl` | Norms from the IOU Norms API of the Linked Data Explorer | `IOU-NORMS_…` |
| **ROO** | `roo`, `roo-uri`, `roo-catalogus` | Public organisations from the Register van Overheidsorganisaties: by key, by TOOI URI, or the whole register | `ROO.…`, `ROOURI…`, `ROO_…` |
| **DSO** | `dso`, `dso-service-register` | STTR decision models from the Digitaal Stelsel Omgevingswet, and the DSO as a register of their services; needs your DSO key | `DSO_…`, `DSOService_…` |

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

## Raw publication download

`/raw/{rule_id_path}` returns the original publication a rule set is read from, untransformed, as a file. The RuleSet itself does not name its source with `prov:wasDerivedFrom`; `/raw` is how to get it. See [API Endpoints](../reference/api-endpoints.md#get-rawrule_id_path).

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

`serve.py` turns the API's routes into a **Model Context Protocol** server with FastMCP (`FastMCP.from_fastapi`) and mounts it on the API at `/mcp/`. It answers on production and acceptance (checked 24 November 2026). Use the address with the trailing slash: `/mcp` is redirected to an `http://` URL ([open-regels/cprmv#2](https://github.com/open-regels/cprmv/issues/2)).

---

## CPRMV Specification hosting

The API serves the CPRMV specification in ReSpec format as static files under `/respec/`, one folder per version (`/respec/0.4.0/` … `/respec/0.4.3/`). On the live hosts, `/respec/` itself opens the 0.4.3 specification. This makes the canonical specification directly co-located with the API that implements it:

- [cprmv.open-regels.nl/respec/](https://cprmv.open-regels.nl/respec/) — production
- [acc.cprmv.open-regels.nl/respec/](https://acc.cprmv.open-regels.nl/respec/) — acceptance
