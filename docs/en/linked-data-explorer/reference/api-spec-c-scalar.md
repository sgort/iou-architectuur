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
- Whether `layout: "classic"` is enough to keep it inside the content column.
- Font rendering: `font-src` is `'self' https://fonts.gstatic.com`, so any
  webfont Scalar pulls from its own host falls back.
- The request-example panel, which is the part Redoc does least well.
- As with the others, the send-request feature is dead on arrival — see the
  note below.

!!! bug "Two findings from the first look at this page"

    **Layout.** In Scalar's default `modern` layout the sidebar and search box
    are `position: fixed`. Scalar assumes it owns the viewport, so inside
    Material's content column its chrome escapes that column and floats over
    the page — two app shells competing for the same screen. This page now
    passes `layout: "classic"`, which Scalar's own bundle validates as one of
    exactly two allowed values and which places the sidebar inline (`after`)
    instead of as a fixed `aside`.

    **Test Request fails, and not only for the reason predicted.** The backend
    allows exactly one origin — its own frontend — and returns **HTTP 500**,
    not 403, for every other `Origin` header. Measured 16 September 2026
    against both environments: `https://linkeddata.open-regels.nl` → 200 with
    `Access-Control-Allow-Origin`; `https://acc.linkeddata.open-regels.nl` →
    500 against production and 200 against acceptance; every other origin
    tried, including `http://localhost:8000` and the docs site's own
    `https://iou-architectuur.open-regels.nl` → 500 with no CORS header. A
    request with no `Origin` header at all (curl, server to server) returns
    200. So the browser is told nothing useful and reports `Failed to fetch`.
    Tracked as
    [linked-data-explorer#145](https://github.com/sgort/linked-data-explorer/issues/145).

!!! note "What has to be true before Test Request works"

    Three things, in two repositories, and one of them is not ours:

    1. **The backend stops answering a disallowed origin with a 500** and
       allowlists both documentation tiers —
       `https://iou-architectuur.open-regels.nl` and
       `https://acc.iou-architectuur.open-regels.nl`, since the same page is
       served from each — on the acceptance backend. Both are covered by
       [linked-data-explorer#145](https://github.com/sgort/linked-data-explorer/issues/145)
       and neither has landed yet, so the button still fails today.
    2. **The site CSP names the backend.** Done: `connect-src` in
       `staticwebapp.config.json` now reads
       `'self' https://acc.backend.linkeddata.open-regels.nl`. Note this applies
       only to the deployed site — `mkdocs serve` sends no CSP at all, so on
       localhost the CORS behaviour above is the only thing in the way.
    3. **The reference points at acceptance.** Done, via Scalar's `servers`
       configuration option rather than by editing the stored specification,
       which stays a faithful copy of what the backend serves.

    Acceptance only is deliberate. The specification declares no
    `securitySchemes` and no global `security`, so every operation is
    unauthenticated — including `POST /dmns/deploy`, `POST /dmns/process/deploy`
    and `DELETE /cache/clear`. Those are already reachable by anything that is
    not a browser, since the origin check passes requests that send no `Origin`
    at all; CORS is a browser policy, not an authorization boundary. But a Send
    button on a public documentation page is a different proposition from an
    endpoint someone has to write a request to reach, and production is left
    locked to its own frontend for that reason.

---

<script
  id="api-reference"
  data-url="/assets/openapi/linked-data-explorer.json"
  data-configuration='{"layout":"classic","withDefaultFonts":false,"hideDownloadButton":false,"showSidebar":true,"servers":[{"url":"https://acc.backend.linkeddata.open-regels.nl/v1","description":"Acceptance"}]}'>
</script>
<script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference@1.68.0/dist/browser/standalone.js"></script>
