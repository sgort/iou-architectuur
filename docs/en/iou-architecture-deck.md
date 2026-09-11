---
scope: cross-cutting
---

# IOU Architecture — Slide Deck

A 25-slide overview of the whole ecosystem, *IOU-architectuur — van geciteerde wettekst tot
het besluit dat de burger ziet* (from quoted legal text to the decision the citizen sees). It
comes in two parts. **App** explains what people see: the problem the architecture answers,
the four boards of the provincial work environment, the public knowledge base, and the design
principle underneath them. **Dev** explains how it is built and kept safe: the components
and standards, the evidence each board carries, the way the work is done, and the gates in
front of acceptance and production. It ends with three decisions.

Every slide carries a badge in its top-right corner, **App** (functional) or **Dev**
(technical), so either half can be presented on its own.

!!! abstract "Download"
    [IOU Architecture Deck (PDF, 1.0 MB)](assets/downloads/iou-architecture-deck.pdf)

    The slides are **in Dutch**, in the Provincie Flevoland house style. The captions and
    descriptions on this page are in English. This copy reflects the deck as of
    **30 August 2026**, with component versions as recorded on the documentation site that
    day.

!!! note "What has changed since 30 August"
    A deck is a snapshot of its date. These slides make claims the documentation has since
    re-checked and updated. The pages linked below are current; the slides are not.

    | Slide | The deck says | Since then |
    |---|---|---|
    | 16 | CPSV Editor v2026.08.3 and Linked Data Explorer v2026.08.9, both on ACC | Both are on PROD at v2026.09.4. The header of each component page carries its current version |
    | 21 | Ten rules in `~/.claude/CLAUDE.md` | Eleven, as of 9 September — see [Skills and Boundaries](contributing/development-workflow/skills-and-boundaries.md) |
    | 22 | The `acc` ruleset requires the `audit` check; the Linked Data Explorer has seven workflows and the CPSV Editor three | In both applications, `acc` requires `audit` **and** `scan`, the Semgrep code and dependency scan. The Linked Data Explorer has eight workflows, the CPSV Editor four — see [Code Standards](contributing/code-standards.md) |
    | 23 | `main` carries none of this; the gate is on `acc` only | The Linked Data Explorer's `main` requires the same `audit` and `scan` checks as its `acc`. The CPSV Editor's `main` requires a pull request and no status checks, by decision — see [Supply-Chain Pinning](contributing/supply-chain.md) |
    | 24 | Six repositories on `git.open-regels.nl` | The CPSV Editor and the Linked Data Explorer are developed on GitHub and mirrored to GitLab by hand, and this site takes its pull requests on GitHub — see [Contributing](contributing/index.md) |

    The RONL Business API figures (slides 7, 8, 10, 18, 19, 22 and 23) have not been
    re-checked against a later release here.

---

## Part one — App: what the user sees

<figure markdown style="width:100%; margin:0;">
  ![Slide 1 of 25, cover on a blue background with a green and yellow diagonal at the right edge: Provincie Flevoland · Open Regels Nederland; title IOU-architectuur; subtitle Van geciteerde wettekst tot het besluit dat de burger ziet (from quoted legal text to the decision the citizen sees); footer iou-architectuur.open-regels.nl · documentatie gebouwd 30 augustus 2026](assets/slides/iou-architecture/slide-01-cover.png)
  <figcaption>From quoted legal text to the decision the citizen sees</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Slide 2 of 25, section divider on green, badge App: App — deel één, Wat de gebruiker ziet (part one, what the user sees). The problem this comes from, the provenance of a single concept, the four boards of the work environment, the public knowledge base — and the design principle, the pipeline and the concept chain beneath them](assets/slides/iou-architecture/slide-02-app-serie.png)
  <figcaption>Part one — what the user sees</figcaption>
</figure>

### Why this architecture

