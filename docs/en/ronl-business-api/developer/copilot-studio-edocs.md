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

| Method | Endpoint                                      | Description                                                |
| ------ | --------------------------------------------- | ---------------------------------------------------------- |
| `GET`  | `/v1/edocs/status`                            | Returns service health and whether stub mode is active     |
| `POST` | `/v1/edocs/workspaces/ensure`                 | Creates or retrieves a project workspace by project number |
| `POST` | `/v1/edocs/documents`                         | Uploads a document to a workspace                          |
| `GET`  | `/v1/edocs/workspaces/:workspaceId/documents` | Lists all documents in a workspace                         |

The routes are registered in `packages/backend/src/index.ts`:

```typescript
import edocsRoutes from "./routes/edocs.routes";
// ...
app.use("/v1/edocs", edocsRoutes);
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

## eDOCS REST API specification notes

The service implementation was verified against the **eDOCS REST API v1.0.0** OpenAPI specification, available at [developer.opentext.com](https://developer.opentext.com/ce/products/edocs/apis/edocs-rest-api).

Three discrepancies were identified during implementation.

**Issue 1 — Session token extraction from `/connect` (fixed)**

The spec defines the `/connect` response as returning the session token via a `Set-Cookie` header, not `X-DM-DST`. The security scheme confirms that `X-DM-DST` is the header used on _subsequent requests_, with the note that the token value is found under "HEADERS" in the connect response. The `private async connect()` method in `edocs.service.ts` was updated to parse `Set-Cookie` and handle both the cookie-value format and a direct `X-DM-DST` header as a fallback, covering any server-side variation between eDOCS versions.

```
private async connect(): Promise<void> {
  // ...
  const response = await this.client.post('/connect', {
    data: {
      userid: config.edocs.userId,
      password: config.edocs.password,
      library: config.edocs.library,
    },
  });

  // The spec returns the session token as Set-Cookie on /connect.
  // Extract the token value from the first cookie.
  const setCookie = response.headers['set-cookie'];
  const cookieHeader = Array.isArray(setCookie) ? setCookie[0] : setCookie;
  const token = cookieHeader?.split(';')[0]?.split('=').slice(1).join('=') ?? undefined;

  if (!token) {
    throw new Error(
      'eDOCS connect() succeeded but no session token found in Set-Cookie response header'
    );
  }

  this.sessionToken = token;
  logger.info('Connected to eDOCS — session token cached');
}
```


**Issue 2 — `_restapi.ref` for workspace linking in document upload (unverified)**

The `UploadData` schema in the spec only documents `_restapi: { form_name: "..." }`. The `ref` object used to link an uploaded document to a workspace (`_restapi.ref.type = "workspace"`) is documented for the `/urls` endpoint but not explicitly for `/documents`. It is expected to work in practice — this is a known eDOCS REST API pattern — but must be confirmed against a live DOCUVITT server when credentials become available.

**Issue 3 — `CollectionResponse` shape (no action required)**

The spec defines `CollectionResponse → data → { set: {...}, list: [...] }`. The service correctly navigates this as `response.data?.data?.list`, where the outer `.data` is the HTTP response body and the inner `.data.list` follows the spec's structure.

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
