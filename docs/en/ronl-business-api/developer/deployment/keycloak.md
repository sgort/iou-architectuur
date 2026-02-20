# Keycloak Deployment (VM)

Keycloak runs in Docker on the VM (`open-regels.nl`). Two fully isolated instances run in parallel: ACC and PROD. Each has its own PostgreSQL database container.

## Repository structure

```
ronl-business-api/
├── deployment/vm/keycloak/
│   ├── acc/
│   │   ├── docker-compose.yml      # ACC configuration
│   │   └── .env.example            # ACC environment template
│   └── prod/
│       ├── docker-compose.yml      # PROD configuration
│       └── .env.example            # PROD environment template
└── config/keycloak/
    └── ronl-realm.json             # Realm configuration (users, clients, mappers)
```

## Prerequisites

On the VM (Ubuntu 24.04 LTS):

- Docker Engine 24+
- Docker Compose 2.x
- Domain `open-regels.nl` with DNS configured
- Ports 80 and 443 open
- Caddy running (see [Caddy Deployment](caddy.md))

## Deploying to ACC

**Step 1 — Copy files to VM:**

```bash
scp deployment/vm/keycloak/acc/docker-compose.yml user@open-regels.nl:~/keycloak/acc/
scp config/keycloak/ronl-realm.json user@open-regels.nl:~/keycloak/acc/
```

**Step 2 — Create the `.env` file on the VM:**

```bash
ssh user@open-regels.nl
cd ~/keycloak/acc
cp .env.example .env
nano .env   # set strong passwords
```

Required variables:

```bash
KEYCLOAK_ADMIN=admin
KEYCLOAK_ADMIN_PASSWORD=<strong-password>
KC_DB_PASSWORD=<strong-db-password>
KC_HOSTNAME=acc.keycloak.open-regels.nl
```

**Step 3 — Start Keycloak ACC:**

```bash
docker compose up -d
```

**Step 4 — Verify:**

```bash
curl https://acc.keycloak.open-regels.nl/health/ready
# Expected: {"status":"UP"}

curl https://acc.keycloak.open-regels.nl/realms/ronl/.well-known/openid-configuration
# Expected: JSON with endpoints
```

## Deploying to PROD

Same steps using `deployment/vm/keycloak/prod/` and hostname `keycloak.open-regels.nl`. The PROD realm import uses the same `config/keycloak/ronl-realm.json` but PROD test users should be removed before going live.

## Realm import

The `ronl-realm.json` is imported on the first container start via the `KEYCLOAK_IMPORT` environment variable in `docker-compose.yml`. It configures:

- Realm `ronl` with brute-force protection
- Client `ronl-business-api` with PKCE and CORS settings
- Protocol mappers: `municipality` (user attribute), `roles` (realm roles), `loa` (user attribute)
- Test users with per-municipality attributes
- Token lifespans: access token 15 min, SSO session 30 min

To re-import the realm after changes:

```bash
docker exec keycloak-acc /opt/keycloak/bin/kc.sh import \
  --file /opt/keycloak/data/import/ronl-realm.json \
  --override true
```

## Backup

```bash
# Daily backup of PROD Keycloak database
docker exec keycloak-postgres-prod pg_dump -U keycloak keycloak \
  > /backup/keycloak-prod-$(date +%Y%m%d).sql
```

Store backups off-VM (e.g. Azure Blob Storage with a 30-day retention policy).

## Updating Keycloak

```bash
# Update docker-compose.yml image tag, then:
docker compose pull
docker compose up -d
docker compose logs -f keycloak-acc   # verify startup
```

## Connecting the backend

After deployment, set these in `packages/backend/.env.production` (or Azure App Settings):

```bash
KEYCLOAK_URL=https://keycloak.open-regels.nl
KEYCLOAK_REALM=ronl
KEYCLOAK_CLIENT_ID=ronl-business-api
JWT_ISSUER=https://keycloak.open-regels.nl/realms/ronl
JWT_AUDIENCE=ronl-business-api
```
