# PostgreSQL (Azure)

The RONL Business API uses **Azure PostgreSQL Flexible Server** as its persistent store for audit logs. The database is provisioned per environment — `ronl-postgres-acc` for ACC and `ronl-postgres-prod` for production — and is accessed exclusively by the backend running on Azure App Service.

---

## Environments

| Environment | Server | Database | App Service |
|---|---|---|---|
| ACC | `ronl-postgres-acc.postgres.database.azure.com` | `audit_logs` | `ronl-business-api-acc` |
| PROD | `ronl-postgres-prod.postgres.database.azure.com` | `audit_logs` | `ronl-business-api-prod` |

Both environments use the same schema. The `audit_logs` database contains one table: `audit_logs` (request-level audit trail).

---

## Initial setup

Azure PostgreSQL Flexible Server does not run the local Docker init script (`config/postgres/init-databases.sql`) automatically. The database and schema must be created manually on first provisioning.

### 1. Open the firewall for your local IP

The server is locked down by default. Add a temporary rule to allow your machine:

```bash
az postgres flexible-server firewall-rule create \
  --resource-group rg-ronl-acc \
  --name ronl-postgres-acc \
  --rule-name allow-my-ip \
  --start-ip-address $(curl -s https://api.ipify.org) \
  --end-ip-address $(curl -s https://api.ipify.org)
```

### 2. Install the PostgreSQL client

```bash
sudo apt install postgresql-client -y
```

### 3. Connect to the server

```bash
psql "postgresql://pgadmin:<password>@ronl-postgres-acc.postgres.database.azure.com:5432/postgres?sslmode=require"
```

Connect to the default `postgres` database first. If `audit_logs` does not yet exist, create it:

```sql
CREATE DATABASE audit_logs;
```

Then reconnect to it:

```bash
psql "postgresql://pgadmin:<password>@ronl-postgres-acc.postgres.database.azure.com:5432/audit_logs?sslmode=require"
```

### 4. Create the schema

```sql
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

CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant_id ON audit_logs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_request_id ON audit_logs(request_id);
```

---

## Firewall configuration

Azure PostgreSQL Flexible Server has no inbound access by default. Two rules are required.

### Allow Azure App Service

This permits the App Service backend to reach the database. The special address range `0.0.0.0`–`0.0.0.0` is Azure's notation for "allow all Azure-internal traffic":

```bash
az postgres flexible-server firewall-rule create \
  --resource-group rg-ronl-acc \
  --name ronl-postgres-acc \
  --rule-name allow-azure-services \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

### Allow local access (temporary)

For schema migrations or manual queries, add your local IP as shown in [Initial setup](#initial-setup) above. Remove the rule when done:

```bash
az postgres flexible-server firewall-rule delete \
  --resource-group rg-ronl-acc \
  --name ronl-postgres-acc \
  --rule-name allow-my-ip
```

---

## Connecting the App Service

The backend reads `DATABASE_URL` from its environment. Set it on the App Service:

```bash
az webapp config appsettings set \
  --name ronl-business-api-acc \
  --resource-group rg-ronl-acc \
  --settings DATABASE_URL="postgresql://pgadmin:<password>@ronl-postgres-acc.postgres.database.azure.com:5432/audit_logs?sslmode=require"
```

`sslmode=require` is mandatory — Azure PostgreSQL Flexible Server enforces SSL. The connection string for the PROD environment uses `ronl-postgres-prod` and `rg-ronl-prod` accordingly.

The App Service restarts automatically when app settings are changed. The backend's `initDb()` call at startup will log a successful pool establishment:

```
Database connection pool established { poolMin: 2, poolMax: 10 }
```

If `DATABASE_URL` is missing or points to an unreachable host, the backend falls back to in-memory audit logging and logs a warning — it does not crash.

---

## Known issue — IP address format on Azure

Azure App Service sets `req.ip` in the format `x.x.x.x:port` (IP with port appended), whereas the `ip_address` column is of PostgreSQL type `inet`, which does not accept a port suffix. Every `INSERT` into `audit_logs` will fail with:

```
invalid input syntax for type inet: "77.161.155.118:40796"
```

This error is swallowed silently by `persistAuditLog()` — the API continues to function but no rows are written to the database.

The fix is in `packages/backend/src/services/audit.service.ts`, stripping the port before the insert:

```typescript
ipAddress: entry.ipAddress ? entry.ipAddress.replace(/:\d+$/, '') : null,
```

!!! note "Local development is not affected"
    `req.ip` on a local Node.js/Express server returns a plain IP without a port, so this issue only manifests on Azure App Service.

---

## Local development

Locally, PostgreSQL runs as a Docker container defined in `docker-compose.yml`. The schema is applied automatically on first start via `config/postgres/init-databases.sql`.

The local connection string in `.env.development`:

```
DATABASE_URL=postgresql://audit_user:audit_password@localhost:5432/audit_logs
```

No firewall configuration is needed for local development.

---

## Related documentation

- [Backend Deployment](backend.md) — App Service environment variable configuration
- [Environment Variables](../../references/environment-variables.md) — Full variable reference including `DATABASE_POOL_MIN` and `DATABASE_POOL_MAX`
- [Security & Compliance](../../features/security-compliance.md) — Audit log retention policy (7-year / 2555 days)
