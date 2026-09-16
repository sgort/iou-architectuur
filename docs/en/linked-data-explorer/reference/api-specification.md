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

!!! success "Test Request works against acceptance"

    Confirmed end to end on the deployed acceptance documentation site on
    16 September 2026: `GET /health` from this page returned **200 OK** in 306 ms
    from `https://acc.backend.linkeddata.open-regels.nl/v1`, reporting backend
    build `ad26349` run 154.

    Two changes made that possible, both on the backend side:

    1. **A disallowed origin no longer answers 500.** `linked-data-explorer`
       PR #146, merged as `ad26349`. The CORS origin callback returns
       `callback(null, false)` rather than an `Error`, so an unlisted origin gets
       an ordinary response with no CORS header instead of falling through to the
       error handler.
    2. **Both documentation tiers are allowlisted on the acceptance backend.**
       `CORS_ORIGIN` on the `ronl-linkeddata-backend-acc` App Service now
       includes `https://iou-architectuur.open-regels.nl` and
       `https://acc.iou-architectuur.open-regels.nl`. Together with #146 this
       closed [linked-data-explorer#145](https://github.com/sgort/linked-data-explorer/issues/145).

    Measured against the acceptance backend after both landed, varying only the
    `Origin` header on `GET /v1/health`:

    | `Origin` sent | Status | `Access-Control-Allow-Origin` |
    | --- | --- | --- |
    | `https://iou-architectuur.open-regels.nl` | 200 | echoed |
    | `https://acc.iou-architectuur.open-regels.nl` | 200 | echoed |
    | `https://acc.linkeddata.open-regels.nl` | 200 | echoed |
    | `http://localhost:8000` | 200 | absent |

    **The production backend is unchanged** and still returns 500 to every origin
    but its own frontend. That fix was deliberately not promoted, and this page
    is pinned to acceptance through the `servers` override described above.

    **Acceptance only is deliberate.** The specification declares no
    `securitySchemes` and no global `security`, so every operation is
    unauthenticated — including `POST /dmns/deploy`, `POST /dmns/process/deploy`
    and `DELETE /cache/clear`. Those are already reachable by anything that is
    not a browser, since the origin check passes requests that send no `Origin`
    at all; CORS is a browser policy, not an authorization boundary. But a Send
    button on a public documentation page is a different proposition from an
    endpoint someone has to write a request to reach, and production is left
    locked to its own frontend for that reason.

!!! warning "The site's Content-Security-Policy is not enforced"

    `staticwebapp.config.json` at the repository root declares a CSP, and
    `connect-src` there names the acceptance backend. **That file is not applied
    to either deployment.** Both pipelines publish with `app_location: "site"`,
    Azure Static Web Apps reads `staticwebapp.config.json` from the app artifact
    root, and `mkdocs build` never copies the file into `site/`.

    Verified 16 September 2026: neither `iou-architectuur.open-regels.nl` nor
    `acc.iou-architectuur.open-regels.nl` returns a `Content-Security-Policy` or
    `X-Frame-Options` header, and both return `Referrer-Policy: same-origin`
    where the file declares `strict-origin-when-cross-origin`.

    So **Test Request reaches the backend because no CSP is enforced**, not
    because the policy permits it. Nothing on this page depends on the CSP today.
    Tracked as
    [iou-architectuur#98](https://github.com/sgort/iou-architectuur/issues/98);
    when the file is actually applied, `connect-src` already names the host and
    this page should keep working unchanged.

---

<script
  id="api-reference"
  data-url="/assets/openapi/linked-data-explorer.json"
  data-configuration='{"layout":"classic","withDefaultFonts":false,"hideDownloadButton":false,"showSidebar":true,"servers":[{"url":"https://acc.backend.linkeddata.open-regels.nl/v1","description":"Acceptance"}]}'>
</script>
<script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference@1.68.0/dist/browser/standalone.js"></script>
