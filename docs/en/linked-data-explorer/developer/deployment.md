---
component: Linked Data Explorer
---

# Deployment

The Linked Data Explorer has eleven GitHub Actions workflows. Six deploy — one per deployable package per environment. The three ACC deploys start when a pull request is merged into `acc`; the three production deploys are called, in order, by a seventh, `promote-to-production.yml`, when a promotion is merged into `main`. No deploy waits for a human approval: the gates are the pull request rulesets and the checks each workflow runs. The remaining four deploy nothing — Semgrep and zizmor scan the code and the workflows themselves, `sbom.yml` records the SBOM of each release, and `dependency-audit.yml` audits both branches daily.

---

## Workflow overview

| Workflow | Started by | Target |
|---|---|---|
| `azure-frontend-acc.yml` | push to `acc`, path-filtered; pull requests into `acc` | Azure Static Web Apps (ACC) |
| `azure-backend-acc.yml` | push to `acc`, path-filtered; pull requests into `acc` (build and test, no deploy); manual | Azure App Service (ACC) |
| `azure-ropa-site-acc.yml` | push to `acc`, path-filtered; pull requests into `acc` | Azure Static Web Apps — public ROPA site (ACC) |
| `promote-to-production.yml` | push to `main`, no path filter; manual (`dry_run`) | Calls the three production workflows below, in order |
| `azure-backend-production.yml` | called by the promotion; manual | Azure App Service (production) |
| `azure-frontend-production.yml` | called by the promotion; pull requests into `main` (production preview) | Azure Static Web Apps (production) |
| `azure-ropa-site-prod.yml` | called by the promotion; pull requests into `main` (production preview) | Azure Static Web Apps — public ROPA site (production) |
| `semgrep.yml` | every pull request; push to `acc` and `main` | — (Semgrep Code and Supply Chain, job `scan`) |
| `zizmor.yml` | every pull request; push to `acc` and `main` | — (supply-chain audit, job `audit`) |
| `sbom.yml` | push to `main`; manual; pull requests touching the SBOM tooling | — (release SBOM) |
| `dependency-audit.yml` | daily at 05:17 UTC; manual; pull requests touching the audit | — (audits `acc` and `main`) |

