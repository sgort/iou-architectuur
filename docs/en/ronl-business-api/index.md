---
component: RONL Business API
---

# RONL Business API

**Serves as a reference for implementing a compliant, secure, and reliable BPMN service using open-source components.**

🧪 **Current deployment:** [acc.mijn.open-regels.nl](https://acc.mijn.open-regels.nl) — Province of Flevoland, acceptance environment

[![Deployed on Azure Web Apps](https://img.shields.io/badge/Azure-Web_Apps-blue?logo=microsoft-azure)](https://ronl.open-regels.nl)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue?logo=typescript)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-18.2-61dafb?logo=react)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-5.0-646cff?logo=vite)](https://vitejs.dev/)
[![Node.js](https://img.shields.io/badge/Node.js-20-339933?logo=node.js)](https://nodejs.org/)
[![Express](https://img.shields.io/badge/Express-4.18-000000?logo=express)](https://expressjs.com/)
[![Keycloak](https://img.shields.io/badge/Keycloak-23.0-4d4d4d?logo=keycloak)](https://www.keycloak.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis)](https://redis.io/)
[![Operaton](https://img.shields.io/badge/Operaton-BPMN%2FDMN-orange)](https://operaton.open-regels.nl)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)](https://www.docker.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3.4-06B6D4?logo=tailwindcss)](https://tailwindcss.com/)
![License](https://img.shields.io/badge/License-EUPL--1.2-yellow.svg)

---

## What is the RONL Business API?

The **RONL Business API** implements the **Business API Layer** pattern: a security and business-logic layer that sits between an IAM system and the Operaton BPMN engine, exposing scoped capabilities — processes, tasks, forms, decisions — rather than raw engine access.

It is deployed for the **Province of Flevoland**, currently on the acceptance environment. Three surfaces put its capabilities to work: a signed-in **werkomgeving** where provincial staff work through role-scoped boards, a public **knowledge base** reachable with no login, and a public **cockpit demo** running on demonstration data with no backend behind it. See [Getting Started](user-guide/getting-started.md) for how these surfaces are organised, and [Features](features/overview.md) for the capabilities themselves.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: RONL Business API Main UI](../../assets/screenshots/ronl-business-api-main-ui.png)
  <figcaption>Example dashboard MijnOmgeving showing Timeline View</figcaption>
</figure>

---

## What it does

Instead of exposing Operaton's REST API directly to portal frontends, RONL Business API provides:

- Secure OIDC/JWT token validation against Keycloak
- Multi-tenant isolation as a platform mechanism — Operaton native tenant-ids and tenant-scoped queries keep each organisation's data apart, so the same deployment can serve more than one organisation without them seeing each other's data
- Claims mapping from JWT to BPMN process variables
- Role-based authorization (citizen, caseworker, admin)
- Compliance-grade audit logging (BIO, NEN 7510, AVG/GDPR)
- A clean, versioned REST API (`/v1/*`) following the Dutch API Design Rules

---

## Architecture at a glance

```
User → Portal → Keycloak IAM → Business API → Operaton BPMN Engine
```

The system is hosted across two platforms. Azure hosts the stateless application layer (frontend, backend, PostgreSQL, Redis). A VM at `open-regels.nl` hosts the services requiring deep customisation or full control (Keycloak, Operaton, Caddy).

---

## Environments

ACC is the environment of record for this documentation — the Province of Flevoland deployment currently runs there. A production environment is also configured in the codebase's deployment workflows:

| Environment | Frontend | Backend | Keycloak |
|---|---|---|---|
| ACC | https://acc.mijn.open-regels.nl | https://acc.api.open-regels.nl | https://acc.keycloak.open-regels.nl |
| Production | https://mijn.open-regels.nl | https://api.open-regels.nl | https://keycloak.open-regels.nl |

---

## Technology stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite, CSS Custom Properties |
| Backend | Node.js 20, Express 4, TypeScript |
| Authentication | Keycloak 23, OIDC Authorization Code Flow |
| Business rules | Operaton BPMN/DMN engine |
| Database | Azure PostgreSQL Flexible Server (audit logs) |
| Cache | Azure Cache for Redis (JWKS, sessions) |
| Hosting | Azure Static Web Apps (frontend), Azure App Service (backend) |
| IAM/BPMN hosting | VM — Caddy, Docker Compose |
| CI/CD | GitHub Actions |
| License | EUPL-1.2 |

---

## Documentation sections

- [**Features**](features/overview.md) — What RONL Business API does and why
- [**User Guides**](user-guide/getting-started.md) — The werkomgeving's four boards and the public knowledge base
- [**Developer Docs**](developer/local-development.md) — Local setup, backend, frontend, deployment
- [**References**](reference/api-endpoints.md) — API endpoints, environment variables, JWT claims, standards
