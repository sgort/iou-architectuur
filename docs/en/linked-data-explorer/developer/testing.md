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
    the suites against **v2026.09.4** on **11 September 2026**, at `be6bc54` on
    `main` — the promoted commit — in a clean export of that commit after
    `npm ci`, under Node 22 (CI pins Node 24; `npm ci` installs from the
    lockfile, so the tree is identical). Rerun the commands in
    [Running the tests](#running-the-tests) to reproduce them.

**At a glance:** 121 test files · **2242 tests** · all passing · backend 98.57%
statements, frontend 94.76%.

| Package | Runner | Files | Tests | Statements | Branches | Functions | Lines |
|---|---|---:|---:|---:|---:|---:|---:|
| `packages/backend` | Jest + ts-jest | 52 | 1151 | 98.57% | 92.96% | 97.17% | 99.05% |
| `packages/frontend` | Vitest + RTL | 69 | 1091 | 94.76% | 92.88% | 91.78% | 95.72% |

**The frontend nearly doubled, and then was given margin.** v2026.09.1 raised
per-file branch coverage above 80% across both packages: the frontend gained
**8 files and 447 tests**, taking branches from 65.67% to 90.62% and statements
from 74.72% to 94.30%. The backend moved far less because it had further to go —
six tests, and branches from 91.49% to 92.22%.

v2026.09.2 took the frontend from 1020 to **1073** tests. **31 of those came from
one commit** that added them to twelve existing files and no new file, taking
branches to **92.88%** and changing no production code — margin above the floor
rather than new behaviour. See
[The per-file branch floor](#the-per-file-branch-floor). The rest of the delta is
ordinary work in the same release, minus the nine tests deleted with the Tutorial
component.

**v2026.09.3 added a test file to each package**, both for defects the first
Semgrep triage found rather than for coverage. `publicPaths.test.ts` asserts that
wildcard CORS reaches the two public mounts and paths below them, and **never a
sibling that shares the prefix** — `/v1/ropa/publications`, `/v1/ropa/public-admin`
and `/v1/bundles/publicity` must all fall through to the allowlist.
`ronlAttributes.test.ts` pins the escaping of BPMN process metadata, including the
`$'` value that `String.replace` used to expand into the rest of the document.
Across v2026.09.3 and v2026.09.4 together, backend branches moved 92.22% →
**92.96%**; the frontend's held at 92.88%.

Two jsdom limitations had to be worked around to reach the d3 drag and zoom
paths, and they are the kind that make a branch look untestable when it is not:
jsdom rejects `view` in the `MouseEvent` constructor, and `SVGSVGElement`
carries no `width`/`height` `baseVal` for the default extent `d3-zoom`
computes.

!!! note "An invocation caveat that no longer reproduces"
    Through v2026.08.9 this page warned that backend branch coverage read 91.49%
    via `npm test -w packages/backend` but 92.22% when Jest was invoked directly
    from the repository root, with the same config and the same tests. The
    measurement above used the **workspace** invocation and read 92.22%, so the
    discrepancy is not reproducible as described. Whether v2026.09.1 closed it or
    the original diagnosis was wrong is not established here — only that the two
    invocations no longer disagree in the way the warning claimed. The root
    invocation was not separately re-run.

---

## Running the tests

Run from the repository root after `npm install`. The root scripts fan out over
both workspaces with `--workspaces --if-present`.

| Command | Scope | Files | Tests |
|---|---|---:|---:|
| `npm test` | Both packages | 121 | 2242 |
| `npm test -w packages/backend` | Backend only (Jest, with coverage) | 52 | 1151 |
| `npm test -w packages/frontend` | Frontend only (Vitest, with coverage) | 69 | 1091 |

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
    Neither hook invokes a test script, so nothing *client-side* stops a push
    that breaks the suite — run `npm test` yourself before pushing. What has
    changed is what happens next: since 20 August 2026 the deploy pipelines run
    the suites and a failure blocks the deploy, so a broken push no longer
    reaches acceptance. See [CI](#ci-the-test-gate).

---

## CI — the test gate

Four of the six Azure workflows run the suites, and a failure blocks the deploy:

| Workflow | Lint | **Tests** | Build | Deploy |
|---|:---:|:---:|:---:|:---:|
| `azure-backend-acc` / `-production` | ✅ | **✅** | ✅ | ✅ |
| `azure-frontend-acc` / `-production` | ✅ | **✅** | ✅ | ✅ |
| `azure-ropa-site-acc` / `-prod` | – | – | – | ✅ |

The two `ropa-site` workflows run nothing, correctly: `packages/ropa-site` is a
static `index.html` plus a `staticwebapp.config.json`, with no build and no test
script to run.

The backend workflows already installed and linted, so the test step slots in
beside the existing `npm run lint`. The frontend workflows had no npm steps at
all — the Static Web Apps action builds inside its own container and runs none of
the repository's scripts — so they gained an explicit install, lint and test
sequence ahead of the deploy action, installing from the workspace root since
that is where the only lockfile lives.

!!! note "Why this was deferred, and what changed"
    There was no test step anywhere until 20 August 2026. That was a deliberate
    P7 decision taken when coverage was first measured: 109 backend tests at
    13.82% statements against 557 frontend tests at 74.03%. The reasoning was
    that the backend gap was **breadth** — whole route and service files never
    touched — rather than depth, and gating on a number that low would be
    theatre. The same call the RONL Business API made at 83.39%.

    The condition recorded for revisiting it was *"once backend breadth
    improves"*. v2026.08.2 took the backend from 16.79% to 98.06% statements,
    which met it.

---

## Backend suite (Jest)

`packages/backend`, `jest.config.js` with the `ts-jest` preset.
`collectCoverageFrom` spans all of `src/**/*.ts`, so untested files report as 0%
rather than being omitted from the report — a deliberate choice that keeps the
headline number honest.

| Area | Tests | Covers |
|---|---:|---|
| `src/services` | 626 | Every service: operaton, sparql, dso, norms, edocs, ropa, vendor, assets, template, triplydb, orchestration, shacl-validation, dmn-validation, externalTaskWorker |
| `src/routes` | 389 | Every route module plus `routes/index` and `routes/registry`, each mounted in isolation (a fresh `express()` app per file, not the full `index.ts`) with the service layer mocked and supertest driving requests |
| `src/utils` | 96 | `etag`, `errors`, `logger`, `rootViews`, `config`, `publicPaths` |
| `src/db` | 22 | `pool`, `migrate` |
| `src/middleware` | 9 | `error.middleware`, `version.middleware` |
| `src/example-fixture-parity.test.ts` | 4 | Every file in a mirrored RIP bundle is byte-identical to its twin — `examples/organizations/flevoland/rip-phase-2x/` against `e2e-fixtures/flevoland/`. Bundles opt in through `MIRRORED_BUNDLES` |
| `src/e2e-fixtures.test.ts` | 5 | The `e2e-fixtures/` bundle consumed by the RONL Business API's E2E suite — manifest parses, every declared file exists, each BPMN's process id matches its `processDefinitionKey`, each shell's `calledElement` references resolve, and every process keeps its artifacts after its flow elements |

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
| `components/ChainBuilder` | 184 | First `@dnd-kit`-coupled area. The hooks render fine with no `DndContext` wrapper — dnd-kit's context hooks fall back to sane defaults |
| `components/DocumentComposer` | 167 | The heaviest area, coupling `@tiptap/react` and `@dnd-kit`. Real ProseMirror runs under jsdom once `Range.getClientRects`/`getBoundingClientRect` and `document.elementFromPoint` are polyfilled |
| `src/components` (top level) | 149 | `ShaclValidator` 37, `DmnValidator` 30, `ResultsTable` 26, `GraphView` 23, `OrganizationCard` 12, `Changelog` 11, `OrganizationsView` 10 |
| `src/services` | 142 | All 11 service modules — `msw` for the network-calling ones, jsdom `localStorage` for the two storage modules, raw `fetch` mocking for `sparqlService`'s CORS-proxy fallback |
| `components/BpmnModeler` | 134 | `bpmn-js` and the properties panel mocked outright via a small fake modeler class built in a `vi.hoisted` block |
| `src/utils` | 98 | Pure logic: `exportFormats`, `exampleVersions`, `testData`, `logoResolver`, `ronlAttributes` |
| `components/DsoExplorer` | 64 | The largest single component file; `dsoService` mocked via `vi.mock` + `vi.importActual` so the pure URL/URN helpers stay real |
| `components/FormEditor` | 58 | `@bpmn-io/form-js` mocked — exercising the real library would mean mounting a full canvas editor |
| `components/RopaEditor` | 43 | Record fields, legal-basis SPARQL lookup, hydrate-from-linked-forms, the BPMN `ronl:ropaRef` tab, confirm-gated status transitions |
| `src/App.test.tsx` | 26 | `App.tsx` renders 11 feature components as inspectable stubs, isolating the orchestrator's own state machine. Includes the regression test for the error overlay, which is asserted on the view that raises it |
| `components/common` | 26 | Toolbar, language and organisation selectors |

!!! note "These are the runner's own per-file counts, summed"
    Every row above was derived from Vitest's default reporter — the
    `(N tests)` it prints beside each file — grouped by directory. The rows
    therefore sum to exactly 1091. The backend table is the same, from Jest's
    `--json` report, and sums to 1151.

    **The previous revision of this table did not.** Its rows summed to 573
    against a stated total of 1020, because they had been gathered per area at
    different times rather than from one run, and the top-level
    `src/components` files were never a row at all. A per-area table that does
    not reconcile with the headline is worth less than no table, so this one is
    generated rather than maintained.

`components/Tutorial` was a row here until v2026.09.2, which
[removed the Tutorial view outright](changelog-roadmap.md) — the
component, its nine tests and the 596 lines of `tutorial.json` behind it.

The component strategy throughout is **critical interactions, not exhaustive
branch coverage**: orchestrators mock their already-tested children as clickable
stubs and assert on their own state machine.

### Deliberately not covered

Documented rather than silently skipped:

- **`bpmnTemplates.ts`** (0%) — confirmed to be pure static XML template data.
- **The actual `@dnd-kit` pointer-drag gesture** — `handleDragEnd`'s logic is
  exercised directly instead, by constructing `DragEndEvent` objects.
- **Three submit-guard branches**, each sitting behind a button that is already
  disabled on the same condition. Reaching them means driving the component into
  a state the interface does not offer.

Two entries left this list. **`exportService.ts` was 0%** — only 2 of its 6
functions are exported, the rest reachable only through real DOM manipulation and
JSZip archive building — and now reads 100% statements, 94.66% branches.
**`DsoExplorer.tsx` was the largest genuine gap at 72% statements** and now sits
at 92.55%.

---

## The per-file branch floor

Since v2026.09.2 both runners enforce **80% branch coverage per file**, natively:
`jest.config.js` takes a glob key it applies to each matching file individually,
`vite.config.ts` takes `thresholds: { branches: 80, perFile: true }`.

`perFile` is the mechanism, not a detail. Against a package *average* the
threshold is inert — the frontend sits at 92.88% and the backend at 92.22%, so a
single file dropping to 40% would barely move either. Branches specifically,
because statement and line coverage largely restate *"was this file imported"*,
while an uncovered branch is a decision no test has ever checked.

**Branches only.** A functions floor would fail today, and is not a companion
setting to add without measuring first.

### The margin, and why it needed widening

The floor landed measured-clean but with none to spare:
`ChainBuilder/TestCasePanel.tsx` sat at **exactly 80.00%**, with thirteen more
files between 80 and 85. The first uncovered branch added to any of them would
have turned CI red on an unrelated change — which is how a floor stops being read
as a floor and starts being read as an obstacle.

v2026.09.2 raised twelve files. Of the frontend files carrying at least one
branch — 69 of 78 at v2026.09.4 — **one is below 85%**: `GraphView.tsx` at 82.26%. Its eleven remaining
uncovered branches are all inside d3's force-simulation tick and drag handlers —
`d.x || 0` position fallbacks, `if (!event.active)` drag guards — which need a
running simulation and synthesised drag events to reach. That is a d3 harness,
not a test of this component. The config comment says so, so that whoever next
turns this red knows the answer is to test their new branch rather than lower the
floor.

### Every new test was mutation-checked

A test written against code that already exists **passes on its first run**,
which proves nothing about whether it can fail. Each of the 31 tests written for
the floor had the branch it targets deliberately broken and had to fail before it
was kept.

That caught **five tests asserting nothing**. Four share a shape worth knowing on
any React codebase: an assertion that *"nothing happened"* stays true when the
handler **throws** partway through, because React surfaces an error thrown inside
a click handler on `window`'s `error` event rather than rejecting the click. The
test sees no state change and passes — for the wrong reason. See
[Raising coverage without writing hollow tests](../../contributing/coverage-floor.md#raising-coverage-without-writing-hollow-tests).

---

## Defects the tests found

Six real problems surfaced from writing tests rather than from use. A seventh,
at the end, is the reverse case — one the suite was well placed to catch and
did not.

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

The last two were first written up as *documented quirks* — pre-existing,
unrelated to the test that found them, and left alone on purpose. Both were
fixed on 20 August 2026 once the CI gate made an unexplained red run expensive.

**The error overlay was unreachable from the Orchestration view.** It lived
inside `App`'s right panel, which is itself hidden whenever `viewMode` is
Orchestration — so a failed cache refresh, triggerable only from that view, set
the error state correctly and had nowhere to render until the user happened to
navigate elsewhere. Documented as a quirk when first found, fixed on 20 August
2026 by lifting the overlay to be a direct child of the workspace container, so
it renders in every view. `App.test.tsx` now asserts the error appears on the
view that caused it, and is dismissible there.

**The deploy modal's process key was always the literal string `"process"`.**
`doc.querySelector('process')` is a CSS *type* selector, which matches only the
null namespace and so never found the `<bpmn:process>` element that real
`bpmn-js` output always emits; `BpmnCanvas` fell through to its own fallback
every time. Sub-process lookups by `calledElement` failed the same way. Also
documented as a jsdom quirk when first found — the fixture behind that reading
declared none of the prefixes it used, so `DOMParser` rejected it outright and
returned a `<parsererror>` document in which nothing was findable under any
lookup, masking the real defect underneath. Fixed on 20 August 2026 with a
`findProcessElement` helper matching on local name across namespaces, and the
fixture made well-formed.

### The one the tests missed

**Four of the five E2E fixture BPMNs were undeployable for weeks.** BPMN 2.0's
`tProcess` is an ordered sequence — `laneSet*`, `flowElement*`, `artifact*`,
`resourceRole*`, `correlationSubscription*`, `supports*` — so once an artifact
appears, no further flow element may follow it. The commit that added the
on-canvas "E2E FIXTURE" warning inserted its `textAnnotation` and `association`
directly after the first flow element in each file, and Operaton's XSD
validation rejects the whole deployment on sight:

```
cvc-complex-type.2.4.a: Invalid content was found starting with element
'{http://www.omg.org/spec/BPMN/20100524/MODEL}scriptTask'. One of
'{…}artifact, {…}resourceRole, {…}correlationSubscription, {…}supports'
is expected.
```

`TreeFellingPermitSubProcessE2E` was the one file with its banner correctly at
the end of the process, and the only one that deployed.

This is worth recording precisely because the suite had every opportunity. The
manifest integrity test read each BPMN, checked that the file existed, that its
process id matched the declared `processDefinitionKey`, and that a shell's
`calledElement` references resolved to its nested sub-processes — but never that
the document would survive the validator it was written for. These fixtures are
hand-edited and never round-trip through bpmn-js, which would have re-serialised
them into schema order and silently repaired the mistake, so nothing else stood
between the edit and a failed deploy.

The fix was a pure move of each banner to just before `</bpmn:process>`; all five
now validate against `bpmn-moddle`'s `BPMN20.xsd`. The integrity test gained a
fifth case asserting the ordering rule directly, confirmed failing against the
broken fixtures before it was allowed to pass.

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

**Close the remaining frontend gaps.** Both items that stood here are done —
`DsoExplorer.tsx` went from 72% to 92.55% statements, and `exportService.ts` got
its DOM/JSZip harness and reads 100%. What is left is `GraphView.tsx` at 82.26%
branches, which is a deliberate hold rather than a gap: see
[The per-file branch floor](#the-per-file-branch-floor).

**Deliberately out of scope for now:** visual regression, a cross-browser matrix,
and E2E in this repository. Note the E2E fixtures that live here under
`e2e-fixtures/` are consumed by the **RONL Business API's** E2E suite, not run by
this one — this repository is their source of truth, with a manifest and an
integrity test, but not their runner.
