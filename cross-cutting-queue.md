# Cross-cutting queue

What a component sync noticed but did not act on, waiting for the weekly Sunday
pass over `docs/en/contributing/**`.

**Why this file exists.** Until 20 September 2026 every component sync carried the
cross-cutting re-check with it. That made a sync too large to finish in one
sitting, and it meant the contributing pages were re-read only when a component
happened to ship. The two halves now run on different cadences — but a component
sync still *reads* the changelog that falsifies a contributing page, and that
observation is worth more on the day it is made than a week later, reconstructed.
So a sync records it here instead of acting on it.

**The contract.**

- A component sync **appends** one entry per release range it documents, with one
  bullet per cross-cutting fact: what changed, the evidence (the changelog entry,
  or the source file and what it says), and the page it bears on. If a release
  surfaced nothing cross-cutting, it writes that sentence with the date — a silent
  no-op cannot be told apart from a forgotten step.
- A component sync **never** edits a contributing page and **never** refreshes a
  `verified:` stamp. Both assert a re-check that did not happen.
- The weekly pass **verifies each entry against source** — an entry is a lead, not
  a finding — then strikes it, in the same commit as the corrections it produced.
  Anything it cannot verify stays, with a note saying why.

## Pending

Two items remain after the weekly pass of 27 September 2026; everything queued on 24 and 26 September
was verified against source at `a7fe76f` / `0143ea2` / `3c44b9e` and drained (see the table below).

### 27 September 2026 — carried over from the weekly pass

1. **`check-previews.sh` strips the carriage returns `az` writes on Windows — `acc` only.**
   Evidence: ronl-business-api `80e34a2`, merged as `3c44b9e` (#245); not on `main` (`2443adc`).
   Bears on: `the-gitlab-mirror.md` and wherever `check-previews` is described. Document it after the
   promotion that carries it, not before. (Was 26 September RONL Business API item 11.)

2. **A component page repeats a claim the weekly pass corrected on `openapi-rendering.md` — for the next
   Linked Data Explorer sync, not a contributing page.**
   Evidence: `docs/en/linked-data-explorer/reference/api-specification.md`'s leading HTML comment says
   `/v1/openapi.json` "carries no version of its own". It does, since linked-data-explorer `31e7c9f`
   (15 September 2026): `info.version` is `2026.09.8` at `0143ea2`. The weekly pass may not edit a
   component page, so the correction waits for that component's sync.

## Drained

| Pass | Entries drained | Where they landed |
|---|---|---|
| 20 September 2026 | — | The first weekly pass predates this queue: the cross-cutting re-check ran inside the RONL Business API sync to v2026.09.9, which is the run that split the two halves apart |
| 27 September 2026 | All of 24 September LDE (1–10) and RBA (1–15); all of 26 September CPSV (1–7), LDE (1–11) and RBA (1–10, 12). LDE-26 #11 (Windows `test:scripts`) is a tooling defect, filed as iou-architectuur#105 item 5 rather than documented; RBA-24 #11 (preview opt-in) is documented on the component's own `cicd.md` and `backend-development.md`, and no contributing page contradicts it; LDE-24 #4 settled by reading the four App Services from Azure (LDE `NODE\|24-lts`, RBA `NODE\|22-lts`) | `supply-chain.md`, `dependency-scanning.md`, `controls.md`, `code-standards.md`, `branch-protection.md`, `coverage-floor.md`, `build-provenance.md`, `the-gitlab-mirror.md`, `index.md`, `ictu-dependency-guideline.md`, `ci-posture-deck.md`, `development-workflow/*`, `doc-architecture/*`; source defects to iou-architectuur#105 items 8–18 |
