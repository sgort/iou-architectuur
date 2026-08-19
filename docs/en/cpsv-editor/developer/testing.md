---
component: CPSV Editor
---

# Testing

The CPSV Editor's automated test suite covers the pure-logic core the editor
depends on — TTL generation and parsing, DMN XML handling, validators, the
iKnow import mapping — plus the state hooks and the network-boundary
utilities. Components and `App.js` orchestration are largely uncovered by
design; see [Roadmap](#roadmap) for why, and what comes next.

!!! info "Figures on this page are measured, not estimated"
    Every count, command and coverage percentage below was produced by
    running the suite against **v2026.08.0** on **18 August 2026**. Rerun the
    commands in [Running the tests](#running-the-tests) to reproduce them.

**At a glance:** 16 suites · **257 tests** · all passing · ~50 s for a full
run with coverage.

---

## Running the tests

All tests run on Jest via `react-scripts test` — this is still a Create React
App project, with a Vite/Vitest migration planned (see [Roadmap](#roadmap)).
Run everything from the repository root after `npm install`.

| Command | Scope | Suites | Tests |
|---|---|---:|---:|
| `npm run test:ci` | Everything, once, with coverage | 16 | 257 |
| `npm test` | Everything, interactive watch mode | 16 | 257 |
| `npm run test:generator` | TTL generator regression tests | 3 | 22 |
| `npm run test:roundtrip` | TTL round-trip tests (P1) | 1 | 9 |
| `npm run test:p2` | Pure-logic utilities (P2) | 6 | 157 |
| `npm run test:p3` | State hooks (P3) | 3 | 28 |
| `npm run test:p4` | Network-touching utilities (P4) | 2 | 40 |

Each scoped script has a `:watch` counterpart — `test:generator:watch`,
`test:roundtrip:watch`, `test:p2:watch`, `test:p3:watch`, `test:p4:watch` —
that runs the same `--testPathPattern` without `--watchAll=false`.

```bash
# Full suite, non-interactive, with a coverage report
npm run test:ci

# Day-to-day watch mode
npm test

# One layer in isolation
npm run test:p2
```

!!! warning "`npm test` is watch mode — it does not exit"
    Use `npm run test:ci` in CI, scripts, or anywhere a process must
    terminate. Note also that `--coverage` lives on `test:ci` and not on
    `npm test`: in watch mode Jest pins coverage collection to whatever
    matched the *first* run, which on a clean start is nothing, so a watch
    run would report 0% across the board no matter what you exercise
    afterwards.

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
    `pre-push` gates on lint and formatting only. Nothing stops a push that
    breaks the suite, so run `npm run test:ci` yourself before pushing.
    Note that `check-format` runs across the **whole tree**, not just staged
    files — a Prettier violation in a Markdown file fails the push just as a
    source file would.

---

## Test inventory

Test files are colocated with the source they cover (`foo.js` →
`foo.test.js`). Counts are per file, as reported by Jest.

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
| `src/utils/validators.test.js` | 29 | Pure unit | All eight form validators, plus `validateForm` aggregation across every section including array fields |
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

## Coverage

Measured with `npm run test:ci` against v2026.08.0 on 18 August 2026.

**Overall: 54.58% statements · 40.81% branches · 38.51% functions · 55.42% lines.**

That headline number is dominated by untested UI. The layers the suite
actually targets are well covered:

| Area | Statements | Branches | Functions | Lines |
|---|---:|---:|---:|---:|
| `src/hooks` | 96.73% | 75.40% | 97.05% | 100% |
| `src/config` | 92.15% | 80.39% | 75.00% | 91.83% |
| `src/utils` | 84.66% | 62.11% | 90.05% | 85.35% |
| `src/components` | 24.44% | 4.05% | 18.18% | 23.80% |
| `src/components/tabs` | 5.74% | 2.72% | 2.46% | 6.03% |

Per module, highest first:

| Module | Statements | Branches |
|---|---:|---:|
| `utils/ttlHelpers.js` | 100% | 100% |
| `utils/ronlHelper.js` | 100% | 100% |
| `utils/shaclHelper.js` | 100% | 87.50% |
| `hooks/useEditorState.js` | 96.77% | 50.00% |
| `utils/validators.js` | 97.40% | 94.31% |
| `hooks/useArrayHandlers.js` | 97.14% | 75.00% |
| `utils/triplydbHelper.js` | 96.69% | 83.62% |
| `hooks/useDsoImport.js` | 96.42% | 78.43% |
| `utils/dmnHelpers.js` | 90.62% | 81.18% |
| `utils/cprmvImport.js` | 90.54% | 81.81% |
| `utils/iknowParser.js` | 88.95% | 70.10% |
| `parseTTL.enhanced.js` | 81.34% | 71.11% |
| `utils/ttlGenerator.js` | 80.09% | 53.87% |
| `utils/importHandler.js` | 10.34% | 0% |
| `App.js` | 14.16% | 31.87% |
| `components/tabs/DMNTab.jsx` | 8.24% | 3.31% |

The two hand-written files the [Due Diligence](due-diligence.md) review flagged
as the biggest risk — `ttlGenerator.js` and `parseTTL.enhanced.js`, neither
backed by an RDF library — now sit around 80% statement coverage with a
round-trip harness over real fixtures. `importHandler.js`, `App.js` and
`DMNTab.jsx` remain the largest gaps, and are exactly what phases P5 and P6
target.

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

## Roadmap

**Vite/Vitest migration checkpoint — next.** P0–P4 are green, which is the
precondition. The plan is to migrate the bundler (CRA → Vite, following the
Linked Data Explorer's proven configuration) and re-run the existing suite
under Vitest as the proof the migration regressed nothing. These phases were
written to port cheaply: they are pure logic and hooks, with Jest and Vitest
sharing nearly the same API surface (`jest.fn()` → `vi.fn()` and
`jest.mock()` → `vi.mock()` are close to mechanical renames), and they touch
neither JSX nor CRA-specific tooling.

| Phase | Scope | Notes |
|---|---|---|
| **P5** | Tab components, `PreviewPanel`, `PublishDialog` | Written directly under Vite/Vitest after the checkpoint. Critical interactions only — field entry → state update → preview reflects it; publish-workflow step transitions — not exhaustive branch coverage |
| **P6** | `components/tabs/DMNTab.jsx` | The largest and most complex file. Mock the backend at the fetch boundary and validate the validate → deploy → test → generate-concepts lifecycle at the interaction level |
| **P7** | Playwright E2E smoke tests | Start narrow: the app loads, a minimal service description exports successfully. Expand once there is more automated-testable surface |

The DOM-heavy phases are sequenced deliberately *after* the migration so that
bundler-sensitive work — Tailwind/CSS processing, the JSX transform,
`process.env` versus `import.meta.env` — gets written once against the final
toolchain instead of twice.

**Deliberately out of scope for now:** swapping in an RDF library (the
round-trip tests are the data that should decide whether the hand-rolled
parser is fragile enough to justify the migration cost); OIDC and production
publishing auth, which is a separate security workstream described in
[Due Diligence](due-diligence.md); and visual regression, cross-browser
matrices and CI wiring, which are worth revisiting once the phases above are
stable locally.

An E2E phase here will not resemble the RONL Business API's. There is no
Keycloak, no roles and no tenants — the editor is a single-user authoring tool
today, so a login-flow test has nothing to drive until OIDC lands. Publishing
to TriplyDB and deploying to Operaton are real side effects against shared
infrastructure; prefer a disposable or local target over the shared instances
if an E2E test ever needs to deploy for real.
