---
component: CPSV Editor
---

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

---

## Step 2: Review the syntactic validation result

Immediately after upload, the editor runs the file through the five-layer syntactic validator and displays the result in the file card.

**If the file is valid**, a green *Syntax valid* badge appears. Any warnings or informational messages are shown in a collapsed panel — review them before deploying.

**If the file has errors**, the panel expands automatically and lists the issues grouped by layer. Address the errors in your DMN authoring tool before proceeding with deployment.

| Badge | Meaning |
|---|---|
| 🟢 Syntax valid | No errors. Warnings and info messages may still be present. |
| 🔴 Validation failed | One or more errors detected. Deployment will likely fail or produce incorrect results. |

!!! tip
    Warnings in the **Interaction Rules** layer often indicate orphaned `<inputData>` elements — inputs that exist in the DRD but are not connected to any decision via `<informationRequirement>`. These are harmless for execution but result in dead data in the model.

For a full explanation of every issue code and its rationale, see the [DMN Validation Reference](../../../linked-data-explorer/reference/dmn-validation-reference.md).

---

## Step 3: Configure the API endpoint

The **Base URL** identifies the Operaton engine to deploy to and evaluate against. It defaults to `https://operaton.open-regels.nl` — change it if you are using a different instance.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: API Configuration panel showing the Base URL and the Evaluation URL preview pointing at the Linked Data Explorer backend](../../assets/screenshots/cpsv-editor-dmn-api-configuration.png)
  <figcaption>API Configuration panel — the Evaluation URL preview shows the backend endpoint the editor actually calls</figcaption>
</figure>

The **Evaluation URL** preview below it shows the URL the editor will actually call. Since v2026.08.0 that is a Linked Data Explorer backend endpoint, not an Operaton one: the browser posts to the backend, and the backend calls Operaton server-to-server. Calling the engine directly from the browser is blocked by CORS, so this indirection is what makes deploy and evaluate work in local development.

!!! tip "Pointing local development at a local engine"
    Set `REACT_APP_OPERATON_URL` in your `.env` to target a local Operaton container. Without it the Base URL falls back to the shared production instance — so a local dev session would otherwise deploy to, and evaluate against, shared infrastructure.

---

## Step 4: Deploy to Operaton

Click **Deploy to Operaton**. The editor posts the DMN file to the backend's `POST /v1/dmns/deploy`, which forwards it to the engine.

On success, the button changes to **Deployed — ID: {deployment-id}** and the deployment ID and timestamp are stored. These are included in the Turtle output.

---

## Step 5: Test the decision

Review the auto-generated request body in the test panel. Edit variable values to match your test scenario.

Click **Evaluate Decision**. The editor calls `POST /v1/dmns/evaluate/{decisionKey}` on the backend, which evaluates the decision on Operaton and returns the result. The response is displayed inline.

If the file contains more than one testable decision, use the **Decision Key** dropdown on the DMN File card to choose which decision to evaluate — the editor defaults to the root decision (one no other decision requires), but you can point it at any of them, and the evaluation URL updates to match (v1.10.3).

For multi-table DMNs, expand the **Intermediate Decision Tests** section and click **Run Intermediate Tests** to evaluate each sub-decision individually — useful for isolating which part of a complex DRD is producing an unexpected result. For batch, *verified* scenario testing, see [DMN Testing](dmn-testing.md).

---

## Step 6: Export TTL with DMN metadata

Click **Download TTL**. The exported file includes:

- The `cprmv:DecisionModel` entity with deployment ID (`cprmv:deploymentId`) and API endpoint (`cprmv:implementedBy`)
- All input variables as `cpsv:Input` entities and output variables as `cpsv:Output` entities
- All extracted decision rules as `cpsv:Rule, cprmv:DecisionRule` entities (with `dct:title`/`dct:description`), each linked to the relevant legal article via `cprmv:isBasedOn` and, when a legal resource is set, to the `eli:LegalResource` via `cpsv:implements`

The DMN section is appended after the core service metadata.

---

## Tips

- Fill in the Service identifier before uploading the DMN — it is used to construct the DMN model URI.
- Use descriptive decision keys in your DMN XML (e.g. `zorgtoeslag_resultaat` rather than `Decision_1`).
- Do not use spaces in decision keys — use underscores or camelCase.
- Deploy and test before exporting. Undeployed DMN metadata in the Turtle output has no deployment ID, which limits its usefulness.
- Resolve all validation **errors** before deploying. **Warnings** are advisory and will not prevent a successful deployment.

---

## Authoring pitfalls

Bringing a real, tool-exported DMN (Amsterdam's 25-decision HvA model) to a deployable and evaluable state surfaced a set of defects that a syntactically valid file can still carry. They are worth checking in any DMN produced by an authoring tool rather than hand-written.

**Blocking deployment:**

| Symptom | Cause | Fix |
|---|---|---|
| Deployment rejected | No `camunda:historyTimeToLive` on the decisions | Set it on every `<decision>` |
| Deployment rejected, XML parse error | Unescaped `&` in `knowledgeSource` URLs | Escape as `&amp;` |

**Blocking evaluation** — the file deploys, but decisions cannot be evaluated:

| Symptom | Cause | Fix |
|---|---|---|
| `FEEL/SCALA-01008` | Multi-word bare names in input expressions — the FEEL engine consumes only the first word | Flatten names to a single token |
| Blank, unlogged exception | `<dmn:output>` declares `label` but no `name`; Operaton needs `name` to serialise the result | Add `name` to every `<dmn:output>` |
| `DMN-01005 Invalid value … for clause with type 'date'` | A date input sent as a string | Send the full ISO timestamp with `type: "Date"` — the editor now does this automatically |

**Silently wrong results** — evaluation succeeds but the logic is not what was intended:

- `not -` and `not(null) -` are malformed FEEL: `not` requires a parenthesised argument. Rewrite as `false` and `not(null)` respectively, after confirming the intent against the business rule.
- Bare `and`-joined comparisons are not valid unary tests. Rewrite in interval notation, e.g. `[18..67)`.
- `not "met partner"` needs parentheses: `not("met partner")`.
- A decision with a wildcard default rule must not use `hitPolicy="UNIQUE"` (the implicit default) — the default rule always matches alongside a specific one. Use `FIRST`.
