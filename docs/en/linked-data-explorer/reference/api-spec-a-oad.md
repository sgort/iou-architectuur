---
component: Linked Data Explorer
---

# API Specification — Option A (neoteroi-mkdocs)

!!! warning "Trial page"

    This page exists on the `docs/openapi-render-trial` branch to compare
    OpenAPI renderers. It is not part of the published documentation set, and
    the specification it renders is the **beta** document served from the
    acceptance backend, fetched on 16 September 2026.

**Renderer:** [`neoteroi-mkdocs`](https://www.neoteroi.dev/mkdocs-plugins/web/oad/)
(`neoteroi.mkdocsoad` plugin, version 1.2.0), driven by `essentials-openapi`.

**How it works:** the plugin reads the specification at build time and emits
plain HTML into the page, before Material's own styling and before the search
indexer runs. Nothing is fetched in the browser.

**What to look for:**

- Does it inherit the site palette, dark mode and typography?
- Are the request/response schemas legible, including `oneOf` / `$ref` chains?
- Does the page appear in site search when you look for an endpoint path?
- Does it handle OpenAPI **3.1.0** constructs, or degrade on them?

**One caveat found while building this page:** the renderer emits semantic
class names (`http-get`, `api-tag`) but ships no stylesheet for them — the
`neoteroi.css` on its own site covers the cards/timeline/gantt plugins only.
Tables, `details` blocks and the tabbed response panels are styled by Material
already; the verb badges needed the ~25 lines now in
`docs/stylesheets/oad-trial.css`, written against Material's own custom
properties so dark mode needs no second rule.

---

[OAD(./docs/assets/openapi/linked-data-explorer.json)]
