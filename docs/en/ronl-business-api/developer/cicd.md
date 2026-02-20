# CI/CD

RONL Business API uses four GitHub Actions workflows for continuous integration and deployment. All workflows run on `ubuntu-latest`.

## Workflow overview

| File | Branch | Target | Auto-deploy |
|---|---|---|---|
| `azure-backend-acc.yml` | `acc` | Backend ACC (Azure App Service) | Yes |
| `azure-backend-production.yml` | `main` | Backend PROD (Azure App Service) | **No — requires approval** |
| `azure-frontend-acc.yml` | `acc` | Frontend ACC (Azure Static Web Apps) | Yes |
| `azure-frontend-production.yml` | `main` | Frontend PROD (Azure Static Web Apps) | Yes |

## Path filters

Workflows only trigger when relevant files change, avoiding unnecessary deployments:

- Backend workflows: `packages/backend/**`, `packages/shared/**`, or the workflow file itself
- Frontend workflows: `packages/frontend/**`, or the workflow file itself

All workflows also support `workflow_dispatch` for manual triggering.

## Branch strategy

```
feature/*  →  PR  →  acc  →  manual review  →  main
                ↓                                ↓
           ACC deploy                       PROD deploy
         (auto, no approval)         (auto frontend, manual backend)
```

Changes are developed on feature branches, merged to `acc` for acceptance testing, and promoted to `main` for production. The backend PROD deployment has a mandatory manual approval gate to prevent accidental production changes.

## Backend deployment pipeline

```
Push to acc/main
    ↓
npm ci (all workspaces)
    ↓
Build @ronl/shared
    ↓
ESLint (packages/backend)
    ↓
tsc (packages/backend) → dist/
    ↓
Verify dist/index.js exists
    ↓
Prepare deployment package
  (preserve dist/ structure, add shared, production dependencies)
    ↓
[PROD only] Wait for manual approval
    ↓
azure/webapps-deploy@v3
    ↓
Wait 30 seconds
    ↓
Health check: GET /v1/health (5 retries × 10s)
    ↓
Verify /v1/health and /v1/dmns return HTTP 200
```

## Frontend deployment pipeline

```
Push to acc/main
    ↓
npm ci
    ↓
npm run build:acc / build:prod
  (selects .env.acceptance or .env.production)
    ↓
Verify dist/ is not empty
    ↓
Azure/static-web-apps-deploy@v1 (skip_app_build: true)
    ↓
Wait 15 seconds
    ↓
Verify HTTP 200 on frontend URL
```

## Required GitHub secrets

| Secret | Used by |
|---|---|
| `AZURE_WEBAPP_PUBLISH_PROFILE_ACC` | Backend ACC workflow |
| `AZURE_WEBAPP_PUBLISH_PROFILE_PROD` | Backend PROD workflow |
| `AZURE_STATIC_WEB_APPS_API_TOKEN_ACC` | Frontend ACC workflow |
| `AZURE_STATIC_WEB_APPS_API_TOKEN_PROD` | Frontend PROD workflow |

To rotate a publish profile: Azure Portal → App Service → Overview → Get publish profile → download, then update the GitHub secret with the file contents.

## Rolling back a deployment

**Backend** — redeploy the previous commit:
```bash
git revert HEAD
git push origin main    # triggers new deployment
```

Or use the Azure Portal: App Service → Deployment Center → select a previous deployment → Redeploy.

**Frontend** — Azure Static Web Apps keeps deployment history. In the Azure Portal: Static Web App → Environments → select a previous deployment → Promote.
