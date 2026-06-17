# SHACL Shape Diagrams

Feasibility exploration: converting the SHACL node shapes from the [Linked Data Explorer](../../../linked-data-explorer/index.md) backend directly into embedded class diagrams in these reference docs.

The conversion script is operational and `.graphml` files have been generated. The remaining step is a one-time manual export from yEd.

---

## Pipeline

``` mermaid
flowchart LR
    A[Source] --> B[rdflib]
    B --> C[Saxon]
    C --> D[.graphml]
    D --> E[yEd]
    E --> F[Markdown]

    class A source
    class B,C,D done
    class E,F pending

    classDef source fill:#f3f4f6,stroke:#9ca3af,color:#374151
    classDef done fill:#d1fae5,stroke:#6ee7b7,color:#065f46
    classDef pending fill:#fef3c7,stroke:#fcd34d,color:#92400e
```

---

## Status

| Step | Component | Status | Notes |
|---|---|---|---|
| Source | `.ttl` Turtle files | ✅ Done | `cprmv.shacl.ttl`, `cpsv-ap-SHACL.ttl` |
| Step 1 | rdflib 7.6.0 | ✅ Done | Turtle → RDF/XML; no extra deps beyond `pip install rdflib` |
| Step 2 | saxonche + `rdf2graphml.xsl` | ✅ Done | RDF/XML → GraphML via XSLT 2.0; `rdf2graphml.xsl` patched for `sh:path` fallback |
| Output | `.graphml` files | ✅ Done | Two files committed to `docs/assets/diagrams/` |
| Step 3 | yEd Graph Editor | ⏳ Pending | Installed (free); SVG export not yet performed |
| Embed | Markdown image tags | ⏳ Pending | Blocked on step 3 |

---

## How to run

From the `iou-architectuur` root:

```bash
python shacl_to_graphml.py <input.ttl> <output.graphml>
```

**Examples (Windows):**

```bat
REM CPRMV 0.4.1
python shacl_to_graphml.py ^
  ..\linked-data-explorer\packages\backend\shapes\cprmv\0.4.1\cprmv.shacl.ttl ^
  docs\assets\diagrams\cprmv-shacl.graphml

REM CPSV-AP 3.2.0
python shacl_to_graphml.py ^
  ..\linked-data-explorer\packages\backend\shapes\cpsv-ap\3.2.0\cpsv-ap-SHACL.ttl ^
  docs\assets\diagrams\cpsv-ap-shacl.graphml
```

The script handles:

- Missing prefix declarations in the SHACL source (`skos:`, `schema:`, `dct:`, etc.) via a built-in lookup table
- `sh:name` injection for property nodes that only carry `sh:path`
- XSLT 2.0 transformation via saxonche (Saxon-HE Python binding for `rdf2graphml.xsl`)

---

## Generated files

| File | Nodes | Edges | Source SHACL |
|---|---|---|---|
| `docs/assets/diagrams/cprmv-shacl.graphml` | 19 | 8 | CPRMV 0.4.1 |
| `docs/assets/diagrams/cpsv-ap-shacl.graphml` | 32 | 85 | CPSV-AP 3.2.0 |

---

## Remaining steps

1. Open `docs/assets/diagrams/cprmv-shacl.graphml` in yEd (File → Open).
2. Apply **Layout → Hierarchical** (default settings, click OK).
3. **File → Export** → select SVG → save as `docs/assets/diagrams/cprmv-shacl.svg`.
4. Repeat for `cpsv-ap-shacl.graphml` → `cpsv-ap-shacl.svg`.
5. Add image tags to this page below the pipeline section:

    ```markdown
    ![CPRMV 0.4.1 SHACL shapes](../../assets/diagrams/cprmv-shacl.svg)
    ![CPSV-AP 3.2.0 SHACL shapes](../../assets/diagrams/cpsv-ap-shacl.svg)
    ```

---

## Dependencies

| Dependency | Install | Purpose |
|---|---|---|
| rdflib | `pip install rdflib` | Turtle parse and RDF/XML serialisation |
| saxonche | `pip install saxonche` | XSLT 2.0 processor (Saxon-HE Python binding) |
| yEd | Free — yworks.com | Hierarchical auto-layout and SVG export |
