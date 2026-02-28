# Getting Started

---

## Prerequisites

**To use the web application:** a modern browser (Chrome, Firefox, Edge, or Safari). No installation required — the editor runs entirely in the browser at [cpsv-editor.open-regels.nl](https://cpsv-editor.open-regels.nl).

**To run the editor locally:**

- Node.js 14 or higher
- npm

---

## Local installation

```bash
git clone https://github.com/your-org/cpsv-editor.git
cd cpsv-editor
npm install
npm start
```

The application opens at `http://localhost:3000`.

To build a production bundle:

```bash
npm run build
```

The `build/` directory contains the static files ready for deployment.

---

## Creating your first service definition

The typical workflow for a new service definition follows these steps:

1. **Fill in Service Details** — Enter the service identifier, official name, description, and sector. The identifier becomes the base for all RDF URIs in the output, so choose something stable and descriptive (e.g. `aow-leeftijdsbepaling`).

2. **Add Organisation** — Enter the competent authority. The geographic jurisdiction (`cv:spatial`) is mandatory.

3. **Link Legal Resource** — Enter the BWB ID of the governing legislation (e.g. `BWBR0002221`). The editor validates the format and constructs the ELI URI.

4. **Define Rules** *(optional)* — Add temporal rules that implement the legal resource.

5. **Add Parameters** *(optional)* — Add configurable constants used by the rules.

6. **Add Policy (CPRMV)** *(optional)* — Import or enter normative rules extracted from the legislation.

7. **Validate** — Click the **Validate** button to check for errors. Missing mandatory fields are highlighted.

8. **Download TTL** — Click **Download TTL** to export the compliant Turtle file.

<figure markdown>
  ![Screenshot: The editor in its initial empty state showing the tab navigation and the Service tab with empty fields and the Validate and Download TTL buttons visible](../../assets/screenshots/cpsv-editor-empty-state.png)
  <figcaption>The editor in its initial empty state</figcaption>
</figure>

---

## Importing an existing file

If you have an existing `.ttl` file:

1. Click **Import TTL File** in the header.
2. Select the file.
3. All tabs populate automatically from the imported data.
4. Edit the fields as needed.
5. Download the updated Turtle.

---

## Clearing the editor

Click **Clear** in the header to reset all fields. A confirmation dialog prevents accidental data loss.
