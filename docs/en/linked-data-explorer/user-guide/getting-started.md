---
component: Linked Data Explorer
---

# Getting Started

This guide walks you through the Linked Data Explorer for the first time, from opening the application to executing your first DMN chain.

---

## Prerequisites

- Access to [linkeddata.open-regels.nl](https://linkeddata.open-regels.nl) or the [acceptance environment](https://acc.linkeddata.open-regels.nl)
- A modern browser (Chrome, Firefox, Safari, or Edge — latest two versions)
- No sign-in for looking around, querying and running chains. Saving to the shared library, deploying and publishing need one — see [Signing in](#signing-in)

---

## Application layout

The application has a narrow left sidebar with navigation icons, and a main content area that changes depending on the active view.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Linked Data Explorer sidebar navigation with the Orchestration view active](../../assets/screenshots/linked-data-explorer-orchestration-nav.png)
  <figcaption>Linked Data Explorer sidebar navigation with the Orchestration view active</figcaption>
</figure>

| Icon | View |
|---|---|
| Search | SPARQL Query Editor |
| GitBranch | Chain Builder (DMN Orchestration) |
| Workflow | BPMN Modeler |
| LayoutTemplate | Form Editor |
| FileOutput | Document Composer |
| ScrollText | RoPA Records |
| Landmark | DSO Explorer |
| ShieldCheck | DMN Validator |
| BadgeCheck | SHACL Validator |
| Share2 | Graph Visualisation |
| BookOpen | Changelog |

**Settings** sits below the rail, pinned. The eleven view icons above it scroll
on a short window rather than being pushed off the bottom edge — before
v2026.09.2 they were, taking Settings with them, and a window shorter than the
rail left both unreachable.

!!! info "The in-app tutorial was removed in v2026.09.2"
    A **HelpCircle** icon used to open a guided tutorial inside the application.
    It is gone, and this page is where that walkthrough now lives.

---

## Signing in

You can open every view, run queries and execute chains without signing in. Changing what others see needs a sign-in with the `lde-author` role: saving processes, forms and document templates to the shared library, deploying, saving a chain as a DRD, refreshing the DMN cache, and saving or deleting RoPA records.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: The right end of the header with the Sign in menu open, listing its two routes, Flevoland-account and Medewerker](../../assets/screenshots/linked-data-explorer-sign-in-menu.png)
  <figcaption>The Sign in menu in the header, with its two routes</figcaption>
</figure>

1. Click **Sign in** at the right of the header.
2. Choose **Flevoland-account** to sign in with your province account, or **Medewerker** for an employee account with a password.
3. Complete the sign-in in the popup. It closes by itself, and the page keeps what you had open.

Signed in, the header shows your name and **Sign out**. If your account does not have the `lde-author` role, a **View only** label appears next to your name, and a note explains that saving to the shared library, deploying and publishing are locked. Ask an administrator for the role, then sign in again.

Signed out, a locked button shows a lock and says *Sign in to …*. You can still save processes, forms and document templates: they stay in this browser, marked *only in this browser*, until you save them again as an author.

If your browser blocks the popup, the sign-in opens in the same tab instead.

---

## Your first chain execution — 5-minute walkthrough

This walkthrough uses the Heusdenpas chain: three DMNs from SVB, SZW, and the Heusden municipality that together assess eligibility for the Heusdenpas social benefit pass.

**Step 1 — Open the Chain Builder**

Click the GitBranch icon in the left sidebar. The view splits into three panels: Available DMNs (left), Chain Composer (centre), and Configuration (right).

**Step 2 — Verify DMNs are loaded**

The Available DMNs panel should show several DMN cards. If it is empty, check that the active endpoint is set to the RONL TriplyDB dataset in the configuration panel. You should see `SVB_LeeftijdsInformatie`, `SZW_BijstandsnormInformatie`, and at minimum one Heusden DMN.

**Step 3 — Build the chain**

Drag `SVB_LeeftijdsInformatie` into the Chain Composer. Then drag `SZW_BijstandsnormInformatie` below it. The validation panel should show a green checkmark: "Chain is valid and ready to execute."

**Step 4 — Provide inputs**

The input form in the Configuration panel shows the inputs the chain needs from you. Fill in a `geboortedatum` (date of birth in YYYY-MM-DD format, e.g., `1960-01-01`).

**Step 5 — Execute**

Click **Execute**. The execution panel shows per-step progress with timing. When complete, the results panel shows the final output values.

---

## Smoke test checklist

Use this after any configuration change to verify core functionality:

- [ ] Backend health: `GET https://backend.linkeddata.open-regels.nl/v1/health` returns `"status": "healthy"`
- [ ] DMN list loads in Chain Builder (at least 3 cards)
- [ ] Dragging two DMNs into the composer produces either a green or amber validation status (not an error)
- [ ] An exact-match chain (SVB → SZW) shows green validation and active Execute/Save/Export buttons
- [ ] Clicking Execute with valid inputs returns results without console errors
- [ ] SPARQL Query Editor: clicking Run Query returns results in the table

---

## Next steps

- [Running SPARQL Queries](sparql-queries.md) — use the query editor to explore the knowledge graph directly
- [Building DMN Chains](chain-building.md) — detailed chain-building workflow
- [BPMN Modeler](bpmn-modeler.md) — embed decision references in BPMN process diagrams
