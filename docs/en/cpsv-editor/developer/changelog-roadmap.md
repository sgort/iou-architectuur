---
component: CPSV Editor
---

# Changelog & Roadmap

---

## Changelog

### v2026.08.0 — Cell-Level Legislative Grounding & Backend-Routed DMN Calls (August 2026)

> Full deep-dive: [Cell-Level Legislative Grounding](cell-level-grounding.md).

**Legislation is now linked at decision-table cell granularity.** DMN's native `knowledgeSource` links legislation at *decision* level, and CPRMV's `extends`/`ruleType`/`confidence` at *rule* level — neither can express that one cell of one rule rests on one specific article. Three layers close that gap. In the DMN, `<inputEntry>`/`<outputEntry>` elements carry `dct:source`, `cprmv:sourceQuote` and `cprmv:isBasedOn` attributes, with a numbered family (`dct:source1`, `cprmv:sourceQuote1`, …) for compound cells whose conjuncts each need their own citation. `extractRulesFromDMN` in `dmnHelpers.js` reads every cell's id, FEEL text and groundings into `rule.inputEntries`/`outputEntries`. `generateDmnSection` in `ttlGenerator.js` then emits a `cprmv:hasPart` list of per-cell `cprmv:Rule` resources on each `DecisionRule`, deduplicating minted concepts and nesting a further `hasPart` for compound cells.

**A namespace-agnostic DOM lookup, fixing a defect that predates cell grounding.** Building Layer 2 surfaced that every selector-based DMN lookup silently matched nothing against a real, `dmn:`-prefixed file: CSS type selectors match on (namespace, local name), and an unprefixed selector implies the null namespace. Cell-level grounding — and the pre-existing rule-level export — therefore never actually worked for real DMN files. New `queryAllLocal`/`queryLocal` helpers match on local name regardless of prefix.

**Cell-grounding resources are SHACL-conformant.** Live validation against a published `.ttl` surfaced two `RuleShape` violations. `cprmv:id` is required (`sh:minCount 1`) on every `cprmv:Rule`, but cell resources emitted `dct:identifier` — a property that shape does not check at all — and concept resources carried no identifier whatsoever; both now emit `cprmv:id`, including compound-cell sub-resources. And `cprmv:isBasedOn` has `sh:class cprmv:Rule`, so its object must itself be typed `cprmv:Rule`: concept targets already were, but a bare external citation URI (CVDR, `wetten.overheid.nl`) was not. Every distinct citation URI referenced via `isBasedOn` now gets a minted, deduplicated stub — `<uri> a cprmv:Rule ; cprmv:id "<uri>" .`

**DMN deploy and evaluate now route through the Linked Data Explorer backend.** Posting straight from the browser to Operaton's `/engine-rest/…` hits CORS in local development. `handleDeployDMN` now posts to the backend's `POST /v1/dmns/deploy`, and Evaluate Decision, *Run intermediate tests* and *Run test cases* all go through a shared `evaluateViaBackend()` helper hitting `POST /v1/dmns/evaluate/:decisionKey` — mirroring the pattern `runBackendValidation()` already used for `/v1/dmns/validate`. The browser talks to the backend; the backend talks to Operaton server-to-server. The **Evaluation URL** preview in the API Configuration panel shows the backend URL it actually calls, and the now-unused `apiConfig.deploymentEndpoint` field is removed.

**Date-typed DMN inputs are sent as `Date`, not `String`.** `generateRequestBodyFromDMN`'s `typeRef="date"` branch typed every date input as `{ value: "YYYY-MM-DD", type: "String" }`, assuming Operaton would convert internally. That is wrong for any DMN calling `.year`/`.years` on the input directly, as several Amsterdam decisions do — confirmed from Operaton's own logs (`DMN-01005 Invalid value … for clause with type 'date'`). The generated body now emits a full ISO timestamp with offset and `type: 'Date'`.

**The Concepts tab keeps its output variables when an evaluation returns no match.** A DRD root with `hitPolicy="RULE ORDER"` and no catch-all rule legitimately returns an empty result set against the auto-generated baseline request body. `extractOutputsFromTestResult` could only learn an output's name and type from what the engine actually returned, so an empty result yielded zero output concepts even though the DMN declares one — a gap inputs never had, since `generateRequestBodyFromDMN` reads `<dmn:inputData>` straight from the XML. New `extractOutputsFromDMN` closes it for outputs, reading a decision's declared `<dmn:output>` name and type from the XML namespace-agnostically, handling multiple output columns and the name-vs-label fallback; `handleEvaluateDMN` falls back to it whenever the live result yields nothing.

**The DMN tab's Base URL follows `REACT_APP_OPERATON_URL` in development.** `apiConfig.baseUrl` now reads that variable, falling back to the production instance, instead of hardcoding the shared Operaton URL — without it, local development silently pointed at the shared ACC/PROD engine rather than a local Docker container.

