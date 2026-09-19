---
component: Linked Data Explorer
---

# Deployment

The Linked Data Explorer deploys through six GitHub Actions workflows — one per deployable package per environment — with automatic deployment to ACC and a reviewer-approved gate on the production backend. Two further workflows, Semgrep and zizmor, scan the code and the workflows themselves and deploy nothing.

---

## Workflow overview

| Workflow | Trigger | Target | Approval |
|---|---|---|---|
| `azure-frontend-acc.yml` | push to `acc` | Azure Static Web Apps (ACC) | Automatic |
| `azure-frontend-production.yml` | push to `main` | Azure Static Web Apps (production) | Automatic |
| `azure-backend-acc.yml` | push to `acc` | Azure App Service (ACC) | Automatic |
| `azure-backend-production.yml` | push to `main` | Azure App Service (production) | Required reviewer |
| `azure-ropa-site-acc.yml` | push to `acc` | Azure Static Web Apps — public ROPA site (ACC) | Automatic |
| `azure-ropa-site-prod.yml` | push to `main` | Azure Static Web Apps — public ROPA site (production) | Automatic |

The production backend job declares `environment: production`, whose protection rules require a reviewer and restrict the branch. That gate exists because the production backend serves both the production LDE frontend and the production CPSV Editor.

---

## Frontend deployment

The frontend builds to a static site on Node.js 20:

```
git push → GitHub Actions
  npm ci
  lint, typecheck, unit tests
  npm run build:acc   (ACC)   /   npm run build:prod   (production)
  Azure Static Web Apps deployment action
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
git push → GitHub Actions
  npm ci (backend package only)
  lint · lint the OpenAPI description · typecheck · unit tests
  npm run build                        (tsc → dist/)
  prepare the deployment package       (dist/, the SHACL shapes, deploy/build-info.json)
  Azure Web Apps deploy
  health check
  verify v1 endpoints                  (build.sha and shacl.complete — see below)
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
             (auto)      (auto frontend and ROPA site,
                          reviewer-approved backend)
```

All changes go to `acc` first. After acceptance testing, `acc` is promoted to `main` through a pull request. The production backend deployment then waits for a reviewer in the `production` environment.

---

## Post-deployment verification

### What the workflows check

The backend workflows do not stop at a health check, because the health check passes against the **previous** build too — Azure keeps it answering while it starts the new one. After the deploy, *Verify v1 endpoints* reads `/v1/health` up to twelve times, fifteen seconds apart, and passes only when **both** hold:

- `build.sha` equals the commit this run deployed — so a deploy that left the old artifact serving fails instead of passing; and
- `shacl.complete` is `true` — every SHACL shape layer loaded.

Each failed attempt logs the values it read. The window is about three minutes; a 34-second window was measured to give up 14 seconds before a new build came up.

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
