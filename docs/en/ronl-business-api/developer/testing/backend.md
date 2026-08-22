---
component: RONL Business API
---

# Backend suite

`packages/backend`, Jest with the `ts-jest` preset. **74 files · 1576 tests ·
all passing · ~23s.** Coverage is on by default; see
[Coverage](coverage.md#backend-by-area) for the per-area figures.

Test files are colocated with the source they cover (`foo.ts` →
`foo.test.ts`) and picked up automatically — there is no separate `tests/`
directory.

| Area | Files | Tests | Covers |
|---|---:|---:|---|
| `src/pa-monitoring` | 16 | 533 | Public Affairs monitoring — the largest area in the repository. `pa.routes` (131), `pa-dossiers.routes` (96) and `pa-dossiers.db` (30) for dossier authoring, `curation.service` (61), `rules` (38, pure scoring), the TK/OB/EU/agenda/media source clients, `pa-cache`, `query-match`, `rss`, `notifications.service` |
| `src/services` | 21 | 389 | Every service — `operaton`, `edocs`, `doccle`, `audit`, `berichten`, `nieuws`, `search`, `regelcatalogus`, `productenDiensten`, `mcpChat`, `externalTaskWorker`, `lde`, the `llm/` providers (Anthropic, OpenAI) and the `mcp/` provider wrappers (Cprmv, Lde, Operaton, TriplyDb) |
| `src/routes` | 15 | 388 | Every route module, mounted with the service layer and auth mocked and supertest driving requests — `m2m` (76), `process` (64), `public.routes` + `public.routes.security` (64 combined), `edocs` (36), `task` (39), `rip` (25), plus `doccle`, `mcp`, `health`, `hr`, `capacity`, `decision`, `brp`, `admin` |
| `src/media-aggregator` | 8 | 107 | `net-guard` (the SSRF guard: IPv4/IPv6 rules, every DNS path), `ingest`, `search`, `store`, `sanitize`, `stable-id`, plus the aggregator's own route module |
| `src/utils` | 8 | 73 | `config` (34), `env` (10), `logger` (8), `operaton-variables` (7), `slug` (5), `tls-bootstrap` (5), `altcha` (2), `errors` (2) |
| `src/mcp-servers` | 3 | 49 | The standalone stdio MCP servers (`lde`, `triplydb`, `edocs`) — each mocks the MCP SDK to capture and drive its `ListTools`/`CallTool` handlers directly |
| `src/middleware` | 2 | 24 | `tenant.middleware` and `audit.middleware` |
| `src/auth` | 1 | 13 | `jwt.middleware` — token validation, role and assurance gates |

The `src/utils` area is the one that changed shape most in this window, going
from 5 files and 21 tests to 8 and 73. `config.test.ts` is new and is the
largest single addition, covering the config surface including the rate-limit
defaults; `tls-bootstrap` and `operaton-variables` are also newly covered. That
is what took the area from 43.47% statements to 100% — see
[Coverage](coverage.md#backend-by-area).

## Techniques worth knowing before adding tests here

- **Mock at the service boundary** (axios, pg-promise, the MCP SDK) and drive
  routes with supertest through a real `jwtMiddleware` test stub reading an
  `x-test-roles` header.
- **Path aliases** (`@utils/`, `@services/`, `@auth/`, `@middleware/`,
  `@routes/`, `@models/`, `@ronl/shared`) are mapped in
  `packages/backend/jest.config.js` and work inside test files.
- **Module-level singletons** are re-imported per test case via
  `jest.isolateModules` with a patched environment, since their behaviour is
  fixed at import time.
- **Every test file must be a module.** A file with no top-level `import` or
  `export` is a global script to TypeScript, and its top-level declarations
  collide with identically-named ones in sibling files. This has already broken
  the build — see
  [Writing tests](writing-tests.md#make-every-test-file-a-module).

!!! warning "Clear the cache before trusting a green run"
    ts-jest caches type diagnostics per file. A warm cache will happily report
    a suite green when files in it no longer compile:

    ```bash
    npx jest --config packages/backend/jest.config.js --clearCache
    ```
