# Project Structure

**Version:** 1.9.x (fully modularised)  
**Framework:** React 18.3.1

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
│   │   ├── PublishDialog.jsx       # TriplyDB publish dialog
│   │   └── tabs/
│   │       ├── index.js            # Barrel export
│   │       ├── ServiceTab.jsx
│   │       ├── OrganizationTab.jsx
│   │       ├── LegalTab.jsx
│   │       ├── RulesTab.jsx        # RPP: Rules
│   │       ├── ParametersTab.jsx   # RPP: Parameters
│   │       ├── CPRMVTab.jsx        # RPP: Policy
│   │       ├── DMNTab.jsx          # DMN upload, deploy, test
│   │       ├── VendorTab.jsx       # Vendor integration
│   │       ├── IKnowMappingTab.jsx # iKnow import
│   │       └── ChangelogTab.jsx
│   │
│   ├── hooks/
│   │   ├── useEditorState.js       # Centralised state management
│   │   └── useArrayHandlers.js     # DRY CRUD for array-based fields
│   │
│   ├── utils/
│   │   ├── index.js                # Barrel export
│   │   ├── constants.js            # Shared constants, dropdown options
│   │   ├── ttlGenerator.js         # TTL generation class
│   │   ├── importHandler.js        # Import logic
│   │   ├── dmnHelpers.js           # DMN-specific utilities
│   │   ├── validators.js           # Form validation
│   │   ├── parseTTL.enhanced.js    # TTL parser with DMN preservation
│   │   ├── triplydbHelper.js       # TriplyDB API integration
│   │   ├── ronlHelper.js           # RONL vocabulary SPARQL queries
│   │   └── iknowParser.js          # iKnow XML parser
│   │
│   ├── data/
│   │   ├── changelog.json          # Powers ChangelogTab
│   │   ├── roadmap.json            # Planned features for ChangelogTab
│   │   └── cprmv-example.json      # Example data for CPRMV "Load Example"
│   │
│   └── config/
│       ├── vocabularies_config.js  # RDF vocabulary mappings for parser
│       └── iknow-mappings.js       # iKnow default field mapping templates
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

- State slices for every tab (service, organization, legalResource, temporalRules, parameters, cprmvRules, cost, output, dmnData, iknowMappingConfig)
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

### `src/config/vocabularies_config.js`

Configuration-driven vocabulary management. Defines namespace-to-prefix mappings, RDF type-to-editor-section mappings, and property aliases. See [Vocabulary Configuration](vocabulary-configuration.md) for how to extend it.

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
