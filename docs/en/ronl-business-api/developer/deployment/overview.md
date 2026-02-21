# Deployment Overview

RONL Business API uses a **hybrid deployment architecture**: stateless application components run on Azure managed services, while components requiring deep customisation or full control run in Docker on a VM.

## Architecture

```
┌────────────────────────────────────────┐
│           Azure Cloud                  │
│                                        │
│  Static Web App (ACC + PROD)           │
│    ← React frontend                    │
│            ↓                           │
│  App Service (ACC + PROD)              │
│    ← Node.js Business API              │
│            ↓                           │
│  PostgreSQL Flexible Server            │
│    ← Audit logs                        │
│  Azure Cache for Redis                 │
│    ← JWKS cache, sessions              │
└─────────────────┬──────────────────────┘
                  │  JWT validation (HTTPS)
┌─────────────────▼──────────────────────┐
│     VM — open-regels.nl                │
│                                        │
│  Keycloak (ACC + PROD)                 │
│    ← IAM, DigiD federation             │
│  Operaton                              │
│    ← BPMN/DMN engine                   │
│  Caddy                                 │
│    ← Reverse proxy, TLS                │
└────────────────────────────────────────┘
```

## Environments

### ACC (Acceptance)

| Component | URL | Platform |
|---|---|---|
| Frontend | https://acc.mijn.open-regels.nl | Azure Static Web App |
| Backend | https://acc.api.open-regels.nl | Azure App Service |
| Keycloak | https://acc.keycloak.open-regels.nl | VM |
| Operaton | https://operaton.open-regels.nl | VM (shared with PROD) |

### PROD (Production)

| Component | URL | Platform |
|---|---|---|
| Frontend | https://mijn.open-regels.nl | Azure Static Web App |
| Backend | https://api.open-regels.nl | Azure App Service |
| Keycloak | https://keycloak.open-regels.nl | VM |
| Operaton | https://operaton.open-regels.nl | VM (shared with ACC) |

## Why the split?

**VM (full control):**  
Keycloak requires deep customisation for government compliance (DigiD federation, custom JWT mappers, realm import). Operaton is a frequently updated open-source engine where container control simplifies upgrades. Both run in Docker on a VM at approximately €30/month total.

**Azure (managed services):**  
The stateless frontend and backend benefit from auto-scaling, managed TLS, deployment slots, and built-in monitoring. Azure Static Web Apps provides a CDN for the frontend at negligible cost.

## Deployment guides

Each component has its own deployment page:

- [Keycloak (VM)](keycloak.md) — Docker Compose ACC + PROD, realm import
- [Operaton (VM)](operaton.md) — BPMN engine Docker setup
- [Backend (Azure App Service)](backend.md) — GitHub Actions, build process, env config
- [Frontend (Azure Static Web Apps)](frontend.md) — GitHub Actions, env files, deployment
- [Caddy (Reverse Proxy)](caddy.md) — Caddyfile, SSL termination, routing

## Azure resource groups

```
rg-ronl-acc
├── ronl-frontend-acc          (Static Web App)
├── ronl-business-api-acc      (App Service, Node.js 20)
├── ronl-postgres-acc          (PostgreSQL Flexible Server)
└── ronl-redis-acc             (Cache for Redis)

rg-ronl-prod
├── ronl-frontend-prod         (Static Web App)
├── ronl-business-api-prod     (App Service, Node.js 20)
├── ronl-postgres-prod         (PostgreSQL Flexible Server)
└── ronl-redis-prod            (Cache for Redis)
```

## Monitoring

### VM health checks

```bash
# Container resource usage (one-shot)
docker stats --no-stream

# All VM service status
docker ps | grep -E "keycloak|operaton|caddy"

# Service health endpoints (from the VM itself)
curl https://acc.keycloak.open-regels.nl/health/ready
curl https://keycloak.open-regels.nl/health/ready
curl https://operaton.open-regels.nl/

# Follow logs
docker logs keycloak-acc -f
docker logs keycloak-prod -f
docker logs operaton -f
docker logs caddy -f
```

### Azure monitoring

Azure Monitor and Application Insights are available for App Service (backend), PostgreSQL, and Redis. Backend API traces, performance metrics, and error tracking are visible in the Azure Portal under the `rg-ronl-acc` and `rg-ronl-prod` resource groups.

