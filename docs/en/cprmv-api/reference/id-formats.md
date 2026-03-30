# Rule Set ID Formats

Rule Set IDs passed to `/rules/{rule_id_path}` are matched against the `cprmv-serve:normalized-id-format` pattern of each registered method. `serve.py`'s `normalize_ruleset_id` function canonicalises shortened forms before matching.

---

## Normalisation

| Incoming form | Normalised to | Example in → out |
|---|---|---|
| `{BWBID}` | `{BWBID}_now_latest` | `BWBR0015703` → `BWBR0015703_now_latest` |
| `{BWBID}_{INDEX}` | `{BWBID}_na_{INDEX}` | `BWBR0015703_0` → `BWBR0015703_na_0` |
| Full form | unchanged | `BWBR0015703_2025-07-01_0` → unchanged |

The `now` and `na` placeholders are artefacts of the normalisation step and are handled by the `latest` resolution logic — they are never exposed to callers.

---

## BWB

**Publication ID format:** `BWB{rulesetid}_{date}_{index}`

**Normalised ID format (parsed):** `BWB{rulesetid}_{date}_{index}`

| Named field | Description |
|---|---|
| `rulesetid` | The BWB identifier without `BWB` prefix (e.g. `R0015703`) |
| `date` | Publication date in `YYYY-MM-DD` format |
| `index` | Publication index digit, or `latest` |

**Publication URL template:**

```
https://repository.officiele-overheidspublicaties.nl/bwb/BWB{rulesetid}/{date}_{index}/xml/BWB{rulesetid}_{date}_{index}.xml
```

**SRU URL template (for `latest` resolution):**

```
https://zoekservice.overheid.nl/sru/Search?x-connection=BWB&operation=searchRetrieve
  &version=2.0&maximumRecords=1
  &query=dcterms.identifier=BWB{rulesetid}%20and%20overheidbwb.geldigheidsdatum={valid-on}
```

SRU response field for publication URL: `locatie_toestand` (namespace: `http://standaarden.overheid.nl/bwb/terms/`)

SRU response field for valid-from date: `geldigheidsperiode_startdatum`

---

## CVDR

**Publication ID format:** `CVD{rulesetid}_{index}`

**Normalised ID format (parsed):** `CVD{rulesetid}_{date}_{index}`

| Named field | Description |
|---|---|
| `rulesetid` | CVDR regulation number |
| `date` | Valid-on date (for `latest` forms) |
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
  sortby overheidrg.inwerkingtredingDatum/descending
```

SRU response field for publication URL: `publicatieurl_xml` (namespace: `http://standaarden.overheid.nl/sru`)

SRU response field for valid-from date: `inwerkingtredingDatum` (namespace: `http://standaarden.overheid.nl/cvdr/terms/`)

---

## EU CELLAR (Formex v4)

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

**Publication ID format:** `DMN1.3_{deploymentid}R{resourceid}_{date}_{index}`

**Normalised ID format (parsed):** `DMN1.3_{rulesetid}_{date}_{index}`

The `{rulesetid}` field encodes `{deploymentid}R{resourceid}` and is split by `serve.py` using positional string parsing.

**Publication URL template:**

```
https://operaton.open-regels.nl/engine-rest/deployment/{deploymentid}/resources/{resourceid}/data
```
