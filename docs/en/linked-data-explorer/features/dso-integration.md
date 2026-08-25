---
component: Linked Data Explorer
---

# DSO Integration

## Overview

The Linked Data Explorer integrates with the **Digitaal Stelsel Omgevingswet (DSO)** — the national catalogue and registry stack underpinning the Dutch Environment and Planning Act. This integration lets process designers link BPMN subprocesses directly to their authoritative DSO activiteit, browse the Stelselcatalogus and werkzaamheden registry from inside LDE, verify references against live DSO data, and — as of v1.9.3–v1.9.5 — extract an activity's *toepasbare regels* into deploy-ready LDE assets (DMN, form scaffold) or hand them off to the CPSV Editor for publishing.

A toggle in Settings selects between the **pre-production** and **production** DSO environments independently of the LDE environment.

!!! tip "Prefer the short version?"
    [DSO Viewer APIs — Slide Deck](dso-viewer-apis-deck.md) covers the same ground in twelve
    slides, and is downloadable as a PDF.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: DSO Explorer panel open in LDE with the three tabs visible at the top — Concepts, Works, Activities — the Activities tab active showing a list of activiteiten with omschrijving, validity dates, and rule-types-present badges, plus a date input and authority preset dropdown above the list](../../assets/screenshots/linked-data-explorer-dso-explorer-overview.png)
  <figcaption>DSO Explorer with the Activities tab active and the Lelystad authority preset selected</figcaption>
</figure>

---

## The five DSO APIs behind the viewer

The frontend never calls DSO directly. Every request goes through the LDE backend, which
mounts its DSO proxy at `/v1/dso` and attaches the `x-api-key` credential server-side. That
keeps the DSO key out of the browser and lets a single `X-Dso-Env` header switch the whole
viewer between the pre-production and production stelsel.

```
DsoExplorer.tsx  →  dsoService.ts  →  LDE /v1/dso/*  →  dso.service.ts  →  DSO API
   (component)      (frontend client)     (proxy route)      (backend service)
```

Five separate upstream APIs back the viewer:

| # | API | Path | What it backs in LDE |
|---|---|---|---|
| 1 | **Stelselcatalogus** | `catalogus/api/opvragen/v3` | Concepts tab — concept and term lookup |
| 2 | **RTR Gegevens** | `toepasbare-regels/api/rtrgegevens/v2` | Activities tab, activity detail, child-activity lookups, BPMN URN verification |
| 3 | **Zoekinterface** | `toepasbare-regels/api/zoekinterface/v2` | Works tab — werkzaamheden search and autocomplete |
| 4 | **Opvragen Werkzaamheden** | `toepasbare-regels/api/opvragenwerkzaamheden/v1` | Works tab — versioned werkzaamheid detail |
| 5 | **Toepasbare Regels Uitvoeren Gegevens** | `toepasbare-regels/api/toepasbareregelsuitvoerengegevens/v1` | Applicable Rules panel — rule metadata and STTR download |

Pre-production base URLs are `service.pre.omgevingswet.overheid.nl/publiek/<path>`; production
is the same path on `service.omgevingswet.overheid.nl`. Each base URL is overridable per
environment (`DSO_CATALOGUE_BASE_URL`, `DSO_RTR_BASE_URL`, `DSO_ZOEKINTERFACE_BASE_URL`,
`DSO_OPVRAGEN_WERKZAAMHEDEN_BASE_URL`, `DSO_UITVOEREN_GEGEVENS_BASE_URL`, each with a `_PROD`
counterpart), and the two environments carry their own keys (`DSO_API_KEY` / `DSO_API_KEY_PROD`).

Common to every call: `Accept: application/hal+json` (STTR downloads ask for `application/xml`,
autocomplete for `application/json`), a `DSO_TIMEOUT` of 15 000 ms enforced with an
`AbortController`, and HAL payloads returned **verbatim** inside LDE's `{ success, data }`
envelope — the frontend unwraps `_embedded.*` and `_links.next` itself. Any non-2xx from DSO
surfaces as a `502` from LDE carrying the upstream body, except an upstream `404`, which is
passed through as a `404`.

