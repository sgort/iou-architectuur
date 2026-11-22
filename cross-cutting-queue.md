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
drained by the pass of 27 September, everything queued from 27 September to 3 October by the pass of 4 October, everything queued from 4 to 11 October by the pass of 11 October, and everything queued from 12 October to 7 November — the three syncs of 7 November — by the pass of 8 November, and everything queued from 8 to 14 November — the syncs of 12 and 14 November — by the pass of 15 November, with one carry-over (see the table at the end).

### 15 November 2026 — carried over from the weekly pass

1. **The reasons recorded with the Semgrep Supply Chain accepted-risk entries.** The entries exist (verified 8 November); the
   reason and date recorded with each are not returned by the Semgrep tool and cannot be read from here. Tracked in
   iou-architectuur#132, still open on 15 November. (Was 8 November carry-over 1, 11 October carry-over 1 and 4 October
   carry-over 1 before it.)

### 18 November 2026 — RONL Business API v2026.11.4 → v2026.11.5 and hot fix #473 (production, `1784a72`)

1. **The accepted Semgrep findings have their reasons in git** (#470, `SECURITY-PIPELINE.md:182-213`): one row per package and
   advisory, six rows (react-router ×2, postcss-selector-parser, minimatch 10, minimatch 9, playwright-core as a false positive).
   That answers the RONL Business API's half of the 15 November carry-over above; the Linked Data Explorer's two entries are not
   covered, so iou-architectuur#132 stays open. One more `nosemgrep`, on the certificate probe (`check-upstream-certs.mjs:111`).
   Bears on `dependency-scanning.md`.
2. **The `audit` job runs two more script tests** (`zizmor.yml:194-206`): `keycloak-restrict-rba-client.test.mjs` and
   `keycloak-add-brp-raadpleger.test.mjs`, so sixteen steps. Still 15 workflows and 45 `uses:` references. Bears on
   `code-standards.md`.
3. **The frontend's production pattern includes `keycloak-themes/`** (#465, `scripts/promotion-targets.sh:50`), which closes the
   difference recorded on 15 November; ronl-business-api#457 is closed. Bears on `development-workflow/overview.md`.
4. **Dependencies:** hono 4.13.16, `@hono/node-server` 2.1.6 and fast-xml-parser 5.12.0 clear eight Dependabot alerts (#469);
   three remained open on 18 November (two react-router mediums at runtime, one minimatch high in development). supertest 7.3.1;
   one prettier in the lockfile, the backend's own pin gone (#287); `cheerio` removed (#467). SBOM 2026.11.5 lists 471 components
   (493 before; npm 11.19.1). Bears on `dependency-scanning.md`, `supply-chain.md`, the ICTU R10 and R3 cells.
5. **Two new live-realm scripts** change acceptance and production Keycloak: `keycloak-restrict-rba-client.sh` and
   `keycloak-add-brp-raadpleger.sh`, both already run on both realms. Bears on `controls.md` if it lists how the realms change.
6. **PSA, for the re-check on `main`; word every open gap generically, without routes, hosts or issue links:**
   - **AB-17:** the RONL Business API's login client accepts only its own return addresses and requires PKCE (#460). On
     acceptance a wider pattern remains for preview builds, as an accepted risk.
   - **AB-18:** a resident can start only the services offered to residents and look up only their own personal record;
     caseworkers may look up anyone (#463, #464, `packages/backend/src/auth/brp-access.ts`).
   - **AB-19:** a third action is gated by assurance level: the personal-record lookup, `hoog` for one's own record and
     `substantieel` for staff with the lookup role. Status probably stays *deels*.
   - **R-03:** until DigiD is active, the citizen service number in the token is a test value set on test accounts.
   - **AB-23 / a possible new risk,** if still open on Sunday: the portal exposes the citizen service number in the browser's
     developer tools, and the record of a personal-data lookup does not always name every person asked for (filed as
     ronl-business-api#477 and #478; the PSA text carries no link while they are open).
   - **R-14, R-16, AB-26:** no change found in this range.
7. **Hot fix #473 is on production in no release:** Flevoland's accent fill. No rule, workflow or hook changed. It bears on no
   contributing page; `ci-posture-deck.md` and the PSA do not describe tenant colours.

### 22 November 2026 — CPSV Editor v2026.11.1 → v2026.11.2 (production, `5d6345c`) and Linked Data Explorer v2026.11.2 → v2026.11.3 (production, `4e80c74`)

1. **zizmor-action no longer runs zizmor from a container digest.** Since v0.8.0 the action installs zizmor from the lock
   file it ships per version (`support/locks/zizmor-<version>.txt`) with `pip download --require-hashes`; the Renovate
   mapping to the `ghcr.io/zizmorcore/zizmor` image is only how Renovate notices a release. The CPSV Editor and the Linked
   Data Explorer pin v0.8.1 on `main` (ttl-editor `69be5ac`, `.github/workflows/zizmor.yml:75`; LDE `c0065c8`,
   `SECURITY-PIPELINE.md` §4); zizmor stays 1.29.0. Check the RONL Business API's pin before writing anything for all
   three. Bears on `supply-chain.md` (the digest-table sentences around :389 and :431-441) and PSA **AB-28** (still pinned,
   now by wheel hashes).
2. **The CPSV Editor's `main` no longer lags `acc` by the zizmor bump and the lab.** `main` `5d6345c` carries both and
   v0.8.1; `acc` is one fix ahead (#268, vendor logo scaling). Bears on the status box in `supply-chain.md:15-35`,
   `ci-posture-deck.md` (EN :55, :235; NL :45-46) and `the-gitlab-mirror.md:79`.
3. **The CPSV Editor's deploys queue per branch** (`06a4672`): both Static Web Apps workflows set `concurrency` per ref
   with `cancel-in-progress: false`; pull requests keep their own group. Bears on `dependency-scanning.md:83-84` if it
   compares the components' concurrency policies.
4. **The Linked Data Explorer's SBOM check compares content** (`0244183`, `scripts/write-sbom.mjs`): `--check` ignores
   `metadata.tools`, so an SBOM written with another npm no longer fails. ttl-editor#269 and ronl-business-api#481 are to
   follow, so state it per repository. New committed SBOMs: `linked-data-explorer-2026.11.3.cdx.json`,
   `ttl-editor-2026.11.2.cdx.json`. Bears on `dependency-scanning.md:420-429`.
5. **Linked Data Explorer tooling:** the backend dev server runs on `tsx` instead of `ts-node` (12 fewer transitive
   packages), supertest 7, `@types/jszip` removed; `SECURITY-PIPELINE.md` counts twelve workflows (closes
   linked-data-explorer#342); `npm run test:shacl-smoke` runs four checks and is not yet in CI (#352). Still 12 workflows,
   rulesets and hooks unchanged. Bears on `code-standards.md` and `dependency-scanning.md`.
6. **CPSV Editor tooling:** `test:app` is a new phase script, and `src/testing/phaseScripts.test.js` fails when a test
   file belongs to no phase script; Vitest 5.1.0. Still 8 workflows. Bears on `code-standards.md` and the ICTU test rows.
7. **PSA, for the re-check on `main`** (generic wording, no routes, hosts or issue links for open gaps):
   - **AB-17:** the Linked Data Explorer accepts only access tokens, and answers that sign-in is unavailable when the issuer
     cannot be reached, instead of asking to sign in again (`auth.middleware.ts:88-93, 129-141`). Verify the RONL Business
     API before writing it as a general statement.
   - **AB-20, AB-21, R-02:** unchanged. The CPSV Editor no longer lets a lapsed session fall back to a test deploy, but the
     author role is still not per organisation.
   - **Possible risk wording**, only if still open on Sunday: an anonymous test feature on the acceptance tier can cause
     many engine reads per request, and a burst of unknown signing-key references can make sign-in read as unavailable for
     up to a minute (filed as linked-data-explorer#358; no link in the PSA while open).
   - Re-pin every PSA page and the template to CPSV Editor `5d6345c` and Linked Data Explorer `4e80c74`.

## Drained

| Pass | Entries drained | Where they landed |
|---|---|---|
| 20 September 2026 | — | The first weekly pass predates this queue: the cross-cutting re-check ran inside the RONL Business API sync to v2026.09.9, which is the run that split the two halves apart |
| 27 September 2026 | All of 24 September LDE (1–10) and RBA (1–15); all of 26 September CPSV (1–7), LDE (1–11) and RBA (1–10, 12). LDE-26 #11 (Windows `test:scripts`) is a tooling defect, filed as iou-architectuur#105 item 5 rather than documented; RBA-24 #11 (preview opt-in) is documented on the component's own `cicd.md` and `backend-development.md`, and no contributing page contradicts it; LDE-24 #4 settled by reading the four App Services from Azure (LDE `NODE\|24-lts`, RBA `NODE\|22-lts`) | `supply-chain.md`, `dependency-scanning.md`, `controls.md`, `code-standards.md`, `branch-protection.md`, `coverage-floor.md`, `build-provenance.md`, `the-gitlab-mirror.md`, `index.md`, `ictu-dependency-guideline.md`, `ci-posture-deck.md`, `development-workflow/*`, `doc-architecture/*`; source defects to iou-architectuur#105 items 8–18 |
| 4 October 2026 | Every entry of 27 September (carry-overs 1–2), 28 September RBA (1–6), 30 September RBA (1–3, 5, 7–12, and the first halves of 4 and 6), 2 October CPSV (1–4), 3 October RBA (1–7) and 3 October LDE (1–9). Carry-over 2 (the `api-specification.md` comment) was fixed by the Linked Data Explorer sync of 3 October. 2 October CPSV #4 changed before it could land: `0bf8e46` runs the live-stack preflight only for journeys that need it. 3 October RBA #1 was partly right — the RONL Business API's first audit catch was #208 (adm-zip), #303 the first on `acc`'s own tree. 30 September #4 (Semgrep UI) and #6 (85% margin) carried over above | `supply-chain.md`, `dependency-scanning.md`, `ictu-dependency-guideline.md`, `controls.md`, `branch-protection.md`, `coverage-floor.md`, `build-provenance.md`, `the-gitlab-mirror.md`, `ci-posture-deck.md` (and its Dutch translation), `code-standards.md`, `index.md`, `development-workflow/*`, `doc-architecture/openapi-rendering.md` and `technology-stack.md`; source findings to ronl-business-api (Redis Renovate hold, `SECURITY-PIPELINE.md` `main` row, docker major approval), linked-data-explorer#254 and ttl-editor |
| 11 October 2026 | Every entry of 4 October (carry-over 2, the 85% margin, now restated with the files below it), 6 October LDE (1–7), 9 October RBA (1–9), 9 October Norm Editor (3–4), 10 October CPRMV (1–3), 10 October CPSV (1–5), 10 October LDE (1–5; item 5 was done by the RBA sync of 11 October) and 11 October RBA (1–6). 9 October RBA #1 (SBOM checks cannot fail) is history in all three since #274/#354; CPRMV #1 became one sentence on `controls.md`; 4 October carry-over 1 and Norm Editor 1–2 carried over above, with a new lead on the Azure DevOps pipeline file | `supply-chain.md`, `dependency-scanning.md`, `controls.md`, `build-provenance.md`, `ci-posture-deck.md` (and its Dutch translation), `code-standards.md`, `branch-protection.md`, `coverage-floor.md`, `the-gitlab-mirror.md`, `index.md`, `ictu-dependency-guideline.md`, `development-workflow/*`, `doc-architecture/*`; no new source findings |
| 8 November 2026 | 11 October carry-over 2 (Norm Editor `build_gui`: observed in pipeline 737 — the step fails on a missing `node` without failing the job; remote tags still only `2026.07.0` and `2026.07.1`) and the first, existence half of carry-over 1 (accepted-risk entries read from Semgrep; the unreadable reasons carried over above); every entry of 7 November CPSV (1–4), LDE (1–5) and RBA (1–8). LDE #2 was partly wrong — the Linked Data Explorer already carried ten inline `nosemgrep` lines, and `aec5c34` added five; LDE #3 was wider than queued — the `follow-redirects` high is open on `acc` too. The PSA items (CPSV #4, LDE #4, RBA #4–5) were verified by the PSA re-check: AB-13, AB-08 and R-01 reworded, AB-04 updated, AB-03 / R-04 and AB-20 / R-02 unchanged. RBA #6 touched no contributing page; RBA #7 landed on the ICTU page. Found in the same pass, not queued: `ci-posture-deck.md` left `lockfile-review` out of its `acc` cells, and four pages dated three RONL Business API changes to v2026.09.11 that shipped in v2026.09.10. Carry-over 3 (Azure DevOps pipeline file) stays, still unverifiable | `supply-chain.md`, `dependency-scanning.md`, `code-standards.md`, `controls.md`, `branch-protection.md`, `coverage-floor.md`, `build-provenance.md`, `the-gitlab-mirror.md`, `ci-posture-deck.md` (and its Dutch translation), `index.md`, `ictu-dependency-guideline.md`, `development-workflow/*`, `doc-architecture/*`; `docs/{nl,en}/psa/**`; no new source findings |
| 15 November 2026 | 8 November carry-over 2 (the Azure DevOps pipeline file): settled by the user — a push of `acc` to `flevoland` deploys the acceptance site through the root `azure-static-web-apps-pipeline.yml`, which the 14 November push showed within two minutes; `az devops` is still not installed. Every entry of 12 November CPSV (1–3), LDE (1–5) and RBA (1–3), 14 November RBA v2026.11.3 (1–5) and 14 November RBA v2026.11.4 (1–7). The PSA items were verified on `main` by the PSA re-check: no status changed; AB-08, AB-17, AB-20, AB-21, AB-23, AB-18, AB-26 and AB-32 reworded, R-02 reworded with links to the closed parts (linked-data-explorer#163, ttl-editor#234), and R-16 added for the open authentication gap, generic and unlinked. Leads that did not hold: the Linked Data Explorer does not record who may start a process (only the RONL Business API enforces it), and `keycloak-js` 23.0.7 dates from February 2024, not December 2023. 14 November v2026.11.4 #6 (the BES test users in ACC and PROD) rests on the owner's note; AB-15 does not depend on it. `upstream-certs.yml` also runs on pull requests that touch its own files. Found in the same pass, not queued: the Keycloak VM's Postgres has been digest-pinned since 6 November, the RONL Business API local stack has six images, and `openapi-rendering.md` said the Linked Data Explorer's API declares no security scheme. 8 November carry-over 1 stays above | `supply-chain.md`, `dependency-scanning.md`, `code-standards.md`, `controls.md`, `branch-protection.md`, `coverage-floor.md`, `build-provenance.md`, `the-gitlab-mirror.md`, `ci-posture-deck.md` (and its Dutch translation), `index.md` (stamp only), `ictu-dependency-guideline.md`, `development-workflow/*`, `doc-architecture/*`; `docs/{nl,en}/psa/**` and the template; source findings: the Linked Data Explorer's `SECURITY-PIPELINE.md` counts eleven workflows (twelve; linked-data-explorer#342), the RONL Business API's five local images (six; added to ronl-business-api#457) |
