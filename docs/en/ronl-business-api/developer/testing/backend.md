---
component: RONL Business API
---

# Backend suite

`packages/backend`, Jest with the `ts-jest` preset. **89 files · 2072 tests ·
all passing · nothing skipped · `Time: 118.063 s`.** Coverage is on by default;
see [Coverage](coverage.md#backend-by-area) for the per-area figures.

Measured on **24 September 2026** on `main` at `86af73e` (v2026.09.11) with
`npm test --workspace=@ronl/backend`, after a clean `npm ci` in a separate clone
on Node 24.14.1 / npm 11.11.0. Counts come from the runner's own JSON output,
not from grepping for `it(`, which miscounts parameterised and multi-line cases.

!!! note "2011 → 2008 → 2028 → 2072, and nothing was lost on the way"
    The suite reported **2011** for several releases, of which 2008 ran and
    **three were permanently skipped**. Those three guarded the
    `PHASE_NOT_MODELLED` branch of the RIP phase model. v2026.09.7 made an
    unmodelled phase unrepresentable (issue #85), the branch went, and the
    three skipped cases went with it — a deletion of dead tests rather than a
    regression. The **2072** measured here is growth on that 2008 base. No
    workspace in this repository skips anything.

    This is the release where the growth arrived as **new files** rather than as
    new cases in old ones — the first time in several windows. The three are
    `routes/root.routes.test.ts` (4 tests), `utils/build-info.test.ts` (6) and
    `utils/cors-origin.test.ts` (18), each covering a source file added
    alongside it, and each at **100% statements, branches, functions and
    lines**. The remaining 16 of the +44 are new cases in four existing files:
    `routes/health.routes.test.ts`, `services/regelcatalogus.service.test.ts`,
    `services/search.service.test.ts` and `utils/config.test.ts`.

Both backend workflows run this suite as `npm test`, coverage included, so the
per-file 80% branch floor in `jest.config.js` rides along with it rather than
needing a coverage job of its own. Since v2026.09.7 `azure-backend-acc.yml` also
triggers on `pull_request`, so these 2072 tests run *before* a merge rather than
only after one — and since **19 September 2026 that run is a required check**,
so a red backend suite now blocks the merge to `acc` outright. See
[Overview → What actually gates a merge](overview.md#what-actually-gates-a-merge).

| Area | Files | Tests |
|---|---:|---:|
| `src/pa-monitoring` | 16 | 578 |
| `src/routes` | 17 | 524 |
| `src/services` | 27 | 522 |
| `src/utils` | 13 | 130 |
| `src/rip-swimlane` | 2 | 119 |
| `src/media-aggregator` | 8 | 107 |
| `src/mcp-servers` | 3 | 49 |
| `src/middleware` | 2 | 25 |
| `src/auth` | 1 | 18 |

!!! success "Both columns are current, and they sum"
    Re-derived on 24 September 2026 from the run's own JSON output: the Files
    column accounts for all **89** files and the Tests column sums to **2072**,
    the measured total. Earlier versions of this page carried a Files column
    from one date and a Tests column from another that fell 274 short, with a
    warning attached; that gap is closed and has stayed closed across two
    re-derivations.

    Three areas moved in this window and the other six are unchanged to the
    test: **`src/utils`** 11 → 13 files and 100 → 130 tests, the largest
    proportional jump on the page, taking it past `src/media-aggregator`;
    **`src/routes`** 16 → 17 and 519 → 524; **`src/services`** 27 files still,
    513 → 522.

    `src/rip-swimlane` is the area that used to read *not counted* —
    `bpmn-swimlane.test.ts` and `doc-label.test.ts`, covering the derivation of
    an Infra-board phase swimlane from deployed BPMN against twelve real process
    fixtures. It holds **119 tests**, which is most of why the old column fell
    short. `src/routes` has also overtaken `src/services`.

!!! info "ValidSign is 160 of those tests, across five files"
    The [signing feature](../validsign-signing.md) arrived in v2026.08.36 and
    was the whole of the backend's growth in file terms for several releases.
    It did not grow at all in this one — all five counts below are a repeat
    measurement:

    | File | Tests | File time, 24 Sep |
    |---|---:|---:|
    | `routes/validsign.routes.test.ts` | 108 | 81.7s |
    | `services/validsign.service.test.ts` | 32 | 50.3s |
    | `services/validsignCompletion.service.test.ts` | 9 | 4.2s |
    | `services/validsignPoller.service.test.ts` | 7 | 1.5s |
    | `utils/config.validsign.test.ts` | 4 | 1.4s |

    The route file carries the most because the two unauthenticated routes are
    where the security properties live — capability URLs, the shared-secret
    check, and a rate limiter keyed on client IP rather than on an
    attacker-controlled header. It grew from 66 tests to 108 in v2026.09.9 and
    has not moved since.

    The route module reports **97.09% statements · 98.19% branches · 100%
    functions · 96.86% lines**; `validsign.service.ts` and
    `validsignPoller.service.ts` are at 100 on all four, and
    `validsignCompletion.service.ts` at 93.47 / 91.3 / 100 / 95.34 — every one
    of them unchanged from v2026.09.9.

!!! warning "A per-file time is not a ranking, and this page used to publish it as one"
    Through v2026.09.9 the note above called `validsign.routes.test.ts` *the
    slowest single file in the backend suite*, at 38.5 seconds. Measured again
    on 24 September the same unchanged file took **81.7 seconds** and was
    **fifth**, behind `pa-monitoring/pa.routes.test.ts` (102.2s),
    `pa-monitoring/curation.service.test.ts` (100.8s),
    `routes/process.routes.test.ts` (84.5s) and
    `services/operaton.service.test.ts` (82.0s).

    Neither figure is wrong and nothing regressed. Jest reports each file's
    **elapsed** time while running several workers at once, so a file's number
    depends on what shared the machine with it — which is why the nine file
    times on this page sum to far more than the suite's own
    `Time: 118.063 s`. Compare per-file times within one run, never across two,
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
| `src/routes` | Every route module, mounted with the service layer and auth mocked and supertest driving requests — `m2m`, `process`, `public.routes` and its security counterpart, `edocs`, `task`, `rip`, plus `doccle`, `mcp`, `health`, `hr`, `capacity`, `decision`, `brp`, `admin`, `validsign`, and — new in v2026.09.11 — `root` |
| `src/media-aggregator` | `net-guard` (the SSRF guard: IPv4/IPv6 rules, every DNS path), `ingest`, `search`, `store`, `sanitize`, `stable-id`, plus the aggregator's own route module |
| `src/utils` | `config` and its ValidSign counterpart, `env`, `logger`, `operaton-variables`, `slug`, `tls-bootstrap`, `altcha`, `errors`, `client-ip`, `dutch-datetime`, and — new in v2026.09.11 — `build-info` and `cors-origin` |
| `src/mcp-servers` | The standalone stdio MCP servers (`lde`, `triplydb`, `edocs`) — each mocks the MCP SDK to capture and drive its `ListTools`/`CallTool` handlers directly |
| `src/middleware` | `tenant.middleware` and `audit.middleware` |
| `src/auth` | `jwt.middleware` — token validation, role and assurance gates |
| `src/rip-swimlane` | `bpmn-swimlane` and `doc-label` — parsing lanes, nodes and rework loops out of deployed BPMN so the Infra-board can draw a phase swimlane, against twelve real process fixtures |

`src/utils` was rebuilt over the v2026.08.21 window, going from 5 files and 21
tests to 8 and 73 — `config.test.ts` the largest single addition, with
`tls-bootstrap` and `operaton-variables` newly covered. That is what took the
area from 43.47% statements to 100%. It has kept growing since: 11 files when
ValidSign added its own config coverage, and **13 files and 130 tests** at
v2026.09.11, which added `build-info.test.ts` and `cors-origin.test.ts` and
another 25 cases to `config.test.ts`. Of the twelve source files the area now
reports, **eleven are at 100 on all four measures**; the twelfth is `config.ts`
at 95.12% statements and 98.31% branches — see
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
