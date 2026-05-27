# Backend-architectuur

De backend is een Node.js/Express TypeScript-API. Het staat tussen de React-frontend en twee externe services: TriplyDB (SPARQL-kennisgraaf) en Operaton (DMN-uitvoeringsengine). De functies zijn SPARQL-queries uitvoeren, DMN-keten-orkestratie, variabelenmapping tussen ketenstappen en het proxyen van dynamische TriplyDB-endpointaanroepen.

---

## API-versiebeheer

Alle endpoints volgen `/v1/*`. Legacy-endpoints `/api/*` bestaan met `Deprecation`-responseheaders voor achterwaartse compatibiliteit. De versie wordt in elke respons opgenomen via de `API-Version`-header, conform de Nederlandse API Design Rules API-20 en API-57 van de Overheid.

---

## Endpoints

### Health

```
GET /v1/health
```

Retourneert servicehealth inclusief latency-checks van TriplyDB en Operaton. Gebruikt door CI/CD-pipelines en de statusindicator van de frontend.

```json
{
  "name": "Linked Data Explorer Backend",
  "version": "0.4.0",
  "environment": "production",
  "status": "healthy",
  "uptime": 3600,
  "services": {
    "triplydb": { "status": "up", "latency": 145 },
    "operaton": { "status": "up", "latency": 98 }
  }
}
```

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

Voert de keten sequentieel uit, met flattening van outputs naar inputs tussen stappen. Retourneert resultaten per stap en de gecombineerde eindoutput.

```
POST /v1/chains/execute/heusdenpas
```

Convenience-endpoint voor de vaste driestaps-Heusdenpasketen met productie-testdata. Doel-uitvoeringstijd: <1000ms. Zie [API Reference](../reference/api-reference.md) voor het volledige request/response.

```
POST /v1/chains/export
```

Genereert een DRD XML-bestand vanuit een keten en deployt het naar Operaton. Zie [DRD-generatie](drd-generation.md).

### eDOCS

```
GET  /v1/edocs/status
POST /v1/edocs/workspaces/ensure
POST /v1/edocs/documents
GET  /v1/edocs/workspaces/:workspaceId/documents
```

Integreert met het OpenText eDOCS-documentmanagementsysteem. Gebruikt door het RIP Fase 1-proces om project-workspaces aan te maken en documenten te dossieren. In stub-modus (`EDOCS_STUB_MODE=true`, default) retourneren alle methoden realistische nepresponses zodat het proces end-to-end draait voordat een live eDOCS-server beschikbaar is.

