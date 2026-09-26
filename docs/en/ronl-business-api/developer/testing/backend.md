---
component: RONL Business API
---

# Backend suite

`packages/backend`, Jest with the `ts-jest` preset. **96 files · 2198 tests ·
all passing · nothing skipped · `Time: 59.864 s`.** Coverage is on by default;
see [Coverage](coverage.md#backend-by-area) for the per-area figures.

Measured on **26 September 2026** for v2026.09.12 (`main` at `2443adc`) with
`npm test --workspace=@ronl/backend`, in the working checkout on `acc` at
`3c44b9e` — which differs from `main` only in `scripts/check-previews.sh` —
after `npm run deps:check` reported the install in step with the lockfile, on
Node 24.14.1 / npm 11.11.0 (`.nvmrc` names 22.23.2). Counts come from the
runner's own JSON output, not from grepping for `it(`, which miscounts
parameterised and multi-line cases.

!!! note "2011 → 2008 → 2028 → 2072 → 2198, and nothing was lost on the way"
    The suite reported **2011** for several releases, of which 2008 ran and
    **three were permanently skipped**. Those three guarded the
    `PHASE_NOT_MODELLED` branch of the RIP phase model. v2026.09.7 made an
    unmodelled phase unrepresentable (issue #85), the branch went, and the
    three skipped cases went with it — a deletion of dead tests rather than a
    regression. The **2198** measured here is growth on that 2008 base. No
    workspace in this repository skips anything.

    v2026.09.11 added three files; **v2026.09.12 added seven, and 73 of its
    +126 tests are in them**:

    | New file | Tests | What it covers |
    |---|---:|---|
    | `auth/tenant-access.test.ts` | 26 | The one module that decides tenant questions for process and task access (#218, #219, #229) |
    | `routes/registry.test.ts` | 9 | The route registry — the single source of the `/v1` mounts |
    | `openapi/testing/routeOperations.test.ts` | 13 | The helpers that turn the registry and the document into comparable operation lists |
    | `openapi/coverage.test.ts` | 7 | The OpenAPI coverage gate (#200) |
    | `openapi/document.test.ts` | 7 | Reading the built OpenAPI document |
    | `routes/openapi.routes.test.ts` | 6 | `GET /v1/openapi.json` |
    | `middleware/version.middleware.test.ts` | 5 | The `API-Version` response header |

    Each source file they cover — `tenant-access.ts`, `registry.ts`,
    `routeOperations.ts`, `document.ts`, `openapi.routes.ts`,
    `version.middleware.ts` — is at **100% statements, branches, functions and
    lines**. The other 53 are new cases in existing files — 40 across the
    route suites, `routes/validsign.routes.test.ts` among them at 108 → 116, 12
    in `services/operaton.service.test.ts`, one in `utils/errors.test.ts`. Most
    of the route cases are the same tenant rules seen from the outside:
    `process.routes` now asserts that staff are refused across tenants while a
    citizen's case is stamped with the deployed tenant, `task.routes` answers
    `403 TENANT_MISMATCH` when an instance names another tenant or none, and
    `validsign.routes` gained a *tenant isolation on the task endpoints* block
    (#227). `capacity.routes` and `rip.routes` each had one case **inverted**:
    an instance with no tenant label used to be served, *"since there is nothing
    to mismatch"*, and is now refused, because *"an unlabelled instance belongs
    to no tenant"*. `routes/root.routes.test.ts` was rewritten too — it now
    asserts that the banner advertises `/v1/openapi.json`, where it used to
    assert that no documentation endpoint was advertised — and still holds four
    tests.

Both backend workflows run this suite as `npm test`, coverage included, so the
per-file 80% branch floor in `jest.config.js` rides along with it rather than
needing a coverage job of its own — and so does the OpenAPI coverage gate
below, since it is an ordinary test file. Since v2026.09.7 `azure-backend-acc.yml` also
triggers on `pull_request`, so these 2198 tests run *before* a merge rather than
only after one — and since **19 September 2026 that run is a required check**,
so a red backend suite now blocks the merge to `acc` outright. See
[Overview → What actually gates a merge](overview.md#what-actually-gates-a-merge).

| Area | Files | Tests |
|---|---:|---:|
| `src/routes` | 19 | 579 |
| `src/pa-monitoring` | 16 | 578 |
| `src/services` | 27 | 534 |
| `src/utils` | 13 | 131 |
| `src/rip-swimlane` | 2 | 119 |
| `src/media-aggregator` | 8 | 107 |
| `src/mcp-servers` | 3 | 49 |
| `src/auth` | 2 | 44 |
| `src/middleware` | 3 | 30 |
| `src/openapi` | 3 | 27 |

!!! success "Both columns are current, and they sum"
    Re-derived on 26 September 2026 from the run's own JSON output: the Files
    column accounts for all **96** files and the Tests column sums to **2198**,
    the measured total. Earlier versions of this page carried a Files column
    from one date and a Tests column from another that fell 274 short, with a
    warning attached; that gap is closed and has stayed closed across three
    re-derivations.

    Five areas moved in this window, one is new, and the other four are
    unchanged to the test. **`src/routes`** 17 → 19 files and 524 → 579 tests,
    taking it past `src/pa-monitoring` to the largest area in the package;
    **`src/auth`** 1 → 2 and 18 → 44, more than doubling on `tenant-access`;
    **`src/middleware`** 2 → 3 and 25 → 30; **`src/services`** 27 files still,
    522 → 534; **`src/utils`** 13 files still, 130 → 131. **`src/openapi`** is
    new, at 3 files and 27 tests, counting `src/openapi/testing/` with it.

    `src/rip-swimlane` is the area that used to read *not counted* —
    `bpmn-swimlane.test.ts` and `doc-label.test.ts`, covering the derivation of
    an Infra-board phase swimlane from deployed BPMN against twelve real process
    fixtures. It holds **119 tests**, which is most of why the old column fell
    short. `src/routes` has also overtaken `src/services`.

!!! info "ValidSign is 168 of those tests, across five files"
    The [signing feature](../validsign-signing.md) arrived in v2026.08.36 and
    was the whole of the backend's growth in file terms for several releases.
    In this one only the route file grew; the other four counts are a repeat
    measurement:

    | File | Tests | File time, 26 Sep |
    |---|---:|---:|
    | `routes/validsign.routes.test.ts` | 116 | under 5s |
    | `services/validsign.service.test.ts` | 32 | under 5s |
    | `services/validsignCompletion.service.test.ts` | 9 | under 5s |
    | `services/validsignPoller.service.test.ts` | 7 | under 5s |
    | `utils/config.validsign.test.ts` | 4 | under 5s |

    *Under 5s* is all the console says: Jest prints a file's time only when it
    exceeds its five-second slow-test threshold, and none of these five did.

    The route file carries the most because the two unauthenticated routes are
    where the security properties live — capability URLs, the shared-secret
    check, and a rate limiter keyed on client IP rather than on an
    attacker-controlled header. It grew from 66 tests to 108 in v2026.09.9 and
    to **116** in v2026.09.12, the eight new cases asserting that the signing
    endpoints refuse a task belonging to another tenant, or to none (#227).

    The route module reports **97.21% statements · 98.29% branches · 100%
    functions · 96.99% lines**, each a little up on v2026.09.11;
    `validsign.service.ts` and `validsignPoller.service.ts` are at 100 on all
    four, and `validsignCompletion.service.ts` at 93.47 / 91.3 / 100 / 95.34,
    unchanged.

!!! warning "A per-file time is not a ranking, and this page used to publish it as one"
    Through v2026.09.9 the note above called `validsign.routes.test.ts` *the
    slowest single file in the backend suite*, at 38.5 seconds. Measured on
    24 September the same unchanged file took **81.7 seconds** and was
    **fifth**. On 26 September, with eight more tests in it, it did not take
    long enough for Jest to print a time at all. The slowest files in that run
    were two of the new ones — `openapi/coverage.test.ts` (51.7s) and
    `routes/registry.test.ts` (51.6s), each of which imports every route module
    through the registry — ahead of `pa-monitoring/pa.routes.test.ts` (42.7s)
    and `pa-monitoring/curation.service.test.ts` (41.8s).

    None of these figures is wrong and nothing regressed or improved. Jest
    reports each file's **elapsed** time while running several workers at once,
    so a file's number depends on what shared the machine with it — which is why
    the file times on this page sum to far more than the suite's own
    `Time: 59.864 s`. Compare per-file times within one run, never across two,
    and do not build a superlative out of them.

Test files are colocated with the source they cover (`foo.ts` →
`foo.test.ts`) and picked up automatically — there is no separate `tests/`
directory.

!!! note "Counts live in one table only"
    The area table above carries every file and test count on this page. This
    second table describes *what each area covers* and deliberately repeats no
    figures — two tables of the same numbers is a contradiction waiting for the
    next release, and this page has already had one.

| Area | Covers |
|---|---|
| `src/pa-monitoring` | Public Affairs monitoring — the largest area in the repository. `pa.routes` and `pa-dossiers.routes` for dossier authoring, `curation.service`, `rules` (pure scoring), the TK/OB/EU/agenda/media source clients, `pa-cache`, `query-match`, `rss`, `notifications.service` |
| `src/services` | Every service — `operaton`, `edocs`, `doccle`, `audit`, `berichten`, `nieuws`, `search`, `regelcatalogus`, `productenDiensten`, `mcpChat`, `externalTaskWorker`, `lde`, the `llm/` providers (Anthropic, OpenAI), the `mcp/` provider wrappers (Cprmv, Lde, Operaton, TriplyDb), and the three [ValidSign](../validsign-signing.md) services |
| `src/routes` | Every route module, mounted with the service layer and auth mocked and supertest driving requests — `m2m`, `process`, `public.routes` and its security counterpart, `edocs`, `task`, `rip`, plus `doccle`, `mcp`, `health`, `hr`, `capacity`, `decision`, `brp`, `admin`, `validsign`, `root` (new in v2026.09.11, and now built from the registry's advertised endpoints). New in v2026.09.12: **`openapi.routes`** — `GET /v1/openapi.json` serves the document with any origin allowed, reads it once when the router is built rather than per request (so a zip deploy cannot serve a document from an artifact the process is not running), and answers 500 with the error envelope rather than crashing at load when the file is missing; and **`registry`** — every mount is under `/v1`, the ValidSign callback router precedes the authenticated one on the same mount, only `/v1/validsign` and `/v1/pa` carry two routers, and every path the root banner advertises is actually mounted, the drift that let it promise `/v1/docs` from the initial commit (#67) |
| `src/openapi` | New in v2026.09.12 (#200). **`coverage`** is the contract gate: every served operation is documented in `openapi/openapi.yaml` or listed in `openapi/pending.json`, nothing is both, every pending and every documented operation is still served, pending lists each operation once, and pending may only shrink — its ceiling is 18 — plus a first rule that both sides actually loaded, since two empty lists agree perfectly. **`document`** reads the real built `openapi.json` and rejects anything that is not an OpenAPI document with paths, without masking a missing file. **`testing/routeOperations`** turns the registry and the document into comparable operation lists, and throws rather than skips on a nested router, a non-string path or an unsupported method, since skipping would hide an operation from the gate |
| `src/media-aggregator` | `net-guard` (the SSRF guard: IPv4/IPv6 rules, every DNS path), `ingest`, `search`, `store`, `sanitize`, `stable-id`, plus the aggregator's own route module |
| `src/utils` | `config` and its ValidSign counterpart, `env`, `logger`, `operaton-variables`, `slug`, `tls-bootstrap`, `altcha`, `errors`, `client-ip`, `dutch-datetime`, and — new in v2026.09.11 — `build-info` and `cors-origin` |
| `src/mcp-servers` | The standalone stdio MCP servers (`lde`, `triplydb`, `edocs`) — each mocks the MCP SDK to capture and drive its `ListTools`/`CallTool` handlers directly |
| `src/middleware` | `tenant.middleware` and `audit.middleware`, and — new in v2026.09.12 — `version.middleware`: every response carries an `API-Version` header with the CalVer release string, error responses and unrouted 404s included |
| `src/auth` | `jwt.middleware` — token validation, role and assurance gates — and, new in v2026.09.12, **`tenant-access`**, the one module that decides tenant questions for process and task access (#218, #219, #229): an exact, case-sensitive tenant match with no match for a missing label; a staff start across tenants refused while a citizen's case is stamped with the deployed tenant and its origin recorded; a token without a roles claim treated as staff; case reads admitted to the owning tenant or the applicant only; and the single `403 TENANT_MISMATCH` answer |
| `src/rip-swimlane` | `bpmn-swimlane` and `doc-label` — parsing lanes, nodes and rework loops out of deployed BPMN so the Infra-board can draw a phase swimlane, against twelve real process fixtures |

`src/utils` was rebuilt over the v2026.08.21 window, going from 5 files and 21
tests to 8 and 73 — `config.test.ts` the largest single addition, with
`tls-bootstrap` and `operaton-variables` newly covered. That is what took the
area from 43.47% statements to 100%. It has kept growing since: 11 files when
ValidSign added its own config coverage, and **13 files and 130 tests** at
v2026.09.11, which added `build-info.test.ts` and `cors-origin.test.ts` and
another 25 cases to `config.test.ts`, and 131 at v2026.09.12, one more case in
`errors.test.ts`. Of the twelve source files the area reports on 26 September,
**eleven are at 100 on all four measures**; the twelfth is `config.ts`
at 95.12% statements and 98.31% branches — see
[Coverage](coverage.md#backend-by-area).

## Techniques worth knowing before adding tests here

- **Mock at the service boundary** (axios, pg-promise, the MCP SDK) and drive
  routes with supertest through a real `jwtMiddleware` test stub reading an
  `x-test-roles` header.
- **Path aliases** (`@utils/`, `@services/`, `@auth/`, `@middleware/`,
  `@routes/`, `@models/`, `@ronl/shared`) are mapped in
  `packages/backend/jest.config.js` and work inside test files.
- **Two setup scripts run before any test** since v2026.09.12, both wired in
  `jest.config.js`: `scripts/jest-global-setup.cjs` builds
  `openapi/openapi.json`, which the coverage gate reads and which CI would
  otherwise only build after the tests; and `scripts/jest-setup-env.cjs` sets
  the one variable `validateConfig()` demands, so a test that imports the whole
  registry can load the real `@utils/config` instead of a stub that would have
  to satisfy every field nineteen route modules read.
- **Adding a route is a registry entry and an OpenAPI description.** See
  [Writing tests](writing-tests.md#conventions) for what the coverage gate
  expects.
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
