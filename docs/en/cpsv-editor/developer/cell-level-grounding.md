---
component: CPSV Editor
---

# Cell-Level Legislative Grounding

Linking legislation to decision logic at **decision-table cell** granularity —
finer than DMN's native decision-level `knowledgeSource`, and finer than
CPRMV's rule-level `extends`/`ruleType`/`confidence`.

Shipped in v2026.08.0. See the [Changelog](changelog-roadmap.md) for the
release summary and [Namespace & Property Reference](../reference/namespace-property-reference.md#cell-level-grounding-v2026080)
for the property definitions.

---

## Why cell granularity

A decision table rule is a row; each of its cells is a separate condition or
outcome, and in practice each cell can rest on a *different* article. Take a
rule that qualifies an applicant: one cell tests residence, another tests
household composition, a third sets the resulting entitlement. Those three
conditions routinely come from three different provisions.

The existing linking levels cannot express that:

| Level | Mechanism | Granularity |
|---|---|---|
| DMN native | `<knowledgeSource>` + `authorityRequirement` | Whole decision |
| CPRMV | `cprmv:isBasedOn` on a `cprmv:Rule` | Whole rule (row) |
| **This** | `cprmv:hasPart` → per-cell `cprmv:Rule` | One cell |

Cell-level grounding adds the third row without replacing either of the first
two — a DMN keeps its `knowledgeSource` links, and rule-level `isBasedOn`
still emits as before.

The implementation spans three layers: attributes carried in the DMN file,
the reader that extracts them, and the TTL emitter that publishes them.

---

## Layer 1 — DMN attributes

Grounding travels **inside the DMN file**, on the `<inputEntry>` and
`<outputEntry>` elements themselves, so it survives any tool that round-trips
the XML. Two namespaces are declared on `<dmn:definitions>`:

```xml
<dmn:definitions
    xmlns:cprmv="https://standaarden.open-regels.nl/standards/cprmv/0.4.1#"
    xmlns:dct="http://purl.org/dc/terms/">
```

Each grounded cell then carries up to three attributes:

| Attribute | Meaning |
|---|---|
| `dct:source` | The annotation or concept id this cell was derived from |
| `cprmv:sourceQuote` | The quoted text fragment the grounding rests on |
| `cprmv:isBasedOn` | The citation — a full URL, or a bare JuriConnect (JCI) reference |

```xml
<inputEntry id="ie1a"
            dct:source="apt-1"
            cprmv:sourceQuote="Woonadres"
            cprmv:isBasedOn="https://lokaleregelgeving.overheid.nl/CVDR1/1">
  <dmn:text>"Amsterdam"</dmn:text>
</inputEntry>
```

Cells carrying none of the three are **ungrounded**, which is the normal case
— wildcards and cross-decision references have nothing to cite.

### Compound cells

A single cell can be a compound FEEL expression whose conjuncts each need
their own citation. Two encodings were tested directly against Operaton:
repeatable child elements were rejected outright (the DMN schema's
unary-tests content model has no extension point for them), while a **numbered
attribute family** deploys cleanly with no upper bound. That is what shipped:

```xml
<inputEntry id="ie2b"
            dct:source1="concept-A"
            cprmv:isBasedOn1="jci1.3:c:BWBR0002&amp;artikel=9"
            dct:source2="concept-B"
            cprmv:sourceQuote2="tweede grondslag">
  <dmn:text>&gt;= 18 and &lt; 67</dmn:text>
</inputEntry>
```

The reader scans `dct:source1`/`cprmv:sourceQuote1`/`cprmv:isBasedOn1`, then
`…2`, and so on, stopping at the first index where none of the three is
present.

!!! note "Grounding attributes are inert to evaluation"
    They are extension attributes in foreign namespaces, so Operaton ignores
    them. This was confirmed empirically rather than assumed: after grounding
    was applied, the 100-case MC/DC suite still passed 100/100 against the
    redeployed model.

---

## Layer 2 — Reading the DMN

`src/utils/dmnHelpers.js` extracts groundings while it parses the decision
table. `extractCellGroundings(entryEl)` returns an array of
`{ source, sourceQuote, isBasedOn }` — empty for an ungrounded cell, one entry
for the shorthand form, N for the numbered form. `extractCell(entryEl)` wraps
that together with the cell's own `id` and its FEEL text, and
`extractRulesFromDMN` attaches the results to each rule as `inputEntries` and
`outputEntries`.

The cell's `id` matters: it is the stable key the published cell URI is built
from. The iKnow re-export in this release gives every `<inputEntry>` and
`<outputEntry>` its own id for exactly this reason — keying off the id rather
than column position keeps URIs stable when columns are reordered. A
positional fallback covers sources that emit no per-cell ids.

### The namespace-agnostic lookup

Building this layer surfaced a defect that **predates cell grounding
entirely**. Every selector-based DMN lookup in the codebase silently matched
nothing against a real, `dmn:`-prefixed file:

```js
// Matches only elements in the null namespace — i.e. an unprefixed DMN.
xmlDoc.querySelectorAll('decision');
```

CSS type selectors match on the pair (namespace, local name), and an
unprefixed selector implies the null namespace. Against a real DMN — where
every element is `dmn:decision` — the selector returns nothing. Cell-level
grounding could never have worked, and neither did the pre-existing
rule-level export.

The fix is a pair of helpers that match on local name regardless of prefix:

```js
function queryAllLocal(root, localName) { /* … */ }
function queryLocal(root, localName)    { /* … */ }
```

Every DMN lookup now goes through them.

---

## Layer 3 — Emitting the TTL

`generateDmnSection()` in `src/utils/ttlGenerator.js` emits a
`cprmv:hasPart` list of per-cell resources on each `cprmv:DecisionRule`:

```turtle
<…/rules/DecisionRule_1> a cpsv:Rule, cprmv:DecisionRule ;
    dct:identifier "DecisionRule_1" ;
    cprmv:hasPart ( <…/rules/DecisionRule_1/cell/ie1a>
                    <…/rules/DecisionRule_1/cell/ie1b> ) .
```

### URI scheme

| Resource | URI | `cprmv:id` |
|---|---|---|
| Cell | `{ruleUri}/cell/{cellId}` | `{ruleId}-cell-{cellId}` |
| Compound sub-grounding | `{cellUri}/grounding/{n}` | `{ruleId}-cell-{cellId}-grounding-{n}` |
| Minted concept | `{serviceUri}/concepts/{sourceId}` | `{sourceId}` |

### Two kinds of grounding

A cell **with** a `sourceQuote` grounds directly — the quote and its citation
are emitted on the cell resource:

```turtle
<…/rules/DecisionRule_1/cell/ie1a> a cprmv:Rule ;
    cprmv:id "DecisionRule_1-cell-ie1a" ;
    dct:source <https://hva.pna-web.com/hva/?type=APT&id=apt-1> ;
    cprmv:sourceQuote "Woonadres" ;
    cprmv:isBasedOn <https://lokaleregelgeving.overheid.nl/CVDR1/1> .
```

A cell with **only** a `dct:source` points instead at a shared concept
resource, minted once and reused by URI wherever it recurs:

```turtle
<…/rules/DecisionRule_1/cell/ie1b> a cprmv:Rule ;
    cprmv:id "DecisionRule_1-cell-ie1b" ;
    cprmv:isBasedOn <…/concepts/cpt-shared> .

<…/concepts/cpt-shared> a cprmv:Rule ;
    cprmv:id "cpt-shared" ;
    dct:source <https://hva.pna-web.com/hva/?type=CPT&id=cpt-shared> .
```

Deduplication is not cosmetic — a decision's own `authorityRequirement` and a
rule's output cell were verified to resolve to the same underlying concept, so
minting once and referencing by URI is what keeps the graph joinable.

A compound cell composes the two forms with a nested list:

```turtle
<…/cell/ie2b> a cprmv:Rule ;
    cprmv:id "DecisionRule_2-cell-ie2b" ;
    cprmv:hasPart ( <…/cell/ie2b/grounding/1> <…/cell/ie2b/grounding/2> ) .
```

### Citation resolution

`cprmv:isBasedOn` values are passed through when they are already full URLs,
and resolved against `https://wetten.overheid.nl/` when they are bare
JuriConnect references — the same construction the rule-level emission already
used.

---

## SHACL conformance

Live validation against a real published `.ttl` surfaced two `RuleShape`
violations. Both are fixed, and both are worth knowing about before extending
the emitter:

**`cprmv:id` is mandatory on every `cprmv:Rule`** (`sh:minCount 1`). Cell
resources originally emitted `dct:identifier` — a property `RuleShape` does
not check at all, so the constraint failed while the data looked fine — and
concept resources carried no identifier whatsoever. Every resource this layer
mints now emits `cprmv:id`, sub-groundings included.

**`cprmv:isBasedOn` has `sh:class cprmv:Rule`**, so its object must itself be
typed `cprmv:Rule`. Concept targets already were. A direct external citation
URI — CVDR, `wetten.overheid.nl` — was not, so every such reference failed the
shape. Each distinct citation URI now gets a minted, deduplicated stub:

```turtle
<https://lokaleregelgeving.overheid.nl/CVDR1/1> a cprmv:Rule ;
    cprmv:id "https://lokaleregelgeving.overheid.nl/CVDR1/1" .
```

The `cprmv:id` falls back to the URI itself — there is no other identifier
available for an external resource this graph does not otherwise describe.

No new SHACL shapes were needed: cell resources are ordinary `cprmv:Rule`
instances composed with the existing `cprmv:hasPart`, so the recursion is
covered by shapes that already exist.

---

## Verification

- 12 tests in `src/utils/ttlGenerator.cellGrounding.test.js` cover emission,
  concept dedup, compound nesting and the conformance rules; further tests in
  `dmnHelpers.test.js` cover the reader. See [Testing](testing.md).
- End-to-end against the real Amsterdam HvA model: grounding applied,
  deployed, evaluated, and published live through the editor with zero DMN
  evaluation issues and zero SHACL validation issues.
- The 100-case MC/DC suite passes unchanged after grounding, confirming the
  attributes stay inert to FEEL evaluation.

---

## Open questions

- **Cross-export id stability.** Cell URIs key off `<inputEntry>`/
  `<outputEntry>` ids. Whether those ids survive a fresh export from the
  authoring tool is not yet established — if they do not, republishing after
  a re-export would mint new cell URIs for unchanged logic.
- **`ruleType` / `rulesetType` on cell resources.** Flagged by the CPRMV spec
  owner as still under consideration; cell resources currently carry neither.
- **CPRMV `ReferenceMethod`.** CPRMV 0.4.2 introduces `ReferenceMethod` as a
  pluggable concept with JCI and ELI as known methods, rather than mandating
  one citation grammar. The emission here predates it and resolves JCI
  directly; aligning with `ReferenceMethod` is a future change. See
  [External Standards](../reference/external-standards.md).
