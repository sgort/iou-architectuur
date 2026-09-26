---
component: RONL Business API
---

# Backend Development

The backend is `packages/backend` (`@ronl/backend`) — a Node.js 22 Express application written in TypeScript. The repository pins the runtime in `.nvmrc` at `22.23.2`, and the root `engines.node` is `>=22`; both App Service plans run `NODE|22-lts`.

---

## Project structure

```
packages/backend/
├── openapi/
│   ├── openapi.yaml              # The OpenAPI 3.1 description, written by hand
│   ├── pending.json              # Served operations not described yet — may only shrink
│   ├── .spectral.yaml            # Spectral config: extends the ruleset below, with recorded exceptions
│   └── adr-ruleset-2.2.1.yaml    # NL API Design Rules 2.2.1 ruleset, vendored
│                                 # (openapi.json is generated beside these and gitignored)
├── scripts/
│   ├── build-openapi.cjs         # openapi.yaml → openapi.json; info.version from package.json
│   ├── jest-global-setup.cjs     # Builds openapi.json before every Jest run
│   ├── jest-setup-env.cjs        # The one variable validateConfig() demands in tests
│   └── edocs-healthcheck.ts, doccle-healthcheck.ts, reset-pa-data.ts
└── src/
    ├── index.ts                  # Bootstrap: middleware, mounts from the registry, startup
    ├── routes/
    │   ├── registry.ts           # The /v1 route topology: mounts, banner, coverage gate
    │   ├── root.routes.ts        # Service banner at /
    │   ├── openapi.routes.ts     # GET /v1/openapi.json
    │   ├── health.routes.ts      # /v1/health, /live, /ready, /external
    │   ├── process.routes.ts     # /v1/process
    │   ├── decision.routes.ts    # /v1/decision
    │   ├── task.routes.ts        # /v1/task
    │   ├── brp.routes.ts, hr.routes.ts, capacity.routes.ts, public.routes.ts
    │   ├── rip.routes.ts, edocs.routes.ts, doccle.routes.ts, validsign.routes.ts
    │   └── admin.routes.ts, m2m.routes.ts, mcp.routes.ts
    ├── openapi/
    │   ├── document.ts           # Reads the built openapi/openapi.json
    │   ├── coverage.test.ts      # Document vs. served routes vs. pending.json
    │   └── testing/routeOperations.ts  # Lists served and documented operations
    ├── middleware/
    │   ├── version.middleware.ts # API-Version response header
    │   ├── audit.middleware.ts   # Audit entry per request, and auditLog()
    │   └── tenant.middleware.ts  # Municipality claim extraction and validation
    ├── auth/
    │   ├── jwt.middleware.ts     # JWT validation, role and assurance-level guards
    │   └── tenant-access.ts      # Every tenant decision for process and task access
    ├── pa-monitoring/            # Policy analysis: /v1/pa routers, sources, curation
    ├── media-aggregator/         # /v1/media-aggregator
    ├── rip-swimlane/             # BPMN swimlane rendering for RIP
    ├── mcp-servers/              # eDOCS, LDE and TriplyDB MCP servers
    ├── services/                 # Operaton, audit, eDOCS, ValidSign, Doccle, … plus llm/, mcp/, document/
    ├── types/                    # audit.types.ts, auth.types.ts
    └── utils/                    # config, cors-origin, client-ip, logger, errors, …
```

Tests sit beside the file they cover as `*.test.ts`.

---

## Middleware stack

Middleware is registered in this order in `src/index.ts`:

