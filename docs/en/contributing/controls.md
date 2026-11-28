---
scope: cross-cutting
verified:
  date: 2026-11-28
  against:
    CPSV Editor: "4ec37df"
    Linked Data Explorer: "6ce7df8"
    RONL Business API: "f267d7a"
    CPRMV: "ebf7def"
    Norm Editor: "fed2de3"
---

# Controls at a Glance

One matrix of every control in the five repositories. Each row links to the page and section that explains the
mechanism, names its files and lists its limits; a cell says only whether and where the control holds.

## The matrix

| Control | CPSV Editor | Linked Data Explorer | RONL Business API | CPRMV | Norm Editor |
|---|---|---|---|---|---|
| [Pull request required into `acc` and `main`](branch-protection.md#what-blocks-a-merge) | required | required | required | required | not in place |
| [Required checks on `acc`](branch-protection.md#what-blocks-a-merge) | 4, with build | 6, with builds | 7, with builds | 4, with test | no `acc` |
| [Required checks on `main`](branch-protection.md#what-blocks-a-merge) | audit, scan | audit, scan | audit, scan | audit, scan, test, build | not in place |
| [Actions pinned by hash](supply-chain.md#what-is-pinned-per-repository) | all | all | all | all | no Actions |
| [Images by digest](supply-chain.md#what-is-pinned-per-repository) | none built | none built | mostly | all | by tag |
| [Lockfile with integrity or hashes](supply-chain.md#how-it-works) | npm integrity | npm integrity | npm integrity | pip hashes | partial |
| [Renovate, 14-day minimum age](supply-chain.md#renovate-per-repository) | 14 days | 14 days | 14 days | 14 days | not in place |
| [Package-manager cooldown (`.npmrc`)](supply-chain.md#the-cooldown-stops-at-the-manifest) | 14 days | 14 days | 14 days | not in place | not in place |
| [CI cooldown on lockfile versions](dependency-scanning.md#the-cooldown-on-lockfile-versions) | required on `acc` | required on `acc` | required on `acc`, daily proof | not in place | not in place |
| [Dependency register gate](dependency-scanning.md#a-new-direct-dependency-needs-a-register-entry) | required on `acc` | required on `acc` | required on `acc` | not in place | not in place |
| [Dependency audit](dependency-scanning.md#when-the-scans-run) | daily, npm | daily, npm | daily, npm | daily, pip-audit | not in place |
| [Registry signatures](dependency-scanning.md#when-the-scans-run) | in `audit` | in `audit` | in `audit` | hashes instead | not in place |
| [Quarterly dependency review](dependency-scanning.md#when-the-scans-run) | quarterly | quarterly | quarterly | not in place | not in place |
| [Semgrep](dependency-scanning.md#when-the-scans-run) | required, both | required, both | required, both | required, both | not in place |
| [Per-file coverage floor](coverage-floor.md#coverage-floors) | 80% branches | 80% branches | 80% branches | no coverage | no coverage |
| [Tests before deploy](coverage-floor.md#per-repository) | ACC and PROD | ACC and PROD | ACC and PROD | ACC and stable | before image build |
| [End-to-end tests in CI](coverage-floor.md#per-repository) | by hand | none | PA demo only | none | none |
| [Lint, format, type check in CI](code-standards.md#per-repository) | lint, format | all three | all three | shellcheck only | not in place |
| [Git hooks](code-standards.md#per-repository) | Husky | Husky | Husky | not in place | opt-in, commit messages |
| [Build id on the running app](build-provenance.md#per-repository) | changelog tab | changelog | changelog, footer | no frontend | not in place |
| [`/health` build stamp](build-provenance.md#per-repository) | no backend | deploy waits | deploy waits | deploy waits | not in place |
| [Provenance attestation](build-provenance.md#cprmvs-image) | not in place | not in place | not in place | image, in GHCR | not in place |
| [Release SBOM](build-provenance.md#release-sboms) | every release | every release | every release | every release | not in place |
| [GitLab mirror](the-gitlab-mirror.md#per-repository) | at a release | at a release | at a release | `main`, publishes | GitLab is home |

## Legend

| Cell | Means |
|---|---|
| required | a GitHub ruleset makes it a condition of merging (a pull request, or a named status check) |
| required on `acc` | a required check on `acc`; `main` changes only by promotion of commits that passed it |
| required, both | a required check on `acc` and on `main` |
| 4, with build | the number of required checks on `acc`, of which the deploy build or test jobs are part; the names are on [Branches & Promotion](branch-protection.md#what-blocks-a-merge) |
| in `audit` | a step of the required `audit` job |
| daily, quarterly | a scheduled workflow that opens or updates an issue; it does not block a merge |
| mostly, partial | in place for some inputs and not for others; the row's page names which |
| by hand | the suite exists and is run by a person, not by CI |
| not in place | no such mechanism at the verified head |
| no `acc`, no Actions, none built, no frontend, no backend | the control has nothing to apply to |

## What none of these cover

- **No one else has to look.** Every ruleset requires 0 approvals, so the author can merge their own pull request
  once the checks pass ([Branches & Promotion](branch-protection.md#what-it-does-not-cover)).
- **`main` takes the scanners' word.** In the three applications the promotion pull request requires `audit` and
  `scan` only; the production build and its tests run after the merge, and a red run stops the deploy without
  undoing the merge ([Tests & Coverage Gates](coverage-floor.md#what-it-does-not-cover)).
- **A green check on a stale base.** No ruleset requires a branch to be up to date, so two pull requests that each
  pass can combine into a state neither was checked in ([Dependencies](dependency-scanning.md#what-it-does-not-cover)).
- **A pull request runs its own copy of the gates.** The workflows and scripts that check a pull request come from
  that pull request, so a change can weaken a gate; it shows only in the diff.
- **The hosting platform floats.** The Static Web Apps upload container, the hosted runner image and the App Service
  Node runtime are named by a tag, a release or a major, not pinned
  ([Pinning](supply-chain.md#what-this-does-not-protect)).
- **Nothing runs on GitLab.** The mirrors carry the same commits without any of these gates, and the Norm Editor,
  which lives there, has none of the GitHub controls ([The GitLab Mirror](the-gitlab-mirror.md#what-it-does-not-cover)).
