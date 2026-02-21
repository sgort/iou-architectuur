# Technology Stack

## Documentation Framework

The site is built on MkDocs with the Material theme, the mkdocs-static-i18n plugin for dual-language support, and the git-revision-date-localized plugin for showing last-modified timestamps.

| Component | Technology | Version |
|---|---|---|
| Static site generator | MkDocs | 1.5+ |
| Theme | Material for MkDocs | 9.5+ |
| Internationalisation | mkdocs-static-i18n | 1.2+ |
| Revision dates | git-revision-date-localized | 1.2+ |
| Diagram rendering | Mermaid | via Material |
| Hosting | Azure Static Web Apps | — |
| CI/CD | GitHub Actions | — |

```mermaid
graph LR
    subgraph "Documentation Framework"
        MKDOCS[MkDocs 1.5+]
        MATERIAL[Material Theme 9.5+]
        I18N[mkdocs-static-i18n]
        GIT_REV[git-revision-date-localized]
    end

    subgraph "Content"
        MD[Markdown Files]
        MERMAID[Mermaid Diagrams]
        CODE[Syntax Highlighting]
    end

    subgraph "Styling"
        CUSTOM[Custom CSS<br/>NL Design System]
    end

    subgraph "Deployment"
        GH_ACTIONS[GitHub Actions]
        AZURE_SWA[Azure Static Web Apps]
        CDN[Global CDN]
    end

    MKDOCS --> MATERIAL
    MATERIAL --> I18N
    MATERIAL --> GIT_REV

    MD --> MKDOCS
    MERMAID --> MKDOCS
    CODE --> MKDOCS

    MATERIAL --> CUSTOM

    MKDOCS --> GH_ACTIONS
    GH_ACTIONS --> AZURE_SWA
    AZURE_SWA --> CDN

    style MKDOCS fill:#4a90e2
    style MATERIAL fill:#e17000
    style I18N fill:#50c878
    style AZURE_SWA fill:#4a90e2
```

## Build & Deploy Pipeline

Every push to `main` triggers a GitHub Actions workflow that builds the site and deploys to Azure Static Web Apps. The `acc` branch deploys to the acceptance environment.

```mermaid
graph TB
    DEV[Developer] -->|Edit Markdown| LOCAL[Local Repository]
    LOCAL -->|git push| GITHUB[GitHub Repository]

    GITHUB -->|Trigger| CI[GitHub Actions]

    CI -->|1. Install| DEPS[Python Dependencies<br/>mkdocs, mkdocs-material<br/>mkdocs-static-i18n]
    DEPS -->|2. Build| BUILD{mkdocs build}

    BUILD -->|3. Generate| EN_SITE[site/<br/>English Site at root]
    BUILD -->|3. Generate| NL_SITE[site/nl/<br/>Dutch Site]

    EN_SITE -->|4. Deploy| AZURE[Azure Static Web Apps]
    NL_SITE -->|4. Deploy| AZURE

    AZURE -->|5. Serve| PROD_EN[https://iou-architectuur.open-regels.nl/]
    AZURE -->|5. Serve| PROD_NL[https://iou-architectuur.open-regels.nl/nl/]

    USER[End Users] -->|Visit| PROD_EN
    USER -->|Visit| PROD_NL

    PROD_EN <-.Language Switch.-> PROD_NL

    style DEV fill:#4a90e2
    style GITHUB fill:#e17000
    style AZURE fill:#50c878
    style PROD_EN fill:#4a90e2
    style PROD_NL fill:#e17000
    style BUILD fill:#ffd700
```
