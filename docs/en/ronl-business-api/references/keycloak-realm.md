# Keycloak Realm Configuration

The `ronl` realm is defined in `config/keycloak/ronl-realm.json`. It is imported automatically on first Keycloak container start and can be re-imported at any time without data loss (using `--override true`).

## Realm settings

| Setting | Value |
|---|---|
| Realm name | `ronl` |
| Display name | RONL — Regels Overheid Nederland |
| SSL required | External requests only |
| Registration | Disabled |
| Brute force protection | Enabled |
| Max failed attempts | 5 |
| Wait increment | 60 seconds |
| Max delta time | 12 hours |

## Token lifespans

| Token | Lifespan |
|---|---|
| Access token | 15 minutes (`accessTokenLifespan: 900`) |
| Access token (implicit flow) | 15 minutes |
| SSO session idle | 30 minutes (`ssoSessionIdleTimeout: 1800`) |
| SSO session max | 10 hours (`ssoSessionMaxLifespan: 36000`) |
| Offline session idle | 30 days |
| Auth code | 60 seconds |

## Client: `ronl-business-api`

| Setting | Value |
|---|---|
| Client ID | `ronl-business-api` |
| Client authentication | Off (public client) |
| Standard flow | Enabled |
| Implicit flow | Disabled |
| Direct access grants | Enabled (test users only) |
| Service accounts | Disabled |
| PKCE | Code challenge method: S256 |
| Valid redirect URIs | `*` (restrict in production) |
| Web origins | `*` (restrict in production) |

## Protocol mappers

Three protocol mappers are configured on the `ronl-business-api-dedicated` client scope:

| Mapper name | Type | Token claim | Source |
|---|---|---|---|
| `municipality` | User Attribute | `municipality` | User attribute `municipality` |
| `roles` | User Realm Role | `roles` | Realm roles assigned to the user |
| `loa` | User Attribute | `loa` | User attribute `loa` |

These mappers add `municipality`, `roles`, and `loa` to every access token issued for this client.

## Test users

All test users have password `test123` and `directAccessGrantsEnabled: true`.

| Username | `municipality` attribute | Realm roles |
|---|---|---|
| `test-citizen-utrecht` | `utrecht` | `citizen` |
| `test-caseworker-utrecht` | `utrecht` | `caseworker` |
| `test-citizen-amsterdam` | `amsterdam` | `citizen` |
| `test-caseworker-amsterdam` | `amsterdam` | `caseworker` |
| `test-citizen-rotterdam` | `rotterdam` | `citizen` |
| `test-caseworker-rotterdam` | `rotterdam` | `caseworker` |
| `test-citizen-denhaag` | `denhaag` | `citizen` |
| `test-caseworker-denhaag` | `denhaag` | `caseworker` |

## Re-importing the realm

After modifying `config/keycloak/ronl-realm.json`:

```bash
# On the VM, for ACC
docker exec keycloak-acc /opt/keycloak/bin/kc.sh import \
  --file /opt/keycloak/data/import/ronl-realm.json \
  --override true

# Restart to apply
docker compose restart keycloak-acc
```
