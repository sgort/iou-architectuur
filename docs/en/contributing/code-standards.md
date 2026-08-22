# Code Standards

This page covers three application repositories — CPSV Editor (`ttl-editor`), Linked
Data Explorer, and RONL Business API — that share a common tooling convention:
Husky-managed git hooks, npm workspaces, and four identically named root scripts. It
documents what their tooling actually enforces, measured from each repository's own
configuration rather than assumed to be uniform.

---

## Linting and formatting

Every repository exposes the same four commands at its root, but the shape behind them
differs — RONL Business API and Linked Data Explorer are npm workspaces fanning out
across multiple packages; CPSV Editor is a single package.

| Command | RONL Business API | Linked Data Explorer | CPSV Editor |
|---|---|---|---|
| Lint | `npm run lint` | `npm run lint` | `npm run lint` |
| Lint, fixing what it can | `npm run lint:fix` | `npm run lint:fix` | `npm run lint:fix` |
| Format | `npm run format` | `npm run format` | `npm run format` |
| Format, check only | `npm run check-format` | `npm run check-format` | `npm run check-format` |

At the root, the four names line up. Underneath, they don't. RONL Business API's root
`check-format` isn't a workspace fan-out at all — it runs `prettier --check` directly
against the whole tree (`**/*.{ts,tsx,json,md}`), so it reaches every package in one
pass regardless of what each package calls its own script. Linked Data Explorer's root
`check-format` instead runs `npm run check-format --workspaces --if-present`, which
invokes *whichever workspace defines a script of that exact name* and silently omits
any that don't, because `--if-present` treats a missing script as nothing to do rather
than an error.

That distinction was not academic. Linked Data Explorer's backend package used to name
its script `format:check`, not `check-format` — a one-character difference from what the
root fan-out was looking for. The root command exited 0 on every run, having quietly
checked only the frontend the whole time. The fix keeps `check-format` as the backend's
canonical name and `format:check` as an alias that delegates to it, so the workspace is
picked up under either name. The practical rule this leaves behind: if you're running a
formatter or linter by drilling into a single workspace (`npm run check-format
--workspace=@ronl/backend`, for example) rather than from the repository root, check
that package's own `package.json` for the script's actual name — don't assume it matches
the root's.

---

## Git hooks

All three repositories wire the same two hooks through Husky, and they gate the same
two things everywhere: staged-file linting and formatting on commit, full linting and
formatting on push.

- **`pre-commit`** runs `lint-staged`, formatting and linting only the files staged for
  that commit (via `prettier --write` and each affected workspace's `lint:fix`).
- **`pre-push`** runs the full lint and format-check across the repository (RONL
  Business API's `pre-push` also rebuilds the shared package and runs a type check
  first, since its packages depend on it).

**None of the three repositories' git hooks run the test suite.** Neither `pre-commit`
nor `pre-push` invokes `npm test` anywhere. A passing hook is not evidence your change
didn't break a test — only CI, or running the suite yourself, tells you that.

---

## CI

Every deploy pipeline that has something to test now runs the suite before it builds,
and a failing test blocks the deploy. That has only been true since 20 August 2026 —
before then CI and the hooks left the same gap, and RONL Business API's public-site
package had the only real test gate anywhere.

**RONL Business API** — six workflows, one acc/prod pair per package:

| Workflow pair | Lint | Type-check | Tests | Notes |
|---|:---:|:---:|:---:|---|
| `azure-backend-*` | ✅ | – | ✅ | Builds and uploads a deployment artifact; it does not deploy |
| `azure-frontend-*` | ✅ | – | ✅ | Also runs `npm run test:perf`, the wall-clock budget, as a step of its own |
| `azure-publicsite-*` | ✅ | ✅ | ✅ | Its build additionally gates on a prerender and a bundle-cleanliness check |

The frontend's performance budget runs separately because it asserts wall-clock time,
which means nothing while 133 test files compete for cores — see
[The performance budget](../ronl-business-api/developer/testing/overview.md#the-performance-budget).

**Linked Data Explorer** — six workflows. Both backend and both frontend workflows run
lint and then the suite before building. The two `ropa-site` workflows run neither, and
correctly so: that package is a static `index.html` plus a `staticwebapp.config.json`,
with no build and no test script to run.

**CPSV Editor** — both Azure Static Web Apps workflows, `acc` and `main` alike, run
`npm ci`, `npm run lint` and `npm run test:ci` ahead of the deploy action.

None of this replaces running the suite yourself before opening a merge request — and a
green local run is weaker evidence than it looks. RONL Business API's first gated run
failed on test files that had been latently broken for weeks: ts-jest caches type
diagnostics per file, so a warm local cache kept skipping the check that CI, starting
cold, performed immediately. Clearing the cache reproduced it at once.

---

## Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/), as
described in [Contributing → Commit your changes](index.md#5-commit-your-changes). None
of the three repositories above enforce this mechanically — Norm Editor does: its
`commit-msg` and `pre-push` git hooks reject any commit whose subject line does not
match the Conventional Commits pattern, so a non-conforming message there hard-fails
rather than merely failing review.

**No Claude attribution trailers.** If you're using an AI assistant to help prepare a
commit, the commit message ends with its substantive body and nothing else —
`Co-Authored-By` and similar trailers are not added, regardless of what a tool's default
template suggests appending. This applies whether the change came from Claude Code, the
`superpowers` plugin, or any other assistant.

---

## Testing

Each application repository documents its own testing setup, and this page doesn't
repeat it, because counts and commands there go stale the moment a suite grows:

- [CPSV Editor — Testing](../cpsv-editor/developer/testing.md)
- [Linked Data Explorer — Testing](../linked-data-explorer/developer/testing.md)
- [RONL Business API — Testing](../ronl-business-api/developer/testing/overview.md)

New code is expected to arrive with tests written red/green — the failing test first,
watched to fail for the right reason, then the minimum code to pass. For the mechanics
of that cycle, see
[Working with Claude Code](development-workflow/working-with-claude-code.md) rather than
this page.
