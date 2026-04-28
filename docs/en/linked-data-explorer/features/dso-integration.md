# DSO Integration

## Overview

The Linked Data Explorer integrates with the **Digitaal Stelsel Omgevingswet (DSO)** — the national catalogue and registry stack underpinning the Dutch Environment and Planning Act. This integration lets process designers link BPMN subprocesses directly to their authoritative DSO activiteit, browse the Stelselcatalogus and werkzaamheden registry from inside LDE, and verify references against live DSO data.

The integration spans three DSO APIs:

- **Stelselcatalogus** — the conceptual model (concepts, properties, value lists)
- **Zoekinterface** — search interface over werkzaamheden (the citizen-facing tasks like "boom kappen")
- **RTR (Registratie Toepasbare Regels)** — the activity registry where each authority's activiteiten and rule types live

A toggle in Settings selects between the **pre-production** and **production** DSO environments independently of the LDE environment.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: DSO Explorer panel open in LDE with the three tabs visible at the top — Concepts, Works, Activities — the Activities tab active showing a list of activiteiten with omschrijving, validity dates, and rule-types-present badges, plus a date input and authority preset dropdown above the list](../../assets/screenshots/linked-data-explorer-dso-explorer-overview.png)
  <figcaption>DSO Explorer with the Activities tab active and the Lelystad authority preset selected</figcaption>
</figure>

---

## DSO environment toggle

The DSO environment is set in **Settings → DSO environment** and persisted to localStorage. It is independent of the LDE environment toggle — pre-production LDE can talk to production DSO and vice versa, which matters because some authority data is only available in one environment.

| LDE setting | API target |
|---|---|
| **Pre-production** | `service.pre.omgevingswet.overheid.nl` |
| **Production** | `service.omgevingswet.overheid.nl` |

A coloured badge in the DSO Explorer header reflects the active environment — amber for pre-production, green for production.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: DSO Explorer header showing the environment badge — amber pill with text Pre-production next to the panel title, plus the cog icon that opens the Settings panel](../../assets/screenshots/linked-data-explorer-dso-environment-badge.png)
  <figcaption>DSO environment badge in the panel header</figcaption>
</figure>

---

## Concepts tab

Full-text search over the Stelselcatalogus. Returns concepts with their URI, label, definition, and source. Useful for discovering the canonical conceptual reference behind a citizen-facing term.

---

## Works tab — werkzaamheden

Search the Zoekinterface for werkzaamheden (the citizen-facing tasks that anchor a permit application — "boom kappen", "Bed & Breakfast starten"). Autocomplete fires after two characters with 300ms debounce.

Each result shows:

- The human-readable **omschrijving** (e.g. "Bed & Breakfast starten")
- The full **`functioneleStructuurRef`** URI — the pivot to STTR files for the upcoming Phase 4 import
- The short werkzaamheid URN

Selecting a result opens a detail panel with the current version's metadata, validity period, and full version history (each version showing start/end dates and a "current" badge).

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Works tab in the DSO Explorer with a search for boom in the search box, showing autocomplete suggestions in a dropdown, and below that a results list with multiple werkzaamheden cards — each showing the omschrijving, the ref URI line, and a short URN at the bottom](../../assets/screenshots/linked-data-explorer-dso-works-search.png)
  <figcaption>Werkzaamheden search with autocomplete suggestions</figcaption>
</figure>

Default sort order is `meestGekozen` — the most-used Omgevingsloket werkzaamheden appear first.

---

## Activities tab — activiteiten

Browse the RTR (Registratie Toepasbare Regels) for activiteiten. The default view lists recent activities; the **authority presets** (Lelystad, Flevoland) filter the list by authority OIN (Organisatie-identificatienummer) using `POST /activiteiten/_zoek` with `bestuursorgaan.oin` as the body filter.

The date input above the list defaults to today; changing the date and clicking **Load** re-fetches the authority list valid on that date.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Activities tab showing the date input at the top with todays date, the authority preset dropdown showing Lelystad selected, a Load button next to it, and below a list of activiteiten cards each with omschrijving, validity period, and small badges indicating which rule types are present — Conclusie, Indieningsvereisten, Maatregelen](../../assets/screenshots/linked-data-explorer-dso-activities-list.png)
  <figcaption>Activities list filtered by Lelystad authority OIN</figcaption>
</figure>

Each activity card shows badges for the rule types declared on the activity:

- **Conclusie** — full DMN decision content available
- **Indieningsvereisten** — application requirements (questionnaire-style DMN)
- **Maatregelen** — measures (textual content, structured per maatregel)

These badges flag which downstream LDE assets can eventually be derived from the activity in Phase 4 (DMN, form, document template).

### Activity Detail panel

Clicking an activity row opens the detail panel. It shows:

- omschrijving and full URN
- bestuursorgaan (authority) — bestuurslaag, organisatieType, code, OIN
- validity (begindatum / einddatum)
- parent activity link (if any)
- child activities — names fetched in parallel after the parent loads
- rule types present, with download links

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Activity Detail panel for Bed & Breakfast starten showing the omschrijving as the heading, authority block with gemeente Lelystad GM 0995 OIN, validity from 09-07-2025, two rule-type rows for Conclusie and Indieningsvereisten each with their functioneleStructuurRef and a Download STTR button, and a child activities list at the bottom](../../assets/screenshots/linked-data-explorer-dso-activity-detail.png)
  <figcaption>Activity Detail panel for "Bed & Breakfast starten"</figcaption>
</figure>

If an activity is queried from the wrong DSO environment (e.g. trying to view a production-only URN while the toggle is on pre-production), the detail panel shows a clear "not available in this environment" message rather than a raw 404.

---

## Linking a BPMN subprocess to a DSO activiteit

The BPMN Modeler footer panel has a **DSO Activity** selector. Pasting a URN and clicking **Verify** queries the live DSO RTR — on success, the panel shows the omschrijving, authority, and a direct link to the public RTR viewer. The URN is then persisted on the BPMN process element as `ronl:dsoActiviteitUrn`.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: BPMN Modeler footer panel with the DSO Activity section open showing a URN paste field with a Lelystad B&B URN entered, the Verify button, and below it a teal info card showing the omschrijving Bed & Breakfast starten, the authority gemeente Lelystad, and an external link icon labelled View in DSO RTR viewer](../../assets/screenshots/linked-data-explorer-dso-selector-bpmn.png)
  <figcaption>DSO Activity selector pinned to the BPMN Modeler footer</figcaption>
</figure>

The verified URN survives saveXML round-trips and follows the same pattern as other `ronl:` extensions (RoPA, language, organization).

---

## Phase plan

The integration is delivered in phases. The detailed plan, current status, confirmed test anchors, and remaining work for each phase are tracked in [DSO Integration Phase Plan](dso-integration-phase-plan.md). Phases 1–3 are live as of v1.5.3; Phase 4 (STTR → DMN/form/document import) is the next development cycle.

---

## Related documentation

- [DSO Explorer user guide](../user-guide/dso-explorer.md) — step-by-step search and link workflow
- [DSO Integration Phase Plan](dso-integration-phase-plan.md) — phase status, test anchors, implementation order
- [BPMN Modeler — DSO activiteit linkage](bpmn-modeler.md#dso-activiteit-linkage)
- [Backend API reference — DSO routes](../reference/api-reference.md#dso-routes)