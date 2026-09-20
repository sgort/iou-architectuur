---
scope: cross-cutting
verified:
  date: 2026-09-20
  against:
    CPSV Editor: "1868087"
    Linked Data Explorer: "0e7733e"
    RONL Business API: "6ca80f2"
---

# Branch Protection

*What blocks a merge, and what only reports*

Running a check and being able to block on it are different things. This page covers the
second: the branch rulesets, which checks each one requires, and the settings that decide
how a merge is allowed to land. The checks themselves are documented on their own pages —
[Supply-Chain Pinning](supply-chain.md), [Dependency Scanning](dependency-scanning.md) and
the [Coverage Floor](coverage-floor.md) — and the
[controls index](controls.md) is the one-page summary of where each holds.

All three repositories' rulesets were read from the API on 20 September 2026, and **all
three `acc` rulesets moved on 19 September**: each now requires the build and deploy
checks alongside `audit` and `scan`, so a red test suite blocks a merge to `acc` rather
than only stopping the deploy. The `main` rulesets did not move. What made that possible
was not a ruleset edit alone — see
[How a path-filtered workflow became requireable](#how-a-path-filtered-workflow-became-requireable).

## What blocks a merge

Running a check and being able to block on it are different things, and until August
2026 these repositories only did the first. **All three** now carry a branch ruleset
named `acc supply-chain gate`, active on `refs/heads/acc` with **no bypass actors**.
All three share the two rules that matter:

- `required_status_checks` → the `audit` context must pass, and since 19 September 2026
  `scan` and each repository's build/deploy checks alongside it
- `pull_request` → a pull request is required (0 approvals; these repositories have a
  single maintainer, and GitHub does not permit self-approval)

Both rules are needed together — requiring the status check alone would still let a
direct push to `acc` sail past it. The practical effect is that **`git push origin acc`
is rejected outright** in all three repositories, including for releases and including
for the repository owner. Linked Data Explorer adopted the same ruleset in v2026.08.7;
all three are named `acc supply-chain gate` and carry zero bypass actors.

They are not identical in shape. Read per ruleset from the API on 20 September 2026:

| | `acc` | `main` |
|---|---|---|
| CPSV Editor | pull request, `audit`, `scan`, `Build and deploy ACC` | a pull request, no status checks |
| Linked Data Explorer | pull request, `audit`, `scan`, `deploy`, `Build and Deploy Frontend`, `Build and Deploy ROPA Site`, deletion, non-fast-forward | pull request, `audit`, `scan`, deletion, non-fast-forward |
| RONL Business API | pull request, `audit`, `scan`, `build`, `Build and Deploy ACC Frontend`, `Build and Deploy ACC PA Demo`, `Build and Deploy ACC Public Site`, deletion, non-fast-forward | pull request, `audit`, deletion, non-fast-forward |

**Two of the three now gate `main`.** The Linked Data Explorer's `main promotion gate`
came first, on 9 September 2026; the RONL Business API created its own on 12 September,
before the promotion pull request was opened, replacing a classic protection under which
an administrator could push to `main` directly — so the branch that deploys production
had been the *less* protected of its two.

**Each `main` ruleset used to mirror its `acc` twin, and no longer does.** Until
19 September the two differed in exactly one parameter:
`require_extra_approval_for_unattributed_changes` is `true` on `acc` and `false` on
`main`, because a promotion carries commits under several author identities against a
ruleset requiring zero approvals, and the flag would demand an approval nobody can give.
That difference stands. What joined it is the build checks, which were added to `acc`
only — so `acc` now requires strictly more than `main` does in both repositories, and
the RONL Business API's `main` still requires `audit` alone, without `scan`. Read the
table rather than assuming symmetry.

The CPSV Editor's `main` requires a pull request but no status checks — **decided and
kept**, not overlooked
([ttl-editor#131](https://github.com/sgort/ttl-editor/issues/131)): `main` is promoted
from `acc`, whose commits already passed `audit` and `scan`. See
[Supply-Chain Pinning](supply-chain.md#adoption-status) for the argument on both sides.

**`scan` is now required on `acc` in all three.** The RONL Business API was the last
holdout: its scan ran on every pull request while the baseline from its first
authenticated scan was triaged, on the reasoning that a gate required before its baseline
is triaged is a gate that gets bypassed in its first week. The triage finished, and the
promotion was — as predicted — a ruleset edit that touched no file. Its `main` still
requires `audit` alone.

Merge strategy is enforced by repository settings rather than by convention: all three
disable squash and rebase merges, leaving merge commits only, with
`delete_branch_on_merge` enabled. Both alternatives rewrite commit hashes — rebase
deceptively so, since it preserves the commit count — and a changelog entry that cites
commits by SHA is orphaned either way.

## What the rulesets still do not require

**A red suite now blocks a merge to `acc` in all three, and still does not block one to
`main`.** This page said the opposite until 19 September 2026, and was right at the time:
the builds and suites ran on every pull request, a red one stopped the deploy, and the
only checks the rulesets named were `audit` and — in two of the three — `scan`. A
dependency pull request whose build failed could be merged.

That was not hypothetical. The RONL Business API's `axios` security update
([#109](https://github.com/sgort/ronl-business-api/pull/109)) broke its backend build:
`axios` 1.18 widened a header type, and one suite stopped compiling while 1,859 tests passed.
It showed as a red check on the pull request — which is what running the suite before the
merge buys — and with `audit` the only required check, nothing more: the pull request stayed
mergeable until the fix landed in v2026.09.7.

What closed it is the build and deploy checks in the table above. Each of those jobs runs
`npm ci`, the linter, the type check where one exists and the unit suites **before** it
builds, so requiring the job requires everything in front of it. On `acc`, a pull request
that breaks a test now has a red required check and no merge button.

**On `main` it is still advice.** The Linked Data Explorer's `main promotion gate`
requires `audit` and `scan`; the RONL Business API's requires `audit`; the CPSV Editor's
`main` requires no status check at all. The deploy checks were deliberately not added
there, for the reason the next section gives: a production deploy workflow that ignores
documentation paths cannot report on a documentation-only promotion, and a required check
that never reports wedges the pull request permanently.

ICTU's guideline asks for more than the check list — that **the entire pipeline** succeeds
before an update merges, and that the transitive changes in a lockfile diff are reviewed on
a risk basis: new runtime packages, new origins, downgrades and licence changes. The first
half is now met on `acc`; **none of the three has tooling for that lockfile review yet.**
The scores are on [ICTU Dependency Guideline](ictu-dependency-guideline.md), recommendation
R9, and the work was tracked in
[linked-data-explorer#119](https://github.com/sgort/linked-data-explorer/issues/119).

## How a path-filtered workflow became requireable

Requiring a build check looks like one ruleset edit and is not, because of a rule that
only bites once the check is required:

> A required status check must **report** on every pull request. A check that never
> reports is not "skipped" — it is pending forever, and the pull request can never merge.

The deploy workflows were all path-filtered, so a pull request touching nothing they watch
started no run and reported no check. Filtering at the trigger and requiring the check are
therefore mutually exclusive — which is why this was open work for as long as it was.

The fix is to move the filter one level down, and it is worth copying verbatim:

- **The trigger loses its `paths:` / `paths-ignore:` on `pull_request`.** The workflow now
  starts for every pull request against its branch. `push` keeps its filter; nothing is
  required on a push.
- **A first job, `changes`, decides relevance.** It asks the API for the pull request's
  changed files and matches them against the same pattern the `push` filter uses, kept in
  step by hand — GitHub Actions has no YAML anchors, so the two copies are maintained
  together. Renames count under both names, as GitHub's own filter does.
- **The build job runs `needs: changes` with an `if:` instead.** A job skipped by its own
  `if:` **reports success**, where a workflow filtered out at its trigger reports nothing
  at all. That difference is the whole mechanism.
- **The condition is fail-safe.** It reads
  `!cancelled() && (needs.changes.result != 'success' || needs.changes.outputs.relevant == 'true')`
  — so the build runs whenever the lookup did *not* succeed, not only when it says
  "relevant". An API failure or a rate limit means a full build, never a free pass.

This landed in all three repositories on 19 September 2026, in the CPSV Editor's
`Deploy ACC (orange-beach)`, the Linked Data Explorer's three `*-acc` workflows and the
RONL Business API's four. Production workflows were left filtered at the trigger and
their checks left un-required, which is why `main` is still ungated on builds.

## What makes it enforcement

A workflow that runs but cannot block is advice. The ruleset converts it into a
gate. In all three adopting repositories the ruleset is named **`acc
supply-chain gate`**, targets `refs/heads/acc`, and is `active` with **zero
bypass actors**:

- `required_status_checks` → context **`audit`**; **`scan`** as well, in the CPSV Editor
  and the Linked Data Explorer since v2026.09.3 and in the RONL Business API since
  19 September 2026; and, since the same date, each repository's **build and deploy
  checks** — the full list is in the table above
- `pull_request` → `required_approving_review_count: 0`

The Linked Data Explorer and the RONL Business API each have a twin, `main promotion
gate`, on `main` — see [Adoption status](supply-chain.md#adoption-status).

Both rules are needed *together*. Requiring the check alone would still let a
direct push to `acc` bypass the gate entirely.

Approvals are `0` because these repositories have a single maintainer and GitHub
does not permit self-approval — requiring `1` would make `acc` unmergeable.
Raise it when a second reviewer exists.

## The merge method is a setting, not a rule

A changelog entry names each commit by its SHA, so any merge strategy that
rewrites hashes orphans every citation in it. The first version of this rule
said *never squash* — and missed that **rebase-and-merge rewrites hashes just as
thoroughly**, deceptively so, because it preserves the commit count while
replacing every hash. That gap surfaced only when someone looked at the actual
merge dropdown.

All three repositories now disable squash and rebase at repository level
(Settings → General → Pull Requests), leaving merge commits only, with
`delete_branch_on_merge` enabled:

```
allow_merge_commit: true    allow_squash_merge: false
allow_rebase_merge: false   delete_branch_on_merge: true
```

GitHub's default button is *Squash and merge*, so without the setting a single
absent-minded click would orphan a release's entire entry. The failure is now
impossible by construction rather than forbidden by prose — which is the general
shape worth copying: **a rule that depends on remembering is a rule that
eventually fails.**

A side effect is that Renovate's dependency pull requests land as merge commits
too. That costs nothing: `--no-merges` already excludes the merge commit from a
changelog range, and the underlying update commit is what an entry should name.

**A repository adopting this template must apply the setting too.** The rule
without it is one click from failing.

---