<figure markdown style="width:100%; margin:0;">
  ![Slide 3 of 25, De opgave (the problem), three numbered cards. 01 Interpretation disappears into code: every rule involves an interpretation decision, and today it sits implicitly in software instead of being recorded next to the article it follows from. 02 A decision cannot be traced: the citizen receives an outcome, not a chain, and for an objection, an audit or a Woo request that chain has to be reconstructed by hand. 03 Two competent authorities, one journey: ISDE is national, Thuisbatterij is provincial; the applicant sees one route, while behind the screen sit two rule sets from two organisations. Footer: each of the three is an information-architecture problem, not a capacity problem](assets/slides/iou-architecture/slide-03-de-opgave.png)
  <figcaption>Three problems, each about information architecture rather than capacity</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Slide 4 of 25, public search site, Provenance tab: Herkomst van een begrip — acht stappen, twee sporen (the provenance of a concept — eight steps, two tracks). Left track, Law and regulation: 1 legal analysis, quoted legal text plus annotation; 2 rule, the rule in one sentence; 3 DMN, expression, input and output; 4 concepts, clickable, so the chain continues. Right track, Users — what the citizen sees: 1 concepts explained in plain language; 2 data requested, the questions with their field names; 3 data checked, what is held against the registry; 4 conclusion, which check deviates, not simply rejected. Footer: data is itself a consequence of law and regulation; clicking through leads to a registry datum or a definition in the law](assets/slides/iou-architecture/slide-04-herkomst.png)
  <figcaption>One concept, traced from legal analysis to what the citizen is shown</figcaption>
</figure>

### The four boards

The work environment of the RONL Business API. Each board has its own user guide:
[Caseworker](ronl-business-api/user-guide/caseworker.md),
[PA-Cockpit](ronl-business-api/user-guide/pa-cockpit.md),
[Infra-board](ronl-business-api/user-guide/infra-board.md) and
[Woo-dashboard](ronl-business-api/user-guide/woo-dashboard.md).

