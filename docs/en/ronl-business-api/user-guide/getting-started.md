---
component: RONL Business API
---

# Getting Started

RONL Business API (RBA) is made up of three separate environments. The **werkomgeving** is where provincial staff sign in with a medewerkersaccount to do their work. The **public knowledge base** is a separate, public site with no login and no account, where the same information that provincial staff can see is published for anyone to read. The **PA-Cockpit demo** is a third public site, running the PA-Cockpit itself on demonstration data so it can be shown to someone without an account. Which of the werkomgeving's boards you see depends on your role and authorisations within the province.

---

## Werkomgeving

The werkomgeving (`ronl.werkomgeving`, Province of Flevoland) presents four boards: "Vier borden voor het werk van de provincie." Not everyone sees all four — the set of boards shown depends on your role and authorisations.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: RONL Business API werkomgeving landing page showing the four boards — Caseworker, PA-Cockpit, Infra-board, and Woo-dashboard](../../assets/screenshots/ronl-business-api-landing-page.png)
  <figcaption>Werkomgeving landing page with its four boards: Caseworker, PA-Cockpit, Infra-board, and Woo-dashboard</figcaption>
</figure>

| Board | Tagline | What it's for |
|---|---|---|
| [Caseworker](caseworker.md) | *werk · taken* | Personal work queue for case handlers: tasks, claims and deadlines per case, with a built-in assistant for quick assessment. |
| [PA-Cockpit](pa-cockpit.md) | *kompas · issues* | Administrative overview of dossiers and issues: a compass weighing priority and momentum so the executive can steer in time. |
| [Infra-board](infra-board.md) | *portfolio · fases* | Portfolio steering for infrastructure projects: phase swimlanes, per-project status and RIP management, from planning through delivery. |
| [Woo-dashboard](woo-dashboard.md) | *woo · compliance* | Steering on the Wet open overheid: compliance, lead times, process bottlenecks and active publication, with traffic lights and a "Woo in cijfers" benchmark. |

---

## Public knowledge base

[Open Regels Nederland](public-site.md) is the public counterpart to the werkomgeving. It requires no login and no account, and processes no personal data. Every piece of public information a Flevoland civil servant sees in the werkomgeving is published here too, alongside combined search across five sources.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Open Regels Nederland public knowledge base site](../../assets/screenshots/ronl-business-api-public-site.png)
  <figcaption>Open Regels Nederland — the public knowledge base</figcaption>
</figure>

This site is currently **ACC-only**, at `acc.publiek.open-regels.nl`.

---

## PA-Cockpit demo

[The PA-Cockpit demo](pa-demo.md) is the third public surface. It runs the same PA-Cockpit the werkomgeving does, but on demonstration data and with no connection to any backend — so it can be opened by anyone with the link, including people who will never have an account.

It exists for showing the product: to a prospective province, to a colleague from another organisation, or to a room. Because it is the real cockpit rather than a mock-up, what a visitor clicks is what the product does. A role selector lets a visitor see how the same board changes for a narrower set of rights.

This site is currently **ACC-only**, at `acc.plato.open-regels.nl`.

---

!!! info "Documentation depth follows release maturity"
    The RONL Business API is developed in short cycles with a diverse user
    group. While a board is on the acceptance environment it is documented at
    this level — what it is for and what you see. Full step-by-step guides
    follow when a board reaches production. Guides describing earlier versions
    are kept under [Archive](archive/login-flow.md).
