---
component: RONL Business API
---

# Public site suite

`packages/public-site`, Vitest with jsdom. **34 files · 275 tests · all
passing · 71.32s** without file parallelism.

!!! success "Re-measured at v2026.10.1: nothing changed, and the figures held"
    Re-run on **9 October 2026** for v2026.10.1 (`main` at `ebec288`), in the
    working checkout on `acc` at `0ea4985`, a tree identical to `ebec288`,
    with `npm run test:serial --workspace=packages/public-site` on
    Node 22.23.3: **34 files · 275 tests · all passing · `Duration 71.32s`**,
    coverage **96.68 / 97.41 / 95.09 / 97.23**. v2026.10.1 did not touch this
    package — `git diff 0625d48 ebec288 -- packages/public-site` is empty —
    and every count reproduced. Branches read 97.41 against 97.40 on
    3 October: one hundredth of run-to-run noise on identical code, in
    `src/pages` (97.29 → 97.31), which [Coverage](coverage.md) explains.

!!! note "History: re-measured at v2026.10.0, one new file, ten new tests"
    Re-run on **3 October 2026** for v2026.10.0 (`main` at `0625d48`), in the
    working checkout on `acc` at `0e3eed8`, a tree identical to `0625d48`,
    with `npm run test:serial --workspace=packages/public-site` on
    Node 22.23.2: **34 files · 275 tests · all passing · `Duration 76.58s`**,
    coverage **96.68 / 97.40 / 95.09 / 97.23**, against 33 · 265 and
    96.60 / 97.34 / 95.07 / 97.17 on 30 September. The duration is a serial
    run's and not comparable with the 24.09s parallel figure of 30 September.

    One change accounts for all of it: **v2026.10.0's problem details** (#216).
    The backend now answers every error as RFC 9457
    `application/problem+json`, and the site reads the message from a
    problem's `detail`. `src/lib/problem.test.ts` is new, **9 tests** —
    `problemMessage` returning a problem's `detail`, still reading a legacy
    envelope's `error.message`, and falling back for anything else — and
    `lib/api.test.ts` gained one, 13 → **14**. `lib/problem.ts` is at 100 on
    all four measures; `lib/api.ts` reads 96.55% branches, against 97.29% on
    30 September.

!!! note "History: re-measured at v2026.09.15, one new file, thirty new tests"
    Measured on 30 September 2026 for v2026.09.15: **33 files · 265 tests**,
    against 32 · 235 on 28 September.

    Two changes accounted for all of it. **v2026.09.14's link previews**
    (`6c3fe10`) added `src/indexHtml.test.ts` — the Open Graph and robots tags
    in `index.html`, filled per build mode from the committed `.env` files, 23
    tests — and three cases to `scripts/prerender.test.ts`, which now reads the
    site's origin, API and indexability through Vite's `loadEnv`, builds a
    `robots.txt` that shuts crawlers out on ACC, and replaces the shell's
    canonical link rather than adding a second. **v2026.09.15's branch-margin
    commit** (`73a6764`) added three cases to `lib/api.test.ts` and one to
    `Footer.test.tsx`, and made the package's only source change: `lib/api.ts`
    now reads `import.meta.env` directly so its base-URL fallbacks can be
    stubbed, taking that file from 83.78% branches to 97.29%.

The public site is the auth-free search and rule-catalogue package, measured
with `npm run test:serial --workspace=packages/public-site`, coverage
included, on Node 22.23.3, the version `.nvmrc` names. The suite grew in
every window up to v2026.10.0 — 30 files and 204 tests at v2026.09.5, 31 and
225 at v2026.09.7, 32 and 231 at v2026.09.9, 32 and 235 at v2026.09.11
through v2026.09.13, 33 and 265 at v2026.09.15, **34 and 275** at
v2026.10.0 — and held at that in v2026.10.1.

Coverage is **96.68% statements · 97.41% branches · 95.09% functions · 97.23%
lines**, and the package passes the per-file 80% branch floor that its
`vite.config.ts` enforces rather than merely records: no file in it is below the
line, and since v2026.09.15 none is below 85 either. The lowest by branches are
`lib/useQueryState.ts` and `pages/herkomst/HerkomstTrace.tsx`, both at 87.50%.

!!! note "History: branches fractionally down at v2026.09.11, and why"
    Against v2026.09.9 — 95.82 / 96.45 / 94.89 / 96.33 — v2026.09.11 gained on
    statements, functions and lines while branches gave up 0.14 of a point.
    `Detail.tsx` was at 100% statements and 97.84% branches after its change,
    so nothing regressed; what moved the package figure was `lib/api.ts`, which
    gained branch surface it was not yet fully exercising (83.78% branches).
    That is the ordinary shape of adding a guarded code path and testing its
    main case first — and v2026.09.15 tested the rest, taking the file to
    97.29%.

---

## Inventory

**Re-derived on 9 October 2026** at `ebec288`, identical to 3 October at
`0625d48`. The Files column accounts for all **34** files and the Tests
column sums to **275**, the runner's total. The per-area test counts are
taken from the source — each test file parsed, with `it.each` tables and the
`describe.each` in `indexHtml.test.ts` expanded — because this pass used
Vitest's console reporter, which prints only the package total; the same
method reproduces the 24 September runner-derived table exactly at
`963fe24`.

