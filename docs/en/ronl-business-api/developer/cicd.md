---
component: RONL Business API
---

# CI/CD

RONL Business API runs **nine GitHub Actions workflows** on `acc`: an
acceptance/production pair for each of four packages, plus the supply-chain
audit gate. All run on `ubuntu-latest`.

!!! info "This page describes `acc`"
    Verified against `acc` at `1e7fb19` on 29 August 2026. The `main` branch is
    behind: it carries **four** workflows (the backend and frontend pairs) and
    none of the pinning or gating described below. Where the two differ, this
    page says so.

---

## Workflow overview

| File | Trigger | Target | Deploys? |
|---|---|---|---|
| `zizmor.yml` | PR, push to `acc`/`main` | — | No — the `audit` gate |
| `azure-backend-acc.yml` | push to `acc` | — | **No** — builds and uploads an artifact |
| `azure-backend-prod.yml` | push to `main` | — | **No** — builds and uploads an artifact |
| `azure-frontend-acc.yml` | push + PR to `acc` | `acc.mijn.open-regels.nl` | Yes |
| `azure-frontend-prod.yml` | push to `main` | `mijn.open-regels.nl` | Yes |
| `azure-publicsite-acc.yml` | push + PR to `acc` | `acc.publiek.open-regels.nl` | Yes |
| `azure-publicsite-prod.yml` | push to `main` | `publiek.open-regels.nl` | Yes |
| `azure-pa-demo-acc.yml` | push + PR to `acc` | `acc.plato.open-regels.nl` | Yes |
| `azure-pa-demo-prod.yml` | push to `main` | `plato.open-regels.nl` | Yes |

All eight Azure workflows also support `workflow_dispatch`.

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
    the bsdtar bundled at `System32	ar.exe`, because Info-ZIP's `zip` cannot be
    installed on a managed Windows laptop. They also fail fast on a dead Azure
    session rather than part-way through.

---

## What each pipeline runs

Every pipeline that has something to test runs the suite **before** it builds,
and a failing test blocks the deploy.

| Workflow | Lint | Type-check | Tests | Extra gates |
|---|:---:|:---:|:---:|---|
| `azure-backend-*` | ✅ | – | ✅ | Verifies `dist/index.js` exists |
| `azure-frontend-*` | ✅ | – | ✅ | Performance budget, as its own step |
| `azure-publicsite-*` | ✅ | ✅ | ✅ | Prerender + bundle-cleanliness gate, inside the build |
| `azure-pa-demo-*` | ✅ | ✅ | ✅ | **Playwright E2E**, then the bundle gate inside the build |

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

---

## Path filters

Workflows trigger only when relevant files change. The filters are mirrored onto
both `push` and `pull_request`:

| Workflow | Paths |
|---|---|
| `azure-backend-*` | `packages/backend/**`, `packages/shared/**`, own file |
| `azure-frontend-*` | `packages/frontend/**`, `packages/shared/**`, `packages/pa-cockpit/**`, own file |
| `azure-pa-demo-*` | `packages/pa-demo/**`, `packages/shared/**`, `packages/pa-cockpit/**`, own file |
| `azure-publicsite-*` | `packages/public-site/**`, own file |
| `zizmor.yml` | **none, deliberately** — the audit must run on every pull request |

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

The backend workflows carry no concurrency group: they build and upload an
artifact and never reach Azure, so no race exists.

---

## Branch strategy

```
feature/*  →  PR to acc  →  audit + path-matched deploys  →  merge  →  main
                  ↓                                                     ↓
             ACC deploys                                          PROD deploys
```

A pull request is **required** to land on `acc`, and the `audit` check must pass
— a repository ruleset enforces both. A direct push is rejected. Squash and
rebase merging are disabled repo-wide, because changelog entries name commits by
SHA and both alternatives rewrite those hashes.

Releases therefore land through a pull request rather than a local fast-forward.

---

## Pull-request previews

Each preview deploys to its own Static Web Apps staging environment.

!!! warning "A preview cannot reach the backend"
    A preview gets an ephemeral `*.azurestaticapps.net` origin that is not in the
    backend's `CORS_ORIGIN` allowlist, and `VITE_API_URL` is baked in at build
    time. The backend is not deployed per pull request at all — the backend
    workflows have no `pull_request` trigger — so every preview talks to the one
    shared acceptance backend and is refused. **A preview demonstrates that
    static pages render; nothing more.**

There is a three-environment ceiling per app. Before the `pull_request` path
filters were mirrored from the `push` triggers, a one-file change redeployed all
three sites, and five open pull requests exhausted the quota.

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
only to the six jobs that comment on pull requests and `permissions: {}` on the
three that only tear down a preview.

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
