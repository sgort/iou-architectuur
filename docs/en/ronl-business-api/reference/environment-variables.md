---
component: RONL Business API
---

# Environment Variables

---

## Backend — `packages/backend/.env`

### Server

| Variable | Required | Default | Description |
|---|---|---|---|
| `NODE_ENV` | Yes | — | `development`, `acceptance`, or `production` |
| `PORT` | Yes | `3002` | HTTP listen port (Azure uses `8080`) |
| `HOST` | No | `0.0.0.0` | Bind address |

### CORS

| Variable | Required | Description |
|---|---|---|
| `CORS_ORIGIN` | Yes | Comma-separated allowed origins (e.g. `https://mijn.open-regels.nl`), matched by exact equality |
| `CORS_PREVIEW_SLUGS` | No | Comma-separated Static Web Apps **app slugs** whose numbered preview environments may call this backend. Empty by default, and **ignored outright in production** |

!!! note "`CORS_PREVIEW_SLUGS` holds slugs, not hostnames"
    A pull-request preview gets an ephemeral origin, and there is a new one per
    pull request, so it cannot be listed in `CORS_ORIGIN`. Azure derives a
    preview hostname from the app's **stable slug**, so the pattern anchors on
    the slug — a bare `*.azurestaticapps.net` pattern would let any Azure Static
    Web App in the world make credentialed cross-origin requests to the tier.

    Two properties are enforced in code rather than left to configuration. It is
    never honoured in production, so a value that finds its way onto the
    production App Service changes nothing about what production accepts. And
    the guard reads the **deployment** environment, not `NODE_ENV`: acceptance
    deliberately runs `NODE_ENV=production`, so keying on that would have
    treated it as production and refused every preview.

### Keycloak / JWT

| Variable | Required | Description |
|---|---|---|
| `KEYCLOAK_URL` | Yes | Keycloak base URL (e.g. `https://keycloak.open-regels.nl`) |
| `KEYCLOAK_REALM` | Yes | Realm name — always `ronl` |
| `KEYCLOAK_CLIENT_ID` | Yes | Client ID — always `ronl-business-api` |
| `JWT_ISSUER` | Yes | Full issuer URL: `https://keycloak.open-regels.nl/realms/ronl` |
| `JWT_AUDIENCE` | Yes | Must match token `aud` claim — always `ronl-business-api` |
| `TOKEN_CACHE_TTL` | No | `300` | JWKS cache TTL in seconds |

!!! warning "There is no `KEYCLOAK_CLIENT_SECRET`"
    `ronl-business-api` is a **public client**: the realm export gives it
    `publicClient: true`, no secret and no service account. The setting existed
    on `Config` until v2026.09.10, was populated from the environment, was
    required in production — and was read by no code path. Requiring a value
    nobody reads is how the production App Service came to hold the literal
    `not-used`. It was removed rather than corrected.

!!! note "An unfilled value fails the boot in production"
    A non-empty check passes a placeholder, so the backend boots, `/v1/health`
    reports healthy, and the breakage surfaces at first use. Since v2026.09.10 a
    boot-time check rejects an unfilled value in production as well as an empty
    one, and `ANTHROPIC_API_KEY` uses it — that key is genuinely consumed.

    Matching is **anchored, never by substring**: `exchange-mechanism-2026`
    contains `change-me`, and failing a boot over a legitimate secret would be a
    worse failure than the one this prevents. Production only, because failing a
    developer's boot over an unfilled `.env` would be hostile.

### Operaton

| Variable | Required | Description |
|---|---|---|
| `OPERATON_BASE_URL` | Yes | `https://operaton.open-regels.nl/engine-rest` |
| `OPERATON_TIMEOUT` | `30000` | Operaton request timeout in ms |
| `OPERATON_M2M_BASE_URL` | — | Dedicated Operaton `engine-rest` base URL for M2M routes. Defaults to `https://operaton-doc.open-regels.nl/engine-rest` when unset |
| `OPERATON_M2M_USERNAME` | — | Basic auth username for the M2M Operaton instance |
| `OPERATON_M2M_PASSWORD` | — | Basic auth password for the M2M Operaton instance |

