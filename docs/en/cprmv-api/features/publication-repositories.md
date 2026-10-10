---
component: CPRMV
---

# Publication Repositories

The CPRMV API supports four publication methods. Each is acknowledged in the `cprmvmethods:publicationmethods` list of `data/cprmvmethods.ttl` and implemented as a Python class in `serve_api/methods/`. For every request, `detect_publication` in `serve.py` walks that list in order and asks each method to interpret the rule set identifier against its `cprmv-serve:normalized-id-format`; the first method that parses it handles the request.

| Method id | Python class (module) | Built from |
|---|---|---|
| `repository-overheid-nl-bwb` | `repository_overheid_nl_bwb` (`repository_overheid_nl.py`) | `frbr_sru` + `bwb` |
| `repository-overheid-nl-cvdr` | `repository_overheid_nl_cvdr` (`repository_overheid_nl.py`) | `frbr_sru` + `cvdr` |
| `eucellar-fmx4` | `eucellar_fmx4` (`eucellar.py`) | `core_web` + `fmx4` |
| `operaton.open-regels.nl` | `operaton_open_regels_nl` (`open_regels_nl.py`) | `operaton` (`core_web` + `dmn13`) |

---

## How methods are loaded

At start-up `load_methods()` imports every module in `serve_api/methods/` and instantiates each class whose name begins or ends with the module name, provided `get_method_config` finds a method with that id in the acknowledged `cprmvmethods:rulemethods` list. Method ids are matched with `.` and `-` replaced by `_`, so `operaton.open-regels.nl` becomes `operaton_open_regels_nl`. The configuration of parent methods (their RDF types, up to ten levels) is copied onto the loaded method, so a repository method inherits, for example, the `cprmv-serve:xslt` of its serialisation method.

The building blocks are:

| Base | Role |
|---|---|
| `PublicationMethod` | Normalises the identifier, parses it against the configured formats, and triggers the `latest` lookup |
| `core_web` | Downloads the publication from `cprmv-serve:repository-publication-location-format` |
| `frbr_sru` | Finds the version valid on a date through an SRU service, configured with `frbr-sru:url` and the `frbr-sru:response-*` terms |
| `SerialisationMethod` / `core_xml` | Transforms the raw publication to CPRMV Turtle with the XSLT named in `cprmv-serve:xslt` |
| `bwb`, `cvdr`, `fmx4`, `dmn13` | Serialisation methods, each naming its XSLT |

`frbr-sru:` is the namespace `https://cprmv.open-regels.nl/0.4.2/methods/frbr-sru/`; `cprmv-serve:` is `https://cprmv.open-regels.nl/0.4.2/serve-api/`.

