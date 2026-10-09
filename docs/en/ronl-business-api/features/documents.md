---
component: RONL Business API
---

# Documents

A case can carry documents held in an external system rather than inside the platform itself. This page describes how that external document material is reached. A case's own record, by contrast, is the variables its running process instance has accumulated — described in [Processes](processes.md) and [Tasks](tasks.md).

---

## Referencing an external document store

A process can carry, among its own variables, a reference to a workspace in an external document-management system — the same way it carries any other variable accumulated as the process runs. That reference is what ties a case to the documents held for it externally: the platform itself stores the pointer, not the documents.

---

## Documents in a document-management integration

One integration pattern manages documents the way a records-management system does: a workspace is created (or reused if one already exists) to hold a case's documents, a document is uploaded into it with descriptive metadata such as its name and the responsible department, and from there a document can be listed, profiled, retrieved by version, or deleted. Every version of a document is addressable on its own, so a later upload does not replace what came before it — it adds a new version alongside it.

### As whom the document system sees a call

The document-management integration distinguishes two identities:

- **A person** — a caseworker or admin who signed in with their organisation account — works in the document system **as themselves**: the platform opens a session with that person's own identity, so the document system enforces and records that person's rights. No shared password is involved.
- **The service account** serves registered machine clients and background archiving, such as a process step that files a document or the archiving of a signed document.

Every data response says which one acted (`actingAs: "user"` or `"service"`). A person is never silently turned into the service account: when the platform cannot act as them, the request is refused with a reason they can act on, such as signing in again.

Background archiving runs as the service account, which can only record itself as the author. The employee who caused the write is therefore recorded at the end of the document's title, as **"<title> — namens <naam> (<e-mail>)"**.

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
