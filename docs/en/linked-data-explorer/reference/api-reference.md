# API Reference

Base URL — production: `https://backend.linkeddata.open-regels.nl`
Base URL — acceptance: `https://acc.backend.linkeddata.open-regels.nl`

All endpoints are under `/v1/`. Every response includes an `API-Version` header. Legacy `/api/*` endpoints exist with `Deprecation` headers and will be removed in v2.0.0.

---

## Root

### `GET /`

Returns API metadata and a directory of current and legacy endpoint paths.

**Response:**

```json
{
  "name": "Linked Data Explorer Backend",
  "version": "0.4.0",
  "status": "running",
  "environment": "production",
  "documentation": "/v1/openapi.json",
  "health": "/v1/health",
  "endpoints": {
    "health": "/v1/health",
    "dmns": "/v1/dmns",
    "chains": "/v1/chains"
  },
  "legacy": {
    "health": "/api/health (deprecated)",
    "dmns": "/api/dmns (deprecated)",
    "chains": "/api/chains (deprecated)"
  }
}
```

---

## Health

### `GET /v1/health`

Returns service health and dependency status. Used by CI/CD pipelines and the frontend status indicator.

**Response:**

```json
{
  "name": "Linked Data Explorer Backend",
  "version": "0.4.0",
  "environment": "production",
  "status": "healthy",
  "uptime": 123.456,
  "timestamp": "2026-01-13T19:44:14.971Z",
  "services": {
    "triplydb": {
      "status": "up",
      "latency": 165,
      "lastCheck": "2026-01-13T19:44:15.401Z"
    },
    "operaton": {
      "status": "up",
      "latency": 119,
      "lastCheck": "2026-01-13T19:44:15.401Z"
    }
  },
  "documentation": "/v1/openapi.json"
}
```

**Response headers:**

```http
HTTP/1.1 200 OK
API-Version: 0.4.0
Content-Type: application/json
```

**`status` values:**

| Value | HTTP | Meaning |
|---|---|---|
| `healthy` | 200 | All dependencies operational |
| `degraded` | 503 | One or more dependencies down |
| `unhealthy` | 503 | Health check itself failed |

---

## DMN discovery

### `GET /v1/dmns`

Query TriplyDB for all published DMN decision models at the given endpoint.

**Query parameters:**

| Parameter | Required | Description |
|---|---|---|
| `endpoint` | Yes | SPARQL endpoint URL (URL-encoded) |

**Response:**

```json
{
  "success": true,
  "data": {
    "dmns": [
      {
        "id": "https://regels.overheid.nl/services/aow-leeftijd/dmn",
        "identifier": "SVB_LeeftijdsInformatie",
        "title": "AOW Leeftijdsberekening",
        "inputs": [
          { "identifier": "geboortedatum", "title": "Geboortedatum", "type": "Date" }
        ],
        "outputs": [
          { "identifier": "aanvragerIs181920", "title": "Aanvrager is 18/19/20", "type": "Boolean" }
        ],
        "validationStatus": "validated",
        "validatedByName": "Sociale Verzekeringsbank",
        "validatedAt": "2026-02-14",
        "vendorCount": 1,
        "vendors": [ "..." ]
      }
    ],
    "endpoint": "https://api.open-regels.triply.cc/...",
    "cached": false
  }
}
```

Response is cached per endpoint for 5 minutes. `cached: true` in subsequent responses.

---

### `GET /v1/dmns/:identifier`

Returns full metadata for a single DMN by its identifier.

**Path parameters:**

| Parameter | Description |
|---|---|
| `identifier` | The `dct:identifier` value of the DMN (e.g., `SVB_LeeftijdsInformatie`) |

**Query parameters:** `endpoint` (required)

**Response:** Same shape as a single entry in the `GET /v1/dmns` response array.

---

### `GET /v1/dmns/enhanced-chain-links`

Returns all DMN variable pairs that are connectable, including both exact identifier matches and semantic `skos:exactMatch` matches.

**Query parameters:** `endpoint` (required)

**Response:**