**Amsterdam HvA reference DMN: deploy blockers, FEEL fixes and a 100-case MC/DC suite.** The `HvA_full_dmn_export.dmn` reference export was brought to a deployable, evaluable state, and the fixes double as standing guidance for DMN authors — see the [DMN Workflow](../user-guide/dmn-workflow.md) tips and [DMN Testing](../user-guide/dmn-testing.md) troubleshooting. Deployment was blocked by a missing `camunda:historyTimeToLive` and 48 unescaped `&` characters in `knowledgeSource` URLs. Evaluation was blocked by multi-word FEEL bare names — Operaton's feel-scala engine consumes only the first word and throws `FEEL/SCALA-01008` — and by `<dmn:output>` elements declaring only `label` and no `name`, which makes evaluation throw a blank, unlogged exception. Malformed rule cells (`not -` on boolean columns, `not(null) -` on string columns, bare `and`-joined comparisons, and an unparenthesised `not "met partner"`) were rewritten, and two decisions that defaulted to `hitPolicy="UNIQUE"` while carrying a wildcard default rule were corrected to `FIRST`. A test suite now covers every one of the 99 rules across all 25 decisions with one empirically-verified case each (100 cases, run live), and `extract-legal-sources.py` resolves each decision's `authorityRequirement` → `knowledgeSource` links against the annotation registry — 97 of 99 resolve cleanly across 14 source documents and 23 distinct JuriConnect citations.

---

### v2026.07.0 — CalVer Releases & a Real Test Suite (July 2026)

> Full inventory and commands: [Testing](testing.md).

**Release versions switch to CalVer.** New releases are numbered `YYYY.MM.patch` — `2026.07.0`, then `2026.07.1` for a same-month follow-up, `2026.08.0` the next month — matching the Norm Editor's tagging convention. Only the version string changes; the release workflow is otherwise untouched. Historical SemVer entries up to and including v1.10.7 are left as they were.

**A phased test suite lands (P0–P4).** The suite grew from three incidental regression files to 16 suites covering the pure-logic core, the hooks, and the network-boundary utilities: TTL round-trip tests against real `examples/*.ttl` fixtures (P1); `validators`, `ttlHelpers`, `ronlHelper`, `dmnHelpers`, `iknowParser` and `cprmvImport` (P2); `useEditorState`, `useArrayHandlers` and `useDsoImport` via `renderHook` (P3); and `shaclHelper` and `triplydbHelper` behind a plain `global.fetch` mock (P4). Each phase has its own `test:<phase>` script pair so a layer can be run in isolation. The CRA `App.test.js` stub — which asserted on text this app never rendered and had kept `test:ci` red since the project was scaffolded — was replaced with a real smoke test (P0).

**Two defects surfaced by writing the tests.** A past commit renamed the generator's `cprmv:extends` predicate to `cprmv:isBasedOn`, but `parseTTL.enhanced.js`'s read side was never updated to match — so since that rename, **every export-then-reimport of a temporal rule silently dropped its `isBasedOn` relationship**. The round-trip test caught it immediately as a field that came back empty; the parser now recognises both spellings, `isBasedOn` first and `extends` for historical exports. Separately, `flattenCprmvRules` minted ids as `Date.now()` plus a sequence counter that reset on every call, so two calls landing in the same millisecond produced identical ids that collided as React keys; a module-level counter now keeps ids unique for the life of the page.

**Coverage collection moved to `test:ci`.** In interactive watch mode, `react-scripts test --coverage` pins collection to whatever matched the very first run — on a clean start, *"no tests found related to files changed since last commit"*, i.e. nothing — so pressing `a` afterwards still reported 0% across the board. `--coverage` now lives on `test:ci`, which runs `--watchAll=false`, leaving `npm test` plain for day-to-day watch mode.

---

### v1.10.7 — Per-Commit Changelog Format (July 2026)

**The in-app Changelog tab renders per-commit entries.** `ChangelogTab.jsx` now renders `"format": "commits"` entries — an icon-and-colour header per commit, an sha/author trailer, and an Upcoming/Released status badge — alongside the existing `"sections"` shape, adopting the same per-commit changelog convention already used by the RONL Business API and the Linked Data Explorer. Legacy entries are unaffected and render exactly as before.

**Version reconciled with the changelog.** `package.json` still carried the scaffold's `0.1.0` while `changelog.json` was at `1.10.6`; the two are now in lockstep. A repo-local `bump-release` command ships with the repository rather than staying machine-local, adapted for this single-package repo — no scope dimension, no endpoint-map reconciliation — and targeting `src/data/changelog.json` directly.

**A testing strategy was drafted**, grounding a phased plan in the app's state at the time — thin and undocumented coverage, a stale failing `App.test.js` stub, no RDF library, no local backend — and sequencing it against the CRA-to-Vite migration flagged in the [Due Diligence](due-diligence.md) review: pure-logic tests first, then the bundler swap, then the DOM-heavy component and E2E work written once directly under Vite/Vitest. The phases it defined are what shipped in v2026.07.0; see [Testing](testing.md) for the current state.

---

### v1.10.6 — Empty-result Test Verification (July 2026)

