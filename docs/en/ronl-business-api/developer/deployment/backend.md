---
component: RONL Business API
---

# Backend Deployment (Azure App Service)

The backend deploys to **Azure App Service** (Node.js 22) from GitHub Actions.
There are two deployment targets, ACC and PROD, and since v2026.09.10 **both are
deployed by CI** — until then the workflows ended at an uploaded artifact and a
person ran a script afterwards.

!!! info "There is no approval gate"
    Neither the `acc` nor the `production` GitHub environment carries a
    protection rule, so nothing pauses a deploy waiting for a reviewer. What
    stands between a commit and production is the promotion workflow and the
    pull request required to reach `main` — not an approval on the deployment
    itself.

---

## GitHub Actions workflows

| Workflow file | Trigger | Target |
|---|---|---|
| `.github/workflows/azure-backend-acc.yml` | Push to `acc` with changes in `packages/backend/**`, `packages/shared/**`, the root manifest or lockfile, `.nvmrc` or its own file — plus every pull request to `acc`, where the deploy steps are skipped | `ronl-business-api-acc` |
| `.github/workflows/azure-backend-prod.yml` | `workflow_call` from `promote-to-production.yml`, or `workflow_dispatch` | `ronl-business-api-prod` |

The production workflow has **no branch trigger of its own**. A push to `main`
starts the promotion workflow, which decides whether the backend needs deploying
and calls this one first, before any site that depends on it.

---

## How a promotion reaches production

```
push to main
    ↓
promote-to-production.yml         (no paths filter — it must always start)
    ↓
changes         scripts/promotion-targets.sh reads the pushed commit range
    ↓
backend         azure-backend-prod.yml, alone and first
    ↓
frontend · pa-demo · public-site  in parallel, once the backend is done
```

**Why the backend goes first and alone.** Until v2026.09.10 four workflows fired
at once on a push to `main` and nothing sequenced them. The backend is the
slowest — it runs the full backend suite before it packages anything, while a
Static Web App deploy is a build and an upload — so the frontends reliably
finished first. A frontend calling a route the deployed backend does not yet
serve gets a 404, and on the public site that is worse than transient: its build
**prerenders against the live API**, so a prerender inside that window bakes the
failure into the deployed output.

**The sites wait for a result, not merely for the absence of failure.** They run
when `needs.backend.result` is `success` **or** `skipped` — a skipped backend
means nothing backend-shaped changed, so the deployed backend already serves
what they expect. `cancelled` or `failure` means nobody knows, and they do not
go.

**A promotion that cannot read its own commit range deploys everything.** Three
cases reach that fail-safe: a manual dispatch, which carries no `before`; a
first or force push, whose `before` is all zeros; and a `before` the clone
cannot resolve.

!!! danger "If the promotion workflow breaks, nothing deploys — silently"
    The four production workflows are not required checks on `main`, which
    requires `audit` alone. A promotion whose orchestrating workflow fails
    produces a red run and no deployment, and nothing else reports it. The
    escape hatch is `workflow_dispatch` on each of the four.

---

## Build and deployment steps

Both backend workflows follow the same process:

```yaml
 1. Checkout code
 2. Setup Node.js from .nvmrc (22.23.2)
 3. npm ci                          (install all workspace dependencies)
 4. Build shared package            (npm run build --workspace=@ronl/shared)
 5. Lint backend                    (npm run lint in packages/backend)
 6. Lint the OpenAPI document       (npm run lint:openapi in packages/backend)
 7. Unit tests                      (npm test in packages/backend)
 8. Build TypeScript                (npm run build in packages/backend → dist/)
 9. Verify dist/index.js exists
10. Prepare deployment package:
      deploy/
        dist/                       (compiled TypeScript, structure preserved)
        package.json                (backend package.json at deploy root)
        openapi/openapi.json        (the document GET /v1/openapi.json serves)
        build-info.json             (commit SHA, run number, run id)
        node_modules/               (production dependencies, from the lockfile)
        node_modules/@ronl/shared/  (shared package dist + package.json)
        .deployment                 (SCM_DO_BUILD_DURING_DEPLOYMENT=false)
11. Create deployment zip → Upload artifact
12. azure/login                     (OIDC — no publish profile, no secret)
13. az webapp deploy --type zip
14. Liveness check                  (5 attempts, 10s apart → /v1/health/live)
15. Verify the deploy took effect   (12 attempts, 15s apart → /v1/health build.sha)
```

