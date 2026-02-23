# Troubleshooting

## Diagnosing a problem

Start by identifying which layer the error comes from:

| Where to look | What it covers |
|---|---|
| Browser console (F12 → Console) | Frontend JavaScript errors |
| Browser network tab (F12 → Network) | API call failures, CORS errors, HTTP status codes |
| Terminal running `npm run dev` | Backend errors, stack traces |
| `docker compose logs -f keycloak` | Keycloak startup, authentication errors |
| `docker compose logs -f postgres` | Database connection errors |

---

## Authentication errors

### JWT audience invalid

```
Token validation failed: jwt audience invalid. expected: ronl-business-api
```

The access token is missing the `aud` claim. Add the Audience mapper in Keycloak Admin:

1. Open Keycloak Admin: `http://localhost:8080`
2. Select realm **ronl**
3. Navigate to **Clients → ronl-business-api → Client scopes → ronl-business-api-dedicated**
4. Click **Add mapper → By configuration → Audience**
5. Set:
   - Name: `audience`
   - Included Client Audience: `ronl-business-api`
   - Add to access token: **ON**
6. Save, then log out and log back in

Verify by decoding your token at `jwt.io` and checking for `"aud": "ronl-business-api"`.

---

### Roles not appearing in JWT

All users show as `citizen` even though a test user is configured as `caseworker`.

The `realm_roles` protocol mapper is missing. Add it in Keycloak Admin:

1. **Clients → ronl-business-api → Client scopes → ronl-business-api-dedicated → Mappers**
2. If `realm_roles` is missing, click **Add mapper → By configuration → User Realm Role**
3. Set:
   - Name: `realm_roles`
   - Multivalued: **ON**
   - Token Claim Name: `realm_access.roles`
   - Add to access token: **ON**
4. Save, then log out and log back in

---

### Login redirects to blank page

**Cause:** Invalid redirect URIs in the Keycloak client.

1. **Clients → ronl-business-api → Settings**
2. Set **Valid Redirect URIs** to `*`
3. Set **Valid Post Logout Redirect URIs** to `*`
4. Set **Web Origins** to `+`
5. Save

---

### Token expired

```
JWT validation failed: jwt expired
```

This is expected — access tokens have a 15-minute lifetime. Log out and log back in. Token refresh is a planned production feature.

---

## CORS errors

### CORS policy blocking Keycloak

```
Access to XMLHttpRequest at 'http://localhost:8080/realms/ronl/...'
from origin 'http://localhost:5173' has been blocked by CORS policy
```

1. **Clients → ronl-business-api → Settings**
2. Set **Web Origins** to `+` (inherits all valid redirect URIs)
3. Save

If the error persists, verify `CORS_ORIGIN` in `packages/backend/.env` matches `http://localhost:5173` exactly (no trailing slash).

---

## Backend API errors

### Health check returns unhealthy dependencies

```bash
curl http://localhost:3002/v1/health | jq .
```

Expected:
```json
{
  "status": "healthy",
  "services": {
    "keycloak": { "status": "up" },
    "operaton": { "status": "up" }
  }
}
```

If `keycloak` is `"down"`: check Docker — `docker compose ps` — and that Keycloak is listening on port 8080.  
If `operaton` is `"down"`: check that `https://operaton.open-regels.nl` is reachable from your network.

---

### Port already in use

```
Error: listen EADDRINUSE: address already in use :::3002
```

Find and stop whatever is occupying the port:

```bash
# Linux/Mac
lsof -i :3002
kill -9 <PID>

# Windows
netstat -ano | findstr :3002
taskkill /PID <PID> /F
```

Alternatively, change the port in `packages/backend/.env`:

```bash
PORT=3003
```

And update `VITE_API_URL` in `packages/frontend/.env` to match.

---

### API returns 500 Internal Server Error

Check the backend terminal for a stack trace. Common causes:

- Operaton unreachable (`OPERATON_BASE_URL` wrong or service down)
- Invalid request body (missing required fields)
- Missing environment variable (check `packages/backend/.env` is populated)

---

### Zorgtoeslag calculation fails

#### DMN hit policy violation

**Symptom:**
```
POST /v1/decision/berekenrechtenhoogtezorg/evaluate → 500
{
  "success": false,
  "error": {
    "code": "DECISION_EVALUATION_FAILED",
    "message": "DMN configuratiefout in beslissingstabel 'berekenrechtenhoogtezorg': meerdere regels zijn tegelijk van toepassing, maar het trefriebeleid (hit policy) staat slechts één treffer toe. Neem contact op met de beheerder."
  }
}
```

