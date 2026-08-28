# Working with Claude Code

This page covers the third stage of the [pipeline](overview.md): implementation itself,
once a change (with or without a handoff package behind it) reaches Claude Code.

## The plugin set

Six plugins are installed and enabled at **user level**, so they apply in every
repository and every session. They come from three marketplaces: Anthropic's
`claude-plugins-official`, and one each for `claude-mem` and `understand-anything`.

| Plugin | Version | What it contributes |
|---|---|---|
| [`claude-mem`](https://github.com/thedotmack/claude-mem) | 13.16.1 | Cross-session memory: observations captured as work proceeds, searchable later. Also supplies the planning and execution skills below |
| [`superpowers`](https://github.com/obra/superpowers) | 6.3.0 | The brainstorm → plan → execute structure for multi-step work, and a TDD skills library |
| [`understand-anything`](https://github.com/Lum1104/Understand-Anything) | 2.7.6 | Builds a navigable knowledge graph of a codebase — architecture, domains, guided tours, diff analysis |
| `github` | — | The official GitHub MCP server: issues, pull requests, reviews, repository search |
| `semgrep` | 2.1.4 | Scans generated code for security findings — SAST, secrets, and supply-chain |
| `typescript-lsp` | 1.0.0 | TypeScript/JavaScript language server: go-to-definition, find references, error checking |

Two notes on that table, because both are easy to get wrong:

- **`superpowers` used to be project-scoped.** It was installed only for
  `ronl-business-api` and was promoted to user level on 2026-08-28, on the same
  reasoning that moved the working rules to `~/.claude/CLAUDE.md` — it describes *how
  you work*, not *what the repository is*. See
  [Skills & Boundaries](skills-and-boundaries.md#user-level-versus-project-level).
- **`typescript-lsp` needs `typescript-language-server` on the `PATH`, and it resolves
  `typescript` from the workspace — not globally.** Install the server with
  `npm install -g typescript-language-server`. Do **not** add `typescript` to that
  command: npm now resolves it to 7.x, the native rewrite, which ships `tsc` only —
  no `tsserver.js`, no `typescript.js`, and no `tsserver` bin. The language server
  cannot use it, and the failure surfaces as
  `Could not find a valid TypeScript installation`. The working arrangement is the
  server installed globally, plus a `typescript` package carrying `lib/tsserver.js`
  in the repository you have **open** — the workspace root is the session's working
  directory, not wherever the file lives. Measured on 28 August 2026:
  `ronl-business-api` and `linked-data-explorer` both have 5.9.3, `ttl-editor` has
  4.9.5 via `react-scripts`; the Norm Editor has no `typescript` dependency, and this
  documentation repository is Python/MkDocs, so the plugin does nothing in either.

`semgrep` deserves a specific mention: it is the assistant-side counterpart to the
[supply-chain gate](../supply-chain.md) in CI. One scans what is being written, the
other gates what the pipeline executes — and neither substitutes for the other.

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
