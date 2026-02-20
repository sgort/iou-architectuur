# DMN Workflow

This guide walks through uploading, deploying, testing, and exporting a DMN decision model as part of a service definition.

---

## Prerequisites

- A `.dmn` file (DMN 1.3 XML format)
- The service metadata tabs (Service, Organisation, Legal) filled in — the service identifier is used to construct DMN URIs
- Access to the Operaton rule engine (default: `https://operaton.open-regels.nl`)

---

## Step 1: Upload the DMN file

In the **DMN tab**, click **Upload DMN File** and select your `.dmn` file.

On upload, the editor:

- Parses all `<decision>` elements from the XML
- Filters out constant parameters (`p_*` prefix) automatically
- Extracts the primary decision key (the main output decision)
- Auto-generates a test request body from the `<inputData>` elements
- Shows a badge: "N testable decisions detected (p_* constants filtered)"

If you do not have a DMN file yet, click **Load Example** to use the provided AOW example.

![Screenshot: DMN tab after file upload showing the file card with decision count badge, the auto-populated Decision Key field, and the auto-generated request body](../../assets/screenshots/cpsv-editor-dmn-uploaded.png)

---

## Step 2: Configure the API endpoint

The API endpoint defaults to `https://operaton.open-regels.nl/engine-rest`. Change it if you are using a different Operaton instance.

---

## Step 3: Deploy to Operaton

Click **Deploy to Operaton**. The editor sends the DMN file to the engine via `POST /engine-rest/deployment/create`.

On success, the button changes to **Deployed — ID: {deployment-id}** and the deployment ID and timestamp are stored. These are included in the Turtle output.

---

## Step 4: Test the decision

Review the auto-generated request body in the test panel. Edit variable values to match your test scenario.

Click **Evaluate Decision** to call `POST /engine-rest/decision-definition/key/{decisionKey}/evaluate`. The response is displayed inline.

For multi-table DMNs, expand the **Intermediate Decision Tests** section and click **Run Intermediate Tests** to evaluate each sub-decision individually — useful for isolating which part of a complex DRD is producing an unexpected result.

---

## Step 5: Export TTL with DMN metadata

Click **Download TTL**. The exported file includes:

- The `cprmv:DecisionModel` entity with deployment ID and API endpoint
- All input variables as `cpsv:Input` entities
- All extracted decision rules as `cprmv:DecisionRule` entities, each linked to the relevant legal article via `cprmv:extends`

The DMN section is appended after the core service metadata.

---

## Tips

- Fill in the Service identifier before uploading the DMN — it is used to construct the DMN model URI.
- Use descriptive decision keys in your DMN XML (e.g. `zorgtoeslag_resultaat` rather than `Decision_1`).
- Do not use spaces in decision keys — use underscores or camelCase.
- Deploy and test before exporting. Undeployed DMN metadata in the Turtle output has no deployment ID, which limits its usefulness.
