# Documentation Architecture Diagram

## Overview

```mermaid
graph TB
    subgraph "IOU Architecture Documentation Site"
        subgraph "English (Primary)"
            EN_HOME[Home/Index]
            EN_IOU[IOU Architecture<br/>Framework]
            EN_CPSV[CPSV Editor<br/>Documentation]
            EN_LDE[Linked Data Explorer<br/>Documentation]
            EN_BACKEND[Shared Backend<br/>Documentation]
            EN_CONTRIB[Contributing<br/>Guidelines]
        end
        
        subgraph "Nederlands (Translation)"
            NL_HOME[Home/Index]
            NL_IOU[IOU Architectuur<br/>Framework]
            NL_CPSV[CPSV Editor<br/>Documentatie]
            NL_LDE[Linked Data Explorer<br/>Documentatie]
            NL_BACKEND[Gedeelde Backend<br/>Documentatie]
            NL_CONTRIB[Bijdrage<br/>Richtlijnen]
        end
        
        subgraph "Shared Resources"
            ASSETS[Assets<br/>images, diagrams, screenshots]
            CSS[Custom CSS<br/>NL Design System]
            ABBREV[Abbreviations<br/>& Snippets]
        end
    end
    
    EN_HOME --> EN_IOU
    EN_HOME --> EN_CPSV
    EN_HOME --> EN_LDE
    EN_HOME --> EN_BACKEND
    EN_HOME --> EN_CONTRIB
    
    NL_HOME --> NL_IOU
    NL_HOME --> NL_CPSV
    NL_HOME --> NL_LDE
    NL_HOME --> NL_BACKEND
    NL_HOME --> NL_CONTRIB
    
    EN_IOU -.uses.-> ASSETS
    EN_CPSV -.uses.-> ASSETS
    EN_LDE -.uses.-> ASSETS
    
    NL_IOU -.uses.-> ASSETS
    NL_CPSV -.uses.-> ASSETS
    NL_LDE -.uses.-> ASSETS
    
    EN_HOME -.styled by.-> CSS
    NL_HOME -.styled by.-> CSS
    
    EN_HOME -.includes.-> ABBREV
    NL_HOME -.includes.-> ABBREV
    
    LANG_SWITCH[Language Switcher] -.->|EN| EN_HOME
    LANG_SWITCH -.->|NL| NL_HOME
    
    style EN_HOME fill:#4a90e2
    style NL_HOME fill:#e17000
    style ASSETS fill:#50c878
    style LANG_SWITCH fill:#ffd700
```

## Content Sources

```mermaid
graph LR
    subgraph "Source Repositories"
        SRC_IOU[IOU Architecture<br/>Framework Docs]
        SRC_CPSV[CPSV Editor<br/>README + Docs]
        SRC_LDE[Linked Data Explorer<br/>README + Docs]
        SRC_BACKEND[Backend Package<br/>Documentation]
    end
    
    subgraph "Sync Process"
        MANUAL[Manual Conversion<br/>Quarterly Sync]
        SCRIPT[sync-content.sh<br/>Automated Extraction]
    end
    
    subgraph "IOU Docs Site"
        DOC_IOU[docs/en/iou-architecture/]
        DOC_CPSV[docs/en/cpsv-editor/]
        DOC_LDE[docs/en/linked-data-explorer/]
        DOC_BACKEND[docs/en/shared-backend/]
    end
    
    SRC_IOU -->|Native| DOC_IOU
    SRC_CPSV -->|via| SCRIPT
    SRC_LDE -->|via| SCRIPT
    SRC_BACKEND -->|via| SCRIPT
    
    SCRIPT --> DOC_CPSV
    SCRIPT --> DOC_LDE
    SCRIPT --> DOC_BACKEND
    
    DOC_IOU -.translate.-> DOC_IOU_NL[docs/nl/iou-architectuur/]
    DOC_CPSV -.translate.-> DOC_CPSV_NL[docs/nl/cpsv-editor/]
    DOC_LDE -.translate.-> DOC_LDE_NL[docs/nl/linked-data-explorer/]
    DOC_BACKEND -.translate.-> DOC_BACKEND_NL[docs/nl/gedeelde-backend/]
    
    style SRC_IOU fill:#e1f5ff
    style SRC_CPSV fill:#ffe1e1
    style SRC_LDE fill:#e1ffe1
    style SCRIPT fill:#ffd700
    style DOC_IOU_NL fill:#e17000
    style DOC_CPSV_NL fill:#e17000
    style DOC_LDE_NL fill:#e17000
    style DOC_BACKEND_NL fill:#e17000
```

## Build & Deploy Pipeline

