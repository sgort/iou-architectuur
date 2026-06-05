# Environment Variables

The services are configured through environment variables and a generated `config.json`. This
page lists them. **Never commit real secrets** — the values shown are placeholders.

!!! danger "Treat `TRIPLY_KEY_R` as a secret"
    `TRIPLY_KEY_R` is a TriplyDB API token. Keep it in an untracked `.env` file or a secrets
    store (Key Vault in Azure). Do not paste real tokens into documentation, issues, or commits.

---

## Shared / backend variables

Set in `.env` (local) or injected by the deployment. Used by the backend and the Python
services.

| Variable | Example (placeholder) | Purpose |
|---|---|---|
| `TRIPLY_KEY_R` | `your-triply-api-key` | TriplyDB API token |
| `TRIPLY_ENDPOINT` | `https://api.open-regels.triply.cc/` | TriplyDB API base URL |
| `TRIPLY_URL` | `https://open-regels.triply.cc/` | TriplyDB web URL |
| `TRIPLY_DATASET` | `datasets/TNO/editor/sparql` | Dataset path used for SPARQL |
| `INT_BACKEND_URL` | `http://backend:3000` | Internal backend URL |
| `UNWRAP_BACKEND_URL` | `http://unwrap-api:5001` | Internal unwrap service URL |
| `NLP_BACKEND_URL` | `http://nlp-api:8081` | Internal NLP service URL |
| `WRAP_UP_BACKEND_URL` | `http://wrap-up-api:5002` | Internal wrap-up service URL |

---

## Frontend `config.json`

The Compose file injects a `config.json` mounted at `/data/config.json` for the web service:

```json
{
  "triply_endpoint": "https://api.open-regels.triply.cc/",
  "triply_url": "https://open-regels.triply.cc/",
  "triply_key_r": "${TRIPLY_KEY_R}",
  "triply_dataset": "datasets/tno/editor/sparql",
  "int_backend_url": "http://backend:3000",
  "ext_backend_url": "http://backend:3000",
  "unwrap_backend_url": "http://unwrap-api:5001",
  "nlp_backend_url": "http://nlp-api:8081",
  "wrap_up_backend_url": "http://wrap-up-api:5002"
}
```

The frontend's config store exposes `int_backend_url` and `ext_backend_url` to the API
service layer.

---

## Build-time frontend variables

Read via `process.env` in the frontend build:

| Variable | Purpose |
|---|---|
| `X_API_KEY` | Sent as `X-API-KEY` on `predict` and `process_and_save` requests |
| `VERSION` | Git commit hash, shown in the deployment-info welcome banner |
| `REPOSITORY_URL` | Repository URL for the welcome banner |
| `BRANCH` | Branch name for the welcome banner |

---

## Deployment (`deploy.sh`) variables

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `TRIPLY_KEY_R` | yes | — | Triply API token |
| `REGISTRY_PASSWORD` | yes | — | Container registry admin password |
| `REGISTRY_NAME` | yes | — | Registry name (without `.azurecr.io`) |
| `IMAGE_TAG` | no | current git commit | Image tag to deploy |
| `APP_NAME` | no | `name` parameter | Application name |
| `RESOURCE_GROUP` | no | `{APP_NAME}-{suffix}` | Resource group name |
| `LOCATION` | no | `westeurope` | Azure region |
| `TEMPLATE_FILE` | no | `infra/main.bicep` | Bicep template path |
| `PARAMETERS_FILE` | no | `infra/main.parameters.json` | Parameters file path |
| `ACA_DOMAIN` | (set by Bicep) | — | ACA default domain, used by nginx at runtime |

Non-secret Bicep parameters (`location`, `name`, `resourceGroupName`) live in
`infra/main.parameters.json`.
