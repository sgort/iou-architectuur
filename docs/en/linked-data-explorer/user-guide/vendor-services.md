# Vendor Services

Some DMN decision models published by government agencies have commercial implementations offered by software vendors. The Linked Data Explorer shows these alongside the reference implementation.

---

## Finding vendor implementations

Look for a blue badge with a number on a DMN card in the Available DMNs panel. The number indicates how many vendor implementations are registered for that decision model. DMN cards without a blue badge have only the open-source reference implementation.

---

## Viewing vendor details

Click the blue vendor badge on any DMN card. A modal opens listing all vendor implementations for that decision model.

Each vendor entry shows:

- **Provider** — organisation name and logo
- **Platform** — the technology platform (e.g., Blueriq)
- **License** — Commercial, Open Source, or Free
- **Access type** — IAM Required, Public Access, or API Key Required
- **Contact** — contact person, email (click to compose), phone (click to dial)
- **Service URL** — click to open the vendor's implementation in a new tab
- **Homepage** — vendor website link
- **Description** — free-text summary of the vendor implementation

---

## Understanding access types

| Badge | What it means |
|---|---|
| IAM Required | Access requires Dutch government IAM authentication (DigiD/eIDAS) |
| Public Access | The service is publicly accessible without authentication |
| API Key Required | Registration for an API key is required before access |

---

## Understanding licence types

| Badge | What it means |
|---|---|
| Commercial | Paid licence; typically includes SLA and support |
| Open Source | Source code available; free to use |
| Free | Free to use, possibly with usage limits |

---

## Publishing vendor metadata (for vendors)

Vendor implementations are registered by publishing a `ronl:VendorService` resource to TriplyDB via the CPSV Editor's Vendor tab. For the full workflow, see [CPSV Editor — Vendor Integration](../../cpsv-editor/user-guide/vendor-integration.md).
