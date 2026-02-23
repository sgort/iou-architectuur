# Backend Deployment (Azure App Service)

The backend deploys to **Azure App Service** (Node.js 20) via GitHub Actions. There are two independent deployment targets: ACC and PROD. PROD requires a manual approval step.

## GitHub Actions workflows

| Workflow file | Trigger | Target | Approval |
|---|---|---|---|
| `.github/workflows/azure-backend-acc.yml` | Push to `acc` branch with changes in `packages/backend/**` or `packages/shared/**` | `ronl-business-api-acc` (App Service) | Automatic |
| `.github/workflows/azure-backend-production.yml` | Push to `main` branch (same path filters) or manual `workflow_dispatch` | `ronl-business-api-prod` (App Service) | **Manual required** |

## Build and deployment steps

Both workflows follow the same build process:

```yaml
1. Checkout code
2. Setup Node.js 20
3. npm ci                          (install all workspace dependencies)
4. Build shared package            (npm run build --workspace=@ronl/shared)
5. Lint backend                    (npm run lint in packages/backend)
6. Build TypeScript                (npm run build in packages/backend → dist/)
7. Verify dist/index.js exists
8. Prepare deployment package:
     deploy/
       dist/                       (compiled TypeScript, structure preserved)
       package.json                (backend package.json at deploy root)
       node_modules/@ronl/shared/  (shared package dist + package.json)
       node_modules/               (production dependencies only)
       .deployment                 (SCM_DO_BUILD_DURING_DEPLOYMENT=false)
9. Deploy to Azure Web App         (azure/webapps-deploy@v3, package: ./packages/backend/deploy)
10. Wait 30 seconds
11. Health check with 5 retries (10-second intervals) → GET /v1/health
12. Verify /v1/health and /v1/dmns return HTTP 200
```

!!! warning "Deployment package structure"
    The `dist/` folder must be copied as a folder (`cp -r dist deploy/`), not flattened (`cp -r dist/* deploy/`). Flattening breaks TypeScript module resolution paths and causes 404 errors on all `/v1/*` endpoints after deployment.

## Azure App Service configuration

**App name:** `ronl-business-api-acc` / `ronl-business-api-prod`  
**Runtime:** Node.js 20  
**Startup command:** `node dist/index.js`

Azure App Settings (environment variables) are configured via CLI or the Azure Portal. Set the production values from `docs/deployment/environment-variables.md`:

```bash
az webapp config appsettings set \
  --name ronl-business-api-prod \
  --resource-group rg-ronl-prod \
  --settings \
    NODE_ENV=production \
    PORT=8080 \
    KEYCLOAK_URL=https://keycloak.open-regels.nl \
    KEYCLOAK_REALM=ronl \
    KEYCLOAK_CLIENT_ID=ronl-business-api \
    KEYCLOAK_CLIENT_SECRET=<secret> \
    JWT_ISSUER=https://keycloak.open-regels.nl/realms/ronl \
    JWT_AUDIENCE=ronl-business-api \
    CORS_ORIGIN=https://mijn.open-regels.nl \
    OPERATON_BASE_URL=https://operaton.open-regels.nl/engine-rest \
    DATABASE_URL="postgresql://pgadmin:<password>@ronl-postgres-prod.postgres.database.azure.com:5432/audit_logs?sslmode=require" \
    REDIS_URL="redis://ronl-redis-prod.redis.cache.windows.net:6380?password=<key>&ssl=true" \
    LOG_LEVEL=info \
    HELMET_ENABLED=true \
    SECURE_COOKIES=true \
    TRUST_PROXY=true \
    AUDIT_LOG_ENABLED=true \
    ENABLE_TENANT_ISOLATION=true
```

The full variable reference is in [Environment Variables](../../references/environment-variables.md).

Complete command for **ACC** (all 30+ variables in one call):

