# Multilingualism

A step-by-step walkthrough for tagging design artefacts with a language and organization, importing translated artefacts, and working with the HR-capacity Dutch reference bundle. For the architectural overview, see [Multilingualism](../features/multilingualism.md).

---

## Workflow 1 — Tag an existing artefact

1. Open the artefact in its editor (BPMN Modeler, Form Editor, or Document Composer).
2. Scroll to the footer panel below the list.
3. **Language** — pick from the dropdown: Language-agnostic (default), English, Dutch, German.
4. **Organization** — type the key, or pick from the autocomplete suggestions populated from existing organizations.
5. Click **Save** in the canvas toolbar. The artefact is committed and the list panel regroups it under the new organization header.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: BPMN Modeler footer panel zoomed in showing the Language section open as a dropdown with the four options visible — Language-agnostic, English (English), Dutch (Nederlands), German (Deutsch) — and Dutch (Nederlands) about to be selected](../../assets/screenshots/linked-data-explorer-language-dropdown.png)
  <figcaption>Picking a language from the footer dropdown</figcaption>
</figure>

Until you click Save, the artefact stays in its old group — the list panel reflects the committed state, not the in-progress draft. Type without commitment.

If you change the shell of a multi-process bundle and click Save, the shell's language and organization propagate to every linked subprocess in the same atomic write — even if you only edited the shell.

---

## Workflow 2 — Filter the list panel

1. In any list panel (Processes, Forms, Documents), use the **search box** at the top for free-text matching against name, description, and identifier.
2. Use the **language dropdown** next to the search box to narrow by tag:
   - `All languages` — every artefact, tagged or not
   - `Untagged` — only artefacts with no language tag (useful for finding artefacts that still need tagging)
   - A specific language — only that code
3. The match counter shows `<matched>/<total>` so you can see how many artefacts match.
4. Click an organization header to collapse or expand the group.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Form list panel toolbar with the search box containing capacity, the language dropdown showing Dutch (Nederlands) selected, the match counter showing 8 of 17 to the right of the dropdown, and below the toolbar the FLEVOLAND group expanded showing eight HR Dutch form cards](../../assets/screenshots/linked-data-explorer-form-list-filtered.png)
  <figcaption>Form list filtered to Dutch with the search "capacity"</figcaption>
</figure>

Untagged artefacts always match the `All languages` filter — they only disappear when you switch to a specific language. Use the `Untagged` option to find artefacts that still need tagging.

---

## Workflow 3 — Import a translated artefact

The cleanest way to add a translated sibling is to drop a properly-named file into the importer.

1. Save your translated file with a language suffix: `<artefact-id>.<lang>.<ext>` — e.g. `capacity-claim-intake.nl.form`, `MyProcess.de.bpmn`, `decision-letter.nl.document`.
2. Click the upload icon in the editor's list panel.
3. Select the file (or multiple files at once for a whole bundle).
4. The imported artefact is automatically tagged with the inferred language. Set the organization in the footer if the file doesn't already carry it.
5. Click Save.

If you exported the file from LDE earlier with **Export .form** (or the equivalent), the language and organization are baked into the JSON and survive the round-trip — no need to re-tag.

The order of precedence for inferring the language on import is:

1. Language inside the file (`ronl:language` for BPMN, top-level `language` for form/document JSON)
2. Filename suffix `.<lang>.<ext>`
3. Untagged

---

## Workflow 4 — Translate an existing artefact in place

When you have an existing artefact and want to produce a translated sibling:

1. **For forms:** Click **Export .form** on the original. Open the downloaded JSON in a code editor, translate the user-visible text (labels, descriptions, button text, option labels) keeping `id` and `key` fields stable. Save with a language-suffixed filename. Re-import.
2. **For BPMN:** Export the BPMN, copy to a sibling file in your repo with `.<lang>.bpmn` suffix, translate `name` attributes (process, tasks, gateways, flows). Keep `id` values, `conditionExpression` values, `formRef` (suffix with `-<lang>` if you want a separate Dutch form sibling), and `decisionRef` unchanged. Re-import.
3. **For documents:** Documents authored in the LDE Document Composer can also be exported and re-imported the same way; structural fields (zone IDs, binding placeholders) stay stable across translations.

