---
scope: cross-cutting
verified:
  date: 2026-10-04
  against:
    CPSV Editor: "4cba989"
    Linked Data Explorer: "9e0d18e"
    RONL Business API: "5c6e716"
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
| **CPSV Editor** | ✅ since v2026.09.3 — the pilot | **`acc` and `main`** — `main` since 30 September 2026 | ✅ since v2026.09.4 |
| **RONL Business API** | ✅ since v2026.09.7 | **`acc` and `main`** — `acc` since 19 September 2026, `main` since 29 September 2026 | ✅ since v2026.09.7 |

**The RONL Business API's `scan` ran without being required for a fortnight**, and the
reason is worth keeping because it is the pattern to copy: its first authenticated scan
reported a baseline far larger than either of the others — hundreds of Supply Chain
findings across a monorepo's npm tree — and a gate required before its baseline is triaged
is a gate that gets bypassed in its first week. The triage finished and the promotion, as
predicted, was a ruleset edit that touched no file; nothing in the workflow moved.
Marking the job non-blocking instead would have been the obvious alternative and the wrong
tool, for the reason set out under
[where `check-supply-chain` blocks](supply-chain.md#where-it-runs-and-where-it-blocks):
`continue-on-error` hides the finding rather than declining to act on it.

Its lock-file maintenance landed in the same release and before any triage, deliberately:
one refresh closed 63 of 66 Supply Chain findings in the Linked Data Explorer and took the
CPSV Editor to zero, so triaging first would have been work thrown away. Its own first
refresh bore that out — see [the alert counts](#what-nothing-watches-between-merges) below.

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
`acc` and, since 30 September 2026, on `main`**, where the new `main promotion gate` ruleset
requires `audit` and `scan`. Until then `main` required a pull request and no status checks
at all, by decision: `main` is promoted from `acc`, whose commits already passed `audit` and
`scan`, and a required check that never reports wedges a pull request
([ttl-editor#131](https://github.com/sgort/ttl-editor/issues/131)). By the repository's own
account, that reasoning held for the path-filtered deploy job but not for `audit` and `scan`,
whose workflows run on every pull request; the deploy check is still not required on
`main`. A single package, it
needed neither of the Linked Data Explorer's filter fixes: its deploy workflows use
`paths-ignore` for documentation only, so a lockfile change already builds and deploys,
and it has no group rules to multiply a refresh into three pull requests.

Its last four Code findings had been ignored in the Semgrep dashboard during that triage, where the reasoning was invisible from the code. v2026.09.5 answered them in the source instead: two prototype-pollution warnings in the iKnow parser's path helpers carry a suppression scoped to one rule on one line, with the reason and the condition under which it stops being true, and two `renovate.json` major-version holds now state their 14-day minimum release age themselves, because JSON cannot carry a suppression comment. By the release's own record, the full scan on `acc` after the merge reported 0 Code findings.

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

Two more have joined since, on the backend's DMN quality service, for the same rule and the
same reason: its tag parameter was narrowed to a closed union, `MeasuredTag`, so the
Linked Data Explorer carries **ten** such lines at `0143ea2`, five of them
`detect-non-literal-regexp`. The RONL Business API took the same approach on 24 September
2026, for the first time — *"No nosemgrep annotation existed in this repository before"* —
annotating fifteen false positives on fourteen lines, each with its own reason; with one
added later the same day for its public OpenAPI route, it carried fifteen at `3c44b9e`. Three
more came on 30 September 2026 (`c395696`), in the Open Graph check scripts —
`detect-non-literal-regexp` in the frontend's `scripts/check-og.mjs`, and
`path-join-resolve-traversal` and `detect-non-literal-regexp` in the public site's — so it
carries eighteen at `5c6e716`. The Linked Data Explorer's ten are unchanged at `9e0d18e`.

That change also recorded the lesson that belongs next to every "0 findings" claim: *"The
first scan used --config=p/javascript and reported 0 findings. Running it against the
PRE-change tree also reported 0 … Re-run with the five exact rule ids: before 14, after
0."* The ruleset had not contained those rules at all. **A zero counts as evidence only if
the same scan finds the findings before the fix.**

Each comment also says **when it stops being true**. `insecure-object-assign` is
safe because of its current caller, not because of the line, so its comment ends
by naming the change that would make it unsafe: `updateTestCase` receiving
imported or URL-supplied data. A suppression that states only why it is fine
today reads as settled long after it has stopped being so.

The one Code finding left after that pass was a true positive — the Tailwind Play CDN
running from a third-party origin in the production frontend
([linked-data-explorer#96](https://github.com/sgort/linked-data-explorer/issues/96)) —
and this page said it would clear because the script was removed, not because anything
was suppressed. That is how it went: v2026.09.5 builds Tailwind with the application,
the script tag is gone, and #96 closed on 17 September 2026.

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

**That none fell inside the cooldown was the calendar, not the policy.** Renovate does not
apply `minimumReleaseAge` to lock-file maintenance, because the package manager performs the
update — so a weekly refresh can take a transitive version published that morning. See
[the cooldown stops at the manifest](supply-chain.md#the-cooldown-stops-at-the-manifest).

Keeping it running took four changes, and the order in which they proved
necessary is the useful part:

1. **The root `package-lock.json` and `package.json` are in the backend and frontend
   deploy filters**, acceptance and production: in the acceptance workflows' `push`
   filters and `changes` patterns, and in `scripts/promotion-targets.mjs` for
   production. Before, a
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

### What nothing watches between merges

Semgrep runs on `push` and `pull_request` and on nothing else. **Since 24 September 2026
one workflow in each repository does run on a schedule**: `dependency-audit.yml`, daily at
05:17 UTC and on demand, runs `npm audit --package-lock-only` against the lockfiles of
**both `acc` and `main`** — the branch production is built from included — and on a high or
critical advisory in production dependencies it fails and opens or updates a single
tracking issue, closing it again once clean. It is npm's advisory database rather than
Semgrep's, and it deliberately passes moderates and development-only advisories. It proved
itself on its first scheduled runs: on 25 and 26 September it passed in the CPSV Editor and
the Linked Data Explorer and failed in the RONL Business API, on an `adm-zip` high that was
gone from `acc` and still on `main` — the version production ran. The promotion that
removed `keycloak-connect` cleared it
([ronl-business-api#208](https://github.com/sgort/ronl-business-api/issues/208)).

It has caught two more since, and in both the fix was to shrink the production tree rather
than wait for an upstream patch:

- **The Linked Data Explorer, 30 September – 3 October 2026**
  ([#240](https://github.com/sgort/linked-data-explorer/issues/240)): `brace-expansion` and
  `http-cache-semantics`, reached through `libxmljs2`'s `node-gyp`. `http-cache-semantics` has
  no patched release, so a lockfile refresh (`7dcfdea`) and an override giving `libxmljs2`
  `node-gyp` 13 (`be5bc99`) removed the chain; by the commit's record the backend's production
  install went from 349 packages to 271.
- **The RONL Business API, 3 October 2026**: a `braces` high, opened as
  [#303](https://github.com/sgort/ronl-business-api/issues/303) at 10:24 and closed at 11:45,
  once `@tailwindcss/typography` became the build-time devDependency it is (`c48b2cd`, #305);
  [#307](https://github.com/sgort/ronl-business-api/issues/307) held `main` until the
  promotion cleared it the same afternoon.

Of the three repositories, only the CPSV Editor's audit has not yet failed for a real
reason; every scheduled run there has passed.

Dependabot *alerts* still watch the default branch only, which is `acc` in all three, so
the daily audit is what now sees `main`. Read from the API on 4 October 2026, with the
27 September figures beside them:

| Repository | Open alerts | On 27 September | Dismissed with a reason |
|---|:-:|:-:|:-:|
| CPSV Editor | **0** | 0 | 0 |
| Linked Data Explorer | **2** — `@tiptap/core` medium, `dompurify` low | 3 | 0 |
| RONL Business API | **4** — `minimatch` high (development scope), `react-router` ×2 medium, `dompurify` low | 5 | 0 |

**The RONL Business API's drop is what lock-file maintenance does on its first run.** It
was enabled on 12 September 2026 and had not yet had a Monday; the refresh that followed
took 154 alerts — 2 critical, 54 high — to single figures without a line of application
code changing, exactly as it had in the other two. The reading to take from it is not that
the number is small now but that **nothing had ever refreshed the transitive tree** —
Renovate maintains the packages a manifest names, and the alerts were almost all beneath
them. Three more went on 24 September by removal rather than update: `keycloak-connect`,
declared in the backend's `package.json` and imported nowhere, took `adm-zip`, `elliptic`
and a `chromedriver` pulled at the floating tag `latest` out of the tree with it.

ICTU's guideline asks for each finding to be mitigated **or explicitly accepted**. Two were
dismissed with a written reason on 24 September — the RONL Business API's `adm-zip` and
`elliptic`, neither with a patched version — and both closed as fixed the same day, when
`keycloak-connect` went. None of the six open today is dismissed, so each is still neither
mitigated nor accepted. Four wait on a major queued behind Dependency Dashboard approval —
Tiptap 3 in the Linked Data Explorer, React Router 7 and a `typescript-eslint` major in the
RONL Business API — while the two `dompurify` lows have a patch release, 3.4.16. The `qs`
alerts, and with them the need for Express 5, are gone. In the RONL Business API the triage
is tracked in [#311](https://github.com/sgort/ronl-business-api/issues/311).

Two further gaps belonged with this one, and one has closed. **Every release now carries an
SBOM**, since 26 September 2026: `scripts/write-sbom.mjs`, a `/bump-release` step, writes a
CycloneDX 1.5 bill of the production dependencies from the lockfile to
`docs/sbom/<name>-<version>.cdx.json`. On each push to `main`, `sbom.yml` runs
`write-sbom.mjs --verify-release`, which fails only if the released version has no SBOM: a
promotion carries commits merged after the release, so lockfile drift is reported as a
warning and the job still passes. The strict match — the committed file describes the
lockfile exactly — is `--check`, which belongs where the release is cut. Committed so far:
the CPSV Editor's 2026.09.6 (backfilled), 2026.09.7 and 2026.10.0; the Linked Data
Explorer's 2026.09.7, 2026.09.8 and 2026.10.0; the RONL Business API's 2026.09.11 to
2026.09.15 and 2026.10.0. Nothing yet re-analyses them when a new advisory lands. The other
gap stands: **every resolved package comes straight from the public registry** — 566 in the
CPSV Editor's lockfile, 1,527 in the Linked Data Explorer's, 1,497 in the RONL Business
API's at `4cba989`, `9e0d18e` and `5c6e716`, all from `registry.npmjs.org` — with no proxy
in between and no provenance or signature check. (The only entries resolving elsewhere are
the workspace links each monorepo makes to its own packages: 2 and 6.) That one is an ICTU
infrastructure question before it is a repository one, and it is tracked in
[linked-data-explorer#249](https://github.com/sgort/linked-data-explorer/issues/249).

Whether Semgrep Cloud re-evaluates a stored scan against advisories published after it ran is
not established, so it is not counted here as monitoring. The scores these gaps earn against
ICTU's guideline are on [ICTU Dependency Guideline](ictu-dependency-guideline.md).

### What making it required costs

- **semgrep.dev is now in the merge path.** The rulesets that require `scan` carry
  **zero bypass actors**, so if semgrep.dev is unreachable or `SEMGREP_APP_TOKEN` is
  revoked, merges stop until a ruleset is edited — on `acc` and `main` in **all three**
  repositories: on every `acc` since 19 September 2026, on the RONL Business API's `main`
  since 29 September and on the CPSV Editor's since 30 September.
  `check-supply-chain` accepted an analogous risk for
  the GitHub API — but the GitHub API is a dependency of the platform anyway, and
  semgrep.dev is not. It is a genuinely new class of outage.
- **A pull request from a fork cannot pass.** Secrets are not passed to fork runs,
  so `semgrep ci` cannot start and `--no-suppress-errors` fails the step — which,
  for a required check, blocks the merge. Accept that knowingly, or solve it,
  before requiring the scan in a repository that takes outside contributions.
