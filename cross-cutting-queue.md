# Cross-cutting queue

What a component sync noticed but did not act on, waiting for the weekly Sunday
pass over `docs/en/contributing/**`.

**Why this file exists.** Until 20 September 2026 every component sync carried the
cross-cutting re-check with it. That made a sync too large to finish in one
sitting, and it meant the contributing pages were re-read only when a component
happened to ship. The two halves now run on different cadences — but a component
sync still *reads* the changelog that falsifies a contributing page, and that
observation is worth more on the day it is made than a week later, reconstructed.
So a sync records it here instead of acting on it.

**The contract.**

- A component sync **appends** one entry per release range it documents, with one
  bullet per cross-cutting fact: what changed, the evidence (the changelog entry,
  or the source file and what it says), and the page it bears on. If a release
  surfaced nothing cross-cutting, it writes that sentence with the date — a silent
  no-op cannot be told apart from a forgotten step.
- A component sync **never** edits a contributing page and **never** refreshes a
  `verified:` stamp. Both assert a re-check that did not happen.
- The weekly pass **verifies each entry against source** — an entry is a lead, not
  a finding — then strikes it, in the same commit as the corrections it produced.
  Anything it cannot verify stays, with a note saying why.

## Pending

Each section below was queued by one run and waits for the next weekly pass, which verifies
every entry against source before draining it. Everything queued on 24 and 26 September was
drained by the pass of 27 September, and everything queued from 27 September to 3 October by the pass of 4 October (see the table at the end).

### 4 October 2026 — carried over from the weekly pass

