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

!!! note "Correcting this file's own record"
    Until 24 September 2026 this section read *"Nothing queued … and no component has been
    synced since."* That was already untrue when written: the RONL Business API sync to
    **v2026.09.9** landed at `2c85691` on this branch, and the CPSV Editor sync to
    **v2026.09.6** at `948d860` before it. Neither left an entry here — the first because it
    *was* the run that split the two halves apart and carried its cross-cutting work inline,
    the second because this file did not yet exist. Both are accounted for; neither is
    outstanding. The sentence is replaced rather than amended, because a queue that misreports
    its own emptiness is the failure this file was created to prevent.

### 24 September 2026 — Linked Data Explorer v2026.09.5 → v2026.09.6

Read at `origin/acc` = `9c58737` (v2026.09.6, released 23 September, 54 commits).
**Not on `main`** — `origin/main` is still `ec4792f` = v2026.09.5, so the docs record
this release as `environment: acc`, to be re-stamped after promotion. Every fact below
was checked against source at that commit, not against the prose it bears on.

The CI half of this release is the largest cross-cutting yield since the 20 September
pass. Eleven of its commits are typed `ci` or `chore`.

1. **`.nvmrc` is now `24.21.0`, and four contributing sentences still say `22.23.2`.**
   Evidence: `git show origin/acc:.nvmrc` → `24.21.0`. History: `8a85abd` (19 Sep)
   created the file at `22.23.2`; `20c86d8` (23 Sep) bumped it. **The 20 September pass
   read `22.23.2` correctly** — the value went stale three days later, which is exactly
   the case this queue exists for.
   Bears on: `ictu-dependency-guideline.md` — *"`.nvmrc` carries `24.20.0` in the CPSV
   Editor and `22.23.2` in the other two"* and the deploy-comparison row *"Linked Data
   Explorer — frontend … the runner's build, Node 22.23.2"*; `supply-chain.md` — the
   `.nvmrc` table row *"| **Linked Data Explorer** | **`22.23.2`** | all six deploy
   workflows | the same |"* and the cooldown-coverage row *"**Node 22.23.2 bundles npm
   10.9.8** | So the **Linked Data Explorer and the RONL Business API are not covered by
   their own setting**"*. That last row now needs splitting: on `.nvmrc` 24.21.0 the
   Linked Data Explorer **is** covered; the RONL Business API presumably still is not,
   which is a fact to re-read at its own head rather than infer from here.
   Secondary, same evidence: the per-workflow literals are gone. `origin/main` carried
   `node-version: '22.23.2'` in both backend workflows and `"20.20.2"` in both frontend
   ones; at `acc` all four read `node-version-file: .nvmrc`. `zizmor.yml` keeps its own
   `24.20.0` literal, so the "one deliberate exception in each" paragraph still holds.

