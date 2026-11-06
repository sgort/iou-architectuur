---
title: "1. Executive summary"
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

# 1. Executive summary

**Purpose.** IOU carries legislation and regulation to execution in one
continuous chain: from the interpretation of a legal text, through the
description of a service and its rules, to the design and execution of the
process. Every step delivers an artefact in an open format, which the next step
takes over unchanged and which organisations share with each other. A decision
can thus be traced back to the article of law it rests on.

**Rationale.** Organisations that introduce IOU must write a PSA. This guide gives
them the basis: what IOU has decided, how binding that is, how far IOU itself has
got with it, and what you fill in.

**The key architectural choices:**

- **IOU adopts evolving standards step by step and learns from them** (AB-01).
  This is the first decision: it explains why statuses change and why some
  decisions are under review. It is how CPRMV and the proposed Dutch profile for
  DMN (DMN-AP NL) grow together with IOU.
- **Shared artefacts in open standards, made with fixed tools**: CPSV-AP and CPRMV
  with the CPSV Editor, BPMN and DMN with the Linked Data Explorer (AB-03, AB-06,
  AB-07, AB-08). You do not deviate from these.
- **One API layer between all portals and the engine, with authorisation per case
  in the backend** (AB-13, AB-18). This lets residents gain access later without a
  rebuild.
- **One OIDC issuer for all backends** (AB-17), behind which you connect your own
  login service and later DigiD and eHerkenning.
- **The engine, triple store, login service and Norm Editor are replaceable**
  (AB-12, AB-14, AB-16), provided you record the deviation.
- **Hosting, environments, retention periods and operations are your
  organisation's own choice.**

**Where IOU stands.** IOU is not finished as a reference. The biggest open
points: the engine is still directly reachable (R-01), the design tools do not yet
check who uses them (R-02), DigiD and eHerkenning are not yet active (R-03), and
there is no standard delivery pipeline yet (R-07). On test and acceptance the
chain to your own systems breaks (R-14); IOU recommends setting up test and
acceptance environments for them.

**Phasing.** Phase 1 is for staff and can start now, provided you shield the
design tools and the engine yourself. Phase 2 opens execution to residents and
businesses and first requires a connection to DigiD and eHerkenning, a threat
analysis, a penetration test and a formal release.
