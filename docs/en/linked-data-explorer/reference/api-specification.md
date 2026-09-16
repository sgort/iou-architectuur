---
component: Linked Data Explorer
---

# API Specification

The interactive reference below is rendered from the backend's own OpenAPI
document, so it describes the API as the service actually declares it rather
than as prose repeats it. For the narrative version — base URLs, the
deprecation story for `/api/*`, worked response examples — see
[API Reference](api-reference.md).

!!! warning "Rendered from a beta specification"

    The stored document is the **beta** specification served at
    `/v1/openapi.json`, fetched on 16 September 2026. Work on a complete
    specification is still underway, so descriptions and schemas here may be
    thinner than the endpoints they document. The copy under
    `docs/assets/openapi/` is kept faithful to what the backend serves; it is
    never hand-edited to read better.

**Renderer:** [Scalar](https://github.com/scalar/scalar)
`@scalar/api-reference` 1.68.0, loaded from `cdn.jsdelivr.net` — the one
external script host this site's CSP allows. The document itself is served from
this origin, not fetched across the network.

Two configuration choices are deliberate and worth knowing before changing them:

- **`layout: "classic"`.** In Scalar's default `modern` layout the sidebar and
  search box are `position: fixed`; Scalar assumes it owns the viewport, and
  inside a Material content column its chrome escapes that column and floats
  over the page. `classic` places the sidebar inline instead.
- **`servers` is overridden** to the acceptance API, rather than the servers
  array being reordered in the stored document. Which environment a reader is
  pointed at is a presentation choice, and belongs in the page.

!!! note "Test Request: what has to be true before it works"

    Three things, in two repositories, and one of them is not ours:

    1. **The backend stops answering a disallowed origin with a 500** and
       allowlists both documentation tiers —
       `https://iou-architectuur.open-regels.nl` and
       `https://acc.iou-architectuur.open-regels.nl`, since the same page is
       served from each — on the acceptance backend. Both are covered by
       [linked-data-explorer#145](https://github.com/sgort/linked-data-explorer/issues/145)
       and neither has landed yet, so the button still fails today.
    2. **The site CSP names the backend.** Done: `connect-src` in
       `staticwebapp.config.json` reads
       `'self' https://acc.backend.linkeddata.open-regels.nl`. This applies only
       to the deployed site — `mkdocs serve` sends no CSP at all, so on
       localhost the backend's CORS behaviour is the only thing in the way.
    3. **The reference points at acceptance.** Done, via the `servers`
       override described above.

    On the CORS behaviour, measured 16 September 2026: the backend allows
    exactly one origin — its own frontend — and returns **HTTP 500**, not 403,
    for every other `Origin` header. `https://linkeddata.open-regels.nl` → 200
    with `Access-Control-Allow-Origin`; every other origin tried, including both
    documentation tiers and `http://localhost:8000` → 500 with no CORS header. A
    request with no `Origin` header at all (curl, server to server) returns 200.
    The browser is told nothing useful and reports `Failed to fetch`.

    **Acceptance only is deliberate.** The specification declares no
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