1. `helmet()` — security headers (CSP, HSTS), only when `config.security.helmetEnabled`
2. `cors()` — `origin` is `corsOriginCallback(...)`; see [CORS](#cors)
3. `rateLimit()` — one global limiter, skipped for the ValidSign callback path, which has its own
4. `express.json({ limit: '1mb' })` — wrapped so the ValidSign callback path skips it and parses its own body
5. `express.urlencoded({ limit: '1mb' })`
6. Request logging — method, path, query, IP, user agent
7. `API-Version` header — set by an inline handler and again by `versionMiddleware`; both write `package.json`'s version, so the duplicate is harmless
8. `auditMiddleware` — writes an audit entry once the response is sent
9. The root router at `/` — the service banner
10. The route registry — `app.use(mount, router)` for each entry of `routes/registry.ts`, in array order
11. 404 handler — `NOT_FOUND`
12. Error handler — `INTERNAL_ERROR`, with the message hidden when `NODE_ENV` is `production`

JWT validation (`jwt.middleware.ts`) is applied per router or per route, not globally. Public endpoints (e.g. `GET /v1/health`) do not require authentication.

---

## Adding a new route

A route is one entry in `src/routes/registry.ts`. That array drives three things: `index.ts` mounts from it, the banner at `/` advertises from it, and `src/openapi/coverage.test.ts` compares the OpenAPI document against it.

1. Create `src/routes/myfeature.routes.ts` following the existing pattern:

```typescript
import { Router, Request, Response } from 'express';
import { jwtMiddleware } from '@auth/jwt.middleware';
import logger from '@utils/logger';

const router = Router();

router.use(jwtMiddleware);

router.get('/', async (req: Request, res: Response) => {
  try {
    res.json({ success: true, data: { ... } });
  } catch (error) {
    logger.error('myfeature error', error);
    res.status(500).json({ success: false, error: { code: 'ERROR', message: String(error) } });
  }
});

export default router;
```

2. Add it to `routeRegistry` in `src/routes/registry.ts`:

```typescript
import myfeatureRoutes from './myfeature.routes';

// in routeRegistry:
{
  mount: '/v1/myfeature',
  router: myfeatureRoutes,
  advertiseAs: 'myfeature',
  summary: 'What this mount serves',
},
```

   Every mount is under `/v1` — `registry.test.ts` checks it — and there is no `/api` alias. Omit `advertiseAs` only for a second router on a mount the first already advertises, as `/v1/validsign` and `/v1/pa` do.

3. Describe every operation it serves in `openapi/openapi.yaml`. `coverage.test.ts` fails when a served operation is neither documented nor listed in `openapi/pending.json`, when a documented operation is not served, when a pending one is already documented or no longer served, and when `pending.json` grows past its ceiling of 18. The pending list may only shrink: a new route is described, not parked. Run `npm run lint:openapi` as well — both backend workflows run it. See [API specification](../reference/api-specification.md) for the published document.

**Mount order is data.** Express matches in mount order, and the ValidSign callback router must precede the authenticated router on the same `/v1/validsign` path, because ValidSign sends no token. That ordering is the array order in `registry.ts`, and `registry.test.ts` asserts it.

---

## eDOCS service and external task worker
 
`edocs.service.ts` wraps the OpenText eDOCS REST API. It authenticates once via `POST /connect`, caches the `X-DM-DST` session token extracted from the `Set-Cookie` response header, and re-authenticates automatically on `401`/`403`. Key methods:
 
```typescript
ensureWorkspace(projectNumber: string, projectName: string): Promise<EdocsWorkspaceResult>
uploadDocument(workspaceId: string, filename: string, contentBase64: string, metadata: EdocsDocumentMetadata): Promise<EdocsDocumentResult>
getWorkspaceDocuments(workspaceId: string): Promise<...>
healthCheck(): Promise<{ status: 'up' | 'down' | 'stub' }>
```
 
When `EDOCS_STUB_MODE=true` (the default), all methods return realistic fake data and log what they would have done. The stub is transparent — callers cannot distinguish it from a live server.
 
`externalTaskWorker.service.ts` polls Operaton's external task API (`POST /external-task/fetchAndLock`) using long-polling (`asyncResponseTimeout: 20 000 ms`). It handles two topics:
 
| Topic | Reads | Writes |
|---|---|---|
| `rip-edocs-workspace` | `projectNumber`, `projectName` | `edocsWorkspaceId`, `edocsWorkspaceName`, `edocsWorkspaceCreated` |
| `rip-edocs-document` | `edocsWorkspaceId`, `documentTemplateId`, `edocsDocumentVariableName`, + template variables | `<edocsDocumentVariableName>` (e.g. `edocsIntakeReportId`) |
 
The worker is started inside the `app.listen()` callback and stopped in both `SIGTERM` and `SIGINT` handlers. It will not begin polling until the HTTP server is fully bound.
 
For configuration and live-mode switchover, see [Copilot Studio — eDOCS OAuth Integration](copilot-studio-edocs.md).

---
 
## M2M route group
 
`m2m.routes.ts` exposes the full Operaton surface to machine-to-machine clients without tenant scoping. It applies `jwtMiddleware` only — `tenantMiddleware` is intentionally absent.
 
A `M2M_ALLOWED_OPERATIONS` constant at the top of the file controls which operations are active. Commenting out an entry returns `403 OPERATION_NOT_PERMITTED` for that operation with no other code changes required.
 
The route group is instantiated with a dedicated `OperatonService` when `OPERATON_M2M_BASE_URL` is set, otherwise it reuses the shared singleton:
 
```typescript
const m2mOperatonService = config.operaton.m2mBaseUrl
  ? new OperatonService(
      config.operaton.m2mBaseUrl,
      config.operaton.m2mUsername,
      config.operaton.m2mPassword
    )
  : operatonService;
```
 
See [Operaton MCP Client](operaton-mcp-client.md) for the full endpoint reference and Keycloak setup.

---

## Authentication on protected routes

Apply the JWT middleware to a whole router with `router.use(jwtMiddleware)`, or to a single route:

```typescript
import { jwtMiddleware } from '@auth/jwt.middleware';

router.post('/sensitive', jwtMiddleware, async (req, res) => {
  const { municipality, roles } = req.user!;
  // ...
});
```

After `jwtMiddleware`, `req.user` is populated from the validated token. `jwt.middleware.ts` also exports `optionalJwtMiddleware`, `requireRoles(...)` and `requireAssuranceLevel(...)`. Tenant decisions for process and task access — `tenantAllows`, `caseReadAllowed`, `denyTenant`, `resolveStartTenant` — live in `auth/tenant-access.ts`, and every tenant refusal answers `403 TENANT_MISMATCH`.

---

## TypeScript path aliases

The `tsconfig.json` configures path aliases for clean imports:

```
@/*          → src/*
@routes/*    → src/routes/*
@services/*  → src/services/*
@middleware/* → src/middleware/*
@auth/*      → src/auth/*
@models/*    → src/models/*
@types/*     → src/types/*
@utils/*     → src/utils/*
```

`tsc-alias` resolves these aliases during the build step (`npm run build`).

`tsconfig.json` uses `module: node16` / `moduleResolution: node16` (upgraded from CommonJS/Node10) — this enables subpath-exports resolution and aligns TypeScript's module semantics with the Node.js runtime actually executing the compiled output.

---

## Development commands

```bash
npm run dev                    # tsx watch (hot-reload); predev builds openapi.json first
npm run build                  # tsc + tsc-alias → dist/; prebuild builds openapi.json first
npm run start                  # Run compiled dist/index.js
npm run lint                   # ESLint 9 flat config
npm run lint:fix               # ESLint with auto-fix
npm run type-check             # tsc --noEmit (no output, type check only)
npm test                       # Jest with coverage
npm run test:serial            # Jest with coverage, --runInBand
npm run test:unit              # Unit tests only
npm run test:integration       # Integration tests only
npm run build:openapi          # openapi/openapi.yaml → openapi/openapi.json
npm run lint:openapi           # build:openapi, then Spectral against openapi/.spectral.yaml (fails on error)
npm run test:openapi-coverage  # Jest over src/openapi — the coverage gate, without coverage reporting
npm run test:contract          # Jest over src/openapi and src/routes, without coverage reporting
```

Run these in `packages/backend`, or from the root with `--workspace=@ronl/backend`. `scripts/jest-global-setup.cjs` also builds `openapi.json` before every Jest run, because both backend workflows run the tests before they build.

---

## Shared types

Types shared between backend and frontend are in `packages/shared/src/`. Import them as `@ronl/shared`:

```typescript
import { ApiResponse, TenantConfig } from '@ronl/shared';
```

After modifying shared types, rebuild the package before the backend picks up the changes:

```bash
npm run build --workspace=@ronl/shared
```

---

## Security implementation

The following code patterns are used across the middleware stack. These are the actual implementations — not configuration values — for reference when modifying security behaviour.

### JWT validation

`auth/jwt.middleware.ts` validates every protected request:

```typescript
const authHeader = req.headers.authorization;
const token = authHeader?.split(' ')[1];

// Fetch JWKS from Keycloak (cached in Redis, TTL 300s)
const jwks = await fetchJWKS(config.keycloakUrl, config.keycloakRealm);
const decoded = jwt.verify(token, jwks);

// Validate standard claims
if (decoded.exp < Date.now() / 1000) {
  throw new Error('Token expired');
}
if (decoded.aud !== config.jwtAudience) {
  throw new Error('Invalid audience');
}
if (!decoded.iss.startsWith(config.keycloakUrl)) {
  throw new Error('Invalid issuer');
}

// Attach to request for downstream handlers
req.user = decoded;
```

### Rate limiting

`src/index.ts` applies one global limiter to every request:

```typescript
const limiter = rateLimit({
  windowMs: config.rateLimit.windowMs,        // RATE_LIMIT_WINDOW_MS, default 60000
  max: config.rateLimit.maxRequests,          // RATE_LIMIT_MAX_REQUESTS, default 1000
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req) =>
    rateLimitKey(req.ip, config.rateLimit.perTenant ? req.user?.tenantId : undefined),
  skip: (req) => isCallbackPath(req.path),
});
app.use(limiter);
```

`rateLimitKey()` in `utils/client-ip.ts` strips the port Azure writes into `X-Forwarded-For`, so each new connection does not get a fresh budget. A refusal answers `429 RATE_LIMIT_EXCEEDED`. The ValidSign callback is skipped here and has its own limiter in `validsign.routes.ts` (60 per minute), so a busy board cannot exhaust the budget a signature callback needs.

### Public write-endpoint hardening

`POST /v1/public/use-case`, `POST /v1/public/upload-file`, and `POST /v1/public/feedback` accept unauthenticated citizen submissions, so they carry extra hardening beyond the global rate limiter above:

- **ALTCHA proof-of-work** — `use-case` and `feedback` require a solved PoW challenge before a GitLab work item is created. `GET /v1/public/altcha/challenge` issues a signed challenge (max 50,000 iterations, 10-minute expiry) via `altcha-lib`; `verifySolution()` checks it on submit. `ALTCHA_HMAC_KEY` configures the HMAC secret — when unset, the check bypasses gracefully so local dev isn't blocked. `upload-file` is intentionally excluded, since it's a pre-upload step rather than the final submission gate.
- **Upload type whitelist** — `upload-file` checks both MIME type and file extension independently against `ALLOWED_UPLOAD_MIMETYPES`, blocking extension spoofing (a file claiming an allowed MIME type with a disallowed extension, or vice versa).
- **Dedicated rate limit** — `publicWriteLimiter` caps these three routes at 10 requests per 15 minutes per IP, on top of the global limiter, with standardised `RateLimit-*` response headers.

### CORS

`src/index.ts` passes `cors` a function rather than an array:

```typescript
const isProductionTier = config.deploymentEnv === 'production';

app.use(
  cors({
    origin: corsOriginCallback(config.corsOrigin, config.corsPreviewSlugs, isProductionTier),
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization', 'X-Request-ID'],
  })
);
```

`corsOriginCallback()` in `utils/cors-origin.ts` decides per request:

- **No `Origin` header** — allowed. Server-to-server calls, curl and health probes are not browsers, and CORS is not an authentication boundary.
- **Configured origins** — `CORS_ORIGIN`, a comma-separated list, matched by exact string equality. In production it is `https://mijn.open-regels.nl`, in ACC `https://acc.mijn.open-regels.nl`; unset, it defaults to the local dev servers on ports 3000, 5173, 5175 and 3002.
- **Pull-request previews** — `CORS_PREVIEW_SLUGS`, a comma-separated list of Static Web Apps slugs, not hostnames. An origin matches when it is `https://<slug>-<number>.<region>.<n>.azurestaticapps.net`, the hostname Azure gives a numbered preview of that app. The slug is regex-escaped, and nothing broader than the slug matches — a `*.azurestaticapps.net` pattern would admit any Static Web App in the world to credentialed requests. Set on the ACC App Service only.
- **Production refuses previews** in code, whatever `CORS_PREVIEW_SLUGS` holds: the guard reads `DEPLOYMENT_ENV`, not `NODE_ENV`, because acceptance runs `NODE_ENV=production`. A production tier with the setting present logs a warning at startup and ignores it.

A disallowed origin gets no CORS headers rather than an error. See [Pull-request previews](cicd.md#pull-request-previews) for why the preview allowance exists.

`GET /v1/openapi.json` is the exception: `openapi.routes.ts` mounts its own `cors({ origin: '*', methods: ['GET', 'OPTIONS'] })`, because `/core/publish-openapi` requires any origin to be able to fetch the document. It is public, read-only and carries no credentials.

### Secrets in production (Azure Key Vault)

Azure App Settings are the standard secrets store (injected as environment variables). For an additional layer, the Key Vault SDK can be used:

```typescript
import { SecretClient } from '@azure/keyvault-secrets';
import { DefaultAzureCredential } from '@azure/identity';

const credential = new DefaultAzureCredential();
const client = new SecretClient(process.env.KEY_VAULT_URL!, credential);

const dbPassword = await client.getSecret('db-password');
```

The App Service managed identity must be granted `Key Vault Secrets User` on the vault.

---

## Audit logging

### Architecture

Audit logging spans two files:

- `src/types/audit.types.ts` — `AuditLogEntry` interface, the single source of truth for the shape of an audit record
- `src/middleware/audit.middleware.ts` — `auditMiddleware` (automatic per-request logging) and `auditLog()` (explicit action logging from route handlers); re-exports `AuditLogEntry` for backward compatibility
- `src/services/audit.service.ts` — pg-promise connection pool and `persistAuditLog()`

### Automatic vs. explicit logging

Every authenticated request is logged automatically by `auditMiddleware`, which wraps `res.end` and calls `createAuditLog()` after the response is sent. The action is `${req.method} ${req.path}` and the result is derived from the HTTP status code:

| Status range | Result |
|---|---|
| 200–399 | `success` |
| 400–499 | `failure` |
| 500+ | `error` |

Route handlers can additionally call `auditLog()` directly to record domain-level actions with richer detail:
```typescript
auditLog(req, 'process.start.zorgtoeslag', 'success', {
  processInstanceId: instance.id,
});
```

### Database persistence

`persistAuditLog()` in `audit.service.ts` writes each entry to the `audit_logs` table on Azure PostgreSQL Flexible Server using a pg-promise named-parameter `INSERT`. It is called fire-and-forget from `createAuditLog()` — errors are caught and logged but never propagated to the request cycle, so a database outage does not affect API availability.

`initDb()` is called at server startup to verify connectivity. If the database is unreachable at startup, the backend falls back to in-memory logging and logs a warning. In-memory entries are not persisted to the database later; they exist only for the lifetime of the process.

See [PostgreSQL Deployment](deployment/postgresql.md) for schema, firewall, and connection string setup.

### Skipping self-referential entries

`GET /audit` requests are excluded from the audit log to prevent the Audit Log viewer from recording its own page loads. The skip is applied inside `auditMiddleware` before `createAuditLog()` is called:
```typescript
if (req.path === '/audit') {
  return originalEnd.apply(this, args as any);
}
```

### Known issues fixed

**IP address format on Azure App Service**

`req.ip` on Azure App Service includes the port (`77.161.155.118:40796`). PostgreSQL's `inet` type does not accept a port suffix, causing every `INSERT` to fail silently. Fixed in `audit.service.ts` by stripping the port before the insert:
```typescript
ipAddress: entry.ipAddress ? entry.ipAddress.replace(/:\d+$/, '') : null,
```

This only affects Azure — local Express sets `req.ip` without a port.

**Audit log viewer pagination reset**

The `useEffect` that triggers `loadAuditLogs(0)` on section entry incorrectly included `auditLogs.length` in its dependency array. When "Meer laden" appended records, the length change re-fired the effect and reset pagination to offset 0. Fixed by removing `auditLogs.length` from the dependency array — `activeSection` changing to `audit-overzicht` or `audit-details` is sufficient to trigger the initial load.