# PROD Deployment Notes — v2.9.1

**Date:** 24 March 2026  
**Branch:** `acc` → `main` (v2.0.2 → v2.9.1)

---

## Pre-deploy checklist

### 1. PostgreSQL — audit_logs schema

The `audit_logs` database existed on PROD but contained no tables. Run the following against the PROD PostgreSQL instance connected as a superuser (`pgadmin`):

```sql
\c audit_logs

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    tenant_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255) NOT NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    result VARCHAR(50) NOT NULL,
    error_message TEXT,
    request_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_tenant_id ON audit_logs(tenant_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_request_id ON audit_logs(request_id);

GRANT ALL PRIVILEGES ON TABLE audit_logs TO audit_user;
GRANT ALL PRIVILEGES ON SEQUENCE audit_logs_id_seq TO audit_user;
```

> The `tenants` table in `init-databases.sql` is bookkeeping only — the backend never queries it at runtime. Skip it.

### 2. Azure App Service — new environment variables

All of the following are new since v2.0.2:

```bash
az webapp config appsettings set \
  --name ronl-business-api-prod \
  --resource-group rg-ronl-prod \
  --settings \
    DATABASE_URL="postgresql://audit_user:<password>@ronl-postgres-prod.postgres.database.azure.com:5432/audit_logs?sslmode=require" \
    DATABASE_POOL_MIN="2" \
    DATABASE_POOL_MAX="10" \
    EDOCS_BASE_URL="" \
    EDOCS_LIBRARY="DOCUVITT" \
    EDOCS_USER_ID="" \
    EDOCS_PASSWORD="" \
    EDOCS_STUB_MODE="true" \
    OPERATON_M2M_BASE_URL="https://operaton-doc.open-regels.nl/engine-rest" \
    OPERATON_M2M_USERNAME="" \
    OPERATON_M2M_PASSWORD="" \
    RONL_SPARQL_ENDPOINT=""
```

> `EDOCS_STUB_MODE=true` keeps eDOCS in stub mode until the `copilot-studio-edocs` Keycloak client secret is rotated and live DOCUVITT credentials are configured.

### 3. PostgreSQL firewall — App Service outbound IPs

Azure PostgreSQL Flexible Server requires explicit firewall rules per outbound IP. Get the full list from the App Service:

```bash
az webapp show \
  --name ronl-business-api-prod \
  --resource-group rg-ronl-prod \
  --query outboundIpAddresses \
  -o tsv
```

Add a rule for each IP returned:

```bash
az postgres flexible-server firewall-rule create \
  --resource-group rg-ronl-prod \
  --name ronl-postgres-prod \
  --rule-name allow-appservice-prod \
  --start-ip-address <ip> \
  --end-ip-address <ip>
```

To look up the PostgreSQL server name:

```bash
az postgres flexible-server list \
  --resource-group rg-ronl-prod \
  --query "[].name" \
  -o tsv
```

### 4. Keycloak — realm import

The realm JSON accumulates client, mapper, and user additions across versions. A full re-import is the reliable path.

```bash
docker cp /path/to/ronl-realm.json keycloak-prod:/tmp/ronl-realm.json

docker exec keycloak-prod /opt/keycloak/bin/kc.sh import \
  --file /tmp/ronl-realm.json \
  --override true
```

After the import, regenerate secrets for the two M2M clients via the Keycloak admin console (the realm JSON ships with `change-me-in-keycloak-console`):

- `copilot-studio-edocs` → Clients → Credentials → Regenerate
- `operaton-mcp-client` → Clients → Credentials → Regenerate

> `--override true` does not backfill `organisation_type` on pre-existing users. Set it manually for any user created before v2.4.1: Users → [user] → Attributes → `organisation_type` = `municipality`.

---

## Debugging — audit log 500 on PROD

### Symptom

`GET /v1/admin/audit?limit=50&offset=0` returned HTTP 500 immediately after deployment. The user had the `admin` role and a valid JWT — auth was not the issue.

### Step 1 — tail the App Service logs

```bash
az webapp log tail \
  --name ronl-business-api-prod \
  --resource-group rg-ronl-prod
```

Trigger the request from the browser. The relevant log line:

```
"error":"no pg_hba.conf entry for host \"20.73.200.86\", user \"audit_user\",
database \"audit_logs\", no encryption"
```

Two problems in that single error:

1. The App Service outbound IP `20.73.200.86` was not in the PostgreSQL firewall allowlist.
2. The connection string lacked `?sslmode=require`, which Azure PostgreSQL Flexible Server mandates.

### Step 2 — confirm the table was missing

Connected to the PROD database via psql:

```
audit_logs=> \dt
Did not find any relations.
```

The `audit_logs` database existed but had never had the schema applied. The schema creation SQL above (pre-deploy step 1) resolved this.

### Step 3 — add firewall rules and SSL to the connection string

Added firewall rules for all App Service outbound IPs (see pre-deploy step 3) and updated `DATABASE_URL` with `?sslmode=require` (see pre-deploy step 2).

The App Service restarted automatically after the settings update. No backend restart was needed after the schema was created — pg-promise reconnects on the next request.

### Resolution

Audit log endpoint returned HTTP 200 with 9 records after all three fixes were in place.

---

## Execution order

1. Apply PostgreSQL schema (psql)
2. Set App Service environment variables (`az webapp config appsettings set`)
3. Add PostgreSQL firewall rules (`az postgres flexible-server firewall-rule create`)
4. Deploy backend zip (manual steps)
5. Import Keycloak realm (`docker cp` + `kc.sh import`)
6. Merge PR → GitHub Actions deploys frontend automatically
