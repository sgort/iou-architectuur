---
component: RONL Business API
---

# Procesbibliotheek

A **procesbibliotheek** is a browsable library of the process definitions deployed to the platform: what each one is called, what state it is in, and what else is deployed alongside it. Where a [regelcatalogus](regelcatalogus.md) catalogues rules against the services they implement, a procesbibliotheek catalogues the process definitions themselves.

---

## What a library entry describes

An entry represents one deployed process definition. It carries the process's name, the identifying key it is deployed under, a lifecycle status, and whether it runs standalone or as a subprocess invoked by another. An entry also lists what is deployed alongside that process definition and bound to it: the forms it uses, any document templates it produces, and the decision tables it evaluates — so the entry reflects everything that ships with the process, not the process definition in isolation.

---

## How a definition reaches the library

An entry is not authored separately from the deployment itself. It is derived from a deployment index that tracks every deployed process bundle, so a process definition appears in the library once it has actually been deployed — and disappears from it, or its listed status changes, as that deployment changes. There is no parallel documentation step to keep in sync: the library is a read view onto what is deployed.

---

## What it relates to

Because an entry is derived from the deployment itself, it stays tied to what is actually runnable rather than describing a process definition as it was once designed. A form, document template, or decision key listed against an entry is the one that resolves at runtime — the same binding described in [Dynamic Forms](dynamic-forms.md) and [Business Rules Execution](business-rules-execution.md) — not a separately maintained description of it.

---

## Public and internal exposure

A process definition can be attributed to the surface that owns it, and only definitions owned by a public-facing surface — or carrying no such attribution at all — are exposed on the library's public, read-only view; others stay restricted to internal use. A lifecycle status gates visibility the same way: a definition still in progress is held back from the public view by default, independently of who owns it.

Within that public boundary, the library is reachable in more than one place at once — inside an otherwise authenticated working environment, and on a public site with no login — both reading the same underlying data; see [Public Publication](public-publication.md).

---

## Related

- [Regelcatalogus](regelcatalogus.md) — the equivalent catalogue for rules and the services they implement
- [Processes](processes.md) — deploying and starting the process definitions a library entry describes
- [Dynamic Forms](dynamic-forms.md) and [Business Rules Execution](business-rules-execution.md) — the forms and decisions a library entry links to
- [Public Publication](public-publication.md) — the public, unauthenticated surface a library entry can be exposed on
