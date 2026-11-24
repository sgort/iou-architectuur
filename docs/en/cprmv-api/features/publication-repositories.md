---
component: CPRMV
---

# Publication Repositories

The CPRMV API acknowledges eleven publication methods in the `cprmvmethods:publicationmethods` list of `data/cprmvmethods.ttl`; ten have a Python class in `serve_api/methods/` and so can be fetched (RegelRecht has none). For every request, `detect_publication` in `serve.py` walks that list in order and asks each method to interpret the rule set identifier against its `cprmv-serve:normalized-id-format`; the first method that parses it handles the request.

| Method id | Python class (module) | Built from |
|---|---|---|
| `repository-overheid-nl-bwb` | `repository_overheid_nl_bwb` (`repository_overheid_nl.py`) | `frbr_sru` + `bwb` |
| `repository-overheid-nl-cvdr` | `repository_overheid_nl_cvdr` (`repository_overheid_nl.py`) | `frbr_sru` + `cvdr` |
| `eucellar-fmx4` | `eucellar_fmx4` (`eucellar.py`) | `core_web` + `fmx4` |
| `operaton.open-regels.nl` | `operaton_open_regels_nl` (`open_regels_nl.py`) | `iou_operaton` (`operaton` = `core_web` + `dmn13`) |
| `norms-backend.linkeddata.open-regels.nl` | `norms_backend_linkeddata_open_regels_nl` (`open_regels_nl.py`) | `iou_norms` (`core_web` + `core_json`) |
| `dso` | `dso` (`dso.py`) | `core_api` + `sttr` |
| `dso-service-register` | `dso_service_register` (`dso.py`) | `ServiceRegister` + `core_api` + `core_json` |
| `roo`, `roo-uri`, `roo-catalogus` | `roo`, `roo_uri`, `roo_catalogus` (`roo.py`) | `OrganisationRegister` + `core_api` + `core_json` |

---

## How methods are loaded

At start-up `load_methods()` imports every module in `serve_api/methods/` and instantiates each class whose name begins or ends with the module name, provided `get_method_config` finds a method with that id in the acknowledged `cprmvmethods:rulemethods` list. Method ids are matched with `.` and `-` replaced by `_`, so `operaton.open-regels.nl` becomes `operaton_open_regels_nl`. The configuration of parent methods (their RDF types, up to ten levels) is copied onto the loaded method, so a repository method inherits, for example, the `cprmv-serve:xslt` of its serialisation method.

The building blocks are:

| Base | Role |
|---|---|
| `PublicationMethod` | Normalises the identifier, parses it against the configured formats, and triggers the `latest` lookup; reads `cprmv-serve:utilizes` to find the service or organisation register a method consults |
| `core_web` | Downloads the publication from `cprmv-serve:repository-publication-location-format` |
| `core_api` | Downloads from an API, with the HTTP method (`core-api:http-method`, `GET` or `POST`) and request headers (`core-api:api-headers`) from the configuration, passing the caller's `x-api-key` on where configured |
| `frbr_sru` | Finds the version valid on a date through an SRU service, configured with `frbr-sru:url` and the `frbr-sru:response-*` terms |
| `SerialisationMethod` / `core_xml` | Transforms the raw publication to CPRMV Turtle with the XSLT named in `cprmv-serve:xslt` |
| `core_json` | Turns a JSON publication into a RuleSet, one `cprmv:Rule` per key, nested with `cprmv:hasPart` |
| `bwb`, `cvdr`, `fmx4`, `dmn13`, `sttr` | Serialisation methods, each naming its XSLT (`sttr2cprmv.xsl` for STTR) |
| `OrganisationRegister`, `ServiceRegister` | Base classes for a register a method can consult |

`frbr-sru:` is the namespace `https://cprmv.open-regels.nl/0.4.3/methods/frbr-sru/`; `cprmv-serve:` is `https://cprmv.open-regels.nl/0.4.3/serve-api/`.

Method definitions are maintained per method module in `rdf/0.4.3/methods/<module>/method.ttl`; `make methods` concatenates them into `serve_api/data/cprmvmethods.ttl` and copies the XSLT files to `serve_api/data/`. The API reads only the copy in `data/`. The committed copy is what `make methods` produces, so `/methods` lists the full contents of `rdf/0.4.3/methods/`.

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

