# Security & Compliance

RONL Business API is designed to meet Dutch government security requirements. The following standards inform the security architecture and audit requirements.

## Applicable standards

| Standard | Scope |
|---|---|
| **BIO** (Baseline Informatiebeveiliging Overheid) | Overall information security baseline for Dutch government |
| **NEN 7510** | Information security in healthcare; applied here for sensitive citizen data |
| **AVG / GDPR** | Data minimisation, audit trails, retention periods, right to access |
| **DigiD Norm** | Authentication assurance levels for citizen-facing services |
| **NCSC Guidelines** | Secure software development, dependency management |

## Security controls

### HTTPS everywhere

All traffic between components is encrypted. Caddy (the VM reverse proxy) handles TLS termination for Keycloak and Operaton using automatically-renewed Let's Encrypt certificates. Azure manages certificates for the Static Web App and App Service.

### Helmet middleware

The backend applies `helmet` with a strict Content Security Policy:

```
defaultSrc: ["'self'"]
styleSrc:   ["'self'", "'unsafe-inline'"]
scriptSrc:  ["'self'"]
imgSrc:     ["'self'", "data:", "https:"]
```

HSTS is enabled with `maxAge: 31536000` and `includeSubDomains: true`.

### Rate limiting

Two rate limit policies are applied:

- **General API** — 100 requests per 15 minutes per IP (or per tenant+IP if `RATE_LIMIT_PER_TENANT=true`)
- **Authentication endpoints** — 5 requests per 15 minutes per IP

Keycloak adds brute-force protection independently: 5 failed login attempts trigger a 15-minute lockout with exponential backoff.

### CORS

The backend only accepts requests from its configured `CORS_ORIGIN` values:

```
https://mijn.open-regels.nl          (production)
https://acc.mijn.open-regels.nl      (acceptance)
http://localhost:5173                 (local development)
```

All other origins receive HTTP 403. Keycloak client settings mirror these origins in `Web Origins` and `Valid Redirect URIs`.

### JWT validation

Every request to a protected endpoint passes through the JWT middleware:

1. Signature verified against Keycloak JWKS (cached in Redis, TTL 300s)
2. `exp` checked — 15-minute token lifetime enforced
3. `iss` verified against the configured Keycloak realm URL
4. `aud` verified to be `ronl-business-api`

Tokens failing any check are rejected with HTTP 401. No request data is processed before successful validation.

### Secrets management

Secrets are stored as Azure App Settings (environment variables on App Service) and VM `.env` files (not committed to git). The repository contains only `.env.example` templates. The following are never in version control:

- Keycloak client secrets
- Database connection strings with passwords
- Redis primary keys
- Admin passwords

## Audit logging

Every API call that results in a process action is written to the PostgreSQL audit log with:

| Field | Value |
|---|---|
| `user_id` | JWT `sub` claim |
| `municipality` | JWT `municipality` claim |
| `action` | HTTP method + endpoint |
| `resource_id` | Process instance ID |
| `timestamp` | UTC timestamp |
| `ip_address` | Client IP (from trusted proxy headers) |
| `result` | HTTP response code |

Audit records have a configured retention of 2555 days (7 years) to satisfy BIO and AVG archiving requirements. The table schema is initialised by `config/postgres/init-databases.sql`.

## Data minimisation

The Business API applies AVG data minimisation:

- BSN (Citizen Service Number) is encrypted at rest and never logged in plaintext
- The `userinfo_endpoint` is not exposed externally
- Process variables containing personal data are not included in error responses
- Log entries at DEBUG level are disabled in production (`LOG_LEVEL=info`)
