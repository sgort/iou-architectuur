---
component: RONL Business API
---

# Keycloak Timeline Setup - Configuration Reference

---

## Overview

The Timeline Navigation feature needs a `bsn` claim in the JWT: the frontend takes the citizen's BSN (Burgerservicenummer) from it, and the backend checks a citizen's lookup against it. This page explains how the claim gets there.

---

## Why This Is Needed

### The Problem

- Timeline needs a BSN to fetch BRP data
- The token carries none by default
- On test realms the BSN is a user attribute; where DigiD is real it is to come from the DigiD subject

### The Solution

A protocol mapper puts the user attribute `bsn` in the token as `bsn`. The realm export has it; `scripts/keycloak-add-brp-raadpleger.sh` adds it, with the role and the test citizens' attribute, to an existing realm. The steps below do the mapper by hand.

---

## Configuration Steps

### 1. Access Keycloak Admin Console

```
URL: http://localhost:8080 (local)
     https://acc.keycloak.open-regels.nl (ACC)
     https://keycloak.open-regels.nl (PROD)

Login: admin / <admin-password>
```

### 2. Navigate to Client Scopes

1. Select **Realm:** `ronl` (top-left dropdown)
2. In left menu, click **Clients**
3. Find and click **`ronl-business-api`**
4. Click **Client scopes** tab
5. Click on **`ronl-business-api-dedicated`** (in the table)

### 3. Add Protocol Mapper

1. Click **Mappers** tab
2. Click **Add mapper** button
3. Select **By configuration**
4. Select **User Attribute**

### 4. Configure Mapper

Fill in the form:

| Field | Value |
|-------|-------|
| **Name** | `bsn` |
| **Mapper Type** | User Attribute |
| **User Attribute** | `bsn` |
| **Token Claim Name** | `bsn` |
| **Claim JSON Type** | String |
| **Add to ID token** | ☑️ ON |
| **Add to access token** | ☑️ ON |
| **Add to userinfo** | ☑️ ON |
| **Multivalued** | ☐ OFF |

5. Click **Save**

---

## Verification

### Test the Configuration