<figure markdown style="width:100%; margin:0;">
  ![Slide 5 of 25, RONL work environment · Provincie Flevoland: Vier borden voor het werk van de provincie (four boards for the province's work). A screenshot of the landing page shows four board cards — Caseworker, PA-Cockpit, Infra-board and Woo-dashboard — each marked available. Beside it: one front door, four boards, from case handling to executive alignment, project steering and Woo accountability; access by role, which boards a member of staff sees depends on role and authorisations, enforced in Keycloak and not in the frontend; two entrances, staff through their staff account and residents through DigiD, both over the same identity provider; visible status, each board shows whether it is available, with a changelog in the footer. Callout: the four boards share one shell — section router, command palette and rail — so a new board is a set of sections, not a new application](assets/slides/iou-architecture/slide-05-landingspagina.png)
  <figcaption>One front door, four boards, one shared shell</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Slide 6 of 25, board spotlight: PA-Cockpit — een bestuurlijk kompas (an executive compass). A screenshot shows the dossier Stikstof en landbouwtransitie with its issue map and the Flevolands Kompas radar, scoring 14 of 16. Beside it: the Flevolands Kompas weighs every dossier on eight criteria scored 0 to 2, with the reasoning for each criterion; top issues and signals from the Tweede Kamer, Officiële Bekendmakingen, EU feeds and regional news, curated before they reach the board; recommended interventions per dossier, each card ending with the same line — AI advises, the professional decides; dossier management with a markdown editor, template gallery, archiving and saved searches, and notifications per followed dossier. Callout: since v2026.08.27 it is its own package, @ronl/pa-cockpit; the host declares what it provides, and the 44-file forked copy was removed](assets/slides/iou-architecture/slide-06-pa-cockpit.png)
  <figcaption>Eight criteria, curated signals, and advice the professional decides on</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Slide 7 of 25, board spotlight · work · tasks: Caseworker — de persoonlijke werkvoorraad (the personal work queue). A screenshot shows the task list next to a tree felling permit case review with its process data and process steps. Beside it: tasks from Operaton, claimed and completed on the board itself, where the task form comes from the deployed process definition and the decision comes back as a document; a rule catalogue in four tabs — organisations, services, rules with decision logic per rule, and concepts that link through to Skosmos; a process library served directly by the LDE backend, where only bundles with status active and the right owner come through; tools bringing eight together — CPSV Editor, CPRMV API, TriplyDB, Linked Data Explorer, Operaton Cockpit, with eDOCS, SAP and KMS marked coming soon. Callout: the section library under this board is reused by Caseworker V2, Infra-board and PA-Cockpit, so changes there ripple through — hence 185 tests across 26 files](assets/slides/iou-architecture/slide-07-caseworker.png)
  <figcaption>Operaton tasks, the rule catalogue and the process library in one place</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Slide 8 of 25, board spotlight · portfolio · phases: Infra-board — sturen op de faseladder (steering by the phase ladder). A screenshot shows the project portfolio as a Gantt timeline of 44 projects across RIP phases, 2022 to 2027. Beside it: My day, today's tasks, urgent or overdue, and my projects with each one's real current RIP phase; Portfolio, a Gantt timeline and a Kanban per phase over the twelve real RIP phases, R2.1 to R6.1, grouped by stage, with transitions and health in green, amber and red; Management, a work-in-progress and a done tab per phase with real process instances from Operaton, including the derived current step and the number of rework loops; a rail with real counts per mode behind login, where anonymous visitors used to see live-looking project figures next to a log-in notice. Callout: the highest frontend coverage, 99.64% on pages/infra-board; there is not a single end-to-end spec — a gap, not a decision](assets/slides/iou-architecture/slide-08-infra-board.png)
  <figcaption>Twelve real RIP phases, with real process instances behind them</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Slide 9 of 25, Infra-board · phase exit R2.1 · new in v2026.08.36: Een fase-uitgang ondertekenen (signing a phase exit). Some approval tasks are signed rather than ticked off, and where that is so a signing panel appears instead of a form. Four steps: 1 claim the task, an unclaimed task shows the claim button as always; 2 the panel replaces the form, building the phase document from the supplied template and opening the signing ceremony inside the panel; 3 sign, the project leader signs and the panel waits for the result itself, with nothing to tick; 4 the task closes itself, the signed document and the evidence attachment go to the project's eDOCS dossier and the process continues. Below: opt-in from the process model — one attribute, ronl:signatureRef="rip-pdp", set by the Linked Data Explorer on the task Accorderen Projectplan 4, switches the whole feature on, and a task without it, which is every ordinary task, is unchanged. Callout: if the panel seems to hang after signing, reload; the status is fetched fresh rather than kept in the panel, because a signature can arrive by two routes](assets/slides/iou-architecture/slide-09-ondertekenen.png)
  <figcaption>Signing replaces the form only where the process model asks for it</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Slide 10 of 25, board spotlight · Woo · compliance: Woo-dashboard — verantwoording in cijfers (accountability in figures). A screenshot shows the workload and intake view: requests per department and per subject, a donut of where requests come from, and repeat requesters. Beside it: an overview with traffic lights for compliance and lead time, and Woo in cijfers as a benchmark next to the province's own performance; Requests and Register, where the register is a deterministically generated set of 218 rows with filters and a command palette to move through it; Timeliness, Process, Publication and Objection as separate sections — where things stall, how long they take, and what has been actively made public; the same shell as the other boards — section router, dock and command palette — with its own charts. Callout: by test count the most thinly covered board, 39 tests across 12 files at 97.68% statement coverage; the board is small, not lightly proven](assets/slides/iou-architecture/slide-10-woo-dashboard.png)
  <figcaption>Compliance, lead times and active publication, benchmarked</figcaption>
</figure>

### The public knowledge base

