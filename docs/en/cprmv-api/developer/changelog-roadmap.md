# Changelog & Roadmap

---

## Changelog

### v0.4.0 — Initial Release (February 2026)

This changelog is going to be maintained starting from CPRMV / CPRMV API v0.4.0.
Usage of earlier versions is deprecated and at own risk.
Note that CPRMV / CPRMV API still is highly subjected to change

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
| CPRMV   | v0.4.0  |
| CPRMV   | v0.3.1  |

---

### Planned

### v0.4.x — Features & ReSpec documentation

**v0.4.1 — Respec documentation**

- Documentation on properties in the ReSpec documentation
- Improved class diagram layout in the ReSpec documentation
- Examples and link to RDF definitions in the ReSpec documentation
- Adds a property “:publication-location” (or similar) which refers to the location a RuleSet is officially published (which is something different from :isBasedOn)

**v0.4.1 - CPRMV API**

- /cellar-by-celex endpoint : redirects to the output of CELLAR instead of giving the user a URL to CELLAR
- /cellar-by-eli endpoint : new variant of /cellar-by-celex which accepts a full ELI URI as argument. Also redirecting to output of CELLAR.
- /ref endpoint : new version which accepts supported types of references, currently being ELI and Juriconnect.. For the CPRMV API style reference one can just use the /rules endpoint
- Link to /respec section from within the /docs section
- The /rules endpoint allows for retrieving the raw unprocessed source (the whole ruleset, not transformed into a CPRMV ruleset if the source isn’t a CPRMV ruleset)
- The /rules endpoint adds :publication-location property to RuleSet’s with an URI’s as value (This will be the link to repository.overheid.nl in case for BWB,CVDR, an ELI reference in case of Formex 4 (these are seen as root sources for now). In the case of DMN it is the URI to the Operaton server
- Fix escaping of quotes and newlines in transformations to RDF, which up until 0.4.1 can cause some sources to fail to load
- Improved and more complete support for BWB, CVDR, Formex 4 and DMN 1.3 standards through usage of the existing XML Schema’s independent from XSL stylesheets (CPRMV uses a generic single stylesheet for all XML based standards which are constrained through schema checking)
- Adds (basic) support for using the CPRMV API as MCP server

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
