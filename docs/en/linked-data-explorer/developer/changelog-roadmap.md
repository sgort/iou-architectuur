---
component: Linked Data Explorer
---

# Changelog & Roadmap

---

## Changelog

### v2026.08.9 — Changelog gains `ci` and `repo` scopes, and stops crashing on an unknown one (August 2026)

**Three entries in the previous release changed no deployable's code at all**, and the scope field offered only `frontend`, `backend` and `both` — so none of the three was true for them. Labelling any of it `both` would have told a reader that a release touching only `.github/` had changed application code. `ci` now covers pipeline and supply-chain work, mirroring the tag `ronl-business-api` already uses so both repositories label the same kind of work the same way; `repo` covers everything else that ships no application code — documentation, and the Operaton deploy bundles under `examples/` and `e2e-fixtures/`. Those bundles are worth distinguishing from a frontend change, because the frontend serves its own copies from `packages/frontend/public/examples/`, while the root directories are read only by the backend's tests and deployed to Operaton separately.

**An unrecognised scope would have taken the whole panel down.** The commit-type union had no `ci`, but unknown types fall back to `other`, so a `ci` entry rendered as a generic document icon — filing an entire supply-chain effort under "other" rather than crashing. `ScopeBadge` had no such fallback: `changelog.json` is imported as untyped JSON and cast at the module boundary, so TypeScript never checks the scope strings the data actually carries. An unrecognised one reached `SCOPE_BADGE[scope]`, yielded `undefined`, and would fail on `config.cls`. The type system cannot help here by construction, which is what makes the guard — not the types — the thing that made the new scope tags safe to introduce.

**The release command lands through a pull request.** Two steps of `/bump-release` were not merely out of date but impossible: it fast-forwarded `acc` locally and asked separately about pushing, and both halves are now rejected, because `acc` requires a pull request and a passing `audit`. It pushes the branch and opens a pull request instead — merging *is* the push. The merge method is called out explicitly, because both alternatives silently break the changelog entry that names every commit by SHA: squash collapses them into one new commit, and rebase replays them as new commits, preserving the count while replacing every hash. A new first step reconciles open Renovate pull requests, which rewrite `package-lock.json` — the same file a version bump edits.

---

### v2026.08.8 — Four advisories closed, and a formatter that reformatted five untouched files (August 2026)

**Twenty-three backend packages were brought up to date, of which exactly one carried an advisory**: `express` 4.18.2 → 4.22.2. The rest — `helmet`, `pg`, `winston`, `dotenv`, `cors`, `sparql-http-client` and the TypeScript, ESLint and Jest toolchain — are routine currency rather than security work, and are recorded as such rather than presented as advisory fixes.

**Three further advisories closed through the security fast-lane**, which clears the 14-day cooldown for known advisories — the one class of update that must not wait. `axios` ^1.6.5 → ^1.18.0 (lockfile 1.20.0), spanning fourteen minor releases and the widest jump in this release; `fast-xml-parser` ^5.3.5 → ^5.7.0 (lockfile 5.11.1); and `vite` ^6.2.0 → ^6.4.3. The split between a raised floor and a newer resolved version is `rangeStrategy: bump` working as intended: raise the range to the safe minimum, let the lockfile pin what is current.

**Only one of the three ran a full check.** The frontend workflow triggers on pull requests, so the `vite` update ran lint, tests and a preview deploy; the backend workflow triggers on push only, so the `axios` and `fast-xml-parser` updates had no pull-request check that said anything about whether a dependency had broken something. Both were verified against the full backend suite locally before merging. The same asymmetry meant `concurrently`'s branch was never rebased — it did not conflict — so the merge was trialled locally first and the lockfile checked with `npm ci`, because a clean textual merge of two lockfile diffs can still produce a file npm refuses.

**Prettier 3.9 reformatted five files nobody had touched.** It formats short union types on a single line where 3.7 produced the leading-pipe multiline style, so those five began failing `prettier --check` the moment the upgrade landed. No workflow runs `check-format` — the deploy workflows run lint and tests only — so nothing in CI reported it. The gate that catches this is the `pre-push` hook, which means the symptom would otherwise have been the next person's push failing on files they had never opened.

---

### v2026.08.7 — Supply-chain pinning enforced, and a silently inert Renovate (August 2026)

> Cross-repository detail: [Supply-chain gate](../../contributing/supply-chain.md).

**Nothing this pipeline downloads or executes may float.** All twenty action references across the six deployment workflows are now commit digests with their version in a trailing comment, and a `zizmor` gate refuses any pull request that reintroduces a floating tag. Findings go from **40 to 0**. Each workflow also gains the hardening zizmor was reporting: `persist-credentials: false` on checkout, explicit workflow and job permissions, and a `concurrency` group keyed on the pull-request number rather than the ref — because `github.ref` alone puts the `pull_request(closed)` teardown and the `push` deploy that a merge fires into one group, where they cancel each other at random.

**`renovate.json` supplies the other half of the policy**: a 14-day cooldown with `internalChecksFilter: strict`, cleared by `vulnerabilityAlerts` for known advisories, and dependencies grouped per workspace. `SECURITY-PIPELINE.md` records what is pinned and, more importantly, what is not — the `static-web-apps-deploy` Docker image behind four workflows, and the backend deploy step's lockfile-less `npm install`.

**Renovate had been opening nothing at all.** It validates strictly and rejects unknown options, so the five `"//"`-prefixed keys used as JSON comments were read as five invalid settings rather than ignored, and Renovate stopped raising pull requests as a precaution. That is correct behaviour from it — but it meant the half of the supply-chain policy that keeps pins current was inert from the moment it landed. Pins without updates decay into an unpatched tree, so a silently inert Renovate is precisely the failure the audit exists to prevent. Every comment moved to a `description` field, valid at the top level and inside any nested object; no policy changed, only the annotation style.

**The gate now validates the configuration too.** `renovate-config-validator` runs as a second step in the same `audit` job, so it is covered by the existing required status check and needs no ruleset change. It runs under `if: always()`, so a zizmor failure cannot hide a broken configuration behind it, and with no filename argument — passing one switches the validator into global-config mode, which applies different rules than the repository config this file actually is. `--strict` earned its place immediately: it fails on configuration Renovate would silently auto-migrate, which surfaced `baseBranches`, renamed upstream to `baseBranchPatterns` and therefore invisible on every previous run.

**The validator runs on the Node version Renovate requires.** `renovate@44.50.3` declares `engines.node ^24.11.0` while the runner defaults to Node 22, and npm accepts that mismatch with an `EBADENGINE` *warning* rather than refusing — so the validator had been running unsupported and still reporting green. `setup-node` is placed before the zizmor step rather than beside the validator it serves: a step following a failed one is skipped, so putting it after would leave the validator's `if: always()` running on whatever Node the runner defaulted to, precisely when zizmor had already failed and the logs were being read.

---

### v2026.08.6 — A ValidSign signature on the R2.1 phase exit (August 2026)

**One attribute is the switch for the whole signing feature.** `ronl:signatureRef="rip-pdp"` is added to `Task_AccorderenProjectplan4` — the *"Accorderen Projectplan 4. Uitgangspunten VO-fase"* task that closes R2.1. The RONL Business API resolves `ronl:signatureRef` on a user task and, when present, replaces that task's plain approval form with a ValidSign signing ceremony: the phase document is rendered from its deployed template, a signature package is created, and the Operaton task completes only once the signature lands.

**The parity test had been failing since that commit.** `RipR21Process.bpmn` exists in two places the test locks together byte for byte — `examples/organizations/flevoland/rip-phase-21/` is the authored source, `e2e-fixtures/flevoland/` the mirror — and the attribute had been added to the mirror only. Because the backend deploy workflow triggers on push and not on pull requests, no pull request runs these tests: the failure would have surfaced on `acc` after merge, where `npm test` gates the deploy step, leaving a red acceptance branch and no deployment. The `xmlns:ronl` namespace was already declared in both files and the byte delta was exactly the length of the attribute, so the repair adds one attribute rather than reflowing the document.

---

### v2026.08.5 — The R2.2 VO bundle, and a parity test that locks each bundle's two copies together (August 2026)

> Bundle contents and deployment: [RIP R2.2 VO Bundle](../features/rip-r22-bundle.md).

**`RipR22Process` picks up where R2.1's "Fase 1 voltooid → R2.2" end event left off** — four lanes and nine user tasks, from `R2_2 - VO.pdf` (rev. 21-11-2024). All five branches of the opening parallel split rejoin the join gateway. The source PDF does not draw it that way: it shows *Inventariseren kabels en leidingen* and *Aanvragen raamvergunning* leaving the pool into CO1 and JU3.5 and never returning, which as control flow deadlocks at the join. Those hand-offs are `textAnnotation`s instead, because CO1 and JU3.5 do not exist as fixtures and a `callActivity` would dangle at deploy time and fail the manifest's `calledElement` test. They are referenced by several phases and belong in a shared bundle of their own.

**Nine forms and five document templates complete the bundle.** One form per user task, bound by `camunda:formRef`, with field types kept inside the eight the R2.1 bundle already uses, since nothing else is exercised against this Camunda 7.21 stack. One template per green *"Format …"* box in the specification — KES, Ontwerptoelichting, Objectenboom, Bevindingenformulier and Hoeveelheidsbepaling — because a Format in the diagram and a `.document` here are the same thing: a template with bindings. The blue outputs beside them in the spec are instances of these templates rather than artifacts of their own. Their zone keys are `signOff` and `contactInformation` from the start, unlike R2.1's templates, which shipped with `signoff` and `contactInfo` — keys `DocumentZones` never declares, leaving their signature blocks unrendered until v2026.08.4 repaired them.

**The templates would have imported and attached to nothing.** R2.1 wires each document template to the task that produces it with `ronl:documentRef` — the attribute `DocumentTemplateSelector` writes and `BpmnCanvas` reads to render the document badge on a task. The R2.2 specification never mentioned it, so the process shipped without it. The attribute is single-valued, so a task carries at most one template, and four of the five bind. `rip-objectenboom` stays unattached deliberately: `Task_OpstellenConceptVO` produces both the Ontwerptoelichting and the Objectenboom, and its one slot went to the Ontwerptoelichting. The Objectenboom still ships and imports normally — it simply carries no task badge, and its reference is maintained in Relatics instead.

**Each bundle now exists twice on disk, and a test keeps the copies identical.** Authored under `examples/`, imported and deployed from `e2e-fixtures/` — with nothing stopping the two drifting, and they had: v2026.08.4 repaired the document zone keys in the `e2e-fixtures` copies only, and the `examples` copies kept the dead keys until they were re-pasted by hand. A new test asserts every file in a mirrored bundle is byte-identical to its twin; new bundles opt in by adding an entry to `MIRRORED_BUNDLES`.

**`rip-phase1-swimlanes` is renamed to `rip-phase-21`.** The `-swimlanes` suffix distinguished the bundle from a competing `rip-phase1/` draft that has since been deleted, so it distinguished nothing, and the directory name no longer matched the process it holds. `rip-phase-21/` holds `RipR21Process` and `rip-phase-22/` holds `RipR22Process`, which makes the two obvious siblings. Contents are untouched, and exactly one reference to the old path existed — the `source` field of the `RipR21Process` entry in `e2e-fixtures/manifest.json`. Nothing resolves this directory at runtime: the application serves examples from `packages/frontend/public/examples/`, which has never held the RIP bundles.

---

### v2026.08.4 — Signature blocks that had never rendered, and the DSO API surface documented (August 2026)

**Two defects had shipped with every deployment of the three RIP document templates.** The templates used `signoff` and `contactInfo` where `DocumentZones` declares `signOff` and `contactInformation`; `DocumentCanvas` iterates `ZONE_ORDER` and calls `getZoneBlocks('signOff')`, so the lowercase key meant the Signatures block was dropped silently — the three signature lines in these templates had never rendered at all. They also declared `processKey: "RipPhase1Process"` while the BPMN they deploy with declares `RipR21Process`, which is also the key the fixture manifest lists them under. The authored `examples/` copies were brought back in line with the `e2e-fixtures/` mirror ahead of the parity test that would later enforce it mechanically.

**The DSO Viewer's full API surface was written down**, mapping each viewer feature to the upstream API behind it — Stelselcatalogus v3 for concepts, RTR Gegevens v2 for activities, Zoekinterface v2 for werkzaamheden search, Opvragen Werkzaamheden v1 for werkzaamheid detail, and Toepasbare Regels Uitvoeren Gegevens v1 for rule metadata — together with the call path per feature, a complete endpoint map, pre- and production base URLs, and the transport conventions. That material is already reflected on [DSO integration](../features/dso-integration.md) and [API reference](../reference/api-reference.md).