Steps 12–15 are skipped on a pull request to `acc`, so a pull request builds and
tests the backend without shipping it while the build check stays required.

Step 6 lints the published contract against the NL API Design Rules 2.2.1
ruleset before the tests run, so a document that breaks a rule fails fast and
names it; the coverage gate inside `npm test` then checks the document against
the routes actually served. `openapi/openapi.json` is generated from
`openapi/openapi.yaml` by the `prebuild` hook and is gitignored, so step 10 copies
it into the artifact explicitly — only the JSON, since the YAML source, the
vendored ruleset and the Spectral config are build-time inputs. The backend
resolves it as `../../openapi/openapi.json` from `dist/openapi`, and reads it once
at startup. See [API specification](../../reference/api-specification.md).

### Authentication is OIDC

The cheap fix would have been a publish profile, as a neighbouring repository
uses — but **SCM basic auth is disabled on both App Services**
(`basicPublishingCredentialsPolicies/scm` `allow=false`, measured on the
resources rather than assumed), so a publish-profile deploy would be rejected.

OIDC is not a new mechanism here: the hand-run scripts already deploy with `az
webapp deploy` over an ARM token from `az login`. The workflow makes that same
call with a machine identity instead of a human session, which removes the
failure that once stopped a release reaching acceptance — an expired login,
discovered after the merge. The acceptance and production identities are
separate, each scoped to its own App Service, so a mistake in the acceptance
workflow cannot reach production.

The job grants itself `id-token: write` to mint the token `azure/login`
exchanges, and reads `vars.AZURE_CLIENT_ID_ACC` / `_PROD`, `vars.AZURE_TENANT_ID`
and `vars.AZURE_SUBSCRIPTION_ID`. Those are repository **variables**, not
secrets, which is why the promotion passes this call no secrets at all.

### The bundle installs from the lockfile

It used to be `npm install --production` in a directory holding a `package.json`
and **no lockfile**, so it re-resolved every caret range at deploy time. On
29 August 2026 an acceptance deploy ran with `@anthropic-ai/sdk` freshly jumped
42 minor versions and `uuid` five majors, none of it matching what any build had
verified.

The install now runs in a staging copy holding the root manifest and lockfile
and the two manifests the backend needs, filtered to the backend workspace with
production dependencies only:

```bash
npm ci --omit=dev --workspace=@ronl/backend --no-audit --no-fund
```

`npm ci` refuses a lockfile that does not satisfy the manifests rather than
resolving around it. Two `prepare` scripts are deleted from the staged copy
first: the root's is `husky`, a devDependency, and `@ronl/shared`'s is `tsc` —
under `--omit=dev` npm runs both with nothing installed to run them.

!!! note "Un-hoisted dependencies are packaged, not rejected"
    The staging install's guard used to assert that **no** production dependency
    is installed under `packages/backend/node_modules`. `altcha-lib` has been
    recorded there by the lockfile since it was added, so the guard failed every
    run.

    `deploy/` is the backend's root, so an un-hoisted entry belongs in
    `deploy/node_modules` and is merged in after the hoisted tree is copied.
    Where the same package is **also** hoisted the two versions cannot both live
    there — something else resolves to the hoisted one, and overwriting it would
    break that instead — so that case still fails rather than guessing.

`@ronl/shared` is copied in **after** the install, deliberately. Copied in
before, npm sees a package not declared in the manifest it is installing, prunes
it as extraneous, and the app dies at runtime with *"Cannot find module
'@ronl/shared'"*.

### The deploy proves itself

A liveness check alone cannot tell a new deployment from an old one: the
previous build keeps answering while Azure starts the new one, so the check
passes against either. `build-info.json` in the artifact records which commit and
run produced it, `/v1/health` reports it, and the workflow polls that value —
twelve attempts, fifteen seconds apart — until it equals the commit just
deployed. Without it, a deploy that silently left the old artifact serving would
have passed every check above it.

