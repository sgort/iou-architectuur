---
component: CPSV Editor
---

# Testing

The CPSV Editor's automated test suite runs on **Vitest**, and covers the
pure-logic core the editor depends on — TTL generation and parsing, DMN XML
handling, validators, the iKnow import mapping — plus the state hooks, the
network-boundary utilities, every tab component, and two end-to-end journeys
driven against a live stack.

The testing roadmap that ran from P0 to P7 is **complete**: every phase has
landed, and the per-file 80% branch floor is enforced natively by the runner.

!!! info "Figures on this page are measured, not estimated"
    Every count and percentage below was produced by running the suite against
    **v2026.09.2** on **9 September 2026** on `main` at `bbda389` — the full run
    and each scoped script individually, after a clean `npm ci`. The two
    end-to-end journeys were run against a live Linked Data Explorer backend and
    Operaton engine. Rerun the commands in
    [Running the tests](#running-the-tests) to reproduce them.

**At a glance:** 60 files · **736 tests** · all passing · ~54 s for a full run
with coverage, plus **2 end-to-end journeys** run separately.

Coverage: **89.89% statements · 87.39% branches · 78.46% functions · 90.61%
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
| `npm run test:ci` | Everything, once, with coverage | 60 | 736 |
| `npm test` | Everything, interactive watch mode | 60 | 736 |
| `npm run test:generator` | TTL generator regression tests | 7 | 111 |
| `npm run test:roundtrip` | TTL round-trip tests (P1) | 1 | 9 |
| `npm run test:p2` | Pure-logic utilities (P2) | 8 | 184 |
| `npm run test:p3` | State hooks (P3) | 3 | 33 |
| `npm run test:p4` | Network-touching utilities (P4) | 2 | 40 |
| `npm run test:p5` | Tab components, PreviewPanel, PublishDialog (P5) | 23 | 181 |
| `npm run test:p6` | `DMNTab`'s full lifecycle (P6) | 6 | 96 |
| `npm run test:e2e` | Playwright journeys (P7) — **needs a live stack** | 2 | 2 |

Each scoped script has a `:watch` counterpart. The phase scripts overlap
deliberately — a file can belong to more than one phase — so their counts do
not sum to 736.

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
| `pre-push` | `npm run lint` then `npm run check-format` |

!!! important "The hooks do not run the tests"
    `pre-push` gates on lint and formatting only, so nothing client-side stops
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

Three workflows run in this repository.

| Workflow | Job | Runs |
|---|---|---|
| **Deploy ACC (orange-beach)** | `build_and_deploy_job` | `npm ci` → `npm run lint` → `npm run test:ci` → deploy to acceptance |
| **Deploy PROD (white-sky)** | `build_and_deploy_job` | The same sequence, deploying production |
| **Supply-chain audit** (`zizmor.yml`) | `audit` | zizmor 1.29.0, `renovate-config-validator --strict`, `npm run check-format`, and `npm run check-supply-chain` |

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
| `src/utils/ttlGenerator.cellGrounding.test.js` | 12 | Pure unit | Per-cell `cprmv:Rule` emission, concept dedup, nested `hasPart` for compound cells, and the SHACL-conformance rules — see [Cell-Level Legislative Grounding](cell-level-grounding.md) |
| `src/utils/ttlGenerator.versionTarget.test.js` | 7 | Pure unit | The CPRMV version selector — namespace and shape differences between the `0.4.1` and `0.3.2` targets |
| `src/utils/ttlGenerator.dateAxis.test.js` | 3 | Pure unit | Rules-derived consolidation dates and duplicate-path rule URIs |
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
| `src/utils/iknowParser.test.js` | 24 | Real DOM parsing | Both iKnow XML export formats, format auto-detection, the field-map helper, the dot-path value extractor, and `applyMapping` including filters and transforms |
| `src/utils/cprmvImport.test.js` | 13 | Pure unit | `flattenCprmvRules` — sub-clause folding, namespace variants (0.4.1 slash, 0.3.0 `contains`, legacy flat arrays), multi-entry input, malformed input tolerance, id uniqueness |
| `src/utils/ronlHelper.test.js` | 5 | `global.fetch` mock | The two SPARQL functions that query the RONL vocabulary through the shared backend proxy |

### State hooks (P3)

| File | Tests | Style | Covers |
|---|---:|---|---|
| `src/hooks/useArrayHandlers.test.js` | 13 | `renderHook` + a `useState` harness | Array CRUD handlers, the four default-item factories, and the pre-configured wrapper hooks. New ids continue from the highest existing id, not the array length |
| `src/hooks/useDsoImport.test.js` | 8 | `renderHook` + fetch mock + real `window.history` | The DSO → DMN deep-link import: no-op paths, params stripped before the fetch resolves, error branches, and the full success path prefilling three tabs |
| `src/hooks/useEditorState.test.js` | 7 | `renderHook` + mocked `ronlHelper` | Initial defaults, the mount effects, and `clearAllData` — including its documented exception that TriplyDB config is *not* cleared |

### Network-boundary utilities (P4)

| File | Tests | Style | Covers |
|---|---:|---|---|
| `src/utils/triplydbHelper.test.js` | 37 | `global.fetch` mock + real `File`/`FormData`/`Blob` | All ten exports: graph-IRI construction, config validation, the three publish paths (including the `@prefix` → `PREFIX` conversion and `INSERT DATA`/`GRAPH` wrapping asserted against the posted body), logo upload, connection testing across every HTTP status branch, and the three `localStorage`-backed config functions |
| `src/utils/shaclHelper.test.js` | 3 | `global.fetch` mock | `validateTtl` — success, a parsed-but-invalid backend response, and the distinct `unavailable` shape on network failure. SHACL validation is advisory and must never block publishing |

These use a plain `global.fetch` mock rather than `msw`. Every function here
is a single self-contained fetch call rather than a multi-request flow, so the
lighter approach stays proportionate; `msw` is worth revisiting if a future
phase needs to model a multi-endpoint flow or share fixtures across many
tests.

### Smoke test (P0)

| File | Tests | Covers |
|---|---:|---|
| `src/App.test.js` | 1 | Renders `<App />` and asserts on the real header. Replaces CRA's stock "learn react link" stub, which asserted text this app never rendered and had kept `test:ci` red since the project was scaffolded |

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

Two Playwright specs, run against a live stack rather than mocks.

| Spec | What it proves |
|---|---|
| `e2e/authoring-journey.spec.js` | The application can create a service: empty form → real deploy → real evaluation → exported TTL |
| `e2e/round-trip-journey.spec.js` | It can read an existing one back: import a full TTL, swap its decision model, deploy, evaluate, download and check what was written |

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

Measured with `npm run test:ci` against v2026.09.2 on 9 September 2026, after a
clean `npm ci`.

**Overall: 89.89% statements · 87.39% branches · 78.46% functions · 90.61%
lines** — against 54.75% / 40.88% / 38.68% / 55.57% at v2026.09.0. The jump is
P5, P6 and the branch-floor work landing together.

| Area | Statements | Branches | Functions | Lines |
|---|---:|---:|---:|---:|
| `src/hooks` | 99.33% | 83.60% | 100% | 100% |
| `src/utils` | 94.76% | 86.74% | 98.43% | 95.63% |
| `src/config` | 92.15% | 82.35% | 75.00% | 91.83% |
| `src/components` | 84.41% | **88.65%** | 85.71% | 87.50% |
| `src` (App, index) | 84.56% | 81.70% | 58.62% | 85.63% |

`src/components` was at **4.05% branches** three releases ago. That is the P5 and
P6 work.

### Every file clears the 80% branch floor

The floor is enforced natively — `thresholds: { branches: 80, perFile: true }` —
so this is a gate rather than a report. See
[The Coverage Floor](../../contributing/coverage-floor.md) for how the three
repositories reached it.

`DMNTab.jsx`, the largest file in the repository at 1855 lines, is now the
**best-covered component** at 98.34% branches, from 45.73% one release earlier.

!!! warning "Three files sit one branch above the floor"
    `useDsoImport.js` 80.39%, `ConceptsTab.jsx` 80.55% and `ChangelogTab.jsx`
    80.70%. Thresholds pass at `>= 80`, and the ratchet that used to absorb a
    slip is gone, so **a single added `?.` or `||` default in any of them turns
    CI red** on an otherwise unrelated change.

!!! note "What the branch column does not see"
    A branch floor steps straight over branch-free code. `ConceptsTab.jsx` reads
    80.55% on branches but **71.62% statements and 63.33% functions**;
    `App.jsx` reads 81.48% / 72.44% / **55.55%**. The uncovered code there is
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
- **Split by concern, not by file size.** `ttlGenerator.js` already has three
  separate test files (`dateAxis`, `versionTarget`, `cellGrounding`) rather
  than one large one — easier to review, and easier to see what is covered at
  a glance.
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
