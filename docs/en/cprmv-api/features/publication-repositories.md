# Publication Repositories

The CPRMV API supports four publication methods, each registered in `data/cprmvmethods.ttl` under the `cprmvmethods:analysismethods` or `cprmvmethods:formalisationmethods` collection. The method detection logic in `serve.py` (`detect_cprmv_serve_acknowledged_method`) walks these RDF lists and attempts to parse the incoming rule set identifier against the `cprmv-serve:normalized-id-format` pattern of each method.

---

## BWB — Basis Wettenbestand (Dutch national law)

The BWB repository holds consolidated versions of Dutch national legislation. The API supports three identifier forms:

| Form | Example | Behaviour |
|---|---|---|
| `{BWBID}_{DATE}_{INDEX}` | `BWBR0015703_2025-07-01_0` | Fetches the specific indexed publication |
| `{BWBID}_{DATE}_latest` | `BWBR0015703_2025-07-02_latest` | SRU search for version valid on that date |
| `{BWBID}` | `BWBR0015703` | SRU search for version valid today |

For `latest` and bare-ID forms, the API queries the BWB SRU endpoint:

```
https://zoekservice.overheid.nl/sru/Search?x-connection=BWB&operation=searchRetrieve
  &version=2.0&maximumRecords=1
  &query=dcterms.identifier=BWBR0015703 and overheidbwb.geldigheidsdatum={valid-on}
```

The response identifies the publication XML at:

```
https://repository.officiele-overheidspublicaties.nl/bwb/{BWBID}/{DATE}_{INDEX}/xml/{BWBFILENAME}.xml
```

Transform: `data/bwb2cprmv.xsl` — converts BWB `toestand` XML structure (hoofdstuk / paragraaf / artikel / lid / li) to nested CPRMV Turtle with `cprmv:id`, `cprmv:definition`, and `cprmv:hasPart` relations.

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

Transform: `data/cvdr2cprmv.xsl`.

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

Date-based version resolution is not yet supported for CELLAR publications.

Transform: `data/fmx4cellar2cprmv.xsl`.

---

## DMN 1.3 via Operaton (experimental)

Decision models deployed to the Operaton BPMN/DMN engine can also be fetched. The identifier embeds the Operaton deployment ID and resource ID:

| Form | Example |
|---|---|
| `DMN1.3_{deploymentid}R{resourceid}_{date}_{index}` | (from Operaton deployment API) |

Publication URL:

```
https://operaton.open-regels.nl/engine-rest/deployment/{deploymentid}/resources/{resourceid}/data
```

Transform: `data/dmn13operaton2cprmv.xsl`.

!!! warning "Experimental"
    The DMN 1.3 method is explicitly marked experimental. The deployment/resource ID extraction relies on a positional parsing hack in `serve.py` and is subject to change.

---

## Analysis methods (non-publication)

`cprmvmethods.ttl` also registers analysis methods that are not publication endpoints — these describe how a rule set was analysed but do not provide publication URLs:

| Method | ID |
|---|---|
| Law Analysis / Wetsanalyse (JAS) | `cprmvmethods:lawanalysis` |
| Calculemus / FLINT | `cprmvmethods:calculemusflint` |

These are used to annotate rule sets via `cprmv:hasMethod` in TTL files but are not matched by the serve API's method detection for retrieval purposes.
