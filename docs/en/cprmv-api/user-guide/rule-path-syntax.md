---
component: CPRMV
---

# Rule Path Syntax

The `rule_id_path` path parameter is the primary way to address rules. This page documents the full syntax.

---

## Structure

```
{RuleSetId}[{delimiter}{RuleId1}[{delimiter}{RuleId2}[...]]]
```

- The first segment is always the **Rule Set ID**. The whole `rule_id_path` is 10–500 characters.
- Each subsequent segment is a **Rule ID** from the publication hierarchy.
- The default delimiter is `,` (comma). It can be overridden with `path_delimiter`.

---

## Rule Set ID formats

### BWB

```
BWBR0015703                         ← current version (valid today)
BWBR0015703_2025-07-02_latest       ← latest version valid on date
BWBR0015703_2025-07-01_0            ← specific publication (date + index)
```

Pattern: `BWB{rulesetid}_{date}_{index}` where `index` may be a digit or `latest`.

### CVDR

```
CVDR712517                          ← current version
CVDR712517_2025-07-02_latest        ← latest version valid on date
CVDR712517_1                        ← specific indexed version
```

Publication pattern: `CVD{rulesetid}_{index}`; the identifier is matched against the normalised pattern `CVD{rulesetid}_{date}_{index}`, where `index` may be a digit or `latest`. See [ID Formats](../reference/id-formats.md).

### EU CELLAR

```
CFMX483e4752e-f2e5-11e8-9982-01aa75ed71a1.0017.02_DOC_2
```

Pattern: `CFMX4{rulesetid}_{docid}` — no date-based resolution available.

### DMN 1.3 (Operaton)

```
DMN1.3_{deploymentid}R{resourceid}_{date}_{index}
```

Example: `DMN1.3_e62cb254-0e74-11f1-a5e9-f68ed60940f5Re62cb255-0e74-11f1-a5e9-f68ed60940f5_2026-01-01_1, LiteralExpression_2021`.

---

## Rule ID matching rules

Rule identifiers in the path are matched against `cprmv:id` literals in the RDF graph using the following normalisation:

- All non-alphanumeric characters (spaces, periods, parentheses, hyphens, slashes) are **stripped** from both the path segment and the stored identifier before comparison.
- Matching is **case-sensitive** after normalisation.

**Examples of equivalent path segments:**

| Path segment | Matches graph value |
|---|---|
| `Artikel 20` | `Artikel 20` |
| `Artikel20` | `Artikel 20` |
| `onderdeel a.` | `onderdeel a.` |
| `onderdeel a` | `onderdeel a.` |
| `lid 1` | `lid 1` |

---

## Depth-first search

When multiple rules could match a path segment, the traversal is depth-first and returns the first match. A segment that does not match a rule is carried down into that rule's parts, which is why intermediate identifiers can be skipped. To ensure you target the correct rule, include all intermediate identifiers in the path.

**Ambiguous (may return wrong rule):**

```
BWBR0015703_2025-07-01_0, onderdeel a.
```

**Unambiguous:**

```
BWBR0015703_2025-07-01_0, Artikel 20, lid 1, onderdeel a.
```

---

## URL encoding

All special characters in the path must be URL-encoded when constructing request URLs manually:

| Character | Encoded |
|---|---|
| `,` (comma) | `%2C` |
| ` ` (space) | `%20` |
| `.` (period) | `%2E` |
| `(` | `%28` |
| `)` | `%29` |

FastAPI's Swagger UI (`/docs`) handles encoding automatically when using **Try it out**.

---

## Minimum and maximum length

The `rule_id_path` parameter enforces a minimum length of 10 characters and a maximum of 500 characters.

---

## Responses for unmatched input

Both cases return HTTP `200`:

| Situation | Body |
|---|---|
| No publication method recognises the Rule Set ID | `{"error": "No supported publication repository use identifiers with the format of the given Ruleset Id."}` |
| The Rule Set is found but the path matches no rule | `No rules found for given path...` |