Zie [eDOCS-integratie](edocs-integration.md) en de [API Reference](../reference/api-reference.md#edocs) voor request-/responsedetails.

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

Proxyt een SPARQL-query naar een willekeurig TriplyDB-endpoint, om CORS-restricties te omzeilen. Gebruikt door de Query Editor in de frontend voor dynamische endpoint-ondersteuning.

### Normen

```
GET /v1/norms?endpoint={url}&rulesetid={ruleset}&applicable_date={YYYY-MM-DD}
```

Retourneert alle `cprmv:Rule`-paden en normen vanuit het geconfigureerde TriplyDB-endpoint in het publicatieformaat dat de normenpublisher van de SPARQL-editor consumeert. Elk regelobject spiegelt exact de vorm van `cprmv-example.json`: volledig-gekwalificeerde RDF/CPRMV-sleutels voor `type`, `id`, `definition` en `contains`; korte sleutels voor `situatie`, `norm`, `per`, `rulesetid`, `applicable_date` en `rule_id_path`.

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

Elke BWB-regelset (BWBR0002471, BWBR0015703, …) wordt door de CPSV editor gepubliceerd als een afzonderlijke `cprmv:Dataset`-resource in TriplyDB (zie [CPRMV-datasetgeneratie](../../cpsv-editor/developer/cprmv-dataset-generation.md)). Eén regelset kan meerdere Dataset-records hebben — verschillende toepasselijke perioden van dezelfde wet (bijv. BWBR0015703 op `2025-01-01` en `2026-01-01`) zijn **gelijktijdig en even gezaghebbend**, geen concurrerende versies. Eén `/v1/norms`-respons kan meerdere regelsets bestrijken, elk met meerdere records; de envelop draagt daarom een `dataset_versions`-map gekeyd op `cprmv:rulesetId`, waarbij elke waarde een **lijst** met records is:

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

De lijst is vooraf gesorteerd: **`version` aflopend met nulls achteraan, gelijke waarden gebroken door `published_at` aflopend**. Element `[0]` is de meest recente toepasselijke versie van die regelset. Niet-primaire regelsets (geen `dcat:version` in TriplyDB) vallen terug op pure `published_at` desc-volgorde.

Drie velden per entry, waarvan twee nullable:

| Veld           | Bron           | Altijd aanwezig? |
| -------------- | -------------- | ---------------- |
| `version`      | `dcat:version` | Alleen primaire regelset — de editor kent alleen de versie van het `legalResource.bwbId` van de dienst. `null` voor niet-primaire regelsets. |
| `published_at` | `dct:issued`   | Ja. Het tijdstempel van de publicatie van dit `cprmv:Dataset`-record — het betekenisvolle signaal voor cachegeldigheid. |
| `title`        | `dct:title`    | Alleen primaire regelset. `null` voor niet-primaire regelsets. |

`cprmv_version` is een enkele string die de versie van het CPRMV-vocabulaire naar buiten brengt die de backend spreekt — onafhankelijk van welke datasets zijn gepubliceerd.

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

Wanneer **enige** rulesetid in de respons `cprmv:Dataset`-records mist, wordt `Cache-Control: no-cache` gezet en worden `ETag` / `Last-Modified` weggelaten. Veilig-by-default: afnemers moeten altijd opnieuw ophalen totdat elke BWB die zij bevragen is gepubliceerd met ten minste één `cprmv:Dataset`-record. Tijdens de periode van uitrol-vanaf-nul betekent dit dat caching geleidelijk in werking treedt naarmate Datasets worden gepubliceerd.

Dataset-metadata wordt 60 seconden in-memory gecached per endpoint-URL.

**Queryparameters** (alle optioneel, mogen worden gecombineerd):

| Parameter         | Beschrijving                                                                                                                                                          |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `endpoint`        | SPARQL-endpoint-URL. Default `config.triplydb.endpoint` (`TRIPLYDB_ENDPOINT`) wanneer weggelaten, conform het patroon dat `/v1/dmns` gebruikt.                        |
| `rulesetid`       | Filter op exact-match van `cprmv:rulesetId` (bijv. `BWBR0015703`). Moet voldoen aan `/^[A-Za-z0-9_-]+$/`, anders wordt de request afgewezen met `400 INVALID_PARAM`.  |
| `applicable_date` | Filter op het gedateerde segment van `cprmv:ruleIdPath` (bijv. `2026-01-01` matcht paden die `_2026-01-01_` bevatten). Moet voldoen aan `/^\d{4}-\d{2}-\d{2}$/` of `400`. |

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

!!! note
    De vorm met geneste kinderen hierboven is het formaat dat het endpoint zal produceren *wanneer* `cprmv:contains`-triples aanwezig zijn in TriplyDB. De huidige acceptance-dataset bevat er geen, dus elke respons is momenteel plat. End-to-end-validatie van het geneste geval is nog uitstaand: upload een dataset met `cprmv:contains`-koppelingen en verifieer dat `/v1/norms` deze correct materialiseert in het publicatieformaat.

**Voorbeeldrequests:**

```
GET /v1/norms
GET /v1/norms?rulesetid=BWBR0015703
GET /v1/norms?applicable_date=2026-01-01
GET /v1/norms?rulesetid=BWBR0015703&applicable_date=2026-01-01
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

Persisteert BPMN-processen, formulierschema's en documenttemplates naar PostgreSQL. Alle routes retourneren `503 DB_NOT_CONFIGURED` wanneer `DATABASE_URL` ontbreekt. Zie [Asset-opslag](asset-storage.md) voor de service-architectuur en [API Reference](../reference/api-reference.md#asset-storage) voor volledige request-/responsedocumentatie.

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

Een centrale `errorHandler.ts`-middleware vangt niet-afgevangen fouten op en retourneert gestandaardiseerde JSON-foutresponses met passende HTTP-statuscodes. SPARQL- en Operaton-fouten worden omhuld met beschrijvende berichten voordat zij worden teruggegeven aan de frontend. Geen gevoelige data is opgenomen in foutresponses.

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

**CORS** — alleen origins die in `CORS_ORIGIN` staan zijn toegestaan. In productie is dit beperkt tot `https://linkeddata.open-regels.nl` en `https://cpsv.open-regels.nl`. Alle andere origins ontvangen een CORS-afwijzing.

**Invoervalidatie** — typechecking wordt toegepast op alle request-inputs. Variabelennamen, DMN-identifiers en SPARQL-endpoint-URL's worden gevalideerd voordat een serviceaanroep wordt gedaan. De grootte van de request body is beperkt tot 10 MB.

**Omgevingsvariabelen** — alle gevoelige configuratie (TriplyDB-endpoint-URL's, Operaton API-URL's, CORS-origins, eDOCS-credentials) wordt opgeslagen in omgevingsvariabelen en nooit hardcoded. eDOCS-specifieke variabelen: `EDOCS_BASE_URL`, `EDOCS_LIBRARY`, `EDOCS_USER_ID`, `EDOCS_PASSWORD`, `EDOCS_STUB_MODE`.

**Foutresponses** — de centrale error handler schrobt stack traces en interne context voordat responses worden teruggegeven aan clients, om te garanderen dat geen implementatiedetails worden blootgelegd.

---

## Conformiteit met API Design Rules van de Nederlandse Overheid

De API volgt de [Nederlandse API Design Rules van de Overheid](https://publicatie.centrumvoorstandaarden.nl/api/adr/) voor interoperabiliteit en standaardisatie.

**Geïmplementeerde regels:**

| Regel  | Beschrijving                                    | Implementatie                          |
| ------ | ----------------------------------------------- | -------------------------------------- |
| API-20 | Major versie in URI                             | `/v1/*`-endpoints                      |
| API-57 | Versieheader in responses                       | `API-Version: 0.4.0` op elke respons   |
| API-05 | Gebruik zelfstandige naamwoorden voor resources | `dmns`, `chains`, `health`             |
| API-54 | Meervoud/enkelvoud-naamgeving                   | Correct gebruik overal                 |
| API-48 | Geen trailing slashes                           | Afgedwongen in routing                 |
| API-53 | Verberg implementatiedetails                    | Schone service-abstracties             |

**Taalnotitie (API-04)** — technische endpoint-namen (`health`, `version`) volgen internationale conventie in het Engels. Business-resource-namen (`dmns`, `chains`) volgen de brondata. Nederlandse variabelennamen (bijv. `geboortedatum`) worden zoals zij zijn behouden vanuit de DMN-definities.

**Gepland:**

| Regel          | Beschrijving                            | Doelversie     |
| -------------- | --------------------------------------- | -------------- |
| API-16, API-51 | OpenAPI 3.0-spec op `/v1/openapi.json`  | v0.5.0         |
| API-02         | Standaard foutresponse-formaat          | v0.5.0         |
| API-10         | Resource-collecties met paginering      | v1.0.0         |