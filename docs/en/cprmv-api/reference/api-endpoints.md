---
component: CPRMV
---

# API Endpoints

Interactive documentation is available at the live environments:

- **Production:** [https://cprmv.open-regels.nl/docs](https://cprmv.open-regels.nl/docs) (also [https://cprmv.open-rules.eu/docs](https://cprmv.open-rules.eu/docs))
- **Acceptance:** [https://acc.cprmv.open-regels.nl/docs](https://acc.cprmv.open-regels.nl/docs)

Responses from `/methods` and `/rules`, and errors from `/raw`, are plain text (`text/plain; charset=utf-8`) whatever the requested serialisation. Errors are reported in the body with HTTP status `200`, except where noted.

`/rules`, `/raw` and `/ref` accept an optional `x-api-key` header. The API passes it on to a source that needs the caller's own key — today the DSO methods (see [Publication Repositories](../features/publication-repositories.md#dso-sttr)); the other sources need none.

---

## GET /

Returns the API title and the vocabulary and API version.

**Response:**

```json
{"CPRMV Rules Serve API": "0.4.3"}
```

---

## GET /health

Reports liveness and what the host runs. Every field is read when the request arrives; one that is not set, or is empty, is `null`.

**Response** (from `cprmv.open-regels.nl` on 27 November 2026):

```json
{"status": "ok", "version": "0.4.3", "environment": "stable", "release": "v2026.11.0",
 "build": {"sha": "502a3517f0c1d1f56aa4f57a42a37a42daf28657", "run": "21"},
 "image": {"digest": "sha256:047d4d416d50a3fe9147d2e63d81d06ab07ec8b7f44c1aa83ffedceb7091b8fc"}}
```

| Field | Source |
|---|---|
| `version` | the vocabulary and API version, as on `/` ([two version numbers](../developer/ci-cd.md#two-version-numbers)) |
| `environment` | `CPRMV_ENVIRONMENT`, set by the tier's Compose file: `acceptance` or `stable` |
| `release` | the release number the image was built at, `vYYYY.MM.N` (`BUILD_RELEASE`, from `serve_api/RELEASE`); on acceptance, the last release its code is at or after; `null` before the first release and in local builds |
| `build.sha`, `build.run` | the commit and CI run number the image was built from (`BUILD_SHA`, `BUILD_RUN`); `run` is a string |
| `image.digest` | the registry digest the VM runs (`CPRMV_IMAGE_DIGEST`) |

CI and the VMs compare `build.sha` with the commit they deploy ([VM Deployment](../developer/vm-deployment.md#what-health-proves)). Only `GET` is served: `HEAD /health` answers `405`.

The hosts also serve `/deploy-status.json`. That file comes from the VM, not from the API: see [VM Deployment](../developer/vm-deployment.md#reading-deploy-statusjson).

---

## GET /methods

Returns the Methods Knowledge Graph, loaded at start-up from `data/cprmvmethods.ttl` and `data/cprmv.ttl`.

**Query parameters:**

| Parameter | Type | Default | Values |
|---|---|---|---|
| `format` | string | `json-ld` | `json-ld`, `xml`, `turtle`, `ttl`, `n3`, `turtle2` |
| `method_name` | string | — | A method's local name, e.g. `iou-norms` or `core-api` (names starting with `core` are looked up in `cprmv-serve:`, the others in `cprmvmethods:`) |

**Response:** Plain text in the requested RDF serialisation; `null` for any other `format` value.

The graph lists the acknowledged methods per category (`cprmvmethods:rulemethods`, `publicationmethods`, `referencemethods`, `analysismethods`, `formalisationmethods`, `serialisationmethods`, `executionmethods`, …) and each method's definition. It is the committed `data/cprmvmethods.ttl`, which `make methods` generates from `rdf/0.4.3/`, merged with the vocabulary.

With `method_name`, the response is the description of one node whose type is that method, following blank nodes — for `iou-norms`, the configured instance `norms-backend.linkeddata.open-regels.nl`, not the `iou-norms` method itself. A name that no node is typed by, such as `roo`, `dso` or a misspelling, returns the whole graph with status `200`, not an error ([open-regels/cprmv#2](https://github.com/open-regels/cprmv/issues/2)).

---

## GET /0.4.3/methods/{method_name}

The same as `/methods?method_name=…`, as a path, so that the method URIs in the ReSpec value lists (`https://cprmv.open-regels.nl/0.4.3/methods/…`) lead to the API. Takes `format` like `/methods`, and selects the same way.

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

**Supported Rule Set ID formats:** See [ID Formats](id-formats.md). Besides BWB, CVDR and EU CELLAR: DMN 1.3 decision models on `operaton.open-regels.nl`, norms from the IOU Norms API, organisations from the Register van Overheidsorganisaties, and STTR decision models from the DSO (with `x-api-key`).

---

## GET /raw/{rule_id_path}

Returns the original publication behind a rule set, untransformed, as a download. Only the rule set id counts; any rule path after it is ignored.

**Path and query parameters:** `rule_id_path` and `path_delimiter` as for `/rules`.

**Response:** the file, `application/octet-stream`, with `Content-Disposition: attachment; filename="{RuleSetId}"` (the id as given, no extension) — for BWB the `toestand` XML. If the id is not recognised or the download fails, the body is `{"error retrieving raw Rule Set publication": "…"}` as text, with status `200`.

The source URL is the method's `cprmv-serve:repository-publication-location-format` (see [ID Formats](id-formats.md)).

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

**Response:** `307 Temporary Redirect`, or `{"error": "not a valid or supported reference..."}` if no method resolves the reference. The redirect response carries the request's own headers back, the `x-api-key` included ([open-regels/cprmv#1](https://github.com/open-regels/cprmv/issues/1)). A malformed Juriconnect reference currently fails with `500 Internal Server Error` (see [Reference Resolution](../features/reference-resolution.md#juriconnect)).

**Supported reference types:** See [Reference Resolution](../features/reference-resolution.md).

---

## /mcp/

`serve.py` builds a **Model Context Protocol** server from the API's routes with FastMCP (`FastMCP.from_fastapi(app=app, name="CPRMV")`) after every route is registered, and mounts it on the API at `/mcp`. The endpoint is `/mcp/` (streamable HTTP): a request to `/mcp` is redirected, to an `http://` address ([open-regels/cprmv#2](https://github.com/open-regels/cprmv/issues/2)). On 24 November a `GET /mcp/` answered on all three hosts with the MCP error for a missing session, as the protocol prescribes.

---

## Static: /respec/

Serves the CPRMV specification as a static ReSpec HTML site, with one folder per version (`/respec/0.4.0/` … `/respec/0.4.3/`); `/respec/` itself opens 0.4.3. From 0.4.1 on, each version folder also holds a PDF (`cprmv.pdf`). Navigate to `/respec/` in a browser.
