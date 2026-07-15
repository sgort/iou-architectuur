# API-stabiliteitscontract — `/v1/norms`

Dit document is het bindende stabiliteitscontract voor afnemers van `/v1/norms`. Het definieert waar afnemers op kunnen vertrouwen, hoe wijzigingen efficiënt te detecteren zijn, en welke soorten wijzigingen een major versie-update rechtvaardigen.

## Doelgroep

Dit contract richt zich op **G2G-afnemers** — andere Nederlandse overheidsdiensten die `/v1/norms` integreren om `cprmv:Rule`-paden en normen af te nemen. Externe afnemers kunnen op basis van dit contract langetermijnintegraties bouwen zonder vrees voor breuk binnen v1.

## De vier versielagen

`/v1/norms` draagt vier verschillende versienummers, elk voor een andere stabiliteitslaag:

| Laag | Locatie | Wat het bijhoudt | Wanneer het verandert |
|------|---------|-------------------|------------------------|
| **API-contract** | URL-pad `/v1/` | Het schema en de vorm waar afnemers tegen aan coderen | Uitsluitend breaking changes (rechtvaardigt `/v2/`) |
| **Dataset-versies** | `data.dataset_versions`-envelopmap | Publicatie-snapshots per rulesetid | Elke BWB-regelset met eigen cadans; de map bevat de meest recente versie per rulesetid in het antwoord |
| **CPRMV-vocabulaire** | `?cprmv_version=`-requestparameter ↔ `data.cprmv_version`-envelopveld | In welke CPRMV-vocabulaireversie de respons wordt gevraagd en uitgeleverd | **Door de afnemer gekozen** per request (`0.3.0` default, `0.3.2`, `0.4.1`); de namespace van de data volgt de keuze |
| **Backend-service** | `API-Version` HTTP-header | De uitgerolde backendcode | Bij elke backendrelease (operationeel, geen contractsignaal) |

Alleen de eerste drie maken deel uit van het afnemerscontract. De `API-Version`-header is informatief — bruikbaar voor supporttickets, niet voor cache-invalidatie of schema-onderscheid.

!!! note "`cprmv_version` is nu een request-input"
    Sinds backend v1.9.10 is `cprmv_version` een **onderhandelbare** laag: afnemers kiezen de
    vocabulaireversie via de optionele parameter `?cprmv_version=` (default `0.3.0`), en het
    envelopveld `cprmv_version` echoot de keuze. Voorheen gaf het alleen "wat de backend spreekt"
    weer. De parameter weglaten behoudt exact het eerdere gedrag, dus dit is een additieve
    wijziging binnen v1.

## Stabiliteitsbelofte binnen v1

### Primaire-sleutelsemantiek

De tupel `(rulesetid, applicable_date, rulesetid_index)` is de **onveranderlijke primaire sleutel** voor elke individuele regel. Zodra gepubliceerd, identificeert deze combinatie een regel waarvan de waarden nooit meer veranderen.

- Correcties worden gepubliceerd als nieuwe rijen met een hogere `rulesetid_index`
- Wetswijzigingen worden gepubliceerd als nieuwe rijen met een nieuwe `applicable_date`
- Oude rijen blijven ongewijzigd en oneindig opvraagbaar

**Afnemers kunnen rijen onbeperkt cachen op basis van deze tupel. Cache-invalidatie is niet vereist.**

### Logische identiteit over versies

Het veld `rule_id_path_key` biedt een stabiele identificator voor de *logische* regel over al zijn versies heen. Om "de huidige waarde van deze regel" op te vragen:

1. Filter regels op `rule_id_path_key`
2. Kies de rij met de meest recente `applicable_date`
3. Kies daarbinnen de rij met de hoogste `rulesetid_index`

De aard van de wijziging is **af te leiden uit de inhoud** — een nieuwe `applicable_date` impliceert een wetswijziging; dezelfde datum met een hogere `rulesetid_index` impliceert een correctie. Er wordt geen aparte metadata over het soort wijziging gepubliceerd.

### Additieve evolutie

Binnen v1 zijn alle wijzigingen additief:

- Nieuwe velden kunnen verschijnen in de responsenvelop of in regelobjecten — afnemers moeten onbekende velden netjes negeren
- Nieuwe optionele queryparameters kunnen worden toegevoegd — afnemers mogen deze negeren
- Bestaande velden, hun namen, types en semantiek veranderen niet

### CPRMV-vocabulaireversie

