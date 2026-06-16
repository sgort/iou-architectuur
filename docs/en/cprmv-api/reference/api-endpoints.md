# API Endpoints

Interactive documentation is available at the live environments:

- **Production:** [https://cprmv.open-regels.nl/docs](https://cprmv.open-regels.nl/docs)
- **Acceptance:** [https://acc.cprmv.open-regels.nl/docs](https://acc.cprmv.open-regels.nl/docs)

---

## GET /

Returns the API title and version.

**Response:**

```json
{"CPRMV Rules Serve API": "0.4.1"}
```

---

## GET /methods

Returns the Methods Knowledge Graph (cprmvmethods.ttl + cprmv.ttl merged).

**Query parameters:**

| Parameter | Type | Default | Values |
|---|---|---|---|
| `format` | string | `json-ld` | `json-ld`, `xml`, `turtle`, `ttl`, `n3`, `turtle2` |

**Response:** Plain text in the requested RDF serialisation.

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
| `format` | string | `cprmv-json` | Output format: `cprmv-json`, `json-ld`, `xml`, `turtle`, `ttl`, `n3`, `turtle2` |
| `language` | string | `null` | Language for output (currently `nl` only; limited effect) |
| `unformat` | string | `""` | `parse` pattern for structured extraction from `cprmv:definition`. As of v0.4.1 works with **any** `format` — the extracted values are added as triples on the rule. |

**Response:** Plain text in the requested format. As of v0.4.1 the endpoint always returns a `cprmv:RuleSet` with at least the selected `cprmv:Rule` as its `cprmv:hasPart` — even when a specific sub-rule is requested — so RuleSet-level properties (method, validity, provenance) always travel with the rule. The output (and JSON dumps) are UTF-8 encoded.

**Error response:**

```json
{"error": "No supported publication repository use identifiers with the format of the given Ruleset Id."}
```

**Supported Rule Set ID formats:** See [ID Formats](id-formats.md). DMN 1.3 rule sets published on `operaton.open-regels.nl` can also be retrieved (and the underlying DMN file fetched); this is documented inline in the `/rules` Swagger description.

---

## GET /ref

Resolves an external legal reference to a CPRMV API path and returns an HTTP redirect. The reference **method is auto-detected** — there is no `referencemethod` path segment (changed in v0.4.1).

**Query parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `reference` | string | `""` | The reference, in any supported format (auto-detected) |

**Supported reference formats (v0.4.1):**

| Type | Example | Resolves to |
|---|---|---|
| Juriconnect (`jci1.3` / `jci1.31`) | `jci1.31:c:BWBR0015703&artikel=20&o=a.` | a `/rules/` path |
| ELI → Formex 4 on EU CELLAR | `http://data.europa.eu/eli/reg/2018/1805/oj` | the EU CELLAR item (defaults language `NLD`, format `fmx4`) |
| ELI for BWB / CVDR (experimental) | `https://wetten.overheid.nl/BWBR0015703/Artikel%2020/onderdeel%20a.` | a `/rules/` path |
| CPRMV API rule id path | `https://cprmv.open-regels.nl/rules/BWBR0015703/Artikel%2020/onderdeel%20a.` | a `/rules/` path |

**Response:** `302 Found` redirect, or `{"error": "not a valid or supported reference..."}` if the reference cannot be resolved.

**Supported reference types:** See [Reference Resolution](../features/reference-resolution.md).

---

## GET /cellar-by-celex/{celexid}

Redirects to the EU CELLAR SPARQL endpoint running a query that finds the manifestation items for a given CELEX id. As of v0.4.1 it **redirects to the CELLAR output** rather than returning the URL as text.

**Path / query parameters:**

| Parameter | In | Default | Description |
|---|---|---|---|
| `celexid` | path | `32018R1805` | CELEX identifier of the work |
| `language` | query | `NLD` | Language code |
| `format` | query | `fmx4` | Manifestation format |

**Response:** `302 Found` redirect to the CELLAR SPARQL results.

---

## GET /cellar-by-eli/{elipath}/{language}/{format}

Helper added in v0.4.1. Works like `/cellar-by-celex` but accepts an ELI reference (matched against the EU CELLAR knowledge graph). Only ELI references explicitly linked to CELLAR documents resolve (partial ELIs do not).

**Example:** `/cellar-by-eli/http://data.europa.eu/eli/reg/2018/1805/oj/NLD/fmx4`

**Response:** `302 Found` redirect to the CELLAR SPARQL results.

!!! note
    For both `/cellar-by-*` endpoints, a CORS limitation in Swagger UI can make the
    redirect surface as `TypeError: Load failed`. Open the request URL directly to see
    the actual CELLAR response.

---

## /mcp

The API also exposes itself as a (basic) **Model Context Protocol** server, mounted via
`fastapi-mcp` at `/mcp` (v0.4.1). This lets MCP-capable clients call the CPRMV API endpoints
as tools.

---

## Static: /respec/

Serves the CPRMV specification as a static ReSpec HTML site. Navigate to `/respec/` in a browser.
