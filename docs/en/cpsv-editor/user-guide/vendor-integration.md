# Vendor Integration

---

## Overview

The Vendor tab is used when a commercial vendor has built an implementation of your service's reference decision model. It lets you record that vendor's details, link their implementation to your reference service, and track certification status — all as queryable Linked Data.

---

## Selecting a vendor

1. Navigate to the **Vendor** tab.
2. Open the vendor dropdown. Vendors are loaded from the RONL vocabulary in TriplyDB — this may take a moment.
3. Select the vendor. The form below the dropdown updates to show the fields for that vendor's integration.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Vendor tab showing the vendor dropdown open with several vendor options listed, and the Blueriq form visible below with contact and technical information fields](../../assets/screenshots/cpsv-editor-vendor-dropdown.png)
  <figcaption>Vendor tab showing the vendor dropdown open with several vendor options listed, and the iKnow form visible below</figcaption>
</figure>

---

## iKnow integration

iKnow is the only vendor with a fully implemented import workflow. It operates in two modes, switched via the **Configure / Import** toggle.

**Configure mode** — map iKnow XML fields to CPSV-AP properties:

1. Upload an example iKnow XML export (CognitatieAnnotationExport.xml or SemanticsExport.xml), or click **Load Example**.
2. For each section (Service, Legal, Rules, Parameters, CPRMV), map the XML fields you want to import to the corresponding CPSV-AP property.
3. Click **Save Configuration** and give it a name.

**Import mode** — import actual data:

1. Upload your real iKnow XML data file.
2. Select a saved mapping configuration.
3. Review the preview of the mapped data.
4. Click **Import** to populate the editor tabs.

---

## Vendor metadata form

For other vendors (currently Blueriq as the reference implementation), the form captures:

- **Basic information** — vendor name and service title
- **Contact details** — contact person, email, phone, website, logo
- **Technical details** — service endpoint URL, license, access type
- **Service notes** — free-text description of the vendor implementation
- **Certification** — see below

The logo field works the same way as the Organisation tab: upload a JPG or PNG, and an asset path is generated for inclusion in the Turtle output.

---

## Certification workflow

To record that a vendor implementation has been assessed against the reference model:

1. In the Certification section, change **Certification Status** from *Not certified*.
2. Click **Start Certification Assessment** to open the certification modal.
3. Select or enter the certifying organisation URI. This defaults to the competent authority from the Organisation tab.
4. Enter the certification date and an optional certification note.
5. Confirm to save.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Certification workflow modal showing the certifying organisation field pre-filled from the Organisation tab, the certification date picker, and the optional certification note](../../assets/screenshots/cpsv-editor-certification-modal.png)
  <figcaption>Certification workflow modal</figcaption>
</figure>

The certification details are stored as `ronl:certificationStatus`, `ronl:certifiedBy`, `ronl:certifiedAt`, and `ronl:certificationNote` in the exported Turtle.

---

## Adding a new vendor

The architecture is extensible. If your organisation uses a vendor not in the dropdown, it can be added to the RONL vocabulary in TriplyDB (making it appear in the dropdown automatically) and a form component can be created in the codebase. See [Vendor Tab Implementation](../developer/vendor-tab-implementation.md) for technical details.
