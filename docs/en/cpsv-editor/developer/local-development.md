---
component: CPSV Editor
---

# Local Development

This guide covers running the CPSV Editor locally, the Linked Data Explorer backend it
talks to, and the two Docker containers from the RONL Business API stack that backend
needs.

---

## When you need a local backend

In development mode the editor sends every backend call to `http://localhost:3001`, the
Linked Data Explorer (LDE) backend. Form editing, TTL generation, and TTL import and
export happen in the browser and work without it. These features call the backend:

| Feature | Backend route | Source |
|---|---|---|
| RONL analysis and method concepts, loaded **on mount** | `POST /v1/triplydb/query` | `src/utils/ronlHelper.js`, `src/hooks/useEditorState.js` |
| SHACL validation | `POST /v1/shacl/validate` | `src/utils/shaclHelper.js` |
| TriplyDB publishing — the service-update step | `POST /v1/triplydb/update-service` | `src/utils/triplydbHelper.js` |
| DMN validate, deploy and evaluate | `POST /v1/dmns/validate`, `/v1/dmns/deploy`, `/v1/dmns/evaluate/{key}` | `src/components/tabs/DMNTab.jsx` |
| DSO handoff from the LDE (`?dsoImport=dmn`) | `GET /v1/dso/toepasbare-regels/{id}/dmn` | `src/hooks/useDsoImport.js` |

Because the RONL concepts load as soon as the editor opens, starting the editor without a
backend is not silent: the Legal tab reports "Failed to load concepts from TriplyDB" and
the Vendor tab "Failed to load vendors from TriplyDB". Locally, the usual cause is not
TriplyDB but a backend that is not running.

The same backend serves the Linked Data Explorer. Changing it for the editor can break
the explorer, and the other way round.

---

## The local stack

```
┌─────────────────────────────────────────────────────────────┐
│  Local Development Environment                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  CPSV Editor                 Linked Data Explorer frontend  │
│  http://localhost:3000       http://localhost:3000          │
│  — or :3002 alongside LDE    (React / Vite)                 │
│  (React / Vite)                                             │
│           │                          │                      │
│           └────────────┬─────────────┘                      │
│                        ↓                                    │
│            Linked Data Explorer backend                     │
│            http://localhost:3001                            │
│            (Node.js + Express + TypeScript)                 │
│                        │                                    │
│          ┌─────────────┴──────────────┐                     │
│          ↓                            ↓                     │
│  Docker (ronl-business-api stack)   Remote services         │
│  • ronl-operaton  localhost:8081    • TriplyDB              │
│  • ronl-postgres  localhost:5432      api.open-regels.      │
│                                       triply.cc             │
│                                     • DSO APIs              │
│                                       (pre-production)      │
└─────────────────────────────────────────────────────────────┘
```

Operaton is **not** remote in local development. The LDE backend's
`packages/backend/.env.example` points `OPERATON_BASE_URL` at
`http://localhost:8081/engine-rest`, the `ronl-operaton` container from the
ronl-business-api stack, and the editor's `.env.development` sets `VITE_OPERATON_URL` to
`http://localhost:8081`. TriplyDB and the DSO APIs stay remote.

---

## Prerequisites

| Tool | Version | Why |
|---|---|---|
| Node.js | 24.20.0 | `.nvmrc`. CI installs exactly this version (`node-version-file: .nvmrc`). The LDE repository pins its own version in its own `.nvmrc`, currently 24.21.0. |
| npm | 11.10 or newer | `.npmrc` sets a 14-day cooldown (`min-release-age=14`) that older npm ignores without a warning. Node 24.20.0 bundles npm 11.19. npm 10 also crashes on anything that re-resolves the tree (`npm install <package>`, `npm update`) — see below. |
| bash | on `PATH` | `npm start` runs `npm run deps:check`, which is `bash scripts/check-deps.sh`; the pre-push hook runs it too. On Windows, npm runs scripts through `cmd.exe`, so `bash` must be found on `PATH` — Git for Windows provides one. |
| Git | — | |
| Docker | — | Only to run the LDE backend: its `dev` script refuses to start without the `ronl-postgres` and `ronl-operaton` containers. |