2. **`engines.node` moved `>=20.20.2` → `>=22.23.2` while `.nvmrc` says `24.21.0`.**
   Evidence: `git diff origin/main origin/acc -- package.json packages/backend/package.json`.
   The declared floor now sits a major below the pin. `supply-chain.md` already makes
   exactly this argument about the RONL Business API (*"a floor of `>=20.13.0` permits
   precisely the mismatch being removed"*); the same shape is now present in the Linked
   Data Explorer and is not recorded anywhere.

3. **A deployed-app native-binding smoke test now gates both backend workflows.**
   Evidence: `5115cd1`; the step and its rationale are in
   `.github/workflows/azure-backend-acc.yml` (after the `/v1/dmns` check) and
   `azure-backend-production.yml`. Both POST a minimal DMN to `/v1/dmns/validate`
   **on the deployed app** and fail only on the native-load signature — a message naming
   `NODE_MODULE_VERSION` or *"was compiled against"* — never on a DMN that is merely
   invalid.
   Why it exists, in the workflow's own words: on 23 September the `.nvmrc` move to
   24.21.0 plus a switch to `NODE|24-lts` left a Node-22 `xmljs.node` on a Node-24 host.
   *"The deploy went fully green — health 200, `build.sha` equal to the merge commit,
   every shape layer loaded, `/v1/dmns` answering — and DMN validation was broken for
   every user"*, returning `NODE_MODULE_VERSION 127. This version of Node.js requires 137`.
   The pre-existing `require('libxmljs2')` assertion **cannot** see this: it runs on the
   runner, so it proves the binary matches the Node that built it, which is the one axis
   a runner-versus-host mismatch is invisible on. `build.sha` is not at fault either — it
   answers which commit's *JavaScript* is running, and that answer was correct.
   Bears on: `code-standards.md` (what each workflow's CI steps actually are),
   `supply-chain.md` (what a green deploy does and does not prove — the `build.sha`
   discussion in particular).

4. **The App Service runtime decision: majors only, so the control is the ordering.**
   Evidence: `docs/ci-posture-across-repos.md` on `acc`, the section beginning *"The App
   Service runtime cannot be pinned, and that is now a decision rather than an open
   question."* `az webapp list-runtimes --os linux` returns, for Node, exactly
   `NODE|22-lts`, `NODE|24-lts` and `NODE|26` — major-level only, no exact version, no
   digest, no setting that takes one. What remains reachable is keeping the App Service's
   major in step with `.nvmrc`'s, and **the ordering is part of the pin**: switch the App
   Service first, then merge the `.nvmrc` bump. No pull-request check runs against an App
   Service, so nothing enforces it.
   **The Linked Data Explorer is the named exception.** `switch first, then merge` is
   complete only for a pure-JavaScript backend; `libxmljs2` builds against NAN rather than
   N-API, so between switching the runtime and deploying an artifact rebuilt on the new
   major the binary does not match the host and the backend will not start — and the same
   is true in reverse if the merge comes first. The RONL Business API is unaffected: thirty
   runtime dependencies, none native.
   Bears on: `supply-chain.md`, which currently lists this under *"Two things still float"*
   as *"Whether the platform allows an exact pin is not yet established."* That is now
   **established and answered**, and the item should move from "floating" to "decided, with
   an ordering control that nothing enforces". Also `ictu-dependency-guideline.md` (R2).

   ⚠️ **Open question for the pass to settle — do not resolve it from this entry.** Two
   statements written on the same day disagree about the current runtime. The backend
   workflow comment (`5115cd1`, 23 Sep) says *"the App Service was switched to
   `NODE|24-lts`"*. `ci-posture-across-repos.md`, also 23 Sep, says *"All four App
   Services across both repositories run `NODE|22-lts`"*. They read as before-and-after
   within one day, but that is an inference. **Confirm the live runtime with
   `az webapp config show` (or the portal) for each of the four App Services before
   writing either value onto a page.**

5. **The backend deploy installs from the lockfile — verify the page already says so.**
   Evidence: `fb97d16`. Both backend workflows now run
   `npm ci --omit=dev --workspace=@linked-data-explorer/backend` in a staging copy holding
   the root manifest and lockfile plus the backend's manifest, then copy that
   `node_modules` into `deploy/` — measured at 349 packages, each at the root lockfile's
   version and integrity hash. Previously they assembled `deploy/` with `package.json` and
   no lockfile and ran `npm install --production` there, re-resolving every caret range at
   deploy time. `a646f61` and `398aea8` then corrected the un-hoisted-dependency guard: it
   had failed whenever `packages/backend/node_modules` merely *existed*, and its
   explanatory comment claimed the directory holds hidden npm bookkeeping — the run that
   passed logged its contents and it was empty.
   Bears on: `supply-chain.md`, which already records this as closed. **Re-read rather
   than assume, and confirm the RONL Business API half is still the open one.**

6. **`.npmrc`'s own comment now contradicts `.nvmrc` at the same head.**
   Evidence: `git show origin/acc:.npmrc` reads *"npm older than 11.10 ignores it without
   a warning. **Node 22.23.2, which `.nvmrc` names**, bundles npm 10.9.8"* — while
   `.nvmrc` at that same commit says `24.21.0`. A source-level contradiction, and it is the
   same sentence `supply-chain.md`'s cooldown-coverage table mirrors. Read the file, not
   the table.

7. **`scripts/check-deps.sh` gained the npm-version warning in this release — the page is
   right, record it as verified.** Evidence: `3f9e42f` adds a second check that warns
   (never fails) when `npm --version` is below 11.10, naming `npm install -g npm@11`, and
   rewords the stale-install message to say the `.npmrc` cooldown holds `npm install` back
   14 days on npm 11.10 or newer. `supply-chain.md` already claims this exists *"in all
   three"*; true at the `acc` heads. **Verified, no change needed** — recorded so the pass
   does not re-derive it.

8. **Runner-image and job-count claims re-counted and found correct.**
   Evidence: `git grep -c "runs-on:" origin/acc -- .github/workflows` → **15 jobs across 8
   workflow files, all `ubuntu-24.04`, zero `ubuntu-latest`** (`52e94f1`).
   `ictu-dependency-guideline.md`'s *"All 39 jobs — 7, 15 and 17"* and `supply-chain.md`'s
   *"7, 15 and 17 jobs respectively"* both still hold for this component. **Verified, no
   change needed.**
   ⚠️ One caveat worth carrying: the GitHub API lists a **ninth** workflow for this
   repository, `azure-static-web-apps-delightful-cliff-04b2d4e03.yml`, which does **not**
   exist in the tree at `acc`. A tree-based count says 8 workflow files, an API-based count
   says 9. Any contributing sentence that counts this repository's workflows should say
   which it counted.

9. **Required build checks on `acc`, via a `changes` job.**
   Evidence: `a31dfac` and `e188dde`. Each ACC deploy workflow drops the path filter from
   its `pull_request` trigger and gains a `changes` job that asks the GitHub API for the
   pull request's files — under both names for a rename — and matches them against one
   pattern mirroring the push filter. A required check must report on every pull request,
   and a workflow its trigger filters out never starts and reports nothing; a job skipped
   by its own `if:` reports success instead. The build and close jobs also run when
   `changes` did **not** succeed, so a failed lookup means a full build rather than a free
   pass. The two jobs both named *Build and Deploy Job* became **Build and Deploy Frontend**
   and **Build and Deploy ROPA Site**, because required checks are matched by job name —
   and `SECURITY-PIPELINE.md` now records that renaming one means updating the ruleset in
   the same change.
   Bears on: `code-standards.md` (CI section, job names), `supply-chain.md` (which checks
   gate `acc` and `main`). **Verify the ruleset against `gh api repos/.../rulesets`, not
   from this entry.**

10. **`.nvmrc` is in every deploy filter — and the consequence that is on no page.**
    Evidence: `2cda481`. `.nvmrc` sets the Node version every deploy workflow builds, tests
    and ships on, and no path filter included it, so a Node bump *built nothing, tested
    nothing and deployed nothing* — the new Node reached the next unrelated deploy
    untested. `supply-chain.md` and `doc-architecture/technology-stack.md` already state
    the filter rule. What neither says is the sharper half, which the commit records:
    **once the build checks became required on `acc`, such a pull request also showed every
    required build check skipped and was therefore mergeable.** Found on `#80`, which
    changes `.nvmrc` alone.


## Drained

| Pass | Entries drained | Where they landed |
|---|---|---|
| 20 September 2026 | — | The first weekly pass predates this queue: the cross-cutting re-check ran inside the RONL Business API sync to v2026.09.9, which is the run that split the two halves apart |
