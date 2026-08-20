# Working with Claude Code

This page covers the third stage of the [pipeline](overview.md): implementation itself,
once a change (with or without a handoff package behind it) reaches Claude Code.

## Session memory

[`claude-mem`](https://github.com/thedotmack/claude-mem) runs by default and captures
session memory as work proceeds. Its viewer
runs at `http://localhost:37780`. The port is configurable via
`CLAUDE_MEM_WORKER_PORT` in `~/.claude-mem/settings.json` — if you have changed it
locally, use your own value instead.

## Inline versus superpowers

Small, well-understood changes proceed inline. Multi-step work goes through the
[`superpowers`](https://github.com/obra/superpowers) plugin instead, which structures it
as brainstorming a design, writing a plan, and executing it with review between tasks.

The choice is made by the size and uncertainty of the work, not by preference. A change
whose steps and outcome are already clear does not need a plan written for it; a change
where either is still unclear benefits from `superpowers` slowing it down.

## Subagent-driven development

Once a plan exists, it is executed one task at a time, and each task goes to a **fresh
subagent** rather than continuing in the session that wrote the plan. The subagent
receives a brief containing only what its own task needs — the files, the exact values,
the constraints that bind it — and none of the conversation history behind it.

After each task, a **separate reviewer** reads the resulting diff and checks two things:
that the task did what the plan specified, and that the result is good work on its own
terms. The implementer's own self-review does not replace this. When the reviewer finds
something, a fix round follows and the review is repeated, scoped to the fix. When every
task is done, one broader review reads the whole branch at once, which is the only stage
that can catch the things no single task could see — a page contradicting another page,
a reader's route through the result, a claim that drifted.

Progress is recorded in a **ledger file**, not only in the conversation, because
conversation memory does not survive being compacted. The ledger names every commit and
every decision taken along the way, so work can resume accurately after a break.

Two properties make this worth the overhead:

- **Context isolation.** An implementer that never sees the preceding twenty tasks
  cannot be distracted or misled by them, and the reviewing agent has no stake in the
  implementation it is judging.
- **The brief is not the authority.** Where a brief and the source disagree, the source
  wins and the implementer is expected to say so. During the work that produced this
  subsection, five separate briefs turned out to be wrong and were correctly overridden
  from what was actually on disk. That is the intended behaviour, not insubordination.

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
