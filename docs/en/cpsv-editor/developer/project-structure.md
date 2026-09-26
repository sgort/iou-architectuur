---
component: CPSV Editor
---

# Project Structure

**Version:** CalVer, `YYYY.MM.N` (2026.09.7 at the time of writing)  
**Framework:** React 19, built with Vite and tested with Vitest

---

## Directory layout

The repository is `ttl-editor`. Test files are colocated with their source
(`foo.js` → `foo.test.js`) and are left out of the tree below; see
[Testing](testing.md#test-inventory).

```
ttl-editor/
├── index.html                      # Vite entry page (at the root, not in public/)
├── vite.config.mjs                 # Build and Vitest configuration; output to dist/
├── eslint.config.mjs               # ESLint flat config
├── playwright.config.js            # End-to-end journeys
├── tailwind.config.js
├── postcss.config.js
├── package.json
├── package-lock.json
├── renovate.json                   # Dependency update policy
├── SECURITY-PIPELINE.md            # Pins, required checks, accepted risks
├── .nvmrc                          # Exact Node version (24.20.0); CI reads it
├── .npmrc                          # min-release-age=14 — npm's 14-day cooldown
├── .env.development                # Local: backend :3001, Operaton :8081
├── .env.production                 # Loaded by every `vite build`
├── .env.acceptance                 # Loaded by nothing unless --mode acceptance
├── .env.example
├── .husky/
│   ├── pre-commit                  # npx lint-staged
│   └── pre-push                    # deps:check, lint, check-format
│
├── public/                         # Copied verbatim into dist/
│   ├── favicon.svg, favicon.ico, favicon-96x96.png, apple-touch-icon.png
│   ├── manifest.json, web-app-manifest-192x192.png, web-app-manifest-512x512.png
│   ├── robots.txt
│   ├── CognitatieAnnotationExport.xml
│   └── examples/
│       └── organizations/svb/      # RONL_BerekenLeeftijden_CPRMV.dmn
│
├── src/
│   ├── App.jsx                     # Main orchestrator: layout, navigation, import
│   ├── App.css
│   ├── index.jsx                   # React entry point
│   ├── index.css                   # Global styles, Tailwind imports
│   ├── parseTTL.enhanced.js        # TTL parser with DMN preservation
│   ├── setupTests.js               # Vitest setup
│   ├── logo.svg
│   │
│   ├── components/
│   │   ├── PreviewPanel.jsx        # Live TTL preview side panel
│   │   ├── PublishDialog.jsx       # TriplyDB publish dialog + pre-publish SHACL panel
│   │   └── tabs/
│   │       ├── index.js            # Barrel export — the four lazy tabs deliberately excluded
│   │       ├── ServiceTab.jsx
│   │       ├── CostSection.jsx     # Embedded in ServiceTab
│   │       ├── OutputSection.jsx   # Embedded in ServiceTab
│   │       ├── OrganizationTab.jsx
│   │       ├── LegalTab.jsx
│   │       ├── RulesTab.jsx        # RPP: Rules
│   │       ├── ParametersTab.jsx   # RPP: Parameters
│   │       ├── CPRMVTab.jsx        # RPP: Policy (lazy-loaded)
│   │       ├── DMNTab.jsx          # DMN upload, deploy, test (lazy-loaded)
│   │       ├── ConceptsTab.jsx     # NL-SBB concept definitions
│   │       ├── VendorTab.jsx       # Vendor integration, hosts the iKnow UI (lazy-loaded)
│   │       ├── IKnowMappingTab.jsx # iKnow mapping config (rendered inside VendorTab)
│   │       └── ChangelogTab.jsx    # Version history and build provenance (lazy-loaded)
│   │
│   ├── hooks/
│   │   ├── useEditorState.js       # Centralised state management
│   │   ├── useArrayHandlers.js     # DRY CRUD for array-based fields
│   │   └── useDsoImport.js         # DSO → DMN deep-link import
│   │
│   ├── utils/
│   │   ├── index.js                # Barrel export
│   │   ├── constants.js            # Shared constants, TTL_NAMESPACES, dropdown options
│   │   ├── ttlGenerator.js         # TTL generation class
│   │   ├── ttlHelpers.js           # TTL string/IRI helpers (escapeTTLString, sanitizeIri, …)
│   │   ├── importHandler.js        # Import logic
│   │   ├── cprmvImport.js          # CPRMV 0.4.1 Rules API → flat model
│   │   ├── shaclHelper.js          # Pre-publish SHACL validation
│   │   ├── dmnHelpers.js           # DMN-specific utilities
│   │   ├── validators.js           # Form validation
│   │   ├── triplydbHelper.js       # TriplyDB API integration, buildGraphIRI
│   │   ├── ronlHelper.js           # RONL vocabulary SPARQL queries
│   │   ├── iknowParser.js          # iKnow XML parser
│   │   ├── problem.js              # Reads the backend's RFC 9457 error detail
│   │   └── buildInfo.js            # Build SHA and run number, injected at build time
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
├── e2e/                            # Playwright journeys and their global setup
├── e2e-fixtures/                   # Journey fixtures, with a provenance manifest
├── examples/                       # Reference TTL/DMN exports; round-trip test fixtures
│   └── organizations/              # Per-organisation examples and test cases
│
├── scripts/
│   ├── check-deps.sh               # npm run deps:check — install vs lockfile; warns on npm < 11.10
│   ├── write-deps-marker.mjs       # postinstall — snapshots the lockfile deps:check compares with
│   ├── check-supply-chain.mjs      # npm run check-supply-chain — pin truth and register agreement
│   ├── audit-tree.mjs              # Daily dependency audit, grouped by advisory
│   ├── write-sbom.mjs              # npm run sbom — CycloneDX SBOM into docs/sbom/
│   ├── check-mirror.sh             # npm run check-mirror — GitLab mirror vs GitHub (never pushes)
│   └── check-previews.sh           # npm run check-previews — orphaned preview environments (never deletes)
│
├── docs/
│   └── sbom/                       # <name>-<version>.cdx.json, one per release
│
└── .github/
    ├── zizmor.yml                  # zizmor configuration
    └── workflows/
        ├── azure-static-web-apps-orange-beach-0574c2a03.yml  # Deploy ACC
        ├── azure-static-web-apps-white-sky-02b674303.yml     # Deploy PROD
        ├── close-preview-environments.yml
        ├── dependency-audit.yml
        ├── sbom.yml
        ├── semgrep.yml
        └── zizmor.yml                                        # Supply-chain audit
```

What each workflow does is on [Deployment](deployment.md#cicd-pipeline).

---

## Key modules

### `src/hooks/useEditorState.js`

Centralises all editor state into a single custom hook, providing:

- State slices for every tab (service, organization, legalResource, ronlAnalysis, ronlMethod, temporalRules, parameters, cprmvRules, concepts, cost, output, dmnData, vendorService, iknowMappingConfig, triplyDBConfig)
- Shared RONL vocabulary concepts (analysis/method/vendor), fetched once on mount and shared across the Legal and Vendor tabs
- A `clearAllData()` action that resets the entire editor

This replaces dozens of individual `useState` calls that were previously spread across the main component.

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

Class-based TTL generation. Each tab section has a corresponding generate method. Called by `App.jsx` on export and by `PreviewPanel` on every state change.

### `src/parseTTL.enhanced.js`

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