**Test cases that expect an empty result set are now auto-verified.** A DMN test case whose expected value is the literal empty collection `[]` (or `{}`) — meaning no rule matches and the engine correctly returns an empty result — was previously reported as *"OK (unchecked)"* because the empty-result branch in `evaluateTestCaseExpectation` only recognised the descriptive strings *"empty result"* / *"no matching rule"*. A literal `[]` fell through to the `key=value` parser, found no pairs, and was judged unverified even though the response was exactly correct. The empty-result check now also matches a literal empty array or object, so an expected value of `[]` is treated as *"expect an empty result set"*. Boundary cases such as the Thuisbatterij `jaarGebondenBudget` years outside the modelled range (2025, 2028) now pass automatically. A non-empty response against an `[]` expectation still fails, and structured/descriptive expectations are unaffected.

---

### v1.10.5 — CPRMV Version Selector & Rules-derived Dates (June 2026)

> Full deep-dive: [CPRMV RuleSet / Dataset Generation](cprmv-dataset-generation.md).

**Choose which CPRMV vocabulary version to preview, export and publish.** A CPRMV version selector (`0.4.1` / `0.3.2`) next to the preview/export controls now drives the generated TTL. The editor previously always emitted the `0.4.1` namespace (`https://standaarden.open-regels.nl/standards/cprmv/0.4.1#`), so data published for a `0.3.x` consumer was invisible to it. Selecting `0.3.2` binds `cprmv:` to `https://cprmv.open-regels.nl/0.3.2/` — the versioned-path namespace the Linked Data Explorer `/v1/norms?cprmv_version=0.3.2` query reads. The two targets differ in shape, not just prefix: `0.4.1` wraps the rules in a `cprmv:RuleSet` (+ `cprmv:hasPart`); `0.3.2` instead emits a `cprmv:Dataset` per ruleset — the unit `/v1/norms` reports under `dataset_versions`. The flat `cprmv:Rule` resources are emitted for both targets. The selection applies consistently to the live preview, the TTL download, and the publish-to-TriplyDB action.

**Consolidation date is derived from the rules, not entered by hand.** The published consolidation date — the `eli:is_realized_by` version on the LegalResource and every `cprmv:RuleSet`'s `cprmv:validFrom` and versioned `cprmv:id` — is now derived per ruleset from the BWB in-force date the rules themselves carry in their `ruleIdPath` (e.g. `BWBR0015703_2026-04-03_0` → `2026-04-03`), rather than the manually-entered *"Version or consolidation date"* field, which had let an operator pick a date that disagreed with the rules. Each ruleset is dated from its own rules, so non-primary rulesets (entering via `cprmv:Rule` references, e.g. BWBR0044894 and BWBR0015711) are now versioned correctly too — previously they were emitted version-less. The manual field remains a fallback when no rule carries a dated `ruleIdPath`, with today's date as a last resort.

**Rules sharing a legal path no longer collapse on publish.** A `cprmv:Rule`'s subject URI was built only from its `ruleIdPath`, so two rules on the same legal path — a range's bounds or multiple maxima (*"per maand"* / *"per kalenderjaar"*) — resolved to the same RDF subject and silently merged on publish (a 69-rule import surfaced as only 66 norms). Each rule now gets a unique subject URI: the first occurrence of a path keeps the path-derived URI, and each subsequent duplicate gets an `_N` suffix (`_2`, `_3`, …) in document order. Both the flat `cprmv:Rule` resources and the `0.4.1` `cprmv:RuleSet` `hasPart` list use the same assignment (69 in, 69 out). The duplicates still share a `rule_id_path_key`, which the LDE treats as the dedup key.

**`0.3.2` datasets pass CPSV-AP 3.2.0 validation.** The `0.3.2` `cprmv:Dataset` records were co-typed `dcat:Dataset`, which triggered the CPSV-AP 3.2.0 `DatasetShape` and raised an error per dataset for missing `dct:title`/`dct:description`/`dct:publisher` plus an untyped `dcat:landingPage`. They are now typed only `cprmv:Dataset` — the class the LDE `dataset_versions` query reads, and one that no shape targets — so pre-publish validation passes (4 errors per dataset → 0) while the data stays fully consumable.

**Nested sub-clauses fold into their parent rule on import.** Importing a CPRMV Rules API payload no longer creates standalone, norm-less rules for nested enumeration sub-clauses (e.g. the *onderdeel 1°./2°./3°.* under *Artikel 31, lid 2, onderdeel r.*). Those `hasPart` members carry no `rule_id_path`, so they are folded — in order, recursively — into the parent rule's `cprmv:definition`, which keeps the complete legal text. Nested members that are rules in their own right (carry a `rule_id_path`) are still imported separately. For the 1 juli 2026 `0.4.1` normenbrief this turns 81 imported entries into 72 — exactly the norms `/v1/norms` returns.

**Toolbar polish and a runnable generator test suite.** The CPRMV version selector is styled as a toolbar control matching the action buttons, and the Import / Show Preview / Clear All buttons no longer wrap to two lines. Generator tests are runnable with `npm run test:generator` (one-shot), `test:generator:watch` and `test:ci`; they cover the version selector (namespace + shape), the rules-derived dates, and the duplicate-path URI handling, and live in `src/utils/ttlGenerator.*.test.js`.

---

### v1.10.4 — Test Routing, Concept Coverage & Parameter Validation (June 2026)

