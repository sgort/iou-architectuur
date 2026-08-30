---
component: RONL Business API
---

# E2E & live smoke

Three Playwright suites and four gated shell scripts. None of them runs as part
of `npm test`, and **one of the three runs in CI**.

| Suite | Where | Tests | In CI? | Last measured |
|---|---|---:|---|---|
| Frontend Playwright | `packages/frontend/e2e/` | **27** | No | **30 Aug — 27 passed, 1.9m** |
| Public-site Playwright | `packages/public-site/e2e/` | **6** | No | **30 Aug — 6 passed, 26.5s** |
| **PA-demo Playwright** | `packages/pa-demo/e2e/` | **11** | **Yes** — `azure-pa-demo-acc.yml` | **30 Aug — 11 passed, 14.7s** |
| Live smoke scripts | `scripts/*.sh` | 4 scripts | No | never run for these pages |

**44 end-to-end tests, all three suites green**, measured on 30 August 2026
against `acc` at `15dfbf9` with a full local stack running. This is the first
pass in which all three were run together rather than described from
configuration.

!!! warning "Count these with the runner, never with `grep`"
    A static count of `test(` across the frontend specs gives **23**. The runner
    reports **27**. `login-redirect.spec.ts` alone declares one `test(` and runs
    five, because the cases are parameterised — and `rip-r21-journey.spec.ts`
    contains a `test.skip(true, reason)` *inside* its test body, a runtime skip
    that a naive grep reads as a skipped declaration. Neither is visible from
    the source text.

!!! note "The public-site suite needs the backend, and says nothing useful without it"
    Run with no backend on `:3002`, three of its six fail on timeouts — the two
    search-journey tests and the detail-page axe scan, all of which need search
    results. That is an unmet dependency, not a regression: the same specs at the
    same commit pass 6/6 once the backend is up. Re-running serially reproduces
    the same three, so it is not contention either.

The PA-demo suite is covered on its own page — see
[PA-demo suite](pa-demo.md#the-playwright-suite). It is in CI because it needs
no backend, database or Keycloak: Playwright starts its own dev server and that
is the whole environment. The other two need a running stack, which is the whole
of why they are not there yet — though the gap is narrower than it looks: the
public-site suite needs **one** service, not five, and starts its own dev server
already.

---

## Frontend Playwright suite

`packages/frontend/e2e/`, its own `playwright.config.ts`
(`npm run test:e2e --workspace=@ronl/frontend`). Chromium only, `workers: 1`.

The single worker is deliberate: two specs race to claim an identically-named
task for the same caseworker against the shared local Operaton engine, so the
suite trades parallelism for correctness.

The directory holds **27 tests across 10 specs**, measured in one pass on
30 August 2026 against `acc` at `15dfbf9`: **27 passed, 1.9m**, no failures, no
flakes, nothing skipped.

| Spec | Tests | Covers |
|---|---:|---|
| `infra-board-journey.spec.ts` | 7 | The Infra-board, including a full sweep asserting no failed request and no console error |
| `pa-mock-journey.spec.ts` | 5 | PA cockpit mock mode against the real store |
| `login-redirect.spec.ts` | 5 | Role-based landing, parameterised per role |
| `protected-route.spec.ts` | 3 | Route guards |
| `pa-live-authoring.spec.ts` | 2 | Authoring against the live backend and a real database |
| `rip-r21-journey.spec.ts` | 1 | **The R2.1 phase, all twelve tasks, ending in the signing panel** |
| `caseworker-journey.spec.ts` | 1 | The caseworker journey end to end |
| `zorgtoeslag-journey.spec.ts` | 1 | The zorgtoeslag journey |
| `tenant-isolation.spec.ts` | 1 | Tenant scoping |
| `smoke.spec.ts` | 1 | Boot and render |

The R2.1 journey is the one to watch after a signing change. Because the
approval task carries `ronl:signatureRef`, the board renders the
[signing panel](../validsign-signing.md) where a form used to be — and the
journey previously drove every task by filling a form, so it failed on the last
one reporting that a form never rendered. A true statement about a task that no
longer has one.

It also carries a `test.skip(true, reason)` **inside** the test body, which
skips the run when its preconditions are not met and logs the reason first. It
did not skip in this measurement.

### Coverage per board

The 27 tests do not spread evenly, and three of the ten specs belong to no board
at all. This table is the one to check before claiming a board has or lacks
end-to-end coverage — the per-board pages defer to it.

| Board | Specs | Tests | Which |
|---|---:|---:|---|
| [Infra-board](dashboards/infra-board.md) | 2 | **8** | `infra-board-journey` (7, the shell), `rip-r21-journey` (1, the work) |
| [PA cockpit](dashboards/pa-cockpit.md) | 2 | **7** | `pa-mock-journey` (5), `pa-live-authoring` (2) |
| [Caseworker](dashboards/caseworker.md) | 2 | **2** | `caseworker-journey` (1), `zorgtoeslag-journey` (1) |
| [Woo-dashboard](dashboards/woo-dashboard.md) | 0 | **0** | — |
| *No single board* | 4 | **10** | `login-redirect` (5), `protected-route` (3), `tenant-isolation` (1), `smoke` (1) |

The last row is the reason a naive per-board sum does not reach 27: authentication
redirects, route guards, tenant scoping and the boot smoke test cut across every
board and belong to none.

!!! warning "Re-derive this table from the spec directory, not from the release being synced"
    The Infra-board specs landed on 24 August 2026 and this documentation
    continued to record the board as having *no end-to-end coverage at all*
    through two subsequent syncs. Nothing in a changelog-driven pass pointed at
    them, because neither release that added them was the one being documented.
    A per-board E2E claim is only as current as the last time somebody listed
    `packages/frontend/e2e/`.

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
