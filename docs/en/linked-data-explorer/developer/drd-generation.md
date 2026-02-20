# DRD Generation

This page covers the implementation of the DRD save flow — from the frontend validation check through XML assembly to Operaton deployment.

---

## Preconditions

DRD generation is only triggered when `isDrdCompatible = true` in the validation result, meaning all variable connections in the chain are exact identifier matches. The frontend gates the "Save as DRD" path on this flag. Attempting to call the DRD assembly endpoint with a semantic chain will result in an error from the backend because the `<informationRequirement>` wiring cannot be determined from identifier matches alone.

---

## XML assembly

`POST /v1/chains/export` receives the ordered chain of DMN identifiers and the active endpoint. The backend:

1. Fetches the full DMN metadata for each model from TriplyDB (including the original DMN XML if available, otherwise generates a skeleton).
2. Identifies the **entry point** — the last DMN in the chain, whose decision is the one that aggregates all upstream inputs. Operaton evaluates the DRD by calling this decision.
3. For each adjacent pair in the chain, adds an `<informationRequirement>` element to the downstream DMN's decision:

```xml
<decision id="SZW_BijstandsnormInformatie" name="Bijstandsnorm Informatie">
  <informationRequirement id="req_SVB_to_SZW">
    <requiredDecision href="#SVB_LeeftijdsInformatie" />
  </informationRequirement>
  <!-- decision table content -->
</decision>
```

4. Wraps all decisions in a single `<definitions>` element with a generated DRD identifier prefixed with `dmn1_` (e.g., `dmn1_SZW_BijstandsnormInformatie`).

The prefix convention (`dmn1_`) is used to distinguish DRD entry-point identifiers from individual DMN identifiers in the `DmnTemplateSelector` dropdown in the BPMN Modeler.

---

## Operaton deployment

After XML assembly, the backend deploys the DRD to Operaton:

```
POST {OPERATON_BASE_URL}/deployment/create
Content-Type: multipart/form-data

deployment-name: {drdName}
enable-duplicate-filtering: true
{drdXml file}
```

Operaton returns a deployment ID (UUID format). This ID is stored in the template record alongside the DRD entry-point identifier.

---

## localStorage template schema

After successful deployment, the frontend stores the template in localStorage:

```typescript
{
  id: crypto.randomUUID(),
  name: "Social Benefits DRD",
  description: "SVB + SZW eligibility chain",
  endpoint: "https://api.open-regels.triply.cc/...",
  chain: ["SVB_LeeftijdsInformatie", "SZW_BijstandsnormInformatie"],
  type: "drd",
  isDrd: true,
  drdDeploymentId: "43c759d6-082b-11f1-a5e9-f68ed60940f5",
  drdEntryPointId: "dmn1_SZW_BijstandsnormInformatie",
  drdOriginalChain: ["SVB_LeeftijdsInformatie", "SZW_BijstandsnormInformatie"]
}
```

`drdEntryPointId` is what gets passed to Operaton at execution time. `drdOriginalChain` is used by the BPMN Modeler's info card to display the composition of the DRD.

---

## DRD execution path

When a DRD template is loaded and executed:

```
POST /v1/chains/execute
{
  "chain": ["dmn1_SZW_BijstandsnormInformatie"],  ← single entry point
  "inputs": { "geboortedatum": "1960-01-01" },
  "endpoint": "...",
  "isDrd": true
}
```

The orchestration service detects `isDrd: true` and skips the sequential loop, issuing a single Operaton call with the DRD entry-point identifier. Operaton resolves all `<informationRequirement>` dependencies internally.

---

## BPMN Modeler integration

`DmnTemplateSelector.tsx` loads DRD templates alongside regular DMNs when a `BusinessRuleTask` is selected:

```typescript
const loadOptions = async () => {
  // Fetch regular DMNs from API
  const response = await fetch(`${API_BASE_URL}/v1/dmns?endpoint=${endpoint}`);
  const dmnArray = data.data.dmns;

  // Load local DRD templates
  const userTemplates = getUserTemplates(endpoint);
  const drdOptions = userTemplates
    .filter(t => t.isDrd && t.drdEntryPointId)
    .map(t => ({
      identifier: t.drdEntryPointId,
      title: `${t.name} (DRD)`,
      isDrd: true,
      originalChain: t.drdOriginalChain,
    }));

  setOptions({ drds: drdOptions, dmns: dmnArray });
};
```

Selecting a DRD option sets `camunda:decisionRef` to the `drdEntryPointId`. Operaton uses this to look up and evaluate the deployed DRD.
