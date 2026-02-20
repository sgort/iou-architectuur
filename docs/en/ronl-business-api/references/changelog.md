# Changelog

## v1.0.0 — Initial Release

**Status:** Production  
**Released:** February 2026

### Features

- Secure Business API Layer for Dutch municipality government services
- OIDC Authorization Code Flow + PKCE via Keycloak 23
- Multi-tenant isolation for Utrecht, Amsterdam, Rotterdam, Den Haag
- JWT validation with JWKS caching (Redis)
- Zorgtoeslag calculation via Operaton BPMN/DMN
- Compliance-grade audit logging (PostgreSQL, 7-year retention)
- Rate limiting per IP and per tenant
- Helmet security headers (CSP, HSTS)
- Versioned REST API (`/v1/*`) following Dutch API Design Rules
- Deprecated `/api/*` routes with `Deprecation` headers
- Multi-tenant frontend theming via CSS custom properties
- Dynamic `tenants.json` configuration (no rebuild needed for theme changes)
- GitHub Actions CI/CD for ACC (auto) and PROD (manual approval for backend)
- Hybrid deployment: Azure App Service + Static Web Apps + VM (Keycloak, Operaton, Caddy)

### Supported municipalities

Utrecht, Amsterdam, Rotterdam, Den Haag — each with isolated data, custom theme, role-based access, and dedicated audit logs.

### Technology versions

| Component | Version |
|---|---|
| Node.js | 20 |
| React | 18 |
| TypeScript | 5.3 |
| Keycloak | 23 |
| Express | 4.18 |
| Vite | Latest |
| Caddy | 2 |
| PostgreSQL | 16 |