1. **The Semgrep Supply Chain triage of 30 September is recorded as accepted risk in the Semgrep UI.**
   Evidence: ronl-business-api `3d4913f` (PR #286) raised the `multer` floor and left the rest as
   accepted risk. The pass cannot read the Semgrep dashboard, so whether those entries exist, and with
   what reason, is unverified. Bears on: `dependency-scanning.md` (Semgrep Supply Chain). (Was 30
   September RONL Business API item 4.)

2. **The RONL Business API's "every file clears 85% branches" no longer holds.**
   Evidence: `73a6764` claimed all 32 files at 85% or above at v2026.09.15; the v2026.10.0 measurement of
   3 October 2026 (component sync) puts `BesluitOverzichtSection.tsx` at 80.43% — one branch above the
   80% floor. The pass did not run the suites; the next one that measures coverage should restate the
   margin on `coverage-floor.md`. (Was 30 September RONL Business API item 6, second half.)

### 6 October 2026 — Linked Data Explorer v2026.10.0 → v2026.10.1 (production, `dd4728d`)

Read at `origin/main` = `dd4728d` (Promote to Production #4); `origin/acc` `85f484d` holds the same tree.

1. **The fingerprint checks now run in CI, in both repositories.**
   Evidence: LDE `zizmor.yml:180` runs `check-rip-bpmn` in the required `audit` job (a424e95); RBA `origin/acc`
   `zizmor.yml:190` runs `check-swimlane-fixtures`. Both now also cover the declared-phase models
   (LDE `DECLARED_PHASE_MODELS`, 61ad418; RBA `__fixtures__/declared/`). Was iou-architectuur's finding on
   linked-data-explorer#254 items 5 and 11 and ronl-business-api#312.
   Bears on: `code-standards.md` (the "pre-push only, in no workflow" paragraph and the fingerprint-contract scope).

2. **A fixture- or example-only pull request now runs the LDE backend suite.**
   Evidence: `azure-backend-acc.yml:38-40,91` — paths and `PATTERN` include `examples/`, `e2e-fixtures/` and
   `packages/frontend/public/examples/` (#257). Bears on: `code-standards.md` (the quoted old pattern and "gate nothing").

3. **`lockfile-review` is required on `acc` in all three repositories — ICTU R9.**
   Evidence: the `lockfile-review` job in each `zizmor.yml` (LDE `:239`, RBA `:285`, TTL `:246`); live rules on
   `acc` list `lockfile-review` beside the existing checks in all three (read 6 October 2026). linked-data-explorer#248
   closed on 6 October. Bears on: `branch-protection.md` (the R9 "no tooling" paragraph and the ruleset table),
   `ictu-dependency-guideline.md` (R9 row, the #248 link as open; a score to reconsider), `controls.md`,
   `supply-chain.md`.

4. **A release pull request's SBOM is checked strictly, in all three repositories.**
   Evidence: `sbom.yml` runs `write-sbom.mjs --check` on a pull request that changes the version's SBOM
   (LDE `:81-104`; RBA and TTL `:101-104`), and each `package.json` has `sbom:check` (#255, closed 5 October).
   Bears on: `dependency-scanning.md` (the paragraph saying the strict check runs nowhere; the SBOM list gains LDE
   2026.10.1 — re-count all three).

5. **The LDE serves a second public OpenAPI document at `/v2/openapi.json`.**
   Evidence: c5165d6 — `registry.ts`, `publicPaths.ts:15-20`; both documents linted (`lint:openapi`) and smoke-checked
   by the deploy. Since 6 October the documentation site renders it on a second page,
   `linked-data-explorer/reference/api-specification-v2.md` — the same Scalar setup as the v1 page, `data-url` on
   `/v2/openapi.json`, a `servers` override on the acceptance `/v2` base (the document lists Production first), and the
   banner still reading `/v1/health`; `GET /v2/norms` echoes the ACC docs origin, so Test Request works. Bears on:
   `doc-architecture/openapi-rendering.md`, which describes one rendered document per component.

6. **The LDE raised its engines floor rather than widening it.**
   Evidence: root and backend `package.json` `engines.node` `>=24.21.0` (v2026.10.1); RBA stays `>=22`.
   Bears on: `supply-chain.md` (the "floors are widened, not bumped" sentences).

7. **A CPSV Editor page repeats a claim `/v2/norms` has overtaken — for the next CPSV sync, not a contributing page.**
   Evidence: `docs/en/cpsv-editor/developer/cprmv-dataset-generation.md:344-352` says a stale `/v1/norms` response
   lasts "up to max-age (1 h)" and plans a publication timestamp. On v1 a same-date correction keeps its ETag, so a
   revalidating client can get 304 indefinitely; `/v2/norms` signs a digest of the rules instead (517cd71).

### 9 October 2026 — RONL Business API v2026.10.0 → v2026.10.1 (production, `ebec288`)

Read at `origin/main` = `ebec288` (Promote to Production #7); `origin/acc` `0ea4985` holds the same tree.

1. **Neither SBOM check can fail in CI — in RBA and the LDE.**
   Evidence: `sbom.yml` runs "Generate the SBOM" (`write-sbom.mjs`, which rewrites the committed file in the workspace)
   before `--verify-release` and the release-PR `--check`; run 37909059258 generated 409 components with npm 11.19.0 and then
   reported "matches the lockfile", while the committed 2026.10.1 SBOM was generated with npm 10.9.9 and lists 423.
   Filed as ronl-business-api#354 and linked-data-explorer#274. The 6 October LDE item 4 ("the SBOM is checked strictly,
   in all three") therefore overstates it. Bears on: `dependency-scanning.md` (the SBOM paragraph), `ictu-dependency-guideline.md`
   (R10 evidence), and any page that names the release-PR check as a safeguard.

2. **RBA frontends build and deploy on lockfile-only changes on `acc` — but a promotion still skips them.**
   Evidence: 6f79e93 (#247) adds `package-lock.json` and `package.json` to the three `*-acc` filters;
   `scripts/promotion-targets.sh:44-47` is unchanged (ronl-business-api#354 item 2). Bears on: `code-standards.md`,
   `ictu-dependency-guideline.md` and `branch-protection.md` (the long-standing "lockfile-only pull request skips the site
   checks" warning — now true for promotions only).

3. **`check-swimlane-fixtures` covers 14 fixtures** (12 RIP + 2 declared-phase, d2d10b4) and runs in `audit` (`zizmor.yml:177`).
   Adds the count to the 6 October LDE item 1. Bears on: `code-standards.md` (the fingerprint-contract scope, "twelve").

4. **RBA `.nvmrc` is 22.23.3** (2ff98e3). Bears on: `supply-chain.md` (the `.nvmrc` table and the npm it bundles — the committed
   SBOM records npm 10.9.9), `ictu-dependency-guideline.md`, `controls.md`.

5. **Two production advisories cleared.** `dompurify` 3.4.16 (4953ba6) closes the two `dompurify` lows; `@modelcontextprotocol/sdk`
   1.31.0 (bbfac17, PR #331) for GHSA-6qxp-vccf-f47h — RBA's audit issue #323 (opened 6 Oct, closed 9 Oct); verify whether the
   cooldown exception was used. Bears on: `dependency-scanning.md` (catch list, alert table), `ictu-dependency-guideline.md` (R6, R10).

6. **RBA `SECURITY-PIPELINE.md` counts 41 `uses:` references across 13 workflows** (was 39), and its `main` row now lists `scan`.
   RBA has 26 jobs, 22 choosing a runner, and `audit` has ten steps. Bears on: `supply-chain.md`, `code-standards.md`.

7. **The PA demo job's Playwright browser install has `timeout-minutes: 10`** (c9c7edd, #337) — the first step-level timeout in RBA.
   Bears on: `code-standards.md` (the PA demo row).

8. **Accepted risk: Keycloak stores brokered Entra tokens a person can read** (#325). Not in `SECURITY-PIPELINE.md`
   (ronl-business-api#354 item 6). Bears on: `controls.md` if it keeps an accepted-risk list.

9. **The 85% margin carry-over (4 October item 2)** — still unmeasured by this sync; the next coverage measurement should restate it.

### 9 October 2026 — Norm Editor 2026.09.1 → 2026.09.15-2

Read at `origin/main` `c47096b`. The pages themselves were not touched and no stamp was refreshed.

1. **CI now also regenerates the changelog, in `build_gui`** (945a70f): `./scripts/generate-changelog.mjs && mv ./changelog.json gui/public`
   runs before the image build, in `docker:latest`, which has no Node. The step very likely fails on every `main` push since
   10 September (not observed: the pipelines are not visible from outside the project). Bears on: `code-standards.md`
   ("The Norm Editor is shaped differently": the hooks paragraph says the changelog is regenerated on commit; CI now does it too,
   and the "pipeline gates on tests alone" line).
2. **The release tags after `2026.07.1` exist only in a local clone.** The changelog groups by tag, so CI's build would label
   everything after `2026.07.1` as Unreleased, and the hashes the *What's new* dialog links are on no branch on the remote.
   Bears on: `code-standards.md` (the git-log-derived changelog), any page describing how a Norm Editor release lands.
3. **Deployments are per environment with a shared resource group** — `{name}-{environment}-rg` and `{name}-general-rg` for the
   registry, pull identity and DNS zone; `ENVIRONMENT` defaults to `acceptance`, production takes the apex and other environments
   `acc.` (db0a26a, 28b5183). Bears on: `code-standards.md` (the "Deploy artifact" row is still right), `contributing/index.md` if it
   describes where the Norm Editor runs.
4. **No lint, format, coverage or supply-chain change** in this range. The `.gitlab-ci.yml` diff is the one line in item 1.

Findings for these went into [regels/editor#1](https://git.open-regels.nl/regels/editor/-/work_items/1).

### 10 October 2026 — CPRMV v0.4.1 → v0.4.2

Read at `origin/main` `ace9dfa`. The pages themselves were not touched and no stamp was refreshed.

1. **CPRMV's CI tests the code but not the image, and most tests are disabled.** `test-cprmv-api` (python:3.14-bookworm) runs on merge
   requests and `main` when `serve_api/**` changes: `py_compile`, an import check, warn-only data checks and `pytest`, which collects
   3 of 13 tests since 0661a0d. `develop` builds and pushes an image with no test job, and nothing runs the built image — which is
   how a `:latest` without `serve_api/methods/` reached all three hosts (fixed by standards/cprmv!20, findings in #31). Bears on:
   `controls.md` ("The fourth and fifth components" — the CPRMV API is "outside this set"; consider one sentence on what its
   pipeline does gate), `code-standards.md` if it ever describes the GitLab components' CI.
2. **Deployment is a manual image pull on three hosts** — `cprmv.open-regels.nl`, `cprmv.open-rules.eu` and `acc.cprmv.open-regels.nl`;
   `deploy-cprmv-api` only prints pull hints. Bears on: `contributing/index.md` (the CPRMV row) and `development-workflow/overview.md`
   if either says how a CPRMV release lands.
3. **No supply-chain change**: the Python requirements are unpinned in `pyproject.toml` and locked in `requirements.txt` (pip-compile),
   with no scanning job. Nothing to change on `supply-chain.md`, which already leaves CPRMV out.

### 10 October 2026 — CPSV Editor v2026.10.0 → v2026.10.1

Read at `origin/main` `98458fa` (same tree as `acc` `2cf6a90`). The pages themselves were not touched and no stamp was refreshed.

1. **TTL now has a lockfile review, required on `acc`.** `zizmor.yml` gains a `lockfile-review` job (8bf8d50, 68bac82); the live
   `acc supply-chain gate` ruleset requires `audit`, `scan`, `Build and deploy ACC` and `lockfile-review`; `main promotion gate`
   requires `audit` and `scan`. All three applications now carry the review. Bears on: `supply-chain.md`, `code-standards.md`
   (required checks per repository), `ictu-dependency-guideline.md` (R1/R11).
2. **Registry signatures and provenance are verified in TTL's `audit` job** — step *Verify registry signatures*,
   `npm run audit:signatures` → `scripts/audit-signatures.sh` (3fcdbbd, `zizmor.yml:193-209`). Bears on: `supply-chain.md`,
   `ictu-dependency-guideline.md` (R5, provenance half).
3. **A quarterly dependency review** — `dependency-review.yml`, cron `23 6 2 1,4,7,10 *`, opens an issue per quarter with the
   evidence for every direct dependency; first review 2026-Q4 (#210). The criteria live in linked-data-explorer's
   `docs/dependency-criteria.md` (e4af5e6). Bears on: `dependency-scanning.md` or `supply-chain.md`, `ictu-dependency-guideline.md` (R1, R11).
4. **The SBOM checks now run before generation in TTL** (7a35934, fixing linked-data-explorer#274's defect here), the release
   PR checks strictly (8417da0), and the SBOM lists the full production tree (c8f8804 — "the same fix landed in
   linked-data-explorer and ronl-business-api"). This **corrects** the 6 October LDE item and the 9 October RBA item 1 for TTL;
   verify the LDE and RBA state in their own syncs before the weekly pass. Bears on: `supply-chain.md`, `ictu-dependency-guideline.md` (R10).
5. **TTL's workflow count is now eight** (`dependency-review.yml` added). Bears on: `code-standards.md` and any page that counts workflows.

### 10 October 2026 — Linked Data Explorer v2026.10.1 → v2026.10.2

Read at `origin/main` `82f461f` (same tree as `acc` `a87f64b`). The pages themselves were not touched and no stamp was refreshed.

1. **LDE verifies registry signatures in its required `audit` job** (`npm run audit:signatures`, 42ca25f); the registry or
   proxy half of ICTU R5 stays open (#249). With TTL's 3fcdbbd, two of the three applications now do — check RBA in its sync.
   Bears on: `supply-chain.md`, `ictu-dependency-guideline.md` (R5).
2. **Dependency criteria are written down and applied twice**: `docs/dependency-criteria.md` (six criteria) in this repository,
   a checklist in the lockfile-review comment for a new direct dependency, and the quarterly `dependency-review.yml`
   (ddb1687). Bears on: `ictu-dependency-guideline.md` (R1, R11), `dependency-scanning.md`.
3. **LDE's SBOM checks run before generation, and the production set is read from the lockfile** (af06deb, a87f64b/#297); the
   6 October LDE item 4 and the 9 October RBA item 1 are corrected for LDE — `sbom:check` passed locally on 10 October.
   Bears on: `supply-chain.md`, `ictu-dependency-guideline.md` (R10).
4. **LDE now has twelve workflows** (`dependency-review.yml` added) and five script harnesses. Bears on: `code-standards.md`.
5. **Cross-component:** RBA's `ronl-business-api/reference/bpmn-design-criteria.md` still recommends `mapDecisionResult="singleResult"`
   plus a script task, the pattern LDE removed from every example for ENGINE-03005 (2cbfa2b) — a component page, so it belongs
   to the RBA sync, recorded here so it is not lost.

### 11 October 2026 — RONL Business API v2026.10.1 → v2026.10.2 (production, `7117914`)

Read at `origin/main` `7117914` (Promote to Production #8); `origin/acc` `c51ec0a` holds the same tree. The pages themselves were
not touched and no stamp was refreshed.

1. **All three applications now verify registry signatures in their required `audit` job.** RBA `zizmor.yml` runs
   `npm run audit:signatures` (74ebeeb, `scripts/audit-signatures.sh`); measured 11 October: 1575 signatures and 213 attestations
   verified. Completes the 10 October LDE item 1. Bears on: `supply-chain.md`, `controls.md` (R5 "nowhere yet"),
   `ictu-dependency-guideline.md` (R5).
2. **RBA applies the shared dependency criteria too**: the lockfile-review checklist for a new direct dependency
   (`scripts/lockfile-diff.mjs`) and the quarterly `dependency-review.yml` (83fc2a1); the first review, 2026-Q4, is
   ronl-business-api#362 (closed). Bears on: `controls.md` (R1, R11 "nowhere yet"), `ictu-dependency-guideline.md` (R1, R11),
   `dependency-scanning.md`.
3. **RBA has fourteen workflows, 27 jobs (23 choosing a runner), `audit` has eleven steps, and `check-supply-chain` counts 43
   pinned references across 6 actions** (was 13 / 26 / 22 / ten / 41). Supersedes the counts in the 9 October RBA item 6.
   Bears on: `code-standards.md` (":174 thirteen workflows"), `supply-chain.md`.
4. **RBA's SBOM checks run before generation and the production set comes from the lockfile** (5a0d969, 38a3bcb, #354/#368).
   The 9 October RBA item 1 is now history for RBA too: the v2026.10.2 SBOM lists 487 components and records npm 11.19.0, and a
   local `sbom:check` with another npm (11.21.0) exits 1 on `metadata.tools` alone. Bears on: `supply-chain.md`,
   `dependency-scanning.md`, `ictu-dependency-guideline.md` (R10).
5. **The 10 October LDE item 5 is done:** this sync rewrote `ronl-business-api/reference/bpmn-design-criteria.md` for plain
   variables. Nothing for the weekly pass to do there; drain it.
6. **The 85% margin carry-over (4 October item 2)**: measured in this sync. Two RBA files are below 85% branches: `BesluitOverzichtSection.tsx` 80.43% (37/46, as on 3 October) and the frontend's `components/process/phaseSet.ts` 83.33% (10/12); none is below the 80% floor. Bears on: `coverage-floor.md` (the margin sentence).

## Drained

| Pass | Entries drained | Where they landed |
|---|---|---|
| 20 September 2026 | — | The first weekly pass predates this queue: the cross-cutting re-check ran inside the RONL Business API sync to v2026.09.9, which is the run that split the two halves apart |
| 27 September 2026 | All of 24 September LDE (1–10) and RBA (1–15); all of 26 September CPSV (1–7), LDE (1–11) and RBA (1–10, 12). LDE-26 #11 (Windows `test:scripts`) is a tooling defect, filed as iou-architectuur#105 item 5 rather than documented; RBA-24 #11 (preview opt-in) is documented on the component's own `cicd.md` and `backend-development.md`, and no contributing page contradicts it; LDE-24 #4 settled by reading the four App Services from Azure (LDE `NODE\|24-lts`, RBA `NODE\|22-lts`) | `supply-chain.md`, `dependency-scanning.md`, `controls.md`, `code-standards.md`, `branch-protection.md`, `coverage-floor.md`, `build-provenance.md`, `the-gitlab-mirror.md`, `index.md`, `ictu-dependency-guideline.md`, `ci-posture-deck.md`, `development-workflow/*`, `doc-architecture/*`; source defects to iou-architectuur#105 items 8–18 |
| 4 October 2026 | Every entry of 27 September (carry-overs 1–2), 28 September RBA (1–6), 30 September RBA (1–3, 5, 7–12, and the first halves of 4 and 6), 2 October CPSV (1–4), 3 October RBA (1–7) and 3 October LDE (1–9). Carry-over 2 (the `api-specification.md` comment) was fixed by the Linked Data Explorer sync of 3 October. 2 October CPSV #4 changed before it could land: `0bf8e46` runs the live-stack preflight only for journeys that need it. 3 October RBA #1 was partly right — the RONL Business API's first audit catch was #208 (adm-zip), #303 the first on `acc`'s own tree. 30 September #4 (Semgrep UI) and #6 (85% margin) carried over above | `supply-chain.md`, `dependency-scanning.md`, `ictu-dependency-guideline.md`, `controls.md`, `branch-protection.md`, `coverage-floor.md`, `build-provenance.md`, `the-gitlab-mirror.md`, `ci-posture-deck.md` (and its Dutch translation), `code-standards.md`, `index.md`, `development-workflow/*`, `doc-architecture/openapi-rendering.md` and `technology-stack.md`; source findings to ronl-business-api (Redis Renovate hold, `SECURITY-PIPELINE.md` `main` row, docker major approval), linked-data-explorer#254 and ttl-editor |
