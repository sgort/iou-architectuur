# Project Start Architecture — [organisation name]

| | |
|---|---|
| Organisation | […] |
| Version | […] |
| Status | […] |
| Date | […] |
| Author | […] |
| Approved by | […] |

Based on the IOU PSA guide, verified on 2026-11-06 against CPSV Editor 0412e9b, Linked Data Explorer 814c4bb, RONL Business API ff6c362, Norm Editor c47096b, CPRMV 8262d3e.

## About this template

This template contains the decisions IOU has already taken, per chapter. You fill in only what your organisation decides itself: wherever […] appears.

Decisions in the **Core** tier are fixed. You may deviate from a decision in the **Replaceable** tier; record it in chapter 11 as a deviation (DEV-nn). Decisions in the **Organisation's own** tier you fill in yourself.

The status at IOU shows how far IOU itself has got with a decision, on the date above.

## 1. Executive summary

Explained in the guide: https://iou-architectuur.open-regels.nl/psa/01-executive-summary/

IOU's first decision, which applies to everyone: AB-01 — IOU adopts standards that are still evolving step by step, and feeds back what it learns. A function that needs a newer version stays deliberately off until that version is deployed; the rest keeps working.

**Purpose.** […]

**Rationale.** […]

**Key architectural choices.** […]

**Phasing.** […]

## 2. Context and scope

Explained in the guide: https://iou-architectuur.open-regels.nl/psa/02-context-and-scope/

### IOU's decisions

| ID | Decision | Tier | Status at IOU | Deviation |
|---|---|---|---|---|
| AB-02 | Every step delivers its artefact in an open format; nothing is re-typed. | Core | partly | not open to deviation |
| AB-21 | The design tools are for staff only; residents and businesses reach only the portals and the public site. | Core | partly | not open to deviation |

