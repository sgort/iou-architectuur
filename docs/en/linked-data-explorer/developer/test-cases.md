# Test Cases

This page covers end-to-end test procedures for the validation system, semantic chain detection, DRD compatibility checks, and template management. Use this as a QA checklist before pushing to ACC.

---

## Prerequisites

- Backend running locally: `npm run dev` in `packages/backend`
- Frontend running locally: `npm run dev` in `packages/frontend`
- Active TriplyDB endpoint: `https://api.open-regels.triply.cc/datasets/stevengort/DMN-discovery/services/DMN-discovery/sparql`
- `ZorgtoeslagVoorwaardenCheck.ttl` uploaded to the test TriplyDB dataset (required for semantic chain tests)

---

## Scenario 1 — Exact match chain (DRD-compatible)

**Chain:** `SVB_LeeftijdsInformatie → SZW_BijstandsnormInformatie`

**Steps:**

1. Open Chain Builder
2. Drag `SVB_LeeftijdsInformatie` into composer
3. Drag `SZW_BijstandsnormInformatie` below it

**Expected results:**

- Console: `[SemanticLinks] ✓ Loaded 26 links (16 semantic)`
- Console: `[Validation] ✓ DRD | 0 missing | 0 semantic`
- Validation panel: green checkmark, "Chain is valid and ready to execute"
- Buttons: Execute, Save, Export all active
- Save modal: purple "🎯 DRD Template" badge, "Save as DRD" button

---

## Scenario 2 — Semantic chain (sequential only)

**Chain:** `ZorgtoeslagVoorwaardenCheck → berekenrechtenhoogtezorg`

**Steps:**

1. Clear composer
2. Drag `ZorgtoeslagVoorwaardenCheck` into composer
3. Drag `berekenrechtenhoogtezorg` below it

**Expected results:**

- Console: `[Validation] ⚠️ Sequential | 0 missing | 6 semantic`
- Six semantic match log entries for: `isIngezetene`, `heeftJuisteLeeftijd`, `betalingsregelingOK`, `vrijVanDetentie`, `heeftGeldigeVerzekering`, `inkomenBinnenGrenzen`
- Validation panel: amber warning, "Sequential execution required (semantic links)"
- Save modal: sequential template badge, no "Save as DRD" option

---

## Scenario 3 — DRD save and execute

Continuation from Scenario 1 with a DRD-compatible chain:

1. Click **Save**
2. Enter name: "Test DRD" → click **Save as DRD**
3. Wait for deployment success message with deployment ID (UUID format)

**Verify localStorage:**

```javascript
const templates = JSON.parse(
  localStorage.getItem('linkeddata-explorer-user-templates')
);
const endpoint = 'https://api.open-regels.triply.cc/...';
const testDrd = templates[endpoint].find(t => t.name === 'Test DRD');
console.log('drdDeploymentId:', testDrd.drdDeploymentId); // UUID
console.log('drdEntryPointId:', testDrd.drdEntryPointId); // dmn1_SZW_...
console.log('type:', testDrd.type);                       // "drd"
```

4. Load the template from My Templates
5. Fill `geboortedatum: 1960-01-01`
6. Click **Execute** → verify single API call in backend logs, results appear

---

## Scenario 4 — Template system

1. Build the SVB → SZW chain and save as DRD ("Chain A")
2. Build the Zorg → Belasting semantic chain and save as sequential ("Chain B")
3. Check My Templates: "Chain A" shows 🔗 DRD badge; "Chain B" shows no DRD badge
4. Switch to a different endpoint: verify neither template appears (endpoint-scoped)
5. Switch back: both templates reappear
6. Delete "Chain A" from My Templates: verify it disappears from the list

---

## Scenario 5 — BPMN Modeler + DRD linking

1. Navigate to BPMN Modeler
2. Open the Tree Felling Permit example
3. Click the "Assess Felling Permit" BusinessRuleTask
4. In the properties panel, click **Link to DMN/DRD**
5. Verify two option groups appear: "🔗 DRDs" and "📋 Single DMNs"
6. If a DRD was saved in Scenario 3, verify it appears in the DRDs group
7. Select it: verify `camunda:decisionRef` populates with the `dmn1_` prefixed identifier
8. Verify the purple DRD info card appears with the chain composition

---

## Scenario 6 — Governance badges

1. Open Chain Builder with an endpoint that has validation metadata
2. Locate a DMN with `ronl:validationStatus "validated"` in TriplyDB
3. Verify a green "✓ Gevalideerd" badge appears on the card
4. Hover over the badge: verify tooltip shows organisation name and date
5. Drag the card into composer: verify badge persists on the composer card

---

## Scenario 7 — Vendor services

1. Open Chain Builder with an endpoint that has vendor metadata
2. Locate a DMN with an associated `ronl:VendorService` in TriplyDB
3. Verify a blue vendor count badge appears on the card
4. Click the badge: verify modal opens with provider details
5. Verify all links work (email, phone, service URL, homepage)
6. Close modal via close button, backdrop click, and ESC key

---

## Common issues

**No semantic links loaded:**
- Check TriplyDB for `dct:subject` integrity — must point to variable URI, not DMN URI
- Check `skos:exactMatch` URIs — must be identical between the two concepts
- Check `dct:type` values — case-sensitive, must match exactly

**DRD deployment fails:**
- Verify Operaton is accessible: `curl https://operaton.open-regels.nl/engine-rest/version`
- Check backend logs for specific Operaton error message
- Try removing the `<dmndi:DMNDI>` block from the generated XML temporarily

**Validation shows amber for an exact-match chain:**
- Open browser console, look for `[Validation]` log line
- If `semantic > 0` despite visual identifier match, check for variable type mismatch in TriplyDB (`"Boolean"` vs `"boolean"`)
