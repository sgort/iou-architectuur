# DMN Orchestration

The DMN tab enables the editor to go beyond metadata authoring and become an active tool for deploying and testing decision logic. It integrates directly with the Operaton rule engine, which hosts the DMN models that execute government service decisions.

![Screenshot: DMN tab showing a deployed decision model with deployment ID, the test request body, and intermediate decision test results](../../assets/screenshots/cpsv-editor-dmn-tab.png)

---

## What the DMN tab does

The tab handles the complete lifecycle of a Decision Model and Notation (DMN 1.3) file within a service definition:

**File management.** Upload a `.dmn` file, or load one of the provided examples. The editor parses the DMN XML, extracts all `<decision>` elements, identifies the primary decision key (automatically skipping constant parameters prefixed with `p_*`), and pre-populates the request body with the correct input variable names and types.

**Deployment to Operaton.** Send the DMN file to the configured Operaton engine endpoint via the REST deployment API. Deployment status and ID are tracked and included in the exported Turtle.

**Live decision evaluation.** Test the deployed model with configurable input variables using a Postman-style interface. The request body is auto-generated but fully editable. Responses are displayed inline.

**Metadata documentation.** The exported Turtle includes the full DMN metadata: the decision model URI, deployment ID, API endpoint, all input variables as `cpsv:Input` entities, and extracted decision rules with their legal article references as `cprmv:DecisionRule` entities.

**Import preservation.** When a Turtle file containing DMN data is imported, the DMN blocks are preserved exactly as-is across the import/export cycle. The tab displays a clear notice indicating that the DMN is in imported state, and provides the option to clear and recreate it.

---

## Testing capabilities

Beyond single-evaluation testing, the DMN tab includes two advanced testing modes:

**Intermediate decision tests** evaluate each sub-decision in the Decision Requirements Diagram (DRD) individually. This is invaluable for debugging complex multi-table DMNs — rather than examining the final output, you can see exactly which sub-decision is producing an unexpected result. Constant parameters are automatically filtered out; only testable decisions are shown.

**Test cases** run multiple predefined scenarios from an uploaded JSON file against the primary decision key. Results are displayed progressively — pass/fail counters update in real time as each case executes. Two JSON formats are supported (Toeslagen and DUO format), with automatic normalisation.

A successful test case run also generates NL-SBB concepts for semantic linking via the Linked Data Explorer.

---

## Smart constant filtering

DMNs for government services frequently contain a large number of constant parameter decisions (prefixed `p_`) alongside the actual decision logic. The editor automatically detects and filters these from the decision key extraction and intermediate test list, so you work with only the testable decisions. The file card shows a badge like "12 testable decisions detected (p_* constants filtered)" to make the filtering transparent.
