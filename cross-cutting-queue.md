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


### 24 September 2026 — RONL Business API v2026.09.9 → v2026.09.11

Read at `origin/main` = `86af73e` (v2026.09.11, promoted 23 September). `origin/acc` is
two commits further on with no version bump. Every fact below was checked against source
at that commit — the workflow YAML, `scripts/promotion-targets.sh`, `SECURITY-PIPELINE.md`,
`config.ts`, and the GitHub Actions and rulesets APIs — not against the prose it bears on,
and not against the changelog's own wording.

Twenty-eight commits across the two releases. Twenty-five have no component surface at
all: this is a CI, deployment and supply-chain release, so the cross-cutting half is the
larger one.

1. **Production deployment is promotion-driven. A push to `main` no longer deploys
   anything directly.**
   Evidence: `promote-to-production.yml` at `86af73e` — `on: push: branches: [main]` with
   **no `paths:` filter, deliberately** (*"a trigger filter would mean the decision is made
   by not running at all"*), plus `workflow_dispatch` with `dry_run` defaulting to true.
   Five jobs: `changes` → `backend` → `frontend` / `pa-demo` / `public-site` in parallel.
   The four `azure-*-prod.yml` files now carry `workflow_call:` + `workflow_dispatch:` and
   **no `push:`** — verified file by file.
   The sites run on `contains(fromJSON('["success","skipped"]'), needs.backend.result)`: a
   skipped backend and a successful one both mean production serves what they expect,
   while `cancelled` or `failure` means nobody knows. Every job also carries
   `needs.changes.result != 'success' || needs.changes.outputs.<t> == 'true'` with
   `!cancelled()`, so a failed range lookup deploys everything rather than granting a free
   pass.
   **This is invisible in an Actions listing.** Reusable-workflow calls are jobs inside the
   caller's run, so `86af73e` shows only Semgrep, Supply-chain audit and *Promote to
   Production #2*. Run `35891822589` holds all four deploys, every one concluded `success`.
   Bears on: `development-workflow/overview.md` (how a release lands — the pipeline's shape
   changed), `branch-protection.md`, `controls.md`.

2. **`controls.md`'s stated premise for "no `main` requires a build check" is now wrong for
   this repository, though its conclusion holds.**
   Evidence: `controls.md:73–76` reads *"The production deploy workflows kept their
   trigger-level path filters, and a required check that never reports…"*. The RONL
   Business API's four have **no trigger-level path filters at all** any more — the filters
   moved into `scripts/promotion-targets.sh`. The conclusion (`main` requires `audit` alone)
   is still right, for the older reason that none of the four ever had a `pull_request`
   trigger. Correct the premise; do not disturb the conclusion.
   Bears on: `controls.md`.

3. **A control gap the source names itself: if the promotion workflow breaks, nothing
   deploys, silently.**
   Evidence, quoted from `promote-to-production.yml`'s header: *"CONSEQUENCE WORTH KNOWING:
   the four deploy workflows no longer trigger on a push to main. If THIS workflow breaks,
   nothing deploys — silently, because `main`'s ruleset requires only `audit` and these are
   not required checks. The escape hatch is that all four keep `workflow_dispatch`."*
   Confirmed against the ruleset: `main promotion gate` requires `audit` only
   (`gh api repos/sgort/ronl-business-api/rulesets/23019967`).
   Worth recording as a named residual risk rather than being discovered. Bears on:
   `controls.md`, `branch-protection.md`.

4. **`acc` is deliberately unchanged, and the reason is a ruleset constraint worth
   documenting once.**
   Evidence: the same header — *"ACC IS NOT CHANGED HERE… its workflows also carry the
   `pull_request` trigger whose JOB NAMES the `acc supply-chain gate` ruleset requires by
   name."* A reusable workflow's check renames every required context, so converting the
   acceptance four would silently detach four required checks. Confirmed:
   `acc supply-chain gate` requires `audit`, `scan`, `build`, `Build and Deploy ACC
   Frontend`, `Build and Deploy ACC PA Demo`, `Build and Deploy ACC Public Site`.
   **Do not describe `acc` as promotion-driven.** Bears on: `branch-protection.md`,
   `code-standards.md`.

5. **The RONL Business API's CI now deploys its backend — this falsifies a sentence built
   around it being the one that does not.**
   Evidence: `e3c7dd6`. `azure-backend-prod.yml` ends in `azure/login` (OIDC) →
   `az webapp deploy` → a liveness loop → a `build.sha` verification loop;
   `azure-backend-acc.yml` has the same four steps gated
   `if: github.event_name != 'pull_request'`.
   `code-standards.md:170–172` currently reads *"Unlike the other two, **the Linked Data
   Explorer's CI does deploy its backend** — the backend workflows end in
   `azure/webapps-deploy`, where RONL Business API's end in an uploaded artifact that a
   developer deploys by hand."* Also `code-standards.md:137`, the table row *"Builds and
   uploads a deployment artifact; it does not deploy"*.
   Note the mechanism differs from the Linked Data Explorer's and the difference is
   load-bearing: **SCM basic auth is disabled on both of these App Services**
   (`basicPublishingCredentialsPolicies/scm` `allow=false`, measured 2026-09-20), so a
   publish-profile deploy would be rejected. That also retires the v2026.08.34 conclusion
   these pages inherited, *"OIDC is not needed"*.
   Bears on: `code-standards.md`, `supply-chain.md`, `controls.md`.

6. **`supply-chain.md`'s backend rows and its two open issues.**
   Evidence: `supply-chain.md:116` — *"| Backend deployed by CI | n/a | **no** — script from
   a developer machine¹ | **yes** — `azure/webapps-deploy` |"*, and `supply-chain.md:639–641`
   — *"**The RONL Business API's backend is the one that did not move.** Its deploy scripts
   still install from a developer machine without the lockfile ([#34])."*
   Issues **#34 and #35 are both closed**. Upstream `SECURITY-PIPELINE.md` was rewritten in
   this gap and now says: *"The CI workflows' 'Prepare deployment package' step used to
   carry the same pattern; it now installs from the root lockfile in a staging copy,
   filtered to the backend workspace with production dependencies only"*, and — the part
   that must not be lost in the correction — ***"The scripts remain, and so does the
   exception — narrowed… The exception closes when they are retired, not when the workflow
   lands."***
   Also `controls.md:103`, which lists *"the RONL Business API's hand-deployed backend"*
   among what R2–R4 do not reach. That is now the break-glass path rather than the normal
   one.
   Bears on: `supply-chain.md`, `controls.md`, `ictu-dependency-guideline.md` (R2–R4).

7. **Counted claims: workflows, jobs and pinned references all moved.**
   Evidence, counted at `86af73e`: **11 workflow files, 22 jobs**, every `runs-on`
   `ubuntu-24.04`, zero `ubuntu-latest` (counted file by file; previously 10 and 17).
   Upstream `SECURITY-PIPELINE.md` now reads **"34 `uses:` references across 11 workflows,
   all 34 digest-pinned"**, verified on `acc` at `65850f9`, 22 September 2026, with a new
   row `azure/login (×2)` at `a641126d1b8aa4d1fa005f4f92df94a3a4c4c906` (v3.1.0, Renovate)
   and `actions/checkout` moving from ×10 to ×11.
   Pages that count this: `code-standards.md:131` (*"**ten** workflows"*),
   `supply-chain.md:110` (*"31 / 31"*), `supply-chain.md:683–684` (*"**31 `uses:`
   references across ten workflows**"*), `ci-posture-deck.md:204` (*"the RONL Business API
   31 of 31 across ten"* — a deck transcript, so decide whether to re-state or date it),
   and `ictu-dependency-guideline.md`'s job-count arithmetic.

8. **The production path filters live in a script now, and it is runnable.**
   Evidence: `scripts/promotion-targets.sh` at `86af73e`. Reads changed paths on stdin,
   writes `<target>=true|false` per target, appends to `GITHUB_OUTPUT` when set. `--all` is
   the fail-safe for the three cases that cannot produce a range: a `workflow_dispatch`
   (no `before`), a first or force push (all-zero `before`), and a `before` the clone cannot
   resolve. The diff is taken `--no-renames`, because with rename detection a file moved
   *out of* `packages/backend/` would not deploy the backend it left.
   Two design notes worth carrying: it is **a file rather than a `run:` block** so the
   decision can be run locally against a real commit range, and
   **`promote-to-production.yml` is in none of the four patterns** — each deploy workflow
   lists itself so a change to it is exercised by running it, but the promotion runs on
   every promotion already, so listing it would mean editing a comment in it redeployed all
   four sites.
   Bears on: `code-standards.md` (path filters and what each workflow runs),
   `development-workflow/overview.md`.

9. **Secrets in a called workflow: named, never inherited — and the publish-profile
   secrets are dead.**
   Evidence: `promote-to-production.yml` passes the backend **no secrets at all** (OIDC via
   `vars.AZURE_CLIENT_ID_PROD`, `vars.AZURE_TENANT_ID`, `vars.AZURE_SUBSCRIPTION_ID` —
   repository *variables*, which need no passing) and each site exactly its one Static Web
   Apps token. Its comment: *"`secrets: inherit` would have handed each site workflow the
   Keycloak VM's SSH key and the Semgrep token to deploy one static site."* Permissions are
   granted on the call because a called workflow cannot hold more than its caller.
   `AZURE_WEBAPP_PUBLISH_PROFILE_ACC` survives only inside a comment describing it as
   *"The unused … secret from 2026-03-01"*. A least-privilege example worth having on a
   cross-cutting page.
   Bears on: `supply-chain.md` (least privilege), `code-standards.md`.

10. **A supply-chain hazard documented upstream and on no page here: how a deploy
    credential reaches CI is not checked.**
    Evidence: the new `SECURITY-PIPELINE.md` section — piping an Azure token into
    `gh secret set` stores a trailing newline, *"120 bytes where the key is 119. Both halves
    are the documented way to do their job; the composition is what goes wrong. It cost the
    public site's first production deploy on 12 September 2026, and the failure named
    nothing."* A secret's value cannot be read back, so no check can confirm this after the
    fact and none is proposed; `scripts/set-secret.sh` (`3636ecd`) removes the trap at the
    point of use — stdin with a sentinel, whitespace stripped, empty refused, byte count
    reported, value never echoed, never an argument, never written to a file.
    Bears on: `supply-chain.md` (*"What the audit cannot see"*).

11. **Preview environments: opt-in, and able to reach the acceptance backend.**
    Evidence: `32ddf67` — a preview is created only when the pull request changed something
    other than a manifest **and** carries the `preview` label; `labeled` is in the trigger
    types. Both conditions gate the **deploy step, not the job**, because
    `build_and_deploy_job` is the only place three packages are linted, type-checked,
    tested and built on a pull request, and a skipped job reports success — gating the job
    would have passed the required check having tested nothing. The two decisions fail safe
    in opposite directions deliberately: the build filter errs towards building, the
    preview decision withholds.
    Evidence: `64d8f3f` — `CORS_ORIGIN` is matched by exact equality, so `origin` became a
    function matching on the app's **stable slug** (`CORS_PREVIEW_SLUGS`); a
    `*.azurestaticapps.net` pattern would have let any Azure Static Web App in the world
    make credentialed cross-origin requests to the tier. Never honoured in production,
    enforced in code, and keyed on the **deployment** environment rather than `NODE_ENV` —
    acceptance deliberately runs `NODE_ENV=production`.
    Evidence: `ae83054` — `scripts/check-previews.sh` reports previews that outlived their
    pull request. GitHub does not run `pull_request` workflows while a pull request has a
    merge conflict, closing included; eight previews leaked across three apps on
    12 September and were still standing on 20 September. It finds apps by `repositoryUrl`
    rather than by workflow filename, reads every subscription, proves the session with a
    real ARM call rather than `az account show` (which reads cached state and succeeds
    against a token that expired days ago), fails on a subscription it cannot read and on
    finding no apps at all, and **never deletes**.
    Bears on: `supply-chain.md`, `code-standards.md`, `controls.md`.

12. **The release process gained a test step.**
    Evidence: `2d1cf27`; the diff of `.claude/commands/bump-release.md` between `10bcf8b`
    and `86af73e` (+81 lines). Step 6 now runs root `npm test` — *"step 4 edited source
    files, and some tests read them… Lint and Prettier both read a `package.json` as data.
    A test can read it as input, and then a version bump is a behaviour change."* Step 7's
    report must now state format, lint and test clean with the suite's counts, *"because a
    step nothing reports on is a step that gets skipped."* The failure that forced it is
    named in the file: v2026.09.10 bumped `packages/pa-cockpit` for the first time while its
    own scaffold test still asserted `toBe('1.0.0')`, and the release was committed, pushed
    and opened as a pull request before anything said otherwise.
    Bears on: `development-workflow/overview.md` (how a release lands).

13. **`zizmor.yml`'s Node moved to `24.21.0`, and the cooldown produced its first measured
    confirmation.**
    Evidence: `417cd53`; `zizmor.yml` line 57 at `86af73e` reads `node-version: '24.21.0'`.
    Deliberately not shared with `.nvmrc`, which stays `22.23.2` and which the App Service
    plans match: `renovate@44.50.3` declares `engines.node ^24.11.0`, and npm accepts a
    mismatch with `EBADENGINE` rather than refusing — so before that pin the validator ran
    unsupported and green.
    On the cooldown: `d7f6231` moved 62 packages and **every version it introduced was at
    least 14 days old**, measured against the npm registry's own publish dates. Both commits
    make the same methodological point, which belongs on a cross-cutting page:
    ***the `renovate/stability-days` status is not evidence*** — it read *"Updates have not
    met minimum release age requirement"* on branches that were in fact compliant, because
    `lockFileMaintenance` is flagged rather than evaluated. Read the measurement.
    Bears on: `supply-chain.md`, `dependency-scanning.md`, `ictu-dependency-guideline.md`
    (R2–R4, and the `.nvmrc` / `zizmor` runtime rows — note this is the *opposite* movement
    to the Linked Data Explorer's `.nvmrc` bump recorded above, so the two entries must be
    reconciled rather than applied independently).

14. **A plugin was uninstalled.**
    Evidence: `da31955` removes the understand-anything plugin's leftovers —
    `.understandignore`, a tracked file predating the ignore rule, and 736K of generated
    artefacts — *"The plugin has been uninstalled locally, so nothing generates or reads
    these files any more."*
    **Do not write the page from this entry.** Re-derive from
    `~/.claude/plugins/installed_plugins.json` and `~/.claude/settings.json` →
    `enabledPlugins`, and re-count `grep -c '^## ' ~/.claude/CLAUDE.md` while there.
    Bears on: `development-workflow/working-with-claude-code.md`,
    `development-workflow/skills-and-boundaries.md`.

15. **Tooling, not documentation: `stamp-staleness.py` cannot recognise a promotion run.**
    Evidence: `.claude/skills/iou-document-patch/scripts/stamp-staleness.py` —
    `DEPLOY_WORKFLOW = re.compile(r"deploy|static web apps", re.IGNORECASE)`, matched
    against a run's **name**. *Promote to Production* matches neither. Two consequences,
    both live now that this component's `build` points at run `35891822589`: `check_build`
    emits the warning *"'Promote to Production' does not look like a deploy workflow"*
    (a warning, not a problem — the four hard checks on sha, run number, event and
    conclusion all pass, so the script still exits 0), and a future `verified:` stamp at a
    promoted commit will warn *"triggered no successful deploy run on GitHub"* although
    four deploys succeeded inside that run.
    Not a claim on any page. Raise it with the weekly pass as a change to the skill.


### 26 September 2026 — CPSV Editor v2026.09.6 → v2026.09.7

Read at `origin/acc` = `a7fe76f`; `origin/main` = `7d154ba` holds the same tree, **promoted**
(Deploy PROD run #102 green). The release is CI and supply-chain work almost entirely, so this
is its larger half. The same changes landed in the Linked Data Explorer (v2026.09.8) and the
RONL Business API (v2026.09.12) the same week, all citing `sgort/linked-data-explorer#119` —
their entries below repeat the shared facts per repository; merge them per page, not per entry.

1. **A release SBOM exists.**
   Evidence: `5b83e8d`. `scripts/write-sbom.mjs` (`npm run sbom`, a bump-release step) writes
   `docs/sbom/ttl-editor-<version>.cdx.json` — CycloneDX, production dependencies only, from the
   lockfile. `docs/sbom/` holds `2026.09.6` (backfilled) and `2026.09.7`. `sbom.yml`, job
   `release-sbom`, runs on push to `main`, dispatch, and tooling pull requests; modes write,
   `--check`, `--verify-release`.
   Bears on: `ictu-dependency-guideline.md` (R10 SBOM row, CPSV ⬜; the sentence that SBOMs are
   pipeline work nobody has started), `dependency-scanning.md` ("No release carries an SBOM"),
   and the weekly score.

2. **Dependencies are audited daily on `acc` and `main`.**
   Evidence: `417a510`, `7e5ef52`, `d1a2639`. `dependency-audit.yml`, cron `17 5 * * *` plus
   dispatch, `npm audit --package-lock-only` per branch, fails on a high or critical production
   advisory, one tracking issue. `scripts/audit-tree.mjs` groups by advisory; exit 2 = could not
   run = finding. The script is copied to `$RUNNER_TEMP` because the branch checkouts remove it.
   Bears on: `ictu-dependency-guideline.md` (R10 daily-audit row, and the claim that no workflow
   in any of the three has a `schedule:` trigger), `dependency-scanning.md` (same claim). For the
   pass to decide: whether "scan what production runs, not only `acc`" is now partly met, since
   the audit reads `main`'s lockfile.

3. **A job may not share a required check's name.**
   Evidence: `d1a2639` — the daily job was first named `audit`, the name of zizmor's required
   job; required checks match by name, and the collision blocked `ronl-business-api#206`. It is
   now `dependency-audit`; `sbom.yml` names `release-sbom` for the same reason.
   Bears on: `branch-protection.md` (how required checks match).

4. **The audit job checks lockfile sync before installing.**
   Evidence: `d37875d`, `35c3712`. `zizmor.yml` step "Lockfile matches package.json" =
   `npm ci --dry-run --ignore-scripts`; `--ignore-scripts` because a dry run still runs
   `postinstall`, which failed on a clean checkout. Stated limit: it checks the pull request's own
   merge commit — dependency pull requests merge one at a time, each rebased onto `acc`.
   Bears on: `supply-chain.md` and `code-standards.md` (what the `audit` job contains).

5. **Renovate: no `X.0.0`, and ubuntu 26.04 deferred on record.**
   Evidence: `9cda617` (`allowedVersions: "!/^\\d+\\.0\\.0$/"`, `matchManagers: ["npm"]`),
   `e2b3396` (a disabled rule for the runner's `ubuntu` major with its reason and exit condition;
   the other queued majors deliberately stay behind Dependency Dashboard approval).
   Bears on: `ictu-dependency-guideline.md` (R7 — wait for the first patch; the deferral record),
   `supply-chain.md` (runner-pin section).

6. **The ACC build check is required, via a `changes` job.**
   Evidence: `1ab793e`, `e69db67`. `orange-beach.yml` drops the `pull_request` path filter and
   decides relevance in a `changes` job; `gh api repos/sgort/ttl-editor/rulesets/21728745` requires
   `audit`, `scan`, `Build and deploy ACC`. `main` still requires nothing (#131). The PROD workflow
   keeps its `paths-ignore`.
   Bears on: `branch-protection.md`, `controls.md`. (Pages written ahead of this sync may already
   say so — verify rather than re-add.)

7. **Counts moved.** 7 workflow files, 9 jobs, all `ubuntu-24.04`, none `ubuntu-latest`.
   Evidence: `git grep -c runs-on origin/acc -- .github/workflows`.
   Bears on: `ictu-dependency-guideline.md` ("All 39 jobs — 7, 15 and 17"), `supply-chain.md`
   (the runner-pin count), `code-standards.md`.

Checked and already right on the contributing pages, no entry needed: `.nvmrc` 24.20.0 and
`skip_app_build` on both deploy steps; "Node 24.20.0 bundles npm 11.19"; the `acc` ruleset's
three checks on `branch-protection.md`. Queue item 10 of the Linked Data Explorer entry above
(`.nvmrc` missing from the deploy filters) does **not** apply here: this repository filters with a
`paths-ignore` denylist, so a pull request changing only `.nvmrc` builds.

### 26 September 2026 — Linked Data Explorer v2026.09.6 → v2026.09.8

Read at `origin/acc` = `0143ea2`; `origin/main` = `4148c9a` holds the same tree, **promoted**
(Promote to Production run 36255107973: backend and frontend deployed, ropa-site skipped). The
SBOM, daily-audit, lockfile-sync and Renovate facts repeat the CPSV Editor entry above for this
repository.

1. **Production is promotion-driven here too.**
   Evidence: `09c475a`. `promote-to-production.yml` is the only workflow a push to `main` starts that deploys anything (`semgrep`, `zizmor` and `sbom` also run on that push — and the LDE's own `SECURITY-PIPELINE.md` repeats the overstated wording);
   it calls the three production deploys as reusable workflows (backend first, then both sites,
   each gated on the backend result being `success` or `skipped`). Path rules live in
   `scripts/promotion-targets.mjs`, whose test the `changes` job runs first, with a drift guard
   against the sites' `pull_request` paths. Unlike the RONL Business API, the two site workflows
   **keep** a `pull_request` preview trigger on `main`, as a recorded decision (`e14a79a`); the
   backend is excluded. `build.run` in `repo-versions.json` is now the promotion run's number (#2).
   Bears on: `development-workflow/overview.md`, `branch-protection.md`, `controls.md`,
   `build-provenance.md`. The `stamp-staleness.py` limitation queued as RBA item 15 now applies
   to this component as well.

2. **The production reviewer is gone.**
   Evidence: `azure-backend-production.yml` comment (removed 24 September 2026, #210);
   `gh api repos/sgort/linked-data-explorer/environments/production` → protection rules
   `branch_policy` only.
   Falsifies: `coverage-floor.md` (the passage saying `production` has required reviewers and
   that tests would wait on a human approval — that page's stated reason for an exclusion; the
   source keeps the conclusion for a different reason, that `main` is promoted from `acc`).
   Bears on: `controls.md`, `branch-protection.md`.

3. **Rulesets, as read on 26 September 2026.**
   `acc supply-chain gate`: pull request plus `audit`, `scan`, `deploy`, `Build and Deploy
   Frontend`, `Build and Deploy ROPA Site`. `main promotion gate`: pull request (0 approvals) plus
   `audit`, `scan`. The production job renames (`a66ca3f` — "Build and Deploy Production
   Frontend" / "… ROPA Site") change no ruleset; they make requiring those jobs possible.
   Bears on: `branch-protection.md`, `controls.md`.

4. **SBOM per release** (`e2cb5cc`): `docs/sbom/linked-data-explorer-2026.09.{7,8}.cdx.json`,
   `sbom.yml` on push to `main` with `--verify-release`.
   Falsifies: `ictu-dependency-guideline.md` (R10 SBOM row, LDE ⬜; "SBOMs are pipeline work
   nobody has started"), `dependency-scanning.md` ("No release carries an SBOM").

5. **Daily dependency audit on `acc` and `main`** (`e02f8d5`, `18eae21`, `bd88c6e`). On
   24 September this repository's 28 moderate entries were three advisories, 24 of them
   `@tiptap/core` — the example `audit-tree.mjs`'s grouping exists for.
   Falsifies: `ictu-dependency-guideline.md` (R10 daily-audit row, LDE ⬜; possibly "scan what
   production runs"); bears on `dependency-scanning.md`, `controls.md`.

6. **Lockfile-sync step** (`d9200ba`, `bf62026`) in `zizmor.yml`, as in the CPSV entry.
   Bears on: `supply-chain.md`, `development-workflow/overview.md`.

7. **Renovate R7** (`bd79d04`, `faae5f8`): npm `allowedVersions` excludes `X.0.0`; ubuntu 26.04
   deferred by a rule with its reason. Falsifies `ictu-dependency-guideline.md` R7 LDE ⬜.

8. **Counts at `0143ea2`:** 11 workflow files, 21 jobs, 34 `uses:` lines of which 3 are local
   reusable-workflow calls (31 action references). Re-derive against `SECURITY-PIPELINE.md`
   before writing. Bears on: `code-standards.md`, `supply-chain.md`.

9. **Evidence for the open LDE item 4 (App Service runtime) — do not resolve it from this.**
   Both sides now sit in the same tree: `docs/ci-posture-across-repos.md` says Node 24 on both
   tiers in one place and all four App Services on `NODE|22-lts` in another;
   `azure-backend-production.yml` says "matches the App Service runtime, NODE|22-lts" near
   line 79 and "switched to NODE|24-lts" near lines 368–369.

10. **The zizmor register drift is systemic** (`c515682`, `07ef51e`): Renovate rewrites a
    workflow pin and its comment but never `SECURITY-PIPELINE.md`, so every action-bump pull
    request fails the register half of `audit` until the row is edited on the bump branch.
    Bears on: `supply-chain.md`.

11. **The script harness runs in CI now, and fails on Windows.** `npm run test:scripts` exists
    (`node scripts/promotion-targets.test.mjs && node scripts/dso-dossier.test.mjs`);
    `promotion-targets.test.mjs` runs in the promotion's `changes` job ("PASS: 24 checks" in run
    36255107973). On a Windows workstation it fails — it resolves its script with
    `new URL(...).pathname`, which yields `/C:/…` — and the `&&` then skips `dso-dossier`
    (24 checks, passing on its own). Measured 26 September 2026.
    Bears on: `code-standards.md` and the weekly `tests:` rows (what counts as a suite in CI).

### 26 September 2026 — RONL Business API v2026.09.11 → v2026.09.12

Read at `origin/main` = `2443adc`, **promoted** (Promote to Production run #3: backend, frontend,
public-site and pa-demo all deployed). `origin/acc` = `3c44b9e` is two commits ahead, touching only
`scripts/check-previews.sh` (item 11). The SBOM, daily-audit, lockfile-sync and Renovate facts
repeat the CPSV Editor and Linked Data Explorer entries above for this repository.

1. **`openapi-rendering.md` describes one component; a second now publishes.**
   Evidence: `3c8d0b3`, `openapi.routes.ts` (wildcard CORS on the document), and live reads of
   `acc.api.open-regels.nl` on 26 September 2026. What that page states as general is
   LDE-specific: RBA's document **carries its own version** (`info.version`, injected from
   `package.json` by `scripts/build-openapi.cjs`); RBA **declares `securitySchemes`**
   (`bearerAuth`, `mediaAggregatorKey`); RBA's `/v1/health` is wrapped (`{ success, data }`) with
   `build { sha, run, runId }` and no `label`; RBA acceptance echoes only
   `https://iou-architectuur.open-regels.nl` on `/v1/health` — not `acc.iou-architectuur…`, not
   `localhost` — so its provenance banner **and Scalar's Test Request** work only on the production docs tier (a preflight from the acceptance docs origin gets no `Access-Control-Allow-Origin`; adding `https://acc.iou-architectuur.open-regels.nl` to the RBA acceptance App Service's `CORS_ORIGIN` would change that); and CSP
   `connect-src` now names a second host (`https://acc.api.open-regels.nl`, added in this sync).
   Bears on: `contributing/doc-architecture/openapi-rendering.md`.

2. **SBOM per release** (`c43de59`): `docs/sbom/` holds 2026.09.11 and 2026.09.12; `sbom.yml` on
   push to `main` with `--verify-release`. Falsifies the RBA cells of the R10 SBOM row and
   `dependency-scanning.md` ("No release carries an SBOM").

3. **Daily dependency audit** (`34a5a57`, `9ded0aa`, `dfb6ace`). This is the repository whose
   `#206` the job-name collision blocked; Node is pinned as a literal `24.20.0` in the job because
   it audits two branches that need not share an `.nvmrc`. Bears on: `dependency-scanning.md`,
   `branch-protection.md`, `ictu-dependency-guideline.md`.

4. **The lockfile incident this week's checks came from** (`05d76bd`, `b2e9bf1`, `c81098b`).
   Three dependency pull requests (#221–#223) merged back to back without rebasing, each green
   against its own base, left `acc` with a lockfile matching no `package.json`; `npm ci` failed
   with `EUSAGE`. The ruleset does not require a branch to be up to date. Bears on:
   `supply-chain.md`, `branch-protection.md`, `code-standards.md`.

5. **Renovate R7, and a Node deferral the other two repositories do not have** (`617d105`,
   `0a75676`). Ubuntu 26.04 **and Node 24** are disabled rules with reasons and exit conditions:
   both App Services run `NODE|22-lts` against an `.nvmrc` of 22.23.2, and taking 24 in `.nvmrc`
   alone would build for a major the host does not run. **Reconcile with LDE item 4 and the LDE
   `.nvmrc` 24.21.0 movement** rather than applying either alone. Bears on:
   `ictu-dependency-guideline.md` (R7), `supply-chain.md`.

6. **`keycloak-connect` removed** (`bae66c9`): production tree −48 packages, including
   `chromedriver` via an optionalDependency on `latest`, `adm-zip`, `elliptic`, `proxy-agent`;
   three Dependabot alerts can no longer arrive by that route. Bears on: `supply-chain.md`,
   `dependency-scanning.md` (alert counts).

7. **Pinning scope** (`08a988a`): local compose images pinned by digest via `docker:pinDigests`;
   `deployment/vm/` compose deliberately unpinned (#196); the App Service runtime cannot be pinned
   below the major (`az webapp list-runtimes`: `NODE|22-lts`, `NODE|24-lts`, `NODE|26`). Bears on:
   `supply-chain.md` (pinning table).

8. **Counts moved:** 13 workflow files on `main` (was 11). Re-count jobs and `uses:` against
   `SECURITY-PIPELINE.md` before writing. Bears on: `code-standards.md`, `supply-chain.md`,
   `ci-posture-deck.md`.

9. **Semgrep triage method** (`cbbb57c`): a verification scan whose ruleset lacked the rules
   reported 0 on the old tree too; re-run with the five exact rule ids, 14 → 0. The lesson —
   a zero is evidence only if the same scan finds the findings before the fix — belongs with the
   scanning methodology. Bears on: `dependency-scanning.md`, `code-standards.md`.

10. **The LDE production reviewer's removal is recorded in this repository too** (`7ed9ba7`):
    both repositories now exclude `pull_request` from production workflows for the promotion
    argument alone. Bears on the same pages as LDE item 2.

11. **Acc-only, not promoted:** `check-previews.sh` strips the carriage returns `az` writes on
    Windows (`80e34a2`, merged `3c44b9e`). Document after promotion, wherever `check-previews` is
    described.

12. **Test posture for the weekly `tests:` rows:** backend test files 89 → 96; new scripts
    `test:contract` and `test:openapi-coverage`; the OpenAPI coverage gate's pending ceiling is 18.
    Use the figures measured in this sync (RBA testing pages), not these counts.

## Drained

| Pass | Entries drained | Where they landed |
|---|---|---|
| 20 September 2026 | — | The first weekly pass predates this queue: the cross-cutting re-check ran inside the RONL Business API sync to v2026.09.9, which is the run that split the two halves apart |
