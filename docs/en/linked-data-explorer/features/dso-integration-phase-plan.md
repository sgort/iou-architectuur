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

Every regelBeheerobject on an activity carries a `functioneleStructuurRef`. This reference links the RTR activity taxonomy to the actual applicable rule files (STTR) in the Uitvoeren Gegevens API. The Zoekinterface returns it directly alongside each werkzaamheid result — visible in the Works tab as the `ref:` line on each row. The Activity Detail panel shows rule types present; the `functioneleStructuurRef` per rule type is returned by the RTR detail call and is the input to Step 1 of the next cycle.

The `functioneleStructuurRef` is a full concept URI. Two formats exist:

- **Zoekinterface** (werkzaamheid-level): `http://toepasbare-regels.omgevingswet.overheid.nl/werkzaamheden/id/concept/GebouwPlaatsen`
- **RTR detail** (regelBeheerobject-level): `http://toepasbare-regels.omgevingswet.overheid.nl/00000001005024249000/id/concept/Conclusienl.imow-gm0995.activiteit.a42ec23b8e4d464b8d32a1e88ac6d4cd`

Both are passed to `GET /toepasbareRegels?functioneleStructuurRef=...` in Phase 4 — the authority-scoped format from the RTR detail is the more precise one.

---

## APIs involved

### Already integrated

| API | Version | Used for |
|---|---|---|
| RTR CRUD (raadplegen) | v2 | Activity list, detail, OIN-based browse via `_zoek` with `bestuursorgaan.oin` |
| Catalogus opvragen | v3 | Concepts search |
| Zoekinterface | v2.2.3 | Werkzaamheden search + autocomplete, `functioneleStructuurRef` retrieval |
| Opvragen Werkzaamheden | v1 | Werkzaamheid version history |

### Pending integration

| API | Version | Key capability |
|---|---|---|
| Uitvoeren Gegevens | v1 | STTR file metadata + download by `functioneleStructuurRef` |
| Samengestelde RTR services | v2 | Rule type completeness check for werkzaamheid + location |

### STTR standard (XSD)

| XSD | Relevant content |
|---|---|
| `Bedrijfsregel_v2.xsd` | Root envelope: `<sttr versie="3">` + `<functioneleStructuurRef href="..."/>` |
| `Content_v2.xsd` | `maatregel` elements (nummer, maatregeltekst, toelichting, frequentie, volgorde, kenmerk, thema) |
| `DMN_v12.xsd` | Full DMN 1.2 schema — the `conclusie` STTR file embeds a complete DMN decision model |

**The critical insight:** an STTR file for a `conclusie` regelBeheerobject **is** a DMN file in an STTR envelope. Strip the envelope, register the DMN — it is deployable via the existing LDE bundle mechanism.

### Known DSO API quirks

- **Opvragen Werkzaamheden `_expandScope`:** the spec documents `logischeRelaties` as the valid enum value but the runtime rejects both `logischeRelaties` and `LogischeRelaties`. `_expand=true` without `_expandScope` is also rejected. Current workaround: call without expand — returns version history with omschrijving and dates only. Keywords and logical relations pending until the correct enum value is confirmed with DSO support.
- **RTR `_wijzigingen`:** is a **delta sync endpoint**, not a browse endpoint. It returns activities that changed since `datumVanaf`, not activities valid on a date. Empty results for recent dates are expected if nothing changed. Replaced by `POST /activiteiten/_zoek` with `bestuursorgaan.oin` for all OIN-based browsing in LDE.
- **Manual date format:** `dd-MM-yyyy` throughout — no `Intl` dependency due to Azure App Service locale issues.
- **`functioneleStructuurRef` format:** two variants exist (see above). The authority-scoped RTR detail format is needed for the Uitvoeren Gegevens lookup in Phase 4.

### What each rule type yields from the STTR

| Rule type | STTR content | LDE asset |
|---|---|---|
| `conclusie` | Full DMN decision model embedded in STTR envelope | Import as `.dmn`, deploy to Operaton via existing bundle mechanism |
| `indieningsvereisten` | DMN questionnaire logic (questions, options, conditions) | Form field scaffold — each question → form-js field |
| `maatregelen` | `<maatregel>` elements with nummer, maatregeltekst, toelichting, frequentie | Document template zones — each maatregel → beschikking section |

---

## Phased approach

### Phase 1 — Navigate ✅ Done (v1.5.0 / v1.5.3)