Method definitions are maintained per method in `rdf/0.4.2/methods/<method>/method.ttl`; `make methods` concatenates them into `serve_api/data/cprmvmethods.ttl` and copies the XSLT files to `serve_api/data/`. The API reads only the copy in `data/`. That copy is older than the method folders — it still contains NRML, which has been removed from `rdf/0.4.2/methods/`, and lacks method nodes added since, such as `sttr` and `normenbrief` ([standards/cprmv#31](https://git.open-regels.nl/standards/cprmv/-/work_items/31)). `/methods` therefore lists what is in `data/cprmvmethods.ttl`, not the full contents of `rdf/0.4.2/methods/`.

---

## BWB — Basis Wettenbestand (Dutch national law)

The BWB repository holds consolidated versions of Dutch national legislation. The API supports three identifier forms:

| Form | Example | Behaviour |
|---|---|---|
| `{BWBID}_{DATE}_{INDEX}` | `BWBR0015703_2025-07-01_0` | Fetches the specific indexed publication |
| `{BWBID}_{DATE}_latest` | `BWBR0015703_2025-07-02_latest` | SRU search for version valid on that date |
| `{BWBID}` | `BWBR0015703` | SRU search for version valid today |

For `latest` and bare-ID forms, the API queries the BWB SRU endpoint (`frbr-sru:url`):

```
https://zoekservice.overheid.nl/sru/Search?x-connection=BWB&operation=searchRetrieve
  &version=2.0&maximumRecords=1
  &query=dcterms.identifier=BWB{rulesetid} and overheidbwb.geldigheidsdatum={valid-on}
```

The response identifies the publication XML at:

```
https://repository.officiele-overheidspublicaties.nl/bwb/BWB{rulesetid}/{date}_{index}/xml/BWB{rulesetid}_{date}_{index}.xml
```

Transform: `bwb2cprmv.xsl` (method `bwb`) — converts BWB `toestand` XML structure (hoofdstuk / paragraaf / artikel / lid / li) to nested CPRMV Turtle with `cprmv:id`, `cprmv:definition`, and `cprmv:hasPart` relations. The resulting rule set carries `cprmv:hasMethod cprmvmethods:bwb`.

The repository serves an incomplete TLS certificate chain; the API bundles the missing certSIGN Web CA intermediate (`serve_api/certs/`) and adds it to its SSL context, so downloads from `repository.officiele-overheidspublicaties.nl` verify.

---

## CVDR — Centrale Voorziening Decentrale Regelgeving (municipal regulations)

The CVDR repository holds regulations from Dutch municipalities, provinces, and water boards. Identifier forms:

| Form | Example | Behaviour |
|---|---|---|
| `{CVDRID}_{INDEX}` | `CVDR712517_1` | Fetches the specific indexed version |
| `{CVDRID}_{DATE}_latest` | `CVDR712517_2025-07-02_latest` | SRU search for version valid on that date |
| `{CVDRID}` | `CVDR712517` | SRU search for version valid today |

SRU endpoint used for `latest`/bare forms:

```
https://zoekservice.overheid.nl/sru/Search?x-connection=cvdr&operation=searchRetrieve
  &version=2.0&maximumRecords=1
  &query=dcterms.identifier=CVD{rulesetid}_* and overheidrg.inwerkingtredingDatum<={valid-on}
  sortby overheidrg.inwerkingtredingDatum/descending
```

Transform: `cvdr2cprmv.xsl` (method `cvdr`).

---

## EU CELLAR — European Union legislation (Formex v4)

EU legislation in Formex v4 format is fetched from the Publications Office of the EU. Identifier form:

| Form | Example |
|---|---|
| `CFMX4{CELLAR_ID}_{ITEM_ID}` | `CFMX483e4752e-f2e5-11e8-9982-01aa75ed71a1.0017.02_DOC_2` |

Publication URL:

```
https://publications.europa.eu/resource/cellar/{rulesetid}/{docid}
```

Date-based version resolution is not supported for CELLAR publications.

Transform: `fmx42cprmv.xsl` (method `fmx4`). The stylesheet sets `cprmv:hasMethod` to `cprmvmethods:cellarfmx4`, an id that is not defined in the methods registry.

---

## DMN 1.3 via Operaton (experimental)

Decision models deployed to the Operaton engine at `operaton.open-regels.nl` can also be fetched. The identifier embeds the Operaton deployment ID and resource ID, separated by the letter `R`:

| Form | Example |
|---|---|
| `DMN1.3_{deploymentid}R{resourceid}_{date}_{index}` | `DMN1.3_e62cb254-0e74-11f1-a5e9-f68ed60940f5Re62cb255-0e74-11f1-a5e9-f68ed60940f5_2026-01-01_1` |

Publication URL:

```
https://operaton.open-regels.nl/engine-rest/deployment/{deploymentid}/resources/{resourceid}/data
```

Transform: `dmn13operaton2cprmv.xsl` (method `dmn13`). The result is a `cprmv:DecisionModel`.

!!! warning "Experimental"
    The DMN 1.3 method is explicitly marked experimental. The `operaton` module splits the identifier on the letter `R`, so it works only when the deployment and resource IDs contain no upper-case `R` themselves.

---

## Analysis methods (non-publication)

`cprmvmethods.ttl` also acknowledges analysis methods that are not publication endpoints — these describe how a rule set was analysed but do not provide publication URLs:

| Method | ID |
|---|---|
| Law Analysis / Wetsanalyse (JAS) | `cprmvmethods:jas` |
| Calculemus / FLINT | `cprmvmethods:flint` |

These are used to annotate rule sets via `cprmv:hasMethod` in TTL files. They have no Python module, so the API does not use them for retrieval.