### MCP AI Assistant

| Variable            | Required              | Default | Description                                                                 |
|---------------------|-----------------------|---------|-----------------------------------------------------------------------------|
| `MCP_ENABLED`       | No                    | `false` | Enables the MCP client and `POST /v1/mcp/chat`. Must be `true` on ACC/PROD. |
| `MCP_SKIP_HEALTH_CHECK` | No | `false` | Skips provider health checks on startup. Useful when providers start slowly on first deployment. |
| `ANTHROPIC_API_KEY` | Yes | — | Anthropic API key. Required in every environment, whatever `MCP_ENABLED` says: the boot fails without it, and in production also when it is still a placeholder value. |
| `OPENAI_API_KEY` | No | — | Enables `OpenAILlmProvider` and exposes `gpt-4o` and `gpt-4o-mini` in the model selector. Leave unset to use Anthropic only. Requires the `openai` package: `npm install openai --workspace=@ronl/backend`. |
| `TRIPLYDB_MCP_ENABLED` | No | `false` | Enables the TriplyDB Knowledge Graph MCP provider. |
| `TRIPLYDB_ENDPOINT` | Conditional | — | SPARQL endpoint URL. Required when `TRIPLYDB_MCP_ENABLED=true`. Use `https://api.open-regels.triply.cc/datasets/stevengort/RONL/services/RONL/sparql` for the canonical RONL graph. |
| `TRIPLYDB_TOKEN` | No | — | TriplyDB API token. May be empty for public datasets. |
| `CPRMV_MCP_ENABLED` | No | `false` | Enables the CPRMV legislation provider (Dutch and EU law via HTTP MCP). |
| `CPRMV_URL` | No | `https://acc.cprmv.open-regels.nl/mcp` | CPRMV MCP server URL. Override for PROD deployment. |
| `LDE_MCP_ENABLED` | No | `false` | Enables the LDE Process Library provider. Exposes deployed BPMN bundles, form schemas, and document templates to the AI Assistant. |
| `LDE_DATABASE_URL` | Conditional | — | PostgreSQL connection string for the `lde_assets` database. Required when `LDE_MCP_ENABLED=true`. On Azure: use a separate Flexible Server and append `?sslmode=require`. Locally: reuse the existing `ronl-postgres` container. |

> `OPERATON_USERNAME` and `OPERATON_PASSWORD` are also passed to the `operaton-mcp` child process.
> Ensure they are set before enabling MCP.

### Operaton — M2M
 
| Variable | Required | Default | Description |
|---|---|---|---|
| `OPERATON_M2M_BASE_URL` | No | `https://operaton-doc.open-regels.nl/engine-rest` | Base URL for a dedicated Operaton instance used by M2M routes only. The default applies when unset, so M2M routes never fall back to `OPERATON_BASE_URL` |
| `OPERATON_M2M_USERNAME` | No | — | Basic auth username for the M2M Operaton instance |
| `OPERATON_M2M_PASSWORD` | No | — | Basic auth password for the M2M Operaton instance |

### eDOCS
 
| Variable | Required | Default | Description |
|---|---|---|---|
| `EDOCS_BASE_URL` | Yes (live mode) | — | eDOCS REST API base URL, e.g. `https://docuvitt-host/edocsapi/v1.0` |
| `EDOCS_LIBRARY` | Yes (live mode) | `DOCUVITT` | eDOCS library name |
| `EDOCS_USER_ID` | Yes (live mode) | — | eDOCS service account user ID |
| `EDOCS_PASSWORD` | Yes (live mode) | — | eDOCS service account password |
| `EDOCS_STUB_MODE` | No | `true` | When `true`, all eDOCS service methods return realistic fake responses. Set to `false` to enable live calls. Never commit real credentials to the repository — use Azure App Service Application settings. |
 
### GitLab integration

