---
component: CPRMV
---

# API Endpoints

Interactive documentation is available at the live environments:

- **Production:** [https://cprmv.open-regels.nl/docs](https://cprmv.open-regels.nl/docs) (also [https://cprmv.open-rules.eu/docs](https://cprmv.open-rules.eu/docs))
- **Acceptance:** [https://acc.cprmv.open-regels.nl/docs](https://acc.cprmv.open-regels.nl/docs)

Responses from `/methods` and `/rules` are plain text (`text/plain; charset=utf-8`) whatever the requested serialisation. Errors are reported in the body with HTTP status `200`, except where noted.

---

## GET /

Returns the API title and version.

**Response:**

```json
{"CPRMV Rules Serve API": "0.4.2"}
```

---

## GET /methods

Returns the Methods Knowledge Graph, loaded at start-up from `data/cprmvmethods.ttl` and `data/cprmv.ttl`.

**Query parameters:**

| Parameter | Type | Default | Values |
|---|---|---|---|
| `format` | string | `json-ld` | `json-ld`, `xml`, `turtle`, `ttl`, `n3`, `turtle2` |

**Response:** Plain text in the requested RDF serialisation; `null` for any other `format` value.

The graph lists the acknowledged methods per category (`cprmvmethods:rulemethods`, `publicationmethods`, `referencemethods`, `analysismethods`, `formalisationmethods`, `serialisationmethods`, `executionmethods`, …) and each method's definition. It reflects the committed `data/cprmvmethods.ttl`, which lags behind `rdf/0.4.2/methods/` ([standards/cprmv#31](https://git.open-regels.nl/standards/cprmv/-/work_items/31)).

---

## GET /rules/{rule_id_path}

Retrieves a rule or rule set from an official publication repository.

**Path parameters:**

| Parameter | Type | Constraints |
|---|---|---|
| `rule_id_path` | string | 10–500 characters. Format: `{RuleSetId}[, {RuleId1}[, {RuleId2}...]]` |

**Query parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `path_delimiter` | string | `,` | Delimiter between identifiers in `rule_id_path` |
| `format` | string | `cprmv-json` | Output format: `cprmv-json`, `json-ld`, `xml`, `turtle`, `ttl`, `n3`, `turtle2`. Other values fall back to `cprmv-json`. |
| `_language` | string | `null` | Described as the output language (`nl` only); the value is not used. |
| `unformat` | string | `""` | `parse` pattern for structured extraction from `cprmv:definition`. Works with **any** `format` — the extracted values are added as triples on the rule. |

**Response:** Plain text in the requested format. The endpoint always returns a `cprmv:RuleSet` with at least the selected `cprmv:Rule` as its `cprmv:hasPart` — even when a specific sub-rule is requested — so RuleSet-level properties (method, validity, provenance) always travel with the rule. The output (and JSON dumps) are UTF-8 encoded.

**Error responses:**

```json
{"error": "No supported publication repository use identifiers with the format of the given Ruleset Id."}
```

when no publication method recognises the Rule Set ID, and the text `No rules found for given path...` when the rule set is found but the path matches no rule.

**Supported Rule Set ID formats:** See [ID Formats](id-formats.md). Besides BWB, CVDR and EU CELLAR, DMN 1.3 decision models deployed on `operaton.open-regels.nl` can be retrieved.

---

## GET /ref

Resolves an external legal reference to a CPRMV API path and returns an HTTP redirect. The reference **method is auto-detected** — there is no `referencemethod` path segment.

**Query parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `reference` | string | `""` | The reference, in any supported format (auto-detected) |

**Supported reference formats:**

| Type | Example | Resolves to |
|---|---|---|
| CPRMV API rule id path | `https://cprmv.open-regels.nl/rules/BWBR0015703/Artikel%2020/onderdeel%20a.` | a `/rules/` path |
| Juriconnect (`jci1.3` / `jci1.31`) | `jci1.31:c:BWBR0015703&artikel=20&o=a.` | a `/rules/` path |
| ELI → Formex 4 on EU CELLAR | `http://data.europa.eu/eli/reg/2018/1805/oj` | the EU CELLAR item (language `NLD`, format `fmx4`) |
| ELI for BWB / CVDR (experimental) | `https://wetten.overheid.nl/BWBR0015703/Artikel%2020/onderdeel%20a.` | a `/rules/` path |

**Response:** `307 Temporary Redirect`, or `{"error": "not a valid or supported reference..."}` if no method resolves the reference. A malformed Juriconnect reference currently fails with `500 Internal Server Error` (see [Reference Resolution](../features/reference-resolution.md#juriconnect)).

**Supported reference types:** See [Reference Resolution](../features/reference-resolution.md).

---

## GET /cellar-by-celex/{celexid}

Redirects to the EU CELLAR SPARQL endpoint running a query that finds the manifestation items for a given CELEX id.

**Path / query parameters:**

| Parameter | In | Default | Description |
|---|---|---|---|
| `celexid` | path | `32018R1805` | CELEX identifier of the work |
| `language` | query | `NLD` | Language code |
| `format` | query | `fmx4` | Manifestation format |

**Response:** `307 Temporary Redirect` to the CELLAR SPARQL results.

---

## GET /cellar-by-eli/{elipath}/{language}/{format}

Works like `/cellar-by-celex` but accepts an ELI reference (matched against the EU CELLAR knowledge graph). Only ELI references explicitly linked to CELLAR documents resolve (partial ELIs do not). The language is upper-cased and the format lower-cased before the query is built.

**Example:** `/cellar-by-eli/http://data.europa.eu/eli/reg/2018/1805/oj/NLD/fmx4`

**Response:** `307 Temporary Redirect` to the CELLAR SPARQL results.

!!! note
    For both `/cellar-by-*` endpoints, a CORS limitation in Swagger UI can make the
    redirect surface as `TypeError: Load failed`. Open the request URL directly to see
    the actual CELLAR response.

---

## /mcp

`serve.py` builds a **Model Context Protocol** server with FastMCP (`FastMCP.from_fastapi(app=app, name="CPRMV")`) and mounts it at `/mcp` on a combined application (`combined_app`). In the current deployment `/mcp` returns `404`: the MCP server is created before the API routes are registered, so it would expose no tools, and the container runs `fastapi run src/serve.py`, which serves `app` rather than `combined_app`. See [standards/cprmv#31](https://git.open-regels.nl/standards/cprmv/-/work_items/31).

---

## Static: /respec/

Serves the CPRMV specification as a static ReSpec HTML site, with one folder per version (`/respec/0.4.0/`, `/respec/0.4.1/`, `/respec/0.4.2/`). Navigate to `/respec/` in a browser.