**Parameter notation and label are now unconditionally required.** `validateParameter` previously only required `skos:notation` when `schema:value` was also present, and never validated `skos:prefLabel` at all. A new `cprmv:ParameterWaardeShape` (added in LDE v1.9.8) makes both properties mandatory `[1,n]`, so the client-side check now mirrors the SHACL constraint: both fields are required regardless of whether a numeric value is set. The pre-publish validation panel and the inline Parameters-tab error now surface missing notation and label immediately, rather than letting the file through to the back-end SHACL check.

**Run test cases per decision, and gather concepts across the whole DMN.** Run All Test Cases now routes each case to its own decision: a case's optional `decision` field is used as the evaluation key, falling back to the selected Decision Key when absent. One test file can therefore exercise every decision of a deployed DMN, and each result shows the decision it ran against. NL-SBB concept generation now unions both inputs and outputs across every case (deduped by name), where it previously took outputs from a single result; each variable records the decision(s) it appears in.

**Per-decision concept badges and persistent DMN tab.** The Concepts tab shows a decision badge next to each variable, colour-matched to its kind: blue beside Input #x, green beside Output #x. Output concepts are clustered so variables from the same decision sit together. The DMN tab now keeps its state when switching tabs — an uploaded DMN, deployment status, and the full test-case run results survive a hop to the Concepts tab and back, instead of being reset each time the tab unmounted.

---

### v1.10.3 — Decision Selection & Functional Test Verification (June 2026)

**Pick which decision to evaluate in multi-decision DMNs.** `extractPrimaryDecisionKey` now prefers a *root* decision — one that no other decision requires via `informationRequirement`/`requiredDecision` — instead of blindly taking the first `<decision>` element in document order, fixing models where the intended output decision is authored later in the file. When a DMN has several independent roots, document order breaks the tie and a console warning points to the picker. The DMN File card shows a Decision Key dropdown whenever a file contains more than one testable decision, listing each as *"Name (id)"*; selecting one updates the Decision Key and the evaluation URL everywhere.

**Test cases now verify functional correctness, not just a 200.** Previously a test case went green whenever the HTTP call succeeded, regardless of the returned values. A new `evaluateTestCaseExpectation` compares each case's expected outputs against the engine's actual outputs and returns PASS, FAIL, or unverified. It parses the readable `key=value, reden="…"` expected strings, accepts a structured expected object, and special-cases the *"empty result set"* expectation. Results render **PASS** (green), **FAIL** (red, with an Expected-vs-Actual mismatch table per output), **ERROR** (red, when the call itself fails) and **OK-unchecked** (amber, when no expectation could be parsed — never a silent green). Summary and header counts are now verdict-based, so *"N/N passed"* means functionally correct results.

---

### v1.10.2 — Conformance Round-trip Fixes (June 2026)

**Imported DMNs SHACL-conformant.** Imported DMN blocks are preserved verbatim, so their Decision Rules previously bypassed the v1.10.0 CPSV-AP fixes. `generateDmnSection` now runs a `normalizeImportedDmnBlocks` pass: each `cpsv:Rule` gets `dct:title`/`dct:description` injected when absent, and a `cpsv:implements` pointing at a `/services/` URI is repointed to the `eli:LegalResource` (or dropped when none exists). Edits are additive/repointing only and idempotent.

**Valid, readable IRIs for NL-SBB concept URIs.** A shared `sanitizeIri` helper replaces whitespace with underscores and percent-encodes IRI-illegal characters, applied to the concept URI, `dct:subject` and `skos:exactMatch`. The Concepts tab "Variable Name (used in URI)" input now enforces URI-safe names. Existing `skos:exactMatch` values under the `…/concepts/` namespace have hyphens converted to underscores to match the underscore-style concept URIs.

**Populate the Concepts tab from test cases.** Running uploaded test cases now fills the Concepts tab even without a manual evaluate — input concepts are derived from the union of every uploaded case's request-body variables; output concepts still come from the last successful result.

**Round-trip `dct:spatial` on import.** Import now reads the organisation's spatial value from both `dct:spatial` (current output) and `cv:spatial` (legacy), so downloaded files re-import and re-validate cleanly.

---

### v1.10.1 — SHACL Scope Clarification (June 2026)

The PublishDialog pre-publish SHACL panel now explains that it checks the Turtle that will actually be published — the editor's current (regenerated) output — which can differ from an originally-imported file, since import normalises legacy CPRMV/CPSV-AP terms to CPRMV 0.4.1 / CPSV-AP 3.2.0. An imported file that fails validation on its own may still publish as conformant.

---

### v1.10.0 — CPRMV 0.4.1 & CPSV-AP 3.2.0 Conformance (June 2026)

**CPRMV 0.4.1 conformance.** The `cprmv:` namespace was bumped to the canonical `https://standaarden.open-regels.nl/standards/cprmv/0.4.1#`, and a `prov:` prefix added. `ttlGenerator` now emits a 0.4.1-conformant `cprmv:RuleSet` per `rulesetId` — replacing the old `cprmv:Dataset` — carrying `cprmv:id`, `cprmv:validFrom`^^`xsd:date`, `cprmv:isOutputOf` → the service, `cprmv:hasMethod` → a dual-typed `cprmv:RuleMethod`/`cprmv:CodificationMethod`, an ordered `cprmv:hasPart` RDF list of its rules, and `prov:wasDerivedFrom`. Every `cprmv:Rule` now always emits `cprmv:id`; `cprmv:extends` was renamed to `cprmv:isBasedOn`.