- DSO Explorer panel with Concepts, Works, and Activities tabs
- Concepts tab: full-text search across the Stelselcatalogus
- Works tab: Zoekinterface-backed werkzaamheden search with autocomplete, version history in detail panel, `functioneleStructuurRef` visible per result
- Activities tab: RTR activiteiten list with OIN presets (Lelystad, Flevoland) via `_zoek` + `bestuursorgaan.oin`, date filtering, activity detail panel with child/parent navigation, rule types present badges
- DSO environment toggle (pre-production / production) in Settings, independent of LDE environment
- DSO activiteit URN linkable to BPMN subprocess via `ronl:dsoActiviteitUrn` moddleExtension

### Phase 2 — Locate (next)

Find the right activity and confirm its rule content is available before attempting generation.

**Step 2a — Applicable Rules panel in Activity Detail** (Uitvoeren Gegevens) ← **highest priority**
- When `conclusie` or `indieningsvereisten` is present, call `GET /toepasbareRegels?functioneleStructuurRef=...` using the authority-scoped URI from the RTR detail response
- Show metadata: STTR version, authority OIN, validity, aansluitpunt name, `modelName`, `decisionName`
- Download STTR XML button
- Import into LDE button (Phase 4 trigger)

**Step 2b — Works tab → Applicable Rules shortcut**
- Each werkzaamheid result carries `functioneleStructuurRef` — wire a "View applicable rules" action that calls the Uitvoeren Gegevens API directly, without navigating through the activity hierarchy

**Step 2c — Rule type completeness check** (Samengestelde services)
- `POST /regelbeheerobjectedtypen` for a werkzaamheid + location: confirm which rule types are present before attempting generation

### Phase 3 — Map (partially done in v1.5.0 / v1.5.3)

- ✅ `ronl:dsoActiviteitUrn` moddleExtension on `bpmn:Process` — persisted in BPMN XML
- ✅ `DsoActiviteitSelector` in BPMN Modeler footer: paste URN, verify live, save to process
- ✅ Direct link to RTR viewer after verification
- Pending: `indieningsvereisten` checklist in BPMN properties panel
- Pending: rule object type badges on subprocess element (✓ Form ✓ Decision ✓ Document)

### Phase 4 — Generate

**Step 4.1 — DMN import from STTR** (`conclusie`) ← entry point after Step 2a
- Backend parses STTR XML, extracts `<definitions>` element, returns as DMN
- "Import into LDE" button registers the DMN as a new asset linked to the subprocess
- Filter: `sttrBestandInhoudFilter=herbruikbareBeslissing` targets directly importable reusable decisions

**Step 4.2 — Form scaffold from STTR** (`indieningsvereisten`)
- Each question node in the questionnaire DMN → form-js field
- Field type inferred from DSO data type

**Step 4.3 — Document template scaffold from STTR** (`maatregelen`)
- Each `<maatregel>` → beschikking document zone: `maatregeltekst` → label, `toelichting` → body

**Step 4.4 — BPMN subprocess scaffold**
- Complete subprocess XML wired to imported DMN, form, and document template via `ronl:` moddleExtensions

### Phase 5 — Deploy

- Wire subprocess into AWB shell as call activity (Camunda Modeler)
- Deploy bundle via existing LDE mechanism: BPMN + DMN + form refs + document template
- Process runnable in Operaton with DSO-authoritative rule content

---

## Implementation order for the next development cycle

| Step | API | Deliverable |
|---|---|---|
| 1 | Uitvoeren Gegevens | `GET /v1/dso/toepasbare-regels?functioneleStructuurRef=...` backend route |
| 2 | Uitvoeren Gegevens | `GET /v1/dso/toepasbare-regels/:id/sttr` backend route (raw XML) |
| 3 | Uitvoeren Gegevens | Applicable Rules section in Activity Detail panel (metadata + Download) |
| 4 | Uitvoeren Gegevens | STTR → DMN extraction; "Import into LDE" button |
| 5 | Opvragen Werkzaamheden | Resolve correct `_expandScope` enum value with DSO support; add keywords + logical relations to Works detail panel |
| 6 | Zoekinterface | "View applicable rules" action on werkzaamheid list row |
| 7 | Content_v2.xsd | Maatregel extraction → document template scaffold |
| 8 | Samengestelde services | Rule type completeness check for werkzaamheid + location |

Steps 1–4 are the highest value items and unlock Phase 4 for `conclusie`.

---

## Current state — v1.5.3

### What is deployed and working

