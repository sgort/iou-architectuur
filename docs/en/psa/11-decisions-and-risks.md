---
title: "11. Architectural decisions and risks"
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

# 11. Architectural decisions and risks

This chapter is the backbone of the guide. The decision register holds every
decision IOU has taken, with its tier and its status. The other chapters refer to
it by number. Copy the register into your own PSA, add your deviations, and take
over the risks that apply to you. The
[template](../../assets/downloads/psa-template-en.zip) already contains this
register, with an empty table for your deviations and two columns on the risks
for your own assessment and measure.

What the tiers and statuses mean is explained on
[About this PSA](index.md#three-tiers).

## Decision register

| ID | Decision | Tier | Status | Note |
|---|---|---|---|---|
| AB-01 | IOU adopts standards that are still evolving step by step, and feeds back what it learns. A function that needs a newer version stays deliberately off until that version is deployed; the rest keeps working. | Core | realised | This is how IOU and CPRMV grow together; for DMN, IOU proposes a Dutch application profile, [DMN-AP NL](https://github.com/sgort/ttl-editor/blob/main/docs/dmn-ap-nl-proposal.md). See [How IOU develops](index.md#how-iou-develops). |
| AB-02 | Every step delivers its artefact in an open format; nothing is re-typed. | Core | partly | True from service description to execution. The step from legal interpretation (Norm Editor) to service description (CPSV Editor) is still manual. |
| AB-03 | Shared artefacts use CPSV-AP 3.2.0, CPRMV 0.4.2, BPMN 2.0, DMN 1.3, RDF/Turtle, SKOS/NL-SBB, and ELI, BWB, CVDR and JuriConnect for references to legislation. | Core | partly | The CPSV Editor still writes CPRMV 0.4.1. |
| AB-04 | Open source is the default (EUPL-1.2). A closed product is allowed only behind a replaceable interface. | Core | partly | CPSV Editor, Linked Data Explorer, RONL Business API and CPRMV are EUPL-1.2; the Norm Editor is Apache-2.0. The RONL Business API requires a closed language-model service in production (see AB-31). |
| AB-05 | APIs follow the API Design Rules and have an OpenAPI 3.1 description that is checked automatically. | Core | partly | RONL Business API and Linked Data Explorer yes; CPRMV and the Norm Editor not yet. |
| AB-06 | Public services are described and published with the CPSV Editor. | Core | realised | |
| AB-07 | Rules are recorded in CPRMV: a rule set belongs to a public service, refers to the law it is based on, and has a validity period. | Core | partly | The CPSV Editor links a rule set to the law with a different relation than CPRMV prescribes. CPRMV is still a first public working draft. |
| AB-08 | Processes are designed in the Linked Data Explorer and deployed only through its backend, as one bundle of process, forms and document templates. | Core | partly | This is how the Linked Data Explorer deploys. But as long as the engine is directly reachable, a deployment can bypass it (see AB-13). |
| AB-09 | Decision models are found with standard SPARQL; rules are consumed through the version-2 norms API, under a fixed stability promise. | Core | realised | The version-1 API is deprecated and is removed on 1 November 2028. |
| AB-10 | Every published service lives in its own graph per organisation and service, at a fixed address. | Core | realised | Republishing overwrites the graph; no history is kept (risk R-06). |
| AB-11 | Shared artefacts are validated against the SHACL shapes of CPSV-AP, CPRMV and RONL before publication; an error blocks publication. While drafting, the check is advisory. | Core | not yet | The check exists, but never blocks. |
| AB-12 | Legal interpretation is recorded in FLINT, linked to the source text. The Norm Editor is IOU's tool for it. | Replaceable | partly | Two of the Norm Editor's six parts are not yet built, and no other component reads FLINT yet. |
| AB-13 | A Business API stands between every portal and the process engine; the engine is never reachable from outside. | Core | partly | The portals go through the RONL Business API. The engine itself is still directly reachable. |
| AB-14 | Processes and decisions run on an engine with the Camunda 7 REST API; IOU chooses Operaton. | Replaceable | realised | Camunda 7 Enterprise fits; Camunda 8 means a rebuild. |
| AB-15 | The organisation travels with every deployment and every case. A decision model is deployed once and shared; differences per organisation are in the decision table itself. | Core | realised | |
| AB-16 | Published artefacts live in a SPARQL 1.1 triple store; IOU chooses TriplyDB. | Replaceable | realised | **Under review**: IOU is considering Apache Jena Fuseki. |
| AB-17 | Backends accept tokens from one OIDC issuer, which brokers the login services for staff and residents. Which product the issuer is, is AB-32. | Core | partly | The RONL Business API yes. The design tools do not check tokens yet (see AB-20). |
| AB-18 | The backend decides per case who may do what, and refuses when in doubt: only the owning organisation or the applicant themselves. | Core | realised | In the RONL Business API. |
| AB-19 | Actions require a level of assurance: `basis` to have a decision evaluated, `midden` to start a process. | Core | partly | The check works. DigiD and eIDAS are prepared but switched off; eHerkenning does not exist yet. |
| AB-20 | Every write in every component is authenticated, authorised and recorded. Publishing happens on behalf of a competent organisation. | Core | partly | The RONL Business API yes. Linked Data Explorer, CPSV Editor and Norm Editor not yet. |
| AB-21 | The design tools are for staff only; residents and businesses reach only the portals and the public site. | Core | partly | Residents are not offered the design tools, but the tools do not enforce it yet (see AB-20). |
| AB-22 | Public catalogues are read live from the knowledge graph, through a separate public layer that only reads, without login and with a limit on the number of requests. | Core | realised | |
| AB-23 | Every authenticated request is recorded in a separate audit store. You set the retention period. | Core | partly | Recording works; no retention period is applied anywhere yet. |
| AB-24 | Documents stay in the organisation's document management system; the case holds only a reference. | Organisation's own | realised | |
| AB-25 | Every component manages its own data; no component reads another's database. | Core | partly | The RONL Business API still reads directly from the Linked Data Explorer's database. |
| AB-26 | Data stays at the source: base registers are queried, not copied. | Core | partly | The BRP is queried through the Haal Centraal API, but still against a test service. Other registers are not connected yet. |
| AB-27 | The record of processing activities (GDPR article 30) is kept per process in the Linked Data Explorer and published. | Replaceable | realised | You may keep your register elsewhere. |
| AB-28 | Every IOU component builds reproducibly: nothing a build fetches is unpinned, every release has a CycloneDX SBOM, updates wait a fixed period, and the ICTU dependency guideline is measured weekly. | Core | partly | CPSV Editor, Linked Data Explorer and RONL Business API yes; CPRMV and the Norm Editor not yet. |
| AB-29 | Every component has independent releases with calendar versions; changes reach acceptance and production only through a pull request. | Core | partly | CPSV Editor, Linked Data Explorer and RONL Business API yes. CPRMV follows the version of its specification; the Norm Editor has only a production branch. |
| AB-30 | Production is delivered through a standard delivery pipeline with a quality gate. | Core | not yet | All components currently deliver through the rapid-prototyping track. |
| AB-31 | A language-model assistant is optional and the organisation's choice. | Organisation's own | not yet | The RONL Business API does not start in production without a key for a closed language-model service. |
| AB-32 | IOU chooses Keycloak as the OIDC issuer. | Replaceable | realised | Another issuer that issues OIDC tokens and brokers the login services will do; for example Entra ID. |

## Recording a deviation

You do not deviate from a decision in the **Core** tier. You may deviate from a
decision in the **Replaceable** tier; record each deviation in your own PSA in
this form:

| ID | Deviates from | Reason | Conflicts with principle | Cost | Way back |
|---|---|---|---|---|---|
| DEV-01 | AB-14: Operaton | Existing contract and team knowledge for Camunda 7 Enterprise. | AB-04: open source is the default. | Licence costs, dependence on one vendor, improvements in Operaton do not come along automatically. | Both follow the Camunda 7 REST API; switching means redeploying, not rebuilding. |

A deviation from a decision in the **Organisation's own** tier does not exist:
there you simply record your choice, in the chapter where it belongs.

## Risks

Every decision IOU has partly or not yet realised appears below as a risk. A security gap that is still open is described here in general terms,
without a link to its issue; the link follows once the gap is closed. There
are also risks that touch no decision but apply to every implementation. Take
over what applies to you, and add your own.

| ID | Risk | Affects | What you do meanwhile | Issue |
|---|---|---|---|---|
| R-01 | The process engine is directly reachable, bypassing the Business API's checks. | AB-08, AB-13 | Place the engine in your own network so that only the backends can reach it. | Filed with the component; link follows once fixed |
| R-02 | The design tools accept writes without establishing who makes them. | AB-17, AB-20, AB-21 | Make the design tools reachable only inside your network, behind your organisation's login service. | Filed with the component; link follows once fixed |
| R-03 | Access for residents and businesses does not really work yet: DigiD and eIDAS are switched off, eHerkenning is missing, the BRP is a test service. | AB-19, AB-26 | Limit adoption to phase 1. Plan the connection to DigiD, eHerkenning and the BRP as a project of its own before phase 2. | — |
| R-04 | What the CPSV Editor writes differs from CPRMV 0.4.2, and CPRMV itself is still a working draft. That is part of how IOU and CPRMV grow together, but it means shared rules can differ between versions. | AB-03, AB-07 | Validate published rules against the CPRMV shapes, follow CPRMV's development, and feed what you find back to IOU. | — |
| R-05 | SHACL validation is advisory only; an artefact with errors can be published. | AB-11 | Agree that nobody publishes while validation reports errors. | — |
| R-06 | A published service description keeps no history: republishing overwrites the previous version. This affects the Archiefwet (Public Records Act). | AB-10 | Archive every published version yourself, with its date, in your archive system. | — |
| R-07 | Not every component meets the build and API agreements, and there is no standard delivery pipeline yet. | AB-05, AB-28, AB-29, AB-30 | Include CPRMV and the Norm Editor in your own acceptance test; take no release into production without that test. | — |
| R-08 | The RONL Business API requires a closed language-model service in production. | AB-04, AB-31 | Assess the service against the GDPR and a processing agreement, or wait until it is optional. | — |
| R-09 | One component reads another's database directly; changes to that database can break it. | AB-25 | Always include both components together in your acceptance test. | — |
| R-10 | No retention period is applied to audit data. | AB-23 | Set your retention period and arrange the clean-up yourself. | — |
| R-11 | The legal interpretation is carried into the service description by hand, and the Norm Editor is not yet complete. | AB-02, AB-12 | Record who checks the transfer, and how. | — |
| R-12 | The process engine has no production instance of its own yet: acceptance and production share one engine. No back-up is set up for the engine or the Linked Data Explorer's database. | — | Set up a separate engine per environment in your own environment, with a production database, back-up and a tested restore procedure. | Filed with the component; link follows once fixed |
| R-13 | Moving to another triple store or hosting requires code changes; not every address is configurable. | AB-16 | With another triple store or hosting, expect development work and plan for it. | — |
| R-14 | On test and acceptance the chain breaks: the existing systems IOU connects to (for example document management, signing, identity management, finance) often have only a production environment. Acceptance then tests an imitation, or touches production data. | — | Have administrators and suppliers set up a test and acceptance environment for every connected system (route 3 in [chapter 7](07-integration-architecture.md)). Until then: test against stubs, and record that the real connection is first used in production. | — |
| R-15 | A decision model can pass every check and still never give the right outcome: DMN does not require a model to prove that it works, nor say how it refers to the law. | AB-03 | Test every decision model with test cases before deployment, including the outcomes it must be able to give. Follow the development of [DMN-AP NL](https://github.com/sgort/ttl-editor/blob/main/docs/dmn-ap-nl-proposal.md). | — |
