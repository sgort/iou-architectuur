# Operaton Access Patterns

This page documents the three distinct ways to access Operaton within the RONL ecosystem. Each pattern targets a different caller, speaks a different protocol contract, and requires a different authentication strategy. Choosing the wrong pattern is the most common source of integration errors.

---

## Overview
```
┌─────────────────────────────────────────────────────────────────┐
│                         Callers                                 │
├──────────────────┬──────────────────────┬───────────────────────┤
│  Human operator  │   AI agent / tool    │  Caseworker portal /  │
│  (browser)       │   (operaton-mcp)     │  automation script    │
├──────────────────┼──────────────────────┼───────────────────────┤
│  Pattern 1       │  Pattern 2           │  Pattern 3            │
│  Cockpit         │  engine-rest + OIDC  │  RONL M2M routes      │
│  (web UI)        │  (native REST)       │  (/v1/m2m/*)          │
├──────────────────┼──────────────────────┼───────────────────────┤
│  operaton-doc    │  operaton-doc        │  RONL Business API    │
│  directly        │  directly            │  → operaton-doc       │
└──────────────────┴──────────────────────┴───────────────────────┘
```

The key insight: Patterns 1 and 2 talk **directly to Operaton**. Pattern 3 talks to the **RONL Business API**, which in turn proxies to Operaton. These are not interchangeable — the path structures, authentication mechanisms, and response shapes are all different.

---

## Pattern 1 — Cockpit (browser)

The Operaton Cockpit is the built-in web UI for process operators. It is served directly by the Operaton container at the root path and uses Operaton's own session-based authentication.

**URL:** `https://operaton-doc.open-regels.nl/`

**Authentication:** Operaton internal user credentials (username/password form login). On the `operaton-doc` instance, the JWT security filter chain only protects `/engine-rest/**` — all other paths including the Cockpit, Tasklist, and Welcome page are permitted without a Bearer token, relying on Operaton's own `LazySecurityFilter`.

**Use for:** Manual process inspection, deployment management, incident resolution, monitoring running instances, viewing the DMN decision tables.

**Not for:** Programmatic access. The Cockpit has no stable API contract for external callers.

---

## Pattern 2 — `operaton-mcp` via `engine-rest` + OIDC

`operaton-mcp` is an MCP server that exposes the full Operaton REST API surface (300+ operations) as AI-callable tools. It talks **directly to Operaton's `engine-rest` API** — bypassing the RONL Business API entirely.

**Base URL:** `https://operaton-doc.open-regels.nl/engine-rest`

**Authentication:** OAuth 2.0 Client Credentials via the `operaton-mcp-client` Keycloak client. `operaton-mcp` fetches a Bearer token from Keycloak and attaches it as `Authorization: Bearer <token>` on every request to `engine-rest`. Operaton validates the token via the JWKS endpoint of the `ronl` realm (configured via `spring.security.oauth2.resourceserver.jwt.jwk-set-uri` in `default.yml`).

