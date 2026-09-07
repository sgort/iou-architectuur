# Norm Editor — screenshots to capture

*A running record across syncs, newest first. Last reviewed for 2026.09.1 on
7 September 2026 — **nothing outstanding, and nothing requested**.*

Real screenshot files live in **`docs/assets/screenshots/`** (language-neutral,
served at the site root). Docs reference them as
`../../assets/screenshots/<file>` inside a `<figure markdown>` block.

---

## Sync 2026.07.0 → 2026.09.1 — no screenshots requested

Reviewed on 7 September 2026 for the five-version gap covering 2026.07.1, .2, .3,
.4 and 2026.09.1.

**The Norm Editor's documentation embeds no screenshots at all**, and this sync
does not change that. The decision is recorded here rather than left silent, so a
later run can tell a deliberate choice from a forgotten step.

The one candidate was the **NLP model dropdown** added in 2026.09.1 — a genuine
new user-facing control, on the Act frame form. It is documented in prose on
[Using NLP suggestions](../docs/en/norm-editor/user-guide/using-nlp-suggestions.md)
and [NLP Assistance](../docs/en/norm-editor/features/nlp-assistance.md) instead,
for two reasons:

- **A single-field dropdown is fully describable in a sentence.** What matters is
  which models exist, that the choice is per request, and that an unknown key
  falls back to the default and says so in the response — none of which a picture
  conveys better than the text does.
- **Starting a screenshot practice for a component is a decision in its own
  right.** Every image added has to be recaptured when the UI moves, and this
  component has no existing set to keep consistent with. Worth doing deliberately
  rather than as a side effect of one dropdown.

**Nothing else in the gap has a visual surface.** 2026.07.1 is a filesystem-import
fix, .2 a pre-commit hook, .3 tests and CI, .4 Python packaging and pipeline steps.

**If a screenshot practice does start here**, the strongest first candidates are
the Act frame form as a whole (which the FLINT frame model pages describe at
length) and the source-annotation view — not this dropdown on its own.