!!! warning "npm 10 crashes on re-resolving the tree"
    The README records that npm 10 (bundled with Node 22) installs from the lockfile with
    `npm ci`, but crashes on `npm install <package>`, `npm update`, or regenerating the
    lockfile, with `Cannot read properties of null (reading 'edgesOut')` — a resolver bug
    hit on `vitest`'s optional peer chain. npm 11 resolves the same tree. Verified with
    npm 10.9.4 and 11.19.1 on 11 September 2026.

`scripts/check-deps.sh` warns at every `npm start` and every push when npm is older than
11.10, and names `npm install -g npm@11` as the fix. It is a warning, not a failure.

---

## Install and start the editor

```bash
git clone https://github.com/sgort/ttl-editor.git
cd ttl-editor
npm ci
npm start
```

What each step does:

| Step | Effect |
|---|---|
| `npm ci` | Installs exactly what `package-lock.json` records. |
| `postinstall` → `node scripts/write-deps-marker.mjs` | Copies the lockfile to `node_modules/.package-lock-installed.json`, the snapshot `deps:check` compares against. |
| `prepare` → `husky` | Installs the Git hooks in `.husky/`. |
| `npm start` → `npm run deps:check && vite` | Checks the install against the lockfile, then starts the Vite dev server on `http://localhost:3000`. It does not open a browser. |

`deps:check` compares the lockfile with the install marker, ignoring the repository's own
version number so a release bump alone does not count as a change. When they differ, or
`node_modules` or the marker is missing, it exits 1, prints `npm ci` as the fix, and Vite
does not start. A fast-forward brings lockfile changes in and installs nothing, so this is
what catches a stale install after a pull.

!!! note "`npm ci`, not `npm install`"
    `npm install` re-resolves the version ranges. `npm ci` installs the lockfile as it is,
    and ignores the `.npmrc` cooldown by design — the lockfile is the source of truth. Use
    `npm install <package>` only to add or upgrade one package. `npm ci` deletes
    `node_modules` first, so stop the dev server before running it.

The port is fixed: `vite.config.mjs` sets `server: { port: 3000, strictPort: true }`. The
LDE backend allowlists browser origins for CORS by port, and `strictPort` stops Vite from
quietly moving to another port that the backend does not allow. If 3000 is taken, the
editor exits instead of starting.

---

## Running alongside the Linked Data Explorer

### Port 3000 is taken twice

The LDE frontend's dev server also uses port 3000 (`packages/frontend/vite.config.ts`).
With it running, `npm start` in the editor fails because of `strictPort`. The LDE's
`packages/frontend/.env.development` resolves this the other way round: it says to run
the CPSV Editor on a non-3000 port, and sets

```
VITE_CPSV_EDITOR_URL=http://localhost:3002
```

That is where the LDE's DSO explorer sends its DSO → DMN handoff link. `3002` is in the
backend's local CORS allowlist, together with `3000`. So when both frontends run, start
the editor on 3002:

```bash
npm start -- --port 3002
```

npm appends the arguments after `--` to the end of the script string, so this runs
`npm run deps:check && vite --port 3002`. The appending is confirmed on npm 11.11; Vite's
CLI accepts `--port`, and a CLI option overrides the config file. Starting the editor
this way has not been tested end to end.

### Start the LDE backend

The backend needs three things before it starts: Docker containers, a `.env`, and an
install.

**1. The Docker containers.** The backend's `dev` script runs
`bash scripts/check-docker.sh` first. That script exits 1 unless the `ronl-postgres` and
`ronl-operaton` containers are both running and, where they define a health check,
healthy. Both come from the ronl-business-api `docker-compose.yml`:

```bash
cd ../ronl-business-api
docker compose up -d postgres operaton
```

| Container | Host port | Notes |
|---|---|---|
| `ronl-postgres` | 5432 | PostgreSQL 16 |
| `ronl-operaton` | 8081 → 8080 | Operaton 2.1.5 on an H2 file database. Its health check allows a 60-second start period. |

