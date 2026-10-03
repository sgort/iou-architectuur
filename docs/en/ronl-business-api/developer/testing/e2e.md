---
component: RONL Business API
---

# E2E & live smoke

Three Playwright suites and four gated shell scripts. None of them runs as part
of `npm test`, and **one of the three runs in CI**.

| Suite | Where | Specs | Tests | In CI? | Last measured |
|---|---|---:|---:|---|---|
| Frontend Playwright | `packages/frontend/e2e/` | **11** | **28** | No | **3 Oct — 27 passed, 1 skipped, 2.8m** |
| Public-site Playwright | `packages/public-site/e2e/` | 1 | **6** | No | **3 Oct — 6/6 serially, 7.8s; 2 timeouts in the parallel run** |
| **PA-demo Playwright** | `packages/pa-demo/e2e/` | 1 | **11** | **Yes** — `azure-pa-demo-acc.yml` | **3 Oct — 11 passed, 10.2s** |
| Live smoke scripts | `scripts/*.sh` | 4 scripts | — | No | never run for these pages |

**45 end-to-end tests, all three suites green — the frontend with one
journey skipping itself by design, and the public site green serially.**
Measured on **3 October 2026** for v2026.10.0 (`main` at `0625d48`), from the
working checkout on `acc` at `0e3eed8`, against the full local stack the
developer already had running; nothing was started or stopped for the run.
It is the first pass since 30 August 2026 in which the three were run rather
than described from configuration.

