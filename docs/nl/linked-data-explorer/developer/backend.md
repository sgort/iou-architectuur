---
component: Linked Data Explorer
---

# Backend-architectuur

De backend is een Node.js/Express TypeScript-API. Het staat tussen de React-frontend en twee externe services: TriplyDB (SPARQL-kennisgraaf) en Operaton (DMN-uitvoeringsengine). De functies zijn SPARQL-queries uitvoeren, DMN-keten-orkestratie, variabelenmapping tussen ketenstappen en het proxyen van dynamische TriplyDB-endpointaanroepen.

---

<a id="api-versioning"></a>

## API-versiebeheer

| Omgeving | Basis-URL |
|---|---|
| Productie | `https://backend.linkeddata.open-regels.nl/v1` |
| Acceptatie | `https://acc.backend.linkeddata.open-regels.nl/v1` |

Alle endpoints volgen `/v1/*`. De releaseversie wordt in elke respons opgenomen via de `API-Version`-header — op het moment van schrijven `API-Version: 2026.09.6` op acceptatie en `2026.09.5` op productie, want de twee omgevingen kunnen een release uiteenlopen — conform de Nederlandse API Design Rules API-20 en API-57 van de Overheid.

**Het contract is gepubliceerd.** `GET /v1/openapi.json` levert een OpenAPI 3.1-beschrijving van elke `/v1`-route, gebouwd uit `packages/backend/openapi/openapi.yaml`. Het is de referentie voor de vorm van requests en responses; de pagina [API Specification](../reference/api-specification.md) toont hem. `/v1/openapi.json` is een van de drie openbare mounts die aan elke origin worden geleverd (zie [Beveiliging](#beveiliging)), dus elke client kan hem lezen.

**Legacy-aliassen `/api/*`** werken nog voor achterwaartse compatibiliteit en sturen een `Deprecation`-header en een `Link`-header die de `/v1`-opvolger noemt. Ze verdwijnen in v2.0.0.

**`GET /`**, buiten `/v1`, retourneert API-metadata en een overzicht van de huidige en legacy-endpointpaden, inclusief de `documentation`-verwijzing naar `/v1/openapi.json`.

---

## Endpoints

### Health

```
GET /v1/health
```

Retourneert servicehealth: latency-checks van TriplyDB en Operaton, de SHACL-shapelagen die de validator heeft geladen, en **welke build draait**. Gebruikt door de verificatie na deployment in de deployworkflows en door de statusindicator van de frontend. De respons van productie op 19 september 2026:

```json
{
  "name": "Linked Data Explorer Backend",
  "version": "2026.09.5",
  "environment": "production",
  "build": {
    "sha": "ec4792f09c289f8fee6c68da5184fd775a27ccc9",
    "shortSha": "ec4792f",
    "run": "19",
    "isTracked": true,
    "label": "build ec4792f · #19"
  },
  "status": "healthy",
  "services": {
    "triplydb": { "status": "up", "latency": 98 },
    "operaton": { "status": "up", "latency": 105 }
  },
  "shacl": {
    "complete": true,
    "layers": {
      "cpsv-ap": { "label": "CPSV-AP 3.2.0", "loaded": true },
      "ronl-custom": { "label": "RONL Custom", "loaded": true },
      "cprmv": { "label": "CPRMV 0.4.1", "loaded": true }
    }
  },
  "documentation": "/v1/openapi.json"
}
```

`version` noemt de release; `build` noemt de commit en de workflowrun, gelezen uit het `deploy/build-info.json` dat de deployworkflow in het artefact schrijft. `build` geldt alleen als getrackt wanneer zowel `sha` als `run` aanwezig zijn — een ontbrekend of onleesbaar bestand meldt een lokale build en heeft nooit invloed op `status`.

`utils/buildInfo.ts` leest `build-info.json` **één keer, bij het laden van de module** — hetzelfde moment waarop `version` uit `package.json` wordt vastgelegd — zodat de twee niet van elkaar kunnen afwijken: een verouderd proces kan alleen de build melden waarmee het is gestart. Het lezen is bewust niet lui. Een zip-deploy overschrijft `build-info.json` terwijl het vorige proces nog draait en herstart het pas daarna, dus een lezing bij eerste gebruik liet het oude proces de nieuwe `build.sha` melden — een onterechte geslaagde controle in de deploy-gate, gezien bij de productiepromotie van v2026.09.6, waar `build.sha` de nieuwe commit toonde terwijl `version` nog 2026.09.5 was. Het vroege lezen sluit dat sinds v2026.09.7 uit. `/v1/openapi.json` blijft bewust lui: het leest zijn document bij het eerste verzoek en cachet het, maar cachet geen mislukte lezing, zodat een document dat nog niet gebouwd is opnieuw wordt geprobeerd en als `500` zichtbaar wordt in plaats van als kapot te worden onthouden.

De deployworkflows wachten tot `build.sha` gelijk is aan de gedeployde commit en `shacl.complete` `true` is voordat ze slagen; zie [Post-deployment verification](deployment.md#post-deployment-verification).

### DMN deployen en evalueren (v2026.08.2)

```
POST /v1/dmns/deploy
POST /v1/dmns/evaluate/:decisionKey
```

Twee routes toegevoegd voor de DMN-tab van de CPSV Editor, die Operaton
voorheen rechtstreeks vanuit de browser aanriep — wat CORS blokkeert voor een
lokale ontwikkel-origin. De browser post naar deze routes; de backend praat
server-to-server met Operaton.

`deploy` accepteert ruwe DMN-XML en vereist geen vooraf geregistreerde
norm-identifier, zodat ook een geüpload of gegenereerd bestand zonder
registratie-entry gedeployed kan worden. De route is een dunne wrapper om
`operatonService.deployDrd()`.

`evaluate/:decisionKey` is een **ruwe passthrough**: het antwoord van Operaton
wordt byte-voor-byte en met dezelfde statuscode doorgegeven — de success-array of
het exception-object — en dus *niet* in de gebruikelijke
`{ success, data }`-envelope, omdat de aanroepende tab de JSON van Operaton
zelf leest. `evaluateRaw()` geeft ook de request-body ongewijzigd door en slaat
de type-inferentie over die `evaluateDecision()` voor zijn eigen (andere)
aanroepcontract toepast; de DMN-tab stelt de body al in Operaton-vorm samen, dus
opnieuw inpakken zou die dubbel verpakken.

Beide routes zijn beschreven in de [API Specification](../reference/api-specification.md).

### DMN-discovery

```
GET /v1/dmns?endpoint={sparql_endpoint_url}
```

Bevraagt TriplyDB op alle `cprmv:DecisionModel`-resources op het opgegeven endpoint. Retourneert modellen met volledige variabelenlijsten en governance-/leveranciersmetadata. Per endpoint 5 minuten gecached.

```
GET /v1/dmns/:identifier?endpoint={url}
```

Retourneert volledige metadata voor een enkele DMN op basis van zijn `dct:identifier`-waarde.

```
GET /v1/dmns/enhanced-chain-links?endpoint={url}
```

Retourneert alle ketenkoppelingen inclusief zowel exacte identifier-matches als semantische `skos:exactMatch`-matches. Elke koppeling bevat een `matchType`-veld: `"exact"`, `"semantic"` of `"both"`.

```
GET /v1/dmns/semantic-equivalences?endpoint={url}
```

Retourneert alle variabelenparen uit verschillende DMNs die een `skos:exactMatch`-concept-URI delen.

```
GET /v1/dmns/cycles?endpoint={url}
```

Retourneert circulaire afhankelijkheden gedetecteerd via semantische koppelingen (3-hop-traversal).

### Chain-discovery

```
GET /v1/chains?endpoint={url}
```

Retourneert alle DMN-paren waarbij een outputvariabele van het ene model exact op identifier overeenkomt met een inputvariabele van een ander.

### Ketenuitvoering

```
POST /v1/chains/execute
```

Request body:

```json
{
  "chain": ["SVB_LeeftijdsInformatie", "SZW_BijstandsnormInformatie"],
  "inputs": { "geboortedatum": "1960-01-01" },
  "endpoint": "https://api.open-regels.triply.cc/..."
}
```

Voert de keten sequentieel uit, met flattening van outputs naar inputs tussen stappen. Retourneert resultaten per stap en de gecombineerde eindoutput. Een keten die halverwege faalt antwoordt met een problem-details-fout **en** behoudt het gedeeltelijke resultaat onder `data`, zodat de uitgevoerde stappen en hun outputs niet verloren gaan.

```
POST /v1/dmns/drd/deploy
```

Voegt gedeployde DMN's samen tot één DRD en deployt die naar Operaton. Zie [DRD-generatie](drd-generation.md).

### eDOCS

```
GET  /v1/edocs/status
POST /v1/edocs/workspaces/ensure
POST /v1/edocs/documents
GET  /v1/edocs/workspaces/:workspaceId/documents
```

Integreert met het OpenText eDOCS-documentmanagementsysteem. Gebruikt door het RIP Fase 1-proces om project-workspaces aan te maken en documenten te dossieren. In stub-modus (`EDOCS_STUB_MODE=true`, default) retourneren alle methoden realistische nepresponses zodat het proces end-to-end draait voordat een live eDOCS-server beschikbaar is.

Zie [eDOCS-integratie](edocs-integration.md), en de [API Specification](../reference/api-specification.md) voor request- en responsedetails.

### TriplyDB-proxy

```
POST /v1/triplydb/query
```

Request body:

```json
{
  "endpoint": "https://api.open-regels.triply.cc/...",
  "query": "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 5"
}
```

Voert een SPARQL-query uit tegen een door de aanroeper opgegeven endpoint. **Elke query die de Query Editor van de frontend verstuurt gaat hierlangs** — de editor haalt endpoints niet langer vanuit de browser op, en de vroegere fallback-proxy `api.allorigins.win` is verdwenen. Het endpoint passeert eerst de [uitgaande controle](#outbound-guard): het moet `https:` zijn, geen credentials bevatten en naar een openbaar adres verwijzen, anders antwoordt de route `400 INVALID_INPUT` voordat er een request wordt gedaan.

### Normen

```
GET /v1/norms?endpoint={url}&rulesetid={ruleset}&applicable_date={YYYY-MM-DD}&cprmv_version={0.3.0|0.3.2|0.4.1}
```

Retourneert alle `cprmv:Rule`-paden en normen vanuit het geconfigureerde TriplyDB-endpoint in het publicatieformaat dat de normenpublisher van de SPARQL-editor consumeert. Elk regelobject spiegelt exact de vorm van `cprmv-example.json`: volledig-gekwalificeerde RDF/CPRMV-sleutels voor `type`, `id`, `definition` en `contains`; korte sleutels voor `situatie`, `norm`, `per`, `rulesetid`, `applicable_date` en `rule_id_path`. De volledig-gekwalificeerde sleutels dragen de namespace van de **geselecteerde `cprmv_version`** (zie hieronder).

Bovenliggende regels en hun `cprmv:contains`-kinderen worden geaggregeerd tot één geneste object per ouder. De invoegvolgorde van sleutels blijft consistent tussen runs:

```
type, id, definition, contains?, situatie?, norm?, per?, rulesetid, applicable_date, rulesetid_index, rule_id_path, rule_id_path_key
```

Drie velden zijn afgeleid van `rule_id_path` en emit JSON `null` wanneer het pad niet overeenkomt met de canonieke vorm `<rulesetid>_<YYYY-MM-DD>_<index>[, <rest>]`:

| Veld               | Bron uit `rule_id_path`                                     | Voorbeeld                              |
| ------------------ | ----------------------------------------------------------- | -------------------------------------- |
| `applicable_date`  | Het `_YYYY-MM-DD_`-segment                                  | `"2025-07-01"`                         |
| `rulesetid_index`  | Het integer na de datum                                     | `0`                                    |
| `rule_id_path_key` | Pad met datum en index verwijderd; stabiel over versies     | `"BWBR0002471, Artikel 2, lid 6"`     |

De responsenvelop draagt ook een `aggregations`-blok naast `rules`:

```
data: {
  total: <number>,
  aggregations: { norms_per_rulesetid: { "<rulesetid>": <count>, ... } },
  rules: [...]
}
```

Tellingen gelden over de gefilterde resultatenset, dus `total` is gelijk aan de som van alle `norms_per_rulesetid`-waarden. Gebruik dit om samenvattingen op regelset-niveau te renderen zonder opnieuw te tellen op de client.

**Datasetversiebeheer en HTTP-cacheheaders**

Elke BWB-regelset (BWBR0002471, BWBR0015703, …) draagt versiemetadata per regelset, gepubliceerd door de CPSV editor (zie [CPRMV RuleSet / Dataset-generatie](../../cpsv-editor/developer/cprmv-dataset-generation.md)). **Waar die metadata staat hangt af van `cprmv_version`:** voor `0.3.0`/`0.3.2` is het een `cprmv:Dataset`-resource (met `dct:issued` + `dcat:version`); voor `0.4.1` is er geen `cprmv:Dataset` en wordt het uit de `cprmv:RuleSet` gelezen (`cprmv:validFrom`, dat tevens als `published_at` dient — zie de tabel hieronder). Eén regelset kan meerdere records hebben — verschillende toepasselijke perioden van dezelfde wet (bijv. BWBR0015703 op `2025-01-01` en `2026-01-01`) zijn **gelijktijdig en even gezaghebbend**, geen concurrerende versies. Eén `/v1/norms`-respons kan meerdere regelsets bestrijken, elk met meerdere records; de envelop draagt daarom een `dataset_versions`-map gekeyd op `cprmv:rulesetId`, waarbij elke waarde een **lijst** met records is:

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

De lijst is vooraf gesorteerd: **`version` aflopend met nulls achteraan, gelijke waarden gebroken door `published_at` aflopend**. Element `[0]` is de meest recente toepasselijke versie van die regelset.

Drie velden per entry:

| Veld           | Bron (0.3.x / 0.4.1)              | Opmerkingen |
| -------------- | --------------------------------- | ----------- |
| `version`      | `dcat:version` / `cprmv:validFrom` | **Nu voor elke regelset aanwezig.** Sinds v1.10.5 leidt de editor de versie van elke regelset af uit de BWB-datum die de eigen regels dragen (hun `ruleIdPath`), zodat ook niet-primaire regelsets zijn geversioneerd. (`null` blijft alleen over voor legacy-data die vóór die wijziging is gepubliceerd.) |
| `published_at` | `dct:issued` / `cprmv:validFrom`   | **0.3.x:** het publicatietijdstempel van het `cprmv:Dataset`-record — verandert bij elke (her)publicatie, het primaire signaal voor cachegeldigheid. **0.4.1:** er is geen `dct:issued`, dus `cprmv:validFrom` dient als `published_at` (zie de waarschuwing hieronder). |
| `title`        | `dct:title`                       | Alleen primaire regelset — de editor kent alleen de menselijke titel van het `legalResource` van de dienst. `null` voor niet-primaire regelsets. |

!!! warning "0.4.1-cachekanttekening"
    Voor `cprmv_version=0.4.1` is `published_at` gelijk aan `cprmv:validFrom` (de toepasselijke datum), niet aan een publicatietijdstempel. Een herpublicatie van een RuleSet **met dezelfde `validFrom`** maar gewijzigde regelwaarden verandert de ETag/`Last-Modified` **niet**, dus een gecachete 0.4.1-respons kan tot `max-age` (1 u) na een correctie op dezelfde datum worden geserveerd. `0.3.x` heeft deze kanttekening niet (`dct:issued` loopt op bij elke publicatie). Een toekomstige fix is het emitteren van `dct:issued`/`prov:generatedAtTime` op de 0.4.1-RuleSet.

**CPRMV-versieselectie (`?cprmv_version=`)**

De optionele queryparameter `cprmv_version` selecteert welke CPRMV-vocabulaireversie het endpoint **bevraagt en uitlevert** — een van `0.3.0`, `0.3.2` of `0.4.1` (anders → `400 INVALID_PARAM`). Default is `0.3.0`, wat het historische gedrag behoudt. De gekozen waarde wordt teruggegeven in het envelopveld `cprmv_version`, en de volledig-gekwalificeerde regelsleutels (`type`, `id`, `definition`, `contains`) dragen de namespace van die versie:

| `cprmv_version` | Namespace gebonden aan `cprmv:` | Bron van metadata per regelset |
| --------------- | ------------------------------- | ------------------------------ |
| `0.3.0` (default) | `https://cprmv.open-regels.nl/0.3.0/` | `cprmv:Dataset` |
| `0.3.2` | `https://cprmv.open-regels.nl/0.3.2/` | `cprmv:Dataset` |
| `0.4.1` | `https://standaarden.open-regels.nl/standards/cprmv/0.4.1#` | `cprmv:RuleSet` |

Alle drie de versies dragen **platte `cprmv:Rule`-resources met identieke predicaten** (`id`, `definition`, `rulesetId`, `ruleIdPath`, `situatie`, `norm`), dus de regels-query is één vorm met een verwisselde namespace. De gekozen versie wordt doorgegeven aan de regels-query, de dataset-metadata-query (cache gekeyd op endpoint **+ versie**), de uitvoersleutels, het `cprmv_version`-veld en de ETag-signature — zodat verschillende versies nooit een cache-entry delen.

!!! warning "Gewijzigde semantiek"
    `cprmv_version` beschreef voorheen "het vocabulaire dat de backend spreekt, onafhankelijk van de data". Het weerspiegelt nu de **gevraagde** versie en daarmee de namespace van de geretourneerde data. Afnemers die op `0.3.0` vastzaten merken geen verschil (het is de default).

Wanneer **elke** rulesetid in de respons ten minste één `dataset_versions`-entry heeft, draagt de respons strong HTTP-cacheheaders:

```
ETag: "3c899856"
Last-Modified: Fri, 15 May 2026 07:45:36 GMT
Cache-Control: public, max-age=3600
```

De `ETag` is een opaque 8-hex-hash over elk `(version, published_at)`-paar in `dataset_versions` plus alle requestparameters die de vorm van het response beïnvloeden. `title` is bewust uitgesloten — uitsluitend informatief, en een titel-only-update zou hoe dan ook arriveren als een nieuwe `dct:issued`. `Last-Modified` is de maximum `published_at` over *alle* records in de respons (niet alleen de eerste per regelset), dus de `If-Modified-Since` van een afnemer retourneert pas `304 Not Modified` wanneer er niets in hun query opnieuw is gepubliceerd.

Conditionele requests worden gehonoreerd via Express's `req.fresh`:

```http
GET /v1/norms HTTP/1.1
If-None-Match: "3c899856"
```

Voor queries op een enkele rulesetid (`?rulesetid=<id>`) vindt de 304-check **vóór** de dure rules-SPARQL-query plaats — alleen de goedkope (gecachete) metadata-query draait voor een 304-respons. Voor multi-rulesetid-queries moet de rules-query eerst draaien om te weten welke rulesetid's in de respons verschijnen.

Wanneer **enige** rulesetid in de respons een versierecord mist (een `cprmv:Dataset` voor 0.3.x, een `cprmv:RuleSet` voor 0.4.1), wordt `Cache-Control: no-cache` gezet en worden `ETag` / `Last-Modified` weggelaten. Veilig-by-default: afnemers moeten altijd opnieuw ophalen totdat elke BWB die zij bevragen met ten minste één versierecord is gepubliceerd. Tijdens de periode van uitrol-vanaf-nul betekent dit dat caching geleidelijk in werking treedt naarmate er metadata wordt gepubliceerd.

Dataset-metadata wordt 60 seconden in-memory gecached, gekeyd op endpoint-URL **en `cprmv_version`** (zodat de `cprmv:Dataset`- en `cprmv:RuleSet`-metadata-queries nooit een cache-entry delen).

**Queryparameters** (alle optioneel, mogen worden gecombineerd):

| Parameter         | Beschrijving                                                                                                                                                          |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `endpoint`        | SPARQL-endpoint-URL. Default `config.triplydb.endpoint` (`TRIPLYDB_ENDPOINT`) wanneer weggelaten, conform het patroon dat `/v1/dmns` gebruikt.                        |
| `rulesetid`       | Filter op exact-match van `cprmv:rulesetId` (bijv. `BWBR0015703`). Moet voldoen aan `/^[A-Za-z0-9_-]+$/`, anders wordt de request afgewezen met `400 INVALID_PARAM`.  |
| `applicable_date` | Filter op het gedateerde segment van `cprmv:ruleIdPath` (bijv. `2026-01-01` matcht paden die `_2026-01-01_` bevatten). Moet voldoen aan `/^\d{4}-\d{2}-\d{2}$/` of `400`. |
| `cprmv_version`   | CPRMV-vocabulaireversie om te bevragen en uit te leveren: een van `0.3.0`, `0.3.2`, `0.4.1` (anders `400 INVALID_PARAM`). Default `0.3.0`. Selecteert de `cprmv:`-namespace en het metadatamodel (`cprmv:Dataset` vs `cprmv:RuleSet`) — zie de subsectie **CPRMV-versieselectie** hierboven. |

Gevalideerde filterwaarden worden server-side toegepast als SPARQL `FILTER`-clauses: exact-match op `?rulesetId` en `CONTAINS(STR(?ruleIdPath), "_<date>_")`. Filters worden pas geïnterpoleerd na het passeren van de regex-poort, waardoor SPARQL-injectie onmogelijk is.

**Voorbeeldrespons — platte regel** (meest voorkomend; geen `contains`-sleutel):

```json
{
  "success": true,
  "data": {
    "total": 1,
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
      ]
    },
    "cprmv_version": "0.3.0",
    "aggregations": {
      "norms_per_rulesetid": {
        "BWBR0015703": 1
      }
    },
    "rules": [
      {
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "https://cprmv.open-regels.nl/0.3.0/Rule",
        "https://cprmv.open-regels.nl/0.3.0/id": "onderdeel a.",
        "https://cprmv.open-regels.nl/0.3.0/definition": "een alleenstaande van 18, 19 of 20 jaar: € 337,98;",
        "situatie": "een alleenstaande van 18, 19 of 20 jaar",
        "norm": "337,98",
        "rulesetid": "BWBR0015703",
        "applicable_date": "2025-07-01",
        "rulesetid_index": 0,
        "rule_id_path": "BWBR0015703_2025-07-01_0, Artikel 20, lid 1, onderdeel a.",
        "rule_id_path_key": "BWBR0015703, Artikel 20, lid 1, onderdeel a."
      }
    ]
  },
  "timestamp": "2026-05-14T14:00:00.000Z"
}
```

**Voorbeeldrespons — regel met geneste kinderen** (conditionele `contains`-map; alleen geëmit wanneer de ouder `cprmv:contains`-koppelingen naar subregels heeft):

```json
{
  "success": true,
  "data": {
    "total": 1,
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
      ]
    },
    "cprmv_version": "0.3.0",
    "aggregations": {
      "norms_per_rulesetid": {
        "BWBR0015703": 1
      }
    },
    "rules": [
      {
        "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "https://cprmv.open-regels.nl/0.3.0/Rule",
        "https://cprmv.open-regels.nl/0.3.0/id": "onderdeel r.",
        "https://cprmv.open-regels.nl/0.3.0/definition": "inkomsten uit arbeid van een alleenstaande ouder ...",
        "https://cprmv.open-regels.nl/0.3.0/contains": {
          "onderdeel 1°.": {
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "https://cprmv.open-regels.nl/0.3.0/Rule",
            "https://cprmv.open-regels.nl/0.3.0/id": "onderdeel 1°.",
            "https://cprmv.open-regels.nl/0.3.0/definition": "hij de volledige zorg heeft voor een tot zijn last komend kind tot 12 jaar,"
          },
          "onderdeel 2°.": {
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#type": "https://cprmv.open-regels.nl/0.3.0/Rule",
            "https://cprmv.open-regels.nl/0.3.0/id": "onderdeel 2°.",
            "https://cprmv.open-regels.nl/0.3.0/definition": "de periode van zes maanden, bedoeld in onderdeel n, is verstreken, en"
          }
        },
        "situatie": "inkomsten uit arbeid van een alleenstaande ouder ...",
        "norm": "173,87",
        "per": "maand, gedurende een aaneengesloten periode van maximaal 30 maanden, ...",
        "rulesetid": "BWBR0015703",
        "applicable_date": "2025-07-01",
        "rulesetid_index": 0,
        "rule_id_path": "BWBR0015703_2025-07-01_0, Artikel 31, lid 2, onderdeel r.",
        "rule_id_path_key": "BWBR0015703, Artikel 31, lid 2, onderdeel r."
      }
    ]
  },
  "timestamp": "2026-05-14T14:00:00.000Z"
}
```

!!! note "`contains` wordt door de huidige editor niet geproduceerd"
    De vorm met geneste kinderen hierboven wordt *alleen* gematerialiseerd wanneer er
    `cprmv:contains`-triples in TriplyDB aanwezig zijn. Sinds CPSV editor v1.10.5 worden die
    **niet** meer geëmit: geneste subclausules (opsommingsitems zoals *"onderdeel 1°./2°./3°."*)
    worden bij het importeren **in de `cprmv:definition` van de bovenliggende regel gevouwen**
    in plaats van als `cprmv:contains`-kinderen gepubliceerd. Het endpoint behoudt de
    `OPTIONAL { ?rule cprmv:contains … }`-tak voor achterwaartse compatibiliteit met eventuele
    legacy-data, maar de huidige acceptance/productie-responses zijn plat (de bovenliggende
    definitie draagt de volledige wettekst). Het veld `per` wordt eveneens alleen gevuld
    wanneer een `cprmv:per`-triple bestaat.

**Voorbeeldrequests:**

```
GET /v1/norms
GET /v1/norms?rulesetid=BWBR0015703
GET /v1/norms?applicable_date=2026-01-01
GET /v1/norms?rulesetid=BWBR0015703&applicable_date=2026-01-01
GET /v1/norms?cprmv_version=0.4.1
GET /v1/norms?cprmv_version=0.3.2&rulesetid=BWBR0015703
GET /v1/norms?endpoint=https://api.open-regels.triply.cc/datasets/stevengort/RONL/services/RONL/sparql
```

---

### Asset-opslag
```
GET    /v1/assets/bpmn
POST   /v1/assets/bpmn
DELETE /v1/assets/bpmn/:id
GET    /v1/assets/bpmn/by-bpmn-id/:bpmnProcessId

GET    /v1/assets/forms
POST   /v1/assets/forms
DELETE /v1/assets/forms/:id

GET    /v1/assets/documents
POST   /v1/assets/documents
DELETE /v1/assets/documents/:id
```

Persisteert BPMN-processen, formulierschema's en documenttemplates naar PostgreSQL. Alle routes retourneren `503 DB_NOT_CONFIGURED` wanneer `DATABASE_URL` ontbreekt. De upserts, de deploymarkering en het verwijderen van een ROPA-record valideren hun invoer voordat die Postgres bereikt, en antwoorden `400 INVALID_INPUT` met een detail dat elk afgekeurd veld noemt; de controles volgen de eigen constraints van de database, en een lege titel, id of naam wordt geweigerd op de velden die een record identificeren. Zie [Asset-opslag](asset-storage.md) voor de service-architectuur en de [API Specification](../reference/api-specification.md) voor de vorm van requests en responses.

---

## Database

De backend verbindt met een PostgreSQL-database via een `pg.Pool`. De pool wordt geïnitialiseerd in `src/db/pool.ts` wanneer `DATABASE_URL` aanwezig is in de omgeving. Wanneer de variabele afwezig is, is `pool` `null` en retourneren alle asset-endpoints `503`.

Schemamigraties draaien automatisch bij opstart via `migrate()` in `src/db/migrate.ts`, aangeroepen vanuit `startServer()` vóór `app.listen()`. De migratie is idempotent (`CREATE TABLE IF NOT EXISTS`).
```
src/db/
├── pool.ts       — pg.Pool-initialisatie, error listener, null-if-unconfigured guard
└── migrate.ts    — idempotente DDL: process_definitions, form_schemas, document_templates
```

Zie [PostgreSQL-deployment](deployment-postgresql.md) voor Azure-provisioning.

---

## SPARQL-service

`sparql.service.ts` bouwt en voert alle SPARQL-queries uit tegen TriplyDB. Belangrijke functies:

```typescript
findAllDmns(endpoint: string): Promise<DmnModel[]>
findEnhancedChainLinks(endpoint: string): Promise<EnhancedChainLink[]>
findSemanticEquivalences(endpoint: string): Promise<SemanticEquivalence[]>
```

De query `findEnhancedChainLinks` gebruikt een `BIND(IF(...))`-patroon om elke koppeling te categoriseren als `exact`, `semantic` of `both`, en expandeert vervolgens `both`-entries na de query in twee afzonderlijke records. Dit is het mechanisme dat beschreven wordt in [Enhanced Validation](enhanced-validation.md).

Een aparte `norms.service.ts` handelt de `cprmv:Rule`-publicatieformaat-query af die `/v1/norms` ondersteunt. Hij bouwt de query dynamisch op — filter-clauses (rulesetid exact-match, applicable-date `CONTAINS`) worden pas geïnjecteerd na upstream regex-validatie — en aggregeert vervolgens ouder/kind-rijen tot geneste objecten met deterministische sleutelvolgorde die overeenkomt met `cprmv-example.json`.

---

## Orchestratieservice

`orchestration.service.ts` voert sequentiële ketens uit:

1. Haal DMN-metadata op voor elke stap vanuit de SPARQL-service (gecached)
2. Gebruik voor de eerste stap de door de gebruiker opgegeven inputs
3. Bouw voor elke volgende stap inputs op door:
   - Alle outputs van eerdere stappen plat te maken tot één map
   - Voor semantische matches: hernoem outputvariabele-sleutels zodat ze overeenkomen met de verwachte input-identifiers
   - Te combineren met eventuele extra door de gebruiker opgegeven inputs
4. Roep `operaton.service.ts` aan voor elke stap
5. Accumuleer resultaten

Variabelen-flattening betekent dat een semantische keten zoals `heeftJuisteLeeftijd → leeftijd_requirement` transparant wordt overbrugd — de outputwaarde wordt doorgegeven onder de verwachte sleutel van de input.

---

## Operaton-service

`operaton.service.ts` roept de Operaton REST-API aan:

```
POST {OPERATON_BASE_URL}/decision-definition/key/{decisionRef}/evaluate
```

Request payload mapt naar het variabelenformaat van Operaton:

```json
{
  "variables": {
    "geboortedatum": { "value": "1960-01-01", "type": "String" }
  }
}
```

Voor DRD-uitvoering wordt hetzelfde endpoint gebruikt met de DRD-entry-point-identifier. Operaton handelt interne beslissingsafhankelijkheidsevaluatie af.

---

## eDOCS-service

`edocs.service.ts` omhult de OpenText eDOCS REST-API. Hij authenticeert eenmaal via `POST /connect`, cachet het `X-DM-DST`-sessietoken en authenticeert automatisch opnieuw bij `401`/`403`. Belangrijke methoden:

```typescript
ensureWorkspace(projectNumber: string, projectName: string): Promise<EdocsWorkspaceResult>
uploadDocument(workspaceId: string, filename: string, contentBase64: string, metadata: EdocsDocumentMetadata): Promise<EdocsDocumentResult>
getWorkspaceDocuments(workspaceId: string): Promise<...>
healthCheck(): Promise<{ status: 'up' | 'down' | 'stub' }>
```

Wanneer `EDOCS_STUB_MODE=true`, retourneren alle methoden realistische nepdata en loggen zij wat zij zouden hebben gedaan. De stub is transparant voor alle callers.

---

## External task worker

`externalTaskWorker.service.ts` pollt de external task-API van Operaton (`POST /external-task/fetchAndLock`) met long-polling (`asyncResponseTimeout: 20 000 ms`). Hij verwerkt twee topics:

| Topic                 | Leest                                                                                       | Schrijft                                                          |
| --------------------- | ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| `rip-edocs-workspace` | `projectNumber`, `projectName`                                                              | `edocsWorkspaceId`, `edocsWorkspaceName`, `edocsWorkspaceCreated` |
| `rip-edocs-document`  | `edocsWorkspaceId`, `documentTemplateId`, `edocsDocumentVariableName`, + templatevariabelen | `<edocsDocumentVariableName>` (bijv. `edocsIntakeReportId`)       |

`documentTemplateId` en `edocsDocumentVariableName` worden per ServiceTask geïnjecteerd via `camunda:inputParameter` in het BPMN, waardoor de enkele topic handler herbruikbaar is over alle drie de documentuploadstappen in het RIP Fase 1-proces.

De worker start binnen de callback van `app.listen()` en stopt in zowel de `SIGTERM`- als `SIGINT`-handlers.

---

## Logging

Gestructureerde logging met Winston en JSON-output. Alle serviceaanroepen loggen op `[INFO]`-niveau met context (endpoint, querylengte, aantal resultaten, latency). Fouten loggen op `[ERROR]` met stack traces. Het loglevel is configureerbaar via de omgevingsvariabele `LOG_LEVEL`.

---

## Foutafhandeling

Elke fout die de API zelf produceert is een **RFC 9457 problem details**-respons, `application/problem+json`:

```json
{
  "type": "about:blank",
  "title": "Bad Request",
  "status": 400,
  "detail": "…",
  "instance": "/v1/dmns",
  "code": "INVALID_INPUT"
}
```

`code` is een extension member en het veld waarop aanroepers vertakken — `INVALID_INPUT`, `MALFORMED_BODY`, `PAYLOAD_TOO_LARGE`, `DB_NOT_CONFIGURED` enzovoort. `type` is `about:blank`, omdat er geen documentatiepagina per soort probleem bestaat en een URL die nergens heen wijst slechter zou zijn dan geen. `instance` is het requestpad zonder querystring. Succesresponses zijn ongewijzigd en houden `{ success: true, data }`.

Dit verving in v2026.09.5 vijf verschillende envelopes. `POST /v1/dmns/evaluate/:decisionKey` is de enige uitzondering: die geeft de eigen fouten van Operaton ongewijzigd door, omdat de aanroeper de JSON van Operaton leest.

`middleware/error.middleware.ts` is de centrale handler. Een body die niet te parsen is krijgt **400 `MALFORMED_BODY`**, een body boven de limiet van 10 MB **413 `PAYLOAD_TOO_LARGE`** met die limiet in het detail, en andere body-parserfouten de eigen status van de parser als `INVALID_BODY` — parserfouten worden herkend aan hun type, zodat een willekeurige fout met een `status`-eigenschap nog steeds 500 geeft in plaats van zelf een respons te kiezen. Stack traces en interne context bereiken de client nooit.

---

## Performance

**Doelen:**

| Operatie                | Doel     |
| ----------------------- | -------- |
| Ketenuitvoering         | < 1000ms |
| Health-checkrespons     | < 100ms  |
| DMN-lijstquery          | < 500ms  |
| API-responstijd (p95)   | < 200ms  |

**Productiebaselines (Heusdenpasketen, 3 DMNs):**

| Meting                                   | Waargenomen |
| ---------------------------------------- | ----------- |
| Volledige ketenuitvoering                | ~827ms      |
| Health-check (incl. TriplyDB + Operaton) | ~180ms      |
| DMN-discovery (SPARQL + parsing)         | ~350ms      |
| TriplyDB round-trip-latency              | 150–200ms   |
| Operaton per-DMN-uitvoering              | 80–120ms    |

---

## Beveiliging

**HTTP-headers** — [Helmet](https://helmetjs.github.io/) is geconfigureerd om uitgebreide beveiligingsheaders te zetten op alle responses, waaronder `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options` en `Strict-Transport-Security`.

**CORS** — alleen origins die in `CORS_ORIGIN` staan zijn toegestaan. In productie is dit beperkt tot `https://linkeddata.open-regels.nl` en `https://cpsv.open-regels.nl`; acceptatie laat daarnaast beide omgevingen van de IOU-architectuurdocumentatie toe. Elke andere origin krijgt een gewone respons zonder `Access-Control-Allow-Origin`-header, die de browser vervolgens weigert — **behalve op de drie openbare, alleen-lezen mounts**, `/v1/ropa/public`, `/v1/bundles/public` en `/v1/openapi.json`, die bewust elke origin toestaan voor `GET` en `OPTIONS`. `isPublicPath` herkent die mounts of een pad daaronder, nooit een zusterroute die alleen hetzelfde voorvoegsel deelt; zie [RoPA Records — de openbare routes](ropa-records.md#publieke-route).

**Invoervalidatie** — request-inputs worden gecontroleerd voordat een serviceaanroep wordt gedaan, en een afgekeurde invoer antwoordt `400 INVALID_INPUT` met de betrokken velden, in plaats van als 500 terug te komen uit een achterliggend systeem. De grootte van de request body is beperkt tot 10 MB.

<a id="outbound-guard"></a>**Uitgaande controle** — de backend vraagt nooit een host op die een aanroeper noemde zonder die te controleren (v2026.09.5, [#142](https://github.com/sgort/linked-data-explorer/issues/142)). Er zijn twee lagen:

- **Bij de route** controleert `utils/outboundUrl.ts` elk door de aanroeper opgegeven SPARQL-endpoint — op `GET /norms`, de DMN-leesroutes, ketenuitvoering, de vendor-leesroutes, samengevoegde SHACL-validatie en `POST /triplydb/query` — en weigert het met `400 INVALID_INPUT` wanneer het geen `https:` is, credentials bevat of naar een intern adres verwijst. Interne adressen worden herkend in elke tekstuele IPv4- en IPv6-vorm, ook de IPv6-vormen waarin een IPv4-adres is opgenomen.
- **Bij het verbinden** levert `utils/outboundHttp.ts` de axios-client die elk request naar een door de aanroeper gekozen host gebruikt. De agents weigeren een naam die naar een intern adres *resolvet*, redirects worden opnieuw gecontroleerd, en de client zet `proxy: false`, omdat axios anders `HTTP(S)_PROXY` volgt met een tunnelagent die de controle overslaat.

TriplyDB-aanroepen die het token van de aanroeper doorsturen gaan alleen naar `https:`-hosts in `TRIPLYDB_ALLOWED_HOSTS`. Processen worden alleen naar de geconfigureerde Operaton gedeployd, via de gedeelde client met `OPERATON_API_KEY` — een request kan de Operaton-URL niet meer opgeven en geen credentials meesturen. `ALLOW_LOCAL_ENDPOINTS=true` laat `http:` en lokale adressen toe voor lokale ontwikkeling, en staat nooit aan op ACC of productie.

**CSP-rapporten** — `POST /v1/csp-reports` ontvangt de Content-Security-Policy-schendingsrapporten van de frontend in beide formaten (`application/csp-report` en `application/reports+json`, tot 64 KB) en logt per schending één waarschuwingsregel. Er wordt niets opgeslagen.

**Omgevingsvariabelen** — alle gevoelige configuratie (TriplyDB-endpoint-URL's, Operaton API-URL's, CORS-origins, eDOCS-credentials) wordt opgeslagen in omgevingsvariabelen en nooit hardcoded. eDOCS-specifieke variabelen: `EDOCS_BASE_URL`, `EDOCS_LIBRARY`, `EDOCS_USER_ID`, `EDOCS_PASSWORD`, `EDOCS_STUB_MODE`.

**Foutresponses** — de centrale error handler schrobt stack traces en interne context voordat responses worden teruggegeven aan clients, om te garanderen dat geen implementatiedetails worden blootgelegd.

---

## Conformiteit met API Design Rules van de Nederlandse Overheid

De API volgt de [Nederlandse API Design Rules van de Overheid](https://publicatie.centrumvoorstandaarden.nl/api/adr/) voor interoperabiliteit en standaardisatie.

**Geïmplementeerde regels:**

| Regel  | Beschrijving                                    | Implementatie                          |
| ------ | ----------------------------------------------- | -------------------------------------- |
| API-20 | Major versie in URI                             | `/v1/*`-endpoints                      |
| API-57 | Versieheader in responses                       | `API-Version: <release>` op elke respons |
| API-16 | Gebruik OpenAPI voor documentatie               | OpenAPI 3.1-beschrijving (v2026.09.5)  |
| API-51 | Publiceer het OpenAPI-document op een vaste plek | `/v1/openapi.json` (v2026.09.5)       |
| API-05 | Gebruik zelfstandige naamwoorden voor resources | `dmns`, `chains`, `health`             |
| API-54 | Meervoud/enkelvoud-naamgeving                   | Correct gebruik overal                 |
| API-48 | Geen trailing slashes                           | Afgedwongen in routing                 |
| API-53 | Verberg implementatiedetails                    | Schone service-abstracties             |

**Taalnotitie (API-04)** — technische endpoint-namen (`health`, `version`) volgen internationale conventie in het Engels. Business-resource-namen (`dmns`, `chains`) volgen de brondata. Nederlandse variabelennamen (bijv. `geboortedatum`) worden zoals zij zijn behouden vanuit de DMN-definities.

**Gecontroleerd in CI.** `npm run lint:openapi` lint de gepubliceerde beschrijving met Spectral tegen de NL API Design Rules 2.2.1 in beide backend-deployworkflows. Fouten volgen de problem-details-eisen van de regels (`nlgov:problem-*`). Waar de API van een regel afwijkt, is de uitzondering per pad vastgelegd in `openapi/.spectral.yaml` in plaats van globaal uitgezet.
| API-10         | Resource-collecties met paginering      | v1.0.0         |