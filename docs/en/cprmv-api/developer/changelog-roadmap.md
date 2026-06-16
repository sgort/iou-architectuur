# Changelog & Roadmap

---

## Changelog

This changelog is maintained starting from CPRMV / CPRMV API v0.4.0.
Usage of earlier versions is deprecated and at own risk.
Note that CPRMV / CPRMV API still is highly subject to change.

### v0.4.1 (June 2026)

**v0.4.1 - CPRMV**

- Updates URIs and documentation to mention `0.4.1` instead of `0.4.0` (vocabulary namespace `https://standaarden.open-regels.nl/standards/cprmv/0.4.1#`).
- `cprmv:RuleSet` is now a subclass of **FRBR Work** (`frbroo:F1_Work`) instead of `eli:LegalResource`: a formalisation such as a business rule is not in itself a legal resource in the ELI sense (note `eli:LegalResource` is itself a subclass of FRBR Work).
- `cprmv:isBasedOn` is now a subproperty of `frbroo:R2_is_derivative_of` instead of `eli:based_on`; it remains a subproperty of `prov:wasDerivedFrom`.
- Documentation on properties added to the ReSpec specification.
- Class diagram in the ReSpec docs now uses the Elk layout engine (rectangular edges) via PlantUML instead of Graphviz.
- Fixes publication paths in the ReSpec document.
- Adds a PDF version of the ReSpec (built with pandoc, committed to the repository).
- `npm run build` (and `full-package.json`, which also generates the PDF and runs shaclgen) now also updates the ReSpec folder bundled with the CPRMV API.

**v0.4.1 - CPRMV API**

- Updates URIs and documentation to mention `0.4.1` instead of `0.4.0` (serve-API/methods namespaces `https://cprmv.open-regels.nl/0.4.1/…`).
- `/ref` endpoint reworked: the reference method is **auto-detected** from a single `reference` query parameter (the `/ref/{referencemethod}/{reference}` path form is gone). Now (partly) supports Juriconnect, ELI to EU CELLAR, the CPRMV API `/rules` rule-id path, and an experimental ELI style for NL (BWB/CVDR) references.
- Bugfix: invalid arguments in a Juriconnect reference no longer cause an internal server error.
- `/cellar-by-celex` now **redirects** to the CELLAR output instead of returning the CELLAR URL as text.
- New `/cellar-by-eli` helper — works like `/cellar-by-celex` but accepts ELI references (only those explicitly linked to EU CELLAR documents; partial ELIs do not resolve).
- Fixes a quote-escaping bug for certain BWB resources.
- `/rules` always returns a `cprmv:RuleSet` with at least the selected `cprmv:Rule` as part of it, so RuleSet-level properties always travel with the rule.
- The RuleSet instance returned by `/rules` now lives in the `cprmv.open-regels.nl` / `operaton.open-regels.nl` namespace instead of `opencatalogi.open-regels.nl`.
- `/rules` automatically adds a provenance link to the source publication on BWB, CVDR, FMX4 and DMN RuleSets (`prov:wasDerivedFrom`, the superproperty of `cprmv:isBasedOn`).
- `/rules` `unformat` now applies before serializing to **any** requested format (e.g. rdflib's `n3`), not only `cprmv-json`.
- `/rules` transforms and dumps JSON in UTF-8 encoding.
- Retrieving DMN files is now documented in the `/rules` Swagger docs.
- Adds (basic) support for using the CPRMV API as an **MCP server** (`/mcp`).

---

### v0.4.0 — Initial Release (February 2026)

**v0.4.0 - CPRMV**

- More elaborated and updated RDFS/OWL/SHACL specification of CPRMV. Adds several new classes like types of methods. Adds start for alignment with ELI.
- Changes the official cprmv URI to one that resolves to the respective documentation
- Normative section generated from RDFS/OWL/SHACL in the ReSpec documentation
- Generated class diagram in ReSpec documentation

**v0.4.0 - CPRMV API**

- bugfixes around support for BWB schema (now supports circulaire’s)
- Adds /respec section hosting the respec documentation (besides the official URI)
- Adds /ref endpoint which is going to support all reference methods (but currently only implements juriconnect at a basic level)
- Allows for retrieving DMN 1.3 rulesets published in acknowledged (in value list in cprmvmethods.ttl) Operaton servers (currently only operaton.open-regels.nl)

---

## Roadmap

### Completed

| Feature | Version |
| ------- | ------- |
| CPRMV / CPRMV API | v0.4.1  |
| CPRMV / CPRMV API | v0.4.0  |
| CPRMV   | v0.3.1  |

---

### Planned

### v0.4.x — Features & documentation

**v0.4.x — CPRMV / ReSpec documentation (carried over)**

- Examples and link to RDF definitions in the ReSpec documentation.
- Adds a `:publication-location` (or similar) property referring to where a RuleSet is officially published (distinct from `:isBasedOn`). On a RuleSet this would be `repository.overheid.nl` for BWB/CVDR, an ELI reference for Formex 4, and the Operaton server URI for DMN.

**v0.4.x — CPRMV API (carried over)**

- Link to the `/respec` section from within the `/docs` section.
- The `/rules` endpoint allows retrieving the raw unprocessed source (the whole ruleset, not transformed into a CPRMV ruleset when the source isn't one).
- Improved and more complete support for BWB, CVDR, Formex 4 and DMN 1.3 by using the existing XML Schemas independently from XSL stylesheets (a generic single stylesheet for all schema-constrained XML standards).

**v0.4.2 - CPRMV**

- Improved and more complete cprmv methods knowledge / value lists
- Better defined relation with with official organisation registers (EU)
- Start of a CPRMV-NL variant, based on MIM and CPSV-NL and the ROO
- Adds acknowledgement of RegelSpraak as a FormalisationMethod and ALEF as tooling related to it
- Adds acknowledgement of OpenFisca as a FormalisationMethod and tooling related to it

**v0.4.2 - CPRMV API**

- Support for using the /rules endpoint to find multiple published ruleset’s, which is a modus separate from referencing a single published ruleset. In the case of multiple ruleset’s the CPRMV API returns a list with references RuleSets which can be used with the CPRMV API to retrieve them.
- Support for utilizing organisation and product and services catalog information within references in the /rules endpoint.
- Support for utilizing :isBasedOn relations within references in the /rules endpoint. It should be possible to refer to.
- Support for using ELI and where possible juriconnect references for other publication methods than typically supported by these reference types.
- Adds a /browser section offering a minimal viable web based GUI to browse organisations, services and rulesets. Offers a searchable tree control at the left and a resource viewer at the right from which should offer users to start processes related to the resources (as defined by services)
- Adds user friendly access to method knowledge in the /browser section relating to defined services for governance on value lists
- Adds basic support for RegelSpraak sources (depending on where these will get published)