The per-endpoint parameters and the complete LDE-endpoint-to-DSO-call map live in the
[API Reference — DSO Integration](../reference/api-reference.md#dso-integration).

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

Full-text search over the Stelselcatalogus, paged 20 at a time. Returns concepts with their URI, label, definition, and source. Useful for discovering the canonical conceptual reference behind a citizen-facing term.

The backend also accepts a validity date (`geldigOp`, `YYYY-MM-DD`) on this search, but the
Concepts tab has no field for it — historical concept lookups are out of reach from the UI.

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

**The tab straddles two APIs.** Search and autocomplete hit the *Zoekinterface*
(`POST /werkzaamheden/_zoek`, `POST /werkzaamheden/_suggereer`), but the detail panel that
opens on a result comes from *Opvragen Werkzaamheden* (`GET /werkzaamheden/{urn}`) — that is
the call that returns the full `_embedded.werkzaamheidversies` list with `trefwoorden` and
`logischeRelaties`. Autocomplete failures degrade silently to an empty suggestion list rather
than surfacing an error.

---

## Activities tab — activiteiten

Browse the RTR (Registratie Toepasbare Regels) for activiteiten. The tab has two load modes:

| Mode | Call | Paging |
|---|---|---|
| **By date** (default) | `GET /activiteiten?datum` — every activity valid on that date | 20 per page |
| **By authority** (location preset) | `POST /activiteiten/_zoek` with `bestuursorgaan.oin` — that authority's complete set in one call | `pageSize=200`, so the name filter runs client-side |

The **authority presets** — Lelystad, Flevoland, and, since v2026.08.0, Ede and Gelderland —
filter by authority OIN (Organisatie-identificatienummer). The preset list carries the
OIN-to-name mapping too, because the RTR only ever returns the authority code (`GM0995`),
never a readable name.

The date input above the list defaults to today; changing the date and clicking **Load** re-fetches the authority list valid on that date. Dates are entered as ISO (`YYYY-MM-DD`) and converted to the DSO's `dd-MM-yyyy` before being sent.

A third mode exists in the backend but has no UI: `POST /v1/dso/activiteiten/zoek` also accepts
a WGS84 point (`geometrie` + `crs=epsg:4326`) and is implemented and tested end to end. It is
waiting on a map or point-selection feature — see
[API Reference](../reference/api-reference.md#post-v1dsoactiviteitenzoek).

**Name search (v1.9.4).** Fixing a location loads that authority's full activity set in one call and reveals a search box that live-filters by name — so activities such as "Boom kappen of houtopstand vellen" are findable without walking the hierarchy.

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
- child activities — see the fan-out below
- rule types present, with download links

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Activity Detail panel for Bed & Breakfast starten showing the omschrijving as the heading, authority block with gemeente Lelystad GM 0995 OIN, validity from 09-07-2025, two rule-type rows for Conclusie and Indieningsvereisten each with their functioneleStructuurRef and a Download STTR button, and a child activities list at the bottom](../../assets/screenshots/linked-data-explorer-dso-activity-detail.png)
  <figcaption>Activity Detail panel for "Bed & Breakfast starten"</figcaption>
</figure>

If an activity is queried from the wrong DSO environment (e.g. trying to view a production-only URN while the toggle is on pre-production), the detail panel shows a clear "not available in this environment" message rather than a raw 404.

### Child-activity fan-out — one click, `1 + N` requests

The RTR returns child activities as bare HAL hrefs under `_links.onderliggendeActiviteiten`,
with no `omschrijving` attached. The panel therefore cannot label them without asking the API
about each child individually. As soon as the parent resolves, it fires **one additional
activity-detail request per child, all in parallel**, purely to read each child's name:

```
GET /v1/dso/activiteiten/{parent-urn}       ->  1 request
  |- GET /v1/dso/activiteiten/{child-1}     -+
  |- GET /v1/dso/activiteiten/{child-2}      |-  N requests, fired together
  |- ...                                    -+
```

Every one of those is the same endpoint chain as the parent, so a single click costs `1 + N`
upstream RTR calls. `N` is whatever the parent declares — an activity such as
*Bedrijfsactiviteiten*, with 23 children, means 24 requests to render one detail panel.

What that means in practice:

- The fan-out uses `Promise.allSettled`, so one failing child never breaks the panel or the
  other lookups.
- Children that resolve render as a named link; children that fail, or that come back without
  an `omschrijving`, fall back to the raw URN — still clickable, just unlabelled. This is why
  a panel can show a mix of names and URNs.
- The `Child activities (N)` heading counts the *href list*, not the resolved names, so the
  count stays correct even when some lookups fail.
- Each child request inherits the parent's `datum` and `env`.
- Names live in local component state, cleared and re-fetched on every `urn` / `datum` / `env`
  change. There is **no cache and no concurrency cap**: navigating into a child issues its own
  fan-out, and re-opening an activity you already visited fetches everything again.

This is the viewer's heaviest interaction and exists only to turn hrefs into readable names.
If child counts grow or DSO rate limiting appears, it is the first thing to memoise.

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

**Form scaffold mapping.** The STTR questionnaire is mapped to form-js controls:

| STTR question | form-js field |
|---|---|
| `boolean` | checkbox |
| `list` | select, options from `uitv:optie` |
| `number` | number |
| `inter:inputType=textarea` | textarea |
| anything else | textfield |
| `uitv:bijlage` (attachment) | labelled placeholder textfield |
| `uitv:geoVerwijzing` | **skipped** — not representable in form-js |

A questionnaire containing a geo reference therefore produces a scaffold with that question
missing; check the source STTR if a generated form looks short.

Scaffolds are stamped `executionPlatform: Camunda Platform 7.21.0` and `status: 'dso'`, and can
be downloaded as JSON or imported straight into the Form Editor. Imported forms are tagged with
the readable authority name (e.g. "Lelystad", v1.9.4), falling back to the RTR code (GM0995) for
authorities outside the known presets, and show a green **DSO** badge in the Form Editor list
(v1.9.5).

**Deploy-ready DMN.** `normalizeDmnForOperaton` applies five fixes that make Sogelink STTR Builder output both deployable and evaluatable (v1.9.4–v1.9.5): DMN 1.2 namespaces are upgraded to 1.3; missing `id`s are injected on `<input>` and `<inputExpression>`; `<variable>` names are made FEEL-safe with the `<inputExpression>` references rewritten to match (hyphens and spaces previously broke evaluation); untyped outputs get an explicit `typeRef` (BIZ-004); and `camunda:historyTimeToLive="180"` is set per decision so the model deploys exactly as handed off. Verified end-to-end against Operaton (the normalized `HoutopstandVellen` decision deploys with all 7 decisions and its root decision evaluates without the previous FEEL error).

The DMN publish handoff is the LDE side of the same deep-link contract the CPSV Editor consumes via its [DSO → DMN import](../../cpsv-editor/features/dso-import.md). LDE has no local DMN store, so the link — `<VITE_CPSV_EDITOR_URL>/?dsoImport=dmn&dmnId=<id>&env=<pre|prod>` plus activity metadata — carries identifiers only; the CPSV Editor then fetches the XML from `GET /v1/dso/toepasbare-regels/{dmnId}/dmn` on this same backend. That endpoint is therefore a cross-application contract, not an internal route.

---

## Linking a BPMN subprocess to a DSO activiteit

The BPMN Modeler footer panel has a **DSO Activity** selector. Pasting a URN and clicking **Verify** queries the live DSO RTR — on success, the panel shows the omschrijving, authority, and a direct link to the public RTR viewer. The URN is then persisted on the BPMN process element as `ronl:dsoActiviteitUrn`.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: BPMN Modeler footer panel with the DSO Activity section open showing a URN paste field with a Lelystad B&B URN entered, the Verify button, and below it a teal info card showing the omschrijving Bed & Breakfast starten, the authority gemeente Lelystad, and an external link icon labelled View in DSO RTR viewer](../../assets/screenshots/linked-data-explorer-dso-selector-bpmn.png)
  <figcaption>DSO Activity selector pinned to the BPMN Modeler footer</figcaption>
