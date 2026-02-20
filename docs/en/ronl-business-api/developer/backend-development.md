# Backend Development

The backend is `packages/backend` (`@ronl/backend`) — a Node.js 20 Express application written in TypeScript.

## Project structure

```
packages/backend/src/
├── index.ts                    # Express app bootstrap, middleware registration
├── routes/
│   ├── index.ts                # Route registration (v1/* and legacy api/*)
│   ├── health.routes.ts        # GET /v1/health
│   ├── decision.routes.ts      # POST /v1/decision/:key/evaluate
│   ├── process.routes.ts       # POST /v1/process/:key/start, GET/DELETE
│   ├── template.routes.ts      # GET /v1/chains/templates
│   ├── triplydb.routes.ts      # GET /v1/triplydb (TriplyDB proxy)
│   ├── vendor.routes.ts        # GET /v1/vendors
│   └── cache.routes.ts         # GET/DELETE /v1/cache
├── middleware/
│   ├── error.middleware.ts     # Global error handler, 404 handler
│   ├── version.middleware.ts   # Adds API-Version header to all responses
│   ├── audit.middleware.ts     # Writes audit log entry for every request
│   └── tenant.middleware.ts    # Extracts and validates municipality claim
├── auth/
│   └── jwt.middleware.ts       # JWT signature validation, JWKS caching
├── services/
│   ├── operaton.service.ts     # Operaton REST API client
│   └── audit.service.ts        # Audit log database writes
└── utils/
    ├── config.ts               # Typed configuration from environment variables
    └── logger.ts               # Winston logger (JSON format in prod)
```

## Middleware stack

Middleware is registered in this order in `src/index.ts`:

1. `helmet()` — security headers (CSP, HSTS, etc.)
2. `cors()` — CORS policy from `CORS_ORIGIN` env var
3. `rateLimit()` — request rate limiting
4. `express.json()` — body parsing, limit 1 MB
5. Request logging — logs method, path, IP
6. `versionMiddleware` — adds `API-Version` response header
7. `auditMiddleware` — writes audit entry post-response
8. Route handlers (`routes/index.ts`)
9. `notFoundHandler` — 404 for unmatched paths
10. `errorHandler` — catches and formats all thrown errors

JWT validation (`jwt.middleware.ts`) is applied per-route on protected endpoints, not globally. Public endpoints (e.g. `GET /v1/health`) do not require authentication.

## Adding a new route

1. Create `src/routes/myfeature.routes.ts` following the existing pattern:

```typescript
import { Router, Request, Response } from 'express';
import { ApiResponse } from '@ronl/shared';
import logger from '@utils/logger';

const router = Router();

router.get('/', async (req: Request, res: Response) => {
  try {
    res.json({
      success: true,
      data: { ... },
      timestamp: new Date().toISOString(),
    } as ApiResponse);
  } catch (error) {
    logger.error('myfeature error', error);
    res.status(500).json({ success: false, error: { code: 'ERROR', message: String(error) } });
  }
});

export default router;
```

2. Register it in `src/routes/index.ts`:

```typescript
import myfeatureRoutes from './myfeature.routes';

router.use('/v1/myfeature', myfeatureRoutes);
router.use('/api/myfeature', deprecationMiddleware('/v1/myfeature'), myfeatureRoutes);
```

## Authentication on protected routes

Apply the JWT middleware to any route that requires a logged-in user:

```typescript
import { authenticateJWT } from '@auth/jwt.middleware';

router.post('/sensitive', authenticateJWT, async (req, res) => {
  const { sub, municipality, roles } = req.user!;
  // ...
});
```

After `authenticateJWT`, `req.user` is populated with the decoded JWT claims.

## TypeScript path aliases

The `tsconfig.json` configures path aliases for clean imports:

```
@routes/*    → src/routes/*
@services/*  → src/services/*
@middleware/* → src/middleware/*
@auth/*      → src/auth/*
@utils/*     → src/utils/*
```

`tsc-alias` resolves these aliases during the build step (`npm run build`).

## Development commands

```bash
npm run dev           # Start with tsx watch (hot-reload)
npm run build         # Compile TypeScript → dist/
npm run start         # Run compiled dist/index.js
npm run lint          # ESLint 9 flat config
npm run lint:fix      # ESLint with auto-fix
npm run type-check    # tsc --noEmit (no output, type check only)
npm test              # Jest with coverage
npm run test:unit     # Unit tests only
npm run test:integration  # Integration tests only
```

## Shared types

Types shared between backend and frontend are in `packages/shared/src/`. Import them as `@ronl/shared`:

```typescript
import { ApiResponse, TenantConfig } from '@ronl/shared';
```

After modifying shared types, rebuild the package before the backend picks up the changes:

```bash
npm run build --workspace=@ronl/shared
```
