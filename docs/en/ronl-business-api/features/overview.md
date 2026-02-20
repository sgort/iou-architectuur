# Overview

## The Business API Layer Pattern

RONL Business API implements the **Business API Layer** pattern for government digital services. This pattern provides a secure, audited interface between a municipality's IAM system and the Operaton BPMN engine.

### The challenge

Dutch municipalities need to offer digital services to residents that satisfy:

- **DigiD / eIDAS / eHerkenning** authentication (government-grade security)
- **Multi-tenancy** — each municipality has its own users, data, and branding
- **Compliance** — BIO, NEN 7510, AVG/GDPR requirements
- **Audit logging** — a complete trail of all actions
- **Reliability** — comparable to formally certified government services

### The integration pattern

```
Resident
   ↓
Municipality Portal (MijnOmgeving)
   ↓  (DigiD, eIDAS, eHerkenning)
Keycloak IAM
   ↓  (OIDC / JWT / signed claims)
Business API Layer  ← RONL sits here
   ↓  (authenticated REST)
Operaton BPMN Engine
```

The Business API Layer sits between Keycloak and Operaton, handling all security and business logic before any request reaches the execution engine.

### Why not expose Operaton directly?

Operaton's native REST API does not perform JWT validation, does not enforce multi-tenant isolation, does not emit audit logs in a compliance-grade format, and is not designed for public exposure. Fronting it with RONL Business API addresses all of these concerns without modifying the engine itself.

## Core responsibilities

**Token validation** — validates OIDC/JWT tokens issued by Keycloak, verifying the signature against JWKS, checking expiration, and confirming the audience claim matches `ronl-business-api`.

**Claims mapping** — converts JWT custom claims into Operaton process variables. The claim `municipality` becomes the tenant context; `roles` drives authorization decisions; `loa` (Level of Assurance) gates access to sensitive operations.

**Authorization** — enforces per-municipality access rules and validates that the user's role permits the requested action (e.g. caseworkers can process applications, citizens can only view their own).

**Tenant isolation** — ensures that a caseworker from Utrecht cannot read process instances belonging to Amsterdam. All queries are filtered by the `municipality` claim extracted from the JWT.

**Process invocation** — calls Operaton's REST API with the validated user context injected as process variables, hiding BPMN complexity behind a clean REST interface.

**Audit logging** — writes a tamper-evident audit entry for every API call, recording who performed what action and when. Stored in Azure PostgreSQL with 7-year retention.

**API simplification** — presents a versioned (`/v1/*`) REST API following the Dutch Government API Design Rules (API-05, API-20, API-57), hiding Operaton's internal API structure from municipality frontends.

## Example flow: zorgtoeslag calculation

```
1.  Resident visits https://mijn.open-regels.nl (Utrecht portal)
2.  Frontend detects no valid JWT → redirects to Keycloak
3.  Keycloak authenticates (DigiD simulation) → issues JWT:
      { "municipality": "utrecht", "roles": ["citizen"], "loa": "substantial" }
4.  Frontend submits calculation:
      POST /v1/calculations/zorgtoeslag
      Authorization: Bearer <JWT>
      { "income": 24000, "age": 25, "healthInsurance": true }
5.  Backend validates JWT signature against JWKS endpoint
6.  Maps claims → process variables:
      { "initiator": "user-uuid", "municipality": "utrecht",
        "input": { "inkomenEnVermogen": 24000, "18JaarOfOuder": true, ... } }
7.  Calls Operaton: POST /process-definition/key/zorgtoeslag/start
8.  Operaton executes BPMN workflow and evaluates DMN rules
9.  Backend writes audit log entry
10. Returns to frontend: { "eligible": true, "amount": 1150 }
```

## Open source components

RONL Business API uses exclusively open source components under government-compatible licences.

| Component | Purpose | Licence |
|---|---|---|
| Keycloak 23 | IAM federation | Apache 2.0 |
| Operaton | BPMN/DMN engine | Apache 2.0 |
| Node.js 20 | Backend runtime | MIT |
| Express 4 | Web framework | MIT |
| React 18 | Frontend framework | MIT |
| PostgreSQL 16 | Audit database | PostgreSQL |
| Redis | Session / JWKS cache | BSD 3-Clause |
| Caddy 2 | Reverse proxy | Apache 2.0 |
