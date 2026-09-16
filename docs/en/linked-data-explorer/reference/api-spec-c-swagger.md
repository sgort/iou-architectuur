---
component: Linked Data Explorer
---

# API Specification — Option C2 (Swagger UI)

!!! warning "Trial page"

    This page exists on the `docs/openapi-render-trial` branch to compare
    OpenAPI renderers. It is not part of the published documentation set, and
    the specification it renders is the **beta** document served from the
    acceptance backend, fetched on 16 September 2026.

**Renderer:** [Swagger UI](https://github.com/swagger-api/swagger-ui) 5.32.15 —
the presentation FastAPI serves at `/docs`, and the one the CPSV/Norm Editor
pages already send readers to. The script comes from `cdn.jsdelivr.net`; the
stylesheet is **vendored into `docs/stylesheets/swagger-ui.css`**, because the
site CSP sets `style-src 'self'` and would block it from any CDN.

!!! danger "Try it out cannot work here"

    The site CSP sets `connect-src 'self'`. Swagger UI's **Try it out** button
    issues an XHR to `acc.backend.linkeddata.open-regels.nl`, which the browser
    refuses. The button renders and then fails silently. `tryItOutEnabled` is
    left off below for that reason — turning it on would only advertise
    something that does not work.

**What to look for:**

- Whether the familiar Swagger chrome sits comfortably inside a Material page.
- Tag grouping (`Health & monitoring`, `Discovery`, `Assets`) versus the
  untagged endpoints.
- That it, too, ignores the site's dark mode.

---

<link rel="stylesheet" href="/stylesheets/swagger-ui.css">

<div id="swagger-ui-container"></div>

<script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5.32.15/swagger-ui-bundle.js"></script>
<script>
  (function () {
    var mount = document.getElementById('swagger-ui-container');
    if (!mount || typeof SwaggerUIBundle === 'undefined') { return; }
    SwaggerUIBundle({
      url: '/assets/openapi/linked-data-explorer.json',
      domNode: mount,
      deepLinking: true,
      docExpansion: 'list',
      defaultModelsExpandDepth: 1,
      tryItOutEnabled: false,
      supportedSubmitMethods: []
    });
  })();
</script>
