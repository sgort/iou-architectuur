# Semantic Analysis

Different government agencies publish DMN decision models using their own naming conventions for variables. When one agency's output variable and another agency's input variable represent the same concept but have different identifiers, exact identifier matching fails and chain building appears to break. The Semantic Analysis feature resolves this by using SKOS concept mappings to discover variable relationships across agency boundaries.

<figure markdown>
  ![Screenshot: Semantic Analysis tab showing variable equivalences across government agencies](../../assets/screenshots/linked-data-explorer-semantic-analysis.png)
  <figcaption>Semantic Analysis tab showing variable equivalences across government agencies</figcaption>
</figure>

---

## The problem

```
SVB output:   "aanvragerIs181920"
SZW input:    "aanvragerIs181920"   ← exact match, chain works

Zorg output:  "heeftJuisteLeeftijd"
Belasting input: "leeftijd_requirement"  ← no exact match, chain appears broken
```

---

## The solution

The CPSV Editor, when publishing a DMN to TriplyDB, generates a `skos:Concept` for each input and output variable. When two variables from different agencies represent the same thing, both concepts carry a `skos:exactMatch` link pointing to the same shared concept URI from a central vocabulary. The Linked Data Explorer queries for these shared concept URIs and surfaces all variable pairs that connect via them.

This means a chain between Zorg and Belasting is discoverable and executable — not as a DRD (because the identifiers differ), but as a sequential chain where the backend maps the output value of one step to the correctly named input of the next.

---

## Semantic Analysis tab

In the Chain Builder, the **Semantic Analysis** tab (next to the chain composer) shows:

- **Statistics** — counts of semantic equivalences, semantic chain suggestions, and exact match links in the current endpoint
- **Semantic Equivalences** — a table of variable pairs sharing a concept, with labels, notations, and the shared concept URI
- **Semantic Chain Suggestions** — output/input pairs from different DMNs that are connectable via a shared concept but would not appear in exact-match chain detection

Results populate automatically from the active TriplyDB endpoint whenever NL-SBB concepts with `skos:exactMatch` links have been published from the CPSV Editor.

---

## Standards

The semantic matching system follows these specifications:

- **NL-SBB** — Dutch profile for SKOS concept schemes, used for the concept vocabulary
- **SKOS** (`skos:exactMatch`) — cross-vocabulary alignment between agency-specific variable concepts and the shared central vocabulary
- **CPSV-AP 3.2.0** (`cpsv:Input`, `cpsv:Output`) — linked to concepts via `dct:subject`

---

## Graph view

In the SPARQL graph visualisation, semantic links (`skos:exactMatch`, `dct:subject`) are rendered as dashed green lines (2.5 px), visually distinct from standard RDF property edges (solid grey, 1.5 px).
