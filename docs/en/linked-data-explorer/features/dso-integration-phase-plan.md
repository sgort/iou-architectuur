# DSO Integration — Phase Plan & Test Guidance

## Phased approach

The end goal is a **DSO-driven AWB process bundle**: given a location and a werkzaamheid, LDE produces a deployable Operaton package — BPMN subprocess + DMN + form schema + document template — all seeded from authoritative DSO source data rather than authored by hand.

### The data flow that makes this possible

```
Werkzaamheid (what someone wants to do)
    ↓  linked to
Activiteit (the legal activity at that location)
    ↓  has
Regelbeheerobjecten
    ├── indieningsvereisten  →  Form fields (what must be submitted)
    ├── conclusie            →  DMN decision logic (what the authority decides)
    └── maatregelen          →  Document template variables (conditions in the beschikking)
    ↓  governed by
BPMN subprocess (the AWB procedural shell wrapping all of the above)
```

### Phase 1 — Navigate ✅ Done (v1.5.0 / v1.5.2)

Browse and understand what is inside a DSO activity before trying to use it.

- DSO Explorer panel in LDE sidebar
- Concepts tab: full-text search across the Stelselcatalogus
- Activities tab: paginated list of RTR activiteiten, date-filterable
- Activity Detail panel: omschrijving, authority, validity, rule types present, child activities, locations
- Parent and child activity navigation within the detail panel
- Location presets (Lelystad, Flevoland) filtered by authority OIN
- URN paste-to-inspect for any activiteit
- DSO environment toggle (pre-production / production) in Settings, independent of LDE environment
- DSO activiteit URN linkable to a BPMN subprocess via `ronl:dsoActiviteitUrn` moddleExtension

### Phase 2 — Locate (next)

Filter by location, because the same werkzaamheid yields different activiteiten depending on where the project is.

- Address or coordinate input → resolved geometry
- `POST /activiteiten/_zoek` with bounding box — location-scoped results
- `POST /regelbeheerobjectedtypen` (Samengestelde services) — for a werkzaamheid + location, determine which rule object types are actually present
- This is the key gating call before any generation step: it tells you whether `indieningsvereisten`, `conclusie`, and `maatregelen` are all available

### Phase 3 — Map (partially done in v1.5.0)

Bridge the DSO data model to LDE's asset model.

- ✅ `ronl:dsoActiviteitUrn` moddleExtension on `bpmn:Process` — persisted in BPMN XML
- ✅ `DsoActiviteitSelector` in BPMN Modeler footer panel: paste URN, verify live against DSO, save to process
- ✅ Direct link to activity in RTR viewer after verification
- Pending: expose `indieningsvereisten` as a structured checklist in the BPMN properties panel
- Pending: show rule object type badges (✓ Form ✓ Decision ✓ Document) on the subprocess element

### Phase 4 — Generate

Turn DSO metadata into LDE asset scaffolds.

- **Form scaffold** — from `indieningsvereisten` fields, generate a form-js JSON schema with one field per requirement; field types inferred from DSO data types
- **DMN scaffold** — from `conclusie` criteria, generate a DMN table skeleton: one input column per criterion, one output column for the decision result, hit policy FIRST
- **Document template scaffold** — from `maatregelen`, generate a beschikking template with one zone per measure, variable bindings pre-populated from DMN output names
- **BPMN subprocess scaffold** — complete subprocess XML wired to the generated form, DMN, and document template via existing `ronl:` moddleExtensions

### Phase 5 — Deploy

Package and ship to Operaton.

- Wire the generated subprocess into the AWB shell as a call activity (done in Camunda Modeler)
- Use the existing LDE deploy bundle mechanism to package BPMN + DMN + form refs + document template
- Deploy to Operaton — the process is runnable

---

## Current state — v1.5.1 / v1.5.2

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

This is the activity that grounds the existing `TreeFellingPermitSubProcess` in DSO. It can be pasted into the URN inspector or linked to the subprocess via `DsoActiviteitSelector` in the BPMN Modeler.

### Lelystad equivalent (production only)

- **URL pattern:** `omgevingswet.overheid.nl/registratie-toepasbare-regels/id/nl.imow-gm0995.activiteit.HoutopstandVellen`
- Available in **production DSO only** — not in pre-production
- Switch to production in Settings before searching

---

## Things worth paying attention to while testing

### DSO data coverage

- Which authorities in Flevoland/Lelystad have **published toepasbare regels** to production? Activities with `None registered` under Rule Types Present are in the RTR taxonomy but have not yet attached rule objects. These are not yet useful for Phase 4.
- Look specifically for activities that show **all three rule types** (`conclusie` + `indieningsvereisten` + `maatregelen`) — these are the candidates for Phase 4 generation.
- Note any activity URN that has `conclusie` in production and is relevant to the AWB + kapvergunning scope.

### datumVanaf behaviour

- The Lelystad/Flevoland preset uses yesterday as `datumVanaf`. Try changing the date to earlier periods (e.g. 01-01-2024) to see historical activity registrations. Some activities may only appear from a certain date onwards.
- If a preset returns an empty list, try an earlier date — the authority may have published before yesterday's cutoff.

### Cross-environment URN gaps

- URNs that appear in the Lelystad/Flevoland preset list in production may not exist in pre-production. The detail panel will show a clear message if this happens. This is expected — pre-production has a subset of production data.
- Switch to production DSO to verify Lelystad activity details.

### Child activity navigation

- The detail panel shows child activities with human-readable names (fetched in parallel). For large lists (20+ children), names appear progressively. Verify names are correct and match what DSO shows in the RTR viewer.
- Parent activity navigation (clicking the parent URN in the detail panel) should walk up the taxonomy. Verify the hierarchy makes sense: leaf activity → thematic group → `ActInOmgevingsplan` → national root.

### BPMN linking

- Open `TreeFellingPermitSubProcess` in the BPMN Modeler. Scroll down in the left panel past the RoPA selector to find the DSO Activity section.
- Paste `nl.imow-gm0014.activiteit.1d52a3b09a7a4b2f846ae1e171f6678d` and press Verify.
- Confirm it shows "boom kappen · gemeente GM0014" and the RTR link is correct.
- Save and verify the `ronl:dsoActiviteitUrn` attribute appears in the BPMN XML.
