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
declares right now. **Test Request** calls acceptance and never production, on
purpose.

**Every operation the service serves is described** — 133 in release
2026.09.15, the machine-to-machine surface under `/v1/m2m` included. Two
backend checks hold the document to the code:

- **Coverage.** `src/openapi/coverage.test.ts` compares the document with the
  route registry and fails on a served operation that is not described, and on
  a described operation that is not served.
- **Conformance.** Route tests compare real responses against the document with
  `expectToMatchOperation`, which validates with Ajv against JSON Schema
  2020-12 with strict schema checking on. `npm test` then runs
  `scripts/check-conformance-coverage.cjs`, which fails the run when any
  described operation was never compared against a real response.

Three security schemes are declared:

- `bearerAuth`, a Keycloak-issued JWT, applies by default.
- `m2mOAuth`, the client-credentials grant, applies to `/v1/m2m`. A valid token
  is not enough: the token's `azp` must be on `M2M_ALLOWED_CLIENTS`
  (`operaton-mcp-client` alone by default). OpenAPI cannot express that
  condition, so the scheme's description states it and every `/v1/m2m`
  operation carries the shared `M2mForbidden` response — `403
  M2M_CLIENT_NOT_ALLOWED` for a caller off the allow-list, `403
  OPERATION_NOT_PERMITTED` for an operation withdrawn from machine consumers.
- `mediaAggregatorKey` applies to the media-aggregator search, which requires it
  only when the service is configured with a key.

Deploying process definitions is not part of this API: it belongs to the Linked
Data Explorer — see its
[API Specification](../../linked-data-explorer/reference/api-specification.md).

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
