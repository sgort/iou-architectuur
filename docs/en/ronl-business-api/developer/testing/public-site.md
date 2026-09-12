---
component: RONL Business API
---

# Public site suite

`packages/public-site`, Vitest with jsdom. **31 files · 225 tests · all
passing · 24.89s.**

The public site is the auth-free search and rule-catalogue package. Measured on
**12 September 2026** on `main` at `311d732` (v2026.09.7) with
`npm test --workspace=@ronl/public-site`, coverage included. The suite has
grown since v2026.09.5 — 30 files and 204 tests then, 31 and 225 now — the
added file being `src/lib/buildInfo.test.ts`.

Coverage is **95.79% statements · 96.41% branches · 94.87% functions · 96.28%
lines**, and the package passes the per-file 80% branch floor that its
`vite.config.ts` now enforces rather than merely recording.

---

## Inventory

| Area | Files | Tests | Covers |
|---|---:|---:|---|
| `src/pages` | 16 | 71 | Includes a full `herkomst/` provenance-explorer sub-area (`HerkomstExplorer`, `HerkomstTrace`, `HerkomstChip`, `HerkomstBackground`, `herkomstConcepts`, `herkomstData`, `herkomstScroll`, `herkomstTrail` — 8 files) plus the generic `SectionIndex` / `Regelcatalogus` / `Results` / `Detail` / `Woordenboek` / static pages |
| `src/lib` | 7 | 26 | `slug` (kept identical to the backend's slugifier by design), `useQueryState` (URL-backed filters), `search` (`highlight()`), `api` (the typed `/v1/public/*` client), `sectionHits` (`mapToHits()`), `prerenderedData` (the seeded-render reader), `buildInfo` (new in v2026.09.6) |
| `scripts/` | 2 | 15 | `prerender.test.ts` (11 — `escapeHtml`, `buildSitemap`, `injectIntoShell`), `check-bundle.test.ts` (4 — the build-time gate that fails if any auth or telemetry string ships in the bundle) |
| `src/components` | 3 | 13 | Presentational chrome, `Footer`, `TechDetails` |
| `src/App.test.tsx` | 1 | 5 | Routing shell — every route registered, `<html lang>` synced to the language switch |
| `src/i18n` | 1 | 3 | NL/EN dictionary key parity |
| `src/staticwebapp-csp.test.ts` | 1 | 1 | Guards the shipped CSP header — a regression here silently breaks the org-logo host |

!!! note "File counts are current; the test counts beside them are not"
    The Files column was re-derived from the tree at `311d732` on 12 September
    2026 and accounts for all 31 files. The Tests column dates from the
    19 August split, sums to 134 against today's 225, and was not
    re-generated — read it as showing where the weight sits rather than as a
    current count.

Per-area coverage was last derived on 22 August 2026 — `src/components` 96.77%,
`src/lib` 84.9%, `src/pages` 82% — and was not re-generated in this pass
either; see [Coverage](coverage.md#public-site-by-area).

The statement-to-branch gap this package was once known for is gone. It was the
widest of the five at 16.4 points, 86.82% statements against 70.39% branches.
Today branches sit **above** statements — 96.41% against 95.79% — which is
what a campaign against a per-file *branch* floor looks like once it lands.

---

## Playwright suite

`packages/public-site/e2e/publiek.spec.ts`
(`npm run test:e2e --workspace=@ronl/public-site`) against real
`/v1/public/*` data with no mocks — search → filter → detail → back with URL
preservation, a deep link with pre-applied filters, keyboard-only navigation,
and three axe-core accessibility scans (home, results, a detail page) asserting
no critical or serious violations.

!!! warning "These figures date from 19 August and were not re-run for v2026.09.7"
    **Measured 19 August 2026 against v2026.08.19: 6 tests, 6 passed, 0 failed,
    0 flaky, 0 skipped, 8.9s.**

    They were not re-measured on 12 September 2026, and this time the package
    *has* changed underneath them, so take the six as an inventory figure
    rather than as a result. What was re-checked is the inventory itself:
    `e2e/publiek.spec.ts` is still the one spec, and it still runs in no
    workflow. These remain the oldest figures on these pages.

Unlike the frontend suite, Playwright starts its own dev server for this package
(`webServer` in `playwright.config.ts`) — only the backend needs to already be
running. Setting `E2E_BASE_URL` points the suite at an already-deployed site
instead, which is how it is used for post-deploy verification against ACC.

---

## CI

Public-site is the package that had a real CI test gate before the others did.
Both `azure-publicsite-acc.yml` and `-prod.yml` run `npm run lint`,
`npm run type-check`, then `npm test` before building, and the build itself
gates on a prerender step and a bundle-cleanliness check. A failing test blocks
the deploy.

It blocks the deploy, not the merge: the only required status check on `acc`
and `main` is `audit`, so a red suite here has to be read rather than relied on
to stop a pull request. Since the per-file branch floor lives in
`vite.config.ts`, this same `npm test` step is also where coverage is enforced.
