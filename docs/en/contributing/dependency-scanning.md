---
scope: cross-cutting
verified:
  date: 2026-09-12
  against:
    CPSV Editor: "f5bae6a"
    Linked Data Explorer: "be6bc54"
    RONL Business API: "311d732"
---

# Dependency Scanning

*The other supply chain: the npm tree*

## Why the npm tree needs its own gate

[Supply-Chain Pinning](supply-chain.md) verifies **GitHub Actions**: zizmor checks that
each `uses:` names a digest, `check-supply-chain` checks that the digest is the version
its comment claims, and the register checks the two agree. None of them says anything about
the packages in `package-lock.json` — and neither does the coverage floor. Until
September 2026, npm dependency vulnerabilities across these repositories were
remediated by Renovate and verified by nobody: a bot being trusted rather than a
gate being enforced, and the difference only shows on the day the bot is wrong or
stalled.

The second half is a **Semgrep** scan — Code and Supply Chain — as its own
workflow, required in the rulesets.

| Repository | Semgrep `scan` | Required on | Lock-file maintenance |
|---|---|---|---|
| **Linked Data Explorer** | ✅ since v2026.09.3 | **`acc` and `main`** | ✅ with a slot kept for it |
| **CPSV Editor** | ✅ since v2026.09.3 — the pilot | **`acc`** — `main` ungated by decision | ✅ since v2026.09.4 |
| **RONL Business API** | ✅ since v2026.09.7 | **nowhere yet** — it runs on every pull request and is deliberately not required | ✅ since v2026.09.7 |

