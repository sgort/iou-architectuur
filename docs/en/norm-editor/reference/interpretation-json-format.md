# Interpretation JSON Format

This is the editor's **native serialisation** — the structure produced by
`convertInterpretationToJson` and read back by `parseJsonToInterpretation`. It is what a
saved `.json` file contains and what the conversion services translate to and from RDF.

---

## Top-level structure

```json
{
  "id": "http://ontology.tno.nl/normengineering/editor#task-<uuid>",
  "type": "Task",
  "label": "GDPR – right of access",
  "description": "Interpretation of article 15 ...",
  "hasEditor": "J. Jansen",
  "interpretation": "http://ontology.tno.nl/normengineering/editor#interpretation-<uuid>",
  "sourceDocs": [ ... ],
  "frames": [ ... ]
}
```

| Field | Description |
|---|---|
| `id` | Task IRI |
| `type` | Always `Task` |
| `label`, `description` | Task metadata |
| `hasEditor` | Name of the interpreter |
| `interpretation` | Interpretation IRI linked to the task |
| `sourceDocs` | The loaded documents and selection state |
| `frames` | The interpretation's frames |

---

## Source documents

Each entry keeps the original JSON-LD plus which sentences were selected and which were
collapsed, so the document reopens in the same state:

```json
{
  "jsonLd": { "@context": { ... }, "@graph": [ ... ] },
  "selectedSentencesIds": ["s1", "s2", ...],
  "collapsedSentencesIds": ["s5", ...]
}
```

---

## Frames

All frames share `id`, `typeId`, `label`, `comments`, and `annotations`. The remaining fields
depend on the type.

### Fact

```json
{
  "id": "<uuid>",
  "typeId": "fact",
  "label": "personal data",
  "fact": "any information relating to an identified person",
  "subTypeIds": ["object"],
  "isComplex": true,
  "subdivision": { /* boolean construct */ },
  "comments": [ ... ],
  "annotations": [ ... ]
}
```

`subTypeIds` is a list — a fact may have several subtypes. (Older files using a single
`subTypeId` are still read.)

### Act

```json
{
  "id": "<uuid>",
  "typeId": "act",
  "label": "process personal_data controller subject",
  "act": "the controller processes personal data",
  "actionId": "<fact-id>",
  "actorId": "<fact-id>",
  "objectId": "<fact-id>",
  "recipientId": "<fact-id>",
  "precondition": { /* boolean construct */ },
  "creates": ["<fact-id>", ...],
  "terminates": ["<fact-id>", ...],
  "comments": [ ... ],
  "annotations": [ ... ]
}
```

Roles reference facts **by id**. `creates` and `terminates` are arrays.

### Claim-duty

```json
{
  "id": "<uuid>",
  "typeId": "claim_duty",
  "label": "...",
  "claimduty": "the data subject has the right to ...",
  "dutyId": "<fact-id>",
  "claimantId": "<fact-id>",
  "holderId": "<fact-id>",
  "comments": [ ... ],
  "annotations": [ ... ]
}
```

`actorId` may also appear as a deprecated alias of `claimantId` for backwards compatibility.

---

## Boolean constructs

Used for an act's `precondition` and a fact's `subdivision`:

```json
{
  "frame": "<fact-id> or null",
  "isNegated": false,
  "operatorToJoinChildren": "and",
  "children": [ /* nested boolean constructs */ ]
}
```

- An **atomic** node sets `frame` to a fact id and has no children.
- A **composite** node sets `frame` to `null`, joins `children` with
  `operatorToJoinChildren` (`"and"` / `"or"`), and may be negated.
- Empty nodes (no frame, no children) are pruned on export.

---

## Annotations and snippets

Each frame carries the snippets of source text it is anchored to:

```json
"annotations": [
  {
    "snippets": [
      {
        "documentId": "<source @base IRI>",
        "sentenceId": "<sentence id>",
        "sentenceIri": "<sentence IRI>",
        "characterRange": [6, 36],
        "text": "protection of natural persons"
      }
    ]
  }
]
```

On load, snippets are reattached to the right sentence in the right document, splitting the
sentence's spans as needed and re-linking the annotation to its frame. Snippets of length 0
are ignored.

---

## Comments

```json
{
  "content": "Interpreted broadly per recital 26.",
  "author": "Guest",
  "createdAt": "2026-02-01T10:15:30.000Z",
  "lastEditedAt": null
}
```

For backwards compatibility, a comment stored as a **plain string** is also accepted and read
as the comment's content.

---

## Worked examples

The wrap-up and unwrap test suites contain matched `.json` ↔ `.ttl` fixtures covering atomic
facts, negation, double negation, nested boolean constructs, `creates`/`terminates`,
claim-duties, and fact subtypes — useful as concrete examples of every field above.