!!! success "Re-run on 3 October — the frontend count is a total again"
    Every pass from 12 to 30 September left the Playwright suites alone, and
    the 27-test frontend figure they repeated was measured when there were ten
    specs, so it could not include `thuisbatterij-journey.spec.ts`. On
    3 October the runner collected **28 tests across the eleven specs** —
    27 passed and one skipped:

    - **`thuisbatterij-journey`** ran for the first time on these pages:
      **1 test, passed, 8.4s**.
    - **`rip-r21-journey`** skipped itself, by one of its two runtime guards:
      the local stack signs with the real ValidSign
      (`VALIDSIGN_STUB_MODE=false`), and the journey will not request a binding
      signature, so it refuses before sending a package and creates nothing.
      See [below](#frontend-playwright-suite).

    **The public-site suite went red once and green serially, and is recorded
    that way.** Run with its config's default workers — six on that machine —
    it returned **4 passed, 2 failed**: both search-journey tests
    (`publiek.spec.ts:6` and `:27`) timed out after 10s waiting for the
    search-result filter checkbox to appear. Re-run with `--workers=1` against
    the same running backend, it passed **6/6 in 7.8s**. *6/6 serially; 2
    timeouts in the parallel run* — not a defect until it fails on its own;
    see [Public-site Playwright suite](#public-site-playwright-suite).

    **The inventory is thirteen specs**, unchanged since v2026.09.11: eleven in
    `packages/frontend/e2e/`, plus `packages/pa-demo/e2e/plato-demo.spec.ts`
    and `packages/public-site/e2e/publiek.spec.ts`. v2026.10.0 changed no
    spec, no `playwright.config.ts` and no helper:
    `git diff ae06c9e 0625d48 -- 'packages/*/e2e'` is empty. The workflow
    wiring is unchanged too: the pa-demo spec runs in `azure-pa-demo-acc.yml`
    and only there, and no workflow runs the other two.

    The eleven: `caseworker-journey`, `infra-board-journey`, `login-redirect`,
    `pa-live-authoring`, `pa-mock-journey`, `protected-route`,
    `rip-r21-journey`, `smoke`, `tenant-isolation`, `thuisbatterij-journey`,
    `zorgtoeslag-journey`.

    **History: v2026.09.14 changed three specs and the login helper, none in
    its test count** — read from the source at `ae06c9e`:

    - **`e2e/helpers/auth.ts` matches the medewerker login button exactly**
      (`9f54e82`). v2026.09.13 added *"Inloggen met uw Flevoland-account"* to
      the landing page, and `loginAsMedewerker` looked its button up by the
      name *"Inloggen"*, which Playwright matches as a substring — so it
      resolved to both buttons and strict mode refused to click. The commit
      records that **26 of 28 E2E tests against ACC failed at that one line**;
      that run is the commit's account, not a measurement these pages made.
      The helper now passes `exact: true`, because the plain *"Inloggen"* in the
      top bar is the Keycloak login it fills in, while the new button goes to
      Entra ID.
    - **`caseworker-journey.spec.ts` accepts the Dutch Kapvergunning task
      names** (`10e83ce`), and **`zorgtoeslag-journey.spec.ts` and
      `tenant-isolation.spec.ts` the Dutch Zorgtoeslag ones** (`1f0e52b`) —
      the same pattern `thuisbatterij-journey` adopted in v2026.09.12; see
      [below](#frontend-playwright-suite).

    The three `playwright.config.ts` files are unchanged between `86af73e` and
    `0625d48`, and `e2e/global-setup.ts` changed only in v2026.09.13, when its
    fix messages began naming `npm run e2e:deploy-fixtures` — see
    [What each suite needs running](#what-each-suite-needs-running).

### What each suite needs running

The `webServer` block is declared **per config, not per spec**, so it applies to
every spec under that directory. This is the table to check before running
anything locally — it is what separates a suite you can start cold from one that
will fail its preconditions.

Re-read at `86af73e` on 24 September 2026; the configs are unchanged at
`2443adc` (v2026.09.12), `963fe24` (v2026.09.13), `ae06c9e` (v2026.09.15) and
`0625d48` (v2026.10.0).

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
    **24** at `86af73e`, and still 24 at `2443adc`, `ae06c9e` and `0625d48`.
    The runner reported **27** across ten of them on 30 August, and **28**
    across all eleven on 3 October. `login-redirect.spec.ts` alone declares
    one `test(` and runs five, because the cases are parameterised — and
    `rip-r21-journey.spec.ts` contains **two** `test.skip(true, reason)` calls
    *inside* test bodies, runtime skips that a naive grep reads as skipped
    declarations, and one of which fired on 3 October. Neither is visible
    from the source text.

    This is why `thuisbatterij-journey.spec.ts` was listed without a test count
    until it was run, rather than with the 1 its source shows. The runner
    agreed on 3 October, but only the run could say so.

!!! note "The public-site suite needs the backend, and says nothing useful without it"
    Run with no backend on `:3002`, three of its six fail on timeouts — the two
    search-journey tests and the detail-page axe scan, all of which need search
    results. That is an unmet dependency, not a regression: the same specs at the
    same commit pass 6/6 once the backend is up. Re-running serially reproduces
    the same three, so it is not contention either.

    **3 October was the other case, and the check told them apart.** With the
    backend up, the default parallel run failed **two** — the two
    search-journey tests, waiting 10s for the filter checkbox — while the
    detail-page axe scan, which also needs search results, passed. Re-run
    serially it was 6/6 in 7.8s. A missing backend fails the same three
    serially and in parallel; this failed two in parallel only. That is
    consistent with contention, not with an absent dependency, and a
    parallel-only failure is not a defect until it fails on its own —
    recorded as *6/6 serially; 2 timeouts in the parallel run*.

The PA-demo suite is covered on its own page — see
[PA-demo suite](pa-demo.md#the-playwright-suite). It is in CI because it needs
no backend, database or Keycloak: Playwright starts its own dev server and that
is the whole environment. The other two need a running stack, which is the whole
of why they are not there yet — though the gap is narrower than it looks: the
public-site suite needs **one** service, not five, and starts its own dev server
already.

### Deploying the E2E fixtures

**New in v2026.09.13**, and read at `963fe24` rather than run: the repository
root gained a script for the one precondition the table above describes but
cannot help you meet — the process and decision bundle that the frontend
suite's `globalSetup` refuses to start without.

```bash
npm run e2e:deploy-fixtures    # repo root
```

!!! info "It is a shim. The deployer lives in linked-data-explorer"
    `scripts/deploy-e2e-fixtures.mjs` in this repository **deploys nothing**. It
    resolves a linked-data-explorer checkout — `LDE_PATH`, defaulting to a
    sibling directory — and, if
    `<LDE>/scripts/deploy-e2e-fixtures.mjs` is not there, exits 1 saying so and
    naming the two ways to fix it. Otherwise it runs that script with
    `cwd` set to the LDE checkout and passes arguments and the exit code
    straight through.

    **The deployer moved because two copies had already drifted.** Both read
    `ronl:documentRef` out of the BPMN; when that attribute became a
    comma-separated list, the copy here silently stopped matching any template
    and the whole bundle would have failed to deploy. The fixtures, the
    manifest and the deploy route all live in linked-data-explorer, so the
    script does too — and the command name stays here, because this
    repository's E2E gate is what needs the bundle and what prints the command
    when it is missing.

What the real deployer does, and what it needs:

| | |
|---|---|
| **Talks to** | the **linked-data-explorer backend** at `LDE_URL`, default `http://localhost:3001` — never straight to Operaton, so the bundle is also recorded in LDE's own store and the `boardOwner` tag is derived by the same code a Modeler deploy uses |
| **Refuses** | any target that is not on this machine. It asks `GET /v1/dmns/process/deploy-target` first and rejects a host that is not `localhost`, `127.0.0.1` or `::1` — a fixture bundle on a shared tier is drift, not a deployment |
| **Reads** | `linked-data-explorer/e2e-fixtures/manifest.json`, plus the external `zorgtoeslag_resultaat` rules set from `TTL_EDITOR_REPO`, default `../ttl-editor` — the manifest names that decision but deliberately does not ship it |
| **Step 1** | every file under `sharedDecisions.files` through `POST /v1/dmns/deploy`, **without** a tenant id, which is the point: each `businessRuleTask` resolves its decision with `decisionRefTenantId="${null}"` |
| **Step 2** | one `POST /v1/dmns/process/deploy` per top-level manifest entry — sub-processes, forms and documents in the same request, `organization` set to the tenant directory it lives in — one request per entry, as one Modeler action is |
| **Exit** | 0 when everything deployed, 1 on the first failure. Every run deploys a new version of everything, since LDE disables Operaton's duplicate filtering; the gate reads the latest version, so a run always leaves the engine matching the fixtures on disk |

!!! note "The gate prints this command, which is why the shim had to stay"
    `packages/frontend/e2e/global-setup.ts` checks four things, in order, and
    throws on the first that fails with a message naming the fix:

    1. **Chromium actually launches.** It launches a browser and closes it
       rather than comparing version strings — Playwright keeps its browsers
       outside `node_modules`, so `npm ci` installs a new Playwright without
       fetching the build it needs, and every spec would otherwise die in
       `browserType.launch` with the one explanatory line buried in the first
       of N identical failures. The fix it names is
       `npx playwright install chromium`.
    2. **Four services answer**: the frontend, the backend's `/v1/health`,
       Keycloak, and — locally, or whenever `LDE_URL` is set — the LDE
       backend's `/v1/health`. Three seconds each locally, fifteen against a
       remote tier.
    3. **Every process in the manifest is deployed under its tenant**
       (`verifyRequiredProcesses()`).
    4. **Every decision those processes call is deployed _without_ an
       Organization** (`verifyRequiredDecisions()`), so a tenant-scoped process
       can reach it.

    **Failures 3 and 4 both print `npm run e2e:deploy-fixtures` as the fix** —
    which is precisely why the shim stays in this repository after the deployer
    left it. A gate that names a command has to name one that exists.

    Checks 3 and 4 are separate on purpose. A missing or tenant-pinned DMN does
    not show up as a missing process; it surfaces mid-journey as a 500 on
    process start, or on a citizen's screen as *"probeer het opnieuw"*, neither
    of which mentions a decision.

!!! warning "What a full local E2E run actually needs"
    Five things, and none of them is started by Playwright for this suite:

    - `docker compose up -d` at this repository's root — Keycloak, Postgres,
      Redis;
    - `npm run dev` at this repository's root — frontend on `:5173` and backend
      on `:3002`;
    - `npm run dev:backend` in the **linked-data-explorer** checkout — the LDE
      backend on `:3001`, which is also what the fixture deploy goes through;
    - a **ttl-editor** checkout beside them, for the one external decision;
    - `npx playwright install chromium`, then `npm run e2e:deploy-fixtures`.

    Only then does `npm run test:e2e --workspace=@ronl/frontend` get past its
    own preconditions. That list is the whole reason this suite is not in CI,
    and the reason its figures went unmeasured from 30 August until a pass on
    3 October found the stack already up.

---

## Frontend Playwright suite

`packages/frontend/e2e/`, its own `playwright.config.ts`
(`npm run test:e2e --workspace=@ronl/frontend`). Chromium only, `workers: 1`.

The single worker is deliberate: two specs race to claim an identically-named
task for the same caseworker against the shared local Operaton engine, so the
suite trades parallelism for correctness.

**Measured 3 October 2026: 28 tests across 11 specs — 27 passed, 1 skipped,
2.8m**, one worker, against the developer's already-running local stack.
Nothing failed and nothing was retried. The previous run, on 30 August 2026
against `acc` at `15dfbf9`, was 27 tests across the 10 specs there were then:
27 passed, 1.9m.

| Spec | Tests | 3 October | Covers |
|---|---:|---|---|
| `infra-board-journey.spec.ts` | 7 | 7 passed | The Infra-board, including a full sweep asserting no failed request and no console error |
| `pa-mock-journey.spec.ts` | 5 | 5 passed | PA cockpit mock mode against the real store |
| `login-redirect.spec.ts` | 5 | 5 passed | Role-based landing, parameterised per role |
| `protected-route.spec.ts` | 3 | 3 passed | Route guards |
| `pa-live-authoring.spec.ts` | 2 | 2 passed | Authoring against the live backend and a real database |
| `rip-r21-journey.spec.ts` | 1 | **skipped** — real ValidSign on the stack | **The R2.1 phase, all twelve tasks, ending in the signing panel** |
| `caseworker-journey.spec.ts` | 1 | passed, 24.5s | The caseworker journey end to end |
| `zorgtoeslag-journey.spec.ts` | 1 | passed, 6.1s | The zorgtoeslag journey |
| `tenant-isolation.spec.ts` | 1 | passed, 11.5s | Tenant scoping |
| `smoke.spec.ts` | 1 | passed | Boot and render |
| **`thuisbatterij-journey.spec.ts`** | **1** | **passed, 8.4s — first measurement** | **New in v2026.09.11.** A third deep two-persona journey: a citizen applies for a Thuisbatterij subsidy, the six-decision `RechtEnHoogteSubsidieThuisbatterij` DRD evaluates, and the caseworker reviews the resulting task |

!!! note "The thuisbatterij journey accepts both task names — edited in v2026.09.12"
    `0e71fd3`, *"match the Thuisbatterij tasks by their Dutch names as well"*,
    widened the two task matchers the caseworker half of the journey depends
    on, because the Thuisbatterij process definitions — which come from
    linked-data-explorer — rename those tasks in the swimlane redesign. Each
    regex now accepts the old English name **or** the new Dutch one:

    | Task | Before the redesign | After it |
    |---|---|---|
    | The review | *Case review: recht en hoogte subsidie…* | *Beoordeling behandelaar: recht en hoogte subsidie…* |
    | The follow-up notify task | *Phase 6: Notify applicant of decision* | *Fase 6: Aanvrager informeren over besluit* |

    Accepting both rather than switching to the new names is deliberate, and the
    commit says why: the journey should pass on engines still running the old
    definitions and on those running the new ones. The test count is
    unchanged — one `test()`. Read from the spec at `2443adc`; the spec was
    first run by these pages on 3 October 2026, and passed.

!!! note "Three more specs accept the Dutch names, and the login helper matches exactly — v2026.09.14"
    linked-data-explorer redrew the Kapvergunning and Zorgtoeslag processes in
    swimlanes with Dutch task names, and three specs followed the
    Thuisbatterij one, each regex accepting the old English name **or** the
    new Dutch one so the journeys pass against either deployment:

    | Spec | Commit | Review task, after the redesign | Notify task, after it |
    |---|---|---|---|
    | `caseworker-journey.spec.ts` | `10e83ce` | *Beoordeling behandelaar: besluit kapvergunning* | *Fase 6: Aanvrager informeren over besluit* |
    | `zorgtoeslag-journey.spec.ts` | `1f0e52b` | *Beoordeling behandelaar: besluit voorlopige aanspraak* | *Fase 6: Aanvrager informeren over besluit* |
    | `tenant-isolation.spec.ts` | `1f0e52b` | *Beoordeling behandelaar: besluit voorlopige aanspraak* | *Fase 6: Aanvrager informeren over besluit* |

    In `tenant-isolation.spec.ts` the change matters more than a selector
    usually does: `REVIEW_TASK_NAME` became a regex so that the check that a
    Flevoland caseworker **cannot** see the task stays meaningful after the
    rename, instead of passing on a name that no longer exists. A negative
    assertion against a stale name is green for the wrong reason.

    Separately, `e2e/helpers/auth.ts` now finds the medewerker login button
    with `{ name: 'Inloggen', exact: true }` (`9f54e82`), because the landing
    page's new *"Inloggen met uw Flevoland-account"* button made the substring
    match ambiguous and Playwright's strict mode refused to click either. Every
    spec that signs a medewerker in goes through that helper. Test counts are
    unchanged in all four files; read from the source at `ae06c9e`, and all
    four passed when run on 3 October.

!!! note "What the thuisbatterij journey is actually guarding"
    Read from the spec at `86af73e`, not run; the passage below is unchanged at `2443adc`. Its processes deploy under
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
measurement, which predates both. **On 3 October the second one fired**, on a
local stack configured with `VALIDSIGN_STUB_MODE=false`, and logged:

```text
[rip-r21-journey] SKIPPED — local dev stack signs with the real ValidSign
(VALIDSIGN_STUB_MODE=false), and this journey will not request a binding
signature. Nothing was created — the refusal happens before
POST /task/:id/package. Run it against a target where VALIDSIGN_STUB_MODE=true.
```

That is the outcome the commit designed for, and it is why the run reads
*27 passed, 1 skipped* rather than 28 passed. It also means the R2.1 work —
and v2026.10.0's signing changes, the panel now shared with the caseworker
inbox and signing state kept per task — was not driven in a browser by this
pass. A run against a target in stub mode is what would.

### Coverage per board

The 28 tests do not spread evenly, and four of the eleven specs belong to no
board at all. This table is the one to check before claiming a board has or
lacks end-to-end coverage — the per-board pages defer to it.

| Board | Specs | Tests | Which |
|---|---:|---:|---|
| [Infra-board](dashboards/infra-board.md) | 2 | **8** | `infra-board-journey` (7, the shell), `rip-r21-journey` (1, the work — skipped on 3 October, see above) |
| [PA cockpit](dashboards/pa-cockpit.md) | 2 | **7** | `pa-mock-journey` (5), `pa-live-authoring` (2) |
| [Caseworker](dashboards/caseworker.md) | 3 | **3** | `caseworker-journey` (1), `zorgtoeslag-journey` (1), `thuisbatterij-journey` (1) — all three matching the Dutch task names as well as the English ones since v2026.09.14 |
| [Woo-dashboard](dashboards/woo-dashboard.md) | 0 | **0** | — |
| *No single board* | 4 | **10** | `login-redirect` (5), `protected-route` (3), `tenant-isolation` (1), `smoke` (1) |

The last row is the reason a naive per-board sum of the boards alone does not
reach 28: authentication redirects, route guards, tenant scoping and the boot
smoke test cut across every board and belong to none.

The Caseworker row is the one that moved: `thuisbatterij-journey.spec.ts` is a
third deep journey ending in a caseworker review task. It landed after the
30 August run, and until 3 October its count was left blank rather than
guessed from the single `test()` it declares — the warning above is exactly
about not trusting that reading. The run confirmed it: one test.

No spec drives Besluitvorming, the caseworker section v2026.10.0 added; it is
covered by unit tests only — see [Caseworker](dashboards/caseworker.md#e2e).

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

**Re-run on 3 October 2026**, for the first time since 30 August, against the
developer's already-running backend — and the one suite in this pass that went
red before it went green:

| Run | Workers | Result | Time |
|---|---:|---|---:|
| Default (`fullyParallel: true`, no `workers` set) | 6 | **4 passed, 2 failed** — `publiek.spec.ts:6` *search → filter → detail → back preserves the filtered URL* and `:27` *a deep link with filters pre-applied renders those filters checked*, each a `TimeoutError` after 10s waiting for `getByRole('checkbox', { name: /Regel/ })` | 17.2s |
| `--workers=1` | 1 | **6 passed** | 7.8s |

**Recorded as 6/6 serially, with 2 timeouts in the parallel run — not as a
defect.** Both failures are the same wait in the two tests that need a
filtered result list; the detail-page axe scan, which also needs search
results, passed in the same parallel run, and the serial run passed all six
against the same backend. That is consistent with contention, not with a
missing backend (which fails three, serially too), and nothing failed on its
own. It is worth
watching rather than dismissing: if this suite is wired into CI — see
[Overview → Roadmap](overview.md#roadmap) — that 10-second wait under
parallel workers is the first thing the run will test. The spec is unchanged
since `2443adc` and still in no workflow. See
[Public site suite](public-site.md#playwright-suite).

---

## Live smoke suite (shell scripts, cross-app)

Four gated shell scripts under `scripts/`, deliberately kept out of `npm test` —
they hit real running services over the network, mutate real data in three
cases (one of them only data it created itself), and need real credentials for
some tiers.

**These were not run for this page.** They are described from their
configuration and source only — `test-m2m-routes.sh` read at `0625d48`.

| Script | Covers | Mutates? |
|---|---|---|
| `test-smoke-live.sh` | Cross-app health: Operaton, Keycloak, LDE, TriplyDB, CPRMV, media store, eDOCS reach/status, MCP layer | No |
| `test-edocs-live.sh` | eDOCS workspace and document lifecycle — see [eDOCS — Live Testing](edocs-live-testing.md) | Yes |
| `test-doccle-live.sh` | Doccle sender API — see [Doccle — Live Testing](doccle-live-testing.md) | Yes — not yet live-tested, still `DOCCLE_STUB_MODE=true` in every run so far |
| `test-m2m-routes.sh` | The active `/v1/m2m` operations: the reads, `decision.evaluate`, and — since v2026.09.14 (#214) — a write lifecycle of start, claim, complete and delete. Since v2026.10.0 it also asserts that **`POST /v1/m2m/process/history` filters** — a request filtered on one `processDefinitionKey` must return at least one instance and none of another key, since a dropped filter answers 200 with the whole history (#263); that the deprecated **`GET` answers with `Deprecation: @1790985600`**; and that **start and complete refuse a caller-supplied `municipality` with `400 RESERVED_VARIABLE`** (#261), the refused completion leaving the task open for the real one. Its tenant-isolation check reads the problem's `code`. Local by default, reading the seeded client secret from the realm file; `TARGET=acc` needs an explicit `CLIENT_SECRET`, and on ACC the M2M surface now uses ACC's main engine (#262) | Yes, but only its own: the lifecycle starts two instances and removes both, and never writes to an instance it did not create — if the reserved-variable guard on start ever failed, the stray instance is cancelled at once |

```bash
bash scripts/test-smoke-live.sh                                     # local, full run
CLIENT_SECRET=<secret> TARGET=acc bash scripts/test-smoke-live.sh   # against ACC
bash scripts/test-edocs-live.sh                                     # eDOCS, mutating
CLIENT_SECRET=<secret> bash scripts/test-doccle-live.sh              # Doccle, mutating
bash scripts/test-m2m-routes.sh                                     # M2M routes, local
TARGET=acc CLIENT_SECRET=<secret> bash scripts/test-m2m-routes.sh   # M2M routes vs ACC
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
