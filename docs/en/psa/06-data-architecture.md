---
title: "6. Data architecture"
scope: cross-cutting
verified:
  date: 2026-11-08
  against:
    CPSV Editor: "84886c9"
    Linked Data Explorer: "189435e"
    RONL Business API: "35fb3a8"
    Norm Editor: "c47096b"
    CPRMV: "8262d3e"
---

# 6. Data architecture

## What this chapter settles in your PSA

Which data IOU uses and creates, where it lives, who owns it and how long it is
kept. A complete data model belongs in the technical design; this chapter sets out
the main lines and the responsibilities.

## What IOU decides

**Shared artefacts live in the knowledge graph, each in its own graph per
organisation and service** (AB-10). Republishing overwrites that graph, so earlier
versions are not kept (risk R-06).

**The organisation travels with everything** (AB-15). Every deployment and every
case belongs to one organisation. Who may access which case is decided by the
backend, using an organisation label the server sets itself (AB-18).

**Every authenticated request is recorded in a separate audit store** (AB-23).
You set the retention period; IOU does not apply one yet (risk R-10).

**Documents stay in your document management system; the case keeps only a
reference** (AB-24).

**Every component manages its own data** (AB-25) and **data stays at the
source** (AB-26): base registers are queried, not copied. The RONL Business API
still reads directly from the Linked Data Explorer's database (risk R-09).

**The record of processing activities can be kept per process in the Linked Data
Explorer** (AB-27). This is replaceable: you may use your existing register.

### Data objects

| Data | Where it lives | Owner | Retention |
|---|---|---|---|
| Interpretations of legislation (FLINT) | Knowledge graph | The organisation that interprets | Organisation's own choice |
| Service descriptions and rule sets | Knowledge graph, one graph per organisation and service | The competent organisation | Organisation's own choice; no history (R-06) |
| Decision models (DMN) | Process engine; findable through the knowledge graph | The organisation that adopts them | Organisation's own choice |
| Process bundles: process, forms, document templates | Linked Data Explorer database; deployed in the process engine | The organisation that designs the process | Organisation's own choice |
| Record of processing activities | Linked Data Explorer database; public without contact details | The controller | As long as the processing exists |
| Cases: process data and decisions | Process engine | The organisation that owns the case | Organisation's own choice; IOU sets no period |
| Documents | Your document management system | The organisation that owns the case | According to your retention schedule |
| Audit data | Separate database of the RONL Business API | Your organisation | Organisation's own choice; not yet applied (R-10) |
| Personal data from base registers | At the source; fetched when needed | The source holder | Not copied |
| Legal text | Official publication sources; fetched through the CPRMV API | The legislator | Not copied |

Two smaller places of storage: the Linked Data Explorer keeps test cases and chain
templates in the user's browser, and the CPSV Editor keeps the TriplyDB token used
for publishing there (see [chapter 8](08-security-and-privacy.md)).

## Phasing

| | Phase 1: staff | Prepare now | Phase 2: residents and businesses |
|---|---|---|---|
| Case data | Cases of your own organisation | Authorisation per case already works in the backend (AB-18) | Residents see only their own cases |
| Personal data | Processing by staff | Record legal basis, purpose and retention period per processing activity | Access by the resident themselves; reassess |
| Audit data | Actions by staff | Set and apply the retention period | Actions by residents as well |

## What you fill in

- Which data you process in IOU, with legal basis and purpose per processing
  activity.
- Retention periods per data object, derived from your retention schedule, and who
  carries out the clean-up.
- How you archive earlier versions of published service descriptions, as long as
  IOU does not.
- Which document management system you connect, and where your record of
  processing activities lives.
- How you hand over data if you stop using IOU: the shared artefacts are in open
  formats in the knowledge graph; case data you must extract from the process
  engine.

## Further reading

- [Publishing to TriplyDB](../cpsv-editor/features/triplydb-publishing.md)
- [Storage of process bundles](../linked-data-explorer/developer/asset-storage.md)
  and the [Linked Data Explorer database](../linked-data-explorer/developer/deployment-postgresql.md)
- [The record of processing activities](../linked-data-explorer/features/ropa-records.md)
- [Cases and organisations](../ronl-business-api/features/processes.md) and
  [documents](../ronl-business-api/features/documents.md)
