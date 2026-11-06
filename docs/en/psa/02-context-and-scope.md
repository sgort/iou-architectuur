---
title: "2. Context and scope"
scope: cross-cutting
verified:
  date: 2026-11-06
  against:
    CPSV Editor: "0412e9b"
    Linked Data Explorer: "814c4bb"
    RONL Business API: "ff6c362"
    Norm Editor: "c47096b"
    CPRMV: "8262d3e"
---

# 2. Context and scope

## What this chapter settles in your PSA

What IOU does, for whom, which processes it supports and where it stops. After
this chapter a reader of your PSA knows where IOU fits in your information
landscape, and which existing systems it touches.

## What IOU decides

**IOU carries legislation and regulation to execution in a chain of steps.**
Every step delivers an artefact that the next step takes over unchanged, in an
open format (AB-02):

| Step | What happens | Component | Artefact |
|---|---|---|---|
| 1. Interpret | Lawyers and policy officers record what a legal text means: which acts, facts and duties it contains. | Norm Editor | Interpretation in FLINT, linked to the source text |
| 2. Describe | The service is described: what it is, which organisation is competent, which law it rests on and which rules apply. | CPSV Editor, with CPRMV | Service description (CPSV-AP) with rule sets (CPRMV) |
| 3. Design | Decisions are worked out in decision tables, the work in a process model, with forms and document templates. | Linked Data Explorer | Decision models (DMN) and a process bundle (BPMN, forms, templates) |
| 4. Execute | Staff handle cases; decisions are evaluated; later residents apply themselves. | RONL Business API, with a process engine | Cases, tasks, decisions, documents |
| 5. Account for | Rules, processes and the record of processing activities are made public. | RONL Business API (public site), Linked Data Explorer | Public rule catalogue, process library, record of processing activities |

In addition, the CPRMV API fetches the current text of laws and regulations from
the official publication sources, so that the text is not copied.

**The design tools are for staff; residents reach only the portals and the public
site** (AB-21). Phase 2 opens execution to residents and businesses, not design.

**Who uses IOU:**

| User | Works with | Phase |
|---|---|---|
| Lawyer, policy officer | Norm Editor | 1 |
| Rule analyst, service owner | CPSV Editor | 1 |
| Process designer, product owner | Linked Data Explorer | 1 |
| Caseworker, team lead | Work environment of the RONL Business API | 1 |
| Administrator | All components, the process engine, the login service | 1 |
| Resident, authorised representative | MijnOmgeving | 2 |
| Business | MijnOmgeving | 2 |
| Anyone, without login | Public site: rule catalogue, process library, record of processing activities | 1 and 2 |

**Where IOU stops.** IOU is not a document management system, an identity
service, a base register or a financial system. It connects to the systems your
organisation already has for those (see [chapter 7](07-integration-architecture.md)).
Nor does IOU replace existing case systems in one go: you choose per process
whether it runs in IOU.

## Phasing

| | Phase 1: staff | Prepare now | Phase 2: residents and businesses |
|---|---|---|---|
| Users | Staff of your own organisation | Roles for resident and representative already exist in the login service | Residents, representatives and businesses |
| Processes | Internal handling, with or without an application from outside | Design processes so that an application can also come from a resident | Applications through MijnOmgeving |
| Openness | Public site with rules and processes | Decide what becomes public | Unchanged |

## What you fill in

- Which processes you run in IOU first, and why those.
- Which of the five steps you use. Not every organisation starts with
  interpreting legislation.
- Which user groups you admit in phase 1, and when phase 2 starts.
- Which existing systems IOU touches: case systems, document management, signing,
  identity management, finance, base registers.
- Where IOU overlaps with what you already have, and how you resolve the overlap.

## Further reading

- [IOU architecture in slides](../iou-architecture-deck.md)
- [Norm Editor](../norm-editor/index.md)
- [CPSV Editor](../cpsv-editor/index.md)
- [Linked Data Explorer](../linked-data-explorer/index.md)
- [RONL Business API](../ronl-business-api/index.md) and the
  [feature overview](../ronl-business-api/features/overview.md)
- [CPRMV API](../cprmv-api/index.md)
