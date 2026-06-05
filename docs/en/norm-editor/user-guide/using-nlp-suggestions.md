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
    languages are unreliable. Run it on **selected sentences or fragments**, not on an entire
    document — very long inputs can exceed the model's token limit.

---

## How to use it

1. Work on a selected Dutch sentence in the source panel.
2. Request suggestions for that sentence.
3. The model returns each word labelled as **Actor**, **Action**, **Object**, **Recipient**,
   or *none*.
4. The editor surfaces these suggestions so you can turn them into facts and place them into
   the matching roles of an act.
5. **Review every suggestion.** Accept the ones that are right, adjust the boundaries where the
   model over- or under-selected, and ignore anything incorrect.

When the editor creates an **agent** fact from a suggestion, it records the model's
recommended role as a **comment** on that fact, so later reviewers can see where the
classification came from.

---

## Suggestions are a draft, not an answer

The model is a labelling aid, not an authority on the law. It does not understand claim-duty
relations, preconditions, or fact subdivisions — those remain your judgement. Treat its output
as a fast first draft of an act's roles that you then verify against the text.

For the technical details of the model and service, see
[NLP Assistance](../features/nlp-assistance.md) and
[Backend & API services](../developer/backend-and-apis.md#nlp-api).
