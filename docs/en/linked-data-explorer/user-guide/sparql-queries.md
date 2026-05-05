# Running SPARQL Queries

The SPARQL Query Editor lets you run queries directly against any configured TriplyDB endpoint and explore results as a table or interactive graph.

---

## Running a query

1. Click the search icon in the left sidebar to open the Query Editor.
2. The editor pane contains a sample query by default. You can modify it or select a different query from the library in the left panel.
3. Click **Run Query** (top right).
4. Results appear in the table below the editor.

---

## Selecting from the query library

The left panel lists pre-built queries for common DMN discovery tasks. Click any entry to load it into the editor without executing immediately, so you can review or adapt it first. The library includes:

- **Find All DMNs** — retrieves all `cprmv:DecisionModel` resources with titles and identifiers
- **Input/Output Details** — lists all input and output variables for every DMN
- **Find Chains** — finds DMN pairs where an output of one matches an input of another
- **Chain Paths** — traces multi-hop chains across the dataset
- **Complete Metadata** — retrieves the full metadata graph for a specific DMN
- **Service Rules Metadata** — retrieves `cprmv:Rule` → `eli:LegalResource` → `cpsv:PublicService` relationships

---

## Switching endpoints

The endpoint selector at the top of the configuration panel shows the active TriplyDB dataset URL. To switch:

1. Open the configuration panel (gear icon).
2. Select a preset endpoint or type a custom SPARQL endpoint URL.
3. Click **Apply**.

The active endpoint applies to both the Query Editor and the Chain Builder. Switching it reloads the DMN list in the Chain Builder.

---

## Exporting results

Click **Export CSV** below the results table to download a `.csv` file. The filename is timestamped (e.g., `sparql-results-2026-02-06.csv`). Values with commas, quotes, or newlines are escaped correctly.

---

## Graph view

If your query returns `?s ?p ?o` triple patterns, a **Graph** button appears alongside the Table button. The graph view renders an interactive D3.js force-directed diagram. Drag nodes to reposition them; use scroll to zoom. Semantic links appear as dashed green edges.

---

## Writing queries

The endpoint follows SPARQL 1.1. Key prefixes for DMN discovery:

```sparql
PREFIX cprmv: <https://cprmv.open-regels.nl/0.3.0/>
PREFIX cpsv:  <http://www.w3.org/ns/regorg#>
PREFIX dct:   <http://purl.org/dc/terms/>
PREFIX skos:  <http://www.w3.org/2004/02/skos/core#>
PREFIX ronl:  <https://regels.overheid.nl/ontology#>
PREFIX schema: <http://schema.org/>
```

Example — find all DMNs with their input variable counts:

```sparql
PREFIX cprmv: <https://cprmv.open-regels.nl/0.3.0/>
PREFIX dct:   <http://purl.org/dc/terms/>
PREFIX cpsv:  <http://www.w3.org/ns/regorg#>

SELECT ?identifier ?title (COUNT(?input) AS ?inputCount)
WHERE {
  ?dmn a cprmv:DecisionModel ;
       dct:identifier ?identifier ;
       dct:title ?title .
  OPTIONAL {
    ?input a cpsv:Input ;
           cpsv:isRequiredBy ?dmn .
  }
}
GROUP BY ?identifier ?title
ORDER BY ?identifier
```
