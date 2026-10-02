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
drained by the pass of 27 September (see the table at the end).

### 27 September 2026 — carried over from the weekly pass

1. **`check-previews.sh` strips the carriage returns `az` writes on Windows — `acc` only.**
   Evidence: ronl-business-api `80e34a2`, merged as `3c44b9e` (#245); not on `main` (`2443adc`).
   Bears on: `the-gitlab-mirror.md` and wherever `check-previews` is described. Document it after the
   promotion that carries it, not before. (Was 26 September RONL Business API item 11.)

2. **A component page repeats a claim the weekly pass corrected on `openapi-rendering.md` — for the next
   Linked Data Explorer sync, not a contributing page.**
   Evidence: `docs/en/linked-data-explorer/reference/api-specification.md`'s leading HTML comment says
   `/v1/openapi.json` "carries no version of its own". It does, since linked-data-explorer `31e7c9f`
   (15 September 2026): `info.version` is `2026.09.8` at `0143ea2`. The weekly pass may not edit a
   component page, so the correction waits for that component's sync.

### 28 September 2026 — RONL Business API v2026.09.13 (acc, `963fe24`)

Queued by the component sync of 28 September 2026. Six facts, read from source at
`963fe24`. No contributing page was opened for edit and no `verified:` stamp was
touched.

1. **`pre-push` gained a sixth step in the RONL Business API.**
   Evidence: `.husky/pre-push` at `963fe24` (commit `2bdff69`) now runs
   `npm run check-swimlane-fixtures` between the shared-package build and the type
   check, so the order is `deps:check` → build `@ronl/shared` →
   `check-swimlane-fixtures` → `type-check` → `lint` → `check-format`.
   Bears on: `code-standards.md`, which says at *"All three repositories wire the
   same two hooks through Husky"* that they **"gate the same two things
   everywhere: staged-file linting and formatting on commit, full linting and
   formatting on push"** — no longer true of this repository — and on the
   `pre-push` bullet below it, which lists the RONL Business API's extras as the
   shared build and a type check only.
   **Do not change the neighbouring claim** that *"None of the three
   repositories' git hooks run the test suite"*: it is still correct. The new
   step compares files against committed sha256 fingerprints; it invokes no
   `test` script.

2. **Two new root npm scripts in the RONL Business API.**
   Evidence: `package.json` at `963fe24` — `"check-swimlane-fixtures": "node
   scripts/check-swimlane-fixtures.mjs"` and `"e2e:deploy-fixtures": "node
   scripts/deploy-e2e-fixtures.mjs"`.
   Bears on: `code-standards.md` wherever per-repository root scripts are
   enumerated — in particular *"Every repository exposes the same four commands
   at its root"*, whose scope should be re-counted rather than re-read.

3. **A fingerprint contract now spans two repositories.**
   Evidence: `rip-bpmn-fingerprints.json` is committed **identically** in
   `ronl-business-api` and `linked-data-explorer`, and
   `scripts/check-swimlane-fixtures.mjs` (its header states the design) has each
   side verify its own copy of the twelve RIP phase BPMNs against it — so a model
   edited upstream fails there until the fingerprints are regenerated, a fixture
   edited downstream fails here because the edit belongs upstream, and updating
   both together is the only green path. Where both trees are checked out the
   hashes are backed by a byte-for-byte comparison; `--sync` copies from upstream
   and `LDE_PATH` says where it is.
   Bears on: `code-standards.md` — this is a gate whose two halves live in
   different repositories, which no per-repository section currently describes —
   and possibly `contributing/index.md`.

4. **The E2E fixture deployer moved out of `ronl-business-api` into
   `linked-data-explorer`; a shim stays behind.**
   Evidence: `scripts/deploy-e2e-fixtures.mjs` at `963fe24` is a 45-line shim
   that resolves the checkout (`LDE_PATH`, defaulting to a sibling), runs the
   real script and passes arguments and the exit code through. Its header records
   why: two copies had already drifted once — when `ronl:documentRef` became a
   comma-separated list, the copy here stopped matching any template and the
   bundle would have failed to deploy.
   Bears on: `contributing/index.md` (the repository table and the local-development
   routes — this repository's end-to-end setup now *requires* a
   `linked-data-explorer` checkout beside it) and
   `development-workflow/overview.md`.

5. **Secret-bearing Keycloak configuration is deliberately kept out of the realm
   export.**
   Evidence: `scripts/keycloak-add-entra-idp.sh` and `scripts/keycloak-entra-idp.json`
   at `963fe24` provision the identity provider per environment with an idempotent
   script that never puts the client secret in argv, in a file or in its output,
   checks the four mapped realm roles exist before creating anything, and verifies
   the result; `config/keycloak/ronl-realm.json` stays secret-free and carries only
   two disabled SAML placeholders.
   Bears on: `controls.md` / `supply-chain.md` — secrets handling as a practice
   across the repositories, rather than as one component's runbook.

6. **The pending `check-previews` item (27 September, #1) is unchanged by this
   sync, and was not resolved here.**
   Its instruction — *document it after the promotion that carries it, not
   before* — **stands exactly as written**. Documenting v2026.09.13 as an
   **acceptance** release does not carry `80e34a2` to `main`: `origin/main` is
   still `2443adc`, and the commit remains `acc`-only.
   Two notes for whoever drains it. First, the fact now has a home on a component
   page — the v2026.09.13 changelog entry, which is explicitly marked as an
   acceptance release — so a contributing page is no longer the only place it
   could be recorded. Second, when the promotion happens it will carry `80e34a2`
   and the whole of v2026.09.13 together, so this item and the RONL Business API's
   re-stamp from `acc` to `prod` in `repo-versions.json` fall due in the same
   pass.

**Nothing else cross-cutting surfaced.** In particular, **no `.github/workflows/`
file changed in this release** — verified with `git diff --stat origin/main
origin/acc` — so the thirteen-workflow count and every CI claim in
`code-standards.md`, `branch-protection.md`, `dependency-scanning.md`,
`coverage-floor.md` and `build-provenance.md` is untouched by it.

### 30 September 2026 — RONL Business API v2026.09.13 → v2026.09.15 (production, `ae06c9e`)

Read at `origin/main` = `ae06c9e` (Promote to Production run #5, all four deploys green); `origin/acc`
`142d909` holds the same tree. v2026.09.13 reached production with v2026.09.14 (#292, `ae4538b`), so the
28 September entry above is no longer acc-only, and **27 September item 1 is now due**: the
`check-previews.sh` carriage-return fix (`80e34a2`) is on `main`.

1. **Skosmos is pinned by digest — the stated reason RBA R2 is held at 3.**
   Evidence: `62c05a7` — `deployment/vm/skosmos/docker-compose.yml` now reads
   `quay.io/natlibfi/skosmos:latest@sha256:c585569…`. The VM Keycloak composes still carry
   `postgres:16-alpine` and `keycloak:23.0` without a digest, and #196 is open; the tag string itself is
   still `latest`. The weekly pass decides the cell.
   Bears on: `ictu-dependency-guideline.md` (the R2 held-at-3 sentence and the work-table footnote on
   row 206), `supply-chain.md` (the "what still floats" VM paragraph).

2. **The audit and SBOM workflows moved to Node 24.21.0 in the RONL Business API.**
   Evidence: `fc50fed` — `dependency-audit.yml:60`, `sbom.yml:56`.
   Bears on: `supply-chain.md` (the sentence that the audit and SBOM literals are `24.20.0` in all three).
   Re-read the CPSV Editor and the Linked Data Explorer before rewriting it.

3. **Inline `nosemgrep` annotations in the RONL Business API grew from 15 to 18.**
   Evidence: `c395696` — frontend `scripts/check-og.mjs:44`, public-site `scripts/check-og.mjs:50,60`
   (`detect-non-literal-regexp`, `path-join-resolve-traversal`; eight findings on three lines), each with
   its reason, per the CLAUDE.md rule recorded the same day.
   Bears on: `dependency-scanning.md` (the suppression counts).

4. **A Semgrep Supply Chain triage, 30 September.**
   Evidence: `3d4913f` — lockfile-only bumps for every finding with a non-breaking fix (multer 2.4.0,
   moment 2.31.0, qs 6.16.0 via body-parser 1.20.8 / express 4.22.3, ip-address 10.7.2, fast-uri 3.1.8,
   brace-expansion ×3), superseding Renovate #273; react-router (fix only in v7) and minimatch via
   @typescript-eslint v6/v7 (dev-only) left as accepted risk in the Semgrep UI.
   Bears on: `dependency-scanning.md`, the ICTU page's alert evidence (R10). Lead to verify: whether this
   lockfile-only pull request skipped the three required site checks, as `code-standards.md` and
   `coverage-floor.md` say such a pull request does.

5. **Branch protection changed on 29–30 September (a settings change, outside the release range).**
   Evidence: `gh api` — the RONL Business API's `main` ruleset (`23019967`) requires `audit` + `scan`, and
   classic protection is deleted on both `acc` and `main` (iou-architectuur#105 item 18).
   Bears on: `branch-protection.md`, `dependency-scanning.md`, `ictu-dependency-guideline.md`,
   `ci-posture-deck.md`, `supply-chain.md` — every sentence describing RBA's `main` as "audit alone" or
   its classic protection as still configured. Re-read LDE and TTL settings at the same time.

6. **The coverage floor's documented margins moved.**
   Evidence: `391b1a8` — the five runner configs' functions-floor comments now say 26 (was 31), dated
   28 September; `73a6764` — the 32 files between 80 and 85% branches are all at 85% or above (#294 open
   for the two unreachable arms).
   Bears on: `coverage-floor.md` (the count the configs carry, the files near the floor).

7. **A new gate inside the backend's `npm test`: conformance coverage.**
   Evidence: `1fb8dbf` — `packages/backend/package.json` `test` and `test:serial` end with
   `&& node scripts/check-conformance-coverage.cjs`, which fails when the OpenAPI document holds an
   operation no test compared against a real response; both backend workflows run it. A filtered Jest run
   skips it. `openapi/pending.json` is deleted (`5d244c5`): the document describes all 133 operations.
   Bears on: `code-standards.md` (CI gates), possibly `coverage-floor.md`; `openapi-rendering.md` if it
   mentions a pending list.

8. **`.prettierignore` keeps design handoff folders out of the format check.**
   Evidence: `96fabb6` — `check-format` and `format` add `--ignore-path .prettierignore`, which excludes
   `*-handoff/`. Note: `docs/pa-demo-social-handoff/` (14 files) is tracked in the repository
   (`13f9c9a`) despite the handoff-package rule.
   Bears on: `development-workflow/design-and-handoff.md`, `code-standards.md`.

9. **Source fixes from iou-architectuur#105 reached production.**
   Evidence: `d61734e` (items 1–3) and `537fc2f` (items 9, 13–16 and the RBA half of 17), both in
   v2026.09.14. `SECURITY-PIPELINE.md` no longer says all four App Services run `NODE|22-lts` or that the
   backend deploy has no lockfile, and quotes its register headline as 39 references across 13
   workflows.
   Bears on: any contributing page that quotes `SECURITY-PIPELINE.md` — a lead, not a finding.

10. **The seven Awb swimlane fixtures are outside the fingerprint contract.**
    Evidence: `edb4ff0` adds `packages/backend/src/rip-swimlane/__fixtures__/awb/*.bpmn` copied from the Linked
    Data Explorer; `check-swimlane-fixtures` only matches `^RipR\d\dProcess\.bpmn$`. `97e0534` made the
    check direction-aware (it names which repository to update, and `--sync` refuses the destructive
    direction unless `--force`). Extends 28 September item 3.
    Bears on: whichever contributing page describes the cross-repository fixture contract.

11. **`~/.claude/CLAUDE.md` now holds sixteen rules.**
    Evidence: `grep -c '^## ' ~/.claude/CLAUDE.md` = 16 on 30 September 2026. Two were added that day:
    "Semgrep: suppress false positives in code, not in the UI" and "Azure: changing an App Service
    setting" (read first, hand the user a short script, verify with `list`, restart and check
    `uptime`, verify the effect).
    Bears on: `development-workflow/skills-and-boundaries.md` (states fourteen) and possibly
    `working-with-claude-code.md`. Re-derive from the file, not from this entry.

12. **RBA acceptance now allows the acceptance docs origin — the RBA spec page's banner and Test
    Request work on both docs tiers.**
    Evidence: `CORS_ORIGIN` on `ronl-business-api-acc` set on 30 September 2026 to
    `https://acc.mijn.open-regels.nl,https://iou-architectuur.open-regels.nl,https://acc.publiek.open-regels.nl,https://acc.iou-architectuur.open-regels.nl`
    and the app restarted; `curl -H "Origin: https://acc.iou-architectuur.open-regels.nl"
    https://acc.api.open-regels.nl/v1/health` now returns that origin in
    `Access-Control-Allow-Origin`. `localhost` is still not allowed.
    Bears on: `doc-architecture/openapi-rendering.md` (says the RBA banner and Test Request work only on
    the production docs tier). The same sentence in the leading HTML comment of
    `ronl-business-api/reference/api-specification.md` was corrected on 30 September 2026.

### 2 October 2026 — CPSV Editor v2026.09.7 → v2026.10.0 (production, `719683b`)

Read at `origin/main` = `719683b` (Deploy PROD (white-sky) #104); `origin/acc` `acac6b3` holds the same tree.

1. **The CPSV Editor's Node literals moved to 24.21.0.**
   Evidence: `c65c698` — `.nvmrc`, `dependency-audit.yml:60`, `sbom.yml:56` and `zizmor.yml:71`, together. All three
   repositories' audit and SBOM workflows now name 24.21.0 (RBA moved in `fc50fed`, item 2 of the 30 September entry).
   Node 24.21.0 bundles npm 11.19, so the cooldown claim still holds.
   Bears on: `supply-chain.md` (the `.nvmrc` table's CPSV row, "24.20.0 in the CPSV Editor" for the zizmor literal,
   "24.20.0 in all three" for the audit and SBOM literals, the npm-bundling row), `ictu-dependency-guideline.md`
   (the Node evidence for R2/R3).

2. **zizmor-action v0.6.4 reached the CPSV Editor, with its register row moved on the bump branch.**
   Evidence: `10b6805` (pin `cc914d7f…`), `79475ce` (the `SECURITY-PIPELINE.md` row, on Renovate's PR #166).
   The same hand step the Linked Data Explorer and the RONL Business API needed — the register drift is now
   observed in all three.
   Bears on: `supply-chain.md` (the register-habit section, which cites only the other two).

3. **The CPSV Editor's `main` now has a ruleset; classic protection is gone on both branches.**
   Evidence: `gh api repos/sgort/ttl-editor/rulesets` — `main promotion gate` (id `24227117`), created
   30 September 2026, active, no bypass actors: pull request (merge commits only), `audit` + `scan` required,
   deletion and non-fast-forward blocked. `branches/main/protection` and `branches/acc/protection` both answer 404.
   `acc supply-chain gate` (`21728745`) keeps its checks and now sets `require_extra_approval_for_unattributed_changes`.
   With item 5 of the 30 September entry, all three repositories now gate `main` with a ruleset requiring
   `audit` + `scan`, and none keeps classic protection.
   Bears on: `branch-protection.md` (the CPSV `main` cell — "classic branch protection, not a ruleset" — and the
   "requires no status check" sentences), `ictu-dependency-guideline.md`, `ci-posture-deck.md`,
   `supply-chain.md#adoption-status`. Source-side: the CPSV `SECURITY-PIPELINE.md:111` still says "`main` still
   requires nothing, as decided in #131".

4. **The fourth end-to-end journey cannot run without the stack it does not need.**
   Evidence: `06ac5e7` adds `e2e/amsterdam-reimport-journey.spec.js`, which needs neither Operaton nor the
   backend; `e2e/global-setup.js` probes both for every run and throws "Nothing was run" when either is down.
   Measured 2 October 2026: 4 of 4 journeys pass against a live stack.
   Bears on: `code-standards.md` and the weekly `tests:` row (e2e count 3 → 4 for the CPSV Editor).

Nothing else cross-cutting surfaced: no `.husky`, `renovate.json` or `package.json` script changed in the range.

## Drained

| Pass | Entries drained | Where they landed |
|---|---|---|
| 20 September 2026 | — | The first weekly pass predates this queue: the cross-cutting re-check ran inside the RONL Business API sync to v2026.09.9, which is the run that split the two halves apart |
| 27 September 2026 | All of 24 September LDE (1–10) and RBA (1–15); all of 26 September CPSV (1–7), LDE (1–11) and RBA (1–10, 12). LDE-26 #11 (Windows `test:scripts`) is a tooling defect, filed as iou-architectuur#105 item 5 rather than documented; RBA-24 #11 (preview opt-in) is documented on the component's own `cicd.md` and `backend-development.md`, and no contributing page contradicts it; LDE-24 #4 settled by reading the four App Services from Azure (LDE `NODE\|24-lts`, RBA `NODE\|22-lts`) | `supply-chain.md`, `dependency-scanning.md`, `controls.md`, `code-standards.md`, `branch-protection.md`, `coverage-floor.md`, `build-provenance.md`, `the-gitlab-mirror.md`, `index.md`, `ictu-dependency-guideline.md`, `ci-posture-deck.md`, `development-workflow/*`, `doc-architecture/*`; source defects to iou-architectuur#105 items 8–18 |
