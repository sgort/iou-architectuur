# DMN Implementation

---

## Component structure

```
src/
├── components/tabs/
│   └── DMNTab.jsx                    # Main UI (850+ lines)
│       • File upload + card display
│       • API configuration
│       • Deployment controls
│       • Single evaluate (Postman-style)
│       • Intermediate decision tests
│       • Test cases upload + runner
│       • Import preservation notice
│
├── utils/
│   ├── dmnHelpers.js                 # DMN TTL generation utilities (370 lines)
│   └── parseTTL.enhanced.js          # DMN block capture on import (523 lines)
│
└── config/
    └── vocabularies_config.js        # DMN entity type detection
```

---

## DMN state shape

```javascript
dmnData: {
  // File
  fileName: string,
  content: string,              // Raw DMN XML

  // Deployment
  decisionKey: string,          // Primary key extracted from DMN
  deployed: boolean,
  deploymentId: string | null,
  deployedAt: string | null,

  // API
  apiEndpoint: string,

  // Testing
  lastTestResult: object | null,
  lastTestTimestamp: string | null,
  testBody: string | null,

  // Import preservation (v1.5.1+)
  importedDmnBlocks: string | null,  // Raw Turtle lines preserved verbatim
  isImported: boolean,
}
```

---

## Import preservation

### Detection

`vocabularies_config.js` detects DMN entities before regular entities to avoid misclassification:

```javascript
export const detectEntityType = (line) => {
  // DMN detection FIRST
  if (line.includes('a cprmv:DecisionModel')) return 'dmnModel';
  if (line.includes('a cpsv:Input'))          return 'dmnInput';
  if (line.includes('a cprmv:DecisionRule'))  return 'dmnRule';

  // Regular entity detection below...
};
```

### Capture

`parseTTL.enhanced.js` captures DMN lines verbatim when detected:

```javascript
let inDmnSection = false;
let dmnLines = [];

if (['dmnModel', 'dmnInput', 'dmnRule'].includes(detectedType)) {
  if (!inDmnSection) {
    inDmnSection = true;
    parsed.hasDmnData = true;
  }
  dmnLines.push(rawLine);  // exact line, no transformation
  continue;
}

if (parsed.hasDmnData && dmnLines.length > 0) {
  parsed.importedDmnBlocks = dmnLines.join('\n');
}
```

### Export

`ttlGenerator.js` appends preserved blocks unchanged at the end of the generated output — after all form-based sections.

---

## Primary decision key extraction

The `extractPrimaryDecisionKey()` helper skips constant parameters automatically:

```javascript
// Filters decisions with p_* prefix (constants)
// Returns the last non-constant decision (typically the output decision)
// Falls back to first decision if all are constants
```

Console log on extraction:
```
[DMN] Extracted primary decision key: "zorgtoeslag_resultaat" (skipped 8 p_* constant(s))
```

---

## Operaton REST API

**Deploy endpoint:**

```
POST /engine-rest/deployment/create
Content-Type: multipart/form-data
Body: deployment-name={serviceId}, upload={dmnFile}
```

**Evaluate endpoint:**

```
POST /engine-rest/decision-definition/key/{decisionKey}/evaluate
Content-Type: application/json
Body: { "variables": { ... } }
```

---

## URI generation

DMN URIs are derived from the service identifier. Given `service.identifier = "aow-leeftijd"`:

```turtle
<https://regels.overheid.nl/services/aow-leeftijd/dmn>
    a cprmv:DecisionModel .

<https://regels.overheid.nl/services/aow-leeftijd/dmn/input/1>
    a cpsv:Input .

<https://regels.overheid.nl/services/aow-leeftijd/rules/DecisionRule_2020>
    a cpsv:Rule, cprmv:DecisionRule .
```

Spaces in the service identifier are replaced with hyphens. Full URIs in the organisation field are used as-is; short IDs are expanded.

---

## Shell script parity

The intermediate tests and test cases features in the UI mirror the shell scripts in `examples/organizations/*/`:

| Shell script | UI equivalent |
|---|---|
| `test-dmn-zorgtoeslag.sh` | DMN Tab → Intermediate Decision Tests |
| `test-cases-zorgtoeslag.sh` | DMN Tab → Test Cases |

The shell scripts can still be used for CI/CD automation independently of the UI.
