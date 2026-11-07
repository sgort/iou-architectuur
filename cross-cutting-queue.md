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
drained by the pass of 27 September, everything queued from 27 September to 3 October by the pass of 4 October, and everything queued from 4 to 11 October by the pass of 11 October (see the table at the end).

### 11 October 2026 — carried over from the weekly pass

1. **The Semgrep Supply Chain triage of 30 September is recorded as accepted risk in the Semgrep UI.** Still unverified:
   the Semgrep tool returned only open findings (11 on RBA `main`) and ignored the state filter, so whether the
   accepted-risk entries exist, and with what reason, cannot be read from here. Bears on: `dependency-scanning.md`
   (Semgrep Supply Chain). (Was 4 October carry-over 1.)
2. **The Norm Editor's `build_gui` changelog step, and its release tags.** `code-standards.md` now states what is in source
   (the step regenerates the changelog in `docker:latest`; the remote holds only the tags `2026.07.0` and `2026.07.1`), but
   that the step fails is inferred, not observed — the pipelines are not visible from outside the project — and whether the
   later tags exist in any clone is unknown (regels/editor#1). (Was 9 October Norm Editor items 1–2.)
3. **A tracked `azure-static-web-apps-pipeline.yml` at this repository's root** is an Azure DevOps pipeline that triggers on
   pushes and pull requests to `acc` (last changed 25 June 2026). `doc-architecture/technology-stack.md` says there are two
   deployment pipelines and that pushing to `acc` deploys nothing; if Azure DevOps runs this file, both claims are at risk.
   Unverifiable without the `az devops` extension. Bears on: `technology-stack.md`, `the-gitlab-mirror.md` if it describes
   the Flevoland remote.

### 7 November 2026 — CPSV Editor v2026.10.1 → v2026.11.0 (production, `84886c9`)

Read at `origin/main` `84886c9` (Deploy PROD (white-sky) #110). The pages themselves were not touched and no stamp was refreshed.

1. **Node 24.22.1** in `.nvmrc` and four workflows, zizmor carrying the literal twice (9537af4); npm 11.19.1. The `.npmrc` cooldown
   exception was used for the advisory refresh (`--min-release-age=6`, 03d5df6). Bears on: `supply-chain.md` (Node table, cooldown
   exceptions), `ictu-dependency-guideline.md` (R6/R10 evidence).
2. **`acc` is ahead of `main` by two Renovate action pins** — `actions/setup-node` v7.1.0 (#230) and `actions/upload-artifact` v7.0.2
   (#215); `main` still runs setup-node v7.0.0. Read the pins at `acc` in the pass. Bears on: `supply-chain.md` (pinned register).
3. **Still eight workflows**; two new SBOM files (2026.10.2, 2026.11.0). Bears on: `code-standards.md` (count unchanged — verified).
4. **PSA:** the Service tab lists published services through the Linked Data Explorer's `/v1/triplydb/query` proxy, without credentials
   (a read). No AB status changes; **AB-03 / R-04** unchanged — the editor still writes CPRMV 0.4.1 (`vocabularies.config.js:29`).
   A new inter-service relation, `dct:requires`, now appears in published data. Bears on: `docs/{nl,en}/psa/06-data-architecture.md`
   and `07-integration-architecture.md` if they list the published relations or the editor's calls.

### 7 November 2026 — Linked Data Explorer v2026.10.2 → v2026.11.1 (production, `189435e`)

Read at `origin/main` `189435e` (Promote to Production #9). The pages themselves were not touched and no stamp was refreshed.

1. **Node 24.22.1 / npm 11.19.1**: `.nvmrc`, `engines >=24.22.1`, and the literals in five workflows (dependency-audit,
   dependency-review, sbom, zizmor ×2). Cooldown exception used for the lockfile refresh. Bears on: `supply-chain.md`,
   `ictu-dependency-guideline.md`.
2. **The first inline `nosemgrep` suppressions** (`processIdentity.ts`, `build-openapi.cjs`), and `@tiptap/core` / `deepmerge` triaged
   as accepted risk. Bears on: `dependency-scanning.md` (the per-repository `nosemgrep` count, accepted risk).
3. **A production high is open on `main`**: follow-redirects GHSA-mrwp-f3q8-3g9p, linked-data-explorer#313, opened 7 November; the
   lockfile still pins 1.16.1. Bears on: `dependency-scanning.md` (alert table), `ictu-dependency-guideline.md` (R10).
4. **PSA — AB-08 / AB-13 / R-01:** the backend now calls Operaton with basic auth (`OPERATON_USERNAME` / `OPERATON_PASSWORD`; start-up
   refused on ACC and PROD without them; `OPERATON_API_KEY` removed) and encodes every engine path value. The engine asks for
   credentials; whether it is still reachable from outside is the RONL Business API section below. **AB-20 / R-02 unchanged**: the
   Linked Data Explorer's own deploy and evaluate routes stay anonymous while holding the engine credentials (#163, open). Keep the
   wording generic, no issue link while open.
5. Findings filed as linked-data-explorer#328 (a stale comment, a fixture deploy that checks the engine without its login, #299's
   Node version). #300 is still open, unchanged.

### 7 November 2026 — RONL Business API v2026.10.2 → v2026.11.1 (production, `35fb3a8`)

Read at `origin/main` `35fb3a8` (Promote to Production #11). The pages themselves were not touched and no stamp was refreshed.

1. **Node 22.23.4** (app) and **24.22.1** (tooling), action pins bumped by digest; still **fourteen** workflows; the frontend
   acceptance filter adds `keycloak-themes/**`. The `.npmrc` urgent-security exception was used twice. Bears on: `code-standards.md`,
   `supply-chain.md`.
2. **New gates**: CI fails on a new hard-coded hex colour; stylelint is added in report-only mode, and `test:stylelint` runs in no CI job
   or hook. New direct dev dependencies: stylelint and `@axe-core/playwright` (axe checks in the E2E suite). Bears on: `code-standards.md`
   (lint/format and CI section), `dependency-scanning.md` if it lists new direct dependencies.
3. **The release SBOM is generated with CI's npm** (11.19.1). A local `sbom:check` with npm 10.9.9 (the npm of the app's Node 22)
   fails and generates 505 components; with npm 11.19.1 the committed 487-component SBOM regenerates identically (measured
   7 November). Bears on: `supply-chain.md` / `dependency-scanning.md` (SBOM paragraph).
4. **PSA — AB-04:** `LICENSE` (EUPL-1.2) is now on `main` — the condition the 6 November note waited for. Propose the note change.
5. **PSA — AB-08 / AB-13 / R-01:** the VM's Operaton is pinned to 1.0.0 with authentication and authorisation on; reading and
   evaluating rules stays public through a read-only account, everything else on the engine's REST API needs credentials; the backend
   and its worker send credentials and a production start is refused without them (#415, closed). The engine is still reachable, but
   no longer without a login: propose rewording R-01 and re-weighing AB-13's status in the pass — generic wording, no hostnames or
   routes. A temporary engine access log remains in the Caddyfile, and the VM's Caddy image floats on `caddy:2-alpine` (filed below).
   Operaton 1.0.0 on the VM versus 2.1.5 locally is #423; unpinned VM images #196. Bears on: `08-security-and-privacy.md`,
   `09-technical-infrastructure.md`, chapter 11.
6. **One Keycloak theme copy** at `keycloak-themes/ronl/`; `deployment/vm/keycloak/themes/` is deleted. Bears on: PSA chapter 9 if it
   names the theme location; `contributing/` pages that describe the Keycloak deployment.
7. **E2E measured 7 November against the local stack**: frontend 18 specs, 61 tests (56 passed, 5 skipped by design), pa-demo 11/11,
   public-site 6/6 with one worker. Bears on: `ictu-dependency-guideline.md` (tests row: e2e specs).
8. Findings filed as ronl-business-api#433 (the ⌘K changelog claim, `test:stylelint` unwired, the temporary engine log, the floating
   Caddy image, #354 items 2–6 still open); #371 fixed. CPSV Editor findings: ttl-editor#238.

## Drained

| Pass | Entries drained | Where they landed |
|---|---|---|
| 20 September 2026 | — | The first weekly pass predates this queue: the cross-cutting re-check ran inside the RONL Business API sync to v2026.09.9, which is the run that split the two halves apart |
| 27 September 2026 | All of 24 September LDE (1–10) and RBA (1–15); all of 26 September CPSV (1–7), LDE (1–11) and RBA (1–10, 12). LDE-26 #11 (Windows `test:scripts`) is a tooling defect, filed as iou-architectuur#105 item 5 rather than documented; RBA-24 #11 (preview opt-in) is documented on the component's own `cicd.md` and `backend-development.md`, and no contributing page contradicts it; LDE-24 #4 settled by reading the four App Services from Azure (LDE `NODE\|24-lts`, RBA `NODE\|22-lts`) | `supply-chain.md`, `dependency-scanning.md`, `controls.md`, `code-standards.md`, `branch-protection.md`, `coverage-floor.md`, `build-provenance.md`, `the-gitlab-mirror.md`, `index.md`, `ictu-dependency-guideline.md`, `ci-posture-deck.md`, `development-workflow/*`, `doc-architecture/*`; source defects to iou-architectuur#105 items 8–18 |
| 4 October 2026 | Every entry of 27 September (carry-overs 1–2), 28 September RBA (1–6), 30 September RBA (1–3, 5, 7–12, and the first halves of 4 and 6), 2 October CPSV (1–4), 3 October RBA (1–7) and 3 October LDE (1–9). Carry-over 2 (the `api-specification.md` comment) was fixed by the Linked Data Explorer sync of 3 October. 2 October CPSV #4 changed before it could land: `0bf8e46` runs the live-stack preflight only for journeys that need it. 3 October RBA #1 was partly right — the RONL Business API's first audit catch was #208 (adm-zip), #303 the first on `acc`'s own tree. 30 September #4 (Semgrep UI) and #6 (85% margin) carried over above | `supply-chain.md`, `dependency-scanning.md`, `ictu-dependency-guideline.md`, `controls.md`, `branch-protection.md`, `coverage-floor.md`, `build-provenance.md`, `the-gitlab-mirror.md`, `ci-posture-deck.md` (and its Dutch translation), `code-standards.md`, `index.md`, `development-workflow/*`, `doc-architecture/openapi-rendering.md` and `technology-stack.md`; source findings to ronl-business-api (Redis Renovate hold, `SECURITY-PIPELINE.md` `main` row, docker major approval), linked-data-explorer#254 and ttl-editor |
| 11 October 2026 | Every entry of 4 October (carry-over 2, the 85% margin, now restated with the files below it), 6 October LDE (1–7), 9 October RBA (1–9), 9 October Norm Editor (3–4), 10 October CPRMV (1–3), 10 October CPSV (1–5), 10 October LDE (1–5; item 5 was done by the RBA sync of 11 October) and 11 October RBA (1–6). 9 October RBA #1 (SBOM checks cannot fail) is history in all three since #274/#354; CPRMV #1 became one sentence on `controls.md`; 4 October carry-over 1 and Norm Editor 1–2 carried over above, with a new lead on the Azure DevOps pipeline file | `supply-chain.md`, `dependency-scanning.md`, `controls.md`, `build-provenance.md`, `ci-posture-deck.md` (and its Dutch translation), `code-standards.md`, `branch-protection.md`, `coverage-floor.md`, `the-gitlab-mirror.md`, `index.md`, `ictu-dependency-guideline.md`, `development-workflow/*`, `doc-architecture/*`; no new source findings |
