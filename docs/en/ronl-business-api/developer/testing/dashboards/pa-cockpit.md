---
component: RONL Business API
---

# PA cockpit — tests

The Public Affairs cockpit is the most heavily tested surface in the product,
and the only board with its own end-to-end suite.

!!! info "These tests moved into a package"
    As of v2026.08.27 the cockpit lives in
    [`@ronl/pa-cockpit`](../../pa-cockpit-package.md), and its tests travelled
    with it — they are no longer part of the `packages/frontend` suite. That is
    why the frontend's own totals fell between v2026.08.23 and v2026.08.33
    without anything being deleted.

**Package: 43 files · 516 tests.** **Backend: 15 files · 551 tests** in
`src/pa-monitoring` — since v2026.10.1 the third-largest area in the backend,
after `src/routes` and `src/services`. **E2E: 2 specs · 7 tests**, still in
the frontend package, carried forward from 14 November.

Measured serially, with coverage and without file parallelism, on
**18 November 2026** at `be0a1f0`, a tree identical to `main` at `1784a72`
(v2026.11.5 plus hot fix #473): **516 of 516 passing**, `Duration 127.69s`.
v2026.11.5 added one test, in `BronnenSection.test.tsx` (7 → **8**: a disabled
flag shows as *uitgeschakeld*), and changed `BronnenSection.tsx`,
`services/pa.api.ts` and an assertion in `services/pa.api.test.ts` when the
EP scrape's flag went (#57). The package's four coverage figures
reproduced; one area row moved by two hundredths, `src/services` lines
95.28 → 95.26.

Before that, measured serially, with coverage and without file parallelism, on
**14 November 2026** for v2026.11.3 (`main` at `f54e4f0`), in the working
checkout at `6f86b10`, a tree identical to `f54e4f0`:
**515 of 515 passing**, `Duration 74.79s` (102.79s on 12 November, 116.83s on
7 November, 136.61s on 9 October, 133.53s on 3 October, 35.32s in the
parallel run of 30 September). Every count and percentage reproduced the
12 November figures exactly; v2026.11.3 changed only the package's version.
Re-run the same day for v2026.11.4 (`acc` at `4579486`, a tree identical to
`main` at `67bac28`), every count and percentage held again: v2026.11.4 did
not touch this package.
v2026.11.2 changed one assertion and no count: `pages/PADashboardV2.test.tsx`
finds the ⌘K button by its visible text, *Spring naar een dossier of
sectie…*, now that the button has no `aria-label` (WCAG 2.5.3); its
development dependencies moved to vite ^6.4.5 and vitest ^4.1.12. Every count
and percentage reproduced the 7 November figures exactly. v2026.11.0 moved the
package's colours onto the shared tokens and its shared chrome into
`packages/shared/styles/v2-chrome.css`; no test changed, and every count and
percentage reproduced the 9 and 11 October figures exactly. Coverage **92.61 % statements · 93.89 % branches ·
89.57 % functions · 93.13 % lines** — branches up 18.34
points from v2026.08.36 under the per-file 80% floor adopted in v2026.09.2,
which v2026.09.6 wrote into this package's `vitest.config.ts` as
`thresholds: { branches: 80, perFile: true }`. The run passed it without naming
a file, and no file is below 85% either: the lowest is
`services/dossierbeheer.api.ts` at 85.10%.

!!! note "Six releases of identical counts, then +39 tests, then one more"
    43 files and 476 tests at v2026.09.7, v2026.09.9, v2026.09.11, v2026.09.12
    and v2026.09.13 — **43 files and 515 tests** at v2026.09.15 and every
    release through v2026.11.4 — and **516** at v2026.11.5. Every one
    of the 39 is from the two branch-margin commits: `391b1a8` (#256) added four
    to `DossierRow.test.tsx`, taking a file that sat at exactly 80.00% branches
    to 100 and exposing a latent crash when a dossier had no `kompas`, fixed in
    the same commit; `73a6764` added 35 across six files, `Monitoring.test.tsx`
    (+16) and `services/pa.api.test.ts` (+13) above all.

    **The package's percentages had wobbled in the second decimal while
    nothing changed.** Across v2026.09.12 and v2026.09.13 — no `src/` change and
    no test change — branches and lines read **88.52** and **91.33** on every
    pass, while statements and functions alternated between 90.11 / 86.52 and
    90.07 / 86.39 on identical code. That is the second-decimal warning on
    [Coverage](../coverage.md) in its cleanest form, and it is why the moves of
    two to five points on 30 September are worth reporting and a move in the
    second decimal is not.

    This package holds **7 of the 23 files** an 80% *functions* floor would
    fail — the second-largest share after the frontend — while **none** of its
    38 source files is below the 80% *branch* floor that is actually
    configured.

!!! warning "Until v2026.09.6, this package's tests ran nowhere in CI"
    `@ronl/pa-cockpit` is a library: it has no deploy workflow of its own, and
    no other workflow ran its suite. The most heavily tested surface in the
    product was therefore covered on developer machines and nowhere else, while
    every deployable package had had a pipeline running its tests since
    20 August. Both frontend workflows now run it, as a step placed **before**
    the frontend's own — the frontend imports the package, so there is no point
    testing the consumer while the library is broken. The pa-demo workflows
    consume it too and watch `packages/pa-cockpit/**` in their path filters,
    but run only pa-demo's own suite.

!!! note "Which figures are from which date"
    The package counts and coverage and the `src/pa-monitoring` backend figure
    (15 files, 551 tests) were measured on **18 November 2026**. The two E2E
    specs were **not re-run**: their figures are carried forward from
    **14 November 2026**, when they ran against the developer's
    already-running local stack, as on 3 and 9 October and 7 November. See
    [E2E & live smoke](../e2e.md).

---

## The package suite

Read on **18 November 2026** from Vitest's JSON report of the measured run:
every file with eight tests or more. All the package's files sum to exactly the
runner's **516**. The counts are the same as those derived from the source on
9 October at `ebec288`, but for `BronnenSection.test.tsx`, which then held
seven and so fell below this table.

| File | Tests | Covers |
|---|---:|---|
| `services/pa.api.test.ts` | 90 | The cockpit's API client — the single largest test file in the package |
| `pages/public-affairs-v2/Monitoring.test.tsx` | 51 | Monitoring view (35 on 28 September) |
| `pages/PADashboardV2.test.tsx` | 27 | The page container and the host contract it requires |
| `pages/public-affairs-v2/PaDataProvider.test.tsx` | 24 | The context every cockpit screen consumes |
| `pages/public-affairs-v2/Issuekaart.test.tsx` | 24 | The issue map |
| `components/PADashboardV2/ZoekcriteriaSection.test.tsx` | 22 | Saved-search criteria |
| `pages/public-affairs-v2/Kompas.test.tsx` + `kompas.test.ts` | 21 | The kompas view and its pure data module |
| `pages/public-affairs-v2/NotificationsPanel.test.tsx` | 19 | Previously 0% — notifications were hardcoded to empty |
| `services/dossierbeheer.api.test.ts` | 17 | The dossier API client |
| `components/PADashboardV2/dossierbeheer/Dossierbeheer.test.tsx` | 17 | Dossier list, filters, status transitions |
| `pages/public-affairs-v2/dossierbeheer.data.test.ts` | 16 | The dossier data module |
| `pages/public-affairs-v2/AgendaView.test.tsx` | 16 | The agenda |
| `components/PADashboardV2/PaSectionsRouter.test.tsx` | 15 | The section-id grammar that replaced a fourteen-export surface |
| `components/PADashboardV2/dossierbeheer/DossierEditor.test.tsx` | 14 | Authoring a dossier |
| `components/PADashboardV2/dossierbeheer/DossierRow.test.tsx` | 12 | Row rendering and actions (8 on 28 September) |
| `components/PADashboardV2/dossierbeheer/MdEditor.test.tsx` | 11 | The Markdown editor |
| `services/mock-demo.store.test.ts` | 11 | The mock store both hosts drive |
| `components/PADashboardV2/PACommandPalette.test.tsx` | 11 | The ⌘K palette |
| `pages/public-affairs-v2/Vandaag.test.tsx` | 8 | The 30-second start screen |
| `pages/public-affairs-v2/FeitenCijfers.test.tsx` | 8 | Facts and figures |
| `pages/public-affairs-v2/modes.gate.test.ts` | 8 | The per-item rail gate — authentication, role and organisation type — which no shipped item uses yet |
| `components/PADashboardV2/BronnenSection.test.tsx` | 8 | The source list; since v2026.11.5 a disabled flag shows as *uitgeschakeld* (7 on 14 November) |

By directory: `pages/public-affairs-v2` **203**, `services` **118**,
`components/PADashboardV2/dossierbeheer` **74**, `components/PADashboardV2`
**74**, `pages` **27**, package root **10**, `modes` **7**, `test` **3**.

### The guards that came with the extraction

Seven of the smallest files are not feature tests at all — they are structural
guards protecting the package boundary, and they matter out of proportion to
their test counts:

| File | Tests | Guards |
|---|---:|---|
| `host.test.ts` | 3 | That a host must configure the package before render, and fails with a named error if it does not |
| `index.test.ts` | 2 | The public surface — so a re-export added by accident is caught |
| `modes/no-module-scope-modes.test.ts` | 2 | That the unfiltered mode helpers stay unreachable, which is what keeps the demo's curation honest |
| `no-tailwind.test.ts` | 1 | That no Tailwind utility class returns to the package |
| `no-host-protocol.test.ts` | 1 | That no host session-storage key, IdP literal or router path is hardcoded back in |

The last one is the residue of a real defect class. The package had previously
hardcoded five facts belonging to a host application; the guard exists so the
seam cannot silently close again.

!!! warning "Two of these guards were themselves defective when written"
    The modes guard matched raw text, so a single line of documentation-shaped
    string could disarm the only rule covering dynamic imports — and a decoy
    function declared in an inner scope disarmed it for a whole file while
    compiling with zero type and lint errors. It now parses the source, and its
    accusing and excusing inputs are split so one can no longer feed the other.
    A guard is code, and needs its own red/green like anything else.

## Backend

`src/pa-monitoring` — **551 tests across 15 files**, from the backend run's own
JSON output on 18 November 2026. v2026.11.5 removed the European Parliament
scrape and its flag (#57): `sources/ep-texts-submitted.client.test.ts` (24)
went, and `curation.service.test.ts` fell 61 → **53** with its routing cases,
from the 583 across 16 files that had held since 30 September:

| File | Tests |
|---|---:|
| `pa.routes.test.ts` | 133 |
| `pa-dossiers.routes.test.ts` | 96 |
| `curation.service.test.ts` | 53 |
| `rules.test.ts` | 38 (pure scoring) |
| `pa-dossiers.db.test.ts` | 30 |
| `pa-cache.test.ts` | 23 |
| `pa-monitoring.db.test.ts` | 10 |
| `notifications.service.test.ts` | 8 |
| `query-match.test.ts` | 6 |
| `rss.test.ts` | 4 |

Plus 150 tests in the five source clients under `pa-monitoring/sources`: EU
(73), media (27), TK (21), OB (19) and agenda (10).
Coverage on 18 November (statements / branches): `pa-monitoring`
**99.04 / 89.01** and `pa-monitoring/sources` **98.34 / 93.27**, against
98.95 / 89.35 and 98.13 / 93.05 from 30 September to 14 November;
`pa-monitoring`'s lines moved 99.16 → 98.99 when `pa.routes.ts`
and `pa-dossiers.routes.ts` began answering problems, and read 99.08 now.

---

## E2E

Two Playwright specs, run with the same `playwright.config.ts` as the rest of
the frontend suite.

**Last measured 14 November 2026, and not re-run on 18 November: 7 tests, all passing**, as part of the full
frontend run against the developer's already-running local stack (60 passed,
7 skipped, 3.9m) — the five mock-mode tests in 2.0–3.0s each and the two
live-authoring tests in 4.8s and 2.9s. On 7 November: 7 passing, mock mode
in 4.8–8.3s and live authoring in 7.4s and 6.4s. On 9 October: 7 passing, mock mode in
2.2–3.3s and live authoring in 4.7s and 3.3s. On 3 October: 7 passing, mock mode in
2.4–4.5s and live authoring in 6.9s and 4.7s. Before that, 30 August 2026 against
`acc` at `15dfbf9`: 7 passing, in a run of 27 in 1.9m. The count is unchanged
since 22 August, when the two together ran in 18.9s and the live spec was
additionally run six consecutive times while chasing a flake, passing 2/2 each
time in 7.3–11.7s.

See [Coverage per board](../e2e.md#coverage-per-board) for how these seven sit
against the other sixty. Since v2026.11.0 `accessibility.spec.ts` also
scans the PA-Cockpit dashboard with axe-core (one test, passing on
7 and 14 November); its first run against ACC found the score total (`.pac-total b`)
at 4.23:1 contrast, now 6.13:1.

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
