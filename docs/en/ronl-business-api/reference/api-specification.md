---
component: RONL Business API
---

# API Specification

<!--
  Modelled on the Linked Data Explorer's API Specification page, with these
  differences — each checked against the acceptance API on 26 September 2026,
  and the CORS point again on 30 September 2026:

  - /v1/openapi.json DOES carry the version (info.version is the CalVer release
    string, set at build time). The banner still reads /v1/health, because that
    is what names the build — commit and workflow run — behind the running
    service, and the environment.

  - /v1/health is WRAPPED here: { success, data: { name, version,
    build: { sha, run, runId } | null, status, environment, … } }. The LDE's is
    flat, with a preformatted build.label. The script below reads h.data and
    formats the build itself (short sha plus run number).

  - CORS: /v1/openapi.json is served with Access-Control-Allow-Origin: *, so the
    render works from any origin. /v1/health — and every other route, so also
    Test Request — goes through the backend's CORS allowlist. On acceptance that
    allowlist (the App Service's CORS_ORIGIN) names both documentation tiers,
    https://iou-architectuur.open-regels.nl and
    https://acc.iou-architectuur.open-regels.nl — the second added on
    30 September 2026 — so the banner and Test Request work on both. localhost
    is not on it: under `mkdocs serve` the banner stays hidden, degrading to
    nothing rather than to an error, as on the LDE page.

  - Scalar version, layout and the Acceptance-only servers override are the
    same as the LDE page. The document itself lists Production first; the
    override keeps Test Request off production.

  How this arrangement works, and what it depends on at run time:
  docs/en/contributing/doc-architecture/openapi-rendering.md
-->
<div id="rba-spec-provenance" class="spec-provenance" hidden></div>

<script>
  (function () {
    var el = document.getElementById('rba-spec-provenance');
    if (!el || !window.fetch) { return; }
    fetch('https://acc.api.open-regels.nl/v1/health', {
      headers: { accept: 'application/json' }
    })
      .then(function (r) { return r.ok ? r.json() : Promise.reject(r.status); })
      .then(function (h) {
        var d = h && h.data;
        if (!d) { return Promise.reject('unexpected shape'); }
        var b = d.build;
        var build = b && b.sha
          ? 'build ' + String(b.sha).slice(0, 7) + (b.run ? ' · #' + b.run : '')
          : 'build not tracked';
        el.textContent =
          'Rendered from ' + (d.environment || 'unknown') +
          ' · version ' + (d.version || 'unknown') +
          ' · ' + build +
          ' · read ' + new Date().toISOString().replace('T', ' ').slice(0, 16) + ' UTC';
        el.hidden = false;
      })
      .catch(function () { /* leave hidden — the reference itself still renders */ });
  })();
</script>

Fetched live from the acceptance API, so it always shows what the service
declares right now. Every operation the service serves is described, `/v1/m2m`
included — the backend's tests fail when one is not, or when a described
operation was never checked against a real response. **Test Request** calls
acceptance and never production, on purpose.

Deploying process definitions belongs to the Linked Data Explorer — see its
[API Specification](../../linked-data-explorer/reference/api-specification.md).
For versioning, the response envelope, the error format and how the document is
linted, see [API Design](../features/api-design.md#published-description); for
who may call `/v1/m2m`, see
[Authentication & IAM](../features/authentication-iam.md). For how this page is
wired and what it depends on at run time, see
[OpenAPI Rendering](../../contributing/doc-architecture/openapi-rendering.md).

<script
  id="api-reference"
  data-url="https://acc.api.open-regels.nl/v1/openapi.json"
  data-configuration='{"layout":"classic","withDefaultFonts":false,"hideDownloadButton":false,"showSidebar":true,"servers":[{"url":"https://acc.api.open-regels.nl/v1","description":"Acceptance"}]}'>
</script>
<script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference@1.68.0/dist/browser/standalone.js"></script>
