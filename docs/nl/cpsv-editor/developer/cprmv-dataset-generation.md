# cprmv:Dataset-generatie

---

## Architectuur

```
Gebruiker bewerkt CPRMV-regels in CPRMVTab
        ↓
Bij TTL-export of publicatie, TTLGenerator.generate() in ttlGenerator.js:
    ...
    Service-sectie                      (cpsv:PublicService)
    Organisatie-sectie                  (cv:PublicOrganisation)
    Legal Resource-sectie               (eli:LegalResource)
    CPRMV Dataset-sectie                 ← één Dataset per unieke rulesetId
    CPRMV Rules-sectie                   ← per regel cprmv:implements-URI
    ...
        ↓
generateDatasetsSection():
    rulesetIds = unieke waarden van cprmv:rulesetId over alle regels
    Voor elke rulesetId:
        isPrimary = (rulesetId komt overeen met legalResource.bwbId)
        legalUri  = buildLegalUriForRulesetId(rulesetId, isPrimary ? version : '')
        Emit Dataset-blok (DCAT-conform)
        ↓
generateCprmvRulesSection():
    Voor elke regel:
        isPrimary  = (rule.rulesetId komt overeen met legalResource.bwbId)
        legalUri   = buildLegalUriForRulesetId(rule.rulesetId, isPrimary ? version : '')
        Emit Rule-blok, inclusief:
            cprmv:rulesetId  "{rule.rulesetId}"
            cprmv:implements <{legalUri}>
```

---

## Bestanden

```
src/
├── utils/
│   ├── ttlGenerator.js         # generateDatasetsSection, generateCprmvRulesSection,
│   │                             buildLegalUriForRulesetId, buildLegalResourceUri
│   ├── constants.js            # TTL_NAMESPACES (cprmv-, dcat-, dct-, xsd-prefixen)
│   └── index.js                # encodeURIComponentTTL, escapeTTLString utilities
└── config/
    └── vocabularies.config.js  # entityTypes.cprmvDataset (acceptedTypes, canonicalType)
```

---

## API-functies

### `generateDatasetsSection()`

Genereert de `cprmv:Dataset`-sectie van het TTL-document. Eén Dataset wordt geëmit per unieke `cprmv:rulesetId` die in de CPRMV Rules-collectie wordt aangetroffen.

```javascript
// binnen TTLGenerator.generate():
if (this.hasCprmvRules()) {
  ttl += this.generateSectionHeader('CPRMV Dataset');
  ttl += this.generateDatasetsSection();
}
```

**Gedrag:**

- Retourneert `''` wanneer er geen CPRMV-regels zijn
- Emit één Dataset per onderscheiden rulesetId
- `dcat:version`, geversiede `cprmv:implements`, geversiede `dcat:landingPage` en `dct:title` worden alleen toegepast op de Dataset die overeenkomt met het primaire `legalResource.bwbId` van de dienst; andere regelsets krijgen ongeversiede URI's en geen titel (zie "Versiebetrouwbaarheid")

### `buildLegalUriForRulesetId(rulesetId, version)`

Bouwt een canonieke legal-resource-URI vanuit een BWB/CVDR-identifier of volledige URI. Wordt gebruikt door zowel de Rule- als de Dataset-emitter zodat zij symmetrische URI's produceren.

```javascript
buildLegalUriForRulesetId('BWBR0015703', '2026-01-01');
// → 'https://wetten.overheid.nl/BWBR0015703/2026-01-01'

buildLegalUriForRulesetId('BWBR0044894', '');
// → 'https://wetten.overheid.nl/BWBR0044894'

buildLegalUriForRulesetId('CVDR123456', '');
// → 'https://lokaleregelgeving.overheid.nl/CVDR123456/1'

buildLegalUriForRulesetId('https://wetten.overheid.nl/BWBR0015703/2026-01-01/0', '2026-01-01');
// → 'https://wetten.overheid.nl/BWBR0015703/2026-01-01'
//   (trailing /YYYY-MM-DD[/N] wordt verwijderd voordat version opnieuw wordt toegevoegd,
//    wat dubbele-versie-URI's voorkomt bij reeds-geversiede invoer)
```

**Parameters:**

- `rulesetId` — kale ID (`BWBR…` / `CVDR…`) of volledige URI
- `version` — datumstring (`YYYY-MM-DD`); wordt toegevoegd aan de basis-URI wanneer truthy

### `buildLegalResourceUri()`

Dunne wrapper die delegeert naar `buildLegalUriForRulesetId` met gebruik van de primaire legal-resource van de dienst (`this.legalResource.bwbId` en `this.legalResource.version`). Gebruikt als defensief fallback-pad wanneer een Rule geen `rulesetId` heeft.

