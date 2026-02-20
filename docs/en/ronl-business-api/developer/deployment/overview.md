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
│    ← Reverse proxy, TLS               │
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
