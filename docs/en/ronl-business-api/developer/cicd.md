---
component: RONL Business API
---

# CI/CD

RONL Business API runs **ten GitHub Actions workflows**: an
acceptance/production pair for each of four packages, plus two scanning
workflows — the supply-chain `audit` gate and a Semgrep `scan`. Every one of
the **seventeen jobs** across them names `ubuntu-24.04`, never `ubuntu-latest`:
that label is one GitHub moves to a new Ubuntu release on its own schedule, so
pinning it means a change of OS release arrives as a diff here rather than
silently. The label pins the *release*, not the image — GitHub rebuilds the
image about weekly, and a hosted runner cannot pin it by digest.

!!! info "`acc` and `main` carry the same ten workflows"
    Verified against `main` at `10bcf8b` on 20 September 2026 (v2026.09.9);
    `acc` at `6ca80f2` has a byte-identical tree. `main` was once four workflows behind
    and carried none of the pinning or gating described below — closing that gap
    was a CI-alignment programme that finished in v2026.09.7, and `main` now has
    its own `main promotion gate` ruleset. Where the two branches still differ,
    this page says so.

---

## Workflow overview

| File | Trigger | Target | Deploys? |
|---|---|---|---|
| `zizmor.yml` | PR, push to `acc`/`main` | — | No — the `audit` gate |
| `semgrep.yml` | PR, push to `acc`/`main` | — | No — the `scan` job |
| `azure-backend-acc.yml` | push + PR to `acc` | — | **No** — builds and uploads an artifact |
| `azure-backend-prod.yml` | push to `main` | — | **No** — builds and uploads an artifact |
| `azure-frontend-acc.yml` | push + PR to `acc` | `acc.mijn.open-regels.nl` | Yes |
| `azure-frontend-prod.yml` | push to `main` | `mijn.open-regels.nl` | Yes |
| `azure-publicsite-acc.yml` | push + PR to `acc` | `acc.publiek.open-regels.nl` | Yes |
| `azure-publicsite-prod.yml` | push to `main` | `publiek.open-regels.nl` | Yes |
| `azure-pa-demo-acc.yml` | push + PR to `acc` | `acc.plato.open-regels.nl` | Yes |
| `azure-pa-demo-prod.yml` | push to `main` | `plato.open-regels.nl` | Yes |

All eight Azure workflows also support `workflow_dispatch`. Neither scanning
workflow does — both are meant to run from the events themselves and nothing
else.

!!! warning "The backend is not deployed by CI"
    `azure-backend-acc.yml` and `azure-backend-prod.yml` end at *Create
    deployment zip* → *Upload deployment artifact*. **Neither contains a deploy
    step**, and nothing consumes the artifact. The backend reaches acceptance
    and production through `deploy-backend-to-{acc,prod}.sh`, run from a
    developer machine — a workflow-based App Service deploy could not be made to
    work.

    Two consequences follow. There is no post-deployment health check in CI, and
    the [supply-chain gate](../../contributing/supply-chain.md) does not see the backend's
    path to production at all.

    **The cause is not what it was assumed to be.** The standing theory was that
    `azure/webapps-deploy` authenticates over SCM basic auth, which Azure now
    disables by default, and that the way forward was OIDC — an app registration
    with a federated credential. Tested against a real failed run in
    v2026.08.34, that was **disproved: OIDC is not needed**, and the blocker
    remains open rather than diagnosed. The plausible explanation was recorded as
    a hypothesis and has now been retired rather than carried forward as if it
    were established.

    Both deploy scripts now run on any platform: the portable path falls back to
    the bsdtar bundled at `System32\tar.exe`, because Info-ZIP's `zip` cannot be
    installed on a managed Windows laptop. They also fail fast on a dead Azure
    session rather than part-way through.

---

## The two scanning workflows

Neither deploys anything, and neither carries a `paths:` filter: both must reach
every pull request regardless of what it touched.

