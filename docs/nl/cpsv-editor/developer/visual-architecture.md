# CPSV Editor - Visual Architecture

---

## Layer Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                         PRESENTATION LAYER                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                       App.js                             │  │
│  │  • State Management  • Navigation  • Layout  • Import    │  │
│  └────────────────┬─────────────────────────────────────────┘  │
│                   │                                            │
│  ┌────────────────┴──────────────────────────────────────────┐ │
│  │                    COMPONENTS                             │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │ │
│  │  │ Service  │  │   Org    │  │  Legal   │  │  Rules   │   │ │
│  │  │   Tab    │  │   Tab    │  │   Tab    │  │   Tab    │   │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │ │
│  │  ┌──────────┐  ┌──────────┐  ┌─────────────────────────┐  │ │
│  │  │Parameters│  │Changelog │  │   PreviewPanel          │  │ │
│  │  │   Tab    │  │   Tab    │  │   (Side Panel)          │  │ │
│  │  └──────────┘  └──────────┘  └─────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                        BUSINESS LOGIC LAYER                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                        UTILS                             │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │  │
│  │  │constants │  │ttlHelpers│  │validators│  │ parseTTL │  │  │
│  │  │   .js    │  │   .js    │  │   .js    │  │   .js    │  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                          DATA LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                         DATA                             │  │
│  │  ┌──────────────┐        ┌──────────────┐                │  │
│  │  │changelog.json│        │roadmap.json  │                │  │
│  │  └──────────────┘        └──────────────┘                │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

---

## Component Interaction Flow

```
┌─────────────────┐
                    │   User Action   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Tab Component │
                    │ (e.g., Service) │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  State Update   │
                    │  (via setXXX)   │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │                             │
     ┌────────▼────────┐          ┌────────▼────────┐
     │   App.js State  │          │  PreviewPanel   │
     │   (Updated)     │◄─────────│  (Auto-update)  │
     └────────┬────────┘          └─────────────────┘
              │
     ┌────────▼────────┐
     │  TTL Generation │
     │  (ttlHelpers)   │
     └────────┬────────┘
              │
     ┌────────▼────────┐
     │   Download TTL  │
     └─────────────────┘
```

---

## State Management Flow

```
┌───────────────────────────────────────────────────────────┐
│                         App.js State                      │
│                                                           │
│  service = { identifier, name, description, ... }         │
│  organization = { identifier, name, homepage }            │
│  legalResource = { bwbId, versionDate, title, ... }       │
│  temporalRules = [{ id, uri, extends, validFrom, ... }]   │
│  parameters = [{ id, notation, label, value, ... }]       │
│                                                           │
└───────┬─────────┬─────────┬─────────┬─────────┬───────────┘
        │         │         │         │         │
   ┌────▼───┐┌───▼────┐┌───▼────┐┌───▼────┐┌───▼──────┐
   │Service ││  Org   ││ Legal  ││ Rules  ││Parameters│
   │  Tab   ││  Tab   ││  Tab   ││  Tab   ││   Tab    │
   └────────┘└────────┘└────────┘└────────┘└──────────┘
        │         │         │         │         │
        └─────────┴─────────┴─────────┴─────────┘
                          │
                    ┌─────▼──────┐
                    │ generateTTL│
                    │  (Utils)   │
                    └─────┬──────┘
                          │
                   ┌──────▼───────┐
                   │PreviewPanel  │
                   │(Live Display)│
                   └──────────────┘
```

---

## Import/Export Data Flow

### Import Flow

```
┌──────────────┐
│  TTL File    │
│  (uploaded)  │
└──────┬───────┘
       │
┌──────▼──────────┐
│  parseTTL()     │
│  (Utils)        │
└──────┬──────────┘
       │
┌──────▼──────────┐
│  Extract Data:  │
│  • Service      │
│  • Organization │
│  • Legal        │
│  • Rules        │
│  • Parameters   │
└──────┬──────────┘
       │
┌──────▼──────────┐
│ Update App.js   │
│    State        │
└──────┬──────────┘
       │
┌──────▼──────────┐
│  Populate Tabs  │
│  (All 6 tabs)   │
└─────────────────┘
```

