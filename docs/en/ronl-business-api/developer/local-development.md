---
component: RONL Business API
---

# Local Development Setup

This page takes a fresh clone of `ronl-business-api` to a running local stack:
five Docker services, four dev servers, and a Keycloak realm with test users.
It describes release **v2026.09.12**.

---

## Prerequisites

| Tool | Version | Why |
|---|---|---|
| Node.js | **22.23.2** (`.nvmrc`); `engines` asks for `>=22` | Backend and front-end runtimes. The Azure App Services run `NODE|22-lts` |
| npm | `engines` asks for `>=10`; **11.10 or newer** recommended | Node 22.23.2 bundles npm 10.9.8, which silently ignores the 14-day `min-release-age` cooldown in the root `.npmrc`. `deps:check` warns and suggests `npm install -g npm@11` |
| Docker with Compose v2 | `docker compose …` | The five local services |
| Git | — | Includes Git for Windows' **bash**, see below |
| **bash** | Any recent bash | The install, the dev start and the checks are bash scripts |

### A bash shell is required

Several root `package.json` scripts call `bash` explicitly, and the scripts
they run are `#!/usr/bin/env bash` scripts using bash arrays:

| Script | Runs |
|---|---|
| `postinstall` | `bash scripts/write-deps-marker.sh`, so **`npm ci` and `npm install` themselves need bash** |
| `deps:check` | `bash scripts/check-deps.sh` |
| `docker:check` | `bash scripts/check-docker.sh` |
| `dev` | `deps:check`, then `docker:check`, then the dev servers |
| `check-mirror`, `check-previews` | `bash scripts/check-mirror.sh`, `bash scripts/check-previews.sh` |
| `clean` | `rm -rf node_modules` (and `rm -rf dist` in each workspace), so it needs a POSIX `rm` |

On macOS and Linux this needs nothing extra. On **Windows**, npm runs package
scripts through `cmd.exe`, so the word `bash` must resolve to Git for Windows'
`bash.exe`. It does when you work from **Git Bash**, or when
`C:\Program Files\Git\bin` is on your `PATH`.

The Husky hooks are `#!/bin/sh` scripts, which Git runs with its own `sh`
whichever terminal you use. The root `.gitattributes` sets
`* text=auto eol=lf`, so the `.sh` files keep LF line endings on a Windows
checkout and stay runnable regardless of `core.autocrlf`.

!!! warning "WSL's `bash.exe` (untested)"
    If `C:\Windows\System32\bash.exe`, the WSL launcher, comes before Git's
    `bash.exe` on your `PATH`, the scripts run inside WSL, where `node`, `npm`
    and `docker` may be different installations or missing. This combination
    has not been tested. If `npm ci` or `npm run dev` fails in a way that
    suggests the wrong tools, run `where bash` in `cmd.exe` to see which one
    resolves first, and work from Git Bash instead.

---

## Clone and install

```bash
git clone https://github.com/sgort/ronl-business-api.git
cd ronl-business-api
nvm use            # picks up 22.23.2 from .nvmrc, if you use nvm
npm ci
```

Install with **`npm ci`**, not `npm install`. `npm ci` installs exactly what
`package-lock.json` records and never rewrites it; `npm install` re-resolves
the version ranges instead. The root `npm run setup` script still runs
`npm install && npm run docker:up`, so prefer the two separate steps.

The monorepo uses npm workspaces, so one install covers all six packages:
`@ronl/backend`, `@ronl/frontend`, `@ronl/shared`, `@ronl/pa-cockpit`,
`@ronl/pa-demo` and `@ronl/public-site`.

Two lifecycle scripts run during the install:

- The root **`postinstall`** copies `package-lock.json` to
  `node_modules/.package-lock-installed.json`. That snapshot is what
  `deps:check` compares against later.
- The root **`prepare`** runs `husky`, which installs the Git hooks.
  `@ronl/shared` has its own `prepare` script (`tsc`) that builds its `dist/`,
  which the backend and the Vite front ends import. If a fresh clone reports
  that `@ronl/shared` cannot be resolved, run
  `npm run build --workspace=@ronl/shared`.

---

## Backend environment

Only the backend needs a `.env` file you create yourself:

```bash
cp packages/backend/.env.example packages/backend/.env
```

