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

This is not a theoretical distinction — it has history. The working rules now in
`~/.claude/CLAUDE.md` were promoted to user level on 2026-08-19, after the same rules
had been learned independently, project by project, in five separate repositories
(`iou-architectuur`, `ttl-editor`, `linked-data-explorer`, `ronl-business-api` and
`cprmv`). Each rule was already meant generally; it had only ever been written down
project-scoped because that was where the correction happened. Consolidating them once,
at user level, was the fix for that duplication.

## Working boundaries

The assistant operates inside a set of recorded boundaries: things it will not do
unprompted, and approvals it will not infer from an earlier one. `~/.claude/CLAUDE.md`
is the authority for the full set — nine rules at the time of writing — and is not
reproduced here in full, because a copy would drift. The boundaries most visible to a
day-to-day contributor:

- **Never start, stop or restart a dev server.** The contributor owns those processes.
  A shared runner (for example `npm run dev` fanning out to several packages via
  `concurrently`) means killing one process can take its siblings down with it — and an
  orphaned background process can outlive the session and collide on the next port.
- **Ask before every commit.** Approval is per commit, not inferred from an earlier
  one in the same session — an established pattern earlier does not carry forward to
  the next change.
- **Never merge or force-push a shared branch unasked.** Committing on a working
  branch when asked is fine; integrating that branch into another is a separate
  decision the contributor makes explicitly, every time.
- **Create a branch before implementing.** Integration branches (`acc`, `main`) are
  not worked on directly — direct changes there are hard to isolate and review.
- **No Claude attribution trailers in commit messages.** Commit messages end with
  their substantive body and nothing else, regardless of what the harness's default
  prompt suggests appending.

## The two custom capabilities

Two capabilities beyond the built-in ones are specific to this ecosystem.

**`/bump-release`** cuts a release in the repository it is invoked in: it flips the
current changelog entry from upcoming to released, versions the packages the release
actually touched, and lands the result on the integration branch. It is a
project-level *command*, defined separately in each of `ronl-business-api`,
`linked-data-explorer` and `ttl-editor`, at `.claude/commands/bump-release.md` in each
repository — see [User-level versus project-level](#user-level-versus-project-level)
above for why three implementations are correct rather than duplicated effort. It is
invoked by name, as `/bump-release`.

**`/iou-document-patch`** brings this documentation site into sync with a component's
latest release, in staged fashion: analyse the component's changelog against what the
docs currently record, plan the per-perspective updates, get sign-off, apply them, and
verify. It is a *skill*, defined once in this repository at
`.claude/skills/iou-document-patch/SKILL.md`. It is invoked by name, as
`/iou-document-patch`.

Neither is documented here beyond what it is for and where it lives — read the skill
and command files themselves for how they work.
