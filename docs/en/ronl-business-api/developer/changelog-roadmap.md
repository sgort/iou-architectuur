# Changelog & Roadmap

---

## Changelog

### Frontend — v2.0.1 — Feature Release (February 27, 2026)

**Caseworker login** 🏢

Added a dedicated caseworker login path to the MijnOmgeving landing page. A slate-coloured "Inloggen als Medewerker" button, visually separated from the three citizen IdP options by a "MEDEWERKERS" section divider, initiates the new flow. `AuthCallback` uses `check-sso` instead of `login-required`, so caseworkers with an active Keycloak SSO session bypass the login screen on subsequent visits. When a new session is required, `keycloak.login({ loginHint: '__medewerker__' })` redirects to Keycloak, where the custom `login.ftl` theme detects the sentinel and renders an indigo "Inloggen als gemeentemedewerker" context banner with "Medewerker portaal" as the page title.

### Frontend — v2.0.0 — Major Release (February 2026)

**Frontend Redesign** 🎨

- New landing page with identity provider selection (DigiD / eHerkenning / eIDAS)
- Custom Keycloak theme matching MijnOmgeving design
- Blue gradient header with rounded modern inputs
- Multi-tenant theming with CSS custom properties for runtime theme switching
- Dutch language support throughout authentication flow
- Mobile-responsive design for all screen sizes

**Authentication Flow** 🔐

- Identity Provider selection before Keycloak authentication
- DigiD, eHerkenning, and eIDAS support (infrastructure ready)
- Seamless redirect flow with `idpHint` parameter
- Session storage for IDP selection persistence
- Enhanced error handling and user feedback

**Infrastructure** 🏗️

- Azure Static Web Apps deployment with SPA fallback routing
- Custom Keycloak theme deployment to VM
- Theme volume mounting for ACC and PROD environments
- Version-controlled deployment configurations
- Manual deployment process for VM-hosted services

---

### Frontend — v1.5.0 — Feature Release (February 2026)

**Multi-Tenant Support** 🏛️

- Four municipalities supported: Utrecht, Amsterdam, Rotterdam, Den Haag
- Municipality-specific theming with custom colours and logos
- Tenant configuration via JSON for runtime theme switching
- Municipality claim in JWT tokens for backend tenant isolation
- Test users for each municipality with proper attributes

**Zorgtoeslag Calculator** 💰

- DMN-based zorgtoeslag (healthcare allowance) calculation
- Integration with Operaton BPMN/DMN engine
- Business rules evaluation via REST API
- Result display with matched rules and annotations
- Support for multiple requirement checks and income thresholds

**Security & Compliance** 🔒

- JWT audience validation for API security
- Role-based access control (citizen, caseworker, admin)
- Assurance level (LoA) claims for DigiD compliance
- Audit logging with 7-year retention
- BIO (Baseline Information Security) compliance ready

---

### Backend / Frontend — v1.0.0 — Initial Release (January–February 2026)

**Status:** Production  
**Released:** February 2026

**Backend Core**

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

**Frontend Core** 🏗️

- Monorepo structure with frontend, backend, and shared packages
- React 18 + TypeScript frontend with Vite build
- Express + TypeScript backend with PostgreSQL
- Keycloak 23.0 for authentication and authorisation
- Operaton integration for BPMN/DMN execution

**Deployment** 🚀

- Azure Static Web Apps for frontend (ACC + PROD)
- Azure App Service for backend API
- VM-hosted Keycloak with separate ACC/PROD instances
- Caddy reverse proxy for SSL termination
- GitHub Actions for automated deployments
- Multi-tenant frontend theming via CSS custom properties
- Dynamic `tenants.json` configuration (no rebuild needed for theme changes)

**Supported municipalities**

Utrecht, Amsterdam, Rotterdam, Den Haag — each with isolated data, custom theme, role-based access, and dedicated audit logs.

**Technology versions**

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

---

## Roadmap

### Completed

| Feature | Version |
|---|---|
| Monorepo core architecture | v1.0.0 |
| Multi-tenant municipality support | v1.5.0 |
| Zorgtoeslag DMN calculator | v1.5.0 |
| IDP selection landing page | v2.0.0 |
| Custom Keycloak MijnOmgeving theme | v2.0.0 |
| DigiD / eHerkenning / eIDAS infrastructure | v2.0.0 |
| Caseworker login with SSO session reuse | v2.0.1 |

---

### Planned

**Phase 2 — Identity Provider Activation (2026 Q2)**

Live DigiD integration with BSN-based citizen authentication. eHerkenning activation for business users. eIDAS support for EU residents. Full SAML federation with Dutch government identity infrastructure.

**Phase 3 — Extended Business Rules (2026 Q2–Q3)**

Additional DMN-based benefit calculations beyond zorgtoeslag. Parameterised rule sets loaded from TriplyDB. Integration with CPSV Editor published service definitions. Case management workflow with caseworker assignment and review.

**Phase 4 — BRP Integration (2026 Q3)**

Real-time citizen data retrieval from BRP (Basisregistratie Personen). Pre-populated forms using authenticated citizen profile. Timeline navigation for historische persoonsgegevens.

**Phase 5 — Audit & Compliance Dashboard (2026 Q4)**

Real-time audit log viewer for municipality administrators. Compliance reporting against BIO baseline. DPIA (Data Protection Impact Assessment) evidence export. Role-based access management UI.
