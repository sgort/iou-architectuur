# Standards & Compliance

## Dutch government standards

| Standard | Relevance to RONL Business API |
|---|---|
| **BIO** (Baseline Informatiebeveiliging Overheid) | Overall information security baseline. RONL implements BIO controls including access management (Keycloak RBAC), audit logging (PostgreSQL), and secure transmission (TLS everywhere). |
| **NEN 7510** | Information security in healthcare settings. Applied to the handling of citizen health-related data (zorgtoeslag eligibility). |
| **AVG / GDPR** | Data minimisation (BSN encrypted, not logged in plaintext), audit trail (7-year retention), purpose limitation (process variables scoped to the requesting service). |
| **DigiD Norm** | Authentication assurance levels (LoA) for citizen-facing services. RONL enforces LoA checks on sensitive endpoints via the `loa` JWT claim. |
| **NCSC Beveiligingsrichtlijnen** | Secure software development practices, dependency management, vulnerability disclosure. |

## API design rules

| Rule | Applied in RONL |
|---|---|
| **API-05**: Use nouns for resource names | `/process`, `/decision`, `/health` |
| **API-20**: Major version in URI | `/v1/*` |
| **API-48**: No trailing slashes | Enforced in routing |
| **API-51**: Deprecation signalling | `Deprecation: true` + `Link` header on `/api/*` routes |
| **API-53**: Hide implementation details | Operaton-internal IDs not exposed in responses |
| **API-54**: Plural/singular naming | Collections use plural, single resources use ID |
| **API-57**: Version header in responses | `API-Version: 1.0.0` on all responses |

Reference: [Nederlandse API Strategie](https://docs.geostandaarden.nl/api/API-Strategie/)

## Authentication & identity standards

| Standard | Implementation |
|---|---|
| **OpenID Connect 1.0** | OIDC Authorization Code Flow + PKCE via Keycloak |
| **OAuth 2.0 (RFC 6749)** | Token exchange, scopes, audience validation |
| **JWT (RFC 7519)** | RS256 signed access tokens |
| **JWKS (RFC 7517)** | Public key distribution for JWT validation |
| **SAML 2.0** | DigiD / eHerkenning / eIDAS federation via Keycloak IdP brokering |

## Licences

| Component | Licence |
|---|---|
| RONL Business API | EUPL-1.2 |
| Keycloak | Apache 2.0 |
| Operaton | Apache 2.0 |
| Node.js | MIT |
| Express | MIT |
| React | MIT |
| PostgreSQL | PostgreSQL Licence |
| Redis | BSD 3-Clause |
| Caddy | Apache 2.0 |

All dependencies use government-compatible open source licences. No proprietary software is required.

## External references

- [Nederlandse API Strategie](https://docs.geostandaarden.nl/api/API-Strategie/)
- [BIO — Baseline Informatiebeveiliging Overheid](https://www.digitaleoverheid.nl/overzicht-van-alle-onderwerpen/cybersecurity/bio-en-ensia/)
- [OpenID Connect specification](https://openid.net/connect/)
- [Keycloak 23 documentation](https://www.keycloak.org/docs/23.0/)
- [Operaton documentation](https://docs.operaton.org)
- [EUPL-1.2 licence text](https://eupl.eu/1.2/en/)
