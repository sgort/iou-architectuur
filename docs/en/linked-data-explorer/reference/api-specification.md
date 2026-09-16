---
component: Linked Data Explorer
---

# API Specification

The interactive reference below is rendered from the backend's own OpenAPI
document, so it describes the API as the service actually declares it rather
than as prose repeats it. For the narrative version — base URLs, the
deprecation story for `/api/*`, worked response examples — see
[API Reference](api-reference.md).

!!! warning "Rendered live, from a specification still being written"

    This page fetches `/v1/openapi.json` from the acceptance backend **on every
    page load**. There is no stored copy: what you see is whatever the service
    declares right now.

    That is deliberate while
    [linked-data-explorer#129](https://github.com/sgort/linked-data-explorer/issues/129)
    is in progress. It covers roughly 66 route handlers against the 24 paths
    described today, so the document will change often over the coming weeks and
    a committed snapshot would be stale within days. Expect descriptions and
    schemas to be thinner than the endpoints they document until that work
    lands.

    Live rendering does not cost the provenance: the banner below reports the
    version and build the document was served by, read from `/v1/health` at the
    same moment. What it does cost is reproducibility — this page cannot be
    replayed as it looked last week — and it shows nothing if the backend is
    unreachable. When the specification settles, a stored copy under
    `docs/assets/openapi/` is the more durable arrangement: reviewable in a
    diff, and immune to a backend deploy.

**Renderer:** [Scalar](https://github.com/scalar/scalar)
`@scalar/api-reference` 1.68.0, loaded from `cdn.jsdelivr.net` — the one
external script host this site's CSP names. The document is fetched from the
acceptance backend at render time.

Two configuration choices are deliberate and worth knowing before changing them:

- **`layout: "classic"`.** In Scalar's default `modern` layout the sidebar and
  search box are `position: fixed`; Scalar assumes it owns the viewport, and
  inside a Material content column its chrome escapes that column and floats
  over the page. `classic` places the sidebar inline instead.
- **`servers` is overridden** to the acceptance API, rather than the servers
  array being reordered in the stored document. Which environment a reader is
  pointed at is a presentation choice, and belongs in the page.

!!! info "What the render itself depends on"

    `/v1/openapi.json` is a **public mount** served with
    `Access-Control-Allow-Origin: *` — verified from a documentation origin on
    16 September 2026 — rather than through the `CORS_ORIGIN` allowlist that
    governs every other route. So the fetch works from any origin, and it does
    not depend on either documentation tier being allowlisted. **Test Request**
    does; the render does not.

    One consequence of rendering live: `connect-src` in the site's CSP is now
    load-bearing for the page itself, not only for Test Request. It already
    names `https://acc.backend.linkeddata.open-regels.nl`, so nothing needs
    changing — but if that host is ever removed from the policy while the policy
    is enforced, this page goes blank rather than merely losing a button. See
    the note below on why the CSP is not enforced today.

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

    So **both the render and Test Request reach the backend because no CSP is
    enforced**, not because the policy permits them. Tracked as
    [iou-architectuur#98](https://github.com/sgort/iou-architectuur/issues/98);
    when the file is actually applied, `connect-src` already names the host, so
    this page should keep working unchanged. That entry stops being cosmetic the
    moment the policy is switched on.

---

<!--
  Provenance banner. /v1/openapi.json carries no version of its own, so the
  version and build are read from /v1/health, which reports both for the very
  service that just served the document.

  Unlike /v1/openapi.json — a public mount with wildcard CORS — /v1/health goes
  through the CORS_ORIGIN allowlist. Both deployed documentation tiers are on
  it; localhost is not, so under `mkdocs serve` this banner stays hidden. That
  is intended: it degrades to nothing rather than to an error.
-->
<div id="lde-spec-provenance" hidden></div>

<script>
  (function () {
    var el = document.getElementById('lde-spec-provenance');
    if (!el || !window.fetch) { return; }
    fetch('https://acc.backend.linkeddata.open-regels.nl/v1/health', {
      headers: { accept: 'application/json' }
    })
      .then(function (r) { return r.ok ? r.json() : Promise.reject(r.status); })
      .then(function (h) {
        var build = h.build && h.build.label ? h.build.label : 'build not tracked';
        el.textContent =
          'Rendered from ' + (h.environment || 'unknown') +
          ' · version ' + (h.version || 'unknown') +
          ' · ' + build +
          ' · read ' + new Date().toISOString().replace('T', ' ').slice(0, 16) + ' UTC';
        el.hidden = false;
      })
      .catch(function () { /* leave hidden — the reference itself still renders */ });
  })();
</script>

<script
  id="api-reference"
  data-url="https://acc.backend.linkeddata.open-regels.nl/v1/openapi.json"
  data-configuration='{"layout":"classic","withDefaultFonts":false,"hideDownloadButton":false,"showSidebar":true,"servers":[{"url":"https://acc.backend.linkeddata.open-regels.nl/v1","description":"Acceptance"}]}'>
</script>
<script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference@1.68.0/dist/browser/standalone.js"></script>
