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
| **CPRMV-vocabulaire** | `data.cprmv_version`-envelopveld | Welk vocabulaire de data gebruikt | Versie-updates van het vocabulaire (meestal additief) |
| **Backend-service** | `API-Version` HTTP-header | De uitgerolde backendcode | Bij elke backendrelease (operationeel, geen contractsignaal) |

Alleen de eerste drie maken deel uit van het afnemerscontract. De `API-Version`-header is informatief — bruikbaar voor supporttickets, niet voor cache-invalidatie of schema-onderscheid.

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

Het envelopveld `cprmv_version` geeft aan welk CPRMV-vocabulaire de responsdata gebruikt (momenteel `"0.3.0"`). Een bump binnen de `0.x`-lijn wordt behandeld als additieve groei van het vocabulaire (nieuwe predicates, nieuwe optionele velden). Een major bump die de predicate-URI's verandert die de afnemer ziet, zou worden uitgebracht als `/v2/norms`.

## Datasetversiebeheer per rulesetid

Elke BWB-regelset (BWBR0002471, BWBR0004044, …) wordt door de CPSV editor gepubliceerd als een afzonderlijke `cprmv:Dataset`-resource in TriplyDB. **Eén regelset kan meerdere Dataset-records hebben** — verschillende toepasselijke perioden van dezelfde wet (bijv. de edities `2025-01-01` en `2026-01-01` van de Participatiewet) zijn *gelijktijdig en even gezaghebbend*, geen concurrerende versies van elkaar. Beide ondersteunen regels die afnemers legitiem kunnen opvragen. Eén `/v1/norms`-respons kan regels over N regelsets aggregeren, elk met M records.

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

De lijst is **vooraf gesorteerd**: `version` aflopend met nulls achteraan, gelijke waarden gebroken door `published_at` aflopend. Element `[0]` is de meest recente toepasselijke versie van die regelset. Niet-primaire regelsets (waar de editor `dcat:version` niet kent) vallen terug op pure `published_at` desc-volgorde.

De map bevat alleen entries voor rulesetid's die ten minste één `cprmv:Dataset`-record hebben. Rulesetid's zonder zo'n record zijn stilzwijgend afwezig (overgangsstaat tijdens de uitrol).

Drie velden per entry, waarvan twee nullable:

| Veld           | Bron           | Altijd aanwezig?                                                                                              |
| -------------- | -------------- | ------------------------------------------------------------------------------------------------------------- |
| `version`      | `dcat:version` | **Alleen primaire regelset.** De CPSV editor kent alleen de versie van het `legalResource.bwbId` van de dienst — de wet die expliciet is ingevoerd op het tabblad Legal. Voor andere regelsets die via `cprmv:Rule`-referenties in de dienst voorkomen is de versie onbekend en wordt deze als `null` uitgezonden. |
| `published_at` | `dct:issued`   | **Altijd aanwezig.** Tijdstempel van wanneer dit `cprmv:Dataset`-record is gepubliceerd. Dit is het betekenisvolle signaal voor wijzigingsdetectie — het wordt bij elke (her)publicatie bijgewerkt, ongeacht of de eigen versie van de BWB bekend is. |
| `title`        | `dct:title`    | **Alleen primaire regelset.** `null` voor niet-primaire regelsets, om dezelfde reden als `version`. |

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

Een null-waarde voor `version` betekent niet dat de data niet cachebaar is — het betekent enkel dat het eigen versielabel van de BWB onbekend is. Het werkelijke wijzigingssignaal is `published_at` (`dct:issued`), dat altijd aanwezig is en bij elke publicatiegebeurtenis wordt bijgewerkt. ETag en Last-Modified steunen op `published_at`; het veld `version` is informatieve metadata voor menselijke en UI-consumptie.

#### Gedrag bij gedeeltelijke dekking

Wanneer **een** rulesetid in de respons geen `cprmv:Dataset`-record heeft (een niet-versie-gebonden regelset), degradeert de respons als volgt:

- De `dataset_versions`-map laat de niet-versie-gebonden rulesetid(s) weg
- De headers `ETag` en `Last-Modified` worden niet gezet
- `Cache-Control: no-cache`

Rationale: we kunnen een wijziging in een niet-versie-gebonden regelset niet betrouwbaar detecteren. Een 304 retourneren in dat geval zou het risico van verouderde data opleveren, dus vertellen we afnemers altijd opnieuw op te halen. Naarmate meer BWB-regelsets worden gepubliceerd met `cprmv:Dataset`-metadata, treedt caching geleidelijk in werking voor queries die uitsluitend versie-gebonden regelsets bestrijken.

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
| Wat als een rulesetid ontbreekt in `dataset_versions`? | Die regelset heeft nog geen `cprmv:Dataset`-record; niet cachen |
| Wat betekent `Cache-Control: no-cache` hier? | Ten minste één rulesetid in uw query is niet versie-gebonden — telkens opnieuw ophalen |
| Wat betekent `version: null`? | De eigen versie van de BWB is onbekend (deze regelset is niet de primaire wet van een dienst die hem publiceert). `published_at` blijft gezaghebbend voor wijzigingsdetectie. |
| Waarom heeft één rulesetid meerdere Dataset-records? | Verschillende toepasselijke perioden van dezelfde wet zijn gelijktijdig en even gezaghebbend. De edities `2025-01-01` en `2026-01-01` van de Participatiewet ondersteunen beide actuele regels; beide worden vermeld. |
| Hoe vind ik welk Dataset-record een specifieke regel ondersteunt? | Zoek op `dataset_versions[<rule.rulesetid>]`, vind de entry waarvan `version` overeenkomt met `<rule.applicable_date>`; val door naar de meest recente op `published_at` wanneer `version` null is. |
| Hoe vind ik de huidige waarde van een regel? | Filter op `rule_id_path_key`, sorteer op `applicable_date` desc en vervolgens `rulesetid_index` desc, neem de eerste |
| Verschijnen er nieuwe velden in responsen? | Ja — additief, nooit als breaking change. Negeer onbekende velden |
| Staan alle BWB-regelsets op dezelfde publicatiecyclus? | Nee — elke regelset heeft een eigen cadans; controleer `dataset_versions[<id>][0].published_at` per regelset |