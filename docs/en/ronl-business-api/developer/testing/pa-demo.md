---
component: RONL Business API
---

# pa-demo suite

`packages/pa-demo`, Vitest with jsdom. **13 files · 68 tests · all passing ·
~5s**, plus a 9-test Playwright suite in ~6.3s.

!!! info "Figures on this page are measured, not estimated"
    Measured **25 August 2026** on branch `feat/public-pa-cockpit` at `a59a0a7`
    — pa-demo has not merged to `acc` yet, so these figures stand apart from
    the rest of this page's siblings, which remain dated 22 August 2026
    against `acc` @ `57ce4c2`. Rerun with:

    ```bash
    npm test --workspace=@ronl/pa-demo -- --reporter=json --outputFile=/tmp/pa-demo-tests.json
    npm run test:e2e --workspace=@ronl/pa-demo
    ```

pa-demo is `plato.open-regels.nl` — a public, unauthenticated, **mock-only**
showcase build of the PA Cockpit. It holds a byte-identical vendored copy of
`packages/frontend`'s cockpit (39 source files + 15 assets, kept in sync by a
drift checker — see below) plus demo-owned shims, an allow-list curating
Beheer down to nine sections, a role context, and a build that proves the
result never talks to a backend.

---

## Inventory

| Area | Files | Tests | Covers |
|---|---:|---:|---|
| `src/demo` | 6 | 36 | `DemoRoleContext` (7 — role switching writes the synthetic token, caps derivation for each of the four positions, StrictMode-safe); `DemoSectionRouter` (5 — routes `profiel`/`rollen` to the demo-owned pages, renders nothing for a dropped id, imports no `CaseworkerDashboard` component, re-renders on a role change rather than a stale mount-time snapshot); `modes.filtered` (9 — keeps exactly the nine Beheer sections, drops IOU and Gereedschap entirely, hides them from the command palette, resolves a dropped id to `null`); `Profiel` (6); `RollenRechten` (6); `demo-overrides` (3 — source-text guard on the CSS, see [The four no-Live layers](#the-four-no-live-layers)) |
| `src/demo/shims` | 2 | 8 | `keycloak` shim (5 — the synthetic user's two gating claims, role swap without disturbing `public-affairs`, never exposes a real token); `tenant` shim (3 — Flevoland theme applied via `setProperty`, matches the vendored `tenants.json` so the two cannot silently diverge) |
| `src/` (root) | 3 | 9 | `mock-lock.test.ts` (3), `staticwebapp-csp.test.ts` (4), `scaffold.test.ts` (2 — the injected `__APP_VERSION__` global and a sanity check that the suite runs in a DOM environment) |
| `scripts/` | 2 | 15 | `check-bundle.test.ts` (7), `check-drift.test.ts` (8) |

Coverage: **73.94% statements, 63.41% branches, 72.22% functions, 73.87%
lines** package-wide (`src/` 75.00/100/50.00/75.00, `src/demo`
76.08/61.53/95.45/76.19, `src/demo/shims` 65.21/100/33.33/65.21) — see
[Coverage](coverage.md#pa-demo-by-area).

### Coverage excludes `src/vendor/**`

`vite.config.ts`'s `coverage.exclude` drops `src/vendor/**` explicitly. Those
39 files are the **same files** already exercised by the frontend suite's
1155 tests — measuring them again here would double-count work done
elsewhere, and worse, would inflate pa-demo's own figures with someone else's
coverage and let demo-owned code (`src/demo/**`, `src/main-helpers.ts`,
`src/App.tsx`) hide behind a healthy-looking package total. Coverage on this
page is coverage of the ~13% of this package that pa-demo actually wrote.

---

## The four no-Live layers

plato issues no network requests at all — no App Service, no CORS entry, no
Keycloak client, no database. That guarantee is not one control but four
independent layers, each sufficient alone, and each has its own test:

| Layer | Mechanism | Asserted by |
|---|---|---|
| 1. Forced mock | Both legacy mock env vars are `true` (an absent `paV2.mock` key means mock by build-time default), and `main.tsx` writes `'1'` to `paV2.mock` before mounting so an inherited or stale key from another Open Regels app on the same origin cannot win | `src/mock-lock.test.ts` |
| 2. No toggle in the UI | `src/demo/demo-overrides.css` hides Dossierbeheer's vendored `toggleMock` button with a CSS override loaded after the vendored stylesheet (the reset button is deliberately spared, via a `:not()` on its own class) | `src/demo/demo-overrides.test.ts` (source-text guard) plus the E2E test `Dossierbeheer hides its own live toggle; only Reset demodata is offered` (the one that proves the CSS actually wins the cascade in a real browser) |
| 3. CSP | `public/staticwebapp.config.json` ships `connect-src 'self'` — no backend origin in any directive, unlike `public-site`, which lists its API origins because it genuinely calls them | `src/staticwebapp-csp.test.ts` |
| 4. Build-time bundle gate | `scripts/check-bundle.mjs` scans every built `.js` file for forbidden strings and fails the build if any are found | `scripts/check-bundle.test.ts` |

Layer 1 is a build-time default plus a boot-time write, not an absolute lock
against someone with devtools open — layers 3 and 4 are what make that
acceptable even so: even if a visitor forced `paV2.mock` to `'0'` by hand, the
CSP would refuse the resulting request and the bundle would not contain a
backend URL to request in the first place.

### Why the bundle gate's forbidden list differs from public-site's

`packages/public-site/scripts/check-bundle.mjs` fails on the bare string
`'keycloak'` anywhere in the bundle. Copying that list verbatim would fail
plato's build on **correct** code: `DB_ROLES` carries
`keycloak: 'pa-author' | 'pa-editor' | 'pa-admin'`, and `Dossierbeheer.tsx`
renders `· Keycloak: {role.keycloak}` as visible UI in the role bar — a
legitimate label, not a leaked credential. So plato's list targets the
**library and the origins** instead of the word: `keycloak-js`, `msal`,
`@azure/msal`, `oidc-client` (the other auth libraries), `react-ga`,
`google-analytics`, `gtag(` (telemetry), and `api.open-regels.nl` /
`acc.api.open-regels.nl` (the backend origins) — a stronger assertion than the
CSP, since an origin absent from the bundle cannot be requested at all,
regardless of what the CSP would otherwise allow.
`check-bundle.test.ts` asserts both directions: the forbidden list is
rejected, and the bare word `keycloak` — including the exact shape
`{keycloak:"pa-admin",label:"Beheerder"}` — is explicitly allowed.

---

## The drift checker

`scripts/check-drift.mjs` (exercised by `scripts/check-drift.test.ts`, 8
tests) compares every vendored file against its `packages/frontend` origin
and reports anything that no longer matches — `npm run vendor:check
--workspace=@ronl/pa-demo`.

The comparison reads both sides as raw `Buffer`s and compares with
`Buffer.equals()`, not as decoded UTF-8 strings. That is deliberate for the
15 binary PNG assets in the vendored tree: a lossy UTF-8 decode replaces any
invalid byte sequence with U+FFFD, so two **different** PNGs can decode to an
**identical** string once their differing bytes all collapse to the same
replacement character — which would silently defeat drift detection for
exactly the files most likely to need it. `check-drift.test.ts` proves this
directly: two five-byte buffers differing only in their last byte
(`0x...ff` vs `0x...fe`, neither a valid standalone UTF-8 sequence) are
correctly reported as changed.

The checker has its own workflow rather than living inside pa-demo's deploy
pipeline — see [CI](#ci) below — because drift is caused by edits to
`packages/frontend/**`, which never touch `packages/pa-demo/**` and so would
never trigger a path-filtered check placed there.

---

## Playwright suite

`e2e/plato-demo.spec.ts` (`npm run test:e2e --workspace=@ronl/pa-demo`),
Chromium only, `fullyParallel: true`. **9 tests, all passing, ~6.3s** (25
August 2026, `a59a0a7`):

- the landing view carries no disclaimer and offers no Live toggle
- the page has one scrollbar, not two
- Beheer shows nine sections and no IOU or Hulpmiddelen
- switching role on Rollen & rechten changes what Dossierbeheer permits
- an authored dossier appears immediately and does not survive a reload
- Dossierbeheer hides its own live toggle; only Reset demodata is offered
- Reset demodata clears an authored dossier without a full page reload
- the page issues no request to any backend
- Feiten & cijfers renders its monitor icons and issues no backend request

### The E2E suite needs no backend

Unlike every other Playwright suite in this repo, pa-demo's needs **nothing**
else running. The frontend suite needs Keycloak, Postgres, Redis and two
backends up first (see [E2E & live smoke](e2e.md#what-it-needs-running));
public-site's needs the real backend for its `/v1/public/*` data. plato talks
to neither — Playwright's own `webServer` (`npm run dev` on `:5176`) is the
entire environment, because plato itself makes no network request to
anything but its own origin. `E2E_BASE_URL` retargets the suite at
`acc.plato.open-regels.nl` / `plato.open-regels.nl` for post-deploy
verification, the same pattern as the other two suites.

---

## CI

Two Azure Static Web Apps workflows, `azure-pa-demo-acc.yml` (branch `acc` →
`acc.plato.open-regels.nl`) and `azure-pa-demo-prod.yml` (branch `main` →
`plato.open-regels.nl`), each path-filtered to `packages/pa-demo/**` and
`packages/shared/**`. Both gate, in order: lint → type-check → unit tests →
`vendor:check` → build (which itself runs the bundle gate) → deploy. A
failing step at any of those blocks the deploy.

A third workflow, `pa-demo-drift.yml`, is separate from both and
**deliberately non-blocking**. It triggers on `packages/frontend/src/**`
rather than on pa-demo's own path, runs `check-drift.mjs`, and writes a
GitHub annotation (`::notice` when clean, `::warning` when stale) rather than
failing the job — failing the build would turn an unrelated cockpit PR red
because a demo copy had drifted, training people to ignore the signal. The
`@ronl/pa-cockpit` extraction (tracked separately) is what resolves drift for
good; the annotation only has to keep it visible until then.
