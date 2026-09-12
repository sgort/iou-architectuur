---
scope: cross-cutting
verified:
  date: 2026-09-12
  against:
    CPSV Editor: "f5bae6a"
    Linked Data Explorer: "be6bc54"
    RONL Business API: "311d732"
---

# Branch Protection

*What blocks a merge, and what only reports*

Running a check and being able to block on it are different things. This page covers the
second: the branch rulesets, which checks each one requires, and the settings that decide
how a merge is allowed to land. The checks themselves are documented on their own pages —
[Supply-Chain Pinning](supply-chain.md), [Dependency Scanning](dependency-scanning.md) and
the [Coverage Floor](coverage-floor.md) — and the
[controls index](controls.md) is the one-page summary of where each holds.

## What blocks a merge

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

## What makes it enforcement

A workflow that runs but cannot block is advice. The ruleset converts it into a
gate. In all three adopting repositories the ruleset is named **`acc
supply-chain gate`**, targets `refs/heads/acc`, and is `active` with **zero
bypass actors**:

- `required_status_checks` → context **`audit`** — and, in the CPSV Editor and
  the Linked Data Explorer since v2026.09.3, **`scan`** as well
- `pull_request` → `required_approving_review_count: 0`

The Linked Data Explorer also has a twin, `main promotion gate`, on `main` — see
[Adoption status](supply-chain.md#adoption-status).

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
