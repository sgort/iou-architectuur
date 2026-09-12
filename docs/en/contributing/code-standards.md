---
scope: cross-cutting
verified:
  date: 2026-09-12
  against:
    CPSV Editor: "f5bae6a"
    Linked Data Explorer: "be6bc54"
    RONL Business API: "311d732"
---

# Code Standards

!!! info "Re-verified for all three applications on 12 September 2026"
    Every claim on this page was re-checked against `f5bae6a`, `be6bc54` and
    `311d732` — the commits that published v2026.09.4 of the first two and v2026.09.7
    of the RONL Business API. Rulesets were read from the API per branch rather than
    from prose, and workflow and pin counts were derived by listing the files.

    **The RONL Business API's claims were the stale ones**, and this sync is where they
    were earned back: it closed ten of eleven cross-repository alignment items on 12
    September 2026, and several sentences on this page described the state before that.

This page covers three application repositories — CPSV Editor (`ttl-editor`), Linked
Data Explorer, and RONL Business API — that share a common tooling convention:
Husky-managed git hooks, npm workspaces, and four identically named root scripts. It
documents what their tooling actually enforces, measured from each repository's own
configuration rather than assumed to be uniform.

**The Norm Editor is the fourth application repository and is deliberately out of
scope below**, because it shares none of that convention — see
[The Norm Editor is shaped differently](#the-norm-editor-is-shaped-differently) at the
foot of this page.

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

**And a red test does not block a merge in any of the three.** Since August 2026 the
suites run on every pull request, so a failure shows there and stops the deploy — but no
ruleset names a test workflow as a required check. What the rulesets require is `audit`
in all three, and `scan` in the CPSV Editor and the Linked Data Explorer; see
[Enforcement](#enforcement-what-blocks-a-merge) below. In the RONL Business API that is
not an oversight: every deploy workflow on `main` is push-only, and a required check that
never reports on a pull request wedges it permanently.

---

## CI

Every deploy pipeline that has something to test now runs the suite before it builds,
and a failing test blocks the deploy. That has only been true since 20 August 2026 —
before then CI and the hooks left the same gap, and RONL Business API's public-site
package had the only real test gate anywhere.

**RONL Business API** — **ten** workflows: an acc/prod pair for each of **four**
deployable packages, plus the supply-chain `audit` and, since v2026.09.7, the Semgrep
`scan`:

| Workflow pair | Lint | Type-check | Tests | Notes |
|---|:---:|:---:|:---:|---|
| `azure-backend-*` | ✅ | – | ✅ | Builds and uploads a deployment artifact; it does not deploy |
| `azure-frontend-*` | ✅ | – | ✅ | Also runs `npm run test:perf`, the wall-clock budget, as a step of its own |
| `azure-publicsite-*` | ✅ | ✅ | ✅ | Its build additionally gates on a prerender and a bundle-cleanliness check |
| `azure-pa-demo-*` | ✅ | ✅ | ✅ | Also installs Chromium and runs the Playwright E2E suite before the bundle gate |

The frontend's performance budget runs separately because it asserts wall-clock time,
which means nothing while 133 test files compete for cores — see
[The performance budget](../ronl-business-api/developer/testing/overview.md#the-performance-budget).

Two changes in v2026.09.6 and v2026.09.7 are worth reading off that table rather than
inferring from it. **`@ronl/pa-cockpit` has no workflow of its own**, being a library
rather than a deployable, so its 476 tests ran nowhere in CI; both frontend workflows now
run its suite first, because the frontend imports it. And **the backend pair now triggers
on `pull_request` as well as `push`**
([#87](https://github.com/sgort/ronl-business-api/issues/87)), so its 2008 tests run
before the merge rather than after it. That needed no per-step event guards, unlike the
Linked Data Explorer's equivalent change below: the backend workflow ends at an uploaded
artifact and has no deploy step to gate. Both filters gained `package-lock.json` and
`package.json`, because every workspace resolves through them and a lockfile-only change
was built and tested by nothing.

**Linked Data Explorer** — **eight** workflows: six deployment workflows, the
supply-chain `audit` gate added in v2026.08.7, and the Semgrep `scan` added in
v2026.09.3 (see [Supply-Chain Pinning — the npm tree](supply-chain.md#7-the-other-supply-chain-the-npm-tree)).
Both backend and both frontend workflows run lint and then the suite before building.
The two `ropa-site` workflows run neither, and correctly so: that package is a static
`index.html` plus a `staticwebapp.config.json`, with no build and no test script to run.

Unlike the other two, **the Linked Data Explorer's CI does deploy its backend** — the
backend workflows end in `azure/webapps-deploy`, where RONL Business API's end in an
uploaded artifact that a developer deploys by hand. **Since v2026.09.2 the backend's
acceptance workflow also triggers on `pull_request`**, with its six deploy-side steps
gated on the event, so a pull request runs the backend suite before the merge rather
than `acc` discovering a break afterwards. The production backend workflow stays
push-only on purpose: it declares the protected `production` environment, and a
pull-request trigger there would put a human approval *in front of* the tests meant to
inform it.

Since v2026.09.1 all four of its deployment workflows also run a **Typecheck** step.
That closed a real hole rather than adding ceremony: **fifteen type errors had
accumulated invisibly, because nothing in the repository ran `tsc` at all.** `build` is
`vite build`, which strips types through esbuild without checking them; `lint` is
ESLint; `test` is Vitest. None of the three typechecks, so a type error could reach
`acc` and deploy. A `typecheck` script now exists at the root and in both workspaces.

**CPSV Editor** — four workflows: two Azure Static Web Apps workflows, `acc` and `main`
alike, running `npm ci`, `npm run lint` and `npm run test:ci` ahead of the deploy action,
plus the supply-chain `audit` and, since v2026.09.3, the Semgrep `scan` (see
[Supply-Chain Pinning — the npm tree](supply-chain.md#7-the-other-supply-chain-the-npm-tree)). Since v2026.09.2 that `audit` job also runs
`npm run check-format` and `npm run check-supply-chain` — and it gained its first
`npm ci` to do so, everything in it having previously run from `npx` or plain node. Since v2026.09.0 the deploy workflows are named
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

**An allowlist has to name the files every package shares, too.** Until v2026.09.4 the
Linked Data Explorer's filters named each workflow's own package and nothing else, so a
change to the root `package-lock.json` alone — Renovate's lock-file maintenance, above
all — was built, tested and deployed by nothing. The root `package.json` and
`package-lock.json` are now in all four backend and frontend filters, acceptance and
production.

**A workflow's own file in its `paths:` list is a trigger.** Each Linked Data Explorer
filter names its workflow file alongside its package, which is correct — a change to how
a thing deploys should redeploy it — but it means a sweep across workflow files, such as
a pinning pass, redeploys every package whose workflow it touched, whether or not the
package changed. Predict what a merge will deploy from the whole list, not the entry that
looks like the package.

!!! warning "A skip marker in a commit message turns every gate off"
    GitHub Actions skips all `push` and `pull_request` workflows for a commit whose
    message contains `[skip ci]`, `[ci skip]`, `[no ci]`, `[skip actions]` or
    `[actions skip]` — **anywhere in the message, including in prose that is only
    discussing them**. A skipped required check reports nothing rather than failing,
    so the symptom is a pull request that can never become mergeable and has no red
    run to explain why. Describe the markers in words in a commit message; they are
    safe in a file. The Linked Data Explorer composes merge commits from the pull
    request **title** with a **blank** body, so a marker quoted in a pull request
    description cannot reach its merge commit — check that repository setting before
    relying on it anywhere else.

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
all three are named `acc supply-chain gate` and carry zero bypass actors.

They are not identical in shape. Read per branch from the API on 12 September 2026:

| | `acc` | `main` |
|---|---|---|
| CPSV Editor | pull request, `audit`, `scan` | a pull request, no status checks |
| Linked Data Explorer | pull request, `audit`, `scan`, deletion, non-fast-forward | the same four |
| RONL Business API | pull request, `audit`, deletion, non-fast-forward | the same four |

**Two of the three now gate `main`.** The Linked Data Explorer's `main promotion gate`
came first, on 9 September 2026; the RONL Business API created its own on 12 September,
before the promotion pull request was opened, replacing a classic protection under which
an administrator could push to `main` directly — so the branch that deploys production
had been the *less* protected of its two. Both mirror their `acc` ruleset and differ from
it in exactly one parameter, deliberately:
`require_extra_approval_for_unattributed_changes` is `true` on `acc` and `false` on
`main`, because a promotion carries commits under several author identities against a
ruleset requiring zero approvals, and the flag would demand an approval nobody can give.

The CPSV Editor's `main` requires a pull request but no status checks — **decided and
kept**, not overlooked
([ttl-editor#131](https://github.com/sgort/ttl-editor/issues/131)): `main` is promoted
from `acc`, whose commits already passed `audit` and `scan`. See
[Supply-Chain Pinning](supply-chain.md#adoption-status) for the argument on both sides.

**`scan` is required in two of the three.** The RONL Business API's runs on every pull
request and is deliberately not a required check while the baseline from its first
authenticated scan is triaged — a gate required before its baseline is triaged is a gate
that gets bypassed in its first week, and promoting it later is a ruleset edit that
touches no file.

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

Two Renovate settings joined that list in September 2026, and they matter more than they
look. **Lock-file maintenance** is what moves the transitive tree at all — Renovate
maintains the dependencies you name, not what they resolve to, and `config:recommended`
leaves it disabled; all three repositories now run it on a weekly schedule. And **majors
sit behind Dependency Dashboard approval** rather than a global approval flag, so the
concurrent-pull-request limit is spent on the updates that can actually merge. See
[Supply-Chain Pinning — Renovate maintains dependencies, not the tree](supply-chain.md#renovate-maintains-dependencies-not-the-tree).

Since v2026.09.0 the CPSV Editor's `audit` job also validates `renovate.json` with
`--strict` — pinning without working automated updates decays into an unpatched tree, so
a Renovate that has silently stopped running is itself a supply-chain failure. That is
not hypothetical: five keys used as JSON comments in the Linked Data Explorer's
configuration were rejected as invalid and Renovate stopped opening pull requests, with
nothing in CI noticing.

The rollout is not identical across the three. All three are now on the v7 action
majors — RONL Business API first, the CPSV Editor since v2026.09.0, and the Linked Data
Explorer since v2026.09.2, which retired its last `actions/checkout` at v3.7.0 on the
way. **The CPSV Editor is now the only one whose `main` is ungated**, by decision; the
Linked Data Explorer and the RONL Business API both hold a promotion pull request to the
same rules as the pull requests it carries.

[Supply-Chain Pinning](supply-chain.md) covers the mechanism, what the gate deliberately
does not protect, and the order to copy the four artifacts into the next repository. The
[controls index](controls.md) is the one-page version of where each control holds.

---

## Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/), as
described in [Contributing → Commit your changes](index.md#5-commit-your-changes). None
of the three repositories above enforce this mechanically — the Norm Editor does, and
how it does so is covered in
[The Norm Editor is shaped differently](#the-norm-editor-is-shaped-differently).

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

### The 80% branch floor, natively enforced

**All three repositories** hold new and changed code to 80% branch coverage **per
file**, and as of September 2026 all three enforce it *natively* — in their test
runners' own configuration, with no exemptions and no custom script:

| Repository | Where |
|---|---|
| CPSV Editor | `vite.config.mjs` — `{ branches: 80, perFile: true }` |
| Linked Data Explorer | `packages/backend/jest.config.js` and `packages/frontend/vite.config.ts` |
| RONL Business API | All five workspace runner configs |

!!! warning "This page said the opposite until 9 September 2026, and was right at the time"
    Through v2026.09.1 the floor was a **convention held by review**: no threshold
    was configured anywhere and no workflow measured coverage. Two things changed
    it — RONL Business API and the Linked Data Explorer configured native
    thresholds, and the CPSV Editor retired the ratchet script that had been
    carrying its last exemption. A claim about enforcement is exactly the kind
    that goes stale without a word of its own text changing.

The route each took differs, and the CPSV Editor's is the instructive one: Vitest's
threshold globs are **additive rather than overriding**, so a repository not yet at
80% everywhere cannot express a partial rollout and needs a ratchet script instead.
[The Coverage Floor](coverage-floor.md) covers that mechanism, why branches rather
than functions, the load cost of bringing a large file up, and how to prove a
threshold actually bites rather than trusting a green run.

**A floor only gates where the tests run before the merge**, and as of 12 September 2026
all three do. The RONL Business API's backend workflow triggered on `push` alone until
v2026.09.7, so its 2008 tests ran only *after* a merge and its branch threshold gated
nothing on a pull request; the trigger closed that
([#87](https://github.com/sgort/ronl-business-api/issues/87)) and proved itself
immediately, when an `axios` 1.18 security bump broke the backend build on the pull
request rather than on `acc`.

`@ronl/shared` is deliberately outside this: it has no test script and needs none,
being types plus constant data with no functions and no branches. That exemption has
a consequence worth knowing — **executable logic placed in the shared package is
unmeasurable by construction**, which is why a branching helper was moved out of it in
v2026.09.4 rather than left where a passing test run concealed the gap. That move was
caught by hand, by someone who happened to look, and **v2026.09.7 replaced the
convention with a check**
([#84](https://github.com/sgort/ronl-business-api/issues/84)): `check-shared` runs in
the `audit` job and fails on a function, a class, a conditional or a loop anywhere in the
package. It uses the TypeScript compiler API rather than a pattern over text, because an
arrow in an interface is a type and the same syntax assigned to a const is logic, and no
regex separates them.


---

## The Norm Editor is shaped differently

The three repositories above converged on one toolchain. The Norm Editor did not, and
the differences are structural rather than stylistic — which is why applying this
page's expectations to it would produce wrong answers rather than merely strict ones.

| | The other three | Norm Editor |
|---|---|---|
| CI | GitHub Actions | **GitLab CI** (`.gitlab-ci.yml`) |
| Languages | TypeScript / JavaScript | **JavaScript *and* Python**, five services |
| Repository shape | npm workspaces (two of three) | **No root `package.json` at all** — each service stands alone |
| Git hooks | Husky + `lint-staged` | **`.githooks/`**, plain shell, no Husky |
| Deploy artifact | Static Web Apps bundle or artifact | **Docker images** pushed to Azure Container Registry |

### Its hooks enforce more, not less

The other three gate formatting and linting on commit. The Norm Editor's hooks do
something the others do not attempt:

- **`commit-msg`** rejects any subject line not matching the Conventional Commits
  pattern, with merge, revert and fixup commits explicitly exempted. A non-conforming
  message hard-fails rather than merely failing review.
- **`pre-push`** re-checks that pattern across every commit in the push range, so a
  message that slipped through locally cannot reach the remote.
- **`pre-commit`** regenerates `gui/public/changelog.json` from the git history via
  `scripts/generate-changelog.mjs`, so the in-app changelog cannot drift from what was
  actually committed. It degrades gracefully when `node` is absent rather than
  blocking the commit.

That last one is the reason its changelog is **git-log-derived** rather than
hand-curated, and why its entries read as commit subjects. A sync reading it should
expect terse text and check the source for anything substantive.

### What it does not have

No lint or format script is wired into CI, and **no coverage is measured anywhere** —
neither runner is invoked with coverage flags and no threshold is configured. Its
pipeline gates on tests alone. See
[Testing](../norm-editor/developer/testing.md) for what those tests are and what the
pipeline actually blocks.
