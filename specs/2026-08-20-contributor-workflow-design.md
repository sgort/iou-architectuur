# Contributor workflow documentation & homepage restructure

**Date:** 2026-08-20
**Status:** awaiting review
**Scope:** documentation only — no component code changes.

> Placed at the repository root rather than under `docs/`, because `docs/` is the
> MkDocs source tree: a Markdown file there that is not in the `nav` produces a
> "not included in the nav configuration" warning on every build.

---

## Problem

Two gaps, one cause.

**The site does not describe how the work is actually done.** Nothing anywhere
mentions Claude Design, Claude Code, `claude-mem`, `superpowers`, or the two
custom skills this ecosystem depends on. A first-time contributor reading
`contributing/index.md` finds a six-step process — open an issue, fork, branch,
change, commit, open a merge request — that describes a purely human workflow.
That path is still correct for an outside contributor, but it is not how
features get built by the people building them.

**The homepage has accumulated.** Ten top-level sections, added one at a time,
with no organising idea. Documentation Status and Contributing rarely reach the
same reader, yet sit in one undifferentiated list.

A third, smaller gap: `contributing/code-standards.md` is a 19-line "Coming
Soon" stub with a nav entry.

---

## Decisions

| # | Question | Decision |
|---|---|---|
| 1 | Relationship to the existing six-step process | **Two tracks.** The AI-assisted workflow is how the core team works; fork-and-MR remains the route for outside contributors. Both documented, clearly labelled. |
| 2 | Homepage | **Restructure around three questions** — what is this / what's its state / how do I work on it. Sections are grouped, not deleted. |
| 3 | Depth of the workflow docs | **A subsection of four pages** under `contributing/`. |
| 4 | `code-standards.md` | **Folded into this work** — written for real from verified facts, kept at its existing path and nav position. |

### A correction carried into this spec

The option text that won decision 2 said reference material could move off the
homepage into Contributing "where it is already half-documented". **That was
wrong**, and the design does not do it. The homepage's *Technology Stack* is the
**ecosystem's** stack — Keycloak, Operaton, Node, React, PostgreSQL, Redis, with
licences — an open-source credentials statement. `contributing/doc-architecture/
technology-stack.md` is the **documentation site's** stack — MkDocs, Material,
the i18n plugin. Merging them would conflate the product with the site that
documents it. Both stay where they are.

---

## Design

### 1. Homepage — three questions

Same sections, grouped under three signposted headings:

| Question | Sections, in order |
|---|---|
| **What is this?** | What is IOU Architecture · Architecture Overview · Ecosystem Components · Technology Stack · Standards Compliance |
| **What is the state of it?** | Documentation Status · What's New · How this documentation is maintained |
| **How do I work on it?** | **Development workflow** *(new)* · Contributing · Quick Links |

The new *Development workflow* section is a summary of roughly eight lines — one
sentence per pipeline stage — ending in a link to the subsection. It does not
duplicate the subsection's content.

Nothing is deleted from the homepage. The value is the grouping.

### 2. `contributing/development-workflow/` — four pages

**`overview.md`** — the pipeline end to end, in one pass:

> Claude Design for medium-to-large features that need fundamental UX → a design
> handoff package → implementation in Claude Code, red/green TDD → release via
> `/bump-release` → documentation via `/iou-document-patch`.

A newcomer can stop after this page and understand the shape. Each stage links
to its own page or to the relevant skill.

**`design-and-handoff.md`** — when a feature warrants Claude Design rather than
going straight to code: medium-to-large scope, fundamental UX at stake. Then the
handoff package and what it contains — the design, standalone HTML, screenshots,
a README, and a PROMPT. Two rules learned in practice belong here:

- The handoff folder's own files are the **single source of truth** for that
  piece of work — not a same-named or similar-looking file already in the app.
  The two are easy to confuse and only the handoff copy is the deliverable.
- The handoff folder is **briefing material, not repo content**. Port what it
  specifies into the real source files; do not commit the folder.

**`working-with-claude-code.md`** — `claude-mem` runs by default, capturing
session memory; the viewer is at `http://localhost:37780` (verified:
`CLAUDE_MEM_WORKER_PORT` is `37780` in `~/.claude-mem/settings.json`). Then the
choice between inline coding for small changes and the `superpowers` plugin for
multi-step work — brainstorming into a design, a written plan, then execution
with review between tasks.

**`working-with-claude-code.md`** also covers **red/green test-driven
development**, which is how implementation proceeds here: write the failing
test first, watch it fail for the reason expected, write the minimum that makes
it pass, then refactor. The page should be explicit that seeing the test fail is
not a formality — a test that has never failed proves nothing, and a test that
passes before the implementation exists is testing something other than what it
claims. Note that the `superpowers` plugin structures work this way by default,
so a contributor using it follows the cycle whether or not they think of it as
TDD.

