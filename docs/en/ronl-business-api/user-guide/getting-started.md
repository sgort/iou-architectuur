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

### Signing in

The landing page's primary action is **Inloggen met uw Flevoland-account**. It takes you to Provincie Flevoland's own sign-in, brokered by the platform's identity server; on a Flevoland-managed laptop you are usually signed in with the account the device is joined to, without a prompt. **Bekijk de borden** beside it scrolls to the board cards without signing you in, and inwoners sign in with DigiD from the link at the top.

After signing in you land on the board your roles allow. Picking a board card first takes you to that board instead, so the card you clicked is the one you get. The boards you are not entitled to see are not shown.

For how access is granted, and what an administrator has to set up per environment, see [Entra ID (Provincie Flevoland)](../developer/deployment/entra-id.md).

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

The site is live at `publiek.open-regels.nl`, with an acceptance copy at `acc.publiek.open-regels.nl`.

A shared link to the werkomgeving or to the public knowledge base unfolds into a preview card. On the acceptance copies the card's title begins with `[ACC]`, and those copies are kept out of search engines.

---

## PA-Cockpit demo

[The PA-Cockpit demo](pa-demo.md) is the third public surface. It runs the same PA-Cockpit the werkomgeving does, but on demonstration data and with no connection to any backend — so it can be opened by anyone with the link, including people who will never have an account.

It exists for showing the product: to a prospective province, to a colleague from another organisation, or to a room. Because it is the real cockpit rather than a mock-up, what a visitor clicks is what the product does. A role selector lets a visitor see how the same board changes for a narrower set of rights.

It runs in production at `plato.open-regels.nl` since 12 September 2026, with an
acceptance copy at `acc.plato.open-regels.nl`.

---

!!! info "Documentation depth follows release maturity"
    The RONL Business API is developed in short cycles with a diverse user
    group. Something that is only on the acceptance environment is documented
    briefly — what it is for and what you see — and gets a full step-by-step
    guide once it reaches production. All four boards are in production: the
    [Caseworker](caseworker.md) guide is full, and the other three are brief
    for now and will be expanded. Guides describing earlier versions are kept
    under [Archive](archive/login-flow.md).
