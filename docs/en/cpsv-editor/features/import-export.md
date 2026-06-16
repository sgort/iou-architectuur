# Import, Export & Live Preview

---

## Import

The editor can import existing `.ttl` files, populating all tabs from the imported data. This enables round-trip editing: export a service definition, share it, have a colleague edit it, then import the updated file. No data is lost in the cycle.

The import system uses vocabulary configuration to recognise entities by their RDF type (`cpsv:PublicService`, `eli:LegalResource`, `cprmv:TemporalRule`, etc.) and maps properties to editor fields via a configurable alias table. This means the editor can import Turtle files that use variant vocabulary prefixes or alternative property names and still parse them correctly. Legacy types and namespaces are normalised on import — `ronl:TemporalRule`/`ronl:ParameterWaarde`, the `cprmv/0.3.0/` namespace, and the organisation's legacy `cv:spatial` (read alongside the current `dct:spatial`) all round-trip cleanly.

**CPRMV 0.4.1 API import.** Beyond Turtle, the CPRMV (Policy) tab's **Import JSON** accepts the CPRMV 0.4.1 Rules API output — an array of `cprmv:RuleSet` objects with nested `…#hasPart` maps — flattening nested sub-rules into the editor's rule model. Legacy 0.3.0 and flat-array exports are tolerated too.

**DMN preservation.** When a Turtle file contains DMN blocks (`cprmv:DecisionModel`, `cpsv:Input`, `cprmv:DecisionRule`), those blocks are detected and preserved verbatim in the exported output. The DMN tab displays an imported-state notice. On re-export the preserved blocks are appended after a conformance-only normalisation pass (v1.10.2) that injects missing `dct:title`/`dct:description` on Decision Rules and repoints a `cpsv:implements` that targets the service to the legal resource — additive edits only, so deployed decision logic is never modified.

**IRI safety.** Generated NL-SBB concept URIs, `dct:subject` links and `skos:exactMatch` values are sanitised so whitespace becomes underscores and IRI-illegal characters are percent-encoded (v1.10.2). A downloaded `.ttl` therefore parses under a strict (SHACL) parser and re-imports cleanly.

---

## Export

Clicking **Download TTL** generates the complete Turtle output for all tabs and triggers a browser download. The filename is derived from the service identifier.

The export always includes the full set of namespace declarations, all populated entities, and — when present — the preserved DMN blocks. Export and re-import of the same file produces identical output (round-trip fidelity).

---

## Live preview

The preview panel shows the generated Turtle in real time as you type, with syntax highlighting and line numbering. It can be toggled on and off via the **Show Preview** button in the header. When visible, the application switches to a split-screen layout with the form on the left and the Turtle preview on the right.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Split-screen layout with the Organization tab active on the left and the live TTL preview panel showing the generated Turtle on the right, with the line count visible at the bottom of the preview](../../assets/screenshots/cpsv-editor-main-ui.png)
  <figcaption>Split-screen layout with the Organization tab active on the left and the live TTL preview panel showing the generated Turtle on the right</figcaption>
</figure>

A **Copy** button in the preview panel copies the full Turtle content to the clipboard without downloading a file.
