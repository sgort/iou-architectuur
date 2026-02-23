# Keycloak Timeline Setup - Configuration Reference

## Overview

The Timeline Navigation feature requires the `preferred_username` field in JWT tokens to map test users to their BSN (Burgerservicenummer). This document explains how to configure Keycloak to include this field.

---

## Why This Is Needed

### The Problem

- Timeline needs to fetch BRP data using a BSN
- In production, BSN comes from DigiD via SAML assertion
- In test/ACC, BSN is mapped from Keycloak username
- JWT token doesn't include username by default

### The Solution

Add a Keycloak Protocol Mapper that includes `username` in the JWT token as `preferred_username`.

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
4. Select **User Property**

### 4. Configure Mapper

Fill in the form:

| Field | Value |
|-------|-------|
| **Name** | `username` |
| **Mapper Type** | User Property |
| **Property** | `username` |
| **Token Claim Name** | `preferred_username` |
| **Claim JSON Type** | String |
| **Add to ID token** | ☑️ ON |
| **Add to access token** | ☑️ ON |
| **Add to userinfo** | ☑️ ON |
| **Multivalued** | ☐ OFF |

5. Click **Save**

---

## Verification

### Test the Configuration

1. **Login** to MijnOmgeving with a test user
2. **Open browser DevTools** (F12)
3. **Go to Console tab**
4. **Look for the log:** `🔍 Full token as JSON:`
5. **Verify** the token contains:

```json
{
  "preferred_username": "test-citizen-utrecht",
  "municipality": "utrecht",
  "sub": "uuid-here",
  "roles": ["citizen"],
  "loa": "hoog"
}
```

### If It's Not Working

**Token missing `preferred_username`:**

1. Clear browser cache and cookies
2. Logout and login again (force new token)
3. Verify mapper is saved correctly
4. Check mapper is in `ronl-business-api-dedicated` scope (not a different scope)

**Still not working:**

1. Restart Keycloak: `docker compose restart keycloak`
2. Check Keycloak logs: `docker compose logs keycloak`

---

## Production Considerations

### DigiD Integration

In production with real DigiD, you'll also need:

1. **BSN Mapper** — Maps SAML attribute to `bsn` claim
2. **Municipality Mapper** — Maps organization to `municipality` claim
3. **LoA Mapper** — Maps DigiD assurance level to `loa` claim

See [Authentication & IAM](../features/authentication-iam.md) for full DigiD setup.

### Security Notes

- ✅ `preferred_username` is safe to include (not sensitive data)
- ✅ BSN should NEVER be in logs (masked as `999-99-2235`)
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

### Wrong Value in Token

**If `preferred_username` shows UUID instead of username:**

- Check **Property** field is set to `username` (not `id`)
- Verify user actually has a username set in Keycloak

**If `preferred_username` is `null`:**

- User might not have username set
- Check user attributes in Keycloak Users section

### Multiple Mappers Conflict

If you have multiple mappers for `preferred_username`:

1. Delete all except one
2. Logout/login to refresh token
3. Verify only one `preferred_username` claim in token

---

## Related Configuration

### Other Timeline-Related Settings

Beyond this mapper, ensure these are also configured:

1. **Shared Package Types** — `KeycloakUser` interface includes `preferred_username`
2. **Backend tsconfig** — Removed `composite: true` (see [Technical Architecture](../technical/brp-timeline-integration.md))
3. **BSN Mapping Service** — Maps usernames to BSN (see [Developer Guide](../developer/implementing-timeline.md))

### Test Users Setup

Verify test users have correct attributes:

```json
{
  "username": "test-citizen-utrecht",
  "attributes": {
    "municipality": ["utrecht"],
    "assurance_level": ["hoog"]
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
- [ ] Protocol mapper `username` → `preferred_username` created
- [ ] Mapper enabled for access token, ID token, userinfo
- [ ] Test user has username attribute set
- [ ] Token verified to contain `preferred_username`
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
  "roles": ["citizen"]
}
```

**Timeline Behavior:**
- Cannot map user to BSN
- Timeline fails to load
- Error: "No BSN found for user"

### After Configuration

**JWT Token:**
```json
{
  "sub": "uuid-abc-123",
  "preferred_username": "test-citizen-utrecht",
  "municipality": "utrecht",
  "roles": ["citizen"]
}
```

**Timeline Behavior:**

- ✅ Maps `test-citizen-utrecht` → BSN `999992235`
- ✅ Fetches person data from BRP API
- ✅ Timeline loads successfully

---

## Further Reading

- [Keycloak Protocol Mappers Documentation](https://www.keycloak.org/docs/latest/server_admin/#_protocol-mappers)
- [OIDC Standard Claims](https://openid.net/specs/openid-connect-core-1_0.html#StandardClaims)
- [JWT Claims Reference](../references/jwt-claims.md)
- [Timeline Technical Architecture](../references/brp-timeline-integration.md)

