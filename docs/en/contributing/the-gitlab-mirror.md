---
scope: cross-cutting
verified:
  date: 2026-09-12
  against:
    CPSV Editor: "f5bae6a"
    Linked Data Explorer: "be6bc54"
    RONL Business API: "311d732"
---

# The GitLab Mirror

*The one control that cannot run in CI*

Every CI gate in this documentation — [pinning](supply-chain.md),
[scanning](dependency-scanning.md), the [coverage floor](coverage-floor.md) and the
[rulesets](branch-protection.md) that require them — runs on GitHub Actions. The
applications are also mirrored by hand to the open-regels.nl GitLab instance, and
**the mirror is outside all of them**. It stays outside: each merge leaves it behind
until someone pushes.

What changed on 12 September 2026 is that something now *notices*. A release-time check,
`scripts/check-mirror.sh`, runs in all three repositories from step 8 of `/bump-release`
and compares each remote-tracking ref with the mirror's. **It closes the observation half
of the problem, not the drift.** It cannot run in CI, and that is a property of the mirror
rather than a shortcoming of the check: the `gitlab` remote lives in `.git/config` and no
tracked file names the host, so a runner has no such remote and no route to it. It also
never pushes — it prints the exact command and stops, because writing to a shared remote
is a decision for a person.

Its output separates the two cases that a commit count cannot, and it prints the
remote-tracking form rather than the local branch, which drifts. All four of its paths —
match, behind, diverged, missing — were exercised against a scratch bare repository rather
than assumed.

On 12 September 2026, by `git ls-remote` against both remotes:

| Repository | `acc` | `main` |
|---|---|---|
| CPSV Editor | ✅ `f7fe80f` on both | ✅ `f5bae6a` on both |
| Linked Data Explorer | ✅ `1babd54` on both | ✅ `be6bc54` on both |
| RONL Business API | ✅ `28e1a9e` on both | ✅ `311d732` on both |

A tick is *synced at the last check*, not *kept in sync*. The RONL Business API's mirror
had never been audited before that day, and both branches turned out to be strict
ancestors — `acc` eight commits behind and `main` one hundred and eighty-four — so two
fast-forwards reconciled it. It then drifted three more times the same day, as each
promotion pull request merged, which is the behaviour the check exists to surface.

## Behind is not the same as diverged

One command separates the two cases before anything is pushed:

```bash
git merge-base --is-ancestor gitlab/<branch> origin/<branch>
```

An ancestor means a fast-forward, and reconciliation is one push. Anything else means the
mirror holds commits GitHub has never seen. Commit counts alone do not tell the two
apart — *"253 behind"* and *"18 ahead and 306 behind"* both read as *stale*. And push the
**remote-tracking** ref, not the local branch, which drifts:

```bash
git push gitlab origin/acc:refs/heads/acc
git push gitlab origin/main:refs/heads/main
```

## What the CPSV Editor's divergence turned out to be

The CPSV Editor's GitLab `main` had not moved since **4 March 2026** while GitHub moved on,
and it carried **18 commits GitHub had never seen**. By the repository's own record,
seventeen were cross-remote merges with no content of their own. The trees disagreed by
more than that: files existed on GitLab and on no GitHub branch at all — most of them
Create React App leftovers the Vite migration had removed on purpose, and **two example
TTLs that existed nowhere on GitHub**, neither on `main` nor on `acc`. They had been
committed with a CI-skip marker, which is how they came to be on one remote and not the
other without anything noticing.

**Compare trees, not commit counts.** Eighteen commits ahead was almost entirely noise;
filtering `git diff --name-status origin/main gitlab/main` to additions is what found the
two files that mattered. Check each result against *every* branch on the other remote,
not just the matching one.

The reconciliation, in the order that keeps content safe on both remotes:

1. **Land the missing content on GitHub** — v2026.09.3 recovered the two files by
   cherry-picking the commit that restores them, not by merging a branch based on the
   stale remote.
2. **Push `acc` to the mirror first**, so the files exist on GitLab outside the branch
   about to be overwritten.
3. **Archive the ref being replaced** — `archive/gitlab-main-2026-09-09` still holds
   `15a7d17` on the mirror, so the operation is reversible.
4. **Reset with `--force-with-lease=main:<old-sha>`**, naming the SHA, so the push refuses
   if anything moved underneath. Before it, confirm every file about to disappear has a
   successor.

!!! warning "A skip marker in a commit message switches every gate off"
    GitHub Actions honours `[skip ci]`, `[ci skip]`, `[no ci]`, `[skip actions]` and
    `[actions skip]` **anywhere in a commit message**, including in prose that only
    discusses them. That is how the two files bypassed every check, and it is a signal
    that something skipped review rather than a convenience for documentation — use
    `paths-ignore` to express *"this change does not need a deploy"* without switching
    the gates off. See [Code Standards](code-standards.md#ci) for why the symptom is
    silence rather than red.
