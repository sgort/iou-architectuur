# API Endpoints

Interactive documentation is available at the live environments:

- **Production:** [https://cprmv.open-regels.nl/docs](https://cprmv.open-regels.nl/docs)
- **Acceptance:** [https://acc.cprmv.open-regels.nl/docs](https://acc.cprmv.open-regels.nl/docs)

---

## GET /

Returns the API title and version.

**Response:**

```json
{"CPRMV Rules Serve API": "0.4.0"}
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
| `unformat` | string | `""` | `parse` pattern for structured extraction from `cprmv:definition`. Forces `cprmv-json`. |

**Response:** Plain text in the requested format.

**Error response:**

```json
{"error": "No supported publication repository use identifiers with the format of the given Ruleset Id."}
```

**Supported Rule Set ID formats:** See [ID Formats](id-formats.md).

---

## GET /ref/{referencemethod}/{reference}

Resolves an external legal reference URI to a CPRMV API `/rules/` path and returns an HTTP redirect.

**Path parameters:**

| Parameter | Type | Description |
|---|---|---|
| `referencemethod` | string | Reference system. Currently: `Juriconnect` |
| `reference` | string | The reference URI (e.g. `jci1.3:c:BWBR0015703&artikel=20&z=2025-07-01&g=2025-07-01`) |

**Response:** `302 Found` redirect to the corresponding `/rules/` path, or `null`/error if the reference cannot be resolved.

**Supported reference types:** See [Reference Resolution](../features/reference-resolution.md).

---

## Static: /respec/

Serves the CPRMV specification as a static ReSpec HTML site. Navigate to `/respec/` in a browser.