**The RONL Business API's `scan` is the one that runs without being required**, and the
reason is worth keeping: its first authenticated scan reported a baseline far larger than
either of the others — hundreds of Supply Chain findings across a monorepo's npm tree —
and a gate required before its baseline is triaged is a gate that gets bypassed in its
first week. Promotion is a ruleset edit, reversible and touching no file, which is also
why nothing in its workflow will move when it happens. Marking the job non-blocking
instead is the obvious alternative and the wrong tool, for the reason set out under
[where `check-supply-chain` blocks](supply-chain.md#where-it-runs-and-where-it-blocks):
`continue-on-error` hides the finding rather than declining to act on it.

Its lock-file maintenance landed in the same release and before any triage, deliberately:
one refresh closed 63 of 66 Supply Chain findings in the Linked Data Explorer and took the
CPSV Editor to zero, so triaging first would have been work thrown away.

### The workflow, as the Linked Data Explorer runs it

| | |
|---|---|
| Workflow | `.github/workflows/semgrep.yml` |
| Job / check context | `scan` |
| Trigger | `pull_request` with **no** branch or paths filter; `push` on `acc` and `main` |
| Scanner | `semgrep==1.176.1`, installed into a venv and registered in `SECURITY-PIPELINE.md` |
| Auth | `SEMGREP_APP_TOKEN` repository secret |
| Scope | One job for all three workspaces — they resolve through the single root `package-lock.json`, so there is no per-workspace fan-out to keep in step |

It triggers exactly as the `audit` does, and for the same reason: a required check
that a pull request can avoid by its base branch or by the paths it touches is a
check that goes missing, and a missing required check blocks the pull request
permanently. **Audit widely, deploy narrowly** applies to this job as much as to
`zizmor.yml`.

Four decisions in the file are worth keeping when it is copied:

- **A separate workflow, not a step in the `audit` job.** `audit` is already
  required, so a step there would have blocked from the day it merged. A separate
  workflow reports on every pull request and gates nothing until its job is added
  to a ruleset — which makes promotion a ruleset change, reversible without
  touching the file. The Linked Data Explorer ran it as a reporting check while
  the first baseline was triaged, and required it the same day.
- **The token is not optional.** Semgrep Supply Chain resolves only on an
  authenticated scan. An unauthenticated run gets the open-source SAST rules and
  no Supply Chain at all — the entire reason the job exists.
- **`--no-suppress-errors`.** By default `semgrep ci` reports errors during
  analysis and still exits 0, so a scanner that cannot run reads as a clean scan.
  In CI, a tool that cannot run is a failure.
- **Only superseded pull-request runs are cancelled** —
  `cancel-in-progress: ${{ github.event_name == 'pull_request' }}`. The acceptance
  and audit workflows cancel unconditionally and the production ones never do;
  this one needs a third policy, because a push run on `acc` or `main` writes the Semgrep Cloud baseline, and cancelling one
  leaves the dashboard describing a scan that never finished, with nothing queued
  to correct it.

!!! warning "A `.semgrepignore` replaces Semgrep's default ignore list — it does not extend it"
    The defaults exclude `test/` and `tests/`. The Linked Data Explorer's first
    `.semgrepignore` listed only what it meant to add, and so **silently brought 16
    test files back into scope**. The finding count came out exactly as predicted
    either way, because none of those files happened to trip a rule — only diffing
    the scanned file sets showed it. The file now restates `test/` and `tests/`
    explicitly.

    The same file ignores `/examples/` **with its leading slash**. The root
    `examples/` is reference material; `packages/frontend/public/examples/` is
    served, because Vite copies `public/` into the build. An unanchored `examples/`
    matches both — `.gitignore` syntax matches a directory of that name at any
    depth — and would drop served files from the scan while the total stays
    plausible. **Check the set of files scanned, not the count.**

### The CPSV Editor, which piloted it

The CPSV Editor adopted the same workflow first, in v2026.09.3, and it is **required on
`acc` only**. Its `main` requires a pull request and no status checks at all — decided
and kept rather than overlooked, because `main` is promoted from `acc`, whose commits
already passed `audit` and `scan`
([ttl-editor#131](https://github.com/sgort/ttl-editor/issues/131)). A single package, it
needed neither of the Linked Data Explorer's filter fixes: its deploy workflows use
`paths-ignore` for documentation only, so a lockfile change already builds and deploys,
and it has no group rules to multiply a refresh into three pull requests.

**The finding count is not the measure.** The triage that produced the gate
([ttl-editor#112](https://github.com/sgort/ttl-editor/issues/112)) opened at **36
findings and closed at 0**, and by the repository's own record almost none of that
movement was vulnerabilities being fixed:

| Findings | What moved the number |
|--:|---|
| 36 | Scanned by hand against a local checkout **51 commits behind `acc`** |
| 17 | The real figure on the branch head — Renovate had already closed the other 19 |
| 14 | `/examples/` excluded — reference material, not application code |
| 16 | A new test file arrived carrying two more |
| 12 | Test files taken out of Code scanning |
| 11 | After a fix, a suppression, and one finding that got worse first |
| 7 | CI honours dashboard triage; a local `--dry-run` does not |
| **0** | **The lockfile refreshed for the first time** (v2026.09.4) |

Three lessons from that trajectory transfer beyond this repository:

- **A scan run by hand is pinned to whatever is checked out**, and nothing in its output
  names the commit. The first figure described a tree that was not the branch head. A
  scan in CI cannot make that mistake — which, more than any individual finding, is what
  the gate buys.
- **"The finding will go away" is a prediction, not a plan.** Fixes justified partly on
  retiring a finding did not all retire it — a rule that matches the *shape* of a loop
  fired twice after one of them. Verify after, not before.
- **The last seven were never going to close on their own.** They were first written off
  as needing an upstream release, but each had a fixed version inside its declared range;
  nothing had moved them because **lock-file maintenance had never been turned on**. It
  was checked before any configuration changed — an in-range refresh and a scan in a
  scratch worktree predicted 7 → 0 — and the first real refresh delivered exactly that.

Two scoping rules, each with a reason worth keeping: **`/examples/` is ignored with its
leading slash**, because `public/examples/` is served and an unanchored rule dropped a
served file from the scan while the counts agreed; and **test files are out of Code
scanning but not Secrets scanning**, which keeps its own ignore list — a hardcoded
credential in a test is the one finding class genuinely worth having there. Semgrep has no
per-rule path setting, so the narrower fix would have meant forking two registry rules.

!!! warning "npm 10 cannot perform that refresh on this tree"
    npm 10.9.4, bundled with Node 22, crashes in its resolver — `Cannot read properties
    of null (reading 'edgesOut')` — on both a fresh resolution and `npm update`. npm 11
    resolves the same tree cleanly. `npm ci` and CI (Node 24) are unaffected, so it
    surfaces only on a Node 22 workstation adding or updating a package. The repository's
    README says to use **Node 24 / npm 11**, and why.

**A pull request from a fork cannot pass the scan**, since secrets are not passed to fork
runs. The repository has one fork; the cost is accepted knowingly and tracked in
[ttl-editor#128](https://github.com/sgort/ttl-editor/issues/128).

### Suppressions live in the code

By the repository's own CI posture record, the Linked Data Explorer's first scan
found 76 findings after the ignore file, none blocking, and the day closed at four. Every false positive among them now carries
a `nosemgrep` **naming the single rule, on the single line, with the reason directly
above it** — eight in all:

| Rule | Count | Why it is a false positive |
|---|--:|---|
| `cors-permissive-express` | 4 | The two deliberately public, read-only mounts — see [RoPA Records — the public routes](../linked-data-explorer/developer/ropa-records.md#public-route-v1ropapublic) |
| `detect-non-literal-regexp` | 3 | The interpolated attribute name is a closed TypeScript union, so it is a compile-time literal, never data |
| `insecure-object-assign` | 1 | Its only caller passes a fixed timestamp field, and the data is the user's own |

None lives in the Semgrep dashboard. A `nosemgrep` travels with the line, is
visible in review, and survives the Semgrep project being recreated; a dashboard
ignore is platform state nobody reading the file can see, lost with the project.
Use the dashboard only where the file cannot carry a comment — JSON, for instance.

Each comment also says **when it stops being true**. `insecure-object-assign` is
safe because of its current caller, not because of the line, so its comment ends
by naming the change that would make it unsafe: `updateTestCase` receiving
imported or URL-supplied data. A suppression that states only why it is fine
today reads as settled long after it has stopped being so.

The one Code finding left is a true positive — the Tailwind Play CDN running from a
third-party origin in the production frontend
([linked-data-explorer#96](https://github.com/sgort/linked-data-explorer/issues/96))
— and it will clear because the script is removed, not because anything is
suppressed.

!!! note "Reachability is decided in CI, not on a laptop"
    The repository's CI posture record reports that a local dry run classed every
    one of the first 66 Supply Chain findings as unreachable, while the CI scan of
    the same tree classed **5 as reachable — all HIGH** — 23 as undetermined and 38
    as unreachable. Why the two disagreed was not established. What follows from
    it is: a local `--dry-run` is fine for Code findings and for checking what an
    ignore file excludes, and **not** for deciding whether a Supply Chain finding
    matters.

### Renovate maintains dependencies, not the tree

Renovate proposes updates to the packages a manifest **names**. The transitive tree
underneath moves only through `lockFileMaintenance`, which the recommended preset
leaves off. The Linked Data Explorer's first scan found `rollup` at 4.55.1 from
January, although 4.59.0 had been out since February, because two failures had
stacked:

- **Lock-file maintenance was not enabled until 29 August 2026.** Before that,
  nothing refreshed a transitive dependency at all.
- **Once enabled, it was starved.** It is eligible only inside its Monday
  schedule, and `prConcurrentLimit: 5` was full of open updates, so it sat in the
  Dependency Dashboard as rate-limited and never opened a pull request.

Forced by hand, **one refresh moved 338 packages and closed 63 of 66 Supply Chain
findings**, including all five reachable ones — every fix inside a range the
manifests already declared, none published within the 14-day cooldown. The three
left are held by a tilde range in `express` and by a major version of
`@tiptap/core`, and no refresh can close them.

Keeping it running took four changes, and the order in which they proved
necessary is the useful part:

1. **The root `package-lock.json` and `package.json` are in all four deploy
   workflows' `paths:` filters**, acceptance and production. Before, a
   lockfile-only change — lock-file maintenance above all — was built, tested and
   deployed by nothing: every filter named its own package, and the one file all
   three workspaces share was in none of them. The first two pull requests after
   the change ran both applications' suites where the old filters would have run
   one.
2. **The per-workspace group rules list every update type except
   `lockFileMaintenance`**, so one refresh is one pull request rather than three
   identical ones. Lock-file maintenance's own default is no group; the rules
   were overriding it.
3. **Lock-file maintenance has `prPriority: 10`** — which turned out to be the
   weaker half. Priority orders branches eligible *in the same run*; it never
   holds a slot free for a branch that becomes eligible on Monday.
4. **Major updates need Dependency Dashboard approval**, and that is what keeps
   the slot. The queue competing with the refresh was almost entirely majors,
   which nobody merges on autopilot anyway; behind approval they wait as
   checkboxes and hold no slot. `vulnerabilityAlerts` sets
   `dependencyDashboardApproval: false` explicitly, so **a security fix that
   happens to be a major version never waits on a click**.

!!! warning "Widening a deploy filter costs staging environments — check the plan first"
    Every lockfile pull request now takes a Static Web Apps preview environment on
    the acceptance app. The Linked Data Explorer can afford it: its frontend apps
    are on the Standard plan, ten environments each, and `prConcurrentLimit: 5`
    leaves five for people. On a plan with fewer slots the same change reproduces
    the collision described under
    [`renovate.json`](supply-chain.md#4-renovatejson-keeping-the-pins-alive). **Size the Renovate cap
    against the slots, not the other way round.**

### What making it required costs

- **semgrep.dev is now in the merge path.** The rulesets that require `scan` carry
  **zero bypass actors**, so if semgrep.dev is unreachable or `SEMGREP_APP_TOKEN` is
  revoked, merges stop until a ruleset is edited — to `acc` in both repositories, and to
  `main` in the Linked Data Explorer. `check-supply-chain` accepted an analogous risk for
  the GitHub API — but the GitHub API is a dependency of the platform anyway, and
  semgrep.dev is not. It is a genuinely new class of outage.
- **A pull request from a fork cannot pass.** Secrets are not passed to fork runs,
  so `semgrep ci` cannot start and `--no-suppress-errors` fails the step — which,
  for a required check, blocks the merge. Accept that knowingly, or solve it,
  before requiring the scan in a repository that takes outside contributions.
