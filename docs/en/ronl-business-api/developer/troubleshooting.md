---
component: RONL Business API
---

# Troubleshooting

---

## Diagnosing a problem

Start by identifying which layer the error comes from:

| Where to look | What it covers |
|---|---|
| Browser console (F12 → Console) | Frontend JavaScript errors |
| Browser network tab (F12 → Network) | API call failures, CORS errors, HTTP status codes |
| Terminal running `npm run dev` | Backend errors, stack traces |
| `docker compose logs -f keycloak` | Keycloak startup, authentication errors |
| `docker compose logs -f postgres` | Database connection errors |
| `docker compose logs -f operaton` | Local engine startup, deployment and process errors |

---

## Authentication errors

### JWT audience invalid

```
Token validation failed: jwt audience invalid. expected: ronl-business-api
```

The access token is missing the `aud` claim. Locally, a realm imported from the
current `config/keycloak/ronl-realm.json` already carries this mapper and the
`realm_roles` mapper below; see
[Local Development — Common issues](local-development.md#common-issues) for
resetting an older realm. On an environment you cannot reset, add the Audience
mapper in Keycloak Admin:

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

### Procesbibliotheek CORS error

**Symptom:** The Procesbibliotheek section is empty and the browser console shows a CORS policy error for a request to `https://backend.linkeddata.open-regels.nl/v1/bundles/public` from origin `https://mijn.open-regels.nl`.

**Cause:** Procesbibliotheek calls the standalone LDE backend directly from the browser (`VITE_LDE_API_URL/bundles/public`), not via the business API. The LDE backend is a separate deployment with its own ACC/PROD environment split and its own CORS allowlist. A new frontend origin is not automatically allowed.

**Fix:** Add the frontend origin (e.g. `https://mijn.open-regels.nl`) to the LDE backend's CORS allowlist — wherever that backend configures it (env var or its own `cors()` config) — then restart it. Confirm with:

```bash
curl -s -i -X OPTIONS https://backend.linkeddata.open-regels.nl/v1/bundles/public \
  -H "Origin: https://mijn.open-regels.nl" \
  -H "Access-Control-Request-Method: GET" | grep -i 'access-control'
```

The response must include `Access-Control-Allow-Origin: https://mijn.open-regels.nl`. The rest of the dashboard is unaffected by this — only Procesbibliotheek degrades.

---

## Backend API errors

### Health check returns unhealthy dependencies

```bash
curl http://localhost:3002/v1/health | jq .
```

The endpoint answers `200` with `data.status` `"healthy"` when Keycloak and
Operaton are both up, and `503` with `"degraded"` otherwise:

```json
{
  "success": false,
  "data": {
    "status": "degraded",
    "dependencies": {
      "keycloak": { "status": "up", "latency": 9 },
      "operaton": { "status": "down", "error": "<the connection error>" },
      "cache": { "status": "up" }
    }
  }
}
```

The full response shape is on [Local Development — Verifying the setup](local-development.md#verifying-the-setup).

If `keycloak` is `"down"`: check `docker compose ps` and that `ronl-keycloak` is
healthy and listening on port 8080.  
If `operaton` is `"down"`: locally the engine is the `ronl-operaton` container.
Check `docker compose ps` and `docker compose logs operaton`, and check that
`OPERATON_BASE_URL` in `packages/backend/.env` is
`http://localhost:8081/engine-rest`. Without that key the backend falls back to
the shared remote engine.  
If `cache` is `"down"`: Redis (`ronl-redis`) is not reachable. This does not
make the check fail; the PA monitoring cache falls back to live fetches.

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

And point `VITE_API_URL` at it in `packages/frontend/.env.development.local`
(gitignored; it overrides the committed `.env.development`). Add
`http://localhost:<port>` origins to `CORS_ORIGIN` if you move a front end.

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
3. The realm holds 22 test users across eight tenants, all with password
   `test123`; see [Local Development — Test users](local-development.md#test-users)

If the users are missing, the realm import did not run, or ran from an older
realm file. Keycloak stores the realm in Postgres and skips the import when a
`ronl` realm already exists, so removing only `keycloak-data` does not bring it
back. Reset all volumes:

```bash
npm run docker:down:volumes
npm run docker:up
# Wait up to a minute for Keycloak to become healthy and import the realm
npm run dev
```

This also clears the audit database, Redis and the Operaton deployments, so
[deploy the fixtures again](local-development.md#the-engine-starts-empty).

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

The repository's `.gitattributes` sets `* text=auto eol=lf`, which keeps text
files LF on checkout and commit whatever your `core.autocrlf` says. You do not
need to change your Git configuration for this repository. If a file still shows
up as modified with only line-ending changes after you pull the `.gitattributes`
change, run `git add --renormalize .` once.

### `bash` not found, or scripts running in WSL

`npm ci`, `npm run dev` and the checks call `bash`. See
[Local Development — A bash shell is required](local-development.md#a-bash-shell-is-required).

---

## Emergency reset

When everything is broken and you want a clean slate:

```bash
# 1. Stop dev servers
Ctrl+C

# 2. Wipe Docker: containers and all four volumes
#    (Keycloak realm, audit database, Redis, Operaton deployments)
npm run docker:down:volumes

# 3. Reinstall exactly what package-lock.json records
#    (npm ci deletes node_modules itself)
npm ci
npm run build --workspace=@ronl/shared

# 4. Start
npm run docker:up
# Wait until docker compose ps shows the containers healthy
npm run dev
```

After this the local Operaton engine is empty. Deploy the process and decision
fixtures again before starting processes; see
[Local Development — The engine starts empty](local-development.md#the-engine-starts-empty).

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

# Keycloak: is the ronl realm served?
curl http://localhost:8080/realms/ronl/.well-known/openid-configuration

# Operaton engine version
curl -u demo:demo http://localhost:8081/engine-rest/version
```
