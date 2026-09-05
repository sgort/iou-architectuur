---
scope: cross-cutting
---

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
didn't break a test — only CI, or running the suite yourself, tells you that. Since
August 2026 CI closes that gap on the way in as well as on the way out: in CPSV Editor
and RONL Business API a failing check now blocks the *merge*, not just the deploy — see
[Enforcement](#enforcement-what-blocks-a-merge) below.

---

## CI

Every deploy pipeline that has something to test now runs the suite before it builds,
and a failing test blocks the deploy. That has only been true since 20 August 2026 —
before then CI and the hooks left the same gap, and RONL Business API's public-site
package had the only real test gate anywhere.

**RONL Business API** — **nine** workflows: an acc/prod pair for each of **four**
packages, plus the supply-chain `audit`:

| Workflow pair | Lint | Type-check | Tests | Notes |
|---|:---:|:---:|:---:|---|
| `azure-backend-*` | ✅ | – | ✅ | Builds and uploads a deployment artifact; it does not deploy |
| `azure-frontend-*` | ✅ | – | ✅ | Also runs `npm run test:perf`, the wall-clock budget, as a step of its own |
| `azure-publicsite-*` | ✅ | ✅ | ✅ | Its build additionally gates on a prerender and a bundle-cleanliness check |
| `azure-pa-demo-*` | ✅ | ✅ | ✅ | Also installs Chromium and runs the Playwright E2E suite before the bundle gate |

The frontend's performance budget runs separately because it asserts wall-clock time,
which means nothing while 133 test files compete for cores — see
[The performance budget](../ronl-business-api/developer/testing/overview.md#the-performance-budget).

**Linked Data Explorer** — **seven** workflows on `acc`: six deployment workflows plus
the supply-chain `audit` gate added in v2026.08.7. Both backend and both frontend
workflows run lint and then the suite before building. The two `ropa-site` workflows run
neither, and correctly so: that package is a static `index.html` plus a
`staticwebapp.config.json`, with no build and no test script to run.

Unlike the other two, **the Linked Data Explorer's CI does deploy its backend** — the
backend workflows end in `azure/webapps-deploy`, where RONL Business API's end in an
uploaded artifact that a developer deploys by hand. Its backend workflows trigger on
push only, though, so no pull request runs the backend suite; a break surfaces on `acc`
after merge, where `npm test` gates the deploy step.

**CPSV Editor** — three workflows: two Azure Static Web Apps workflows, `acc` and `main`
alike, running `npm ci`, `npm run lint` and `npm run test:ci` ahead of the deploy action,
plus the supply-chain `audit`. Since v2026.09.0 the deploy workflows are named
**`Deploy ACC (orange-beach)`** and **`Deploy PROD (white-sky)`**; both were previously
called `Azure Static Web Apps CI/CD`, with both jobs named `Build and Deploy Job`, so a
production run was indistinguishable from an acceptance one in the Actions list, in a
pull request's checks, and in `gh run list` — telling them apart meant opening the run
and reading which API token it used. Renaming a job renames the check it reports, which
is why it was done before any deploy check is made required.

Those two workflows also skip documentation-only changes, via `paths-ignore` on
`docs/**`, `.claude/**` and `**/*.md`. The direction is deliberate: an allowlist
(`paths:`) would mean enumerating every path that affects the build, and anything
forgotten from such a list *silently skips a deploy* — a worse failure than one
unnecessary preview. RONL Business API and Linked Data Explorer can use `paths:`
because `packages/frontend/**` is a real boundary there; the CPSV Editor is a single
package with no such boundary, so copying that pattern would be the obvious move and
the wrong one.

None of this replaces running the suite yourself before opening a merge request — and a
green local run is weaker evidence than it looks. RONL Business API's first gated run
failed on test files that had been latently broken for weeks: ts-jest caches type
diagnostics per file, so a warm local cache kept skipping the check that CI, starting
cold, performed immediately. Clearing the cache reproduced it at once.

### Enforcement: what blocks a *merge*

Running a check and being able to block on it are different things, and until August
2026 these repositories only did the first. **All three** now carry a branch ruleset
named `acc supply-chain gate`, active on `refs/heads/acc` with **no bypass actors**.
All three share the two rules that matter:

- `required_status_checks` → the `audit` context must pass
- `pull_request` → a pull request is required (0 approvals; these repositories have a
  single maintainer, and GitHub does not permit self-approval)

Both rules are needed together — requiring the status check alone would still let a
direct push to `acc` sail past it. The practical effect is that **`git push origin acc`
is rejected outright** in all three repositories, including for releases and including
for the repository owner. Linked Data Explorer adopted the same ruleset in v2026.08.7;
all three are named `acc supply-chain gate` and carry zero bypass actors. They are not
identical in shape, though: only the Linked Data Explorer's also blocks branch deletion
and non-fast-forward pushes.

Merge strategy is enforced by repository settings rather than by convention: all three
disable squash and rebase merges, leaving merge commits only, with
`delete_branch_on_merge` enabled. Both alternatives rewrite commit hashes — rebase
deceptively so, since it preserves the commit count — and a changelog entry that cites
commits by SHA is orphaned either way.

### Supply-chain hardening

Alongside the test gate, all three application repositories — CPSV Editor (the pilot,
v2026.08.2), RONL Business API, and Linked Data Explorer (v2026.08.7) — have
adopted a common set of pipeline controls: every `uses:` reference pinned to a commit
digest rather than a tag, `permissions: contents: read` as the workflow default,
`persist-credentials: false` on checkout, a blocking zizmor `audit` job, and Renovate
maintaining the digests under a 14-day cooldown with a no-cooldown lane for security
advisories. What *cannot* be pinned is written down in each repository's
`SECURITY-PIPELINE.md` rather than glossed over.

Since v2026.09.0 the CPSV Editor's `audit` job also validates `renovate.json` with
`--strict` — pinning without working automated updates decays into an unpatched tree, so
a Renovate that has silently stopped running is itself a supply-chain failure. That is
not hypothetical: five keys used as JSON comments in the Linked Data Explorer's
configuration were rejected as invalid and Renovate stopped opening pull requests, with
nothing in CI noticing.

The rollout is not identical across the three. RONL Business API and — since
v2026.09.0 — the CPSV Editor have taken the v7 action majors; the Linked Data Explorer
remains on v4 and carries one `actions/checkout` at v3.7.0, all pinned by digest but
pinned to older majors. **No `main` branch is gated**: the rulesets target
`refs/heads/acc` everywhere, so the gate protects the acceptance path only. The CPSV
Editor is the only repository whose `main` even carries the four artifacts, and
carrying them is not the same as enforcing them.

[Supply-Chain Pinning](supply-chain.md) covers the mechanism, the measured results
(16 findings to zero in the CPSV Editor, 49 in RONL Business API, 40 in the Linked Data
Explorer), what the gate deliberately does not protect, and the order to copy the four
artifacts into the next repository.

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

### The 80% branch floor is a convention, not a gate

RONL Business API adopted a **per-file 80% branch-coverage floor across all five
workspaces that have a test runner** in v2026.09.2, taking 53 files below the line to
none. It is a real standard and new code is held to it — but it is worth being precise
about what enforces it, because the answer is *review*, and nothing else:

- **No coverage threshold is configured** in any of the five runner configs
  (`packages/backend/jest.config.js`, and the four Vite/Vitest configs). A file that
  drops below 80% fails nothing locally.
- **Coverage is not run in CI at all.** None of the nine workflows mentions it, so no
  pipeline measures coverage, let alone gates on it.
- The floor is recorded in an implementation plan in the repository, and honoured by
  the people and reviews that read it.

That is a legitimate way to hold a standard, and stating it plainly is better than
implying a gate that does not exist — a contributor who assumes CI will catch a
coverage regression will be wrong. The measured figures live on
[Coverage](../ronl-business-api/developer/testing/coverage.md), which records when they
were last taken.

`@ronl/shared` is deliberately outside this: it has no test script and needs none,
being types plus two seed modules with no functions and no branches. That exemption has
a consequence worth knowing — **executable logic placed in the shared package is
unmeasurable by construction**, which is why a branching helper was moved out of it in
v2026.09.4 rather than left where a passing test run concealed the gap.
