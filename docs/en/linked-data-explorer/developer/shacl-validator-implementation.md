# SHACL Validator Implementation

---

## Architecture overview

Validation is split across the same three layers as the DMN validator:

```
Browser (React)                 Backend (Node.js / Express)
─────────────────────           ──────────────────────────────────────────────
ShaclValidator.tsx              packages/backend/src/
  │  POST /v1/shacl/validate      ├── routes/shacl.routes.ts          (route handler)
  │  POST /v1/shacl/validate-merged
  │  { content, endpoint? }  ───► └── services/shacl-validation.service.ts
  │                                      (two-layer SHACL engine)
  ◄──────────────────────────────
  { success, data: ShaclValidationResult }
```

The frontend component is a pure React display layer. All validation logic lives in the backend service.

---

## Frontend — `ShaclValidator.tsx`

**Location:** `packages/frontend/src/components/ShaclValidator.tsx`

The component is a close clone of `DmnValidator.tsx` — `SeverityIcon`, `IssueRow`, `LayerSection`, and `EntryCard` are structurally identical. The differences are the accepted extension (`.ttl`), the file-local/merge-simulated toggle with its optional endpoint field, and a two-key `layers` result shape.

### State model

```typescript
interface ShaclEntry {
  id: string;
  name: string;
  size: number;
  content: string;       // raw Turtle read by FileReader
  isValidating: boolean;
  result: ValidationResult | null;
  error: string | null;
}

type ValidationMode = 'file' | 'merged';
```

`ValidationResult.layers` is typed with three keys (the `cprmv` layer was added in v1.9.5):

```typescript
layers: {
  'cpsv-ap': LayerResult;
  'cprmv': LayerResult;
  'ronl-custom': LayerResult;
};
```

Layer rows are rendered with `Object.values(result.layers)`, so the component never hard-codes the keys — adding or renaming a layer on the backend does not require a frontend change.

### Key behaviours

**Persistence across navigation.** The component is rendered unconditionally in `App.tsx` and hidden with the Tailwind `hidden` class when `viewMode !== ViewMode.SHACL`, exactly as `DmnValidator` is hidden outside `ViewMode.VALIDATE`. This keeps React from unmounting it and discarding loaded files.

**Mode toggle.** A `file` / `merged` toggle selects the endpoint. In `merged` mode an optional endpoint input is shown; its value (or, if blank, the configured default) is sent alongside the content.

**Not-loaded vs OK.** `LayerSection` renders three states from `LayerResult.loaded` and `LayerResult.issues`: `loaded:false` → a dashed-circle "Not loaded" pill; `loaded:true` with no issues → green check + OK; `loaded:true` with issues → severity badge and counts.

### Component tree

```
ShaclValidator
├── Header (title, mode toggle, "Clear all")
├── Drop zone (always mounted, compact when entries exist)
├── Endpoint field (merge-simulated mode only)
└── Entry cards (horizontal scrollable row)
    └── EntryCard (one per ShaclEntry)
        ├── Card header (filename, size, Validate, ×)
        └── Card body
            ├── Validation spinner / error / placeholder
            └── Result
                ├── Summary badge (valid/invalid + E/W/I counts)
                └── LayerSection × 3  (cpsv-ap, cprmv, ronl-custom)
                    └── IssueRow × n
```

---

## Backend — route handler

**Location:** `packages/backend/src/routes/shacl.routes.ts`

```typescript
router.post('/validate', async (req: Request, res: Response) => {
  const { content } = req.body as { content?: string };
  if (!content || typeof content !== 'string') {
    return res.status(400).json({
      success: false,
      error: { code: 'INVALID_REQUEST', message: '...' },
    });
  }
  const data = await shaclValidationService.validateFile(content);
  res.json({ success: true, data, timestamp: new Date().toISOString() });
});

router.post('/validate-merged', async (req: Request, res: Response) => {
  const { content, endpoint } = req.body as { content?: string; endpoint?: string };
  // ...same guard, then:
  const data = await shaclValidationService.validateMerged(content, endpoint);
  res.json({ success: true, data, timestamp: new Date().toISOString() });
});
```

The routes are registered under `/v1/shacl`, so the full paths are `POST /v1/shacl/validate` and `POST /v1/shacl/validate-merged`. Both are unauthenticated; body size is limited by the `express.json()` middleware in `index.ts`.

---

## Backend — validation service

**Location:** `packages/backend/src/services/shacl-validation.service.ts`

### Dependencies

