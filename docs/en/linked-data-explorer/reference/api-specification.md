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

!!! info "Rendering never depended on any of this"

    `/v1/openapi.json` is a public mount served with
    `Access-Control-Allow-Origin: *`, verified from a documentation origin on
    16 September 2026. The reference above therefore renders from any origin and
    always has. Only the **Test Request** control depends on the allowlist
    described below — so if the reference ever fails to render, CORS on the
    specification fetch is not the reason.

!!! note "Test Request: what has to be true before it works"

    Four things, in two repositories. Three are settled; one is an Azure app
    setting that has not been made.

    1. **The backend stops answering a disallowed origin with a 500.** Done —
       `linked-data-explorer` PR #146, merged to `acc` as `ad26349` and deployed
       on 16 September 2026. The CORS origin callback now returns
       `callback(null, false)` instead of an `Error`, so an unlisted origin gets
       an ordinary response with no CORS header rather than a server error.
    2. **Both documentation tiers are in `CORS_ORIGIN` on the acceptance
       backend** — `https://iou-architectuur.open-regels.nl` and
       `https://acc.iou-architectuur.open-regels.nl`, since the same page is
       served from each. **Not done.** This is an Azure app setting on
       `ronl-linkeddata-backend-acc`, not a code change, and it is the remaining
       half of
       [linked-data-explorer#145](https://github.com/sgort/linked-data-explorer/issues/145).
       Until it lands the button still fails, and the browser console may still
       read `Failed to fetch` — the cause has changed, not yet the outcome.
    3. **The site CSP names the backend.** Done: `connect-src` in
       `staticwebapp.config.json` reads
       `'self' https://acc.backend.linkeddata.open-regels.nl`. This applies only
       to the deployed site — `mkdocs serve` sends no CSP at all, so on
       localhost the backend's CORS behaviour is the only thing in the way.
    4. **The reference points at acceptance.** Done, via the `servers`
       override described above.

    Measured against the acceptance backend on 16 September 2026, after the fix
    in step 1, varying only the `Origin` header on `GET /v1/health`:

    | `Origin` sent | Status | `Access-Control-Allow-Origin` |
    | --- | --- | --- |
    | `https://acc.linkeddata.open-regels.nl` | 200 | echoed |
    | `https://iou-architectuur.open-regels.nl` | 200 | absent *(was 500)* |
    | `https://acc.iou-architectuur.open-regels.nl` | 200 | absent *(was 500)* |
    | `http://localhost:8000` | 200 | absent *(was 500)* |
    | *no `Origin` header* | 200 | n/a |

    A preflight `OPTIONS` from an unlisted origin likewise returns 200 with no
    CORS headers, where it used to return 500. A missing
    `Access-Control-Allow-Origin` still makes the browser reject the response,
    which is why step 2 is what actually unblocks the button.

    **The production backend is unchanged** and still returns 500 for every
    origin but its own frontend. That fix was deliberately not promoted.

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
