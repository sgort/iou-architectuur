---
component: CPSV Editor
---

# Changelog & Roadmap

---

## Changelog

### v2026.09.6 — The Error Says Why Again, and Previews Stop Outliving Their Pull Requests (September 2026)

> Measured suites: [Testing](testing.md). The backend change this answers: [Linked Data Explorer v2026.09.5](../../linked-data-explorer/developer/changelog-roadmap.md).

**The editor shows the Linked Data Explorer backend's reasons again.** The backend now answers every error as an RFC 9457 problem-details response, with the reason in `detail`. The editor was still reading the older `error.message` envelope, so DMN validation, DMN deployment, SHACL validation and the TriplyDB service update all fell back to generic text instead of saying what was wrong. A shared `getProblemDetail()` in `src/utils/problem.js` now reads `detail` first and still understands the two older shapes — `error.message` and a bare-string `error` — so the editor keeps working against a backend that has not been promoted yet. Each call site keeps its previous fallback for a response that carries no reason. See [Reading the backend's error messages](dmn-implementation.md#reading-the-backends-error-messages-v2026096).

**The DMN tab renders when a DSO import opens it.** The DMN tab is lazy: it renders only once visited, and a visit was recorded only by the tab button's own handler. The DSO import hook was handed the raw `setActiveTab`, so an import from the Linked Data Explorer made DMN the active tab **without marking it visited** — the tab was highlighted over an empty panel until the user clicked away and back. The hook now receives `openTab`, the same handler the buttons use, and the lazy-tab tests cover the deep link.

**Preview environments close from a workflow with no path filter.** Four Static Web Apps previews were still running on acceptance for pull requests closed days or weeks earlier, and four more on production, each serving a public URL with old code and holding one of the ten slots the Standard plan allows. One was left by the deploy workflows' own path filter, which applies to the close event too: a pull request that changed only documentation never started the workflow holding its close job. Both close jobs now live in `close-preview-environments.yml`, which runs on every pull-request close for `acc` and `main`. The other three were pull requests with a merge conflict, for which GitHub starts no workflow at all — so the release procedure now also runs `npm run check-previews`, which lists the environments Azure has against the pull requests GitHub has open and prints the exact delete command for each orphan. Like the mirror check, it never deletes anything itself.

---

### v2026.09.5 — The Install Is Checked Before It Is Trusted (September 2026)

> The mechanism across repositories: [Code Standards — git hooks](../../contributing/code-standards.md). Measured suites: [Testing](testing.md).

**A stale install stops the dev server and the push.** Nothing told a developer that `node_modules` had fallen behind the lockfile: a fast-forward merge brings in lockfile changes and installs nothing. Measured on a workstation on 14 September, 53 packages were installed at a different version from the one the lockfile named, and 86 were missing. `npm start` now runs `npm run deps:check` first — the check the RONL Business API and Linked Data Explorer use — and so does the pre-push hook, before lint and the format check. When stale it names `npm ci`, not `npm install`, so the committed lockfile is installed exactly. It caught exactly that on its first day, stopping a push of the GitLab mirror after this release's dependency updates until `npm ci` had run.

**The last four Semgrep findings are answered in the source.** Every full scan since 11 September had shown four Code findings that were ignored in the Semgrep dashboard, where the reasoning was invisible from the code. Two were prototype-pollution warnings in the iKnow parser's path helpers, which only read and refuse `__proto__`, `constructor` and `prototype` before walking a path; each now carries a suppression scoped to that one rule on that one line, with the reason and the condition under which it stops being true. The other two flagged the `tailwindcss` and `eslint` major-version holds in `renovate.json` for lacking a minimum release age — they inherit the repository-wide 14 days, but the rule checks each package rule on its own and JSON cannot carry a suppression comment, so both holds now state the 14 days themselves. The full scan on `acc` after the merge reported **0 Code findings**.

**Lock-file maintenance no longer waits for a pull-request slot.** It is only eligible inside its Monday window, so it cannot wait for a slot to free, and holding majors for approval could not keep one free: Renovate's concurrency count includes every open Renovate pull request, security fixes included. The lock-file maintenance rule now sets `prConcurrentLimit` and `prHourlyLimit` to `0`, which Renovate reads as no limit for that branch alone. Its first scheduled run moved six packages, all within declared ranges and past the 14-day cooldown.

**Each release checks the GitLab mirror.** `npm run check-mirror` compares the mirror with GitHub and tells *behind* from *diverged* — which a commit count cannot, and which this repository learned the hard way when its GitLab `main` once held commits GitHub had never seen. It runs on a workstation, where the push happens, and prints the fast-forward command rather than running it.

**The supply-chain register follows zizmor.** `zizmor-action` moved to v0.6.3, with its register row moved on the same branch so the required audit stayed green. The register now also says what it had got wrong: Renovate **does** maintain zizmor's own version, mapping the action's `version` input to the `ghcr.io/zizmorcore/zizmor` image — and the zizmor-action bump has to merge first, because the action only runs zizmor versions in its own digest table. `lucide-react` moved to 1.38.0, the only runtime dependency that changed.

---

### v2026.09.4 — The Lockfile Moves, and the Scan Reads Zero (September 2026)

> The mechanism across repositories: [Supply-Chain Pinning — the npm tree](../../contributing/dependency-scanning.md).

**The transitive dependency tree is refreshed every week.** Renovate only ever proposes packages a manifest names; lock-file maintenance, which refreshes everything else in `package-lock.json`, is off by default and **had never been turned on here**. That was the whole explanation for the seven Supply Chain findings v2026.09.3 left open — each had a fixed version inside its declared range, and nothing had ever moved them. It now runs on Monday mornings with `prPriority: 10`, and major updates wait in the Dependency Dashboard for approval so they cannot crowd it out — the lesson the Linked Data Explorer learned first. Security fixes are exempt, so one that happens to be a major version never waits on a click.

**The first refresh took the scan to zero.** It changed 202 entries in `package-lock.json` — 68 moved, 87 added, 47 removed — every one within a range `package.json` already declared, so the manifest is untouched. It closed the last seven Semgrep Supply Chain findings: every copy of `brace-expansion` 1.x to 1.1.18, `picomatch` 2.x to 2.3.2, and `postcss-selector-parser` to 6.1.4. **The scan on `acc` reports 0.** The only dependency of the application itself that moved is `lucide-react`, to 1.35.0.

Three packages behind Vite and jsdom moved *back* a patch version — `rolldown` to 1.2.6, `@oxc-project/types` to 0.147.0, `@csstools/css-color-parser` to 4.2.1. That is the 14-day cooldown working as designed: the newer versions had arrived through a local install on 4 September, were 8 to 11 days old when the refresh ran, and so it resolved each to the newest version past the cooldown.

!!! warning "npm 10 cannot perform that refresh"
    npm 10.9.4, bundled with Node 22, crashes in its resolver on this dependency
    tree — `Cannot read properties of null (reading 'edgesOut')` — on both a fresh
    resolution and `npm update`. npm 11 resolves the same tree cleanly. `npm ci` is
    unaffected, because it only installs from the lockfile, and so is CI, which runs
    Node 24. The failure lands only on a workstation running Node 22 that tries to
    add or update a package, which is why the README now says to use **Node 24 /
    npm 11**.

---

### v2026.09.3 — Semgrep in the Gate, and Two Hardened Parsers (September 2026)

**Semgrep scans dependencies and code in CI, on a ref rather than a laptop.** The three controls this repository already gated on — build provenance, supply-chain pinning, the coverage floor — say nothing about the packages in `package-lock.json`. `check-supply-chain` verifies GitHub Actions pins and does not look at npm at all. Renovate had been doing the remediation and nothing was verifying it. The new `scan` job runs Semgrep Code and Supply Chain on every pull request and every push to `acc` and `main`, and is a **required check on `acc`**, alongside `audit`.

The second reason is the one that prompted it: **a scan run by hand is pinned to whatever happens to be checked out**, and nothing in its output names the commit. A triage run that way reported 36 findings against a tree 51 commits behind `acc`; the real number on the branch head was 17, Renovate having already closed the other 19. A scan in CI cannot make that mistake.

It is a separate workflow rather than a step in the existing `audit` job, so promotion to a required check was a ruleset change rather than a file change; and it runs with `--no-suppress-errors`, because the default prints *"there were errors during analysis but Semgrep will succeed"* and exits 0 — which is exactly how a broken local install went unnoticed.

**Two scoping rules for the scan**, each for a reason worth keeping:

- **`/examples/` is out, with its leading slash.** Root `examples/` is reference material — three findings came from a standalone documentation artifact and an archived demo of an unrelated project — while `public/examples/` is served at runtime and stays scanned. A bare `examples/` matches a directory of that name at any depth and **silently dropped a served file from the scan**, caught only by diffing the scanned file lists; the finding counts agreed either way.
- **Test files are out of Code scanning.** Four of sixteen findings were test files tripping two rules — reading a fixture means `path.resolve`, asserting on generated text means a RegExp built from a variable — and the set grows with every test that does either. Secrets scanning keeps its own ignore list and still covers them. Semgrep has no per-rule path setting, so the narrower fix would have meant forking two registry rules to maintain against upstream drift.

**Two latent parser defects, fixed where they live rather than where they are currently called from** — see [Vendor Integration](../features/vendor-integration.md#iknow-integration):

- **iKnow replace-transform patterns are bounded before they compile.** `applyTransform` compiled a mapping config's `transform.pattern` straight into a RegExp. A pattern shaped like `(a+)+` can run effectively forever on a non-matching subject of a few dozen characters — on the main thread, in the browser. A quantified group containing a quantifier is now refused, and so is any pattern over 200 characters, a backstop precisely because the first check is a heuristic. **Rejection throws** rather than skipping the transform, because silently wrong output is worse than a visible configuration error.
- **iKnow mapping paths refuse prototype segments.** `setNestedValue` creates missing objects as it walks, so a target field of `__proto__.polluted` wrote straight to `Object.prototype`. Neither function was reachable — every production call site passes a bundled config — but that is a property of today's wiring, not of the functions, and the mapping tab already parses a user-supplied config into its editing state.

**No stub `cprmv:id` over a rule the document already publishes.** A citation target of `cprmv:isBasedOn` gets a minimal typed stub so it satisfies `sh:class cprmv:Rule` — but when the target is a rule the same document emits in its own Rules section, the stub asserted a second, contradictory `cprmv:id`. Observed rather than hypothesised: twelve of the normenbrief export's 216 `cprmv:Rule` subjects carried two. See [Cell-Level Grounding](cell-level-grounding.md).

**Two new example models, each with a live test suite.** *PW Normbedragen* gains the second-half-2026 bijstandsnormen — all twenty amounts from the CPRMV norms API rather than a transcription, closing a hole where any peildatum in 2026-H2 answered with a null bedrag — with 80 cells grounded in the norms this project publishes and a 121-case suite. *Den Haag ALO*, the third pass in the Amsterdam / SZW series, turns a nine-decision DRD written against an object model, which no DMN engine can evaluate, into a deployable model with a 62-case suite. Publishing it exposed a gap no test had: nothing named the RechtOpALO decision as a case's own decision, so the published vocabulary omitted the model's central intermediate concept — three cases that do took the suite to 65. The whole route, across all three passes, is on [DMN to Linked Data Workflow](../user-guide/dmn-workflow.md).

**E2E journeys can drive an already-deployed build.** `E2E_BASE_URL` points them at a deployed app instead of a local dev server, and drops the `webServer` block so none is started. **Both deployed environments share one Operaton engine**, so a run against acceptance deploys real decision versions into the engine production evaluates against — see [Testing](testing.md#end-to-end-journeys-p7). A third journey, `normbedragen-journey`, drives one chained deployment through four evaluations.

**Two example files recovered from the GitLab mirror**, where they had existed on no GitHub branch at all — the recovery that preceded [reconciling the mirror](../../contributing/the-gitlab-mirror.md).

---

### v2026.09.2 — The Branch Floor Goes Native (September 2026)

> Measured inventory and commands: [Testing](testing.md). Cross-repository posture: [Coverage Floor](../../contributing/coverage-floor.md).

**`DMNTab.jsx` was the last file below the per-file 80% branch floor, and the script carrying the exemptions is deleted.** The largest file in the repository at 1855 lines went from 45.73% to **98.34%** branch coverage (415/422), measured identically in isolation and in the full suite — which is the property that matters, because a per-file figure read only from a full run cannot tell whether another file's tests are propping it up. Four new suites cover the test-case batch runner, DRD parsing and the intermediate runner, the import and example lifecycles, and the validation panel. Reaching the later stages means walking the whole chain — upload, validate, deploy, evaluate — because each stage gates the next stage's controls.

With nothing left to exempt, `scripts/check-branch-coverage.mjs` is gone and the policy is four lines of config: `thresholds: { branches: 80, perFile: true }`. **That the native threshold actually gates was proved by raising it to 99 and watching it name eight files** — a green run proves nothing about a check that might be silently inert.

**Formatting is now checked in CI, not only on a developer's machine.** `check-format` was enforced by the pre-push hook alone, so the rule held locally and not on the shared branch. That gap is not theoretical: in the Linked Data Explorer a Prettier 3.7 → 3.9 bump changed how short union types are formatted, and five untouched files began failing `prettier --check` the moment it merged, with every CI check green. The symptom would have been the next person's `git push` failing on files they had never opened.

The step goes in the **`audit` job**, not the deploy workflows — those carry `paths-ignore` for `docs/**` and `**/*.md`, deliberately, so a documentation change does not claim one of ten staging environments; a formatting check placed there would never see markdown, which is precisely what drifts, since `lint-staged` only formats `src/**` and `package.json` on commit. That job had no `npm ci` at all until now, because zizmor is an action, the Renovate validator runs from `npx`, and `check-supply-chain` is plain node. Prettier needs `node_modules`, and it has to be **this repository's** Prettier rather than a version named in the workflow — a second pinned version is a second thing to keep in step, reintroducing the drift the check exists to catch.

**The four heavy tabs are lazy-loaded**, taking the entry chunk from 685.71 kB to **392.74 kB** (176.58 → 104.71 kB gzipped) and clearing both build warnings. The `lazy()` calls turned out to be the smaller half: a static re-export in the tabs barrel pins a module into the entry chunk even when `App` imports it dynamically, and measuring before designing showed it — with `ChangelogTab` left in the barrel, adding `lazy()` moved nothing at all. `DMNTab` needed more still, because it stays mounted while hidden so an uploaded file, deployment status and test-case results survive tab switches; it now renders once its tab has been visited and stays mounted thereafter, with each lazy tab getting its own Suspense boundary so one re-suspending cannot blank the always-mounted DMN subtree.

**The unit suite no longer reaches TriplyDB**, which was making coverage depend on the machine. `useEditorState` fetches the RONL concept vocabularies on mount, so every test rendering `App` made a live request — and whether it came back before the test ended decided whether the effect's continuation ran at all. The same commit and the same tests measured `useEditorState.js` at 83.33% locally and 50% on CI, and the per-file floor read the local number while CI failed on the merge. **The floor was honest; the measurement it was pinned to was not.** `setupTests.js` now stubs the fetch suite-wide.

**Each tab words its own RONL fetch failure.** One sentence was stored centrally and shown verbatim in two places, so the Vendor tab reported a failure to load *concepts* directly above its own "Loading vendors…" line. `useEditorState` now reports *that* the fetch failed rather than *how to say so* — a string becomes a boolean. Both existing tests were asserting the wrong thing; the Vendor test checked for a string the test itself invented and passed in as a prop, so it asserted that the component rendered whatever it was handed, matching the defect rather than catching it.

**`PublishDialog` is mounted only while it is open.** It had been mounted permanently and hid itself with an early return, so its state survived every close — and three pieces of machinery existed only to undo by hand what unmounting does for free, two of them needing lint suppressions to pass.

**The lazy-tab guard recognises both Babel majors' dynamic-import AST.** `no-eager-tabs.test.js` knew only `@babel/parser` v7's representation of `import()`, so under v8 it stopped recognising dynamic imports entirely — finding no lazy bindings and no stray imports, going blind to the property it exists to check. v7 emits a `CallExpression` with an `Import` callee; v8 an ESTree-aligned `ImportExpression`. Both shapes are now pinned with literal AST fixtures, because a parsing check can only ever exercise whichever parser is installed, which is exactly how the defect shipped.

**Also in this release:** `importHandler` comes off the debt list at **100%** (132/132 branches) from zero unit tests; `ttlGenerator` from 60.49% to 81.66%; `PublishDialog`, `App` and `IKnowMappingTab` all clear the floor; the DMN request-body generator is pinned precisely; and `@babel/parser` v8 and `lucide-react` v1.34.0 land verified on the merged tree.

---

### v2026.09.1 — Create React App Is Gone (September 2026)

> The migration's four phases, and what each proved: [Testing](testing.md#the-vite-migration).

**The Vite migration completed in four phases, each independently revertable, in an order chosen so a working test suite exists at every point.** `react-scripts` provided both the build and the test runner, so swapping the build first would have removed the regression net and the thing being tested at the same moment — leaving no way to tell a migration defect from a configuration defect.

**Phase 1 — Vitest alongside Jest.** Both runners reported the same 16 suites and 257 tests. Three files were renamed to `.jsx`, the only ones carrying JSX in a `.js` extension: Vite has never parsed JSX out of that extension and under Vite 8 there is no configuration escape hatch.

**Phase 2 — Vite builds alongside Create React App.** Still additive: `react-scripts` owned the build and CI still published `build/`. The two toolchains genuinely coexist, since Create React App reads `public/index.html` and Vite a new root `index.html`. Output was compared rather than assumed — the same eleven public assets in both, one main chunk each within a kilobyte of the other. Two differences are deliberate: Vite does not publish sourcemaps, and an `apple-touch-icon` that has 404'd in both builds for as long as the template has existed was carried over verbatim rather than quietly fixed inside a toolchain migration.

**Phase 3 — the atomic cutover.** The only phase that cannot be half-done: the build now emits `dist/` instead of `build/`, so the deploy workflows had to expect `dist/` in the same commit. `react-scripts` is gone and its dependency tree with it — **`npm audit` dropped from 52 vulnerabilities to 10**, and production builds from roughly 30 seconds to under two.

!!! warning "Two things the plan did not cover, both of which would have deployed green and broken"
    The workflows pass the backend URL through an `env` block, and **Vite only exposes `VITE_`-prefixed variables** — renaming the call sites alone would have left both environments talking to `localhost`. And `react-scripts` was where ESLint itself came from, so removing it would have broken the lint step that runs before the tests.

**Phase 4 — the shims are gone.** Both transitional shims that carried the suite across the migration are removed, and the Vitest setup file folded back into one. Three corrections to the plan came from testing rather than reading: there were 45 `jest` call sites, not the 43 counted, because both counts came from a pattern that missed two wrapped across lines; and only one of three Renovate deferral rules was actually removable, the constraints having changed owner rather than disappeared.

**ESLint 9 flat config, and `eslint-config-react-app` dropped.** It was carrying more than its rules: it pinned ESLint to 8, which is end-of-life; it pulled `babel-preset-react-app`, whose `@babel/plugin-transform-runtime@^7` was the last thing holding `@vitejs/plugin-react` at v5; and it contributed three Flow rules to a repository with no Flow. The rule set was chosen from measurement rather than a guess — a candidate config reported 100 errors, of which 63 were missing globals *in the candidate itself* rather than findings.

**Every form control is now associated with its label.** 102 form controls had no `id` and one `htmlFor` between them, and 38 had **no accessible name at all** — no label association, no `aria-label`, not even a placeholder. In a government authoring tool that is a WCAG 1.3.1 and 4.1.2 gap independent of testing, and `eslint-config-react-app` never enabled the rule that would have flagged it. The codemod that fixed it introduced a real defect first: `VendorTab`'s access-type radios are nested inside their labels, and pairing them walked past a label's own radio to the next one, leaving the *Fair Use* label pointing at the *IAM Required* radio. That passed the lint rule, because a `htmlFor` did exist — only computing the accessible name at runtime caught it.

**P5, P6 and P7 landed, completing the testing roadmap.** P5 gave every tab component, `PreviewPanel` and `PublishDialog` smoke coverage, moving `src/components` from 3.9% to 41%; P6 covered `DMNTab`'s validate → deploy → evaluate lifecycle, walking the real order because the interface enforces it; P7 added two Playwright journeys against a live stack. See [Testing](testing.md) for the measured inventory.

**The Changelog tab shows the build id** — see [Build Provenance](../../contributing/build-provenance.md). Version headings come from `package.json` and are bumped by hand, so they identify a release but not a build of it. The tab now shows the commit SHA and workflow run number beneath the heading, reading `local build` when nothing was injected.

**`check-supply-chain` shipped**, the preflight zizmor cannot be: zizmor validates that a pin *has the shape* of a 40-character SHA but cannot confirm it is the right one, so a wrong or hostile digest carrying a plausible version comment passes zizmor, Prettier and human review alike. It resolves every digest against the GitHub API and compares the register with the workflows — and a fix in the same release taught it that an action can legitimately be pinned at **two** digests mid-upgrade, a case neither visible nor reproducible in this repository. See [Supply-Chain Pinning](../../contributing/supply-chain.md).

---

### v2026.09.0 — The Gate Widens, the Tree Settles, Vite is Planned (September 2026)

> Cross-repository treatment of the gate: [Supply-Chain Pinning](../../contributing/supply-chain.md).

**The supply-chain audit now runs on every pull request, and the old shape was hiding a pull request that could never merge.** The audit triggered on `pull_request` only for `acc` and `main`. Combined with the ruleset that makes `audit` a required check on `acc`, that produced a genuinely nasty failure: a *stacked* pull request — one based on a feature branch rather than on `acc` — matched no trigger, so it accumulated no audit at all, and because the ruleset applies only while the base **is** `acc`, GitHub reported it as **CLEAN with zero checks**. It read as ready and was not. The moment its parent merged, GitHub auto-retargeted the child onto `acc`, the ruleset began applying, the required check was missing, and the pull request blocked permanently — a retarget emits no `pull_request` event, so nothing ever backfilled it. The `branches` filter is gone. The file already carried the same argument one dimension over, in its reasoning for having no `paths` filter: a path filter lets a pull request skip the gate by touching nothing watched, and a branch filter lets it skip by targeting a base that is not watched. `push` stays filtered to `acc` and `main`. The rule the workflow now states for itself is **audit widely, deploy narrowly**.

**`renovate.json` is validated inside the audit gate.** The gate enforced that every action reference is a commit hash but had nothing to say about the file that keeps those hashes current — and pinning without automated updates decays into an unpatched tree, so a Renovate that has silently stopped running is exactly the kind of supply-chain failure the audit exists to catch. It is not hypothetical: in the Linked Data Explorer, five keys used as JSON comments were rejected as invalid configuration and Renovate stopped opening pull requests as a precaution, while nothing in CI noticed and the repository looked green with half its policy inert. The validator runs as a second step of the existing `audit` job, so it is covered by the current required status check without touching the ruleset, and it runs `if: always()` so one run reports on both halves of the policy rather than the first failure hiding the second. It runs with `--strict`, which also fails on configuration Renovate would silently auto-migrate. It is invoked with no filename argument on purpose — passing one switches the validator into global-config mode, which applies different rules than the repository config the file actually is.

**The validator runs on the Node version Renovate requires.** Renovate declares `engines.node ^24.11.0` and the runner defaults to Node 22. npm accepts that mismatch with a warning rather than refusing, so the validator ran unsupported and reported green — the kind of mismatch that keeps working right up until it abruptly does not, at which point the gate fails for a reason unrelated to anything anyone changed. A `Set up Node 24` step now precedes it, reusing the `setup-node` digest the repository already pins so Renovate maintains one pin rather than two. It is placed *before* the zizmor step deliberately: a step following a failed one is skipped, so putting it after would leave the validator's `always()` condition running on whatever Node the runner happened to default to.

**Documentation-only changes no longer claim a staging slot.** Both Static Web Apps workflows deployed on every pull request regardless of what changed, so a two-file documentation change claimed a staging environment and returned nothing for it. They are now filtered with `paths-ignore` — `docs/**`, `.claude/**` and `**/*.md` — rather than with `paths`. The direction matters: an allowlist would mean enumerating every path that affects the build, and this is a single package rather than a monorepo, so there is no natural boundary to enumerate. Anything forgotten from such a list *silently skips a deploy*, which is a considerably worse failure than one unnecessary preview. The default stays deploy.

**The deploy workflows are named after the environments they deploy.** Both were called `Azure Static Web Apps CI/CD` and both their jobs `Build and Deploy Job`, so in the Actions list, in a pull request's checks, and in `gh run list`, a run against production looked identical to one against acceptance — telling them apart meant opening the run and reading which API token it used. They are now `Deploy ACC (orange-beach)` and `Deploy PROD (white-sky)`. Names only: triggers, permissions, action pins and every step are untouched. Renaming a job renames the check it reports, which is why it was worth doing *before* any deploy check is ever made required.

**Renovate is capped at five concurrent pull requests.** Its default `prConcurrentLimit` is ten, and the Static Web Apps staging ceiling is also ten. The two numbers being equal meant a full Renovate queue consumed every staging environment and the next pull request opened by a human was refused outright — not hypothetical: ten open dependency pull requests held all ten slots, and two unrelated pull requests had their deploy fail on arrival. It self-perpetuated, too, since merging two freed two slots and Renovate opened two new pull requests into them within the minute. Capping at five leaves five permanently available for human work. Deliberately not solved by raising the tier: a higher ceiling moves the number at which the same collision happens rather than removing it.

**The merge method is enforced by repository settings rather than by remembering.** The previous rule said *never squash* and missed that rebase-and-merge rewrites hashes just as thoroughly — deceptively so, since it preserves the commit count while replacing every hash. Either one orphans the commit SHAs a changelog entry names. Squash and rebase are now disabled repository-wide, leaving merge commits only, so the failure is impossible by construction rather than forbidden by prose. GitHub's default button is *Squash and merge*, so without the setting a single absent-minded click would orphan a release's entire entry. A side effect is that Renovate's dependency pull requests land as merge commits too, which costs nothing here — `--no-merges` already excludes the merge commit from the changelog range, and the underlying update commit is what an entry should name anyway.

**The release process verifies the working branch is gone from the remote.** Merging with `--delete-branch` removes both copies, and the repository deletes branches on merge, so there is normally nothing to do — but a release merged some other way leaves the remote branch behind, and one survived exactly that way and was noticed only later. A stale merged branch is harmless alone; they accumulate, and each one makes it harder to see which branches are genuinely in flight, which is the question the next release's first step has to answer.

**Dependency majors were taken deliberately, and two were deliberately held.** `actions/checkout` and `actions/setup-node` moved to v7 (digest-pinned, as the policy requires), Node in the deploy workflows to v24, React to 19.2.8, `lucide-react` to v1.33.0, `@testing-library/jest-dom` to 7 and `user-event` to 14, `lint-staged` to v17, `eslint-plugin-simple-import-sort` to v14, plus `prettier`, `postcss` and `autoprefixer`. The `lint-staged` major was verified rather than assumed — a deliberately misformatted file was staged and the hook run directly, confirming Prettier and ESLint both still execute and re-stage their output. The `user-event` 13→14 bump is normally the breaking one, since v14 made the API async and introduced `setup()`, but no file in `src` imports it: it arrived with the Create React App template and was never used, which is also why it is slated for deletion. **Tailwind v4 and TypeScript v7 are held until the Vite migration**, each with the reason recorded inline in `renovate.json`. Tailwind v4 moves its PostCSS plugin to a separate package and needs the configuration rewritten — throwaway work under Create React App, since the Vite setup replaces the PostCSS wiring rather than porting it. TypeScript v7 cannot resolve at all: `react-scripts@5.0.1` peer-requires `typescript ^3.2.1 || ^4`, so Renovate's lockfile generation failed and the pull request shipped a `package.json` bump with no lockfile. Only the majors are held; minor and patch updates continue to flow, and both rules are written to be removed as part of the migration.

**Stored line endings are normalised.** The repository stored 263 text files with LF and two without — one workflow with CRLF throughout and one XML example with mixed endings — and nothing declared which was intended, so a file's form depended on which tool last wrote it. Editing the CRLF workflow with a tool that writes LF turned a three-line change into a seventy-four-line diff, which is how it was noticed. `.gitattributes` now sets `* text=auto` to normalise the *stored* form, and declares binary extensions explicitly rather than leaving them to content sniffing. Checkout is deliberately left alone — there is no `eol=lf` — so `core.autocrlf` still decides what lands in the working tree and nobody's editor behaviour changes. The renormalisation changes no content.

**The Create React App to Vite migration is planned.** Create React App was deprecated in February 2025: it still builds, but receives no new features, no performance work and no active security updates, which sits badly in a repository that spent August enforcing that nothing a pipeline downloads may float. The plan is written against measurements rather than assumptions — the acceptance criterion is the existing suite passing under Vitest and the built site behaving identically, explicitly *not* "does it build", because a Vite build pointed at the wrong output directory succeeds and publishes nothing. Scope was counted rather than estimated: env-var uses, `process.env` references, `%PUBLIC_URL%` occurrences, `jest.*` call sites and test scripts were each enumerated. Four phases are ordered so a working test suite exists at every point, because `react-scripts` provides both the build and the test runner — removing it takes away the regression net and the thing being tested at the same moment. See [Testing](testing.md#roadmap) for how the existing P0–P4 suite serves as that net.

---

### v2026.08.3 — Releases Land Through a Pull Request (August 2026)

> How the gate itself works: [Supply-Chain Pinning](../../contributing/supply-chain.md).

**A release is now cut through a pull request, not a local fast-forward.** The `acc` branch gained a ruleset requiring a pull request and a passing `audit` check, so the previous release flow — `git checkout acc`, `git merge --ff-only`, `git push` — is rejected outright: a locally created bump commit has never been through CI. `/bump-release` now pushes the working branch, opens a pull request against `acc`, and lets the human merge it; merging *is* the push, so the separate "shall I push?" step is gone. Five further corrections came out of cutting v2026.08.2 as the first release under the gate, each found by running it rather than by reasoning about it: `--no-merges` in the commit range, since pull-request landing puts a merge commit in every range; computing that range only *after* the branch is up to date, because rebasing rewrites the very SHAs the entry records; a new first step that reconciles open pull requests before any version editing, because dependency updates rewrite the same lockfile the version bump edits; `ci` added to the recognised commit types; and a rule that a source change the entry depends on must be committed *before* the bump, since the bump commit is the boundary marker `git log --grep` searches for and is never listed in its own entry.

**Release pull requests are merged, never squashed.** A changelog entry names each commit by its SHA. Squashing a release pull request collapses them into one new commit, leaving every citation in the entry pointing at commits that do not exist on the target branch. Renovate's dependency pull requests are the opposite case and *should* be squashed — each is a single change, and no entry names its constituent commits. The rule is therefore not "never squash" but "never squash a pull request whose commits a changelog entry names".

**`postcss` 8.5.23 — a published security advisory, and the first proof the fast lane works.** Renovate raised this through its `vulnerabilityAlerts` path, which sets `minimumReleaseAge: null` and so overrides the 14-day cooldown: the pull request carried no minimum-release-age check at all, while the `tailwindcss` 3.4.19 update in the same release went through the cooldown normally. That contrast is the first end-to-end confirmation that the no-cooldown security lane behaves as designed — GitHub advisory alerts feed Renovate, the cooldown is bypassed for those alone, and the update is still gated by the blocking supply-chain audit before it can merge. It is the rule most cooldown policies omit, and its absence is why such policies get disabled mid-incident.

---

### v2026.08.2 — Supply-Chain Pinning: the Gate Gets Teeth (August 2026)

> Full cross-repository treatment: [Supply-Chain Pinning](../../contributing/supply-chain.md).

**Nothing a pipeline downloads or executes may float.** Following IOU's post-incident policy, every `uses:` reference in both Azure Static Web Apps workflows is now a 40-character commit digest with a trailing `# vX.Y.Z` comment — `actions/checkout` at `a37ce91…` (v3.7.0), `actions/setup-node` at `49933ea…` (v4.4.0), `Azure/static-web-apps-deploy` at `4d27395…` (v1). Pins were taken at the *then-current major and not upgraded*, so adopting the policy was behaviour-preserving; version upgrades arrive separately as reviewed Renovate pull requests. `github.com/ictu` enforces this at organisation level, but these repositories live under `github.com/sgort` with GitLab as the code host and inherit none of it, so enforcement is built inside the repository, where it travels with the code regardless of which remote hosts it. This repository is the **pilot**; `ronl-business-api` has since followed.

**The `@v1` ambiguity, and why it mattered here specifically.** `Azure/static-web-apps-deploy` publishes `v1` as *both* a 2021 tag (`1a947af…`) and a 2024 branch head (`4d27395…`) 28 commits ahead, so `@v1` named two commits 3.5 years apart and GitHub does not document how it resolves the collision. The bounded risk becomes sharp in a two-environment setup: the `acc` and `main` workflows resolve the same ref *independently, at their own run times*, so a ref moving between an acceptance deploy and the later production deploy would send different action code to each environment from identical repository content — leaving no trace in git history, and quietly ending acceptance's status as a faithful rehearsal of production. The branch head was chosen on evidence, not inference: the executed surface (`action.yml`'s `runs:` block, the `Dockerfile`, `entrypoint.sh`) is byte-identical at both candidates, a real Actions run log shows GitHub resolving `v1` to the branch, and the branch declares a strict superset of inputs.

**`GITHUB_TOKEN` scoped down, and a live credential removed from a third-party container.** Both workflows now default to `permissions: contents: read`; `build_and_deploy_job` adds only `pull-requests: write` for the deploy action's PR comments, and `close_pull_request_job` takes an empty `permissions: {}` block. `actions/checkout` sets `persist-credentials: false` — previously a live workflow token was written into `.git/config` and mounted into a closed-source third-party container on every run. That is a real hole closed, not a lint fix; the deploy action authenticates with explicitly passed tokens instead.

**A blocking supply-chain audit.** A new `Supply-chain audit` workflow runs [zizmor](https://github.com/zizmorcore/zizmor) on pull requests and pushes to `acc` and `main`, under job name `audit`. Its own action reference is digest-pinned and its `version` input is pinned to `1.29.0` rather than the action default of `latest` — an unpinned tool inside the gate that forbids unpinned things would defeat itself. It landed only *after* the tree already reported zero findings, so the gate arrived green rather than red. Measured adoption: **16 findings → 0**, verified at every intermediate step (8 `unpinned-uses`, 6 `excessive-permissions`, 2 `artipacked`). A workflow that runs but cannot block is advice, so the `acc supply-chain gate` ruleset makes `audit` a required status check *and* requires a pull request — the status check alone would still let a direct push bypass it. There are no bypass actors: the gate applies to the owner and to releases alike.

**`.github/zizmor.yml` states the policy in the repository.** `unpinned-uses` is configured with policy `'*': hash-pin` — a commit hash for every namespace, with no exemption for first-party `actions/*`. zizmor 1.29.0 already enforces this by default, so the file changes no findings today; it is committed deliberately, so enforcement does not depend on a tool default that a future release could quietly relax.

**Renovate keeps the pins alive, under a cooldown with an advisory bypass.** `renovate.json` extends `helpers:pinGitHubActionDigests` (which maintains the digest *and* rewrites the version comment Renovate parses), sets `minimumReleaseAge: "14 days"` with `internalChecksFilter: "strict"` so a pull request is suppressed entirely until the age is genuinely met, and adds a `vulnerabilityAlerts` rule with `minimumReleaseAge: null` for security advisories. Renovate raises its pull requests against `acc` like any contributor, so **the bot's own pull requests are gated by the policy the bot maintains** — observed on the first two, with `audit` passing in 11–13 seconds. One dependency is exempted: Renovate's `github-tags` datasource resolves `Azure/static-web-apps-deploy@v1` to the 2021 *tag* while the workflows pin the *branch*, so a routine-looking digest update would have silently reverted the production deploy step to 3.5-year-old code — against which the 14-day cooldown offers no protection at all, the target commit being years old.

**`SECURITY-PIPELINE.md` records what cannot be pinned.** A register that claims total coverage produces a permanent unfixable finding at the first audit, and the predictable response is to weaken the gate. The primary entry: `Azure/static-web-apps-deploy` is a three-line wrapper whose `action.yml` declares `runs: using: docker, image: "Dockerfile"`, and that Dockerfile is `FROM mcr.microsoft.com/appsvc/staticappsclient:stable`. Because `skip_app_build` is not set, Oryx runs *inside* that floating image and builds the production bundle there — making it the build toolchain that produces the deployed artifact, not merely an upload step. Pinning the action makes the wrapper immutable and leaves the payload floating. A final review corrected two further understatements: the container exception had been described as an upload step, and the register had claimed blanket Renovate coverage when the zizmor version pin is an *action input*, which Renovate does not parse and which must be bumped by hand — a `Maintained by` column now separates automated pins from manual ones.

**The gate caught a real breakage on its first live run, and the failure is instructive.** During review, `token: ''` was added to the zizmor action as optional least-privilege hardening. Every local check passed — zizmor reported zero findings, Prettier was clean, two independent reviews approved — and in CI it failed in seven seconds with `error: invalid value '' for '--gh-token <GH_TOKEN>'`. The action passes the input as an environment variable and zizmor's `--gh-token` is env-backed through clap, which distinguishes *unset* (fine) from *set-but-empty* (rejected) at argument parsing, before any audit runs; `online-audits: false` does not avoid it. The default was restored — it is scoped to `contents: read` and mounted read-only, so the exposure removed was negligible — with a comment recording the failure so the same hardening is not retried. Three lessons stand: the only change with no functional justification was the one that broke it, everything load-bearing worked first time; it was invisible to local tooling by construction, since zizmor validates format and Prettier validates syntax and neither executes the action; and static analysis proves a configuration is well-formed, never that it runs.

**`bump-release` no longer uses `npm version`, which mangles CalVer.** npm coerces its argument to strict SemVer, and a zero-padded CalVer month is not a valid numeric identifier — so `npm version 2026.08.3` silently writes `2026.8.3`, with no flag to disable the coercion. The release step now spells out editing `package.json` and `package-lock.json` by hand, naming the exact keys (`version` and `packages[""].version` in the lockfile).

**The lockfile is versioned too, closing 35 entries of drift.** No release had ever touched `package-lock.json`, so through v2026.08.1 it still carried `0.1.0` from the initial commit while `package.json` had moved on across 35 changelog entries. The drift was never fatal — `npm ci` validates dependency satisfiability rather than the root `version` field, and exits 0 either way — but the lockfile is what CI installs from and what audit, SBOM and provenance tooling reads, so all of it reported the wrong version.

**`ci` becomes a first-class changelog type.** The in-app changelog renderer had no `ci` type, so pipeline and supply-chain commits fell through to the generic `other` icon. This release alone carries four of them, and the repository now does enough CI work for the distinction to be worth drawing.

**Dangling `docs/` references repointed at this site.** Earlier commits deleted the repo-side testing and namespace documentation, but references to those paths survived in the source. The IOU Architecture documentation site is the single source of truth for them, so the references now point here directly rather than at paths that no longer resolve. The README's claim that the `docs/` directory had been removed was corrected at the same time: product documentation lives on this site, while `docs/` now holds engineering records that belong beside the code.

---

### v2026.08.1 — Deploys Gated on the Test Suite (August 2026)

> Full inventory, commands and coverage: [Testing](testing.md).

**Both deploy workflows now run lint and the full test suite before deploying, and a failure blocks the deploy.** Neither Azure Static Web Apps workflow previously ran anything of this repository's own: the deploy action builds inside its own container and invokes none of the project's scripts, so both went from checkout straight to build-and-deploy. With `pre-push` gating only `lint` and `check-format`, nothing anywhere stopped a deploy that broke the suite. Both workflows now carry an explicit Node 20 setup, `npm ci`, `npm run lint` and `npm run test:ci` ahead of the deploy action — covering `acc` (orange-beach) and `main` (white-sky) alike. Measured before wiring: 16 suites, 257 tests, all passing.

**Repo-side test documentation is retired in favour of this site.** `docs/TESTS.md` (333 lines) and `docs/TESTING-GUIDE.md` (188 lines) are deleted. [Testing](testing.md) is the single source of truth for the suite, and the repo-side copies had drifted from what the tests actually do.

**The Changelog tab label loses a stray exclamation mark.** An earlier commit changed the label from `Changelog` to `Changelog!` with nothing else in that commit touching it and no test asserting on it; it read as an accidental edit rather than deliberate copy, and is reverted. The two changes cancel out within this release, so there is no net change for users.

---

### v2026.08.0 — Cell-Level Legislative Grounding & Backend-Routed DMN Calls (August 2026)

> Full deep-dive: [Cell-Level Legislative Grounding](cell-level-grounding.md).

**Legislation is now linked at decision-table cell granularity.** DMN's native `knowledgeSource` links legislation at *decision* level, and CPRMV's `extends`/`ruleType`/`confidence` at *rule* level — neither can express that one cell of one rule rests on one specific article. Three layers close that gap. In the DMN, `<inputEntry>`/`<outputEntry>` elements carry `dct:source`, `cprmv:sourceQuote` and `cprmv:isBasedOn` attributes, with a numbered family (`dct:source1`, `cprmv:sourceQuote1`, …) for compound cells whose conjuncts each need their own citation. `extractRulesFromDMN` in `dmnHelpers.js` reads every cell's id, FEEL text and groundings into `rule.inputEntries`/`outputEntries`. `generateDmnSection` in `ttlGenerator.js` then emits a `cprmv:hasPart` list of per-cell `cprmv:Rule` resources on each `DecisionRule`, deduplicating minted concepts and nesting a further `hasPart` for compound cells.

**A namespace-agnostic DOM lookup, fixing a defect that predates cell grounding.** Building Layer 2 surfaced that every selector-based DMN lookup silently matched nothing against a real, `dmn:`-prefixed file: CSS type selectors match on (namespace, local name), and an unprefixed selector implies the null namespace. Cell-level grounding — and the pre-existing rule-level export — therefore never actually worked for real DMN files. New `queryAllLocal`/`queryLocal` helpers match on local name regardless of prefix.

**Cell-grounding resources are SHACL-conformant.** Live validation against a published `.ttl` surfaced two `RuleShape` violations. `cprmv:id` is required (`sh:minCount 1`) on every `cprmv:Rule`, but cell resources emitted `dct:identifier` — a property that shape does not check at all — and concept resources carried no identifier whatsoever; both now emit `cprmv:id`, including compound-cell sub-resources. And `cprmv:isBasedOn` has `sh:class cprmv:Rule`, so its object must itself be typed `cprmv:Rule`: concept targets already were, but a bare external citation URI (CVDR, `wetten.overheid.nl`) was not. Every distinct citation URI referenced via `isBasedOn` now gets a minted, deduplicated stub — `<uri> a cprmv:Rule ; cprmv:id "<uri>" .`

**DMN deploy and evaluate now route through the Linked Data Explorer backend.** Posting straight from the browser to Operaton's `/engine-rest/…` hits CORS in local development. `handleDeployDMN` now posts to the backend's `POST /v1/dmns/deploy`, and Evaluate Decision, *Run intermediate tests* and *Run test cases* all go through a shared `evaluateViaBackend()` helper hitting `POST /v1/dmns/evaluate/:decisionKey` — mirroring the pattern `runBackendValidation()` already used for `/v1/dmns/validate`. The browser talks to the backend; the backend talks to Operaton server-to-server. The **Evaluation URL** preview in the API Configuration panel shows the backend URL it actually calls, and the now-unused `apiConfig.deploymentEndpoint` field is removed.

**Date-typed DMN inputs are sent as `Date`, not `String`.** `generateRequestBodyFromDMN`'s `typeRef="date"` branch typed every date input as `{ value: "YYYY-MM-DD", type: "String" }`, assuming Operaton would convert internally. That is wrong for any DMN calling `.year`/`.years` on the input directly, as several Amsterdam decisions do — confirmed from Operaton's own logs (`DMN-01005 Invalid value … for clause with type 'date'`). The generated body now emits a full ISO timestamp with offset and `type: 'Date'`.

**The Concepts tab keeps its output variables when an evaluation returns no match.** A DRD root with `hitPolicy="RULE ORDER"` and no catch-all rule legitimately returns an empty result set against the auto-generated baseline request body. `extractOutputsFromTestResult` could only learn an output's name and type from what the engine actually returned, so an empty result yielded zero output concepts even though the DMN declares one — a gap inputs never had, since `generateRequestBodyFromDMN` reads `<dmn:inputData>` straight from the XML. New `extractOutputsFromDMN` closes it for outputs, reading a decision's declared `<dmn:output>` name and type from the XML namespace-agnostically, handling multiple output columns and the name-vs-label fallback; `handleEvaluateDMN` falls back to it whenever the live result yields nothing.

**The DMN tab's Base URL follows `REACT_APP_OPERATON_URL` in development.** `apiConfig.baseUrl` now reads that variable, falling back to the production instance, instead of hardcoding the shared Operaton URL — without it, local development silently pointed at the shared ACC/PROD engine rather than a local Docker container.

**Amsterdam HvA reference DMN: deploy blockers, FEEL fixes and a 100-case MC/DC suite.** The `HvA_full_dmn_export.dmn` reference export was brought to a deployable, evaluable state, and the fixes double as standing guidance for DMN authors — see the [DMN Tab](../user-guide/dmn-tab.md) tips and [DMN Testing](../user-guide/dmn-testing.md) troubleshooting. Deployment was blocked by a missing `camunda:historyTimeToLive` and 48 unescaped `&` characters in `knowledgeSource` URLs. Evaluation was blocked by multi-word FEEL bare names — Operaton's feel-scala engine consumes only the first word and throws `FEEL/SCALA-01008` — and by `<dmn:output>` elements declaring only `label` and no `name`, which makes evaluation throw a blank, unlogged exception. Malformed rule cells (`not -` on boolean columns, `not(null) -` on string columns, bare `and`-joined comparisons, and an unparenthesised `not "met partner"`) were rewritten, and two decisions that defaulted to `hitPolicy="UNIQUE"` while carrying a wildcard default rule were corrected to `FIRST`. A test suite now covers every one of the 99 rules across all 25 decisions with one empirically-verified case each (100 cases, run live), and `extract-legal-sources.py` resolves each decision's `authorityRequirement` → `knowledgeSource` links against the annotation registry — 97 of 99 resolve cleanly across 14 source documents and 23 distinct JuriConnect citations.

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
| Deploys gated on lint and the [test suite](testing.md) | v2026.08.1 |
| [Digest-pinned CI with a blocking supply-chain audit](../../contributing/supply-chain.md) | v2026.08.2 |
| Renovate under a 14-day cooldown, with a no-cooldown advisory lane | v2026.08.2 |
| Releases land through a pull request, gated by `audit` | v2026.08.3 |
| [Audit gate widened to every pull request](../../contributing/supply-chain.md) | v2026.09.0 |
| `renovate.json` validated inside the audit gate | v2026.09.0 |
| Deploys skip documentation-only changes | v2026.09.0 |
| Merge method enforced by repository settings | v2026.09.0 |
| Create React App → Vite migration (four phases) | v2026.09.1 |
| [`check-supply-chain`](../../contributing/supply-chain.md) — pin truth and register agreement | v2026.09.1 |
| [Build id in the Changelog tab](../../contributing/build-provenance.md) | v2026.09.1 |
| Test phases P5, P6 and P7 — the roadmap complete | v2026.09.1 |
| Every form control associated with its label (WCAG 1.3.1 / 4.1.2) | v2026.09.1 |
| [Per-file 80% branch floor](../../contributing/coverage-floor.md), natively enforced | v2026.09.2 |
| Formatting checked in CI, not only on a developer's machine | v2026.09.2 |
| The four heavy tabs lazy-loaded — entry chunk 685.71 → 392.74 kB | v2026.09.2 |
| [Semgrep Code and Supply Chain](../../contributing/dependency-scanning.md), a required check on `acc` | v2026.09.3 |
| E2E journeys against an already-deployed build (`E2E_BASE_URL`) | v2026.09.3 |
| Weekly lock-file maintenance, with majors behind approval — Supply Chain findings at 0 | v2026.09.4 |

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