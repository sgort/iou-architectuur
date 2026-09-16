---
scope: cross-cutting
---

# OpenAPI Rendering

How the [API Specification](../../linked-data-explorer/reference/api-specification.md)
page turns a component's OpenAPI document into a browsable reference, what it
depends on at run time, and which of those dependencies are load-bearing.

This page exists so the specification page itself can stay what a reader came
for — the reference — rather than opening with four boxes of operational
detail.

---

## The arrangement

The page declares two script tags and nothing else. Scalar
(`@scalar/api-reference`, pinned) is loaded from `cdn.jsdelivr.net`, and a
configuration element tells it which document to fetch:

```html
<script
  id="api-reference"
  data-url="https://acc.backend.linkeddata.open-regels.nl/v1/openapi.json"
  data-configuration='{"layout":"classic", …,"servers":[{"url":"…/v1","description":"Acceptance"}]}'>
</script>
```

Everything below is a consequence of those two lines.

### Live, not stored

The document is fetched from the backend **on every page load**. There is no
committed copy.

That is deliberate while
[linked-data-explorer#129](https://github.com/sgort/linked-data-explorer/issues/129)
is in progress: it covers roughly 66 route handlers against the 24 paths
described today, so a snapshot would be stale within days, and every backend
deploy would owe the documentation site a fetch, a commit, a build and a
promotion.

The cost is **reproducibility**. The page cannot be replayed as it looked last
week, and it shows nothing at all if the backend is unreachable. When the
specification settles, a stored copy under `docs/assets/openapi/` becomes the
better arrangement — reviewable in a diff, and immune to a backend deploy. The
switch back is a one-line change to `data-url` plus the file.

### Provenance comes from a second endpoint

`/v1/openapi.json` carries no version of its own. `/v1/health` reports the
version and build of the very service that just served the document, so a small
script reads it and renders the banner at the top of the page:

```
Rendered from acceptance · version 2026.09.4 · build 6a9b7fa · #157 · read … UTC
```

If that fetch fails the banner stays hidden and the reference still renders. It
degrades to nothing, never to an error.

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

### The CORS asymmetry

`/v1/openapi.json` is a **public mount** served with
`Access-Control-Allow-Origin: *`, entirely separate from the `CORS_ORIGIN`
allowlist that governs every other route. So the render works from any origin
and does not depend on either documentation tier being allowlisted — a third
party could render the same document.

`/v1/health` does **not** get that treatment. It goes through the allowlist.
Both deployed documentation tiers are on it; `localhost` is not, which is why
the provenance banner is absent under `mkdocs serve` and present on the
deployed site.

### Test Request targets acceptance, deliberately

Scalar's **Test Request** control issues a real request. It is pinned to the
acceptance API, and the production backend still refuses every origin but its
own frontend.

That split is a decision, not an accident. The specification declares no
`securitySchemes` and no global `security`, so every operation is
unauthenticated — including `POST /dmns/deploy`, `POST /dmns/process/deploy`
and `DELETE /cache/clear`. Those are already reachable by anything that is not
a browser, since the origin check passes requests that send no `Origin` at all;
CORS is a browser policy, not an authorization boundary. But a Send button on a
public documentation page is a different proposition from an endpoint someone
has to write a request to reach, so production stays locked to its own
frontend.

Measured against the acceptance backend on 16 September 2026, varying only the
`Origin` header on `GET /v1/health`:

| `Origin` sent | Status | `Access-Control-Allow-Origin` |
|---|---|---|
| `https://iou-architectuur.open-regels.nl` | 200 | echoed |
| `https://acc.iou-architectuur.open-regels.nl` | 200 | echoed |
| `https://acc.linkeddata.open-regels.nl` | 200 | echoed |
| `http://localhost:8000` | 200 | absent |

Both halves of
[linked-data-explorer#145](https://github.com/sgort/linked-data-explorer/issues/145)
made that possible: a disallowed origin no longer answers `500`, and both
documentation tiers are allowlisted on the acceptance App Service.

---

## The Content-Security-Policy is not enforced

!!! warning "A security header file that looks active and is not"

    `staticwebapp.config.json` at the repository root declares a CSP, and
    `connect-src` there names the acceptance backend. **That file is not applied
    to either deployment.** Both pipelines publish with `app_location: "site"`,
    Azure Static Web Apps reads `staticwebapp.config.json` from the app artifact
    root, and `mkdocs build` never copies the file into `site/`.

    Verified 16 September 2026: neither `iou-architectuur.open-regels.nl` nor
    `acc.iou-architectuur.open-regels.nl` returns a `Content-Security-Policy` or
    `X-Frame-Options` header, and both return `Referrer-Policy: same-origin`
    where the file declares `strict-origin-when-cross-origin`.

    Tracked as
    [iou-architectuur#98](https://github.com/sgort/iou-architectuur/issues/98).

So the render and Test Request reach the backend **because no policy is
enforced**, not because one permits them. The policy already names the right
host, so the page should keep working unchanged when the file is finally
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
indexes, so a schema name like `ErrorEnvelope` becomes findable through site
search. The client-side renderers contribute nothing but the page's own prose.
Scalar was chosen knowing that cost, for a presentation that reads as an API
console and for a Test Request control that build-time HTML cannot offer at all.

Two constraints found during that trial are worth keeping in mind for any future
renderer:

- **A renderer shipping its own stylesheet needs it vendored** if the CSP is
  ever enforced, since `style-src 'self'` admits no CDN.
- **The iframe-based MkDocs plugins** (`mkdocs-swagger-ui-tag`,
  `mkdocs-redoc-tag`) are a trap: they work on localhost and would be blocked in
  production by `X-Frame-Options: DENY` — again, once the header is actually
  sent.
