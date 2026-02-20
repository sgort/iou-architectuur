# Testing

## Backend tests

The backend uses **Jest** with **ts-jest** for TypeScript support and **Supertest** for HTTP integration tests.

```bash
npm test                      # All tests with coverage report
npm run test:unit             # Unit tests only (tests/unit/)
npm run test:integration      # Integration tests only (tests/integration/)
npm run test:watch            # Watch mode — re-runs on file change
```

### Unit tests

Unit tests cover individual services and middleware in isolation, using Jest mocks for external dependencies (Keycloak JWKS, Operaton API, PostgreSQL).

Location: `packages/backend/tests/unit/`

### Integration tests

Integration tests send real HTTP requests to a running Express instance (not a deployed server) and verify the full middleware chain including JWT validation. The test setup uses an in-memory Keycloak mock that issues valid test JWTs.

Location: `packages/backend/tests/integration/`

### What to test

When adding a new route or service:
- Unit test: the service function in isolation (mock all external calls)
- Integration test: the route with a valid JWT → expected response, and with no/invalid JWT → HTTP 401

## Health check verification

The health endpoint is the fastest way to verify a running instance:

```bash
# Local
curl http://localhost:3002/v1/health | jq .

# ACC
curl https://acc.api.open-regels.nl/v1/health | jq .
```

Expected healthy response:
```json
{
  "name": "RONL Business API",
  "version": "1.0.0",
  "environment": "development",
  "status": "healthy",
  "uptime": 42.1,
  "timestamp": "2026-02-20T10:00:00.000Z",
  "services": {
    "keycloak": { "status": "up", "latency": 45 },
    "operaton": { "status": "up", "latency": 112 }
  }
}
```

Status values: `healthy` (HTTP 200), `degraded` (HTTP 503 — one or more services down), `unhealthy` (HTTP 503 — health check itself failed).

## Pre-commit and pre-push hooks

Husky hooks run automatically:

**Pre-commit** (via lint-staged):
- ESLint + Prettier on changed `packages/backend/**/*.ts` files
- ESLint + Prettier on changed `packages/frontend/**/*.{ts,tsx}` files

**Pre-push**:
- `npm run type-check` across all workspaces

These hooks run before any push reaches CI and catch common issues early.

## CI test run

GitHub Actions runs the test suite on every push to `acc` and `main`:

```yaml
- name: Run linter
  working-directory: packages/backend
  run: npm run lint

- name: Build TypeScript
  working-directory: packages/backend
  run: npm run build
```

A post-deployment health check with 5 retries (10-second intervals) verifies that the deployed instance is responding correctly before the workflow marks the deployment as successful.
