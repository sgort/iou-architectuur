---
component: Linked Data Explorer
---

# Testing

The Linked Data Explorer is an npm-workspaces monorepo, and its two packages are
tested with different runners: the Express/TypeScript backend on **Jest**, the
Vite/React frontend on **Vitest**. Both were built from zero in v2026.07.0 —
before that the repository had no test files at all and `npm test` exited 1 with
*"No tests found"*.

!!! info "Figures on this page are measured, not estimated"
    Every count, command and coverage percentage below was produced by running
    the suites against **v2026.08.2** on **19 August 2026**. Rerun the commands
    in [Running the tests](#running-the-tests) to reproduce them.

**At a glance:** 110 test files · **1702 tests** · all passing · backend 98.56%
statements, frontend 74.73%.

| Package | Runner | Files | Tests | Statements | Branches | Functions | Lines |
|---|---|---:|---:|---:|---:|---:|---:|
| `packages/backend` | Jest + ts-jest | 50 | 1129 | 98.56% | 91.49% | 97.15% | 99.05% |
| `packages/frontend` | Vitest + RTL | 60 | 573 | 74.73% | 65.65% | 69.44% | 77.01% |

---

## Running the tests

Run from the repository root after `npm install`. The root scripts fan out over
both workspaces with `--workspaces --if-present`.

| Command | Scope | Files | Tests |
|---|---|---:|---:|
| `npm test` | Both packages | 110 | 1702 |
| `npm test -w packages/backend` | Backend only (Jest, with coverage) | 50 | 1129 |
| `npm test -w packages/frontend` | Frontend only (Vitest, with coverage) | 60 | 573 |

Both packages' `test` scripts include coverage by default, so a plain run always
produces a report. Watch modes are `test:watch` in either package; the backend
additionally has `test:coverage` as an explicit alias.

```bash
# Everything
npm test

# One package
npm test -w packages/backend
npm test -w packages/frontend

# Watch mode while working on the backend
npm run test:watch -w packages/backend
```

### Linting and formatting

| Command | Backend | Frontend |
|---|---|---|
| `npm run lint` | ✅ runs | ✅ runs |
| `npm run check-format` | ✅ runs | ✅ runs |

Both root commands fan out over both packages. The backend checks
`src/**/*.ts`; the frontend checks the whole package.

!!! note "`check-format` skipped the backend until 19 August 2026"
    The two packages used to name their Prettier check differently — the backend
    `format:check`, the frontend `check-format`. The root script runs
    `npm run check-format --workspaces --if-present`, so `--if-present` quietly
    skipped the backend rather than failing, and since `pre-push` runs exactly
    that script, **backend formatting was never gated on push**.

    The backend now defines `check-format` as its canonical name, with
    `format:check` retained as an alias so existing muscle memory and tooling
    references keep working. On a checkout from before this change, check the
    backend explicitly with `npm run format:check -w packages/backend`.

    `lint-staged` had the same blind spot at `pre-commit` — it was configured for
    `packages/frontend/**` only — and was extended to the backend at the same
    time. Neither change had formatting fallout: the backend already passed both
    its lint and its format check.

### Git hooks

| Hook | Runs | Scope |
|---|---|---|
| `pre-commit` | `npx lint-staged` | Staged files only — Prettier `--write` then ESLint `--fix`, per package with that package's own config |
| `pre-push` | `npm run lint`, then `npm run check-format` | Both packages in full |

`lint-staged` matches `packages/frontend/**/*.{js,jsx,ts,tsx,json,css,md}` and
`packages/backend/src/**/*.ts`. The backend glob mirrors exactly what its
`check-format` gates, so the pre-commit and pre-push scopes agree rather than one
rewriting files the other never checks.

!!! important "The hooks do not run the tests"
    Neither hook invokes a test script, and — see [CI](#ci-no-test-step-by-design)
    — neither does any CI workflow. Nothing anywhere blocks a push or a deploy
    that breaks the suite, so run `npm test` yourself before pushing.

---

## CI — no test step, by design

None of the six Azure workflows (`azure-backend-acc`, `azure-backend-production`,
`azure-frontend-acc`, `azure-frontend-production`, `azure-ropa-site-acc`,
`azure-ropa-site-prod`) runs a test step, blocking or non-blocking.

This was a deliberate decision taken in P7, when coverage was first measured:
109 backend tests at 13.82% statements against 557 frontend tests at 74.03%. The
reasoning was that the backend gap at that point was **breadth** — whole route
and service files never touched — rather than depth, and gating on a number that
low would be theatre. The same call the RONL Business API made at 83.39%.

The condition recorded for revisiting it was *"once backend breadth improves"*.
**That condition has since been met** — v2026.08.2 took the backend from 16.79%
to 98.06% statements — but the CI step has not yet been added. Wiring one in is
now a straightforward, and overdue, change.

---

## Backend suite (Jest)

`packages/backend`, `jest.config.js` with the `ts-jest` preset.
`collectCoverageFrom` spans all of `src/**/*.ts`, so untested files report as 0%
rather than being omitted from the report — a deliberate choice that keeps the
headline number honest.

| Area | Tests | Covers |
|---|---:|---|
| `src/services` | 620 | Every service: operaton, sparql, dso, norms, edocs, ropa, vendor, assets, template, triplydb, orchestration, shacl-validation, dmn-validation, externalTaskWorker |
| `src/routes` | 389 | Every route module plus `routes/index` and `routes/registry`, each mounted in isolation (a fresh `express()` app per file, not the full `index.ts`) with the service layer mocked and supertest driving requests |
| `src/utils` | 85 | `etag`, `errors`, `logger`, `rootViews`, `config` |
| `src/db` | 22 | `pool`, `migrate` |
| `src/middleware` | 9 | `error.middleware`, `version.middleware` |

Techniques worth knowing before adding tests here:

- **Module-level singletons** (`db/pool`, `utils/logger`, `utils/config`) are
  re-imported per test case via `jest.isolateModules` with a patched
  environment, since their behaviour is fixed at import time.
- **"Pool is null" branches** — the database-not-configured path for the ropa and
  assets services — live in their own `*.no-pool.test.ts` files with a single
  static mock. `jest.doMock` inside `isolateModulesAsync` did not reliably
  override a file's top-level `jest.mock('../db/pool')`.
- **ESM-only dependencies** (`@rdfjs/dataset`, `rdf-validate-shacl`) are stubbed,
  so the SHACL suite exercises layer loading and issue mapping rather than the
  RDF libraries themselves.
- A few defensive outermost `catch` blocks are left deliberately uncovered —
  `health.routes.ts` sits at 89.74% for this reason.

---

## Frontend suite (Vitest)

`packages/frontend`. `vite.config.ts`'s `defineConfig` comes from
`vitest/config`; `test.environment` defaults to `node` with a per-file
`// @vitest-environment jsdom` opt-in, so the many pure-logic tests never pay for
a DOM. Uses `@testing-library/react`, `jest-dom`, `user-event`, `jsdom` and
`msw`.

| Area | Tests | Notes |
|---|---:|---|
| `src/services` | 116 | All 11 service modules — `msw` for the network-calling ones, jsdom `localStorage` for the two storage modules, raw `fetch` mocking for `sparqlService`'s CORS-proxy fallback |
| `components/ChainBuilder` | 102 | First `@dnd-kit`-coupled area. The hooks render fine with no `DndContext` wrapper — dnd-kit's context hooks fall back to sane defaults |
| `components/BpmnModeler` | 84 | `bpmn-js` and the properties panel mocked outright via a small fake modeler class built in a `vi.hoisted` block |
| `components/DocumentComposer` | 76 | The heaviest area, coupling `@tiptap/react` and `@dnd-kit`. Real ProseMirror runs under jsdom once `Range.getClientRects`/`getBoundingClientRect` and `document.elementFromPoint` are polyfilled |
| `components/FormEditor` | 38 | `@bpmn-io/form-js` mocked — exercising the real library would mean mounting a full canvas editor |
| `src/utils` | 37 | Pure logic: `exportFormats`, `exampleVersions`, `testData`, `logoResolver` |
| `components/RopaEditor` | 33 | Record fields, legal-basis SPARQL lookup, hydrate-from-linked-forms, the BPMN `ronl:ropaRef` tab, confirm-gated status transitions |
| `src/` (App, Changelog) | 26 | `App.tsx` renders 12 feature components as inspectable stubs, isolating the orchestrator's own state machine |
| `components/common` | 26 | Toolbar, language and organisation selectors |
| `components/DsoExplorer` | 21 | The largest single component file; `dsoService` mocked via `vi.mock` + `vi.importActual` so the pure URL/URN helpers stay real |
| `components/Tutorial` | 9 | Fixture-mocked `tutorial.json` |

The component strategy throughout is **critical interactions, not exhaustive
branch coverage**: orchestrators mock their already-tested children as clickable
stubs and assert on their own state machine.

### Deliberately not covered

Documented rather than silently skipped:

- **`exportService.ts`** (0%) — only 2 of its 6 functions are exported; the rest
  are reachable only through real DOM manipulation and JSZip archive building.
- **`bpmnTemplates.ts`** (0%) — confirmed to be pure static XML template data.
- **The actual `@dnd-kit` pointer-drag gesture** — `handleDragEnd`'s logic is
  exercised directly instead, by constructing `DragEndEvent` objects.

`DsoExplorer.tsx` is the largest genuine gap at 72% statements.

---

## Defects the tests found

Four real problems surfaced from writing tests rather than from use.

**`tsconfig.eslint.json` excluded every test file from linting.** It extended
`tsconfig.json` without overriding its `exclude` of `**/*.test.ts`, so ESLint's
type-aware parser could not see a single test file. Latent only because the
repository had no test files until P0.

**`.gitignore`'s blanket `*.js` rule blocked `jest.config.js`.** The rule existed
for compiled TypeScript output, but silently prevented the hand-authored Jest
config from ever being tracked.

**Ten CPRMV validation rules were dead code.** The backend coverage campaign in
v2026.08.2 documented — as a testing-scope decision, then fixed two commits later
— that `cprmvAttr()` called libxmljs2's attribute *setter* rather than a
namespaced getter, threw, and had its throw swallowed by its own `catch`.
`EXEC-002`–`EXEC-010` and `CON-001`–`CON-003` had therefore never fired for any
DMN while the validator reported clean results. See
[DMN Validation Reference](../reference/dmn-validation-reference.md).

**`assetService.ts` had a cross-test-polluting module-level cache**, found in P5
and fixed by giving each test a distinct dataset name.

---

## Documented quirks

Surfaced while testing, documented rather than patched, because each is
pre-existing and unrelated to the test that found it:

- **The error overlay is unreachable from the Orchestration view.** It lives
  inside `App`'s right panel, which is itself hidden whenever `viewMode` is
  Orchestration — so a failed cache refresh, triggerable only from that view,
  sets the error state correctly but has nowhere to render until the user
  navigates elsewhere.
- **The deploy modal's process-key extraction never matches under jsdom.**
  `doc.querySelector('process')` does not match a namespace-prefixed
  `<bpmn:process>` element in jsdom's XML parser, so the component's own
  fallback to the literal string `"process"` always wins for XML shaped like
  real `bpmn-js` output.

---

## Adding tests

- **Colocate** — `foo.ts` → `foo.test.ts`, beside the source.
- **Backend**: mock the service layer and mount routes in isolation rather than
  booting `index.ts`. Reach for `jest.isolateModules` when a module captures
  state at import time.
- **Frontend**: default to the `node` environment and opt into jsdom per file
  with `// @vitest-environment jsdom`. Use `msw` for network-calling services;
  mock heavyweight editor libraries outright, but prefer the real library when
  it works under jsdom with a small polyfill, as ProseMirror does.
- **Scope components to critical interactions.** Mock already-tested children as
  stubs and test the orchestrator's own state machine.
- **Document what you skip.** Every deliberate omission above is written down
  with its reason; silent gaps are what this suite was built to remove.
- **Update the figures on this page** when a phase lands, from a real run rather
  than an estimate.

---

## Roadmap

**Wire the CI test step.** The P7 deferral was conditional on backend breadth
improving, and it has. This is the outstanding item.

**Close the remaining frontend gaps** — `DsoExplorer.tsx` at 72%, and a decision
on whether `exportService.ts` is worth the DOM/JSZip harness it would need.

**Deliberately out of scope for now:** visual regression, a cross-browser matrix,
and E2E in this repository. Note the E2E fixtures that live here under
`e2e-fixtures/` are consumed by the **RONL Business API's** E2E suite, not run by
this one — this repository is their source of truth, with a manifest and an
integrity test, but not their runner.