Decision models deployed to the Operaton engine at `operaton.open-regels.nl` can also be fetched (method `operaton.open-regels.nl`, an `iou-operaton` method of the IOU module). The identifier embeds the Operaton deployment ID and resource ID, separated by the letter `R`:

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

## IOU Norms (open-regels.nl)

Norms are fetched from the IOU Norms API, the Linked Data Explorer's `/v2/norms`, on the IOU showcase (method `norms-backend.linkeddata.open-regels.nl`, an `iou-norms` method).

| Form | Example |
|---|---|
| `IOU-NORMS_{rulesetid}_{date}_{index}` | `IOU-NORMS_BWBR0015703_2026-01-01_1` |

Publication URL:

```
https://acc.backend.linkeddata.open-regels.nl/v2/norms/?rulesetid={rulesetid}&valid-on={date}
```

The date and index must be present but do not select a version: the API sends the date as `valid-on`, while the Norms API reads `valid_on`, so the norms valid today are returned. The URL points at the acceptance backend, also from production ([open-regels/cprmv#2](https://github.com/open-regels/cprmv/issues/2)).

Each norm becomes a rule set member with its own `cprmv:id` and the type the Norms API gives it — today `https://standaarden.open-regels.nl/standards/cprmv/0.4.1#Rule`, the namespace the Norms API answers in. Its other fields are kept together, as the text of a Python dictionary, in one `cprmv:definition` ([open-regels/cprmv#2](https://github.com/open-regels/cprmv/issues/2)).

---

## Register van Overheidsorganisaties (ROO)

Organisations are fetched from the Register van Overheidsorganisaties API (`https://api-organisaties.overheid.nl/v1/`), in three forms:

| Form | Example | Publication URL |
|---|---|---|
| `ROO.{key}={rulesetid}_{date}_{index}` (method `roo`) | `ROO.organisatiecode=gm1926_2026-01-01_1` | `…/overheidsorganisaties/identificatie-uitgebreid?{key}={rulesetid}` |
| `ROOURI{uri}_{date}_{index}` (method `roo-uri`), with the URL-encoded TOOI URI | `ROOURIhttps%3A%2F%2Fidentifier.overheid.nl%2Ftooi%2Fid%2Fgemeente%2Fgm1926_2026-01-01_1` | `…/overheidsorganisaties/{uri}` |
| `ROO_{date}_{index}` (method `roo-catalogus`) — the whole register, a slow request | `ROO_2026-01-01_1` | `…/overheidsorganisaties` |

The date and index must be present but are not used. The JSON answer becomes a RuleSet through `core_json`, with one `cprmv:Rule` per field. Its `cprmv:isOutputOf` is a public service of the Ministry of the Interior (BZK), with the API as its channel.

---

## DSO (STTR)

STTR decision models (toepasbare regels) are fetched from the Digitaal Stelsel Omgevingswet (method `dso`):

| Form | Example |
|---|---|
| `DSO_{rulesetid}_{date}_{index}` | `DSO_14_2026-01-01_1` |

Publication URL:

```
https://service.omgevingswet.overheid.nl/publiek/toepasbare-regels/api/toepasbareregelsuitvoerengegevens/v1/toepasbareRegels/{rulesetid}/sttrBestand
```

Only the `rulesetid` goes into the URL. Transform: `sttr2cprmv.xsl` (method `sttr`); the result is a `cprmv:DecisionModel`, with `cprmv:validFrom` fixed at `2026-01-01` for now.

The API then looks the rule set up in the DSO as a service register (method `dso-service-register`, `DSOService_{rulesetid}_{date}_{index}`, the same URL without `/sttrBestand`): its `functioneleStructuurRef` is the service and its `oin` the organisation. It looks that organisation up in ROO by OIN, and adds `cprmv:isOutputOf` with the service and its competent authority.

Both DSO methods need the caller's own DSO API key, sent to the CPRMV API as the `x-api-key` header, which the API passes on. Without it the answer is `{"error": "'x-api-key'"}`.

---

## Analysis methods (non-publication)

`cprmvmethods.ttl` also acknowledges analysis methods that are not publication endpoints — these describe how a rule set was analysed but do not provide publication URLs:

| Method | ID |
|---|---|
| Law Analysis / Wetsanalyse (JAS) | `cprmvmethods:jas` |
| Calculemus / FLINT | `cprmvmethods:flint` |

These are used to annotate rule sets via `cprmv:hasMethod` in TTL files. They have no Python module, so the API does not use them for retrieval.