**Cause:** The DMN decision table uses the default `UNIQUE` hit policy, which requires exactly one rule to match per evaluation. When multiple disqualifying conditions are true simultaneously (e.g. both `betalingsregeling = true` and `detentie = true`), two rules match and Operaton throws a runtime exception. Operaton surfaces this as `"Exception while evaluating decision with key 'null'"` — the `'null'` refers to the internal rule key that could not be resolved, not to the decision key itself.

**Fix:** Open `BerekenRechtEnHoogteZorg.dmn` in Camunda Modeler and set the hit policy on the decision table to `FIRST`:
```xml
<decisionTable id="decisionTable" hitPolicy="FIRST">
```

With `FIRST`, rules are evaluated top-to-bottom and evaluation stops at the first match. Ensure the disqualifying rules (betalingsregeling, detentie, ingezetene, leeftijd, verzekering) appear above the income threshold rules and the positive allowance rule.

Also correct the `Null` literals in all disqualifying output entries — the FEEL spec requires lowercase `null`:
```xml
<!-- Wrong -->
<outputEntry><text>Null</text></outputEntry>

<!-- Correct -->
<outputEntry><text>null</text></outputEntry>
```

After editing, redeploy the DMN to Operaton via the Camunda Modeler deploy feature or the Operaton REST API.

**Error message routing:** The `operaton.service.ts` catch block detects this specific error pattern and throws a descriptive `Error` instead of re-throwing the raw axios exception. `decision.routes.ts` propagates that message as `error.message` in the 500 response body. The frontend `api.ts` reads `error.response.data` on a 500 and returns it as a structured `ApiResponse`, so `Dashboard.tsx` renders `result.error.message` directly. Citizens see a neutral notification; caseworkers see the technical message.

#### Other causes

1. Open browser DevTools → **Network tab**
2. Find the request to `/v1/decision/berekenrechtenhoogtezorg/evaluate`
3. Check the response body — the `error.message` field identifies the cause
4. Common causes: `aud` claim missing from token (see JWT audience fix above), Operaton service unreachable (check health endpoint), invalid input variable types

---

## Test user issues

### Can't log in with test users

Verify the users exist in Keycloak:

1. Open Keycloak Admin → **Users**
2. Search for `test-citizen-utrecht`
3. Should find 8 users total (citizen + caseworker × 4 municipalities)

If the users are missing, the realm import did not run. Reimport:

```bash
docker compose down
docker volume rm ronl-business-api_keycloak-data
docker compose up -d
# Wait 60 seconds for Keycloak to start and import the realm
npm run dev
```

---

## Browser issues

### Changes not visible after saving

Vite HMR should update automatically. If it doesn't:

```
Ctrl+Shift+R   (Windows/Linux)
Cmd+Shift+R    (Mac)
```

If that fails: F12 → Application → Clear storage → Clear site data → reload.

---

### Regular Chrome not working, Incognito works

**Cause:** Browser cache holding stale CORS errors.

1. Close all Chrome windows completely
2. Reopen Chrome
3. Try again

If still broken, use Incognito for the remainder of the session. This is a browser cache issue, not a code issue.

---

## Windows-specific issues

### Line ending warnings

```
warning: LF will be replaced by CRLF
```

```bash
git config --global core.autocrlf false
```

---

## Emergency reset

When everything is broken and you want a clean slate:

```bash
# 1. Stop dev servers
Ctrl+C

# 2. Wipe Docker (containers + volumes = all Keycloak data)
docker compose down -v
docker system prune -f

# 3. Wipe Node modules
rm -rf node_modules
rm -rf packages/*/node_modules

# 4. Fresh install and start
npm install
npm run build --workspace=@ronl/shared
npm run docker:up
# Wait 60 seconds
npm run dev
```

---

## Diagnostic commands

```bash
# Check tool versions
node --version
npm --version
docker --version

# Check running containers
docker compose ps
docker compose logs keycloak --tail=50

# Check ports in use (Linux/Mac)
sudo lsof -i :5173    # frontend
sudo lsof -i :3002    # backend
sudo lsof -i :8080    # keycloak

# Check ports in use (Windows)
netstat -ano | findstr :5173
netstat -ano | findstr :3002
netstat -ano | findstr :8080

# API health with formatted output
curl http://localhost:3002/v1/health | jq

# Keycloak health
curl http://localhost:8080/health/ready
```
