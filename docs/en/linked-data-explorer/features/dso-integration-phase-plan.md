# DSO Integration — Phase Plan & Test Guidance

## End goal

A **DSO-driven AWB process bundle**: given a location and a werkzaamheid, LDE produces a deployable Operaton package — BPMN subprocess + DMN + form schema + document template — all seeded from authoritative DSO source data rather than authored by hand.

---

## The data flow that makes this possible

```
Werkzaamheid (what someone wants to do)
    ↓  linked to
Activiteit (the legal activity at that location)
    ↓  has
Regelbeheerobjecten
    ├── indieningsvereisten  →  STTR file → Form fields (what must be submitted)
    ├── conclusie            →  STTR file → DMN decision model (what the authority decides)
    └── maatregelen          →  STTR file → Document template (conditions in the beschikking)
    ↓  governed by
BPMN subprocess (the AWB procedural shell wrapping all of the above)
```

### The `functioneleStructuurRef` is the pivot

Every regelBeheerobject on an activity carries a `functioneleStructuurRef`. This reference is the key that links the RTR activity taxonomy to the actual applicable rule files (STTR) in the Uitvoeren Gegevens API. Without it you can browse activities; with it you can retrieve and import their rule content.

---

## APIs involved

### Already integrated

| API | Version | Used for |
|---|---|---|
| RTR CRUD (raadplegen) | v2 | Activity list, detail, OIN-based browse |
| Catalogus opvragen | v3 | Concepts search |
| Samengestelde RTR services | v2 | (Planned) rule type determination by location |

### New

| API | Version | Key capability |
|---|---|---|
| Zoekinterface | v2.2.3 | Human-intent search: type "boom kappen" → get activities + `functioneleStructuurRef` directly |
| Uitvoeren Gegevens | v1 | STTR file metadata + download by `functioneleStructuurRef` or identifier |

### STTR standard (XSD)

The STTR XML file is the applicable rule file stored in the RTR. Its structure, defined by the XSD files, determines exactly what LDE can extract:

| XSD | Relevant content |
|---|---|
| `Bedrijfsregel_v2.xsd` | Root envelope: `<sttr versie="3">` + `<functioneleStructuurRef href="..."/>` |
| `Content_v2.xsd` | `maatregel` elements (nummer, maatregeltekst, toelichting, frequentie, volgorde, kenmerk, thema) — structured measure content for beschikking templates |
| `DMN_v12.xsd` | Full DMN 1.2 schema — the `conclusie` STTR file embeds a complete DMN decision model |

**The critical insight:** an STTR file for a `conclusie` regelBeheerobject **is** a DMN file in an STTR envelope. The aansluitpunt metadata (`modelName`, `decisionName`) identifies the Operaton entry point decision. Strip the envelope, register the DMN — it is deployable as-is via the existing LDE bundle mechanism.

### Zoekinterface key details

- `POST /werkzaamheden/_zoek` — full-text search for werkzaamheden, returns `functioneleStructuurRef`
- `POST /werkzaamheden/_suggereer` — autocomplete suggestions while typing
- `POST /activiteiten/_zoek` — search activities that have `indieningsvereisten` rules, filterable by `datum`, `locaties` (geometry IDs), `bestuurslagen`, `toestemmingen`
- `ActiviteitResponse` returns `urn`, `omschrijving`, `functioneleStructuurRef`, `bestuursorgaan`, `locaties` — richer than the RTR list endpoint
- Sorting: `meestGekozen` (default — surfaces most-used Omgevingsloket activities first), `besteMatch`, `alfabetisch`

### Uitvoeren Gegevens key details

- `GET /toepasbareRegels?functioneleStructuurRef=...` — list applicable rules for an activity
- `GET /toepasbareRegels/{identifier}/sttrBestand` — download STTR XML (`application/xml`)
- `sttrBestandInhoudFilter=herbruikbareBeslissing` — filter for STTR files containing a reusable DMN decision (directly importable as Operaton decision definition)
- **Aansluitpunt / aansluiting model:** an aansluitpunt (connection point) is the base rule set for a bestuurslaag with `naam`, `modelName`, `decisionName`; aansluitingen are authority-specific additions to the aansluitpunt

### What each rule type yields from the STTR

| Rule type | STTR content | LDE asset |
|---|---|---|
| `conclusie` | Full DMN decision model embedded in STTR envelope | Import as `.dmn`, deploy to Operaton via existing bundle mechanism |
| `indieningsvereisten` | DMN questionnaire logic (questions, options, conditions) | Form field scaffold — each question → form-js field |
| `maatregelen` | `<maatregel>` elements with nummer, maatregeltekst, toelichting, frequentie | Document template zones — each maatregel → beschikking section |

