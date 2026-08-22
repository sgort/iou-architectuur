---
component: RONL Business API
---

# Writing tests

Conventions for adding tests here, and the traps that have already cost real
time. The second half is the more valuable part: each one is a case where the
suite was green and wrong.

---

## Conventions

- **Colocate.** `foo.ts(x)` → `foo.test.ts(x)`, next to the source, in all three
  packages — no `__tests__` or `tests/` directories.
- **Backend**: mock at the service boundary (axios, pg-promise, the MCP SDK) and
  drive routes with supertest through a real `jwtMiddleware` test stub reading
  an `x-test-roles` header. Path aliases (`@utils/`, `@services/`, `@auth/`,
  `@middleware/`, `@routes/`, `@models/`, `@ronl/shared`) are mapped in
  `packages/backend/jest.config.js` and work inside test files.
- **Frontend and public site**: default to the `node` Vitest environment and opt
  into `jsdom` per file with `// @vitest-environment jsdom` only when a component
  or DOM-touching hook needs it. Mock at the network boundary with `msw`, not by
  stubbing `axios` methods directly. Use `vi.hoisted` for any mock referenced
  inside a `vi.mock` factory.
- **Shared mocks and fixtures** used by more than one test file in a directory go
  in a local `__helpers__` subdirectory — do not create one until a second file
  actually needs to share something.
- **Scope large containers to critical interactions**, not exhaustive branch
  coverage: mock every child component or context one level below what the
  container under test actually consumes, since those children have their own
  test files.
- **Keep wall-clock assertions out of the main suite.** A budget asserted against
  `performance.now()` measures the machine as much as the code once 133 test
  files compete for cores. Name such a spec `*.perf.test.ts`: the default run
  excludes them and `npm run test:perf` executes them without file parallelism,
  as its own CI step.
- **Update the counts on these pages** when work lands, from a real run
  (`--json --outputFile=…` for Jest, `--reporter=json --outputFile=…` for
  Vitest) rather than an estimate or a grep for `it(` / `test(` — both miscount
  multi-line and parameterised cases.

---

## Make every test file a module

A `.ts` file with no top-level `import` or `export` is a **global script** to
TypeScript, not a module. Every top-level declaration in it lands in the global
scope, where it collides with identically-named declarations in sibling files.

Nine backend test files were in exactly that state — using `jest.mock()` and
`require()` inside functions, with no top-level import — and ten names collided
across them: `mockAxios` in five files, `Mod` and `freshModule` in six each,
`Handler` / `listTools` / `callTool` / `call` / `textOf` / `mockServer` across
the three `mcp-servers` suites, and `RSS` in two.

The fix is one line per file:

```ts
export {};
```

**This was invisible locally for weeks.** ts-jest caches type diagnostics per
file, so a warm cache skipped re-checking the collision and every local run was
green. The first CI run on a cold runner failed immediately. Which files fail
also varies, because it depends on the order the type program reaches them — CI
reported three, a cold local run reported two, and all nine were latent
regardless.

```bash
npx jest --config packages/backend/jest.config.js --clearCache
```

Run that before trusting a green backend suite to mean the code compiles.

---

## A throttled run is not a failing run

`pa-live-authoring` failed roughly every other run. Two diagnoses were written
and both were wrong — a slow stack, then a post-login token race — and neither
had evidence behind it.

Instrumenting the failing run with a response listener showed six consecutive
**429s**. The backend allowed 100 requests per minute per IP, and one short
authoring journey measures 21 requests to `/v1/pa/*`, so two specs back to back
exhausted the budget. The UI renders a 429 as *"Kon dossiers niet laden"*,
which is indistinguishable from a backend that is down.

`e2e/helpers/rate-limit.ts` now records the first 429 of a run and fails the
test with a message naming the throttle. It deliberately does **not** retry or
wait it out — a test that silently absorbs a throttle is a test that will
mislead the next person too. The shipped default was raised to 1000/min in
`config.ts`; the limiter keys on IP, so `TRUST_PROXY` decides whether that
budget is per user or per deployment.

The lesson generalises: when a test fails intermittently, instrument before
theorising. Both wrong diagnoses were plausible, and one response listener
settled it in a single run.

---

## `locator.count()` and `locator.isVisible()` do not auto-wait

An `afterEach` cleanup guarded with `if (await count())` read `0` before the
list had rendered, silently deleted nothing, and left ten test dossiers in the
dev database.

A cleanup that quietly does nothing is indistinguishable from one that worked.
Cleanup now waits with `expect(...).toBeVisible()` and warns rather than
swallowing.

Most Playwright assertions auto-wait; these two query methods do not. That
asymmetry is easy to miss precisely because everything around them is
forgiving.

---

## A hand-written mock can pass vacuously

`expectMockNamesRealExports` was first written comparing `import(path)` against
the mock — but the path is mocked, so it compared the mock with itself and would
have passed no matter what.

It was caught only by deliberately injecting a bogus export name and noticing
that the assertion **failed to fail**. That is the check worth internalising:
a new assertion is not trustworthy until you have seen it go red for the right
reason.

Both helpers — `packages/frontend/src/test/mockModule.ts` and
`packages/backend/src/test-utils/mockModule.ts` — now require
`vi.importActual` / `jest.requireActual`, and say so in their own doc comments.

The companion pattern, spreading the real module before the overrides, is what
stops an export added later from silently becoming `undefined`. That is exactly
how `EU_DOCUMENT_TYPES` disappeared from a mock and made `GET /v1/pa/types`
answer 500 while every test passed.

A related guard, `packages/frontend/src/test/paData.stub.ts` and its parity
test, renders the real `PaDataProvider` and asserts key equality in both
directions against the canonical stub. Adding a member to the context without
adding it to the stub now fails once, loudly, instead of surfacing as an
unhandled rejection inside whichever component happens to call it first — which
is how a CI run failed in this window with 1070 tests passing.
