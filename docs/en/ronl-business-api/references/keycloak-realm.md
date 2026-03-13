# Keycloak Realm Configuration

The `ronl` realm is defined in `config/keycloak/ronl-realm.json`. It is imported automatically on first Keycloak container start and can be re-imported at any time without data loss (using `--override true`).

---

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

---

## Token lifespans

| Token | Lifespan |
|---|---|
| Access token | 15 minutes (`accessTokenLifespan: 900`) |
| Access token (implicit flow) | 15 minutes |
| SSO session idle | 30 minutes (`ssoSessionIdleTimeout: 1800`) |
| SSO session max | 10 hours (`ssoSessionMaxLifespan: 36000`) |
| Offline session idle | 30 days |
| Auth code | 60 seconds |

---

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

---

## Protocol mappers

The following protocol mappers are configured on the `ronl-business-api-dedicated` client scope:

| Mapper name | Type | Token claim | Source attribute |
|---|---|---|---|
| `municipality` | User Attribute | `municipality` | `municipality` |
| `organisation_type` | User Attribute | `organisation_type` | `organisation_type` |
| `assurance_level` | User Attribute | `loa` | `assurance_level` |
| `mandate` | User Attribute | `mandate` | `mandate` |
| `realm_roles` | User Realm Role | `realm_access.roles` | Realm roles |
| `audience-mapper` | Audience | `aud` | Fixed: `ronl-business-api` |
| `employee_id` | User Attribute | `employeeId` | `employee_id` |

All mappers have `id.token.claim`, `access.token.claim`, and `userinfo.token.claim` set to `true`.

---

## Realm roles

| Role | Description |
|---|---|
| `citizen` | Regular citizen using municipality services |
| `representative` | Representative acting on behalf of a citizen (with mandate) |
| `caseworker` | Municipality caseworker processing applications |
| `hr-medewerker` | HR department employee who manages staff onboarding |
| `admin` | Municipality administrator |

---

## Test users

All test users have password `test123` and `directAccessGrantsEnabled: true`.

| Username | `municipality` | `organisation_type` | Realm roles |
|---|---|---|---|
| `test-citizen-utrecht` | `utrecht` | `municipality` | `citizen` |
| `test-caseworker-utrecht` | `utrecht` | `municipality` | `caseworker` |
| `test-citizen-amsterdam` | `amsterdam` | `municipality` | `citizen` |
| `test-caseworker-amsterdam` | `amsterdam` | `municipality` | `caseworker` |
| `test-citizen-rotterdam` | `rotterdam` | `municipality` | `citizen` |
| `test-caseworker-rotterdam` | `rotterdam` | `municipality` | `caseworker` |
| `test-citizen-denhaag` | `denhaag` | `municipality` | `citizen` |
| `test-caseworker-denhaag` | `denhaag` | `municipality` | `caseworker` |
| `test-hr-denhaag` | `denhaag` | `municipality` | `caseworker`, `hr-medewerker` |
| `test-onboarded-denhaag` | `denhaag` | `municipality` | `caseworker` |
| `test-caseworker-flevoland` | `flevoland` | `province` | `caseworker` |
| `test-caseworker-uwv` | `uwv` | `national` | `caseworker` |

---

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
