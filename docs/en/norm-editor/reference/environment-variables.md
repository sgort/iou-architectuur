---
component: Norm Editor
---

# Environment Variables

The services are configured through environment variables. This page lists them, together with
the variables the deployment scripts read. **Never commit real secrets** — the values shown are
placeholders.

!!! danger "Treat `TRIPLY_KEY_R` as a secret"
    `TRIPLY_KEY_R` is a TriplyDB API token. Keep it in an untracked `.env` file or a secrets
    store (Key Vault in Azure). Do not paste real tokens into documentation, issues, or commits.

---

## Shared / backend variables

`docker-compose.yml` sets these on every service (`TRIPLY_KEY_R` comes from `.env`); in Azure,
`resources.bicep` sets them on every Container App, with the internal URLs pointing at
`http://<service>.internal.<environment default domain>`.

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
| `MODEL_PATH` | `/mnt/models` | Directory holding the NLP model directories; nlp-api falls back to `./` when unset. Compose sets it on every service, Azure on `nlp-api` only |

In Azure the Container Apps also get `VERSION` (the image tag), `REPOSITORY_URL` and `BRANCH`;
no service reads them at this release. The nginx sidecar gets only `ACA_DOMAIN` (the
environment's internal domain), which `nginx/docker-entrypoint.sh` substitutes into
`aca.conf` at start-up.

---

## Frontend `config.json`

The frontend calls the services on relative `/api/*` paths through nginx, so it needs no
endpoint configuration. Docker Compose provides no `config.json`. In Azure, `resources.bicep`
still mounts one as a secret volume at `/data/config.json` in the `web` container, with this
shape:

```json
{
  "triply_endpoint": "https://api.open-regels.triply.cc/",
  "triply_url": "https://open-regels.triply.cc/",
  "triply_key_r": "<TRIPLY_KEY_R>",
  "triply_dataset": "datasets/tno/editor/sparql",
  "int_backend_url": "http://backend.<domain>",
  "ext_backend_url": "http://backend.<domain>",
  "unwrap_backend_url": "http://unwrap-api.<domain>",
  "nlp_backend_url": "http://nlp-api.<domain>",
  "wrap_up_backend_url": "http://wrap-up-api.<domain>"
}
```

The SPA does not read it.

---

## Deployment (`deploy.sh`) variables

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `TRIPLY_KEY_R` | yes | — | Triply API token |
| `REGISTRY_PASSWORD` | yes | — | Container registry admin password |
| `REGISTRY_NAME` | yes | — | Registry name (without `.azurecr.io`); also the registry username |
| `SSL_CERTIFICATE_DATA` | yes | — | Base64-encoded PFX for HTTPS on the Application Gateway |
| `SSL_CERTIFICATE_PASSWORD` | yes | — | Password of that PFX |
| `DNS_ZONE_NAME` | yes, in practice | empty | DNS zone (domain) to create; passed as `dnsZoneName` only when set, and `main.bicep` has no default for it |
| `APP_NAME` | no | `regels` | Bicep `name`: prefix of both resource groups and of the resource names |
| `ENVIRONMENT` | no | `acceptance` | Bicep `environment`: the environment resource group `{APP_NAME}-{ENVIRONMENT}-rg`; `production` puts the site on the zone apex, anything else on `acc.<zone>` |
| `IMAGE_TAG` | no | `git rev-parse --short HEAD` | Image tag to deploy |
| `REVISION_SUFFIX` | no | deployment timestamp (set in Bicep) | Container App revision suffix, passed as `revisionSuffix` only when set |
| `LOCATION` | no | `westeurope` | Location of the subscription deployment (`--location`); it is not passed as the Bicep `location` parameter, so the resources take that parameter's default, `westeurope` |
| `TEMPLATE_FILE` | no | `infra/main.bicep` | Bicep template path |
| `PARAMETERS_FILE` | no | `infra/main.parameters.json` | Read but not passed to the deployment |
| `RESOURCE_GROUP_SUFFIX` | no | `rg` | Read but not used |
| `WEB_APP_NAME` | no | `web` | Read but not used |
| `OUTPUT_DIR` | no | `$PWD/certs` | Read but not used (`issue-cert.sh` has its own) |

Resource group names are not configurable through `deploy.sh`: `main.bicep` derives
`{APP_NAME}-{ENVIRONMENT}-rg` and `{APP_NAME}-general-rg`. See
[Deployment](../developer/deployment.md).

---

## Helper script variables

| Script | Variable | Required | Default | Purpose |
|---|---|---|---|---|
| `scripts/bootstrap-dns.sh` | `DNS_ZONE_NAME` | yes | — | Zone to create |
| | `RESOURCE_GROUP` | yes | — | Group for the zone (created if absent) |
| | `LOCATION` | no | `westeurope` | Region of that group |
| `scripts/issue-cert.sh` | `DOMAIN` | yes | — | Certificate name; `www.DOMAIN` is added |
| | `EMAIL` | yes | — | Let's Encrypt account e-mail |
| | `RESOURCE_GROUP` | yes | — | Group holding the DNS zone |
| | `DNS_ZONE_NAME` | no | `DOMAIN` | Zone used for the DNS-01 challenge |
| | `PFX_PASSWORD` | no | random (`openssl rand -hex 16`) | Password of the exported PFX |
| | `OUTPUT_DIR` | no | `$PWD/certs` | Where `cert.pfx`, the Let's Encrypt state and the cached service principal go |
| | `SP_CLIENT_ID`, `SP_CLIENT_SECRET`, `SP_TENANT_ID`, `SP_SUBSCRIPTION_ID` | no | cached / created | An existing service principal instead of the cached or newly created one |
| `scripts/update-revision.sh` | `APP_NAME` | no | `regels-acceptance` | Prefix of the resource group |
| | `RESOURCE_GROUP` | no | `{APP_NAME}-rg` | Group holding the Container Apps |
| | `REVISION_SUFFIX` | no | UTC timestamp | Suffix of the new revisions (lowercased, prefixed with `r`) |