| Area | Files | Tests | Covers |
|---|---:|---:|---|
| `src/pages` | 16 | 137 | Includes a full `herkomst/` provenance-explorer sub-area (`HerkomstExplorer`, `HerkomstTrace`, `HerkomstChip`, `HerkomstBackground`, `herkomstConcepts`, `herkomstData`, `herkomstScroll`, `herkomstTrail` — 8 files) plus the generic `SectionIndex` / `Regelcatalogus` / `Results` / **`Detail` (25)** / `Woordenboek` / static pages |
| `src/lib` | 8 | 59 | `slug` (kept identical to the backend's slugifier by design), `useQueryState` (URL-backed filters), `search` (`highlight()`), `api` (the typed `/v1/public/*` client, 14 — three new in v2026.09.15 for its base-URL fallbacks, one in v2026.10.0), **`problem` (9, new in v2026.10.0** — reading the message from an RFC 9457 problem's `detail`, or a legacy envelope's `error.message`), `sectionHits` (`mapToHits()`), `prerenderedData` (the seeded-render reader), `buildInfo` |
| `scripts/` | 2 | 24 | `prerender.test.ts` (14 — `escapeHtml`, `readSiteEnv` per build mode, `buildRobots`, `buildSitemap`, `injectIntoShell`), `check-bundle.test.ts` (10 — the build-time gate that fails if any auth or telemetry string ships in the bundle) |
| `src/components` | 4 | 23 | `chrome` (7), `Footer` (7), `StatusTag` (5, new in v2026.09.9), `TechDetails` (4) |
| **`src/indexHtml.test.ts`** | 1 | 23 | **New in v2026.09.14.** The link-preview and robots tags in `index.html` as `vite build --mode <mode>` writes them, for production, acceptance, development and test (five tests each), plus the fixed Dutch copy, the title and the card image's size |
| `src/App.test.tsx` | 1 | 5 | Routing shell — every route registered, `<html lang>` synced to the language switch |
| `src/i18n` | 1 | 3 | NL/EN dictionary key parity |
| `src/staticwebapp-csp.test.ts` | 1 | 1 | Guards the shipped CSP header — a regression here silently breaks the org-logo host |

!!! success "Both columns are current, and they sum"
    Earlier versions of this page carried a Files column from one date and a
    Tests column from 19 August that summed to 134 against a measured 225, with
    a warning attached. Re-derived, the columns agree: 34 files, **275** tests.
    Against 30 September, only `src/lib` moved — 7 files and 49 tests to
    **8 and 59**, `problem.test.ts` and one case in `api.test.ts`. Between
    24 and 30 September, `src/lib` gained 3, `scripts/` 3 and
    `src/components` 1, and `indexHtml.test.ts` arrived with 23.

    The prerender test runs in the `node` environment rather than jsdom since
    v2026.09.14: `prerender.ts` now reads the `.env` files through Vite's
    `loadEnv`, and the esbuild that Vite loads refuses to start under jsdom.
    Both it and `indexHtml.test.ts` set the inherited `VITE_*` variables aside
    first, because Vitest has already put the test mode's values into
    `process.env`, which `loadEnv` lets override the file — without that, every
    mode would read the test file.

!!! info "`StatusTag` is the file v2026.09.9 added"
    `src/components/StatusTag.test.tsx` arrived with the `StatusTag.tsx` it
    covers, and both are at **100% statements, branches, functions and lines**
    — 3/3 statements, 2/2 branches, 1/1 functions, 3/3 lines. Its five tests
    run in 91ms:

    - renders the known status `example` with its own class
    - renders the known status `wip` with its own class
    - renders the known status `e2e` with its own class
    - falls back to a neutral class for a status label it does not recognise
    - **always shows the label as text, never colour alone**

    The last is an accessibility property rather than a rendering detail: a
    status conveyed only by colour fails for anyone who cannot distinguish the
    palette, and it is the kind of regression a snapshot test would happily
    wave through.

Per-area coverage was also re-derived on 9 October and reconciles to the
package total — see [Coverage](coverage.md#public-site-by-area).

The statement-to-branch gap this package was once known for is gone. It was the
widest of the five at 16.4 points, 86.82% statements against 70.39% branches.
Today branches sit **above** statements — 97.41% against 96.68% — which is
what a campaign against a per-file *branch* floor looks like once it lands. The
margin had narrowed from 0.63 of a point to 0.39 by 28 September; the
`lib/api.ts` work widened it again, to 0.74 on 30 September; it was 0.72 on
3 October and is 0.73 now.

---

## Playwright suite

`packages/public-site/e2e/publiek.spec.ts`
(`npm run test:e2e --workspace=@ronl/public-site`) against real
`/v1/public/*` data with no mocks — search → filter → detail → back with URL
preservation, a deep link with pre-applied filters, keyboard-only navigation,
and three axe-core accessibility scans (home, results, a detail page) asserting
no critical or serious violations.

!!! warning "Re-run on 9 October 2026: 6/6 serially, 2 timeouts in the parallel run — as on 3 October"
    **Measured 9 October 2026 for v2026.10.1**, against the developer's
    already-running backend: **default run, six parallel workers, 4 passed,
    2 failed, 16.8s** — the same two search-journey tests as on 3 October,
    each the same `TimeoutError` after 10s waiting for the *Regel* filter
    checkbox — and **6 passed in 6.4s with `--workers=1`** against the same
    backend. Recorded the same way: **6/6 serially, 2 timeouts in the
    parallel run**, not a defect. Two passes a week apart failing the same
    wait under six workers is a pattern, and the thing to fix at the spec's
    own boundary before this suite goes into CI.

    **Measured 3 October 2026 for v2026.10.0**, against the developer's
    already-running backend, the first run since 30 August:

    - **Default run, six parallel workers: 4 passed, 2 failed, 17.2s.** Both
      failures were the search-journey tests — `publiek.spec.ts:6`
      (*search → filter → detail → back preserves the filtered URL*) and
      `:27` (*a deep link with filters pre-applied renders those filters
      checked*) — and both the same `TimeoutError`: 10s waiting for
      `getByRole('checkbox', { name: /Regel/ }).first()` to be visible.
    - **Re-run with `--workers=1`: 6 passed, 7.8s**, against the same backend.

    Recorded that way — **6/6 serially, 2 timeouts in the parallel run** — and
    not as a defect: nothing failed on its own, and the detail-page axe scan,
    which needs search results as much as the two that failed, passed in the
    parallel run. A missing backend fails three, serially as well (see below).
    The config sets `fullyParallel: true` and no `workers`, so a default run
    takes Playwright's default worker count — six on that machine — and
    `retries` is 2 in CI and 0 locally. The spec is unchanged since `2443adc`
    and still runs in no workflow.

    Before this, the figures were **19 August 2026, against v2026.08.19: 6 tests,
    6 passed, 0 failed, 0 flaky, 0 skipped, 8.9s**, and a 30 August inventory
    count of six.

Unlike the frontend suite, Playwright starts its own dev server for this package
— `playwright.config.ts` declares a `webServer` running `npm run dev` on
`:5175`, with `reuseExistingServer` on outside CI. **Only the backend needs to
already be running**, on whatever `VITE_API_URL` points at: these specs hit real
`/v1/public/*` search results rather than mocks, which is why three of the six
fail on timeouts without it.

Setting `E2E_BASE_URL` skips starting the local server entirely and points
`baseURL` at an already-deployed site instead, which is how the suite is used
for post-deploy verification against ACC. Re-read from the config at `86af73e`
on 24 September 2026 and unchanged at `ae06c9e`, `0625d48` and `ebec288`: `webServer` on
`:5175`, no `globalSetup` of
any kind, and the backend dependency stated in the config's own header comment
rather than checked before the run.

---

## CI

Public-site is the package that had a real CI test gate before the others did.
Both `azure-publicsite-acc.yml` and `-prod.yml` run `npm run lint`,
`npm run type-check`, then `npm test` before building, and the build itself
gates on a prerender step and a bundle-cleanliness check. A failing test blocks
the deploy.

**Since v2026.09.14 the build step also runs `node scripts/check-og.mjs
acceptance`** (or `production`) against the built `dist/`, before the upload.
The unit tests prove the template, the `.env` files and the prerender agree;
this proves the files actually shipped are the ones for their environment —
every prerendered page, not only the home page, since each is a copy of the
shell. An ACC build carrying the production card, or letting crawlers in,
fails the deploy rather than reaching every link unfurler's cache or a search
index.

**Since 19 September 2026 it blocks the merge as well.** The `acc` ruleset
(*acc supply-chain gate*) lists **`Build and Deploy ACC Public Site`** among its
required status checks, alongside `audit`, `scan`, `build`,
`Build and Deploy ACC Frontend`, `Build and Deploy ACC PA Demo` and, since
v2026.10.1, `lockfile-review` — so a red suite here now stops the pull
request rather than merely reporting against it. Read from
`gh api repos/sgort/ronl-business-api/rulesets` on 20 September 2026,
unchanged when re-read on 30 September, and re-read as the rules in force on
`acc` on 9 October. Since v2026.10.1 `azure-publicsite-acc.yml` also runs on
a change to `package-lock.json` or `package.json`, so a lockfile-only pull
request — Renovate's above all — is built and tested here too.

!!! warning "This page said the opposite until 20 September 2026"
    It previously stated that the only required check on `acc` and `main` was
    `audit`, so "a red suite here has to be read rather than relied on to stop a
    pull request". That was true when written and is now false for `acc`. It
    remains true for `main`, deliberately — `main` requires `audit` and, since
    the end of September, `scan`, but no suite: no production workflow has a
    `pull_request` trigger, so no production check could be required of a
    promotion. See
    [Overview → What actually gates a merge](overview.md#what-actually-gates-a-merge).

Since the per-file branch floor lives in `vite.config.ts`, this same `npm test`
step is also where coverage is enforced — the required check and the coverage
gate are one command.