The production backend job declares `environment: production`. Its only protection rule is a branch policy; it has **no required reviewer**. The reviewer was removed on 24 September 2026 ([#210](https://github.com/sgort/linked-data-explorer/issues/210)): it gated the one production deploy that already carried the most automated checks, while both production site workflows deployed with no approval at all. What orders the production deploys now is the promotion itself — see [How a promotion reaches production](#how-a-promotion-reaches-production).

---

## Frontend deployment

The frontend builds to a static site on the Node version pinned in `.nvmrc` (24.21.0), which the workflows read with `node-version-file`:

```
merge into acc (ACC)   /   called by the promotion (production)
  npm ci
  lint, typecheck, unit tests
  npm run build:acc   (ACC)   /   npm run build:prod   (production)
  Azure Static Web Apps deployment action, uploading that build (skip_app_build)
```

The two build commands differ because they inject different `VITE_API_BASE_URL` values through `.env.acceptance` and `.env.production`.

**ACC:** `https://acc.linkeddata.open-regels.nl`
**Production:** `https://linkeddata.open-regels.nl`

### `staticwebapp.config.json` is generated, not committed

The frontend's Static Web Apps configuration is written **at build time** by a Vite plugin, `packages/frontend/vite/cspPlugin.ts`, into the build output — where Azure Static Web Apps reads it. It carries a `Content-Security-Policy-Report-Only` header built from the same `VITE_API_BASE_URL` the application uses, so ACC's policy names the ACC backend in `connect-src` and production's names production's, together with `Reporting-Endpoints`, `X-Content-Type-Options: nosniff` and `Referrer-Policy: strict-origin-when-cross-origin`. A missing or invalid API URL **fails the build** rather than producing a policy that points nowhere.

Violations are reported to `POST /v1/csp-reports` on the same backend, which logs one line per violation — look for `[CSP] violation` in `az webapp log tail` — and stores nothing. The policy is report-only until those reports justify switching it to enforcing.

The only committed `staticwebapp.config.json` is the public ROPA site's, in `packages/ropa-site/`.

---

## Backend deployment

The backend builds TypeScript and runs on Azure App Service (Linux, Node.js 22). Both backend workflows run the same steps:

```
merge into acc (ACC)   /   called by the promotion (production)
  npm ci (backend package only)
  lint · lint the OpenAPI description · typecheck · unit tests
  npm run build                        (tsc → dist/)
  prepare the deployment package       (dist/, the SHACL shapes, deploy/build-info.json)
  Azure Web Apps deploy
  health check
  verify v1 endpoints                  (build, shape layers, OpenAPI version, native binding — see below)
```

**ACC:** `https://acc.backend.linkeddata.open-regels.nl`
**Production:** `https://backend.linkeddata.open-regels.nl`

**The OpenAPI description gates the deploy.** `npm run lint:openapi` builds `openapi/openapi.json` from `openapi/openapi.yaml` and lints it with Spectral against the NL API Design Rules 2.2.1 before anything is built.

**The deployment package carries its own provenance.** The workflow writes `deploy/build-info.json` — the commit SHA, the run number and the run id — into the artifact, and `/v1/health` reports it as a `build` block. `version` and the `API-Version` header still name the release.

**The SHACL shapes ship with the code.** `packages/backend/shapes` is copied into the deployment package; `tsc` emits only `dist/`, so without that copy the validator runs with no shape layers loaded. Until v2026.09.5 only the ACC workflow copied them.

---

## Environment variables (Azure App Service)

Set through the Azure CLI or the Azure portal. **None of these values is recorded in the repository** — there is no infrastructure-as-code for App Service settings, so the portal is the only place the deployed values exist.

**ACC:**

```bash
az webapp config appsettings set \
  --name ronl-linkeddata-backend-acc \
  --resource-group RONL-Preproduction \
  --settings \
    NODE_ENV=acceptance \
    DEPLOYMENT_ENV=acc \
    PORT=8080 \
    CORS_ORIGIN="…" \
    TRIPLYDB_ENDPOINT="https://api.open-regels.triply.cc/..." \
    OPERATON_BASE_URL="https://operaton.open-regels.nl/engine-rest" \
    LOG_LEVEL=info
```

**Production:**

```bash
az webapp config appsettings set \
  --name ronl-linkeddata-backend-prod \
  --resource-group RONL-Production \
  --settings \
    NODE_ENV=production \
    DEPLOYMENT_ENV=prod \
    PORT=8080 \
    CORS_ORIGIN="…" \
    TRIPLYDB_ENDPOINT="https://api.open-regels.triply.cc/..." \
    OPERATON_BASE_URL="https://operaton.open-regels.nl/engine-rest" \
    LOG_LEVEL=info
```

`SCM_DO_BUILD_DURING_DEPLOYMENT=false` must be set on both App Service instances — the build happens in GitHub Actions, not on Azure.

| Variable | Default | Notes |
|---|---|---|
| `DEPLOYMENT_ENV` | falls back to `NODE_ENV` | The tier `/v1/health` and the root page report: `acc` or `prod`. |
| `CORS_ORIGIN` | `http://localhost:3000` | Comma-separated allowlist. **An update replaces the whole value** — see below. |
| `OPERATON_API_KEY` | unset | Carried by the shared Operaton client. Processes deploy only through it, so Operaton credentials never come from a request. |
| `TRIPLYDB_ALLOWED_HOSTS` | `api.open-regels.triply.cc` | Hosts a TriplyDB call that forwards a caller's token may go to; the URL must also be `https:`. |
| `ALLOW_LOCAL_ENDPOINTS` | off | Admits `http:` and local addresses as caller-supplied endpoints. **For local development only**; enabled only by the exact value `true`, and never set on ACC or production. |

!!! danger "`CORS_ORIGIN` replaces, it does not append"
    `az webapp config appsettings set --settings CORS_ORIGIN=…` overwrites the entire list. Retyping it from memory, or running an example with `…` left in, silently drops every origin you did not name — with no error, and no test that would notice. Read the current value first and append to it:

    ```bash
    CUR=$(az webapp config appsettings list -g <rg> -n <app> \
          --query "[?name=='CORS_ORIGIN'].value" -o tsv)
    az webapp config appsettings set -g <rg> -n <app> \
      --settings CORS_ORIGIN="$CUR,https://new.origin.example"
    ```

    The two tiers deliberately allow different origins. Probed on 19 September 2026, production allows its own two frontends — `linkeddata.open-regels.nl` and `cpsv.open-regels.nl` — and nothing else. Acceptance allows `acc.linkeddata.open-regels.nl`, `acc.cpsv.open-regels.nl` and both documentation tiers, `iou-architectuur.open-regels.nl` and `acc.iou-architectuur.open-regels.nl`, which is what lets the [API Specification](../reference/api-specification.md) page send test requests to acceptance and never to production. A disallowed origin gets an ordinary response with no `Access-Control-Allow-Origin` header, which the browser then refuses.

---

## Branch strategy

```
feature/xyz  →  acc  →  main
                 ↓         ↓
               ACC       production
             (each deploy  (one promotion: backend first,
              on its own)   then frontend and ROPA site)
```

All changes go to `acc` first, through a pull request. After acceptance testing, `acc` is promoted to `main` through a pull request, and merging it starts the promotion described below. Both branches change only through a pull request; the rulesets that enforce it are listed under [The rulesets](#the-rulesets).

---

## How a promotion reaches production

`promote-to-production.yml` is the only workflow a push to `main` starts that deploys anything. (Semgrep, zizmor and `sbom.yml` run on the same push; none of them deploys.) It calls the three production deploys as reusable workflows, in this order:

```
changes ──▶ backend ──┬──▶ frontend
                      └──▶ ropa-site
```

Until [#210](https://github.com/sgort/linked-data-explorer/issues/210) each production workflow started itself on a push to `main`, with its own path filter, and the three raced: on the v2026.09.6 promotion the ROPA site finished deploying before the backend had started building.

**Its trigger has no path filter, on purpose.** The workflow is what decides which deploys a promotion needs, so it has to start on every push to `main` — a filter would mean the decision never ran. It can also be dispatched by hand, with a `dry_run` input that **defaults to true**: a dry run reports which deploys would be needed and stops before deploying anything.

**The `changes` job decides.** It first runs `scripts/promotion-targets.test.mjs`, then feeds `git diff --name-only --no-renames` over the pushed commit range to `scripts/promotion-targets.mjs`, which answers `backend`, `frontend` and `ropa_site` with `true` or `false`. `--no-renames` makes a moved file count under both its old and its new name, as GitHub's own path filters do. When the range cannot be read — a manual dispatch, a first push or force-push, or a `before` commit the clone does not have — it runs the script with `--all` and deploys everything. A failure of the `changes` job itself also deploys everything: each deploy runs when `changes` did not succeed, as well as when it said `true`.

**The backend goes first, and alone.** The two sites wait for it, then run in parallel. Each site deploys only when the backend's result is `success` or `skipped` — a positive list, so a cancelled backend stops them too — and its own target is needed. A failed backend stops both sites.

**The path rules live in one place.** `scripts/promotion-targets.mjs` holds the three patterns. The backend's and the frontend's include the root `package.json`, `package-lock.json` and `.nvmrc`; the ROPA site's does not. Changes to the ACC workflows or to the promotion workflow itself deploy nothing. The two production site workflows still carry their own paths on their `pull_request` trigger, and the test's drift guard fails when those lists and the script's patterns stop agreeing.

### The production preview on a promotion pull request

The frontend and ROPA site production workflows keep a `pull_request` trigger on `main`. A promotion pull request therefore builds a preview of the **production** site from `acc`, so the real thing can be looked at before anything is promoted. That preview is not part of the promotion sequence: a different trigger, a different concurrency group, and it runs before the promotion exists.

It was kept deliberately (commit `e14a79a`), with its costs recorded:

- a public URL on the production resource, serving unreleased code, for as long as the pull request is open;
- an environment slot on the production Static Web App;
- teardown depends on `close_pull_request_job`, and GitHub does not run `pull_request` workflows while a pull request has a merge conflict — closing included — so a conflicted pull request that is closed can leave its preview behind.

The **backend is excluded on purpose**: a preview site is a page to look at, while a preview backend on production would be a second live API against production data.

The site jobs are named **Build and Deploy Production Frontend** and **Build and Deploy Production ROPA Site**, distinct from the ACC jobs, because required checks are matched by job name.

### The rulesets

| Ruleset | Branch | Pull request | Required checks |
|---|---|---|---|
| `acc supply-chain gate` | `acc` | required, 0 approvals, merge commits only | `audit`, `scan`, `deploy`, `Build and Deploy Frontend`, `Build and Deploy ROPA Site` |
| `main promotion gate` | `main` | required, 0 approvals, merge commits only | `audit`, `scan` |

Both also block deleting the branch and non-fast-forward pushes.

### Supporting workflows

- **`sbom.yml`** runs on every push to `main`. It generates the CycloneDX SBOM from the lockfile, checks with `--verify-release` that the committed `docs/sbom/` file for the released version exists, and uploads the SBOM as an artifact kept for 90 days. The committed copy is the durable one.
- **`dependency-audit.yml`** runs daily at 05:17 UTC and audits both `acc` and `main`. A high or critical advisory in production dependencies fails it and opens — or updates — a tracking issue, which it closes once the audit is clean.
- **zizmor's lockfile step.** `zizmor.yml` runs `npm ci --dry-run --ignore-scripts`, so a `package-lock.json` that no longer matches `package.json` fails under its own name rather than inside a later install.

### A promotion, as it ran

The v2026.09.8 promotion — run [36255107973](https://github.com/sgort/linked-data-explorer/actions/runs/36255107973), at `4148c9a` on 26 September 2026 — is the sequence working as designed. The `changes` job printed `PASS: 24 checks` for the decision script's test, read 16 changed files, and answered `backend=true`, `frontend=true`, `ropa_site=false`. The backend deployed first (16:20–16:24 UTC), the frontend deployed once it had succeeded (16:24–16:27 UTC), and the ROPA site was skipped.

---

## Post-deployment verification

### What the workflows check

The backend workflows do not stop at a health check, because the health check passes against the **previous** build too — Azure keeps it answering while it starts the new one. After the deploy, *Verify v1 endpoints* asserts, in both the ACC and the production workflow:

- **`build.sha` equals the commit this run deployed** — so a deploy that left the old artifact serving fails instead of passing. `/v1/health` is read up to twelve times, fifteen seconds apart; the window is about three minutes, because a 34-second window was measured to give up 14 seconds before a new build came up.
- **`shacl.complete` is `true`** — every SHACL shape layer loaded. Read in the same loop.
- **`/v1/openapi.json` describes the running release** — its `info.version` equals the `version` `/v1/health` reports, retried up to five times.
- **The libxmljs2 native binding loads on the deployed app.** The step posts a small DMN to `POST /v1/dmns/validate` and fails only when the base layer reports a native-load error — a message matching `NODE_MODULE_VERSION` or `was compiled against` — never because the DMN is invalid. The packaging step already proves the binding loads on the runner; this proves it on the host, where on 23 September 2026 a stale `.node` file broke DMN validation for every user while health, `build.sha` and the shape layers all reported fine.

Each failed attempt logs the values it read. **Every assertion runs.** Since v2026.09.7 a failed check sets `checks_failed` and the step fails at the end, naming each failure, instead of exiting at the first one — on the v2026.09.6 promotion the version comparison failed first, and the native-binding check below it never ran.

### Release checklist

At each release, once both environments are deployed, run these against ACC and production. Each row says what passing looks like.

| Check | Request | Passes when |
|---|---|---|
| Backend health | `GET /v1/health` | `status: healthy`, the release `version`, and a `build` label naming the deployed commit |
| OpenAPI description | `GET /v1/openapi.json` | `info.version` is the release; the path count matches the release notes |
| Outbound guard | `GET /v1/dmns?endpoint=https://169.254.169.254/latest/meta-data/` | `400`, `application/problem+json`, `code: INVALID_INPUT` — an internal address is refused before any request is made |
| Malformed body | `POST /v1/dmns/validate` with the body `{"bad` | `400`, `application/problem+json`, `code: MALFORMED_BODY` |
| CSP collector | `POST /v1/csp-reports`, `Content-Type: application/csp-report` | `204` |
| Frontend policy | response headers of the frontend root | `Content-Security-Policy-Report-Only` present, with `connect-src 'self'` and **that environment's** backend |
| Frontend headers | the same response | `Reporting-Endpoints`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin` |
| DSO paging | `POST /v1/dso/activiteiten/oin?env=prod` with the OIN of Provincie Zuid-Holland, `00000001002306608000` | every page combined — the item count equals `page.totalElements` |
| SPARQL through the backend | `POST /v1/triplydb/query`, `ASK { ?s ?p ?o }` against the RONL endpoint | `{"boolean": true}` |
| Public ROPA | `GET /v1/ropa/public`, and the public ROPA site | `200` for both |
| Asset status | `GET /v1/assets/forms` | no form without a `status` |

The CSP collector check sends one synthetic report, which the backend logs as a violation; give it a `document-uri` that says it is a probe, so the log line cannot be mistaken for a real one.

### v2026.09.5 — measured 19 September 2026, 12:44 UTC

| Check | ACC | Production |
|---|---|---|
| Backend health | healthy · 2026.09.5 · `build 379cbab · #193` | healthy · 2026.09.5 · `build ec4792f · #19` |
| OpenAPI description | 2026.09.5 · 63 paths | 2026.09.5 · 63 paths |
| Outbound guard | `400` problem+json `INVALID_INPUT` | `400` problem+json `INVALID_INPUT` |
| Malformed body | `400` problem+json `MALFORMED_BODY` | `400` problem+json `MALFORMED_BODY` |
| CSP collector | `204` | `204` |
| Frontend policy | report-only · `connect-src 'self' https://acc.backend.linkeddata.open-regels.nl` | report-only · `connect-src 'self' https://backend.linkeddata.open-regels.nl` |
| Frontend headers | present | present |
| DSO paging, Zuid-Holland | 516 of 516 | 516 of 516 |
| SPARQL through the backend | `true` | `true` |
| Public ROPA — endpoint · site | `200` · `200` (`acc.ropa.open-regels.nl`) | `200` · `200` (`ropa.open-regels.nl`) |
| Asset status | 253 forms, none without a status | 42 forms, none without a status |

The asset-status row checks the **outcome** of the v2026.09.5 migration that made `form_schemas.status` and `document_templates.status` `NOT NULL`. The migration itself runs at start-up and cannot be observed from outside; that no row lacks a status can.

v2026.09.5 was also the release that put the outbound guard ([#142](https://github.com/sgort/linked-data-explorer/issues/142)) into production. Before it, the production backend would request any host a caller named.

### v2026.09.8 — the production verify step, 26 September 2026

The release checklist above was not run by hand for v2026.09.8. What is on record is the production backend's own *Verify v1 endpoints* step in the promotion run [36255107973](https://github.com/sgort/linked-data-explorer/actions/runs/36255107973), at `4148c9a`:

| Check | Production |
|---|---|
| Running build | `4148c9a` on the fifth read — the first four, 16:23:19 to 16:24:07 UTC, still returned the previous build, `99e29f9`, with every shape layer loaded |
| SHACL shape layers | all loaded |
| OpenAPI description | `info.version` 2026.09.8, equal to `/v1/health` |
| Native binding | libxmljs2 loads on the deployed app |

The first four reads are the stale window the three-minute loop exists for: the previous build kept answering, and a check that stopped at the health endpoint would have passed against it.
