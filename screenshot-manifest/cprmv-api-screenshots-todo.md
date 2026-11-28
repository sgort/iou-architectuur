# CPRMV API — screenshots to capture

*A running record across syncs, newest first. Last reviewed for release v2026.11.1 (vocabulary 0.4.3) at
`0c4d236` on 28 November 2026 — **nothing outstanding, and nothing requested**.*

Real screenshot files live in **`docs/assets/screenshots/`** (language-neutral,
served at the site root). Docs reference them as
`../../assets/screenshots/<file>` inside a `<figure markdown>` block.

---

## Sync `502a351` → release v2026.11.1 (`0c4d236`) — no screenshots requested

Reviewed on 28 November 2026. The release changes how `/ref` redirects and what it sends back, adds the first Semgrep triage and updates dependencies; none of it has a screen, and the pages give `/ref` as requests and answers.

---

## Sync `8f01b2b` → release v2026.11.0 (`502a351`) — no screenshots requested

Reviewed on 27 November 2026 for the first CalVer release, v2026.11.0, with the vocabulary still at 0.4.3. Nothing on screen changed: the release number shows in `/health`, which the pages give as its JSON answer, and the bill of materials is a file.

---

## Sync v0.4.3 at `d597671` → `8f01b2b` (the move to GitHub) — no screenshots requested

Reviewed on 26 November 2026 for the move to GitHub `open-regels/cprmv` and the VM deployment, in production at `8f01b2b` with no new version. Nothing on screen changed; the new VM deployment page describes the pipeline in tables and text, and `/health` is shown as its JSON answer.

---

## Sync v0.4.2 → v0.4.3 — no screenshots requested

Reviewed on 24 November 2026 for **v0.4.3**, in production (`main` `d597671`). The CPRMV pages embed no screenshots, and none of the changes needs one: the new endpoints are described by their requests and answers, and the specification's new chapters and class diagrams are linked at `/respec/` rather than copied. An interactive API reference page stays on hold: the API still sends no `Access-Control-*` headers (checked 24 November).

---

## Sync v0.4.1 → v0.4.2 — no screenshots requested

Reviewed on 10 October 2026.

**The CPRMV API documentation embeds no screenshots, and this sync adds none.** The
component is an HTTP API with no user interface of its own; its pages show requests,
responses and RDF as text, which a reader can copy. The two browsable surfaces —
FastAPI's `/docs` and the ReSpec specification at `/respec` — are generated, and a
picture of either would go stale with every release without saying anything the text
does not.

The one candidate for later is an **API Specification** page rendering
`/openapi.json` with Scalar, as the Linked Data Explorer and the RONL Business API
have. It waits for CORS on the CPRMV API
([standards/cprmv#31](https://git.open-regels.nl/standards/cprmv/-/work_items/31),
item 4), and it renders live rather than as a screenshot.
