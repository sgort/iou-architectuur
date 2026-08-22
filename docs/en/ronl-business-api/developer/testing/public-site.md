---
component: RONL Business API
---

# Public site suite

`packages/public-site`, Vitest with jsdom. **28 files · 134 tests · all
passing · ~12s.**

The public site is the auth-free search and rule-catalogue package. Nothing
under `packages/public-site/src/` changed between v2026.08.20 and v2026.08.23,
so every figure here reproduced the earlier measurement exactly.

---

## Inventory

| Area | Files | Tests | Covers |
|---|---:|---:|---|
| `src/pages` | 14 | 71 | Includes a full `herkomst/` provenance-explorer sub-area (`HerkomstExplorer`, `HerkomstTrace`, `HerkomstChip`, `HerkomstBackground`, `herkomstConcepts`, `herkomstData`, `herkomstTrail` — 7 files, 39 tests) plus the generic `SectionIndex` / `Regelcatalogus` / `Results` / `Detail` / `Woordenboek` / static pages |
| `src/lib` | 6 | 26 | `slug` (kept identical to the backend's slugifier by design), `useQueryState` (URL-backed filters), `search` (`highlight()`), `api` (the typed `/v1/public/*` client), `sectionHits` (`mapToHits()`), `prerenderedData` (the seeded-render reader) |
| `scripts/` | 2 | 15 | `prerender.test.ts` (11 — `escapeHtml`, `buildSitemap`, `injectIntoShell`), `check-bundle.test.ts` (4 — the build-time gate that fails if any auth or telemetry string ships in the bundle) |
| `src/components` | 3 | 13 | Presentational chrome, `Footer`, `TechDetails` |
| `src/App.test.tsx` | 1 | 5 | Routing shell — every route registered, `<html lang>` synced to the language switch |
| `src/i18n` | 1 | 3 | NL/EN dictionary key parity |
| `src/staticwebapp-csp.test.ts` | 1 | 1 | Guards the shipped CSP header — a regression here silently breaks the org-logo host |

Coverage: `src/components` 96.77%, `src/lib` 84.9%, `src/pages` 82% — see
[Coverage](coverage.md#public-site-by-area).

This package has the widest statement-to-branch gap of the three, at 16.4
points (86.82% → 70.39%), and it has not moved because nothing here changed.

---

## Playwright suite

`packages/public-site/e2e/publiek.spec.ts`
(`npm run test:e2e --workspace=@ronl/public-site`) against real
`/v1/public/*` data with no mocks — search → filter → detail → back with URL
preservation, a deep link with pre-applied filters, keyboard-only navigation,
and three axe-core accessibility scans (home, results, a detail page) asserting
no critical or serious violations.

!!! warning "These figures were not re-measured for v2026.08.23"
    **Measured 19 August 2026 against v2026.08.19: 6 tests, 6 passed, 0 failed,
    0 flaky, 0 skipped, 8.9s.**

    Nothing under `packages/public-site/src/` changed between that release and
    this one, so the suite is expected to be unaffected — but it was not re-run
    to confirm, and this is the only figure on these pages carrying an older
    date than the rest.

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
