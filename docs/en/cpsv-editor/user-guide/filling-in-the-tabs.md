# Filling In the Tabs

This page describes each tab's fields, what they map to in the generated Turtle, and what validation rules apply. For the full UI field ↔ RDF property mapping tables, see the [Field Mapping Reference](../reference/field-mapping.md).

---

## Service tab

The Service tab models `cpsv:PublicService`.

**Unique identifier** (`dct:identifier`) — Mandatory. Used as the base for all URIs in the file. Spaces are converted to hyphens automatically. Choose a stable, human-readable value.

**Official name** (`dct:title`) — Mandatory. The public-facing name of the service, stored with `@nl` language tag.

**Description** (`dct:description`) — Detailed explanation of what the service does.

**Thematic area** (`cv:thematicArea`) — URI for thematic classification. Select from the dropdown or enter a URI directly.

**Government level** (`cv:sector`) — Mandatory. Select from the controlled vocabulary (national, provincial, municipal, etc.).

**Keywords** (`dcat:keyword`) — Comma-separated terms for discoverability.

**Language** (`dct:language`) — Outputs as a LinguisticSystem URI (e.g. `https://publications.europa.eu/resource/authority/language/NLD`).

**Cost section** — Documents fees associated with the service as `cv:Cost`. Enter amount and currency.

**Output section** — Documents what the citizen receives as `cv:Output`. Enter a title and description.

---

## Organisation tab

The Organisation tab models `cv:PublicOrganisation`.

**Organisation identifier** — Mandatory. Enter a short ID (e.g. `SVB`) or a full URI. Short IDs are expanded to `https://regels.overheid.nl/organizations/{id}`.

**Organisation name** (`skos:prefLabel`) — The official name.

**Geographic jurisdiction** (`dct:spatial`) — Mandatory. The geographic area the organisation is responsible for, as a URI. Emitted as `dct:spatial` pointing at a `dct:Location`-typed node (was `cv:spatial` before v1.10.0; both are still read on import).

**Homepage** (`foaf:homepage`) — The organisation's official website URI.

**Logo** — Upload a JPG or PNG. The editor resizes it to 256×256px. The logo URI is generated as `./assets/{OrganisationName}_logo.png` and included in the Turtle as both `foaf:logo` and `schema:image`.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Organisation tab showing the identifier field, name, spatial jurisdiction dropdown, and the logo upload area with a preview of an uploaded logo](../../assets/screenshots/cpsv-editor-organisation-tab.png)
  <figcaption>Organisation tab showing the identifier field, name, spatial jurisdiction dropdown, and the logo upload area with a preview of an uploaded logo</figcaption>
</figure>

---

## Legal tab

The Legal tab models `eli:LegalResource`.

**BWB ID** — The Dutch legal resource identifier (e.g. `BWBR0002221`). Validated against the BWB pattern. The editor constructs a `wetten.overheid.nl` URI automatically.

**Version / consolidation date** — The specific version of the legislation being referenced.

**Title and description** — Human-readable metadata for the legal resource.

---

## Rules tab (RPP: Rules)

Each rule models `cpsv:Rule, cprmv:TemporalRule`.

**Rule identifier** (`dct:identifier`) — Mandatory. Unique identifier for this rule.

**Rule title** (`dct:title`) — Mandatory. Human-readable name.

**Rule URI** — Full URI for the rule, or leave blank to auto-generate from the service identifier.

**Extends** (`cprmv:isBasedOn`) — URI of the legal article or version this rule implements. (Was `ronl:extends` before v1.10.0.)

**Valid from / until** (`cprmv:validFrom`, `cprmv:validUntil`) — Temporal validity window as ISO dates.

**Confidence level** (`cprmv:confidenceLevel`) — The certainty with which this rule implements the policy.

When a legal resource is set in the Legal tab, each rule's `cpsv:implements` automatically points at the `eli:LegalResource` (CPSV-AP 3.2.0 RuleShape), and a `dct:description` is emitted (falling back to the title).

Multiple rules can be added with the **Add Rule** button. Each rule appears as an expandable card.

---

## Parameters tab (RPP: Parameters)

Each parameter models `cprmv:ParameterWaarde`.

**Notation** (`skos:notation`) — Machine-readable identifier for the parameter (e.g. `AOW_LEEFTIJD_STANDAARD`).

**Label** (`skos:prefLabel`) — Human-readable name.

**Value** (`schema:value`) — The numeric or string value.

**Unit** (`schema:unitCode`) — The unit of measurement (e.g. `ANN` for years, `EUR` for euros).

**Valid from / until** — Temporal validity.

---

## CPRMV tab (RPP: Policy)

Each entry models `cprmv:Rule`. All six fields are mandatory.

**Rule ID** (`cprmv:id`) — Identifier of the rule (e.g. `onderdeel a.`).

**Ruleset ID** (`cprmv:rulesetId`) — The legal source (BWB/CVDR) the rule belongs to. Drives the `cprmv:RuleSet` grouping and the rule's `cprmv:implements` link.

**Definition** (`cprmv:definition`) — The full legal text.

**Situation** (`cprmv:situatie`) — The contextual situation to which the rule applies.

**Norm** (`cprmv:norm`) — The normative value mandated by the rule.

**Rule ID path** (`cprmv:ruleIdPath`) — The full legislative path to the source article (used to build a unique rule URI).

CPRMV rules can be entered individually or imported in bulk via the **Import JSON** button, which accepts the CPRMV 0.4.1 Rules API output (an array of `cprmv:RuleSet` objects with nested `hasPart` maps) as well as legacy flat-array exports. **Load Example** loads the bundled conformant 0.4.1 sample.

---

## DMN tab

See the [DMN Workflow](dmn-workflow.md) and [DMN Testing](dmn-testing.md) user guides.

---

## Concepts tab

The Concepts tab holds NL-SBB concept definitions (`skos:Concept`) for the DMN's input and output variables. Concepts are populated automatically once a DMN is loaded and its inputs/outputs are known — by running a single evaluate, by running uploaded test cases (the union of all uploaded cases' request-body variables is used, so no successful evaluate is required), or restored on import. A badge on the tab shows the concept count, or "Needs DMN" when none exist yet.

Each concept exposes editable **Preferred Label** (`skos:prefLabel`), **Notation** (`skos:notation`), **Definition** (`skos:definition`), an optional **Exact Match URI** (`skos:exactMatch`) for cross-DMN semantic linking, and a **Variable Name** that forms the concept URI. The Variable Name input is URI-safe — spaces are converted to underscores and IRI-illegal characters are stripped (v1.10.2), so generated Turtle always parses.

Concepts can be added or removed manually with **Add Input Concept** / **Add Output Concept**. They are written to the export as a `skos:ConceptScheme` plus the input and output concepts, each linked to its DMN variable via `dct:subject`.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Concepts tab showing the green "N concepts" summary, the Concept Scheme info box, and an Input Concepts section with an editable concept card (Preferred Label, Notation, Definition, Exact Match URI, Variable Name fields)](../../assets/screenshots/cpsv-editor-concepts-tab.png)
  <figcaption>Concepts tab with auto-generated NL-SBB concepts and their editable semantic properties</figcaption>
</figure>

---

## Vendor tab

See the [Vendor Integration](vendor-integration.md) user guide.