| Package | Role |
|---|---|
| `rdf-validate-shacl` | The SHACL engine. Default export is the `SHACLValidator` class; it ships its own RDF/JS factory, so no external factory is passed. `validate()` is async. |
| `n3` | Turtle parsing — `new Parser().parse(ttl)` returns a quad array. |
| `@rdfjs/dataset` | Wraps quads into a real `Dataset` (with `.match`) — required for the data graph; shapes may stay a plain quad array. |

`@rdfjs/dataset` and `rdf-validate-shacl` are ESM with no bundled types. A global ambient shim at `packages/backend/src/types/shacl-rdf.d.ts` declares the modules and minimal RDF/JS interfaces. It is loaded via a triple-slash reference at the top of the service (the project's `tsconfig` `include` does not glob it):

```typescript
// eslint-disable-next-line @typescript-eslint/triple-slash-reference
/// <reference path="../types/shacl-rdf.d.ts" />
```

!!! note
    The runtime requires Node ≥ 20.19 / 22, because the emitted CommonJS uses `require()` on these ESM packages. Azure App Service runs Node 22, so this is satisfied in all environments.

### Shape layers

Shapes are read once and cached for the life of the process (a deploy restarts it). Layers are declared as:

```typescript
const LAYER_SPECS: LayerSpec[] = [
  { key: 'cpsv-ap',     label: 'CPSV-AP 3.2.0', files: ['cpsv-ap/3.2.0/cpsv-ap-SHACL.ttl'] },
  { key: 'cprmv',       label: 'CPRMV 0.4.1',   files: ['cprmv/0.4.1/cprmv.shacl.ttl'] }, // v1.9.5
  { key: 'ronl-custom', label: 'RONL Custom',   dir: 'ronl' },
];
```

`SHAPES_ROOT` resolves to `packages/backend/shapes`. The CPSV-AP layer loads the single combined SHACL file vendored from SEMIC; the RONL layer loads every `*.ttl` under `shapes/ronl/`. A layer whose files are absent loads as `{ loaded: false }` rather than failing.

!!! note
    The `shapes/` directory is not part of the TypeScript build output. The deploy workflow copies it into the deployment package (`cp -r shapes deploy/`); without that step the shapes are missing at runtime.

### Severity mapping

Each SHACL result's `sh:resultSeverity` maps to the issue severity, and the code is derived from the local name of `sh:sourceConstraintComponent`:

| SHACL severity | Issue severity |
|---|---|
| `sh:Violation` | `error` |
| `sh:Warning` | `warning` |
| `sh:Info` | `info` |

`MaxCountConstraintComponent` → `SHACL-MAXCOUNT`, `UniqueLangConstraintComponent` → `SHACL-UNIQUELANG`, and so on. Offending values are whitespace-normalised and capped at 60 characters.

### Merge mode

`validateMerged(content, endpoint?)` parses the file, extracts its distinct subjects, builds a SPARQL `CONSTRUCT` scoped to those subjects, fetches the published graph as Turtle, unions it with the file, and runs the same three layers. The fetch is injectable:

```typescript
type GraphFetcher = (endpoint: string, query: string) => Promise<string>;

constructor(private readonly fetchGraph: GraphFetcher = constructGraph) {}
```

The default (`constructGraph` from `triplydb.service.ts`) issues a real `CONSTRUCT` and returns `text/turtle`. Tests inject a fixed published graph instead, making merge-mode deterministic without a live endpoint.

---

## Adding a new shape

1. Add or edit a `*.ttl` file under `packages/backend/shapes/ronl/` (RONL invariants) — the directory is globbed, so a new file is picked up on restart.
2. Target the relevant class with `sh:targetClass` and add property shapes (`sh:path`, `sh:minCount`/`sh:maxCount`/`sh:uniqueLang`/…).
3. Document the shape and the codes it produces in the [SHACL Validation Reference](../reference/shacl-validation-reference.md).
4. Add or extend a smoke script under `packages/backend/scripts/`, asserting on the `ronl-custom` layer so the test is independent of whether CPSV-AP is vendored.

Prefer `sh:uniqueLang true` over `sh:maxCount 1` for human-readable labels (`dct:title`, `dct:description`, `skos:prefLabel`) so bilingual `nl`/`en` records are tolerated while same-language collisions are still caught.

---

## Environment variables

| Variable | Component | Default |
|---|---|---|
| `VITE_API_BASE_URL` | Linked Data Explorer frontend | `http://localhost:3001` |
| `TRIPLYDB_ENDPOINT` | Backend (merge-simulated default endpoint) | — |