It is a file in the artifact rather than an App Service setting on purpose:
settings persist across deploys and can describe a build that is no longer
running, which is the failure this exists to detect.

!!! warning "Deployment package structure"
    The `dist/` folder must be copied as a folder (`cp -r dist deploy/`), not flattened (`cp -r dist/* deploy/`). Flattening breaks TypeScript module resolution paths and causes 404 errors on all `/v1/*` endpoints after deployment.

---

## Azure App Service configuration

**App name:** `ronl-business-api-acc` / `ronl-business-api-prod`  
**Runtime:** `NODE|22-lts`  
**Startup command:** `node dist/index.js`

App Service pins the Node runtime at the major only: `az webapp list-runtimes
--os linux` offers `NODE|22-lts`, `NODE|24-lts` and `NODE|26`, with no exact
version and no digest. What can be kept is the major in step with `.nvmrc`,
which is `22.23.2`. A Node major bump therefore changes two places in a fixed
order — **switch both App Services to the new `NODE|<major>-lts` first, then
merge the `.nvmrc` bump** — because the other order builds the artifact on one
major and runs it on another. No pull-request check runs against an App Service,
so nothing enforces this; `SECURITY-PIPELINE.md` records it as the rule, and a
disabled Renovate rule holds Node 24 until it is followed (see
[CI/CD → Node runtime](../cicd.md#node-runtime)).

Azure App Settings (environment variables) are configured via CLI or the Azure Portal. Set the production values from `docs/deployment/environment-variables.md`:

```bash
az webapp config appsettings set \
  --name ronl-business-api-prod \
  --resource-group rg-ronl-prod \
  --settings \
    NODE_ENV=production \
    PORT=8080 \
    KEYCLOAK_URL=https://keycloak.open-regels.nl \
    KEYCLOAK_REALM=ronl \
    KEYCLOAK_CLIENT_ID=ronl-business-api \
    JWT_ISSUER=https://keycloak.open-regels.nl/realms/ronl \
    JWT_AUDIENCE=ronl-business-api \
    CORS_ORIGIN=https://mijn.open-regels.nl \
    OPERATON_BASE_URL=https://operaton.open-regels.nl/engine-rest \
    DATABASE_URL="postgresql://pgadmin:<password>@ronl-postgres-prod.postgres.database.azure.com:5432/audit_logs?sslmode=require" \
    REDIS_URL="redis://ronl-redis-prod.redis.cache.windows.net:6380?password=<key>&ssl=true" \
    LOG_LEVEL=info \
    HELMET_ENABLED=true \
    SECURE_COOKIES=true \
    TRUST_PROXY=true \
    AUDIT_LOG_ENABLED=true \
    ENABLE_TENANT_ISOLATION=true
```

The full variable reference is in [Environment Variables](../../reference/environment-variables.md).

Complete command for **ACC** (all 30+ variables in one call):

```bash
az webapp config appsettings set \
  --name ronl-business-api-acc \
  --resource-group rg-ronl-acc \
  --settings \
    NODE_ENV=production \
    PORT=8080 \
    HOST=0.0.0.0 \
    CORS_ORIGIN="https://acc.mijn.open-regels.nl" \
    KEYCLOAK_URL="https://acc.keycloak.open-regels.nl" \
    KEYCLOAK_REALM="ronl" \
    KEYCLOAK_CLIENT_ID="ronl-business-api" \
    JWT_ISSUER="https://acc.keycloak.open-regels.nl/realms/ronl" \
    JWT_AUDIENCE="ronl-business-api" \
    TOKEN_CACHE_TTL="300" \
    OPERATON_BASE_URL="https://operaton.open-regels.nl/engine-rest" \
    OPERATON_TIMEOUT="30000" \
    DATABASE_URL="postgresql://pgadmin:<PASSWORD>@ronl-postgres-acc.postgres.database.azure.com:5432/audit_logs?sslmode=require" \
    DATABASE_POOL_MIN="2" \
    DATABASE_POOL_MAX="10" \
    REDIS_URL="redis://ronl-redis-acc.redis.cache.windows.net:6380?password=<PRIMARY_KEY>&ssl=true" \
    REDIS_TTL="3600" \
    RATE_LIMIT_WINDOW_MS="60000" \
    RATE_LIMIT_MAX_REQUESTS="1000" \
    RATE_LIMIT_PER_TENANT="true" \
    LOG_LEVEL="info" \
    LOG_FORMAT="json" \
    LOG_FILE_ENABLED="true" \
    LOG_FILE_PATH="/home/site/wwwroot/logs" \
    LOG_FILE_MAX_SIZE="10m" \
    LOG_FILE_MAX_FILES="7" \
    AUDIT_LOG_ENABLED="true" \
    AUDIT_LOG_INCLUDE_IP="true" \
    AUDIT_LOG_RETENTION_DAYS="2555" \
    HELMET_ENABLED="true" \
    SECURE_COOKIES="true" \
    TRUST_PROXY="true" \
    ENABLE_METRICS="true" \
    ENABLE_HEALTH_CHECKS="true" \
    ENABLE_TENANT_ISOLATION="true" \
    DEFAULT_MAX_PROCESS_INSTANCES="1000"
```

For PROD, substitute `ronl-business-api-acc` → `ronl-business-api-prod`, `rg-ronl-acc` → `rg-ronl-prod`, and the ACC URLs → PROD URLs.

!!! warning "There is no `KEYCLOAK_CLIENT_SECRET` to set"
    `ronl-business-api` is a **public client**: the realm export gives it
    `publicClient: true`, no secret and no service account. The setting was once
    declared on `Config`, populated from the environment and required in
    production — and read by no code path, which is how the production App
    Service came to hold the literal `not-used`. It was removed in v2026.09.10
    rather than corrected. Do not put it back.

!!! note "The two tiers differ on the rate limit, deliberately"
    Acceptance runs `RATE_LIMIT_MAX_REQUESTS=1000`, raised from 100 so a full
    end-to-end run from one machine stops throttling in the PA cockpit specs,
    which spend about twenty requests per authoring journey.

    **Production should not follow automatically.** `TRUST_PROXY` is `true` on
    both tiers, so the limiter buckets **per client** rather than once per
    deployment — which is what makes a raise a convenience decision on
    acceptance and a weakening of a real defence on a public tier.

---

## Post-deployment verification

The workflow verifies the deployment in two stages, and the second is the one
that matters:

```bash
# 1. Liveness — 5 attempts, 10 seconds apart
curl -s -o /dev/null -w "%{http_code}" https://api.open-regels.nl/v1/health/live
# Expected: 200

# 2. Identity — 12 attempts, 15 seconds apart
curl -s https://api.open-regels.nl/v1/health | jq -r '.data.build.sha'
# Expected: the commit this run deployed
```

A liveness check passes against the *previous* build while Azure starts the new
one, so on its own it cannot tell a successful deploy from one that silently
left the old artifact serving. Comparing `build.sha` can. If either stage fails,
the job fails and the deployment is reported unsuccessful.

Roll back by dispatching `azure-backend-prod.yml` against the previous commit,
or from the Azure Portal: App Service → Deployment Center → select a previous
deployment → *Redeploy*.

---

## Manual deployment

`deploy-backend-to-acc.sh` and `deploy-backend-to-prod.sh` still exist at the
repository root. They are the **break-glass path** for when CI cannot deploy —
not the normal route, and not a shortcut.

!!! danger "The scripts resolve dependencies on a developer machine"
    They install without the lockfile, against semver ranges, with no
    package-manager cooldown and no CI record of what was installed. That is the
    exact pattern the workflow was changed to stop doing, and the repository's
    supply-chain register keeps it as a **named exception** rather than treating
    it as closed: *the exception closes when the scripts are retired, not when
    the workflow lands.*

    Use `workflow_dispatch` on `azure-backend-prod.yml` or
    `azure-backend-acc.yml` instead wherever that is possible — it deploys one
    tier's backend alone, from the lockfile, with the verification above.

Both scripts carry real safety rails: they refuse to run off `acc`, refuse a
dirty working tree, and resolve an archiver before building anything. The
portable path falls back to the bsdtar bundled at `System32\tar.exe`, because
Info-ZIP's `zip` cannot be installed on a managed Windows laptop. They also fail
fast on a dead Azure session rather than part-way through.
