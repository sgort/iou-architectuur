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
drained by the pass of 27 September, everything queued from 27 September to 3 October by the pass of 4 October, everything queued from 4 to 11 October by the pass of 11 October, and everything queued from 12 October to 7 November — the three syncs of 7 November — by the pass of 8 November, with two of the three 11 October carry-overs (see the table at the end).

### 8 November 2026 — carried over from the weekly pass

1. **The reasons recorded with the Semgrep Supply Chain accepted-risk entries.** Half of the 11 October carry-over 1 is
   now verified: the Semgrep tool's state filter works, and the entries exist — on 8 November RBA `main` held four findings
   ignored in the platform (`postcss-selector-parser` ×2, `react-router` ×2) and LDE `acc` two (`deepmerge`, `@tiptap/core`);
   `dependency-scanning.md` now says so. The reason and date recorded with each are not returned by the tool and cannot be
   read from here; tracked in iou-architectuur#132. (Was 11 October carry-over 1, and 4 October carry-over 1 before it.)
2. **A tracked `azure-static-web-apps-pipeline.yml` at this repository's root** is an Azure DevOps pipeline that triggers on
   pushes and pull requests to `acc` (last changed 25 June 2026, `38f6725`). `doc-architecture/technology-stack.md` says there
   are two deployment pipelines and that pushing to `acc` deploys nothing; if Azure DevOps runs this file, both claims are at
   risk. Still unverifiable on 8 November: the `az devops` extension is not installed (`az extension list` is empty), and the
   pass installs nothing. Bears on: `technology-stack.md`, `the-gitlab-mirror.md` if it describes the Flevoland remote.
   (Was 11 October carry-over 3.)

### 12 November 2026 — CPSV Editor v2026.11.0 → v2026.11.1 (production, `6910bb8`)

1. **Optional sign-in, and deploying and publishing by role.** The editor signs in through Keycloak (realm `ronl`, client
   `ttl-editor`, `keycloak-js` 23.0.7, a new runtime dependency; dd7e87f) and presents the token to the Linked Data Explorer.
   Deploy, publish, update-service, list-graphs and test-connection need `lde-author`; anyone else gets a test deploy into
   tenant `TestOnly`, offered only off production (4334a55). Bears on PSA **AB-17** (its note says the design tools check no
   tokens yet), **AB-20** (now authenticated and role-authorised, not per organisation), **AB-23** (a publish writes one log
   line, not an audit record), **R-02**, **AB-32** (the editor now uses Keycloak), and **AB-28** (`keycloak-js` 23.0.7 dates
   from December 2023, the same in all three repositories); `supply-chain.md` for the dependency.
