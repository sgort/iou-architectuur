# Working with Claude Code

This page covers the third stage of the [pipeline](overview.md): implementation itself,
once a change (with or without a handoff package behind it) reaches Claude Code.

## Session memory

`claude-mem` runs by default and captures session memory as work proceeds. Its viewer
runs at `http://localhost:37780`. The port is configurable via
`CLAUDE_MEM_WORKER_PORT` in `~/.claude-mem/settings.json` — if you have changed it
locally, use your own value instead.

## Inline versus superpowers

Small, well-understood changes proceed inline. Multi-step work goes through the
`superpowers` plugin instead, which structures it as brainstorming a design, writing a
plan, and executing it with review between tasks.

The choice is made by the size and uncertainty of the work, not by preference. A change
whose steps and outcome are already clear does not need a plan written for it; a change
where either is still unclear benefits from `superpowers` slowing it down.

## Red/green test-driven development

Implementation, inline or via `superpowers`, follows red/green TDD. The cycle:

1. Write the failing test first.
2. Run it and watch it fail, for the reason you expect.
3. Write the minimum code that makes it pass.
4. Run it again.
5. Refactor with the test as the safety net.

Step 2 is the one most often skipped, and the only one that actually proves anything. A
test that has never been seen to fail proves nothing: it may be asserting something
already true, or nothing at all. If a test passes before the implementation exists, it
is testing something other than what it claims — and the fix is to correct the test,
not to celebrate an early pass.

The `superpowers` plugin structures work this way by default, so a contributor using it
follows the cycle whether or not they think of it as TDD. Where it does not apply, say
so plainly rather than forcing it: a documentation change has no failing test to write,
and pretending otherwise is cargo cult.

## What this means for a contributor

Within all of this, the assistant works inside recorded boundaries — rules about what it
will do unprompted and what it always asks first. [Skills & Boundaries](skills-and-boundaries.md),
the next page in this subsection, covers those boundaries in detail.
