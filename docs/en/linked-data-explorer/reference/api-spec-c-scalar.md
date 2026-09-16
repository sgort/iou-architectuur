---
component: Linked Data Explorer
---

# API Specification — Option C3 (Scalar)

!!! warning "Trial page"

    This page exists on the `docs/openapi-render-trial` branch to compare
    OpenAPI renderers. It is not part of the published documentation set, and
    the specification it renders is the **beta** document served from the
    acceptance backend, fetched on 16 September 2026.

**Renderer:** [Scalar](https://github.com/scalar/scalar) `@scalar/api-reference`
1.68.0 from `cdn.jsdelivr.net`. The newest of the three client-side options, and
the only one with first-class OpenAPI 3.1 support in its own documentation.

**What to look for:**

- Whether its dark theme can be pinned to match the site rather than fighting it.
- Font rendering: `font-src` is `'self' https://fonts.gstatic.com`, so any
  webfont Scalar pulls from its own host falls back.
- The request-example panel, which is the part Redoc does least well.
- As with the others, the send-request feature is dead on arrival under
  `connect-src 'self'`.

---

<script id="api-reference" data-url="/assets/openapi/linked-data-explorer.json"></script>
<script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference@1.68.0/dist/browser/standalone.js"></script>