## Disaster recovery

### VM total failure

| Metric | Value |
|---|---|
| RTO (Recovery Time Objective) | 2–4 hours |
| RPO (Recovery Point Objective) | Last backup — max 24 hours |

Recovery steps:

1. Provision a new VM with Docker Engine 24+
2. Clone the repository
3. Deploy Keycloak ACC and PROD from `deployment/vm/keycloak/` (see [Keycloak Deployment](keycloak.md))
4. Restore Keycloak databases from backup:
   ```bash
   cat keycloak-prod-YYYYMMDD.sql | docker exec -i keycloak-postgres-prod psql -U keycloak keycloak
   ```
5. Deploy Caddy and Operaton
6. Update DNS A records if the VM IP has changed
7. Verify all services: `curl https://keycloak.open-regels.nl/health/ready`

### Azure region failure

| Metric | Value |
|---|---|
| RTO | 1–2 hours (with multi-region setup) |
| RPO | Near-zero (continuous replication enabled) |

Recovery steps:

1. Deploy frontend and backend to a different Azure region
2. Restore PostgreSQL from automated backup (point-in-time restore)
3. Update DNS CNAME records to the new Azure endpoints

## VM maintenance

### OS security updates

```bash
sudo apt update
sudo apt upgrade
# If a kernel update was applied:
sudo reboot
```

Schedule during off-peak hours. All Docker services restart automatically after reboot due to `restart: unless-stopped` / `restart: always` policies.

### Updating Keycloak

```bash
# Update the image tag in docker-compose.yml, then:
cd ~/keycloak/acc
docker compose pull
docker compose up -d
docker compose logs -f keycloak-acc   # watch for successful startup

# Repeat for PROD during a maintenance window
cd ~/keycloak/prod
docker compose pull
docker compose up -d
```

### Updating Caddy

```bash
docker pull caddy:2-alpine
docker restart caddy
```

### Keycloak database backups

```bash
# Run daily (add to cron on VM)
docker exec keycloak-postgres-prod pg_dump -U keycloak keycloak \
  > /backup/keycloak-prod-$(date +%Y%m%d).sql

docker exec keycloak-postgres-acc pg_dump -U keycloak keycloak \
  > /backup/keycloak-acc-$(date +%Y%m%d).sql
```

Store backups off-VM (e.g. Azure Blob Storage, 30-day retention policy).

### Volume backup

For a complete binary backup of the PostgreSQL data volume (weekly recommended):

```bash
docker run --rm \
  -v keycloak-prod-db-data:/data \
  -v /backup:/backup \
  alpine tar czf /backup/keycloak-prod-$(date +%Y%m%d).tar.gz /data
```

## VM-level troubleshooting

### Service not accessible from outside the VM

1. Check container is running: `docker ps`
2. Verify service responds locally from the VM: `curl http://localhost:8080`
3. Check Caddy routing: `docker logs caddy | grep <service-name>`
4. Check DNS resolves to the correct IP: `dig acc.keycloak.open-regels.nl`
5. Check firewall: `sudo ufw status` — ports 80 and 443 must be open

### Container shows as unhealthy

```bash
# View logs
docker compose logs <service>

# Check resource usage (CPU/memory)
docker stats <service>

# Restart
docker compose restart <service>
```

### Keycloak database connection failing

```bash
# Check PostgreSQL is accepting connections
docker exec keycloak-postgres-acc pg_isready -U keycloak

# Test TCP connectivity from inside the Keycloak container
docker exec keycloak-acc bash -c \
  'timeout 2 bash -c "</dev/tcp/keycloak-postgres-acc/5432" && echo OK || echo FAILED'
```

## Production security checklist

Before going live, verify:

- ✅ All services are behind Caddy with SSL — no service exposed directly to the internet
- ✅ Strong unique passwords for all admin accounts (different for ACC and PROD)
- ✅ Firewall configured: only ports 80 and 443 open (`ufw status`)
- ✅ Regular OS security updates scheduled
- ⚠️ Enable MFA for the Keycloak admin account
- ⚠️ Switch PROD Keycloak from `start-dev` to `start` (production mode) in `docker-compose.yml`
- ⚠️ Monitor Caddy access logs regularly for anomalous traffic
