---
component: RONL Business API
---

# Public Site

**Open Regels Nederland** is the public knowledge base of the Province of Flevoland. It publishes public information only — no personal data is processed, and no login or account is needed. It is for anyone: residents, businesses or officials from other organisations who want to look up the same regulations, products, processes and concepts that a Flevoland civil servant sees in the werkomgeving.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Open Regels Nederland public knowledge base landing page with combined search and five source cards](../../assets/screenshots/ronl-business-api-public-site.png)
  <figcaption>Open Regels Nederland — public knowledge base landing page</figcaption>
</figure>

## Combined search

A single search box queries all five sources at once — announcements, news, products, rules and processes.

## Five sources

| Source | Description |
|---|---|
| Announcements | Official announcements from the Province of Flevoland. |
| News | National news from the Dutch central government. |
| Products & Services | Permits, notifications and grants for residents and businesses. |
| Rule catalogue | Public services and the rules used to execute them, including validity dates and source. |
| Process library | How an application moves through the organisation, step by step. Each process carries a status label — see below. |

### Every deployed process, with its status on it

The process library lists **every process deployed to a public-facing board**,
whatever state it is in, and each one shows its status — `example`, `wip` or
`e2e` — beside its name. The label appears in the listing and in search results,
not only on a process's own page, so you can see at a glance that something is a
worked example or still in progress without opening it.

The label is always written out as text rather than signalled by colour alone.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: the public process library listing, each process showing its status label beside its name](../../assets/screenshots/ronl-business-api-public-site-processen.png)
  <figcaption>The process library — every deployed process, each with its status label</figcaption>
</figure>

!!! note "If you looked here before September 2026 and found it empty"
    You were not missing anything and nothing was hidden from you: production
    listed **no processes at all**. The library had been filtering on a status
    value the underlying catalogue cannot hold, so nothing ever passed it. It
    now filters on which board owns a process and nothing else.

## A rule's concepts, split into input and output

Open a rule from the search results and scroll to its concepts. They are no
longer one alphabetical row of chips. The heading still names the section and
counts every concept of the service, and below it the chips are divided into two
labelled groups, each carrying its own count:

- **Invoer — gegevens die de regels nodig hebben.** The values the rules take in
  before they can decide anything.
- **Uitvoer — wat de regels bepalen.** What comes out: the entitlements, amounts
  and decisions the rules arrive at.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: a rule's detail page on the public site, its concepts divided into Invoer and Uitvoer groups, each heading carrying its own count](../../assets/screenshots/ronl-business-api-public-site-begrippen-io.png)
  <figcaption>Invoer and Uitvoer, on a rule's detail page</figcaption>
</figure>

Every chip still links out to the term in the shared vocabulary, exactly as
before.

!!! note "Some concepts sit in a third group, and that is not a fault"
    The division comes from the knowledge graph. Where the graph does not say
    which side a concept belongs to, the concept is shown in a group of its own
    rather than dropped or guessed at — so nothing goes missing from the count.

    Two other things are worth knowing if a page looks different from this one.
    The grouping is **per service, not per rule**: where a service's rules all
    hang off one decision model, a value reads as an output of the service even
    if the particular rule you are reading consumes it. And a page served by a
    tier that has not yet been updated shows the single undivided row it always
    did.

## Further sections

The top navigation also has **Data dictionary** and **Provenance**, alongside an **NL/EN** language toggle and a **Staff login** link across to the werkomgeving.

## Accountability

The footer's "Accountability" column links to the **Accessibility statement (WCAG 2.1 AA)** and **Open data & API**.

## Which build you are looking at

The foot of every page ends with a small monospace line naming the site, the release, and the build it was made from. On production on 12 September 2026 it read:

```
publiek.open-regels.nl · v2026.09.6 · build 04840ed · #2
```

The address is the environment you are actually on — the acceptance copy shows its own address there. The `v…` is the release. `build …` is the first seven characters of the commit the site was built from, and the `#…` after it is the number of the deployment run, which is what tells two builds of the same release apart. Hovering the build shows the full commit hash, so it can be copied into a bug report. A copy of the site that did not come from a deployment reads `local build` instead.

---

!!! info "Acceptance runs alongside production"
    The site is live at `publiek.open-regels.nl`. An acceptance copy runs at
    `acc.publiek.open-regels.nl`, where a release is tried before it is
    promoted. The footer line above is how to tell which of the two you have
    open.
