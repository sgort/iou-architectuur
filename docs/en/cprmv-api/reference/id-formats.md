---
component: CPRMV
---

# Rule Set ID Formats

Rule Set IDs passed to `/rules/{rule_id_path}` are offered to each acknowledged publication method in turn. `PublicationMethod.normalize_ruleset_id` (`serve_api/methods/PublicationMethod.py`) first canonicalises shortened forms; the result is then parsed against the method's `cprmv-serve:normalized-id-format`. The formats below are configured on the method nodes in `data/cprmvmethods.ttl`.

---

## Normalisation

| Incoming form | Normalised to | Example in → out |
|---|---|---|
| `{ID}` (no underscore) | `{ID}_now_latest` | `BWBR0015703` → `BWBR0015703_now_latest` |
| `{ID}_{INDEX}` (one underscore) | `{ID}_na_{INDEX}` | `CVDR712517_1` → `CVDR712517_na_1` |
| Any other form | unchanged | `BWBR0015703_2025-07-01_0` → unchanged |

`na` stands for "not applicable": the `{ID}_{INDEX}` form is the CVDR form, which has no date. When the index is `latest`, the date part is used as the valid-on date if it is a valid ISO date; otherwise (`now`) the valid-on date is today. The method then looks up the version valid on that date, and the official ID of the version found replaces the shortened form in the rule ID path.

---

## BWB

Method: `repository-overheid-nl-bwb`

**Publication ID format:** `BWB{rulesetid}_{date}_{index}`

**Normalised ID format (parsed):** `BWB{rulesetid}_{date}_{index}`

| Named field | Description |
|---|---|
| `rulesetid` | The BWB identifier without `BWB` prefix (e.g. `R0015703`) |
| `date` | Date of the consolidated version in `YYYY-MM-DD` format, or the valid-on date for `latest` |
| `index` | Publication index digit, or `latest` |

**Publication URL template:**

```
https://repository.officiele-overheidspublicaties.nl/bwb/BWB{rulesetid}/{date}_{index}/xml/BWB{rulesetid}_{date}_{index}.xml
```

**SRU URL template (`frbr-sru:url`, for `latest` resolution):**

```
https://zoekservice.overheid.nl/sru/Search?x-connection=BWB&operation=searchRetrieve
  &version=2.0&maximumRecords=1
  &query=dcterms.identifier=BWB{rulesetid}%20and%20overheidbwb.geldigheidsdatum={valid-on}
```

SRU response field for publication URL (`frbr-sru:response-publication-location-term`): `locatie_toestand` (namespace: `http://standaarden.overheid.nl/bwb/terms/`)

SRU response field for valid-from date (`frbr-sru:response-from-date-term`): `geldigheidsperiode_startdatum` (namespace: `http://standaarden.overheid.nl/bwb/terms/`)

The index of the version found is parsed from the publication URL with the publication URL template.

---

## CVDR

Method: `repository-overheid-nl-cvdr`

**Publication ID format:** `CVD{rulesetid}_{index}`

**Normalised ID format (parsed):** `CVD{rulesetid}_{date}_{index}`

| Named field | Description |
|---|---|
| `rulesetid` | The CVDR identifier without `CVD` prefix (e.g. `R712517`) |
| `date` | Valid-on date (for `latest` forms), `na` or `now` |
| `index` | Index digit or `latest` |

**Publication URL template:**

```
https://repository.officiele-overheidspublicaties.nl/cvdr/CVD{rulesetid}/{index}/xml/CVD{rulesetid}_{index}.xml
```

**SRU URL template:**

```
https://zoekservice.overheid.nl/sru/Search?x-connection=cvdr&operation=searchRetrieve
  &version=2.0&maximumRecords=1
  &query=dcterms.identifier=CVD{rulesetid}_*%20and%20overheidrg.inwerkingtredingDatum%3C={valid-on}
  %20sortby%20overheidrg.inwerkingtredingDatum/descending
```

SRU response field for publication URL: `publicatieurl_xml` (namespace: `http://standaarden.overheid.nl/sru`)

SRU response field for valid-from date: `inwerkingtredingDatum` (namespace: `http://standaarden.overheid.nl/cvdr/terms/`)

---

## EU CELLAR (Formex v4)

Method: `eucellar-fmx4`

**Publication ID format:** `CFMX4{rulesetid}_{docid}`

**Normalised ID format (parsed):** `CFMX4{rulesetid}_{docid}`

| Named field | Description |
|---|---|
| `rulesetid` | CELLAR resource UUID |
| `docid` | Document identifier within the CELLAR resource |

**Publication URL template:**

```
https://publications.europa.eu/resource/cellar/{rulesetid}/{docid}
```

No SRU / date-based resolution available.

---

## DMN 1.3 (Operaton, experimental)

Method: `operaton.open-regels.nl`

**Publication ID format:** `DMN1.3_{deploymentid}R{resourceid}_{date}_{index}`

**Normalised ID format (parsed):** `DMN1.3_{rulesetid}_{date}_{index}`

The `{rulesetid}` field encodes `{deploymentid}R{resourceid}`; the `operaton` method module splits it on the letter `R` into `deploymentid` and `resourceid`.

**Publication URL template:**

```
https://operaton.open-regels.nl/engine-rest/deployment/{deploymentid}/resources/{resourceid}/data
```