<figure markdown style="width:100%; margin:0;">
  ![Slide 11 of 25, Open Regels Nederland · acc.publiek.open-regels.nl: De publieke kennisbank (the public knowledge base). A screenshot shows the English home page with one search box and cards for Announcements, News, Products and Services, Rule catalogue and Process library. Beside it: public information only — no personal data, no account, no login — for residents, businesses and civil servants of other organisations; one search bar over five sources, announcements, news, products and services, rule catalogue and process library, with facet counts computed server-side before that facet's own filter is applied; a data dictionary and Provenance in the navigation, with an NL/EN switch and a staff login through to the work environment; accountability in the footer, an accessibility statement (WCAG 2.1 AA) and open data and API, with a prerender per route plus a sitemap making the content findable. Callout: runs on acceptance (v2026.08.19) and there is no production environment yet; the Provenance tab from this presentation lives here](assets/slides/iou-architecture/slide-11-publieke-site.png)
  <figcaption>Everything a civil servant sees that is public, with no login</figcaption>
</figure>

See the [Public Site](ronl-business-api/user-guide/public-site.md) user guide.

### The design principle

<figure markdown style="width:100%; margin:0;">
  ![Slide 12 of 25, statement on blue, badge App, the design principle: Elk stadium levert een artefact op dat het volgende stadium ongewijzigd overneemt (every stage delivers an artefact the next stage takes over unchanged). Nothing is reinterpreted or retyped. The handover happens in an open format, so a decision can be traced back to the legal text it comes from](assets/slides/iou-architecture/slide-12-ontwerpprincipe.png)
  <figcaption>Every stage hands the next an artefact it takes over unchanged</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Slide 13 of 25, from regulation to execution: De pijplijn — vier stadia (the pipeline — four stages). 1 Legal analysis, in the Norm Editor (FLINT), deterministic, marked new in the stack: a lawyer records what the text says — which act, by whom, under which condition — not as a summary but as a formal frame linked to the article; output FLINT frames in TriplyDB. 2 CPSV publication, in the CPSV Editor, CPSV-AP 3.2.0 as RDF: the service is described in the European vocabulary — who carries it out, for whom, on what legal basis, with which conditions and evidence — machine-readable and so findable outside its own system; output the TriplyDB knowledge graph. 3 Design and deploy, in the Linked Data Explorer, BPMN, DMN and forms: execution follows from the published service — process model, decision tables, form fields and letters — and what is built here points back to the rule, and the rule to the article; output Operaton plus a bundle. 4 Verify and go live, in MijnOmgeving, acc to prod, Flevoland: the application runs first on acceptance with real test cases, then in production within the province's tenant, and the citizen sees one environment; output application and decision](assets/slides/iou-architecture/slide-13-de-pijplijn.png)
  <figcaption>Four stages, four components, and what each one hands on</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Slide 14 of 25, one concept in three places: De conceptketen (the concept chain). (a) In the law: concepts and definitions as they appear in legal texts, quoted unchanged with a reference to article and paragraph — Juriconnect. (b) In the rules: interpreted concepts in rule models, where the interpretation decision falls, and it is recorded rather than hidden implicitly in code. (c) In the registries: data points that serve as evidence for the concepts in (b) — BRP, BAG, Kadaster, Handelsregister — each with its own legal basis. Beneath them the rule catalogue spans (a) and (b), the data dictionary spans (c), and the process library binds (a), (b) and (c) to execution](assets/slides/iou-architecture/slide-14-de-conceptketen.png)
  <figcaption>The law, the rules and the registries, bound together by the process library</figcaption>
</figure>

---

## Part two — Dev: how it is built and safeguarded

<figure markdown style="width:100%; margin:0;">
  ![Slide 15 of 25, section divider on green, badge Dev: Dev — deel twee, Hoe het gebouwd en geborgd is (part two, how it is built and safeguarded). The components and standards that carry the chain, the evidence per board, and the way of working and the gates through which anything reaches acceptance or production](assets/slides/iou-architecture/slide-15-dev-serie.png)
  <figcaption>Part two — how it is built and safeguarded</figcaption>
</figure>

### Components and standards

