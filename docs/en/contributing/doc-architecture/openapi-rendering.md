---
scope: cross-cutting
verified:
  date: 2026-10-04
  against:
    Linked Data Explorer: "9e0d18e"
    RONL Business API: "5c6e716"
---

# OpenAPI Rendering

How the API Specification pages — the
[Linked Data Explorer's](../../linked-data-explorer/reference/api-specification.md)
and, since 26 September 2026, the
[RONL Business API's](../../ronl-business-api/reference/api-specification.md) — turn
a component's OpenAPI document into a browsable reference, what they depend on at
run time, and which of those dependencies are load-bearing. The two pages are built
the same way; where they differ, this page says so.

This page exists so the specification page itself can stay what a reader came
for — the reference — rather than opening with four boxes of operational
detail.

---

## The arrangement

Each page declares an empty banner element and three script tags: the provenance
script described below, then Scalar (`@scalar/api-reference`, pinned at 1.68.0 on
both pages) loaded from `cdn.jsdelivr.net`, and a configuration element that tells it
which document to fetch:

```html
<script
  id="api-reference"
  data-url="https://acc.backend.linkeddata.open-regels.nl/v1/openapi.json"
  data-configuration='{"layout":"classic", …,"servers":[{"url":"…/v1","description":"Acceptance"}]}'>
</script>
```

Everything below is a consequence of the last two.

### Live, not stored

The document is fetched from the backend **on every page load**. There is no
committed copy.

That was chosen on 16 September 2026, while
[linked-data-explorer#129](https://github.com/sgort/linked-data-explorer/issues/129)
was describing the API route group by route group: the document went from 24 paths
to 63 in three days, so a snapshot would have been stale within days, and every
backend deploy would have owed the documentation site a fetch, a commit, a build and
a promotion. #129 closed on 17 September, and every `/v1` route is now described —
the backend's tests fail when one is not.

The cost is **reproducibility**. The page cannot be replayed as it looked last
week, and it shows nothing at all if the backend is unreachable. When the
specification stops changing from one release to the next, a stored copy under
`docs/assets/openapi/` becomes the better arrangement — reviewable in a diff, and
immune to a backend deploy. #129 closing is a sign of that, not proof of it; the
page stays live until releases stop moving the document. The switch back is a
one-line change to `data-url` plus the file.

### Provenance comes from a second endpoint

Both documents carry their own release version: `info.version` is injected from
`package.json` at build time, never written in the source, so the document and the
running service cannot disagree about it. What the document cannot say is **which
build** is serving it, or in which environment — so the banner reads `/v1/health`,
which reports the version, the environment and the build (commit and workflow run)
of the very service that just served the document:

```
Rendered from acceptance · version 2026.10.0 · build 9e0d18e · #342 · read … UTC
```

The two services shape `/v1/health` differently, and each page's script reads its
own. The Linked Data Explorer's is flat and carries a preformatted `build.label`. The
RONL Business API's is wrapped in its `{ success, data }` envelope, with
`data.build = { sha, run, runId }` and no label, so its script formats the short SHA
and run number itself.

If that fetch fails the banner stays hidden and the reference still renders. It
degrades to nothing, never to an error.

Both banners are styled by `docs/stylesheets/spec-provenance.css`, listed in
`extra_css`. The Linked Data Explorer's element is targeted by its id,
`#lde-spec-provenance`; any later page uses the shared `.spec-provenance` class, as
the RONL Business API's does.

### Two configuration choices that look wrong and are not

- **`layout: "classic"`.** Scalar's default `modern` layout puts its sidebar and
  search box at `position: fixed`. Scalar assumes it owns the viewport, so
  inside a Material content column its chrome escapes that column and floats
  over the page — two application shells competing for one screen. `classic`
  places the sidebar inline.
- **`servers` is overridden** rather than the servers array being reordered in
  the document. Which environment a reader is pointed at is a presentation
  choice and belongs in the page, not in a copy of someone else's contract.

---

## What it depends on at run time

Three separate mechanisms, commonly confused with one another.

| Mechanism | Governs | Load-bearing for |
|---|---|---|
| Wildcard CORS on `/v1/openapi.json` | the document fetch | **the render** |
| `CORS_ORIGIN` allowlist | every other route | **Test Request**, and the provenance banner |
| `connect-src` in the site CSP | all outbound fetches | both — if the CSP is ever enforced |

The mechanisms are the same for both components; what differs is who is on the
allowlist.

### The CORS asymmetry

`/v1/openapi.json` is a **public mount** served with
`Access-Control-Allow-Origin: *`, entirely separate from the `CORS_ORIGIN`
allowlist that governs every other route. So the render works from any origin
and does not depend on either documentation tier being allowlisted — a third
party could render the same document.

`/v1/health` does **not** get that treatment. It goes through the allowlist, and
both acceptance backends now allowlist both deployed documentation tiers —
`https://iou-architectuur.open-regels.nl` and
`https://acc.iou-architectuur.open-regels.nl`. Neither allowlists `localhost`. So
both banners show on both deployed tiers; under `mkdocs serve`, neither shows. The
RONL Business API's allowlist named only the production tier until its acceptance
App Service's `CORS_ORIGIN` gained the acceptance documentation origin on
30 September 2026.

### Test Request targets acceptance, deliberately

Scalar's **Test Request** control issues a real request. It is pinned to the
acceptance API. The production backend allows only its own two frontends — the
Linked Data Explorer's and the CPSV Editor's — so no documentation page can reach it
from a browser.

That split is a decision, not an accident. The Linked Data Explorer's specification declares no
`securitySchemes` and no global `security`, so every operation is
unauthenticated — including `POST /dmns/deploy`, `POST /dmns/process/deploy`
and `DELETE /cache/clear`. Those are already reachable by anything that is not
a browser, since the origin check passes requests that send no `Origin` at all;
CORS is a browser policy, not an authorization boundary. But a Send button on a
public documentation page is a different proposition from an endpoint someone
has to write a request to reach, so production stays locked to its own
frontend.

The RONL Business API's document is different on both counts. It declares three
security schemes — `bearerAuth`, a Keycloak-issued JWT that applies to every
operation by default, `mediaAggregatorKey`, and since 28 September 2026 `m2mOAuth`,
an OAuth2 client-credentials scheme for the machine-to-machine surface — so Test
Request against it needs a token for most operations. And since 30 September 2026
its acceptance `CORS_ORIGIN` includes `https://acc.iou-architectuur.open-regels.nl`,
so Test Request works from both documentation tiers.

Measured against the Linked Data Explorer's acceptance backend on 16 September 2026
(and identically again on 27 September and 4 October), varying only the
`Origin` header on `GET /v1/health`:

| `Origin` sent | Status | `Access-Control-Allow-Origin` |
|---|---|---|
| `https://iou-architectuur.open-regels.nl` | 200 | echoed |
| `https://acc.iou-architectuur.open-regels.nl` | 200 | echoed |
| `https://acc.linkeddata.open-regels.nl` | 200 | echoed |
| `http://localhost:8000` | 200 | absent |

Measured against the RONL Business API's acceptance backend on 4 October 2026:

| `Origin` sent | Status | `Access-Control-Allow-Origin` |
|---|---|---|
| `https://iou-architectuur.open-regels.nl` | 200 | echoed |
| `https://acc.iou-architectuur.open-regels.nl` | 200 | echoed (preflight 204, echoed) |
| `http://localhost:8000` | 200 | absent |

On 27 September 2026 the acceptance documentation origin's row read *absent
(preflight too)*; it changed with the `CORS_ORIGIN` update of 30 September.

Both halves of
[linked-data-explorer#145](https://github.com/sgort/linked-data-explorer/issues/145)
made the Linked Data Explorer's table possible: a disallowed origin no longer answers
`500`, and both documentation tiers are allowlisted on the acceptance App Service.

---

## The Content-Security-Policy is not enforced

!!! warning "A security header file that looks active and is not"

    `staticwebapp.config.json` at the repository root declares a CSP, and
    `connect-src` there names both acceptance backends —
    `https://acc.backend.linkeddata.open-regels.nl` and `https://acc.api.open-regels.nl`.
    **That file is not applied
    to either deployment.** Both pipelines publish with `app_location: "site"`,
    Azure Static Web Apps reads `staticwebapp.config.json` from the app artifact
    root, and `mkdocs build` never copies the file into `site/`.

    Verified 16 September 2026, and again on 27 September: neither `iou-architectuur.open-regels.nl` nor
    `acc.iou-architectuur.open-regels.nl` returns a `Content-Security-Policy` or
    `X-Frame-Options` header, and both return `Referrer-Policy: same-origin`
    where the file declares `strict-origin-when-cross-origin`.

    Tracked as
    [iou-architectuur#98](https://github.com/sgort/iou-architectuur/issues/98).

So the render and Test Request reach the backend **because no policy is
enforced**, not because one permits them. The policy already names both
hosts, so the page should keep working unchanged when the file is finally
applied — but that entry stops being cosmetic at that moment. Removing the
backend from `connect-src` under an enforced policy would blank the page, not
merely disable a button.

---

## Renderers considered

Four were trialled against the same document before Scalar was chosen. The
comparison is worth recording, because the trade it revealed is not obvious.

| Renderer | Search records contributed | Indexed text |
|---|---|---|
| neoteroi-mkdocs (build-time HTML) | 62 | 105,298 chars |
| Redoc / Swagger UI / Scalar | 1 each | ~1 KB each |

Build-time rendering wins decisively on search: it emits real HTML that MkDocs
indexes, so a schema name like `ErrorEnvelope` (at the time; the Linked Data
Explorer's errors are now RFC 9457 `Problem` objects) becomes findable through site
search. The client-side renderers contribute nothing but the page's own prose.
Scalar was chosen knowing that cost, for a presentation that reads as an API
console and for a Test Request control that build-time HTML cannot offer at all.

Two constraints found during that trial are worth keeping in mind for any future
renderer:

- **A renderer shipping its own stylesheet needs it vendored** if the CSP is
  ever enforced, since `style-src` admits `'self'`, `'unsafe-inline'` and
  `https://fonts.googleapis.com` only — no CDN such as jsDelivr.
- **The iframe-based MkDocs plugins** (`mkdocs-swagger-ui-tag`,
  `mkdocs-redoc-tag`) are a trap: they work on localhost and would be blocked in
  production by `X-Frame-Options: DENY` — again, once the header is actually
  sent.
