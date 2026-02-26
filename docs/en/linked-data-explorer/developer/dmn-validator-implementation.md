# DMN Validator Implementation

---

## Architecture overview

Validation is split across three layers:

```
Browser (React)                Backend (Node.js / Express)
─────────────────────          ──────────────────────────────────────────────
DmnValidator.tsx               packages/backend/src/
  │  POST /v1/dmns/validate      ├── routes/dmn.routes.ts       (route handler)
  │  { content: string }    ───► └── services/dmn-validation.service.ts
  │                                      (five-layer validation engine)
  ◄──────────────────────────────
  { success, data: ValidationResult }
```

The frontend component is a pure React display layer. All business logic lives in the backend service.

---

## Frontend — `DmnValidator.tsx`

**Location:** `packages/frontend/src/components/DmnValidator.tsx`

### State model

```typescript
interface DmnEntry {
  id: string;           // generated: Date.now()-random
  name: string;
  size: number;
  content: string;      // raw XML string read by FileReader
  isValidating: boolean;
  result: ValidationResult | null;
  error: string | null;
}
```

`useState<DmnEntry[]>([])` holds all loaded files. Each entry is updated immutably by id when its validation completes.

### Key behaviours

**Persistence across navigation.** The component is rendered unconditionally in `App.tsx` and hidden with the Tailwind `hidden` class when not active:

```tsx
<div className={`flex-1 overflow-hidden flex flex-col ${
  viewMode === ViewMode.VALIDATE ? '' : 'hidden'
}`}>
  <DmnValidator apiBaseUrl={API_BASE_URL} />
</div>
```

This keeps React from unmounting the component — and therefore from discarding state — when the user switches views.

**Multi-file drop.** The `addFiles(files)` helper iterates `FileList | File[]`, rejects non-`.dmn`/`.xml` files with a toast, and for each accepted file spawns a `FileReader` that appends a new `DmnEntry` to state on `onload`.

**Concurrent validation.** `validateAll()` calls `validateEntry(id)` for every entry that is not already validating. Each call is an independent `fetch` — they run in parallel.

**Non-blocking errors.** A fetch or parse failure sets `entry.error` and clears `entry.isValidating`. It never throws or blocks other entries.

### Component tree

```
DmnValidator
├── Header (title, "Validate all", "Clear all")
├── Drop zone (always mounted, compact when entries exist)
├── Drop error toast (auto-dismisses after 4 s)
└── Entry cards (horizontal scrollable row)
    └── EntryCard (one per DmnEntry)
        ├── Card header (filename, size, Validate, ×)
        └── Card body
            ├── "Press Validate to run checks" placeholder
            ├── Validation spinner
            ├── Error message
            └── Result
                ├── Summary badge (valid/invalid + E/W/I counts)
                └── LayerSection × 5
                    └── IssueRow × n
```

---

## Backend — route handler

**Location:** `packages/backend/src/routes/dmn.routes.ts`

```typescript
router.post('/validate', async (req: Request, res: Response) => {
  const { content } = req.body as { content?: string };

  if (!content || typeof content !== 'string') {
    return res.status(400).json({
      success: false,
      error: { code: 'INVALID_REQUEST', message: '...' },
    });
  }

  const result = await dmnValidationService.validateDmnContent(content);

  res.json({ success: true, data: result, timestamp: new Date().toISOString() });
});
```

The endpoint is unauthenticated. Body size is limited to 10 MB by the `express.json()` middleware in `index.ts`. The route is registered under `/v1/dmns`, so the full path is `POST /v1/dmns/validate`.

---

## Backend — validation service

**Location:** `packages/backend/src/services/dmn-validation.service.ts`

### Dependency

`libxmljs2` is the only added dependency. It provides:

- XML well-formedness parsing (`parseXml`)
- A full DOM-like API with XPath support (`find()`, `get()`, `.attr()`, `.namespace()`)
- Namespace-aware attribute lookup

No XSD validation is used. The library's XSD compiler rejects complex forward-referencing schemas; all structural checks are performed programmatically instead.

### Entry point

```typescript
export async function validateDmnContent(xmlContent: string): Promise<DmnValidationResult> {
  const { layer: baseLayer, doc } = await validateBaseLayer(xmlContent);

  // If XML could not be parsed, abort — layers 2–5 require a valid DOM
  const parseFailure = baseLayer.issues.find(i => i.code === 'BASE-PARSE');
  if (parseFailure) return buildResult(parseFailure.message, baseLayer);

  if (!doc) return buildResult(null, baseLayer);

  return buildResult(
    null,
    baseLayer,
    validateBusinessLayer(doc),
    validateExecutionLayer(doc, xmlContent),
    validateInteractionLayer(doc),
    validateContentLayer(doc),
  );
}
```

### Namespace constants

```typescript
const DMN_NS   = 'https://www.omg.org/spec/DMN/20191111/MODEL/';
const CPRMV_NS = 'https://cprmv.open-regels.nl/0.3.0/';
const NS       = { d: DMN_NS };
```

All XPath queries use the `d:` prefix mapped to `DMN_NS`. The namespace-agnostic fallback `//*[local-name()="decision"]` is used in Layer 1 to handle any DMN version.

### Helper functions

```typescript
find(node, xpath, ns?)    // → XmlElement[]  — returns [] on error
get(node, xpath, ns?)     // → XmlElement | null
cprmvAttr(el, name)       // → string | null — tries namespace-aware then prefix scan
elLoc(el)                 // → '<tagName id="..." />' for issue location strings
iss(severity, code, msg, location?, line?, column?)  // → ValidationIssue
```

---

## Adding a new validation check

1. Identify the appropriate layer function (`validateBusinessLayer`, `validateExecutionLayer`, etc.).
2. Add an XPath query using `find()` or `get()` to locate the relevant elements.
3. Push a new issue using `iss('error'|'warning'|'info', 'LAYER-NNN', 'message', elLoc(el))`.
4. Document the new code in the [DMN Validation Reference](../reference/dmn-validation-reference.md).

Code numbering convention: `BASE-NNN`, `BIZ-NNN`, `EXEC-NNN`, `INT-NNN`, `CON-NNN`. Use the next available number in the relevant range.

---

## Environment variables

| Variable | Component | Default |
|---|---|---|
| `VITE_API_BASE_URL` | Linked Data Explorer frontend | `http://localhost:3001` |
| `REACT_APP_BACKEND_URL` | CPSV Editor frontend | `http://localhost:3001` |