```bash
az webapp config appsettings set \
  --name ronl-business-api-acc \
  --resource-group rg-ronl-acc \
  --settings \
    NODE_ENV=production \
    PORT=8080 \
    HOST=0.0.0.0 \
    CORS_ORIGIN="https://acc.mijn.open-regels.nl" \
    KEYCLOAK_URL="https://acc.keycloak.open-regels.nl" \
    KEYCLOAK_REALM="ronl" \
    KEYCLOAK_CLIENT_ID="ronl-business-api" \
    KEYCLOAK_CLIENT_SECRET="<YOUR_CLIENT_SECRET>" \
    JWT_ISSUER="https://acc.keycloak.open-regels.nl/realms/ronl" \
    JWT_AUDIENCE="ronl-business-api" \
    TOKEN_CACHE_TTL="300" \
    OPERATON_BASE_URL="https://operaton.open-regels.nl/engine-rest" \
    OPERATON_TIMEOUT="30000" \
    DATABASE_URL="postgresql://pgadmin:<PASSWORD>@ronl-postgres-acc.postgres.database.azure.com:5432/audit_logs?sslmode=require" \
    DATABASE_POOL_MIN="2" \
    DATABASE_POOL_MAX="10" \
    REDIS_URL="redis://ronl-redis-acc.redis.cache.windows.net:6380?password=<PRIMARY_KEY>&ssl=true" \
    REDIS_TTL="3600" \
    RATE_LIMIT_WINDOW_MS="60000" \
    RATE_LIMIT_MAX_REQUESTS="100" \
    RATE_LIMIT_PER_TENANT="true" \
    LOG_LEVEL="info" \
    LOG_FORMAT="json" \
    LOG_FILE_ENABLED="true" \
    LOG_FILE_PATH="/home/site/wwwroot/logs" \
    LOG_FILE_MAX_SIZE="10m" \
    LOG_FILE_MAX_FILES="7" \
    AUDIT_LOG_ENABLED="true" \
    AUDIT_LOG_INCLUDE_IP="true" \
    AUDIT_LOG_RETENTION_DAYS="2555" \
    HELMET_ENABLED="true" \
    SECURE_COOKIES="true" \
    TRUST_PROXY="true" \
    ENABLE_SWAGGER="false" \
    ENABLE_METRICS="true" \
    ENABLE_HEALTH_CHECKS="true" \
    ENABLE_TENANT_ISOLATION="true" \
    DEFAULT_MAX_PROCESS_INSTANCES="1000"
```

For PROD, substitute `ronl-business-api-acc` → `ronl-business-api-prod`, `rg-ronl-acc` → `rg-ronl-prod`, and the ACC URLs → PROD URLs.

## Approving a PROD deployment

When a push to `main` triggers the production workflow:

1. The build and lint steps run automatically
2. The workflow pauses at the `deploy` job waiting for approval
3. Go to **GitHub → Actions → the running workflow → Review deployments**
4. Select the `production` environment → **Approve and deploy**

## Post-deployment health check

The workflow automatically verifies the deployment:

```bash
# Retries up to 5 times with 10-second intervals
curl -s -o /dev/null -w "%{http_code}" https://api.open-regels.nl/v1/health
# Expected: 200
```

If the health check fails after 5 attempts, the workflow fails and the deployment is marked unsuccessful. Roll back by redeploying the previous commit or using an Azure deployment slot swap.

## Manual deployment

To deploy without GitHub Actions (emergency or first-time setup):

```bash
# Prepare package (same structure as CI)

# From project root
cd packages/shared
npm run build
cd ../backend

# Build backend
npm run build

# Prepare deployment package
mkdir -p deploy
cp -r dist deploy/
cp package.json deploy/

# Copy shared package
mkdir -p deploy/node_modules/@ronl
cp -r ../shared/dist deploy/node_modules/@ronl/shared
cp ../shared/package.json deploy/node_modules/@ronl/shared/

# Install production dependencies
cd deploy && npm install --production --omit=dev && cd ..

# Create zip file
cd deploy
zip -r ../deployment-acc.zip .
cd ..

# Deploy using Azure CLI
az webapp deploy \
  --name ronl-business-api-acc \
  --resource-group rg-ronl-acc \
  --src-path deployment-acc.zip \
  --type zip

# Cleanup
rm -rf deploy
rm deployment-acc.zip
```
