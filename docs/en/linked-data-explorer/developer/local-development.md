# Local Development

This guide covers setting up the full local development environment: the Linked Data Explorer frontend and its backend. Both must run simultaneously because the frontend calls the backend for all SPARQL and Operaton operations.

---

## Prerequisites

- Node.js 20.0.0 or higher
- npm 10.0.0 or higher
- Git
- Access to the TriplyDB and Operaton remote services (no local setup needed — they are always available remotely)

---

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/sgort/linked-data-explorer.git
cd linked-data-explorer

# 2. Install all workspace dependencies
npm install
```

---

## Backend configuration

```bash
cd packages/backend
cp .env.example .env
```

Edit `.env`:

```env
# Server
NODE_ENV=development
PORT=3001
HOST=localhost

# CORS — must include both frontend dev ports
CORS_ORIGIN=http://localhost:3000,http://localhost:5173

# TriplyDB — default SPARQL endpoint
TRIPLYDB_ENDPOINT=https://api.open-regels.triply.cc/datasets/stevengort/DMN-discovery/services/DMN-discovery/sparql
TRIPLYDB_TIMEOUT=30000

# Operaton
OPERATON_BASE_URL=https://operaton.open-regels.nl/engine-rest
OPERATON_TIMEOUT=10000

# Logging
LOG_LEVEL=debug
LOG_FORMAT=json

# Performance
CHAIN_EXECUTION_TIMEOUT=5000
MAX_CHAIN_DEPTH=10
ENABLE_CACHING=false
```

---

## PostgreSQL setup (local)

For local development, reuse the `ronl-postgres` container already running as part of the RONL Business API stack. Create the LDE database and user once:
```bash
docker exec -it ronl-postgres psql -U postgres -c \
  "CREATE USER lde_user WITH PASSWORD 'lde_password';"

docker exec -it ronl-postgres psql -U postgres -c \
  "CREATE DATABASE lde_assets OWNER lde_user;"

docker exec -it ronl-postgres psql -U postgres -c \
  "GRANT ALL PRIVILEGES ON DATABASE lde_assets TO lde_user;"
```

Then add to `packages/backend/.env`:
```
DATABASE_URL=postgresql://lde_user:lde_password@localhost:5432/lde_assets
```

The migration runs automatically on `npm run dev` startup. Look for `[DB] Migrations applied` in the console.

To verify the tables were created:
```bash
docker exec -it ronl-postgres psql -U lde_user -d lde_assets -c "\dt"
```

If `DATABASE_URL` is absent, the backend logs `[DB] Skipping migrations — database not configured` and continues without asset storage — localStorage fallback remains fully functional for development.

!!! note "Shared container, isolated database"
    The `ronl-postgres` container hosts multiple databases. The LDE uses `lde_assets` with a dedicated `lde_user` scoped to that database only. The RONL Business API uses `audit_logs` with `audit_user`. The two databases are fully isolated.

---

## RoPA Records — local setup

### Seed example records

After the database is running and the backend has started (tables created by migration), seed the four example RoPA records from `packages/backend`:
```bash
cd packages/backend
npx ts-node --project tsconfig.json src/db/seed-ropa.ts
```

Expected output:
```
[seed-ropa] Seeding RoPA records…
[seed-ropa] AwbShellProcess (Flevoland) → <uuid>
[seed-ropa] TreeFellingPermitSubProcess → <uuid>
[seed-ropa] AwbZorgtoeslagProcess → <uuid>
[seed-ropa] ZorgtoeslagProvisionalSubProcess → <uuid>
[seed-ropa] Done.
```

The seed is idempotent — re-running it updates existing rows in place via `ON CONFLICT (bpmn_process_id) DO UPDATE`. It is safe to run multiple times.

### Verify records in the database
```bash
docker exec -it ronl-postgres psql -U lde_user -d lde_assets \
  -c "SELECT bpmn_process_id, process_level, status FROM ropa_records ORDER BY process_level;"
```

Expected output:
```
         bpmn_process_id          | process_level | status
----------------------------------+---------------+--------
 AwbShellProcess                  | shell         | active
 AwbZorgtoeslagProcess            | shell         | active
 TreeFellingPermitSubProcess      | subprocess    | active
 ZorgtoeslagProvisionalSubProcess | subprocess    | active
(4 rows)
```

### Verify the public endpoint
```bash
curl "http://localhost:3001/v1/ropa/public?organisation=flevoland" | jq '.data | length'
```

Should return `4`. If you get `0`, the `controller_name` values in the seeded records do not contain "flevoland" — re-run the seed after verifying the controller names in `src/db/seed-ropa.ts`.

### Test the public site locally

`packages/ropa-site/index.html` has the API URL hardcoded. For local development change it to the local backend:
```javascript
const API_URL =
  'http://localhost:3001/v1/ropa/public?organisation=flevoland';
```

Open the file directly in a browser (`file://`) or serve it:
```bash
cd packages/ropa-site
npx serve .
```

!!! warning "CORS when opening as file://"
    When `index.html` is opened directly from disk, the browser sends `Origin: null`. The global CORS middleware rejects `null` origins. The path-aware CORS fix in `index.ts` that serves `/v1/ropa/public` with `origin: '*'` bypasses this — but only if that fix is in place. If you see a CORS error when opening from `file://`, confirm `index.ts` has the path-aware cors middleware, not just the route-level cors in `ropa.public.routes.ts`.

!!! note "Revert before committing"
    Remember to revert `const API_URL` to the ACC or production URL before committing `packages/ropa-site/index.html`.

---

## Environment comparison

The table below summarises how the LDE stack differs between local development and ACC deployment.

