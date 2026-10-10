# CPRMV API — screenshots to capture

*A running record across syncs, newest first. Last reviewed for v0.4.2 on
10 October 2026 — **nothing outstanding, and nothing requested**.*

Real screenshot files live in **`docs/assets/screenshots/`** (language-neutral,
served at the site root). Docs reference them as
`../../assets/screenshots/<file>` inside a `<figure markdown>` block.

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
