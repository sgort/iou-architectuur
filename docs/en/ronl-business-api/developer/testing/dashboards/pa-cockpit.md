---
component: RONL Business API
---

# PA cockpit — tests

The Public Affairs cockpit is the most heavily tested surface in the product,
and the only board with its own end-to-end suite.

**Frontend: 31 files · 258 tests.** **Backend: 16 files · 533 tests** in
`src/pa-monitoring` — the largest single area in the repository.
**E2E: 2 specs · 7 tests.**

---

## Frontend

| File | Tests | Covers |
|---|---:|---|
| `pages/public-affairs-v2/PaDataProvider.test.tsx` | 21 | The context every cockpit screen consumes |
| `components/PADashboardV2/PASectionRouter.test.tsx` | 19 | Section routing and the shell's own state machine |
| `pages/public-affairs-v2/NotificationsPanel.test.tsx` | 19 | Previously 0% — notifications were hardcoded to empty |
| `components/PADashboardV2/dossierbeheer/Dossierbeheer.test.tsx` | 17 | Dossier list, filters, status transitions |
| `components/PADashboardV2/dossierbeheer/DossierEditor.test.tsx` | 14 | Authoring a dossier |
| `pages/public-affairs-v2/Issuekaart.test.tsx` | 14 | The issue map |
| `pages/public-affairs-v2/Monitoring.test.tsx` | 14 | Monitoring view |
| `pages/public-affairs-v2/Kompas.test.tsx` + `kompas.test.ts` | 20 | The kompas view and its pure data module |
| `components/PADashboardV2/ZoekcriteriaSection.test.tsx` | 9 | Saved-search criteria |
| `components/PADashboardV2/dossierbeheer/MdEditor.test.tsx` | 9 | The Markdown editor |
| `pages/PADashboardV2.test.tsx` | 9 | The page container |
| `components/PADashboardV2/dossierbeheer/DossierRow.test.tsx` | 8 | Row rendering and actions |
| `pages/public-affairs-v2/FeitenCijfers.test.tsx` | 8 | Facts and figures |

Coverage: `src/pages/public-affairs-v2` **86.67%** statements (up from 67.83%),
`src/components/PADashboardV2` 84.77%, `…/dossierbeheer` 81.35%.

## Backend

`src/pa-monitoring` — 533 tests across 16 files:

| File | Tests |
|---|---:|
| `pa.routes.test.ts` | 131 |
| `pa-dossiers.routes.test.ts` | 96 |
| `curation.service.test.ts` | 61 |
| `rules.test.ts` | 38 (pure scoring) |
| `pa-dossiers.db.test.ts` | 30 |
| `pa-monitoring.db.test.ts` | 10 |
| `pa-cache.test.ts` | 9 |
| `notifications.service.test.ts` | 8 |
| `query-match.test.ts` | 6 |
| `rss.test.ts` | 4 |

Plus the TK, OB, EU, agenda and media source clients under
`pa-monitoring/sources`. Coverage: `pa-monitoring` 98.32%,
`pa-monitoring/sources` 97.07%.

---

## E2E

Two Playwright specs, run with the same `playwright.config.ts` as the rest of
the frontend suite.

**Measured 22 August 2026: 7 tests, 7 passed, 0 failed, 0 flaky, 0 skipped,
18.9s** for the two together. The live spec was additionally run six
consecutive times while chasing a flake, passing 2/2 each time in 7.3–11.7s.

| Spec | Tests | Covers |
|---|---:|---|
| `pa-mock-journey.spec.ts` | 5 | Mock mode driven against the real store with no mocking: curating moves the rail badges and the move survives a reload; an ignored signal stays ignored; Reset demodata restores every source to its fixture baseline; the reset control is offered in mock mode only; every signaalbron carries a watchlist orphan that can be linked to a dossier |
| `pa-live-authoring.spec.ts` | 2 | Authoring against the live backend and a real database — a dossier and a zoekcriterium survive a genuine cold reload; live shows authored work while mock shows fixtures, from the same screen |

### Why mock mode is worth an E2E suite

Every mock-mode defect found by hand in this window was invisible to the unit
suites *by construction*. They were not logic errors — a saved-search write that
was a bare `return;`, a confirm that built a new object and discarded it,
notifications hardcoded to empty, a resource fetched once at mount and never
again. Component tests mock the very seam that was broken, so they cannot see
any of it, and each one passed throughout.

Mock mode makes an unmocked end-to-end run affordable: the fixtures are
deterministic and nothing depends on what happens to be in the database.

### Why the live spec only covers authoring

Curation depends on TK OData, the EU RSS feed and the media aggregator, and TK
alone measured 10s and 48s for the same query minutes apart — an assertion about
signals arriving would be flaky by construction.

The live spec creates everything with a run-unique stamp and removes it again in
`afterEach`, including when the test fails part-way. Nothing global is reset:
`pa:reset-data` is a feature of the product, not test tooling.

!!! note "Three lessons came out of building this suite"
    A throttled run that looks exactly like an outage, `locator.count()` not
    auto-waiting, and a hand-written mock that passed vacuously. All three are
    written up on [Writing tests](../writing-tests.md), because they generalise
    well beyond this board.