```json
{
  "success": true,
  "data": [
    {
      "dmn1": { "identifier": "SVB_LeeftijdsInformatie", "title": "..." },
      "dmn2": { "identifier": "SZW_BijstandsnormInformatie", "title": "..." },
      "outputVariable": "aanvragerIs181920",
      "inputVariable": "aanvragerIs181920",
      "variableType": "Boolean",
      "matchType": "exact",
      "sharedConcept": null
    },
    {
      "dmn1": { "identifier": "ZorgtoeslagVoorwaardenCheck", "title": "..." },
      "dmn2": { "identifier": "berekenrechtenhoogtezorg", "title": "..." },
      "outputVariable": "heeftJuisteLeeftijd",
      "inputVariable": "leeftijd_requirement",
      "variableType": "Boolean",
      "matchType": "semantic",
      "sharedConcept": "https://regels.overheid.nl/concepts/leeftijd_requirement"
    }
  ]
}
```

---

### `GET /v1/dmns/semantic-equivalences`

Returns variable pairs from different DMNs that share a `skos:exactMatch` concept.

**Query parameters:** `endpoint` (required)

---

### `GET /v1/dmns/cycles`

Returns circular dependencies detected via semantic links (3-hop traversal).

**Query parameters:** `endpoint` (required)

---

## Chain discovery

### `GET /v1/chains`

Returns all discoverable chains — DMN pairs where an output variable of one model matches an input variable of another by exact identifier.

**Query parameters:** `endpoint` (required)

---

## Chain execution

### `POST /v1/chains/execute`

Execute a DMN chain sequentially.

**Request body:**

```json
{
  "chain": ["SVB_LeeftijdsInformatie", "SZW_BijstandsnormInformatie"],
  "inputs": {
    "geboortedatum": "1960-01-01"
  },
  "endpoint": "https://api.open-regels.triply.cc/...",
  "isDrd": false
}
```

Set `isDrd: true` and provide a single entry-point identifier in `chain` for DRD execution.

**Response:**

```json
{
  "success": true,
  "data": {
    "results": {
      "aanvragerIs181920": true,
      "bijstandsnorm": 1200.00
    },
    "steps": [
      {
        "dmn": "SVB_LeeftijdsInformatie",
        "inputs": { "geboortedatum": "1960-01-01" },
        "outputs": { "aanvragerIs181920": true },
        "duration": 145
      },
      {
        "dmn": "SZW_BijstandsnormInformatie",
        "inputs": { "aanvragerIs181920": true },
        "outputs": { "bijstandsnorm": 1200.00 },
        "duration": 98
      }
    ],
    "totalDuration": 243
  }
}
```

---

### `POST /v1/chains/execute/heusdenpas`

Convenience endpoint for the Heusdenpas chain — a fixed three-step chain (`SVB_LeeftijdsInformatie → SZW_BijstandsnormInformatie → RONL_HeusdenpasEindresultaat`) with known-good production test data. Target execution time: <1000ms.

**Request body:**

```json
{
  "inputs": {
    "geboortedatumAanvrager": "1980-01-23",
    "geboortedatumPartner": null,
    "dagVanAanvraag": "2025-12-24",
    "aanvragerAlleenstaand": true,
    "aanvragerHeeftKinderen": true,
    "aanvragerHeeftKind4Tm17": true,
    "aanvragerInwonerHeusden": true,
    "maandelijksBrutoInkomenAanvrager": 1500,
    "aanvragerUitkeringBaanbrekers": false,
    "aanvragerVoedselbankpasDenBosch": false,
    "aanvragerKwijtscheldingGemeentelijkeBelastingen": false,
    "aanvragerSchuldhulptrajectKredietbankNederland": false,
    "aanvragerDitKalenderjaarAlAangevraagd": false,
    "aanvragerAanmerkingStudieFinanciering": false
  },
  "options": {
    "includeIntermediateSteps": true
  }
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "success": true,
    "chainId": "SVB_LeeftijdsInformatie->SZW_BijstandsnormInformatie->RONL_HeusdenpasEindresultaat",
    "executionTime": 827,
    "finalOutputs": {
      "aanmerkingHeusdenPas": true,
      "aanmerkingKindPakket": true
    },
    "steps": [
      {
        "dmnId": "SVB_LeeftijdsInformatie",
        "dmnTitle": "SVB Leeftijdsinformatie Berekening",
        "inputs": {
          "geboortedatumAanvrager": "1980-01-23",
          "dagVanAanvraag": "2025-12-24"
        },
        "outputs": {
          "aanvragerLeeftijd": 45,
          "aanvragerIs18": true,
          "aanvragerIs65": false
        },
        "executionTime": 234
      },
      {
        "dmnId": "SZW_BijstandsnormInformatie",
        "dmnTitle": "SZW Bijstandsnorm Informatie",
        "inputs": {
          "aanvragerAlleenstaand": true,
          "aanvragerHeeftKinderen": true,
          "aanvragerIs18": true
        },
        "outputs": {
          "bijstandsNorm": 1234.56,
          "toepasselijkeNorm": "alleenstaandeOuder"
        },
        "executionTime": 178
      },
      {
        "dmnId": "RONL_HeusdenpasEindresultaat",
        "dmnTitle": "Heusden Pas Eindresultaat",
        "inputs": {
          "aanvragerHeeftKind4Tm17": true,
          "aanvragerInwonerHeusden": true,
          "maandelijksBrutoInkomenAanvrager": 1500,
          "bijstandsNorm": 1234.56,
          "aanvragerUitkeringBaanbrekers": false,
          "aanvragerVoedselbankpasDenBosch": false,
          "aanvragerKwijtscheldingGemeentelijkeBelastingen": false,
          "aanvragerSchuldhulptrajectKredietbankNederland": false,
          "aanvragerDitKalenderjaarAlAangevraagd": false,
          "aanvragerAanmerkingStudieFinanciering": false
        },
        "outputs": {
          "aanmerkingHeusdenPas": true,
          "aanmerkingKindPakket": true
        },
        "executionTime": 415
      }
    ]
  },
  "timestamp": "2026-01-13T19:44:15.401Z"
}
```

