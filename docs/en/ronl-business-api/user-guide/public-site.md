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
| Process library | How an application moves through the organisation, step by step. |

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
