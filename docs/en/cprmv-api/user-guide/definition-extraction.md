# Definition Extraction

The `unformat` parameter extracts structured values from a rule's `cprmv:definition` text using the Python [`parse`](https://pypi.org/project/parse/) library's pattern syntax.

---

## When to use it

Rule definitions in Dutch law frequently embed domain-specific values in natural language:

> *Huur: € 1.200,—*

The `unformat` parameter allows you to pull these values out as named fields in the JSON response, ready for direct use in downstream processing or decision model inputs — without needing a separate text-parsing step.

---

## Pattern syntax

Use `{fieldname:param_value}` placeholders in the pattern string. The `:param_value` type annotation is required; it matches any non-empty string.

**Pattern:** `{situatie:param_value}: € {norm:param_value}`

This matches a definition like `Huur: € 1.200,—` and extracts:

```json
{
    "situatie": "Huur",
    "norm": "1.200,—",
    "rulesetid": "BWBR0015703_2025-07-01_0",
    "rule_id_path": "BWBR0015703_2025-07-01_0, Artikel 20, lid 1, onderdeel a.",
    "https://standaarden.open-regels.nl/standards/cprmv/0.4.0/#id": "onderdeel a.",
    "https://standaarden.open-regels.nl/standards/cprmv/0.4.0/#definition": "Huur: € 1.200,—"
}
```

The extracted named fields are merged at the top level of the cprmv-json response alongside the full rule predicates and the `rulesetid` and `rule_id_path` context fields.

---

## Behaviour when the pattern does not match

If the `parse` search does not find the pattern in the definition text, `unformat` has no effect and the standard cprmv-json response is returned without the extracted fields.

---

## Non-breaking spaces

The API normalises `cprmv:definition` text before matching: sequences of non-breaking spaces (`\u00A0`) are converted to regular spaces. This ensures patterns work consistently regardless of how the source XML encoded whitespace.

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

## Format override

When `unformat` is specified, the `format` parameter is ignored and the response is always `cprmv-json`. The `unformat` mechanism operates on the rule's definition literal, which is only available in the cprmv-json structure.