**Import the CPRMV 0.4.1 API output.** New `src/utils/cprmvImport.js` `flattenCprmvRules` walks the CPRMV Rules API shape (array of `cprmv:RuleSet` objects with nested `…#hasPart` maps), recursing and flattening sub-rules into the editor's flat model (nested rules inherit their parent's `rulesetId`). Tolerates legacy 0.4.1-slash, 0.3.0, and flat-array exports. Used by both `handleImportJSON` and the CPRMV tab's **Load Example**; the bundled `cprmv-example.json` is now the conformant API output.

**CPSV-AP 3.2.0 conformance.** `dct:language`/`cv:sector`/`cv:thematicArea` references are typed in-graph (`dct:LinguisticSystem`/`skos:Concept`); the organisation emits `dct:spatial` (was the non-conformant `cv:spatial`) pointing at a `dct:Location`-typed node; `cpsv:Rule` nodes (temporal + DMN decision rules) always emit `dct:identifier`/`dct:title@nl`/`dct:description@nl`, and `cpsv:implements` points at the `eli:LegalResource` (or is omitted when none). A full editor-generated TTL validates clean against both the CPSV-AP 3.2.0 and CPRMV 0.4.1 SHACL shapes.

**Pre-publish SHACL validation (advisory).** New `src/utils/shaclHelper.js` `validateTtl` POSTs the generated Turtle to `REACT_APP_BACKEND_URL/v1/shacl/validate` and returns a layered result; it never throws (an unreachable backend yields a neutral `{ unavailable: true }` shape). PublishDialog runs validation on open and via a **Validate now** button, rendering a layered CPRMV / CPSV-AP / RONL panel. It is purely advisory and never blocks publishing.

---

### v1.9.6 — DSO → DMN Handoff (June 2026)

**Consume the DSO → DMN handoff from the Linked Data Explorer.** New `useDsoImport` hook (`src/hooks/useDsoImport.js`) consumes the deep-link contract `/?dsoImport=dmn&dmnId=…&env=…&activityName=…&authority=…&activityUrn=…&fsRef=…` — on mount it fetches the standalone DMN XML from the shared backend (`GET REACT_APP_BACKEND_URL/v1/dso/toepasbare-regels/{dmnId}/dmn`, with `?env=prod` only when `env=prod`) and prefills the DMN/Service/Organization tabs. The DMN tab stays fully interactive (`isImported` stays false), so deploy/test/publish run through the existing flow. After consuming the link the import params are stripped via `history.replaceState`, and a `consumedRef` guard prevents a StrictMode double-invoke.

**Shared decision-key extraction + external-content hydration.** `extractPrimaryDecisionKey` was lifted out of `DMNTab.jsx` into `src/utils/dmnHelpers.js` and exported, so the import hook and the DMN tab share one implementation. `DMNTab` now hydrates its internal uploaded-file/decision-key/test-body/parsed-decisions/validation state from `dmnData.content` whenever content arrives from outside the tab and no local file was uploaded.

---

### v1.9.5 — DMN Workflow Polish (May 2026)

**Request Body Generation Reads `<inputValues>` Constraints**

`generateRequestBodyFromDMN` in `DMNTab.jsx` now consults every decisionTable input column for an `<inputValues>` FEEL allowed-values list and uses the first allowed value as the starter for the corresponding inputData. DMNs that constrain string inputs (e.g., normbedragen descriptions, status codes, enum-style domain values) no longer produce empty strings that would fail at Operaton evaluate time — the generated starter body is runnable as-is.

Two helper closures added: `parseFirstFeelListItem` (unwraps quoted strings, coerces booleans, parses numbers from a comma-separated FEEL list) and `findInputValuesExample` (scans `decisionTable > input` elements for a constraint whose `inputExpression` matches the given inputData name). When no constraint exists, the inputData falls through to the existing `typeRef` switch and name-based heuristics unchanged — every existing project DMN keeps generating the same starter body as before.

**Validation Backend Unreachability Surfaced**

`runBackendValidation` no longer fails silently when the Linked Data Explorer backend at `REACT_APP_BACKEND_URL` cannot be reached. The validation panel renders a third, distinct visual state — amber *"Syntax validation result not available"* — with a short explanation that DMN deployment and testing still work; only the syntactic pre-check is skipped. The amber state is kept visually separate from the existing red *"Syntax issues found"* state so a network failure cannot be mistaken for an actual DMN problem. A new `validationResult.unavailable` flag drives the third branch in the validation pill header; the `parseError` bubble switches between amber and red styling to match the meaning of the message.

**DMN Modelling Reference Updates**

Patterns surfaced while building the Den Haag *Beslissing Levensonderhoud (ALO)* and SZW *normbedragen* deployable DMNs have been folded back as standing guidance: every `<inputData>` element requires a `<variable>` child with `name` and `typeRef` so sub-decision evaluation by key can resolve `requiredInput` references; the primary decision must be listed first in the file because Operaton selects the first `<decision>` as the primary key; and decisions that aggregate output from required decisions should declare passthrough output columns (e.g., `redenAfwijzing`, `informatiebehoefte`) so the response from a primary-decision evaluate call carries the full verdict shape rather than just the headline output.

