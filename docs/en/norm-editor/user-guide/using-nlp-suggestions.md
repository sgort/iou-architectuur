---
component: Norm Editor
---

# Using NLP Suggestions

The editor can suggest the constituents of an act frame — actor, action, object, recipient —
directly from Dutch source text, using a machine-learning model. This removes the manual first
step of deciding which words play which role.

---

## When to use it

NLP suggestions are most useful when you are starting an **act** on a Dutch sentence and want
a head start on identifying its parts. The feature is entirely optional; you can interpret any
source without it.

!!! warning "Dutch text only"
    The underlying model is trained on **Dutch** normative text. Suggestions on text in other
    languages are unreliable. The model runs on the **sentences the act is anchored to**, one
    at a time — very long sentences can exceed the model's token limit.

---

## How to use it

1. Open an act that is linked to source text — for example one you created by highlighting a
   Dutch sentence. The suggestion controls appear in the act's **Roles** heading only when the
   act is linked to source text.
2. Optionally pick a different model in the dropdown next to **Detect roles**: *BERTje (2022)*
   (the default) or *legal-bert-dutch-english*.
3. Click **Detect roles**. The editor sends each sentence the act is anchored to to the model,
   which labels every word as **Actor**, **Action**, **Object**, **Recipient**, or *none*.
4. A **FlintFiller Recommendations** dialog shows each sentence with the suggested words
   highlighted per role. Click a highlighted fragment to **Accept**, **Skip**, or **Discard**
   it. **Review every suggestion** — accept the ones that are right and discard anything
   incorrect.
5. Click **OK** to add the accepted suggestions to the interpretation as facts, anchored to
   their words in the text and given the matching subtype (*Agent* for an actor or recipient,
   *Action*, or *Object*). **Cancel** closes the dialog without changes.
6. Place the new facts into the act's roles with **Select**, as you would any other fact.

If the request fails — for example because the chosen model is not available on the server —
the editor shows the error *Model not present on filesystem.* and stops sending sentences.

!!! warning "Check the facts that OK adds"
    For each sentence, the dialog adds as many facts as you accepted, but it takes them from
    the start of that sentence's list of suggestions rather than from the ones you accepted.
    Unless you accepted the first suggestions in a sentence, compare the new facts in the
    Frames list with what you accepted, and delete any that are wrong.

---

## Suggestions are a draft, not an answer

The model is a labelling aid, not an authority on the law. It does not understand claim-duty
relations, preconditions, or fact subdivisions — those remain your judgement. Treat its output
as a fast first draft of an act's roles that you then verify against the text.

For the technical details of the model and service, see
[NLP Assistance](../features/nlp-assistance.md) and
[Backend & API services](../developer/backend-and-apis.md#nlp-api).