1. **Login** to MijnOmgeving with a test citizen
2. **Open browser DevTools** (F12)
3. **Go to the Network tab** and select a request to `/v1/`
4. **Copy the token** from its `Authorization: Bearer` header and decode the payload, as under [Inspecting a token in the browser](jwt-claims.md#inspecting-a-token-in-the-browser)
5. **Verify** the token contains:

```json
{
  "bsn": "999992235",
  "municipality": "utrecht",
  "sub": "uuid-here",
  "realm_access": { "roles": ["citizen"] },
  "loa": "hoog"
}
```

### If It's Not Working

**Token missing `bsn`:**

1. Clear browser cache and cookies
2. Logout and login again (force new token)
3. Verify mapper is saved correctly
4. Check mapper is in `ronl-business-api-dedicated` scope (not a different scope)
5. Check the user has the attribute `bsn`

**Still not working:**

1. Restart Keycloak: `docker compose restart keycloak`
2. Check Keycloak logs: `docker compose logs keycloak`

---

## Production Considerations

### DigiD Integration

In production with real DigiD, you'll also need:

1. **BSN Mapper** — Maps the DigiD subject to the `bsn` claim
2. **Municipality Mapper** — Maps organization to `municipality` claim
3. **LoA Mapper** — Maps DigiD assurance level to `loa` claim

See [Authentication & IAM](../features/authentication-iam.md).

### Security Notes

- `bsn` is personal data: keep it out of logs. The BRP route's own log lines carry none; its audit entry does, on purpose. The frontend still writes the decoded token, with this claim, to the browser console ([#477](https://github.com/sgort/ronl-business-api/issues/477))
- ✅ Token lifetime should be 15 minutes maximum
- ✅ Tokens must be validated on every request

---

## Troubleshooting

### Mapper Not Appearing in Token

**Check:**

1. Mapper is added to correct client scope (`ronl-business-api-dedicated`)
2. Client scope is assigned to client (`ronl-business-api`)
3. "Add to access token" is enabled
4. User has logged out and back in (to get new token)
5. User has the attribute `bsn`. A realm whose user profile drops unmanaged attributes loses the value silently; the read-back of `scripts/keycloak-add-brp-raadpleger.sh` catches that

### Wrong Value in Token

**If `bsn` holds another value than expected:**

- Check the **User Attribute** field is set to `bsn`
- Check the value of the attribute on the user in Keycloak's Users section

**If `bsn` is missing:**

- The user may not have the attribute
- Check user attributes in Keycloak Users section

### Multiple Mappers Conflict

If you have multiple mappers for `bsn`:

1. Delete all except one
2. Logout/login to refresh token
3. Verify only one `bsn` claim in token

---

## Related Configuration

### Other Timeline-Related Settings

Beyond this mapper, ensure these are also configured:

1. **Shared Package Types** — `KeycloakUser` and `AuthenticatedUser` include `bsn`
2. **Backend tsconfig** — Removed `composite: true` (see [Technical Architecture](../reference/brp-timeline-integration.md))

### Test Users Setup

Verify test users have correct attributes:

```json
{
  "username": "test-citizen-utrecht",
  "attributes": {
    "municipality": ["utrecht"],
    "assurance_level": ["hoog"],
    "bsn": ["999992235"]
  },
  "realmRoles": ["citizen"]
}
```

Import test users from: `config/keycloak/ronl-realm.json`

---

## Configuration Checklist

Use this checklist when setting up timeline in a new environment:

- [ ] Keycloak realm `ronl` exists
- [ ] Client `ronl-business-api` exists
- [ ] Client scope `ronl-business-api-dedicated` exists
- [ ] Protocol mapper `bsn` → `bsn` created
- [ ] Mapper enabled for access token, ID token, userinfo
- [ ] Test citizen has the attribute `bsn`
- [ ] Token verified to contain `bsn`
- [ ] Timeline feature tested and working
- [ ] Documentation updated with environment-specific URLs

---

## Realm Export/Import

### Exporting Realm with Mapper

To export realm configuration including the mapper:

```bash
# Inside Keycloak container
/opt/keycloak/bin/kc.sh export \
  --dir /tmp/export \
  --realm ronl \
  --users realm_file

# Copy from container
docker cp keycloak:/tmp/export/ronl-realm.json ./config/keycloak/
```

### Importing Realm

```bash
# From project root
docker compose exec keycloak \
  /opt/keycloak/bin/kc.sh import \
  --file /opt/keycloak/data/import/ronl-realm.json
```

**Note:** Manual mapper configuration is recommended over import to avoid UUID mismatches.

---

## API Impact

### Before Configuration

**JWT Token:**
```json
{
  "sub": "uuid-abc-123",
  "municipality": "utrecht",
  "realm_access": { "roles": ["citizen"] }
}
```

**Timeline Behavior:**

- The **Tijdlijn** tab reads *Geen tijdlijn gegevens beschikbaar voor deze gebruiker*
- A direct call to `POST /v1/brp/personen` at level `hoog` answers `403 BSN_CLAIM_MISSING`

### After Configuration

**JWT Token:**
```json
{
  "sub": "uuid-abc-123",
  "bsn": "999992235",
  "municipality": "utrecht",
  "realm_access": { "roles": ["citizen"] }
}
```

**Timeline Behavior:**

- ✅ Fetches person data from BRP API for the BSN in the claim
- ✅ Timeline loads successfully

---

## Further Reading

- [Keycloak Protocol Mappers Documentation](https://www.keycloak.org/docs/latest/server_admin/#_protocol-mappers)
- [OIDC Standard Claims](https://openid.net/specs/openid-connect-core-1_0.html#StandardClaims)
- [JWT Claims Reference](../reference/jwt-claims.md)
- [Timeline Technical Architecture](../reference/brp-timeline-integration.md)

