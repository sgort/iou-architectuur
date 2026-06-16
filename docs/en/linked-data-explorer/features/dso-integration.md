# DSO Integration

## Overview

The Linked Data Explorer integrates with the **Digitaal Stelsel Omgevingswet (DSO)** — the national catalogue and registry stack underpinning the Dutch Environment and Planning Act. This integration lets process designers link BPMN subprocesses directly to their authoritative DSO activiteit, browse the Stelselcatalogus and werkzaamheden registry from inside LDE, verify references against live DSO data, and — as of v1.9.3–v1.9.5 — extract an activity's *toepasbare regels* into deploy-ready LDE assets (DMN, form scaffold) or hand them off to the CPSV Editor for publishing.

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
- The full **`functioneleStructuurRef`** URI — the pivot to STTR files used by the Phase 4 extraction (see [Applicable rules → LDE assets](#applicable-rules-lde-assets-phase-4))
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

**Name search (v1.9.4).** Fixing a location (Lelystad / Flevoland) loads that authority's full activity set in one call and reveals a search box that live-filters by name — so activities such as "Boom kappen of houtopstand vellen" are findable without walking the hierarchy.

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

## Applicable rules → LDE assets (Phase 4)

As of v1.9.3 the Activity Detail panel includes an **Applicable Rules** section listing the *toepasbare regels* fetched live from the DSO Uitvoeren Gegevens API, grouped by rule type (Conclusie / Indieningsvereisten) with the validity date and STTR version. Each rule type exposes a set of one-click actions, backed by the `GET /v1/dso/toepasbare-regels/*` backend routes:

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Activity Detail panel "Applicable Rules" section for the HoutopstandVellen activity, showing a Conclusie row and an Indieningsvereisten row each with validity date and STTR version, and the action buttons — Download STTR, Extract DMN, Publish via CPSV Editor on the Conclusie row; Form scaffold and Import into LDE on the Indieningsvereisten row](../../assets/screenshots/linked-data-explorer-dso-applicable-rules.png)
  <figcaption>Applicable Rules section with the Phase 4 extract/import/publish actions</figcaption>
</figure>

| Action | Rule type | What it does | Backend route |
|---|---|---|---|
| **↓ STTR** | any | Downloads the raw STTR XML | `/toepasbare-regels/:id/sttr` |
| **↓ Extract DMN** | Conclusie | Extracts the embedded DMN decision table as a standalone, deploy-ready `.dmn` file | `/toepasbare-regels/:id/dmn` |
| **↓ Form scaffold** | Indieningsvereisten | Generates a form-js JSON scaffold from the STTR questionnaire | `/toepasbare-regels/:id/form-scaffold` |
| **↓ Import into LDE** (v1.9.4) | Indieningsvereisten | Saves the generated form-js scaffold straight into the Form Editor as a draft — no manual download/import | `/toepasbare-regels/:id/form-scaffold` |
| **Publish via CPSV Editor** (v1.9.4) | Conclusie | Opens the CPSV Editor with a deep-link to publish the extracted DMN to TriplyDB, where the LDE DMN picker can consume it | (deep-link) |

**Form scaffold mapping.** The STTR questionnaire is mapped to form-js controls: boolean questions → checkboxes, list questions → select fields with options, number questions → number fields, and attachment requirements → labelled textfields. Imported forms are tagged with the readable authority name (e.g. "Lelystad", v1.9.4), falling back to the RTR code (GM0995) for authorities outside the known presets, and show a green **DSO** badge in the Form Editor list (v1.9.5).

**Deploy-ready DMN.** Extracted DMNs are normalized so they deploy and evaluate on Operaton without hand-patching (v1.9.4–v1.9.5): DMN 1.2 is upgraded to 1.3, missing input ids are added, variable names are made FEEL-safe (hyphens/spaces previously broke evaluation), output columns get an explicit `typeRef`, and `camunda:historyTimeToLive` is added so the model deploys exactly as handed off. Verified end-to-end against Operaton (the normalized `HoutopstandVellen` decision deploys with all 7 decisions and its root decision evaluates without the previous FEEL error).

The DMN publish handoff is the LDE side of the same deep-link contract the CPSV Editor consumes via its [DSO → DMN import](../../cpsv-editor/features/dso-import.md).

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

The integration is delivered in phases. The detailed plan, current status, confirmed test anchors, and remaining work for each phase are tracked in [DSO Integration Phase Plan](dso-integration-phase-plan.md). Phases 1–3 are live as of v1.5.3; Phase 2a/2d and Phase 4 (STTR → DMN/form extraction, Import into LDE, and the DMN publish handoff) landed across v1.9.3–v1.9.5.

---

## Related documentation

- [DSO Explorer user guide](../user-guide/dso-explorer.md) — step-by-step search and link workflow
- [DSO Integration Phase Plan](dso-integration-phase-plan.md) — phase status, test anchors, implementation order
- [BPMN Modeler — DSO activiteit linkage](bpmn-modeler.md#dso-activiteit-linkage)