### What IOU decides (from the IOU PSA guide)

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
organisation already has for those (see [chapter 7](https://iou-architectuur.open-regels.nl/psa/07-integration-architecture/)).
Nor does IOU replace existing case systems in one go: you choose per process
whether it runs in IOU.

### Phasing

| | Phase 1: staff | Prepare now | Phase 2: residents and businesses |
|---|---|---|---|
| Users | Staff of your own organisation | Roles for resident and representative already exist in the login service | Residents, representatives and businesses |
| Processes | Internal handling, with or without an application from outside | Design processes so that an application can also come from a resident | Applications through MijnOmgeving |
| Openness | Public site with rules and processes | Decide what becomes public | Unchanged |

### Our choices

1. Which processes you run in IOU first, and why those.

   […]

2. Which of the five steps you use. Not every organisation starts with interpreting legislation.

   […]

3. Which user groups you admit in phase 1, and when phase 2 starts.

   […]

4. Which existing systems IOU touches: case systems, document management, signing, identity management, finance, base registers.

   […]

5. Where IOU overlaps with what you already have, and how you resolve the overlap.

   […]

## 3. Architecture frameworks

Explained in the guide: https://iou-architectuur.open-regels.nl/psa/03-architecture-frameworks/

### IOU's decisions

| ID | Decision | Tier | Status at IOU | Deviation |
|---|---|---|---|---|
| AB-03 | Shared artefacts use CPSV-AP 3.2.0, CPRMV 0.4.2, BPMN 2.0, DMN 1.3, RDF/Turtle, SKOS/NL-SBB, and ELI, BWB, CVDR and JuriConnect for references to legislation. | Core | partly | not open to deviation |
| AB-04 | Open source is the default (EUPL-1.2). A closed product is allowed only behind a replaceable interface. | Core | partly | not open to deviation |
| AB-05 | APIs follow the API Design Rules and have an OpenAPI 3.1 description that is checked automatically. | Core | partly | not open to deviation |
| AB-06 | Public services are described and published with the CPSV Editor. | Core | realised | not open to deviation |
| AB-07 | Rules are recorded in CPRMV: a rule set belongs to a public service, refers to the law it is based on, and has a validity period. | Core | partly | not open to deviation |
| AB-10 | Every published service lives in its own graph per organisation and service, at a fixed address. | Core | realised | not open to deviation |
| AB-11 | Shared artefacts are validated against the SHACL shapes of CPSV-AP, CPRMV and RONL before publication; an error blocks publication. While drafting, the check is advisory. | Core | not yet | not open to deviation |
| AB-18 | The backend decides per case who may do what, and refuses when in doubt: only the owning organisation or the applicant themselves. | Core | realised | not open to deviation |
| AB-19 | Actions require a level of assurance: `basis` to have a decision evaluated, `midden` to start a process. | Core | partly | not open to deviation |
| AB-23 | Every authenticated request is recorded in a separate audit store. You set the retention period. | Core | partly | not open to deviation |
| AB-25 | Every component manages its own data; no component reads another's database. | Core | partly | not open to deviation |
| AB-26 | Data stays at the source: base registers are queried, not copied. | Core | partly | not open to deviation |
| AB-27 | The record of processing activities (GDPR article 30) is kept per process in the Linked Data Explorer and published. | Replaceable | realised | allowed; see below |
| AB-28 | Every IOU component builds reproducibly: nothing a build fetches is unpinned, every release has a CycloneDX SBOM, updates wait a fixed period, and the ICTU dependency guideline is measured weekly. | Core | partly | not open to deviation |

### What IOU decides (from the IOU PSA guide)

**Open standards for everything that is shared** (AB-03), **open source as the
default** (AB-04), **APIs following the API Design Rules** (AB-05) and **data at
the source** (AB-26). How that works out per framework:

| Framework | How IOU relates to it | What you still do |
|---|---|---|
| **NORA** (Dutch government reference architecture) | The choices for open standards, open source, data at the source and one access route through APIs match the NORA principles. IOU has not worked that out principle by principle. | Record for each relevant NORA principle how your implementation meets it. |
| **GEMMA** (municipalities) or the reference architecture of your tier of government | IOU is not mapped onto the reference components of GEMMA or any other reference architecture. | Map the IOU components onto the reference components you use. Chapter 5 gives the components and their roles. |
| **Common Ground** | IOU separates process, rules and data: rules live in the knowledge graph, processes in the engine, data stays at the source (AB-26) and every component manages its own data (AB-25). Neither decision is fully realised yet. | Determine which Common Ground components you already have and how IOU uses them. |
| **BIO2** (government information security baseline) | IOU has no mapping of its measures onto the BIO2. Some decisions do support BIO2 measures: authorisation per case (AB-18), recording of requests (AB-23), reproducible builds (AB-28). | Do a risk analysis and a BIO2 statement for your implementation. [Chapter 8](https://iou-architectuur.open-regels.nl/psa/08-security-and-privacy/) and [chapter 11](https://iou-architectuur.open-regels.nl/psa/11-decisions-and-risks/) give the known gaps. |
| **GDPR and its Dutch implementation act (UAVG)** | IOU processes personal data in cases. The record of processing activities can be kept and published per process (AB-27). | Determine the legal basis, purposes and retention periods per processing activity, and weigh whether a DPIA is needed. See [chapter 8](https://iou-architectuur.open-regels.nl/psa/08-security-and-privacy/). |
| **Wet digitale overheid** (Digital Government Act) | Governs, among other things, the login means for digital services. IOU requires a level of assurance per action (AB-19) and is prepared for DigiD and eIDAS, but both are still switched off. | Determine per service the required level of assurance and the login means, before phase 2. |
| **Digital accessibility** (EN 301 549 with WCAG 2.1) | The public site of the RONL Business API has automated accessibility tests at WCAG levels A and AA. That is not a full audit. The other components have not been assessed for accessibility. | Have every interface you put into use assessed, and publish an accessibility statement. |
| **Archiefwet** (Public Records Act) | A published service description keeps no history (AB-10, risk R-06). No retention period is applied to audit data yet (AB-23). | Set retention periods and arrange archiving. Take MDTO into account (see below). |
| **Forum Standaardisatie** | See the table below. | Include the mandatory standards in your procurement and record deviations. |

#### Standards and their Forum Standaardisatie status

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

### Our choices

1. Which frameworks apply to your organisation, and which reference architecture you use.

   […]

2. Per mandatory standard: whether your implementation complies, and if not, your explanation.

   […]

3. Your own architecture principles, security guidelines and technology choices, and how IOU fits within them.

   […]

4. Who does the BIO2 statement, the DPIA assessment and the accessibility audit, and when.

   […]

Do we follow IOU's choice for AB-27? [yes / no — see deviation DEV-…]

## 4. Functional architecture

Explained in the guide: https://iou-architectuur.open-regels.nl/psa/04-functional-architecture/

### IOU's decisions

| ID | Decision | Tier | Status at IOU | Deviation |
|---|---|---|---|---|
| AB-06 | Public services are described and published with the CPSV Editor. | Core | realised | not open to deviation |
| AB-07 | Rules are recorded in CPRMV: a rule set belongs to a public service, refers to the law it is based on, and has a validity period. | Core | partly | not open to deviation |
| AB-08 | Processes are designed in the Linked Data Explorer and deployed only through its backend, as one bundle of process, forms and document templates. | Core | partly | not open to deviation |
| AB-12 | Legal interpretation is recorded in FLINT, linked to the source text. The Norm Editor is IOU's tool for it. | Replaceable | partly | allowed; see below |
| AB-15 | The organisation travels with every deployment and every case. A decision model is deployed once and shared; differences per organisation are in the decision table itself. | Core | realised | not open to deviation |
| AB-19 | Actions require a level of assurance: `basis` to have a decision evaluated, `midden` to start a process. | Core | partly | not open to deviation |
| AB-20 | Every write in every component is authenticated, authorised and recorded. Publishing happens on behalf of a competent organisation. | Core | partly | not open to deviation |

### What IOU decides (from the IOU PSA guide)

**Every step has one tool, and the artefacts are shared.** Services are described
with the CPSV Editor (AB-06), rules in CPRMV (AB-07), processes designed in the
Linked Data Explorer (AB-08). Legal interpretation is done in FLINT with the Norm
Editor; that tool is replaceable (AB-12).

**The organisation travels with everything that is deployed** (AB-15). A decision
model is deployed once and used by several organisations; differences per
organisation are in the decision table itself. A process and a case always belong
to one organisation.

#### Main functions

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

#### Roles

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

### Phasing

| | Phase 1: staff | Prepare now | Phase 2: residents and businesses |
|---|---|---|---|
| Roles | Caseworker, administrator, process roles | The resident and representative roles already exist; design processes so they can use them | Resident and representative active |
| Processes | Started by a staff member | Decide per process whether a resident may later start it themselves | Started by a resident or representative |
| Decisions | Evaluated for the caseworker | Decisions a resident may have evaluated in advance require only level `basis` (AB-19) | The resident has them evaluated |

### Our choices

1. Which main functions you use in phase 1.

   […]

2. Which processes you support, and which process roles belong to them.

   […]

3. How the roles map onto your organisation: who may handle cases, who administers, who publishes, who may deploy.

   […]

4. Who owns each shared artefact: which department describes a service, which sets the rules, which designs the process.

   […]

Do we follow IOU's choice for AB-12? [yes / no — see deviation DEV-…]

## 5. Application architecture

Explained in the guide: https://iou-architectuur.open-regels.nl/psa/05-application-architecture/

### IOU's decisions

| ID | Decision | Tier | Status at IOU | Deviation |
|---|---|---|---|---|
| AB-13 | A Business API stands between every portal and the process engine; the engine is never reachable from outside. | Core | partly | not open to deviation |
| AB-14 | Processes and decisions run on an engine with the Camunda 7 REST API; IOU chooses Operaton. | Replaceable | realised | allowed; see below |
| AB-16 | Published artefacts live in a SPARQL 1.1 triple store; IOU chooses TriplyDB. | Replaceable | realised | allowed; see below |
| AB-17 | Backends accept tokens from one OIDC issuer, which brokers the login services for staff and residents. Which product the issuer is, is AB-32. | Core | partly | not open to deviation |
| AB-18 | The backend decides per case who may do what, and refuses when in doubt: only the owning organisation or the applicant themselves. | Core | realised | not open to deviation |
| AB-20 | Every write in every component is authenticated, authorised and recorded. Publishing happens on behalf of a competent organisation. | Core | partly | not open to deviation |
| AB-21 | The design tools are for staff only; residents and businesses reach only the portals and the public site. | Core | partly | not open to deviation |
| AB-22 | Public catalogues are read live from the knowledge graph, through a separate public layer that only reads, without login and with a limit on the number of requests. | Core | realised | not open to deviation |
| AB-25 | Every component manages its own data; no component reads another's database. | Core | partly | not open to deviation |
| AB-32 | IOU chooses Keycloak as the OIDC issuer. | Replaceable | realised | allowed; see below |

### What IOU decides (from the IOU PSA guide)

**One API layer between all portals and the process engine** (AB-13). The work
environment, MijnOmgeving and the public site talk only to the RONL Business API.
It checks who may do what, records it, and talks to the engine. The engine itself
is still directly reachable (risk R-01).

**The engine speaks the Camunda 7 REST API** (AB-14). IOU chooses Operaton.
Another engine with the same API is possible; an engine with a different API
(such as Camunda 8) means a rebuild.

**Shared artefacts live in a SPARQL triple store** (AB-16). IOU chooses TriplyDB;
that decision is under review.

**One OIDC issuer for all backends** (AB-17). IOU chooses Keycloak (AB-32, replaceable), which brokers
your organisation's login service and later DigiD and eHerkenning.

**A separate public layer that only reads** (AB-22), and **every component
manages its own data** (AB-25).

#### The landscape

Every component sits at the step it belongs to. The tier is in brackets.


#### The components

| Component | Role | Consists of | Tier |
|---|---|---|---|
| Norm Editor | Legal interpretation in FLINT | Web interface, backend, three services for text and language analysis | Replaceable |
| CPSV Editor | Describe and publish services and rules | Web interface; uses the Linked Data Explorer's backend for validation and publication | Core |
| CPRMV API | Fetch legal text and rules from official sources | One API service, without storage of its own | Core |
| Linked Data Explorer | Design and deploy decisions and processes; record of processing activities | Web interface, backend with its own database, public site for the record of processing activities | Core |
| RONL Business API | Execute cases; portals for staff and residents; public site | Backend with audit store; web interfaces for the work environment and MijnOmgeving; public site | Core |
| Process engine | Execute processes and decisions | Operaton | Replaceable |
| Knowledge graph | Store shared artefacts and make them queryable | TriplyDB | Replaceable |
| OIDC issuer | Login, roles, brokering other login services | Keycloak | Replaceable |

#### How they communicate

| From | To | For | How |
|---|---|---|---|
| Web interfaces | Their own backend | All functions | HTTPS; the browser does not talk to the engine or knowledge graph itself |
| CPSV Editor | Knowledge graph | Publishing | HTTPS, through TriplyDB's API and the Linked Data Explorer's backend |
| Norm Editor | Knowledge graph | Storing interpretations | HTTPS, through TriplyDB's API |
| Linked Data Explorer | Knowledge graph | Finding decision models, consuming rules | SPARQL 1.1 |
| Linked Data Explorer | Process engine | Deploying process bundles; tasks the system performs itself | Camunda 7 REST API |
| RONL Business API | Process engine | Starting cases, completing tasks, evaluating decisions | Camunda 7 REST API |
| RONL Business API | Knowledge graph | Rule catalogue, process library | SPARQL 1.1, read live |
| RONL Business API | Linked Data Explorer | Published process bundles | REST; and still directly from the database as well (AB-25, risk R-09) |
| RONL Business API | CPRMV API | Legal text for the assistant | Deliberately off as long as the deployed version of the CPRMV API does not yet deliver the function it needs |
| Portals | RONL Business API | Login and actions | OIDC tokens from the issuer, checked by the backend |

A connection to a component that is still evolving is switched on only when the
deployed version delivers what the connection needs. Until then it stays off, and
the rest keeps working. This is how IOU can adopt a standard step by step (see
[About this PSA](https://iou-architectuur.open-regels.nl/psa/#how-iou-develops)).

The design tools do not use tokens yet (AB-20, risk R-02). Where the web
interfaces of the Linked Data Explorer, the CPSV Editor and the Norm Editor talk
to their backend, that backend therefore does not yet check who the user is.

### Phasing

| | Phase 1: staff | Prepare now | Phase 2: residents and businesses |
|---|---|---|---|
| Portals | Work environment | MijnOmgeving already exists as part of the RONL Business API | MijnOmgeving open to residents |
| API layer | Internal clients | All authorisation in the backend, not in the screen (AB-18) | Public clients as an extra user of the same API |
| Design tools | Staff only | Shield them behind your login service | Remain for staff only (AB-21) |

### Our choices

1. Which components you install yourself, and which you consume as a shared service.

   […]

2. Whether you replace a replaceable component; if so, a deviation in chapter 11.

   […]

3. How you map the IOU components onto your reference architecture.

   […]

4. Which of your own systems connect to which components (see [chapter 7](https://iou-architectuur.open-regels.nl/psa/07-integration-architecture/)).

   […]

Do we follow IOU's choice for AB-14? [yes / no — see deviation DEV-…]

Do we follow IOU's choice for AB-16? [yes / no — see deviation DEV-…]

Do we follow IOU's choice for AB-32? [yes / no — see deviation DEV-…]

## 6. Data architecture

Explained in the guide: https://iou-architectuur.open-regels.nl/psa/06-data-architecture/

### IOU's decisions

| ID | Decision | Tier | Status at IOU | Deviation |
|---|---|---|---|---|
| AB-10 | Every published service lives in its own graph per organisation and service, at a fixed address. | Core | realised | not open to deviation |
| AB-15 | The organisation travels with every deployment and every case. A decision model is deployed once and shared; differences per organisation are in the decision table itself. | Core | realised | not open to deviation |
| AB-18 | The backend decides per case who may do what, and refuses when in doubt: only the owning organisation or the applicant themselves. | Core | realised | not open to deviation |
| AB-23 | Every authenticated request is recorded in a separate audit store. You set the retention period. | Core | partly | not open to deviation |
| AB-24 | Documents stay in the organisation's document management system; the case holds only a reference. | Organisation's own | realised | your own choice |
| AB-25 | Every component manages its own data; no component reads another's database. | Core | partly | not open to deviation |
| AB-26 | Data stays at the source: base registers are queried, not copied. | Core | partly | not open to deviation |
| AB-27 | The record of processing activities (GDPR article 30) is kept per process in the Linked Data Explorer and published. | Replaceable | realised | allowed; see below |

### What IOU decides (from the IOU PSA guide)

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

#### Data objects

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
for publishing there (see [chapter 8](https://iou-architectuur.open-regels.nl/psa/08-security-and-privacy/)).

### Phasing

| | Phase 1: staff | Prepare now | Phase 2: residents and businesses |
|---|---|---|---|
| Case data | Cases of your own organisation | Authorisation per case already works in the backend (AB-18) | Residents see only their own cases |
| Personal data | Processing by staff | Record legal basis, purpose and retention period per processing activity | Access by the resident themselves; reassess |
| Audit data | Actions by staff | Set and apply the retention period | Actions by residents as well |

### Our choices

1. Which data you process in IOU, with legal basis and purpose per processing activity.

   […]

2. Retention periods per data object, derived from your retention schedule, and who carries out the clean-up.

   […]

3. How you archive earlier versions of published service descriptions, as long as IOU does not.

   […]

4. Which document management system you connect, and where your record of processing activities lives.

   […]

5. How you hand over data if you stop using IOU: the shared artefacts are in open formats in the knowledge graph; case data you must extract from the process engine.

   […]

Do we follow IOU's choice for AB-27? [yes / no — see deviation DEV-…]

## 7. Integration architecture

Explained in the guide: https://iou-architectuur.open-regels.nl/psa/07-integration-architecture/

### IOU's decisions

| ID | Decision | Tier | Status at IOU | Deviation |
|---|---|---|---|---|
| AB-05 | APIs follow the API Design Rules and have an OpenAPI 3.1 description that is checked automatically. | Core | partly | not open to deviation |
| AB-09 | Decision models are found with standard SPARQL; rules are consumed through the version-2 norms API, under a fixed stability promise. | Core | realised | not open to deviation |
| AB-13 | A Business API stands between every portal and the process engine; the engine is never reachable from outside. | Core | partly | not open to deviation |
| AB-17 | Backends accept tokens from one OIDC issuer, which brokers the login services for staff and residents. Which product the issuer is, is AB-32. | Core | partly | not open to deviation |
| AB-22 | Public catalogues are read live from the knowledge graph, through a separate public layer that only reads, without login and with a limit on the number of requests. | Core | realised | not open to deviation |
| AB-24 | Documents stay in the organisation's document management system; the case holds only a reference. | Organisation's own | realised | your own choice |
| AB-25 | Every component manages its own data; no component reads another's database. | Core | partly | not open to deviation |
| AB-26 | Data stays at the source: base registers are queried, not copied. | Core | partly | not open to deviation |

### What IOU decides (from the IOU PSA guide)

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

#### IOU's APIs

| API | Offered by | For whom | Access |
|---|---|---|---|
| Cases, tasks, decisions, forms, documents | RONL Business API | Work environment and MijnOmgeving | Token from the OIDC issuer, with role and organisation |
| Public catalogues | RONL Business API | Anyone | Without login, read only, with a limit on the number of requests (AB-22) |
| Norms, decision models, process bundles | Linked Data Explorer | Other IOU components, other organisations | Reading public; writing still unchecked (R-02) |
| Legal text and references | CPRMV API | Anyone who needs legal text | Public |
| SPARQL | Knowledge graph | IOU components, other organisations | Reading according to the dataset's settings; writing with a token |

#### Connections to your systems

IOU connects to systems your organisation already has. Which ones is your choice;
the reference deployment shows the following:

| Kind of system | Example in the reference | Connection |
|---|---|---|
| Login service for staff | Entra ID | Brokered behind the OIDC issuer (AB-17) |
| Login means for residents and businesses | DigiD, eIDAS, eHerkenning | DigiD and eIDAS prepared but switched off; eHerkenning not yet present (R-03) |
| Document management | eDOCS | The case keeps a reference (AB-24); the backend acts on behalf of the user |
| Signing | ValidSign | From a task in the process |
| Message box | Doccle | From a task in the process |
| Personal records database | BRP through Haal Centraal | Queried, not copied (AB-26); still a test service for now |

#### Testing and accepting connections

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

### Phasing

| | Phase 1: staff | Prepare now | Phase 2: residents and businesses |
|---|---|---|---|
| APIs | Used by the work environment | Token validation, authorisation per case and a request limit are already in the backend | MijnOmgeving as an extra client of the same API |
| Login means | Your organisation's login service | Plan the connection to DigiD and eHerkenning | DigiD, eHerkenning, possibly eIDAS |
| Connections | With a stub or the real system, per route | Request route 3 from administrators and suppliers | Real systems, tested on acceptance |

### Our choices

1. Which systems you connect to IOU, and which route you choose per connection. If you do not choose route 3, explain why.

   […]

2. Which systems call on their own behalf, and how they identify themselves.

   […]

3. Whether you need Digikoppeling to connect to base registers or other government organisations. IOU does not use it itself.

   […]

4. Which APIs you open to other organisations.

   […]

## 8. Security and privacy

Explained in the guide: https://iou-architectuur.open-regels.nl/psa/08-security-and-privacy/

### IOU's decisions

| ID | Decision | Tier | Status at IOU | Deviation |
|---|---|---|---|---|
| AB-13 | A Business API stands between every portal and the process engine; the engine is never reachable from outside. | Core | partly | not open to deviation |
| AB-17 | Backends accept tokens from one OIDC issuer, which brokers the login services for staff and residents. Which product the issuer is, is AB-32. | Core | partly | not open to deviation |
| AB-18 | The backend decides per case who may do what, and refuses when in doubt: only the owning organisation or the applicant themselves. | Core | realised | not open to deviation |
| AB-19 | Actions require a level of assurance: `basis` to have a decision evaluated, `midden` to start a process. | Core | partly | not open to deviation |
| AB-20 | Every write in every component is authenticated, authorised and recorded. Publishing happens on behalf of a competent organisation. | Core | partly | not open to deviation |
| AB-21 | The design tools are for staff only; residents and businesses reach only the portals and the public site. | Core | partly | not open to deviation |
| AB-22 | Public catalogues are read live from the knowledge graph, through a separate public layer that only reads, without login and with a limit on the number of requests. | Core | realised | not open to deviation |
| AB-23 | Every authenticated request is recorded in a separate audit store. You set the retention period. | Core | partly | not open to deviation |
| AB-26 | Data stays at the source: base registers are queried, not copied. | Core | partly | not open to deviation |
| AB-27 | The record of processing activities (GDPR article 30) is kept per process in the Linked Data Explorer and published. | Replaceable | realised | allowed; see below |
| AB-28 | Every IOU component builds reproducibly: nothing a build fetches is unpinned, every release has a CycloneDX SBOM, updates wait a fixed period, and the ICTU dependency guideline is measured weekly. | Core | partly | not open to deviation |
| AB-31 | A language-model assistant is optional and the organisation's choice. | Organisation's own | not yet | your own choice |
| AB-32 | IOU chooses Keycloak as the OIDC issuer. | Replaceable | realised | allowed; see below |

### What IOU decides (from the IOU PSA guide)

**Login and authorisation**

- **One OIDC issuer for all backends** (AB-17). Staff log in through your
  organisation's login service, later residents through DigiD or eHerkenning, all
  brokered behind the same issuer. The backend checks the token on every request:
  signature, issuer, audience and validity. IOU chooses
  Keycloak as the issuer; that is replaceable (AB-32).
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

#### What IOU does not arrange

- No vulnerability reporting point: none of the components has a `SECURITY.md` or
  `security.txt`.
- No penetration test and no threat analysis.
- No mapping onto the BIO2 and no DPIA.
- No key and secret management for your environment; that belongs to your
  deployment.

### Phasing

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

### Our choices

1. Your risk analysis and BIO2 statement, starting from the risks in [chapter 11](https://iou-architectuur.open-regels.nl/psa/11-decisions-and-risks/).

   […]

2. The DPIA assessment: is a DPIA needed, and if so, when.

   […]

3. How you shield the design tools and the engine as long as IOU does not.

   […]

4. The level of assurance per service in phase 2.

   […]

5. Who reports and handles vulnerabilities, and how you inform IOU.

   […]

6. Key and secret management, including regular key rotation.

   […]

7. Whether you use a language-model assistant, and on which conditions.

   […]

Do we follow IOU's choice for AB-27? [yes / no — see deviation DEV-…]

Do we follow IOU's choice for AB-32? [yes / no — see deviation DEV-…]

## 9. Technical infrastructure

Explained in the guide: https://iou-architectuur.open-regels.nl/psa/09-technical-infrastructure/

### IOU's decisions

| ID | Decision | Tier | Status at IOU | Deviation |
|---|---|---|---|---|
| AB-13 | A Business API stands between every portal and the process engine; the engine is never reachable from outside. | Core | partly | not open to deviation |
| AB-14 | Processes and decisions run on an engine with the Camunda 7 REST API; IOU chooses Operaton. | Replaceable | realised | allowed; see below |
| AB-16 | Published artefacts live in a SPARQL 1.1 triple store; IOU chooses TriplyDB. | Replaceable | realised | allowed; see below |
| AB-25 | Every component manages its own data; no component reads another's database. | Core | partly | not open to deviation |

### What IOU decides (from the IOU PSA guide)

IOU decides about the components, not about where they run. Three decisions do
touch the infrastructure:

- **The engine is never reachable from outside** (AB-13). Your network design must
  enforce that: only the backends reach the engine (risk R-01).
- **An engine with the Camunda 7 REST API** (AB-14) and **a SPARQL 1.1 triple
  store** (AB-16). Which you choose and where it runs is up to you.
- **Every component has its own database** (AB-25).

#### The reference deployment

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

#### Environments (OTAP)

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

The last row is the problem from [chapter 7](https://iou-architectuur.open-regels.nl/psa/07-integration-architecture/#testing-and-accepting-connections):
your existing systems often have only production, so on test and acceptance the
chain breaks (risk R-14). **IOU recommends that administrators and suppliers set
up a test and acceptance environment for every connected system** (route 3).

#### Back-up and restore

Azure Database for PostgreSQL makes back-ups automatically. For the virtual
machine with the engine and Keycloak, the reference describes a back-up
procedure, but it is not set up as a scheduled task. No restore has been tested
for the engine or the Linked Data Explorer's database (risk R-12).

### Phasing

| | Phase 1: staff | Prepare now | Phase 2: residents and businesses |
|---|---|---|---|
| Network | Everything inside your network | Separate the portals, API layer, engine, databases and internal systems | Portals and public site reachable from the internet |
| Availability | Matched to working hours | Set up monitoring and restore | Wider availability; test scalability |
| Protection | Internal shielding | Decide where a WAF and DDoS protection go | WAF and DDoS protection active |

### Our choices

1. Where you run each component: your own data centre, a government cloud, a public cloud.

   […]

2. Your network design, with zones for portals, API layer, engine, databases and internal systems.

   […]

3. Your environments per component, and per connected system whether route 3 exists.

   […]

4. Back-up and restore per component: frequency, retention, recovery time and how much data loss is acceptable; and when you test a restore.

   […]

5. Whether you consume TriplyDB as a service, run a triple store yourself, or choose another (AB-16, under review).

   […]

Do we follow IOU's choice for AB-14? [yes / no — see deviation DEV-…]

Do we follow IOU's choice for AB-16? [yes / no — see deviation DEV-…]

## 10. Management and continuity

Explained in the guide: https://iou-architectuur.open-regels.nl/psa/10-management-and-continuity/

### IOU's decisions

| ID | Decision | Tier | Status at IOU | Deviation |
|---|---|---|---|---|
| AB-01 | IOU adopts standards that are still evolving step by step, and feeds back what it learns. A function that needs a newer version stays deliberately off until that version is deployed; the rest keeps working. | Core | realised | not open to deviation |
| AB-28 | Every IOU component builds reproducibly: nothing a build fetches is unpinned, every release has a CycloneDX SBOM, updates wait a fixed period, and the ICTU dependency guideline is measured weekly. | Core | partly | not open to deviation |
| AB-29 | Every component has independent releases with calendar versions; changes reach acceptance and production only through a pull request. | Core | partly | not open to deviation |
| AB-30 | Production is delivered through a standard delivery pipeline with a quality gate. | Core | not yet | not open to deviation |

### What IOU decides (from the IOU PSA guide)

**IOU adopts standards step by step and learns from them** (AB-01). Components,
statuses and decisions therefore change. This guide is re-checked every week
against the released versions; the date at the top of every page says when.

**Reproducible builds** (AB-28): pinned dependencies, an SBOM with every release, a
waiting period for updates, and a weekly measurement against the ICTU dependency
guideline.

**Independent releases with calendar versions; changes only through a pull
request** (AB-29). Every component has its own version and its own release
moment.

**Production through a standard delivery pipeline with a quality gate** (AB-30).
It does not exist yet: all components deliver through the rapid-prototyping track
(risk R-07).

#### Who does what

| Topic | Comes with the software | IOU team's way of working | You arrange yourself |
|---|---|---|---|
| Dependencies | Pinned; SBOM per release | Updates through automated proposals, after a waiting period; daily check for vulnerabilities; quarterly review | Re-checking the SBOMs you run against new vulnerabilities; possibly your own package registry |
| Quality | Tested before every release; minimum test coverage per file | Test and check gates on every pull request | Your own acceptance test in your own environments |
| Version information | Every web interface and the backends show which build is running | | Using that information in monitoring and incidents |
| Licence | EUPL-1.2 (Norm Editor: Apache-2.0) | | Licences of your own additions |
| Releases | Calendar versions per component | Release and promotion to production through pull requests | Deciding when you take over a release |
| Source code | Public on GitHub; mirror on GitLab | Mirror updated at every release | Deciding which source you follow |
| Hosting and environments | | | Entirely ([chapter 9](https://iou-architectuur.open-regels.nl/psa/09-technical-infrastructure/)) |
| Monitoring and alerts | A health check on the backends | | Entirely: what you measure, when you are alerted |
| Incidents | | | Entirely: reporting, follow-up, communication |
| Back-up and restore | | | Entirely, including restore tests |
| Reporting vulnerabilities | No reporting point yet | | Your own reporting process; agreements with IOU |

This applies in full to the CPSV Editor, the Linked Data Explorer and the RONL
Business API. CPRMV and the Norm Editor are built on GitLab under a lighter regime
of their own: CPRMV tests before every build on its main branch; the Norm Editor
has no test coverage or check gates yet.

### Phasing

| | Phase 1: staff | Prepare now | Phase 2: residents and businesses |
|---|---|---|---|
| Support | Internal service desk | An extensible incident and support process | Support for residents and businesses |
| Availability | Matched to working hours | Monitoring and alerts | Agreements on availability outside working hours |
| Releases | Taken over after your own acceptance test | A fixed rhythm for taking over releases | Releases without interruption for residents |

### Our choices

1. The roles: functional management, application management, technical management, and who handles security updates and incidents.

   […]

2. How you follow and take over IOU releases, and who decides on that.

   […]

3. How you follow changes in this guide: statuses, decisions under review, new versions of standards (AB-01).

   […]

4. Monitoring, alerts and your incident process.

   […]

5. Back-up and restore, and how often you test a restore.

   […]

6. How you feed findings back to IOU, so that IOU learns from them too.

   […]

## 11. Architectural decisions and risks

Explained in the guide: https://iou-architectuur.open-regels.nl/psa/11-decisions-and-risks/

### IOU's decision register

| ID | Decision | Tier | Status | Note |
|---|---|---|---|---|
| AB-01 | IOU adopts standards that are still evolving step by step, and feeds back what it learns. A function that needs a newer version stays deliberately off until that version is deployed; the rest keeps working. | Core | realised | This is how IOU and CPRMV grow together; for DMN, IOU proposes a Dutch application profile, [DMN-AP NL](https://github.com/sgort/ttl-editor/blob/main/docs/dmn-ap-nl-proposal.md). See [How IOU develops](https://iou-architectuur.open-regels.nl/psa/#how-iou-develops). |
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

### Our deviations

| ID | Deviates from | Reason | Conflicts with principle | Cost | Way back |
|---|---|---|---|---|---|
| DEV-01 | […] | […] | […] | […] | […] |

### Risks

| ID | Risk | Affects | What you do meanwhile | Issue | Applies to us? | Our measure |
|---|---|---|---|---|---|---|
| R-01 | The process engine is directly reachable, bypassing the Business API's checks. | AB-08, AB-13 | Place the engine in your own network so that only the backends can reach it. | Filed with the component; link follows once fixed | […] | […] |
| R-02 | The design tools accept writes without establishing who makes them. | AB-17, AB-20, AB-21 | Make the design tools reachable only inside your network, behind your organisation's login service. | Filed with the component; link follows once fixed | […] | […] |
| R-03 | Access for residents and businesses does not really work yet: DigiD and eIDAS are switched off, eHerkenning is missing, the BRP is a test service. | AB-19, AB-26 | Limit adoption to phase 1. Plan the connection to DigiD, eHerkenning and the BRP as a project of its own before phase 2. | — | […] | […] |
| R-04 | What the CPSV Editor writes differs from CPRMV 0.4.2, and CPRMV itself is still a working draft. That is part of how IOU and CPRMV grow together, but it means shared rules can differ between versions. | AB-03, AB-07 | Validate published rules against the CPRMV shapes, follow CPRMV's development, and feed what you find back to IOU. | — | […] | […] |
| R-05 | SHACL validation is advisory only; an artefact with errors can be published. | AB-11 | Agree that nobody publishes while validation reports errors. | — | […] | […] |
| R-06 | A published service description keeps no history: republishing overwrites the previous version. This affects the Archiefwet (Public Records Act). | AB-10 | Archive every published version yourself, with its date, in your archive system. | — | […] | […] |
| R-07 | Not every component meets the build and API agreements, and there is no standard delivery pipeline yet. | AB-05, AB-28, AB-29, AB-30 | Include CPRMV and the Norm Editor in your own acceptance test; take no release into production without that test. | — | […] | […] |
| R-08 | The RONL Business API requires a closed language-model service in production. | AB-04, AB-31 | Assess the service against the GDPR and a processing agreement, or wait until it is optional. | — | […] | […] |
| R-09 | One component reads another's database directly; changes to that database can break it. | AB-25 | Always include both components together in your acceptance test. | — | […] | […] |
| R-10 | No retention period is applied to audit data. | AB-23 | Set your retention period and arrange the clean-up yourself. | — | […] | […] |
| R-11 | The legal interpretation is carried into the service description by hand, and the Norm Editor is not yet complete. | AB-02, AB-12 | Record who checks the transfer, and how. | — | […] | […] |
| R-12 | The process engine has no production instance of its own yet: acceptance and production share one engine. No back-up is set up for the engine or the Linked Data Explorer's database. | — | Set up a separate engine per environment in your own environment, with a production database, back-up and a tested restore procedure. | Filed with the component; link follows once fixed | […] | […] |
| R-13 | Moving to another triple store or hosting requires code changes; not every address is configurable. | AB-16 | With another triple store or hosting, expect development work and plan for it. | — | […] | […] |
| R-14 | On test and acceptance the chain breaks: the existing systems IOU connects to (for example document management, signing, identity management, finance) often have only a production environment. Acceptance then tests an imitation, or touches production data. | — | Have administrators and suppliers set up a test and acceptance environment for every connected system (route 3 in [chapter 7](https://iou-architectuur.open-regels.nl/psa/07-integration-architecture/)). Until then: test against stubs, and record that the real connection is first used in production. | — | […] | […] |
| R-15 | A decision model can pass every check and still never give the right outcome: DMN does not require a model to prove that it works, nor say how it refers to the law. | AB-03 | Test every decision model with test cases before deployment, including the outcomes it must be able to give. Follow the development of [DMN-AP NL](https://github.com/sgort/ttl-editor/blob/main/docs/dmn-ap-nl-proposal.md). | — | […] | […] |
