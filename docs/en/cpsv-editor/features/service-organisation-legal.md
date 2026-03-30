# Service, Organisation & Legal Definition

The editor's three foundational tabs — Service, Organisation, and Legal — cover the mandatory descriptive metadata required by CPSV-AP 3.2.0 for any Dutch government public service.

---

## Service definition

The Service tab captures metadata about the public service itself, modelled as `cpsv:PublicService`. This is the anchor entity that all other data links to.

Key fields include the service's unique identifier (used to construct RDF URIs throughout the document), its official title and description, thematic classification, sector (government level), language, keywords, and cost and output specifications.

The identifier field has special significance: the editor sanitises it automatically, replacing spaces with hyphens and removing invalid URI characters. The resulting value is used as the base for every URI in the exported Turtle file, so a stable, descriptive identifier is important.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: Service tab showing the identifier, title, description, and sector fields with an example service filled in](../../assets/screenshots/cpsv-editor-service-tab.png)
  <figcaption>Service tab showing the identifier, title, description, and sector fields with an example service filled in</figcaption>
</figure>

The **Cost** and **Output** sections within the Service tab implement `cv:Cost` and `cv:Output` from CPSV-AP 3.2.0, allowing services to document fees and the deliverables citizens receive.

---

## Organisation management

The Organisation tab models the competent authority responsible for the service as `cv:PublicOrganisation` (CPSV-AP 3.2.0 compliant — formerly `org:Organization`).

The geographic jurisdiction field (`cv:spatial`) is mandatory under CPSV-AP 3.2.0. The editor enforces this and displays a validation error if it is omitted.

Organisation logos can be uploaded directly in this tab. Uploaded images are resized to 256×256px, encoded as base64, and — when publishing to TriplyDB — uploaded as a named asset. The generated Turtle includes both `foaf:logo` and `schema:image` properties. This creates a full semantic traversal path from a DMN decision model to the organisation's logo: `DMN → Service → Organisation → Logo`.

The organisation identifier supports both short form IDs (e.g. `SVB`) and full URIs. When a short ID is provided, the editor expands it to `https://regels.overheid.nl/organizations/{id}`.

---

## Legal resource linking

The Legal tab links the service to its statutory basis, modelled as `eli:LegalResource`. Dutch laws are identified by their BWB ID (e.g. `BWBR0002221`), which the editor validates against the expected pattern.

Fields include the BWB ID, the version or consolidation date, and an optional title and description. The editor generates a structured ELI URI for the legal resource, which the Rules and DMN tabs then reference to establish traceability from decision logic back to legislation.

The relationship between the service and its legal resource is expressed as `cv:hasLegalResource` (changed from `cpsv:follows` in CPSV-AP 3.2.0).
