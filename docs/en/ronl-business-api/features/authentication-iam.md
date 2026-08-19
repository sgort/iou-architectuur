---
component: RONL Business API
---

# Authentication & IAM

RONL Business API uses **Keycloak** as its identity and access management layer, implementing the OIDC Authorization Code Flow. Every authenticated request carries a JWT access token, and every protected endpoint validates that token before doing anything else.

---

## Authenticating

Keycloak issues tokens along two distinct paths, which converge at the same validation step once a token reaches the Business API:

- A user can sign in directly against Keycloak, with credentials managed in Keycloak itself.
- A user can be authenticated through an external identity provider — DigiD, eHerkenning, or eIDAS — federated by Keycloak acting as an identity broker. The browser is redirected to the chosen provider, the provider returns a signed assertion, and Keycloak validates it and issues a token in exchange, mapping the provider's own attributes onto claims Keycloak controls.

Either way, the caller ends up with a Keycloak-issued JWT access token and presents it on every subsequent request as an `Authorization: Bearer` header.

---

## Validating a token

Every request to a protected endpoint passes through JWT validation before any route handler runs:

1. The `Authorization: Bearer <token>` header is extracted; a missing or malformed header is rejected with `401 MISSING_TOKEN`.
2. The signing key is fetched from Keycloak's JWKS endpoint, matched by the token's `kid`, and cached to avoid a lookup on every request.
3. The signature is verified, and the token's `exp`, `iss`, and `aud` claims are checked against the configured issuer and audience.
4. On success, the decoded claims are attached to the request as the authenticated caller's identity for every downstream check.

A token that fails any of these steps is rejected with `401 INVALID_TOKEN` before it reaches a route handler.

---

## Claims carried in the token

Beyond the standard OIDC claims, a token carries the attributes the platform relies on for authorization: the caller's identity, their tenant, their organisation type, their roles, and — where relevant — a level of assurance reflecting how strongly their identity was established. An optional mandate claim can also express that the caller is acting on someone else's behalf, and where the caller is a member of staff rather than an external user, an employee identifier can be carried as well.

---

## Roles and authorization

A caller's roles are carried in the token and checked against whatever a given endpoint requires: a route can require the caller to hold at least one of a set of roles, and a caller lacking all of them is rejected with `403 FORBIDDEN`. This is the same role-checking mechanism that determines which candidate groups a caller's roles let them see — see [Tasks — Visibility](tasks.md#visibility).

Some operations additionally require a minimum level of assurance, checked against the token's assurance-level claim rather than its roles: evaluating a decision or starting certain processes can require the caller's identity to have been established to at least a given level, rejecting the request with `403 INSUFFICIENT_ASSURANCE` otherwise.

---

## Tenancy

Every authenticated caller carries a tenant identifier and an organisation type as claims in their token. Tenancy is the mechanism, applied consistently, by which the platform scopes what a signed-in caller can reach — it is not a description of any one deployment, and the same underlying mechanism applies whether a given deployment is used by one organisation or by several sharing the platform.

A dedicated tenant-checking step runs after authentication and before a request reaches its handler:

- It requires a tenant identifier to be present in the caller's claims at all, rejecting a token that carries none with `403 MISSING_TENANT`.
- Where a request addresses a resource by an explicit tenant identifier in its path, that identifier is checked against the caller's own tenant, and a mismatch is rejected with `403 TENANT_MISMATCH` — a caller cannot address another tenant's resources by simply naming them.
- When a caller starts a process, their tenant identifier, organisation type, and own identity are attached to the new process instance's variables automatically, and the instance's business key is derived to include the tenant — so every later check against that instance (its status, its variables, its history) traces back to the tenant that started it.

This tenant identifier is a claim the platform itself checks; it is separate from Operaton's own native tenant-id concept, which scopes which *deployment* of a process or decision answers a request rather than which caller may reach it. See [Processes — Tenancy](processes.md#tenancy) for how the two compose: a caller's tenant governs what they are authorized to reach, while a process definition's deployed tenant-id governs which deployment of that process definition actually runs.

---

## Related

- [Tasks](tasks.md) — how a caller's roles determine which candidate groups they belong to, and how tenancy scopes a task list
- [Processes](processes.md) — Operaton's own native tenant-id, and how it composes with a caller's tenant
- [Security & Compliance](security-compliance.md) — how authentication and audit logging fit into the platform's wider security posture
- [API Design](api-design.md) — the versioned surface these checks protect
