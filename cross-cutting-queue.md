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

Eight items are pending: two carried over from the weekly pass of 27 September 2026, and six queued
by the RONL Business API component sync of 28 September. Everything queued on 24 and 26 September
was verified against source at `a7fe76f` / `0143ea2` / `3c44b9e` and drained (see the table below).

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

## Drained

| Pass | Entries drained | Where they landed |
|---|---|---|
| 20 September 2026 | — | The first weekly pass predates this queue: the cross-cutting re-check ran inside the RONL Business API sync to v2026.09.9, which is the run that split the two halves apart |
| 27 September 2026 | All of 24 September LDE (1–10) and RBA (1–15); all of 26 September CPSV (1–7), LDE (1–11) and RBA (1–10, 12). LDE-26 #11 (Windows `test:scripts`) is a tooling defect, filed as iou-architectuur#105 item 5 rather than documented; RBA-24 #11 (preview opt-in) is documented on the component's own `cicd.md` and `backend-development.md`, and no contributing page contradicts it; LDE-24 #4 settled by reading the four App Services from Azure (LDE `NODE\|24-lts`, RBA `NODE\|22-lts`) | `supply-chain.md`, `dependency-scanning.md`, `controls.md`, `code-standards.md`, `branch-protection.md`, `coverage-floor.md`, `build-provenance.md`, `the-gitlab-mirror.md`, `index.md`, `ictu-dependency-guideline.md`, `ci-posture-deck.md`, `development-workflow/*`, `doc-architecture/*`; source defects to iou-architectuur#105 items 8–18 |
