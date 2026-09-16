---
component: Linked Data Explorer
---

# API Specification

<!--
  Provenance banner. /v1/openapi.json carries no version of its own, so the
  version and build are read from /v1/health, which reports both for the very
  service that just served the document.

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

Fetched live from the acceptance API, so it changes as the service does —
descriptions and schemas are still thin in places while
[linked-data-explorer#129](https://github.com/sgort/linked-data-explorer/issues/129)
is in progress. **Test Request** calls acceptance and never production, on
purpose.

For base URLs, the deprecation story for `/api/*` and worked response examples,
see [API Reference](api-reference.md). For how this page is wired and what it
depends on at run time, see
[OpenAPI Rendering](../../contributing/doc-architecture/openapi-rendering.md).

<script
  id="api-reference"
  data-url="https://acc.backend.linkeddata.open-regels.nl/v1/openapi.json"
  data-configuration='{"layout":"classic","withDefaultFonts":false,"hideDownloadButton":false,"showSidebar":true,"servers":[{"url":"https://acc.backend.linkeddata.open-regels.nl/v1","description":"Acceptance"}]}'>
</script>
<script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference@1.68.0/dist/browser/standalone.js"></script>
