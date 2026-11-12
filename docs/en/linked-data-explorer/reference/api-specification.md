---
component: Linked Data Explorer
---

# API Specification (v1)

<!--
  Provenance banner. /v1/openapi.json carries info.version, taken from the
  backend's package.json at build time, but no environment and no build. The
  banner therefore reads /v1/health, which reports the version, environment
  and build of the running process. The document is read lazily, so for a
  moment after a zip deploy it can come from a newer artifact than the process
  /v1/health describes.

  Unlike /v1/openapi.json — a public mount with wildcard CORS — /v1/health goes
  through the CORS_ORIGIN allowlist. Both deployed documentation tiers are on
  it; localhost is not, so under `mkdocs serve` this banner stays hidden. That
  is intended: it degrades to nothing rather than to an error.

  How this page is wired, and what it depends on at run time:
  docs/en/contributing/doc-architecture/openapi-rendering.md
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

Fetched live from the acceptance API, so it always shows what the service
declares right now. Every `/v1` route is described — the backend's tests fail
when one is not. **Test Request** calls acceptance and never production, on
purpose.

!!! tip "Tick a parameter to send it"
    In **Test Request**, a query or header parameter is sent only when its row
    is ticked. Typing a value into a row does not tick it, and an unticked
    value is silently left out, so the service answers as if the parameter
    were absent. The checkbox is the only reliable sign of what is sent: the
    address shown at the top of the panel does not list the query string,
    even for a parameter that is ticked and sent.

Operations that change shared state need a Bearer token from the Keycloak realm `ronl` carrying the role `lde-author` — the `bearerAuth` scheme, since v2026.11.2. Without one they answer `401`. See [Backend — Sign-in](../developer/backend.md#sign-in).

This reference renders `/v1/openapi.json`. The `/v2` routes have their own
document, rendered the same way on [API Specification (v2)](api-specification-v2.md);
see the [stability contract](api-stability.md#v2norms) for what `/v2/norms` returns.

For base URLs, the `/api/*` legacy aliases and the error format, see
[Backend Architecture](../developer/backend.md#api-versioning). For how this
page is wired and what it depends on at run time, see
[OpenAPI Rendering](../../contributing/doc-architecture/openapi-rendering.md).

<script
  id="api-reference"
  data-url="https://acc.backend.linkeddata.open-regels.nl/v1/openapi.json"
  data-configuration='{"layout":"classic","withDefaultFonts":false,"hideDownloadButton":false,"showSidebar":true,"servers":[{"url":"https://acc.backend.linkeddata.open-regels.nl/v1","description":"Acceptance"}]}'>
</script>
<script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference@1.68.0/dist/browser/standalone.js"></script>