---

### v1.9.4 — Dataset Catalog & Stable Graph Publishing (May 2026)

**Legal Resource URI Cleanup**

Parser normalises `legalResource.bwbId` to its canonical un-versioned form on import — trailing `/YYYY-MM-DD` and `/YYYY-MM-DD/<index>` segments are stripped so the version is captured exclusively in `legalResource.version`. The `generateLegalResourceSection` emitter refactored to route both the subject URI and `eli:is_realized_by` through `buildLegalUriForRulesetId`, producing a clean un-versioned `eli:LegalResource` subject (e.g., `https://wetten.overheid.nl/BWBR0015703`) and a single-versioned manifestation URI (`.../BWBR0015703/2026-01-01`), regardless of whether `bwbId` arrived clean or in a legacy already-versioned form. `cv:hasLegalResource` in the Service section automatically points to the same un-versioned URI as the LegalResource block, closing the loop between Service, LegalResource, and versioned manifestation. Resolves the doubled-version URIs (e.g., `.../BWBR0015703/2026-01-01/0/2026-01-01`) that previously appeared in `eli:is_realized_by` and propagated through to `cprmv:implements` on rules.

**cprmv:Dataset Generation**

TTL export now emits a `cprmv:Dataset` block per unique `cprmv:rulesetId` across the CPRMV Rules collection — one Dataset per legal source, dual-typed `cprmv:Dataset` and `dcat:Dataset` for DCAT catalogue interoperability. Dataset properties include `dct:identifier`, optional `dct:title` (primary ruleset only), `cprmv:rulesetId`, `cprmv:implements` pointing to the legal manifestation URI, optional `dcat:version`, `dct:issued`, and `dcat:landingPage`.

CPRMV Rule emitter updated so `cprmv:implements` uses each rule's own `rulesetId` rather than the service's primary legal resource — accurate rule-level claims in multi-BWB services, and identical loose (`cprmv:rulesetId`) and tight (`cprmv:implements`) SPARQL join results. New `buildLegalUriForRulesetId()` helper handles BWB, CVDR, and full-URI inputs; defensively strips already-versioned suffixes before appending the version. `cprmvDataset` entity type registered in `vocabularies.config.js`; `dcat` namespace already present in `TTL_NAMESPACES`. Supports the new `/v1/norms` endpoint in the Linked Data Explorer.

**Deterministic Graph IRI on Publish**

Publishes now land in a per-service graph at `https://regels.overheid.nl/graphs/{org-local}/{service-id}` (e.g., `.../graphs/Sociale_Verzekeringsbank/aow-leeftijd`) instead of the auto-numbered `graph:default-N` series. Republishing the same service overwrites its previous graph rather than creating an incremented copy — each service now corresponds to a single, stable graph IRI in TriplyDB. New `buildGraphIRI()` helper derives the IRI from `organization.identifier` and `service.identifier`, threaded through `publishToTriplyDB` and `publishToTriplyDB_SPARQL` as a `graphIRI` parameter (default fallback: `graphs/default`).

The graph IRI is forwarded to the Linked Data Explorer backend's `/v1/triplydb/update-service` endpoint as `graphName`, logged on the backend as `triggeredByGraph` for end-to-end traceability across multi-publish flows.

**Vendor Tab Polish**

Vendor tab data — selected vendor, contact details, technical fields, certification, service notes — now survives navigation between tabs; the local `selectedVendor` state in `VendorTab.jsx` replaced with a derived alias over lifted `vendorService.selectedVendor`, eliminating the data loss that previously occurred on tab re-entry. RONL concept fetch (analysis, method, and vendor concepts from TriplyDB) lifted from `LegalTab` and `VendorTab` into `useEditorState` — concepts are fetched once on App mount and shared across both tabs, eliminating per-mount network calls and dropdown flicker.

TTL import now restores vendor data: `selectedVendor`, provider organisation name, `contactPoint` (name, email, telephone), `foaf:homepage`, `schema:url`, `schema:license`, `ronl:accessType`, `dct:description`, and `schema:image`. `vendorService` threaded through `parseTTL()` and `applyImportedData()`; `setVendorService` added to the setters object handed to `handleTTLImport`. Round-trip verified against the SVB AOW-leeftijd Vendor example.

---

### v1.9.x — DMN Testing Suite & Vendor Services (February 2026)

**v1.9.3 — DMN Syntactic Validation**

 Immediately after upload, the editor runs the DMN file through the shared backend's five-layer syntactic validator. The result is shown inline in the file card — valid files display a green badge, files with issues display a collapsible panel grouped by layer. Validation covers five layers. Issues are grouped by layer in a collapsible panel. Each issue carries a severity (error, warning, or informational), a typed code, a human-readable message, and — where applicable — an element reference and line number.

**v1.9.2 — DMN Testing Suite**

