# Vendor Services

Alongside the government reference implementations of DMN decision models, commercial vendors may offer certified implementations of the same decisions with additional enterprise features, SLAs, and support. The Vendor Services feature surfaces these implementations directly in the DMN list.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Vendor Services modal showing Blueriq implementation details for a government DMN](../../assets/screenshots/linked-data-explorer-vendor-modal.png)
  <figcaption>Vendor Services modal showing Blueriq implementation details for a government DMN</figcaption>
</figure>

---

## Vendor badges

A blue badge showing a count appears on any DMN card that has at least one associated `ronl:VendorService` resource in TriplyDB. Clicking the badge opens a modal with full details of all vendor implementations for that decision model.

---

## Vendor detail modal

The modal shows for each vendor implementation:

- Provider name, logo, and homepage link
- Platform (e.g., Blueriq)
- License type — Commercial, Open Source, or Free
- Access type — IAM Required, Public Access, or API Key Required
- Contact details (name, email, phone) — all clickable
- Service URL — link to the vendor's implementation endpoint
- Free-text description

---

## Publishing vendor metadata

Vendor implementations are published to TriplyDB via the CPSV Editor's Vendor tab. See the [CPSV Editor — Vendor Integration](../../../cpsv-editor/user-guide/vendor-integration.md) guide for the full publishing workflow.

---

## RONL Ontology

The vendor vocabulary is defined in the RONL Ontology v1.0 using `ronl:VendorService`, `ronl:basedOn`, and `ronl:implementedBy`, combined with Schema.org properties for provider contact information. For the full property specification, see [CPSV Editor — RONL Ontology](../../../cpsv-editor/reference/ronl-ontology.md).
