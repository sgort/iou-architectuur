---
scope: cross-cutting
---

# Overview

This documentation site serves as the central reference for the IOU Architecture Framework and the RONL ecosystem. It is built with MkDocs and published to Azure Static Web Apps, supporting both English and Dutch.

---

## Site Structure

The site is organised into two language trees sharing a common set of assets, stylesheets, and abbreviations.

```mermaid
graph TB
    subgraph "IOU Architecture Documentation Site"
        subgraph "English (Primary)"
            EN_HOME[Home/Index]
            EN_DECK[IOU Architecture slides]
            EN_RONL[RONL Business API]
            EN_NORM[Norm Editor]
            EN_CPSV[CPSV Editor]
            EN_LDE[Linked Data Explorer]
            EN_CPRMV[CPRMV API]
            EN_CONTRIB[Contributing]
        end

        subgraph "Nederlands (Translation)"
            NL_HOME[Home/Index]
            NL_DECK[IOU Architecture slides]
            NL_RONL[RONL Business API]
            NL_NORM[Norm Editor]
            NL_CPSV[CPSV Editor]
            NL_LDE[Linked Data Explorer]
            NL_CPRMV[CPRMV API]
            NL_CONTRIB[Contributing]
        end

        subgraph "Shared Resources"
            ASSETS[Assets<br/>images, diagrams, screenshots]
            CSS[Custom CSS<br/>NL Design System]
            FONT[Code font<br/>JetBrains Mono, vendored]
            ABBREV[Abbreviations<br/>& Snippets]
        end
    end

    EN_HOME --> EN_DECK
    EN_HOME --> EN_RONL
    EN_HOME --> EN_NORM
    EN_HOME --> EN_CPSV
    EN_HOME --> EN_LDE
    EN_HOME --> EN_CPRMV
    EN_HOME --> EN_CONTRIB

    NL_HOME --> NL_DECK
    NL_HOME --> NL_RONL
    NL_HOME --> NL_NORM
    NL_HOME --> NL_CPSV
    NL_HOME --> NL_LDE
    NL_HOME --> NL_CPRMV
    NL_HOME --> NL_CONTRIB

    EN_CPSV -.uses.-> ASSETS
    EN_LDE -.uses.-> ASSETS
    NL_CPSV -.uses.-> ASSETS
    NL_LDE -.uses.-> ASSETS

    EN_HOME -.styled by.-> CSS
    NL_HOME -.styled by.-> CSS
    CSS -.serves.-> FONT
    EN_HOME -.includes.-> ABBREV
    NL_HOME -.includes.-> ABBREV

    LANG_SWITCH[Language Switcher] -.->|EN| EN_HOME
    LANG_SWITCH -.->|NL| NL_HOME

    style EN_HOME fill:#4a90e2
    style NL_HOME fill:#e17000
    style ASSETS fill:#50c878
    style LANG_SWITCH fill:#ffd700
```

---

## Content Sources

English pages are the primary source of truth. Dutch pages are translations or placeholders that link back to the English version until a translation is available. Component documentation is brought into this site by the `/iou-document-patch` skill, which reads each component's changelog at its released commit and patches the affected pages. It covers five components: the three applications, the Norm Editor and CPRMV.

```mermaid
graph LR
    subgraph "Source Repositories"
        SRC_RONL[RONL Business API<br/>changelog + source]
        SRC_NORM[Norm Editor<br/>changelog + source]
        SRC_CPSV[CPSV Editor<br/>changelog + source]
        SRC_LDE[Linked Data Explorer<br/>changelog + source]
        SRC_CPRMV[CPRMV<br/>changelog + source]
    end

    subgraph "Sync Process"
        SCRIPT["/iou-document-patch<br/>skill: changelog → pages"]
    end

    subgraph "IOU Docs Site"
        DOC_RONL[docs/en/ronl-business-api/]
        DOC_NORM[docs/en/norm-editor/]
        DOC_CPSV[docs/en/cpsv-editor/]
        DOC_LDE[docs/en/linked-data-explorer/]
        DOC_CPRMV[docs/en/cprmv-api/]
    end

    SRC_RONL -->|via| SCRIPT
    SRC_NORM -->|via| SCRIPT
    SRC_CPSV -->|via| SCRIPT
    SRC_LDE -->|via| SCRIPT
    SRC_CPRMV -->|via| SCRIPT

    SCRIPT --> DOC_RONL
    SCRIPT --> DOC_NORM
    SCRIPT --> DOC_CPSV
    SCRIPT --> DOC_LDE
    SCRIPT --> DOC_CPRMV

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
