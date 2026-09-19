---
component: CPSV Editor
---

# Testing

The CPSV Editor's automated test suite runs on **Vitest**, and covers the
pure-logic core the editor depends on — TTL generation and parsing, DMN XML
handling, validators, the iKnow import mapping — plus the state hooks, the
network-boundary utilities, every tab component, and three end-to-end journeys
driven against a live stack.

The testing roadmap that ran from P0 to P7 is **complete**: every phase has
landed, and the per-file 80% branch floor is enforced natively by the runner.

!!! info "Figures on this page are measured, not estimated"
    Every unit count and percentage below was produced by running the suite
    against **v2026.09.6** on **19 September 2026** at `2723db1` on `main` — the
    full run and each scoped script individually, in a clean clone of that
    commit after `npm ci`, under Node 24.14.1. The three **end-to-end journeys**
    were run locally against a live stack — this editor's dev server, the Linked
    Data Explorer backend on `:3001` and Operaton on `:8081` — and **3 passed in
    14.0 s**, with Playwright 1.62.1. That stack was running while the unit suite
    was measured, which is the likeliest reason for the slower wall-clock time
    below.
    Rerun the commands in [Running the tests](#running-the-tests) to reproduce
    them.

**At a glance:** 62 files · **763 tests** · all passing · 84 s for a full run
with coverage on this measurement, plus **3 end-to-end journeys** run separately.

Coverage: **90.10% statements · 88.23% branches · 78.71% functions · 90.76%
lines**, with every file at or above the 80% branch floor.

!!! danger "Measure after `npm ci`, never after `npm install`"
    `npm install` has reported *"up to date"* here while `node_modules` still
    held the **old** versions of a just-bumped dependency — npm had written the
    new ones into its hidden lockfile without replacing the package directories.
    A run against that tree reports a green suite measured on the wrong
    instrument. CI is immune because it installs with `npm ci` on a clean
    runner; a local run is not.

---

## Running the tests

All tests run on **Vitest**. `react-scripts` and Create React App are gone as
of v2026.09.1 — see [The Vite migration](#the-vite-migration). Run everything
from the repository root after `npm ci`.

| Command | Scope | Suites | Tests |
|---|---|---:|---:|
| `npm run test:ci` | Everything, once, with coverage | 62 | 763 |
| `npm test` | Everything, interactive watch mode | 62 | 763 |
| `npm run test:generator` | TTL generator regression tests | 8 | 119 |
| `npm run test:roundtrip` | TTL round-trip tests (P1) | 1 | 9 |
| `npm run test:p2` | Pure-logic utilities (P2) | 8 | 191 |
| `npm run test:p3` | State hooks (P3) | 3 | 33 |
| `npm run test:p4` | Network-touching utilities (P4) | 2 | 42 |
| `npm run test:p5` | Tab components, PreviewPanel, PublishDialog (P5) | 23 | 181 |
| `npm run test:p6` | `DMNTab`'s full lifecycle (P6) | 6 | 98 |
| `npm run test:e2e` | Playwright journeys (P7) — **needs a live stack** | 3 | 3 |

Each scoped script has a `:watch` counterpart. The phase scripts overlap
deliberately — a file can belong to more than one phase — so their counts do
not sum to 763.

### End-to-end journeys need a live stack

`test:e2e` drives the real application against a real backend and a real engine,
with nothing mocked between the browser and Operaton. It is **not wired into
CI**: it needs the Linked Data Explorer backend and an Operaton engine, neither
of which exists on a runner.

| Command | What it does |
|---|---|
| `npm run test:e2e` | Headless, and opens the HTML report when it finishes |
| `npm run test:e2e:headed` | A real browser window, actions slowed to 400 ms |
| `npm run test:e2e:ui` | Playwright UI mode |

A **global setup checks both services first and names what is missing**, because
the failure otherwise arrives disguised: a connection refused surfaced as an
amber validation banner, or as a deploy that quietly never enabled the Evaluate
button, with the runner then reporting a timeout on a button several steps from
the cause. The backend URL is read from `.env.development` rather than
hardcoded, so the preflight checks the same host the application will call.

!!! note "UI mode waits for you to press play"
    An idle UI-mode window with an empty trace pane reads as a hang. It is not:
    the runner discovers the tests and then waits, so no dev server starts and
    nothing reaches the backend until play is pressed.

```bash
# Full suite, non-interactive, with a coverage report
npm run test:ci

# Day-to-day watch mode
npm test

# One layer in isolation
npm run test:p2
```

!!! warning "`npm test` is watch mode — it does not exit"
    Use `npm run test:ci` in CI, scripts, or anywhere a process must terminate.
    `--coverage` lives on `test:ci` and not on `npm test`, so a watch run
    reports no coverage figures.

### Linting and formatting

Not tests, but part of the same pre-push gate:

| Command | What it does |
|---|---|
| `npm run lint` | ESLint over `src/**/*.{js,jsx,ts,tsx}` |
| `npm run lint:fix` | The same, applying fixable corrections |
| `npm run check-format` | Prettier in check mode over the whole tree |
| `npm run format` | Prettier in write mode over the whole tree |

### Git hooks

Husky installs two hooks:

| Hook | Runs |
|---|---|
| `pre-commit` | `npx lint-staged` |
| `pre-push` | `npm run deps:check`, then `npm run lint`, then `npm run check-format` |

`deps:check` runs first since v2026.09.5: a clone whose install has fallen behind
the lockfile stops there with `npm ci` named, instead of failing lint or the
format check on the wrong tool versions. `npm start` runs the same check before
Vite starts.

!!! important "The hooks do not run the tests"
    `pre-push` gates on the install, lint and formatting only, so nothing client-side stops
    a push that breaks the suite — run `npm run test:ci` yourself before
    pushing. Since 20 August 2026 the deploy pipelines do run it, and since
    v2026.08.2 a branch ruleset means a failing pull request cannot be merged
    into `acc` at all; see [CI](#ci).
    Note that `check-format` runs across the **whole tree**, not just staged
    files — a Prettier violation in a Markdown file fails the push just as a
    source file would.

    **Since v2026.09.2 formatting is also checked in CI**, in the `audit` job
    rather than the deploy workflows. Those carry `paths-ignore` for `docs/**`
    and `**/*.md`, so a check placed there would never see markdown — precisely
    what drifts, since `lint-staged` only formats `src/**` and `package.json` on
    commit.

### CI

Five workflows run in this repository.

| Workflow | Job | Runs |
|---|---|---|
| **Deploy ACC (orange-beach)** | `build_and_deploy_job` | `npm ci` → `npm run lint` → `npm run test:ci` → deploy to acceptance |
| **Deploy PROD (white-sky)** | `build_and_deploy_job` | The same sequence, deploying production |
| **Supply-chain audit** (`zizmor.yml`) | `audit` | zizmor 1.29.0, `renovate-config-validator --strict`, `npm run check-format`, and `npm run check-supply-chain` |
| **Semgrep** (`semgrep.yml`) | `scan` | Semgrep Code and Supply Chain — see [Dependency Scanning](../../contributing/dependency-scanning.md) |
| **Close preview environments** | `close_acc_preview`, `close_prod_preview` | Deletes a pull request's Static Web Apps preview when it closes — no tests, but see below |

**Preview environments close from a workflow with no path filter** (v2026.09.6). The
close jobs used to live in the deploy workflows, whose `paths-ignore` applies to the
close event too, so a pull request that changed only documentation never started the
workflow holding its close job, and its preview kept running. Four previews on ACC and
four on PROD had been left that way, each serving a public URL with old code and
holding one of the ten slots the Static Web Apps Standard plan allows. The close jobs
now trigger on every pull-request close for `acc` and `main`; closing an environment
that was never created succeeds and does nothing. GitHub starts no workflow at all for
a pull request with a merge conflict, so the release procedure also runs
`npm run check-previews`, which lists orphaned previews and prints the exact delete
command without running it.

The two deploy workflows run lint and then the full suite before the deploy
action, and a failure blocks the deploy. Until 20 August 2026 neither ran
anything of ours at all: the Static Web Apps action builds inside its own
container and invokes none of the repository's scripts, so the workflows went
from checkout straight to build-and-deploy. Both now carry an explicit Node
setup, `npm ci`, lint and test sequence ahead of it.

Two v2026.09.0 changes affect when you see a result. The deploy workflows now
skip documentation-only pull requests (`paths-ignore` on `docs/**`, `.claude/**`
and `**/*.md`), so a docs change gets **no test run and no preview
environment** — if you changed only Markdown and expected a green tick from the
suite, that is why. The `audit` workflow moved the opposite way: it lost its
`branches` filter entirely and now runs on *every* pull request, including one
based on another feature branch. Before that, a stacked pull request accumulated
no audit and GitHub reported it as clean with zero checks, then blocked it
permanently once the base was retargeted to `acc`.

Since v2026.08.2 the `acc supply-chain gate` ruleset makes this *enforcement*
rather than reporting: `acc` requires a pull request, and `audit` is a required
status check. A workflow that runs but cannot block is advice — and requiring
the check without also requiring a pull request would still let a direct push
past it. There are no bypass actors, so this applies to releases and to the
repository owner alike. The mechanics are covered in
[Supply-Chain Pinning](../../contributing/supply-chain.md).

!!! note "`audit` does not run the tests, and the deploy job does not run the audit"
    They are separate gates on the same pull request. `audit` reasons about the
    pipeline's own supply chain; `build_and_deploy_job` reasons about the code.
    A pull request needs both to be green before it can merge — and because the
    deploy workflow is path-filtered while the audit is not, a documentation-only
    pull request is gated by `audit` alone.

---

## Test inventory

Test files are colocated with the source they cover (`foo.js` →
`foo.test.js`). Counts are per file, as reported by Vitest.

### Core: TTL generation and parsing

| File | Tests | Style | Covers |
|---|---:|---|---|
| `src/parseTTL.roundtrip.test.js` | 9 | Real fixtures, no mocks | Parses a real reference export, regenerates TTL from the parsed state, then parses again — comparing business fields between the two parses rather than diffing against the original file's formatting |
| `src/utils/ttlGenerator.sections.test.js` | 29 | Pure unit | The skeleton the others sit in: `generate()` assembles a dozen optional sections, each behind its own condition — service identifier and sector, organisation logo, legal resource, temporal rules |
| `src/utils/ttlGenerator.uris.test.js` | 26 | Pure unit | The URI and date helpers every emitter shares — legal-resource and ruleset URIs, `cprmvValidFrom`, rules-derived dates, CPRMV rule subject URIs. A wrong one does not throw; it publishes a graph that parses and points at the wrong resources |
| `src/utils/ttlGenerator.entities.test.js` | 23 | Pure unit | Parameters, cost, output and the vendor service — above all that an empty field produces **no triple**, never a triple with an empty literal |
| `src/utils/ttlGenerator.dmn.test.js` | 11 | Pure unit | The DMN section for a model uploaded in this editor — deployment, test and validation history, each optional and each its own predicate |
| `src/utils/ttlGenerator.cellGrounding.test.js` | 12 | Pure unit | Per-cell `cprmv:Rule` emission, concept dedup, nested `hasPart` for compound cells, and the SHACL-conformance rules — see [Cell-Level Legislative Grounding](cell-level-grounding.md) |
| `src/utils/ttlGenerator.versionTarget.test.js` | 7 | Pure unit | The CPRMV version selector — namespace and shape differences between the `0.4.1` and `0.3.2` targets |
| `src/utils/ttlGenerator.dateAxis.test.js` | 3 | Pure unit | Rules-derived consolidation dates and duplicate-path rule URIs |
| `src/utils/ttlGenerator.citationStub.test.js` | 8 | Pure unit + the real export | The typed stub minted for a `cprmv:isBasedOn` citation — and **no** stub for a rule the same document already publishes, which asserted a second, contradictory `cprmv:id`. Half the file regenerates the real SZW normenbrief export and checks no subject carries two ids |
| `src/utils/ttlHelpers.test.js` | 32 | Pure unit | All ten TTL string/URI helpers — escaping, sanitising (filenames, `ruleIdPath`, IRIs), formatting. `sanitizeIri` is checked for idempotence and for leaving structural URI characters (`/`, `:`, `#`, `?`) intact |

Round-trip fixtures are the real reference exports in `examples/` —
`full-test.ttl`, `full-test-import-export.ttl`, and the DMN-free
`organizations/svb/Bepaling-leeftijd-AOW.ttl`. `dmnData` is derived from each
fixture's own `hasDmnData`/`importedDmnBlocks` the way `importHandler.js`
really does it, so the tests exercise a shape the app actually produces.
`examples/ronl.ttl` is deliberately excluded — it is the RONL SKOS vocabulary
file, not a CPSV-AP service export, and `parseTTLEnhanced` correctly throws on
it.

### Pure-logic utilities (P2)

| File | Tests | Style | Covers |
|---|---:|---|---|
| `src/utils/dmnHelpers.test.js` | 54 | Real DOM parsing (jsdom `DOMParser`) | Primary-decision-key extraction (root detection, `p_*` constant skipping, multi-root tie-breaking), rule and cell extraction, `validateDMNData`, concept generation, `evaluateTestCaseExpectation`, `extractOutputsFromDMN` |
| `src/utils/validators.test.js` | 29 | Pure unit | All eight exports: the six per-section validators, the `validateForm` aggregation across every section including array fields, and the `isValidDate` helper |
| `src/utils/iknowParser.test.js` | 31 | Real DOM parsing | Both iKnow XML export formats, format auto-detection, the field-map helper, the dot-path value extractor, and `applyMapping` including filters and transforms — plus the two guards: prototype path segments are neither read nor written, and a nested-quantifier or over-long transform pattern throws |
| `src/utils/cprmvImport.test.js` | 13 | Pure unit | `flattenCprmvRules` — sub-clause folding, namespace variants (0.4.1 slash, 0.3.0 `contains`, legacy flat arrays), multi-entry input, malformed input tolerance, id uniqueness |
| `src/utils/ronlHelper.test.js` | 5 | `global.fetch` mock | The two SPARQL functions that query the RONL vocabulary through the shared backend proxy |

### State hooks (P3)

| File | Tests | Style | Covers |
|---|---:|---|---|
| `src/hooks/useArrayHandlers.test.js` | 15 | `renderHook` + a `useState` harness | Array CRUD handlers, the four default-item factories, and the pre-configured wrapper hooks. New ids continue from the highest existing id, not the array length |
| `src/hooks/useDsoImport.test.js` | 9 | `renderHook` + fetch mock + real `window.history` | The DSO → DMN deep-link import: no-op paths, params stripped before the fetch resolves, error branches, and the full success path prefilling three tabs |
| `src/hooks/useEditorState.test.js` | 9 | `renderHook` + mocked `ronlHelper` | Initial defaults, the mount effects, and `clearAllData` — including its documented exception that TriplyDB config is *not* cleared |

### Network-boundary utilities (P4)

| File | Tests | Style | Covers |
|---|---:|---|---|
| `src/utils/triplydbHelper.test.js` | 38 | `global.fetch` mock + real `File`/`FormData`/`Blob` | All ten exports: graph-IRI construction, config validation, the three publish paths (including the `@prefix` → `PREFIX` conversion and `INSERT DATA`/`GRAPH` wrapping asserted against the posted body), logo upload, connection testing across every HTTP status branch, and the three `localStorage`-backed config functions |
| `src/utils/shaclHelper.test.js` | 4 | `global.fetch` mock | `validateTtl` — success, a parsed-but-invalid backend response, and the distinct `unavailable` shape on network failure. SHACL validation is advisory and must never block publishing |

`src/utils/problem.test.js` (7 tests, v2026.09.6) belongs with these, though no phase
script names it: it pins `getProblemDetail`, which reads the backend's RFC 9457 `detail`
first and still understands the older `error.message` and bare-string `error` shapes.
`src/App.lazyTabs.test.jsx` (5 tests) covers the lazy tabs, including the DSO deep link
that used to leave the DMN tab highlighted over an empty panel.

These use a plain `global.fetch` mock rather than `msw`. Every function here
is a single self-contained fetch call rather than a multi-request flow, so the
lighter approach stays proportionate; `msw` is worth revisiting if a future
phase needs to model a multi-endpoint flow or share fixtures across many
tests.

### Smoke test (P0)

| File | Tests | Covers |
|---|---:|---|
| `src/App.test.jsx` | 1 | Renders `<App />` and asserts on the real header. Replaces CRA's stock "learn react link" stub, which asserted text this app never rendered and had kept `test:ci` red since the project was scaffolded |

---

### Tab components and dialogs (P5)

Twenty-three files, 181 tests. Deliberately thin and even: every component
renders with realistic props, and one representative interaction proves the
controlled-component contract. No component is left at zero, and `src/components`
moved from 3.9% to 41% statements in this phase alone.

These tests found a latent crash in `IKnowMappingTab`, which reads
`mappingConfig.mappings` unguarded inside an expression short-circuited by an
empty configuration name — so a config without that key renders fine and throws
the moment someone types a name.

They also pinned something that was invisible: **`VendorTab` switches on the
vendor URI rather than a capability flag**, so iKnow gets integration tooling,
Blueriq gets the contact form, and every other vendor gets an "under development"
placeholder. Adding a vendor to the concept list gives it a dropdown entry and
nothing else.

### `DMNTab` lifecycle (P6)

Six files, 96 tests, covering validate → deploy → evaluate. The suite walks the
real lifecycle rather than testing each call in isolation, **because the interface
enforces that order**: the Evaluate button stays disabled until a deployment has
succeeded.

Two findings worth keeping. The unreachable-backend path is a deliberate *third*
outcome — not valid, not invalid, but skipped — and is now pinned as one. And
`handleDeployDMN`'s opening guard is unreachable: the Deploy button renders inside
the branch that requires an uploaded file, so the error it raises can never fire.

### End-to-end journeys (P7)

Three Playwright specs, run against a live stack rather than mocks. Measured on
11 September 2026 against the acceptance deployment, with the preflight confirming its
backend and the Operaton engine before anything was driven:

```bash
E2E_BASE_URL=https://acc.cpsv-editor.open-regels.nl \
E2E_BACKEND_URL=https://acc.backend.linkeddata.open-regels.nl \
E2E_OPERATON_URL=https://operaton.open-regels.nl \
npx playwright test --reporter=list
#   3 passed (9.3s) — authoring 3.1 s, normbedragen 3.2 s, round-trip 2.0 s
```

`--reporter=list` rather than `npm run test:e2e`, which opens the HTML report when it
finishes — fine at a desk, a hang in anything scripted.

| Spec | What it proves |
|---|---|
| `e2e/authoring-journey.spec.js` | The application can create a service: empty form → real deploy → real evaluation → exported TTL |
| `e2e/round-trip-journey.spec.js` | It can read an existing one back: import a full TTL, swap its decision model, deploy, evaluate, download and check what was written |
| `e2e/normbedragen-journey.spec.js` | One deployment answers repeatedly: a chained DRD deployed once, evaluated with four request bodies that differ only in the peildatum, then exported. Added in v2026.09.3 with the 2026-H2 bijstandsnormen |

!!! danger "`E2E_BASE_URL` points the journeys at a deployed build — and at production's engine"
    Since v2026.09.3 `E2E_BASE_URL` drives the journeys against an already-deployed
    app instead of a local dev server, and drops the `webServer` block so none is
    started. **The journeys are not read-only**: each clicks *Deploy to Operaton*
    and leaves a deployment behind, and the fixtures use real decision keys.
    `.env.acceptance` and `.env.production` name **the same engine**,
    `https://operaton.open-regels.nl`, so a run against acceptance deploys a real
    version of those keys into the engine production evaluates against — and
    Operaton versions a duplicate key rather than rejecting it, so a consumer that
    evaluates *by key* then answers from the test fixture. Only a local stack,
    `.env.development`'s `localhost:8081`, is free of that.

    The app also calls the backend it was **built** against: `E2E_BACKEND_URL`
    redirects the preflight probe, not the application. Driving a deployed build
    means driving its stack.

Both assert **values rather than status codes** — zorgtoeslag 1150 and a specific
annotation string — because a decision table that stopped matching would still
answer 200 with an empty result set. That assertion was verified to bite by
setting the expected value wrong and watching the test fail. The export assertion
reads the downloaded file rather than trusting the filename, since a filename
check passes on an empty file.

Fixtures live in `e2e-fixtures/` with a manifest recording each one's provenance,
so editing an example cannot silently change what a test asserts.

The authoring journey **found a defect no unit test could reach**: below 1600px
the preview panel, mounted fixed and 500px wide, covers the header controls — at
1280px, opening the preview leaves no way to close it. The suite runs at 1600×900
so the journey is not blocked, and the threshold is documented rather than dodged.

## Coverage

Measured with `npm run test:ci` against v2026.09.6 on 19 September 2026, in a
clean clone after `npm ci`.

**Overall: 90.10% statements · 88.23% branches · 78.71% functions · 90.76%
lines** — against 54.75% / 40.88% / 38.68% / 55.57% at v2026.09.0. The jump is
P5, P6 and the branch-floor work landing together; v2026.09.3's two parser guards
moved `src/utils` a little further.

| Area | Statements | Branches | Functions | Lines |
|---|---:|---:|---:|---:|
| `src/hooks` | 100% | 93.44% | 100% | 100% |
| `src/utils` | 94.80% | 88.06% | 97.98% | 95.62% |
| `src/config` | 92.15% | 82.35% | 75.00% | 91.83% |
| `src/components` | 84.41% | 88.65% | 85.71% | 87.50% |
| `src/components/tabs` | 84.46% | **92.18%** | 65.93% | 84.67% |
| `src` (App, index) | 84.56% | 82.22% | 58.62% | 85.63% |

The rows are the runner's own per-directory figures, so `src/components` counts only the
files directly in that folder — the dialogs and panels — and the tabs have a row of their
own. That split is where the functions gap is: the tabs are well branched and thinly
exercised as whole handlers.

`src/components` was at **4.05% branches** before the P5 and P6 work landed.

### Every file clears the 80% branch floor

The floor is enforced natively — `thresholds: { branches: 80, perFile: true }` —
so this is a gate rather than a report. See
[The Coverage Floor](../../contributing/coverage-floor.md) for how the three
repositories reached it.

`DMNTab.jsx`, the largest file in the repository, is the **best-covered component**
at 98.32% branches, from 45.73% at v2026.09.1.

!!! warning "Two files sit one branch above the floor"
    `ConceptsTab.jsx` 80.55% and `ChangelogTab.jsx` 80.70%. Thresholds pass at
    `>= 80`, and the ratchet that used to absorb a slip is gone, so **a single
    added `?.` or `||` default in either turns CI red** on an otherwise
    unrelated change. `useDsoImport.js` was the third until v2026.09.6, when the
    deep-link fix's tests took it from 80.39% to 92.15%.

!!! note "What the branch column does not see"
    A branch floor steps straight over branch-free code. `ConceptsTab.jsx` reads
    80.55% on branches but **71.62% statements and 63.33% functions**;
    `App.jsx` reads 83.33% / 72.44% / **55.55%**. The uncovered code there is
    largely whole handlers no test calls. That asymmetry is why a functions floor
    is [a separate decision](../../contributing/coverage-floor.md#a-functions-floor-is-a-separate-decision)
    rather than a free companion setting.

---

## Defects the tests found

Both were discovered by writing the tests, not known beforehand.

### `cprmv:isBasedOn` was silently dropped on re-import

A past release renamed the generator's `cprmv:extends` predicate to
`cprmv:isBasedOn`, but the read side in `parseTTL.enhanced.js` was never
updated to match. From that rename until v2026.07.0, **every
export-then-reimport of a temporal rule silently lost its
`extends`/`isBasedOn` relationship** — no error, just an empty field. The
round-trip test caught it on the first run. The parser now accepts both
spellings: `isBasedOn` first, `extends` for historical exports.

### `flattenCprmvRules` minted colliding ids

Ids were built as `Date.now()` plus a sequence counter, and *both* were reset
on every call. Two calls landing in the same millisecond — plausible in a fast
import flow — produced identical ids, which collide as React keys if both
results end up in the same list. A module-level counter now keeps ids unique
for the life of the page regardless of call timing.

---

## Documented behaviour

Not a bug, but a coupling worth knowing about before you change either side.

**NL-SBB concepts only regenerate when a DMN model is attached in session
state.** `generateConceptsSection()` is gated behind `hasDMN()` — that is,
`dmnData.isImported && dmnData.importedDmnBlocks`, or `dmnData.fileName &&
dmnData.content` — and *not* on `concepts.length > 0`. End to end this works
correctly, because `importHandler.js` derives `dmnData` from the imported
file. But a caller that skips that mapping and calls `generateTTL` with an
empty `dmnData` will see concepts silently vanish even though `concepts` still
has entries. `parseTTL.roundtrip.test.js` asserts both cases explicitly, so
the coupling is locked in and visible rather than a silent trap. Whether
concepts *should* be exportable independent of an attached DMN is a product
question, deliberately left open.

---

## Adding tests

- **Colocate.** `foo.js` → `foo.test.js`, next to the source.
- **Split by concern, not by file size.** `ttlGenerator.js` has eight separate
  test files — `sections`, `uris`, `entities`, `dmn`, `cellGrounding`,
  `versionTarget`, `dateAxis`, `citationStub` — rather than one large one:
  easier to review, and easier to see what is covered at a glance.
- **Add a script pair per phase.** Each new phase gets
  `test:<phase>` and `test:<phase>:watch` in `package.json`, using a
  `--testPathPattern` regex naming the files it covers, mirroring the existing
  `test:p2` / `test:p3` / `test:p4` entries.
- **Mock at the network boundary.** There is no local backend to run against —
  the editor depends on the Linked Data Explorer's shared Express backend for
  the SPARQL proxy, TriplyDB publishing, and DMN validation, deploy and
  evaluate. Anything touching those needs a `fetch` mock, not an integration
  target.
- **Update the counts on this page** when a phase lands, and rerun
  `npm run test:ci` to get real figures rather than estimating.

---

## The Vite migration

Create React App is gone as of v2026.09.1, migrated in **four phases, each
independently revertable**, in an order chosen so a working test suite exists at
every point. `react-scripts` provided both the build and the test runner, so
swapping the build first would have removed the regression net and the thing being
tested at the same moment — leaving no way to tell a migration defect from a
configuration defect.

| Phase | What landed | What it proved |
|---|---|---|
| **1** | Vitest alongside Jest | Both runners reported the same 16 suites and 257 tests |
| **2** | Vite builds alongside CRA | Same eleven public assets, main chunks within a kilobyte |
| **3** | The atomic cutover | `build/` → `dist/`; `npm audit` 52 → 10; builds ~30 s → under 2 s |
| **4** | The shims removed | 45 `jest` call sites migrated, not the 43 the plan counted |

Two things the plan did not cover would have **deployed green and broken**: Vite
only exposes `VITE_`-prefixed variables, so renaming the env call sites alone
would have left both environments talking to `localhost`; and `react-scripts` was
where ESLint itself came from, so removing it would have broken the lint step that
runs before the tests.

---

## Roadmap

**The P0–P7 roadmap is complete.** Every phase has landed:

| Phase | Scope | Landed |
|---|---|---|
| P0 | Smoke test | v2026.07.0 |
| P1 | TTL round-trip against real fixtures | v2026.07.0 |
| P2 | Pure-logic utilities | v2026.07.0 |
| P3 | State hooks | v2026.07.0 |
| P4 | Network-boundary utilities | v2026.07.0 |
| P5 | Tab components, `PreviewPanel`, `PublishDialog` | v2026.09.1 |
| P6 | `DMNTab`'s validate → deploy → evaluate lifecycle | v2026.09.1 |
| P7 | Playwright journeys against a live stack | v2026.09.1 |

The DOM-heavy phases were sequenced deliberately *after* the migration, so that
bundler-sensitive work — Tailwind/CSS processing, the JSX transform,
`process.env` versus `import.meta.env` — was written once against the final
toolchain instead of twice.

### What remains

Not phases, but the honest remaining edges:

- **Seven unreachable branches in `DMNTab.jsx`**, all guards the UI cannot
  reach — `if (!uploadedFile)` under a button that only renders once a file
  exists, and three of the same shape. Chasing them would mean testing through
  the component's internals; the file documents them as defensive dead code.
- **Three files one branch above the floor**, with no ratchet left to absorb a
  regression.
- **A functions floor**, which is a separate decision needing its own
  measurement — `App.jsx` sits at 55.55% functions against 81.48% branches.

**Deliberately out of scope for now:** swapping in an RDF library (the
round-trip tests are the data that should decide whether the hand-rolled
parser is fragile enough to justify the migration cost); OIDC and production
publishing auth, which is a separate security workstream described in
[Due Diligence](due-diligence.md); and visual regression and cross-browser
matrices, which are worth revisiting once the phases above are stable locally.
CI wiring was on this list too, and came off it on 20 August 2026 — see
[CI](#ci).

An E2E phase here will not resemble the RONL Business API's. There is no
Keycloak, no roles and no tenants — the editor is a single-user authoring tool
today, so a login-flow test has nothing to drive until OIDC lands. Publishing
to TriplyDB and deploying to Operaton are real side effects against shared
infrastructure; prefer a disposable or local target over the shared instances
if an E2E test ever needs to deploy for real.
