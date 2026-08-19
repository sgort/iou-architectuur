---
component: RONL Business API
---

# Public Publication

A **public publication** surface makes information reachable by anyone, with none of the machinery a signed-in surface needs: no login, no account, and no personal data collected or shown. It publishes the same underlying information an authenticated surface draws on, read-only, to an audience that is never asked to identify itself.

---

## What makes it distinct

Nothing on a public surface depends on who is asking. There is no sign-in step to pass, no session to hold, and no per-person view to compute — every visitor is served the same read-only material. Because no caller is identified, nothing personal is collected or displayed; what is published is limited to information that is public by design.

---

## What kinds of material are published

A public surface federates more than one kind of material into a single place: announcements, news, products and services, a [regelcatalogus](regelcatalogus.md) of rules and the services they implement, and a [procesbibliotheek](procesbibliotheek.md) of process definitions. Each kind keeps its own shape, but all of it is reachable from one search.

---

## Searching and browsing across it

A single search spans every kind of published material at once, built from one federated index so that a listing and a search result can never drift apart — an item that appears in a list is resolved through the same index a search query matches against. A search can be narrowed by facets such as the kind of item, its source, or its intended audience, and each item has its own stable, directly linkable detail page.

---

## Served separately from the authenticated surface

A public surface is its own deployment, reachable at its own address, distinct from the signed-in working environment it draws its information from. It carries its own security headers restricting where its scripts and content may load from, and it reaches the platform only through the subset of endpoints deliberately left open to unauthenticated callers — see [API Design — Public versus authenticated surface](api-design.md#public-versus-authenticated-surface). It also accepts a small number of writes on that same public surface — such as an attachment or a message — subject to the stricter rate limit and proof-of-work check described in [Security & Compliance](security-compliance.md).

---

## Accessibility

A public government site commits to WCAG 2.1 level AA conformance. In practice that includes a skip link to the main content visible on keyboard focus, a visible focus indicator on every interactive element, a label on every form field even where it is hidden visually, a minimum text contrast of 4.5:1, and a landmark structure — header, navigation, main content, footer — with a breadcrumb trail. Known gaps against that target, and how to report a new one, are published on the site itself.

---

## Open data

Everything published is also available as open data: every item is machine-readable through the same anonymous API the site itself calls, with no key and no account required, and is free to reuse as public government information without copyright restriction.

---

## Related

- [Regelcatalogus](regelcatalogus.md) and [Procesbibliotheek](procesbibliotheek.md) — two of the catalogues a public surface publishes
- [API Design](api-design.md) — the public-versus-authenticated surface and the envelope a public endpoint follows
- [Security & Compliance](security-compliance.md) — the rate limiting and proof-of-work check guarding a public write
