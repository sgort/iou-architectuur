# Copilot Studio — eDOCS OAuth Integration

This page documents how Microsoft Copilot Studio can connect to the eDOCS document management system using OAuth 2.0 via the RONL Business API and Keycloak.

!!! danger "No working Copilot Studio connector yet — Client Credentials isn't supported the way this page assumes"
    Copilot Studio / Power Platform custom connectors do not generally support arbitrary OAuth 2.0 **Client Credentials** grants for custom connectors the same way they support interactive OAuth. The built-in OAuth experience in Power Platform custom connectors is primarily designed for **delegated user authentication** — not a machine-to-machine `client_credentials` exchange like the one `copilot-studio-edocs` performs against Keycloak. In practice, the architecture below (Copilot Studio itself obtaining the Bearer token) has **not** been successfully wired up as a working custom connector.

    **Recommended approach instead**: don't put OAuth in Copilot Studio at all. Have Copilot Studio call this backend with no OAuth (or a simple API key), and let the backend perform the `client_credentials` exchange with Keycloak itself before proxying to eDOCS:

    ```
    Copilot Studio
          │
          │  (no OAuth)
          ▼
    RONL Business API
          │
          ├── POST /token (client_credentials)
          └── OpenText eDOCS
    ```

    This is the same shape already proven working for the [AI Assistant's own eDOCS MCP source](mcp-ai-assistant.md#edocs-tools-edocs) — it performs its own `client_credentials` exchange against a dedicated Keycloak client (`edocs-mcp-client`) internally, rather than expecting an external caller to hold OAuth credentials for this API at all. The rest of this page (Keycloak client setup, the `/v1/edocs` routes, stub mode, curl testing) still accurately describes the resource-server side and remains useful reference material — only the "Copilot Studio performs the `client_credentials` dance itself" framing in the diagram below is unproven as a working Power Platform custom connector configuration.

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

`packages/backend/src/routes/edocs.routes.ts` registers the `/v1/edocs` surface — workspace and document lifecycle endpoints, all protected by `jwtMiddleware` (a valid Bearer token issued by Keycloak is required on every request). For the full, current endpoint list and request/response shapes, see [API Endpoints — eDOCS](../reference/api-endpoints.md#edocs); for live-tested results and known issues per endpoint, see [eDOCS — Live Testing](testing/edocs-live-testing.md).

The routes are registered in `packages/backend/src/index.ts`:

```typescript
import edocsRoutes from "./routes/edocs.routes";
// ...
app.use("/v1/edocs", edocsRoutes);
```

---

## Stub mode

When `EDOCS_STUB_MODE=true` (the current default on ACC), every `/v1/edocs` endpoint returns realistic fake responses. No live eDOCS server is contacted. The stub is fully transparent to callers — the response shape is identical to what a live server returns.

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
  "timestamp": "2026-03-14T20:32:47.462Z"
}
```

When connected to a live server, `status` will be `"up"` and `stubMode` will be `false`.

!!! warning "Rotate the client secret before switching to live mode"
    The `copilot-studio-edocs` Keycloak client secret currently used on ACC is acceptable while the stub is active — it provides access only to fake data. As soon as `EDOCS_STUB_MODE=false` is set and real DOCUVITT credentials are configured, generate a new client secret in the Keycloak admin console and update the Copilot Studio connector accordingly.

---

## Keycloak client

A dedicated Keycloak client `copilot-studio-edocs` is registered in the `ronl` realm on ACC. It uses the **Client Credentials** grant — no browser redirect or user login is involved.

| Setting            | Value                                                                           |
| ------------------ | ------------------------------------------------------------------------------- |
| **Client ID**      | `copilot-studio-edocs`                                                          |
| **Grant type**     | `client_credentials`                                                            |
| **Token endpoint** | `https://acc.keycloak.open-regels.nl/realms/ronl/protocol/openid-connect/token` |
| **Audience**       | `ronl-business-api` (set via audience mapper)                                   |

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
        "id": "stub-doc-1",
        "name": "rip-intake-report.pdf",
        "documentNumber": "2993898"
      },
      {
        "id": "stub-doc-2",
        "name": "rip-psu-report.pdf",
        "documentNumber": "2993899"
      }
    ]
  },
  "timestamp": "2026-03-14T20:32:53.462Z"
}
```

---

## Configuring Copilot Studio

In the Copilot Studio custom connector, configure OAuth 2.0 as follows:

| Field             | Value                                                                           |
| ----------------- | ------------------------------------------------------------------------------- |
| **Grant type**    | Client Credentials                                                              |
| **Token URL**     | `https://acc.keycloak.open-regels.nl/realms/ronl/protocol/openid-connect/token` |
| **Client ID**     | `copilot-studio-edocs`                                                          |
| **Client Secret** | _(from Keycloak admin console → Clients → copilot-studio-edocs → Credentials)_  |
| **Scope**         | `openid`                                                                        |
| **Base URL**      | `https://acc.api.open-regels.nl/v1/edocs`                                       |

---

## eDOCS REST API — spec vs. reality

The service implementation started from the **eDOCS REST API v1.0.0** OpenAPI specification ([developer.opentext.com](https://developer.opentext.com/ce/products/edocs/apis/edocs-rest-api)), but live testing against a real DM server (`infocenter-test.flevoland.nl`) found several places where the spec doesn't match actual server behaviour — wrong response shapes, an undocumented required field, and an upload path the spec implies works but doesn't. See [eDOCS — Live Testing](testing/edocs-live-testing.md) for the full, current list — that page is now the source of truth for eDOCS implementation details; this page stays focused on the Copilot Studio / OAuth integration itself.

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

Azure restarts the App Service automatically when Application settings are saved. Confirm the slot is back up:
 
```bash
az webapp show \
  --name ronl-business-api-acc \
  --resource-group rg-ronl-acc \
  --query "state" \
  --output tsv
```
 
Then confirm the application itself is healthy:
 
```bash
curl -s https://acc.api.open-regels.nl/v1/health | jq .data.status
```
 
`Running` from Azure confirms the process started. `"healthy"` from the health endpoint confirms Express is bound and all dependencies are reachable.

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
    EDOCS_BASE_URL="https://<docuvitp-host>/edocsapi/v1.0" \
    EDOCS_LIBRARY="DOCUVITP" \
    EDOCS_USER_ID="<user-id-from-credentials>" \
    EDOCS_PASSWORD="<password-from-credentials>" \
    EDOCS_STUB_MODE="false"
```

And rotate the client secret on `keycloak.open-regels.nl` as in step 4.
