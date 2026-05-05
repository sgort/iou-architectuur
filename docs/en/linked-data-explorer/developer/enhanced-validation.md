# Enhanced Validation & Semantic Detection

This page covers the implementation of the chain validation engine and the semantic link detection system. These two subsystems are tightly coupled — the validation engine consumes the output of the semantic link query — so they are documented together.

---

## Architecture

```
ChainBuilder.tsx
  loads semantic links on mount via /v1/dmns/enhanced-chain-links
  on chain change → runValidation()
        │
        ▼
Validation Engine (inline in ChainBuilder.tsx)
  for each DMN in chain, for each input variable:
    check availableOutputs Set (exact identifier matches from prior steps)
    check semanticLinks array (semantic matches from prior steps)
    if neither → user must provide input
  determines:
    isDrdCompatible = no semantic matches used
    missingInputs = inputs requiring user input
        │
        ▼
Backend: findEnhancedChainLinks (sparql.service.ts)
  SPARQL query joining:
    Output Variables → Output Concepts → Shared Concepts
                                            ↑
    Input Variables  → Input Concepts  ────┘
  returns matchType: 'exact' | 'semantic' | 'both'
```

---

## Backend SPARQL query

The core of semantic detection is the `findEnhancedChainLinks` query. It joins output and input variables through their SKOS concepts to find shared concept URIs:

```sparql
PREFIX cprmv: <https://cprmv.open-regels.nl/0.3.0/>
PREFIX cpsv:  <http://www.w3.org/ns/regorg#>
PREFIX dct:   <http://purl.org/dc/terms/>
PREFIX skos:  <http://www.w3.org/2004/02/skos/core#>

SELECT ?dmn1Identifier ?dmn2Identifier
       ?outputVarId ?inputVarId
       ?variableType ?sharedConcept
       ?matchType
WHERE {
  # DMN1 produces an output variable
  ?outputVar a cpsv:Output ;
             cpsv:produces ?dmn1 ;
             dct:identifier ?outputVarId ;
             dct:type ?variableType .

  # DMN2 requires an input variable of the same type
  ?inputVar a cpsv:Input ;
            cpsv:isRequiredBy ?dmn2 ;
            dct:identifier ?inputVarId ;
            dct:type ?variableType .

  FILTER(?dmn1 != ?dmn2)

  ?dmn1 a cprmv:DecisionModel ; dct:identifier ?dmn1Identifier .
  ?dmn2 a cprmv:DecisionModel ; dct:identifier ?dmn2Identifier .

  # Check for semantic matching via shared concept
  OPTIONAL {
    ?outputConcept a skos:Concept ;
                   skos:exactMatch ?sharedConcept ;
                   dct:subject ?outputVar .
    ?inputConcept  a skos:Concept ;
                   skos:exactMatch ?sharedConcept ;
                   dct:subject ?inputVar .
  }

  BIND(
    IF(?outputVarId = ?inputVarId && BOUND(?sharedConcept), "both",
    IF(?outputVarId = ?inputVarId, "exact",
    IF(BOUND(?sharedConcept), "semantic", "none")))
    AS ?matchType
  )

  FILTER(?matchType != "none")
}
```

**Critical requirements for correctness:**

1. **Type compatibility** (`dct:type` must match) — prevents `Boolean` outputs being linked to `Integer` inputs
2. **Shared concept** — both concepts must point to the **identical** third URI via `skos:exactMatch`, not just any concept
3. **`dct:subject` integrity** — the concept's `dct:subject` must correctly point to the variable URI, not a DMN URI

Post-query processing in `sparql.service.ts` expands `"both"` records into two separate entries (one `"exact"`, one `"semantic"`), so the frontend validation engine can process each match type independently:

```typescript
if (matchType === 'both') {
  results.push({ ...link, matchType: 'exact' });
  results.push({ ...link, matchType: 'semantic' });
} else {
  results.push({ ...link, matchType });
}
```

---

## Frontend validation engine

`ChainBuilder.tsx` loads semantic links once on mount (or when the endpoint changes) and stores them in `semanticLinks` state. On every chain change, `runValidation()` evaluates the current chain:

```typescript
const runValidation = () => {
  const availableOutputs = new Set<string>();
  const semanticMatches: SemanticMatch[] = [];
  const missingInputs: string[] = [];
  const drdIssues: string[] = [];

  for (let i = 0; i < chain.length; i++) {
    const dmn = chain[i];
    const prevDmn = chain[i - 1];

    for (const input of dmn.inputs) {
      // Exact match
      if (availableOutputs.has(input.identifier)) continue;

      // Semantic match
      const semanticLink = semanticLinks.find(
        link =>
          link.dmn2.identifier === dmn.identifier &&
          link.dmn1.identifier === prevDmn?.identifier &&
          link.inputVariable === input.identifier &&
          link.matchType === 'semantic'
      );

      if (semanticLink) {
        semanticMatches.push({ ... });
        drdIssues.push(`'${input.identifier}' requires semantic match`);
        continue;
      }

      // User must supply
      missingInputs.push(input.identifier);
    }

    // Add this DMN's outputs to the available set
    for (const output of dmn.outputs) {
      availableOutputs.add(output.identifier);
    }
  }

  const isDrdCompatible = drdIssues.length === 0;
  setValidationResult({ isDrdCompatible, semanticMatches, missingInputs });
};
```

The `isDrdCompatible` flag controls which save path is offered — "Save as DRD" or "Save as Sequential Template" — and whether the DRD deployment flow is triggered.

---

## React state dependency tracking

`runValidation` has a `useEffect` dependency on `[chain, userInputs, semanticLinks]`. The `semanticLinks` dependency is intentional: when the endpoint changes and new links load, validation re-runs even if the chain hasn't changed. This ensures the validation state always reflects the current endpoint's concept graph.

---

## Debugging notes

During development, a common failure mode was that semantic chains appeared to have zero semantic links despite correct SPARQL syntax. The root causes discovered through debugging were:

- **`dct:subject` pointing to the DMN URI instead of the variable URI** — the CPSV Editor at one point generated concepts with `dct:subject <.../dmn>` instead of `dct:subject <.../dmn/output/1>`. The SPARQL join then silently returned nothing.
- **Mismatched `dct:type` values** — `"Boolean"` from one agency and `"boolean"` (lowercase) from another prevented the type filter from matching. RDF datatype URIs are case-sensitive.
- **`skos:exactMatch` pointing to the concept's own URI** — a circular reference that produces no shared concept.

The validation console logs (`[Validation] ✓ DRD | X missing | 0 semantic` and `[SemanticLinks] ✓ Loaded 26 links (16 semantic)`) were added to make these failure modes visible during QA.