### Export Flow

```
┌──────────────┐
│  App.js      │
│  State       │
└──────┬───────┘
       │
┌──────▼──────────────┐
│  generateTTL()      │
│  • Service TTL      │
│  • Organization TTL │
│  • Legal TTL        │
│  • Rules TTL        │
│  • Parameters TTL   │
└──────┬──────────────┘
       │
┌──────▼──────────┐
│ Combine Sections│
│ Add Namespaces  │
└──────┬──────────┘
       │
┌──────▼──────────┐
│  Download .ttl  │
│  File to Disk   │
└─────────────────┘
```

---

## Split-Screen Layout

```
┌──────────────────────────────────────────────────────────────────┐
│                          HEADER                                  │
│  [🏛️ TTL Editor] [📄 Import] [👁️ Show Preview] [🗑️ Clear]        │
└──────────────────────────────────────────────────────────────────┘
┌──────────────────────────────┬───────────────────────────────────┐
│        EDITOR (Left)         │     PREVIEW (Right - Optional)    │
├──────────────────────────────┼───────────────────────────────────┤
│ ┌──────────────────────────┐ │ ┌───────────────────────────────┐ │
│ │  TAB NAVIGATION          │ │ │ Live TTL Preview  [Copy]      │ │
│ │  Service | Org | Legal   │ │ ├───────────────────────────────┤ │
│ └──────────────────────────┘ │ │ @prefix cpsv: <...> .         │ │
│ ┌──────────────────────────┐ │ │ @prefix cv: <...> .           │ │
│ │                          │ │ │                               │ │
│ │  TAB CONTENT             │ │ │ <service-uri> a               │ │
│ │  (Form Fields)           │ │ │   cpsv:PublicService ;        │ │
│ │                          │ │ │   dct:title "..."@nl ;        │ │
│ │  [Input fields...]       │ │ │   dct:description "..."@nl .  │ │
│ │                          │ │ │                               │ │
│ │  [More fields...]        │ │ │ [Updates automatically        │ │
│ │                          │ │ │  as you type!]                │ │
│ │                          │ │ │                               │ │
│ └──────────────────────────┘ │ ├───────────────────────────────┤ │
│                              │ │ 130 lines                     │ │
│ [✅ Validate] [⬇️ Download]  │ └───────────────────────────────┘ │
└──────────────────────────────┴───────────────────────────────────┘
│                          FOOTER                                  │
│  TTL Editor - Part of RONL Initiative                            │
└──────────────────────────────────────────────────────────────────┘
```

---

## File Dependencies

```
App.js
  ├─► components/tabs/
  │     ├─► ServiceTab
  │     ├─► OrganizationTab
  │     ├─► LegalTab
  │     ├─► RulesTab
  │     ├─► ParametersTab
  │     └─► ChangelogTab
  ├─► components/PreviewPanel
  ├─► utils/
  │     ├─► constants (NAMESPACES, OPTIONS)
  │     ├─► ttlHelpers (generateTTL functions)
  │     ├─► validators (validation functions)
  │     └─► parseTTL (import parsing)
  └─► lucide-react (Icons)

ChangelogTab
  └─► data/
        ├─► changelog.json
        └─► roadmap.json

Utils (parseTTL)
  └─► config/vocabularies_config
```

---

## Technology Stack

```
┌─────────────────────────────────────────┐
│            React 18.3.1                 │
│  (Component-based UI framework)         │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│         Tailwind CSS 3.x                │
│  (Utility-first styling)                │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│        Lucide React 0.263.1             │
│  (Icon library)                         │
└───────────────┬─────────────────────────┘
                │
┌───────────────▼─────────────────────────┐
│      Create React App (CRA)             │
│  (Build tooling & dev server)           │
└─────────────────────────────────────────┘
```

---

## Standards & Vocabularies

```
CPSV-AP 3.2.0 ─────┐
                   │
RONL Vocabulary ───┼──► TTL Generation
                   │
CPRMV Vocabulary ──┤
                   │
ELI (Legal) ───────┤
                   │
Dublin Core ───────┤
                   │
SKOS ──────────────┤
                   │
Schema.org ────────┘
```
