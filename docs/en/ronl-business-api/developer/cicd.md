---
component: RONL Business API
---

# CI/CD

RONL Business API runs **eleven GitHub Actions workflows**: an
acceptance/production pair for each of four packages, two scanning
workflows — the supply-chain `audit` gate and a Semgrep `scan` — and, since
v2026.09.10, the **promotion workflow** that orchestrates the four production
deploys. Every one of the **twenty-two jobs** across them names `ubuntu-24.04`,
never `ubuntu-latest`: that label is one GitHub moves to a new Ubuntu release on
its own schedule, so pinning it means a change of OS release arrives as a diff
here rather than silently. The label pins the *release*, not the image — GitHub
rebuilds the image about weekly, and a hosted runner cannot pin it by digest.

!!! info "`acc` and `main` carry the same eleven files, and deliberately different shapes"
    Verified against `main` at `86af73e` on 23 September 2026 (v2026.09.11).
    `main` was once four workflows behind and carried none of the pinning or
    gating described below — closing that gap was a CI-alignment programme that
    finished in v2026.09.7, and `main` has its own `main promotion gate` ruleset.

    The two branches now differ in **how deployment is triggered**, not in which
    files exist. On `main` a single promotion workflow runs and calls the four
    production deploys in order; on `acc` the four acceptance workflows still
    fire independently on a push and on a pull request. That asymmetry is a
    decision, not drift — see [How a promotion reaches
    production](#how-a-promotion-reaches-production).

---

## Workflow overview

| File | Trigger | Target | Deploys? |
|---|---|---|---|
| `zizmor.yml` | PR, push to `acc`/`main` | — | No — the `audit` gate |
| `semgrep.yml` | PR, push to `acc`/`main` | — | No — the `scan` job |
| `promote-to-production.yml` | push to `main` (**no paths filter**), `workflow_dispatch` | — | No — it *calls* the four below |
| `azure-backend-acc.yml` | push + PR to `acc` | `acc.api.open-regels.nl` | **Yes** — except on a pull request |
| `azure-backend-prod.yml` | `workflow_call`, `workflow_dispatch` | `api.open-regels.nl` | **Yes** |
| `azure-frontend-acc.yml` | push + PR to `acc` | `acc.mijn.open-regels.nl` | Yes |
| `azure-frontend-prod.yml` | `workflow_call`, `workflow_dispatch` | `mijn.open-regels.nl` | Yes |
| `azure-publicsite-acc.yml` | push + PR to `acc` | `acc.publiek.open-regels.nl` | Yes |
| `azure-publicsite-prod.yml` | `workflow_call`, `workflow_dispatch` | `publiek.open-regels.nl` | Yes |
| `azure-pa-demo-acc.yml` | push + PR to `acc` | `acc.plato.open-regels.nl` | Yes |
| `azure-pa-demo-prod.yml` | `workflow_call`, `workflow_dispatch` | `plato.open-regels.nl` | Yes |

All eight Azure workflows support `workflow_dispatch`, and for the four
production ones that is now the **only** manual route into Azure — and the
escape hatch if the promotion workflow itself is broken. Neither scanning
workflow supports it: both are meant to run from the events themselves and
nothing else.

!!! note "The four production workflows no longer trigger on a push"
    They carry `workflow_call:` and `workflow_dispatch:` and nothing more. A
    push to `main` starts `promote-to-production.yml`, which decides which of
    them to call and in what order. They never had a `pull_request` trigger,
    which is why `audit` is still the only requirable check on `main`.

---

## How a promotion reaches production

A promotion is one thing, so since v2026.09.10 it is **one workflow run**.

```
push to main
    ↓
promote-to-production.yml        (no paths filter — it must always start)
    ↓
changes        scripts/promotion-targets.sh decides which of the four are needed
    ↓
backend        azure-backend-prod.yml, alone and first
    ↓
frontend  ·  pa-demo  ·  public-site        in parallel, once the backend is done
```

### The failure it fixes

Until v2026.09.10 a push to `main` fired four deploy workflows at once and
nothing sequenced them. The backend job is the slowest of the four — it runs the
full backend suite before it packages anything, while a Static Web App deploy is
a build and an upload — so the frontends reliably finished **first**. A frontend
calling a route the deployed backend does not serve yet gets a 404, and on the
public site that is worse than transient: its build **prerenders against the
live API**, so a prerender inside that window bakes the failure into the
deployed output.

An earlier change had removed the manual *"push, then run the deploy script"*
step without adding ordering, which shrank the window from *until someone
remembers* to *the minutes the backend needs* and made it nobody's decision to
get right.

### How the ordering is expressed

The three site jobs each `needs: [changes, backend]` and run only when
`needs.backend.result` is in `["success", "skipped"]` — a skipped backend
(nothing backend-shaped changed) and a successful one both mean the deployed
backend serves what these sites expect, while `cancelled` or `failure` means
nobody knows and the sites must not go. Every job also carries `!cancelled()`,
without which GitHub skips a job after a failed `need` regardless of what its
condition says.

The whole graph **fails safe towards deploying**. Each job runs when `changes`
said *true* **or when `changes` did not succeed at all**, so a git failure there
means a full deploy rather than a free pass.

The four calls use GitHub's self-repository syntax rather than the
workspace-relative `./` form, which resolves against the runner's filesystem and
can pick up something an earlier step wrote there — zizmor's self-repository
audit flags the latter, and `audit` is a required check.

### Secrets are named, never inherited

The backend call passes **no secrets at all**: it authenticates with OIDC
against a repository *variable*, and repository variables need no passing.
`secrets: inherit` would have handed each site workflow every secret the
repository holds — including the Keycloak VM's SSH key and the Semgrep token —
to deploy one static site. Each site call therefore names exactly its own
Static Web Apps token.

### Proving it without promoting

`workflow_dispatch` takes a `dry_run` input that **defaults to true**. The four
calls are resolved when the run is *parsed*, before any job starts, so a dry run
still fails loudly on a bad workflow reference, a missing secret or an
unsatisfiable `needs` graph — it simply deploys nothing.

!!! danger "If the promotion workflow breaks, nothing deploys — silently"
    The four production workflows are not required checks on `main`; `main`
    requires `audit` alone. So a promotion whose orchestrating workflow fails to
    parse, or fails at `changes`, produces a red run and no deployment, and
    nothing else reports it.

    The escape hatch is that all four keep `workflow_dispatch` and can be run
    alone from the Actions tab.

!!! warning "`acc` is deliberately not restructured"
    Acceptance keeps the same four-way shape on a push to `acc`. Its workflows
    also carry the `pull_request` trigger whose **job names** the `acc
    supply-chain gate` ruleset requires by name, and a reusable workflow's check
    renames every required context — so converting them would silently detach
    four required checks. Acceptance traffic is also us, which makes the
    ordering problem there far less costly.

---

## The two scanning workflows

Neither deploys anything, and neither carries a `paths:` filter: both must reach
every pull request regardless of what it touched.

### `audit` — the required check

`zizmor.yml` has one job, and it runs **eight steps, all of them blocking**:

| # | Step | What it does |
|---|---|---|
| 1 | Checkout | `persist-credentials: false` |
| 2 | Set up Node `24.21.0` | For the config validator only — see [Node runtime](#node-runtime) |
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
- `zizmor.yml` names an exact `'24.21.0'`, deliberately on a different major:
  its `renovate-config-validator` step needs Node 24, because `renovate`
  declares `engines.node ^24.11.0`. npm accepts that mismatch with an
  `EBADENGINE` warning rather than refusing, which is how the validator once
  ran unsupported and green. Pointing it at `.nvmrc` instead would run it on
  Node 22, which `renovate` does not support. Renovate maintains this pin behind
  the same fourteen-day cooldown as everything else — v24.21.0 was released
  sixteen days before the v2026.09.11 bump that adopted it, checked against the
  Node release index rather than taken from the `stability-days` status, which
  reads *not met* on lock-file maintenance branches that are in fact compliant.

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
| `azure-backend-*` | ✅ | – | ✅ | Verifies `dist/index.js` exists, packages from the lockfile, then deploys and verifies the deploy took effect |
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
azure/login (OIDC)  →  az webapp deploy
    ↓
Liveness check (5 × 10s on /v1/health/live)
    ↓
Verify the deploy took effect (12 × 15s, comparing /v1/health build.sha)
```

Since v2026.09.10 the backend is deployed **by the workflow**, not by hand. Three
parts of that are worth knowing, because each replaced something that had gone
wrong:

- **Authentication is OIDC, not a publish profile.** SCM basic auth is disabled
  on both App Services — measured on the resources rather than assumed
  (`basicPublishingCredentialsPolicies/scm` `allow=false`) — so a
  publish-profile deploy would be rejected outright. The workflow does what the
  hand-run scripts already did, `az webapp deploy` over an ARM token, with a
  machine identity instead of a human session. That removes the failure that
  once stopped a release reaching acceptance: an expired `az login`, discovered
  after the merge. The acceptance and production identities are separate and
  each scoped to its own App Service, so a mistake in the acceptance workflow
  cannot reach production.
- **The bundle installs from the lockfile.** It used to be `npm install
  --production` in a directory holding a `package.json` and **no lockfile**, so
  it re-resolved every caret range at deploy time. On 29 August 2026 an
  acceptance deploy shipped `@anthropic-ai/sdk` freshly jumped 42 minor versions
  and `uuid` five majors, none of it matching what any build had verified. The
  install now runs `npm ci --omit=dev --workspace=@ronl/backend` in a staging
  copy holding the root manifest and lockfile. A production dependency the
  lockfile records under the workspace rather than hoisted — `altcha-lib` is
  one — is merged into `deploy/node_modules` afterwards; the genuinely ambiguous
  case, where the same package is *also* hoisted, fails rather than guessing.
- **The deploy proves itself.** A `build-info.json` in the artifact records the
  commit and run that produced it, `/v1/health` reports it, and the workflow
  polls that value until it matches the commit just deployed. The previous build
  keeps answering while Azure starts the new one, so a liveness check passes
  against either — without this, a deploy that silently left the old artifact
  serving would have passed every check above it.

On acceptance those four steps are gated `if: github.event_name !=
'pull_request'`, so a pull request builds and tests the backend without shipping
it and the build check stays required.

Since v2026.09.7 `azure-backend-acc.yml` also runs on a pull request to `acc`,
so the backend suite gates the branch that caused a failure rather than
reporting it on `acc` after the merge.

`azure-backend-prod.yml` deliberately has no `pull_request` trigger — and since
v2026.09.10 no `push` trigger either. Every commit reaching `main` is promoted
from `acc` and has already run this suite on its own pull request, so re-running
it on the promotion says nothing new, while `audit`, which *is* required on
`main`, reports there on every pull request regardless of base. The Linked Data
Explorer excludes its production workflow for a different reason that does not
apply here — there the `production` environment carries required reviewers, so a
`pull_request` trigger would put a human approval in front of the very tests
meant to inform it. **Neither environment in this repository has any protection
rule at all**, so the exclusion here stands on the promotion argument alone.

---

## Path filters

Workflows trigger only when relevant files change. On the **acceptance** side
that is an ordinary `paths:` filter on a `push`; on `pull_request` it is **not**,
and the section after next explains why. On the **production** side the filters
no longer sit on a trigger at all — they moved into a script.

| Acceptance workflow | Paths |
|---|---|
| `azure-backend-acc.yml` | `packages/backend/**`, `packages/shared/**`, `package-lock.json`, `package.json`, `.nvmrc`, own file |
| `azure-frontend-acc.yml` | `packages/frontend/**`, `packages/shared/**`, `packages/pa-cockpit/**`, `.nvmrc`, own file |
| `azure-pa-demo-acc.yml` | `packages/pa-demo/**`, `packages/shared/**`, `packages/pa-cockpit/**`, `.nvmrc`, own file |
| `azure-publicsite-acc.yml` | `packages/public-site/**`, `.nvmrc`, own file |
| `zizmor.yml`, `semgrep.yml` | **none, deliberately** — both scanners must run on every pull request |

### The production filters live in a script

`scripts/promotion-targets.sh` is the one place that answers for all four
production deploys. It reads changed paths on stdin and writes one
`<target>=true|false` line per target, which the promotion workflow uses
directly as its `outputs:` source.

| Target | Matches (anchored at the repository root) |
|---|---|
| `backend` | `packages/backend/`, `packages/shared/`, `azure-backend-prod.yml`, `package-lock.json`, `package.json`, `.nvmrc` |
| `frontend` | `packages/frontend/`, `packages/shared/`, `packages/pa-cockpit/`, `azure-frontend-prod.yml`, `.nvmrc` |
| `pa_demo` | `packages/pa-demo/`, `packages/shared/`, `packages/pa-cockpit/`, `azure-pa-demo-prod.yml`, `.nvmrc` |
| `public_site` | `packages/public-site/`, `azure-publicsite-prod.yml`, `.nvmrc` |

Each pattern mirrors the `paths:` filter its acceptance sibling still carries,
and the acceptance copy is the reference — the two have to be kept in step by
hand.

Three details in it are load-bearing:

- **It is a file rather than a `run:` block** precisely so the decision can be
  run locally against a real commit range. A `run:` block can be read but not
  run, and this decision is the only thing standing between a promotion and a
  deploy that does not happen.
- **`--all` is the fail-safe.** Three cases reach it: a `workflow_dispatch`,
  which carries no `before`; a first or force push, whose `before` is all zeros;
  and a `before` the clone cannot resolve. A promotion whose range cannot be
  read is not a promotion that changed nothing.
- **`promote-to-production.yml` is in none of the patterns.** Each deploy
  workflow lists *itself* so that a change to it gets exercised by running it;
  the promotion workflow runs on every promotion already, so listing it would
  mean editing a comment in it redeployed all four sites.

The diff is taken with `--no-renames`, because with rename detection a moved
file appears under its new name only — and a file moved *out of*
`packages/backend/` would then not deploy the backend it was removed from.
GitHub's own path filters count both names; so does this.

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

Since v2026.09.10 the same job also emits a second, independent output,
`preview`, which decides whether this pull request gets a deployed copy — see
[Pull-request previews](#pull-request-previews).

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

The four acceptance workflows declare a `concurrency:` group keyed
`${{ github.workflow }}-${{ github.event.pull_request.number || github.ref }}`
with `cancel-in-progress: true`.

The four production workflows and the promotion set **`false`**, so runs queue —
interrupting a live production deploy to start another is worse than waiting.
They also key their group on a **literal naming the app** rather than on
`${{ github.workflow }}`, and that is not cosmetic: inside a called workflow
that expression resolves to the **caller's** name, so four groups equal to the
promotion's own would deadlock every deploy against the job waiting for it. The
promotion's own group is the bare literal `promote-to-production`, for the same
reason.

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
succession runs the backend's whole suite twice over.
`azure-backend-prod.yml` carried none while a push to `main` was its only
automatic trigger — one push, one run. It has one now (`deploy-backend-prod-…`,
queueing), because `workflow_dispatch` remains the escape hatch for deploying
the backend alone and that can collide with the backend deploy a promotion is
already running. Two `az webapp deploy` calls at the same App Service is the
failure it prevents.

---

## Branch strategy

```
feature/*  →  PR to acc  →  audit + path-matched deploys  →  merge  →  main
                  ↓                                                     ↓
             ACC deploys                                    promote-to-production
                                                                        ↓
                                                    backend, then the three sites
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
`pull_request` trigger at all** — and since v2026.09.10 they have no `push`
trigger either — so there is no build check there to require. Every commit
reaching `main` is promoted from `acc`, where the full set has already reported
on its own pull request.

The cost of that is recorded rather than glossed: because these are not required
checks, a promotion that deploys nothing looks the same to the branch as one
that deploys everything. See [If the promotion workflow breaks, nothing deploys
— silently](#how-a-promotion-reaches-production).

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

Each preview deploys to its own Static Web Apps staging environment — but since
v2026.09.10 only when someone asks for one.

### A preview is opt-in

Every pull request that touched an app's paths used to deploy a public copy of
it. Most showed nothing a build had not already proved, and each one is a public
URL and a slot on a plan with a ceiling this repository has hit. The clearest
case: three Renovate security pull requests claimed **eight** preview
environments between them, because each path filter matches its own
`package.json` and a dependency bump therefore looks exactly like a source
change.

A preview is now created only when **both** hold:

1. the pull request changed something other than a manifest, and
2. it carries the `preview` label.

Adding the label starts a run — `labeled` is in the workflow's trigger types.

!!! important "Both conditions gate the deploy *step*, not the job"
    That distinction is the whole design. `build_and_deploy_job` is the only
    place the frontend, PA demo and public site are linted, type-checked,
    unit-tested and built on a pull request. Gating the *job* would have made
    labelling a precondition for verifying the code at all — and because a
    skipped job reports success, the required check would have passed having
    tested nothing.

The two decisions fail safe in opposite directions, deliberately. The build
filter errs towards **building** when the GitHub API call fails, because an
error must never be a free pass. The preview decision **withholds**, because the
risk it guards is publishing a copy of an unreviewed branch rather than failing
to test one.

### A preview can reach the acceptance backend

Until v2026.09.10 it could not. A preview gets an ephemeral origin that is not
in the backend's `CORS_ORIGIN` allowlist, and there is a new one per pull
request, so it cannot be listed — which meant a preview could only demonstrate
that static pages render, on an environment the pull request had already paid to
build and deploy.

`CORS_ORIGIN` is handed to `cors` as an array matched by exact equality, so
adding an origin per pull request would have meant an App Service settings write
and a restart of the shared acceptance backend for every preview. So `origin`
becomes a **function**, and three properties of it matter:

- **Matched on the app's stable slug, not on the domain.** A
  `*.azurestaticapps.net` pattern would let any Azure Static Web App in the
  world make credentialed cross-origin requests to the tier. Azure derives a
  preview hostname from the app's stable slug, so `CORS_PREVIEW_SLUGS` carries
  slugs and the pattern anchors on them.
- **Never in production**, enforced in code rather than by trusting the setting
  to be empty — so a value that finds its way onto the production App Service
  changes nothing about what production accepts.
- **The guard reads the deployment environment, not `NODE_ENV`.** Acceptance
  deliberately runs `NODE_ENV=production`, so keying on that would have treated
  it as production and refused every preview, leaving the feature silently doing
  nothing.

Verified live on both tiers afterwards: the three registered slugs allowed on
acceptance, refused on production, and five near-miss origins — another tenant's
app, a slug that merely starts the same, a look-alike domain, the app's own
default hostname, and a non-numeric environment — refused on both.

### Previews that outlive their pull request

A preview is deleted by a close job when the pull request closes, and that job
cannot catch everything: **GitHub does not run `pull_request` workflows while a
pull request has a merge conflict**, closing included. On 12 September 2026
three Renovate security pull requests left eight previews behind across three
apps. Nothing reported them; they were found by listing environments from Azure
by hand on 15 September, and again on 20 September when they were still there.

`npm run check-previews` (`scripts/check-previews.sh`) now asks from the other
end: it lists the environments Azure actually has, compares them with the pull
requests GitHub has open, and names every orphan. It finds the apps by their
`repositoryUrl` rather than by workflow filename, so an app added later is
checked without editing the script, and it reads **every** subscription
`az account list` returns, because these six apps span two of them.

Anything unchecked is reported rather than passed over, and that rule earned its
place while the script was being written: an expired Azure refresh token made
`az staticwebapp list` fail, and with stderr discarded it returned an empty list
— indistinguishable from a subscription holding no apps. So the session is
proven with a real ARM call rather than `az account show`, which reads cached
state and succeeds against a token that expired days ago; a subscription that
cannot be read fails the command; and finding no apps at all fails too, because
it means nothing was compared. Like `check-mirror`, it **never deletes** — it
prints the exact command and stops.

### The plan ceiling

There is a staging-environment ceiling per app, and it was hit: when the three
frontends were on the Free plan, three environments each, a one-file change
redeployed all three sites and five open pull requests exhausted the quota on
28 August 2026. Read from Azure on 15 September 2026, the three *acceptance* apps
are on **Standard** — ten environments — and it is the *production* frontend
that is Free.

A dependency pull request is not automatically preview-free, which
`renovate.json` once claimed: only lockfile-only and root-only ones are. One
editing `packages/pa-cockpit/**` is relevant to **both** `frontend-acc` and
`pa-demo-acc`, since both workflows consume that package — though under the
label rule above it now claims a preview on neither unless someone asks.

---

## Required GitHub secrets and variables

| Secret | Used by |
|---|---|
| `AZURE_STATIC_WEB_APPS_API_TOKEN_ACC` | Frontend |
| `AZURE_STATIC_WEB_APPS_API_TOKEN_PUBLIC_SITE_ACC` | Public site |
| `AZURE_STATIC_WEB_APPS_API_TOKEN_PA_DEMO_ACC` | PA-demo |
| `GITHUB_TOKEN` | Preview comments and teardown (scoped per job) |

Production deploys use the matching `_PROD` token names, passed explicitly by
`promote-to-production.yml` — one token per site call, never `secrets: inherit`.

**The backend workflows need no secret at all.** They authenticate with OIDC, so
what they read are repository **variables**, which need no passing into a called
workflow:

| Variable | Used by |
|---|---|
| `AZURE_CLIENT_ID_ACC` | `azure-backend-acc.yml` |
| `AZURE_CLIENT_ID_PROD` | `azure-backend-prod.yml` |
| `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID` | both |

Each backend job grants itself `id-token: write` to mint the token `azure/login`
exchanges for an ARM token, and the promotion grants the same on the call,
because a called workflow cannot hold more permission than its caller.

!!! warning "There is no publish profile, and `AZURE_WEBAPP_PUBLISH_PROFILE_*` is dead"
    Those secrets date from March 2026 and nothing reads them. SCM basic auth is
    **disabled** on both App Services, so a publish-profile deploy would be
    rejected — which is why the backend deploys over OIDC instead.

### Storing a token without breaking the deploy

Use `scripts/set-secret.sh`. Piping a token straight out of the Azure CLI into
`gh secret set` stores a **trailing newline** — 120 bytes where the key is 119.
Both halves are the documented way to do their job; the composition is what goes
wrong. It cost the public site its first production deploy, and the failure
named nothing: every step passed, then *"An unknown exception has occurred"*
with a DeploymentId printed first, which reads as an upload that began and
failed rather than an authentication that never happened.

The script reads the value from **stdin**, strips leading and trailing
whitespace, refuses an empty result, and reports the **byte count** it stored.
The byte count is the point: a secret cannot be read back, so nothing about a
stored secret can afterwards confirm or deny a stray newline. Stdin is read with
a sentinel rather than plain command substitution, which strips trailing
newlines itself and would therefore store the right value while reporting the
wrong count — for exactly the case this exists to catch. The value is never
echoed, never passed as an argument, and never written to a file.

`GITHUB_TOKEN` is **read-only by default**, with `pull-requests: write` granted
only to the six jobs that comment on pull requests, `pull-requests: read` on the
four `changes` jobs that look up a pull request's changed files, and
`permissions: {}` on the three that only tear down a preview.

---

## Rolling back

**Backend** — `workflow_dispatch` `azure-backend-prod.yml` from the Actions tab
against the previous commit; it deploys the backend alone. Or use the Azure
Portal: App Service → Deployment Center → select a previous deployment →
*Redeploy*. The hand-run `deploy-backend-to-{acc,prod}.sh` scripts still exist
as a break-glass path, but they resolve dependencies on a developer machine
against semver ranges with no lockfile — which is why the
[supply-chain register](../../contributing/supply-chain.md) keeps them as a
named exception rather than treating the workflow as having closed it.

**Static sites** — Azure Static Web Apps keeps deployment history. Azure Portal:
Static Web App → Environments → select a previous deployment → *Promote*.

---

## Related

- [Supply-chain gate](../../contributing/supply-chain.md) — pinning, least privilege,
  and the `audit` gate
- [Testing — Overview](testing/overview.md) — what the suites the pipelines run
  actually cover
