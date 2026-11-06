---
title: "4. Functional architecture"
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

# 4. Functional architecture

## What this chapter settles in your PSA

IOU's main functions, the roles that work with them, and how IOU supports your
processes. Screens and complete functional requirements belong in a functional
design; this chapter stays at the level of functions.

## What IOU decides

**Every step has one tool, and the artefacts are shared.** Services are described
with the CPSV Editor (AB-06), rules in CPRMV (AB-07), processes designed in the
Linked Data Explorer (AB-08). Legal interpretation is done in FLINT with the Norm
Editor; that tool is replaceable (AB-12).

**The organisation travels with everything that is deployed** (AB-15). A decision
model is deployed once and used by several organisations; differences per
organisation are in the decision table itself. A process and a case always belong
to one organisation.

### Main functions

| Function | What it does | Component |
|---|---|---|
| Interpret legal text | Fetch the source text, mark acts, facts and duties (with suggestions from language analysis), and store the interpretation in the knowledge graph. | Norm Editor |
| Describe a service | Record the service, the competent organisation and the legal basis; separate rules into rules, policy and parameters, each with its own owner. | CPSV Editor |
| Publish | Validate the service description with its rules and publish it in the knowledge graph. | CPSV Editor |
| Retrieve legal text | Fetch the text of a law or regulation in force from the official source, on a chosen date. | CPRMV API |
| Design decisions | Find decision models, test them and link them into a chain, also across organisations. | Linked Data Explorer |
| Design processes | Model a process with phases, roles and tasks; create forms and document templates; deploy the whole as a bundle. | Linked Data Explorer |
| Guard quality | Validate decision models and shared artefacts; record who validated or certified an artefact. | Linked Data Explorer |
| Keep the record of processing activities | Record and publish, per process, how personal data is processed. | Linked Data Explorer |
| Handle cases | See, claim and complete tasks; have decisions evaluated; fill in forms; create and store documents. | RONL Business API |
| Apply (phase 2) | A resident or representative starts a service and follows their own cases. | RONL Business API (MijnOmgeving) |
| Make public | Consult the rule catalogue, process library and record of processing activities without logging in. | RONL Business API (public site), Linked Data Explorer |

### Roles

The login service has a few fixed roles, and in addition roles per process.

| Role | What the role may do | Tier |
|---|---|---|
| Resident | Make their own applications and see their own cases (phase 2) | Core |
| Representative | Act on behalf of someone else, within the authorisation (phase 2) | Core |
| Caseworker | Handle cases of their own organisation | Core |
| Administrator | Administer their own organisation | Core |
| Process roles | Tasks within one process, such as submitter, lawyer or signatory; linked to tasks in the process model | Organisation's own |

The design tools have no roles yet: they do not check who uses them (AB-20,
risk R-02).

## Phasing

| | Phase 1: staff | Prepare now | Phase 2: residents and businesses |
|---|---|---|---|
| Roles | Caseworker, administrator, process roles | The resident and representative roles already exist; design processes so they can use them | Resident and representative active |
| Processes | Started by a staff member | Decide per process whether a resident may later start it themselves | Started by a resident or representative |
| Decisions | Evaluated for the caseworker | Decisions a resident may have evaluated in advance require only level `basis` (AB-19) | The resident has them evaluated |

## What you fill in

- Which main functions you use in phase 1.
- Which processes you support, and which process roles belong to them.
- How the roles map onto your organisation: who may handle cases, who
  administers, who publishes, who may deploy.
- Who owns each shared artefact: which department describes a service, which sets
  the rules, which designs the process.

## Further reading

- [The FLINT frame model](../norm-editor/features/flint-frame-model.md)
- [Service, organisation and legal basis](../cpsv-editor/features/service-organisation-legal.md)
  and [rules, policy and parameters](../cpsv-editor/reference/rpp-architecture.md)
- [The BPMN Modeler](../linked-data-explorer/features/bpmn-modeler.md) and
  [chains of decisions](../linked-data-explorer/features/dmn-chain-building.md)
- [Tasks](../ronl-business-api/features/tasks.md),
  [executing decisions](../ronl-business-api/features/business-rules-execution.md)
  and [roles in the login service](../ronl-business-api/reference/keycloak-realm.md)
