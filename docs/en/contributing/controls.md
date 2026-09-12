---
scope: cross-cutting
verified:
  date: 2026-09-12
  against:
    CPSV Editor: "f5bae6a"
    Linked Data Explorer: "be6bc54"
    RONL Business API: "311d732"
---

# Controls at a Glance

Seven pages stand between a change and a deployment: the five controls the
[CI posture deck](ci-posture-deck.md) counts, plus the standards a change is held to on the
way in and the branch rules that make any of it blocking. **One row here, one page** — and
every count, percentage and finding lives on the page that owns it, so there is one place
to correct when a number moves.

## What is enforced, where

| Page | What it answers | CPSV Editor | Linked Data Explorer | RONL Business API |
|---|---|---|---|---|
| [Code Standards](code-standards.md) | Is it linted and formatted before it lands? | hooks · `check-format` in `audit` | hooks · `check-format` in `audit` | hooks · `check-format` in `audit` |
| [Branch Protection](branch-protection.md) | What must pass before a merge can land? | `acc` gated; `main` ungated by decision | `acc` and `main` | `acc` and `main` |
| [Supply-Chain Pinning](supply-chain.md) | Is the pinned digest the version its comment claims? | required on `acc` | required on `acc` and `main` | required on `acc` and `main` |
| [Dependency Scanning](dependency-scanning.md) | Is a known-vulnerable package or pattern shipping? | required on `acc` | required on `acc` and `main` | **runs, not required** |
| [Coverage Floor](coverage-floor.md) | Is every *file* tested, not just the package average? | enforced natively | enforced natively | enforced natively |
| [Build Provenance](build-provenance.md) | Which build is this environment serving? | in place | in place | in place |
| [The GitLab Mirror](the-gitlab-mirror.md) | Does the second copy still match the one the gates run on? | at each release | at each release | at each release |

Read *required* strictly: it means the check is named in a branch ruleset, so the merge
button stays disabled until it reports green. A control that is merely *in place* or *runs*
does real work and blocks nothing by itself.

The deck numbers five of these rows as its controls — build provenance 01, action pin truth
02, the scan 03, the coverage floor 04 and the mirror check 05. The other two rows are not
controls in that sense: **Code Standards** is what a change is held to before any of them
run, and **Branch Protection** is what turns the rest from checks into gates.

## What the rulesets actually require

| | `acc` | `main` |
|---|---|---|
| **CPSV Editor** | pull request · `audit` · `scan` | a pull request, no status checks — [decided](https://github.com/sgort/ttl-editor/issues/131), not overlooked |
| **Linked Data Explorer** | pull request · `audit` · `scan` · no deletion · no force-push | the same four |
| **RONL Business API** | pull request · `audit` · no deletion · no force-push | the same four |

Read from the API on 12 September 2026 with `gh api repos/<owner>/<repo>/rules/branches/<branch>`,
which reports the effective rules from every ruleset at once. Two things this table does not
say, and both matter:

- **The test suites are not in it.** They run on every pull request in all three
  applications, and a red suite stops the deploy — but no ruleset names them, so a red suite
  does not by itself block a merge. See
  [Coverage Floor — a floor only gates where the tests run before the merge](coverage-floor.md#a-floor-only-gates-where-the-tests-run-before-the-merge).
- **`audit` is one check running several things.** Pin truth, the register, formatting and —
  in the RONL Business API — the declarations-only check on `@ronl/shared` all report through
  it. One red cross can mean any of them.

## Where each differs, and why

Three deliberate differences, each decided rather than drifted into:

- **The CPSV Editor's `main` carries no required checks.** It is promoted from `acc`, whose
  commits already passed both, and its production deploy workflow ignores documentation
  paths — so requiring it would wedge any documentation-only promotion permanently
  ([#131](https://github.com/sgort/ttl-editor/issues/131)).
- **The RONL Business API's `scan` is not required yet.** Its first authenticated scan
  returned a large baseline, and a gate required before its baseline is triaged is a gate
  that gets bypassed in its first week. Promotion is a ruleset edit, reversible without
  touching a file.
- **`require_extra_approval_for_unattributed_changes` is `true` on `acc` and `false` on
  `main`** in both repositories whose `main` is gated. A promotion carries commits under
  several author identities against a ruleset requiring zero approvals, so the flag would
  demand an approval nobody can give. Preserved rather than harmonised.

## The fourth and fifth components

The **Norm Editor** runs GitLab CI with its own hook directory and none of the controls
above; see
[Code Standards](code-standards.md#the-norm-editor-is-shaped-differently). The **CPRMV API**
is likewise outside this set. **This documentation repository** has a deliberately deferred
gap of its own: version floors with `>=` and no lockfile, recorded in
[Supply-Chain Pinning](supply-chain.md#what-this-does-not-protect).

## One page owns each number

Each page in the table above is the **only** place its figures live — the pin counts on
Supply-Chain Pinning, the percentages on the Coverage Floor, the findings on Dependency
Scanning, the run numbers on Build Provenance, the drift on The GitLab Mirror. This page
carries enforcement states and no counts at all, so a figure that moves is corrected once
rather than in two places that then disagree.

The [CI Posture Deck](ci-posture-deck.md) is the executive-length version of the same five
controls, and the decision they lead to.
