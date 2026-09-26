---
component: RONL Business API
---

# JWT Claims

RONL Business API validates every request against a JWT access token issued by Keycloak. The token contains standard OIDC claims plus custom claims injected via Keycloak protocol mappers.

---

## Full token example

```json
{
  "header": {
    "alg": "RS256",
    "typ": "JWT",
    "kid": "key-id-123"
  },
  "payload": {
    "exp": 1740492000,
    "iat": 1740491100,
    "iss": "https://keycloak.open-regels.nl/realms/ronl",
    "aud": "ronl-business-api",
    "sub": "user-uuid-abc-123",
    "typ": "Bearer",
    "azp": "ronl-business-api",
    "preferred_username": "test-citizen-utrecht",
    "email_verified": false,
    "municipality": "utrecht",
    "organisation_type": "municipality",
    "realm_access": { "roles": ["citizen"] },
    "loa": "hoog"
  }
}
```

---

## Standard OIDC claims

| Claim                | Type   | Description                                                |
| -------------------- | ------ | ---------------------------------------------------------- |
| `iss`                | string | Token issuer — Keycloak realm URL                          |
| `aud`                | string | Intended audience — must be `ronl-business-api`            |
| `sub`                | string | Subject — unique user UUID, used as `userId` in audit logs |
| `exp`                | number | Expiry — Unix timestamp; token lifetime is 15 minutes      |
| `iat`                | number | Issued at — Unix timestamp                                 |
| `preferred_username` | string | Human-readable username                                    |
| `typ`                | string | Always `Bearer`                                            |

---

## Custom RONL claims

These claims are added by Keycloak protocol mappers configured on the `ronl-business-api` client in the realm export (`config/keycloak/ronl-realm.json`):

| Claim | Type | Mapper | Source | Description |
|---|---|---|---|---|
| `municipality` | string | User Attribute | `municipality` | Tenant identifier — the organisation the caller belongs to (`utrecht`, `flevoland`, `toeslagen`, …) |
| `organisation_type` | string | User Attribute | `organisation_type` | Organisation category: `municipality`, `province`, `national`, or `commercial` |
| `realm_access.roles` | string[] | User Realm Role | realm roles | The caller's realm roles; the backend reads its roles from here |
| `loa` | string | User Attribute | `assurance_level` | Level of assurance: `basis`, `midden`, `substantieel`, or `hoog` |
| `mandate` | string | User Attribute | `mandate` | Representation authority (optional). Passed through to `req.user`; no check reads it |
| `employeeId` | string | User Attribute | `employee_id` | Present on caseworker accounts onboarded via `HrOnboardingProcess`; absent for citizens and non-onboarded caseworkers |
| `given_name`, `family_name`, `email` | string | User Property | `firstName`, `lastName`, `email` | Used for signer details; when the name claims are missing, the name is split from `name` or `preferred_username` |

The client maps no `bsn` claim. The frontend reads a `bsn` claim first when it looks up a citizen's service number — the field DigiD fills — and falls back to a fixed mapping for the test usernames.

---

## How claims are used by the backend

After successful JWT validation in `jwt.middleware.ts`, the claims are mapped onto `req.user`:

| `req.user` field | From claim | Used for |
|---|---|---|
| `userId` | `sub` | Audit log; `applicantId` and `initiator` on a started process |
| `tenantId` | `municipality` | The `MISSING_TENANT` presence check and every tenant decision |
| `organisationType` | `organisation_type` | Propagated to process variables |
| `roles` | `realm_access.roles` | Role checks, the citizen/staff distinction at process start, task candidate groups |
| `assuranceLevel` | `loa` | Assurance-level checks (`basis` for decision evaluation, `midden` for a process start) |
| `mandate` | `mandate` | Carried only |
| `employeeId` | `employeeId` | HR onboarding profile lookup |

The tenant middleware only checks that `tenantId` is present, answering `403 MISSING_TENANT` when it is not. Which organisation may reach a process instance or task is decided separately, in `auth/tenant-access.ts`, from the instance's `municipality` variable — see [Authentication & IAM — Tenancy](../features/authentication-iam.md#tenancy).

---

## Inspecting a token in the browser

```javascript
// In browser DevTools console after login:
const token = /* keycloak.token */;
JSON.parse(atob(token.split('.')[1]));
```

Or paste the token at [jwt.io](https://jwt.io) for a formatted view.

---

## Token lifetime

| Setting          | Value      | Keycloak config key            |
| ---------------- | ---------- | ------------------------------ |
| Access token     | 15 minutes | `accessTokenLifespan: 900`     |
| SSO session idle | 30 minutes | `ssoSessionIdleTimeout: 1800`  |
| SSO session max  | 10 hours   | `ssoSessionMaxLifespan: 36000` |

The Keycloak JS adapter in the frontend automatically refreshes the access token before it expires, as long as the SSO session is still valid.
