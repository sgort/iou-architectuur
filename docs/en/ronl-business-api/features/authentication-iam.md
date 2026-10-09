---
component: RONL Business API
---

# Authentication & IAM

RONL Business API uses **Keycloak** as its identity and access management layer, implementing the OIDC Authorization Code Flow. Every authenticated request carries a JWT access token, and every protected endpoint validates that token before doing anything else.

---

## Authenticating

Keycloak is the only token issuer the Business API accepts. The frontend sends the browser to Keycloak's login, with an identity-provider hint when the user chose an external provider on the landing page — **Inloggen met uw Flevoland-account**, which hints Provincie Flevoland's Entra ID, or **Inwoner? Log in met DigiD**. Staff signing in without a provider go to Keycloak's own form:

- A user can sign in directly against Keycloak, with credentials managed in Keycloak itself. This is how every account in the repository's realm export signs in.
- Keycloak can act as an identity broker for an external provider: the browser is redirected to the provider, the provider returns a signed assertion, and Keycloak validates it and issues its own token. Employees of Provincie Flevoland sign in this way through Entra ID (the `entra-flevoland` provider): Keycloak sets their tenant and assurance level and maps their Entra app roles to realm roles — see [Entra ID](../developer/deployment/entra-id.md). The realm export also defines `digid` and `eidas` as SAML providers, both disabled and pointing at placeholder endpoints; it defines no eHerkenning provider. Where the hinted provider is not available, Keycloak shows its own login form.

Either way, the caller ends up with a Keycloak-issued JWT access token and presents it on every subsequent request as an `Authorization: Bearer` header.

---

## Validating a token

Every request to a protected endpoint passes through JWT validation before any route handler runs:

1. The `Authorization: Bearer <token>` header is extracted; a missing or malformed header is rejected with `401 MISSING_TOKEN`.
2. The signing key is fetched from Keycloak's JWKS endpoint, matched by the token's `kid`, and cached to avoid a lookup on every request.
3. The signature is verified (RS256 only), and the token's `exp`, `iss`, and `aud` claims are checked against the configured issuer and audience.
4. On success, the decoded claims are attached to the request as the authenticated caller's identity for every downstream check.

A token that fails any of these steps is rejected with `401 INVALID_TOKEN` before it reaches a route handler.

---

## Claims carried in the token

Beyond the standard OIDC claims, a token carries the attributes the platform relies on for authorization: the caller's identity, their tenant, their organisation type, their realm roles, and a level of assurance reflecting how strongly their identity was established. An optional mandate claim can express that the caller is acting on someone else's behalf, and where the caller is a member of staff, an employee identifier can be carried as well. See [JWT Claims](../reference/jwt-claims.md) for the claim names and the Keycloak mappers that produce them.

---

## Roles and authorization

A caller's roles are read from the token's `realm_access.roles` and checked against whatever a given endpoint requires: a route can require the caller to hold at least one of a set of roles, and a caller lacking all of them is rejected with `403 FORBIDDEN`. The same roles decide which candidate groups a caller's task list covers — see [Tasks — Visibility](tasks.md#visibility).

Two operations additionally require a minimum level of assurance, checked against the token's `loa` claim rather than its roles. The levels are ordered `basis`, `midden`, `substantieel`, `hoog`: evaluating a decision requires at least `basis`, and starting a process at least `midden`. A token below the required level, or carrying no recognised level at all, is rejected with `403 INSUFFICIENT_ASSURANCE`.

---

## Tenancy

Every authenticated caller carries a tenant identifier (the `municipality` claim) and an organisation type in their token. Tenancy decides which organisation's cases a signed-in caller can reach. The same mechanism applies whether a deployment serves one organisation or several.

**The tenant must be present.** On the process, task, decision, capacity, besluitvorming, HR, RIP, ValidSign and policy-analysis routes, a tenant step runs after authentication and rejects a token that carries no tenant identifier with `403 MISSING_TENANT`. `ENABLE_TENANT_ISOLATION=false` switches this presence check off; it does not switch off any of the checks below.

**One label decides access.** Every tenant decision on a process instance or task is made in one module, `auth/tenant-access.ts`, and reads one value: the instance's `municipality` process variable. Operaton's own tenant-id on the deployment is never compared against. The checks fail closed and answer the same way:

- An instance with no `municipality` label is refused to every caller — an instance started outside this backend carries none.
- Every tenant refusal is `403 TENANT_MISMATCH`.