---

## Phased approach

### Phase 1 — Navigate ✅ Done (v1.5.0 / v1.5.2)

Browse and understand what is inside a DSO activity before trying to use it.

- DSO Explorer panel in LDE sidebar (Concepts + Activities tabs)
- Activity Detail panel: omschrijving, authority, validity, rule types present, child/parent navigation, locations
- Authority presets (Lelystad, Flevoland) filtered by OIN via `_wijzigingen`
- URN paste-to-inspect, date-filterable lists, datumVanaf for OIN presets
- DSO environment toggle (pre-production / production) in Settings, independent of LDE environment
- DSO activiteit URN linkable to a BPMN subprocess via `ronl:dsoActiviteitUrn` moddleExtension + live verification

### Phase 2 — Locate (revised scope)

Find the right activity and confirm its rule content is available, using the Zoekinterface API as the primary entry point.

**Step 2a — Werkzaamheden search tab** (Zoekinterface)
- Full-text search for werkzaamheden by user intent ("boom kappen")
- Autocomplete suggestions while typing
- Results carry `functioneleStructuurRef` directly — no taxonomy navigation needed
- Each result links to Activity Detail

**Step 2b — Applicable Rules panel in Activity Detail** (Uitvoeren Gegevens)
- When a `conclusie` or `indieningsvereisten` regelBeheerobject is present, show the applicable rules registered for that activity via `functioneleStructuurRef`
- Metadata: STTR version, authority OIN, validity period, aansluitpunt name, `modelName`, `decisionName`
- Download STTR XML button
- Import into LDE button (Phase 4 trigger)

**Step 2c — Rule type completeness check** (Samengestelde services)
- `POST /regelbeheerobjectedtypen` for a werkzaamheid + location: confirm which of `conclusie`, `indieningsvereisten`, `maatregelen` are actually present before attempting generation

### Phase 3 — Map (partially done in v1.5.0 / v1.5.2)

Bridge the DSO data model to LDE's asset model.

- ✅ `ronl:dsoActiviteitUrn` moddleExtension on `bpmn:Process` — persisted in BPMN XML
- ✅ `DsoActiviteitSelector` in BPMN Modeler footer: paste URN, verify live, save to process
- ✅ Direct link to RTR viewer after verification
- Pending: `indieningsvereisten` checklist in BPMN properties panel
- Pending: rule object type badges on subprocess element (✓ Form ✓ Decision ✓ Document)

### Phase 4 — Generate

Turn DSO/STTR content into LDE asset scaffolds. Implementation order:

**Step 4.1 — DMN import from STTR** (`conclusie`)
Backend parses STTR XML, extracts `<definitions>` element, returns as DMN. Frontend "Import into LDE" button in the Applicable Rules panel registers the DMN as a new asset linked to the subprocess via existing `ronl:` moddleExtensions. Uses `sttrBestandInhoudFilter=herbruikbareBeslissing` to target directly importable files.

**Step 4.2 — Form scaffold from STTR** (`indieningsvereisten`)
Parse the questionnaire DMN in the STTR file. Each question node becomes a form-js field; field type inferred from DSO data type. Starting point for caseworker refinement, not final.

**Step 4.3 — Document template scaffold from STTR** (`maatregelen`)
Parse `<maatregel>` elements from `Content_v2.xsd` structure. Each maatregel becomes a beschikking document zone: `maatregeltekst` → zone label, `toelichting` → zone body, `kenmerk` / `thema` → zone metadata.

**Step 4.4 — BPMN subprocess scaffold**
Generate a complete subprocess XML wired to the imported DMN, form, and document template via existing `ronl:` moddleExtensions, with `ronl:dsoActiviteitUrn` pre-populated.

### Phase 5 — Deploy

Package and ship to Operaton.

- Wire the generated subprocess into the AWB shell as a call activity (done in Camunda Modeler)
- Use the existing LDE deploy bundle mechanism: BPMN + DMN + form refs + document template
- Deploy to Operaton — the process is runnable with DSO-authoritative rule content

---

## Suggested implementation order for the next development cycle