2. **The TriplyDB token has left the browser.** Publishing is one call to the Linked Data Explorer's
   `POST /v1/triplydb/publish`; the backend holds the token and an old browser copy is deleted on load (e8749d5, closes
   ttl-editor#234). Bears on PSA chapters 6–8 (where the secret lives, data flows), **R-02**, and the #234 Issue cell, which can
   now carry a link if the gap is judged closed.
3. **Node 24.22.2** in `.nvmrc` and the five tooling-workflow literals. **Pins on `main`:** setup-node v7.1.0, upload-artifact
   v7.0.2; `acc` is ahead with zizmor-action v0.8.0 (`e82375e`). Still 8 workflows; rulesets, Renovate, hooks and `.npmrc`
   unchanged. Bears on: `supply-chain.md`, `code-standards.md`, `ci-posture-deck.md` (the `main`/`acc` footnote).

### 12 November 2026 — Linked Data Explorer v2026.11.1 → v2026.11.2 (production, `e11e4ef`)

1. **Writes need a Keycloak token with `lde-author`** (#163, closed 12 November): `requireAuthor` on 16 handlers,
   `optionalAuthor` on `POST /v1/dmns/deploy`, 17 operations marked `bearerAuth`; `KEYCLOAK_URL` is required on acceptance and
   production. Signed-out deploys go to tenant `TestOnly` on localhost and acceptance only (rate-limited, swept after 48 hours).
   Bears on PSA **AB-17** (now false for the LDE), **AB-20** (writes authenticated and authorised; only publish is logged —
   probably still *deels*), **AB-21**, **R-02** (partly mitigated; the anonymous test deploy is a deliberate exception) and
   **AB-32** (a second consumer); and the R-02/AB-20 Issue cells, now that #163 is closed.
2. **Routes and secrets:** the three eDOCS write routes are removed; `POST /v1/triplydb/publish`,
   `GET /v1/triplydb/publish-target` and `GET /v1/dmns/deploy/options` are new; the TriplyDB token is a backend secret on the
   App Service. The CSP adds the Keycloak origin and `frame-src`, and `frame-ancestors` moves from `'none'` to `'self'`. Bears
   on PSA chapters 7–8 and `openapi-rendering.md` if it records the CSP.
3. **Node 24.22.2** in `.nvmrc` and five workflow literals (engines stay `>=24.22.1`); setup-node v7.1.0, upload-artifact v7.0.2
   and zizmor-action v0.8.0 recorded in `SECURITY-PIPELINE.md` (zizmor stays 1.29.0). Still 12 workflows, rulesets and hooks
   unchanged; new SBOM `linked-data-explorer-2026.11.2.cdx.json`. Bears on: `supply-chain.md`, `controls.md`.
4. **follow-redirects 1.16.2** (`bfc7a50`) fixes the open high, but the scheduled audit on `acc` failed again on 12 November
   before #301 merged, and #313 is still open: re-check the next scheduled run. Bears on: `dependency-scanning.md`, the ICTU
   R10 cell.
5. **The per-file branch floor did its job:** it failed the acceptance deploy checks on three new files until tests were added
   (`9112835`). Evidence for `coverage-floor.md`.

### 12 November 2026 — RONL Business API v2026.11.1 → v2026.11.2 (production, `ad0fd62`)

1. **Keycloak for the design tools:** `scripts/keycloak-add-lde-clients.sh` adds the `lde-author` role and the public PKCE
   clients `linked-data-explorer` and `ttl-editor` (b74db31, 57f3943), live on acceptance and production. Caddy drops
   `X-Frame-Options` on the Keycloak third-party-cookie path only (2549feb). Bears on PSA **AB-20**, **R-02** and **AB-32**;
   **R-01** and **AB-13** are unchanged by this release.
2. **The VM's Operaton 1.0.0 is pinned by digest** (568b23f); the VM's Caddy image (`caddy:2-alpine`) still floats. Bears on
   PSA **AB-28** and `supply-chain.md` (the container footnote on the ICTU page too).
3. **Node 24.22.2** in the four tooling workflows (2ba78fa). Still 14 workflows; rulesets, hooks, Renovate,
   `SECURITY-PIPELINE.md`, `.nvmrc` and `.npmrc` unchanged. The lockfile refresh used no cooldown exception; SBOM 2026.11.2
   lists 493 components (npm 11.19.1). Bears on: `code-standards.md`, `supply-chain.md`, `dependency-scanning.md`.

## Drained

| Pass | Entries drained | Where they landed |
|---|---|---|
| 20 September 2026 | — | The first weekly pass predates this queue: the cross-cutting re-check ran inside the RONL Business API sync to v2026.09.9, which is the run that split the two halves apart |
| 27 September 2026 | All of 24 September LDE (1–10) and RBA (1–15); all of 26 September CPSV (1–7), LDE (1–11) and RBA (1–10, 12). LDE-26 #11 (Windows `test:scripts`) is a tooling defect, filed as iou-architectuur#105 item 5 rather than documented; RBA-24 #11 (preview opt-in) is documented on the component's own `cicd.md` and `backend-development.md`, and no contributing page contradicts it; LDE-24 #4 settled by reading the four App Services from Azure (LDE `NODE\|24-lts`, RBA `NODE\|22-lts`) | `supply-chain.md`, `dependency-scanning.md`, `controls.md`, `code-standards.md`, `branch-protection.md`, `coverage-floor.md`, `build-provenance.md`, `the-gitlab-mirror.md`, `index.md`, `ictu-dependency-guideline.md`, `ci-posture-deck.md`, `development-workflow/*`, `doc-architecture/*`; source defects to iou-architectuur#105 items 8–18 |
| 4 October 2026 | Every entry of 27 September (carry-overs 1–2), 28 September RBA (1–6), 30 September RBA (1–3, 5, 7–12, and the first halves of 4 and 6), 2 October CPSV (1–4), 3 October RBA (1–7) and 3 October LDE (1–9). Carry-over 2 (the `api-specification.md` comment) was fixed by the Linked Data Explorer sync of 3 October. 2 October CPSV #4 changed before it could land: `0bf8e46` runs the live-stack preflight only for journeys that need it. 3 October RBA #1 was partly right — the RONL Business API's first audit catch was #208 (adm-zip), #303 the first on `acc`'s own tree. 30 September #4 (Semgrep UI) and #6 (85% margin) carried over above | `supply-chain.md`, `dependency-scanning.md`, `ictu-dependency-guideline.md`, `controls.md`, `branch-protection.md`, `coverage-floor.md`, `build-provenance.md`, `the-gitlab-mirror.md`, `ci-posture-deck.md` (and its Dutch translation), `code-standards.md`, `index.md`, `development-workflow/*`, `doc-architecture/openapi-rendering.md` and `technology-stack.md`; source findings to ronl-business-api (Redis Renovate hold, `SECURITY-PIPELINE.md` `main` row, docker major approval), linked-data-explorer#254 and ttl-editor |
| 11 October 2026 | Every entry of 4 October (carry-over 2, the 85% margin, now restated with the files below it), 6 October LDE (1–7), 9 October RBA (1–9), 9 October Norm Editor (3–4), 10 October CPRMV (1–3), 10 October CPSV (1–5), 10 October LDE (1–5; item 5 was done by the RBA sync of 11 October) and 11 October RBA (1–6). 9 October RBA #1 (SBOM checks cannot fail) is history in all three since #274/#354; CPRMV #1 became one sentence on `controls.md`; 4 October carry-over 1 and Norm Editor 1–2 carried over above, with a new lead on the Azure DevOps pipeline file | `supply-chain.md`, `dependency-scanning.md`, `controls.md`, `build-provenance.md`, `ci-posture-deck.md` (and its Dutch translation), `code-standards.md`, `branch-protection.md`, `coverage-floor.md`, `the-gitlab-mirror.md`, `index.md`, `ictu-dependency-guideline.md`, `development-workflow/*`, `doc-architecture/*`; no new source findings |
| 8 November 2026 | 11 October carry-over 2 (Norm Editor `build_gui`: observed in pipeline 737 — the step fails on a missing `node` without failing the job; remote tags still only `2026.07.0` and `2026.07.1`) and the first, existence half of carry-over 1 (accepted-risk entries read from Semgrep; the unreadable reasons carried over above); every entry of 7 November CPSV (1–4), LDE (1–5) and RBA (1–8). LDE #2 was partly wrong — the Linked Data Explorer already carried ten inline `nosemgrep` lines, and `aec5c34` added five; LDE #3 was wider than queued — the `follow-redirects` high is open on `acc` too. The PSA items (CPSV #4, LDE #4, RBA #4–5) were verified by the PSA re-check: AB-13, AB-08 and R-01 reworded, AB-04 updated, AB-03 / R-04 and AB-20 / R-02 unchanged. RBA #6 touched no contributing page; RBA #7 landed on the ICTU page. Found in the same pass, not queued: `ci-posture-deck.md` left `lockfile-review` out of its `acc` cells, and four pages dated three RONL Business API changes to v2026.09.11 that shipped in v2026.09.10. Carry-over 3 (Azure DevOps pipeline file) stays, still unverifiable | `supply-chain.md`, `dependency-scanning.md`, `code-standards.md`, `controls.md`, `branch-protection.md`, `coverage-floor.md`, `build-provenance.md`, `the-gitlab-mirror.md`, `ci-posture-deck.md` (and its Dutch translation), `index.md`, `ictu-dependency-guideline.md`, `development-workflow/*`, `doc-architecture/*`; `docs/{nl,en}/psa/**`; no new source findings |