**`skills-and-boundaries.md`** — the first-time contributor explainer. See below.

### 3. User vs project level — the explainer

Verified on this machine, 2026-08-20:

| Level | Location | Holds | Applies |
|---|---|---|---|
| **User** | `~/.claude/` | `CLAUDE.md` (9 rules); plugins `superpowers` and `claude-mem` | Every repository, every session |
| **Project** | `<repo>/.claude/` | `iou-document-patch` (skill, docs repo only); `bump-release` (command, three repos) | That repository only |

Actual distribution:

| Repository | Project-level capability |
|---|---|
| `iou-architectuur` | skill `iou-document-patch` |
| `ronl-business-api` | command `bump-release` |
| `linked-data-explorer` | command `bump-release` |
| `ttl-editor` | command `bump-release` |
| `editor` (Norm Editor) | none |

**The example that teaches the distinction:** `/bump-release` exists three times,
once per repository, because each repository's changelog is genuinely different —
one is a JSON array, one a JSON object with a per-entry `scope` field, one a
TypeScript module. Same command name, three implementations, because the thing
it operates on differs. `/iou-document-patch` exists exactly once, because there
is one documentation site.

The rule that follows: **a capability goes to user level when it describes how
you work; it stays at project level when it depends on what the repository
is.** Say plainly that the nine user-level rules were promoted from project level
during a session on 2026-08-19, after the same rule had been independently
re-learned in four separate repositories.

**The boundaries, stated as why rather than what.** Each came from a real
correction, and a newcomer needs the reason or the rule reads as arbitrary. Cover
at minimum: never start, stop or restart a dev server; ask before every commit;
never merge or force-push a shared branch unasked; branch before implementing;
no Claude attribution trailers in commit messages. Point to
`~/.claude/CLAUDE.md` as the authority rather than restating all nine in full.

### 4. `code-standards.md` — written from measured facts

Replaces the "Coming Soon" stub. Stays at its current path and nav position.

Everything below was measured across the four repositories during 2026-08-19 and
must be re-verified before publication rather than copied from this spec:

- **Per-repo commands** — lint, lint:fix, format, and the format-check command,
  noting that its *name* differs between repositories (`check-format` versus
  `format:check`), which has already caused one real defect where a root script
  silently skipped a workspace.
- **What the git hooks actually gate.** In every repository examined,
  `pre-commit` runs `lint-staged` and `pre-push` runs lint and formatting —
  **no repository's hooks run the tests.** State that plainly; a contributor who
  assumes otherwise will push a broken suite.
- **CI is uneven**, and the page should say where. In the RONL Business API only
  the public-site package has a real test gate; the frontend, its largest suite,
  has neither lint nor test in CI.
- **Commit message conventions**, including the no-attribution-trailer rule.
- **Testing expectations**, linking to each component's own `developer/testing`
  page rather than repeating figures that would go stale.

### 5. Two tracks in `contributing/index.md`

A short fork near the top of "How to Contribute", sending the reader one of two
ways:

- **Core team / maintainer** → the development-workflow subsection.
- **Outside contributor** → the existing six-step fork-and-MR path, which stays
  exactly as written.

Neither is presented as the lesser route. The fork-and-MR path is the correct
one for someone without this toolchain, and must not read as a consolation.

### 6. i18n and mechanics

- EN substantive; NL placeholders in the house pattern for all four new pages,
  plus one for the rewritten `code-standards.md` if its headings change.
  **Verified 2026-08-20:** every existing page under `docs/nl/contributing/` is
  a placeholder, none a real translation — so no Dutch prose is owed here, only
  mirrored empty headings.
- `component:` front matter does **not** apply — these are site-level pages, not
  component pages, so they carry no metadata header and show no version.
  **Verified 2026-08-20:** no existing page under `docs/en/contributing/`
  carries front matter, so this follows the section's own convention rather
  than inventing one.
- `mkdocs.yml` nav gains a `Development Workflow` subgroup under Contributing,
  with the four pages. Nested subgroup leaves sit at **8 spaces**.

---

## Out of scope

- Any change to component documentation.
- Rewriting `contributing/doc-architecture/*`.
- Documenting Claude Design's internals — this describes *when and what to hand
  off*, not how the tool works.

---

## Verification

- `venv/Scripts/mkdocs.exe build` — exit 0, zero warnings.
- The absolute-link sweep prints nothing.
- Every command, path and port quoted on the new pages re-verified against the
  machine at write time, not copied from this spec.
- Homepage renders three group headings with every existing section still
  present and reachable.

---

## Open items

None blocking.
