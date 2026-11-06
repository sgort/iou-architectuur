---
title: "7. Integration architecture"
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

# 7. Integration architecture

## What this chapter settles in your PSA

Which APIs IOU offers, which connections it has with your existing systems, and
how systems identify themselves to each other. Complete API specifications are on
the pages this chapter refers to.

## What IOU decides

**APIs follow the API Design Rules and have an OpenAPI description that is checked
automatically** (AB-05). This currently applies to the RONL Business API and the
Linked Data Explorer.

**Rules are consumed through an API with a fixed stability promise** (AB-09). The
Linked Data Explorer's version-2 norms API is that agreement; the version-1 API is
removed on 1 November 2028.

**All portals talk to one API layer, never directly to the engine** (AB-13).

**Backends trust tokens from one OIDC issuer** (AB-17). A user logs in there; the
backend checks the token on every request. Systems that call on their own behalf
are listed by name as allowed clients.

**Components connect through their API, not through each other's database**
(AB-25).

### IOU's APIs

| API | Offered by | For whom | Access |
|---|---|---|---|
| Cases, tasks, decisions, forms, documents | RONL Business API | Work environment and MijnOmgeving | Token from the OIDC issuer, with role and organisation |
| Public catalogues | RONL Business API | Anyone | Without login, read only, with a limit on the number of requests (AB-22) |
| Norms, decision models, process bundles | Linked Data Explorer | Other IOU components, other organisations | Reading public; writing still unchecked (R-02) |
| Legal text and references | CPRMV API | Anyone who needs legal text | Public |
| SPARQL | Knowledge graph | IOU components, other organisations | Reading according to the dataset's settings; writing with a token |

### Connections to your systems

IOU connects to systems your organisation already has. Which ones is your choice;
the reference deployment shows the following:

| Kind of system | Example in the reference | Connection |
|---|---|---|
| Login service for staff | Entra ID | Brokered behind the OIDC issuer (AB-17) |
| Login means for residents and businesses | DigiD, eIDAS, eHerkenning | Prepared, not yet active (R-03) |
| Document management | eDOCS | The case keeps a reference (AB-24); the backend acts on behalf of the user |
| Signing | ValidSign | From a task in the process |
| Message box | Doccle | From a task in the process |
| Personal records database | BRP through Haal Centraal | Queried, not copied (AB-26); still a test service for now |

### Testing and accepting connections

There is a structural problem here. The IOU components have a development, test,
acceptance and production environment. Many systems IOU connects to have only a
production environment. On test and acceptance the chain then breaks
(risk R-14). There are three routes:

| Route | What it is | Consequence |
|---|---|---|
| 1. Carry stubs through | Test and acceptance use an imitated connection. | Acceptance tests an imitation. The real connection is used for the first time in production. |
| 2. Connect acceptance to production | IOU's acceptance environment talks to the production system. | Real documents, signatures and identities enter a test track. The production regime is broken. |
| 3. Have test and acceptance set up | Administrators and suppliers set up a test and acceptance environment for every connected system. | Structural; a decision outside IOU, with the cost at the administrator or supplier. |

**IOU recommends route 3.** Only then does acceptance test the real connection
without touching production data. Route 1 is a temporary way out as long as
route 3 does not exist; route 2 is not recommended.

## Phasing

| | Phase 1: staff | Prepare now | Phase 2: residents and businesses |
|---|---|---|---|
| APIs | Used by the work environment | Token validation, authorisation per case and a request limit are already in the backend | MijnOmgeving as an extra client of the same API |
| Login means | Your organisation's login service | Plan the connection to DigiD and eHerkenning | DigiD, eHerkenning, possibly eIDAS |
| Connections | With a stub or the real system, per route | Request route 3 from administrators and suppliers | Real systems, tested on acceptance |

## What you fill in

- Which systems you connect to IOU, and which route you choose per connection. If
  you do not choose route 3, explain why.
- Which systems call on their own behalf, and how they identify themselves.
- Whether you need Digikoppeling to connect to base registers or other government
  organisations. IOU does not use it itself.
- Which APIs you open to other organisations.

## Further reading

- [API design of the RONL Business API](../ronl-business-api/features/api-design.md)
  and [authentication](../ronl-business-api/features/authentication-iam.md)
- [Stability of the Linked Data Explorer API](../linked-data-explorer/reference/api-stability.md)
- [CPRMV API endpoints](../cprmv-api/reference/api-endpoints.md)
- [Documents](../ronl-business-api/features/documents.md),
  [signing with ValidSign](../ronl-business-api/developer/validsign-signing.md)
