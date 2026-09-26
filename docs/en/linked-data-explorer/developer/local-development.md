---
component: Linked Data Explorer
---

# Local Development

This guide sets up the Linked Data Explorer on a workstation: the frontend, the backend, and the two containers the backend needs from the RONL Business API stack. The frontend sends every SPARQL and Operaton call through the backend, so both run at the same time.

---

## Prerequisites

| Requirement | Why |
|---|---|
| **Node.js 24.21.0** | The version `.nvmrc` names, and the one CI builds and tests on. `package.json` accepts `>=22.23.2`. |
| **npm 11.10 or newer** (recommended) | `.npmrc` sets `min-release-age=14`, a 14-day cooldown on newly published versions. Older npm ignores the setting without a warning, so `scripts/check-deps.sh` warns at every dev-server start and push when npm is older than 11.10. |
| **bash on `PATH`** | The root scripts run `bash scripts/check-deps.sh`, and the backend's `dev` script runs `bash scripts/check-docker.sh`. |
| **Docker** | The backend's Docker check calls `docker info` and `docker inspect` from that bash. |
| **Git** | |
| **The RONL Business API stack** | Its `postgres` and `operaton` services, as the containers `ronl-postgres` and `ronl-operaton`. |

!!! warning "Windows: `bash` must be Git Bash"
    npm runs package scripts through `cmd.exe` on Windows, so `bash` in those scripts resolves through the Windows `PATH`. It must resolve to Git for Windows' bash, and the Docker CLI must be reachable from that bash.

**Which services are local and which are remote:**

| Service | Where it runs locally |
|---|---|
| PostgreSQL | `ronl-postgres` container, host port `5432` |
| Operaton | `ronl-operaton` container, `http://localhost:8081/engine-rest` |
| TriplyDB | Remote: `api.open-regels.triply.cc` |
| DSO APIs | Remote: the Omgevingswet pre-production and production services. The DSO Explorer needs a DSO API key. |

`ronl-operaton` is Operaton 2.1.5 on a file-based H2 database. It starts after a one-shot `operaton-init` container that hands the `operaton-data` volume to the engine's non-root user, so a fresh volume does not fail on permissions. How to bring up the stack is described in [RONL Business API — Local Development](../../ronl-business-api/developer/local-development.md).

---

## Install

```bash
git clone https://github.com/sgort/linked-data-explorer.git
cd linked-data-explorer
npm ci
```

`npm ci`, not `npm install`: it installs exactly what `package-lock.json` records and never re-resolves version ranges. Two root lifecycle scripts run with it:

- `postinstall` (`scripts/write-deps-marker.mjs`) copies `package-lock.json` to `node_modules/.package-lock-installed.json`. `npm run deps:check` compares the lockfile against this snapshot later.
- `prepare` runs `husky || true`, which installs the Git hooks.

---

## Backend configuration

```bash
cd packages/backend
cp .env.example .env
```

`.env.example` is a working local file as it stands. The backend does not start without a `.env`: `src/utils/config.ts` validates its configuration when the module loads and throws `Missing required configuration: triplydb.endpoint, operaton.baseUrl` when those two values are empty. The only exception is `NODE_ENV=test`.

The keys that matter locally:

