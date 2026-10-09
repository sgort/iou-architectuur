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

## Drained

| Pass | Entries drained | Where they landed |
|---|---|---|
| 20 September 2026 | — | The first weekly pass predates this queue: the cross-cutting re-check ran inside the RONL Business API sync to v2026.09.9, which is the run that split the two halves apart |
| 27 September 2026 | All of 24 September LDE (1–10) and RBA (1–15); all of 26 September CPSV (1–7), LDE (1–11) and RBA (1–10, 12). LDE-26 #11 (Windows `test:scripts`) is a tooling defect, filed as iou-architectuur#105 item 5 rather than documented; RBA-24 #11 (preview opt-in) is documented on the component's own `cicd.md` and `backend-development.md`, and no contributing page contradicts it; LDE-24 #4 settled by reading the four App Services from Azure (LDE `NODE\|24-lts`, RBA `NODE\|22-lts`) | `supply-chain.md`, `dependency-scanning.md`, `controls.md`, `code-standards.md`, `branch-protection.md`, `coverage-floor.md`, `build-provenance.md`, `the-gitlab-mirror.md`, `index.md`, `ictu-dependency-guideline.md`, `ci-posture-deck.md`, `development-workflow/*`, `doc-architecture/*`; source defects to iou-architectuur#105 items 8–18 |
| 4 October 2026 | Every entry of 27 September (carry-overs 1–2), 28 September RBA (1–6), 30 September RBA (1–3, 5, 7–12, and the first halves of 4 and 6), 2 October CPSV (1–4), 3 October RBA (1–7) and 3 October LDE (1–9). Carry-over 2 (the `api-specification.md` comment) was fixed by the Linked Data Explorer sync of 3 October. 2 October CPSV #4 changed before it could land: `0bf8e46` runs the live-stack preflight only for journeys that need it. 3 October RBA #1 was partly right — the RONL Business API's first audit catch was #208 (adm-zip), #303 the first on `acc`'s own tree. 30 September #4 (Semgrep UI) and #6 (85% margin) carried over above | `supply-chain.md`, `dependency-scanning.md`, `ictu-dependency-guideline.md`, `controls.md`, `branch-protection.md`, `coverage-floor.md`, `build-provenance.md`, `the-gitlab-mirror.md`, `ci-posture-deck.md` (and its Dutch translation), `code-standards.md`, `index.md`, `development-workflow/*`, `doc-architecture/openapi-rendering.md` and `technology-stack.md`; source findings to ronl-business-api (Redis Renovate hold, `SECURITY-PIPELINE.md` `main` row, docker major approval), linked-data-explorer#254 and ttl-editor |
