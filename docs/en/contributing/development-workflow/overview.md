---
scope: cross-cutting
---

# Development Workflow

This section describes how the maintainers actually build IOU Architecture features —
day to day, AI-assisted, and distinct from the [human contribution process](../index.md)
that outside contributors follow. If you read only one page in this subsection, read
this one.

The pipeline, stage by stage:

## 1. Design

For medium-to-large features where fundamental UX is at stake, design comes first, in
Claude Design. Small changes skip this stage entirely and go straight to implementation.

## 2. Handoff

A design leaves Claude Design as a handoff package: the design itself, standalone HTML,
screenshots, a README, and a PROMPT. The package is briefing material for the next
stage, not something that enters the repository as-is.

## 3. Implementation

Implementation happens in Claude Code, with `claude-mem` capturing session memory by
default. Depending on the size of the change, work proceeds either inline or through the
`superpowers` plugin. Either way it follows **red/green TDD**: the failing test comes
first, then the minimum code needed to make it pass.

## 4. Release

A release is cut with `/bump-release`, a command defined per repository — each component
keeps its own version, tailored to its own changelog format.

**A release lands through a pull request, not a local fast-forward.** Where a
[supply-chain gate](../supply-chain.md) is in place — CPSV Editor and RONL Business API
today — the `acc` branch requires a pull request and a passing `audit` check with no
bypass actors, so the older flow of merging `acc` locally and pushing it is rejected
outright: a locally created bump commit has never been through CI. Merging the pull
request *is* the push, and triggers the acceptance deploy.

A release pull request is **merged, never squashed and never rebased** — the changelog
entry cites each commit by SHA, and both alternatives rewrite those hashes. Squashing
collapses the commits into one new commit; rebasing replays them as new commits,
deceptively, since it preserves the commit count while replacing every hash. Either
orphans every citation in the entry.

Since September 2026 that is enforced by repository settings rather than by
remembering: all three repositories allow merge commits only, with
`delete_branch_on_merge` enabled. GitHub's default button is *Squash and merge*, so
without the setting one absent-minded click would orphan a release's entire entry. A
side effect is that Renovate's dependency pull requests land as merge commits too,
which costs nothing — the changelog range already excludes merge commits, and the
underlying update commit is what an entry should name.

## 5. Documentation

Once a component has shipped, `/iou-document-patch` — defined once, in this
documentation repository — brings these docs into sync with the new release.

## Where to go next

This page is a map, not the territory. The rest of the subsection covers each stage in
more depth:

- **[Design & Handoff](design-and-handoff.md)** — when a feature warrants Claude
  Design, and what the handoff package contains
- **[Working with Claude Code](working-with-claude-code.md)** — `claude-mem`, inline
  work versus the `superpowers` plugin, and red/green TDD in practice
- **[Skills & Boundaries](skills-and-boundaries.md)** — user-level versus
  project-level capabilities, the plugin set, and the working rules every session
  follows
- **[Code Standards](../code-standards.md)** — what lint, format, hooks and CI
  actually enforce, measured per repository
- **[Supply-Chain Pinning](../supply-chain.md)** — what makes a CI check a *gate*,
  and what the gate deliberately does not protect

For the process outside contributors follow instead, see the
[Contributing overview](../index.md).
