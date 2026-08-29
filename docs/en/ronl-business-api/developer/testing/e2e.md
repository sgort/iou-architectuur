---
component: RONL Business API
---

# E2E & live smoke

Three Playwright suites and four gated shell scripts. None of them runs as part
of `npm test`, and **one of the three runs in CI**.

| Suite | Where | Tests | In CI? | Last measured |
|---|---|---:|---|---|
| Frontend Playwright | `packages/frontend/e2e/` | 19 | No | 12 on 20 Aug, 7 on 22 Aug |
| Public-site Playwright | `packages/public-site/e2e/` | 6 | No | 19 Aug — **not re-run since** |
| **PA-demo Playwright** | `packages/pa-demo/e2e/` | **11** | **Yes** — `azure-pa-demo-acc.yml` | 29 Aug |
| Live smoke scripts | `scripts/*.sh` | 4 scripts | No | never run for these pages |

The PA-demo suite is covered on its own page — see
[PA-demo suite](pa-demo.md#the-playwright-suite). It is in CI because it needs
no backend, database or Keycloak: Playwright starts its own dev server and that
is the whole environment. The other two need a running stack, which is the
whole of why they are not there yet.

---

## Frontend Playwright suite

`packages/frontend/e2e/`, its own `playwright.config.ts`
(`npm run test:e2e --workspace=@ronl/frontend`). Chromium only, `workers: 1`.

The single worker is deliberate: two specs race to claim an identically-named
task for the same caseworker against the shared local Operaton engine, so the
suite trades parallelism for correctness.

The directory holds **19 tests across 7 specs**, measured in two groups:

- **12 tests** — the caseworker journeys, tenant isolation, role redirects and
  smoke, measured 20 August against v2026.08.20 in 54.1s. Detailed on
  [Caseworker](dashboards/caseworker.md#e2e).
- **7 tests** — the two PA cockpit specs, measured 22 August in 18.9s. Detailed
  on [PA cockpit](dashboards/pa-cockpit.md#e2e).

### What it needs running

`docker compose up -d` at the repo root (Keycloak + Postgres + Redis), the
backend and frontend dev servers, and a sibling `linked-data-explorer` repo's
backend on `:3001` — the last is required for the Procesbibliotheek journey.

`e2e/global-setup.ts` checks all of these before any test runs and fails fast
with the exact start commands if one is down. **It does not start anything
itself**, which is why *this* suite is not wired into CI: there is no human to
start the stack on a runner. The PA-demo suite has no such dependency and does
run in CI — the difference is the stack, not the tooling. See
[Overview → Roadmap](overview.md#roadmap) for what closing that would take.

### Getting JSON output

The config declares `list` and `html` reporters, not `json`. To capture machine
-readable results:

```bash
PLAYWRIGHT_JSON_OUTPUT_NAME=../../playwright-report/frontend-e2e.json \
  npm run test:e2e --workspace=@ronl/frontend -- --reporter=list,json
```

Three things will bite otherwise. `PLAYWRIGHT_JSON_OUTPUT_NAME` resolves
against the **cwd**, which under `--workspace` is `packages/frontend`, hence the
`../../`. Passing `--reporter` **replaces** the configured list, so the
auto-opening HTML report is lost unless you add it back. And do not redirect
stdout to a file: `globalTeardown` prompts interactively there
(`Clean up Operaton history…? [y/N]`), so the prompt would be swallowed into
the file and the terminal would appear to hang.

The HTML report also embeds the same result data, which is where the 20 August
figures came from when no JSON reporter was configured.

---

## Public-site Playwright suite

Covered on [Public site suite](public-site.md#playwright-suite) — six tests
including three axe-core accessibility scans, and the one suite here that
starts its own dev server.

Its figures date from 19 August and were **not** re-run for v2026.08.23.

---

## Live smoke suite (shell scripts, cross-app)

Four gated shell scripts under `scripts/`, deliberately kept out of `npm test` —
they hit real running services over the network, mutate real data in two cases,
and need real credentials for some tiers.

**These were not run for this page.** They are described from their
configuration and specs only.

| Script | Covers | Mutates? |
|---|---|---|
| `test-smoke-live.sh` | Cross-app health: Operaton, Keycloak, LDE, TriplyDB, CPRMV, media store, eDOCS reach/status, MCP layer | No |
| `test-edocs-live.sh` | eDOCS workspace and document lifecycle — see [eDOCS — Live Testing](edocs-live-testing.md) | Yes |
| `test-doccle-live.sh` | Doccle sender API — see [Doccle — Live Testing](doccle-live-testing.md) | Yes — not yet live-tested, still `DOCCLE_STUB_MODE=true` in every run so far |
| `test-m2m-routes.sh` | M2M decision-evaluation routes against ACC | No |

```bash
bash scripts/test-smoke-live.sh                                     # local, full run
CLIENT_SECRET=<secret> TARGET=acc bash scripts/test-smoke-live.sh   # against ACC
bash scripts/test-edocs-live.sh                                     # eDOCS, mutating
CLIENT_SECRET=<secret> bash scripts/test-doccle-live.sh              # Doccle, mutating
CLIENT_SECRET=<secret> bash scripts/test-m2m-routes.sh               # M2M routes vs ACC
```

Exit `0` when nothing failed, `1` on any real failure — a dependency that is
intentionally off (stub mode, no `CLIENT_SECRET`) skips with a `~` note, never
a red fail. `curl http://localhost:3002/v1/health | jq .`, or the ACC
equivalent, is the fastest single check of a running instance's dependency
status, independent of the smoke scripts.

---

## Rate limiting will masquerade as an outage

The backend rate-limits per IP. A short authoring journey measures ~21 requests
to `/v1/pa/*`, so two specs back to back can exhaust a low budget, and the UI
renders the resulting 429 as *"Kon dossiers niet laden"* — indistinguishable
from a backend that is down.

`e2e/helpers/rate-limit.ts` records the first 429 of a run and fails the test
with a message naming the throttle. It deliberately does **not** retry or wait
it out. The shipped default was raised to 1000/min in `config.ts`; note the
limiter keys on IP, so `TRUST_PROXY` decides whether that budget is per user or
per deployment.

The full account of how that was diagnosed — including two confident wrong
answers before anyone looked at the response codes — is on
[Writing tests](writing-tests.md#a-throttled-run-is-not-a-failing-run).
