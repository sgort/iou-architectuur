# Copilot Studio — eDOCS OAuth Integration

This page documents how Microsoft Copilot Studio can connect to the eDOCS document management system using OAuth 2.0 via the RONL Business API and Keycloak.

---

## Architecture

Copilot Studio never calls eDOCS directly. It authenticates against Keycloak to obtain a Bearer token, then calls the RONL Business API which holds the eDOCS credentials and proxies the request.

```
Copilot Studio
    │
    │  1. POST /token  (client_credentials)
    ▼
Keycloak (acc.keycloak.open-regels.nl)
    │
    │  2. access_token (JWT, aud: ronl-business-api)
    ▼
Copilot Studio
    │
    │  3. GET /v1/edocs/*  Authorization: Bearer <token>
    ▼
RONL Business API (acc.api.open-regels.nl)
    │  jwtMiddleware validates token
    │
    │  4. proxies with eDOCS service credentials
    ▼
eDOCS DOCUVITT
```

The RONL Business API is the OAuth 2.0 resource server. Keycloak is the authorisation server. Copilot Studio is the client.

---

## eDOCS routes

`packages/backend/src/routes/edocs.routes.ts` registers four endpoints under `/v1/edocs`. All are protected by `jwtMiddleware` — a valid Bearer token issued by Keycloak is required on every request.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/v1/edocs/status` | Returns service health and whether stub mode is active |
| `POST` | `/v1/edocs/workspaces/ensure` | Creates or retrieves a project workspace by project number |
| `POST` | `/v1/edocs/documents` | Uploads a document to a workspace |
| `GET` | `/v1/edocs/workspaces/:workspaceId/documents` | Lists all documents in a workspace |

The routes are registered in `packages/backend/src/index.ts`:

```typescript
import edocsRoutes from './routes/edocs.routes';
// ...
app.use('/v1/edocs', edocsRoutes);
```

---

## Stub mode

When `EDOCS_STUB_MODE=true` (the current default on ACC), all four endpoints return realistic fake responses. No live eDOCS server is contacted. The stub is fully transparent to callers — the response shape is identical to what a live server returns.

This allows Copilot Studio to be connected and tested end-to-end before live DOCUVITT credentials are available.

The `GET /v1/edocs/status` response indicates which mode is active:

```json
{
  "success": true,
  "data": {
    "status": "stub",
    "library": "DOCUVITT",
    "stubMode": true
  },
  "timestamp": "2026-03-14T18:39:52.962Z"
}
```

When connected to a live server, `status` will be `"up"` and `stubMode` will be `false`.

!!! warning "Rotate the client secret before switching to live mode"
    The `copilot-studio-edocs` Keycloak client secret currently used on ACC is acceptable while the stub is active — it provides access only to fake data. As soon as `EDOCS_STUB_MODE=false` is set and real DOCUVITT credentials are configured, generate a new client secret in the Keycloak admin console and update the Copilot Studio connector accordingly.

---

## Keycloak client

A dedicated Keycloak client `copilot-studio-edocs` is registered in the `ronl` realm on ACC. It uses the **Client Credentials** grant — no browser redirect or user login is involved.

| Setting | Value |
|---|---|
| **Client ID** | `copilot-studio-edocs` |
| **Grant type** | `client_credentials` |
| **Token endpoint** | `https://acc.keycloak.open-regels.nl/realms/ronl/protocol/openid-connect/token` |
| **Audience** | `ronl-business-api` (set via audience mapper) |

The token endpoint for production will be `https://keycloak.open-regels.nl/realms/ronl/protocol/openid-connect/token`.

---

## Testing with curl

### 1. Obtain a token

```bash
TOKEN=$(curl -s -X POST \
  https://acc.keycloak.open-regels.nl/realms/ronl/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=copilot-studio-edocs" \
  -d "client_secret=ti2rTdYKMexu4LtUeHaw2ZSp70b7nFb0" \
  | jq -r .access_token)
```

