---
component: RONL Business API
---

# Public site suite

`packages/public-site`, Vitest with jsdom. **32 files · 231 tests · all
passing · 15.67s.**

The public site is the auth-free search and rule-catalogue package. Measured on
**20 September 2026** on `main` at `10bcf8b` (v2026.09.9) with
`npm test --workspace=@ronl/public-site`, coverage included, after a clean
`npm ci` in a separate clone on Node 24.14.1 / npm 11.11.0. The suite has grown
in every recent window — 30 files and 204 tests at v2026.09.5, 31 and 225 at
v2026.09.7, **32 and 231 now** — the file added this time being
`src/components/StatusTag.test.tsx`.

Coverage is **95.82% statements · 96.45% branches · 94.89% functions · 96.33%
lines**, and the package passes the per-file 80% branch floor that its
`vite.config.ts` enforces rather than merely records: no file in it is below the
line.

---

## Inventory

**Re-derived on 20 September 2026** from the run's own JSON output. Both numeric
columns are from that run: the Files column accounts for all **32** files and
the Tests column sums to **231**.

| Area | Files | Tests | Covers |
|---|---:|---:|---|
| `src/pages` | 16 | 133 | Includes a full `herkomst/` provenance-explorer sub-area (`HerkomstExplorer`, `HerkomstTrace`, `HerkomstChip`, `HerkomstBackground`, `herkomstConcepts`, `herkomstData`, `herkomstScroll`, `herkomstTrail` — 8 files) plus the generic `SectionIndex` / `Regelcatalogus` / `Results` / `Detail` / `Woordenboek` / static pages |
| `src/lib` | 7 | 46 | `slug` (kept identical to the backend's slugifier by design), `useQueryState` (URL-backed filters), `search` (`highlight()`), `api` (the typed `/v1/public/*` client), `sectionHits` (`mapToHits()`), `prerenderedData` (the seeded-render reader), `buildInfo` |
| `src/components` | 4 | 22 | `chrome` (7), `Footer` (6), **`StatusTag` (5, new in v2026.09.9)**, `TechDetails` (4) |
| `scripts/` | 2 | 21 | `prerender.test.ts` (11 — `escapeHtml`, `buildSitemap`, `injectIntoShell`), `check-bundle.test.ts` (10 — the build-time gate that fails if any auth or telemetry string ships in the bundle) |
| `src/App.test.tsx` | 1 | 5 | Routing shell — every route registered, `<html lang>` synced to the language switch |
| `src/i18n` | 1 | 3 | NL/EN dictionary key parity |
| `src/staticwebapp-csp.test.ts` | 1 | 1 | Guards the shipped CSP header — a regression here silently breaks the org-logo host |

!!! success "Both columns are current, and they sum"
    Earlier versions of this page carried a Files column from one date and a
    Tests column from 19 August that summed to 134 against a measured 225, with
    a warning attached. Re-derived from the runner, the columns now agree: 32
    files, 231 tests. The largest correction is `src/pages`, which was recorded
    at 71 and actually holds **133**.

!!! info "`StatusTag` is the file this release added"
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

Per-area coverage was also re-derived on 20 September and now reconciles to the
package total — see [Coverage](coverage.md#public-site-by-area).

The statement-to-branch gap this package was once known for is gone. It was the
widest of the five at 16.4 points, 86.82% statements against 70.39% branches.
Today branches sit **above** statements — 96.45% against 95.82% — which is
what a campaign against a per-file *branch* floor looks like once it lands.

---

## Playwright suite

`packages/public-site/e2e/publiek.spec.ts`
(`npm run test:e2e --workspace=@ronl/public-site`) against real
`/v1/public/*` data with no mocks — search → filter → detail → back with URL
preservation, a deep link with pre-applied filters, keyboard-only navigation,
and three axe-core accessibility scans (home, results, a detail page) asserting
no critical or serious violations.

!!! warning "These figures date from 19 August and were not re-run for v2026.09.9"
    **Measured 19 August 2026 against v2026.08.19: 6 tests, 6 passed, 0 failed,
    0 flaky, 0 skipped, 8.9s.**

    They were not re-measured on 12 September 2026 and were **not re-measured on
    20 September 2026 either** — running them needs a live backend, and this
    pass deliberately ran nothing that required the stack. The package has
    changed underneath them twice since, so take the six as an inventory figure
    rather than as a result. What *was* re-checked is the inventory itself:
    `e2e/publiek.spec.ts` is still the one spec, and it still runs in no
    workflow. These remain the oldest figures on these pages.

Unlike the frontend suite, Playwright starts its own dev server for this package
— `playwright.config.ts` declares a `webServer` running `npm run dev` on
`:5175`, with `reuseExistingServer` on outside CI. **Only the backend needs to
already be running**, on whatever `VITE_API_URL` points at: these specs hit real
`/v1/public/*` search results rather than mocks, which is why three of the six
fail on timeouts without it.

Setting `E2E_BASE_URL` skips starting the local server entirely and points
`baseURL` at an already-deployed site instead, which is how the suite is used
for post-deploy verification against ACC. Re-read from the config on
20 September 2026.

---

## CI

Public-site is the package that had a real CI test gate before the others did.
Both `azure-publicsite-acc.yml` and `-prod.yml` run `npm run lint`,
`npm run type-check`, then `npm test` before building, and the build itself
gates on a prerender step and a bundle-cleanliness check. A failing test blocks
the deploy.

**Since 19 September 2026 it blocks the merge as well.** The `acc` ruleset
(*acc supply-chain gate*) lists **`Build and Deploy ACC Public Site`** among its
required status checks, alongside `audit`, `scan`, `build`,
`Build and Deploy ACC Frontend` and `Build and Deploy ACC PA Demo` — so a red
suite here now stops the pull request rather than merely reporting against it.
Read from `gh api repos/sgort/ronl-business-api/rulesets` on 20 September 2026.

!!! warning "This page said the opposite until 20 September 2026"
    It previously stated that the only required check on `acc` and `main` was
    `audit`, so "a red suite here has to be read rather than relied on to stop a
    pull request". That was true when written and is now false for `acc`. It
    remains true for `main`, deliberately: no production workflow has a
    `pull_request` trigger, so no production check could be required of a
    promotion. See
    [Overview → What actually gates a merge](overview.md#what-actually-gates-a-merge).

Since the per-file branch floor lives in `vite.config.ts`, this same `npm test`
step is also where coverage is enforced — the required check and the coverage
gate are one command.