```mermaid
graph TB
    DEV[Developer] -->|Edit Markdown| LOCAL[Local Repository]
    LOCAL -->|git push| GITLAB[GitLab Repository]
    
    GITLAB -->|Trigger| CI[GitLab CI/CD]
    
    CI -->|1. Install| DEPS[Python Dependencies<br/>mkdocs, mkdocs-material<br/>mkdocs-static-i18n]
    DEPS -->|2. Build| BUILD{mkdocs build}
    
    BUILD -->|3. Generate| EN_SITE[site/en/<br/>English Site]
    BUILD -->|3. Generate| NL_SITE[site/nl/<br/>Dutch Site]
    
    EN_SITE -->|4. Deploy| AZURE[Azure Static Web Apps]
    NL_SITE -->|4. Deploy| AZURE
    
    AZURE -->|5. Serve| PROD_EN[https://iou-architectuur.open-regels.nl/en/]
    AZURE -->|5. Serve| PROD_NL[https://iou-architectuur.open-regels.nl/nl/]
    
    USER[End Users] -->|Visit| PROD_EN
    USER -->|Visit| PROD_NL
    
    PROD_EN <-.Language Switch.-> PROD_NL
    
    style DEV fill:#4a90e2
    style GITLAB fill:#e17000
    style AZURE fill:#50c878
    style PROD_EN fill:#4a90e2
    style PROD_NL fill:#e17000
    style BUILD fill:#ffd700
```

## Navigation Structure

```
IOU Architecture Docs
│
├── 🇬🇧 English (/en/)
│   ├── 📖 Home
│   ├── 🏗️ IOU Architecture
│   │   ├── Framework Overview
│   │   ├── Ontological Architecture (Part 1)
│   │   ├── Implementation Architecture (Part 2)
│   │   ├── Roadmap & Evaluation (Part 3)
│   │   └── Deployment Guide
│   ├── ✏️ CPSV Editor
│   │   ├── Introduction
│   │   ├── Features
│   │   ├── 👤 User Guide
│   │   │   ├── Getting Started
│   │   │   ├── Service Definition
│   │   │   ├── Rules & Parameters
│   │   │   ├── DMN Integration
│   │   │   └── Import & Export
│   │   └── 🔧 Technical
│   │       ├── Architecture
│   │       ├── Standards Compliance
│   │       ├── Field Mapping
│   │       └── Development
│   ├── 🔍 Linked Data Explorer
│   │   ├── Introduction
│   │   ├── Features
│   │   ├── 👤 User Guide
│   │   │   ├── Getting Started
│   │   │   ├── SPARQL Queries
│   │   │   ├── DMN Orchestration
│   │   │   └── Chain Building
│   │   └── 🔧 Technical
│   │       ├── Architecture
│   │       ├── API Reference
│   │       └── Development
│   ├── 🔗 Shared Backend
│   │   ├── Overview
│   │   ├── API Documentation
│   │   ├── TriplyDB Integration
│   │   ├── Operaton Integration
│   │   └── Deployment
│   └── 🤝 Contributing
│       ├── How to Contribute
│       ├── Documentation Guide
│       └── Code Standards
│
└── 🇳🇱 Nederlands (/nl/)
    └── (Same structure, translated)
```

## Technology Stack

```mermaid
graph LR
    subgraph "Documentation Framework"
        MKDOCS[MkDocs 1.5+]
        MATERIAL[Material Theme 9.5+]
        I18N[i18n Plugin 1.2+]
        GIT_REV[Git Revision Plugin]
    end
    
    subgraph "Content Format"
        MD[Markdown Files]
        MERMAID[Mermaid Diagrams]
        CODE[Syntax Highlighting]
    end
    
    subgraph "Styling"
        TAILWIND[Tailwind CSS]
        CUSTOM[Custom CSS<br/>NL Design System]
    end
    
    subgraph "Deployment"
        GITLAB_CI[GitLab CI/CD]
        AZURE_SWA[Azure Static Web Apps]
        CDN[Global CDN]
    end
    
    MKDOCS --> MATERIAL
    MATERIAL --> I18N
    MATERIAL --> GIT_REV
    
    MD --> MKDOCS
    MERMAID --> MKDOCS
    CODE --> MKDOCS
    
    MATERIAL --> TAILWIND
    TAILWIND --> CUSTOM
    
    MKDOCS --> GITLAB_CI
    GITLAB_CI --> AZURE_SWA
    AZURE_SWA --> CDN
    
    style MKDOCS fill:#4a90e2
    style MATERIAL fill:#e17000
    style I18N fill:#50c878
    style AZURE_SWA fill:#4a90e2
```

## User Journey

```mermaid
journey
    title Documentation User Journey
    section Discovery
      Visit site: 5: User
      Choose language: 5: User
      Read homepage: 4: User
    section Navigation
      Browse sections: 5: User
      Use search: 5: User
      Follow cross-references: 4: User
    section Deep Dive
      Read architecture docs: 5: User
      View diagrams: 5: User
      Try code examples: 4: User
    section Action
      Copy code snippets: 5: User
      Download resources: 4: User
      Visit live apps: 5: User
    section Contribution
      Report issue: 3: User
      Suggest improvement: 4: User
      Submit PR/MR: 3: Developer
```

---

**Diagram Version**: 1.0  
**Last Updated**: January 2026
