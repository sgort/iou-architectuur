---
component: Linked Data Explorer
---

# Frontend Architecture

The frontend is a React 19 TypeScript SPA built with Vite. It has no routing library — navigation is a local state enum. It has no global state management library — state lives in component hooks, with `localStorage` as the only persistence layer.

---

## Project structure

```
packages/frontend/src/
├── components/
│   ├── ChainBuilder/
│   │   ├── ChainBuilder.tsx       main orchestration component
│   │   ├── ChainComposer.tsx      drag-drop chain builder (dnd-kit)
│   │   ├── ChainConfig.tsx        configuration + execution panel
│   │   ├── ChainResults.tsx       execution results display
│   │   ├── DmnCard.tsx            individual DMN card
│   │   ├── DmnList.tsx            available DMNs panel
│   │   ├── ExecutionProgress.tsx  step-by-step progress indicator
│   │   ├── InputForm.tsx          dynamic input form generation
│   │   ├── ExportChain.tsx        export modal (JSON / BPMN 2.0)
│   │   ├── SemanticView.tsx       semantic analysis tab
│   │   ├── ValidationBadge.tsx    governance status badge
│   │   └── ValidationPanel.tsx    chain validation status display
│   ├── BpmnModeler/
│   │   ├── BpmnModeler.tsx        main orchestrator
│   │   ├── BpmnCanvas.tsx         bpmn-js canvas wrapper
│   │   ├── BpmnProperties.tsx     properties panel
│   │   ├── ProcessList.tsx        process management sidebar
│   │   └── DmnTemplateSelector.tsx DMN/DRD dropdown for BusinessRuleTask
│   ├── GraphView.tsx              D3.js RDF graph visualisation
│   ├── ResultsTable.tsx           SPARQL results table + CSV export
│   └── Changelog.tsx              version history display
├── services/
│   ├── sparqlService.ts           SPARQL query execution + result parsing
│   └── templateService.ts         localStorage CRUD for templates + processes
├── utils/
│   ├── exportService.ts           JSON + BPMN 2.0 export logic
│   ├── exportFormats.ts           export format definitions
│   ├── bpmnTemplates.ts           default BPMN XML templates
│   ├── ronlAttributes.ts          ronl:* process attributes — escaped on write, decoded on read
│   └── constants.ts               sample queries, preset endpoints
├── types/
│   ├── index.ts                   core TypeScript interfaces
│   ├── chainBuilder.types.ts      chain builder specific types
│   └── export.types.ts            export types
└── changelog.json                 version history data (JSON)
```

`tutorial.json` sat beside `changelog.json` until v2026.09.2, which removed the
in-app tutorial and its 596 lines of content along with the `Tutorial` component
and `ViewMode.TUTORIAL`.

---

## Key TypeScript interfaces

**DMN model:**

```typescript
interface DmnModel {
  id: string;
  identifier: string;
  title: string;
  description?: string;
  inputs: DmnVariable[];
  outputs: DmnVariable[];
  organisation?: string;
  // Governance metadata
  validationStatus?: 'validated' | 'in-review' | 'not-validated';
  validatedByName?: string;
  validatedAt?: string;
  validationNote?: string;
  // Vendor metadata
  vendorCount?: number;
  vendors?: VendorService[];
}

interface DmnVariable {
  id: string;
  identifier: string;
  title: string;
  type: 'Integer' | 'String' | 'Boolean' | 'Date' | 'Double';
}
```

**Chain template (localStorage schema):**

```typescript
interface ChainTemplate {
  id: string;
  name: string;
  description?: string;
  endpoint: string;
  chain: string[];         // ordered DMN identifiers
  testData?: Record<string, unknown>;
  type: 'sequential' | 'drd';
  // DRD-specific
  isDrd?: boolean;
  drdDeploymentId?: string;
  drdEntryPointId?: string;
  drdOriginalChain?: string[];
}
```

---

## Drag-and-drop (dnd-kit)

The Chain Composer uses `@dnd-kit/core` for drag detection and `@dnd-kit/sortable` for reordering within the composer. DMN cards in the Available DMNs list are `Draggable`; the Chain Composer area is a `Droppable`. Cards already in the composer use `SortableContext` for reordering.

---

## SPARQL service