Starting `operaton` also runs the one-shot `operaton-init` service, which fixes
ownership of the volume first. Once the containers exist, `docker start ronl-postgres
ronl-operaton` is enough. See [RONL Business API — Local Development](../../ronl-business-api/developer/local-development.md)
for that stack.

The LDE backend stores assets in a `lde_assets` database in the same PostgreSQL. Its
`.env.example` gives the one-time setup:

```bash
docker exec -it ronl-postgres psql -U postgres -c "CREATE USER lde_user WITH PASSWORD 'lde_password';"
docker exec -it ronl-postgres psql -U postgres -c "CREATE DATABASE lde_assets OWNER lde_user;"
docker exec -it ronl-postgres psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE lde_assets TO lde_user;"
```

**2. The `.env`.**

```bash
git clone https://github.com/sgort/linked-data-explorer.git
cd linked-data-explorer
cp packages/backend/.env.example packages/backend/.env
```

Without it, `OPERATON_BASE_URL` and `TRIPLYDB_ENDPOINT` are empty, and
`packages/backend/src/utils/config.ts` throws
`Missing required configuration: triplydb.endpoint, operaton.baseUrl` when the backend
loads. The example file's values are the local ones: port 3001, Operaton on
`localhost:8081`, and a CORS allowlist that includes `http://localhost:3000` and
`http://localhost:3002`.

**3. Install and start.**

```bash
npm ci
npm run dev:backend
```

The backend listens on `http://localhost:3001`.

### LDE root scripts

| Script | Starts |
|---|---|
| `npm run dev` | The frontend only, on port 3000 |
| `npm run dev:backend` | The backend only, on port 3001 |
| `npm run dev:full` | Both, through `concurrently` |

Each runs the LDE's own `deps:check` first. There is no `dev:frontend` script. See
[Linked Data Explorer — Local Development](../../linked-data-explorer/developer/local-development.md)
for the explorer itself.

---

## Environment variables

Only variables prefixed `VITE_` reach the browser. The `REACT_APP_` names from before the
v2026.09.1 Vite migration are no longer read. Which tracked file applies depends on the
Vite mode:

| File | Loaded by |
|---|---|
| `.env.development` | `npm start` (Vite dev server, development mode) |
| `.env.production` | `npm run build`, locally **and** in both deploy workflows (production mode) |
| `.env.acceptance` | Nothing. No script passes `--mode acceptance`. The ACC workflow builds in production mode and overrides `VITE_BACKEND_URL` with the acceptance backend. |
| `.env.example` | Nothing — a template listing the variables. |

For a personal override, Vite also reads `.env.development.local`; `.gitignore` excludes
it and the other `.local` variants.

| Variable | Purpose | `.env.development` | Fallback when unset |
|---|---|---|---|
| `VITE_BACKEND_URL` | The LDE backend — SPARQL proxy, SHACL validation, TriplyDB service update, DSO handoff, DMN validate/deploy/evaluate | `http://localhost:3001` | `http://localhost:3001` in `DMNTab.jsx`, `useDsoImport.js`, `shaclHelper.js` and `triplydbHelper.js`; **`https://acc.backend.linkeddata.open-regels.nl`** in `ronlHelper.js` |
| `VITE_OPERATON_URL` | The Operaton base the DMN tab shows as its **Base URL**, and from which it builds the evaluate URL it **publishes** as `cprmv:implementedBy` | `http://localhost:8081` | `https://operaton.open-regels.nl` |
| `VITE_ENV` | Set in every `.env` file, read nowhere in `src/` | `development` | — |
| `VITE_BUILD_SHA`, `VITE_BUILD_RUN` | Build provenance, injected by the deploy workflows — see [Build Provenance](../../contributing/build-provenance.md) | — | local build |

The fallbacks only matter when a mode's file does not set the variable; `.env.development`
sets both URLs, so a normal `npm start` uses `localhost` throughout.

