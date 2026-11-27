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
drained by the pass of 27 September, everything queued from 27 September to 3 October by the pass of 4 October, everything queued from 4 to 11 October by the pass of 11 October, and everything queued from 12 October to 7 November — the three syncs of 7 November — by the pass of 8 November, and everything queued from 8 to 14 November — the syncs of 12 and 14 November — by the pass of 15 November, and everything queued from 16 to 22 November by the pass of 22 November, with one carry-over (see the table at the end).

### 22 November 2026 — carried over from the weekly pass

1. **The reasons recorded with the Linked Data Explorer's Semgrep Supply Chain accepted-risk entries** (`deepmerge`,
   `@tiptap/core`). The RONL Business API's half is answered: its `SECURITY-PIPELINE.md` records a reason, date and revisit
   condition per accepted finding (#470, 17 November). The Linked Data Explorer has no such record yet, so
   iou-architectuur#132 stays open. (Was 15 November carry-over 1, and 8 November, 11 October and 4 October before it.)

### 24 November 2026 — CPRMV v0.4.2 → v0.4.3 (production, `d597671`)

1. **PSA, CPRMV 0.4.3 is released** (`rdf/0.4.3/`, `CHANGELOG.md`; production reports 0.4.3 on `/` and in `openapi.json`).
   `03-architecture-frameworks.md:67` and **AB-03** (`11-decisions-and-risks.md:33`) say "CPRMV 0.4.2": now 0.4.3, still a
   first public working draft (`html/js/config.js:6`, `specStatus "fpwd"`); "the CPSV Editor still writes CPRMV 0.4.1" stays
   true. **AB-07**'s note may add that a RuleSet is now an FRBR Endeavor. **AB-01** and `05-application-architecture.md:104`:
   check whether the function that statement waits for is delivered by 0.4.3. Re-pin every PSA page to CPRMV `d597671`.
2. **CPRMV's CI no longer builds the ReSpec** (`89f1733`, `d597671`, `.gitlab-ci.yml`): `create-pages` publishes the
   committed `html/public`; the in-CI build had failed in pipeline #821. A release reaches Docker Hub only through a
   `serve_api/**` change (hence the `d597671` "trigger pipeline" commit), and the deploy job only prints a pull instruction;
   the hosts are updated by hand. `controls.md:111-113` (tests on merge requests and `main` when `serve_api/` changes; no
   built image run) still holds. Bears on `controls.md` and any CI-posture page that describes CPRMV.
3. **CPRMV development is moving to GitHub** (`open-regels/cprmv`, default branch `acc`; the user, 24 November). New CPRMV
   issues are filed there (#1, #2); the pages and `repo-versions.json` keep the GitLab links for now. Bears on
   `contributing/index.md` (repository table, trackers) once the move completes, and on `the-gitlab-mirror.md` if it lists
   CPRMV's remote.
4. **Open gaps found in this sync, for the PSA's generic wording only if they bear on a decision:** open-regels/cprmv#1
   (an API key reflected in a redirect response) and #2 (a method selection that returns everything; an MCP redirect to
   plain `http`). No link while open.

### 26 November 2026 — `~/.claude/CLAUDE.md` and the skill, for the CPRMV move (no component page yet)

1. **`~/.claude/CLAUDE.md` (user's request, 26 November):** `cprmv` joins `ronl-business-api`, `linked-data-explorer`,
   `ttl-editor` and `lvg` in both pull-request-only lists ("never merge or force-push" and "`acc` and `main` change only
   through a pull request"); the GitLab-mirror bullet says CPRMV moved to GitHub `open-regels/cprmv` on 26 November with
   rulesets on `acc` and `main`, and that its `gitlab` remote, the old home, publishes the ReSpec on a push to `main`
   (ask first). Still sixteen `##` rules. Bears on `development-workflow/skills-and-boundaries.md` (the list of
   pull-request-only repositories, the mirror rule) and `the-gitlab-mirror.md`.
2. **The skill:** `stamp-staleness.py` resolves each component's CI remote from `ci_repo` instead of fixed names or URLs;
   `SKILL.md` gains a CPRMV row, a CPRMV `build` field, owner-agnostic `gh` calls and the Git Bash leading-slash trap.
   Bears on `development-workflow/skills-and-boundaries.md` and `overview.md` where they describe the skill.
3. **The CPRMV pages themselves wait** for fixes the CPRMV session is making (26 November); the queue entries for the move
   (contributing pages, PSA AB-28/AB-29 and three PSA statements, the ICTU question) are added with that sync.

### 26 November 2026 — CPRMV moves to GitHub (no new version; production `8f01b2b`)

Supersedes items 2 and 3 of the 24 November CPRMV entry: GitLab CI and Docker Hub are gone, and the move is complete.
CPRMV is developed on GitHub `open-regels/cprmv` (default branch `acc`); the GitLab project keeps only the ReSpec Pages
job. Evidence: `README.md`, `SECURITY-PIPELINE.md`, `.github/workflows/{ci,zizmor,semgrep,dependency-audit}.yml`,
`.github/rulesets/{acc,main}.json`, `deployment/vm/**` at `8f01b2b`; live `/health` (stable `8f01b2b` run 13, acceptance
`ebff352` run 11).

1. **`contributing/index.md`:** the repository table's CPRMV row (GitLab CI, GitLab issues) → GitHub `open-regels/cprmv`,
   GitHub Actions, issues on GitHub, GitLab only for Pages; the sentences saying the Norm Editor and CPRMV are developed on
   GitLab and take issues there.
2. **`the-gitlab-mirror.md`:** CPRMV's GitLab copy is pushed by hand at a release like the applications' mirrors, but a
   push to `main` still runs its Pages job (its rule is now `$CI_COMMIT_BRANCH == "main"`); no `check-mirror` script.
   GitLab `main` was left at `189cadc` on 26 November by the user's decision.
3. **`branch-protection.md` and `controls.md`:** rulesets "acc supply-chain gate" and "main promotion gate" both require
   `audit`, `scan`, `test` and `build`, pull request with no approvals, merge commits only, no bypass; no
   `lockfile-review`. Unlike the three applications, `main` requires `test` and `build` (contrast `controls.md:78`).
   `controls.md:107-114`'s CPRMV sentence (GitLab pipeline, untested image from `develop`, no built image run) is false.
4. **`supply-chain.md` and `dependency-scanning.md`:** CPRMV's own `SECURITY-PIPELINE.md` (ported from `lvg`'s light
   pipeline, npm → Python); actions hash-pinned (zizmor), base image and Caddy pinned by digest, requirements locked with
   hashes; Renovate with a 14-day cooldown and lock-file maintenance; Semgrep required; a daily pip-audit with a tracking
   issue; no accepted findings recorded.
5. **`build-provenance.md`:** `/health` reports `environment`, `build.sha`, `build.run` and `image.digest`, checked by
   CI's smoke and wait-for-deploy steps; `actions/attest-build-provenance` on every pushed digest. `repo-versions.json`
   now carries a CPRMV `build`.
6. **`code-standards.md` and `coverage-floor.md`:** CPRMV is Python with no hooks and no formatter (SECURITY-PIPELINE
   lists them as follow-ups); no coverage floor; draft PR #29 proposes an 80% per-file branch floor (planned only).
7. **`ictu-dependency-guideline.md`:** CPRMV is not scored. It now carries most of what the guideline asks (cooldown,
   majors on approval with an explicit recommendation-7 rule, hashes, digests, daily audit, Semgrep): decide whether to
   score it as a fourth column from the next weekly pass.
8. **The VM pipeline is the model for ronl-business-api#196** (the user, 26 November): pull, not push; a design recorded
   first; idempotent apply; status readable without SSH (`/deploy-status.json`, `/health`); digest pins reported as
   running; no credentials in CI. Not yet answered for the RBA: one shared VM for several services and both tiers,
   Keycloak and Postgres rollback, and the `docker`-group risk the design says to revisit before a shared VM. Bears on
   the RBA's next sync and on `supply-chain.md` (#196 boundary).
9. **PSA (generic wording, no issue links for open gaps):** re-pin every page to CPRMV `8f01b2b`.
   **AB-28** "CPRMV not yet" (`11-decisions-and-risks.md:58`, `08-security-and-privacy.md:77-80`): CPRMV now pins
   everything a build fetches and waits 14 days, but has no SBOM: propose *deels* for CPRMV. **AB-29** (changes only
   through a pull request): CPRMV now meets it. **AB-30**: still the rapid-prototyping track, unchanged.
   `09-technical-infrastructure.md:42` (CPRMV "container on its own servers") and
   `10-management-and-continuity.md:56-59` ("built on GitLab under a lighter regime") are false. **R-07**: CPRMV has
   its own acceptance tier now; the risk still holds through AB-05 and AB-28. Possible generic chapter-8 wording: the VM
   trusts an image by its tag (provenance attested, not yet checked before deploying), and the deployment user's Docker
   rights amount to root on that VM.
10. **Organisation move:** every IOU component is to move to the `open-regels` GitHub organisation (the user,
    26 November); CPRMV is the first. Record as intent on `contributing/index.md`, not as fact for the others.

### 27 November 2026 — CPRMV release v2026.11.0 (production, `502a351`; vocabulary still 0.4.3)

Evidence: `serve_api/RELEASE`, `.github/workflows/sbom.yml`, `scripts/write-sbom.py`, `.claude/commands/bump-release.md`,
`docs/superpowers/specs/2026-11-27-release-versioning-design.md` and `…-sbom-design.md`, `SECURITY-PIPELINE.md` at `502a351`;
live `/health` (stable: `release` `v2026.11.0`, `version` `0.4.3`, `502a351` run 21).

1. **PSA AB-28** (`11-decisions-and-risks.md:58`, `08-security-and-privacy.md:77-80`): the 26 November entry (item 9)
   proposed *deels* for CPRMV because it had no SBOM. CPRMV now commits a CycloneDX SBOM per release and attaches an
   image SBOM attestation, besides pinning and the 14-day wait, so it meets AB-28's build criteria; whether "measured
   weekly" holds depends on scoring CPRMV (26 November item 7). Revise item 9 with this; R-07 follows.
2. **The release process on `contributing/**`:** CPRMV has `/bump-release` too, with `vYYYY.MM.N` (a `v` prefix, unlike
   the applications' `YYYY.MM.N`), no changelog and no git tags, and a release number beside a vocabulary version.
3. **`the-gitlab-mirror.md`** (extends 26 November item 2): pushing `main` to GitLab is a fixed step of every CPRMV
   release, done by `/bump-release` (fast-forward only, checked before and confirmed after; stops on divergence), which
   publishes the ReSpec. GitLab `main` was `502a351` on 27 November; GitLab `acc` is not kept current.
4. **`supply-chain.md` and the SBOM pages** (extends 26 November item 4): `sbom.yml` (`release-sbom`, not a required
   check), `scripts/write-sbom.py` (Python, `cyclonedx-bom` 8.0.1, CycloneDX 1.6), one file per release number, and an
   image SBOM attestation. Compare with the applications' SBOM practice.
5. **`build-provenance.md`** (extends 26 November item 5): `/health` also reports `release`; `repo-versions.json` gains an
   optional `vocabulary` field, rendered in the page header and the home page's status table.
6. **`ictu-dependency-guideline.md`** (26 November item 7): CPRMV now also keeps an SBOM per release, one more input for
   deciding whether to score it.

### 27 November 2026 — RONL Business API v2026.11.5 → v2026.11.6 (production, `7416c65`)

Evidence: `SECURITY-PIPELINE.md`, `.npmrc`, `.github/workflows/azure-backend-{acc,prod}.yml` at `7416c65` (the scripts
`deploy-backend-to-{acc,prod}.sh` are deleted, b0a12de, #491); `changelog-data.ts` 2026.11.6; findings filed as
ronl-business-api#498.

1. **The break-glass deploy scripts are retired**, and `SECURITY-PIPELINE.md` closes the exception "The backend is deployed
   outside CI, and its dependencies are unpinned" (27 November). The backend now reaches ACC and production only through
   `azure-backend-{acc,prod}.yml`, installed with `npm ci` from the root lockfile. Pages still saying the scripts remain:
   `supply-chain.md:176` and `:874–890` (now only the VM images stay open, #196); `ictu-dependency-guideline.md:217–222`
   and `:447`; `controls.md:128`; `code-standards.md:277`; and the RBA R3/R4 rationale in `docs/data/ictu-assessments.yml`
   (around 494–502). **Score effect is the pass's call:** it removes one of two reasons holding R3/R4 back; the VM images
   without digests (#196) remain.
2. **`supply-chain.md`, what the gate does not protect:** drop the scripts exception, keep the VM-images one, as the RBA's
   register now does.
3. **PSA:** no PSA text names the scripts, so no status changes from item 1; AB-28's RBA evidence can cite the retirement.
   AB-17 / AB-32: the Woo-dashboard now signs in through the Entra broker too (all four boards), an evidence update only.
   AB-20 / AB-23: the new link and upload routes and the 422 refusal are audit-logged. AB-18: the M2M task completion
   skips the linked-document check (filed in #498), for the pass to judge, worded generically and without a link while
   open. Re-pin RBA on the PSA pages from `1784a72` to `7416c65`.
4. **eDOCS archiving:** the open question which eDOCS document type the secretariat and the archive expect (comment beside
   `EDOCS_LINKED_UPLOAD_FORM` in `config.ts` and `.env.example`) may belong with a PSA archiving risk, if one exists.
5. **The unit-test figures:** 359 test files and 5,695 tests at `7416c65` (backend 115 · 2,932; frontend 147 · 1,862;
   pa-cockpit 43 · 516; pa-demo 19 · 109; public site 35 · 276), for the weekly `tests:` rows.

## Drained

| Pass | Entries drained | Where they landed |
|---|---|---|
| 20 September 2026 | — | The first weekly pass predates this queue: the cross-cutting re-check ran inside the RONL Business API sync to v2026.09.9, which is the run that split the two halves apart |
| 27 September 2026 | All of 24 September LDE (1–10) and RBA (1–15); all of 26 September CPSV (1–7), LDE (1–11) and RBA (1–10, 12). LDE-26 #11 (Windows `test:scripts`) is a tooling defect, filed as iou-architectuur#105 item 5 rather than documented; RBA-24 #11 (preview opt-in) is documented on the component's own `cicd.md` and `backend-development.md`, and no contributing page contradicts it; LDE-24 #4 settled by reading the four App Services from Azure (LDE `NODE\|24-lts`, RBA `NODE\|22-lts`) | `supply-chain.md`, `dependency-scanning.md`, `controls.md`, `code-standards.md`, `branch-protection.md`, `coverage-floor.md`, `build-provenance.md`, `the-gitlab-mirror.md`, `index.md`, `ictu-dependency-guideline.md`, `ci-posture-deck.md`, `development-workflow/*`, `doc-architecture/*`; source defects to iou-architectuur#105 items 8–18 |
| 4 October 2026 | Every entry of 27 September (carry-overs 1–2), 28 September RBA (1–6), 30 September RBA (1–3, 5, 7–12, and the first halves of 4 and 6), 2 October CPSV (1–4), 3 October RBA (1–7) and 3 October LDE (1–9). Carry-over 2 (the `api-specification.md` comment) was fixed by the Linked Data Explorer sync of 3 October. 2 October CPSV #4 changed before it could land: `0bf8e46` runs the live-stack preflight only for journeys that need it. 3 October RBA #1 was partly right — the RONL Business API's first audit catch was #208 (adm-zip), #303 the first on `acc`'s own tree. 30 September #4 (Semgrep UI) and #6 (85% margin) carried over above | `supply-chain.md`, `dependency-scanning.md`, `ictu-dependency-guideline.md`, `controls.md`, `branch-protection.md`, `coverage-floor.md`, `build-provenance.md`, `the-gitlab-mirror.md`, `ci-posture-deck.md` (and its Dutch translation), `code-standards.md`, `index.md`, `development-workflow/*`, `doc-architecture/openapi-rendering.md` and `technology-stack.md`; source findings to ronl-business-api (Redis Renovate hold, `SECURITY-PIPELINE.md` `main` row, docker major approval), linked-data-explorer#254 and ttl-editor |
| 11 October 2026 | Every entry of 4 October (carry-over 2, the 85% margin, now restated with the files below it), 6 October LDE (1–7), 9 October RBA (1–9), 9 October Norm Editor (3–4), 10 October CPRMV (1–3), 10 October CPSV (1–5), 10 October LDE (1–5; item 5 was done by the RBA sync of 11 October) and 11 October RBA (1–6). 9 October RBA #1 (SBOM checks cannot fail) is history in all three since #274/#354; CPRMV #1 became one sentence on `controls.md`; 4 October carry-over 1 and Norm Editor 1–2 carried over above, with a new lead on the Azure DevOps pipeline file | `supply-chain.md`, `dependency-scanning.md`, `controls.md`, `build-provenance.md`, `ci-posture-deck.md` (and its Dutch translation), `code-standards.md`, `branch-protection.md`, `coverage-floor.md`, `the-gitlab-mirror.md`, `index.md`, `ictu-dependency-guideline.md`, `development-workflow/*`, `doc-architecture/*`; no new source findings |
| 8 November 2026 | 11 October carry-over 2 (Norm Editor `build_gui`: observed in pipeline 737 — the step fails on a missing `node` without failing the job; remote tags still only `2026.07.0` and `2026.07.1`) and the first, existence half of carry-over 1 (accepted-risk entries read from Semgrep; the unreadable reasons carried over above); every entry of 7 November CPSV (1–4), LDE (1–5) and RBA (1–8). LDE #2 was partly wrong — the Linked Data Explorer already carried ten inline `nosemgrep` lines, and `aec5c34` added five; LDE #3 was wider than queued — the `follow-redirects` high is open on `acc` too. The PSA items (CPSV #4, LDE #4, RBA #4–5) were verified by the PSA re-check: AB-13, AB-08 and R-01 reworded, AB-04 updated, AB-03 / R-04 and AB-20 / R-02 unchanged. RBA #6 touched no contributing page; RBA #7 landed on the ICTU page. Found in the same pass, not queued: `ci-posture-deck.md` left `lockfile-review` out of its `acc` cells, and four pages dated three RONL Business API changes to v2026.09.11 that shipped in v2026.09.10. Carry-over 3 (Azure DevOps pipeline file) stays, still unverifiable | `supply-chain.md`, `dependency-scanning.md`, `code-standards.md`, `controls.md`, `branch-protection.md`, `coverage-floor.md`, `build-provenance.md`, `the-gitlab-mirror.md`, `ci-posture-deck.md` (and its Dutch translation), `index.md`, `ictu-dependency-guideline.md`, `development-workflow/*`, `doc-architecture/*`; `docs/{nl,en}/psa/**`; no new source findings |
| 15 November 2026 | 8 November carry-over 2 (the Azure DevOps pipeline file): settled by the user — a push of `acc` to `flevoland` deploys the acceptance site through the root `azure-static-web-apps-pipeline.yml`, which the 14 November push showed within two minutes; `az devops` is still not installed. Every entry of 12 November CPSV (1–3), LDE (1–5) and RBA (1–3), 14 November RBA v2026.11.3 (1–5) and 14 November RBA v2026.11.4 (1–7). The PSA items were verified on `main` by the PSA re-check: no status changed; AB-08, AB-17, AB-20, AB-21, AB-23, AB-18, AB-26 and AB-32 reworded, R-02 reworded with links to the closed parts (linked-data-explorer#163, ttl-editor#234), and R-16 added for the open authentication gap, generic and unlinked. Leads that did not hold: the Linked Data Explorer does not record who may start a process (only the RONL Business API enforces it), and `keycloak-js` 23.0.7 dates from February 2024, not December 2023. 14 November v2026.11.4 #6 (the BES test users in ACC and PROD) rests on the owner's note; AB-15 does not depend on it. `upstream-certs.yml` also runs on pull requests that touch its own files. Found in the same pass, not queued: the Keycloak VM's Postgres has been digest-pinned since 6 November, the RONL Business API local stack has six images, and `openapi-rendering.md` said the Linked Data Explorer's API declares no security scheme. 8 November carry-over 1 stays above | `supply-chain.md`, `dependency-scanning.md`, `code-standards.md`, `controls.md`, `branch-protection.md`, `coverage-floor.md`, `build-provenance.md`, `the-gitlab-mirror.md`, `ci-posture-deck.md` (and its Dutch translation), `index.md` (stamp only), `ictu-dependency-guideline.md`, `development-workflow/*`, `doc-architecture/*`; `docs/{nl,en}/psa/**` and the template; source findings: the Linked Data Explorer's `SECURITY-PIPELINE.md` counts eleven workflows (twelve; linked-data-explorer#342), the RONL Business API's five local images (six; added to ronl-business-api#457) |
| 22 November 2026 | 15 November carry-over 1 halved (the RONL Business API's reasons are in git; the Linked Data Explorer's two stay above). Every entry of 18 November RBA (1–7) and 22 November CPSV Editor and LDE (1–7). 18 November #5 (the two live-realm scripts) landed on no page, since none lists how the realms change; 22 November #1 was wider than queued, since zizmor-action installs zizmor from hash-locked wheels for the RONL Business API's v0.8.0 too, while its v0.8.1 update (#461) has waited on its register row since 17 November. The PSA items were verified on `main`: no status changed; AB-18, AB-19, AB-23 and R-03 reworded; R-17 added for the browser-visible citizen service number and the incomplete lookup audit, generic and unlinked. Found in the same pass, not queued: the RONL Business API accepts an ID token as a bearer token (ronl-business-api#482), and two source comments still describe zizmor-action's digest table (RBA `SECURITY-PIPELINE.md:61-75`, ronl-business-api#483; ttl-editor `.github/workflows/zizmor.yml:84-86`, ttl-editor#270) | `supply-chain.md`, `code-standards.md`, `dependency-scanning.md`, `controls.md`, `branch-protection.md`, `coverage-floor.md`, `build-provenance.md`, `the-gitlab-mirror.md`, `ci-posture-deck.md` (and its Dutch translation), `index.md`, `ictu-dependency-guideline.md`, `development-workflow/*`, `doc-architecture/*`; `docs/{nl,en}/psa/**` and the template; source findings: ronl-business-api#482 and #483, ttl-editor#270 |