</figure>

The verified URN survives saveXML round-trips and follows the same pattern as other `ronl:` extensions (RoPA, language, organization).

!!! warning "Verification always queries pre-production"
    The selector calls `getActiviteitDetail(urn)` without an `env` argument, so it falls back
    to the `pre` default and **ignores the DSO environment toggle in Settings**. A URN that
    exists only in production will report "URN not found in DSO" here no matter which
    environment is selected — verify it in the DSO Explorer's Activities tab instead.

---

## Phase plan

The integration is delivered in phases. The detailed plan, current status, confirmed test anchors, and remaining work for each phase are tracked in [DSO Integration Phase Plan](dso-integration-phase-plan.md). Phases 1–3 are live as of v1.5.3; Phase 2a/2d and Phase 4 (STTR → DMN/form extraction, Import into LDE, and the DMN publish handoff) landed across v1.9.3–v1.9.5.

---

## Related documentation

- [DSO Viewer APIs — Slide Deck](dso-viewer-apis-deck.md) — the twelve-slide summary, plus the PDF
- [DSO Explorer user guide](../user-guide/dso-explorer.md) — step-by-step search and link workflow
- [DSO Integration Phase Plan](dso-integration-phase-plan.md) — phase status, test anchors, implementation order
- [BPMN Modeler — DSO activiteit linkage](bpmn-modeler.md#dso-activiteit-linkage)