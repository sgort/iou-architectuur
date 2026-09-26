---
component: RONL Business API
---

# API Specification

<!--
  Modelled on the Linked Data Explorer's API Specification page, with these
  differences — each checked against the acceptance API on 26 September 2026:

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
    Test Request — goes through the backend's CORS allowlist, and on acceptance
    that echoes only https://iou-architectuur.open-regels.nl. Neither
    acc.iou-architectuur.open-regels.nl nor localhost is echoed, so the banner
    (and Test Request) work only on the PRODUCTION documentation tier. Elsewhere
    the banner stays hidden: it degrades to nothing rather than to an error.

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
declares right now. **Test Request** calls acceptance and never production, on
purpose.

**113 of 131 operations are described.** The remaining 18 are the `/v1/m2m`
surface, pending [#214](https://github.com/sgort/ronl-business-api/issues/214);
until then they are listed in `openapi/pending.json` and documented on
[API Endpoints](api-endpoints.md#m2m-operaton). A backend test
(`src/openapi/coverage.test.ts`) fails when a served operation is neither
described nor pending, and the pending list may only shrink.

Two security schemes are declared: `bearerAuth`, a Keycloak-issued JWT that
applies by default, and `mediaAggregatorKey`, which the media-aggregator search
requires only when the service is configured with a key.
The document is linted with Spectral against the NL API Design Rules 2.2.1
ruleset, with its deviations recorded rather than hidden: `nlgov:semver` is off
because releases are CalVer, and the problem-details rules are off because the
API answers its own `{ success, error }` envelope rather than
`application/problem+json`.

For versioning, the response envelope and error handling, see
[API Design](../features/api-design.md).

<script
  id="api-reference"
  data-url="https://acc.api.open-regels.nl/v1/openapi.json"
  data-configuration='{"layout":"classic","withDefaultFonts":false,"hideDownloadButton":false,"showSidebar":true,"servers":[{"url":"https://acc.api.open-regels.nl/v1","description":"Acceptance"}]}'>
</script>
<script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference@1.68.0/dist/browser/standalone.js"></script>
