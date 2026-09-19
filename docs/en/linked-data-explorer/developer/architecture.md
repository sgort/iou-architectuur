---
component: Linked Data Explorer
---

# Architecture

The Linked Data Explorer is a monorepo with three workspaces under `packages/`: a React frontend SPA, a Node.js/Express backend API, and `ropa-site`, the static public site for the register of processing activities. The frontend renders in the browser; the backend handles SPARQL queries, Operaton calls, and chain orchestration.

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

The frontend does not call TriplyDB or Operaton itself. Queries, deployments and chain execution all go through the backend, which handles authentication, CORS, caching, variable orchestration — and, since v2026.09.5, the [outbound guard](backend.md#outbound-guard) that checks every host a caller names. That includes the SPARQL Query Editor, which until v2026.09.5 fetched the chosen endpoint straight from the browser and fell back to the third-party `api.allorigins.win` proxy; both paths are gone. The one thing the browser still loads from TriplyDB directly is organisation logo images, which the frontend's Content-Security-Policy admits in `img-src`.

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
│   │   └── Deploy modal (one-click Operaton deployment)
│   └── BpmnProperties (right panel)
│       ├── DmnTemplateSelector (BusinessRuleTask)
│       └── FormTemplateSelector (UserTask / StartEvent)  ← new in v1.0.0
├── FormEditor view                                       ← new in v1.0.0
│   ├── FormList (left panel)
│   └── FormCanvas (@bpmn-io/form-js editor, centre)
└── Changelog / Help view
```

The `FormEditor` view and `BpmnModeler` view share the `FormService` localStorage layer — forms authored in `FormEditor` are immediately available to `FormTemplateSelector` in the BPMN properties panel with no explicit synchronisation step.

State is managed with React hooks at the component level. There is no global state library. The `templateService.ts` utility provides the only persistent state — localStorage CRUD for chain templates and BPMN processes.

---

## Backend architecture

The backend is a structured Express application following the Dutch Government API Design Rules (API-20, API-57).

```
src/
├── index.ts              entry point: middleware, route mounting, server startup
├── routes/               one file per route group, mounted under /v1 by routes/index.ts
│   ├── registry.ts       the route topology, described once (the root page reads it)
│   ├── health · openapi · dmn · chain · template · process · shacl · norms
│   ├── triplydb · vendor · dso · edocs · cache · cspReports
│   └── assets · assets.public · ropa · ropa.public
├── services/             one per external system or domain: sparql, operaton,
│                         orchestration, triplydb, dso, edocs, vendor, norms, template,
│                         dmn-validation, shacl-validation, assets, ropa, externalTaskWorker
├── db/                   pg pool, idempotent migrations, row mappers
├── openapi/              document.ts serves the built description; testing/ holds the
│                         helpers that validate route responses against it
├── middleware/
│   ├── cors.middleware.ts      allowlist, plus wildcard for the three public mounts
│   ├── error.middleware.ts     central RFC 9457 problem-details handler
│   └── version.middleware.ts   API-Version header
└── utils/
    ├── outboundUrl.ts    route-level checks on caller-supplied endpoints
    ├── outboundHttp.ts   the guarded axios client for caller-chosen hosts
    ├── problem.ts        builds problem-details responses
    ├── validation.ts     body validators for the asset and ROPA upserts
    ├── publicPaths.ts    the three mounts served to any origin
    ├── buildInfo.ts      reads deploy/build-info.json for /v1/health
    ├── config.ts         environment configuration
    └── logger.ts         Winston structured logging
```

The request and response shapes of every route are in the [API Specification](../reference/api-specification.md), built from `packages/backend/openapi/openapi.yaml`.

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
