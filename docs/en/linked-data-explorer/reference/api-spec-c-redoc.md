---
component: Linked Data Explorer
---

# API Specification — Option C1 (Redoc)

!!! warning "Trial page"

    This page exists on the `docs/openapi-render-trial` branch to compare
    OpenAPI renderers. It is not part of the published documentation set, and
    the specification it renders is the **beta** document served from the
    acceptance backend, fetched on 16 September 2026.

**Renderer:** [Redoc](https://github.com/Redocly/redoc) 2.5.4, loaded as a
standalone bundle from `cdn.jsdelivr.net` — the one script host the site CSP
allows besides `'self'`.

**How it works:** the browser downloads the renderer, then fetches
`/assets/openapi/linked-data-explorer.json` from this same origin and draws the
three-panel layout client-side. Nothing about it reaches MkDocs' search index.

**What to look for:**

- The three-panel presentation you get on a Redocly-hosted portal.
- Schema expansion depth, and how `oneOf` variants are presented.
- That it ignores the site's light/dark toggle — Redoc carries its own theme.
- Initial render cost on a cold load.

---

<div id="redoc-container"></div>

<script src="https://cdn.jsdelivr.net/npm/redoc@2.5.4/bundles/redoc.standalone.js"></script>
<script>
  (function () {
    var mount = document.getElementById('redoc-container');
    if (!mount || typeof Redoc === 'undefined') { return; }
    Redoc.init(
      '/assets/openapi/linked-data-explorer.json',
      {
        hideDownloadButton: false,
        expandResponses: '200',
        nativeScrollbars: true,
        theme: { typography: { fontSize: '15px' } }
      },
      mount
    );
  })();
</script>
