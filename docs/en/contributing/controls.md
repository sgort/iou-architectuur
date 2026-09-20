---
scope: cross-cutting
verified:
  date: 2026-09-20
  against:
    CPSV Editor: "1868087"
    Linked Data Explorer: "0e7733e"
    RONL Business API: "6ca80f2"
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
| [Dependency Scanning](dependency-scanning.md) | Is a known-vulnerable package or pattern shipping? | required on `acc` | required on `acc` and `main` | required on `acc` |
| [Coverage Floor](coverage-floor.md) | Is every *file* tested, not just the package average? | enforced natively | enforced natively | enforced natively |
| [Build Provenance](build-provenance.md) | Which build is this environment serving? | in place | in place — frontend and backend | in place |
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
| **CPSV Editor** | pull request · `audit` · `scan` · `Build and deploy ACC` | a pull request, no status checks — [decided](https://github.com/sgort/ttl-editor/issues/131), not overlooked |
| **Linked Data Explorer** | pull request · `audit` · `scan` · `deploy` · `Build and Deploy Frontend` · `Build and Deploy ROPA Site` · no deletion · no force-push | pull request · `audit` · `scan` · no deletion · no force-push |
| **RONL Business API** | pull request · `audit` · `scan` · `build` · `Build and Deploy ACC Frontend` · `Build and Deploy ACC PA Demo` · `Build and Deploy ACC Public Site` · no deletion · no force-push | pull request · `audit` · no deletion · no force-push |

Read from the API on 20 September 2026 with `gh api repos/<owner>/<repo>/rules/branches/<branch>`,
which reports the effective rules from every ruleset at once. Three things this table does
not say, and all three matter:

- **The test suites are in it now, on `acc`.** Each build and deploy check runs `npm ci`,
  the linter, the type check where one exists and the unit suites before it builds, so
  requiring the check requires everything in front of it. That changed on 19 September
  2026; until then no ruleset named them and a red suite stopped the deploy without
  blocking the merge. See
  [Coverage Floor — a floor only gates where the tests run before the merge](coverage-floor.md#a-floor-only-gates-where-the-tests-run-before-the-merge).
- **`main` did not move with `acc`.** Every repository now requires strictly more on `acc`
  than on `main`, and a promotion pull request is held to less than the pull requests it
  carries. Read the table rather than assuming the two branches match.
- **`audit` is one check running several things.** Pin truth, the register, formatting and —
  in the RONL Business API — the declarations-only check on `@ronl/shared` all report through
  it. One red cross can mean any of them.

## Where each differs, and why

Three deliberate differences, each decided rather than drifted into:

- **The CPSV Editor's `main` carries no required checks.** It is promoted from `acc`, whose
  commits already passed all three, and its production deploy workflow ignores documentation
  paths — so requiring it would wedge any documentation-only promotion permanently
  ([#131](https://github.com/sgort/ttl-editor/issues/131)).
- **No `main` requires a build check, in any of the three.** The production deploy
  workflows kept their trigger-level path filters, and a required check that never reports
  wedges a pull request forever — see
  [how a path-filtered workflow became requireable](branch-protection.md#how-a-path-filtered-workflow-became-requireable)
  for the mechanism that solved this on `acc` and was deliberately not applied to `main`.
  The RONL Business API's `main` also still omits `scan`.
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

## Measured against ICTU's guideline

ICTU's eleven recommendations for dependency management ask more than the controls above
deliver, and an assessment on 13 September 2026 says where. The scores live on
[ICTU Dependency Guideline](ictu-dependency-guideline.md); this is where each recommendation
is addressed, and what the controls do not yet reach:

| Recommendations | Addressed on | Not yet reached |
|---|---|---|
| R1, R11 — vet before adding; re-check maintenance quarterly | nowhere yet | a written criterion and a scheduled review, in all three |
| R2–R4 — no floating tags, exact pins, hash pins and `npm ci` | [Supply-Chain Pinning](supply-chain.md#what-this-does-not-protect) | the App Service runtime `NODE\|22-lts`, container images, and the RONL Business API's hand-deployed backend. The runner image and **the build that ships** were on this list until 19 September 2026 |
| R5 — internal registry, verified origin | nowhere yet | an ICTU infrastructure question before a repository one |
| R6 — a cooldown of at least 7 days | [Supply-Chain Pinning](supply-chain.md#the-cooldown-stops-at-the-manifest) | the cooldown now exists at the package-manager level too, but `npm ci` ignores it by design and npm older than 11.10 ignores it silently |
| R7, R8 — assess majors; update on a schedule | [Dependency Scanning](dependency-scanning.md#renovate-maintains-dependencies-not-the-tree) | a rule to wait for a major's first patch release |
| R9 — reviewed MR, whole pipeline green, no automerge | [Branch Protection](branch-protection.md#what-the-rulesets-still-do-not-require) | met on `acc` since 19 September 2026; no `main` requires a build or a test, and nothing reviews a lockfile diff |
| R10 — daily audit, including released versions | [Dependency Scanning](dependency-scanning.md#what-nothing-watches-between-merges) | nothing runs on a schedule, and nothing watches `main` |

The finding the assessment ranked first has since been closed. In the CPSV Editor and the
Linked Data Explorer's frontend, **the build that passed the tests was not the build that
shipped** — a vendor container re-resolved the tree on a Node version neither repository
chose. Since 19 September 2026 all three build on the runner and upload the result with
`skip_app_build: true`, so the verified install is the one that produces the deployed
bytes. See [Supply-Chain Pinning](supply-chain.md#what-this-does-not-protect) for what
that leaves open, and
[ICTU Dependency Guideline](ictu-dependency-guideline.md#the-finding-that-was-ranked-first-and-how-it-closed)
for the scores and for what each of the five deployables ships with now. The work was tracked in
[linked-data-explorer#119](https://github.com/sgort/linked-data-explorer/issues/119).

## One page owns each number

Each page in the table above is the **only** place its figures live — the pin counts on
Supply-Chain Pinning, the percentages on the Coverage Floor, the findings on Dependency
Scanning, the run numbers on Build Provenance, the drift on The GitLab Mirror, and the scores
against ICTU's guideline on ICTU Dependency Guideline. This page
carries enforcement states and no counts at all, so a figure that moves is corrected once
rather than in two places that then disagree.

The [CI Posture Deck](ci-posture-deck.md) is the executive-length version of the same five
controls, and the decision they lead to.
