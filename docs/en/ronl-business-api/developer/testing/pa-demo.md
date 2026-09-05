---
component: RONL Business API
---

# PA-demo suite

`packages/pa-demo` — the public, mock-only [PA-Cockpit demo](../../user-guide/pa-demo.md).
Vitest + jsdom, plus a Playwright suite that is the only one in this repository
wired into CI.

!!! info "Figures on this page are measured, not estimated"
    **19 files · 106 tests, all passing**, measured with
    `npm run test:serial --workspace=@ronl/pa-demo` on 5 September 2026 against
    `acc` at `66940d9` (v2026.09.5). Coverage **93.47 % statements ·
    95.65 % branches · 85.00 % functions · 92.85 % lines** — branches up
    8.70 points from v2026.08.33 under the per-file 80% floor adopted in
    v2026.09.2.

**At a glance:**

| | |
|---|---|
| Runner | Vitest 4 + jsdom, coverage via v8 |
| Files / tests | 19 / 104 |
| Wall time | ~27 s serial |
| Playwright | 11 tests in `e2e/plato-demo.spec.ts`, **runs in CI** |

---

## Why this suite is shaped the way it is

Nearly every guarantee the demo makes is a **negative** assertion:

- no backend origin in the Content-Security-Policy
- no auth library or API URL in the built bundle
- no dropped section reachable from the rail or the command palette
- no inherited storage key able to flip the demo out of mock mode

Negative assertions are exactly the ones that pass vacuously when wrong. A test
asserting *the absence* of something is green both when the guard works and when
the test is looking in the wrong place. That shaped the plan the demo was built
from: five of its twelve steps write no production code at all, and instead name
the thing to break, the failure message to expect, and the restore.

That discipline caught real holes, twice over:

- **The mock-lock test only ever proved the test environment file.** Vitest's
  mode is always `test`, so nothing read the production or acceptance
  environment files. Deleting a mock flag from either would have left every
  check green. `env-files.test.ts` now asserts across **all four** environment
  files that the three mock flags are true and the API URL absent — verified red
  by deleting a flag from the production file and confirming the failure names
  that file and that flag.
- **The network-isolation guard compared hostnames only**, so it could not catch
  a same-origin backend-shaped request — which is exactly what the agenda fetch
  issues when the API URL is unset, since the resulting path resolves relative
  to the demo's own origin.

---

## Test inventory

### The no-Live guarantees

| File | Covers |
|---|---|
| `src/staticwebapp-csp.test.ts` | The shipped CSP really carries `connect-src 'self'` |
| `scripts/check-bundle.test.ts` | The build-time bundle gate — its forbidden list, and that it fails rather than warns |
| `src/mock-lock.test.ts` | Mock mode is written before mount, so an inherited flag from another Open Regels app on the same origin cannot win |
| `src/env-files.test.ts` | All four environment files, not just the one the runner happens to load |

The bundle gate's forbidden list is **adapted from the public site's rather than
copied**: it targets the auth library and the two backend origins, not the bare
product name, which this bundle ships legitimately in its role tables and its
visible role bar. The first real build caught a genuine finding.

!!! warning "The gate silently no-opped on Windows until v2026.08.28"
    Both bundle-check scripts guarded their entry point by comparing a module
    URL against the process argument. On Windows that argument is a
    drive-letter path with backslashes, so the comparison never held: the gate
    exited zero having checked nothing, and the build passed. Both scripts run
    as the last step of every build for two public, unauthenticated sites. On
    Windows, none of it had ever been checked.

### Section curation

| File | Covers |
|---|---|
| `src/demo/allowed-modes.test.ts` | The deny-by-default allow-list — 21 static ids plus the dossiers sentinel, reconciled one-to-one against the real mode config's 26 rail items |
| `src/demo/DemoSectionRouter.test.tsx` | Dropped and unmatched ids render nothing rather than falling through to a placeholder |

!!! note "Deny-by-default is only deny-by-default while both lists stay exhaustive"
    A section added to the cockpit later and named in neither list is filtered
    out of the rail and the palette — which looks exactly like the policy
    working, rather than like a gap. That is the failure mode to watch for when
    the cockpit grows.

### Roles and the host adapter

