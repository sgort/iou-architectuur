---
scope: cross-cutting
---

# Skills & Boundaries

This page covers two things a first-time contributor needs before relying on the
[pipeline](overview.md): which capabilities are available where, and what the assistant
will and will not do without being asked first.

## User-level versus project-level

Capabilities are defined at one of two levels:

| Level | Location | Applies |
|---|---|---|
| User | `~/.claude/` | Every repository, every session |
| Project | `<repo>/.claude/` | That repository only |

Both levels carry the same three kinds of thing — **commands**, **skills**, and
**plugins** — plus, at user level, the working rules in `~/.claude/CLAUDE.md`.

The distinction is not arbitrary, and the clearest way to see it is a pair of commands
that sit on opposite sides of it.

**`/bump-release` exists three times**, once per repository, because each repository's
release process is genuinely different. `ronl-business-api` keeps its changelog as a
typed TypeScript module (`changelog-data.ts`) with a per-entry `scope` array, because a
release there can touch any combination of three independently versioned packages
(frontend, backend, public site). `linked-data-explorer` keeps a plain JSON file
(`changelog.json`) with a per-entry `scope` field, for the same reason at a smaller
scale — frontend and backend. `ttl-editor` keeps the same plain-JSON shape but drops
`scope` entirely, because it is a single-package repository with nothing to scope. Same
command name, three implementations, each shaped by what its own repository actually
needs to record. The Norm Editor repository has no `/bump-release` at all — it releases
differently — and defines no project-level commands or skills of its own.

**`/iou-document-patch` exists exactly once**, defined only in this documentation
repository, because there is one documentation site. Nothing about how it works depends
on which repository it happens to run from.

The rule that follows: a capability belongs at user level when it describes *how you
work*, and stays at project level when it depends on *what the repository is*.

This is not a theoretical distinction — it has history, twice over.

The working rules now in `~/.claude/CLAUDE.md` were promoted to user level on
2026-08-19, after the same rules had been learned independently, project by project, in
five separate repositories (`iou-architectuur`, `ttl-editor`, `linked-data-explorer`,
`ronl-business-api` and `cprmv`). Each rule was already meant generally; it had only
ever been written down project-scoped because that was where the correction happened.
Consolidating them once, at user level, was the fix for that duplication.

The same thing happened again on 2026-08-28, to a plugin. The
[`superpowers`](working-with-claude-code.md#the-plugin-set) plugin had been installed
for `ronl-business-api` alone, and was promoted to user level once it was clear the
brainstorm-plan-execute structure is a property of *how the work is done*, not of that
repository. Nothing about it depended on which repository it ran from — which is
precisely the test.

## Working boundaries

The assistant operates inside a set of recorded boundaries: things it will not do
unprompted, and approvals it will not infer from an earlier one. `~/.claude/CLAUDE.md`
is the authority for the full set — **eleven rules** as of 5 September 2026 — and is not
reproduced here in full, because a copy would drift. The set has grown twice since the
2026-08-19 consolidation and will grow again; treat any count on this page as a
snapshot, and the file as the authority. The boundaries most visible to a day-to-day
contributor:

- **Never start, stop or restart a dev server.** The contributor owns those processes.
  A shared runner (for example `npm run dev` fanning out to several packages via
  `concurrently`) means killing one process can take its siblings down with it — and an
  orphaned background process can outlive the session and collide on the next port.
- **Never self-drive a browser to verify UI.** Standing up Playwright, `chromium-cli`
  or an SSR proxy-render script to prove a frontend change works is slower and less
  reliable than asking. Run typecheck, lint and the unit tests as usual, then ask the
  contributor to look at it — they already have the app running and can confirm in
  under a minute.
- **Ask before every commit.** Approval is per commit, not inferred from an earlier
  one in the same session — an established pattern earlier does not carry forward to
  the next change.
- **Never merge or force-push a shared branch unasked.** Committing on a working
  branch when asked is fine; integrating that branch into another is a separate
  decision the contributor makes explicitly, every time.
- **Create a branch before implementing.** Integration branches (`acc`, `main`) are
  not worked on directly — direct changes there are hard to isolate and review.
- **No Claude attribution in any artifact.** Originally scoped to commit trailers,
  this was broadened in September 2026 to cover *every* artifact the assistant
  produces — pull request descriptions, issue bodies, code comments and documentation
  as well as commit messages. Each ends with its substantive content and nothing else,
  regardless of what the harness's default prompt suggests appending, and regardless of
  a mid-session reminder restating that instruction.
- **Never bypass a verification gate.** No `--no-verify`, no `SKIP=`/`HUSKY=0`, no
  disabling, renaming or editing a hook to make a command succeed. If a gate fails, the
  failure is the message: read it, fix what it names, run the command again. Where a
  gate is believed to be wrong, that is a decision to escalate, not a step to route
  around — and inspecting what a gate checks *after* disarming it is not diligence.
  This applies with particular force now that CI gates are
  [genuinely blocking](../supply-chain.md#5-the-acc-ruleset-what-makes-it-enforcement).
- **A parallel-run test failure is not a finding until it fails in isolation.** Test
  runners execute files in parallel, so a failure that appears only in a full run may
  be contention or an order dependency rather than a defect. Re-run it on its own
  before drawing a conclusion, and never disable parallelism globally to make the
  symptom go away — that diverges local runs from CI and converts a signal into
  silence.
- **No shell heredocs for long or punctuation-heavy content.** Added in September
  2026 after it bit repeatedly during releases. Changelog entries are long and full of
  quotes, apostrophes, em dashes and curly quotes, and a heredoc that trips over one
  reports `unexpected EOF while looking for matching` pointing at a line that is not
  where the problem is. The content goes to a scratchpad file instead and is spliced in
  by a short script — one that refuses to run twice, so a retry cannot duplicate the
  entry. The rule is written around `/bump-release` because that is where it bites
  every time, but it applies to any long content.

## The two custom capabilities

Two capabilities beyond the built-in ones are specific to this ecosystem. The
general-purpose plugins that apply everywhere are covered in
[Working with Claude Code](working-with-claude-code.md#the-plugin-set); these two are
IOU's own.

**`/bump-release`** cuts a release in the repository it is invoked in: it flips the
current changelog entry from upcoming to released, versions the packages the release
actually touched, and opens the pull request that lands it on the integration branch.
It is a project-level *command*, defined separately in each of `ronl-business-api`,
`linked-data-explorer` and `ttl-editor`, at `.claude/commands/bump-release.md` in each
repository — see [User-level versus project-level](#user-level-versus-project-level)
above for why three implementations are correct rather than duplicated effort. It is
invoked by name, as `/bump-release`.

Since August 2026 it no longer merges anything locally. Where a
[supply-chain gate](../supply-chain.md) protects the branch, a release must land through
a pull request that passes `audit` — which is the boundary above applied to the
assistant's own tooling rather than to a contributor.

**`/iou-document-patch`** brings this documentation site into sync with a component's
latest release, in staged fashion: analyse the component's changelog against what the
docs currently record, plan the per-perspective updates, get sign-off, apply them, and
verify. It is a *skill*, defined once in this repository at
`.claude/skills/iou-document-patch/SKILL.md`. It is invoked by name, as
`/iou-document-patch`.

Neither is documented here beyond what it is for and where it lives — read the skill
and command files themselves for how they work.

Once a change is ready to commit, [Code Standards](../code-standards.md) covers what
the repository's own tooling — lint, format and hooks — actually enforces.