!!! warning "`VITE_OPERATON_URL` decides what a published DMN claims, not where it deploys"
    Deploy and evaluate both go through the Linked Data Explorer backend, which
    targets **its own** configured Operaton — so where a DMN lands in local
    development is decided by the local backend's `OPERATON_BASE_URL`, not by this
    variable. What this variable does decide is the evaluate endpoint the editor
    records for the decision and writes into the TTL as `cprmv:implementedBy`.
    Publishing from a local session therefore publishes a `localhost:8081`
    endpoint. Publish from acceptance or production, whose builds name the shared
    engine.

---

## Build and preview locally

```bash
npm run build     # vite build → dist/
npm run preview   # serves dist/ on http://localhost:3000
```

`npm run build` runs in production mode, so it reads `.env.production`: a local build
points at the **production** backend, `https://backend.linkeddata.open-regels.nl`. The
deploy workflows get their acceptance or production backend by setting
`VITE_BACKEND_URL` on the build step, not from `.env.acceptance`.

`npm run preview` uses the same fixed port as the dev server:
`preview: { port: 3000, strictPort: true }`.

---

## Tests and hooks

```bash
npm run test:ci   # everything, once, with coverage
npm test          # watch mode
```

See [Testing](testing.md) for the per-layer scripts, the Playwright journeys and the
current test count.

Husky installs two hooks:

| Hook | Runs |
|---|---|
| `pre-commit` | `npx lint-staged` — `prettier --write` and `eslint --fix` on staged files under `src/`, and `prettier --write` on `package.json` |
| `pre-push` | `npm run deps:check`, then `npm run lint`, then `npm run check-format` |

Neither hook runs the tests. The ACC deploy workflow runs `npm run lint` and
`npm run test:ci` before it builds, so a failing test blocks the pull request — but the
feedback arrives in CI rather than on your machine. Run `npm run test:ci` yourself before
pushing.

---

## Getting a change to ACC

!!! danger "`acc` accepts pull requests only"
    The `acc supply-chain gate` ruleset on `acc` requires a pull request and three
    passing checks, with no bypass actors. A direct push is rejected, for the
    repository owner as much as anyone.

| Required check | Workflow |
|---|---|
| `audit` | `zizmor.yml` (Supply-chain audit) |
| `scan` | `semgrep.yml` (Semgrep) |
| `Build and deploy ACC` | `azure-static-web-apps-orange-beach-0574c2a03.yml` (Deploy ACC) |

```bash
# 1. Work on a branch, never on acc directly
git checkout -b feature/your-topic

# 2. Commit, push the branch, and open a pull request against acc
git push -u origin feature/your-topic
gh pr create --base acc

# 3. Watch the required checks
gh pr checks

# 4. Merge once green. Merging is the push to acc, and triggers the deploy.
gh pr merge <n> --merge
```

The repository allows merge commits only — squash and rebase merging are disabled — and
deletes the head branch on merge.

**Preview deployments.** The Deploy ACC workflow's `changes` job lists the pull
request's files. `Build and deploy ACC` builds and uploads a Static Web Apps preview only
when at least one file falls outside `docs/`, `.claude/` and `*.md`. For a docs-only pull
request the job is skipped, which reports success, so the required check is still
satisfied. If the `changes` job itself fails, the build runs anyway.

See [Deployment](deployment.md) for the pipeline and
[Supply-Chain Pinning](../../contributing/supply-chain.md) for the gate.

---

## Maintainer scripts

These are not part of day-to-day development; several are run at each release.

| Script | What it does |
|---|---|
| `npm run lint:fix` | `eslint . --fix` |
| `npm run format` | `prettier --write .` |
| `npm run check-supply-chain` | Checks that each pinned GitHub Actions digest resolves to the version its comment claims, and that `SECURITY-PIPELINE.md` still matches the workflows. `--offline` skips the API. |
| `npm run check-mirror` | Compares `acc` and `main` on the `gitlab` mirror with GitHub. Never pushes; prints the command and exits 1 on drift. |
| `npm run check-previews` | Lists Azure Static Web Apps preview environments with no open pull request. Needs an Azure login. Never deletes. |
| `npm run sbom` | Writes the release SBOM (CycloneDX, production dependencies only) to `docs/sbom/`. `--check` exits 1 if it is missing or stale. |