<figure markdown style="width:100%; margin:0;">
  ![Slide 16 of 25, the RONL ecosystem: De componenten van het ecosysteem (the components of the ecosystem), six cards with version and environment as of 30 August 2026. Norm Editor v2026.07.0 ACC, FLINT interpretations of legal sources — annotate fragments, build Fact, Act and Claim-duty frames, export to RDF — at regeleditor.open-regels.nl. CPSV Editor v2026.08.3 ACC, CPSV-AP 3.2.0-conformant RDF/Turtle for Dutch government services, at acc.cpsv.open-regels.nl. Linked Data Explorer v2026.08.9 ACC, SPARQL querying and BPMN/DMN orchestration on TriplyDB, deploying bundles to Operaton, at acc.linkeddata.open-regels.nl. CPRMV API v0.4.1 PROD, retrieves individual rules from BWB, CVDR and CELLAR and transforms them to CPRMV RDF, recognising Juriconnect and ELI references, Python/FastAPI with MCP at /mcp. RONL Business API v2026.08.36 ACC, authentication and process orchestration for execution — OIDC/JWT via Keycloak, rules via Operaton — at acc.mijn.open-regels.nl. Public search site v2026.08.19 ACC, highlighted: rule catalogue, data dictionary and the Provenance tab, without login, on demonstration data, at acc.publiek.open-regels.nl](assets/slides/iou-architecture/slide-16-componenten.png)
  <figcaption>Six components, as they stood on 30 August 2026</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Slide 17 of 25, open source, open standards: Stack, standaarden en naleving (stack, standards and compliance). Stack and licences: Keycloak for IAM, Apache 2.0; Operaton for BPMN/DMN, Apache 2.0; Node.js with Express, and React, MIT; PostgreSQL, Redis and Caddy, PostgreSQL, BSD and Apache licences; CPRMV API on FastAPI, EUPL-1.2; TriplyDB and eDOCS, closed. What stays closed stays inside the organisation, and so can be replaced without breaking the chain. Open standards carrying the chain: CPSV-AP, CPRMV, FLINT, RDF/Turtle, BPMN, DMN, NL-SBB, Juriconnect, SKOS, OIDC. Compliance: BIO, NEN 7510, AVG/GDPR, WCAG 2.1 AA, EUPL-1.2. Callout: access runs through Keycloak — OIDC/JWT, a validated token, and per municipality its own tenant and theme](assets/slides/iou-architecture/slide-17-stack-en-standaarden.png)
  <figcaption>Open source and open standards, with the two closed parts kept replaceable</figcaption>
</figure>

### Signing and evidence

<figure markdown style="width:100%; margin:0;">
  ![Slide 18 of 25, RONL Business API · developer · measured on ACC at 15dfbf9: ValidSign — ondertekenen achter drie sloten (signing behind three locks). ValidSign is OneSpan Sign in a European deployment; the licence is production-only, with no sandbox, and the API key covers the whole account. Three locks for live signing: 1 stub mode off, VALIDSIGN_STUB_MODE=false; 2 key present, VALIDSIGN_API_KEY; 3 tier on the allowlist, DEPLOYMENT_ENV in VALIDSIGN_LIVE_TIERS. VALIDSIGN_LIVE_TIERS is empty by default, so no environment signs for real until someone names it deliberately — an allowlist, not an exclusion of acceptance; adding acceptance lets ACC sign exactly as production does, and which environment signs is a configuration decision, not one the code makes for you. The signer's identity comes entirely from the Keycloak token; a real token turned out to carry no email or name claim, which would have refused creation for every user, exactly as designed and unusable, and three protocol mappers fix that, added idempotently by a script. Two of the five routes sit outside JWT, deliberately: the callback comes from ValidSign's cloud, which sends no bearer token, so it is checked against a shared secret; the stub ceremony loads in an iframe, which cannot carry a token. Completion is one idempotent path with two callers, the webhook and a poller that sweeps every 15 seconds because that cloud cannot reach localhost. Stub package ids were sequential and are now random UUIDs, because the ceremony URL is the authority. Both pre-auth routes share one rate limiter on client IP, 60 per minute. Callout: six design assumptions proved wrong under live testing, against production ValidSign, real eDOCS and a real browser — an iframe that loaded its own landing page, and 27-byte stub documents that uploaded perfectly and could not be opened; each is written up as a correction, not silently rewritten](assets/slides/iou-architecture/slide-18-validsign.png)
  <figcaption>Three locks before anything is signed for real, and six assumptions corrected</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Slide 19 of 25, measured per board, v2026.08.36, 30 August 2026: Wat de boards aan bewijs dragen (what evidence the boards carry). A table of unit tests, statement coverage and end-to-end tests. PA-Cockpit: package 41 files and 368 tests, backend 16 files and 533 tests; 86.16%, backend 98.32%; 2 specs, 7 tests. Caseworker: 43 files, 329 tests; 86.33% and 81.27%; 2 specs, 2 tests. Infra-board: 17 files, 188 tests; 99.64%, the highest in the frontend; 2 specs, 8 tests. Woo-dashboard: 15 files, 66 tests; 97.68%; none yet. Notes: the 185 tests across 26 files in the section library under Caseworker protect three of the four boards, not one. On 30 August all three Playwright suites ran against a full local stack, 44 tests, all green; one of them runs in CI, the public PA demo's (11 tests); the frontend suite (27 tests over 10 specs) needs Keycloak, Postgres, Redis, Operaton and an LDE backend, and no one on a runner starts that stack. Callout: high coverage says nothing about what a unit test by construction cannot see; every mock-mode defect in the cockpit was invisible to the unit suites, because a component test mocks exactly the seam that was broken — which is why the end-to-end column is the one that counts](assets/slides/iou-architecture/slide-19-bewijs.png)
  <figcaption>Unit tests, coverage and end-to-end specs per board — the last column counts most</figcaption>
