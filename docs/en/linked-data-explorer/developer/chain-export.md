# Chain Export

The Chain Export feature lets you package a built chain as a portable deployment artifact. The current implementation exports a ZIP archive containing everything needed to deploy the chain as a running process in Operaton without any dependency on the Linked Data Explorer.

---

## What gets exported

Clicking **Export** on a built chain produces a `chain-export.zip` file with the following contents:

```
chain-export.zip
├── chain.bpmn          BPMN 2.0 process with a BusinessRuleTask per DMN
├── SVB_*.dmn           DMN file fetched from Operaton
├── SZW_*.dmn           DMN file fetched from Operaton
├── RONL_*.dmn          DMN file fetched from Operaton
└── README.md           Step-by-step deployment instructions
```

The BPMN file has one `BusinessRuleTask` per DMN in the chain, wired sequentially from a Start Event to an End Event. Each task carries an `operaton:decisionRef` pointing to the corresponding DMN identifier. The included `README.md` explains the two-step deployment process.

---

## Exporting a chain

1. Build a chain in the Chain Builder and ensure it shows a valid status (green or amber).
2. Click **Export** in the action buttons below the Chain Composer.
3. The browser downloads `chain-export.zip` automatically.

The export works for both DRD-compatible and sequential chains. For DRD-compatible chains, consider also [saving as a DRD](drd-generation.md) if you want Operaton to handle execution in a single call.

---

## Deploying the exported package

The included `README.md` walks through both steps, but the short version is:

**Step 1 — deploy the DMN files:**

```bash
curl -X POST https://operaton.open-regels.nl/engine-rest/deployment/create \
  -F "deployment-name=chain-dmns-$(date +%Y%m%d-%H%M%S)" \
  -F "enable-duplicate-filtering=true" \
  -F "data=@SVB_LeeftijdsInformatie.dmn" \
  -F "data=@SZW_BijstandsnormInformatie.dmn" \
  -F "data=@RONL_HeusdenpasEindresultaat.dmn"
```

**Step 2 — deploy the BPMN process:**

```bash
curl -X POST https://operaton.open-regels.nl/engine-rest/deployment/create \
  -F "deployment-name=chain-bpmn-$(date +%Y%m%d-%H%M%S)" \
  -F "enable-duplicate-filtering=true" \
  -F "data=@chain.bpmn"
```

The two-step order is required: the BPMN references each DMN via `operaton:decisionRef`, and Operaton validates those references during deployment. Deploying the BPMN before the DMNs causes a deployment failure.

---

## Verifying the deployment

After both steps complete, confirm the process is live:

```bash
# Verify DMNs are registered
curl https://operaton.open-regels.nl/engine-rest/decision-definition/key/SVB_LeeftijdsInformatie | jq

# Verify the BPMN process is registered
curl https://operaton.open-regels.nl/engine-rest/process-definition/key/chain-name | jq
```

A successful deployment shows incrementing version numbers on redeployment, and the process appears in **Operaton Cockpit → Processes** with `historyTimeToLive: 180` and `startableInTasklist: true`.

---

## Planned additions

The following export and deployment capabilities are planned for future releases:

**BPMN export only** — download just the `chain.bpmn` file without DMN files, for teams that manage DMN deployment separately or use a different DMN registry.

**Deploy directly from the UI** — a one-click Deploy button that calls the Operaton deployment API directly from the Chain Builder, removing the need to unzip and run curl commands manually. This will require Operaton endpoint configuration in the LDE settings.

**DRD package export** — a ZIP variant for DRD-compatible chains that includes the assembled DRD XML (the unified file with `<informationRequirement>` wiring) rather than individual DMN files.