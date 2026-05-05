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
│   └── constants.ts               sample queries, preset endpoints
├── types/
│   ├── index.ts                   core TypeScript interfaces
│   ├── chainBuilder.types.ts      chain builder specific types
│   └── export.types.ts            export types
├── changelog.json                 version history data (JSON)
└── tutorial.json                  in-app tutorial content
```

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

`sparqlService.ts` handles query execution via the backend proxy endpoint (`/v1/triplydb/query`). For direct SPARQL endpoints in development, it includes a CORS fallback. Result parsing handles both standard `application/sparql-results+json` and variations in binding formats.

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
| `VITE_OPERATON_BASE_URL` | `https://operaton.open-regels.nl/engine-rest` | Operaton REST base URL |

Build targets: `npm run build` (production), `npm run build:acc` (acceptance), `npm run dev` (development).