---

## Schemaontwerp

Elke Dataset heeft een dubbele typering: `cprmv:Dataset` en `dcat:Dataset`, met DCAT-conforme eigenschappen voor catalogusinteroperabiliteit.

### Primaire Dataset (komt overeen met het `legalResource.bwbId` van de dienst)

```turtle
<https://cprmv.open-regels.nl/datasets/BWBR0015703_2026-01-01> a cprmv:Dataset, dcat:Dataset ;
    dct:identifier "BWBR0015703_2026-01-01" ;
    dct:title "Participatiewet"@nl ;
    cprmv:rulesetId "BWBR0015703" ;
    cprmv:implements <https://wetten.overheid.nl/BWBR0015703/2026-01-01> ;
    dcat:version "2026-01-01" ;
    dct:issued "2026-05-15T06:57:11Z"^^xsd:dateTime ;
    dcat:landingPage <https://wetten.overheid.nl/BWBR0015703/2026-01-01> .
```

### Niet-primaire Dataset (elke andere rulesetId waarnaar regels in deze dienst verwijzen)

```turtle
<https://cprmv.open-regels.nl/datasets/BWBR0044894_2026-01-01> a cprmv:Dataset, dcat:Dataset ;
    dct:identifier "BWBR0044894_2026-01-01" ;
    cprmv:rulesetId "BWBR0044894" ;
    cprmv:implements <https://wetten.overheid.nl/BWBR0044894> ;
    dct:issued "2026-05-15T06:57:11Z"^^xsd:dateTime ;
    dcat:landingPage <https://wetten.overheid.nl/BWBR0044894> .
```

Het achtervoegsel van de Dataset-URI draagt de versie (`BWBR0044894_2026-01-01`), overgenomen uit `legalResource.version` van de dienst. Dit maakt Dataset-URI's sorteerbaar per publicatiebatch, zelfs wanneer de eigen versie van de BWB niet bekend is bij de editor.

---

## CPRMV Rule-tegenhanger

Regels emitten `cprmv:implements` op basis van hun eigen `rulesetId`, niet op basis van de primaire legal-resource van de dienst. Dit is wat de URI-symmetrie tussen Rule en Dataset mogelijk maakt.

```turtle
<https://cprmv.open-regels.nl/rules/BWBR0044894_2026-01-01_0_Artikel-7a_onderdeel-c> a cprmv:Rule ;
    cprmv:id "onderdeel c." ;
    cprmv:rulesetId "BWBR0044894" ;
    cprmv:definition "19-jarigen: € 231,09;"@nl ;
    cprmv:situatie "19-jarigen"@nl ;
    cprmv:norm "231,09" ;
    cprmv:ruleIdPath "BWBR0044894_2026-01-01_0, Artikel 7a., onderdeel c." ;
    cprmv:implements <https://wetten.overheid.nl/BWBR0044894> .
```

Een regel uit Artikel 7a van BWBR0044894 implementeert BWBR0044894 — niet de primaire wet van de dienst (hier BWBR0015703). Wanneer een regel geen `rulesetId` heeft (defensief fallback-pad), roept de emitter `buildLegalResourceUri()` aan en emit de primaire URI van de dienst. In de praktijk handhaaft de editor `rulesetId` als verplicht veld, dus dit pad wordt normaal gesproken niet gebruikt.

---

## Join-semantiek

Datasets verbinden met Rules via twee predicates — beide werken, en beide retourneren identieke recordsets in zowel single-BWB- als multi-BWB-diensten. Ze zijn uitwisselbaar; gebruik welke past bij de querystijl.

### Losse join — via `cprmv:rulesetId`

Granulariteit op regelniveau. Joint op de letterlijke `cprmv:rulesetId` die wordt gedeeld tussen een Rule en zijn Dataset.

```sparql
PREFIX cprmv: <https://cprmv.open-regels.nl/0.3.0/>

SELECT ?rule ?dataset WHERE {
  ?rule a cprmv:Rule ; cprmv:rulesetId ?id .
  ?dataset a cprmv:Dataset ; cprmv:rulesetId ?id .
}
```

### Strikte join — via `cprmv:implements`

Granulariteit op URI-niveau. Joint via de gedeelde legal-resource-URI. Het versie-achtervoegsel is aanwezig voor de primaire regelset en afwezig voor niet-primaire — beide zijden komen door constructie overeen (zie "Versiebetrouwbaarheid").

```sparql
PREFIX cprmv: <https://cprmv.open-regels.nl/0.3.0/>

SELECT ?rule ?dataset WHERE {
  ?rule a cprmv:Rule ; cprmv:implements ?legal .
  ?dataset a cprmv:Dataset ; cprmv:implements ?legal .
}
```