### 2. Check service status

```bash
curl -s \
  https://acc.api.open-regels.nl/v1/edocs/status \
  -H "Authorization: Bearer $TOKEN" \
  | jq .
```

### 3. List documents in a workspace

```bash
curl -s \
  https://acc.api.open-regels.nl/v1/edocs/workspaces/2993896/documents \
  -H "Authorization: Bearer $TOKEN" \
  | jq .
```

Expected response:

```json
{
  "success": true,
  "data": {
    "workspaceId": "2993896",
    "documents": [
      {
        "documentNumber": "2993898",
        "filename": "rip-intake-report.pdf",
        "createdAt": "2026-03-14T18:40:08.694Z",
        "type": "Intakeverslag"
      },
      {
        "documentNumber": "2993899",
        "filename": "rip-psu-report.pdf",
        "createdAt": "2026-03-14T18:40:08.694Z",
        "type": "PSU-verslag"
      }
    ]
  },
  "timestamp": "2026-03-14T18:40:08.694Z"
}
```

---

## Configuring Copilot Studio

In the Copilot Studio custom connector, configure OAuth 2.0 as follows:

| Field | Value |
|---|---|
| **Grant type** | Client Credentials |
| **Token URL** | `https://acc.keycloak.open-regels.nl/realms/ronl/protocol/openid-connect/token` |
| **Client ID** | `copilot-studio-edocs` |
| **Client Secret** | *(from Keycloak admin console → Clients → copilot-studio-edocs → Credentials)* |
| **Scope** | `openid` |
| **Base URL** | `https://acc.api.open-regels.nl/v1/edocs` |

---

## Switching to live mode (DOCUVITT)

No code changes are required. Switching to a live eDOCS server is purely a configuration change.

### 1. Set the environment variables on Azure App Service

```bash
az webapp config appsettings set \
  --name ronl-business-api-acc \
  --resource-group rg-ronl-acc \
  --settings \
    EDOCS_BASE_URL="https://<docuvitt-host>/edocsapi/v1.0" \
    EDOCS_LIBRARY="DOCUVITT" \
    EDOCS_USER_ID="<user-id-from-credentials>" \
    EDOCS_PASSWORD="<password-from-credentials>" \
    EDOCS_STUB_MODE="false"
```

Do not put these values in any `.env` file in the repository.

### 2. Restart the App Service

Azure restarts the App Service automatically when Application settings are saved. Confirm the deployment slot comes back healthy.

### 3. Verify the switch

```bash
TOKEN=$(curl -s -X POST \
  https://acc.keycloak.open-regels.nl/realms/ronl/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials" \
  -d "client_id=copilot-studio-edocs" \
  -d "client_secret=<current-secret>" \
  | jq -r .access_token)

curl -s https://acc.api.open-regels.nl/v1/edocs/status \
  -H "Authorization: Bearer $TOKEN" | jq .
```

`status` should now be `"up"` and `stubMode` should be `false`. A `502` response means `EDOCS_BASE_URL` or the credentials are incorrect.

### 4. Rotate the Keycloak client secret

Once real DOCUVITT credentials are active, the existing client secret must be rotated:

1. Keycloak admin console on ACC → Clients → `copilot-studio-edocs` → Credentials → **Regenerate**
2. Update the Copilot Studio connector with the new secret

### 5. Repeat for production when ready

```bash
az webapp config appsettings set \
  --name ronl-business-api-prod \
  --resource-group rg-ronl-prod \
  --settings \
    EDOCS_BASE_URL="https://<docuvitt-host>/edocsapi/v1.0" \
    EDOCS_LIBRARY="DOCUVITT" \
    EDOCS_USER_ID="<user-id-from-credentials>" \
    EDOCS_PASSWORD="<password-from-credentials>" \
    EDOCS_STUB_MODE="false"
```

And rotate the client secret on `keycloak.open-regels.nl` as in step 4.