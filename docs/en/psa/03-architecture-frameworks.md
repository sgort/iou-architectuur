---
title: "3. Architecture frameworks"
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

# 3. Architecture frameworks

## What this chapter settles in your PSA

Which frameworks and standards apply to your IOU implementation, how IOU's
choices relate to them, and what you still have to do yourself. Not every
framework is mandatory for every organisation; this chapter records which apply
to you and where you deviate.

A PSA shows how frameworks are being addressed. It is not evidence of compliance.
IOU has no formal assessment or certification for any of the frameworks below;
your organisation does that for its own implementation.

## What IOU decides

**Open standards for everything that is shared** (AB-03), **open source as the
default** (AB-04), **APIs following the API Design Rules** (AB-05) and **data at
the source** (AB-26). How that works out per framework:

| Framework | How IOU relates to it | What you still do |
|---|---|---|
| **NORA** (Dutch government reference architecture) | The choices for open standards, open source, data at the source and one access route through APIs match the NORA principles. IOU has not worked that out principle by principle. | Record for each relevant NORA principle how your implementation meets it. |
| **GEMMA** (municipalities) or the reference architecture of your tier of government | IOU is not mapped onto the reference components of GEMMA or any other reference architecture. | Map the IOU components onto the reference components you use. Chapter 5 gives the components and their roles. |
| **Common Ground** | IOU separates process, rules and data: rules live in the knowledge graph, processes in the engine, data stays at the source (AB-26) and every component manages its own data (AB-25). Neither decision is fully realised yet. | Determine which Common Ground components you already have and how IOU uses them. |
| **BIO2** (government information security baseline) | IOU has no mapping of its measures onto the BIO2. Some decisions do support BIO2 measures: authorisation per case (AB-18), recording of requests (AB-23), reproducible builds (AB-28). | Do a risk analysis and a BIO2 statement for your implementation. [Chapter 8](08-security-and-privacy.md) and [chapter 11](11-decisions-and-risks.md) give the known gaps. |
| **GDPR and its Dutch implementation act (UAVG)** | IOU processes personal data in cases. The record of processing activities can be kept and published per process (AB-27). | Determine the legal basis, purposes and retention periods per processing activity, and weigh whether a DPIA is needed. See [chapter 8](08-security-and-privacy.md). |
| **Wet digitale overheid** (Digital Government Act) | Governs, among other things, the login means for digital services. IOU requires a level of assurance per action (AB-19) and is prepared for DigiD and eIDAS, but both are still switched off. | Determine per service the required level of assurance and the login means, before phase 2. |
| **Digital accessibility** (EN 301 549 with WCAG 2.1) | The public site of the RONL Business API has automated accessibility tests at WCAG levels A and AA. That is not a full audit. The other components have not been assessed for accessibility. | Have every interface you put into use assessed, and publish an accessibility statement. |
| **Archiefwet** (Public Records Act) | A published service description keeps no history (AB-10, risk R-06). No retention period is applied to audit data yet (AB-23). | Set retention periods and arrange archiving. Take MDTO into account (see below). |
| **Forum Standaardisatie** | See the table below. | Include the mandatory standards in your procurement and record deviations. |

### Standards and their Forum Standaardisatie status

Checked on 6 November 2026 at forumstandaardisatie.nl. "Comply or explain"
(*pas toe of leg uit*) means the standard is mandatory in procurement and
development unless you explain why not.

| Standard | Where IOU uses it | Status |
|---|---|---|
| BWB (Juriconnect standard for references to legislation) | References to national legislation in service descriptions and rules | Comply or explain |
| JCDR (Juriconnect Decentrale Regelgeving) | References to decentralised regulation | Comply or explain |
| SKOS and NL-SBB | Concepts in service descriptions | Comply or explain |
| DCAT-AP-NL | Describing datasets, if you publish them | Comply or explain |
| OpenAPI Specification and REST-API Design Rules | Description and design of the APIs (AB-05) | Comply or explain |
| Authentication standards (OpenID.NLGov and SAML) | Login through the OIDC issuer; DigiD uses SAML | Comply or explain |
| NL GOV Assurance profile for OAuth 2.0 | Tokens between portals and backend | Comply or explain |
| HTTPS and HSTS, TLS | All traffic | Comply or explain |
| Digitoegankelijk (EN 301 549 with WCAG 2.1) | Interfaces for staff and residents | Comply or explain |
| ODF | Documents you offer for editing | Comply or explain |
| MDTO (metadata for durably accessible government information) | Archiving | Comply or explain, from 1 January 2027 |
| NEN-ISO/IEC 27001 and 27002 | Basis of the BIO2 | Comply or explain |
| RDF, RDFS, OWL, SHACL | Knowledge graph and validation (AB-11) | Recommended |
| CPSV-AP 3.2.0 | Service descriptions (AB-06) | Not on the list; European standard |
| CPRMV 0.4.2 | Rules and their methods (AB-07) | Not on the list; first public working draft |
| ELI | References to legislation | Not on the list; European standard |
| BPMN 2.0, DMN 1.3 | Process and decision models | Not on the list; international standards. For DMN, IOU proposes a Dutch application profile: [DMN-AP NL](https://github.com/sgort/ttl-editor/blob/main/docs/dmn-ap-nl-proposal.md) |
| SPARQL | Querying the knowledge graph | Not on the list |

IOU has not established, standard by standard, whether every component fully
complies. The table says where a standard applies, not that it has been applied
correctly everywhere.

## What you fill in

- Which frameworks apply to your organisation, and which reference architecture
  you use.
- Per mandatory standard: whether your implementation complies, and if not, your
  explanation.
- Your own architecture principles, security guidelines and technology choices,
  and how IOU fits within them.
- Who does the BIO2 statement, the DPIA assessment and the accessibility audit,
  and when.

## Further reading

- [Standards compliance of the RONL Business API](../ronl-business-api/reference/standards-compliance.md)
- [External standards in the CPSV Editor](../cpsv-editor/reference/external-standards.md)
- [CPRMV vocabulary](../cprmv-api/reference/cprmv-vocabulary.md)
- [ICTU dependency guideline](../contributing/ictu-dependency-guideline.md)
