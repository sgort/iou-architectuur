---
scope: cross-cutting
verified:
  date: 2026-10-04
  against:
    RONL Business API: "5c6e716"
---

# Design & Handoff

This page covers the first two stages of the [pipeline](overview.md): deciding whether
a feature needs Claude Design at all, and what crosses over into implementation once it
does.

## When to use Claude Design

Claude Design comes first for medium-to-large features where the fundamental UX is at
stake — where the shape of the interaction itself is still an open question. A bug fix,
a copy change, or a new field on an existing form goes straight to implementation: the
interaction already has a shape, and the change does not alter it.

The test is not how large the change is in lines of code. A large change that fits an
established pattern skips design; a small change that introduces a genuinely new
interaction does not.

## The handoff package

A design leaves Claude Design as a handoff package, not as code. It contains:

- the design itself, as standalone HTML, with screenshots
- a README
- a PROMPT for Claude Code
- a `reference/` folder of the design's own source files
- often, architecture notes

Two rules govern how a handoff package is used, both learned in practice.

**The handoff folder's files are the single source of truth** for that piece of work —
not a same-named or similar-looking file already in the application. The two often
share a shape and a plausible location, and mistaking one for the other means designing
against the wrong data.

**The handoff folder is briefing material, not repository content.** Port what it
specifies into the real source files and leave the folder untracked, or remove it
before the final commit. It has done its job once implementation starts; it does not
belong in the commit history alongside it.

An untracked folder is still in the working tree, though, where a whole-tree format check
reaches it. **The RONL Business API keeps `*-handoff/` out of Prettier**: since
29 September 2026 its `.prettierignore` lists the pattern, so `format` does not rewrite
the design team's files and `check-format` — which runs in `pre-push` — does not fail on
them. One handoff folder is nevertheless tracked there: `docs/pa-demo-social-handoff/`,
fourteen files committed on 25 August 2026, before that ignore existed. The CPSV Editor
and the Linked Data Explorer track no handoff folder and have no such ignore entry.

From here, implementation itself is [Working with Claude Code](working-with-claude-code.md),
the next page in this subsection.
