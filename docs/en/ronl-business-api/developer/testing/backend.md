---
component: RONL Business API
---

# Backend suite

`packages/backend`, Jest with the `ts-jest` preset. **105 files · 2633 tests ·
all passing · nothing skipped · `Time: 228.051 s`** under `--runInBand`,
followed by *"✓ all 136 documented operations were checked against a real
response"*. Coverage is on by default; see
[Coverage](coverage.md#backend-by-area) for the per-area figures.

Measured on **9 October 2026** for v2026.10.1 — the release in production,
`main` at `ebec288` — with `npm run test:serial --workspace=packages/backend`,
in the working checkout on `acc` at `0ea4985` (a tree identical to `ebec288`)
after `npm run deps:check` reported the install in sync with the lockfile, on
Node 22.23.3, the version `.nvmrc` names. The package total is the runner's
own. The per-file and per-area counts are not printed by Jest's default
reporter, so every file's count is parsed from its source at `ebec288` with
the TypeScript compiler, `.each` tables and literal `for … of` loops
expanded — never a grep for `it(`, which miscounts parameterised and
multi-line cases. Two tables are not literals and were resolved by hand:
`SHELLS.slice(1)` in `bpmn-swimlane.test.ts` (2 cases) and the router's
16 route layers in `public.routes.security.test.ts`. The sum is the runner's
2633 exactly, and the same parse at `0625d48` gives 2457 and every per-area
figure the 3 October pass published.

!!! success "`npm test` is two steps: Jest, then the conformance-coverage check"
    Since v2026.09.14 the backend's `test` and `test:serial` scripts end with
    `&& node scripts/check-conformance-coverage.cjs`. Jest runs the suite as
    before; the script then fails the run unless **every operation in the
    OpenAPI document was compared against a real response** at least once. On
    9 October it printed *"✓ all 136 documented operations were checked
    against a real response"* — the same number as on 3 October, by one in
    and one out: v2026.10.1 documented `GET /v1/process/available`, the
    services a citizen may start, and **removed** the `GET` spelling of
    `/v1/m2m/process/history`, deprecated for one release, which now answers
    404. On 3 October it was 133 from 30 September plus the two Besluitvorming
    lists and `POST /v1/m2m/process/history`.

    **That figure, and 2633 / 105, are this package's alone.** The repository
    runs **331 test files and 5069 tests** across five workspaces — see
    [Overview](overview.md). Quoting the backend's count as a repository total
    understates the suite by over two thousand tests.

!!! note "2011 → 2008 → 2028 → 2072 → 2198 → 2202 → 2370 → 2457 → 2633, and nothing was lost on the way"
    The suite reported **2011** for several releases, of which 2008 ran and
    **three were permanently skipped**. Those three guarded the
    `PHASE_NOT_MODELLED` branch of the RIP phase model. v2026.09.7 made an
    unmodelled phase unrepresentable (issue #85), the branch went, and the
    three skipped cases went with it — a deletion of dead tests rather than a
    regression. The **2633** measured here is growth on that 2008 base. No
    workspace in this repository skips anything.

    **v2026.10.1 added +176 tests and five files** against the 3 October
    measurement of v2026.10.0 (100 files, 2457) — 68 in the new files and
    108 in existing ones, most of it eDOCS acting as the person who asked,
    the eDOCS author stamp, and the citizen services:

    | File | Tests | What changed |
    |---|---:|---|
    | `auth/entra-token.service.test.ts` | **24, new** | Reading a person's stored Entra ID token from Keycloak's broker endpoint, so eDOCS can be reached as that person |
    | `routes/edocs.access.test.ts` | **17, new** | Who may use `/v1/edocs` and as whom: a listed machine client acts as the service account, a caseworker or admin as themselves, and every refusal carries its own code |
    | `services/edocs-author.test.ts` | **11, new** | The `edocsAuthor` and `edocsAuthorName` stamp — the member of staff who acted — that archived documents are titled after |
    | `auth/citizen-services.test.ts` | **10, new** | Which services a citizen is offered, from the latest deployment per tenant; a cross-tenant service only when exactly one tenant deploys it |
    | `utils/config.edocs.test.ts` | **6, new** | The eDOCS and Entra settings: the defaults and the three allowed clients, live eDOCS refused at start-up without the service credentials and the `ENTRA_*` settings, and the service-account fallback refused on production |
    | `services/edocs.service.test.ts` | 49 → **81** | One eDOCS session per principal, a person connecting with their own token, and a person's 403 treated as a refusal rather than retried |
    | `routes/process.routes.test.ts` | 104 → **117** | `GET /available` — 401, `403 FORBIDDEN` for anyone not a citizen, `503 SERVICES_UNAVAILABLE` rather than every service — an own-tenant service of another tenant refused (#344), the author stamped at start, and the access check that no longer reads every variable |
    | `routes/task.routes.test.ts` | 47 → **57** | The author stamped at completion and never returned, and the tenant check made on a non-deserialising read for claim, complete and form-schema |
    | `services/operaton.service.test.ts` | 182 → **192** | The latest deployment per tenant, the access variables read without deserialising, root instances only for *Mijn aanvragen*, and the author read for archiving |
    | `mcp-servers/edocs/index.test.ts` | 16 → **25** | Acting as the person: the caller's token instead of the server's own, a person's refusal never retried as the service |
    | `routes/edocs.routes.test.ts` | 36 → **44** | The principals: listed and unlisted machine clients, a person with and without an Entra token, `403 EDOCS_ACCESS_DENIED` rather than 502 |
    | `services/mcp/EdocsMcpProvider.test.ts` | 14 → **19** | The caller's token in `_meta`, never in the tool arguments, and a warning when a call has no caller |
    | `routes/m2m.routes.test.ts` | 91 → **93** | The `GET` history spelling no longer answers (three tests out, one in), and the reserved-variable refusals extended to `edocsAuthor` and `edocsAuthorName` |
    | `auth/tenant-access.test.ts` | 26 → **29** | A citizen's start across tenants only for a cross-tenant service; an untenanted deployment refused for a citizen; the reserved variables now five |
    | `rip-swimlane/bpmn-swimlane.test.ts` | 198 → **201** | Character references in lane and task names decoded |
    | `routes/validsign.routes.test.ts` | 120 → **123** | The signer recorded as `edocsAuthor`, and the task variables read without deserialising |
    | `services/externalTaskWorker.service.test.ts` | 31 → **34** | The author passed to the document worker, and fetched for that topic only |
    | `services/validsignCompletion.service.test.ts` | 13 → **15** | Both documents archived for the employee who acted |
    | `services/mcp/McpRegistry.test.ts` | 12 → **14** | The call context passed only to a provider that acts as the person |
    | `auth/jwt.middleware.test.ts`, `middleware/tenant.middleware.test.ts`, `services/mcpChat.service.test.ts` | +1 each | The bearer token kept out of anything that serialises or copies `req.auth`, and passed to every tool call |

    Every other file kept its count.

    **History: v2026.10.0 added +87 tests and three files** against the 30 September
    measurement of v2026.09.15 (97 files, 2370):

    | File | Tests | What changed |
    |---|---:|---|
    | `middleware/error.middleware.test.ts` | **8, new** | The 404, catch-all and rate-limit handlers, moved out of `index.ts` into a tested module: `404 NOT_FOUND`, `400 MALFORMED_BODY` for JSON that does not parse rather than 500, `413 PAYLOAD_TOO_LARGE`, an arbitrary error unable to choose its own status, the message hidden in production, `429 RATE_LIMIT_EXCEEDED` (#216) |
    | `utils/problem.test.ts` | **13, new** | `sendProblem` — status, `application/problem+json` and the RFC 9457 members, `instance` without the query string, extensions that can never replace an RFC member — and the title derived from a code |
    | `routes/besluitvorming.routes.test.ts` | **10, new** | `GET /v1/besluitvorming/active` and `/completed`, five cases each: 401 without a token, the tenant's besluiten, 500 on a failing service |
    | `rip-swimlane/bpmn-swimlane.test.ts` | 171 → **198** | Process-declared phases (`ronl:phases`, `ronl:phaseLabel`, `ronl:phase`): malformed and duplicate entries skipped, an undeclared code ignored, the two schemes never mixed, and every RIP fixture without a phase set; the HR capacity claim's eight phases; and `GedelegeerdBesluitProcess` — six lanes each with its own besluit role, six phases, and a declined signature escalating forward with no rework loop |
    | `services/operaton.service.test.ts` | 171 → **182** | The besluit lists and their outcome rule (`besluitUitkomst`), and resolving the task that created a signing package rather than any open task |
    | `routes/m2m.routes.test.ts` | 81 → **91** | `POST /process/history` with its filter, the deprecated `GET` still answering and still curated, and `400 RESERVED_VARIABLE` before any engine call — `municipality`, `originTenantId` and `applicantId` on task completion, the first two on start (#261, #263) |
    | `routes/validsign.routes.test.ts` | 116 → **120** | Signing state per task: a later signing task in the same instance starts afresh rather than opening as declined |
    | `services/validsignCompletion.service.test.ts` | 9 → **13** | Archive names built from the template and the business key, with a neutral fallback |

    Every other file kept its count. Twenty-one other test files were edited
    without a test added or removed — eighteen of them, the route suites and
    `auth` and `middleware` above all, because an error is now a problem: their
    assertions read `code` and `detail` where they read `error.code` and
    `error.message`.

    **History: v2026.09.14 and v2026.09.15 together added +168 tests and one file**,
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
triggers on `pull_request`, so these 2633 tests run *before* a merge rather than
only after one — and since **19 September 2026 that run is a required check**,
so a red backend suite now blocks the merge to `acc` outright. See
[Overview → What actually gates a merge](overview.md#what-actually-gates-a-merge).

| Area | Files | Tests |
|---|---:|---:|
| `src/routes` | 21 | 702 |
| `src/services` | 28 | 647 |
| `src/pa-monitoring` | 16 | 583 |
| `src/rip-swimlane` | 2 | 206 |
| `src/utils` | 15 | 150 |
| `src/media-aggregator` | 8 | 112 |
| `src/auth` | 4 | 88 |
| `src/mcp-servers` | 3 | 63 |
| `src/openapi` | 4 | 43 |
| `src/middleware` | 4 | 39 |

!!! success "Both columns are current, and they sum"
    Re-derived on 9 October 2026: the Files column accounts for all **105**
    files and the Tests column sums to **2633**, the measured total, every
    file parsed from its source at `ebec288` (see the note at the top of this
    page). Earlier versions of this page carried a Files column from
    one date and a Tests column from another that fell 274 short, with a
    warning attached; that gap is closed and has stayed closed across seven
    re-derivations.

    **Eight of the ten areas moved in v2026.10.1, and five files were
    added**: `src/routes` 20 → **21** files and 649 → **702** tests
    (`edocs.access` new, `process.routes` +13, `task.routes` +10,
    `edocs.routes` +8), `src/services` 27 → **28** files and 581 → **647**
    (`edocs-author` new, `edocs.service` +32, `operaton.service` +10),
    `src/auth` 2 → **4** files and 50 → **88** (`entra-token.service` and
    `citizen-services` new), `src/utils` 14 → **15** files and 144 → **150**
    (`config.edocs`), `src/mcp-servers` 54 → **63**, `src/rip-swimlane`
    203 → **206** and `src/middleware` 38 → **39**. `src/pa-monitoring`,
    `src/media-aggregator` and `src/openapi` are unchanged to the test.
    `src/services` has passed `src/pa-monitoring` for second place.

    **Five of the ten areas moved in v2026.10.0, and three files were added**:
    `src/routes` 19 → **20** files and 625 → **649** tests
    (`besluitvorming.routes` new, `m2m.routes` +10, `validsign.routes` +4),
    `src/rip-swimlane` 176 → **203**, `src/services` 566 → **581**,
    `src/utils` 13 → **14** files and 131 → **144** (`problem.test.ts`), and
    `src/middleware` 3 → **4** files and 30 → **38**
    (`error.middleware.test.ts`). `src/pa-monitoring`, `src/media-aggregator`,
    `src/mcp-servers`, `src/auth` and `src/openapi` are unchanged to the test.
    `src/services` is within two tests of `src/pa-monitoring` for second place.

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

!!! info "ValidSign is 181 of those tests, across five files"
    The [signing feature](../validsign-signing.md) arrived in v2026.08.36 and
    was the whole of the backend's growth in file terms for several releases.
    v2026.10.0 made signing state per task and named the archived documents
    after their template and case; v2026.10.1 records the signer as the
    archived documents' author. The same two files grew both times:

    | File | Tests | File time, 3 Oct (`--runInBand`) | File time, 9 Oct (`--runInBand`) |
    |---|---:|---:|---:|
    | `routes/validsign.routes.test.ts` | 116 → 120 → **123** | 5.5s | 5.7s |
    | `services/validsign.service.test.ts` | 32 | under 5s | under 5s |
    | `services/validsignCompletion.service.test.ts` | 9 → 13 → **15** | under 5s | under 5s |
    | `services/validsignPoller.service.test.ts` | 7 | under 5s | under 5s |
    | `utils/config.validsign.test.ts` | 4 | under 5s | under 5s |

    Jest prints a file's time only past its five-second slow-test threshold.
    Both time columns are in-band runs, one file at a time; on 30 September,
    in a parallel run, the route file took 29.3s. Read the next warning before
    drawing anything from any of them.

    The route file carries the most because the two unauthenticated routes are
    where the security properties live — capability URLs, the shared-secret
    check, and a rate limiter keyed on client IP rather than on an
    attacker-controlled header. It grew from 66 tests to 108 in v2026.09.9, to
    116 in v2026.09.12 — the signing endpoints refusing a task belonging to
    another tenant, or to none (#227) — to 120 in v2026.10.0, when a later
    signing task in the same instance began to start afresh instead of
    opening as declined, and to **123** in v2026.10.1: the signer recorded as
    `edocsAuthor`, and the task variables read without deserialising them.

    On 9 October the route module reports **97.27% statements · 98.38%
    branches · 100% functions · 97.05% lines**; `validsign.service.ts` and
    `validsignPoller.service.ts` are at 100 on all four, and
    `validsignCompletion.service.ts` at **94 / 92.59 / 100 / 95.74**, its
    branches up from 91.3 on 3 October with the attribution cases.

!!! warning "A per-file time is not a ranking, and this page used to publish it as one"
    Through v2026.09.9 the note above called `validsign.routes.test.ts` *the
    slowest single file in the backend suite*, at 38.5 seconds. The same file,
    across six passes: **38.5s**, then **81.7s** on 24 September (and only
    fifth), then too fast to print at all on 26 September, then **39.6s** on
    28 September, **29.3s** on 30 September, **5.5s** on 3 October, run
    in band, and **5.7s** on 9 October, in band again.

    The slowest files change with it. On 26 September they were
    `openapi/coverage.test.ts` (51.7s) and `routes/registry.test.ts` (51.6s);
    on 28 September the same two took 23.8s and 25.8s, and the top of the list
    was `pa-monitoring/pa.routes.test.ts` (71.5s) and
    `pa-monitoring/curation.service.test.ts` (69.4s). On 30 September it was
    `registry.test.ts` (42.8s) and `coverage.test.ts` (42.7s) again, with
    `pa.routes.test.ts` at 37.8s and `curation.service.test.ts` down to 15.7s.
    On 3 October, in band, only four files crossed five seconds:
    `coverage.test.ts` (65.0s, the first file of the run), `pa.routes.test.ts`
    (14.1s), `validsign.routes.test.ts` (5.5s) and `process.routes.test.ts`
    (5.3s). On 9 October, in band again, eight did: `coverage.test.ts`
    (69.9s, first again), `pa-dossiers.routes.test.ts` (21.9s),
    `sources/tk.client.test.ts` (14.5s), `pa.routes.test.ts` (10.3s),
    `sources/ep-texts-submitted.client.test.ts` (8.0s),
    `edocs.routes.test.ts` (6.7s), `public.routes.test.ts` (6.4s) and
    `validsign.routes.test.ts` (5.7s) — four of them in `pa-monitoring`, which
    v2026.10.1 did not touch.

    None of these figures is wrong and nothing regressed or improved. In a
    parallel run Jest reports each file's **elapsed** time while several workers
    share the machine, so a file's number depends on what ran beside it — which
    is why the 30 September file times sum to far more than that run's own
    `Time: 54.672 s`. In band, a file's time is its own, though the first file
    may also carry the run's start-up cost. Compare per-file times within one run, never
    across two, and do not build a superlative out of them.

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
| `src/services` | Every service — `operaton`, `edocs` and, new in v2026.10.1, **`edocs-author`** (the member of staff who acted, stamped as `edocsAuthor` and `edocsAuthorName`), `doccle`, `audit`, `berichten`, `nieuws`, `search`, `regelcatalogus`, `productenDiensten`, `mcpChat`, `externalTaskWorker`, `lde`, the `llm/` providers (Anthropic, OpenAI), the `mcp/` provider wrappers (Cprmv, Lde, Operaton, TriplyDb), and the three [ValidSign](../validsign-signing.md) services |
| `src/routes` | Every route module, mounted with the service layer and auth mocked and supertest driving requests — `m2m`, `process`, `public.routes` and its security counterpart, `edocs`, `task`, `rip`, plus `doccle`, `mcp`, `health`, `hr`, `capacity`, `decision`, `brp`, `admin`, `validsign`, `root` (new in v2026.09.11, and now built from the registry's advertised endpoints), and, new in v2026.10.1, **`edocs.access`**: a machine client on `EDOCS_ALLOWED_CLIENTS` acts as the service account, a caseworker or admin as themselves, and each refusal has its own code — `EDOCS_CLIENT_NOT_ALLOWED`, `FORBIDDEN`, `EDOCS_USER_TOKEN_UNAVAILABLE`, `EDOCS_REAUTH_REQUIRED`, `EDOCS_ACCESS_DENIED`. In v2026.10.1 `process.routes` gained `GET /available`, the citizen's services, and `m2m` lost the deprecated `GET` history spelling, which a test now asserts no longer answers. Since v2026.10.0 every refusal and failure these suites assert is an RFC 9457 problem — `code` and `detail` where they used to read `error.code` and `error.message` (#216) — and two suites are new or reshaped by the release: **`besluitvorming.routes`**, the tenant-scoped running and completed besluit lists, and **`m2m`**, which now asserts `400 RESERVED_VARIABLE` before any engine call on start and on completion (#261) and the filtered `POST /process/history` (#263). New in v2026.09.12: **`openapi.routes`** — `GET /v1/openapi.json` serves the document with any origin allowed, reads it once when the router is built rather than per request (so a zip deploy cannot serve a document from an artifact the process is not running), and answers a 500 problem rather than crashing at load when the file is missing; and **`registry`** — every mount is under `/v1`, the ValidSign callback router precedes the authenticated one on the same mount, only `/v1/validsign` and `/v1/pa` carry two routers, and every path the root banner advertises is actually mounted, the drift that let it promise `/v1/docs` from the initial commit (#67) |
| `src/openapi` | New in v2026.09.12 (#200), and completed in v2026.09.14 (#214, #269). **`coverage`** is the contract gate, three rules: both sides actually loaded, since two empty lists agree perfectly; every served operation is documented in `openapi/openapi.yaml`; and every documented operation is still served. The pending list that used to sit beside it — `openapi/pending.json`, with a ceiling of 18 that could only move down — is **gone**: #214 described the last undocumented operations, the rules that read the list became trivially true, and they were deleted with the file, so a route added without a description now fails here rather than being let in with the number bumped. **`testing/conformance`** tests `expectToMatchOperation`, which the route suites call on real supertest responses: the operation is documented, the status is documented for it (falling back to `default`), a 2xx carries `API-Version` (ADR API-57), and the content type is documented and the body validates against its schema with Ajv's JSON Schema 2020-12 validator, formats included and strict schema checking on. It also records every operation it is asked about, even one whose check then fails, so that `scripts/check-conformance-coverage.cjs` can fail `npm test` if any documented operation was never checked. **`document`** reads the real built `openapi.json` and rejects anything that is not an OpenAPI document with paths, without masking a missing file. **`testing/routeOperations`** turns the registry and the document into comparable operation lists, and throws rather than skips on a nested router, a non-string path or an unsupported method, since skipping would hide an operation from the gate |
| `src/media-aggregator` | `net-guard` (the SSRF guard: IPv4/IPv6 rules, every DNS path), `ingest`, `search`, `store`, `sanitize`, `stable-id`, plus the aggregator's own route module |
| `src/utils` | `config` and its ValidSign and — new in v2026.10.1 — eDOCS counterparts, `env`, `logger`, `operaton-variables`, `slug`, `tls-bootstrap`, `altcha`, `errors`, `client-ip`, `dutch-datetime`, — new in v2026.09.11 — `build-info` and `cors-origin`, and — new in v2026.10.0 — **`problem`**: `sendProblem` writes `application/problem+json` with `type`, `status`, `title`, `detail` and `instance` (the request path, query string stripped) plus the `code` extension, never lets an extension replace an RFC member, and derives the title from the code |
| `src/mcp-servers` | The standalone stdio MCP servers (`lde`, `triplydb`, `edocs`) — each mocks the MCP SDK to capture and drive its `ListTools`/`CallTool` handlers directly. Since v2026.10.1 the `edocs` server acts as the person whose token arrives in the call's `_meta`, and never retries that person's refusal with its own token |
| `src/middleware` | `tenant.middleware` and `audit.middleware`; — new in v2026.09.12 — `version.middleware`: every response carries an `API-Version` header with the CalVer release string, error responses and unrouted 404s included; and — new in v2026.10.0 — **`error.middleware`**, the 404, catch-all and rate-limit handlers that used to live untested in `index.ts`: `404 NOT_FOUND`, a malformed JSON body answering `400 MALFORMED_BODY` instead of 500, an oversized one `413 PAYLOAD_TOO_LARGE`, an arbitrary error unable to choose its own status, the message hidden in production, and `429 RATE_LIMIT_EXCEEDED` |
| `src/auth` | `jwt.middleware` — token validation, role and assurance gates, and since v2026.10.1 a bearer token kept out of anything that serialises or copies `req.auth` — new in v2026.10.1, **`entra-token.service`**, which reads a person's stored Entra ID token from Keycloak so eDOCS can be reached as that person, refusing with `EDOCS_USER_TOKEN_UNAVAILABLE` or `EDOCS_REAUTH_REQUIRED`, and **`citizen-services`**, the services a citizen may start; and, new in v2026.09.12, **`tenant-access`**, the one module that decides tenant questions for process and task access (#218, #219, #229): an exact, case-sensitive tenant match with no match for a missing label; a staff start across tenants refused while a citizen's case is stamped with the deployed tenant and its origin recorded — since v2026.10.1 only for a cross-tenant service such as Zorgtoeslag, and never from an untenanted deployment; a token without a roles claim treated as staff; case reads admitted to the owning tenant or the applicant only; and the single `403 TENANT_MISMATCH` answer |
| `src/rip-swimlane` | `bpmn-swimlane` and `doc-label` — parsing lanes, nodes and rework loops out of deployed BPMN into a swimlane model, against twelve real RIP phase fixtures, since v2026.09.14 seven Awb process fixtures under `__fixtures__/awb/`, and since v2026.10.0 two under `__fixtures__/declared/` — `GedelegeerdBesluitProcess` (six lanes, six phases) and the HR capacity claim (eight phases). The parser serves any laned process, not only RIP: script, business-rule and call-activity nodes as their own kinds, lane groups, and the phase markers the caseworker's phase stepper reads — the built-in Awb set through `ronl:awbPhase`, or, since v2026.10.0, a process's own set declared with `ronl:phases`, `ronl:phaseLabel` and `ronl:phase`. The tests pin that the two schemes never mix, that malformed, duplicate and undeclared entries are ignored, and that none of the twelve RIP fixtures carries a phase set |

`src/utils` was rebuilt over the v2026.08.21 window, going from 5 files and 21
tests to 8 and 73 — `config.test.ts` the largest single addition, with
`tls-bootstrap` and `operaton-variables` newly covered. That is what took the
area from 43.47% statements to 100%. It has kept growing since: 11 files when
ValidSign added its own config coverage, and **13 files and 130 tests** at
v2026.09.11, which added `build-info.test.ts` and `cors-origin.test.ts` and
another 25 cases to `config.test.ts`, 131 at v2026.09.12, one more case in
`errors.test.ts`, and **14 files and 144 tests** at v2026.10.0, which added
`problem.test.ts` (13), and **15 files and 150 tests** at v2026.10.1, which
added `config.edocs.test.ts` (6). Of the thirteen source files the area
reports on 9 October, **twelve are at 100 on all four measures**, `problem.ts`
among them; the thirteenth is `config.ts` at 96.29% statements and 98.52%
branches —
see [Coverage](coverage.md#backend-by-area).

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
  to satisfy every field every route module reads.
- **The conformance check runs after Jest, as its own process.** `npm test` and
  `npm run test:serial` are `jest --coverage … && node
  scripts/check-conformance-coverage.cjs`. It was first written as a Jest
  `globalTeardown`, and that version was useless: Jest prints an error thrown
  there but still exits 0. A filtered run — `npx jest -t …`, a single file,
  `test:contract`, `test:openapi-coverage` — does not go through `npm test`
  and so never reaches the check, which also skips with a note when there is
  no log at all. **Only the full `npm test` proves every documented operation
  was checked.**
- **Assert an error as a problem.** Since v2026.10.0 every 4xx and 5xx is
  `application/problem+json`, so a route test reads `res.body.code` and
  `res.body.detail` — `expect(res.body.code).toBe('TENANT_MISMATCH')` — not
  `res.body.error.code`. Answer with `sendProblem` from `utils/problem` in the
  route; a `jwtMiddleware` stub that refuses answers a problem too, as
  `task.routes.test.ts`'s does. Success bodies keep `{ success, data }`.
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
