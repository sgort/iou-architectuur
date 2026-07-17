# Testing

RONL Business API has two layers of testing: a **Jest unit/integration suite**
that runs against mocks (fast, no live services, what CI validates indirectly
via lint+build), and a **live smoke suite** — four gated shell scripts that hit
real running services and are deliberately kept out of the Jest run. This page
covers both. For eDOCS specifically, see
[eDOCS — Live Testing](edocs-live-testing.md), which has the full endpoint
results table.

---

## Backend unit & integration tests

**Jest** with **ts-jest**, **Supertest** for HTTP integration tests. Test files
are colocated with the source they cover — `packages/backend/src/**/*.test.ts`
— and picked up automatically; there is no separate `tests/` directory.

```bash
npm test --workspace=@ronl/backend      # all tests, with coverage report
npm run test:watch --workspace=@ronl/backend   # watch mode
npx jest --config packages/backend/jest.config.js --no-coverage --testPathPattern=<name>
```

From the repo root, `npm test` runs every workspace's test script (backend
Jest suite + frontend Vitest suite).

A dedicated coverage campaign brought every backend feature area under test —
routes, services, middleware, MCP providers, the eDOCS live-switch path, the
standalone MCP servers. Run `npm test --workspace=@ronl/backend` for the
current coverage report (`packages/backend/coverage/`); the repo's
`docs/TESTS.md` keeps a per-file inventory and explains the handful of
deliberate low-coverage artifacts (e.g. `utils/config.ts` self-runs `dotenv`
on import and can't be meaningfully unit-tested; `utils/logger.ts` is mocked
so its transport-wiring lines don't execute under test).

**What to test when adding a route or service:**

- Unit test: the service function in isolation, mocking external calls
- Integration test: the route with a valid JWT → expected response, and with
  no/invalid JWT → `401`

---

## Live smoke suite

Four gated shell scripts under `scripts/`, each exercising real cross-app
seams the Jest suite mocks out. They're a developer / pre-deploy tool, never
wired into `npm test` — they hit running services over the network and need
real credentials for some tiers.

| Script | Covers | Mutates? |
| --- | --- | --- |
| `test-smoke-live.sh` | Cross-app health: Operaton, Keycloak, LDE, TriplyDB, CPRMV, media store, eDOCS reach/status, MCP layer | No |
| `test-edocs-live.sh` | eDOCS workspace + document lifecycle — see [eDOCS — Live Testing](edocs-live-testing.md) | Yes (creates real workspaces/documents) |
| `test-doccle-live.sh` | Doccle sender API — see [Doccle — Live Testing](doccle-live-testing.md) | Yes — **not yet live-tested**, still `DOCCLE_STUB_MODE=true` in every run so far |
| `test-m2m-routes.sh` | M2M decision-evaluation routes against ACC | No |

### `test-smoke-live.sh`

```bash
bash scripts/test-smoke-live.sh                     # local, full run
CLIENT_SECRET=<secret> TARGET=acc bash scripts/test-smoke-live.sh   # against ACC
```

eDOCS is checked two ways here on purpose: a Keycloak-free in-process probe
(reflects the local `.env`) and a JWT-gated call through the running backend
(reflects the backend process's config) — comparing the two exposes config
drift after an `.env` edit without a restart.

| Tier | Check | How | Signal |
| --- | --- | --- | --- |
| gate | Backend live | `GET /v1/health/live` | aborts the whole run if the backend is down |
| 1 | Operaton + Keycloak | `GET /v1/health` | both dependencies report `up` |
| 1 | Cross-app reachability | `GET /v1/health/external` | `lde`, `triplydb`, `cprmv` each `up` |
| 1 | Media path | `GET /v1/media-aggregator/health` | store healthy + cached-article count |
| direct | eDOCS 1/2 (local) | `EdocsService.healthCheck()` in-process | `reachable` + `authenticated` (skips if stub) |
| 2a | Client token (M2M) | `client_credentials` grant | a token is obtainable |
| 2a | eDOCS 2/2 (backend) | `GET /v1/edocs/status` (JWT-gated) | `reachable` + `authenticated` + `library` |
| 2b | User token (role) | `password` grant | a token is obtainable |
| 2b | MCP layer | `GET /v1/mcp/sources` | providers advertised (`403` = user lacks role) |

A dependency that's intentionally off (eDOCS stub mode, MCP disabled, no
`CLIENT_SECRET`) skips with a `~` note, never a red fail — only genuine
unreachability or a real auth failure fails the run.

### `test-edocs-live.sh`

Mutating — creates a real workspace and/or document. Full results table and
known-issue details: [eDOCS — Live Testing](edocs-live-testing.md).

### `test-doccle-live.sh`

Mutating — creates a real receiver and document on Doccle staging when run
live. Results table (currently all "not yet"): [Doccle — Live Testing](doccle-live-testing.md).

### `test-m2m-routes.sh`

```bash
CLIENT_SECRET=<secret> bash scripts/test-m2m-routes.sh
```

Validates the active M2M route operations (decision evaluation) against ACC.

---

## Health check verification

The health endpoint is the fastest way to verify a running instance:

```bash
curl http://localhost:3002/v1/health | jq .          # local
curl https://acc.api.open-regels.nl/v1/health | jq .  # ACC
```

```json
{
  "name": "RONL Business API",
  "status": "healthy",
  "uptime": 42.1,
  "services": {
    "keycloak": { "status": "up", "latency": 45 },
    "operaton": { "status": "up", "latency": 112 }
  }
}
```

`status`: `healthy` (`200`), `degraded` (`503` — one or more services down),
`unhealthy` (`503` — the health check itself failed).

---

## Pre-commit / pre-push hooks and CI

**Pre-commit** (via `lint-staged`): ESLint + Prettier on changed
`packages/backend/**/*.ts` and `packages/frontend/**/*.{ts,tsx}` files;
Prettier on changed `*.{json,md}`.

**Pre-push**: build `@ronl/shared`, `type-check` across all workspaces,
`lint`, then `check-format`.

**CI** (GitHub Actions, on push to `acc`/`main`): installs, builds
`@ronl/shared`, lints, builds the TypeScript, then deploys. **CI does not run
the Jest suite** — `npm test` is a manual discipline enforced by review, not
an automated gate. Run it yourself before pushing anything nontrivial. A
post-deployment health check (5 retries, 10s apart) confirms the deployed
instance is responding before the workflow marks the deployment successful.