**Path contract:** Native Operaton `engine-rest` paths — `/task`, `/process-instance`, `/process-definition`, `/history/process-instance`, `/decision-definition/key/:key/evaluate`, `/deployment`, etc. These are exactly what the [Operaton REST API spec](https://docs.operaton.org) documents.

**Configuration:**
```json
{
  "OPERATON_BASE_URL": "https://operaton-doc.open-regels.nl/engine-rest",
  "OPERATON_CLIENT_ID": "operaton-mcp-client",
  "OPERATON_CLIENT_SECRET": "<secret-from-keycloak>",
  "OPERATON_TOKEN_URL": "https://acc.keycloak.open-regels.nl/realms/ronl/protocol/openid-connect/token"
}
```

**Use for:** AI agents and MCP clients that need the full, unfiltered Operaton surface without tenant scoping. The caller gets everything — all process instances, all tasks, all deployments, all tenants — because there is no organisation filter on this path.

**Not for:** Callers that need the RONL-specific abstractions (audit logging through the RONL API, the curation gate, RONL-shaped response envelopes, tenant-scoped access). Those callers should use Pattern 3.

**Important:** `operaton-mcp` does not know about the RONL Business API. Pointing `OPERATON_BASE_URL` at `https://acc.api.open-regels.nl` is wrong — the RONL Business API does not expose `engine-rest` paths. Routes like `/v1/m2m/process-instance` do not exist; the M2M routes use a completely different path structure (`/v1/m2m/process`, `/v1/m2m/task`, `/v1/m2m/decision/:key`).

### `operaton-doc` Docker setup

The `operaton-doc` instance is dedicated to this use case. It is configured with:

- `CAMUNDA_BPM_AUTHORIZATION_ENABLED=false` — disables Operaton's built-in resource-level authorization, which by default returns 404 (not 403) on unauthorized resources and blocks `/process-instance`, `/history`, `/deployment`, and other endpoints from external callers.
- `spring.security.oauth2.resourceserver.jwt.jwk-set-uri` pointing at the Keycloak JWKS endpoint — enables Bearer token validation on `/engine-rest/**`.
- A custom `operaton-security-config` JAR in `userlib` that scopes the JWT `SecurityFilterChain` to `/engine-rest/**` only, leaving all other paths (Cockpit, Tasklist) unprotected for browser access.

The relevant files:
```
~/operaton/doc/
├── Dockerfile                      # Multi-stage: deps + security-config JAR + operaton image
├── pom.xml                         # Pulls operaton-keycloak-jwt 1.1.0 + spring-boot-starter-oauth2-resource-server
├── config/
│   └── default.yml                 # jwk-set-uri + JPA/Hibernate autoconfigure exclusions
└── security-config/
    ├── pom.xml
    └── src/main/java/nl/openregels/operaton/security/
        └── OperatonSecurityConfig.java   # Two SecurityFilterChain beans: Order(1) JWT for engine-rest, Order(2) permitAll for webapp
```

---

## Pattern 3 — RONL Business API M2M routes (`/v1/m2m/*`)

The RONL Business API exposes a curated subset of Operaton operations through its own `/v1/m2m/*` route group. These routes are designed for callers that need to interact with Operaton through the RONL layer — gaining audit logging, the curation gate, and RONL-shaped response envelopes.

**Base URL:** `https://acc.api.open-regels.nl/v1/m2m`

**Authentication:** OAuth 2.0 Client Credentials via the `operaton-mcp-client` Keycloak client. The token audience must be `ronl-business-api`. The RONL Business API validates the token with `jwtMiddleware` — no `tenantMiddleware` is applied, so no `municipality` claim is required.

**Path contract:** RONL-specific paths that do not mirror `engine-rest`:

| `engine-rest` path | M2M path |
|---|---|
| `GET /task` | `GET /v1/m2m/task` |
| `GET /task/{id}` | `GET /v1/m2m/task/:id` |
| `GET /process-instance` | `GET /v1/m2m/process` |
| `POST /history/process-instance` | `GET /v1/m2m/process/history` |
| `POST /decision-definition/key/:key/evaluate` | `POST /v1/m2m/decision/:key/evaluate` |
| `GET /process-instance/:id/variables` | `GET /v1/m2m/process/:id/variables` |

There is no `/v1/m2m/process-instance`, `/v1/m2m/process-definition`, or `/v1/m2m/history` — these `engine-rest` paths have no equivalent in the M2M layer.

The `M2M_ALLOWED_OPERATIONS` constant in `m2m.routes.ts` acts as a curation gate — any operation not in the list returns `403 OPERATION_NOT_PERMITTED` regardless of what Operaton supports. This is intentional: it gives platform operators control over what M2M callers can do without changing authentication or deployment configuration.

Requests through the M2M routes are written to the `audit_logs` PostgreSQL table. Because the `operaton-mcp-client` token carries no `municipality` claim, `tenant_id` is populated with the Keycloak `azp` claim (`operaton-mcp-client`), making M2M activity queryable and distinguishable from human caseworker activity.

**Use for:** Automation scripts, integration workflows, and future tooling that should go through the RONL API layer for auditability, or that need the RONL response envelope shape. Also appropriate for callers that should be gated by the curation mechanism.

**Not for:** `operaton-mcp`. The MCP server constructs requests using native `engine-rest` paths. Pointing it at the RONL Business API will result in 404 on every tool call that uses process, deployment, or history endpoints, and 403 MISSING_TENANT on the standard caseworker routes.

See [Operaton MCP Client](operaton-mcp-client.md) for the full M2M route reference and authentication setup.

---

## Why the patterns are incompatible

The incompatibility is at the path level, not the authentication level. `operaton-mcp` is a generated proxy over the Operaton OpenAPI spec — it knows about `GET /task`, `POST /process-instance/suspended`, `GET /history/variable-instance`, and so on. None of those paths exist under `/v1/m2m/`. Conversely, a caller that knows about `/v1/m2m/process/:id/decision-document` is speaking the RONL contract, not the Operaton contract, and has no equivalent `engine-rest` path to call.

The `operaton-mcp-client` Keycloak client is shared across both Pattern 2 and Pattern 3 — the same credentials work for both. But the `OPERATON_BASE_URL` determines which pattern is in use:

| `OPERATON_BASE_URL` | Pattern | Works with `operaton-mcp` |
|---|---|---|
| `https://operaton-doc.open-regels.nl/engine-rest` | Pattern 2 | Yes |
| `https://acc.api.open-regels.nl` | Pattern 3 | No — wrong path structure |

---

## Operaton authorization note

By default, Operaton returns `404` (not `403`) on resources the caller lacks `READ` permission for when its built-in authorization is enabled. This means that on a default Operaton instance, endpoints like `/process-instance`, `/process-definition`, `/history`, `/deployment`, `/job`, `/incident`, `/user`, and `/group` will return 404 to any caller without explicit authorization grants — including authenticated callers with a valid Bearer token.

The correct solution for controlled environments (where access is governed externally — by OIDC, by Caddy, or by the RONL Business API layer) is `CAMUNDA_BPM_AUTHORIZATION_ENABLED=false`. This is set on `operaton-doc`. Do not set it on production instances that serve multiple tenants through Operaton's own authorization model.

---

## Decision guide

Use this to determine which pattern to use for a new integration:
```
Does the caller use the MCP protocol (operaton-mcp, Claude Desktop, GitHub Copilot)?
  └─ Yes → Pattern 2. Point OPERATON_BASE_URL at engine-rest directly.

Does the caller need audit logging through the RONL API?
  └─ Yes → Pattern 3. Use the /v1/m2m/* routes.

Does the caller need operations not exposed by the M2M curation gate?
  └─ Yes → Pattern 2, or extend the M2M_ALLOWED_OPERATIONS list.

Is the caller a human operator inspecting or managing processes?
  └─ Yes → Pattern 1. Use the Cockpit.

Does the caller need tenant-scoped access (only data for one municipality)?
  └─ Yes → Use the standard caseworker routes (/v1/process, /v1/task, /v1/decision)
            with a token that carries a municipality claim. Not a pattern covered here.
```