| Aspect | Local development | ACC |
|---|---|---|
| Backend URL | `http://localhost:3001` | `https://acc.backend.linkeddata.open-regels.nl` |
| Frontend URL | `http://localhost:5173` | `https://acc.linkeddata.open-regels.nl` |
| PostgreSQL | `ronl-postgres` Docker container, `lde_assets` DB | Azure PostgreSQL Flexible Server, `lde_assets` DB |
| `DATABASE_URL` | `postgresql://lde_user:lde_password@localhost:5432/lde_assets` | Set as Azure App Service env var with `?sslmode=require` |
| DB migrations | Run automatically on `npm run dev` | Run automatically on App Service startup (CI/CD deploy) |
| RoPA seed | Run manually: `npx ts-node ... src/db/seed-ropa.ts` | Run manually once after first ACC deploy |
| RoPA public endpoint | `http://localhost:3001/v1/ropa/public` | `https://acc.backend.linkeddata.open-regels.nl/v1/ropa/public` |
| `ropa-site` API URL | `http://localhost:3001/v1/ropa/public` (hardcoded in `index.html`) | `https://acc.backend.linkeddata.open-regels.nl/v1/ropa/public` (hardcoded in `index.html`) |
| `ropa-site` deployment | Open `index.html` directly or `npx serve .` | Azure Static Web Apps (`ropa-flevoland-acc`), deployed via GitHub Actions on push to `acc` with path filter `packages/ropa-site/**` |
| CORS for public route | Path-aware middleware in `index.ts` bypasses `CORS_ORIGIN` whitelist | Same — `origin: '*'` for `/v1/ropa/public` regardless of `CORS_ORIGIN` env var |
| RoPA Editor | Available in LDE at `http://localhost:5173` under the ScrollText icon | Available at `https://acc.linkeddata.open-regels.nl` under the ScrollText icon |

---

## Frontend configuration

The frontend reads environment variables via Vite. The `packages/frontend/.env.development` file is pre-configured:

```env
VITE_API_BASE_URL=http://localhost:3001
VITE_OPERATON_BASE_URL=https://operaton.open-regels.nl/engine-rest
```

No changes needed for standard local development.

---

## Starting the services

Open three terminal windows.

### Docker readiness check (v1.5.1+)

Before starting the backend, the `npm run dev` script in `packages/backend` runs `scripts/check-docker.sh`. The script verifies the `ronl-postgres` container is up and healthy, fails fast with a clear remediation message if not, and prevents nodemon from starting against a broken database.

Coloured output:

- **Green** — container is running and healthy → dev server starts
- **Yellow** — container is running but not yet healthy (still initialising) → wait briefly and retry
- **Red** — container is missing, stopped, or Docker daemon not running → script prints the exact `docker start` or `docker run` command for the missing container and exits non-zero

If you bypass the check (e.g. running `nodemon` directly), the backend will still try to migrate against `DATABASE_URL` and you'll get a connection error at startup. Just run `npm run dev` instead.

### Convenience scripts at the repo root

Two scripts at the monorepo root let you start everything with one command:

```bash
npm run dev:full       # backend (with check-docker.sh) and frontend in parallel
npm run dev:backend    # backend only, with the Docker check
```

Both chain through to the per-workspace `npm run dev` so the docker check still runs for the backend.

### Per-terminal startup

**Terminal 1 — Backend:**

```bash
cd packages/backend
npm run dev
```

Expected output:
```
[INFO] Server started
[INFO] environment: development
[INFO] host: localhost
[INFO] port: 3001
[INFO] corsOrigin: http://localhost:3000,http://localhost:5173
[INFO] API available at: http://localhost:3001/v1
[INFO] Health check: http://localhost:3001/v1/health
```

**Terminal 2 — Frontend:**

```bash
cd packages/frontend
npm run dev
```

Expected output:
```
VITE v6.x ready in XXX ms
➜  Local:   http://localhost:5173/
```

The frontend runs at `http://localhost:5173`. The backend runs at `http://localhost:3001`.

---

## Verifying the setup

**Health check:**

```bash
curl http://localhost:3001/v1/health | jq '.'
```

Expected response:
```json
{
  "name": "Linked Data Explorer Backend",
  "version": "0.x.x",
  "environment": "development",
  "status": "healthy",
  "services": {
    "triplydb": { "status": "up", "latency": 150 },
    "operaton": { "status": "up", "latency": 120 }
  }
}
```

If either service shows `"status": "down"`, check your internet connection — both TriplyDB and Operaton are remote services.

**Browser check:**

1. Open `http://localhost:5173`
2. Click the GitBranch icon (Chain Builder)
3. DMN cards should load in the left panel within a few seconds
4. Open browser DevTools → Console: no CORS errors should appear

---

## Running backend tests

```bash
cd packages/backend
npm test                  # run all tests
npm run test:watch        # watch mode
npm run test:coverage     # with coverage report
```

---

## Code quality

```bash
# Lint and format (from repo root)
npm run lint              # lint all packages
npm run lint:fix          # auto-fix
npm run format            # prettier all packages
npm run check-format      # check without writing
```

Pre-commit hooks (husky + lint-staged) run lint and format automatically on staged files in `packages/frontend/`.

---

## Pushing to ACC

After local verification:

```bash
# From repo root
git add packages/backend/src/ packages/frontend/src/
git commit -m "feat: your description"
git push origin acc
```

Monitor the GitHub Actions run for the `acc` branch. The ACC frontend deploys to `https://acc.linkeddata.open-regels.nl` and the ACC backend to `https://acc.backend.linkeddata.open-regels.nl`. Verify the ACC deployment before opening a PR to `main`.
