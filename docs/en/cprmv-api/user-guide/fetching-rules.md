# Fetching Rules

All rule retrieval goes through the `/rules/{rule_id_path}` endpoint. This page covers the full range of retrieval patterns.

---

## Fetching a complete rule set

Omit the rule path after the rule set identifier to retrieve the full set as a single response. The rule set node itself is returned with all its top-level rules.

```
GET /rules/BWBR0015703_2025-07-01_0
```

!!! note
    Large rule sets can produce substantial responses. For most integration work you will want to target a specific rule or article rather than the full set.

---

## Fetching a specific article

Add the article identifier after the rule set ID, separated by a comma:

```
GET /rules/BWBR0015703_2025-07-01_0%2C%20Artikel%2020
```

URL-encoding reference: `,` → `%2C`, space → `%20`.

The response includes the article and all its contained sub-rules recursively.

---

## Navigating to a nested rule

Extend the path with additional comma-separated identifiers:

```
GET /rules/BWBR0015703_2025-07-01_0%2C%20Artikel%2020%2C%20lid%201%2C%20onderdeel%20a.
```

The path traversal is depth-first. Non-alphanumeric characters (spaces, periods, parentheses) are stripped from both the path identifier and the graph identifier before matching, so `"onderdeel a."` and `"onderdeel a"` match the same rule node.

---

## Skipping intermediate identifiers

Intermediate levels can be omitted if there is no ambiguity. Both of the following reach the same rule:

```
/rules/BWBR0015703_2025-07-01_0%2C%20Artikel%2020%2C%20onderdeel%20a.
/rules/BWBR0015703_2025-07-01_0%2C%20Artikel%2020%2C%20lid%201%2C%20onderdeel%20a.
```

---

## CVDR (municipal regulations)

Same pattern, with CVDR identifiers:

```
GET /rules/CVDR712517_1%2C%20Artikel%205
GET /rules/CVDR712517                        ← current version
GET /rules/CVDR712517_2025-07-02_latest      ← valid on date
```

---

## EU CELLAR (European legislation)

```
GET /rules/CFMX483e4752e-f2e5-11e8-9982-01aa75ed71a1.0017.02_DOC_2%2C%20Artikel%201
```

---

## Choosing an output format

Append `?format=turtle` (or any supported format value) to change serialisation:

```
GET /rules/BWBR0015703_2025-07-01_0%2C%20Artikel%2020?format=turtle
GET /rules/BWBR0015703_2025-07-01_0%2C%20Artikel%2020?format=json-ld
```

See [Output Formats](../features/output-formats.md) for the full list.

---

## Using a custom path delimiter

If a rule identifier contains a comma, override the delimiter with `path_delimiter`:

```
GET /rules/BWBR0015703_2025-07-01_0|Artikel%2020?path_delimiter=%7C
```

---

## Extracting structured values with unformat

When a rule definition contains a parseable pattern, `unformat` extracts named fields directly:

```
GET /rules/BWBR0015703_2025-07-01_0%2C%20Artikel%2020%2C%20lid%201%2C%20onderdeel%20a.
    ?unformat=%7Bsituatie%3Aparam_value%7D%3A%20%E2%82%AC%20%7Bnorm%3Aparam_value%7D
```

Decoded `unformat` pattern: `{situatie:param_value}: € {norm:param_value}`

The response merges the extracted `situatie` and `norm` fields into the cprmv-json output alongside the full rule data.

See [Definition Extraction](definition-extraction.md) for more examples.
