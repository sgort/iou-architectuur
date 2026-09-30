---
component: RONL Business API
---

# Backend suite

`packages/backend`, Jest with the `ts-jest` preset. **97 files · 2370 tests ·
all passing · nothing skipped · `Time: 54.672 s`**, followed by
*"✓ all 133 documented operations were checked against a real response"*.
Coverage is on by default; see [Coverage](coverage.md#backend-by-area) for the
per-area figures.

Measured on **30 September 2026** for v2026.09.15 — the release in production,
`main` at `ae06c9e` — with `npm test --workspace=@ronl/backend`, in the working
checkout on `acc` at `142d909` (a tree identical to `ae06c9e`) after
`npm run deps:check` reported the install in sync with the lockfile, on
Node 24.14.1 / npm 11.11.0 (`.nvmrc` names 22.23.2). Counts come from the
runner's own JSON output, not from grepping for `it(`, which miscounts
parameterised and multi-line cases.

!!! success "`npm test` is now two steps: Jest, then the conformance-coverage check"
    Since v2026.09.14 the backend's `test` and `test:serial` scripts end with
    `&& node scripts/check-conformance-coverage.cjs`. Jest runs the suite as
    before; the script then fails the run unless **every operation in the
    OpenAPI document was compared against a real response** at least once. On
    30 September it printed *"✓ all 133 documented operations were checked
    against a real response"*.

    **That figure, and 2370 / 97, are this package's alone.** The repository
    runs **312 test files and 4574 tests** across five workspaces — see
    [Overview](overview.md). Quoting the backend's count as a repository total
    understates the suite by over two thousand tests.

!!! note "2011 → 2008 → 2028 → 2072 → 2198 → 2202 → 2370, and nothing was lost on the way"
    The suite reported **2011** for several releases, of which 2008 ran and
    **three were permanently skipped**. Those three guarded the
    `PHASE_NOT_MODELLED` branch of the RIP phase model. v2026.09.7 made an
    unmodelled phase unrepresentable (issue #85), the branch went, and the
    three skipped cases went with it — a deletion of dead tests rather than a
    regression. The **2370** measured here is growth on that 2008 base. No
    workspace in this repository skips anything.

    **v2026.09.14 and v2026.09.15 together added +168 tests and one file**,
    against the 28 September measurement of v2026.09.13 (96 files, 2202). The
    one file is `openapi/testing/conformance.test.ts`, **20 tests**, for
    `expectToMatchOperation` — the helper that validates a real response
    against the documented schema (#269). One file shrank:
    `openapi/coverage.test.ts` went from **7 tests to 3** when #214 described
    the last undocumented operations and the pending list it policed was
    deleted — see the `src/openapi` row below. The rest is new cases in files
    that already existed: the swimlane parser learning any laned process and
    its Awb phases (`rip-swimlane` +56), the route suites asserting each
    documented response with `expectToMatchOperation` and covering the M2M
    allow-list (#237), the BRP logging fix (#241) and the new lineage and
    swimlane endpoints (`src/routes` +46), and `73a6764`'s branch-margin work
    across services, routes, `auth`, `mcp-servers` and `pa-monitoring`.

    For the record, v2026.09.13 was the smallest step: +4 and no new file, the
    Operaton definition-id caching fix and the swimlane's multiple-documents
    case. v2026.09.11 added three files; **v2026.09.12 added seven, and 73 of
    its +126 tests were in them**, as measured then:

    | New file in v2026.09.12 | Tests | What it covers |
    |---|---:|---|
    | `auth/tenant-access.test.ts` | 26 | The one module that decides tenant questions for process and task access (#218, #219, #229) |
    | `routes/registry.test.ts` | 9 | The route registry — the single source of the `/v1` mounts |
    | `openapi/testing/routeOperations.test.ts` | 13 | The helpers that turn the registry and the document into comparable operation lists |
    | `openapi/coverage.test.ts` | 7, now 3 | The OpenAPI coverage gate (#200) |
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
needing a coverage job of its own — and so do the OpenAPI coverage gate, an
ordinary test file, and the conformance-coverage check that `npm test` runs
after Jest. Since v2026.09.7 `azure-backend-acc.yml` also
triggers on `pull_request`, so these 2370 tests run *before* a merge rather than
only after one — and since **19 September 2026 that run is a required check**,
so a red backend suite now blocks the merge to `acc` outright. See
[Overview → What actually gates a merge](overview.md#what-actually-gates-a-merge).

| Area | Files | Tests |
|---|---:|---:|
| `src/routes` | 19 | 625 |
| `src/pa-monitoring` | 16 | 583 |
| `src/services` | 27 | 566 |
| `src/rip-swimlane` | 2 | 176 |
| `src/utils` | 13 | 131 |
| `src/media-aggregator` | 8 | 112 |
| `src/mcp-servers` | 3 | 54 |
| `src/auth` | 2 | 50 |
| `src/openapi` | 4 | 43 |
| `src/middleware` | 3 | 30 |

!!! success "Both columns are current, and they sum"
    Re-derived on 30 September 2026 from the run's own JSON output: the Files
    column accounts for all **97** files and the Tests column sums to **2370**,
    the measured total. Earlier versions of this page carried a Files column
    from one date and a Tests column from another that fell 274 short, with a
    warning attached; that gap is closed and has stayed closed across five
    re-derivations.

    **Eight of the ten areas moved between v2026.09.13 and v2026.09.15, and one
    file was added**: `src/routes` 579 → **625**, `src/rip-swimlane`
    120 → **176**, `src/services` 537 → **566**, `src/openapi` 3 → **4** files
    and 27 → **43** tests, `src/auth` 44 → **50**, `src/mcp-servers`
    49 → **54**, `src/pa-monitoring` 578 → **583** and `src/media-aggregator`
    107 → **112**. `src/utils` and `src/middleware` are unchanged to the test.
    `src/rip-swimlane` has overtaken `src/utils`: at **176** it is now the
    fourth-largest area, on `bpmn-swimlane.test.ts` alone holding 171.

    Before that, v2026.09.13 moved two areas (`src/services` 534 → 537,
    `src/rip-swimlane` 119 → 120). The v2026.09.12 window moved five areas and
    added one:
    **`src/routes`** 17 → 19 files and 524 → 579 tests, taking it past
    `src/pa-monitoring` to the largest area in the package; **`src/auth`** 1 → 2
    and 18 → 44, more than doubling on `tenant-access`; **`src/middleware`**
    2 → 3 and 25 → 30; **`src/services`** 27 files still, 522 → 534;
    **`src/utils`** 13 files still, 130 → 131; and **`src/openapi`** new, at 3
    files and 27 tests, counting `src/openapi/testing/` with it.

    `src/rip-swimlane` is the area that used to read *not counted* —
    `bpmn-swimlane.test.ts` and `doc-label.test.ts`, covering the derivation of
    a phase swimlane from deployed BPMN. It held **119 tests** when first
    counted, which is most of why the old column fell short, and has grown by
    half since.

!!! info "ValidSign is 168 of those tests, across five files"
    The [signing feature](../validsign-signing.md) arrived in v2026.08.36 and
    was the whole of the backend's growth in file terms for several releases.
    All five counts are a repeat measurement on 30 September; the route file
    gained assertions (each documented response now checked against its
    schema) but no test:

    | File | Tests | File time, 28 Sep | File time, 30 Sep |
    |---|---:|---:|---:|
    | `routes/validsign.routes.test.ts` | 116 | 39.6s | 29.3s |
    | `services/validsign.service.test.ts` | 32 | 32.2s | under 5s |
    | `services/validsignCompletion.service.test.ts` | 9 | 2.4s | under 5s |
    | `services/validsignPoller.service.test.ts` | 7 | 1.5s | under 5s |
    | `utils/config.validsign.test.ts` | 4 | 1.7s | under 5s |

    The times are not a repeat: on 26 September none of these files ran long
    enough for Jest to print a time at all, on 28 September two of them took
    over half a minute, and on 30 September only the route file did — Jest
    prints a file's time only past its five-second slow-test threshold. Read the
    next warning before drawing anything from that.

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
    slowest single file in the backend suite*, at 38.5 seconds. The same file,
    across five passes: **38.5s**, then **81.7s** on 24 September (and only
    fifth), then too fast to print at all on 26 September, then **39.6s** on
    28 September and **29.3s** on 30 September. It gained eight tests in the
    middle of that and nothing since.

    The slowest files change with it. On 26 September they were
    `openapi/coverage.test.ts` (51.7s) and `routes/registry.test.ts` (51.6s);
    on 28 September the same two took 23.8s and 25.8s, and the top of the list
    was `pa-monitoring/pa.routes.test.ts` (71.5s) and
    `pa-monitoring/curation.service.test.ts` (69.4s). On 30 September it was
    `registry.test.ts` (42.8s) and `coverage.test.ts` (42.7s) again, with
    `pa.routes.test.ts` at 37.8s and `curation.service.test.ts` down to 15.7s.

    None of these figures is wrong and nothing regressed or improved. Jest
    reports each file's **elapsed** time while running several workers at once,
    so a file's number depends on what shared the machine with it — which is why
    the file times on this page sum to far more than the suite's own
    `Time: 54.672 s`. Compare per-file times within one run, never across two,
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
| `src/openapi` | New in v2026.09.12 (#200), and completed in v2026.09.14 (#214, #269). **`coverage`** is the contract gate, three rules: both sides actually loaded, since two empty lists agree perfectly; every served operation is documented in `openapi/openapi.yaml`; and every documented operation is still served. The pending list that used to sit beside it — `openapi/pending.json`, with a ceiling of 18 that could only move down — is **gone**: #214 described the last undocumented operations, the rules that read the list became trivially true, and they were deleted with the file, so a route added without a description now fails here rather than being let in with the number bumped. **`testing/conformance`** tests `expectToMatchOperation`, which the route suites call on real supertest responses: the operation is documented, the status is documented for it (falling back to `default`), a 2xx carries `API-Version` (ADR API-57), and the content type is documented and the body validates against its schema with Ajv's JSON Schema 2020-12 validator, formats included and strict schema checking on. It also records every operation it is asked about, even one whose check then fails, so that `scripts/check-conformance-coverage.cjs` can fail `npm test` if any documented operation was never checked. **`document`** reads the real built `openapi.json` and rejects anything that is not an OpenAPI document with paths, without masking a missing file. **`testing/routeOperations`** turns the registry and the document into comparable operation lists, and throws rather than skips on a nested router, a non-string path or an unsupported method, since skipping would hide an operation from the gate |
| `src/media-aggregator` | `net-guard` (the SSRF guard: IPv4/IPv6 rules, every DNS path), `ingest`, `search`, `store`, `sanitize`, `stable-id`, plus the aggregator's own route module |
| `src/utils` | `config` and its ValidSign counterpart, `env`, `logger`, `operaton-variables`, `slug`, `tls-bootstrap`, `altcha`, `errors`, `client-ip`, `dutch-datetime`, and — new in v2026.09.11 — `build-info` and `cors-origin` |
| `src/mcp-servers` | The standalone stdio MCP servers (`lde`, `triplydb`, `edocs`) — each mocks the MCP SDK to capture and drive its `ListTools`/`CallTool` handlers directly |
| `src/middleware` | `tenant.middleware` and `audit.middleware`, and — new in v2026.09.12 — `version.middleware`: every response carries an `API-Version` header with the CalVer release string, error responses and unrouted 404s included |
| `src/auth` | `jwt.middleware` — token validation, role and assurance gates — and, new in v2026.09.12, **`tenant-access`**, the one module that decides tenant questions for process and task access (#218, #219, #229): an exact, case-sensitive tenant match with no match for a missing label; a staff start across tenants refused while a citizen's case is stamped with the deployed tenant and its origin recorded; a token without a roles claim treated as staff; case reads admitted to the owning tenant or the applicant only; and the single `403 TENANT_MISMATCH` answer |
| `src/rip-swimlane` | `bpmn-swimlane` and `doc-label` — parsing lanes, nodes and rework loops out of deployed BPMN into a swimlane model, against twelve real RIP phase fixtures and, since v2026.09.14, seven Awb process fixtures under `__fixtures__/awb/`. The parser now serves any laned process, not only RIP: script, business-rule and call-activity nodes as their own kinds, lane groups, and the `ronl:awbPhase` markers the caseworker's phase stepper reads |

`src/utils` was rebuilt over the v2026.08.21 window, going from 5 files and 21
tests to 8 and 73 — `config.test.ts` the largest single addition, with
`tls-bootstrap` and `operaton-variables` newly covered. That is what took the
area from 43.47% statements to 100%. It has kept growing since: 11 files when
ValidSign added its own config coverage, and **13 files and 130 tests** at
v2026.09.11, which added `build-info.test.ts` and `cors-origin.test.ts` and
another 25 cases to `config.test.ts`, and 131 at v2026.09.12, one more case in
`errors.test.ts`, where it still stands at v2026.09.15. Of the twelve source
files the area reports on 30 September,
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
  otherwise only build after the tests — and, since v2026.09.14, sets
  `CONFORMANCE_LOG` and truncates that file, so a previous run cannot make
  this one look complete; and `scripts/jest-setup-env.cjs` sets the one
  variable `validateConfig()` demands, so a test that imports the whole
  registry can load the real `@utils/config` instead of a stub that would have
  to satisfy every field nineteen route modules read.
- **The conformance check runs after Jest, as its own process.** `npm test` and
  `npm run test:serial` are `jest --coverage … && node
  scripts/check-conformance-coverage.cjs`. It was first written as a Jest
  `globalTeardown`, and that version was useless: Jest prints an error thrown
  there but still exits 0. A filtered run — `npx jest -t …`, a single file,
  `test:contract`, `test:openapi-coverage` — does not go through `npm test`
  and so never reaches the check, which also skips with a note when there is
  no log at all. **Only the full `npm test` proves every documented operation
  was checked.**
- **Adding a route is a registry entry, an OpenAPI description and a
  conformance assertion.** See [Writing tests](writing-tests.md#conventions)
  for what the two gates expect.
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