| Capability | Status |
|---|---|
| DSO Concepts tab (Stelselcatalogus) | ✅ Live |
| DSO Works tab — search + autocomplete + version history | ✅ Live |
| DSO Activities tab — default list | ✅ Live |
| DSO Activity Detail panel | ✅ Live |
| Authority presets (Lelystad, Flevoland) via OIN + `_zoek` | ✅ Live |
| Date-filtered authority list | ✅ Live |
| DSO environment toggle (pre/prod) | ✅ Live |
| DSO activiteit URN on BPMN subprocess | ✅ Live |
| Live URN verification against DSO RTR | ✅ Live |
| Child activity names in detail panel | ✅ Live |
| Graceful 404 for cross-environment URNs | ✅ Live |
| Werkzaamheid keywords + logical relations | ⏳ Pending (_expandScope enum resolution) |
| Applicable Rules (STTR) in detail panel | ⏳ Pending (Step 2a next cycle) |
| STTR → DMN import | ⏳ Pending (Step 4.1 next cycle) |

### Confirmed Phase 4 candidate — "Bed & Breakfast starten" (Lelystad, production)

The first confirmed activity in production with both `Conclusie` and `Indieningsvereisten` present:

- **omschrijving:** Bed & Breakfast starten
- **URN:** `nl.imow-gm0995.activiteit.a42ec23b8e4d464b8d32a1e88ac6d4cd`
- **Authority:** gemeente (GM) · code 0995 · OIN `00000001005024249000`
- **Validity:** from 09-07-2025 · no end date
- **Rule types:** Indieningsvereisten ✅ + Conclusie ✅
- **Conclusie `functioneleStructuurRef`:** `http://toepasbare-regels.omgevingswet.overheid.nl/00000001005024249000/id/concept/Conclusienl.imow-gm0995.activiteit.a42ec23b8e4d464b8d32a1e88ac6d4cd`
- **Indieningsvereisten `functioneleStructuurRef`:** `http://toepasbare-regels.omgevingswet.overheid.nl/00000001005024249000/id/concept/IndieningsvereistenVergunningnl.imow-gm0995.activiteit.a42ec23b8e4d464b8d32a1e88ac6d4cd`
- **Note:** `toonbaar: false` — not visible in the public Omgevingsloket but fully queryable via the API

These two `functioneleStructuurRef` values are the direct inputs to Step 1 of the next development cycle.

### Test anchor: "boom kappen" in gm0014 (Groningen, pre-production)

- **URN:** `nl.imow-gm0014.activiteit.1d52a3b09a7a4b2f846ae1e171f6678d`
- **Authority:** gemeente (GM) · code 0014
- **Validity:** from 30-01-2024 · no end date
- **Rule types:** Conclusie ✅

### Lelystad "HoutopstandVellen" (production only)

- `nl.imow-gm0995.activiteit.HoutopstandVellen` — switch to production in Settings before searching

---

## Things worth paying attention to while testing

### Works tab

- Search is sorted by `meestGekozen` by default — most-used Omgevingsloket werkzaamheden appear first
- The `ref:` line is the `functioneleStructuurRef` full URI — this is what gets passed to the Uitvoeren Gegevens API in Phase 4
- The short URN at the bottom of each row (e.g. `GebouwPlaatsen`) is the Opvragen Werkzaamheden identifier — different from the `ref:` URI, both are needed
- Keywords and logical relations are not yet shown in the detail panel (pending `_expandScope` enum resolution with DSO support)

### Activities tab — OIN presets

- Presets now use `_zoek` with `bestuursorgaan.oin` — results are activities valid on the selected date, not a change log
- Date defaults to today; changing the date and pressing Load reloads the authority list for that date
- Activities with `None registered` under Rule Types Present have no STTR files — not Phase 4 candidates
- Look for activities showing `Conclusie` and/or `Indieningsvereisten` — these are the Phase 4 candidates

### Rule type coverage

- `Conclusie` is the highest priority: if present, a STTR with an embedded DMN exists and is directly importable
- Activities with all three types (`conclusie` + `indieningsvereisten` + `maatregelen`) are the ideal complete Phase 4 candidates

### Cross-environment URN gaps

- Production-only activities will show the graceful "not available in pre-production" message when pre-production is selected in Settings

### BPMN linking

- Open `TreeFellingPermitSubProcess` in the BPMN Modeler, scroll below the RoPA selector to the DSO Activity section
- Paste `nl.imow-gm0014.activiteit.1d52a3b09a7a4b2f846ae1e171f6678d` and press Verify
- Confirm "boom kappen · gemeente GM0014" and save
- Verify `ronl:dsoActiviteitUrn` appears in the BPMN XML