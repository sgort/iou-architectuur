---
component: Norm Editor
---

# Saving and Loading

Your work can be saved as a local file or pushed to TriplyDB, and reopened later from either.
The **load** and **save** buttons sit in the top bar of the header, so these actions are
available on every tab. Each opens a menu with a *Locally* section (**JSON**, **RDF**) and a
*Remotely* section (**Triply**).

---

## Saving

You have three options:

| Save as | Result |
|---|---|
| **JSON** | Downloads the interpretation as a `.json` file with a timestamped name. This is the editor's native format and the fastest, most reliable round trip. |
| **RDF** | Converts the interpretation to RDF (via the wrap-up service) and downloads a `.trig` file — suitable for sharing as Linked Data. |
| **Triply** | Converts to RDF and uploads it to the TriplyDB knowledge graph. |

When saving to TriplyDB, only graphs that are not already present online are uploaded, so
re-saving an interpretation will not create duplicates.

!!! tip "Save early, save often"
    Because the JSON format needs no conversion service, downloading a JSON file is the
    quickest way to checkpoint your work mid-interpretation.

---

## Loading

You can reopen an interpretation in three ways:

- **JSON** — upload a previously saved `.json` interpretation. The editor then opens the
  **Interpret sources** tab.
- **RDF** — upload a `.trig` interpretation, which the unwrap service converts back into
  editor frames. The editor then opens the **Interpret sources** tab.
- **Triply** — a dialog lists the tasks in TriplyDB (title, creator, and date). Select one and
  click **Retrieve task**; the editor pulls the task together with its sources. The current
  tab stays open, so switch to **Interpret sources** to continue the work.

Loading restores everything: the task details, the source documents (including which sentences
were selected and which headings were collapsed), all frames and their roles, the boolean
constructs, the text annotations and their underlining, and any comments.

---

## Compatibility

The editor reads older interpretations as well as current ones. Interpretations that used a
single fact subtype, that referenced the actor of a claim-duty under its old name, or that
stored comments as plain strings, are all upgraded automatically on load — so you can safely
reopen work created with earlier versions of the editor.