| Variable | Default | Description |
|---|---|---|
| `GITLAB_TOKEN` | — | Personal access token with `api` scope for the GitLab instance |
| `GITLAB_BASE_URL` | `https://git.open-regels.nl` | GitLab instance base URL |
| `GITLAB_PROJECT_PATH` | — | URL-encoded project path (e.g. `showcases%2Fiou-architectuur`) |
| `GITLAB_UC_LABEL` | `uc::submitted` | Label applied to newly created use-case issues |

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
| `RATE_LIMIT_MAX_REQUESTS` | No | `1000` | Max requests per window |
| `RATE_LIMIT_PER_TENANT` | No | `true` | Asks for the limit to be keyed per tenant and IP. **Has no effect**: the limiter runs before any route authenticates the caller, so there is never a tenant to key on and every bucket is per client IP |

!!! note "The limit buckets per client, which is why acceptance could raise it"
    `TRUST_PROXY` is `true` on both deployed tiers, so the limiter buckets per
    client rather than once per deployment. Acceptance runs
    `RATE_LIMIT_MAX_REQUESTS=1000`, raised from 100 so a full end-to-end run
    from one machine stops throttling in the PA cockpit specs, which spend about
    twenty requests per authoring journey.

    **Production should not follow automatically.** Per-client bucketing is what
    makes a raise a convenience decision on acceptance; a tenfold ceiling per
    client is a much weaker defence on a public tier.

### Logging

| Variable | Required | Default | Description |
|---|---|---|---|
| `LOG_LEVEL` | No | `info` | `debug`, `info`, `warn`, `error` |
| `LOG_FORMAT` | No | `json` | `json` (production) or `pretty` (local) |
| `LOG_FILE_ENABLED` | No | `true` | Write logs to rotating files |
| `LOG_FILE_PATH` | No | `./logs` | Log file directory |
| `LOG_FILE_MAX_SIZE` | No | `10m` | Max log file size before rotation |
| `LOG_FILE_MAX_FILES` | No | `7` | Number of rotated log files to keep |

### Audit logging

| Variable | Required | Default | Description |
|---|---|---|---|
| `AUDIT_LOG_ENABLED` | No | `true` | Enable audit log writes |
| `AUDIT_LOG_INCLUDE_IP` | No | `true` | Include client IP in audit records |
| `AUDIT_LOG_RETENTION_DAYS` | No | `2555` | Parsed into `Config` and **read by no code**: nothing purges audit records |

### Security

| Variable | Required | Default | Description |
|---|---|---|---|
| `HELMET_ENABLED` | No | `true` | Enable Helmet security headers |
| `SECURE_COOKIES` | No | `false` | Set Secure flag on cookies (enable in prod) |
| `TRUST_PROXY` | No | `false` | Trust Azure/proxy `X-Forwarded-*` headers (enable in prod) |

### Features

| Variable | Required | Default | Description |
|---|---|---|---|
| `ENABLE_TENANT_ISOLATION` | No | `true` | Switches the tenant middleware's presence check (`403 MISSING_TENANT` for a token without a tenant). It does not switch tenant access: the `TENANT_MISMATCH` checks on process instances and tasks always run |
| `ENABLE_METRICS` | No | `true` | Parsed into `Config` and **read by no code**; no metrics endpoint is served |
| `ENABLE_HEALTH_CHECKS` | No | `true` | Parsed into `Config` and **read by no code**; `/v1/health` is always served |
| `DEFAULT_MAX_PROCESS_INSTANCES` | No | `1000` | Parsed into `Config` and **read by no code**; no per-tenant instance limit is applied |
| `RONL_SPARQL_ENDPOINT` | No | `https://api.triplydb.com/...` | Override the default RONL TriplyDB SPARQL endpoint used by the Regelcatalogus service |

### Media aggregator

The backend both serves a media aggregator at `/v1/media-aggregator` and, for the policy-analysis cockpit, consumes one as a media source. The two halves are configured separately.

