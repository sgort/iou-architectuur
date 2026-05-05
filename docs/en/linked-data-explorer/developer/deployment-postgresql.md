# PostgreSQL Deployment

The LDE backend requires a dedicated PostgreSQL Flexible Server for each environment. This is separate from the RONL Business API's `ronl-postgres-prod` instance — see [Infrastructure decisions](#infrastructure-decisions) for the rationale.

---

## Provisioning

### 1 — Create the Flexible Server

Create one server per environment in the Azure Portal or via CLI:

- ACC: resource group `RONL-Preproduction`
- PROD: resource group `RONL-Production`

Recommended tier: Burstable, 1–2 vCores.

### 2 — Create the database and user

Connect to the new server as the admin user and run:
```sql
CREATE USER lde_user WITH PASSWORD '<strong-password>';
CREATE DATABASE lde_assets OWNER lde_user;
GRANT ALL PRIVILEGES ON DATABASE lde_assets TO lde_user;
GRANT ALL ON SCHEMA public TO lde_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO lde_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO lde_user;
```

!!! warning "PostgreSQL 15+ public schema permissions"
    Azure PostgreSQL Flexible Server running PostgreSQL 15 or later revokes `CREATE` on the `public` schema from non-superusers by default. The `GRANT ALL ON SCHEMA public` statement is required — without it, the migration fails with `permission denied for schema public` and the backend crashes on startup.

### 3 — Configure App Settings
```bash
az webapp config appsettings set \
  --name ronl-linkeddata-backend-acc \
  --resource-group RONL-Preproduction \
  --settings \
    DATABASE_URL="postgresql://lde_user:<password>@lde-postgres-acc.postgres.database.azure.com:5432/lde_assets?sslmode=require"

```
```bash
az webapp config appsettings set \
  --name ronl-linkeddata-backend-prod \
  --resource-group RONL-Production \
  --settings \
    DATABASE_URL="postgresql://lde_user:<password>@lde-postgres-prod.postgres.database.azure.com:5432/lde_assets?sslmode=require"
```

`sslmode=require` is mandatory — Azure PostgreSQL Flexible Server enforces SSL.

### 4 — Deploy and verify

Push to the `acc` branch. The CI/CD pipeline builds and deploys the backend. On first startup `migrate()` creates all three tables automatically.

Check the App Service log stream for:
```
[DB] Migrations applied
Server started
```

Then smoke-test the asset endpoints:
```bash
curl https://acc.backend.linkeddata.open-regels.nl/v1/assets/bpmn
curl https://acc.backend.linkeddata.open-regels.nl/v1/assets/forms
curl https://acc.backend.linkeddata.open-regels.nl/v1/assets/documents
```

All three should return `{"success":true,"data":[]}`.

---

## Troubleshooting

### `permission denied for schema public`

**Symptom:** Backend crashes on startup with:
```
error: permission denied for schema public
code: '42501'
```

**Cause:** Azure PostgreSQL Flexible Server (PostgreSQL 15+) does not grant `CREATE` on the `public` schema to non-superusers by default.

**Fix:** Connect as the admin user to `lde_assets` and run:
```sql
GRANT ALL ON SCHEMA public TO lde_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO lde_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO lde_user;
```

The third statement covers future tables created by migrations.

To find the server name:
```bash
az postgres flexible-server list \
  --resource-group RONL-Preproduction \
  --query "[].{name:name, host:fullyQualifiedDomainName}" \
  --output table
```

---

### SSL warning on startup

**Symptom:** Log line at startup:
```
Warning: SECURITY WARNING: The SSL modes 'prefer', 'require', and 'verify-ca' are treated
as aliases for 'verify-full'.
```

**Cause:** `pg-connection-string` v2.x warning about upcoming v3 SSL semantics. Not an error — the connection succeeds.

**Suppress (optional):** Change the connection string to use `sslmode=verify-full` explicitly:
```
DATABASE_URL=...?sslmode=verify-full
```

---

### `DATABASE_URL` not configured

**Symptom:** Log line at startup:
```
[DB] Skipping migrations — database not configured
```

The backend starts successfully but all `/v1/assets/*` endpoints return `503 DB_NOT_CONFIGURED`.

**Fix:** Add `DATABASE_URL` to the App Service Application Settings. The App Service restarts automatically when settings are saved.

---

### Health check fails after deploy (`503`)

**Symptom:** CI/CD health check step reports HTTP 503 after deployment.

**Most likely cause:** The backend is crashing on startup — `migrate()` is throwing before `app.listen()` is reached. Check the App Service log stream for the actual error.

To retrieve historical logs:
```bash
az webapp log download \
  --name ronl-linkeddata-backend-acc \
  --resource-group RONL-Preproduction \
  --log-file acc-logs.zip
```

---

## Infrastructure decisions

The LDE uses its own dedicated PostgreSQL Flexible Server rather than sharing the RONL Business API's `ronl-postgres` instance for three reasons:

1. **Domain isolation** — The RONL Business API's `audit_logs` database stores compliance-classified security data under a 7-year AVG/BIO retention policy. BPMN processes, form schemas, and document templates are authoring assets with entirely different lifecycle semantics. They must not share a database boundary.

2. **Operational independence** — The LDE and RONL Business API are deployed independently, live in different Azure resource groups, and serve different users. Their databases must be independently operable: independently backed up, scaled, and reset.

3. **No shared-database precedent** — The existing pattern is one service → one database → one scoped user. Introducing a second service connection to an existing database would require either sharing credentials or manually provisioning a second database user on a server that has no tooling for it.

---

## Related pages

- [Asset Storage](asset-storage.md) — write-through cache and hydration architecture
- [Local Development — PostgreSQL setup](local-development.md#postgresql-setup-local)
- [Backend Architecture](backend.md)
- [API Reference — Asset Storage](../reference/api-reference.md#asset-storage)