| Key | Value in `.env.example` | What it does |
|---|---|---|
| `PORT` / `HOST` | `3001` / `localhost` | Where the backend listens |
| `CORS_ORIGIN` | `http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:5174` and the four deployed LDE and CPSV Editor origins | Credentialed CORS allowlist. The LDE frontend runs on `3000`. The comment above the key says that this is the local list and not a template for the deployed tiers. |
| `TRIPLYDB_ENDPOINT` | The `DMN-discovery` SPARQL service on `api.open-regels.triply.cc` | Default SPARQL endpoint (required) |
| `ALLOW_LOCAL_ENDPOINTS` | `true` | Admits `http:` and local SPARQL endpoints (see below) |
| `OPERATON_BASE_URL` | `http://localhost:8081/engine-rest` | The local `ronl-operaton` container (required) |
| `LOG_LEVEL` / `LOG_FORMAT` | `info` / `json` | `json` writes one JSON object per line. Any other value, such as `pretty`, writes coloured, timestamped lines. |
| `EDOCS_STUB_MODE` | `true` | eDOCS calls are stubbed. Stub mode is also the default when the key is absent. |
| `DATABASE_URL` | `postgresql://lde_user:lde_password@localhost:5432/lde_assets` | Asset storage (see [PostgreSQL setup](#postgresql-setup-local)) |
| `DSO_API_KEY` / `DSO_API_KEY_PROD` | `your-dso-api-key-here` | Replace these with real keys to use the DSO Explorer. The DSO base URLs default to pre-production, and the `_PROD` variants hold the production ones. |
| `DEPLOYMENT_ENV` | commented out | Tier label. Falls back to `NODE_ENV`, so leave it unset locally. |

**Why `ALLOW_LOCAL_ENDPOINTS`.** Since v2026.09.5, the backend refuses any caller-supplied endpoint that does not use `https:` or that points to an internal address, including `localhost`. That is right for ACC and production and wrong for a laptop, where the useful endpoints are local. `ALLOW_LOCAL_ENDPOINTS=true` admits them. It takes effect only for the exact value `true`. For the same reason, the frontend's **Local Jena** endpoint preset appears only in development builds. See the [outbound guard](backend.md#outbound-guard).

The backend's Jest setup, `scripts/jest-env.cjs`, pins `ALLOW_LOCAL_ENDPOINTS=false` and `TRIPLYDB_ALLOWED_HOSTS` to their production values before any module reads `.env`. This setting in your `.env` therefore does not change what the tests assert. Without that pin, 46 outbound-guard tests failed on a machine configured for local Jena.

---

## PostgreSQL setup (local)

Locally, the LDE reuses the `ronl-postgres` container from the RONL Business API stack. That stack's init script does not create the LDE database, so create the database and user once. These are the commands `.env.example` documents:

```bash
docker exec -it ronl-postgres psql -U postgres -c "CREATE USER lde_user WITH PASSWORD 'lde_password';"
docker exec -it ronl-postgres psql -U postgres -c "CREATE DATABASE lde_assets OWNER lde_user;"
docker exec -it ronl-postgres psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE lde_assets TO lde_user;"
```

The `DATABASE_URL` in the copied `.env` already points at this database.

The backend runs its migrations on every start, before it begins listening. Look for `[DB] Migrations applied` in the log. To list the tables:

```bash
docker exec -it ronl-postgres psql -U lde_user -d lde_assets -c "\dt"
```

When `DATABASE_URL` is empty, the backend logs `[DB] Skipping migrations — database not configured` and runs without asset storage. The frontend's localStorage fallback keeps working for development.

!!! note "Shared container, isolated database"
    The `ronl-postgres` container hosts several databases. The LDE uses `lde_assets` with a dedicated `lde_user`. The RONL Business API uses `audit_logs` with `audit_user`. The two databases are fully isolated.

---

## Frontend configuration

Vite reads `packages/frontend/.env.development`, which is committed and needs no changes:

```env
VITE_API_BASE_URL=http://localhost:3001
VITE_CPSV_EDITOR_URL=http://localhost:3002
```

`VITE_CPSV_EDITOR_URL` is the CPSV Editor that the DSO-to-DMN publish handoff opens. Run the editor on port `3002` locally, because the LDE's dev server uses `3000`. The frontend has no Operaton setting: since v2026.09.6, the deploy modal asks the backend which Operaton it deploys to.

---

## Starting the services

Start the `ronl-postgres` and `ronl-operaton` containers first. Then, from the repository root, use one terminal:

```bash
npm run dev:full       # backend and frontend together (concurrently)
```

or two terminals:

```bash
npm run dev:backend    # terminal 1: backend
npm run dev            # terminal 2: frontend
```

| URL | Service |
|---|---|
| `http://localhost:3000` | Frontend (Vite also binds `0.0.0.0` and prints a Network address) |
| `http://localhost:3001` | Backend: root page, `/v1`, `/v1/health`, `/v1/openapi.json` |

### The checks that run first

**Dependency check.** All three root scripts run `npm run deps:check` (`scripts/check-deps.sh`) first. It compares `package-lock.json` with the snapshot taken at the last install, ignoring the repository's own version numbers. When they differ, it stops and names the fix, `npm ci`. It also warns when npm is older than 11.10. A `git merge --ff-only` brings in lockfile changes and installs nothing, and this check is what says so. On 14 September 2026, a routine fast-forward of `acc` left one workstation with 152 packages at a different version and 95 missing compared with what CI tests. `npm ci` removes `node_modules` first, so stop the dev servers before you run it. Running `npm run dev` inside a package directory skips this check.

**Backend startup.** The backend's `npm run dev` runs these steps in order:

1. `predev` (`build:openapi`) regenerates `openapi/openapi.json` from `openapi/openapi.yaml`. The JSON is generated and gitignored.
2. `scripts/check-docker.sh` checks that the Docker daemon answers and that `ronl-postgres` and `ronl-operaton` are running. A container with a health check must report `healthy`. Each container gets a green, yellow (running, not yet healthy) or red (not running or missing) line. If any container is not ready, the script exits non-zero and prints:

    ```text
    docker start ronl-postgres ronl-operaton
    ```

    and, for containers that don't exist yet:

    ```text
    cd ../ronl-business-api && docker compose up -d postgres operaton
    ```

3. `nodemon` watches `src/**/*.ts` and runs `ts-node src/index.ts`.

`npm run docker:check` in `packages/backend` runs step 2 on its own.

### What the backend logs

With the default `LOG_FORMAT=json`, every log line is a JSON object. The start sequence is:

- `[DB] Migrations applied` (or the skip warning when `DATABASE_URL` is empty)
- `Server started`, with `environment`, `host`, `port`, `corsOrigin`, `triplydbEndpoint` and `operatonBaseUrl`
- `API available at: http://localhost:3001/v1`
- `Health check: http://localhost:3001/v1/health`
- `Legacy API: http://localhost:3001/api (deprecated)`

The same logger also writes to `logs/error.log` and `logs/combined.log` under `packages/backend`, and every request is logged as `Incoming request`.

---

## Verifying the setup

```bash
curl -s http://localhost:3001/v1/health | jq '.'
```

The response has this shape (values abbreviated):

```json
{
  "name": "Linked Data Explorer Backend",
  "version": "2026.09.8",
  "environment": "development",
  "build": { "sha": "", "shortSha": "", "run": "", "isTracked": false, "label": "local build" },
  "status": "healthy",
  "uptime": 12.3,
  "timestamp": "…",
  "services": {
    "triplydb": { "status": "up", "latency": 150, "lastCheck": "…" },
    "operaton": { "status": "up", "latency": 20, "lastCheck": "…" }
  },
  "shacl": { "complete": true, "…": "…" },
  "documentation": "/v1/openapi.json"
}
```

- `version` is the CalVer release from `packages/backend/package.json`, and the response also carries it in the `API-Version` header.
- `environment` is `NODE_ENV`.
- `build` reads `local build` with `isTracked: false` locally. Only the deploy workflows write the `build-info.json` that identifies a tracked build.
- `status` is `healthy` with HTTP 200, or `degraded` with HTTP 503 when TriplyDB or Operaton does not answer. Locally, Operaton is `ronl-operaton`, so `operaton: down` means that container is down and your network is not the cause. `triplydb: down` points to the network or to the remote service.
- `shacl.complete` reports whether all SHACL shape layers loaded. It never changes `status`.

The [Health endpoint](backend.md#health) section describes each field.

**In the browser:** open `http://localhost:3000`, choose **DMN Orchestration** (the GitBranch icon) and check that the DMN list loads. The DevTools console should show no CORS errors.

---

## RoPA records (local)

### Seed example records

After the database is running and the backend has started once, so that the migrations have created the tables, seed the four example RoPA records from `packages/backend`:

```bash
cd packages/backend
npx ts-node --project tsconfig.json src/db/seed-ropa.ts
```

Expected output:

```text
[seed-ropa] Seeding RoPA records…
[seed-ropa] AwbShellProcess (Flevoland) → <uuid>
[seed-ropa] TreeFellingPermitSubProcess → <uuid>
[seed-ropa] AwbZorgtoeslagProcess → <uuid>
[seed-ropa] ZorgtoeslagProvisionalSubProcess → <uuid>
[seed-ropa] Done.
```

The seed is idempotent. Re-running it updates existing rows in place via `ON CONFLICT (bpmn_process_id) DO UPDATE`.

### Verify records in the database

```bash
docker exec -it ronl-postgres psql -U lde_user -d lde_assets \
  -c "SELECT bpmn_process_id, process_level, status FROM ropa_records ORDER BY process_level;"
```

Expected output:

```text
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
curl -s "http://localhost:3001/v1/ropa/public?organisation=flevoland" | jq '.data | length'
```

This returns `4`. If it returns `0`, the `controller_name` values in the seeded records do not contain "flevoland". Check the controller names in `src/db/seed-ropa.ts` and re-run the seed.

### Test the public site locally

`packages/ropa-site/index.html` has no build step and no URL to edit. It derives its API base from `location.hostname`:

| Hostname | API base |
|---|---|
| `localhost` or `127.0.0.1` | `http://localhost:3001` |
| starts with `acc.` | `https://acc.backend.linkeddata.open-regels.nl` |
| anything else | `https://backend.linkeddata.open-regels.nl` |

Serve the file on localhost so that it calls your local backend:

```bash
cd packages/ropa-site
npx serve .
```

`serve` listens on port 3000 by default. If the LDE frontend already holds that port, `serve` picks another one, or you can choose one with `-l <port>`.

!!! warning "Opening from `file://` calls production"
    A page opened directly from disk has an empty hostname, so it falls through to the production backend and does not use your local one. Use `npx serve .` to test against local data.

CORS does not get in the way: `middleware/cors.middleware.ts` answers the public mounts listed in `utils/publicPaths.ts` (`/v1/ropa/public`, `/v1/bundles/public` and `/v1/openapi.json`) with `origin: '*'` for `GET` and `OPTIONS`, whatever `CORS_ORIGIN` holds.

---

## Environment comparison

| Aspect | Local development | ACC |
|---|---|---|
| Backend URL | `http://localhost:3001` | `https://acc.backend.linkeddata.open-regels.nl` |
| Frontend URL | `http://localhost:3000` | `https://acc.linkeddata.open-regels.nl` |
| Operaton | `ronl-operaton` container, `http://localhost:8081/engine-rest` | Set in the App Service configuration, see [Deployment](deployment.md#environment-variables-azure-app-service) |
| PostgreSQL | `ronl-postgres` container, `lde_assets` database | Azure Database for PostgreSQL Flexible Server, see [PostgreSQL deployment](deployment-postgresql.md) |
| DB migrations | Run on every backend start | Run on every backend start |
| RoPA seed | Run manually: `npx ts-node … src/db/seed-ropa.ts` | Run manually. No workflow runs it. |
| `ropa-site` API base | `http://localhost:3001`, derived from the hostname | `https://acc.backend.linkeddata.open-regels.nl`, derived from the hostname |
| `ropa-site` hosting | `npx serve .` | Azure Static Web Apps, deployed by `azure-ropa-site-acc.yml` on a push to `acc` that touches `packages/ropa-site/**` |
| CORS for public routes | `origin: '*'` for the three public mounts, regardless of `CORS_ORIGIN` | Same |
| `build` in `/v1/health` | `local build` | `build <sha> · #<run>` |

---

## Tests and code quality

From the repository root:

```bash
npm test               # every workspace: backend Jest, frontend Vitest
npm run typecheck      # tsc --noEmit in every workspace
npm run lint           # ESLint in every workspace
npm run lint:fix
npm run format         # Prettier, writing
npm run check-format   # Prettier, checking only
npm run test:scripts   # the repository scripts' own tests
```

[Testing](testing.md) has the suites, their current counts, the contract subset and the CI gate.

!!! warning "`npm run test:scripts` fails on Windows"
    `scripts/promotion-targets.test.mjs` resolves the script it runs with `new URL(...).pathname`, which yields `/C:/…` on Windows. Its four command-line checks therefore fail there, while it passes on Linux CI (24 checks). Because `test:scripts` chains the two files with `&&`, `dso-dossier.test.mjs` then never runs. It passes on its own: `node scripts/dso-dossier.test.mjs` (24 checks). Measured 26 September 2026.

### Git hooks

Husky installs two hooks:

| Hook | Runs |
|---|---|
| `pre-commit` | `npx lint-staged`: `prettier --write` and `eslint --fix` on staged files in `packages/frontend/**` (`js`, `jsx`, `ts`, `tsx`, `json`, `css`, `md`) and `packages/backend/src/**/*.ts` |
| `pre-push` | `npm run deps:check`, then `npm run lint`, then `npm run check-format` |

When a hook fails, fix what it names. Never bypass it.

---

## Repository scripts

The root `package.json` also defines these scripts:

| Script | What it does |
|---|---|
| `deps:check` | `bash scripts/check-deps.sh`: checks the installed dependencies against the lockfile and warns about npm older than 11.10 |
| `check-supply-chain` | `node scripts/check-supply-chain.mjs` |
| `sbom` | `node scripts/write-sbom.mjs`: writes a software bill of materials |
| `test:scripts` | Tests `promotion-targets.mjs` and `dso-dossier.mjs` (see the warning above) |
| `check-mirror` | `bash scripts/check-mirror.sh`: compares `acc` and `main` on `origin` with the `gitlab` mirror. It prints the push command for any drift and never pushes. |
| `authorities:generate` | `node scripts/generate-dso-authorities.mjs` |
| `dso:dossier` | `node scripts/dso-dossier.mjs` |
| `build` / `preview` | Builds the frontend or previews the build |

In `packages/backend`, `docker:check`, `build:openapi`, `lint:openapi`, `test:contract` and `test:openapi-coverage` cover the Docker check and the OpenAPI document.

---

## Getting a change to ACC

`acc` accepts changes only through a pull request. The `acc supply-chain gate` ruleset blocks direct pushes, force-pushes and deletion. It requires a pull request, merged with a merge commit, and these status checks: `audit`, `scan`, `deploy`, `Build and Deploy Frontend` and `Build and Deploy ROPA Site`.

1. Create a branch from `acc` and push it.
2. Open a pull request into `acc`. The backend workflow's `deploy` job runs lint, the OpenAPI lint, typecheck, the full test suite and the build on the pull request, and skips its deploy steps. The frontend and RoPA site workflows build from the pull request.
3. Merge the pull request. The push to `acc` deploys the backend, frontend and RoPA site to ACC. Each of these workflows filters on the paths it deploys.

Production follows the same pattern. A pull request from `acc` into `main` (the `main promotion gate` ruleset requires `audit` and `scan`), and its merge runs `promote-to-production.yml`, which deploys the backend first and the two sites after it. See [Deployment](deployment.md).
