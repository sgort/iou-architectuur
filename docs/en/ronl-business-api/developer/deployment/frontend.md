# Frontend Deployment (Azure Static Web Apps)

The frontend deploys to **Azure Static Web Apps** via GitHub Actions. Both ACC and PROD deploy automatically without a manual approval step.

## GitHub Actions workflows

| Workflow file | Trigger | Target | Approval |
|---|---|---|---|
| `.github/workflows/azure-frontend-acc.yml` | Push to `acc` branch with changes in `packages/frontend/**` | ACC Static Web App | Automatic |
| `.github/workflows/azure-frontend-production.yml` | Push to `main` branch with changes in `packages/frontend/**` | PROD Static Web App | Automatic |

Pull request close events trigger the `close_pull_request_job` to clean up ephemeral preview deployments.

## Build and deployment steps

```yaml
1. Checkout code
2. Setup Node.js 20
3. Install dependencies         (npm ci)
4. Build frontend
     ACC:   npm run build:acc   (uses .env.acceptance → acc.api.open-regels.nl)
     PROD:  npm run build:prod  (uses .env.production → api.open-regels.nl)
5. Verify dist/ directory exists and is not empty
6. Deploy to Azure Static Web Apps
     app_location:    /packages/frontend/dist
     skip_app_build:  true       (pre-built, no Azure-side build)
7. Wait 15 seconds
8. Verify deployment (HTTP 200 on the frontend URL)
```

## Environment files

The build step selects the correct `.env` file via Vite's `--mode` flag:

**`.env.acceptance`** (ACC deployment):
```bash
VITE_API_URL=https://acc.api.open-regels.nl/v1
VITE_KEYCLOAK_URL=https://acc.keycloak.open-regels.nl
```

**`.env.production`** (PROD deployment):
```bash
VITE_API_URL=https://api.open-regels.nl/v1
VITE_KEYCLOAK_URL=https://keycloak.open-regels.nl
```

**`.env`** (local development — not deployed):
```bash
VITE_API_URL=http://localhost:3002/v1
VITE_KEYCLOAK_URL=http://localhost:8080
```

## Azure Static Web App configuration

**ACC app name:** `ronl-frontend-acc`  
**PROD app name:** `ronl-frontend-prod`  
**Location:** West Europe  

The apps are configured with custom domains:
- ACC: `acc.mijn.open-regels.nl`
- PROD: `mijn.open-regels.nl`

Azure manages TLS certificates for these domains automatically.

Azure App Settings for the Static Web App (these supplement the baked-in `.env` values and can override them at deploy time):

```bash
az staticwebapp appsettings set \
  --name ronl-frontend-prod \
  --setting-names \
    VITE_API_URL=https://api.open-regels.nl/v1 \
    VITE_KEYCLOAK_URL=https://keycloak.open-regels.nl
```

## GitHub secrets required

The workflows use the following repository secrets:

| Secret | Used by |
|---|---|
| `AZURE_STATIC_WEB_APPS_API_TOKEN_ACC` | ACC frontend workflow |
| `AZURE_STATIC_WEB_APPS_API_TOKEN_PROD` | PROD frontend workflow |

To rotate: Azure Portal → Static Web App → Manage deployment token → Reset, then update the GitHub secret.

## Post-deployment verification

The workflow checks that the deployed frontend is accessible:

```bash
response=$(curl -s -o /dev/null -w "%{http_code}" https://acc.mijn.open-regels.nl)
# Expected: 200
```

## Manual deployment

To deploy without GitHub Actions:

```bash
cd packages/frontend

# Build for ACC
npm run build:acc
# Output: dist/

# Deploy using Azure CLI
az staticwebapp deploy \
  --name ronl-frontend-acc \
  --resource-group rg-ronl-acc \
  --source dist
```

## Keycloak redirect URI

After deploying a new frontend URL (or when adding a new ACC/PROD environment), add the URL to Keycloak's client settings:

Keycloak Admin → `Clients` → `ronl-business-api` → `Settings`:
- **Valid Redirect URIs**: add `https://acc.mijn.open-regels.nl/*`
- **Web Origins**: add `https://acc.mijn.open-regels.nl`

Without this, Keycloak will reject the OIDC callback with an "invalid redirect_uri" error.
