---
component: RONL Business API
---

# E2E & live smoke

Three Playwright suites and four gated shell scripts. None of them runs as part
of `npm test`, and **one of the three runs in CI**.

| Suite | Where | Specs | Tests | In CI? | Last measured |
|---|---|---:|---:|---|---|
| Frontend Playwright | `packages/frontend/e2e/` | **11** | **27**, and now a floor | No | **30 Aug — 27 passed, 1.9m** |
| Public-site Playwright | `packages/public-site/e2e/` | 1 | **6** | No | **30 Aug — 6 passed, 26.5s** |
| **PA-demo Playwright** | `packages/pa-demo/e2e/` | 1 | **11** | **Yes** — `azure-pa-demo-acc.yml` | **30 Aug — 11 passed, 14.7s** |
| Live smoke scripts | `scripts/*.sh` | 4 scripts | — | No | never run for these pages |

**44 end-to-end tests, all three suites green**, measured on 30 August 2026
against `acc` at `15dfbf9` with a full local stack running. That was the first
pass in which all three were run together rather than described from
configuration, and it is still the last.

!!! warning "Not re-run on 24 September — and now understating the frontend suite"
    The unit suites were re-measured against `main` at `86af73e` (v2026.09.11);
    the Playwright suites were **not**, for the third pass running. Every count
    in this page's tables dates from 30 August and is repeated unchanged rather
    than re-derived — a measured number is worth more stale than a guess is
    fresh. Two of the three suites need services these passes deliberately did
    not start.

    **What has changed is the inventory, and this time it moved.** Re-checked at
    `86af73e` straight from the spec tree: `packages/frontend/e2e/` now holds
    **eleven** specs, not ten. `thuisbatterij-journey.spec.ts` was added in this
    window, so the 27-test frontend figure — measured when there were ten —
    **cannot** include it. Read 27 as a floor rather than a total until the
    suite is run again. The other two directories are unchanged at one spec
    each, and so is the workflow wiring: the pa-demo spec runs in
    `azure-pa-demo-acc.yml` and only there, and no workflow runs the other two.

    The eleven: `caseworker-journey`, `infra-board-journey`, `login-redirect`,
    `pa-live-authoring`, `pa-mock-journey`, `protected-route`,
    `rip-r21-journey`, `smoke`, `tenant-isolation`, **`thuisbatterij-journey`**,
    `zorgtoeslag-journey`.

    The three `playwright.config.ts` files were re-read at `86af73e` — see
    [What each suite needs running](#what-each-suite-needs-running), which is
    current as of 24 September even though the counts above are not.

### What each suite needs running

The `webServer` block is declared **per config, not per spec**, so it applies to
every spec under that directory. This is the table to check before running
anything locally — it is what separates a suite you can start cold from one that
will fail its preconditions.

Re-read at `86af73e` on 24 September 2026.

| Config | Declares `webServer`? | Has a `globalSetup`? | What must already be up |
|---|---|---|---|
| `packages/frontend/e2e/playwright.config.ts` | **No — none at all** | **Yes** — `./global-setup.ts`, plus a `globalTeardown` | **Four services**: the frontend on `:5173`, the backend on `:3002`, Keycloak on `:8080`, and the sibling **Linked Data Explorer** backend on `:3001` — plus `docker compose up -d` behind them, and a deployed process/decision bundle |
| `packages/pa-demo/e2e/playwright.config.ts` | **Yes**, conditionally — `npm run dev` on `:5176` | No | Nothing. No backend, database or Keycloak; plato issues no network requests at all |
| `packages/public-site/e2e/playwright.config.ts` | **Yes**, conditionally — `npm run dev` on `:5175` | No | **The backend**, on whatever `VITE_API_URL` points at. The config starts the site but not the API, and these specs hit real search results |

Four things follow from that table:

- **The frontend suite is the one that needs a human**, and its `globalSetup`
  now checks considerably more than three URLs. In order, it refuses to run
  against production without `CONFIRM_PROD=1`; launches and closes a Chromium to
  prove the browser binary is actually on the machine; probes the frontend,
  backend `/v1/health`, Keycloak and — locally, or whenever `LDE_URL` is set —
  the LDE backend `/v1/health`; then calls `verifyRequiredProcesses()` and,
  separately, `verifyRequiredDecisions()` against the engine. Each failure
  throws naming what is missing and how to fix it, rather than surfacing later
  as a confusing connection error. It starts nothing itself, which is exactly
  why it is not in CI.
- **The decision check is a separate gate for a reason.** Decisions deploy
  *without* an Organization so a tenant-scoped process can reach them, so a
  missing or tenant-pinned DMN does not show up as a missing process — it
  surfaces mid-journey as a 500 on process start, or on a citizen's screen as
  *"probeer het opnieuw"*, neither of which mentions a decision.
- **"Starts its own server" is not the same as "self-contained."** public-site
  declares a `webServer` and still needs the backend; pa-demo declares one and
  needs nothing. Only pa-demo is genuinely cold-startable, which is why it is
  the suite that runs in CI.
- **Both conditional configs skip the server entirely when `E2E_BASE_URL` is
  set**, pointing `baseURL` at a deployed site instead — the post-deploy
  verification path against ACC. `reuseExistingServer` is on outside CI, so a
  dev server you already have running is attached to rather than duplicated.
  The frontend config has its own equivalent in `e2e/helpers/target.ts`, which
  reads `FRONTEND_URL`, `BACKEND_URL`, `KEYCLOAK_URL`, `LDE_URL` and
  `OPERATON_URL` and falls back to localhost for each.

!!! note "`workers: 1` on the frontend suite is deliberate, not a leftover"
    The config pins a single worker and says why: every Operaton-touching spec
    shares the same stateful local engine, and two files creating
    identically-named tasks for the same caseworker —
    `tenant-isolation.spec.ts` and `zorgtoeslag-journey.spec.ts`, both *"Case
    review: provisional entitlement decision"* — raced when run in different
    workers. A `.first()` task-list match grabbed the other file's task
    mid-flight, producing a real Operaton save conflict (*"Opslaan mislukt"*),
    not merely a bad selector. One worker serializes everything, trading suite
    speed for correctness.

    This is the one place in the repository where serial execution is the right
    answer, and it is worth contrasting with the unit suites, where it is not —
    see [Overview](overview.md#a-parallel-failure-is-not-a-finding). The
    difference is that here the shared state is real and external; there it is
    the machine's own CPU.

!!! warning "Count these with the runner, never with `grep`"
    A static count of top-level `test(` across the eleven frontend specs gives
    **24** at `86af73e`. The runner reported **27** across ten of them on
    30 August. `login-redirect.spec.ts` alone declares one `test(` and runs
    five, because the cases are parameterised — and `rip-r21-journey.spec.ts`
    contains **two** `test.skip(true, reason)` calls *inside* test bodies,
    runtime skips that a naive grep reads as skipped declarations. Neither is
    visible from the source text.

    This is why `thuisbatterij-journey.spec.ts` is listed above without a test
    count rather than with the 1 its source shows. The only honest way to fill
    that cell is to run the suite.

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

The directory held **27 tests across 10 specs** when it was last run, in one
pass on 30 August 2026 against `acc` at `15dfbf9`: **27 passed, 1.9m**, no
failures, no flakes, nothing skipped. It holds **eleven specs** at `86af73e`,
so the 27 is a floor — see the warning at the top of this page.

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
| **`thuisbatterij-journey.spec.ts`** | *not yet measured* | **New in this window.** A third deep two-persona journey: a citizen applies for a Thuisbatterij subsidy, the six-decision `RechtEnHoogteSubsidieThuisbatterij` DRD evaluates, and the caseworker reviews the resulting task |

!!! note "What the thuisbatterij journey is actually guarding"
    Read from the spec at `86af73e`, not run. Its processes deploy under
    tenant-id `flevoland` while the DMNs they call deploy **without** a tenant,
    so every business-rule task carries
    `camunda:decisionRefTenantId="${null}"` to reach them. Drop that attribute
    and the engine refuses to instantiate at all — *"no decision definition
    deployed with key 'AwbCompletenessCheck' and tenant-id 'flevoland'"* —
    which reaches a user as a 500 from `POST /v1/process/:key/start` and an
    unexplained *"aanvraag kon niet worden ingediend"*. That is an ACC outage
    that already happened once; this spec exists to catch the next one before a
    deploy repeats it, which is also why `globalSetup` gained its separate
    decision check.

!!! success "`rip-r21-journey.spec.ts` now starts R2.1 with a project identity — [issue #165](https://github.com/sgort/ronl-business-api/issues/165) is closed"
    Fixed in `aadedfc` on 20 September 2026 and **closed as completed the same
    day**. Established by reading the spec and the component at `86af73e` on
    24 September, **not** by running either.

    Through v2026.09.9 the spec clicked the R2.1 start button without filling
    the two fields v2026.09.8 had made required, so it waited ninety seconds for
    a control that could never become enabled. **The spec had not been updated
    alongside its component**; the component was right.

    What it does now (`rip-r21-journey.spec.ts:617-630`):

    ```ts
    const startForm = page.locator('.pb-new-project');
    const startButton = page.locator('.pb-new-project + button');
    await expect(startForm).toBeVisible();
    await expect(startButton).toHaveText(/R2\.1 starten/);

    await startForm.getByLabel('Projectnummer').fill(PROJECT_NUMBER);
    await startForm.getByLabel('Projectnaam').fill(PROJECT_NAME);
    await expect(startButton).toBeEnabled();
    ```

    Three things in that block are worth copying rather than merely reading:

    - **Both fields are filled from module-scope fixtures** — `E2E-26014` and
      *"E2E — R2.1 journey (test, safe to delete)"* — deliberately unmistakable
      rather than realistic, so a project this spec leaves behind is obvious in
      the board.
    - **`toBeEnabled()` comes before the click.** That turns the gate into an
      assertion instead of an implicit wait, so the next regression here names
      the gate rather than timing out on it.
    - **The locator is pinned structurally** to the block the step means, and
      what it found is asserted before it is clicked. Two buttons in this tab
      read *"R2.1 starten"* — this one and the bulk "start the selected
      projects" — in different branches of `PhaseDetail`'s ternary. They cannot
      render together today, so a bare `getByRole` resolves; pinning keeps that
      true if the branches ever converge.

    A further assertion switches to the WIP tab and checks the started instance
    carries the number and name it was started with. Without it the spec would
    pass just as happily against a build that dropped both values on the floor.

    The component confirms it, read at the same commit:
    `PhaseDetail.tsx` renders both inputs as `required` inside
    `<div className="pb-new-project">`, and the sibling button is

    ```tsx
    disabled={submitting || !newProjectReady}
    ```

    ```tsx
    const newProjectReady = newProjectNumber.trim() !== '' && newProjectName.trim() !== '';
    ```

    Spec and component now agree.

The R2.1 journey is the one to watch after a signing change. Because the
approval task carries `ronl:signatureRef`, the board renders the
[signing panel](../validsign-signing.md) where a form used to be — and the
journey previously drove every task by filling a form, so it failed on the last
one reporting that a form never rendered. A true statement about a task that no
longer has one. Issue #165 was the same failure mode one step earlier in the
journey: the UI grew a precondition and the spec did not hear about it. Twice in
two releases, in one spec, is the pattern to take from it — this journey drives
more UI surface than any other here, so it is the first to notice when that
surface moves.

It also carries **two** `test.skip(true, reason)` calls **inside** test bodies,
which skip the run when preconditions are not met and log the reason first.
There was one at v2026.09.9; the second arrived in `097ff84`, *"skip rather than
fail where a tier signs for real"* — a tier with real signing configured cannot
complete the journey's approval task, and skipping with a reason is the honest
outcome there rather than a red run. Neither skipped in the 30 August
measurement, which predates both.

### Coverage per board

The 27 tests do not spread evenly, and four of the eleven specs belong to no
board at all. This table is the one to check before claiming a board has or
lacks end-to-end coverage — the per-board pages defer to it.

| Board | Specs | Tests | Which |
|---|---:|---:|---|
| [Infra-board](dashboards/infra-board.md) | 2 | **8** | `infra-board-journey` (7, the shell), `rip-r21-journey` (1, the work) |
| [PA cockpit](dashboards/pa-cockpit.md) | 2 | **7** | `pa-mock-journey` (5), `pa-live-authoring` (2) |
| [Caseworker](dashboards/caseworker.md) | 3 | **2 + thuisbatterij** | `caseworker-journey` (1), `zorgtoeslag-journey` (1), `thuisbatterij-journey` (not yet measured) |
| [Woo-dashboard](dashboards/woo-dashboard.md) | 0 | **0** | — |
| *No single board* | 4 | **10** | `login-redirect` (5), `protected-route` (3), `tenant-isolation` (1), `smoke` (1) |

The last row is the reason a naive per-board sum does not reach 27:
authentication redirects, route guards, tenant scoping and the boot smoke test
cut across every board and belong to none.

The Caseworker row is the one that moved: `thuisbatterij-journey.spec.ts` is a
third deep journey ending in a caseworker review task, and it landed after the
only pass in which this suite was run. Its test count is left blank rather than
guessed — it declares a single `test()`, but the warning below is exactly about
not trusting that reading.

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

`e2e/global-setup.ts`, re-read at `86af73e`, probes **four** URLs before any
test runs — `http://localhost:5173`, `http://localhost:3002/v1/health`,
`http://localhost:8080` for Keycloak, and `http://localhost:3001/v1/health` —
and throws with each missing one named:

```text
E2E preconditions not met — target: local dev stack.
- Frontend not reachable at http://localhost:5173
- Backend not reachable at http://localhost:3002/v1/health
- Keycloak not reachable at http://localhost:8080
- LDE backend not reachable at http://localhost:3001/v1/health
```

The LDE probe runs locally, or whenever `LDE_URL` is set explicitly — a shared
tier has no LDE backend under a predictable name, so it is skipped there rather
than failed. Against a remote target the per-probe timeout rises from 3s to 15s,
because a cold-started App Service is slower to answer than loopback.

Two further gates run after the probes, and each throws with its own
instructions: `verifyRequiredProcesses()` checks the fixture bundle is deployed
under the right tenant, and `verifyRequiredDecisions()` checks the DMN
definitions are deployed **without** an Organization. A decision listed *under*
an Organization is the failure mode here, not an absent one.

Before any of that, `globalSetup` launches and closes a Chromium. Playwright
keeps its browsers outside `node_modules`, so `npm ci` installs a new Playwright
without fetching the build it needs; every spec would otherwise die in
`browserType.launch` and the one line explaining it would be buried in the first
of N identical failures. The launch costs about a second and is the thing that
actually has to work, which is why it is preferred to comparing versions or
guessing at paths.

It also refuses to run against production unless `CONFIRM_PROD=1` is set. These
journeys are not read-only — they start real process instances and complete real
tasks, which against production is real case data in the audit log.

**It does not start anything itself**, and `playwright.config.ts` declares no
`webServer`, which is why *this* suite is not wired into CI: there is no human
to start the stack on a runner. The PA-demo suite has no such dependency and
does run in CI — the difference is the stack, not the tooling. See
[Overview → Roadmap](overview.md#roadmap) for what closing that would take.

The probe deliberately builds its own `AbortController` rather than using
`AbortSignal.timeout()`: the latter did not always clean up its internal timer
before the fetch settled, crashing Node on Windows with a libuv
`UV_HANDLE_CLOSING` assertion during process exit. That crash used to be listed
as a blocker for putting this suite in CI and no longer is.

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

Its own tests were last counted on 30 August; the timing and pass figures on
[Public site suite](public-site.md#playwright-suite) date from 19 August and
were re-run for none of v2026.08.23, v2026.09.7, v2026.09.9 or v2026.09.11. The
package's unit suite has grown three times since (**32 files, 235 tests on
24 September 2026**, up from 31 and 225), so the six E2E tests are an inventory
figure, not a fresh result. The inventory itself was re-checked at `86af73e`:
still one spec, still in no workflow.

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
