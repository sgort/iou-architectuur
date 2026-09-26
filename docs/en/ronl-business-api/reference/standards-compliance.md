---
component: RONL Business API
---

# Standards & Compliance

This page maps standards onto what the code does. It is not a certification: nothing here has been audited against these standards, and where the code falls short of a standard's expectation, the gap is stated.

---

## Dutch government standards

| Standard | What the code does |
|---|---|
| **BIO** (Baseline Informatiebeveiliging Overheid) | Access management through Keycloak realm roles and tenant checks on every process instance and task; an audit record of every authenticated request, stored in PostgreSQL; HTTP Strict Transport Security on every response. |
| **NEN 7510** | Listed by the service's root banner among its compliance claims. No control in the code is specific to it. |
| **AVG / GDPR** | Case access is limited to the owning organisation and the case's own applicant, and every authenticated request is audited. Two gaps: the BRP person lookup logs the citizen service number (BSN) in plaintext at `info` level (open issue #241), and its audit entry stores the BSN; and no retention period is applied — nothing purges audit records. |
| **DigiD Norm** | Assurance levels from the token's `loa` claim gate two operations: `basis` for evaluating a decision, `midden` for starting a process. The realm export defines a DigiD SAML broker, disabled, with placeholder endpoints. |
| **NCSC Beveiligingsrichtlijnen** | Supply-chain practice in the pipeline: GitHub Actions pinned to commit digests, a blocking audit gate on every pull request, a daily dependency audit of `acc` and `main`, a fourteen-day cooldown on new dependency versions, Semgrep scanning, and an SBOM committed for every release. |

The root banner's `security.compliance` list (`BIO`, `NEN 7510`, `AVG/GDPR`, `eIDAS`) is a fixed string in the code; nothing checks it.

---

## API design rules

The NL API Design Rules are applied as a Spectral lint of the published description `/v1/openapi.json`, against a vendored copy of the 2.2.1 ruleset, in both backend workflows. Every rule gates except the recorded deviations: `nlgov:semver` is off because releases are CalVer, and the three problem-details rules are off because errors use the API's own `{ success, error }` envelope rather than `application/problem+json`. See [API Design — Published description](../features/api-design.md#published-description).

| Rule | Applied in RONL |
|---|---|
| **API-05**: Use nouns for resource names | `/process`, `/decision`, `/task`, `/health`; actions on a resource are verb sub-paths (`/start`, `/claim`, `/complete`, `/evaluate`) |
| **API-20**: Major version in URI | `/v1/*`; the OpenAPI `servers` entry carries `/v1` |
| **API-48**: No trailing slashes | No documented path ends in a slash, which Spectral checks. Express's default routing still answers a request with a trailing slash |
| **API-51** (`/core/publish-openapi`): Publish an OpenAPI description | `GET /v1/openapi.json` — OpenAPI 3.1, open to every origin, advertised as `documentation` in the root banner |
| **API-53**: Hide implementation details | Operaton's REST API is not exposed directly; the backend serves its own smaller surface. Process instance, definition and task ids are Operaton's own, and a failed process start reports Operaton's error message and the engine URL |
| **API-54**: Plural/singular naming | Not uniform. The execution core is singular (`/v1/process`, `/v1/task`, `/v1/decision`); other mounts use plural collections (`/v1/edocs/documents`, `/v1/pa/dossiers`, `/v1/public/processen`) |
| **API-57**: Version header in responses | `API-Version` on every response, carrying the CalVer release (e.g. `2026.09.12`) |

Reference: [Nederlandse API Strategie](https://docs.geostandaarden.nl/api/API-Strategie/)

---

## Authentication & identity standards

| Standard | Implementation |
|---|---|
| **OpenID Connect 1.0** | OIDC Authorization Code Flow via Keycloak and `keycloak-js`. The frontend does not configure PKCE |
| **OAuth 2.0 (RFC 6749)** | Bearer access tokens; audience validation against `ronl-business-api` |
| **JWT (RFC 7519)** | RS256 signed access tokens; the backend accepts no other algorithm |
| **JWKS (RFC 7517)** | Public key distribution for JWT validation, cached by the backend |
| **SAML 2.0** | The realm export defines DigiD and eIDAS as SAML identity providers for Keycloak brokering, both disabled; it defines no eHerkenning provider |

---

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

The API's own dependencies use government-compatible open source licences. The running service also relies on proprietary services: the backend does not boot without an Anthropic API key, and it is hosted on Azure App Service.

---

## External references

- [Nederlandse API Strategie](https://docs.geostandaarden.nl/api/API-Strategie/)
- [BIO — Baseline Informatiebeveiliging Overheid](https://www.digitaleoverheid.nl/overzicht-van-alle-onderwerpen/cybersecurity/bio-en-ensia/)
- [OpenID Connect specification](https://openid.net/connect/)
- [Keycloak 23 documentation](https://www.keycloak.org/docs/23.0/)
- [Operaton documentation](https://docs.operaton.org)
- [EUPL-1.2 licence text](https://eupl.eu/1.2/en/)
