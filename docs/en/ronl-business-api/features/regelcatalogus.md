---
component: RONL Business API
---

# Regelcatalogus

A **regelcatalogus** is a browsable catalogue of the public services a government body offers, paired with the rules used to carry each one out. It answers two questions together rather than separately: what a service is, and which concrete rule implements it — alongside the organisation responsible for the service and the concepts a rule refers to.

---

## What an entry carries

A catalogue is organised around four related kinds of entry: a **service**, described by a title and a description; the **organisation** that implements it, with a name and a link to its own site; a **rule**, the concrete implementation of a service, carrying a title, a description, and — where it applies — a validity date; and a **concept** a rule or service refers to, drawn from a shared vocabulary and linked back to the service it belongs to. An entry in any of the four is connected to the others: a rule belongs to a service, a service belongs to an organisation, a concept is scoped to the service that uses it.

---

## Where entries come from

Entries are not authored inside the catalogue itself. They are read live from an underlying knowledge graph, queried on demand rather than copied into the catalogue's own storage — so the catalogue always reflects whatever the graph currently holds, with no separate authoring step and no risk of the two drifting apart. Because the graph is the single source, the same data can be queried again for other purposes without a second copy being kept in sync.

---

## Browsing and finding an entry

A catalogue can be browsed by kind — organisations, services, rules, or concepts — with a rule list groupable by the service it implements. A search narrows the list by matching text against an entry's title and description; a filter narrows it further by the service or organisation an entry belongs to. Selecting an entry can also cross-navigate: choosing a service can jump straight to the concepts scoped to it, filtered accordingly.

---

## Freshness and resilience

Because entries are read live rather than stored, a catalogue caches what it reads for a short interval so that repeated browsing does not re-query the graph on every request. If the underlying graph is briefly unreachable, the catalogue keeps serving what it last read rather than showing nothing.

---

## Public and internal exposure

A regelcatalogus is read-only and reachable without authentication — see [Public Publication](public-publication.md) for what that means for the surface it sits on. The same underlying data can be surfaced in more than one place at once: as a section inside an otherwise authenticated working environment, and as its own page on a public site with no login at all. Both read the same catalogue through the same public endpoint, so what one shows is exactly what the other shows.

---

## Related

- [Procesbibliotheek](procesbibliotheek.md) — the equivalent catalogue for process definitions rather than rules
- [Public Publication](public-publication.md) — the public, unauthenticated surface a catalogue is exposed on
- [API Design](api-design.md) — the public-versus-authenticated surface a catalogue's endpoint follows
- [Security & Compliance](security-compliance.md) — the rate limiting that protects a public, unauthenticated endpoint
