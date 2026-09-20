---
scope: cross-cutting
verified:
  date: 2026-09-20
  against:
    CPSV Editor: "1868087"
    Linked Data Explorer: "0e7733e"
    RONL Business API: "6ca80f2"
---

# ICTU Dependency Guideline

*Eleven recommendations, and where the three applications stand, week by week*

ICTU publishes eleven recommendations for managing dependencies — for everything a build
pulls in, direct and indirect, including the images, hooks and pipeline definitions around
the code. The three applications were first assessed against them on 13 September 2026, and
have been re-assessed every Sunday since. This page owns the **scores**; the mechanisms each
recommendation touches are documented on the control pages, and the
[controls index](controls.md#measured-against-ictus-guideline) maps each recommendation to
the page that covers it.

!!! info "Sources and scope"
    The guideline and the assessment live in the Linked Data Explorer repository —
    [`ICTU-dependencies-guideline.md`](https://github.com/sgort/linked-data-explorer/blob/acc/docs/ICTU-dependencies-guideline.md)
    and
    [`ICTU-dependencies-assessment.md`](https://github.com/sgort/linked-data-explorer/blob/acc/docs/ICTU-dependencies-assessment.md)
    — and the work that follows is tracked in
    [linked-data-explorer#119](https://github.com/sgort/linked-data-explorer/issues/119).

    Every assessment reads each repository's `acc`, the branch of record. The scores below
    were read at `1868087` (CPSV Editor), `0e7733e` (Linked Data Explorer) and `6ca80f2`
    (RONL Business API). Work that has reached `acc` therefore counts before it is promoted
    to `main`.

    This documentation repository is not assessed; its own gap is recorded under
    [Supply-Chain Pinning](supply-chain.md#what-this-does-not-protect).

## The eleven recommendations

| | Recommendation | In short |
|---|---|---|
| | **Adding** | |
| R1 | Vet maintenance before adding a dependency | licence, maintainers, release policy, activity, open security issues |
| | **Specifying** | |
| R2 | No unpinned tags | no `latest`, no tag that does not name a version |
| R3 | Pin at the highest precision | `3.14.5`, not `3.14`; no ranges unless the software is a library |
| R4 | Pin by hash | digests, and a committed lockfile installed with `npm ci` |
| R5 | Use an internal registry or proxy | and verify origin — signed releases, provenance, signed images |
| | **Updating** | |
| R6 | A cooldown of at least 7 days | configured in the tools; skippable for critical security fixes |
| R7 | Assess a major before taking it | wait for the first or second patch release when it is risky |
| R8 | Update periodically, with tools | once a sprint, for instance |
| R9 | Treat an update like any other change | a reviewed merge request, the whole pipeline green, transitive changes reviewed, no automerge |
| | **Monitoring** | |
| R10 | Audit daily, including released versions | `npm audit` or an SBOM; mitigate each finding or explicitly accept it |
| R11 | Re-check maintenance quarterly | the same points as R1 |

The guideline permits deviations, but only for valid reasons — which makes a *written*
reason part of meeting it.

## Progress

Every score on this page, in every table and chart, comes from one file —
`docs/data/ictu-assessments.yml` — rendered at build time. There is one record to correct
when a score is wrong, and no second copy to drift away from it.

<!-- ictu:totals -->

A filled marker is a week scored against the repositories on the day. A hollow one was
reconstructed afterwards from the commits that were on `acc` that Sunday: the shape of the
curve is reliable, an individual cell is worth about ±1. See
[How the earlier weeks were reconstructed](#how-the-earlier-weeks-were-reconstructed).

<!-- ictu:movement -->

**Two weeks carry almost all of it.** The week of 24–30 August, when Renovate, digest
pinning, zizmor and the first rulesets arrived together, and the week just ended, which was
spent on the findings of the assessment itself. The weeks between them are the cadence
weeks: updates merging, deferrals written down, nothing structural.

## Scores

Scale: **0** absent or contradicted · **1** incidental only · **2** partly met, large gaps ·
**3** mostly met, a clear gap · **4** met, a small gap · **5** fully met, and enforced rather
than intended. The superscript is the change since 13 September.

<!-- ictu:scores -->

<!-- ictu:heatmap -->

**The pattern matters more than the ordering.** All three are strongest where tooling does
the work — digest-pinned actions verified by a blocking check, Renovate under a 14-day
cooldown, a build that ships what the tests ran on — and weakest in the three places tooling
does not reach on its own: infrastructure that does not exist here (R5), monitoring on a
schedule (R10), and a human process that leaves a written trace (R1, R11). Those three have
not moved since the first assessment, and nothing in the past week touched them.

## What moved this week

The week of 14–20 September was spent on the assessment's own findings, and it closed the
three that decided the most cells.

- **What ships is now what was tested.** The CPSV Editor and the Linked Data Explorer's
  frontends are built on the runner with `npm ci` and uploaded with `skip_app_build: true`,
  so the vendor container no longer runs an install of its own. The Linked Data Explorer's
  backend deploys 349 packages with `npm ci --omit=dev` against the root lockfile, in place
  of an `npm install` that never saw it. That is R2, R3 and R4 in all three.
- **One exact Node version each, in one place.** `.nvmrc` carries `24.20.0` in the CPSV
  Editor and `22.23.2` in the other two, read by every deploy workflow; each `zizmor.yml`
  keeps its own exact `24.20.0` for the config validator. Three drifting literals in the
  Linked Data Explorer became one file, closing its #113.
- **The runner image is pinned.** All 39 jobs — 7, 15 and 17 — name `ubuntu-24.04`. Not one
  `ubuntu-latest` survives in any workflow of any of the three.
- **The cooldown reaches npm itself.** A root `.npmrc` sets `min-release-age=14` in all
  three, so the weekly lockfile refresh — which Renovate cannot hold to its own cooldown —
  is held back by npm instead. With one measured caveat: `npm ci` ignores the setting by
  design, and npm older than 11.10 ignores it *silently*, which covers Node 22's npm 10.9.8
  in two of the three. `scripts/check-deps.sh` warns when it finds one.
- **A red suite now blocks a merge to `acc`.** The build and test checks are required in all
  three, which needed a mechanism as well as a ruleset: a required check must report on every
  pull request, and a workflow filtered out at its trigger never reports. The filter moved
  into a `changes` job whose `if:` skips the build — and a skipped job reports success.
  `main` is unchanged in all three and remains the weaker branch, deliberately.
- **The RONL Business API's alert backlog collapsed**, from 154 open Dependabot alerts to 8,
  when its first lock-file refresh landed. It was cleared by the refresh rather than by
  triage, and none of the eight is dismissed with a reason, so R10 moves to 2 and no further.

!!! warning "One gap this work introduced, worth more than the scores it cost"
    In the RONL Business API, the three Static Web App `changes` patterns do not match
    `package-lock.json`. A lock-file maintenance pull request changes nothing else, so all
    three jobs skip — and a skipped job reports success. The update that moves the entire
    transitive tree is therefore the one update that merges with three of its four required
    build checks never having run.

    The Linked Data Explorer's backend and frontend patterns both name the lockfile, and the
    CPSV Editor filters by exclusion, so neither has the hole. It is the reason the RONL
    Business API scores 3 on R9 where the other two score 4.

<!-- ictu:changes -->

## How the earlier weeks were reconstructed

The first assessment was made on 13 September, after most of the work had already happened.
The four earlier Sundays were reconstructed afterwards, so that the series starts where the
work did rather than where the measuring did.

Each was scored from the last commit on each repository's `acc` that day, reading the same
evidence the live assessment reads: `renovate.json`, every workflow file, `.nvmrc`, the
rulesets and their creation dates, and the Renovate pull requests merged in the preceding 30
days. The method was calibrated against the week that was measured: run over the 13 September
window it reproduces that day's counts exactly.

What a reconstruction cannot recover is what someone knew or decided at the time, so R1, R7,
R9 and R11 are scored only from what a repository records. The least certain cells are the
monitoring ones in the two August weeks, where the date Dependabot alerts were switched on is
inferred from the oldest surviving alert. Treat a single reconstructed cell as ±1 and the
totals as ±2; the curve is not in doubt.

## The finding that was ranked first, and how it closed

The first assessment ranked one finding above the others: **the code that passed the tests
and the code that shipped were produced by different installs, on different Node versions,
inside a container the repository did not choose.** It decided R2, R3 and R4 together.

| | Tested with | Shipped with, on 13 September | Shipped with, today |
|---|---|---|---|
| CPSV Editor | `npm ci` on the runner | Oryx's `npm install`, Node 22.22.0 | the runner's build, Node 24.20.0 |
| Linked Data Explorer — frontend | `npm ci` on the runner | Oryx's `npm install`, Node 22.22.0 | the runner's build, Node 22.23.2 |
| Linked Data Explorer — backend | `npm ci` on the runner | `npm install --production`, no lockfile | `npm ci --omit=dev` from the root lockfile |
| RONL Business API — frontends | `npm ci` on the runner | the same build, uploaded | unchanged |
| RONL Business API — backend | `npm ci` on the runner | a deploy script on a developer machine, `npm install` without the lockfile | unchanged ([#34](https://github.com/sgort/ronl-business-api/issues/34)) |

The evidence was read from the deploy logs rather than the workflow files:
[Linked Data Explorer run 34612031473](https://github.com/sgort/linked-data-explorer/actions/runs/34612031473)
installed 1,288 packages with `npm ci` on Node 20.20.2 for lint and tests, then logged
`Oryx Version: 0.2.20260109.4`, `Downloading and extracting 'nodejs' version '22.22.0'` and
`Running 'npm install'`.
[CPSV Editor run 34622800899](https://github.com/sgort/ttl-editor/actions/runs/34622800899)
tested on Node 24 and shipped the same way.

Four of the five rows are now closed. The fifth is the RONL Business API's backend, which is
still assembled and installed by hand, without a lockfile — the one deployable in the three
applications where a version range still decides what runs in production.

## The work, and what is left

The starting position was 13 September 2026; the ticks below are today's. **The checkboxes
live in [linked-data-explorer#119](https://github.com/sgort/linked-data-explorer/issues/119)**,
which remains the tracker — this table says where each item stands as of the latest
assessment.

✅ done · ⬜ open · — not applicable

| Work item | Serves | CPSV Editor | Linked Data Explorer | RONL Business API |
|---|---|:-:|:-:|:-:|
| Build static web apps on the runner, deploy with `skip_app_build: true` | R2–R4 | ✅ | ✅ | ✅ |
| Deploy backends from the lockfile with `npm ci --omit=dev` | R3, R4 | — | ✅ | ⬜ |
| Add a cooldown at the package-manager level | R6 | ✅ | ✅ | ✅ |
| Pin the runner image to `ubuntu-24.04` | R2 | ✅ | ✅ | ✅ |
| Pin Node exactly, in one place | R3 | ✅ | ✅ | ✅ |
| Require the build and test checks | R9 | ✅ | ✅ | ✅ |
| Add a daily scheduled dependency audit | R10 | ⬜ | ⬜ | ⬜ |
| Triage open Dependabot alerts: fix, or dismiss with a reason | R10 | — | ⬜ | ⬜ |
| Review transitive changes on dependency pull requests | R9 | ⬜ | ⬜ | ⬜ |
| Pin container images by version and digest | R2, R4 | — | — | ⬜ |
| Write down criteria for adding a dependency; review maintenance quarterly | R1, R11 | ⬜ | ⬜ | ⬜ |
| Adopt a rule: wait for a major's first or second patch release | R7 | ⬜ | ⬜ | ⬜ |
| Decide on an internal registry or proxy, and on provenance verification | R5 | ⬜ | ⬜ | ⬜ |
| Decide on the floating App Service runtime `NODE\|22-lts` | R2 | — | ⬜ | ⬜ |
| Assess queued majors and record deferrals with reasons | R7 | ✅ | ⬜ | ⬜ |
| Scan what production runs, not only `acc` | R10 | ⬜ | ⬜ | ⬜ |
| Generate SBOMs for releases | R10 | ⬜ | ⬜ | ⬜ |

Six rows closed in one week. What is left divides cleanly: the RONL Business API's backend
deploy and its container images are repository work; the daily audit, the transitive review
and SBOMs are pipeline work nobody has started; the criteria, the quarterly review and the
major-version rule are decisions to write down rather than code to write; and the registry
is an ICTU infrastructure question before it is a repository one.

The CPSV Editor's triage row is not applicable because it has no open alerts — it is the only
one of the three that has none.

## What the guideline does not measure

The guideline scores how dependencies are managed. It says almost nothing about whether the
code works, and the same eleven weeks hold a great deal of test work that barely registers in
the scores above — the test gates added on 20 August moved exactly one cell, in one
application.

<!-- ictu:tests -->

<!-- ictu:testgates -->

Read the columns as: test files · end-to-end specs · workflows running a suite, of the
workflows in the repository · a per-file coverage floor in the runner configuration.

Three things are visible here that the ICTU scores hide. The CPSV Editor's suite grew more
than fourfold, from 15 files to 65, and gained its first end-to-end journeys. Every
repository's CI began running the suites in the week of 20 August. And the per-file 80%
branch floor arrived in all three at once, in the releases of 11 September — a gate that
fails a single file rather than an average, which is the harder promise to keep. Only the
last of these, and only indirectly, touches a cell on this page.

Counted from the tree at each weekly commit: files whose name ends in `.test.*` or `.spec.*`,
end-to-end specs under an `e2e/` directory, the workflows that run a suite, and the runner
configurations carrying a per-file floor. The published test *counts* — how many cases those
files hold — are measured per release on each application's testing page, not here.

## What was verified

Re-checked for this page on 20 September 2026, at the three commits in the stamp, rather than
carried over from the assessment:

- **`runs-on:` in every job of every workflow**: 7 in the CPSV Editor, 15 in the Linked Data
  Explorer, 17 in the RONL Business API, all `ubuntu-24.04`, none `ubuntu-latest`. And still
  **no `schedule:` trigger** in any workflow of any of the three, which is why R10 does not
  move.
- **`skip_app_build`, the build steps and the deploy packaging**, from the workflow files at
  those commits, including the Linked Data Explorer's staged `npm ci --omit=dev`.
- **The required status checks per branch**, from the rulesets API. On `acc`: `audit`, `scan`
  and `Build and deploy ACC` in the CPSV Editor; `audit`, `scan`, `deploy`,
  `Build and Deploy Frontend` and `Build and Deploy ROPA Site` in the Linked Data Explorer;
  `audit`, `scan`, `build` and the three ACC deploy checks in the RONL Business API. On
  `main`: `audit` and `scan` in the Linked Data Explorer, `audit` alone in the RONL Business
  API, and no required check at all in the CPSV Editor. See
  [Branch Protection](branch-protection.md).
- **Every `changes` job's pattern**, against `package-lock.json` specifically — which is how
  the RONL Business API gap above was found.
- **Open Dependabot alerts**: 0 in the CPSV Editor, 3 in the Linked Data Explorer, 8 in the
  RONL Business API; none dismissed with a reason in any of the three.
- **Renovate pull requests merged in the preceding 30 days**: 22, 18 and 20.
- **The registry origin of every resolved package**: 567, 1,484 and 1,394 entries, every one
  `registry.npmjs.org`. No internal registry, no proxy, no provenance check — R5 stays 0.
- **That npm honours `min-release-age` only from 11.10**, and that Node 22.23.2 bundles npm
  10.9.8 while Node 24.20.0 bundles npm 11.19. This was listed as unverified on 13 September;
  it is now measured, and it is why R6 reaches 4 rather than 5.

## What was not verified

- **The scores themselves.** They are a judgement on a 0–5 scale. Three of this week's cells
  are readings rather than facts, and a stricter reading would score them lower: the CPSV
  Editor's R2, where the only unpinned thing left is a vendor container that no longer builds
  anything; R3 in two applications, where the manifests still hold caret ranges although no
  deploy path re-resolves them; and the RONL Business API's R6, whose backend deploy the
  cooldown does not reach — counted once, against R3 and R4, rather than three times.
- **Whether a person reads release notes or checks maintenance** before merging or adding a
  dependency. Nothing in the repositories records it either way, so R1, R9 and R11 score only
  what is recorded.
- **Whether Semgrep Cloud re-evaluates a stored scan** against advisories published after it
  ran.
- **The published test counts and coverage percentages** shown on the applications' own
  testing pages. This page counts test *files* at each weekly commit, which is a different and
  cheaper measurement.