`sparqlService.ts` sends **every** query through the backend, `POST /v1/triplydb/query`, whatever endpoint the user chose. Until v2026.09.5 it fetched the typed endpoint straight from the browser and fell back to the third-party `api.allorigins.win` proxy when CORS refused; both paths are gone, so no query passes through a third party, the backend's [outbound guard](backend.md#outbound-guard) applies to every one, and the Content-Security-Policy's `connect-src` can name a single origin. When the backend refuses an endpoint, its problem-details `detail` is shown to the user; a non-JSON error page, such as a proxy's HTML 502, shows as `Query failed (502).` rather than a JSON parse error. Result parsing handles both standard `application/sparql-results+json` and variations in binding formats.

The connection badge always reads *Proxied via Backend*. The **Local Jena** endpoint preset is offered only in development builds, the only place the backend admits local endpoints, and the default endpoint is chosen by URL rather than by list position, so it stays DMN Discovery in every build.

---

## Styling

Tailwind CSS 3.4 is **built with the application**, through PostCSS and autoprefixer, from an entry stylesheet imported in `main.tsx` and a content scan over `index.html` and the source. Until v2026.09.5, `index.html` loaded the Tailwind Play CDN on every page load in acceptance and production — third-party JavaScript executing in the application's origin, on an unversioned URL that cannot be pinned with an integrity hash. v3 was kept deliberately, so every class means exactly what the CDN served. An unused import map naming six packages on `esm.sh` was removed at the same time.

The inline `<style>` block that used to sit in `index.html` lives in `src/index.css`, so the Content-Security-Policy needs no `'unsafe-inline'` for `<style>` elements. The error banner's fade-down and the Settings panel's slide-in are two keyframes in `tailwind.config.js`, which `motion-reduce` turns off.

---

## Content-Security-Policy

`vite/cspPlugin.ts` writes `staticwebapp.config.json` into the build output during `build:acc` and `build:prod`, where Azure Static Web Apps reads it. The policy is served as `Content-Security-Policy-Report-Only`, built from the same `VITE_API_BASE_URL` the app uses, so each environment's `connect-src` names that environment's backend. Every allowed source is there because something in the built app needs it: Google Fonts for the Inter typeface, TriplyDB's assets API for organisation logos in `img-src`, and `data:` for the BPMN icon font and diagram images. Violations are reported to the backend's `POST /v1/csp-reports`. See [Deployment](deployment.md#staticwebappconfigjson-is-generated-not-committed) for how it is shipped.

---

## Template service (localStorage)

`templateService.ts` provides the localStorage interface for both chain templates and BPMN processes. All storage keys are prefixed with `linkeddata-explorer-`. Templates are namespaced by endpoint URL so switching endpoints does not surface templates from another dataset.

Key functions:

```typescript
getUserTemplates(endpoint: string): ChainTemplate[]
saveTemplate(endpoint: string, template: ChainTemplate): void
deleteTemplate(endpoint: string, templateId: string): void
getBpmnProcesses(): BpmnProcess[]
saveBpmnProcess(process: BpmnProcess): void
```

---

## Environment variables (Vite)

All environment variables are prefixed `VITE_` and read at build time:

| Variable | Default (development) | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:3001` | Backend API base URL |
| `VITE_CPSV_EDITOR_URL` | `http://localhost:3002` | The CPSV Editor the DSO → DMN publish handoff deep-links to. Run it on a non-3000 port locally, since LDE's dev server also uses 3000 |

Build targets: `npm run build:prod` (production), `npm run build:acc` (acceptance), `npm run dev` (development). The deploy workflows use `build:acc` and `build:prod`; each mode reads its own `.env.<mode>` file.

!!! note "`VITE_OPERATON_BASE_URL` was removed in v2026.09.6"
    It named, display-only, the Operaton the BPMN deploy modal deploys to and the Cockpit
    link in exported instructions — while the backend's `OPERATON_BASE_URL` decided where a
    process actually landed. A build-time copy of a value the backend owns can drift from it,
    so the modal and the exported README now ask
    [`GET /v1/dmns/process/deploy-target`](backend.md#deploy-target-v2026096) instead, through
    `services/deployTargetService.ts`. The variable is gone from all three `.env` files.
