---
component: CPRMV
---

# Definition Extraction

The `unformat` parameter extracts structured values from a rule's `cprmv:definition` text using the Python [`parse`](https://pypi.org/project/parse/) library's pattern syntax.

---

## When to use it

Rule definitions in Dutch law frequently embed domain-specific values in natural language:

> *een alleenstaande van 18, 19 of 20 jaar: € 337,98;*

The `unformat` parameter allows you to pull these values out as named fields in the response, ready for direct use in downstream processing or decision model inputs — without needing a separate text-parsing step.

---

## Pattern syntax

Use `{fieldname:param_value}` placeholders in the pattern string. The `:param_value` type annotation is required; it matches any non-empty string.

**Pattern:** `{situatie:param_value}: € {norm:param_value}`

Applied to `BWBR0015703_2025-07-01_0, Artikel 20, lid 1, onderdeel a.`, whose definition is `een alleenstaande van 18, 19 of 20 jaar: € 337,98;`, the selected rule in the cprmv-json response becomes:

```json
{
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "https://standaarden.open-regels.nl/standards/cprmv/0.4.2#Rule",
    "https://standaarden.open-regels.nl/standards/cprmv/0.4.2#id": "onderdeel a.",
    "https://standaarden.open-regels.nl/standards/cprmv/0.4.2#definition": "een alleenstaande van 18, 19 of 20 jaar: € 337,98;",
    "http://cprmv.open-regels.nl/situatie": "een alleenstaande van 18, 19 of 20 jaar",
    "http://cprmv.open-regels.nl/norm": "337,98;",
    "http://cprmv.open-regels.nl/rulesetid": "BWBR0015703_2025-07-01_0",
    "http://cprmv.open-regels.nl/rule_id_path": "BWBR0015703_2025-07-01_0, Artikel 20, lid 1, onderdeel a."
}
```

The named fields, plus the `rulesetid` and `rule_id_path` context fields, are added to the selected rule as triples. Their predicate URIs are formed from the namespace of the rule set's URI (here `http://cprmv.open-regels.nl/`) and the field name. In the full response this rule object sits under the rule set's `cprmv:hasPart`.

---

## Behaviour when the pattern does not match

If the `parse` search does not find the pattern in the definition text, or the selected rule has no `cprmv:definition`, `unformat` has no effect and the standard response is returned without the extracted fields.

---

## Non-breaking spaces

The API normalises `cprmv:definition` text before matching: every run of whitespace, including non-breaking spaces (`\u00A0`), is collapsed to a single regular space. This ensures patterns work consistently regardless of how the source XML encoded whitespace.

---

## URL encoding the pattern

The `unformat` value must be URL-encoded in requests constructed manually:

| Character | Encoded |
|---|---|
| `{` | `%7B` |
| `}` | `%7D` |
| `:` | `%3A` |
| ` ` | `%20` |
| `€` | `%E2%82%AC` |

**Example full URL:**

```
GET /rules/BWBR0015703_2025-07-01_0%2C%20Artikel%2020%2C%20lid%201%2C%20onderdeel%20a.
    ?unformat=%7Bsituatie%3Aparam_value%7D%3A%20%E2%82%AC%20%7Bnorm%3Aparam_value%7D
```

FastAPI's Swagger UI handles encoding automatically.

---

## Works with any output format

`unformat` works with any format: the values extracted from the definition are added as additional triples on the selected rule, so they appear in the RDF serialisations too (e.g. `turtle`, `n3`, `json-ld`). Combine `unformat` with `format=turtle` to get the extracted `situatie`/`norm` values as triples in the Turtle output.

!!! note
    The interactive Swagger description of the `unformat` parameter still states that it implies `cprmv-json`; that text is stale — the cross-format behaviour above is what the API does.
