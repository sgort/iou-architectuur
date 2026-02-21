# Overview

This documentation site serves as the central reference for the IOU Architecture Framework and the RONL ecosystem. It is built with MkDocs and published to Azure Static Web Apps, supporting both English and Dutch.

## Site Structure

The site is organised into two language trees sharing a common set of assets, stylesheets, and abbreviations.

```mermaid
graph TB
    subgraph "IOU Architecture Documentation Site"
        subgraph "English (Primary)"
            EN_HOME[Home/Index]
            EN_RONL[RONL Business API]
            EN_CPSV[CPSV Editor]
            EN_LDE[Linked Data Explorer]
            EN_CONTRIB[Contributing]
        end

        subgraph "Nederlands (Translation)"
            NL_HOME[Home/Index]
            NL_RONL[RONL Business API]
            NL_CPSV[CPSV Editor]
            NL_LDE[Linked Data Explorer]
            NL_CONTRIB[Bijdragen]
        end

        subgraph "Shared Resources"
            ASSETS[Assets<br/>images, diagrams, screenshots]
            CSS[Custom CSS<br/>NL Design System]
            ABBREV[Abbreviations<br/>& Snippets]
        end
    end

    EN_HOME --> EN_RONL
    EN_HOME --> EN_CPSV
    EN_HOME --> EN_LDE
    EN_HOME --> EN_CONTRIB

    NL_HOME --> NL_RONL
    NL_HOME --> NL_CPSV
    NL_HOME --> NL_LDE
    NL_HOME --> NL_CONTRIB

    EN_CPSV -.uses.-> ASSETS
    EN_LDE -.uses.-> ASSETS
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

English pages are the primary source of truth. Dutch pages are translations or placeholders that link back to the English version until a translation is available. Component documentation originates in each component's own repository and is synced into this site.

```mermaid
graph LR
    subgraph "Source Repositories"
        SRC_RONL[RONL Business API<br/>README + Docs]
        SRC_CPSV[CPSV Editor<br/>README + Docs]
        SRC_LDE[Linked Data Explorer<br/>README + Docs]
    end

    subgraph "Sync Process"
        SCRIPT[sync-content<br/>Manual Extraction]
    end

    subgraph "IOU Docs Site"
        DOC_RONL[docs/en/ronl-business-api/]
        DOC_CPSV[docs/en/cpsv-editor/]
        DOC_LDE[docs/en/linked-data-explorer/]
    end

    SRC_RONL -->|via| SCRIPT
    SRC_CPSV -->|via| SCRIPT
    SRC_LDE -->|via| SCRIPT

    SCRIPT --> DOC_RONL
    SCRIPT --> DOC_CPSV
    SCRIPT --> DOC_LDE

    DOC_RONL -.translate.-> NL_RONL[docs/nl/ronl-business-api/]
    DOC_CPSV -.translate.-> NL_CPSV[docs/nl/cpsv-editor/]
    DOC_LDE -.translate.-> NL_LDE[docs/nl/linked-data-explorer/]

    style SRC_RONL fill:#ffe1e1
    style SRC_CPSV fill:#ffe1e1
    style SRC_LDE fill:#e1ffe1
    style SCRIPT fill:#ffd700
    style NL_RONL fill:#e17000
    style NL_CPSV fill:#e17000
    style NL_LDE fill:#e17000
```