Intermediate decision tests added, allowing each sub-decision in a DRD to be tested individually. Batch test case upload from JSON files with progressive real-time result display and pass/fail statistics. Smart filtering automatically skips constant `p_*` parameter decisions. NL-SBB concepts auto-generated from last successful test run output. Critical date type fix: date variables now correctly use `type: 'String'` in request bodies, resolving `InvalidRequestException` errors for DMNs with `typeRef='date'`.

**v1.9.1 — Vendor Tab**

Dedicated Vendor tab for publishing `ronl:VendorService` metadata. Dynamic vendor selection dropdown loading RONL Method Concepts from TriplyDB. Full Blueriq implementation: contact information, service URL, licence type, access type (`fair-use` / `iam-required`), logo upload, and certification tracking workflow with pre-populated request email. Generates complete `ronl:VendorService` TTL with `schema:provider` nested structure. Multi-vendor architecture extensible for future platforms. Round-trip import/export support.

**v1.9.0 — Semantic Rule Linking**

Critical bug fix: rule URIs now use the full `cprmv:ruleIdPath` for uniqueness (e.g., `BWBR0015703_2026-01-01_0_Artikel-20_lid-1_onderdeel-a`), eliminating RDF triple merging in TriplyDB caused by duplicate short IDs. Added `cprmv:implements` property linking each rule directly to its legal resource URI, removing fragile string-based matching. Versioned URI support: rules link to `eli:is_realized_by` version URI when available. Policy tab now shows an informational banner with the linked legal resource as a clickable link.

---

### v1.8.x — RONL Concepts & Legal Resource Extensions (January 2026)

**v1.8.3 — RONL Concepts Integration**

Legal tab extended with Analysis dropdown (Wetsanalyse JAS, JRM, FLINT) and Method dropdown (16 options: ALEF, Avola, DMN, RuleSpeak, and more), both loading dynamically from TriplyDB via SPARQL. Properties `ronl:hasAnalysis` and `ronl:hasMethod` link legal resources to RONL vocabulary concepts. Full round-trip import/export. iKnow tab refactored into extensible Vendor tab with vendor selection dropdown as the foundation for multi-vendor architecture.

**v1.8.2 — DMN Type Detection & CVDR Support**

DMN files now read `typeRef` from `<variable>` elements for accurate type detection, with intelligent birth date generation (random age 25–68) for demographic variables. Added CVDR (municipal regulations) support alongside BWB national legislation — automatic repository detection with visual badges, smart URI generation, and quick links to the appropriate repository. Compact tab navigation eliminates horizontal scroll across all 10 tabs.

**v1.8.1 — NL-SBB Concept Layer**

Complete three-phase implementation of the NL-SBB concept layer for DMN variables. Phase A: automatic concept generation from DMN test results with Dutch NL-SBB standard compliance. Phase B: full import/export round-trip support. Phase C: editable Concepts tab with add/edit/delete for all concept properties including preferred labels, definitions, notations, and `skos:exactMatch` URIs. Bidirectional linking via `dct:subject` from concepts to technical variables. Foundation for cross-DMN semantic matching and chain validation in the Linked Data Explorer.

---

### v1.7.0 — Organisation Logo Management (January 2026)

Logo upload with automatic resizing to 256×256px, live preview, and direct publishing to TriplyDB as an asset file. TTL generation adds `foaf:logo` and `schema:image` properties. Added `ronl:implements` link from DMN to Service enabling complete RDF graph traversal: DMN → Service → Organisation → Logo.

---

### v1.6.0 — TriplyDB Publishing (January 2026)

Direct publishing to TriplyDB from the editor. Configuration dialog for API URL, account, dataset, and token (stored in `localStorage`, never on server). Test connection functionality and real-time status feedback. Automatic validation before publish. Supports up to 5 MB per upload. Created `triplydbHelper.js` utility and `PublishDialog` component.

---

### v1.5.x — Modularisation & RPP Architecture (January 2026)

**v1.5.2**

TTL generation for DMN fully moved to `ttlGenerator.js`. DMN output variables now extracted (previously only inputs). Fixed auto-generated request body producing empty values, which caused DMN evaluations to return null.

**v1.5.1**

Complete four-phase modularisation: state management extracted to `useEditorState`, TTL generation to `TTLGenerator` class, import logic to `importHandler.js`, array operations to `useArrayHandlers`. Rules–Policy–Parameters (RPP) separation pattern visualised with colour-coded tab badges and explanatory architecture banners. Seven bug fixes including: missing `cprmv:hasDecisionModel` link, DMN section not appearing on TTL import, file input not resettable for re-import, iKnow mappings not surviving Clear All.

**v1.5.0**

DMN integration: upload DMN files, deploy to Operaton, and test decision evaluations. `dct:source` placeholder URI for DMN file location, `ronl:implementedBy` for the executing software system, `cpsv:isRequiredBy` back-link to the DMN model. Baseline iKnow integration: parses CognitatieAnnotation and SemanticsExport XML formats, maps to CPSV-AP fields via configurable mappings.

---

### v1.4.x — CPSV-AP 3.2.0 Compliance (December 2025)

**v1.4.1**

Fixed missing `cpsv:implements` linking each rule directly to the service it implements.

**v1.4.0**

