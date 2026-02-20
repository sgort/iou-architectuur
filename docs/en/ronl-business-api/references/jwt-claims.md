# JWT Claims

RONL Business API validates every request against a JWT access token issued by Keycloak. The token contains standard OIDC claims plus custom claims injected via Keycloak protocol mappers.

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
    "roles": ["citizen"],
    "loa": "substantial"
  }
}
```

## Standard OIDC claims

| Claim | Type | Description |
|---|---|---|
| `iss` | string | Token issuer — Keycloak realm URL |
| `aud` | string | Intended audience — must be `ronl-business-api` |
| `sub` | string | Subject — unique user UUID, used as `userId` in audit logs |
| `exp` | number | Expiry — Unix timestamp; token lifetime is 15 minutes |
| `iat` | number | Issued at — Unix timestamp |
| `preferred_username` | string | Human-readable username |
| `typ` | string | Always `Bearer` |

## Custom RONL claims

These claims are added by Keycloak protocol mappers configured on the `ronl-business-api` client:

| Claim | Type | Mapper type | Description |
|---|---|---|---|
| `municipality` | string | User Attribute | Tenant identifier — maps to `TenantConfig.id` |
| `roles` | string[] | User Realm Role | Roles assigned in the Keycloak realm |
| `loa` | string | User Attribute | Level of Assurance from DigiD (`low`, `substantial`, `high`) |
| `mandate` | string | User Attribute | Representation authority (optional — `legal-guardian`, `power-of-attorney`) |
| `bsn` | string | User Attribute | Citizen Service Number (encrypted in production, placeholder in test) |

## How claims are used by the backend

After successful JWT validation in `jwt.middleware.ts`, the decoded payload is attached to `req.user`:

```typescript
interface JwtClaims {
  sub: string;           // → userId in audit log
  municipality: string;  // → tenant isolation filter
  roles: string[];       // → authorization checks
  loa: string;           // → LoA-gated endpoint checks
  preferred_username: string;
  mandate?: string;
  bsn?: string;
}
```

The tenant middleware reads `req.user.municipality` to load the `TenantConfig` and apply the feature allowlist for the request.

## Inspecting a token in the browser

```javascript
// In browser DevTools console after login:
const token = /* keycloak.token */;
JSON.parse(atob(token.split('.')[1]));
```

Or paste the token at [jwt.io](https://jwt.io) for a formatted view.

## Token lifetime

| Setting | Value | Keycloak config key |
|---|---|---|
| Access token | 15 minutes | `accessTokenLifespan: 900` |
| SSO session idle | 30 minutes | `ssoSessionIdleTimeout: 1800` |
| SSO session max | 10 hours | `ssoSessionMaxLifespan: 36000` |

The Keycloak JS adapter in the frontend automatically refreshes the access token before it expires, as long as the SSO session is still valid.
