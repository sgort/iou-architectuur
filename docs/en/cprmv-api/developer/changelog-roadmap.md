---
component: CPRMV
---

# Changelog & Roadmap

---

CPRMV has two version numbers ([why](ci-cd.md#two-version-numbers)). A **release** (`vYYYY.MM.N`) is what runs on production: `/health` reports it as `release`, it tags the image and it names the release's bill of materials. The **vocabulary and API version** (`0.4.3`) is the version of the CPRMV vocabulary, its specification and the API's routes and namespaces; it changes only when they do, and several releases can share it.

---

## Releases

Releases are numbered since 27 November 2026 and have no changelog of their own in the repository; each entry below is written from the release's pull requests.

### v2026.11.0 — Release Numbers, a Bill of Materials per Release, and CPRMV on GitHub (November 2026)

> How a release is cut: [CI/CD](ci-cd.md#releasing). What `/health` reports: [GET /health](../reference/api-endpoints.md#get-health). How each tier deploys itself: [VM Deployment](vm-deployment.md). The tests: [Testing](testing.md).

Vocabulary and API version **0.4.3**, unchanged. Production runs `502a351` since 27 November 2026, promoted by [#35](https://github.com/open-regels/cprmv/pull/35).

- **A release number beside the version.** A release is numbered `vYYYY.MM.N`: `.0` is the month's first release, and the count restarts each month. The number is kept in `serve_api/RELEASE`, which only a release writes; CI checks it, fails the build on anything but one line `vYYYY.MM.N`, and builds it into the image, and `/health` reports it as `release`, between `environment` and `build`. On production the image is also tagged `v2026.11.0`. Acceptance reports the last release its code is at or after, and `build.sha` says exactly what runs. No git tags, no GitHub Releases.
- **`/bump-release`.** A Claude Code command in the repository cuts a release: it reconciles the open pull requests, computes the next number, asks whether the vocabulary version changes too (it does not raise it itself), opens the release pull request into `acc` and then `acc` into `main`, checks that both production hosts report the release, and pushes `main` to GitLab, which publishes the specification. It never merges a pull request and never pushes to `acc` or `main`; a maintainer merges both.
- **A bill of materials per release.** Each release commits a CycloneDX 1.6 SBOM of the shipped Python dependencies, `docs/sbom/cprmv-api-v2026.11.0.cdx.json` (98 components), generated deterministically from the hash-locked `serve_api/requirements.txt`. A new workflow, *Release SBOM*, fails a release pull request whose SBOM does not match the requirements, and a push to `main` without a release number or its SBOM; it keeps a copy as a 90-day artifact and is not a required check. The release is in the file's name only: inside, the root component is `cprmv@0.4.3`, the vocabulary version. `cprmv-api-0.4.3.cdx.json` records what production ran before release numbers, and is byte for byte the same file, because the release changed no dependency. The image carries its own SBOM attestation in GHCR, which covers the Debian packages.
- **Developed on GitHub.** Since 26 November 2026 ([#26](https://github.com/open-regels/cprmv/pull/26), [#28](https://github.com/open-regels/cprmv/pull/28), [#31](https://github.com/open-regels/cprmv/pull/31), production at `8f01b2b`) development, issues and CI are at [open-regels/cprmv](https://github.com/open-regels/cprmv), default branch `acc`; GitLab keeps only the job that publishes the specification. Rulesets on `acc` and `main` require `audit`, `scan`, `test` and `build` before a pull request merges. Actions are pinned to commit hashes, the Python and Caddy images by digest, and both requirements files carry hashes; Renovate moves them after 14 days, and a daily `pip-audit` fails on any advisory in a shipped package. Six shipped packages with advisories were upgraded on the way, among them `fastmcp` to 4.1.8. The image moved from Docker Hub to `ghcr.io/open-regels/cprmv-api`, with a provenance attestation, and the Docker Hub Compose file is gone.
- **Each tier deploys itself.** Each tier runs on its own Azure VM, which deploys the head of its branch within minutes of the merge, checks it, and restores the previous deployment if the check fails; `cprmv.open-rules.eu` is served by the stable VM. `/health` reports the environment, the release, the commit and run the image was built from, and its digest. For this release, CI [run 21](https://github.com/open-regels/cprmv/actions/runs/45969250973) published `502a351`, the stable VM reported it running at 08:58 UTC, and `deploy` passed.
- **Tests.** pytest collects seven tests, all passing, measured on 27 November from a scratch export; the new one checks that `/health` reads the release on every request. CI run 21 passed them and 69 bats tests, 15 of them new for `scripts/read-release.sh`. The SBOM script has 75 tests of its own, which the [Release SBOM run](https://github.com/open-regels/cprmv/actions/runs/45969251022) passed; locally 74 passed and the one that runs the real CycloneDX tool was skipped, because the tool was not installed.

---

## Vocabulary and API versions

This changelog is maintained starting from CPRMV / CPRMV API v0.4.0.
Usage of earlier versions is deprecated and at own risk.
Note that CPRMV / CPRMV API still is highly subject to change.

### v0.4.3 (November 2026)

> What a RuleSet is now: [CPRMV Vocabulary](../reference/cprmv-vocabulary.md). The new sources: [Publication Repositories](../features/publication-repositories.md). The new endpoints: [API Endpoints](../reference/api-endpoints.md). The tests: [Testing](testing.md).

**v0.4.3 - CPRMV**

- Updates URIs and documentation to mention `0.4.3` instead of `0.4.2` (vocabulary namespace `https://standaarden.open-regels.nl/standards/cprmv/0.4.3#`).
- **A RuleSet is an FRBR Endeavor.** `cprmv:RuleSet` is a subclass of `frbr:Endeavor` instead of `frbroo:F1_Work`, so a rule set can be a Work, an Expression, a Manifestation or an Item; it is also a `prov:Bundle`, and `cprmv:Rule` a `prov:Entity`. `cprmv:isBasedOn` becomes a subproperty of `frbr:relatedEndeavour` (and stays one of `prov:wasDerivedFrom`).
- **Instruments.** `cprmv:Instrument` with `Standard`, `Tool` and `Method`; a `cprmv:RuleMethod` is a `cprmv:Method`.
- `cprmv:AgreementEchelon` is renamed `cprmv:NaturalEchelon`, in the vocabulary and the SHACL shapes.
- **Method modules.** A module bundles methods (`cprmvmethods:hasMethods`): new are `core.api`, `iou` (IOU Norms and Operaton), `digitaal-stelsel-omgevingswet` (DSO, with DSO as a service register), `register-overheids-organisaties` (ROO, an organisation register) and `sttr`. The Normenbrief method gives way to `iou-norms`.
- The ReSpec documentation has two new introductory chapters, a chapter per method module with links to working examples, a class diagram per OWL class, examples and links to the RDF definitions. The PDF version builds again. The Pages job no longer builds the ReSpec; it publishes the committed output (the in-CI build failed on the release merge, pipeline #821).

**v0.4.3 - CPRMV API**

- Supports CPRMV 0.4.3; serve-API and methods namespaces `https://cprmv.open-regels.nl/0.4.3/…`. The committed `serve_api/data/` is now what `make methods` generates, so `/methods` lists every acknowledged method.
- **New sources.** Organisations from the Register van Overheidsorganisaties (`ROO…`), norms from the IOU Norms API (`IOU-NORMS_…`) and STTR decision models from the DSO (`DSO_…`), each with the service and competent authority it belongs to where the source says so. A DSO request needs the caller's own DSO key in the `x-api-key` header, which the API passes on.
- **`/raw/{rule_id_path}`** returns the original publication as a download. The RuleSet no longer carries `prov:wasDerivedFrom`; `/raw` serves what it was derived from.
- **`/methods`** takes a `method_name`, and `/0.4.3/methods/{method_name}` is meant to give one method's knowledge, so that method URIs in the ReSpec resolve; it returns the node typed by that method, or the whole graph when there is none ([open-regels/cprmv#2](https://github.com/open-regels/cprmv/issues/2)).
- The EU CELLAR helper endpoints `/cellar-by-celex` and `/cellar-by-eli` are removed; `/ref` still resolves ELI references to Formex 4 on EU CELLAR.
- **MCP is reachable.** The MCP server is mounted at `/mcp/` on the API itself, after every route, and answers on all three hosts. This replaces the `combined_app` of the October fix ([standards/cprmv#31](https://git.open-regels.nl/standards/cprmv/-/work_items/31)).
- The Docker image includes `serve_api/methods/`.
- `test_get_root` expects `0.4.3`; nothing else in the tests changed. At `d597671` pytest collected 3 tests in `serve_api/test/test_serve.py` and 3 passed in 6.68 s, measured on 24 November from a scratch export on Windows with Python 3.14.3 (the pinned `requirements-dev.txt` without `uvloop`, plus `pywin32` and `colorama`); CI on Linux (pipeline #824) passed the same suite. Ten tests are still commented out; see [Testing](testing.md).

**Found while documenting it.** The `/ref` redirect carries the request's own headers back to the caller, the `x-api-key` with them ([open-regels/cprmv#1](https://github.com/open-regels/cprmv/issues/1)). [open-regels/cprmv#2](https://github.com/open-regels/cprmv/issues/2) collects the rest: `/0.4.3/methods/{method_name}` and `method_name` return the whole graph for an unknown name or for `roo` and `dso`; `/mcp` redirects to plain `http://`; IOU Norms definitions arrive as the text of a Python dictionary in the 0.4.1 namespace, and their date goes out as `valid-on` where the Linked Data Explorer reads `valid_on`; the `frbr:` prefix lacks its `#`; `cprmv:Method` is labelled "Tool"; the `AgreementEchelon` → `NaturalEchelon` rename is not announced in the upstream changelog; and the Dockerfile comment, the `/ref` docstring and a mutable default argument in `cbd_cprmv_json` are stale or fragile.

---

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
    The `serve_api/Dockerfile` on `main` does not copy `serve_api/methods/`, so an image built from it loads no rule method: every `/rules` ID answered *No supported publication repository…* and `/ref` returned 500 on all three hosts after the 0.4.2 deployment. The hosts were redeployed on 10 October 2026 with an image built from the fix in [standards/cprmv!20](https://git.open-regels.nl/standards/cprmv/-/merge_requests/20). That merge request was closed; the same line reached `main` with v0.4.3.

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
| Release numbers, a release SBOM, `/bump-release` | v2026.11.0 |
| CPRMV / CPRMV API | v0.4.3  |
| CPRMV / CPRMV API | v0.4.2  |
| CPRMV / CPRMV API | v0.4.1  |
| CPRMV / CPRMV API | v0.4.0  |
| CPRMV   | v0.3.1  |

---

### Planned

The repository's roadmap notes that it can change at any moment.

**v0.4.4 — expected by 21 December 2026**

- *CPRMV:* echelons and rule methods soft-typed with a type property, to simplify the vocabulary; method configuration layered by governance level (local, national, EU, worldwide); acknowledgement of the methods in the legal-technology typology inventory, PNA Group's iKnow as an analysis method, and more; DMN knowledge sources read as `cprmv:isBasedOn`; Operaton rulesets referenced by name.
- *CPRMV API:* every RuleSet referenced to a service with the right competent authority, for all supported methods; organisation and service catalogs in references; rule-method types keep their own class in the API; Catala, RegelSpraak, OpenFisca, Legifrance and MC/DC; `cprmv:isBasedOn` relations found automatically with ref2link and usable in references.

**v0.4.5 — expected in the first quarter of 2027**

- *CPRMV:* officially published Dutch parliamentary documents and the rulesets based on them; fully traceable examples from parliament to executed rules (Article 7a of the Dutch old-age pension law, the Flevoland home-battery subsidy, the Normenbrief, a service based on an STTR published in the DSO).
- *CPRMV API:* parliamentary documents; a cache for RuleSets, with recaching on request or when a new version appears and settings for memory and disk use; the API as a publishing node for one organisation's RuleSets, registered as that organisation's publication repository, with RuleSets signed by a key of the competent authority; security improvements.