</figure>

The prose behind these two slides is in the RONL Business API developer docs:
[ValidSign signing](ronl-business-api/developer/validsign-signing.md) and
[Testing](ronl-business-api/developer/testing/overview.md).

### How the work is done

<figure markdown style="width:100%; margin:0;">
  ![Slide 20 of 25, contributing · development workflow: Werkwijze — vijf stadia (way of working — five stages). 1 Design, in Claude Design, only where the UX itself is still an open question; a large change within an existing pattern skips this stage. 2 Handoff, design, standalone HTML, screenshots, README and PROMPT — briefing material that does not enter history as repository content. 3 Implementation, in Claude Code, with session memory and red/green TDD: first the failing test, then the minimal code that makes it pass. 4 Release, /bump-release per repository, each with its own changelog shape; the release lands through a pull request, never as a local fast-forward. 5 Documentation, /iou-document-patch brings this documentation site back in sync with the component after each release. Footer: a capability lives at user level when it describes how you work, and at project level when it depends on what the repository is — which is why /bump-release exists three times and /iou-document-patch exactly once](assets/slides/iou-architecture/slide-20-werkwijze.png)
  <figcaption>Design, handoff, implementation, release, documentation</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Slide 21 of 25, contributing · working with Claude Code: Implementatie — testen, subagents en grenzen (implementation — tests, subagents and boundaries). Red/green TDD: the failing test first, and that test must be seen to fail, for the expected reason; if it passes before the implementation, it tests something other than it claims. Where TDD does not fit, that is said: a documentation change has no failing test. Subagents and review: each task goes to a fresh subagent with only what that task needs; a separate reviewer reads the diff, and self-review does not replace that. Progress is kept in a ledger with commits and decisions, not only in the conversation. Where briefing and source code clash, the source code wins. Recorded boundaries: ten rules in ~/.claude/CLAUDE.md, among them — never bypass a verification gate; ask permission for every commit; never merge or force-push a shared branch unasked; never start or stop a dev server; no Claude attribution in commit messages](assets/slides/iou-architecture/slide-21-implementatie.png)
  <figcaption>Tests seen to fail, fresh subagents, and boundaries written down</figcaption>
</figure>

The five stages are written out in [Development Workflow](contributing/development-workflow/overview.md),
and the boundaries in [Skills and Boundaries](contributing/development-workflow/skills-and-boundaries.md).

### Gates and the supply chain