### `audit` — the required check

`zizmor.yml` has one job, and it runs **eight steps, all of them blocking**:

| # | Step | What it does |
|---|---|---|
| 1 | Checkout | `persist-credentials: false` |
| 2 | Set up Node `24.20.0` | For the config validator only — see [Node runtime](#node-runtime) |
| 3 | Run zizmor | Workflow static analysis, with zizmor itself pinned to `1.29.0` — maintained by Renovate, which maps the action to the image `ghcr.io/zizmorcore/zizmor`, not bumped by hand |
| 4 | Validate `renovate.json` | `renovate-config-validator --strict` |
| 5 | `npm ci` | So the three steps below run *this* repository's tooling rather than a version named in the workflow |
| 6 | `npm run check-format` | Prettier, via the root script the pre-push hook also runs |
| 7 | `npm run check-shared` | [`@ronl/shared` holds declarations, not logic](shared-package.md#kept-declarations-only) |
| 8 | `npm run check-supply-chain` | Every digest resolved against the GitHub API, and the register in `SECURITY-PIPELINE.md` compared against the workflows |

Steps 4 through 8 carry `if: always()`. That makes them run *after* an earlier
failure, so one run reports on every half of the policy instead of stopping at
the first — it does **not** make them non-blocking. The job still fails.

The thing that would make a step non-blocking is `continue-on-error`, and it is
the wrong tool here: it rewrites the *step's* reported conclusion as well as the
job's, and the honest outcome is not exposed by the REST API at all, so a
finding appears only in the log while every check reads *success*.
`check-supply-chain` ran that way from its adoption until v2026.09.7 promoted it
to blocking.

Step 6 is in this job rather than in a deploy workflow for the same reason step 7
is: `audit` has no paths filter and is the required check, so a
documentation-only pull request reaches it too.

### `scan` — Semgrep, required on `acc`

`semgrep.yml` runs Semgrep Code and Supply Chain across the whole monorepo in a
single job. All six workspaces resolve through the one root `package-lock.json`,
so there is a single lockfile to read and no per-workspace fan-out to keep in
step with the workspace list.

It covers what `check-supply-chain` structurally cannot: that step verifies
GitHub Actions digest pins resolve to the versions their comments claim, and
says nothing at all about the packages in the lockfile.

`scan` **is** a required status check on `acc`, promoted once its baseline had
been triaged — a workflow that runs but cannot block is advice, not a gate.
That promotion was a ruleset change, not a change to this file. It is not
required on `main`; see [Required checks and branch
rules](#required-checks-and-branch-rules).

Its concurrency group is the one deliberate divergence from every other workflow
here: pull-request runs cancel, pushes to `acc` and `main` do not. Those pushes
are what write the Semgrep Cloud baseline, and cancelling one mid-upload leaves
the dashboard describing a scan that never finished.

---

## Node runtime

One source of truth. Both App Service plans run `NODE|22-lts`, and until
v2026.09.7 eight workflows asked for `node-version: '20'` — building the
deployed artifact on a major the host does not run.

- The **eight deploy workflows** read `node-version-file: .nvmrc`.
- `.nvmrc` carries an exact `22.23.2`.
- The root `engines.node` is `>=22`, and `engines.npm` is `>=10.0.0`.
- `zizmor.yml` names an exact `'24.20.0'`, deliberately on a different major:
  its `renovate-config-validator` step needs Node 24, because `renovate`
  declares `engines.node ^24.11.0`. npm accepts that mismatch with an
  `EBADENGINE` warning rather than refusing, which is how the validator once
  ran unsupported and green. Pointing it at `.nvmrc` instead would run it on
  Node 22, which `renovate` does not support.

!!! note "`engines` is a floor, not the runtime — and Renovate no longer raises it"
    Renovate's `rangeStrategy bump` applies to `engines` as well as to
    dependencies, and it once raised `engines.node` to `>=22.23.2` and
    `engines.npm` to `>=10.9.9` — a floor **no Node 22 release satisfies**,
    since 22.23.2 bundles npm 10.9.8. Nothing enforces `engines` here, so a
    raised floor produces `EBADENGINE` warnings on a slightly older toolchain
    and drifts the root away from `packages/backend` and App Service's
    `NODE|22-lts`. `engines` now uses `rangeStrategy widen`, which leaves a
    range untouched when the new version already satisfies it: `>=22` stays
    `>=22`, and the exact runtime stays where it belongs, in `.nvmrc`.

`.nvmrc` is also in every deploy workflow's **path filter**, which it was not
until v2026.09.9 — see [Path filters](#path-filters).

---

## The package-manager cooldown

Renovate holds an update for fourteen days before proposing it, but that covers
only the updates *Renovate* proposes. Lock-file maintenance hands the refresh to
npm, which is where the transitive tree actually moves, and Renovate's own
documentation says its cooldown cannot apply there.

A root `.npmrc` closes that gap:

```ini
min-release-age=14
```

npm itself will then not resolve a version published less than fourteen days
ago. Four properties of it were measured rather than assumed, and each one
matters:

| Context | Behaviour |
|---|---|
| npm **11.10 or newer** | Honours it on `install` and `update` |
| `npm ci` | **Ignores it on purpose** — so CI, which only ever runs `npm ci`, cannot fail on it |
| npm **10.9.8** (bundled with Node 22.23.2) | Ignores it *without a warning* — which is why `scripts/check-deps.sh` warns when npm is older than 11.10 |
| The backend deploy | Not covered: it installs in its own `deploy/` folder, and npm reads a project `.npmrc` only from the project root |

An urgent security fix may skip the cooldown, as the guideline allows — set the
flag to zero on that one command line, never in the file, and say why in the
pull request. Renovate's security pull requests already do this themselves,
retrying without the cutoff when npm answers `ETARGET`.

---

## What each pipeline runs

Every pipeline that has something to test runs the suite **before** it builds,
and a failing test blocks the deploy.

| Workflow | Lint | Type-check | Tests | Extra gates |
|---|:---:|:---:|:---:|---|
| `azure-backend-*` | ✅ | – | ✅ | Verifies `dist/index.js` exists |
| `azure-frontend-*` | ✅ | – | ✅ | `@ronl/pa-cockpit`'s 476 tests, then a performance budget, each its own step |
| `azure-publicsite-*` | ✅ | ✅ | ✅ | Prerender + bundle-cleanliness gate, inside the build |
| `azure-pa-demo-*` | ✅ | ✅ | ✅ | **Playwright E2E**, then the bundle gate inside the build |

`@ronl/pa-cockpit` has no deploy workflow of its own — it is a library both the
frontend and the demo consume — so until v2026.09.6 its tests ran nowhere in CI,
even though a change to it already triggered the frontend build through that
workflow's path filter. Both frontend workflows now run them, ahead of the
frontend's own suite: a break there explains a break here.

`azure-pa-demo-acc.yml` is the only workflow in the repository that runs an
end-to-end suite. It installs a Chromium browser first, since no other workflow
here needs Playwright, and runs it **before** the build. The demo needs no
backend, database or Keycloak — Playwright starts its own dev server and that is
the whole environment. See [PA-demo suite](testing/pa-demo.md).

### Static-site deploy shape

The three static sites share one shape:

```
npm ci
    ↓
Build @ronl/shared          (frontend and pa-demo only)
    ↓
Lint → Type-check → Unit tests → [E2E, pa-demo only]
    ↓
Build for the target environment
    ↓
Azure/static-web-apps-deploy   (skip_app_build: true)
    ↓
[frontend only] Wait, then verify HTTP 200
```

`skip_app_build: true` matters more than it looks: the deploy action uploads an
artifact **this pipeline built**, rather than building one inside a floating
vendor container. See
[Supply-chain gate → What this does not protect](../../contributing/supply-chain.md#what-this-does-not-protect).

### Backend pipeline

```
npm ci → Build @ronl/shared → Lint → Unit tests → tsc → Verify dist/index.js
    ↓
Prepare deployment package → Create zip → Upload artifact
    ↓
(deployment happens separately, from a developer machine)
```

Since v2026.09.7 `azure-backend-acc.yml` also runs on a pull request to `acc`,
so the backend suite gates the branch that caused a failure rather than
reporting it on `acc` after the merge. No `if:` guard was needed for that: this
workflow ends at an uploaded artifact and has no deploy step, so a pull-request
run has no external side effect.

`azure-backend-prod.yml` deliberately gains no `pull_request` trigger. Every
commit reaching `main` is promoted from `acc` and has already run this suite on
its own pull request, so re-running it on the promotion says nothing new —
while `audit`, which *is* required on `main`, reports there on every pull
request regardless of base.

---

## Path filters

Workflows trigger only when relevant files change. On `push` that is an
ordinary `paths:` filter on the trigger; on `pull_request` it is **not**, and
the next section explains why.

| Workflow | Paths |
|---|---|
| `azure-backend-*` | `packages/backend/**`, `packages/shared/**`, `package-lock.json`, `package.json`, `.nvmrc`, own file |
| `azure-frontend-*` | `packages/frontend/**`, `packages/shared/**`, `packages/pa-cockpit/**`, `.nvmrc`, own file |
| `azure-pa-demo-*` | `packages/pa-demo/**`, `packages/shared/**`, `packages/pa-cockpit/**`, `.nvmrc`, own file |
| `azure-publicsite-*` | `packages/public-site/**`, `.nvmrc`, own file |
| `zizmor.yml`, `semgrep.yml` | **none, deliberately** — both scanners must run on every pull request |

`.nvmrc` is in all eight deploy filters since v2026.09.9, and its absence was a
real hole rather than an oversight to tidy: `.nvmrc` sets the Node version every
one of these workflows builds, tests and ships on, so a Node bump used to build
nothing, test nothing and deploy nothing — and the new version then reached the
next unrelated deploy untested. Each pattern was checked to match `.nvmrc` at
the repository root only.

### Why the `pull_request` filter moved into a job

This is the part worth copying into another repository, because the reasoning is
not obvious from either half on its own.

**A required status check must report on every pull request.** GitHub waits for
a check it has been told to require. It does not reason about relevance.

**A workflow whose trigger filters it out never starts, and so reports
nothing.** A `paths:` filter on `pull_request` is evaluated before the run
exists. There is no skipped run, no neutral conclusion, no check at all — so a
required build check would leave every pull request that does not touch its
paths waiting forever, unmergeable.

**A job skipped by its own `if:` reports success.** That is the escape: the
workflow starts, the expensive job does not run, and the check reports green.

So each of the four ACC deploy workflows now:

1. drops `paths:` from its `pull_request` trigger entirely — it starts on every
   pull request to `acc`;
2. runs a small `changes` job first, which asks the GitHub API for the pull
   request's files and matches them against **one regular expression mirroring
   the push filter** (renames counted under both names, as GitHub's own filter
   does);
3. gates the build and close jobs on that job's `relevant` output.

The gate is deliberately fail-safe. The jobs run when `changes` says *relevant*
**and** when `changes` did not succeed at all, so a failed API lookup means a
full build rather than a free pass. The push trigger keeps its own `paths:`
filter — nothing is required on a push, so none of this applies there.

!!! warning "Required checks match by job *name*"
    The ruleset names `Build and Deploy ACC Frontend`, not the workflow or the
    job id. Renaming one of those jobs silently detaches the requirement, so the
    rename and the ruleset change belong in the same pull request.

The root lockfile and manifest are in the **backend** filters only. Every
workspace resolves through them, so a hoisted dependency can move under any of
them and a lockfile-only change would otherwise be built and tested by nothing.
Widening the other three filters the same way is a decision of its own: each of
those claims a Static Web Apps staging environment on every pull request that
matches, and widening them would make every lockfile-only pull request claim
three previews.

!!! note "The plan ceiling is not what it was when this rule was written"
    The frontend app was on the **Free** plan, three staging environments, when
    five open pull requests exhausted it on 28 August 2026. Read from Azure on
    15 September 2026, all three *acceptance* apps are **Standard** — ten
    environments — and it is the *production* frontend that is Free. The
    argument for keeping the filters narrow is now about what a lockfile-only
    change should legitimately deploy, not about running out of room.

`packages/pa-cockpit/**` appears in two filters because both the frontend and
the demo consume that package; a cockpit change that triggered neither would
version and deploy nothing.

`packages/shared/**` is in the demo's filter even though its imports from shared
are type-only and erased before the bundler sees them. A shared-only change
cannot alter the demo's compiled output — but without the filter, a breaking
type change would never run the demo's type-check, and would surface later at an
unrelated pull request.

!!! note "A `package.json`-only change still triggers the backend build"
    `packages/backend/**` matches `package.json`, so adding a script or bumping
    `engines` fires a full backend build even though no source changed. Since the
    habit is to run the deploy script whenever that workflow fires, this invites
    a deploy of byte-identical code. The question to ask is not *did the workflow
    run* but:

    ```bash
    git diff --name-only <last-deployed-sha>..HEAD -- packages/backend/src packages/shared/src
    ```

    Empty output means there is nothing to deploy.

---

## Concurrency

All six deploying workflows declare a `concurrency:` group keyed
`${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}`.
The three `acc` workflows set `cancel-in-progress: true`; the three production
workflows set **`false`**, so runs queue — interrupting a live production deploy
to start another is worse than waiting.

Without this, two merges minutes apart sent two deployments at the same Azure
environment and **Azure picked a loser**, reporting `Deployment Canceled` on a
job that had done nothing wrong.

!!! important "The group key must distinguish the event, not just the ref"
    Keyed on `github.ref` alone, the `pull_request(closed)` teardown and the
    `push` deploy that a merge fires simultaneously land in the same group and
    cancel each other at random — observed as two acceptance deploys skipped and
    one preview left standing. Keying pull requests on their number and pushes
    on the ref keeps the two apart.

`azure-backend-acc.yml` gained a group of its own when it started running on
pull requests, keyed the same way: without it a branch pushed twice in quick
succession runs the backend's 2008 tests twice over.
`azure-backend-prod.yml` carries none — it builds and uploads an artifact on a
push to `main` and never reaches Azure, so no race exists.

---

## Branch strategy

```
feature/*  →  PR to acc  →  audit + path-matched deploys  →  merge  →  main
                  ↓                                                     ↓
             ACC deploys                                          PROD deploys
```

A pull request is **required** to land on either branch, and its required
checks must pass — a repository ruleset enforces both on `acc` and on `main`. A
direct push is rejected. Squash and rebase merging are disabled repo-wide, because
changelog entries name commits by SHA and both alternatives rewrite those
hashes.

Releases therefore land through a pull request rather than a local fast-forward.

### Required checks and branch rules

| | `acc` | `main` |
|---|---|---|
| Ruleset | `acc supply-chain gate` | `main promotion gate` |
| Required status checks | `audit`, `scan`, and the four build checks | `audit` |
| Pull request | Required, 0 approvals, merge method `merge` only | Required, 0 approvals, merge method `merge` only |
| `deletion` | Blocked | Blocked |
| `non_fast_forward` | Blocked | Blocked |

The four build checks on `acc` are `build` (the backend), **Build and Deploy ACC
Frontend**, **Build and Deploy ACC PA Demo** and **Build and Deploy ACC Public
Site**. They were promoted together with `scan` once each of their workflows
could report on every pull request — see [Why the `pull_request` filter moved
into a job](#why-the-pull_request-filter-moved-into-a-job).

`main` stays on `audit` alone, and that makes it the weaker branch in this one
respect. It is deliberate: **none of the production workflows has a
`pull_request` trigger at all**, so there is no build check there to require.
Every commit reaching `main` is promoted from `acc`, where the full set has
already reported on its own pull request.

The two rulesets differ in one further parameter, deliberately:
`require_extra_approval_for_unattributed_changes` is `true` on `acc` and
`false` on `main`, because the promotion that created `main` carried commits
under three author identities against a ruleset requiring zero approvals — the
flag would have demanded an approval nobody could give. It is preserved rather
than harmonised, and written down in both places so that the next person to
compare them does not read it as drift.

!!! note "Classic branch protection gives the wrong answer here"
    It still reports `allow_force_pushes: true` on both branches. That is a
    vestigial second layer rather than a hole: the ruleset's `non_fast_forward`
    rule is what refuses the push. Reading the classic protection endpoint alone
    is misleading.

---

## Pull-request previews

Each preview deploys to its own Static Web Apps staging environment.

!!! warning "A preview cannot reach the backend"
    A preview gets an ephemeral `*.azurestaticapps.net` origin that is not in the
    backend's `CORS_ORIGIN` allowlist, and `VITE_API_URL` is baked in at build
    time. The backend is not deployed per pull request at all — its acceptance
    workflow runs on one, but ends at an uploaded artifact with no deploy step —
    so every preview talks to the one shared acceptance backend and is refused.
    **A preview demonstrates that static pages render; nothing more.**

There is a staging-environment ceiling per app, and it was hit: when the three
frontends were on the Free plan, three environments each, a one-file change
redeployed all three sites and five open pull requests exhausted the quota on
28 August 2026. Two things have changed since. The acceptance apps are now on
**Standard**, ten environments each, and the filtering that stops an unrelated
pull request claiming a preview no longer sits on the `pull_request` trigger —
it is the `changes` job described under [Path filters](#path-filters).

A dependency pull request is not automatically preview-free, which
`renovate.json` once claimed: only lockfile-only and root-only ones are. One
editing `packages/pa-cockpit/**` holds a preview on **both** `frontend-acc` and
`pa-demo-acc`, since both workflows consume that package.

---

## Required GitHub secrets

| Secret | Used by |
|---|---|
| `AZURE_WEBAPP_PUBLISH_PROFILE_ACC` / `_PROD` | Backend workflows |
| `AZURE_STATIC_WEB_APPS_API_TOKEN_ACC` | Frontend |
| `AZURE_STATIC_WEB_APPS_API_TOKEN_PUBLIC_SITE_ACC` | Public site |
| `AZURE_STATIC_WEB_APPS_API_TOKEN_PA_DEMO_ACC` | PA-demo |
| `GITHUB_TOKEN` | Preview comments and teardown (scoped per job) |

Production deploys use the matching `_PROD` token names. To rotate a publish
profile: Azure Portal → App Service → Overview → *Get publish profile*, then
update the GitHub secret with the file contents.

`GITHUB_TOKEN` is **read-only by default**, with `pull-requests: write` granted
only to the six jobs that comment on pull requests, `pull-requests: read` on the
four `changes` jobs that look up a pull request's changed files, and
`permissions: {}` on the three that only tear down a preview.

---

## Rolling back

**Backend** — redeploy the previous commit by re-running the deploy script
against it. Or use the Azure Portal: App Service → Deployment Center → select a
previous deployment → *Redeploy*.

**Static sites** — Azure Static Web Apps keeps deployment history. Azure Portal:
Static Web App → Environments → select a previous deployment → *Promote*.

---

## Related

- [Supply-chain gate](../../contributing/supply-chain.md) — pinning, least privilege,
  and the `audit` gate
- [Testing — Overview](testing/overview.md) — what the suites the pipelines run
  actually cover
