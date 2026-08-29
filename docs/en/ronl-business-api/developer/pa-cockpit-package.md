---
component: RONL Business API
---

# PA-Cockpit package

`packages/pa-cockpit` (`@ronl/pa-cockpit`) is the Public Affairs cockpit as a
workspace package, imported by both the caseworker frontend and the public
demo. It exists so that one cockpit renders in two applications without either
one owning it.

!!! info "Measured against `acc`"
    87 source files, package version `1.0.0`, verified on `acc` at `1e7fb19`,
    29 August 2026.

---

## Why it is a package

The public demo was built first as a **byte-identical vendored copy** of the
cockpit — 44 files kept honest by a manifest, a sync script and a byte-level
drift checker. That was deliberate rather than expedient: an extraction has to
commit to an interface, and nothing outside `packages/frontend` had ever
consumed the cockpit. Building a real second consumer first made the boundary
empirical instead of imagined.

The measurement is what reframed the job. Those files left their own set through
exactly **five relative specifiers**, and those five were precisely the five
files the demo already overlaid with shims. The seam had already been
discovered by construction, so the extraction had something concrete to
formalise.

With the package in place, the fork, the manifest, the sync script, the drift
checker and the workflow that ran it were all deleted.

---

## The two kinds of seam

This is the load-bearing rule of the package, and the one most likely to be got
wrong when adding to it:

| Read at | Supplied through | Why |
|---|---|---|
| **Module scope**, by services | `configurePaCockpit({ auth, tenant })` | `services/pa.api.ts` and `services/dossierbeheer.api.ts` read them at module scope and cannot consume a React context |
| **Render time**, by components | the `host` prop on `PADashboardV2` | Module state feeding React components goes stale |

Putting the two non-React services behind a module-scope configuration call is
sound *specifically* because token lookup is not reactive: the value is read
when a request is made, not when something renders.

!!! danger "Do not move a render-time seam into `configurePaCockpit`"
    Module state feeding React components is what caused the role-context defect
    during the demo build: a mount-effect snapshot never saw later mutations, so
    the UI silently kept rendering a stale value. `onLogin` and `onLogout` are
    plain callbacks invoked from a click handler, so they ride the `host` prop
    even though neither is a section or a component.

---

## What a host must supply

```ts
configurePaCockpit({ auth, tenant });
```

**`PaCockpitAuth`** — the subset of the host's auth service the cockpit touches.
Not all of it mirrors keycloak-js:

| Member | Note |
|---|---|
| `authenticated: boolean` | **Required here**, while keycloak-js declares it optional. A host adapter passes `!!keycloak.authenticated` |
| `token: string \| undefined` | mirrors keycloak-js |
| `updateToken(minValidity?)` | mirrors keycloak-js |
| `getUser(): KeycloakUser \| null` | **not keycloak-js's at all** — the host's own function, deriving a user from `keycloak.tokenParsed` |

Ending a session is deliberately *not* part of this contract. A host that wants
a login or logout control wires it through the `onLogin` / `onLogout` callbacks
on the `host` prop, calling its own auth service directly.

**`PaCockpitTenant`** — theme initialisation and tenant config lookup. The only
field the cockpit reads from a tenant config is `displayName`, kept minimal on
purpose so each host can pass its own richer object unchanged; the frontend's
own `TenantConfig` carries theme, feature and contact blocks the cockpit has no
business knowing about.

Auth and tenant resolve through **configured getters inside functions**, so a
refreshed token is never captured by value and left stale.

If a host renders the cockpit without configuring it first, the package throws a
named error rather than failing obscurely later.

### The shell's host prop

`PADashboardV2` takes its host seams as a **required** prop, not an optional
one — so a host cannot silently omit a seam and discover it at runtime. It
carries the session callbacks and the components the shell renders but does not
own.

---

## `PaSectionsRouter`

`PADashboardV2` renders no section content itself. It unconditionally delegates
to a section router, so a host needs something to dispatch with.

Exporting the fourteen section components individually and asking every host to
hand-write the same id-group dispatch **was tried and reverted**. That grammar —
which ids belong to Monitoring, which to Voortgang, which remount — is package
knowledge, not host knowledge, and hand-maintaining it per host was exactly the
vendored fork's most-duplicated behaviour, merely formalised.

`PaSectionsRouter` is that grammar written once. A host composing its own router
checks its own ids first and places this component as the **unconditional tail**.

---

## The mode configuration

The shell groups work into four modes — **Vandaag**, **Dossiers**,
**Monitoring** and **Voortgang** — plus **Beheer**. Static sections live in
`modes.config.ts`; dossier rail items are **data-driven**, built from the
dossier list at render time, so adding a dossier never touches that file.

The rail and the command palette derive from the mode set **the host injects**,
rather than reading a module-level config. That is what lets the public demo
present a curated subset without the package knowing anything about curation.

The whole cockpit is gated on the `public-affairs` realm role and the `province`
org type at shell level; the per-item gates in the config are for future
fine-graining.

---

## What is deliberately not exported

The package surface was narrowed after a consumer audit, and the omissions are
intentional:

- **`allStaticSections` and `findPaModeForSection`** — both operate on the
  *unfiltered* mode list. Re-exporting them would hand a host a second,
  unguarded door onto the full section list, which is precisely what the demo's
  allow-list exists to prevent. A host that needs them gets them from
  `usePaModes()`, narrowed to the modes it supplied.
- **`isPaItemVisible` and the gate context** — real code, but package-internal.
  The shell builds the gate context and applies it when rendering the rail, so a
  host never sees an un-gated rail item and has nothing to call these on.
- **`OrgTypeGate`** — zero consumers of this copy. The frontend appears to use
  it but imports a character-identical union its own caseworker config declares.
  Exporting it advertised a shared vocabulary that nothing shares.

Two exports have only a test as their consumer, recorded so a future audit does
not read them as dead: `getPaCockpitAuth` and `getPaCockpitTenant` are read back
by the frontend's host test, and `SORT_SECTION_IDS` by the demo's allow-list
test. Both are the read side of something a host writes — a host that could not
read its own wiring back could not test it.

---

## Styling

The package ships `@ronl/pa-cockpit/styles.css` with scoped `pac-*` rules rather
than Tailwind utilities. Where the notifications panel was converted, the values
used are the literal Tailwind-computed values rather than the nearest design
token, so the rendered result stays pixel-identical.

**The demo never imports the caseworker stylesheet.** Every class a
package-owned component renders must therefore also have a rule in the package's
own sheet, or the demo renders unstyled. That duplication is required rather
than decay, and a guard fails the build when the two sheets diverge — see
[Testing](testing/dashboards/pa-cockpit.md).

---

## Related

- [PA-Cockpit demo](../user-guide/pa-demo.md) — the public consumer
- [PA cockpit — tests](testing/dashboards/pa-cockpit.md) — the suite that moved
  with the code
- [Shared Package](shared-package.md) — the other workspace package
- [Frontend Development](frontend-development.md) — the host application
