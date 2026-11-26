---
component: CPRMV
---

# CPRMV API

The **CPRMV API** is a Python/FastAPI service that makes individual rules from Dutch and European legal publications accessible as structured, machine-readable data in real time. It implements the [Core Public Rule Management Vocabulary (CPRMV)](https://cprmv.open-regels.nl/respec/) — the RONL standard for expressing and managing public rules across analysis, formalisation, and codification methods.

---

## What it does

The API accepts a Rule Set identifier (a BWB, CVDR, EU CELLAR, Operaton DMN, IOU Norms, ROO or DSO ID) and an optional path of rule identifiers, then:

1. Finds the publication method whose identifier format matches the Rule Set ID.
2. Downloads the publication on-the-fly from its repository.
3. Transforms it to CPRMV — with the method's XSLT stylesheet for XML, or field by field for JSON.
4. Navigates the resulting rule tree to the requested rule.
5. Returns the rule in the requested format — `cprmv-json`, Turtle, JSON-LD, or other RDF serialisations.

No pre-loading or batch conversion is required. For BWB and CVDR, the API resolves "latest version valid on a given date" queries via SRU search of the publication repository.

Each publication and reference method is a Python module in `serve_api/methods/`, configured by its RDF method definition. See [Publication Repositories](features/publication-repositories.md).

`/raw` returns the publication untransformed.

---

## Ecosystem position

The CPRMV API is the **rule-access layer** of the RONL ecosystem. It bridges official legal publication repositories and the knowledge-graph-based tooling (CPSV Editor, Linked Data Explorer):

```mermaid
graph LR
    BWB["BWB Repository<br/>officiele-overheidspublicaties.nl"] -->|XML download| API
    CVDR["CVDR Repository<br/>officiele-overheidspublicaties.nl"] -->|XML download| API
    CELLAR["EU CELLAR<br/>publications.europa.eu"] -->|XML download| API
    OPERATON["Operaton<br/>operaton.open-regels.nl"] -->|DMN download| API
    NORMS["IOU Norms API<br/>Linked Data Explorer"] -->|JSON| API
    ROO["Register van Overheidsorganisaties<br/>api-organisaties.overheid.nl"] -->|JSON| API
    DSO["DSO, with the caller's key<br/>service.omgevingswet.overheid.nl"] -->|STTR download| API

    subgraph "CPRMV API"
        API["serve.py<br/>FastAPI"]
        METHODS["Method modules<br/>serve_api/methods/"]
        XSLT["XSLT Transforms<br/>bwb2cprmv.xsl<br/>cvdr2cprmv.xsl<br/>fmx42cprmv.xsl<br/>dmn13operaton2cprmv.xsl<br/>sttr2cprmv.xsl"]
        KG["Methods KG<br/>cprmvmethods.ttl<br/>cprmv.ttl"]
        API --- METHODS
        METHODS --- XSLT
        METHODS --- KG
    end

    API -->|cprmv-json / RDF| LDE["Linked Data Explorer"]
    API -->|cprmv-json / RDF| CPSV["CPSV Editor"]
    API -->|cprmv-json / RDF| EXT["External consumers"]
    API -->|ReSpec HTML| SPEC["CPRMV Specification<br/>/respec/"]
```

---

## Environments

| Environment | API (interactive docs) | CPRMV Specification |
|---|---|---|
| **Production** | [cprmv.open-regels.nl/docs](https://cprmv.open-regels.nl/docs) | [cprmv.open-regels.nl/respec/](https://cprmv.open-regels.nl/respec/) |
| **Production (alias)** | [cprmv.open-rules.eu/docs](https://cprmv.open-rules.eu/docs) | [cprmv.open-rules.eu/respec/](https://cprmv.open-rules.eu/respec/) |
| **Acceptance** | [acc.cprmv.open-regels.nl/docs](https://acc.cprmv.open-regels.nl/docs) | [acc.cprmv.open-regels.nl/respec/](https://acc.cprmv.open-regels.nl/respec/) |

Production is the stable tier and runs `main`, on its own VM that also answers as `cprmv.open-rules.eu`; acceptance runs `acc` on another. Each reports its tier, commit and image at `/health` ([Deployment](developer/deployment.md#hosts), [VM Deployment](developer/vm-deployment.md)).

Source, issues and pull requests are at [open-regels/cprmv](https://github.com/open-regels/cprmv) on GitHub, default branch `acc`. The published specification is at `https://standaarden.open-regels.nl/standards/cprmv/<version>/`, which GitLab Pages serves.

---

## Technology stack

Versions are those locked in `serve_api/requirements.txt`; `pyproject.toml` lists the direct dependencies without pins.

| Component | Technology | Version |
|---|---|---|
| API framework | FastAPI | 0.142.2 |
| ASGI toolkit / server | Starlette / Uvicorn | 1.7.0 / 0.54.0 |
| MCP integration | FastMCP (MCP SDK 2.3.0) | 4.1.8 |
| RDF library | rdflib | 7.6.0 |
| XML/XSLT processing | lxml | 6.1.3 |
| Pattern matching | parse | 1.22.2 |
| Date parsing | ciso8601 | 2.3.3 |
| Runtime | Python | 3.14 |
| Container | Docker (`python:3.14-bookworm`, pinned by digest) | — |
| Image registry | GitHub Container Registry (`ghcr.io/open-regels/cprmv-api`) | — |
| CI/CD | GitHub Actions; GitLab Pages for the specification | — |
| Deployment | An Azure VM per tier: Docker Compose, Caddy, and a reconciler on a systemd timer | — |

The MCP server is mounted on the API at `/mcp/` — see [MCP server](features/overview.md#mcp-server).

---

## Repository structure

```
cprmv/
├── serve_api/
│   ├── src/
│   │   ├── serve.py               # FastAPI application — endpoints, method loader, rule-path navigation
│   │   └── utils/
│   │       └── constants.py       # RDF namespaces, Path/Query parameter definitions
│   ├── methods/                   # Method modules: RuleMethod, PublicationMethod, ReferenceMethod,
│   │                              # SerialisationMethod, OrganisationRegister, ServiceRegister base classes;
│   │                              # core_web, core_api, core_xml, core_json, frbr_sru;
│   │                              # bwb, cvdr, fmx4, dmn13, sttr, repository_overheid_nl, eucellar,
│   │                              # operaton, iou, open_regels_nl, roo, dso, cprmvapi, juriconnect, eli
│   ├── data/                      # Written by `make methods`
│   │   ├── cprmv.ttl              # CPRMV vocabulary (loaded into the Methods KG)
│   │   ├── cprmvmethods.ttl       # Method registry + all method definitions (loaded into the Methods KG)
│   │   ├── bwb2cprmv.xsl          # XSLT: BWB XML → CPRMV Turtle
│   │   ├── cvdr2cprmv.xsl         # XSLT: CVDR XML → CPRMV Turtle
│   │   ├── fmx42cprmv.xsl         # XSLT: Formex v4 → CPRMV Turtle
│   │   ├── dmn13operaton2cprmv.xsl# XSLT: DMN 1.3 (Operaton) → CPRMV Turtle
│   │   └── sttr2cprmv.xsl         # XSLT: STTR (DSO) → CPRMV Turtle
│   ├── certs/                     # certSIGN Web CA intermediate for repository.officiele-overheidspublicaties.nl
│   ├── respec/                    # Static CPRMV specification per version (served at /respec/)
│   ├── test/                      # pytest suite
│   ├── Dockerfile
│   ├── Makefile                   # install, methods, deps / deps-linux, deps-upgrade, tests
│   ├── pip-compile.sh
│   ├── requirements.txt / requirements-dev.txt
│   └── pyproject.toml
├── rdf/
│   └── 0.4.0/ … 0.4.3/            # One folder per CPRMV version
│       ├── cprmv.ttl              # CPRMV OWL vocabulary
│       ├── cprmvmethods.ttl       # Method registry (acknowledged method lists)
│       ├── cprmv.shacl.ttl        # SHACL shapes for validation
│       └── methods/<module>/      # 0.4.2 and later: one folder per method module — method.ttl, README.md, XSLT
├── html/                          # ReSpec source for the CPRMV specification (shaclgen.py generates chapters)
├── deployment/vm/                 # The two VMs: Compose stacks and Caddyfiles per tier, reconciler, provisioning
├── scripts/                       # CI helper scripts and their bats tests
├── .github/                       # Workflows, zizmor configuration, rulesets as JSON
├── docs/                          # Design specs and implementation plans
├── .gitlab-ci.yml                 # ReSpec publication only
├── README.md
├── SECURITY-PIPELINE.md           # Register of every pin, the checks and the rulesets
├── renovate.json
├── METHODS.md                     # How methods are defined in RDF and implemented in Python
├── ROADMAP.md
└── CHANGELOG.md
```

---

## Licence

EUPL-1.2
