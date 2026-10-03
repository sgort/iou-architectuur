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
    The headline counts, package coverage, per-area tables, per-file coverage
    and command results below were produced by running the suites against
    **v2026.10.0** on **4 October 2026**, at `9e0d18e` on `acc` — the same tree
    as `71a8236` on `main`, so ACC and production both run what was measured.
    The runs used the working checkout, with `npm run deps:check` reporting the
    installed dependencies in step with the lockfile, on **Node 24.21.0**, the
    version `.nvmrc` pins.

    The two packages were not run the same way. The backend ran **serially**,
    `npx jest --coverage --runInBand`; the frontend ran with **Vitest's default
    file parallelism**, `npx vitest run --coverage`. Counts and coverage do not
    depend on that choice; the backend's runner time does, and is not comparable
    with the parallel figures earlier releases quoted. Rerun the commands in
    [Running the tests](#running-the-tests) to reproduce them.

**At a glance:** 146 test files · **3123 tests** · all passing · backend 98.36%
statements, frontend 95.38%.

| Package | Runner | Files | Tests | Runner time | Statements | Branches | Functions | Lines |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `packages/backend` | Jest + ts-jest | 70 | 1841 | 68.7 s (serial) | 98.36% | 91.98% | 97.48% | 99.06% |
| `packages/frontend` | Vitest + RTL | 76 | 1282 | 104.2 s | 95.38% | 92.89% | 93.26% | 96.41% |

`packages/ropa-site` has no `package.json` and is not an npm workspace member, so
`npm test` never reaches it. Two further test files live outside both packages
and outside the total above — see
[Script harnesses outside `npm test`](#script-harnesses-outside-npm-test).

**Against v2026.09.8 that is +2 files and +40 tests**, one file in each
package, and no backend source file changed.

- **Backend, +1 file and +17 tests:** `src/besluitvorming-gedelegeerd-bundle.test.ts`.
  The Besluitvorming bundle is hand-written BPMN, DMN, form and document files
  that refer to each other by id and variable name, and nothing else checks
  those references before a deploy fails on Operaton or a gateway finds no
  variable. Its 17 tests check that `GedelegeerdBesluitRoute` is a FIRST-hit
  decision reading exactly the five inputs the forms produce; that the twelve
  forms set every DMN input and every value the besluit document binds; that
  the process draws six lanes, declares six phases, calls the DMN untenanted,
  signs the besluit document and escalates a declined signature; and that it
  keeps the schema's element order. Backend coverage is identical to
  v2026.09.8 on all four metrics.
- **Frontend, +1 file and +23 tests:** the new `utils/documentRefs.test.ts`
  (7), for the comma-separated `ronl:documentRef` list, and growth in four
  existing files — `DocumentComposer/defaultTemplates.test.ts` +9 (now 47),
  `BpmnModeler/DocumentTemplateSelector.test.tsx` +4 (now 9),
  `utils/exampleVersions.test.ts` +2 (now 9) and `BpmnModeler/BpmnCanvas.test.tsx`
  +1 (now 60). Statements moved 95.37% → **95.38%**, branches 92.93% →
  **92.89%**, functions 93.18% → **93.26%**, lines 96.39% → **96.41%**.

The per-file deltas are the runner's counts against the previous ones; where a
file's previous count was never published, its delta is its area's, since the
diff from `4148c9a` to `71a8236` changes no other test file in that area.

**v2026.09.8 added no file and one test**, in the backend: the
`buildInfo.test.ts` case *"reports the build it loaded with, even after the file
changes underneath"*, which pins that `deploy/build-info.json` is read once, at
start-up, rather than on first request. The frontend count and all four of its
coverage figures were unchanged. Backend branches moved 92.49% → **91.98%**; the
only backend source files changed in that release were `utils/buildInfo.ts`,
`routes/openapi.routes.ts` and `services/quality.service.ts`, and which of them
moved the average was not measured per file.

**v2026.09.6 added 8 files and 261 tests** — backend +174, frontend +87. It was
a DSO release, and its tests follow the new services. Six modules arrived with
their own suites, and two of them landed clean (coverage as measured at
v2026.09.6):

| New module | Package | Tests | Statements | Branches | Functions | Lines |
|---|---|---:|---:|---:|---:|---:|
| `src/services/dossier.service.ts` | backend | 57 | 97.77% | 95.52% (134 br) | 100% | 98.71% |
| `src/services/quality.service.ts` | backend | 38 | 96.47% | 91.11% (45 br) | 95.45% | 100% |
| `src/services/ozon.service.ts` | backend | 13 | **100%** | **100%** (28 br) | **100%** | **100%** |
| `src/utils/ttl-cache.ts` | backend | 13 | **100%** | **100%** (11 br) | **100%** | **100%** |
| `components/DsoExplorer/QualityProfileTab.tsx` | frontend | 43 | 98.77% | 90.65% (246 br) | 98.76% | 99.55% |
| `src/services/deployTargetService.ts` | frontend | 5 | 100% | 91.66% (12 br) | 100% | 100% |

`ozon.service.ts` — the client for Omgevingsdocumenten Presenteren — is the
cleanest new module in the release at 100% on all four metrics, and `ttl-cache.ts`
matches it. Both are small and pure enough to test exhaustively, which is the
point: the branching that resists coverage lives in the components, not here.
The Ozon and dossier suites are backed by a **captured production annotation
payload**, `src/__fixtures__/annotaties-gm0995-prod.json`, rather than a
hand-written stub — so the parsing they assert is parsing that a real response
actually requires.

The two largest existing suites grew to meet them: `routes/dso.routes.test.ts` to
110 tests and `services/dso.service.test.ts` to 92, and on the frontend
`DsoExplorer.test.tsx` to 88 and `services/dsoService.test.ts` to 53. A new
`DsoExplorer/shared.tsx` extracted from the explorer reads 100% on all four.

Package branch averages barely moved — backend 92.41% → **92.49%**, frontend
93.26% → **92.93%** — which is the expected shape when a release adds heavily
branching code and covers it to roughly the existing standard. The average is
not what holds a release to account here; see
[The per-file branch floor](#the-per-file-branch-floor).

**v2026.09.5 added 579 tests, 498 of them in the backend**, almost all of them
new code under test rather than margin on old. The outbound guard alone brought
82 — `outboundUrl.test.ts` 62 and `outboundHttp.test.ts` 20. `src/openapi` is a
new area of 38 tests across four files, and the route suites grew by validating
every response against the published OpenAPI document. Problem details,
build provenance and the extracted CORS middleware each gained their own file.
Backend branches moved 92.96% → **92.41%**: the release added a great deal of
branching code, and the per-file floor, not the package average, is what holds
each file to account. The frontend added 81 tests and four files — among them
`vite/cspPlugin.test.ts` for the Content-Security-Policy generator and
`src/data/dsoAuthorities.test.ts` for the generated authority list — and moved
branches 92.88% → **93.26%**.

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

Run from the repository root after `npm ci`. The root scripts fan out over
both workspaces with `--workspaces --if-present`.

| Command | Scope | Files | Tests | Time |
|---|---|---:|---:|---:|
| `npm test` | Both packages | 146 | 3123 | — |
| `npm test -w packages/backend` | Backend only (Jest, with coverage) | 70 | 1841 | 68.7 s, measured serially with `--runInBand` |
| `npm test -w packages/frontend` | Frontend only (Vitest, with coverage) | 76 | 1282 | 104.2 s |
| `npm run test:contract -w packages/backend` | `src/openapi` and `src/routes`, without coverage | 27 | 762 | 35.2 s |
| `npm run test:scripts` | Both script harnesses in `scripts/` — **not** part of `npm test` | 2 | 24 + 24 checks | — |
| `node scripts/promotion-targets.test.mjs` | The promotion decision script alone | 1 | 24 checks | — |
| `node scripts/dso-dossier.test.mjs` | The dossier renderer alone | 1 | 24 checks | — |

Times are the runner's own figures from the 4 October 2026 measurement. The
backend row was measured with `npx jest --coverage --runInBand`, one file at a
time; `npm test` runs Jest with its default workers, so its time will differ.
`npm run test:scripts` passes on Windows as well as Linux:
both harnesses printed `PASS: 24 checks` on Windows in the same measurement.

Both packages' `test` scripts include coverage by default, so a plain run always
produces a report. Watch modes are `test:watch` in either package; the backend
additionally has `test:coverage` as an explicit alias.

```bash
# Everything
npm test

# One package
npm test -w packages/backend
npm test -w packages/frontend

# The contract subset — the fast loop while editing openapi.yaml or a route
npm run test:contract -w packages/backend

# Watch mode while working on the backend
npm run test:watch -w packages/backend

# The two script harnesses, which npm test does not run
npm run test:scripts

# The dossier renderer's harness alone
node scripts/dso-dossier.test.mjs

# Diagnostic only — see "When the frontend suite fails only in parallel"
cd packages/frontend && npx vitest run --no-file-parallelism --coverage
```

### The contract subset is a backend run, selected by path

`test:contract` is a **subset** of the backend run, not an addition to it, and
not a frontend concern:

```
jest --config jest.config.js src/openapi src/routes --coverage=false
```

**Selection is by path prefix.** Not a filename convention, not a tag, not a
`describe` name: every `*.test.ts` under `src/openapi` or `src/routes` is in the
subset, and everything else is out. That is the whole rule, and it is what you
need to know to add a test to it — put the file under one of those two
directories and it is included; put a contract assertion anywhere else and it
will never run in the fast loop.

At v2026.10.0 that is **27 files and 762 tests**, all passing: **724 tests from
`src/routes`** and **38 from `src/openapi`**, the same as at v2026.09.6, when it
ran in 30.0 seconds against 89.6 for the full backend suite. Jest reported
35.2 seconds for it on 4 October 2026. It is the loop to use while editing
`openapi.yaml` or a route.

**There is no frontend contract subset.** `packages/frontend` defines no
`test:contract` script and carries no test file with `contract` in its name; its
only test entry points are `test` and `test:watch`. If this page's contract
figure is ever quoted beside the frontend total, that is a misreading — the
number belongs to the backend row.

### Script harnesses outside `npm test`

Two test files live in `scripts/`, outside both workspaces, and `npm test` runs
neither. The root script `npm run test:scripts` runs both, in order:
`node scripts/promotion-targets.test.mjs && node scripts/dso-dossier.test.mjs`.

| Harness | Covers | Runs in CI | Checks |
|---|---|---|---:|
| `promotion-targets.test.mjs` | `scripts/promotion-targets.mjs`, which decides which production deploys a promotion needs — including a drift guard that the two production site workflows' `pull_request` paths agree with its patterns | **Yes** — `promote-to-production.yml` runs it in its `changes` job, before the script it tests makes the decision | 24 |
| `dso-dossier.test.mjs` | The DSO activity dossier renderer | **No** — no workflow and neither git hook invokes it | 24 |

So the promotion harness is a gate: a promotion whose decision script fails its
own test deploys nothing. The dossier harness still protects its renderer only
when someone runs it — by hand, or through `test:scripts`.

Neither is a runner. Both are hand-rolled ESM harnesses — not `node:test` — that
push `[name, boolean]` pairs onto a `checks` array, print `PASS: 24 checks`, and
call `process.exit(1)` naming any check that failed.

Both run on Windows since v2026.10.0. Until then the promotion harness located
its script with `new URL(...).pathname`, which on Windows yields `/C:/…`, a
path Node cannot run, so its command-line checks failed there — and because
`test:scripts` joins the two with `&&`, the dossier harness never ran. It now
uses `fileURLToPath`, and stops with a named failure if the resolved path does
not exist, so a regression reports its cause instead of four unexplained
command-line failures.

**Their checks are deliberately excluded from the 3123.** They are not
comparable to a Jest or Vitest test: they have no per-case isolation, no setup or
teardown, no reporter and no coverage instrumentation. Folding them into the
headline would inflate it with a different unit of measurement. Counted as files
rather than tests, the repository has **148** executable test files — 70 in the
backend, 76 in the frontend and 2 in `scripts/` — of which `npm test` runs 146.

### Linting and formatting

| Command | Backend | Frontend |
|---|---|---|
| `npm run lint` | ✅ runs | ✅ runs |
| `npm run typecheck` | ✅ runs | ✅ runs |
| `npm run check-format` | ✅ runs | ✅ runs |
| `npm run lint:openapi` | ✅ runs | – |

`lint:openapi` builds `openapi/openapi.json` from `openapi/openapi.yaml` and lints
it with Spectral against the NL API Design Rules 2.2.1. In the v2026.10.0
measurement at `9e0d18e`, `lint`, `check-format` and `lint:openapi` exited 0;
`typecheck` was not run in that pass. The repository-level checks
`check-supply-chain`, `check-mirror` and `check-rip-bpmn` exited 0 in the same
pass.

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
| `pre-push` | `npm run deps:check`, then `npm run check-rip-bpmn`, then `npm run lint`, then `npm run check-format` | Both packages in full, plus the RIP BPMN copies |

`deps:check` runs first, since v2026.09.5, so a clone whose install has fallen
behind the lockfile stops there with `npm ci` named — instead of failing lint or
the format check on the wrong tool versions, with nothing in the output saying
why.

`check-rip-bpmn` runs second. The twelve RIP phase models exist three times:
the source under `examples/organizations/flevoland/`, the copies in
`e2e-fixtures/flevoland/`, and the RONL Business API's parser fixtures. The
check compares the `e2e-fixtures` copies byte for byte with their source, and
the source against the sha256 fingerprints in `rip-bpmn-fingerprints.json`,
which is committed identically in both repositories. `--write` regenerates the
fingerprints and refreshes the `e2e-fixtures` copies. No CI workflow runs it, so
the hook is where it gates.

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

| Workflow | Lint | Typecheck | OpenAPI lint | **Tests** | Build | Deploy |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `azure-backend-acc` / `-production` | ✅ | ✅ | ✅ | **✅** | ✅ | ✅ |
| `azure-frontend-acc` / `-production` | ✅ | ✅ | – | **✅** | ✅ | ✅ |
| `azure-ropa-site-acc` / `-prod` | – | – | – | – | – | ✅ |

The production workflows in the table are no longer started by a push to `main`:
`promote-to-production.yml` calls them, and runs one test of its own first —
`scripts/promotion-targets.test.mjs`, in its `changes` job, before the decision
that test covers. See
[How a promotion reaches production](deployment.md#how-a-promotion-reaches-production).

!!! warning "A fixture-only or example-only pull request runs no backend suite"
    `azure-backend-acc.yml` triggers on every pull request into `acc`, but its
    `changes` job then matches the changed files against one pattern:

    ```
    ^(\.nvmrc$|packages/backend/|\.github/workflows/azure-backend-acc\.yml$|package-lock\.json$|package\.json$)
    ```

    When nothing matches, the `deploy` job — which holds the lint, typecheck
    and test steps — is skipped and reports success. `e2e-fixtures/`,
    `examples/` and `packages/frontend/public/examples/` are not in the
    pattern, yet the backend tests that guard them read exactly those
    directories: the four fixture-integrity and parity files and
    `besluitvorming-gedelegeerd-bundle.test.ts`. So a pull request that changes
    only fixtures or examples merges with none of them run. A change under
    `packages/frontend/public/examples/` does run the frontend suite, whose
    pattern covers `packages/frontend/`, but not these backend tests. For such a
    change, run `npm test -w packages/backend` before pushing; for the RIP
    copies, the `pre-push` hook's `check-rip-bpmn` is the only automatic check.

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
headline number honest. A coverage tool that only reports files a test happened
to import will show a clean table for a feature nobody tested at all; this one
makes that feature appear as a 0% row. Four things are excluded, each for a
stated reason: `*.test.ts`, `src/types/**` (declarations, no runtime), `index.ts`
(the boot script) and `db/seed-ropa.ts` (a self-executing CLI, not an importable
module). `db/migrate.ts` is pointedly **not** excluded — it exports a plain
`migrate()` that a mocked pool can drive, so it stays visible rather than being
written off. The table instruments **58 backend files**, as it did at
v2026.09.6 — no backend source file has been added since, and v2026.10.0
changed none.

| Area | Files | Tests | Covers |
|---|---:|---:|---|
| `src/services` | 21 | 768 | Every service: operaton, sparql, dso, dossier, quality, ozon, norms, edocs, ropa, vendor, assets, template, triplydb, orchestration, shacl-validation, dmn-validation, externalTaskWorker |
| `src/routes` | 23 | 724 | Every route module plus `routes/index` and `routes/registry`, each mounted in isolation (a fresh `express()` app per file, not the full `index.ts`) with the service layer mocked and supertest driving requests — and each response validated against the OpenAPI document |
| `src/utils` | 11 | 219 | `outboundUrl` 62, `config` 27, `outboundHttp` 23, `errors` 23, `ttl-cache` 13, `rootViews` 13, `publicPaths` 13, `buildInfo` 13, `etag` 11, `logger` 11, `problem` 10 |
| `src/openapi` | 4 | 38 | The conformance helpers routes are checked with (16), route-to-operation matching (10), the served document (9), and the coverage rule that fails when a `/v1` route is undocumented (3) |
| `src/middleware` | 3 | 33 | `error.middleware` 22, `cors.middleware` 8, `version.middleware` 3 |
| `src/db` | 3 | 25 | `mappers` 15, `migrate` 7, `pool` 3 |
| `src/e2e-fixtures.test.ts` | 1 | 5 | The `e2e-fixtures/` bundle consumed by the RONL Business API's E2E suite — manifest parses, every declared file exists, each BPMN's process id matches its `processDefinitionKey`, each shell's `calledElement` references resolve, and every process keeps its artifacts after its flow elements |
| `src/e2e-fixture-decisions.test.ts` | 1 | 5 | The bundle's **DMN dependencies**, which the manifest used to omit entirely: every declared decision file ships, each provides exactly the decisions it claims, those match the `decisionRef`s in its BPMN, every decision any fixture calls is shipped or declared external, and every `businessRuleTask` resolves the untenanted decision |
| `src/example-fixture-parity.test.ts` | 1 | 4 | Every file in a mirrored RIP bundle is byte-identical to its twin — `examples/organizations/flevoland/rip-phase-2x/` against `e2e-fixtures/flevoland/`. Bundles opt in through `MIRRORED_BUNDLES` |
| `src/public-example-fixture-parity.test.ts` | 1 | 3 | The *looser* parity rule for the pair the Modeler serves against the one LDE deploys — `packages/frontend/public/examples/` against `e2e-fixtures/` — which must match once four sanctioned labels are stripped, and where the fixtures copy must actually carry the labels it is allowed to carry |
| `src/besluitvorming-gedelegeerd-bundle.test.ts` | 1 | 17 | The hand-written Besluitvorming bundle under `packages/frontend/public/examples/flevoland/besluitvorming-gedelegeerd/` agrees with itself: the FIRST-hit `GedelegeerdBesluitRoute` decision and its five inputs, the twelve forms, the six lanes and six declared phases, the untenanted DMN call, the signed besluit document and its bindings, the escalation of a declined signature, and schema element order |

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
- A few defensive outermost `catch` blocks are left deliberately uncovered.
  `health.routes.ts`, the example this page used to give at 89.74%, now reads
  100% statements.
- **The outbound-guard tests pin their own environment.** `scripts/jest-env.cjs`
  sets `ALLOW_LOCAL_ENDPOINTS=false` and `TRIPLYDB_ALLOWED_HOSTS` before any
  module reads `.env`; dotenv never overrides a variable that is already set.
  Without that, a developer configured for local Jena saw 46 of them fail.

---

## Frontend suite (Vitest)

`packages/frontend`. `vite.config.ts`'s `defineConfig` comes from
`vitest/config`; `test.environment` defaults to `node` with a per-file
`// @vitest-environment jsdom` opt-in, so the many pure-logic tests never pay for
a DOM. Uses `@testing-library/react`, `jest-dom`, `user-event`, `jsdom` and
`msw`.

| Area | Files | Tests | Notes |
|---|---:|---:|---|
| `components/ChainBuilder` | 13 | 185 | First `@dnd-kit`-coupled area. The hooks render fine with no `DndContext` wrapper — dnd-kit's context hooks fall back to sane defaults |
| `components/DocumentComposer` | 10 | 180 | The heaviest area, coupling `@tiptap/react` and `@dnd-kit`. Real ProseMirror runs under jsdom once `Range.getClientRects`/`getBoundingClientRect` and `document.elementFromPoint` are polyfilled |
| `src/services` | 12 | 164 | All 12 service modules — `msw` for the network-calling ones, jsdom `localStorage` for the two storage modules. `dsoService` is the largest at 53. `sparqlService` is tested against the backend route only; its browser-direct path and CORS-proxy fallback were removed in v2026.09.5 |
| `components/BpmnModeler` | 9 | 160 | `bpmn-js` and the properties panel mocked outright via a small fake modeler class built in a `vi.hoisted` block. `BpmnCanvas` 60, `BpmnModeler` 50 |
| `src/components` (top level) | 7 | 153 | `ShaclValidator` 40, `DmnValidator` 30, `ResultsTable` 26, `GraphView` 23, `OrganizationCard` 12, `Changelog` 11, `OrganizationsView` 11 |
| `components/DsoExplorer` | 2 | 131 | `DsoExplorer` 88 and `QualityProfileTab` 43. `dsoService` is mocked via `vi.mock` + `vi.importActual` so the pure URL/URN helpers stay real |
| `src/utils` | 10 | 117 | Pure logic: `exportService` 38, `ronlAttributes` 17, `logoResolver` 14, `testData` 11, `exampleVersions` 9, `buildInfo` 8, `documentRefs` 7, `exportFormats` 6, `problem` 5, `constants` 2 |
| `components/FormEditor` | 3 | 58 | `@bpmn-io/form-js` mocked — exercising the real library would mean mounting a full canvas editor |
| `components/RopaEditor` | 3 | 45 | Record fields, legal-basis SPARQL lookup, hydrate-from-linked-forms, the BPMN `ronl:ropaRef` tab, confirm-gated status transitions |
| `src/App.test.tsx` | 1 | 33 | `App.tsx` renders 11 feature components as inspectable stubs, isolating the orchestrator's own state machine. Includes the regression test for the error overlay, which is asserted on the view that raises it |
| `components/common` | 4 | 26 | Toolbar, language and organisation selectors |
| `src/data` | 1 | 21 | `dsoAuthorities` — the authority list generated from the government organisations register: levels, OINs, and type-ahead-friendly names |
| `vite/cspPlugin.test.ts` | 1 | 9 | The build-time Content-Security-Policy generator, including the build failing on a missing or invalid API URL |

!!! note "These are the runner's own per-file counts, summed"
    Every row above was derived from **Vitest's own JSON reporter**, grouped by
    directory — never from counting `it(` with grep, which miscounts every
    `test.each`, every commented-out case and every string containing the word.
    The rows therefore sum to exactly 1282, and their file column to 76. The
    backend table is the same, from Jest's `--json` report, and sums to 1841
    across 70 files — 1807 in the six directory areas, plus five files at the
    root of `src/`: the four fixture-integrity files (17) and the Besluitvorming
    bundle test (17).

    Both tables were regenerated at v2026.10.0, from the JSON reports of the
    4 October 2026 runs.

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
JSZip archive building — and now reads 100% statements, 94.80% branches.
**`DsoExplorer.tsx` was the largest genuine gap at 72% statements** and now sits
at 94.40%, over 358 branches — the most branching file in the frontend, and
still 89.38% of them covered after v2026.09.6 grew it again.

---

## The per-file branch floor

Since v2026.09.2 both runners enforce **80% branch coverage per file**, natively:
`jest.config.js` takes a glob key it applies to each matching file individually,
`vite.config.ts` takes `thresholds: { branches: 80, perFile: true }`.

`perFile` is the mechanism, not a detail. Against a package *average* the
threshold is inert — the frontend sits at 92.89% and the backend at 91.98%, so a
single file dropping to 40% would barely move either. Branches specifically,
because statement and line coverage largely restate *"was this file imported"*,
while an uncovered branch is a decision no test has ever checked.

**Branches only.** A functions floor would fail today, and is not a companion
setting to add without measuring first.

**Every file meets it.** At v2026.10.0, measured with the thresholds live,
**zero files are below 80% branches in either package** — 58 instrumented files
in the backend, 85 in the frontend. Both runs exit 0 with the floor enforcing,
which is the only claim worth making here: a threshold that is never exercised is
a comment, not a gate.

### The margin, and why it needed widening

The floor landed measured-clean but with none to spare:
`ChainBuilder/TestCasePanel.tsx` sat at **exactly 80.00%**, with thirteen more
files between 80 and 85. The first uncovered branch added to any of them would
have turned CI red on an unrelated change — which is how a floor stops being read
as a floor and starts being read as an obstacle.

v2026.09.2 raised twelve files. Of the frontend files carrying at least one
branch — **75 of 85** at v2026.10.0 — exactly **one is below 85%**:
`GraphView.tsx` at 82.25%. Its eleven remaining uncovered branches are all inside
d3's force-simulation tick and drag handlers — `d.x || 0` position fallbacks,
`if (!event.active)` drag guards — which need a running simulation and
synthesised drag events to reach. That is a d3 harness, not a test of this
component. The config comment says so, so that whoever next turns this red knows
the answer is to test their new branch rather than lower the floor.

**The backend is no longer the thinner margin.** Of its **58 instrumented files,
52** carry a branch, and **two** sit between the floor and 85%:
`services/sparql.service.ts` at 82.85% and `services/dmn-validation.service.ts`
at 84.97%. `utils/outboundHttp.ts`, flagged here at v2026.09.5 as the likeliest
place for the next uncovered branch to land, was given margin in v2026.09.6 and
now reads 85.71%; `utils/outboundUrl.ts` sits just above it at 85.48%.

The per-file figures in this section are **from the v2026.10.0 measurement**
of 4 October 2026, taken from each run's own coverage report: the coverage map
in Jest's JSON report for the backend, and Vitest's `coverage-final.json` for
the frontend. One row moved this release: `BpmnCanvas.tsx`, which v2026.10.0
changed, gained two branches and went from 86.18% of 181
to **85.79% of 183** — now within a tenth of a point of `AssetLibrary.tsx`.

The tightest files in each package, for anyone about to add a branch to one:

| Package | File | Branches | Of |
|---|---|---:|---:|
| backend | `services/sparql.service.ts` | 82.85% | 70 |
| backend | `services/dmn-validation.service.ts` | 84.97% | 233 |
| backend | `routes/dso.routes.ts` | 85.04% | 107 |
| backend | `utils/outboundUrl.ts` | 85.48% | 62 |
| backend | `utils/outboundHttp.ts` | 85.71% | 21 |
| frontend | `components/GraphView.tsx` | 82.25% | 62 |
| frontend | `DocumentComposer/AssetLibrary.tsx` | 85.71% | 21 |
| frontend | `BpmnModeler/BpmnCanvas.tsx` | 85.79% | 183 |
| frontend | `DocumentComposer/DocumentComposer.tsx` | 86.25% | 80 |
| frontend | `BpmnModeler/DmnTemplateSelector.tsx` | 86.66% | 45 |

Note the branch *counts* beside the percentages. `AssetLibrary.tsx` at 85.71% of
21 branches is three uncovered decisions and one new `if` away from red;
`dmn-validation.service.ts` at 84.97% of 233 has thirty-five uncovered and far
more room to absorb a change. A percentage alone does not tell you which files
are actually fragile.

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

## When the frontend suite fails only in parallel

Vitest runs test files in parallel by default, and on a loaded machine that can
produce failures that are not defects. This happened during the v2026.09.6
measurement and is documented here because the diagnosis is reusable, not because
anything was wrong with the code.

**What was seen.** The first `npm test -w packages/frontend` run reported
`Test Files 1 failed | 74 passed (75)` and `Tests 2 failed | 1257 passed (1259)`.
Both failures were in `components/DsoExplorer/DsoExplorer.test.tsx`, both with
the same message, `Error: Test timed out in 5000ms`:

- *Authority option labels carry no level prefix, so native type-ahead works on
  the short name*
- *switching Activities → Quality Profile → Activities preserves the selected
  authority and its filtered list*

**What establishes it as contention.** A failure inside a full parallel run is
not a finding until it has been reproduced on its own, so three runs were done
before any conclusion was drawn — and the failing run itself took **201.5 s**,
more than three times its normal 64.6:

| Run | Result |
|---|---|
| The file alone — `npx vitest run src/components/DsoExplorer/DsoExplorer.test.tsx` | **88 passed, 0 failed**, 64.55 s. The two named tests took **1632 ms** and **676 ms** |
| The whole suite serially — `npx vitest run --no-file-parallelism --coverage` | **75 files, 1259 tests, all passed**, 375.0 s |
| The same parallel command again, unchanged | **75 files, 1259 tests, all passed**, 64.58 s |

(The first and third rows landing within 0.03 s of each other is coincidence, not
a transcription slip — one file under no contention happens to cost about what
all seventy-five cost when the pool is healthy.)

Two tests that need 1.6 s and 0.7 s do not fail a 5000 ms budget because of
anything in the component. And the retry passing outright settles it: this was
not even a reproducible ordering problem, it was one starved run.

**The diagnostic that makes it legible** is in Vitest's own summary line. Compare
the `environment` figure across the three runs:

| Run | `environment` |
|---|---:|
| The failing parallel run | **862 s** |
| Serial | 121 s |
| The single file alone | 2.95 s |

862 seconds spent constructing test environments, against 121 for the same work
done one file at a time, is a worker pool contending for a machine that had
nothing left to give. When environment setup alone eats that much wall clock, a
5000 ms `findBy*` budget that normally resolves in 1.6 s expires — and the test
that reports the timeout is simply whichever one was waiting when the machine
stalled, not the one at fault.

!!! warning "Do not answer this with a standing `--no-file-parallelism`"
    Serial execution makes the symptom go away and costs more than it saves.
    It is **5.8× slower here** — 375 s against 64.6 s — on every run, forever.
    It diverges local runs from CI, where the Azure workflows still run the
    suite in parallel, so the configuration that is green locally is not the
    one being gated. And flakiness under parallelism is usually a real defect
    — shared module state, an unisolated temp directory, a port collision — so
    switching it off converts a signal into silence.

    `--no-file-parallelism` belongs in the diagnosis, as above, and not in a
    config file.

**If it recurs**, the fix belongs at that file's own boundary: a per-file
`testTimeout` on `DsoExplorer.test.tsx` with a comment naming the contention it
is sized to survive, so the next reader knows the number is deliberate rather
than arbitrary. Not a global timeout, and not a global parallelism setting.

**The v2026.09.6 figures were the clean runs.** Its 75 files and 1259 tests were
confirmed by both the serial run and the second parallel run, which agree
exactly; the 64.6 s quoted above was the parallel run's time, since parallel is
what `npm test` and CI actually do. The v2026.10.0 figures at the top of this
page come from a parallel run in which all 1282 passed.

---

## Defects the tests found

Six real problems surfaced from writing tests rather than from use. The two at
the end are the reverse case — one a test locked in, and one the suite was well
placed to catch and did not.

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

### The one a test locked in

**The SHACL validator passed every file it had not checked, and a unit test
required it to.** Production reported every file *Valid · All checks passed* with
all three shape layers *Not loaded*, while acceptance found the same file invalid
with 25 errors. The production deploy workflow had never copied the shapes into
the package, and the service computed `valid` from errors alone — so a layer that
never loaded, and therefore reported no errors, counted as a pass. A test
asserted exactly that: missing shapes, zero errors, `valid: true`. It was green
for the wrong reason, and it would have stayed green through any fix that kept
the behaviour. v2026.09.5 made `valid` require every layer to have loaded, and
the test now asserts the opposite.

A test that pins today's behaviour is worth only as much as the behaviour. Before
locking one in, ask what the output *should* be when the input is missing — not
what it happens to be.

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

## There is no browser suite in this repository

Stated as established rather than assumed, because the directory name invites the
opposite guess. Three checks at `71a8236`:

- **No dependency.** Neither `package.json` nor any config file in the repository
  mentions Playwright, under any casing. The lockfile names
  `@vitest/browser-playwright` once, as an optional peer of Vitest that is not
  installed.
- **No lockfile entry.** `package-lock.json` contains no
  `node_modules/@playwright`, `node_modules/playwright` or `node_modules/cypress`
  package — so nothing is installed even transitively.
- **No runner script.** Neither workspace defines an e2e entry point. `test` is
  `jest --coverage` in the backend and `vitest run --coverage` in the frontend,
  and that is the whole surface. The root script `npm run e2e:deploy-fixtures`
  (`scripts/deploy-e2e-fixtures.mjs`), new in v2026.10.0, is a **deploy
  helper**, not a runner: it puts the `e2e-fixtures/` bundle on the local
  Operaton through the local LDE backend — the shared decisions without a
  tenant, then each manifest process with its sub-processes, forms and
  documents under its tenant — and refuses an LDE backend whose Operaton is not
  on this machine. It moved here from the RONL Business API, which keeps a
  script of the same name that calls this one.

**`e2e-fixtures/` is not a test suite.** It holds **58 files** — 33 `.form`, 11
`.document`, 8 `.bpmn`, 5 `.dmn` and one `manifest.json` — and no spec of any
kind; a search for a filename containing `spec` or `test` under it returns
nothing. The directory name describes *what the fixtures represent*, a
deployable end-to-end bundle, not a runner that lives here.

What consumes them is four **backend Jest tests** that parse and cross-check the
bundle as data — `e2e-fixtures.test.ts`, `e2e-fixture-decisions.test.ts`,
`example-fixture-parity.test.ts` and `public-example-fixture-parity.test.ts`, 17
tests between them. The bundle is *executed* by the RONL Business API's E2E
suite, in that repository. This one is their source of truth, with a manifest and
integrity tests; it is not their runner. See
[The one the tests missed](#the-one-the-tests-missed) for what that division of
labour cost once.

---

## What this page does not measure

Three gaps, named so that nobody reads a figure here as covering them:

**The backend under parallel workers.** The backend was measured serially, with
`--runInBand`, so its 68.7 s says nothing about how long `npm test` or the CI
step takes with Jest's default workers, and cannot be set against the parallel
backend times earlier releases quoted. The counts and coverage are unaffected.
The measurement ran on Node 24.21.0, the version `.nvmrc` pins.

**Per-test-file coverage attribution on the frontend.** Vitest's v8 coverage is
whole-run: it reports what the suite as a whole covered, not what each test file
contributed. Where the v2026.09.6 table near the top of this page pairs a new
test file with a coverage figure, it is pairing a file with *its obvious
subject*, which is an editorial judgement, not a measurement. Two test files
touching the same module cannot be told apart by these numbers.

**`4148c9a` itself.** The v2026.09.8 commit was not re-run for this pass, so the
delta quoted at the top — +2 files, +40 tests — is arithmetic against the
**previously published** v2026.09.8 figures, not against a fresh measurement of
the older commit. The same holds further back: each release's deltas were
computed from the previous release's published figures. If those figures were
wrong, the deltas inherit the error.

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
`DsoExplorer.tsx` went from 72% to 94.40% statements, and `exportService.ts` got
its DOM/JSZip harness and reads 100%. What is left is `GraphView.tsx` at 82.25%
branches, which is a deliberate hold rather than a gap: see
[The per-file branch floor](#the-per-file-branch-floor).

**Put the dossier harness in CI.** The root has a script for the two harnesses,
`npm run test:scripts`, the promotion harness runs in CI, and since v2026.10.0
`test:scripts` runs on Windows too. One thing remains:
`scripts/dso-dossier.test.mjs` still runs in no workflow and no hook, so its 24
checks protect the dossier renderer only as long as someone remembers. Neither
harness has been ported to `node:test`. See
[Script harnesses outside `npm test`](#script-harnesses-outside-npm-test).

**Deliberately out of scope for now:** visual regression, a cross-browser matrix,
and E2E in this repository — see
[There is no browser suite in this repository](#there-is-no-browser-suite-in-this-repository)
for what does and does not live under `e2e-fixtures/`.
