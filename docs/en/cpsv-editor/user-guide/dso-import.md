# DSO → DMN Import

This guide explains what happens when you arrive in the CPSV Editor from a Linked Data Explorer DSO deep-link, and how to continue from there. For the architecture, see the [DSO → DMN Import feature page](../features/dso-import.md).

---

## Arriving from the Linked Data Explorer

When you choose to turn a DSO *toepasbare regel* into a service definition in the Linked Data Explorer, it opens the CPSV Editor with the decision model already loaded. You do not need to download or upload anything.

On arrival you will see:

- The **DMN tab** active, with the decision model loaded (filename `decision-{dmnId}.dmn`) and its primary decision key detected.
- The **Service tab** prefilled with the activity name, identifier, and a Dutch provenance description.
- The **Organization tab** prefilled with the resolving authority.
- A message banner confirming the import: *"Imported '…' from DSO — review, deploy, and publish."*

The address bar is cleaned automatically, so refreshing the page will **not** re-import.

---

## Completing the service definition

1. **Review the prefilled tabs.** Check the Service identifier and title, and confirm the Organization. Fill in the **Legal** tab with the governing BWB/CVDR resource — this drives the `cpsv:implements` links on the decision rules.
2. **Review the DMN.** The syntactic validation panel runs automatically. Resolve any errors in your DMN authoring tool if needed.
3. **Deploy and test.** Deploy to Operaton and run a single evaluate or test cases — see [DMN Workflow](dmn-workflow.md) and [DMN Testing](dmn-testing.md).
4. **Publish.** Open the publish dialog, review the advisory SHACL result, and publish to TriplyDB — see [Publishing to TriplyDB](publishing-to-triplydb.md).

---

## If the import fails

If the deep-link is missing the decision id, or the backend cannot return the DMN, the banner shows an error such as *"DSO import failed: … You can still upload the DMN manually."* In that case, go to the **DMN tab** and upload the `.dmn` file by hand, then continue as normal.
