---
component: CPRMV
---

# Changelog & Roadmap

---

## Changelog

This changelog is maintained starting from CPRMV / CPRMV API v0.4.0.
Usage of earlier versions is deprecated and at own risk.
Note that CPRMV / CPRMV API still is highly subject to change.

### v0.4.2 (October 2026)

> How the API now finds its sources: [Architecture](architecture.md). The vocabulary: [CPRMV Vocabulary](../reference/cprmv-vocabulary.md). The tests: [Testing](testing.md).

**v0.4.2 - CPRMV**

- Updates URIs and documentation to mention `0.4.2` instead of `0.4.1` (vocabulary namespace `https://standaarden.open-regels.nl/standards/cprmv/0.4.2#`).
- **Echelons.** A `cprmv:Echelon` and six subclasses — Agreement, Semantic, Ontologic, Logic, Operable and Support — to which rule methods can be related, with `cprmv:refinesTowards` and `cprmv:refinesFrom` between them.
- **Acknowledgement of services and organisations.** `OrganisationRegister`, `ServiceRegister`, `OrganisationCatalog`, `ServiceCatalog`, `AcknowledgedOrganisation` and `AcknowledgedService`, related by `cprmv:acknowledges`, so that a catalog published in a register can act as an official publication method.
- `cprmv:SerialisationMethod` is added, and `ReferenceMethod` (previously misspelled `ReferencenMethod`) becomes a subclass of `PublicationMethod`.
- **The method knowledge is split into modules**, one folder per method under `rdf/0.4.2/methods/`. New acknowledged methods include Catala, OpenFisca, ALEF with RegelSpraak, MC/DC as a test method, Legifrance and DSO as publication methods, STTR, the Normenbrief and RegelRecht; NRML is removed.
- **SHACL without recursion.** The recursive `hasPart` list shape is replaced by a sequence-path shape, and the API's output for BWB, CVDR, DMN and Formex 4 validates against the shapes — DMN and Formex 4 with placeholder `validFrom` and `isOutputOf` values for now. `id` and `comment` accept language-tagged strings.
- The ReSpec documentation gains generated chapters on the methods and the API, and `npm run build` creates the folders it writes to. The deprecated `example/` and `tools/` folders are removed.

**v0.4.2 - CPRMV API**

- **Rule methods are plugins.** Each publication and reference method is a Python module in `serve_api/methods/`, loaded at startup by `load_methods()` and configured from its RDF description; the detection and transformation functions that lived in `serve.py` are gone.
- **MCP through FastMCP** at `/mcp`, replacing `fastapi-mcp`. In the current deployment `/mcp` answers 404 — the MCP app is built before the routes it should expose, and the container serves the plain app ([standards/cprmv#31](https://git.open-regels.nl/standards/cprmv/-/work_items/31)).
- Python 3.14; the package versions are unpinned in `pyproject.toml` and locked in `requirements.txt`, with a script to refresh them.
- Updates URIs and documentation to mention `0.4.2` instead of `0.4.1` (serve-API and methods namespaces `https://cprmv.open-regels.nl/0.4.2/…`).
- Ten of the thirteen API tests are disabled while they are rewritten for the plugin structure; see [Testing](testing.md).

!!! warning "The released image could not load its methods"
    The `serve_api/Dockerfile` on `main` does not copy `serve_api/methods/`, so an image built from it loads no rule method: every `/rules` ID answered *No supported publication repository…* and `/ref` returned 500 on all three hosts after the 0.4.2 deployment. The hosts were redeployed on 10 October 2026 with an image built from the fix in [standards/cprmv!20](https://git.open-regels.nl/standards/cprmv/-/merge_requests/20), which is not yet merged.

---

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
| CPRMV / CPRMV API | v0.4.2  |
| CPRMV / CPRMV API | v0.4.1  |
| CPRMV / CPRMV API | v0.4.0  |
| CPRMV   | v0.3.1  |

---

### Planned

The repository's roadmap notes that it can change at any moment.

**v0.4.3 — expected by 15 November 2026**

- *CPRMV:* a RuleSet as an FRBR Expression as well as a Work; officially published Dutch parliamentary documents and the rulesets based on them; fully traceable examples from parliament to executed rules (Article 7a of the Dutch old-age pension law, the Flevoland home-battery subsidy, the Normenbrief, a service based on an STTR published in the DSO); examples and links to the RDF definitions in the ReSpec; PNA Group's iKnow as an analysis method; DMN knowledge sources read as `cprmv:isBasedOn`; Operaton rulesets referenced by name.
- *CPRMV API:* every RuleSet referenced to a service with its competent authority; `/rules` finding multiple published rulesets and returning references to them; organisation and service catalogs in references; basic support for DSO (STTR), MC/DC test sets, RegelSpraak, Legifrance, Catala and OpenFisca sources; `cprmv:isBasedOn` relations found automatically with ref2link and usable in references.

**v0.4.4 — expected by 21 December 2026**

- *CPRMV:* descriptions and names of concepts revised after feedback from expert communities (SEMIC, NORA and others).
- *CPRMV API:* a cache for RuleSets, with recaching on request or when a new version appears and settings for memory and disk use; the API as a publishing node for one organisation's RuleSets, registered as that organisation's publication repository, with RuleSets signed by a key of the competent authority; security improvements.
