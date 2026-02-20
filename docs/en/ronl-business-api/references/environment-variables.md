# Environment Variables

## Backend — `packages/backend/.env`

### Server

| Variable | Required | Default | Description |
|---|---|---|---|
| `NODE_ENV` | Yes | — | `development`, `acceptance`, or `production` |
| `PORT` | Yes | `3002` | HTTP listen port (Azure uses `8080`) |
| `HOST` | Yes | `localhost` | Bind address (`0.0.0.0` on Azure) |

### CORS

| Variable | Required | Description |
|---|---|---|
| `CORS_ORIGIN` | Yes | Comma-separated allowed origins (e.g. `https://mijn.open-regels.nl`) |

### Keycloak / JWT

| Variable | Required | Description |
|---|---|---|
| `KEYCLOAK_URL` | Yes | Keycloak base URL (e.g. `https://keycloak.open-regels.nl`) |
| `KEYCLOAK_REALM` | Yes | Realm name — always `ronl` |
| `KEYCLOAK_CLIENT_ID` | Yes | Client ID — always `ronl-business-api` |
| `KEYCLOAK_CLIENT_SECRET` | Yes (prod) | Client secret from Keycloak |
| `JWT_ISSUER` | Yes | Full issuer URL: `https://keycloak.open-regels.nl/realms/ronl` |
| `JWT_AUDIENCE` | Yes | Must match token `aud` claim — always `ronl-business-api` |
| `TOKEN_CACHE_TTL` | No | `300` | JWKS cache TTL in seconds |

### Operaton

| Variable | Required | Description |
|---|---|---|
| `OPERATON_BASE_URL` | Yes | `https://operaton.open-regels.nl/engine-rest` |
| `OPERATON_TIMEOUT` | No | `30000` | Request timeout in ms |

### Database (PostgreSQL)

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | Full connection string with `?sslmode=require` in production |
| `DATABASE_POOL_MIN` | No | `2` | Minimum pool connections |
| `DATABASE_POOL_MAX` | No | `10` | Maximum pool connections |

### Redis

| Variable | Required | Description |
|---|---|---|
| `REDIS_URL` | Yes | Redis connection string |
| `REDIS_TTL` | No | `3600` | Default key TTL in seconds |

### Rate limiting

| Variable | Required | Default | Description |
|---|---|---|---|
| `RATE_LIMIT_WINDOW_MS` | No | `60000` | Rate limit window in ms |
| `RATE_LIMIT_MAX_REQUESTS` | No | `100` | Max requests per window |
| `RATE_LIMIT_PER_TENANT` | No | `false` | Scope limit per tenant+IP |

### Logging

| Variable | Required | Default | Description |
|---|---|---|---|
| `LOG_LEVEL` | No | `info` | `debug`, `info`, `warn`, `error` |
| `LOG_FORMAT` | No | `json` | `json` (production) or `pretty` (local) |
| `LOG_FILE_ENABLED` | No | `false` | Write logs to file |
| `LOG_FILE_PATH` | No | — | Log file directory |
| `LOG_FILE_MAX_SIZE` | No | `10m` | Max log file size before rotation |
| `LOG_FILE_MAX_FILES` | No | `7` | Number of rotated log files to keep |

### Audit logging

| Variable | Required | Default | Description |
|---|---|---|---|
| `AUDIT_LOG_ENABLED` | No | `true` | Enable audit log writes |
| `AUDIT_LOG_INCLUDE_IP` | No | `true` | Include client IP in audit records |
| `AUDIT_LOG_RETENTION_DAYS` | No | `2555` | Days to retain audit records (7 years) |

### Security

| Variable | Required | Default | Description |
|---|---|---|---|
| `HELMET_ENABLED` | No | `true` | Enable Helmet security headers |
| `SECURE_COOKIES` | No | `false` | Set Secure flag on cookies (enable in prod) |
| `TRUST_PROXY` | No | `false` | Trust Azure/proxy `X-Forwarded-*` headers (enable in prod) |

### Features

| Variable | Required | Default | Description |
|---|---|---|---|
| `ENABLE_SWAGGER` | No | `false` | Enable OpenAPI docs at `/v1/openapi.json` |
| `ENABLE_METRICS` | No | `true` | Enable metrics endpoint |
| `ENABLE_HEALTH_CHECKS` | No | `true` | Enable `/v1/health` endpoint |
| `ENABLE_TENANT_ISOLATION` | No | `true` | Enforce per-tenant data isolation |
| `DEFAULT_MAX_PROCESS_INSTANCES` | No | `1000` | Max active instances per tenant |

## Frontend — `packages/frontend/.env`

| Variable | Required | Description |
|---|---|---|
| `VITE_API_URL` | Yes | Business API base URL (e.g. `https://api.open-regels.nl/v1`) |
| `VITE_KEYCLOAK_URL` | Yes | Keycloak base URL (e.g. `https://keycloak.open-regels.nl`) |

## DNS records

These CNAME records must exist in the `open-regels.nl` DNS zone before deploying:

```
# ACC
acc.api       CNAME   ronl-business-api-acc.azurewebsites.net
acc.mijn      CNAME   <acc-static-web-app>.azurestaticapps.net

# PROD
api           CNAME   ronl-business-api-prod.azurewebsites.net
mijn          CNAME   <prod-static-web-app>.azurestaticapps.net
```

VM subdomains use A records pointing to the VM's public IP:

```
acc.keycloak  A   <VM_IP>
keycloak      A   <VM_IP>
operaton      A   <VM_IP>
```

## GitHub repository secrets

These secrets must be configured in the GitHub repository before any workflow can deploy:

| Secret name | Where to get it |
|---|---|
| `AZURE_WEBAPP_PUBLISH_PROFILE_ACC` | Azure Portal → App Service `ronl-business-api-acc` → Get publish profile |
| `AZURE_WEBAPP_PUBLISH_PROFILE_PROD` | Azure Portal → App Service `ronl-business-api-prod` → Get publish profile |
| `AZURE_STATIC_WEB_APPS_API_TOKEN_ACC` | Azure Portal → Static Web App ACC → Manage deployment token |
| `AZURE_STATIC_WEB_APPS_API_TOKEN_PROD` | Azure Portal → Static Web App PROD → Manage deployment token |

## Generating environment passwords

Save and run this script locally to generate all secrets for an environment:

```bash
#!/bin/bash
set -e

ENV=${1:-acc}   # usage: ./setup-env.sh acc  OR  ./setup-env.sh prod

POSTGRES_PASSWORD=$(openssl rand -base64 32)
KEYCLOAK_PASSWORD=$(openssl rand -base64 32)

mkdir -p ~/.ronl-secrets

cat > ~/.ronl-secrets/${ENV}-passwords.txt << EOF
# RONL ${ENV^^} Environment — Generated: $(date)

PostgreSQL:
  Username: pgadmin
  Password: ${POSTGRES_PASSWORD}

Keycloak Admin:
  Username: admin
  Password: ${KEYCLOAK_PASSWORD}

Connection strings:
  DATABASE_URL: postgresql://pgadmin:${POSTGRES_PASSWORD}@ronl-postgres-${ENV}.postgres.database.azure.com:5432/audit_logs?sslmode=require
  Keycloak VM .env: KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_PASSWORD}
EOF

chmod 600 ~/.ronl-secrets/${ENV}-passwords.txt
echo "Passwords saved to: ~/.ronl-secrets/${ENV}-passwords.txt"
echo "Back this file up securely before proceeding."
```
