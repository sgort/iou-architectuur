# Architecture

The Linked Data Explorer is a monorepo with two packages: a React frontend SPA and a Node.js/Express backend API. The frontend renders in the browser; the backend handles SPARQL queries, Operaton calls, and chain orchestration.

---

## System architecture

```
Browser
  └── Frontend (React + TypeScript, Azure Static Web Apps)
            │ HTTPS/REST
  └── Backend (Node.js + Express, Azure App Service)
            ├── SPARQL ──────► TriplyDB (knowledge graph)
            └── REST API ────► Operaton (DMN execution engine)
```

The frontend never calls TriplyDB or Operaton directly in production. All calls go through the backend, which handles authentication, CORS, caching, and variable orchestration. In local development, the frontend can also use a CORS proxy fallback for public SPARQL endpoints.

---

## Frontend architecture

The frontend is a single-page application with no routing library. Navigation state is managed as an enum (`ViewMode`) in the top-level `App.tsx`.

```
App.tsx
├── Sidebar navigation (ViewMode selector)
├── QueryEditor view
│   ├── SparqlEditor (query input)
│   ├── ResultsTable (tabular results)
│   └── GraphView (D3.js force-directed graph)
├── ChainBuilder view
│   ├── DmnList (available DMNs, left panel)
│   ├── ChainComposer (drag-drop zone, centre panel)
│   │   └── SemanticAnalysis tab
│   ├── ChainConfig (inputs + execution, right panel)
│   │   ├── InputForm
│   │   ├── ExecutionProgress
│   │   ├── ChainResults
│   │   └── ExportChain (JSON / BPMN 2.0)
│   └── ValidationPanel
├── BpmnModeler view
│   ├── ProcessList (left panel)
│   ├── BpmnCanvas (bpmn-js wrapper, centre)
│   └── BpmnProperties (right panel)
│       └── DmnTemplateSelector
└── Changelog / Help view
```

State is managed with React hooks at the component level. There is no global state library. The `templateService.ts` utility provides the only persistent state — localStorage CRUD for chain templates and BPMN processes.

---

## Backend architecture

The backend is a structured Express application following the Dutch Government API Design Rules (API-20, API-57).

```
src/
├── index.ts              entry point, server startup
├── routes/
│   ├── index.ts          registers all route groups
│   ├── dmn.routes.ts     GET /v1/dmns, /v1/dmns/chains, /v1/dmns/semantic-equivalences
│   ├── chain.routes.ts   POST /v1/chains/execute, POST /v1/chains/export
│   ├── triplydb.routes.ts POST /v1/triplydb/query
│   └── health.routes.ts  GET /v1/health
├── services/
│   ├── sparql.service.ts       SPARQL queries against TriplyDB
│   ├── operaton.service.ts     Operaton REST API calls
│   ├── orchestration.service.ts chain execution and variable mapping
│   └── triplydb.service.ts     direct TriplyDB proxy (dynamic endpoints)
├── middleware/
│   ├── cors.ts
│   └── errorHandler.ts
└── utils/
    ├── logger.ts         Winston structured logging
    └── config.ts         environment config with validation
```

Legacy `/api/*` routes exist with deprecation headers for backward compatibility. All new work uses `/v1/*`.

---

## Data flow — chain execution

```
1. Frontend POST /v1/chains/execute
   { chain: [dmnId1, dmnId2], inputs: {...}, endpoint: "..." }

2. orchestration.service.ts
   for each DMN in chain:
     a. sparql.service.ts → fetch DMN metadata from TriplyDB (cached 5 min)
     b. Flatten previous step outputs into current step inputs
     c. operaton.service.ts → POST /engine-rest/decision-definition/key/{id}/evaluate
     d. Collect and flatten results

3. Return combined results to frontend
```

---

## Caching

The backend caches DMN metadata per endpoint with a 5-minute TTL. The cache key is the endpoint URL. Switching endpoints in the frontend bypasses the cache and triggers a fresh SPARQL query.

---

## Environment variables

See [Deployment](deployment.md) for the full list. Key variables:

| Variable | Description |
|---|---|
| `TRIPLYDB_ENDPOINT` | Default SPARQL endpoint URL |
| `OPERATON_BASE_URL` | Operaton engine REST base URL |
| `CORS_ORIGIN` | Comma-separated list of allowed frontend origins |
| `NODE_ENV` | `development`, `acceptance`, or `production` |
| `PORT` | Backend listen port (default 3001 local, 8080 Azure) |