---

### `POST /v1/chains/export`

Assemble a DRD XML from a DRD-compatible chain and deploy it to Operaton. See [DRD Generation](../developer/drd-generation.md) for the full deployment flow.

**Request body:**

```json
{
  "chain": ["SVB_LeeftijdsInformatie", "SZW_BijstandsnormInformatie"],
  "name": "Social Benefits DRD",
  "endpoint": "https://api.open-regels.triply.cc/..."
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "deploymentId": "43c759d6-082b-11f1-a5e9-f68ed60940f5",
    "entryPointId": "dmn1_SZW_BijstandsnormInformatie",
    "xml": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>..."
  }
}
```

---

## TriplyDB proxy

### `POST /v1/triplydb/query`

Execute a SPARQL query against any TriplyDB endpoint, bypassing browser CORS restrictions. Used by the frontend Query Editor for dynamic endpoint support.

**Request body:**

```json
{
  "endpoint": "https://api.open-regels.triply.cc/datasets/stevengort/DMN-discovery/services/DMN-discovery/sparql",
  "query": "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 5"
}
```

**Response:** SPARQL results in `application/sparql-results+json` format, wrapped in the standard response envelope.

---

## Error responses

All error responses follow a standard envelope:

```json
{
  "success": false,
  "error": {
    "code": "EXECUTION_ERROR",
    "message": "Chain execution failed: DMN not found"
  },
  "timestamp": "2026-01-13T19:44:15.401Z"
}
```

**Error codes:**

| Code | Meaning |
|---|---|
| `INVALID_REQUEST` | Invalid or missing request parameters |
| `NOT_FOUND` | Resource not found |
| `QUERY_ERROR` | SPARQL query to TriplyDB failed |
| `EXECUTION_ERROR` | DMN execution via Operaton failed |
| `DISCOVERY_ERROR` | Chain discovery query failed |

---

## Legacy endpoints and deprecation

All `/api/*` endpoints are deprecated and will be removed in v2.0.0. They return identical responses to their `/v1/*` counterparts plus the following headers:

```http
HTTP/1.1 200 OK
API-Version: 0.4.0
Deprecation: true
Link: </v1/health>; rel="successor-version"
```

**Migration:** replace every `/api/` prefix with `/v1/` in API calls.

| Deprecated | Replacement |
|---|---|
| `GET /api/health` | `GET /v1/health` |
| `GET /api/dmns` | `GET /v1/dmns` |
| `GET /api/dmns/:identifier` | `GET /v1/dmns/:identifier` |
| `GET /api/chains` | `GET /v1/chains` |
| `POST /api/chains/execute` | `POST /v1/chains/execute` |
| `POST /api/chains/execute/heusdenpas` | `POST /v1/chains/execute/heusdenpas` |