| Step | API | Deliverable |
|---|---|---|
| 1 | Uitvoeren Gegevens | `GET /v1/dso/toepasbare-regels?functioneleStructuurRef=...` backend route |
| 2 | Uitvoeren Gegevens | `GET /v1/dso/toepasbare-regels/:id/sttr` backend route (returns raw XML) |
| 3 | Uitvoeren Gegevens | Applicable Rules section in Activity Detail panel (metadata + Download button) |
| 4 | Uitvoeren Gegevens | STTR → DMN extraction in backend; "Import into LDE" button in detail panel |
| 5 | Zoekinterface | Werkzaamheden search tab with autocomplete |
| 6 | Zoekinterface | Activiteiten search via Zoekinterface (indieningsvereisten-scoped) as alternative to RTR browse |
| 7 | Content_v2.xsd | Maatregel extraction → document template scaffold |
| 8 | Samengestelde services | Rule type completeness check for werkzaamheid + location |

Steps 1–4 unlock Phase 4 for `conclusie` and are the highest value items. Steps 5–6 complete Phase 2 from the user's perspective. Steps 7–8 complete Phase 4 for the remaining rule types.

---

## Current state — v1.5.2

Phase 1 is complete. Phase 3 is partially done. Phases 2, 4, and 5 are pending.

### What is deployed and working

| Capability | Status |
|---|---|
| DSO Concepts tab (Stelselcatalogus) | ✅ Live |
| DSO Activities tab — default list | ✅ Live |
| DSO Activity Detail panel | ✅ Live |
| Authority presets (Lelystad, Flevoland) via OIN | ✅ Live |
| Date-filtered authority list via datumVanaf | ✅ Live |
| DSO environment toggle (pre/prod) | ✅ Live |
| DSO activiteit URN on BPMN subprocess | ✅ Live |
| Live URN verification against DSO RTR | ✅ Live |
| Child activity names in detail panel | ✅ Live |
| Graceful 404 for cross-environment URNs | ✅ Live |

### Test anchor: "boom kappen" in gm0014 (Groningen)

The canonical test activity confirmed in pre-production:

- **omschrijving:** boom kappen
- **URN:** `nl.imow-gm0014.activiteit.1d52a3b09a7a4b2f846ae1e171f6678d`
- **Authority:** gemeente (GM) · code 0014
- **Validity:** from 30-01-2024 · no end date
- **Rule types:** Conclusie ✅ — decision logic is registered

This activity grounds the existing `TreeFellingPermitSubProcess` in DSO. Its `functioneleStructuurRef` (retrievable via the Zoekinterface) will be the first input to Step 1 of the next development cycle.

### Lelystad equivalent

- **URL pattern:** `omgevingswet.overheid.nl/registratie-toepasbare-regels/id/nl.imow-gm0995.activiteit.HoutopstandVellen`

---

## Things worth paying attention to while testing

### Rule type coverage

- Activities with `None registered` under Rule Types Present are in the RTR taxonomy but have no STTR files yet — not candidates for Phase 4.
- Look specifically for activities showing **all three rule types** (`conclusie` + `indieningsvereisten` + `maatregelen`) — these are the complete Phase 4 candidates.
- The `conclusie` type is the most important: if present, a STTR file with an embedded DMN exists and can be imported directly.

### datumVanaf behaviour

- The Lelystad/Flevoland preset uses yesterday as `datumVanaf`. Try earlier dates (e.g. `01-01-2024`) to see historical registrations — some activities may predate the default cutoff.

### Cross-environment URN gaps

- URNs from the Lelystad/Flevoland OIN preset in production may 404 in pre-production. Expected — pre-production has a subset of production data. The detail panel shows a clear message when this happens.

### Child activity navigation

- Names appear progressively (parallel fetch). For large child lists (20+), verify names match the RTR viewer.
- Hierarchy should walk: leaf activity → thematic group → `ActInOmgevingsplan` → national root.

### BPMN linking

- Open `TreeFellingPermitSubProcess` in the BPMN Modeler. Scroll below the RoPA selector to the DSO Activity section.
- Paste `nl.imow-gm0014.activiteit.1d52a3b09a7a4b2f846ae1e171f6678d` and press Verify.
- Confirm it shows "boom kappen · gemeente GM0014" and the RTR link resolves correctly.
- Save and verify `ronl:dsoActiviteitUrn` appears in the BPMN XML.

### What to capture during the user session

- The `functioneleStructuurRef` for any activity that has `conclusie` — this is Step 1 input for the next development cycle
- Whether the Lelystad `HoutopstandVellen` activity in production has `conclusie` present and what its `functioneleStructuurRef` is
- Whether any activity shows all three rule types (`conclusie` + `indieningsvereisten` + `maatregelen`) — that is the ideal candidate for Phases 4 and 5