### Voorbeeldresultaat (Normenbrief, 69 rijen uit beide joins)

| ?rule | ?dataset |
|---|---|
| `…/rules/BWBR0004163_2026-01-01_0_Artikel-5_lid-4_onderdeel-b` | `…/datasets/BWBR0004163_2026-01-01` |
| `…/rules/BWBR0044894_2026-01-01_0_Artikel-7a_onderdeel-c` | `…/datasets/BWBR0044894_2026-01-01` |
| `…/rules/BWBR0015703_2026-01-01_0_Artikel-22a_lid-3_onderdeel-a` | `…/datasets/BWBR0015703_2026-01-01` |
| `…/rules/BWBR0015711_2026-01-01_0_Artikel-25` | `…/datasets/BWBR0015711_2026-01-01` |
| `…/rules/BWBR0004044_2026-01-01_0_Artikel-8_lid-9` | `…/datasets/BWBR0004044_2026-01-01` |
| … | … |

Elke regel wordt gekoppeld aan de Dataset die dezelfde BWB-versie vertegenwoordigt, of die BWB nu de primaire wet van de dienst is of een andere regelset waarnaar binnen de dienst wordt verwezen.

### Dataset-metadata projecteren voor een API-endpoint

Voor rijkere responses (bijv. een LDE `/v1/norms`-endpoint) projecteert u de metadata van de Dataset naast de regel:

```sparql
PREFIX cprmv: <https://cprmv.open-regels.nl/0.3.0/>
PREFIX dct:   <http://purl.org/dc/terms/>
PREFIX dcat:  <http://www.w3.org/ns/dcat#>

SELECT ?rule ?ruleId ?dataset ?title ?version ?landingPage WHERE {
  ?rule a cprmv:Rule ;
        cprmv:rulesetId ?rulesetId ;
        cprmv:id ?ruleId .
  ?dataset a cprmv:Dataset ;
           cprmv:rulesetId ?rulesetId ;
           dcat:landingPage ?landingPage .
  OPTIONAL { ?dataset dct:title ?title }
  OPTIONAL { ?dataset dcat:version ?version }
}
```

`dct:title` en `dcat:version` zijn `OPTIONAL` omdat niet-primaire Datasets ze weglaten.

---

## Versiebetrouwbaarheid

Slechts één versie van een regelset is bekend bij de editor: de primaire `legalResource` van de dienst, die de gebruiker expliciet invoert op het tabblad Legal. Andere regelsets komen uitsluitend in beeld via het veld `cprmv:rulesetId` op individuele CPRMV-regels — hun versies zijn onbekend.

De generator gaat hiermee om door geversiede URI's alleen te emitten voor de primaire regelset. Zowel de Dataset-emitter als de Rule-emitter vergelijken elke rulesetId met de primaire, en geven de versie alleen door wanneer deze overeenkomen:

```javascript
const primaryMatch = this.legalResource.bwbId.match(/(BWB[A-Z]?\d+|CVDR\d+)/i);
const primaryRulesetId = primaryMatch ? primaryMatch[0] : '';
const isPrimary = rulesetId === primaryRulesetId;
const versionForUri = isPrimary ? this.legalResource.version : '';
```

Symmetrie tussen Rule- en Dataset-emitters is essentieel. Als Rules geversiede URI's zouden emitten voor niet-primaire regelsets terwijl Datasets ongeversiede zouden emitten (of vice versa), zou de strikte join stilzwijgend degraderen voor multi-BWB-diensten.

---

## Vocabulaire

Vereiste prefixen (reeds gedeclareerd in `TTL_NAMESPACES` in `src/utils/constants.js`):

```turtle
@prefix cprmv: <https://cprmv.open-regels.nl/0.3.0/> .
@prefix dcat:  <http://www.w3.org/ns/dcat#> .
@prefix dct:   <http://purl.org/dc/terms/> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
```

Het Dataset-entiteitstype is geregistreerd in `vocabularies.config.js` voor round-trip-herkenning bij TTL-import:

```javascript
cprmvDataset: {
  acceptedTypes: ['cprmv:Dataset', 'dcat:Dataset'],
  canonicalType: 'cprmv:Dataset',
}
```

Round-trip-parsing van Datasets is nog niet geïmplementeerd in `parseTTL.enhanced.js` — bij import worden Dataset-blokken genegeerd. Bij export worden zij deterministisch opnieuw gegenereerd vanuit elke `cprmv:rulesetId` van een regel, dus single-trip-round-tripping produceert equivalente uitvoer. Handmatige bewerkingen aan Dataset-blokken in TTL-bestanden overleven een import/export-cyclus niet.