| File | Covers |
|---|---|
| `src/demo/DemoRoleContext.test.tsx` | Role state, including a StrictMode double-invocation regression |
| `src/demo/RollenRechten.test.tsx` | The role selector and the capability table |
| `src/demo/pa-cockpit-host.test.ts` · `.auth.test.ts` | The host adapter, pinned against the frontend's equivalent |
| `src/demo/shims/keycloak.test.ts` · `tenant.test.ts` | The synthetic auth and tenant shims |
| `src/demo/Profiel.test.tsx` | That the tenant row names the right *kind* of organisation |

The host adapter test **pins the two places the demo's adapter correctly differs
from the frontend's**, rather than asserting a false equivalence. The Profiel
test overrides the shim to a municipality tenant for one render and confirms the
label follows, so the coverage is not merely correct by coincidence for the
single tenant the shim ships.

### Presentation and build

| File | Covers |
|---|---|
| `src/brand-colours.test.ts` | The five brand colours across all four files that declare them |
| `src/demo/demo-overrides.test.ts` | The override rules, including the suppressed live toggle |
| `src/demo/changelog/*.test.*` | The demo's own changelog panel and data |
| `scripts/social-card-origin.test.ts` | The build plugin rewrites the card's absolute URLs per origin |
| `src/scaffold.test.ts` | Package wiring |

Both the brand-colour and class-coverage guards **strip CSS comments before
matching**. Without that, a colour or class named only inside a comment would
count as defined — and a later task in the same plan added prose comments naming
real selectors, which would have opened exactly that hole.

---

## The Playwright suite

`packages/pa-demo/e2e/plato-demo.spec.ts` — **11 tests**, Chromium only.

This is the one Playwright suite in the repository that **runs in CI**, as a
blocking step of `azure-pa-demo-acc.yml`, before the build. It is the only proof
of two of the four no-Live layers: that the live toggle is actually hidden in a
real browser's cascade, and that the page issues no network request at all. A
source-text assertion that the suppressing CSS rule exists cannot show either.

It needs no backend, database or Keycloak. Playwright starts its own dev server
and that is the whole environment — which is why this suite could be wired into
CI when the frontend's, needing a five-service stack, could not.

```bash
npm run test:e2e --workspace=@ronl/pa-demo

# against a deployed environment instead of a local dev server
E2E_BASE_URL=https://acc.plato.open-regels.nl \
  npm run test:e2e --workspace=@ronl/pa-demo
```

Two assertions carry the weight: that switching role actually changes what
Dossierbeheer permits, and that the page issues no request to any backend —
the latter proven load-bearing by a red probe with the agenda mock disabled.

!!! tip "Selectors were read off the running app, not taken from the brief"
    The task brief held several wrong assumptions: rail items are buttons rather
    than links, two expected test ids do not exist, and a created dossier
    survives in-app navigation but not a reload. Read the app.

!!! warning "A guard that hardcodes localhost fails against a real deployment"
    The backend-request guard originally treated localhost as the only
    same-origin host, which is correct only when Playwright serves the app
    itself. Run against a live deployment, the app's own document, bundle and
    stylesheet became off-host by that check, producing two false failures. It
    now compares against the configured base URL's own origin and fails loudly
    if that is missing, rather than silently reverting to the old assumption.

---

## Coverage

| Area | Stmts | Branch | Funcs | Lines |
|---|---:|---:|---:|---:|
| **All files** | **93.47** | **95.65** | **85.00** | **92.85** |
| `src/demo` | 95.91 | 84.61 | 100 | 97.72 |
| `src/demo/changelog` | 100 | 87.50 | 100 | 100 |
| `src/demo/shims` | 75.00 | 100 | 44.44 | 75.00 |
| `src` | 75.00 | 100 | 50.00 | 75.00 |

The uncovered remainder is almost entirely **shims that deliberately return
nothing**: the dock stand-in and the session-expiry warning both render `null`
by design, because the real components pull in chat machinery and session
handling that a public page must not have. They depress the function percentage
without representing a gap.

---

## Related

- [PA-Cockpit demo](../../user-guide/pa-demo.md) — the user-facing guide
- [PA-Cockpit package](../pa-cockpit-package.md) — the package the demo consumes
- [PA cockpit — tests](dashboards/pa-cockpit.md) — the cockpit's own suite
- [E2E & live smoke](e2e.md) — the other Playwright suites
