---
component: Norm Editor
---

# NLP Assistance

Interpreting an act frame means deciding which words are the **action**, which are the
**actor**, the **object**, and the **recipient**. The Norm Editor can do a first pass of this
automatically, using a machine-learning model trained on Dutch normative text.

---

## What it does

The **nlp-api** service wraps a fine-tuned model configured for **token classification**.
Given a piece of Dutch text, it labels each token as one of:

| Model label | Meaning in the editor |
|---|---|
| `ACTION` | Action |
| `ACTOR` | Actor |
| `OBJECT` | Object |
| `RECIPIENT` | Recipient |
| `O` | Not part of an act frame |

### Choosing a model

The model is chosen **per request** rather than fixed at deploy time. `nlp-api` carries a
registry of selectable models and the request names one:

| Key | Model |
|---|---|
| `bertje_2022_e4` | A fine-tuned **BERTje** (a Dutch BERT) — the default |
| `legal-bert-dutch-english` | A legal-domain bilingual model |

The Act frame form offers these in an unlabelled dropdown next to its **Detect roles**
button, in the heading of the **Roles** section, as *BERTje (2022)* and
*legal-bert-dutch-english*. An unknown key, or no key at all, falls back to the default, and
the response echoes the model that was actually used — so a caller can always tell which one
produced the labels rather than assuming its request was honoured.

The editor keeps its own list of the models it offers, in the Act frame form, so a model added
to the `nlp-api` registry also needs an entry there before interpreters can choose it. Model
files are **not** part of the service image — `nlp-api`
takes its model root from configuration, backed by an Azure storage account, so adding
a model does not mean rebuilding the service. A resolved path that does not exist is
reported as an error rather than surfacing a loader traceback.

Word-piece tokens (those continuing a previous word) are merged back into whole words, so the
suggestions are returned as readable word/label pairs rather than sub-word fragments.

!!! note "Scope of the model"
    The model is trained specifically to recognise the constituents of an **Act** frame in
    Dutch text. It does not predict claim-duty roles or fact subdivisions. The model and its
    training are described in the [FlintFillers](https://gitlab.com/normativesystems/flintfillers)
    project.

---

## How it fits the workflow

```mermaid
sequenceDiagram
    participant U as Interpreter
    participant E as Editor (web)
    participant N as nlp-api
    U->>E: Detect roles (on an act)
    E->>N: POST /api/predict { text, model } per sentence
    N->>N: Token classification
    N-->>E: predicted_entities [(word, label), ...]
    E-->>U: Recommendations dialog with highlighted roles
    U->>E: Accept, skip, or discard; OK
```

The interpreter stays in control. The model's output is a **suggestion**: the editor shows the
predicted entities in a review dialog, and only the suggestions the interpreter accepts become
facts — anchored to their words and given the subtype that matches the suggested role. The
interpreter then places those facts into the act's roles. See
[Using NLP suggestions](../user-guide/using-nlp-suggestions.md) for the steps.

---

## Practical considerations

- **Language** — the model expects **Dutch** text. Running it over text in another language
  will produce unreliable labels.
- **Length** — transformer models have a maximum token limit. The editor sends the sentences
  an act is anchored to one at a time, not an entire source document; a very long sentence can
  still exceed the model's limit.
- **Availability** — NLP assistance is optional. The editor is fully usable without it; the
  feature simply removes the manual first step of identifying act constituents.

For the request and response shapes, see the
[API Endpoints reference](../reference/api-endpoints.md#nlp-api). For how to run the service,
see [Backend & API services](../developer/backend-and-apis.md#nlp-api).