The principle: **user-visible strings translate, code-level identifiers do not**. DMN variable keys, BPMN flow IDs, form field keys, and document binding placeholders all stay in their original (English) form. Only labels, descriptions, headings, and button text change.

---

## Workflow 5 — Deploy a multi-language bundle

If you've built a Dutch sibling of a process and want to deploy it:

1. Open the Dutch BPMN in the BPMN Modeler.
2. Click **Deploy**. The deploy modal lists the resources it will deploy (shell BPMN, subprocesses, forms, documents).
3. **Check for the amber language-mismatch warning.** If you see it, the bundle is mixing languages — typically because one of the linked forms or documents is still pointing at an English sibling. The warning lists the offending codes (e.g. `en, nl`).
4. Resolve the mismatch: open the misaligned form/document and either retag it or replace it with the Dutch sibling. Save and reopen the deploy modal — the warning should be gone.
5. Click **Deploy** in the modal.

The warning is advisory, not blocking — you can deploy through it for testing. For production, fix the mismatch first.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Deploy modal listing the HR-capacity bundle resources — ManagementCapacityClaimProcess.bpmn followed by eight capacity-claim-*.form files all with -nl suffixes and two -nl document files, an amber RoPA-missing warning, and the resource count line and Deploy button at the bottom — but no language-mismatch warning, indicating all artefacts are nl](../../assets/screenshots/linked-data-explorer-deploy-modal-clean.png)
  <figcaption>Clean deploy modal for the HR-capacity Dutch bundle — no language mismatch</figcaption>
</figure>

---

## Workflow 6 — Explore the HR-capacity Dutch bundle

A reference bundle ships with v1.6.0 to demonstrate end-to-end multilingualism.

1. Open the BPMN Modeler. Find **Beheer capaciteitsclaim — proces (Voorbeeld, NL)** under the FLEVOLAND group, marked with both `EXAMPLE` and Dutch language.
2. Open it. The canvas shows the translated process: tasks like *Overleggen en classificeren*, *Formatieclaim opstellen*, *Directiebesluit*, gateway labels like *Type aanvraag?* and flow labels like *formatie* / *inhuur* / *akkoord* / *afgewezen*.
3. Open one of its linked forms (e.g. *HR — Overleggen en classificeren (Voorbeeld, NL)*). Every label, description, and option label is in Dutch.
4. Now open the **CapacityClaimRouting** DMN. Note that the variable keys (`requestType`, `department`, `decisionRoute`, `advisoryGroup`) are still English. The same DMN serves both the English and Dutch sibling BPMNs — this is what stable English DMN keys buy you.

The bundle is the canonical example of how to do this for your own translations.

---

## Common situations

**I tagged a form with a language and the list didn't update.** Check that you clicked Save in the canvas toolbar. Until then, the change is in the draft only — the list shows the committed state.

**The amber language-mismatch warning won't go away.** Open each artefact listed in the deploy modal in turn and check its language tag in the footer. The mismatch is usually a form whose tag was left at the wrong value.

**I imported a `.nl.form` and the language wasn't picked up.** Confirm the filename ends `.nl.form` exactly (lowercase). Suffixes like `.NL.form` or `.nl.FORM` won't trigger the inference.

**Switching to a different artefact prompts about unsaved changes I didn't make.** This used to happen on document load before v1.6.0 due to a TipTap mount-time event. If you see it on the current version, treat it as a real bug and report it.

**The footer panel for forms is missing the RoPA and DSO sections.** That's expected — only BPMN processes have RoPA and DSO context. Forms and documents only carry language and organization.

---

## Related documentation

- [Multilingualism feature](../features/multilingualism.md) — overview, model, deploy check
- [BPMN Modeler](../features/bpmn-modeler.md)
- [Form Editor](../features/form-editor.md)
- [Document Composer](../features/document-composer.md)