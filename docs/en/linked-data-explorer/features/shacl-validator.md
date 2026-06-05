# SHACL Validator

The SHACL Validator lets you validate one or more CPSV-AP Turtle files against the canonical **CPSV-AP 3.2.0** shapes and the **RONL Custom** shapes before publishing them to TriplyDB. It is accessible from the badge-check icon in the sidebar.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: SHACL Validator with three files loaded side-by-side — a conformant file (all green) and two collision fixtures showing per-layer errors](../../assets/screenshots/linked-data-explorer-shacl-validator.png)
  <figcaption>SHACL Validator with three files loaded side-by-side — a conformant file (all green) and two collision fixtures showing per-layer errors</figcaption>
</figure>

---

## Two validation modes

A toggle at the top of the panel selects how each file is validated:

- **File-local** — the uploaded Turtle is validated on its own, exactly as written. This catches problems contained within the file (for example, three `cpsv:Rule` blocks accidentally published under one subject URI).
- **Merge-simulated** — before validation, the already-published triples for the file's subjects are fetched from a SPARQL endpoint and unioned with the uploaded file. This catches collisions that only emerge once your file is added to the store — for example, an organisation whose `foaf:homepage` differs between an existing publication and the file you are about to publish.

Merge-simulated mode shows an optional endpoint field; when left blank, the configured default TriplyDB endpoint is used.

---

## Multi-file validation

You can drop any number of `.ttl` files onto the validator at once, or add files incrementally — the drop zone remains visible at the top of the panel whenever files are loaded. Files are validated independently and displayed side-by-side for easy comparison.

Each file card shows:

- File name and size
- A **Validate** button to trigger validation for that file individually
- The validation result with a summary badge and collapsible layer sections
- A remove (×) button to dismiss the file

A **Clear all** button in the header removes every file and resets the panel. Navigation state is preserved: switching to another view and returning does not clear the loaded files or their results.

---

## Validation layers

Results are grouped into two layers. Each layer can be expanded to see individual issues. Issues carry a severity, a typed code, and a human-readable message; cardinality and uniqueness issues also list the offending values.

| Layer | Source | Covers |
|---|---|---|
| CPSV-AP 3.2.0 | Canonical SEMIC shapes, vendored | The full CPSV-AP model — `PublicService`, `Rule`, `PublicOrganisation`, `ContactPoint`, `Channel`, `Address`, and related classes (32 shapes). Enforces required properties, datatypes, and class constraints. |
| RONL Custom | RONL-authored shapes | RONL publishing invariants on top of CPSV-AP — at most one `foaf:homepage` / `dct:identifier` / `cv:spatial` per organisation, and at most one `dct:title` / `dct:description` per language on a rule. |

A file is **valid** when no layer produces an error. Warnings and informational messages are advisory.

A layer is shown as **Not loaded** (rather than OK) when no shape files are present for it — so an unvendored layer never displays a misleading green check. For the complete specification of the shapes and codes, see the [SHACL Validation Reference](../reference/shacl-validation-reference.md).

---

## Severity levels

The SHACL result severity (`sh:Violation`, `sh:Warning`, `sh:Info`) maps directly to:

| Icon | Level | Meaning |
|---|---|---|
| 🔴 | Error | A `sh:Violation` — the data does not conform and should not be published as-is. Must be resolved. |
| 🟡 | Warning | A `sh:Warning` — the data conforms but deviates from a recommended practice. Should be reviewed. |
| 🔵 | Info | A `sh:Info` — a quality suggestion. No conformance impact. |

---

## Validation example

The screenshot below shows `rule-collision-fail.ttl` — three `cpsv:Rule` blocks deliberately published under a single subject URI — expanded in the validator. The CPSV-AP layer reports one error (the rule is missing the required `dct:identifier`); the RONL Custom layer reports two (`sh:uniqueLang` on `dct:title` and `dct:description`, since the single subject now carries three Dutch labels).

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: rule-collision-fail.ttl expanded showing CPSV-AP 1E (missing dct:identifier) and RONL Custom 2E (uniqueLang on dct:title and dct:description)](../../assets/screenshots/linked-data-explorer-shacl-validator-layers.png)
  <figcaption>rule-collision-fail.ttl expanded — CPSV-AP 1E (missing dct:identifier) and RONL Custom 2E (uniqueLang on dct:title and dct:description)</figcaption>
</figure>

Note how the two layers are independent: a file can pass the RONL Custom layer while still failing CPSV-AP conformance (for example, a minimal rule that is unique but lacks `dct:identifier`), and vice versa.

---

## Merge-simulated validation

Merge-simulated mode is the most effective way to catch problems that only appear at publication time. Because TriplyDB merges your file into the existing graph, a property that is single-valued in your file can become multi-valued once unioned with what is already published.

The classic case is `foaf:homepage`: your file lists `https://flevoland.nl/home`, the store already holds `https://www.flevoland.nl/home` for the same organisation, and the merged organisation now has two homepages — which fans out into duplicate rows downstream. File-local validation cannot see this; merge-simulated validation flags it as a `SHACL-MAXCOUNT` error in the RONL Custom layer.

See [Using the SHACL Validator](../user-guide/shacl-validator.md) for the step-by-step workflow.