Minimal CPSV-AP 3.2.0 compliance achieved. Key changes: Organisation class corrected to `cv:PublicOrganisation`, mandatory `cv:spatial` added, `cpsv:follows` replaced with `cv:hasLegalResource`, explicit `dct:identifier` outputs for all major entities, mandatory Rule identifiers and titles. Cost and Output sections added to Service tab with full import/export.

---

### v1.3.0 — CPRMV Tab & Modularisation (December 2025)

Dedicated CPRMV tab with JSON import for all mandatory `cprmv:{...}` fields. Component extraction: separate tab components for Service, Organisation, Legal, Rules, Parameters; Preview moved to a side panel. Changelog tab added.

---

### v1.2.2 — Clear All & Import Fixes (November 2025)

Clear All button with confirmation dialog resets all form fields. Four import bug fixes: `ronl:ParameterWaarde` parameters, `skos:prefLabel` organisation name, sequential import clearing, uncontrolled input warnings.

---

### v1.1.x — Parameters Tab (October 2025)

**v1.1.1**

Rules description field expanded to 10 rows; preview panel expanded to ~80 lines.

**v1.1.0**

Dedicated Parameters tab for `ronl:ParameterWaarde`: define income limits, asset thresholds, and percentages with notation, label, value, unit (`EUR`/`PCT`/`NUM`/etc.), description, and temporal validity dates. `schema:value` and `schema:unitCode` added.

---

### v1.0.x — Initial Release (October 2025)

**v1.0.2**

Bug fixes: BWB ID `c_` prefix stripping, TTL string escaping, URI encoding, filename sanitisation.

**v1.0.1**

TTL import: automatic parsing of CPSV-AP/CPRMV structures populates all form fields. Round-trip editing support. W3C Turtle specification compliance.

**v1.0.0**

Initial release. React + Tailwind CSS web application. Five-tab interface: Service, Organisation, Legal, Rules, Preview. Real-time TTL preview. CPSV-AP 3.0 and CPRMV 0.3.0 compliance. Azure Static Web Apps deployment at `ttl.open-regels.nl` with GitHub Actions CI/CD.

---

## Roadmap

### Completed

| Feature | Version |
|---|---|
| CPSV-AP 3.2.0 compliance | v1.4.0 |
| DMN integration (upload, deploy, test) | v1.5.0 |
| iKnow XML import | v1.5.0 |
| Full modularisation (−66% code) | v1.5.1 |
| RPP architecture visualisation | v1.5.1 |
| TriplyDB direct publishing | v1.6.0 |
| NL-SBB concept layer | v1.8.1 |
| DMN syntactic validation (5-layer) | v1.9.3 |
| CPRMV 0.4.1 + CPSV-AP 3.2.0 SHACL conformance | v1.10.0 |
| Pre-publish SHACL validation (advisory) | v1.10.0 |
| DSO → DMN deep-link import | v1.9.6 |
| Functional test-case verification (PASS/FAIL/ERROR) | v1.10.3 |
| Root-decision selection in multi-decision DMNs | v1.10.3 |
| Per-decision test routing & DMN-wide concept coverage | v1.10.4 |
| CPRMV version selector (0.4.1 / 0.3.2 export) | v1.10.5 |
| Rules-derived consolidation dates & unique rule URIs | v1.10.5 |
| Per-commit in-app changelog format | v1.10.7 |
| CalVer release versioning (`YYYY.MM.patch`) | v2026.07.0 |
| [Automated test suite](testing.md) (P0–P4, 257 tests) | v2026.07.0 |
| [Cell-level legislative grounding](cell-level-grounding.md) (Layers 1–3) | v2026.08.0 |
| Backend-mediated DMN deploy & evaluate | v2026.08.0 |

---

### Planned

**Phase B — RPP Deep Integration (2026 Q1–Q2)**

Cross-references between RPP layers: "This rule implements Policy X", "This parameter is used by Rules Y, Z". Traceability visualisation and impact analysis across the Rules–Policy–Parameters graph.

**Phase 2 — Extended CPSV-AP Support (2026 Q2)**

Add Channel (`cv:Channel`), Contact Points (`cv:ContactPoint`), Criteria requirements, and Evidence requirements to complete full CPSV-AP 3.2.0 coverage.

**Phase 3 — User Experience (2026 Q3)**

Multi-language support beyond Dutch with language-specific fields and translation workflows. Pre-configured service templates for common types (AOW, bijstand, WMO). Real-time collaborative editing with comments, change tracking, and review workflows. Browser `localStorage` auto-save with crash recovery.

**Phase 4 — Technical Enhancements (2026 Q4)**

Advisory pre-publish SHACL validation shipped in v1.10.0; next up is field-level error messages and real-time in-form compliance checking. Additional export formats: JSON-LD, RDF/XML, N-Triples, YAML. Git integration for service versioning and diff viewing.

**Phase 5 — Advanced Features (2027 Q1)**

Multi-service session management with service catalog, bulk operations, and cross-service references. Completeness scores, compliance metrics, and quality dashboards. Semantic search across services.

**Phase 6 — Enterprise Features (2027 Q2+)**

Automated regression testing and CI/CD integration for service definitions. User accounts, role-based access control, organisational workspaces, and audit logging.