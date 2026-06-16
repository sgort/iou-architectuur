# Saving and Loading

Your work can be saved as a local file or pushed to TriplyDB, and reopened later from either.
The **save / load banner** runs across the top of the stepper, so these actions are available
at every step.

---

## Saving

You have three options:

| Save as | Result |
|---|---|
| **JSON** | Downloads the interpretation as a `.json` file with a timestamped name. This is the editor's native format and the fastest, most reliable round trip. |
| **TriG** | Converts the interpretation to RDF (via the wrap-up service) and downloads a `.trig` file — suitable for sharing as Linked Data. |
| **TriplyDB** | Converts to RDF and uploads it to the TriplyDB knowledge graph. |

When saving to TriplyDB, only graphs that are not already present online are uploaded, so
re-saving an interpretation will not create duplicates.

!!! tip "Save early, save often"
    Because the JSON format needs no conversion service, downloading a JSON file is the
    quickest way to checkpoint your work mid-interpretation.

---

## Loading

You can reopen an interpretation in three ways:

- **From a JSON file** — upload a previously saved `.json` interpretation.
- **From RDF** — load a TriG/Turtle interpretation, which the unwrap service converts back
  into editor frames.
- **From TriplyDB** — open the task retrieval panel, pick a task from the list (each shows its
  title, editor, and date), and the editor pulls the task together with its sources and
  reopens it on the interpretation step.

Loading restores everything: the task details, the source documents (including which sentences
were selected and which headings were collapsed), all frames and their roles, the boolean
constructs, the text annotations and their underlining, and any comments.

---

## Compatibility

The editor reads older interpretations as well as current ones. Interpretations that used a
single fact subtype, that referenced the actor of a claim-duty under its old name, or that
stored comments as plain strings, are all upgraded automatically on load — so you can safely
reopen work created with earlier versions of the editor.
