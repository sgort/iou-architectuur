# API Reference

Base URL — production: `https://backend.linkeddata.open-regels.nl`
Base URL — acceptance: `https://acc.backend.linkeddata.open-regels.nl`

All endpoints are under `/v1/`. Every response includes an `API-Version` header. Legacy `/api/*` endpoints exist with `Deprecation` headers.

---

## Health

### `GET /v1/health`

Returns service health and dependency status.

**Response:**

```json
{
  "name": "Linked Data Explorer Backend",
  "version": "0.4.0",
  "environment": "production",
  "status": "healthy",
  "uptime": 3600.5,
  "services": {
    "triplydb": { "status": "up", "latency": 145 },
    "operaton": { "status": "up", "latency": 98 }
  }
}
```

`status` is `"healthy"` when all dependencies are up, `"degraded"` when one or more are down.

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
        "vendors": [ ... ]
      }
    ],
    "endpoint": "https://api.open-regels.triply.cc/...",
    "cached": false
  }
}
```

Response is cached per endpoint for 5 minutes. `cached: true` in subsequent responses.

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

### `POST /v1/chains/export`

Assemble a DRD XML from a chain and deploy it to Operaton.

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
    "xml": "<?xml version=\"1.0\" ...>..."
  }
}
```

---

## TriplyDB proxy

### `POST /v1/triplydb/query`

Execute a SPARQL query against any TriplyDB endpoint, bypassing browser CORS restrictions.

**Request body:**

```json
{
  "endpoint": "https://api.open-regels.triply.cc/datasets/stevengort/DMN-discovery/services/DMN-discovery/sparql",
  "query": "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 5"
}
```

**Response:** SPARQL results in `application/sparql-results+json` format, wrapped in the standard response envelope.
