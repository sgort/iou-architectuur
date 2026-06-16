# FLINT Ontology Reference

The Norm Editor stores interpretations as RDF built on the TNO Norm Engineering ontologies.
This page lists the namespaces, classes, and predicates the editor produces, with worked
examples drawn from the conversion test fixtures.

---

## Namespaces

| Prefix | IRI |
|---|---|
| `flint` | `http://ontology.tno.nl/normengineering/flint#` |
| `src` | `http://ontology.tno.nl/normengineering/source#` |
| `editor` | `http://ontology.tno.nl/normengineering/editor#` |
| `calc` | `http://ontology.tno.nl/normengineering/calculemus#` |
| `choppr` | `http://ontology.tno.nl/normengineering/choppr#` |
| `co` | `http://purl.org/co/` |
| `oa` | `http://www.w3.org/ns/oa#` |
| `prov` | `http://www.w3.org/ns/prov#` |
| `owl` | `http://www.w3.org/2002/07/owl#` |
| `rdf` | `http://www.w3.org/1999/02/22-rdf-syntax-ns#` |
| `rdfs` | `http://www.w3.org/2000/01/rdf-schema#` |
| `xsd` | `http://www.w3.org/2001/XMLSchema#` |

---

## FLINT classes

| Class | Meaning |
|---|---|
| `flint:Act` | An act relation |
| `flint:Fact` | A fact |
| `flint:Agent`, `flint:Action`, `flint:Object`, `flint:Duty` | Fact subtypes (a node is typed with `Fact` plus its subtype) |
| `flint:Duty` (as a relation) | A claim-duty relation (has `hasClaimant`/`hasHolder`) |
| `flint:ComplexFact` | A composite boolean construct node |
| `flint:BooleanFact`, `flint:SimpleFact`, `flint:ContextualizedFact` | Further fact forms recognised on import |

---

## Predicates by frame type

### Act

| Predicate | Object |
|---|---|
| `flint:hasAction` | the action fact |
| `flint:hasActor` | the actor fact |
| `flint:hasObject` | the object fact |
| `flint:hasRecipient` | the recipient fact |
| `flint:hasPrecondition` | a `ComplexFact` (boolean construct) |
| `flint:creates` | created facts (repeatable) |
| `flint:terminates` | terminated facts (repeatable) |

### Claim-duty

| Predicate | Object |
|---|---|
| `flint:hasClaimant` | the claimant fact |
| `flint:hasHolder` | the holder fact |
| `owl:sameAs` | links the duty's fact node |

### Boolean construct (`ComplexFact`)

| Predicate | Object |
|---|---|
| `flint:hasFunction` | `flint:and` or `flint:or` |
| `flint:hasOperands` | an ordered RDF list of operand nodes |

### Common to all frames

| Predicate | Object |
|---|---|
| `rdfs:label` | the frame's short label |
| `rdfs:comment` | the frame's description / comments |
| `editor:hasPositionOnScreen` | `"[x, y]"` — the node's position in the network view |
| `flint:hasTextFragment` | a `src:TextFragment` anchoring the frame to source text |

---

## Source anchoring

| Term | Meaning |
|---|---|
| `src:Source` | A source document |
| `src:TextFragment` | A fragment of source text linked to a frame |
| `src:hasCharacterRange` → `src:CharacterRange` | The character span within the sentence |
| `src:startsAtIndex`, `src:endsAtIndex` | `xsd:nonNegativeInteger` offsets |
| `src:hasContent` | the fragment text |

---

## Tasks

| Term | Meaning |
|---|---|
| `calc:Task` | A task |
| `calc:involves` | Links a task to the interpretation and source graphs it uses |
| `calc:hasEditor`, `calc:hasEditedDate` | Task metadata used by the listing queries |

---

## Worked example — claim-duty

A duty with a claimant and a holder, anchored to a text fragment (abridged):

```turtle
editor:b1a4e817-...
    a flint:Duty ;
    rdfs:label "claim13"^^xsd:string ;
    editor:hasPositionOnScreen "[436, 505]"^^xsd:string ;
    flint:hasClaimant editor:05d840e4-... ;
    flint:hasHolder   editor:7dc0cc08-... ;
    flint:hasTextFragment [
        a src:TextFragment ;
        src:hasCharacterRange [
            a src:CharacterRange ;
            src:startsAtIndex "0"^^xsd:nonNegativeInteger ;
            src:endsAtIndex   "192"^^xsd:nonNegativeInteger ;
        ] ;
        src:hasContent "...General Data Protection Regulation)"^^xsd:string ;
    ] ;
    owl:sameAs editor:6319ed82-... ;
.
```

## Worked example — precondition `(A or B) and (C and D)`

An act precondition expressed as nested `ComplexFact` nodes (abridged):

```turtle
flint:hasPrecondition [
    a flint:ComplexFact ;
    flint:hasFunction flint:and ;
    flint:hasOperands (
        [ a flint:ComplexFact ;
          flint:hasFunction flint:or ;
          flint:hasOperands ( editor:d08ea58a-... editor:3e880258-... ) ]
        [ a flint:ComplexFact ;
          flint:hasFunction flint:and ;
          flint:hasOperands ( editor:25510acf-... editor:3f8aabec-... ) ]
    ) ;
] ;
```

---

## Where the mapping lives

The JSON ↔ RDF mapping is implemented in the **wrap-up-api** (JSON → RDF) and **unwrap-api**
(RDF → JSON) services, and verified by their fixture suites using RDFLib graph isomorphism.
See [Backend & API services](../developer/backend-and-apis.md) and the
[Interpretation JSON Format](interpretation-json-format.md).
