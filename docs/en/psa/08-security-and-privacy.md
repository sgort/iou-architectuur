---
title: "8. Security and privacy"
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

# 8. Security and privacy

## What this chapter settles in your PSA

How access, authorisation, recording and data protection are arranged, which
measures IOU brings itself, and which you take. This chapter is the basis for your
risk analysis, your BIO2 statement and your DPIA assessment. It does not replace
them.

## What IOU decides

**Login and authorisation**

- **One OIDC issuer for all backends** (AB-17). Staff log in through your
  organisation's login service, later residents through DigiD or eHerkenning, all
  brokered behind the same issuer. The backend checks the token on every request:
  signature, issuer, audience and validity.
- **Authorisation per case, in the backend** (AB-18). A staff member sees only
  cases of their own organisation, a resident only their own cases. The server sets
  the organisation label itself; when in doubt, it refuses. The screen is not a
  security boundary.
- **A level of assurance per action** (AB-19). Having a decision evaluated
  requires `basis`, starting a process `midden`.
- **Every write authenticated, authorised and recorded** (AB-20). The RONL
  Business API meets this. The Linked Data Explorer, the CPSV Editor and the Norm
  Editor do not yet: anyone who can reach their backend can write to it
  (risk R-02).
- **The design tools for staff only** (AB-21). This is only enforced once AB-20 is
  realised. Until then, you shield them yourself.

**Shielding**

- **The engine is never reachable from outside** (AB-13). The portals go through
  the RONL Business API, but the engine itself is still directly reachable
  (risk R-01).
- **A separate public layer that only reads** (AB-22). Without login, with a limit
  on the number of requests. Where the public site lets someone submit something,
  it first asks the browser for a computational proof, against automated abuse.
- **Security headers and a request limit** in the RONL Business API. CORS limits
  which web pages may call an API, but it is not access control.

**Recording and privacy**

- **Every authenticated request recorded in a separate audit store** (AB-23). No
  retention period is applied yet (risk R-10).
- **Data at the source** (AB-26): personal data from base registers is fetched
  when needed, not copied.
- **Record of processing activities per process** (AB-27), public without contact
  details.
- **A language-model assistant is your own choice** (AB-31). The RONL Business API
  still requires a key for one in production (risk R-08). If you use it, data goes
  to an external service; assess that against the GDPR and a processing agreement.

**Building and delivering**

- **Reproducible builds** (AB-28): everything a build fetches is pinned, every
  release has an SBOM, and updates wait a fixed period. This applies to the CPSV
  Editor, the Linked Data Explorer and the RONL Business API; not yet to CPRMV and
  the Norm Editor (risk R-07). IOU does not sign its own releases; it does verify
  the signatures of what it pulls in.

### What IOU does not arrange

- No vulnerability reporting point: none of the components has a `SECURITY.md` or
  `security.txt`.
- No penetration test and no threat analysis.
- No mapping onto the BIO2 and no DPIA.
- No key and secret management for your environment; that belongs to your
  deployment.

## Phasing

Based on the phasing table of a compact municipal PSA.

| Topic | Phase 1: staff | Prepare now | Phase 2: residents and businesses |
|---|---|---|---|
| Authentication | Your organisation's login service, behind the OIDC issuer | Issuer separate from the business logic (AB-17, realised for the RONL Business API) | DigiD, eHerkenning, possibly eIDAS |
| Authorisation | Roles and organisation | Authorisation per case in the backend (AB-18, realised) | Only own cases or cases covered by an authorisation |
| Network | Internal access | Shield the design tools and the engine (R-01, R-02) | Public access to the portals and public site |
| Interface | Work environment | Accessibility from the start | MijnOmgeving, assessed for accessibility |
| Data | Internal processing | Separation per case and identity | Access by the resident themselves |
| APIs | Internal clients | Token validation, authorisation and limits in the backend | A public client added |
| Recording | Actions by staff | Set and apply the retention period (R-10) | Actions by residents as well, and abuse detection |
| Privacy | Assessment of internal processing | Record the DPIA assessment | Reassess for external access |
| Assessment | Risk analysis, BIO2 statement | Threat analysis | Penetration test and formal release before public use |

## What you fill in

- Your risk analysis and BIO2 statement, starting from the risks in
  [chapter 11](11-decisions-and-risks.md).
- The DPIA assessment: is a DPIA needed, and if so, when.
- How you shield the design tools and the engine as long as IOU does not.
- The level of assurance per service in phase 2.
- Who reports and handles vulnerabilities, and how you inform IOU.
- Key and secret management, including regular key rotation.
- Whether you use a language-model assistant, and on which conditions.

## Further reading

- [Authentication and access management](../ronl-business-api/features/authentication-iam.md)
- [Security and compliance of the RONL Business API](../ronl-business-api/features/security-compliance.md)
- [Standards compliance](../ronl-business-api/reference/standards-compliance.md)
- [CPSV Editor due diligence](../cpsv-editor/developer/due-diligence.md)
- [Supply-chain pinning](../contributing/supply-chain.md) and
  [dependency scanning](../contributing/dependency-scanning.md)