**Starting a process** stamps the label. The backend first resolves which tenant the process is deployed under (see [Processes — Tenancy](processes.md#tenancy)), then applies the start rule:

- Deployed under the caller's own tenant: the case belongs to the caller's tenant.
- Deployed untenanted (or the lookup failed): a member of staff's case belongs to their own tenant; a citizen (holder of the `citizen` realm role) is refused with `403 TENANT_MISMATCH`, since a citizen's case must belong to a tenant.
- Deployed under another tenant, caller is a citizen and the process is a cross-tenant citizen service (see [Processes — Citizen services](processes.md#citizen-services)): the case goes to the deploying tenant, and `originTenantId` records the citizen's own tenant.
- Deployed under another tenant, in any other case: refused with `403 TENANT_MISMATCH`, and no instance is created.

The stamped `municipality` always comes from this rule, never from the request body. The start also records the caller as `applicantId` and `initiator`, with their organisation type and assurance level. The business key is kept as the caller supplied it; otherwise it is minted as `<owning organisation>-<timestamp>`. It grants nothing — access runs on `municipality`.

**Reading and acting on an instance** follows the owning organisation:

- The six process reads — status, variables, historic variables, activity history, lineage and decision document — are allowed to the owning tenant, or to the case's own applicant (the caller whose user id matches `applicantId`). A citizen whose case went to another tenant's deployment can therefore still follow it.
- Cancelling an instance (`DELETE`) and every task operation are allowed to the owning tenant only.

**The label cannot be rewritten.** `municipality`, `originTenantId` and `applicantId` are reserved, and so are `edocsAuthor` and `edocsAuthorName` — the employee whose name background eDOCS archiving records as "namens", which the backend stamps from the caller's token when a member of staff starts a process, completes a task or sends a document for signing (never for a citizen). A user task completion that includes any of the five is refused with `400 RESERVED_VARIABLE` before anything reaches Operaton. A process start through `/v1` drops an `edocsAuthor` or `edocsAuthorName` the body sends and stamps the caller's own, just as it sets `municipality` itself. The machine-to-machine routes under `/v1/m2m` run without the tenant step, but they guard the label too: their task completion refuses the same five variables, and their process start refuses `municipality`, `originTenantId`, `edocsAuthor` and `edocsAuthorName`, all with `400 RESERVED_VARIABLE`. An M2M start may set `applicantId`, since a machine may start a case on a citizen's behalf.

**Only allow-listed clients reach `/v1/m2m`.** Every person in the realm holds a token for the `ronl-business-api` audience, so a valid token proves nothing about the caller being a machine. After token validation, the M2M routes check the token's `azp` — the client it was issued to — against `M2M_ALLOWED_CLIENTS` (default `operaton-mcp-client`). A token from any other client, every person's token included, or one with no `azp` at all, is refused with `403 M2M_CLIENT_NOT_ALLOWED` before any engine call.

**`/v1/edocs` decides who eDOCS sees.** The eDOCS routes tell a machine from a person by the token's `azp`:

- A machine client — any `azp` other than the frontend's — must be on `EDOCS_ALLOWED_CLIENTS` (default `edocs-mcp-client`, `copilot-studio-edocs` and `operaton-mcp-client`) and acts in eDOCS as the service account. Any other client is refused with `403 EDOCS_CLIENT_NOT_ALLOWED`.
- A person — a token issued to the frontend — needs the `caseworker` or `admin` role, or is refused with `403 FORBIDDEN`, and acts in eDOCS as themselves, with the Entra ID token Keycloak brokered when they signed in with their Flevoland account. Without such a token the data routes refuse with `403 EDOCS_USER_TOKEN_UNAVAILABLE`; when it has expired and cannot be renewed, with `401 EDOCS_REAUTH_REQUIRED`, and the person has to sign in with their Flevoland account again. When eDOCS itself refuses the person, the answer is `403 EDOCS_ACCESS_DENIED`.

In stub mode no request reaches eDOCS, and a person is served by the stub as well. `EDOCS_ALLOW_SERVICE_FALLBACK=true` lets a person without an Entra ID token fall back to the service account, logged as an audit event; the backend refuses to start with it in production.

---

## Related

- [Tasks](tasks.md) — how a caller's roles determine which candidate groups they belong to, and how tenancy scopes a task list
- [Processes](processes.md) — which deployment a start resolves to, and how that sets the owning tenant
- [Security & Compliance](security-compliance.md) — how authentication and audit logging fit into the platform's wider security posture
- [API Design](api-design.md) — the versioned surface these checks protect, and its error codes
- [JWT Claims](../reference/jwt-claims.md) — the claims behind the identity, tenant, role and assurance checks
