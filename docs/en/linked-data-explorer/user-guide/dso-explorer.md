# DSO Explorer

A step-by-step walkthrough for searching the Digitaal Stelsel Omgevingswet from inside LDE and linking the result to a BPMN subprocess. For the architectural overview and API surface, see [DSO Integration](../features/dso-integration.md).

---

## Before you start

- Open LDE and navigate to the **DSO Explorer** view in the sidebar (the globe icon).
- Decide which DSO environment you need. Most authority data is published in pre-production first; production carries the authoritative live ruleset. Test anchors per environment are listed in [DSO Integration Phase Plan](../features/dso-integration-phase-plan.md#current-state--v153).
- Confirm the environment in **Settings → DSO environment**. The header badge turns amber for pre-production, green for production.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Settings panel open over the DSO Explorer with the DSO environment section visible — two radio options labelled Pre-production (default) and Production, with the Pre-production radio currently selected](../../assets/screenshots/linked-data-explorer-dso-settings-panel.png)
  <figcaption>Switching the DSO environment in Settings</figcaption>
</figure>

The setting persists in localStorage — closing and reopening LDE keeps the same environment.

---

## Workflow 1 — Find a werkzaamheid by citizen-facing name

Use this when you know the public name of the task (the term a citizen would use on the Omgevingsloket) but not the underlying URN.

1. Open the **Works** tab.
2. Start typing — autocomplete suggestions appear after two characters. The list is sorted by `meestGekozen`, so the most-used Omgevingsloket terms surface first.
3. Pick a suggestion or hit Enter to run the full search.
4. Click a result to open the detail panel. The panel shows the current version's omschrijving, validity period, and the full version history with start/end dates.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Works tab showing the detail panel open for a selected werkzaamheid — heading with the omschrijving, a metadata row with begindatum and a current badge, the functioneleStructuurRef URI on its own line, and below that a Version history section with three rows each showing a date range and one marked current](../../assets/screenshots/linked-data-explorer-dso-works-detail.png)
  <figcaption>Werkzaamheid detail panel with version history</figcaption>
</figure>

The `functioneleStructuurRef` URI on each result is the pivot to the STTR file used in the upcoming Phase 4 import. Copy it now if you'll be linking it to a BPMN subprocess later.

---

## Workflow 2 — Browse activiteiten by authority

Use this when you know which authority publishes the activity (e.g. gemeente Lelystad) and want to see what they have on a given date.

1. Open the **Activities** tab.
2. Pick an authority preset — **Lelystad** or **Flevoland**.
3. The date input defaults to today; change it if you need a historical view.
4. Click **Load**. The list refreshes with that authority's activiteiten valid on the selected date.

Each card shows badges for which rule types are present:

- **Conclusie** — DMN decision content available
- **Indieningsvereisten** — application questionnaire available
- **Maatregelen** — textual measures available

The badges tell you ahead of time which downstream LDE assets the activity can support.

5. Click an activity card to open the detail panel.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Activities tab with the Lelystad preset selected, todays date shown in the date input, and a list of activity cards beneath — each card has the omschrijving, validity from-date, and small green pill badges for the rule types present, with the Bed & Breakfast starten card highlighted to show it has both Conclusie and Indieningsvereisten](../../assets/screenshots/linked-data-explorer-dso-activities-with-badges.png)
  <figcaption>Activities filtered by Lelystad with rule-type badges</figcaption>
</figure>

---

## Workflow 3 — Verify a URN you already have

Use this when someone has handed you a DSO URN and you need to confirm it resolves and see what it points to.

1. Open a BPMN process in the **BPMN Modeler**.
2. Scroll to the **DSO Activity** section in the footer panel.
3. Paste the URN into the input.
4. Click **Verify**. LDE queries the live DSO RTR.
   - On success, a teal info card appears below showing the omschrijving, the authority block, and a link icon that opens the URN in the public DSO RTR viewer.
   - On 404, a red error appears: "URN not found in DSO". Check the environment toggle — the URN may exist only in production.
5. The URN is persisted as `ronl:dsoActiviteitUrn` on the BPMN process when you click **Save** in the canvas toolbar.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: BPMN Modeler with the footer DSO Activity section showing a URN field with a Lelystad URN entered, the Verify button just clicked, and below it the teal verification card showing the activity omschrijving, the authority block on three lines (gemeente Lelystad GM 0995), and an external-link icon link to the RTR viewer](../../assets/screenshots/linked-data-explorer-dso-verify-bpmn.png)
  <figcaption>Verifying a URN against the live DSO RTR</figcaption>
</figure>

If you switch DSO environments after verifying, re-verify — a URN that resolved in pre-production may 404 in production.

---

## Common situations

**An activity card has only Indieningsvereisten — no Conclusie.** That activity has questionnaire logic but no full decision model. You can still link it to a BPMN subprocess, but Phase 4 will only generate a form scaffold, not a DMN.

**The detail panel shows "not available in this environment".** The URN was queried with the wrong DSO environment toggle. Switch in Settings and try again.

**A werkzaamheid result shows no `ref:` line.** The Zoekinterface didn't return a `functioneleStructuurRef` for that werkzaamheid version. Try a different version from the version history, or contact the publishing authority — the activity may not yet carry a structuur reference.

**Authority preset Load button gives an empty list.** Either the authority has no activities for that date, or the date is outside the validity windows of all activities. Try a recent date close to today.

---

## Related documentation

- [DSO Integration](../features/dso-integration.md) — overview of the three APIs and what each enables
- [DSO Integration Phase Plan](../features/dso-integration-phase-plan.md) — current phase status and test anchors
- [BPMN Modeler — DSO activiteit linkage](../features/bpmn-modeler.md#dso-activiteit-linkage)