# Deployment

The Linked Data Explorer uses four GitHub Actions workflows — one per package per environment — with automatic deployment to ACC and manually approved deployment to production.

---

## Workflow overview

| Workflow | Trigger | Target | Approval |
|---|---|---|---|
| `azure-frontend-acc.yml` | push to `acc` | Azure Static Web Apps (ACC) | Automatic |
| `azure-frontend-production.yml` | push to `main` | Azure Static Web Apps (production) | Automatic |
| `azure-backend-acc.yml` | push to `acc` | Azure App Service (ACC) | Automatic |
| `azure-backend-production.yml` | push to `main` | Azure App Service (production) | Manual |

The manual approval gate on the production backend prevents accidental breakage of the service used by both the ACC CPSV Editor and the production LDE frontend.

---

## Frontend deployment

The frontend builds to a static site. The workflow:

```
git push → GitHub Actions
  npm ci
  npm run build:acc     (ACC) / npm run build (production)
  Azure Static Web Apps deployment action
  Health check
```

Build commands differ by environment because they inject different `VITE_API_BASE_URL` values via `.env.acceptance` and `.env.production`.

**ACC:** `https://acc.linkeddata.open-regels.nl`
**Production:** `https://linkeddata.open-regels.nl`

Azure Static Web Apps routing is configured in `staticwebapp.config.json` at the repo root, handling SPA fallback and CORS headers for the static assets.

---

## Backend deployment

The backend builds TypeScript and runs on Azure App Service (Linux, Node.js 22).

```
git push → GitHub Actions
  npm ci (backend package only)
  npm run build     (tsc → dist/)
  Azure Web Apps Deploy action
  POST-deployment: GET /v1/health → assert status "healthy"
```

**ACC:** `https://acc.backend.linkeddata.open-regels.nl`
**Production:** `https://backend.linkeddata.open-regels.nl`

---

## Environment variables (Azure App Service)

Set via Azure CLI or the Azure portal. Key variables for each environment:

**ACC:**

```bash
az webapp config appsettings set \
  --name ronl-linkeddata-backend-acc \
  --resource-group RONL-Preproduction \
  --settings \
    NODE_ENV=acceptance \
    PORT=8080 \
    CORS_ORIGIN="https://acc.linkeddata.open-regels.nl,https://acc.cpsv-editor.open-regels.nl" \
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
    PORT=8080 \
    CORS_ORIGIN="https://linkeddata.open-regels.nl,https://cpsv-editor.open-regels.nl" \
    TRIPLYDB_ENDPOINT="https://api.open-regels.triply.cc/..." \
    OPERATON_BASE_URL="https://operaton.open-regels.nl/engine-rest" \
    LOG_LEVEL=info
```

`SCM_DO_BUILD_DURING_DEPLOYMENT=false` must be set on both App Service instances — the build happens in GitHub Actions, not on Azure.

---

## Branch strategy

```
feature/xyz  →  acc  →  main
                 ↓         ↓
               ACC       production
             (auto)      (auto frontend,
                          manual backend)
```

All changes go to `acc` first. After acceptance testing, merge `acc` → `main` via a pull request. The production backend deployment then requires manual approval in the GitHub Actions workflow.

---

## Post-deployment verification

After any deployment, verify:

```bash
# Backend health
curl https://backend.linkeddata.open-regels.nl/v1/health

# Frontend loads
# Open https://linkeddata.open-regels.nl in browser
# Check Chain Builder loads DMNs
# Check no CORS errors in browser console
```
