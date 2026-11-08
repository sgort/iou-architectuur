---
title: "9. Technical infrastructure"
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

# 9. Technical infrastructure

## What this chapter settles in your PSA

Where IOU runs: hosting, containers, databases, network, environments and
back-up. Hosting is your organisation's own choice. IOU shows one reference
deployment as an example, not as a prescription.

## What IOU decides

IOU decides about the components, not about where they run. Three decisions do
touch the infrastructure:

- **The engine is never reachable from outside** (AB-13). Your network design must
  enforce that: only the backends reach the engine (risk R-01).
- **An engine with the Camunda 7 REST API** (AB-14) and **a SPARQL 1.1 triple
  store** (AB-16). Which you choose and where it runs is up to you.
- **Every component has its own database** (AB-25).

### The reference deployment

| Component | Runs in the reference on | In a container |
|---|---|---|
| Web interfaces (CPSV Editor, Linked Data Explorer, RONL Business API) | Azure Static Web Apps | No |
| Backends of the Linked Data Explorer and the RONL Business API | Azure App Service (Node.js) | No |
| Databases of the Linked Data Explorer and the RONL Business API | Azure Database for PostgreSQL, one server per component | No |
| Process engine (Operaton) and OIDC issuer (Keycloak) | Virtual machine with Docker, behind a reverse proxy | Yes |
| Norm Editor | Azure Container Apps, provisioned with Bicep | Yes |
| CPRMV API | Container, on its own servers | Yes |
| Knowledge graph (TriplyDB) | Supplier's service | Not applicable |

What this means for you: CPRMV, the Norm Editor, the engine and Keycloak can run
anywhere as containers. For the Linked Data Explorer and the RONL Business API
there are no container definitions or infrastructure as code; running them
outside Azure takes work of your own (risk R-13).

### Environments (OTAP)

The IOU components have four environments: development, test, acceptance and
production (*OTAP* in Dutch). Development and test run on the developer's machine;
acceptance and production are shared environments.

| Component | Development | Test | Acceptance | Production |
|---|---|---|---|---|
| CPSV Editor | local | local | ACC | PROD |
| Linked Data Explorer | local | local | ACC | PROD |
| RONL Business API | local | local | ACC | PROD |
| Operaton (platform) | local | local | ACC | not yet: shares the ACC engine (R-12) |
| Keycloak (platform) | local | local | ACC | PROD |
| PostgreSQL (platform) | local | local | ACC | PROD |
| TriplyDB (linked data) | dataset O | dataset T | dataset A | own instance |
| Document management, signing, identity management, finance (your systems) | stub | usually none | usually none | PROD |

The last row is the problem from [chapter 7](07-integration-architecture.md#testing-and-accepting-connections):
your existing systems often have only production, so on test and acceptance the
chain breaks (risk R-14). **IOU recommends that administrators and suppliers set
up a test and acceptance environment for every connected system** (route 3).

### Back-up and restore

Azure Database for PostgreSQL makes back-ups automatically. For the virtual
machine with the engine and Keycloak, the reference describes a back-up
procedure, but it is not set up as a scheduled task. No restore has been tested
for the engine or the Linked Data Explorer's database (risk R-12).

## Phasing

| | Phase 1: staff | Prepare now | Phase 2: residents and businesses |
|---|---|---|---|
| Network | Everything inside your network | Separate the portals, API layer, engine, databases and internal systems | Portals and public site reachable from the internet |
| Availability | Matched to working hours | Set up monitoring and restore | Wider availability; test scalability |
| Protection | Internal shielding | Decide where a WAF and DDoS protection go | WAF and DDoS protection active |

## What you fill in

- Where you run each component: your own data centre, a government cloud, a
  public cloud.
- Your network design, with zones for portals, API layer, engine, databases and
  internal systems.
- Your environments per component, and per connected system whether route 3
  exists.
- Back-up and restore per component: frequency, retention, recovery time and how
  much data loss is acceptable; and when you test a restore.
- Whether you consume TriplyDB as a service, run a triple store yourself, or choose
  another (AB-16, under review).

## Further reading

- [Deployment overview of the RONL Business API](../ronl-business-api/developer/deployment/overview.md),
  with [Operaton](../ronl-business-api/developer/deployment/operaton.md) and
  [Keycloak](../ronl-business-api/developer/deployment/keycloak.md)
- [Linked Data Explorer deployment](../linked-data-explorer/developer/deployment.md)
- [CPSV Editor deployment](../cpsv-editor/developer/deployment.md)
- [CPRMV API deployment](../cprmv-api/developer/deployment.md)
- [Norm Editor deployment](../norm-editor/developer/deployment.md)