**The Activity Detail panel's child fan-out was recorded as the viewer's heaviest interaction.** The RTR returns `onderliggendeActiviteiten` as bare HAL hrefs with no `omschrijving`, so the panel fires one extra activity-detail request per child, in parallel, purely to resolve names: opening a single activity costs 1 + N upstream calls, and 24 for an activity with 23 children. There is no cache and no concurrency cap, which makes it the first candidate for memoisation.

---

### v2026.08.3 — A test gate, and two defects it did not catch (August 2026)

> Full inventory, commands and coverage: [Testing](testing.md).

**Every deploy now runs the suites, and a failure blocks the deploy.** None of the six Azure workflows previously ran a test step. That was a deliberate P7 decision taken when backend coverage was first measured at 13.82% statements — gating on a number that low would have been theatre — and it was recorded as conditional on backend breadth improving. v2026.08.2 took the backend from 16.79% to 98.06%, meeting the condition. The backend workflows already installed and linted, so a Jest step slots in beside the existing lint; the frontend workflows had no npm steps at all, because the Static Web Apps action builds inside its own container and runs none of this repository's scripts, and they gain an explicit install, lint and test sequence ahead of the deploy action. The two `ropa-site` workflows are deliberately untouched — that package is a static `index.html` with no build and no tests.

**E2E fixture BPMNs were undeployable, and nothing caught it.** BPMN 2.0's `tProcess` is an ordered sequence — `laneSet*`, `flowElement*`, `artifact*`, … — so once an artifact appears, no further flow element may follow. The commit that added the on-canvas "E2E FIXTURE" warning inserted its `textAnnotation` and `association` directly after the first flow element, leaving four of the five fixtures rejected by Operaton's XSD validation on deploy. `TreeFellingPermitSubProcessE2E` was the one file with the banner correctly at the end, and the only one that deployed. Each banner moved to just before `</bpmn:process>`; all five now validate against `bpmn-moddle`'s `BPMN20.xsd`. The manifest integrity test checked file existence, process ids and `calledElement` references but never whether the BPMN would deploy — it now asserts the ordering rule directly.

**The BPMN deploy dialog sent the wrong process key for every model.** `doc.querySelector('process')` is a CSS *type* selector, which matches only the null namespace, so it never found the `<bpmn:process>` element that real bpmn-js output always emits. All four call sites fell through to their own fallbacks: deployments posted the literal string `"process"` instead of the model's id, and sub-process lookups by `calledElement` never matched. A `findProcessElement` helper now matches on local name across namespaces. The test covering this had asserted the fallback as correct, blaming a jsdom quirk — half right, since its fixture declared none of the prefixes it used, so `DOMParser` rejected the document outright and returned a `<parsererror>` in which nothing was findable, masking the real defect underneath.

**The error overlay is reachable from the view that raises it.** It lived inside `App`'s right panel, which is hidden whenever `viewMode` is Orchestration — the only view from which Refresh Cache can be triggered. A failed cache clear set the error state correctly and had nowhere to render, staying silent until the user happened to navigate elsewhere, where a stale error then appeared out of context. The overlay is now a direct child of the workspace container and renders in every view.

---

### v2026.08.2 — DMN deploy/evaluate proxies & ten dead validation rules (August 2026)

**v2026.08.2 — Feature & Patch (August 18, 2026)**