Het envelopveld `cprmv_version` echoot de versie die via `?cprmv_version=` is gevraagd (een van `0.3.0`, `0.3.2`, `0.4.1`; default `0.3.0`). De **volledig-gekwalificeerde regelsleutels** (`type`, `id`, `definition`, `contains`) dragen de namespace van die versie, dus de predicate-URI's die een afnemer ziet zijn een functie van de versie die hij *opvraagt*:

- `0.3.0` / `0.3.2` → `https://cprmv.open-regels.nl/<versie>/…`
- `0.4.1` → `https://standaarden.open-regels.nl/standards/cprmv/0.4.1#…`

Stabiliteit binnen v1: **de default-respons (`0.3.0`) en zijn predicate-URI's veranderen niet.** Een andere `cprmv_version` opvragen is een expliciete opt-in voor die namespace — geen breaking change aan het default-contract. Een afnemer die de parameter nooit meestuurt, wordt niet geraakt door nieuwe versies in de ondersteunde set. Een toekomstige wijziging die de **default**-versie verandert, of de predicate-URI's van de **default**-versie, zou worden uitgebracht als `/v2/norms`.

!!! warning "Experimentele versies — `0.3.2` en `0.4.1` vallen niet onder de v1-garantie"
    Alleen de default **`0.3.0`** valt onder dit stabiliteitscontract. **`0.3.2` en `0.4.1` zijn
    experimenteel / preview:** hun responsvorm, predicate-URI's, `dataset_versions`-semantiek
    (bijv. het 0.4.1-`cprmv:RuleSet`/`validFrom`-model en de
    [cachekanttekening](#publicaties-detecteren)) en zelfs hun beschikbaarheid kunnen wijzigen —
    of worden ingetrokken — **zonder** een `/v2/norms` en buiten de additieve-evolutiebelofte
    hierboven. Bouw langetermijn-G2G-integraties tegen de default; behandel
    `?cprmv_version=0.3.2` / `0.4.1` als opt-in totdat een versie expliciet in dit contract wordt
    opgenomen.

## Datasetversiebeheer per rulesetid

Elke BWB-regelset (BWBR0002471, BWBR0004044, …) draagt versiemetadata per regelset, gepubliceerd door de CPSV editor. **Waar die metadata staat hangt af van de gevraagde `cprmv_version`:** `0.3.0`/`0.3.2` gebruiken een afzonderlijke `cprmv:Dataset`-resource per regelset; `0.4.1` heeft geen `cprmv:Dataset` en de metadata wordt uit de `cprmv:RuleSet` gelezen (`cprmv:validFrom`). Hoe dan ook is de envelopvorm hieronder identiek. **Eén regelset kan meerdere records hebben** — verschillende toepasselijke perioden van dezelfde wet (bijv. de edities `2025-01-01` en `2026-01-01` van de Participatiewet) zijn *gelijktijdig en even gezaghebbend*, geen concurrerende versies van elkaar. Beide ondersteunen regels die afnemers legitiem kunnen opvragen. Eén `/v1/norms`-respons kan regels over N regelsets aggregeren, elk met M records.

### De `dataset_versions`-map

Het envelopveld `data.dataset_versions` is gekeyd op `cprmv:rulesetId`; elke waarde is een **lijst** van records:

```json
"dataset_versions": {
  "BWBR0015703": [
    {
      "version": "2026-01-01",
      "published_at": "2026-05-15T06:57:21Z",
      "title": "Participatiewet"
    },
    {
      "version": "2025-01-01",
      "published_at": "2026-05-15T07:45:36Z",
      "title": "Participatiewet"
    }
  ],
  "BWBR0044894": [
    { "version": null, "published_at": "2026-05-15T07:45:36Z", "title": null }
  ]
}
```

De lijst is **vooraf gesorteerd**: `version` aflopend met nulls achteraan, gelijke waarden gebroken door `published_at` aflopend. Element `[0]` is de meest recente toepasselijke versie van die regelset.

De map bevat alleen entries voor rulesetid's die ten minste één versierecord hebben (een `cprmv:Dataset` voor 0.3.x, een `cprmv:RuleSet` voor 0.4.1). Rulesetid's zonder zo'n record zijn stilzwijgend afwezig (een overgangsstaat voor legacy 0.3.x-data; 0.4.1 heeft altijd een RuleSet per regelset).

Drie velden per entry:

| Veld           | Bron (0.3.x / 0.4.1)              | Opmerkingen |
| -------------- | --------------------------------- | ----------- |
| `version`      | `dcat:version` / `cprmv:validFrom` | **Aanwezig voor elke regelset sinds CPSV editor v1.10.5** — de editor leidt de versie van elke regelset af uit de BWB-datum die de eigen regels dragen (hun `ruleIdPath`), zodat ook niet-primaire regelsets zijn geversioneerd. `null` blijft alleen over voor legacy-data van vóór die wijziging; afnemers moeten dit nog steeds tolereren. |
| `published_at` | `dct:issued` / `cprmv:validFrom`   | **0.3.x:** het publicatietijdstempel — wordt bij elke (her)publicatie bijgewerkt, het signaal voor wijzigingsdetectie. **0.4.1:** er is geen `dct:issued`, dus `cprmv:validFrom` dient als `published_at` (zie de [0.4.1-cachekanttekening](#publicaties-detecteren)). |
| `title`        | `dct:title`                        | **Alleen primaire regelset.** De editor kent alleen de menselijke titel van het `legalResource.bwbId` van de dienst. `null` voor niet-primaire regelsets. |

### Regels koppelen aan Dataset-records

Een regel met `applicable_date: "2025-07-01"` wordt ondersteund door het Dataset-record waarvan de `version` die periode dekt. De koppeling is conventiegebaseerd, niet afgedwongen door de API: de editor publiceert Dataset-records voor dezelfde toepasselijke perioden als de regels die hij genereert. Afnemers die "het Dataset-record dat deze regel ondersteunt" willen vinden, kunnen:

1. Opzoeken `dataset_versions[<rule.rulesetid>]`
2. De entry vinden waarvan de `version` overeenkomt met `<rule.applicable_date>` (wanneer version bekend is)
3. Doorvallen naar de meest recente entry op `published_at` wanneer version null is

### Publicaties detecteren

#### HTTP-cacheheaders

Wanneer **elke** rulesetid in de respons ten minste één `dataset_versions`-entry heeft, draagt de respons:

| Header | Voorbeeld | Betekenis |
|--------|-----------|-----------|
| `ETag` | `"3c899856"` | Opaque strong validator over elk `(version, published_at)`-paar plus filterparameters. `title` is bewust uitgesloten — uitsluitend informatief. |
| `Last-Modified` | `Fri, 15 May 2026 07:45:36 GMT` | Maximum `published_at` over **alle records** in de respons |
| `Cache-Control` | `public, max-age=3600` | Halfjaarlijkse data verdraagt ruime caching |

Afnemers wordt aangeraden conditionele requests te gebruiken voor efficiëntie:

```http
GET /v1/norms HTTP/1.1
Host: backend.linkeddata.open-regels.nl
If-None-Match: "3c899856"
```

De server retourneert `304 Not Modified` zonder body wanneer er sinds de laatste fetch niets in de respons opnieuw is gepubliceerd. Voor queries op een enkele rulesetid (`?rulesetid=<id>`) vindt de 304-check plaats vóór de dure rules-SPARQL-query — alleen de goedkope (gecachete) metadata-lookup draait.

#### Waarom `published_at` (niet `version`) de cachegeldigheid bepaalt

ETag en `Last-Modified` worden berekend uit `published_at`, niet uit `version`; het veld `version` is informatieve metadata voor menselijke en UI-consumptie. Voor `0.3.0`/`0.3.2` is `published_at` gelijk aan `dct:issued`, dat bij elke publicatiegebeurtenis wordt bijgewerkt en daarmee een betrouwbaar wijzigingssignaal is (een legacy-`null` voor `version` maakt de data niet on-cachebaar).

!!! warning "0.4.1-cachekanttekening"
    Voor `cprmv_version=0.4.1` is `published_at` gelijk aan `cprmv:validFrom` (de toepasselijke
    datum), omdat de 0.4.1-RuleSet geen `dct:issued` heeft. Een herpublicatie die **dezelfde
    `validFrom` behoudt** maar regelwaarden corrigeert, verandert de ETag/`Last-Modified`
    **niet**, dus een gecachete respons kan tot `max-age` (1 u) worden geserveerd. Afnemers die
    op `0.4.1` correctie-actuele data nodig hebben, moeten binnen dat venster niet uitsluitend op
    conditionele requests vertrouwen. `0.3.x` wordt niet geraakt (`dct:issued` loopt op bij elke
    publicatie). Een geplande fix emit een publicatietijdstempel op de 0.4.1-RuleSet.

#### Gedrag bij gedeeltelijke dekking

Wanneer **een** rulesetid in de respons een versierecord mist (een `cprmv:Dataset` voor 0.3.x, een `cprmv:RuleSet` voor 0.4.1), degradeert de respons als volgt:

- De `dataset_versions`-map laat de niet-versie-gebonden rulesetid(s) weg
- De headers `ETag` en `Last-Modified` worden niet gezet
- `Cache-Control: no-cache`

Rationale: we kunnen een wijziging in een niet-versie-gebonden regelset niet betrouwbaar detecteren. Een 304 retourneren in dat geval zou het risico van verouderde data opleveren, dus vertellen we afnemers altijd opnieuw op te halen. Naarmate meer BWB-regelsets worden gepubliceerd met versiemetadata, treedt caching geleidelijk in werking voor queries die uitsluitend versie-gebonden regelsets bestrijken.

## Wat rechtvaardigt `/v2/norms`

Het volgende zou het v1-contract doorbreken en zou worden uitgebracht als `/v2/norms`, terwijl `/v1/norms` levend wordt gehouden gedurende een uitfaseringsperiode:

- Een bestaand veld verwijderen of hernoemen
- Het type of de semantiek van een bestaand veld wijzigen
- De PK-semantiek van `(rulesetid, applicable_date, rulesetid_index)` wijzigen (bijv. in-place mutatie toestaan)
- CPRMV major versie-update die de predicate-URI's verandert die de afnemer ziet

## Uitfaseringsbeleid

Wanneer `/v2/norms` uiteindelijk wordt geïntroduceerd:

- `/v1/norms` blijft beschikbaar gedurende **ten minste 24 maanden** na publicatie van `/v2/norms`
- Tijdens de uitfasering bevatten `/v1/norms`-responsen de headers `Deprecation: <date>` en `Sunset: <date>` conform RFC 8594
- Actieve afnemers worden geïnformeerd via de documentatiesite van het IOU Architectuur en de changelog

## Snelle referentie voor afnemers

| Vraag | Antwoord |
|-------|----------|
| Mag ik de waarden van een regel onbeperkt cachen? | Ja, gekeyd op `(rulesetid, applicable_date, rulesetid_index)` |
| Hoe detecteer ik nieuwe publicaties efficiënt? | Gebruik `If-None-Match` met de vorige `ETag` — `304` betekent dat er niets is gewijzigd |
| Welke `cprmv_version` moet ik opvragen? | Laat hem weg voor de stabiele default (`0.3.0`). Stuur `?cprmv_version=0.3.2` of `0.4.1` alleen als u die namespace specifiek wilt — deze zijn **experimenteel** en vallen **niet** onder de v1-garantie (kunnen wijzigen/ingetrokken worden zonder `/v2/`). Alleen de vorm en predicate-URI's van de default zijn contractstabiel binnen v1. |
| Wat als een rulesetid ontbreekt in `dataset_versions`? | Die regelset heeft nog geen versierecord (een `cprmv:Dataset` voor 0.3.x / een `cprmv:RuleSet` voor 0.4.1); niet cachen |
| Wat betekent `Cache-Control: no-cache` hier? | Ten minste één rulesetid in uw query is niet versie-gebonden — telkens opnieuw ophalen |
| Wat betekent `version: null`? | Legacy-data gepubliceerd vóór CPSV editor v1.10.5 — de niet-primaire versie was onbekend. Actuele data versioneert **elke** regelset, dus `null` is zeldzaam. `published_at` blijft gezaghebbend voor wijzigingsdetectie (met de [0.4.1-kanttekening](#publicaties-detecteren)). |
| Is `published_at` altijd een publicatietijdstempel? | Voor `0.3.x` wel (`dct:issued`). Voor `0.4.1` is het `cprmv:validFrom` (de toepasselijke datum) — een herpublicatie op dezelfde datum verhoogt het niet; zie de 0.4.1-cachekanttekening. |
| Waarom heeft één rulesetid meerdere Dataset-records? | Verschillende toepasselijke perioden van dezelfde wet zijn gelijktijdig en even gezaghebbend. De edities `2025-01-01` en `2026-01-01` van de Participatiewet ondersteunen beide actuele regels; beide worden vermeld. |
| Hoe vind ik welk Dataset-record een specifieke regel ondersteunt? | Zoek op `dataset_versions[<rule.rulesetid>]`, vind de entry waarvan `version` overeenkomt met `<rule.applicable_date>`; val door naar de meest recente op `published_at` wanneer `version` null is. |
| Hoe vind ik de huidige waarde van een regel? | Filter op `rule_id_path_key`, sorteer op `applicable_date` desc en vervolgens `rulesetid_index` desc, neem de eerste |
| Verschijnen er nieuwe velden in responsen? | Ja — additief, nooit als breaking change. Negeer onbekende velden |
| Staan alle BWB-regelsets op dezelfde publicatiecyclus? | Nee — elke regelset heeft een eigen cadans; controleer `dataset_versions[<id>][0].published_at` per regelset |