The backend's `config.ts` loads `.env.development` from `packages/backend/`
first (the name follows `NODE_ENV`, which defaults to `development`) and then
`.env`. `dotenv` never overwrites a variable that is already set, so a value in
`.env.development` wins over the same key in `.env`. That file is gitignored and
does not exist unless you create it.

The front ends need no setup: they run in Vite's `development` mode on their
committed `.env.development` files (see [Front-end configuration](#front-end-configuration)).

### Settings to check

`.env.example` works locally as shipped, with these exceptions:

| Key | What to do |
|---|---|
| `NODE_EXTRA_CA_CERTS`, `NODE_TLS_REJECT_UNAUTHORIZED=0` | **Remove both lines** unless you sit behind the corporate proxy they were written for. The first points at a CA file on one developer's machine (the backend logs a warning and carries on when the file is unreadable). The second switches off TLS certificate checking for every outbound HTTPS call the backend makes. Issue [sgort/iou-architectuur#105](https://github.com/sgort/iou-architectuur/issues/105) tracks removing them from `.env.example` |
| `ANTHROPIC_API_KEY` | Must be **non-empty**, or the backend refuses to start with `Configuration validation failed: ANTHROPIC_API_KEY is required`. The shipped placeholder passes the check in development; the AI assistant works only with a real key |
| `OPERATON_BASE_URL` | Keep `http://localhost:8081/engine-rest` with `OPERATON_USERNAME`/`OPERATON_PASSWORD` = `demo`/`demo`. `OPERATON_M2M_BASE_URL` points at the same local engine |
| `DATABASE_URL` | `postgresql://audit_user:audit_password@localhost:5432/audit_logs`, the database and user the Postgres container creates on first start |
| `LDE_MCP_ENABLED` | Set to `false` unless you create the `lde_assets` database yourself. `LDE_DATABASE_URL` points at it, but `init-databases.sql` does not create it. With the flag on, the backend still starts; the assistant's LDE tools fail when called |

!!! danger "An unset Operaton URL reaches the shared engine"
    `OPERATON_BASE_URL` has a default, and it is not local: without the key the
    backend talks to `https://operaton.open-regels.nl/engine-rest`, and
    `OPERATON_M2M_BASE_URL` falls back to `https://operaton-doc.open-regels.nl/engine-rest`.
    Keep both keys in your `.env`, so local process starts and E2E runs land on
    your own engine.

Other defaults worth knowing:

- `PORT=3002`. `CORS_ORIGIN` allows `:3000`, `:5173` and `:5175`. PA-demo on
  `:5176` does not call the backend.
- `EDOCS_STUB_MODE`, `DOCCLE_STUB_MODE` and `VALIDSIGN_STUB_MODE` are `true`, so
  no external document, mail or signing service is called.
- The backend has no `LDE_API_URL` in `.env.example`; its own calls to the
  Linked Data Explorer default to the ACC LDE backend.
- `ENABLE_SWAGGER` no longer exists. The API describes itself at
  `/v1/openapi.json`.

### Front-end configuration

| Package | Committed `.env.development` |
|---|---|
| `@ronl/frontend` | `VITE_API_URL=http://localhost:3002/v1`, `VITE_KEYCLOAK_URL=http://localhost:8080`, `VITE_LDE_API_URL=http://localhost:3001/v1`, and `VITE_PA_SIGNALS_MOCK`, `VITE_PA_DOSSIERS_MOCK`, `VITE_PA_AGENDA_MOCK` all `false` |
| `@ronl/public-site` | `VITE_API_URL=http://localhost:3002/v1`, `VITE_STAFF_APP_URL=http://localhost:5173`, `VITE_SITE_URL=http://localhost:5175` |
| `@ronl/pa-demo` | The three `VITE_PA_*_MOCK` flags, all `true` |

To override a value on your machine only, put it in `.env.development.local`
next to the committed file. `.env.*.local` is gitignored.

`VITE_LDE_API_URL` points at a locally running Linked Data Explorer backend. The
Procesbibliotheek section calls it directly from the browser and shows an error
when nothing listens on `:3001`; the rest of the frontend works without it.

---

## The Docker stack

```bash
npm run docker:up        # docker compose up -d
```

`docker-compose.yml` defines five services on one bridge network,
`ronl-network`. Every image is pinned by tag **and** digest, and Renovate keeps
the digests current (`docker:pinDigests` in `renovate.json`).

| Service | Container | Image | Host port | Data |
|---|---|---|---|---|
| `keycloak` | `ronl-keycloak` | `quay.io/keycloak/keycloak:23.0` | 8080 | Its database is the `keycloak` DB in Postgres |
| `postgres` | `ronl-postgres` | `postgres:16-alpine` | 5432 | Volume `postgres-data` |
| `operaton-init` | `ronl-operaton-init` | `alpine:3.24.2` | — | Runs once and exits |
| `operaton` | `ronl-operaton` | `operaton/operaton:2.1.5` | 8081 → 8080 | Volume `operaton-data` |
| `redis` | `ronl-redis` | `redis:7-alpine` | 6379 | Volume `redis-data`, append-only file on |

**Keycloak** runs `start-dev --import-realm` with admin account `admin`/`admin`.
It waits for Postgres to report healthy, stores its data in Postgres
(`KC_DB=postgres`), imports `config/keycloak/ronl-realm.json`, and loads the
login themes from `./keycloak-themes`. Keycloak imports the realm only when no
`ronl` realm exists yet. Because the realm lives in the Postgres volume, an
existing `postgres-data` volume keeps the realm it was created with.

**Postgres** runs as `postgres`/`postgres`. On the first start of an empty
volume it runs `config/postgres/init-databases.sql`, which creates:

- the `keycloak` database and user;
- the `audit_logs` database and the user `audit_user` / `audit_password`, with
  full privileges on it;
- in `audit_logs`: the `audit_logs` table with its indexes, and a `tenants`
  table seeded with eight tenants: `utrecht`, `amsterdam`, `rotterdam`,
  `denhaag` (municipalities), `flevoland` (province), `uwv`, `toeslagen`
  (national agencies) and `unive` (commercial).

**Redis** runs `redis-server --appendonly yes`. The backend uses it as the PA
monitoring cache; `/v1/health` reports it but does not fail when it is down.

Keycloak, Postgres, Operaton and Redis each have a healthcheck. Keycloak and
Operaton get a 60-second start period, so allow a minute on the first start:

```bash
npm run docker:logs:keycloak     # docker compose logs -f keycloak
docker compose ps                # STATUS shows (healthy) when ready
```

---

## Initialising Operaton

The local Operaton engine starts in two steps, both in `docker-compose.yml`.

1. **`operaton-init`** mounts the `operaton-data` volume, runs
   `chown -R 1000:1000 /data`, and exits. The Operaton image runs as the
   non-root user with uid 1000, but Docker creates a new named volume owned by
   root. Without this step the engine crashes on a fresh volume with
   `java.nio.file.AccessDeniedException` on its `.mv.db` file. The step is
   idempotent, so it runs harmlessly on every `docker compose up`.
2. **`operaton`** starts only after that container has exited successfully
   (`depends_on: operaton-init: condition: service_completed_successfully`).
   It uses an **H2 file database**,
   `jdbc:h2:file:/operaton/h2-data/operaton-local`, on the `operaton-data`
   volume, so no external database is involved. It runs with
   `TZ=Europe/Amsterdam` and `-XX:MaxRAMPercentage=70.0`, and listens on host
   port **8081**. Its healthcheck is a TCP probe on the container's port 8080.

The engine REST API is at `http://localhost:8081/engine-rest`, and the Operaton
web apps are served on `http://localhost:8081`. The backend's
`.env.example` uses `demo`/`demo` for both.

### The engine starts empty

Nothing in this repository deploys BPMN or DMN. A fresh engine has no process
definitions, so any process start fails until you deploy some.

The reference bundle lives in the sibling **Linked Data Explorer** repository,
under `linked-data-explorer/e2e-fixtures/`, and is deployed through the LDE's
BPMN Modeler. [Run the LDE locally](../../linked-data-explorer/developer/local-development.md)
first. Then:

| What | How to deploy it |
|---|---|
| **Processes**, in `e2e-fixtures/<tenant>/` | Import each process and set the **Organization** field to the tenant folder name (`flevoland` or `toeslagen`). That value becomes the Operaton `tenant-id` |
| **Decisions**, listed under `sharedDecisions.files` in `e2e-fixtures/manifest.json` | Import each one with the **Organization field empty**. The processes resolve their decisions untenanted (`decisionRefTenantId="${null}"`), so a decision deployed under a tenant is not found |
| **`zorgtoeslag_resultaat`** | Not in the fixture bundle. `manifest.json` lists it under `sharedDecisions.external`: it ships with the zorgtoeslag rules set |

The frontend E2E suite refuses to run until this is done: its
`global-setup.ts` calls `verifyRequiredProcesses()` and
`verifyRequiredDecisions()` against the engine and names what is missing. See
[What each suite needs running](testing/e2e.md#what-each-suite-needs-running).

Deployments persist in the `operaton-data` volume across restarts. They are
lost on `npm run docker:down:volumes`, which also wipes the Keycloak realm, the
audit database and Redis.

---

## Starting the development servers { #start-development-servers }

```bash
npm run dev
```

`npm run dev` runs three steps in order, and stops at the first one that fails:

1. **`deps:check`** (`scripts/check-deps.sh`) compares `package-lock.json` with
   the snapshot the last install left in `node_modules`. It parses both files
   and ignores this repository's own package version numbers, so a release bump
   does not trip it and line endings do not matter. When a third-party
   dependency has changed, it stops and tells you to run **`npm ci`**, with a
   reminder that `npm ci` deletes `node_modules` first and so takes down any dev
   server running from it. It never installs anything itself. It also warns,
   without failing, when npm is older than 11.10.
2. **`docker:check`** (`scripts/check-docker.sh`) checks that Docker is running
   and that four containers are running and healthy: `ronl-keycloak`,
   `ronl-postgres`, `ronl-redis` and `ronl-operaton`. When one is missing or not
   yet healthy it stops and tells you to run `npm run docker:up`.
3. **`concurrently`** starts four dev servers:

| Server | Command | URL |
|---|---|---|
| Backend | `tsx watch src/index.ts`, after its `predev` script has run `build:openapi` | `http://localhost:3002` |
| Frontend (MijnOmgeving) | `vite` | `http://localhost:5173` |
| Public site | `vite` | `http://localhost:5175` |
| PA-demo | `vite` | `http://localhost:5176` |

The Vite servers bind to `0.0.0.0`. The backend binds to `HOST` from `.env`
(`0.0.0.0` in `.env.example`) and logs `API available at: …/v1` when it is up.
Before it listens it initialises its database tables and, with
`MCP_ENABLED=true`, connects the AI-assistant sources; a source that fails to
connect is logged and skipped.

Open `http://localhost:5173`. The frontend redirects you to Keycloak to log in.

!!! tip "Why the demo starts too"
    The [PA-demo](../user-guide/pa-demo.md) renders from the shared
    [`@ronl/pa-cockpit`](pa-cockpit-package.md) package rather than its own copy,
    so a cockpit change affects both it and the caseworker frontend. Starting one
    without the other makes it easy to verify the frontend and miss the demo.

To run a single server, use its root script: `npm run dev:backend`,
`dev:frontend`, `dev:public-site` or `dev:pa-demo`. These skip both checks.

---

## Test users

`config/keycloak/ronl-realm.json` defines **22 users**, all with password
**`test123`** and assurance level `hoog`. The `municipality` attribute is the
user's tenant.

| Tenant | Username | Realm roles |
|---|---|---|
| utrecht | `test-citizen-utrecht` | citizen |
| utrecht | `test-caseworker-utrecht` | caseworker |
| amsterdam | `test-citizen-amsterdam` | citizen |
| amsterdam | `test-caseworker-amsterdam` | caseworker |
| rotterdam | `test-citizen-rotterdam` | citizen |
| rotterdam | `test-caseworker-rotterdam` | caseworker |
| denhaag | `test-citizen-denhaag` | citizen |
| denhaag | `test-caseworker-denhaag` | caseworker |
| denhaag | `test-hr-denhaag` | caseworker, hr-medewerker |
| denhaag | `test-onboarded-denhaag` | caseworker |
| flevoland | `test-citizen-flevoland` | citizen |
| flevoland | `test-caseworker-flevoland` | caseworker |
| flevoland | `test-hr-flevoland` | caseworker, hr-medewerker, board-secretary, board-director, hrm-unit, procurement-unit, planning-control-officer, financial-controller, hr-business-partner, personnel-controller |
| flevoland | `test-mngr-flevoland` | caseworker, manager |
| flevoland | `test-infra-flevoland` | caseworker, infra-projectteam, infra-medewerker, and the RIP project roles (`rip-*`) |
| flevoland | `test-pa-flevoland` | public-affairs, pa-author, pa-editor, pa-admin |
| flevoland | `test-woo-flevoland` | woo-coordinatie |
| uwv | `test-citizen-uwv` | citizen |
| uwv | `test-caseworker-uwv` | caseworker |
| toeslagen | `test-citizen-toeslagen` | citizen |
| toeslagen | `test-caseworker-toeslagen` | caseworker |
| unive | `test-citizen-unive` | citizen |

The Keycloak admin console is at `http://localhost:8080` with `admin`/`admin`.

---

## Verifying the setup

```bash
curl -s http://localhost:3002/v1/health
```

A healthy local stack answers `200`:

```json
{
  "success": true,
  "data": {
    "name": "RONL Business API",
    "version": "2026.09.12",
    "build": null,
    "status": "healthy",
    "timestamp": "2026-09-26T10:00:00.000Z",
    "uptime": 42.7,
    "environment": "development",
    "duration": 18,
    "dependencies": {
      "keycloak": { "status": "up", "latency": 9 },
      "operaton": { "status": "up", "latency": 14 },
      "cache": { "status": "up" }
    }
  }
}
```

- `status` is `healthy` only when **Keycloak and Operaton** are both up; then
  the endpoint answers `200`. Otherwise it is `degraded`, `success` is `false`,
  and the endpoint answers **`503`**. A down dependency carries an `error`
  field instead of `latency`.
- `cache` is Redis. It is reported but never makes the check fail.
- `build` is `null` in a working tree; the deploy workflow fills it in.
- `environment` comes from `DEPLOYMENT_ENV`, falling back to `NODE_ENV`.

`/v1/health/live` and `/v1/health/ready` are the liveness and readiness probes.
The OpenAPI description is at `http://localhost:3002/v1/openapi.json`; see the
[API Specification](../reference/api-specification.md).

---

## Calling the API with a token

The realm's `ronl-business-api` client is a **public client** with direct
access grants enabled, so a password grant needs only the client ID. There is
no client secret.

```bash
TOKEN=$(curl -s -X POST http://localhost:8080/realms/ronl/protocol/openid-connect/token \
  -d client_id=ronl-business-api \
  -d grant_type=password \
  -d username=test-citizen-utrecht \
  -d password=test123 \
  | node -pe "JSON.parse(require('fs').readFileSync(0, 'utf8')).access_token")
```

`node -pe` parses the response so you do not need `jq`. The client's protocol
mappers put the `ronl-business-api` audience, the realm roles and the
`municipality`, `organisation_type` and `assurance_level` attributes in the
token.

Read the start form of a deployed process:

```bash
curl -s http://localhost:3002/v1/process/AwbZorgtoeslagProcess/start-form \
  -H "Authorization: Bearer $TOKEN"
```

Start it with the form's fields as `variables`, from a JSON file of your own:

```bash
curl -s -X POST http://localhost:3002/v1/process/AwbZorgtoeslagProcess/start \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @zorgtoeslag-start.json      # { "variables": { … } }
```

`AwbZorgtoeslagProcess` is one of the fixture processes, deployed under the
`toeslagen` tenant. Because `test-citizen-utrecht` is a citizen, the backend
starts the case under the deployment's tenant: `municipality` is `toeslagen`,
`originTenantId` is `utrecht`, and the business key starts with `toeslagen-`.
Staff get `403 TENANT_MISMATCH` when they start another tenant's process; see
[Tenancy](../features/authentication-iam.md#tenancy). On success the endpoint
answers `201` with `processInstanceId`, `businessKey`, `status` and
`startTime`.

Before the fixtures are deployed, both calls fail, and the start's
`error.details` carries Operaton's own message. This start call has not been
run end to end for this page.

---

## Database access

```bash
docker exec -it ronl-postgres psql -U postgres -d audit_logs
```

```sql
SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 10;
SELECT tenant_id, name, organisation_type FROM tenants;
\q
```

Connect with `-U audit_user` to see what the backend sees. The Keycloak data is
in the `keycloak` database of the same container.

Redis:

```bash
docker exec -it ronl-redis redis-cli ping      # PONG
```

---

## Service URLs

| Service | URL | Credentials |
|---|---|---|
| Frontend (MijnOmgeving) | `http://localhost:5173` | Test users above |
| Public site | `http://localhost:5175` | — |
| PA-demo | `http://localhost:5176` | — (mock data only) |
| Backend API | `http://localhost:3002/v1` | Bearer token |
| Health | `http://localhost:3002/v1/health` | — |
| OpenAPI | `http://localhost:3002/v1/openapi.json` | — |
| Keycloak admin console | `http://localhost:8080` | `admin` / `admin` |
| Operaton web apps | `http://localhost:8081` | `demo` / `demo` |
| Operaton REST API | `http://localhost:8081/engine-rest` | `demo` / `demo` |
| PostgreSQL | `localhost:5432` | `postgres` / `postgres`; `audit_user` / `audit_password` for `audit_logs` |
| Redis | `localhost:6379` | — |
| LDE backend (optional, sibling repo) | `http://localhost:3001/v1` | — |

---

## Stopping and resetting

```bash
# Ctrl+C in the npm run dev terminal stops the four dev servers
npm run docker:down           # stop the containers, keep the volumes
npm run docker:down:volumes   # stop the containers and delete all four volumes
```

`docker:down:volumes` removes `keycloak-data`, `postgres-data`,
`operaton-data` and `redis-data`. On the next `npm run docker:up`, Postgres runs
`init-databases.sql` again, Keycloak re-imports the realm, and Operaton starts
empty, so you deploy the fixtures again.

---

## Git hooks

Husky installs two hooks during `npm ci`:

| Hook | Runs |
|---|---|
| `pre-commit` | `npx lint-staged`: ESLint `--fix` in the owning workspace and `prettier --write` on the staged files |
| `pre-push` | `deps:check`, then `npm run build --workspace=@ronl/shared`, `type-check`, `lint` and `check-format` |

`deps:check` comes first in `pre-push` so that a push from a stale install stops
with `npm ci` named as the fix, instead of the later checks failing on the wrong
tool versions. On 14 September 2026 a clone still on Prettier 3.8.1 after the
lockfile moved to 3.9.6 failed `check-format` on seven correctly formatted files
with nothing saying why.

For running the test suites, see [Testing](testing/overview.md).

---

## Common issues

**`bash` is not recognized, or `npm ci` fails in `postinstall`**
: npm cannot find bash. On Windows, work from Git Bash or put
  `C:\Program Files\Git\bin` on your `PATH`. See
  [A bash shell is required](#a-bash-shell-is-required).

**`deps:check` says the install is stale**
: Stop the dev servers and run `npm ci`.

**`docker:check` lists a container as not running or not yet healthy**
: Run `npm run docker:up` and wait for `docker compose ps` to show all four as
  healthy. Keycloak and Operaton take up to a minute on first start.

**Operaton exits with `AccessDeniedException` on its `.mv.db` file**
: The volume is still owned by root. Check that `operaton-init` ran:
  `docker compose logs operaton-init`, then `docker compose up -d` again.

**The backend exits with `Configuration validation failed`**
: `ANTHROPIC_API_KEY` is empty or missing in `packages/backend/.env`.

**A process start fails with no matching process definition**
: The local engine is empty. See [The engine starts empty](#the-engine-starts-empty).

**The realm is missing, or the token lacks the audience or roles**
: The realm lives in Postgres, and Keycloak skips the import when a `ronl`
  realm already exists. A `postgres-data` volume from an older realm file keeps
  the older client configuration. The current `ronl-realm.json` already carries
  the audience and realm-role mappers on the `ronl-business-api` client, so
  resetting with `npm run docker:down:volumes && npm run docker:up` picks them
  up. That also clears the audit database and the Operaton deployments.
  `scripts/keycloak-add-token-claim-mappers.sh` adds only the `email`,
  `given_name` and `family_name` mappers that ValidSign signing needs, to an
  existing client, without a re-import.

**CORS error in the browser**
: Check that `CORS_ORIGIN` in `packages/backend/.env` lists the origin exactly,
  including the port.

**Procesbibliotheek shows an error**
: The LDE backend is not running on `:3001`. Start it from the LDE repository,
  or ignore the section.

For more, see [Troubleshooting](troubleshooting.md).