| Variable | Required | Default | Description |
|---|---|---|---|
| `MEDIA_SOURCE_ENABLED` | No | `false` | Adds media as a policy-analysis source: curation and searches query the aggregator at `MEDIA_AGGREGATOR_BASE` |
| `MEDIA_AGGREGATOR_BASE` | When `MEDIA_SOURCE_ENABLED=true` | — | Base URL of the aggregator the policy-analysis media source calls (`<base>/search`) |
| `MEDIA_AGGREGATOR_API_KEY` | When the aggregator requires a key | — | Sent as `Authorization: Bearer` by the policy-analysis media source |
| `MEDIA_AGGREGATOR_ACCEPT_KEY` | No | — | Guards `GET /v1/media-aggregator/search`: when set, a caller must send it as a bearer token, and anything else gets `401`; when unset, the endpoint is open. This is the `mediaAggregatorKey` security scheme in the OpenAPI description. Set it to the same value as `MEDIA_AGGREGATOR_API_KEY` when the backend consumes its own aggregator |
| `MEDIA_AGGREGATOR_CACHE_TTL_MS` | No | `900000` | How long the aggregator's in-memory article set is served before a refresh (15 minutes). A missing or non-positive value uses the default |
| `MEDIA_AGGREGATOR_SENTIMENT_ENABLED` | No | — | **Has no effect**: sentiment analysis is not implemented, and every article's sentiment is `null` whatever this says |

### Public surface

| Variable | Required | Default | Description |
|---|---|---|---|
| `PUBLIC_PROCESS_BOARDS` | No | `caseworker` | Comma-separated list of `boardOwner` values whose process bundles are exposed on the public process library and its search. Bundles carrying no owner at all are always public. Widen it (e.g. `caseworker,infra-board`) to publish another board's bundles. A bundle's **status label plays no part in this** — see [Procesbibliotheek](../features/procesbibliotheek.md#public-and-internal-exposure) |

---

## Frontend — `packages/frontend/.env`

| Variable | Required | Description |
|---|---|---|
| `VITE_API_URL` | Yes | Business API base URL (e.g. `https://api.open-regels.nl/v1`) |
| `VITE_KEYCLOAK_URL` | Yes | Keycloak base URL (e.g. `https://keycloak.open-regels.nl`) |
| `VITE_LDE_API_URL` | Yes | LDE public API base URL. Used by `ProcesBibliotheek` to fetch deployed BPMN bundles. ACC: `https://acc.backend.linkeddata.open-regels.nl/v1`. PROD: `https://backend.linkeddata.open-regels.nl/v1`. |

---

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

---

## GitHub repository secrets and variables

The **static sites** deploy with a token, which is a secret:

| Secret name | Where to get it |
|---|---|
| `AZURE_STATIC_WEB_APPS_API_TOKEN_ACC` | Azure Portal → Static Web App ACC → Manage deployment token |
| `AZURE_STATIC_WEB_APPS_API_TOKEN_PROD` | Azure Portal → Static Web App PROD → Manage deployment token |
| `AZURE_STATIC_WEB_APPS_API_TOKEN_PA_DEMO_ACC` / `_PROD` | Azure Portal → the PA-demo Static Web App → Manage deployment token |
| `AZURE_STATIC_WEB_APPS_API_TOKEN_PUBLIC_SITE_ACC` / `_PROD` | Azure Portal → the public-site Static Web App → Manage deployment token |

The **backend** deploys over OIDC and therefore needs no secret at all. What it
reads are repository *variables*:

| Variable name | Value |
|---|---|
| `AZURE_CLIENT_ID_ACC` / `AZURE_CLIENT_ID_PROD` | The app registration with a federated credential for that App Service — one per tier, each scoped to its own |
| `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID` | The tenant and subscription the App Services live in |

!!! warning "`AZURE_WEBAPP_PUBLISH_PROFILE_ACC` / `_PROD` are dead"
    Those secrets date from March 2026 and nothing reads them. **SCM basic auth
    is disabled on both App Services**, so a publish-profile deploy would be
    rejected — which is why the backend authenticates with OIDC instead.

!!! danger "Store a token with `scripts/set-secret.sh`, not by piping"
    Piping a token straight out of the Azure CLI into `gh secret set` stores a
    **trailing newline** — 120 bytes where the key is 119. Both halves are the
    documented way to do their job; the composition is what goes wrong, and it
    cost the public site its first production deploy. The failure named nothing:
    every step passed, then *"An unknown exception has occurred"*.

    A secret's value cannot be read back, so nothing can confirm or deny a stray
    newline afterwards. The script strips whitespace, refuses an empty result,
    and reports the byte count it stored.

---

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
