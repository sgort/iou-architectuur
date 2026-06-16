# Project Structure

**Version:** 1.10.x (fully modularised)  
**Framework:** React 19

---

## Directory layout

```
cpsv-editor/
├── public/
│   ├── index.html
│   ├── favicon.svg
│   ├── manifest.json
│   └── examples/
│       └── organizations/
│           ├── toeslagen/          # Zorgtoeslag example DMN + test cases
│           ├── duo/                # DUO example DMN + test cases
│           └── svb/                # SVB AOW example DMN + test cases
│
├── src/
│   ├── App.js                      # Main orchestrator: layout, navigation, import
│   ├── App.css
│   ├── index.js                    # React entry point
│   ├── index.css                   # Global styles, Tailwind imports
│   │
│   ├── components/
│   │   ├── PreviewPanel.jsx        # Live TTL preview side panel
│   │   ├── PublishDialog.jsx       # TriplyDB publish dialog + pre-publish SHACL panel
│   │   └── tabs/
│   │       ├── index.js            # Barrel export
│   │       ├── ServiceTab.jsx
│   │       ├── CostSection.jsx     # Embedded in ServiceTab
│   │       ├── OutputSection.jsx   # Embedded in ServiceTab
│   │       ├── OrganizationTab.jsx
│   │       ├── LegalTab.jsx
│   │       ├── RulesTab.jsx        # RPP: Rules
│   │       ├── ParametersTab.jsx   # RPP: Parameters
│   │       ├── CPRMVTab.jsx        # RPP: Policy
│   │       ├── DMNTab.jsx          # DMN upload, deploy, test
│   │       ├── ConceptsTab.jsx     # NL-SBB concept definitions
│   │       ├── VendorTab.jsx       # Vendor integration (hosts the iKnow UI)
│   │       ├── IKnowMappingTab.jsx # iKnow mapping config (rendered inside VendorTab)
│   │       ├── IKnowImportTab.jsx  # iKnow import (rendered inside VendorTab)
│   │       └── ChangelogTab.jsx
│   │
│   ├── hooks/
│   │   ├── useEditorState.js       # Centralised state management
│   │   ├── useArrayHandlers.js     # DRY CRUD for array-based fields
│   │   └── useDsoImport.js         # DSO → DMN deep-link import (v1.9.6)
│   │
│   ├── utils/
│   │   ├── index.js                # Barrel export
│   │   ├── constants.js            # Shared constants, TTL_NAMESPACES, dropdown options
│   │   ├── ttlGenerator.js         # TTL generation class
│   │   ├── ttlHelpers.js           # TTL string/IRI helpers (escapeTTLString, sanitizeIri, …)
│   │   ├── importHandler.js        # Import logic
│   │   ├── cprmvImport.js          # CPRMV 0.4.1 Rules API → flat model (v1.10.0)
│   │   ├── shaclHelper.js          # Pre-publish SHACL validation (v1.10.0)
│   │   ├── dmnHelpers.js           # DMN-specific utilities
│   │   ├── validators.js           # Form validation
│   │   ├── parseTTL.enhanced.js    # TTL parser with DMN preservation
│   │   ├── triplydbHelper.js       # TriplyDB API integration, buildGraphIRI
│   │   ├── ronlHelper.js           # RONL vocabulary SPARQL queries
│   │   └── iknowParser.js          # iKnow XML parser
│   │
│   ├── data/
│   │   ├── changelog.json          # Powers ChangelogTab
│   │   ├── roadmap.json            # Planned features for ChangelogTab
│   │   └── cprmv-example.json      # Conformant 0.4.1 example for CPRMV "Load Example"
│   │
│   └── config/
│       ├── vocabularies.config.js  # RDF vocabulary mappings for parser
│       └── iknow-mappings/         # iKnow default field mapping templates
│
├── .github/
│   └── workflows/
│       └── azure-static-web-apps.yml
│
└── package.json
```

---

## Key modules

### `src/hooks/useEditorState.js`

Centralises all editor state into a single custom hook, providing:

- State slices for every tab (service, organization, legalResource, ronlAnalysis, ronlMethod, temporalRules, parameters, cprmvRules, concepts, cost, output, dmnData, vendorService, iknowMappingConfig, triplyDBConfig)
- Shared RONL vocabulary concepts (analysis/method/vendor), fetched once on mount and shared across the Legal and Vendor tabs
- A `clearAllData()` action that resets the entire editor

This replaces dozens of individual `useState` calls that were previously spread across `App.js`.

### `src/hooks/useArrayHandlers.js`

Provides DRY CRUD handlers for any array-based state (rules, parameters, CPRMV rules):

```javascript
{
  handleAdd,        // Append new item with auto-incremented ID
  handleUpdate,     // Update item by ID with partial patch
  handleRemove,     // Remove item by ID
  handleUpdateField,// Update a single field (convenience wrapper)
  handleClear,      // Clear the entire array
  handleReplace     // Replace the entire array
}
```

IDs use `Math.max(...ids) + 1` — stable under rapid additions, unlike `Date.now()`.

### `src/utils/ttlGenerator.js`

Class-based TTL generation. Each tab section has a corresponding generate method. Called by `App.js` on export and by `PreviewPanel` on every state change.

### `src/utils/parseTTL.enhanced.js`

Full TTL parser. Handles vocabulary detection, multi-line values, namespace resolution, date parsing, array extraction (keywords), and DMN block capture and preservation. Returns a data structure matching the editor state shape for direct use in `useEditorState`.

### `src/config/vocabularies.config.js`

Configuration-driven vocabulary management. Defines namespace-to-prefix mappings, RDF type-to-editor-section mappings, and property aliases, plus the `detectEntityType()` helper. See [Vocabulary Configuration](vocabulary-configuration.md) for how to extend it.

---

## RPP tab mapping

| Layer | Tab | Badge label | Colour |
|---|---|---|---|
| Rules | RulesTab | RPP Layer: Rules | Blue |
| Policy | CPRMVTab | RPP Layer: Policy | Purple |
| Parameters | ParametersTab | RPP Layer: Parameters | Green |

---

## State flow

**Import:**

```
TTL file → importHandler.js → parseTTL.enhanced.js → useEditorState.set*() → tabs re-render
```

**Export / Live preview:**

```
useEditorState → ttlGenerator.js generate() → combine sections → PreviewPanel / download
```