<figure markdown style="width:100%; margin:0;">
  ![Slide 22 of 25, contributing · code standards: Wat een merge blokkeert (what blocks a merge). From push to merge: feature branch, nothing runs; pull request to acc, audit plus build and deploy; audit fails, merge blocked; audit passes, merge allowed; push directly to acc, refused. The ruleset acc supply-chain gate on refs/heads/acc requires a pull request plus the audit check, with no bypass actors; both rules are needed together, since the check alone would still let a direct push through. What is enforced where: git hooks (Husky), pre-commit lints and formats staged files and pre-push checks the whole tree. Callout: none of the three repositories runs the test suite in a hook; a green hook is no proof that nothing is broken — only CI or your own run says that. CI: the RONL Business API has nine workflows, the Linked Data Explorer seven, the CPSV Editor three, and every deploy with something to test runs the suite before the build. Commits: Conventional Commits, enforced mechanically only by the Norm Editor, through a commit-msg hook](assets/slides/iou-architecture/slide-22-wat-blokkeert.png)
  <figcaption>A required pull request and a required check — neither is enough alone</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Slide 23 of 25, contributing · supply-chain pinning: Niets in de pijplijn mag zweven (nothing in the pipeline may float). Unpinned references brought to zero: RONL Business API 49 to 0, Linked Data Explorer 40 to 0, CPSV Editor 16 to 0 as the pilot. Five parts: a zizmor policy in the repository, every uses: pinned to a commit digest, a blocking audit job, Renovate maintaining the pins with a fourteen-day waiting period — and no waiting period for security advisories — and the branch ruleset that turns it into enforcement. The controls live in each repository, not at organisation level, so they travel with the code whichever remote hosts it. What this does not cover, written down rather than glossed over: main carries none of it, the gate is on acc only and a production deploy does not get those guarantees; the Static Web Apps container cannot be pinned, and where skip_app_build is missing that container builds what goes live; zizmor validates the form of a pin, never its truth; this documentation repository is a deliberately deferred gap, with floors using >= and no lockfile. Each exemption register lives in SECURITY-PIPELINE.md; a register that claims full coverage produces an unresolvable finding at the first audit — and then the gate gets weakened](assets/slides/iou-architecture/slide-23-supply-chain.png)
  <figcaption>Every action pinned, and what pinning does not cover written down</figcaption>
</figure>

Current detail: [Code Standards](contributing/code-standards.md) and
[Supply-Chain Pinning](contributing/supply-chain.md). See also the note at the top of
this page.

### Contributing, and what comes next

<figure markdown style="width:100%; margin:0;">
  ![Slide 24 of 25, contributing · documentation architecture: Bijdragen en documenteren (contributing and documenting). Two routes in: maintainers follow the development workflow; external contributors fork, work on a feature/, fix/ or docs/ branch and open a merge request against acc. First an issue, then the work; Conventional Commits; for every English page, update its Dutch counterpart too. Six repositories on git.open-regels.nl; CI/CD runs on GitHub Actions; code of conduct, Contributor Covenant; licence, EUPL-1.2. Users contribute through the Submit a use case form. One site, two languages, four perspectives: MkDocs Material on Azure Static Web Apps, English as the source and Dutch as the translation, with shared assets, stylesheets and abbreviations. Each component has the same four perspectives — Features, User Guides, Developer Docs and References. The depth differs per component, explicitly: release-tagged components get full guides, and the short-cycle RONL Business API gets a short page per board while that board is on acceptance](assets/slides/iou-architecture/slide-24-bijdragen.png)
  <figcaption>Two routes in, and one site with four perspectives per component</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Slide 25 of 25, closing slide on blue, badge App, where we ask for your decision: Vervolgstappen (next steps). 01 Gate to production: the supply-chain gate is on acc; bringing it to main — and taking this documentation repository along — is the next task. 02 Who may really sign: VALIDSIGN_LIVE_TIERS is empty, so today no environment signs for real; which tier may — and when — is a product-owner decision. 03 From example to chain: the provenance content is currently written by hand; filling it from TriplyDB, CPSV-AP and the FLINT frames is the next investment. Footer: iou-architectuur.open-regels.nl · acc.publiek.open-regels.nl/herkomst · EUPL-1.2](assets/slides/iou-architecture/slide-25-vervolgstappen.png)
  <figcaption>Three decisions: a gate to production, who may sign, and a generated chain</figcaption>
</figure>

See [Contributing](contributing/index.md) and
[Documentation Architecture](contributing/doc-architecture/overview.md).