- **`POST /v1/dmns/deploy`** deploys raw DMN XML ad hoc, without requiring a pre-registered LDE norm identifier — built for the CPSV Editor's DMN tab, which holds an uploaded or generated file with no registry entry of its own. A thin wrapper around the proven `operatonService.deployDrd()`.
- **`POST /v1/dmns/evaluate/:decisionKey`** proxies an evaluate call server-side. Both routes exist for the same reason: the CPSV Editor called Operaton directly from the browser, which CORS blocks for a local dev origin. The evaluate proxy forwards Operaton's response **byte-for-byte and status-for-status** — the raw success array or exception object, *not* the usual `{success, data, error}` envelope — because the DMN tab reads Operaton's own JSON. A new `evaluateRaw()` passes variables straight through, skipping the type inference `evaluateDecision()` does for its different caller contract, which would otherwise double-wrap an already Operaton-shaped body. See [API Reference](../reference/api-reference.md#post-v1dmnsdeploy) and the CPSV Editor's [DMN Implementation](../../cpsv-editor/developer/dmn-implementation.md#operaton-calls-go-through-the-backend-v2026080).
- **Ten CPRMV validation rules were dead code and had been since the file was written.** `cprmvAttr()`'s primary lookup called `el.attr({ name, ns })`, which in libxmljs2 0.37 is the *setter* overload, not a namespaced getter: it sets attributes literally named `name` and `ns` on the element and returns a value with no `.value()`, so the call threw. The function's own `try`/`catch` swallowed the throw and returned `null`, so the working `attrs()` fallback beneath it was never reached. `EXEC-002`–`EXEC-010` and `CON-001`–`CON-003` therefore **never fired for any DMN, while the validator reported a clean result** — and every inspected element was mutated with two junk attributes. Dropping the object-form fast path is the whole fix. See [DMN Validation Reference](../reference/dmn-validation-reference.md).
- `CPRMV_NS` was additionally hardcoded to the legacy `cprmv.open-regels.nl/0.3.0/` namespace, so a DMN using the current `standaarden.open-regels.nl/standards/cprmv/0.4.1#` namespace short-circuited on an `EXEC-001` *"CPRMV not declared"* before reaching any check. `CPRMV_NAMESPACES` now accepts both.
- New **`EXEC-011`/`EXEC-012`** validate cell-level `dct:source` / `cprmv:isBasedOn` format on grounded DMN cells — the [cell-level grounding](../../cpsv-editor/developer/cell-level-grounding.md) the CPSV Editor now emits — and **`EXEC-013`** closes a pre-existing gap where `cprmv:extends`' format was never checked at all.
- `INT-007` false-positive fix: `FEEL_RESERVED` carried the singular `year`/`month`/`day`/… for the single-word built-ins but not the plural `years`/`months`, which are the leading words of the `years and months duration(...)` built-in's own name. Those words aren't preceded by a dot, so only the reserved-word check catches them. Reproduced live against `HvA_full_dmn_export-patched.dmn`: 12 warnings across 6 decisions, all false positives from this one construct.
- **BPMN shell/subprocess matching now keys on `shellId`, not `bpmnProcessId` alone.** Once a shell is deliberately duplicated — an e2e-fixtures copy keeps the same `bpmn:process` id, since that is the real production Operaton key — the catalog rendered every subprocess under *every* shell sharing that id. `shellId` (the parent shell's own local record id) is now stored alongside `calledElement`, with a fallback to the old match for records saved earlier.
- That fix did not survive a remount until the data actually reached the database: `hydrateFromServer()` treats the Postgres list as authoritative and replaces local state on every `BpmnModeler` mount. `process_definitions.status` had `CHECK (status IN ('example','wip'))` with no `'e2e'`, so saving an e2e process violated the constraint and failed **silently** (`fetch()` does not reject on non-2xx), and `shell_id` was not in the schema, upsert or list query at all. Adds `shell_id` (additive, idempotent) and widens the `status` CHECK.
- New **E2E status badge** for imported e2e-fixtures forms and documents, detected at import from a self-describing marker in each fixture. A shared `StatusBadge` component replaces three near-identical inline badge blocks across `ProcessList`, `FormList` and `DocumentList`. The badge is orange — indigo read too close to EXAMPLE's blue.
- Seed versions bumped for `example_tree_felling`, `example_zorgtoeslag_provisional` and `example_zorgtoeslag_final` so existing users' copies actually receive `shellId`; without the `EXAMPLE_VERSIONS` bump, `seed()` skipped re-saving them and both stores kept the `shellId`-less copy.
- **Backend statement coverage raised from 16.79% to 98.06%** (branches 18.10% → 89.18%) by adding 31 test files and extending 3, with no production code changed. This is the campaign that *found* the `cprmvAttr()` defect above — documented first as a testing-scope decision, fixed two commits later. Line endings normalised to LF via `.gitattributes`, closing a loop where a Windows checkout produced CRLF files that `format:check` rejected and Git kept renormalising back. See [Testing](testing.md).

**Files:** `packages/backend/src/routes` (`/v1/dmns`), `packages/backend/src/services` (`operaton.service.ts`, `dmn-validation.service.ts`), `packages/backend/src/db`, `packages/frontend/src/components` (`BpmnModeler`, `StatusBadge`)

---

### v2026.08.1 — Mandatory deploy organization & the e2e-fixtures bundle (August 2026)

**v2026.08.1 — Feature (August 14, 2026)**

- **Organization is now mandatory when deploying a BPMN process.** The Deploy action will not submit without one, and sends it to Operaton as its native tenant-id (`POST /deployment/create`'s `tenant-id` field) — closing the gap where a process could deploy with no tenant-id at all, invisible to any tenant-scoped lookup an application later makes against it.
- **Shared DMN decisions resolve as untenanted from tenant-scoped business-rule-tasks.** Confirmed empirically against a live Operaton instance: a business-rule-task's `camunda:decisionRef` resolves against a decision definition under the *exact same* tenant-id as the calling process instance, with **no fallback** to a shared untenanted decision even when one exists. `camunda:decisionRefTenantId` can override this, but only as an EL expression evaluating to null (`${null}`) — a literal empty string is silently ignored. Applied to all 7 business-rule-tasks across the 4 fixture BPMNs that reference genuinely tenant-agnostic regulatory logic.
- A new `e2e-fixtures/<tenant>/` directory with a `manifest.json` and an integrity test becomes the single source of truth for the RONL Business API's E2E suite, replacing two pre-existing and already-diverged "examples" locations.
- The e2e sub-processes were renamed (`TreeFellingPermitSubProcessE2E`, `ZorgtoeslagProvisionalSubProcessE2E`) so LDE's own catalog stops conflating the fixture copy with the seeded-example copy of the same sub-process — previously both shared a `bpmn:process` id, so importing the fixture could silently reuse the example's stale content.
- Fixed a fixture that Operaton's BPMN parser rejected (`ENGINE-09005`): a `textAnnotation`/`association` pair immediately preceding the file's first `businessRuleTask`. Every other fixture has a `scriptTask` in that position, which validates fine, so this adjacency had never been parsed for real. Moving the annotation to the end of the process body is also the more conventional placement.
- Fixed a copy-pasted `processKey` on the Zorgtoeslag provisional document template, and nested each sub-process fixture under its shell's `subProcesses` array rather than listing it as a flat sibling.

**Files:** `packages/frontend/src/components/BpmnModeler`, `e2e-fixtures/`

---

### v2026.08.0 — Ede and Gelderland location presets (August 2026)

**v2026.08.0 — Feature (August 6, 2026)**

- The DSO Viewer's Activities tab gains the municipality of **Ede** and the province of **Gelderland** alongside the existing Lelystad and Flevoland presets. One array drives both the location filter buttons and the authority-name lookup used when importing forms, so no other change was needed.
- OINs were sourced from overheid.nl's Identificatiecodes records and cross-checked structurally — each OIN embeds the organisation's own RSIN, and both new values follow the same `00000001<RSIN>000` pattern as the existing entries.

**Files:** `packages/frontend/src/components/DsoExplorer`

---

### v2026.07.1 — DMN validator: missing-id deploy failures and FEEL false positives (July 2026)

**v2026.07.1 — Patch (July 23, 2026)**

- Adds **`BIZ-010` through `BIZ-014`**, flagging `<input>`, `<output>`, `<rule>`, `<inputEntry>` and `<outputEntry>` elements missing the `id` attribute as **errors**. Operaton's DMN transformer requires `id` on these decision-table clause elements even though the DMN 1.3 XSD marks it optional, and rejects such files with `DMN-02011` at deploy time — a class of failure this validator previously reported as fully valid.
- Fixes two `INT-007` false-positive sources. FEEL names may legally contain spaces, and a bare `<inputExpression>` that is itself one multi-word declared name was being shredded word-by-word by the identifier tokenizer, with every word flagged as an unresolved variable; a whole-string match against declared and produced names is now tried first, falling back to tokenization. Separately, `FEEL_RESERVED` was missing the single-word FEEL date/time component functions (`year`, `month`, `day`, `hour`, `minute`, `second`), so a `year(...)` call flagged `year` itself as unresolved.
- Found while debugging an Amsterdam DMN's Operaton deploy failure in the CPSV Editor repository; together the fixes cut that file's Interaction Rules warnings from **83 to 12**. The residual 12 — multi-word names embedded inside compound expressions, plus one likely real DRD-wiring gap in the source — are documented as open issues rather than fixed, since closing them properly needs a materially larger longest-match tokenizer change.

**Files:** `packages/backend/src/services/dmn-validation.service.ts`

---

### v2026.07.0 — Test suite (P0–P6.8), CalVer, and a coverage baseline (July 2026)

**v2026.07.0 — Infrastructure (July 22, 2026)**

- A phased test suite lands across both packages, taking the repository from **zero test files** — `npm test` exited 1 with *"No tests found"* — to full-stack coverage. Backend P0–P3 covered utilities, errors and middleware, the ropa/vendor/assets services, and the five smallest routes with supertest. Frontend P4–P6.8 bootstrapped Vitest and covered pure-logic utils, the 11-module service layer with `msw`, then every component directory in coupling-severity order: no third-party coupling first, then `@dnd-kit`, then one embedded editor library, then two, with the top-level integration components last. See [Testing](testing.md).
- **P7 measured real coverage and deliberately deferred CI wiring.** At the time: 109 backend tests at 13.82% statements, against 557 frontend tests at 74.03%. No CI test step was added to the Azure workflows, blocking or non-blocking, because the backend gap was *breadth* — whole route and service files never touched — rather than depth. The condition for revisiting it is recorded: once backend breadth improves, or the team accepts breadth alone as a gate. (Backend breadth was subsequently closed in v2026.08.2; the CI step remains deferred.)
- Two real pre-existing tooling gaps surfaced and were fixed, both latent only because the repository had no test files: `tsconfig.eslint.json` extended `tsconfig.json` without overriding its `exclude` of `**/*.test.ts`, so ESLint's type-aware parser could not see any test file; and `.gitignore`'s blanket `*.js` rule, meant for compiled output, silently blocked `jest.config.js` from ever being tracked.
- **Release versions switch to CalVer** (`YYYY.MM.patch`), matching the CPSV Editor. The sequence is product-wide rather than per-scope, so a backend-only and a frontend-only release still share the next number. Historical SemVer entries are left as they are.
- Local development now points at the `ronl-operaton` container from the RONL Business API stack (`localhost:8081`) instead of the remote instance, and `docker:check` verifies it alongside `ronl-postgres`.

**Files:** `packages/backend` (Jest), `packages/frontend` (Vitest, RTL, msw), root `package.json`

---

### v1.9.13 — Per-commit changelog format (July 2026)

**v1.9.13 — Enhancement (July 22, 2026)**

- The in-app Changelog renders `"format": "commits"` entries — an icon-and-colour header per commit, an sha/author trailer, a scope badge and an Upcoming/Released status badge — alongside the existing `"sections"` shape, adopting the same convention as the RONL Business API and the CPSV Editor. Legacy entries render exactly as before.
- A repo-local release command is now tracked with the repository, tailored to this real npm-workspaces monorepo: frontend/backend scope, no endpoint-map reconciliation step (the route registry is already a self-maintaining single source of truth), and a note that `packages/ropa-site` has no `package.json` and is never version-bumped even though it deploys via its own path filter.

**Files:** `packages/frontend/src/components/Changelog.tsx`

---

### v1.9.12 — Query library resolves CPRMV 0.4.1 datasets (July 2026)

**v1.9.12 — Patch (July 9, 2026)**

- *Rules with Their Services*, *Count Rules per Service* and *Services with All Their Rules (Detailed)* joined `?rule cpsv:implements ?service` directly. Since the CPSV-AP RuleShape change, a `cpsv:Rule`'s `cpsv:implements` points at an `eli:LegalResource` — the resource the service declares via `cv:hasLegalResource` — so datasets published in the newer shape returned **no rules at all**. The queries now UNION over both link paths.
- *NL-SBB Concepts and Services* broke at the variable-to-DMN hop: a concept's `dct:subject` points at a bare DMN variable URI (`<dmnUri>/input/N`) that newer exports emit without a `cpsv:isRequiredBy` / `cpsv:produces` edge, so the concept could not reach its DMN or service. The query keeps the explicit edge for older data and, when absent, derives the DMN URI from the variable URI.
- Auto-generated DMN decision rules (placeholder *"Decision rule &lt;id&gt;"* titles) are filtered out of rule listings, and `SELECT DISTINCT` de-duplicates. For the Flevoland Thuisbatterij dataset this surfaces its 3 business rules — previously hidden entirely — and 21 concepts, while dropping roughly 60 placeholder rows across the catalogue.

**Files:** `packages/frontend/src/utils` (sample query library)

---

### v1.9.11 — Board-owner deploy fix & Operaton error surfacing (July 2026)

**v1.9.11 — Patch (July 2, 2026)**

- Fixed `boardOwner` injection breaking BPMN deploys whose `<bpmn:process>` carries a `<bpmn:documentation>` child. `injectBoardOwner` now skips past any leading `<documentation>` element(s) before inserting or locating `extensionElements`, preserving valid BPMN schema order (documentation must precede extensionElements).
- Deploy failures now surface Operaton's real error: the deployment service captures and logs the response body (`operatonResponse` / `operatonStatus`) instead of only the generic Axios message, and `getErrorDetails()` now checks `isAxiosError` **before** the generic `Error` branch — previously dead code, since `AxiosError extends Error` always matched the generic branch first and silently discarded `response.data`.

**Files:** `packages/backend/src/services` (deployment / BPMN board-owner injection)

---

### v1.9.10 — `/v1/norms` CPRMV version selector (June 2026)

**v1.9.10 — Feature (June 30, 2026)**

- A new `?cprmv_version=` query parameter on `/v1/norms` selects which CPRMV vocabulary version to query and emit — one of `0.3.0`, `0.3.2`, or `0.4.1` (else `400 INVALID_PARAM`), defaulting to `0.3.0`. All three carry flat `cprmv:Rule` resources with identical predicates, so the rules query is one shape with the namespace swapped; `0.3.0`/`0.3.2` bind `cprmv:` to the `cprmv.open-regels` versioned-path IRI, `0.4.1` to the `standaarden.open-regels` `0.4.1#` IRI.
- Per-ruleset metadata (`dataset_versions`) differs by version: `0.3.x` reads `cprmv:Dataset` (`dct:issued` + `dcat:version`); `0.4.1` has no `cprmv:Dataset` and reads `cprmv:RuleSet` (`cprmv:validFrom`, which doubles as the ETag / `Last-Modified` freshness signal since `0.4.1` has no `dct:issued`).
- This is the LDE consumer side of the CPSV editor's [CPRMV version selector](../../cpsv-editor/features/import-export.md#cprmv-vocabulary-version-041-032). Full detail: [Backend — `/v1/norms`](backend.md#norms) and the [API Stability Contract](../reference/api-stability.md) (`0.3.2` / `0.4.1` are experimental, `0.3.0` is the stable default).

**Files:** `packages/backend/src/services/sparql.service.ts`, `packages/backend/src/routes` (`/v1/norms`)

---

### v1.9.9 — Deploy-time board ownership & RIP leadRole (June 2026)

**v1.9.9 — Feature (June 22, 2026)**

- **Process board ownership.** The Deploy modal now requires a board owner: a new "Board ownership" section auto-detects the board from the process's candidate groups (infra/rip → Infra-board, caseworker/hr → Caseworker) and lets you override it. Deployed BPMN is stamped with a process-level `camunda:property boardOwner` (explicit choice or auto-derived). `boardOwner` is persisted on the `process_definitions` record (new `board_owner` column) and exposed via `/bundles/public`, so downstream consumers (ronl-business-api Procesbibliotheek and archive split) can read it.
- **RIP Phase 1 leadRole.** The Map-role outputs script now sets a `leadRole` process variable, derived from the intake `projectType` (contractbeheer → `manager-pb`, otherwise `projectleider`). Distinct from the task `candidateGroups`: `leadRole` names who owns the project in the portfolio, not who can claim its tasks.

**Files:** `packages/frontend/src/components` (Deploy modal), `packages/backend/src/services` (deployment, `process_definitions`, `/bundles/public`)

---

### v1.9.8 — CPRMV SHACL: ParameterWaarde & TemporalRule shapes (June 2026)

**v1.9.8 — Feature (June 17, 2026)**

- Added `cprmv:ParameterWaardeShape` targeting `cprmv:ParameterWaarde`: `skos:notation` [1,1] `xsd:string` and `skos:prefLabel` [1,n] `rdf:langString` are **mandatory**; `schema:value` [0,1] `xsd:decimal`, `schema:unitCode` [0,1] `xsd:string`, `dct:description` [0,1] `rdf:langString`, and `cprmv:validFrom`/`validUntil` [0,1] `xsd:date` are optional.
- Added `cprmv:TemporalRuleShape` targeting `cprmv:TemporalRule`: `cprmv:validFrom` [0,1] `xsd:date`, `cprmv:validUntil` [0,1] `xsd:date`, `cprmv:confidenceLevel` [0,1] `xsd:string`, and `cprmv:isBasedOn` [0,n] `sh:class cpsv:Rule` — all optional.
- Also adds the `skos:`, `schema:`, and `dct:` `@prefix` declarations the new shapes require; no changes to existing shapes. (The CPSV editor enforces the `ParameterWaardeShape` client-side as of its v1.10.4.)

**Files:** CPRMV SHACL shapes (`cprmv` custom layer)

---

### v1.9.7 — SHACL display fixes (June 2026)

**v1.9.7 — Patch (June 15, 2026)**

- SHACL Validator: long issue messages and focus-node locations were truncated with a single-line CSS ellipsis and could not be read. They now wrap in full (`break-words` / `break-all`) and expose the complete text on hover (title tooltip).
- SHACL backend: removed the 60-character cap on the offending values reported for cardinality (`maxCount` / `uniqueLang`) violations, so the full value appears in the message.

**Files:** `packages/frontend/src/components/ShaclValidator.tsx`, `packages/backend/src/services/shacl-validation.service.ts`

---

### v1.9.6 — CPRMV 0.4.1 DMN discovery + chain fixes (June 2026)

**v1.9.6 — Patch (June 13, 2026)**

- DMNs published under the new CPRMV 0.4.1 namespace (e.g. `vast_bedrag_op_vestiging`) were missing from `/v1/dmns` and the ChainBuilder DMN picker — `getAllDmns` and the chain-link queries only matched `cprmv:DecisionModel` under the old 0.3.0 namespace. Both namespaces are now matched side by side until existing 0.3.0 data is migrated.
- Fixed "Fill with test data" in the ChainBuilder input form not visibly filling Integer/Double fields when the RDF-sourced test value is `0` (the input rendered empty because `0 || '' === ''`).

**Files:** `packages/backend/src/services/sparql.service.ts`, `packages/frontend/src/components` (ChainBuilder)

---

### v1.9.5 — DSO deploy-ready DMN + SHACL CPRMV layer (June 2026)

**v1.9.5 — Minor (June 11, 2026)**

- **DSO Integration:** extracted DSO DMNs now carry `camunda:historyTimeToLive`, so they deploy to Operaton exactly as handed off — the consumer no longer has to patch the DMN first. LDE now produces a fully deploy-ready and evaluatable DMN (DMN 1.3, input ids, FEEL-safe variable names, output `typeRef`s, history TTL). Forms imported from DSO show a green **DSO** badge in the Form Editor list instead of the generic yellow WIP badge.
- **SHACL Validator:** a third **CPRMV 0.4.1** shape layer now validates uploaded Turtle alongside CPSV-AP 3.2.0 and RONL Custom; the results panel renders it automatically. Added valid/invalid test fixtures for every layer (CPRMV, CPSV-AP, RONL) plus a malformed-Turtle case.

**Files:** `packages/backend/src/services/shacl-validation.service.ts`, `packages/backend/shapes/cprmv/**`, `packages/backend/src/services/dso.service.ts`, `packages/frontend/src/components/DsoExplorer.tsx`, `packages/frontend/src/components/FormEditor.tsx`

---

### v1.9.4 — DSO Phase 2d + DMN publish handoff (June 2026)

**v1.9.4 — Minor (June 10, 2026)**

- **Activities tab name search:** fixing a location (Lelystad / Flevoland) loads that authority's full activity set in one call and reveals a search box that live-filters by name.
- **↓ Import into LDE** (Indieningsvereisten) saves the generated form-js scaffold straight into the Form Editor as a draft, named after the activity and tagged with the readable authority name (falling back to the RTR code).
- **Publish via CPSV Editor** (Conclusie) opens the CPSV Editor with a deep-link to publish the extracted DMN to TriplyDB, where the LDE DMN picker can consume it — no local DMN store needed.
- Extracted DMNs are normalized to deploy and evaluate on Operaton (DMN 1.2 → 1.3, missing input ids added, FEEL-safe variable names, explicit output `typeRef`). Verified end-to-end: the normalized `HoutopstandVellen` decision deploys (all 7 decisions) and the root decision evaluates without the previous FEEL error.

**Files:** `packages/backend/src/routes/dso.routes.ts`, `packages/backend/src/services/dso.service.ts`, `packages/frontend/src/components/DsoExplorer.tsx`

---

### v1.9.3 — DSO Phase 2a + 4 (June 2026)

**v1.9.3 — Minor (June 9, 2026)**

- Activity Detail panel now shows an **Applicable Rules** section listing *toepasbare regels* fetched live from the DSO Uitvoeren Gegevens API, grouped by rule type (Conclusie / Indieningsvereisten) with validity date and STTR version.
- **↓ STTR** downloads the raw STTR XML for any rule type; **↓ Extract DMN** (Conclusie) extracts the embedded DMN decision table as a standalone `.dmn`; **↓ Form scaffold** (Indieningsvereisten) generates a form-js JSON scaffold from the STTR questionnaire (boolean → checkbox, list → select, number → number field, attachment → labelled textfield).
- Added `ronl:dsoActiviteitUrn` on `TreeFellingPermitSubProcess` linking it to `nl.imow-gm0995.activiteit.HoutopstandVellen` (Gemeente Lelystad).

**Files:** `packages/backend/src/routes/dso.routes.ts` (`/toepasbare-regels`, `/toepasbare-regels/:id/sttr`, `/toepasbare-regels/:id/dmn`, `/toepasbare-regels/:id/form-scaffold`), `packages/backend/src/services/dso.service.ts`, `packages/frontend/src/components/DsoExplorer.tsx`

---

### v1.9.2 — BPMN shell/subprocess auto-linking (June 2026)

**v1.9.2 — Patch (June 9, 2026)**

- Uploaded BPMN processes that form a shell/subprocess pair are now automatically linked: a process with call-activity elements is classified as a *shell*, and any process whose BPMN process ID is targeted by a shell's call-activity becomes its *subprocess*. The relationship is detected both on fresh imports and retroactively on startup, so previously uploaded standalone processes are reclassified without a re-upload.
- Removed two unused TypeScript imports (`DsoWerkzaamheid`, `zoekActiviteiten`) in `DsoExplorer`.

**Files:** `packages/frontend/src/components/BpmnModeler` (process classification), `packages/frontend/src/components/DsoExplorer.tsx`

---

### v1.9.0–v1.9.1 — SHACL Validator (June 2026)

**v1.9.0 — Minor (June 4, 2026) · v1.9.1 — Patch (June 5, 2026)**

A new **SHACL Validator** view validates CPSV-AP Turtle against the canonical CPSV-AP 3.2.0 shapes and RONL-authored shapes before publishing to TriplyDB.

- New backend endpoints `POST /v1/shacl/validate` (file-local) and `POST /v1/shacl/validate-merged` (unions the file with the already-published graph via a read-only SPARQL `CONSTRUCT` before validating).
- Two result layers: **CPSV-AP 3.2.0** (the SEMIC shapes vendored verbatim — 32 shapes) and **RONL Custom** (at most one `foaf:homepage`/`dct:identifier`/`cv:spatial` per organisation; one `dct:title`/`dct:description` per language on a rule).
- v1.9.1 vendored the canonical CPSV-AP file and collapsed the earlier Core/Vocabularies split into a single CPSV-AP layer, added the **Not loaded vs OK** distinction, capped offending values at 60 characters, and added a conformant example plus deterministic merge-simulated test coverage.

**Files:** `packages/backend/src/services/shacl-validation.service.ts`, `packages/backend/src/routes/shacl.routes.ts`, `packages/backend/src/types/shacl-rdf.d.ts`, `packages/backend/shapes/**`, `packages/frontend/src/components/ShaclValidator.tsx`

---

### v1.8.2 — DMN XML download (May 2026)

**v1.8.2 — Patch (May 20, 2026)**

- New endpoint `GET /v1/dmns/:identifier/xml` streams the deployed DMN XML from Operaton as `<identifier>.dmn` with the correct `Content-Type` and `Content-Disposition` headers.
- DMN list and detail responses now include an `xmlUrl` field pointing to the download endpoint, making it self-discoverable.
- Backward compatible: the legacy `GET /api/dmns/:definitionKey/xml` route remains available.

**Files:** `packages/backend/src/routes/dmn.routes.ts`, `packages/frontend/src/types` (`DmnModel`)

---

### v1.8.1 — DMN validator: INT-007 false positives eliminated (May 2026)

**v1.8.1 — Patch (May 19, 2026)**

The Interaction Rules layer no longer flags valid intra-DRD references, and now parses FEEL expressions instead of matching the whole `<inputExpression>` text.

#### `requiredDecision` targets resolved

An `<inputExpression>` may legitimately reference a value produced by another decision wired in via `<informationRequirement><requiredDecision>` — that name is the producing decision's `<variable name>` or `<decisionTable>` `<output name>`, never an `<inputData>`. INT-007 now resolves `requiredDecision` targets and treats their output variables as satisfied, mirroring the `requiredInput` → `inputData` resolution INT-001 already performs.

#### FEEL expressions parsed, not whole-text matched

Previously the entire `<inputExpression><text>` was treated as one variable name, so `date and time(aanvraagDatum)` demanded an `<inputData name="date and time(aanvraagDatum)">` and any operator expression false-fired. A new shared `extractFeelIdentifiers()` helper strips string literals, unwraps built-in calls (`date(...)`, `date and time(...)`, `number(...)`, `string(...)`, `not(...)`, …), drops FEEL keywords/operators and qualified-name segments after a dot, and checks each referenced identifier individually.

#### Decision outputs excluded from the input-contract check

Output variable names (decision `<variable>` and decision-table `<output name>`) are, by construction, never external inputs and are no longer subject to the must-have-matching-`inputData` requirement. Genuine gaps still raise INT-007 — now naming the specific identifier rather than the raw expression string.

#### No API change

`POST /v1/dmns/validate` is unchanged; only the interaction-layer issue set for affected files differs (fewer false-positive warnings). Verified against real DMNs that deploy and evaluate on Operaton: `RONL_Heusden_Heusdenpas.dmn`, `RONL_SVB_Leeftijden.dmn`, `EmployeeRoleAssignment.dmn`, `tree-felling-decision.dmn`, and `replacement-tree-decision.dmn` all validate clean; backend `tsc --noEmit` passes.

**Files:** `packages/backend/src/services/dmn-validation.service.ts`

---

### v1.8.0 — Concurrent applicable periods per ruleset (May 2026)

**v1.8.0 — Minor (May 15, 2026)**

#### `dataset_versions` becomes a list per rulesetid

A single BWB ruleset can have multiple `cprmv:Dataset` records — different applicable periods of the same law (e.g. the `2025-01-01` and `2026-01-01` editions of the Participatiewet) are **concurrent and equally authoritative**, not competing versions. The v1.7.0 design treated them as competing and used `FILTER NOT EXISTS` to surface only the latest, hiding any earlier applicable period. v1.8.0 surfaces them all.

- `dataset_versions[<rulesetid>]` is now a **list** of `{ version, published_at, title }` records, not a single record. Replaces the v1.7.x object shape.
- List is pre-sorted: `version` descending with nulls at the end, ties broken by `published_at` descending. Element `[0]` is the most-recent applicable version of that ruleset.
- SPARQL query simplified: dropped the `FILTER NOT EXISTS` subpattern and now fetches all `cprmv:Dataset` records. Grouping and sort live in the service layer.

```json
"dataset_versions": {
  "BWBR0015703": [
    {
      "version": "2026-01-01",
      "published_at": "2026-05-15T06:57:21Z",
      "title": "Participatiewet"
    },
    {
      "version": "2025-01-01",
      "published_at": "2026-05-15T07:45:36Z",
      "title": "Participatiewet"
    }
  ]
}
```

#### Cache headers preserved across the shape change

- `ETag` now hashes every `(version, published_at)` pair in `dataset_versions` — a new applicable period being added to any ruleset changes the ETag
- `Last-Modified` is `max(published_at)` across **all records** in the response (not just the first per ruleset)
- `Cache-Control` semantics unchanged: full headers when every rulesetid has metadata; `no-cache` otherwise

#### Breaking change

Replaces v1.7.1 (which was never used by external G2G consumers — the API stability contract hadn't been promised yet at that release). The shape change from object to list is detected at integration time, not silent runtime breakage. Anyone consuming v1.7.0/v1.7.1 needs to wrap `dataset_versions[<id>]` access in array indexing or iteration.

#### Documentation

- API stability contract updated with the list-shape, the multi-applicable-period rationale, and how consumers can match a rule's `applicable_date` to a specific Dataset record
- Quick-reference table gains two new rows (multi-record explanation and rule→Dataset lookup recipe)

**Files:** `packages/backend/src/utils/etag.ts`, `packages/backend/src/services/norms.service.ts`, `packages/backend/src/routes/norms.routes.ts`, `docs/iou-architectuur/linked-data-explorer/architecture/backend.md`, `docs/iou-architectuur/linked-data-explorer/reference/api-stability.md`

---

### v1.7.0 — Per-rulesetid dataset versioning & HTTP cache headers (May 2026)

**v1.7.0 — Minor (May 14, 2026)**

#### Per-rulesetid dataset versioning on `/v1/norms`

Each BWB ruleset (BWBR0002471, BWBR0004044, …) is now published as a distinct `cprmv:Dataset` resource in TriplyDB, each on its own publication cadence. The response envelope carries a `dataset_versions` map keyed by `cprmv:rulesetId` so G2G consumers can see exactly which version of each ruleset they're reading.

```json
"dataset_versions": {
  "BWBR0002471": { "version": "2025.1.0", "published_at": "2025-01-15T00:00:00Z" },
  "BWBR0015703": { "version": "2026.1.0", "published_at": "2026-01-15T00:00:00Z" }
}
```

- New envelope field `dataset_versions` — only contains entries for rulesetids that have a `cprmv:Dataset` record; rulesetids without one are silently absent (transitional state during rollout)
- New envelope field `cprmv_version` — backend constant extracted from the CPRMV namespace URI, describes which vocabulary the backend speaks independently of which data is published
- Backend picks the latest `cprmv:Dataset` per rulesetid via a `FILTER NOT EXISTS` SPARQL subpattern — historical versions remain queryable in TriplyDB but consumers see only the latest
- Versions follow CalVer per ruleset: `<year>.<cycle>.<patch>` (e.g. `2026.1.0` for the first publication of 2026, `2026.1.1` for a correction)
- Internal 60-second cache on the dataset metadata SPARQL query keeps the metadata lookup off the hot path

#### HTTP cache headers for G2G consumers

When **every** rulesetid in the response has dataset metadata, the response carries strong cache headers:

```
ETag: "a3f99c1d"
Last-Modified: Thu, 15 Jan 2026 00:00:00 GMT
Cache-Control: public, max-age=3600
```

- `ETag` is an opaque 8-hex hash over the sorted `dataset_versions` map plus all filter parameters that affect the response shape
- `Last-Modified` is `max(published_at)` across the response's datasets in RFC 7231 format — `If-Modified-Since` returns `304` only when nothing in the consumer's query has been republished
- For single-rulesetid queries (`?rulesetid=<id>`), the `304 Not Modified` short-circuit happens **before** the expensive rules SPARQL query — only the cheap cached metadata lookup runs
- Safe-by-default partial-coverage policy: if any rulesetid in the response lacks dataset metadata, all three cache headers degrade to `Cache-Control: no-cache` so consumers can't be misled into serving stale data for an unversioned ruleset

#### API stability contract published

New IOU documentation page at [`/linked-data-explorer/reference/api-stability`](../reference/api-stability.md) — the binding contract for G2G consumers covering:

- The four versioning layers (API contract, dataset versions, CPRMV vocabulary, backend service)
- The immutable primary-key promise: `(rulesetid, applicable_date, rulesetid_index)` is the eternal PK; consumers can cache permanently and never invalidate
- The `rule_id_path_key` field as the logical identifier for querying "the current value of this rule" across its lifetime
- Per-rulesetid publication detection mechanics and partial-coverage behaviour
- Breaking-change criteria warranting `/v2/norms` and the 24-month deprecation policy

**Files:** `packages/backend/src/utils/etag.ts` (new), `packages/backend/src/services/norms.service.ts`, `packages/backend/src/routes/norms.routes.ts`, `docs/iou-architectuur/linked-data-explorer/architecture/backend.md`, `docs/iou-architectuur/linked-data-explorer/reference/api-stability.md` (new)

---

### v1.6.3 — Stable keys and per-ruleset aggregation (May 2026)

**v1.6.3 — Patch (May 14, 2026)**

#### Stable keys and version indices on `/v1/norms`

- New `rule_id_path_key` field: `rule_id_path` with the date and index segments removed, e.g. `"BWBR0002471_2025-01-01_0, Artikel 2, lid 6"` → `"BWBR0002471, Artikel 2, lid 6"`; stable across versions of the same ruleset, suitable as a deduplication key when aggregating norms across `applicable_date` values
- New `rulesetid_index` field: the integer index segment after the date in `rule_id_path` (e.g. the `_0` in `BWBR..._2025-01-01_0`); distinguishes multiple versions published on the same date
- Both new fields, together with `applicable_date`, are derived from a single regex pass over `rule_id_path`; all three emit JSON `null` when the path does not match the canonical `<rulesetid>_<YYYY-MM-DD>_<index>[, <rest>]` shape
- Key insertion order extended: `rulesetid`, `applicable_date`, `rulesetid_index`, `rule_id_path`, `rule_id_path_key` — identifier metadata grouped first, then the path and its derived stable key together

#### Per-rulesetid aggregation

- Response envelope now carries an `aggregations.norms_per_rulesetid` map alongside `rules`, listing the count of top-level rules per `cprmv:rulesetId` in the filtered result set
- Counts are keyed by the authoritative `cprmv:rulesetId` value (not parsed from the path), so non-conforming `rule_id_path` values still aggregate correctly
- Sum of values equals `data.total`, letting clients render ruleset-level summaries without a second pass over `rules`
- Additive change — existing readers of `data.rules` and `data.total` see no breaking change

**Files:** `packages/backend/src/services/norms.service.ts`, `packages/backend/src/routes/norms.routes.ts`, `docs/iou-architectuur/linked-data-explorer/architecture/backend.md`

---

### v1.6.2 — Shared route registry & content-negotiated root page (May 2026)

**v1.6.2 — Patch (May 13, 2026)**

#### Single source of truth for v1 routes

- New backend module `packages/backend/src/routes/registry.ts`: every v1 route's mount path, router, summary, and category lives in one array. Adding a route is a one-line entry that both registration and the root page pick up automatically.
- Refactored `packages/backend/src/routes/index.ts` to iterate the registry for v1 mounting; legacy `/api/*` deprecation aliases stay hand-mounted (deprecated routes are intentionally excluded from the registry to steer consumers towards `/v1/*`)
- Mount-order semantics preserved: more specific paths still precede their parents (`/v1/chains/templates` before `/v1/chains`) so Express route precedence behaves exactly as before

#### Content-negotiated root page

- `GET /` now serves HTML when `Accept` includes `text/html` (browsers) and JSON otherwise (curl, fetch with default `Accept`, programmatic pollers); both views are derived from the shared route registry so they cannot drift
- HTML view groups endpoints by category (Health & monitoring, Discovery, Execution, Assets, Integrations) and badges public-CORS endpoints; styling is inline with no external dependencies
- JSON payload preserves backwards compatibility: same top-level keys as before (`name`, `version`, `environment`, `status`, `documentation`, `health`, `endpoints`, `legacy`); existing programmatic clients see no breaking change
- Closes the drift gap that was missing `/v1/dso`, `/v1/norms`, `/v1/assets/*`, `/v1/cache`, `/v1/edocs`, `/v1/ropa`, `/v1/process` and `/v1/chains/templates` from the previous hand-coded listing

#### Deployment tier display label

- New `DEPLOYMENT_ENV` environment variable distinguishes ACC from PROD when `NODE_ENV` is `'production'` for both; falls back to `NODE_ENV` when unset so local development needs no change
- Added `config.displayEnv` (string) and `config.deploymentEnv` (raw value) to `packages/backend/src/utils/config.ts` with mappings: `prod`/`production` → `PROD`, `acc`/`acceptance`/`staging` → `ACC`, `dev`/`development`/`local` → `development`, `test` → `test`, unknown values pass through
- Used consistently by the HTML root page and the `/v1/health` response so the displayed environment stays in sync across surfaces
- Configuration is per Azure App Service: `az webapp config appsettings set ... --settings DEPLOYMENT_ENV=acc` (or `prod`)

**Files:** `packages/backend/src/routes/registry.ts` (new), `packages/backend/src/utils/rootView.ts` (new), `packages/backend/src/routes/index.ts`, `packages/backend/src/index.ts`, `packages/backend/src/utils/config.ts`, `packages/backend/.env.example`, `packages/backend/src/routes/health.routes.ts`

---

### v1.6.1 — Norms publish endpoint (May 2026)

**v1.6.1 — Patch (May 12, 2026)**

#### `/v1/norms` — new

New backend route `GET /v1/norms` exposing all `cprmv:Rule` paths and norms from TriplyDB in the publish format consumed by the SPARQL editor's norm publisher. The response mirrors the `cprmv-example.json` shape exactly: fully-qualified RDF/CPRMV keys for `type`, `id`, `definition`, and `contains`; short keys for `situatie`, `norm`, `per`, `rulesetid`, `applicable_date`, and `rule_id_path`.

- Parent rules and their `cprmv:contains` children are aggregated into a single nested object per parent; key insertion order is preserved across runs (matching the example file)
- Optional `?endpoint=` query parameter overrides the default TriplyDB endpoint, matching the pattern already used by `/v1/dmns`
- Response wrapped in the standard `ApiResponse` envelope with `data.rules` (array) and `data.total` (filtered count)

#### Filtering by ruleset identifier and applicable date

- New `applicable_date` attribute derived from the `_YYYY-MM-DD_` segment embedded in `rule_id_path` (e.g. `"BWBR0015703_2026-01-01_0, Artikel 20, ..."` yields `"2026-01-01"`); `null` when the path carries no parseable date
- Optional `?rulesetid=` filter (exact-match on `cprmv:rulesetId`, e.g. `BWBR0015703`); validated against `/^[A-Za-z0-9_-]+$/`
- Optional `?applicable_date=` filter (matches paths containing `_<date>_`); validated against `/^\d{4}-\d{2}-\d{2}$/`
- Filters can be combined; invalid values return `400 INVALID_PARAM` before any SPARQL fires
- Validated filter values are applied as SPARQL `FILTER` clauses server-side (exact-match on `?rulesetId`, `CONTAINS` on `?ruleIdPath`); regex validation is the injection-prevention contract

#### Maintenance

- `tsconfig.json` cleanup: removed `"ignoreDeprecations": "6.0"` which only became valid in TypeScript 6.0 and broke CI on TypeScript 5.x. Editor-side deprecation warnings are addressed via local `.vscode/settings.json` pointing at the workspace TypeScript instead. Full migration to `moduleResolution: "nodenext"` deferred until ESM-on-Node maturity warrants the per-file `.js` extension changes.

**Files:** `packages/backend/src/services/norms.service.ts` (new), `packages/backend/src/routes/norms.routes.ts` (new), `packages/backend/src/routes/index.ts`, `packages/backend/tsconfig.json`

---

### v1.6.0 — Multilingualism & pending-until-Save editing (April 2026)

**v1.6.0 — New Feature (April 27, 2026)**

#### Multilingualism — language and organization metadata

BPMN processes, Camunda forms, and document templates now carry an optional ISO 639-1 language code (`en`, `nl`, `de`) and an open-ended organization key. The model is sibling-artefact i18n: each artefact exists once per language, with the LDE deploy modal warning on mixed-language bundles. DMNs stay language-agnostic — variable keys remain stable English so a single DMN serves both English and Dutch sibling BPMNs.

- **Database** — `language VARCHAR(2)` and `organization VARCHAR(100)` columns added to `process_definitions`, `form_schemas`, and `document_templates` with partial indexes; nullable, existing rows coexist as `NULL`
- **BPMN moddle descriptor** — `LanguageMixin` and `OrganizationMixin` extending `bpmn:Process` in `ronlModdleDescriptor.json`; survive `saveXML` round-trip via the existing `ronl` namespace registration
- **List panels** — new `ArtefactListToolbar` (search + language filter + match counter) shared by Process, Form, and Document lists; collapsible organization groups; subprocesses follow their shell's organization regardless of their own tag
- **Editor footer panel** — uniform pattern across all three editors: `LanguageSelector` and `OrganizationSelector` (with autocomplete from existing organization keys); BPMN footer additionally retains RoPA and DSO selectors
- **Filename-based language inference on import** — `.bpmn`, `.form`, `.document` files with a `<id>.<lang>.<ext>` suffix are auto-tagged on import; precedence: in-file value → filename → untagged
- **Form export** — `Export .form` now wraps the form-js schema with top-level `language` and `organization` keys and uses a language-suffixed filename; round-trip integrity for all three artefact types
- **Deploy-time language consistency check** — amber warning surfaces inline in the deploy modal when a bundle mixes languages, listing the offending codes; mirrors the existing RoPA-missing warning UX

**Files:** `packages/backend/src/db/migrate.ts`, `packages/backend/src/db/types.ts`, `packages/backend/src/db/mappers.ts`, `packages/backend/src/domain/types.ts`, `packages/backend/src/services/assets.service.ts`, `packages/frontend/src/types/index.ts`, `packages/frontend/src/types/document.types.ts`, `packages/frontend/src/components/BpmnModeler/ronlModdleDescriptor.json`, `packages/frontend/src/components/common/LanguageSelector.tsx`, `packages/frontend/src/components/common/OrganizationSelector.tsx`, `packages/frontend/src/components/common/ArtefactListToolbar.tsx`, `packages/frontend/src/components/BpmnModeler/BpmnModeler.tsx`, `packages/frontend/src/components/BpmnModeler/BpmnCanvas.tsx`, `packages/frontend/src/components/BpmnModeler/ProcessList.tsx`, `packages/frontend/src/components/FormEditor/FormEditor.tsx`, `packages/frontend/src/components/FormEditor/FormCanvas.tsx`, `packages/frontend/src/components/FormEditor/FormList.tsx`, `packages/frontend/src/components/DocumentComposer/DocumentComposer.tsx`, `packages/frontend/src/components/DocumentComposer/DocumentList.tsx`, `packages/frontend/src/services/bpmnService.ts`, `packages/frontend/src/services/formService.ts`

#### Pending-until-Save editing model

Footer edits across BPMN, Form, and Document editors no longer persist immediately. They accumulate in a draft state on the editor parent and flush atomically when Save is clicked. Navigation guards confirm before discarding unsaved changes.

- **Editor architecture** — footer state lifted to the editor parent (`BpmnModeler`, `FormEditor`, `DocumentComposer`); children receive effective values via props and report changes via callbacks; Save is the single point of persistence
- **Shell → subprocess atomic save** — saving a BPMN shell propagates `language` and `organization` to all linked subprocesses in one write; idempotent (skips subprocesses already aligned); shell wins unconditionally; example subprocesses (`readonly: true`) are skipped
- **Save button dirty tracking fixed** — Form Save button was always-enabled (regression); now starts disabled, enables on first edit, disables after Save
- **Document load window** — `DocumentComposer` no longer flips `hasChanges` spuriously on document load; TipTap's mount-time `onUpdate` events are suppressed for the macrotask following load via `isLoadingRef`

#### HR-capacity Dutch reference bundle

The first multi-language reference bundle: 1 BPMN, 8 forms, 2 documents under `examples/organizations/flevoland/HR-capacity/nl/`, all tagged `language=nl`, `organization=flevoland`. Same `CapacityClaimRouting` DMN serves both the English and Dutch siblings.

#### Bug fixes

- BPMN persistence: `language` and `organization` now included in the `BpmnService.saveProcess` POST payload (previously dropped silently, causing values to vanish on hydration)
- `OrganizationSelector` is now controlled (`value`/`onChange`) rather than uncontrolled (`defaultValue`/`onBlur`); switching artefacts refreshes the input correctly
- `BpmnCanvas` no longer resets on parent re-renders — `handleElementSelect` stabilised via a ref, modeler-init effect deps narrowed to `xml`

#### Known limitation

The form-js properties panel loses input focus when typing pauses (Field label, Description, Key). Upstream form-js issue #86, marked wontfix by bpmn-io. Not LDE-caused, not fixable from React without forking form-js. Workaround: edit `.form` JSON in a code editor and re-import — filename-based language inference handles the language tag automatically.

---

### v1.5.3 — DSO Works tab & OIN preset fix (April 2026)

**v1.5.3 — Patch (April 2026)**

#### Works tab — new

New **Works** tab in the DSO Explorer (between Concepts and Activities) backed by the Zoekinterface API.

- Search werkzaamheden by user intent (e.g. "boom kappen") with autocomplete suggestions after 2 characters; selecting a suggestion immediately fires the search
- Each result shows the human-readable `omschrijving`, the `functioneleStructuurRef` (full concept URI — the Phase 4 pivot to STTR files), and the short werkzaamheid URN
- Selecting a result opens a detail panel showing the current version's `omschrijving`, validity period, and full version history with start/end dates and a "current" badge
- Autocomplete uses `POST /werkzaamheden/_suggereer` with 300ms debounce
- Reloads on DSO environment switch with the same clean-slate behaviour as the other tabs

#### Activities tab — OIN preset fix

The Lelystad and Flevoland presets now use `POST /activiteiten/_zoek` with `bestuursorgaan.oin` filter instead of `_wijzigingen` — returning activities valid on a given date rather than a delta sync of changed activities.

- Activities now appear in the list with their full `omschrijving` visible immediately, without requiring parallel detail fetches
- Date field defaults to today for OIN presets (yesterday offset removed — no longer needed with `_zoek`)
- Pagination works correctly in OIN mode — Load button reloads the authority list for the selected date
- Empty state distinguishes between no activities found in general vs no activities found for the selected authority on the selected date

#### Bug fixes

- Activity Detail panel always using pre-production DSO when opened from the Activities list — `env` was missing from the `getActiviteitDetail` call, causing 404 for production-only activities
- Activity Detail panel not re-fetching when DSO environment is switched while a URN is already selected — `env` added to the `useEffect` dependency array
- Activity Detail panel showing stale date context in OIN preset mode — `activeDatum` now set correctly by `loadByOin` alongside the result

#### Backend — DSO service

- `zoekinterfaceBaseUrl` and `opvragenWerkzaamhedenBaseUrl` added to both `dso` and `dsoProd` config blocks — defaults baked in, no new env vars required
- `POST /v1/dso/werkzaamheden/zoek` — proxies Zoekinterface `/werkzaamheden/_zoek`
- `POST /v1/dso/werkzaamheden/suggereer` — proxies Zoekinterface `/werkzaamheden/_suggereer`
- `GET /v1/dso/werkzaamheden/:urn` — proxies Opvragen Werkzaamheden `/werkzaamheden/{urn}` (version history, without expand — `_expandScope` enum value not yet resolved)
- `POST /v1/dso/activiteiten/oin` now uses `/activiteiten/_zoek` with `bestuursorgaan.oin` body field and `datum` instead of `_wijzigingen` with `datumVanaf`

---

### v1.5.2 — DSO Explorer enhancements (April 2026)

**v1.5.2 — Patch (April 2026)**

- DSO environment selector added to the Settings panel (gear icon): switch between pre-production and production DSO independently of the LDE environment, persisted across sessions in localStorage
- Environment badge in the DSO Explorer header updates to reflect the active DSO environment (amber for pre-production, green for production)
- Both DSO environments use separate API keys configured via `DSO_API_KEY` and `DSO_API_KEY_PROD` environment variables
- Location presets (Lelystad, Flevoland) initially filter by authority OIN — replaced with `_zoek` in v1.5.3
- Child activities in the detail panel now show human-readable names fetched in parallel after the parent detail loads
- Graceful 404 handling in the detail panel: activities not available in the active DSO environment show a clear message instead of a raw error

---

### v1.5.1 — Dev infrastructure (April 2026)

**v1.5.1 — Infrastructure (April 2026)**

#### Docker readiness check

New `packages/backend/scripts/check-docker.sh` verifies the `ronl-postgres` container is up and healthy before nodemon starts the backend.

- Coloured terminal output: green for ready, yellow for unhealthy, red for missing or stopped
- Suggests the exact `docker start` or `docker run` command if the container is missing
- Backend `dev` script now runs the check first; `dev:full` and `dev:backend` scripts added to root `package.json` for one-command monorepo startup

**Files:** `packages/backend/scripts/check-docker.sh`, `packages/backend/package.json`, `package.json`

---

### v1.5.0 — DSO Integration Phase 1 (March 2026)

**v1.5.0 — New Feature (March 2026)**

#### DSO Explorer

New top-level view for browsing the Digitaal Stelsel Omgevingswet from inside LDE.

- **Concepts tab** — full-text search across the Stelselcatalogus
- **Activities tab** — RTR `activiteiten` list with date filtering and a detail panel showing `bestuursorgaan`, validity, parent and child activities, and which rule types (`Conclusie`, `Indieningsvereisten`, `Maatregelen`) are present

#### BPMN — DSO activiteit linkage

- New `ronl:dsoActiviteitUrn` mixin on `bpmn:Process` in `ronlModdleDescriptor.json`
- New `DsoActiviteitSelector` component pinned to the BPMN Modeler footer (sibling of `RopaSelector`)
- Live URN verification against DSO RTR; on success shows the omschrijving, authority block, and a direct link to the public RTR viewer
- URN survives `saveXML` round-trips and shows up in process exports

#### Backend — DSO service

- New `src/services/dso.service.ts` covering Stelselcatalogus and RTR endpoints
- New `src/routes/dso.routes.ts` at `/v1/dso/...`
- Pre-production and production base URLs configurable via env; API keys per environment
- Path-aware DSO environment selection via `X-Dso-Env` header

**Files:** `packages/frontend/src/components/BpmnModeler/DsoActiviteitSelector.tsx`, `packages/frontend/src/services/dsoService.ts`, `packages/backend/src/services/dso.service.ts`, `packages/backend/src/routes/dso.routes.ts`

---

### v1.4.0 — RoPA Records & GDPR Article 30 Compliance (March 2026)

**v1.4.0 — New Feature (March 28, 2026)**

#### RoPA Records — PostgreSQL

Two new tables appended to the `migrate.ts` DDL block. Migrations run automatically at backend startup — no manual schema step required.

- `ropa_records` — one row per process (shell or subprocess); keyed on `bpmn_process_id` with a unique index so re-running the seed updates rows in place rather than inserting duplicates; `status` column (`draft` / `active` / `archived`) controls public visibility
- `ropa_personal_data_fields` — one row per personal data field collected by the linked forms; `ON DELETE CASCADE` from `ropa_records`; `special_category` boolean flags Art. 9/10 GDPR fields
- New `src/types/ropa.types.ts` — `RopaRecord`, `RopaPersonalDataField`, `PublicRopaRecord`
- New `src/services/ropa.service.ts` — `listRopa`, `getRopaById`, `getRopaByBpmnProcessId`, `upsertRopa` (transactional: record header + field rows in one `BEGIN`/`COMMIT`), `deleteRopa`, `listPublicRopa`
- New `src/db/seed-ropa.ts` — idempotent seed for four active records covering `AwbShellProcess`, `TreeFellingPermitSubProcess`, `AwbZorgtoeslagProcess`, and `ZorgtoeslagProvisionalSubProcess`

**Files:** `src/db/migrate.ts`, `src/types/ropa.types.ts`, `src/services/ropa.service.ts`, `src/db/seed-ropa.ts`

#### RoPA Records — API routes

- New `src/routes/ropa.routes.ts` — authenticated asset routes at `/v1/assets/ropa`: `GET` (list), `POST` (upsert, returns `{ id }`), `DELETE /:id`, `GET /by-bpmn-id/:bpmnProcessId`
- New `src/routes/ropa.public.routes.ts` — CORS-open public route at `/v1/ropa/public`; `?organisation=` query parameter filters by `controller_name ILIKE '%…%'`; strips `controllerContact`, `dpoContact`, and `schemaVersion` before returning; only `status = 'active'` records returned
- Global CORS middleware in `src/index.ts` patched with path-aware logic: `/v1/ropa/public` bypasses the origin whitelist entirely (`origin: '*'`); all other routes remain subject to `CORS_ORIGIN` env var

**Files:** `src/routes/ropa.routes.ts`, `src/routes/ropa.public.routes.ts`, `src/routes/index.ts`, `src/index.ts`

#### RoPA Editor — LDE UI

New **RoPA Records** view in the LDE sidebar (`ScrollText` icon). `ViewMode.ROPA` added to the enum in `types/index.ts`.

- `RopaEditor.tsx` — root orchestrator; list state, load/save/delete; passes `record={null}` for new records, `key={activeId}` on `RopaRecordEditor` for clean remount on selection change
- `RopaList.tsx` — left panel; shell records first, subprocess records second; DRAFT / ACTIVE / ARCHIVED badges; delete control per record
- `RopaRecordEditor.tsx` — four-tab editor:
  - **Record** — all GDPR Art. 30 mandatory fields; **Lookup from knowledge graph** button fires a SPARQL query against the TriplyDB RONL endpoint via `POST /v1/triplydb/query` and returns a pick-list of `eli:LegalResource` entries
  - **Personal Data Fields** — **Hydrate from forms** reads `camunda:formRef` values from the process XML, loads matching form schemas from `FormService`, and appends one row per component with a `key` property; each row is classified with a data category and Art. 9/10 flag
  - **BPMN Link** — reads `ronl:ropaRef` from the matching process XML via `BpmnService`; **Write ronl:ropaRef to BPMN** injects the attribute and persists via `BpmnService.saveProcess`; status indicator: not linked / linked (green) / points to different record (amber)
  - **Status** — three lifecycle buttons with confirmation dialog before activation
- New `src/services/ropaService.ts` — fetch-based API client for all five backend operations
- New `src/types/ropa.types.ts` (frontend mirror)

**Files:** `src/components/RopaEditor/RopaEditor.tsx`, `RopaList.tsx`, `RopaRecordEditor.tsx`, `src/services/ropaService.ts`, `src/types/ropa.types.ts`, `src/types/index.ts`, `src/App.tsx`

#### RoPA Selector — BPMN Modeler

- New `src/components/BpmnModeler/RopaSelector.tsx` — renders as a fixed footer panel pinned below the scrollable process list in `ProcessList.tsx`; only shown when `activeProcess` is non-null; reads the current `ronl:ropaRef` from the process XML by regex; writes via `handleRopaRefChange` in `BpmnModeler.tsx`
- `ProcessList.tsx` — two new props: `activeProcess: BpmnProcess | null` and `onRopaRefChange: (ropaRef: string | undefined) => void`; `RopaSelector` rendered outside the `overflow-y-auto` scroll container so it stays pinned regardless of list length
- `BpmnModeler.tsx` — new `handleRopaRefChange`: ensures `xmlns:ronl` declaration on `<definitions>`, then sets, updates, or removes `ronl:ropaRef` on the `<bpmn:process>` opening tag; persists via `BpmnService.saveProcess`
- `ronlModdleDescriptor.json` — second type entry added: `RopaRefMixin` extends `bpmn:Process` with `ropaRef` as an `isAttr: true` String property; without this registration the attribute is silently dropped by bpmn-js on `saveXML()`
- Deploy modal — `ropaRefMissing` flag set when `ronl:ropaRef` is absent from the process XML; amber non-blocking warning rendered between the resource list and the resource count line

**Files:** `src/components/BpmnModeler/RopaSelector.tsx`, `ProcessList.tsx`, `BpmnModeler.tsx`, `BpmnCanvas.tsx`, `ronlModdleDescriptor.json`

#### RoPA Public Site — MVP

New package `packages/ropa-site/` — a zero-dependency static HTML/CSS/JS site with no build step.

- `index.html` — fetches `GET /v1/ropa/public`, renders collapsible cards per record with full GDPR Art. 30 field display, personal data fields table with colour-coded data categories and Art. 9/10 red badges, Provincie Flevoland dark green house style; shells rendered before subprocesses
- `staticwebapp.config.json` — Azure Static Web Apps navigation fallback and no-cache headers
- Deployed as a separate Azure Static Web Apps resource (`ropa-flevoland-acc`) independent of the LDE frontend; GitHub Actions workflow scoped to `packages/ropa-site/**` path filter

**Files:** `packages/ropa-site/index.html`, `packages/ropa-site/staticwebapp.config.json`, `packages/ropa-site/README.md`, `.github/workflows/azure-static-web-apps-ropa-flevoland-acc.yml`

---

### v1.3.0 — PostgreSQL Asset Storage & AWB Process Hierarchy (March 2026)

**v1.3.0 — Infrastructure (March 25, 2026)**

#### PostgreSQL asset storage

BPMN processes, form schemas, and document templates now persist to PostgreSQL via the LDE backend rather than living exclusively in browser `localStorage`.

- New `src/db/pool.ts` — `pg.Pool` initialised from `DATABASE_URL`; null-guarded so the backend starts without a database configured
- New `src/db/migrate.ts` — idempotent DDL (`CREATE TABLE IF NOT EXISTS`) for `process_definitions`, `form_schemas`, and `document_templates`; called from `startServer()` before `app.listen()`
- New `src/services/assets.service.ts` — `listBpmn`, `upsertBpmn`, `deleteBpmn`, `getBpmnByBpmnProcessId`, `listForms`, `upsertForm`, `deleteForm`, `listDocuments`, `upsertDocument`, `deleteDocument`
- New `src/routes/assets.routes.ts` — `GET`/`POST`/`DELETE` for each asset type; `GET /v1/assets/bpmn/by-bpmn-id/:bpmnProcessId` for subprocess bundle resolution; all routes return `503 DB_NOT_CONFIGURED` when pool is null
- Registered at `/v1/assets` in `src/routes/index.ts`
- `packages/backend/package.json` — `pg: ^8` added to `dependencies`, `@types/pg: ^8` to `devDependencies`

**Write-through cache strategy:** saves update `localStorage` immediately and fire a background POST to the backend. Reads remain synchronous from `localStorage` — zero-latency UI at all times.

**Hydration on mount:** each editor runs `hydrateFromServer()` on mount — `GET /v1/assets/{type}` merges server records with local read-only examples and updates the `localStorage` cache. Falls back to local cache silently if the backend is unreachable.

**Files:** `src/db/pool.ts`, `src/db/migrate.ts`, `src/services/assets.service.ts`, `src/routes/assets.routes.ts`, `src/routes/index.ts`, `src/index.ts`, `packages/backend/package.json`, `src/services/bpmnService.ts`, `src/services/formService.ts`, `src/services/documentService.ts`

#### AWB shell / subprocess hierarchy

The `BpmnProcess` type and process library now model the two-layer AWB shell pattern explicitly.

- `BpmnProcess` interface extended with `bpmnProcessId?: string`, `processRole?: 'shell' | 'subprocess' | 'standalone'`, and `calledElement?: string`
- `bpmnProcessId` is extracted from `<process id="...">` in the XML automatically on save and import via `extractBpmnProcessId()`
- All five seeded example processes carry explicit role and relationship metadata
- `ProcessList.tsx` renders a hierarchical grouped view: shell entries are top-level, their subprocesses are indented with a tree connector; standalone and unclassified processes appear as top-level entries
- `SHELL` (violet) and `SUB` (teal) role badges added to process cards
- `process_definitions` table stores `process_role`, `called_element`, and `bpmn_process_id` as indexed columns

**Files:** `src/types/index.ts`, `src/components/BpmnModeler/BpmnModeler.tsx`, `src/components/BpmnModeler/ProcessList.tsx`

#### Schema versioning

`schema_version INTEGER NOT NULL DEFAULT 1` column added to all three PostgreSQL tables, enabling server-side re-seeding of example assets across all users and devices when source files change.

#### Zorgtoeslag example processes

Three new versioned example processes added: `AwbZorgtoeslagProcess` (shell), `ZorgtoeslagProvisionalSubProcess`, and `ZorgtoeslagFinalSubProcess` (both subprocesses). Four new example forms: `zorgtoeslag-provisional-start`, `zorgtoeslag-provisional-review`, `zorgtoeslag-final-review`, `zorgtoeslag-notify-applicant`.

**Files:** `src/utils/exampleVersions.ts`, `public/examples/toeslagen/`

#### Azure deployment — troubleshooting notes

During ACC deployment the following issues were encountered and resolved:

- **`permission denied for schema public`** — Azure PostgreSQL Flexible Server (PostgreSQL 15+) revokes `CREATE` on the public schema from non-superusers by default. Fixed by running `GRANT ALL ON SCHEMA public TO lde_user` plus `ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO lde_user` as admin.
- **CI/CD health check failing (`503`)** — caused by the above permission error crashing `migrate()` before `app.listen()` was reached. The App Service showed "Application Error" page with no log output via `az webapp log tail`; logs were only retrievable via `az webapp log download`.

See [PostgreSQL Deployment](deployment-postgresql.md) for the full provisioning guide including these fixes.

---
 
### v1.2.0 — RIP Phase 1 Bundle & eDOCS Integration (March 2026)
 
**v1.2.0 — New Feature (March 14, 2026)**
 
#### RIP Phase 1 Bundle
 
New deployment bundle for the Regular Infrastructure Projects (RIP) Phase 1 workflow — Provincie Flevoland.
 
- 20-step BPMN process (`RipPhase1Process.bpmn`) covering project definition and preliminary design preparation: intake form, intake meeting, intake report, PSU organisation, PSU execution, PSU report, risk file preparation, preliminary design principles, and two approval gateways with rejection loops
- `RipProjectTypeAssignment.dmn` — assigns `candidateGroups` and `assignedRoles` from `projectType` and `department`; all rules resolve to `infra-projectteam` / `infra-medewerker`; designed for granular RBAC extension without BPMN changes
- 7 forms: `rip-intake`, `rip-intake-meeting`, `rip-intake-report`, `rip-psu-organize`, `rip-psu-execution`, `rip-risk-file`, `rip-approval` (reusable at both approval gateways)
- 3 document templates: `rip-intake-report.document` (column 2), `rip-psu-report.document` (column 3), `rip-pdp.document` (column 4)
- Bundle deployed to `examples/organizations/flevoland/rip-phase1/`
 
**Files:** `examples/organizations/flevoland/rip-phase1/`
 
#### eDOCS Integration
 
New backend service and external task worker for OpenText eDOCS document management.
 
- `EdocsService` wraps the eDOCS REST API: `connect` (session token caching with auto re-authentication on 401/403), `ensureWorkspace`, `uploadDocument`, `getWorkspaceDocuments`, `healthCheck`
- `ExternalTaskWorker` polls Operaton via `fetchAndLock` (long-polling, 20s timeout) for two topics: `rip-edocs-workspace` (create/retrieve project workspace, write `edocsWorkspaceId`) and `rip-edocs-document` (render and upload document, write named output variable)
- Stub mode (`EDOCS_STUB_MODE=true`, default) — all methods return realistic fake responses; full process runs end-to-end without a live eDOCS server; no code changes needed when switching to live
- Worker started in `app.listen()` callback; stopped cleanly on `SIGTERM`/`SIGINT`
- 4 new REST endpoints: `GET /v1/edocs/status`, `POST /v1/edocs/workspaces/ensure`, `POST /v1/edocs/documents`, `GET /v1/edocs/workspaces/:id/documents`
- New environment variables: `EDOCS_BASE_URL`, `EDOCS_LIBRARY`, `EDOCS_USER_ID`, `EDOCS_PASSWORD`, `EDOCS_STUB_MODE`
 
**Files:** `packages/backend/src/services/edocs.service.ts`, `packages/backend/src/services/externalTaskWorker.service.ts`, `packages/backend/src/routes/edocs.routes.ts`
 
#### DMN Validator — Interaction Rules
 
- **INT-005** scoped to DRDs only — no longer fires on standalone single-decision DMNs; `<inputData>` elements on standalone models serve as input contract declarations for CPSV publishing and do not require `<informationRequirement>` wiring
- **INT-007** (new) — warns when an `<inputExpression>` references a variable name with no matching top-level `<inputData>` declaration; without this, the CPSV Editor generates an empty request body on deploy
 
**File:** `packages/backend/src/services/dmn-validation.service.ts`
 
**v1.1.2 — Bug Fix (March 11, 2026)**
 
#### Form Editor
 
- **Save** now correctly persists the current schema. `saveSchema()` in form-js 1.20.x returns the schema object directly — not wrapped in `{ schema }`. Destructuring assumption caused `undefined` to be written to `localStorage`, making the active form disappear on the next render.
- **Export .form** fixed for the same reason.
- Vite `dedupe` config added for `preact` / `preact/hooks` / `preact/compat` to prevent duplicate Preact instances after npm version round-trips involving `@bpmn-io/*` packages; fixes `TypeError: Cannot read properties of undefined (reading 'context')` on the form canvas.
 
**Known issue:** Typing in a properties panel field (label, key, etc.) loses focus after the first character. Upstream form-js 1.20.x issue — Preact re-renders the properties panel internally on every change event. Will be resolved when an upstream fix is available.
 
**File:** `packages/frontend/vite.config.ts`, `packages/frontend/src/components/FormEditor/FormCanvas.tsx`
 
**v1.1.1 — Enhancement (March 10, 2026)**
 
#### Import from file
 
- **BPMN Modeler** — import `.bpmn` files via the Upload button in the process list header; process name derived from the `name` attribute on the `<process>` element, falling back to filename
- **Form Editor** — import `.form` files; name derived from the schema `id` field, falling back to filename
- **Document Composer** — import `.document` files; receives a fresh `id` and timestamps on import to avoid collisions with existing templates
- All imported items open immediately in their respective editor and are persisted to `localStorage`
 
**Files:** `BpmnModeler/BpmnModeler.tsx`, `FormEditor/FormEditor.tsx`, `DocumentComposer/DocumentComposer.tsx`
 
---

### v1.1.0 — Document Composer (March 2026)

**v1.1.0 — New Feature (March 8, 2026)**

#### Document Composer

New **Document Composer** view for authoring formal government decision document templates (*beschikkingen*).

- Three-panel layout matching BPMN Modeler and Chain Builder conventions: document list (left), zone canvas (centre), Bindings panel (right)
- Fixed-zone document structure: Letterhead, Contact Information, Reference, Body, Closing, Sign-off, and optional Annex
- Five draggable block types: rich text (TipTap with bold, italic, headings, lists), variable placeholder, image (from TriplyDB), separator, horizontal rule, and spacer
- Blocks dragged from the Content library onto zones; reordering within and across zones by drag
- Image library tab fetches assets from the active TriplyDB dataset
- Documents stored in `localStorage` under `linkedDataExplorer_documentTemplates`; create, rename, delete, and **Save as…** actions
- Export document template as a `.document` JSON file
- Read-only example document pre-loaded: **Kapvergunning Beschikking** (linked to `AwbShellProcess`)

**Files:** `DocumentComposer.tsx`, `DocumentCanvas.tsx`, `DocumentList.tsx`, `ZonePanel.tsx`, `TextBlockEditor.tsx`, `ImageBlock.tsx`, `VariableBlock.tsx`, `BindingPanel.tsx`, `document.types.ts`, `documentService.ts`

#### Variable Bindings

- Bindings panel maps `{{placeholder}}` tokens in rich-text blocks to Operaton process variable keys
- **Discover Variables** button queries `GET /v1/process/:key/variable-hints` for all variables used by completed instances of a given process definition key
- Discovered variables shown as clickable chips labelled with type (`String`, `Boolean`, `Double`, etc.)
- Each binding records placeholder, variable key, source (`process` or `dmn_output`), and optional label

**File:** `BindingPanel.tsx`

#### BPMN Modeler integration

- **Link decision template** dropdown injected into the bpmn-js properties panel for `UserTask` elements (not `StartEvent`)
- Selecting a template writes `camunda:documentRef` to the BPMN XML
- Purple badge (📄) rendered on the canvas below the element, below the existing green form badge
- Badge positioned at `bottom: -36` (vs. `bottom: -22` for the form badge) so both badges are visible simultaneously
- `DocumentTemplateSelector.tsx` follows the identical injection pattern as `FormTemplateSelector.tsx`

**Files:** `BpmnModeler/DocumentTemplateSelector.tsx`, `BpmnCanvas.tsx`

---

### v1.0.1 — Bug Fix & Internal (March 2026)

**v1.0.1 — Bug Fix (March 7, 2026)**

#### Bug fix

Fixed `Task_Phase6_Notify` and `Task_RequestMissingInfo` appearing pre-claimed in the caseworker dashboard. `camunda:assignee="demo"` removed; `camunda:candidateGroups="caseworker"` added to both tasks so they are correctly visible in the task queue.

#### Internal — example file migration and version registry

- Example `.bpmn` and `.form` files moved to `public/examples/flevoland/` as the single source of truth. Inline schemas removed from `bpmnTemplates.ts` and `FormEditor.tsx`.
- Added `exampleVersions.ts` with `EXAMPLE_VERSIONS` record (keyed by example name, value is an integer version). The app compares stored versions in `localStorage` key `linkedDataExplorer_exampleVersions` against `EXAMPLE_VERSIONS` and re-fetches any example whose version has been incremented.
- **Developer workflow:** edit the file in `public/examples/`, mirror the change to `examples/organizations/`, increment the version in `exampleVersions.ts`, commit. Existing users receive the updated example without clearing `localStorage`.

**Files:** `exampleVersions.ts`, `bpmnTemplates.ts`, `FormEditor.tsx`, `public/examples/flevoland/`

---

### v1.0.0 — Form Editor & One-Click Deploy (March 2026)

**v1.0.0 — Major Release**

#### Form Editor

New **Form Editor** view powered by `@bpmn-io/form-js` (schemaVersion 16, MIT licensed). Forms are authored as JSON schema, stored in `localStorage`, and available immediately to the BPMN Modeler.

- Two-panel layout: form list (left) and `@bpmn-io/form-js` editor canvas (right)
- Create, rename, and delete WIP forms; three seed EXAMPLE forms are read-only
- Three built-in examples: `kapvergunning-start` (citizen-facing), `tree-felling-review` (caseworker review), `awb-notify-applicant` (caseworker notification)
- Export individual forms as `.form` JSON files compatible with Camunda Modeler and Operaton
- `FormService` localStorage CRUD shared with the BPMN Modeler — no sync step required

**Files:** `FormEditor.tsx`, `FormCanvas.tsx`, `FormList.tsx`, `formService.ts`

#### BPMN Modeler — Form integration

- **Link to Form** dropdown in the properties panel for `UserTask` and `StartEvent` elements
- Writes `camunda:formRef` and `camunda:formRefBinding="latest"` to the BPMN XML
- `camunda:formRefBinding="latest"` means Operaton always resolves the most recent deployment of that form ID — no version pinning needed
- Green badge overlay on `UserTask` and `StartEvent` elements when a form is linked
- `DmnTemplateSelector` pre-selection bug fixed — dropdown now correctly reflects an existing `camunda:decisionRef` when opening properties for an already-linked element

**Files:** `BpmnCanvas.tsx`, `FormTemplateSelector.tsx`

#### BPMN Modeler — One-click deploy

- **Deploy** button opens a modal listing all resources to be bundled: main BPMN, subprocess BPMNs (resolved via `calledElement` attributes), and all `.form` files referenced by `camunda:formRef`
- All resources deployed in a single multipart `POST /api/dmns/process/deploy` to Operaton — `camunda:formRef` resolves at runtime because BPMN and forms share the same deployment ID
- Configurable Operaton endpoint field pre-filled from `VITE_OPERATON_BASE_URL`
- Optional HTTP Basic Auth credentials per deployment
- Unmatched form references (in BPMN but not in localStorage) shown in modal before deploying
- Deploy button disabled after a successful deployment to prevent accidental re-deploy

**Files:** `BpmnCanvas.tsx` (frontend), `dmn.routes.ts` + `operaton.service.ts` (backend)

---

### v0.9.x — DMN Syntactic Validation (February 2026)

**v0.9.1 — Date Input Validation Fix**

Fixed a false "Missing 1 required input(s)" error in the Chain Composer when a DMN contains an optional `Date` input whose test value is intentionally `null` (e.g. `overlijdensdatum` in `zorgtoeslag_resultaat`).

The root cause was a two-part gap between how RDF stores test data and how the validator tracks input state. In TriplyDB, a `null` value cannot be represented as a `schema:value` triple, so optional date variables have no `testValue` property at all on the `DmnVariable` object returned by the backend. The Fill with test data button in `InputForm.tsx` only wrote a key into the `inputs` state object when `testValue` was defined — silently skipping `null`-default dates. The validator in `ChainBuilder.tsx` then checked `input.identifier in inputs`, found the key absent, and pushed the variable into `missingInputs`.

Two fixes were applied:

- **`InputForm.tsx`** — the Fill button now explicitly sets `Date` inputs to `null` when `testValue` is `undefined`, ensuring the key is always registered in state after filling.
- **`ChainBuilder.tsx`** — the validator now exempts `Date` inputs from the missing-input check when no value is present, consistent with the existing exemption for `Boolean` inputs (which default to `false` without user action). An unset date is a valid input state, not an authoring error.

**v0.9.0 — DMN Validator**

Added DMN Validator feature. The DMN Validator lets you validate one or more DMN files against the RONL DMN+ syntactic layers. It is accessible from the shield icon (🛡) in the sidebar. You can drop any number of .dmn or .xml files onto the validator at once, or add files incrementally — the drop zone remains visible at the top of the panel whenever files are loaded. Files are validated independently and displayed side-by-side for easy comparison.

The validator runs on the shared backend at `POST /v1/dmns/validate` and is used both by this Linked Data Explorer's standalone DMN Validator view and by the CPSV Editor's inline validation in the [DMN tab](../../cpsv-editor/features/dmn-orchestration.md).

### v0.8.x — Governance & Vendor Integration (February 2026)

**v0.8.4 — Vendor Services**

Added vendor service discovery: `ronl:VendorService` resources are queried alongside DMN metadata, surfaced as blue count badges on DMN cards, and displayed in a detail modal with full provider information.

**v0.8.3 — DMN Governance Badges**

Three-state validation badge system using RONL Ontology v1.0 properties (`ronl:validationStatus`, `ronl:validatedBy`, `ronl:validatedAt`). Badges visible in both the DMN list and the Chain Composer. Organisation names resolved via `skos:prefLabel`.

**v0.8.1 — BPMN DRD/DMN Selector**

`DmnTemplateSelector` now loads both locally-saved DRD templates and regular DMNs from the backend, displayed in grouped options. Purple info card for DRDs shows chain composition. Auto-populates `camunda:decisionRef` with prefixed DRD entry-point identifier.

---

### v0.7.x — BPMN Modeler & DRD Templates (February 2026)

**v0.7.3 — DRD Template Linking (partial)**

DMN template dropdown in BPMN properties panel implemented. Exact identifier auto-population working; variable compatibility validation planned for a future release.

**v0.7.2 — DRD Template System**

Users can save DRD-compatible chains as named templates stored in localStorage. Templates are endpoint-scoped. DRD templates load via the new "My Templates" panel.

**v0.7.1 — Semantic Variable Matching Fix**

Fixed `findEnhancedChainLinks` SPARQL query to correctly detect both exact and semantic matches. Heusdenpas chain now shows all 10 variable relationships across 3 DMNs.

**v0.7.0 — BPMN Modeler Foundation**

Full BPMN 2.0 editor using bpmn-js v18.12.0 with official Camunda/Operaton properties panel (`bpmn-js-properties-panel`). Three-panel layout: process list, canvas, properties. Tree Felling Permit example auto-loaded on first visit. localStorage persistence and `.bpmn` export.

---

### v0.6.x — DRD Generation & Enhanced Validation (February 2026)

**v0.6.2 — Semantic Analysis Tab**

Semantic Analysis tab added to Chain Builder. Displays cross-agency variable equivalences and chain suggestions. Backend endpoints: `/api/dmns/semantic-equivalences`, `/api/dmns/enhanced-chain-links`, `/api/dmns/cycles`.

**v0.6.1 — DRD Generation**

Save DRD-compatible chains as single executable DRD files deployed to Operaton. Automatic `<informationRequirement>` wiring, entry-point detection, and deployment ID tracking.

**v0.6.0 — Enhanced Validation**

Validation engine distinguishes DRD-compatible chains (all exact matches) from sequential chains (semantic matches present). Clear UI states: green (DRD), amber (sequential), red (invalid). Separate save paths.

---

### v0.5.x — Multi-Endpoint & Test Data (January 2026)

**v0.5.5 — SPARQL & Export Improvements**

Added "Service Rules Metadata" query (`cprmv:Rule → eli:LegalResource → cpsv:PublicService`). CSV export with timestamped filenames and proper escaping. RDF URI collision fix for `cprmv:Rule` instances.

**v0.5.4 — Multi-Endpoint Chain Execution**

Chain execution now correctly uses the selected endpoint throughout the full execution flow. Automatic test data population from `schema:value` in TriplyDB TTL files. Fallback to `testData.json` for legacy DMNs.

**v0.5.3 — Dynamic Endpoint Selection**

Switch between TriplyDB datasets in real time without page reload. Backend caches DMN metadata per endpoint (5-minute TTL). Connection indicator shows direct vs proxied connection status.

---

### v0.4.x — API Versioning & Export (January 2026)

**v0.4.0 — Backend API v1**

Migrated all endpoints to `/v1/*` following Dutch Government API Design Rules. Legacy `/api/*` endpoints retained with `Deprecation` headers. `API-Version` header in all responses. Chain export as JSON or BPMN 2.0 diagram.

---

### v0.3.x — Chain Builder UI (January 2026)

**v0.3.1 — Bug Fixes**

Enhanced error messages for Operaton failures. Synchronized test data between preset and manual chain. Fixed execution progress visibility on first run.

**v0.3.0 — Chain Builder UI**

Visual drag-and-drop chain builder. Real-time validation with input requirements. Dynamic form generation for DMN inputs. Chain execution with step-by-step progress tracking. In-app tutorial (accessible via ? icon). Deployment metadata display.

---

### v0.2.0 — DMN Discovery & Orchestration View (January 2026)

SPARQL-based DMN discovery using CPRMV vocabulary. Three-panel orchestration view: DMN list, chain composer placeholder, details panel. Real-time search and filter. Input/output variable inspection. Automatic chain detection by variable matching. SPARQL result parsing for multiple query response formats.

---

### v0.1.0 — Initial Release (January 2026)

React-based SPARQL visualisation and query tool. Interactive D3.js force-directed graph. Multiple endpoint support. Query editor with sample library and CORS proxy fallback. SELECT query results table. TypeScript interfaces and Vite build tooling.

---

## Notable backend bug fixes

These fixes are documented here because they involve non-obvious root causes that are likely to recur.

### TriplyDB health check returning HTTP 400

**Root cause:** The health check was calling `axios.get(triplydbEndpoint)` without a query parameter. SPARQL endpoints reject bare GET requests — they require either a POST with a query body or a GET with a `?query=` parameter.

**Fix:** Updated `health.routes.ts` to call `sparqlService.healthCheck()`, which executes a minimal `SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 1` query.

**File:** `packages/backend/src/routes/health.routes.ts`

---

### `/v1/*` endpoints returning 404 after Azure deployment

**Root cause:** The GitHub Actions deployment step used `cp -r dist/* deploy/`, which flattened the compiled output. The `package.json` start script references `dist/index.js`, and `health.routes.js` inside `dist/routes/` uses `require('../../package.json')` — both paths broke when the `dist/` folder was removed.

**Fix:** Changed the deployment step to `cp -r dist deploy/`, preserving the directory structure.

```yaml
# Before (broken)
cp -r dist/* deploy/

# After (correct)
cp -r dist deploy/
```

**Files:** `.github/workflows/azure-backend-acc.yml`, `.github/workflows/azure-backend-production.yml`

---

### Root endpoint referencing deprecated `/api/*` paths

**Root cause:** The `GET /` root response had not been updated when API versioning was introduced, so it still advertised `/api/health` and `/api/` as the documentation and health URLs.

**Fix:** Updated `index.ts` to reference `/v1/*` endpoints in the root response and added a `legacy` block explicitly marking the old paths as deprecated.

**File:** `packages/backend/src/index.ts`

---

## Roadmap

### Frontend — Phase 2

The following items are planned but not yet scheduled. Phase 1 features (v0.1–v0.8) are complete.

**Database migration**

Move chain templates and BPMN processes from `localStorage` to a server-side database. Enables user authentication and ownership, process versioning with history, and public sharing with access control. PostgreSQL is the planned backend, consistent with the RONL Business API stack.

**Collaborative editing**

Multiple users editing shared process definitions. Real-time or optimistic-update model TBD.

**Advanced BPMN properties panel**

Full editing of all BPMN element properties: form fields, execution listeners, input/output mappings, conditional expressions, timers. Currently only name and DMN reference are editable.

**DRD export and versioning**

Export generated DRD XML for versioning and sharing. Track DRD version history alongside template evolution.

**Certification registry**

A queryable view of all `ronl:VendorService` resources with `ronl:certificationStatus "certified"`, enabling cross-service comparison of certified vendor implementations.

**Multi-hop semantic chains**

The current semantic validation checks only adjacent DMN pairs. Phase 2 will extend this to multi-hop: `DMN1 → DMN2 → DMN3` where the connection between DMN1 and DMN3 is bridged semantically through DMN2.

**Semantic concept browser**

UI to explore the `skos:exactMatch` network: graph view of all concepts and their relationships, filterable by DMN or variable type, with search by concept URI.

---

### Backend API — versioning roadmap

**v0.5.0 (planned)**

OpenAPI 3.0 specification served at `/v1/openapi.json`. Request/response validation against the spec. Rate limiting. Per-endpoint response caching layer.

**v1.0.0 (planned)**

Full Dutch Government API Design Rules compliance (API-16, API-51, API-02, API-10). Production-grade monitoring and alerting. Performance target: <800ms for any chain execution. Comprehensive structured error handling across all services.

**v2.0.0 (future)**

Remove all legacy `/api/*` endpoints. Evaluate Dutch naming for business resources (`/v2/besluitmodellen` etc.) per API-04. Enhanced orchestration: parallel chain execution where dependency graph allows. Batch execution support for multiple input sets.