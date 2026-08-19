---
component: RONL Business API
---

# Dossiers & Documents

A case's own record is the variables its running process instance has accumulated — described in [Processes](processes.md) and [Tasks](tasks.md). Alongside that record, a case can also carry documents held in an external system rather than inside the platform itself. This page describes how that external document material is reached.

---

## Referencing an external document store

A process can carry, among its own variables, a reference to a workspace in an external document-management system — the same way it carries any other variable accumulated as the process runs. That reference is what ties a case to the documents held for it externally: the platform itself stores the pointer, not the documents.

---

## Documents in a document-management integration

One integration pattern manages documents the way a records-management system does: a workspace is created (or reused if one already exists) to hold a case's documents, a document is uploaded into it with descriptive metadata such as its name and the responsible department, and from there a document can be listed, profiled, retrieved by version, or deleted. Every version of a document is addressable on its own, so a later upload does not replace what came before it — it adds a new version alongside it.

---

## Delivering a document to a recipient

A second integration pattern is for delivery rather than storage: a document is sent to an external recipient — registered first with the identifying and contact details a delivery platform needs — and the delivery is tracked from there. A document that requires a follow-up state, such as confirmation that it was paid, can have that state recorded back through the same integration.

---

## Integration characteristics

Both patterns follow the same shape. Each is reached through its own set of endpoints, gated by authentication like any other protected route — see [Authentication & IAM](authentication-iam.md). Each exposes a status check reporting whether the external system is reachable. And each can run in a **stub mode**, returning realistic fake responses instead of calling the external system at all, so the platform's own behaviour can be exercised without depending on the external system being available.

---

## Related

- [Processes](processes.md) — the process instance whose variables can reference an external document workspace
- [Tasks](tasks.md) — the human step that most often produces or reviews a case's documents
- [Authentication & IAM](authentication-iam.md) — the token validation every document endpoint requires
- [Security & Compliance](security-compliance.md) — where secrets for an external integration are held
