---
scope: cross-cutting
verified:
  date: 2026-09-27
  against:
    CPSV Editor: "a7fe76f"
    Linked Data Explorer: "0143ea2"
    RONL Business API: "702a4f2"
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
    were read at `a7fe76f` (CPSV Editor), `0143ea2` (Linked Data Explorer) and `3c44b9e`
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

**Three weeks carry most of it.** The week of 24–30 August, when Renovate, digest pinning,
zizmor and the first rulesets arrived together; the week of 14–20 September, spent on the
findings of the assessment itself; and the week just ended, which brought monitoring. The
weeks between them are the cadence weeks: updates merging, deferrals written down, nothing
structural.

## Scores

Scale: **0** absent or contradicted · **1** incidental only · **2** partly met, large gaps ·
**3** mostly met, a clear gap · **4** met, a small gap · **5** fully met, and enforced rather
than intended. The superscript is the change since the previous week.

<!-- ictu:scores -->

<!-- ictu:heatmap -->

**The pattern matters more than the ordering.** All three are strongest where tooling does
the work — digest-pinned actions verified by a blocking check, Renovate under a 14-day
cooldown, a build that ships what the tests ran on — and weakest where tooling does not reach
on its own: infrastructure that does not exist here (R5), and a human process that leaves a
written trace (R1, R11). Those have not moved since the first assessment. Monitoring on a
schedule (R10) was the third such place until this week, and it moved as soon as tooling
reached it — which is the pattern, not an exception to it.

## What moved this week

The week of 21–27 September brought monitoring: for the first time, something in each
repository watches the dependencies on a clock rather than when someone pushes.

- **A daily audit of what production runs.** `dependency-audit.yml` runs at 05:17 UTC in all
  three and audits `acc` *and* `main` from each branch's lockfile with
  `npm audit --package-lock-only`. It fails on a high or critical advisory in production
  dependencies, reports the rest without failing, and keeps one tracking issue so a failure
  reaches a person. It ran on schedule on 25 and 26 September in all three. In the CPSV
  Editor and the Linked Data Explorer both runs passed. In the RONL Business API both
  **failed**, correctly: an `adm-zip` high was still on `main`, reached through
  `keycloak-connect`, a dependency declared and imported nowhere. Removing it and promoting
  cleared it, and a dispatched run passed the same afternoon. Dependabot could not have shown
  it — its alerts watch the default branch, `acc`. Its open alerts fell from 8 to 5, none of
  them a production high or critical. That is R10.
- **Every release carries its SBOM.** A CycloneDX document of the production dependencies is
  committed under `docs/sbom/` at each release and uploaded again on the promotion to `main`,
  which fails if the released version has none: `ttl-editor-2026.09.7`,
  `linked-data-explorer-2026.09.8` and `ronl-business-api-2026.09.12` are the latest. Nothing
  analyses them yet. Also R10.
- **No npm major is taken at `X.0.0`.** A Renovate rule in all three excludes `X.0.0` for the
  npm manager, so the earliest a new major can arrive is its first patch, on top of the
  Dependency Dashboard approval that already held it. The majors taken this week arrived that
  way: `concurrently` 10.0.5, `lint-staged` 17.5.1 and `@testing-library/jest-dom` 7.0.1. The
  `ubuntu` 26.04 runner is deferred in all three by a disabled rule with its reason and the
  condition that ends it, and Node 24 in the RONL Business API. That is R7.
- **The RONL Business API's backend deploys from CI.** Both backend workflows stage the root
  `package.json` and `package-lock.json`, run `npm ci --omit=dev --workspace=@ronl/backend`,
  and deploy with `az webapp deploy` over OIDC, closing
  [#34](https://github.com/sgort/ronl-business-api/issues/34). The two hand-run scripts remain
  as a break-glass path, and still install without a lockfile. That is R3 and R4.
- **The RONL Business API's local stack is pinned by digest.** All five images in the root
  `docker-compose.yml` carry a tag and a digest that Renovate maintains. The three compose
  files under `deployment/vm/` are deliberately not pinned — nothing in the repository applies
  them — and Skosmos still runs `:latest` there
  ([#196](https://github.com/sgort/ronl-business-api/issues/196)). R4 moves; R2 does not.
- **The Linked Data Explorer moved to Node 24.21.0.** Its App Services were switched to
  `NODE|24-lts` first and `.nvmrc` second, and each backend deploy now asks the *deployed* app
  to load its native XML binding, so a host on a different major fails the deploy instead of
  passing it. The platform offers majors only, and that is now a recorded decision rather
  than an open question. That is R2 — and it brings the cooldown within reach of the
  repository's own npm (see below).

!!! warning "One gap last week's work introduced, still open"
    In the RONL Business API, the three Static Web App `changes` patterns do not match
    `package-lock.json`. A lock-file maintenance pull request changes nothing else, so all
    three jobs skip — and a skipped job reports success. The update that moves the entire
    transitive tree is therefore the one update that merges with three of its four required
    build checks never having run. This week's lockfile-sync step in `audit` does not close
    it: it proves the lockfile matches the manifests, not that the three apps build on it.

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
| Linked Data Explorer — frontend | `npm ci` on the runner | Oryx's `npm install`, Node 22.22.0 | the runner's build, Node 24.21.0 |
| Linked Data Explorer — backend | `npm ci` on the runner | `npm install --production`, no lockfile | `npm ci --omit=dev` from the root lockfile |
| RONL Business API — frontends | `npm ci` on the runner | the same build, uploaded | unchanged |
| RONL Business API — backend | `npm ci` on the runner | a deploy script on a developer machine, `npm install` without the lockfile | `npm ci --omit=dev` from the root lockfile, deployed by CI ([#34](https://github.com/sgort/ronl-business-api/issues/34), closed) |

The evidence was read from the deploy logs rather than the workflow files:
[Linked Data Explorer run 34612031473](https://github.com/sgort/linked-data-explorer/actions/runs/34612031473)
installed 1,288 packages with `npm ci` on Node 20.20.2 for lint and tests, then logged
`Oryx Version: 0.2.20260109.4`, `Downloading and extracting 'nodejs' version '22.22.0'` and
`Running 'npm install'`.
[CPSV Editor run 34622800899](https://github.com/sgort/ttl-editor/actions/runs/34622800899)
tested on Node 24 and shipped the same way.

All five rows are now closed: every deployable in the three applications ships the install its
tests ran on. The RONL Business API's backend was the last, on 21 September. One route around
it remains — its two hand-run deploy scripts, kept as a break-glass path, still install
without a lockfile — and the repository's own security notes say the exception closes when
they are retired, not when the workflow lands.

## The work, and what is left

The starting position was 13 September 2026; the ticks below are today's. **The checkboxes
live in [linked-data-explorer#119](https://github.com/sgort/linked-data-explorer/issues/119)**,
which remains the tracker — this table says where each item stands as of the latest
assessment.

✅ done · ⬜ open · — not applicable

| Work item | Serves | CPSV Editor | Linked Data Explorer | RONL Business API |
|---|---|:-:|:-:|:-:|
| Build static web apps on the runner, deploy with `skip_app_build: true` | R2–R4 | ✅ | ✅ | ✅ |
| Deploy backends from the lockfile with `npm ci --omit=dev` | R3, R4 | — | ✅ | ✅ |
| Add a cooldown at the package-manager level | R6 | ✅ | ✅ | ✅ |
| Pin the runner image to `ubuntu-24.04` | R2 | ✅ | ✅ | ✅ |
| Pin Node exactly, in one place | R3 | ✅ | ✅ | ✅ |
| Require the build and test checks | R9 | ✅ | ✅ | ✅ |
| Add a daily scheduled dependency audit | R10 | ✅ | ✅ | ✅ |
| Triage open Dependabot alerts: fix, or dismiss with a reason | R10 | — | ⬜ | ⬜ |
| Review transitive changes on dependency pull requests | R9 | ⬜ | ⬜ | ⬜ |
| Pin container images by version and digest | R2, R4 | — | — | ✅¹ |
| Write down criteria for adding a dependency; review maintenance quarterly | R1, R11 | ⬜ | ⬜ | ⬜ |
| Adopt a rule: wait for a major's first or second patch release | R7 | ✅ | ✅ | ✅ |
| Decide on an internal registry or proxy, and on provenance verification | R5 | ⬜ | ⬜ | ⬜ |
| Decide on the floating App Service runtime (`NODE\|24-lts`, `NODE\|22-lts`) | R2 | — | ✅ | ✅ |
| Assess queued majors and record deferrals with reasons | R7 | ✅ | ✅ | ✅ |
| Scan what production runs, not only `acc` | R10 | ✅ | ✅ | ✅ |
| Generate SBOMs for releases | R10 | ✅ | ✅ | ✅ |

¹ The local stack. The compose files under `deployment/vm/` are deliberately not pinned,
because nothing in the repository applies them
([#196](https://github.com/sgort/ronl-business-api/issues/196)); Skosmos still runs `:latest`
there, which is why the RONL Business API's R2 stays at 3.

Eight rows closed this week, and thirteen of the seventeen are now done. What is left divides
cleanly: the Dependabot triage waits on majors already queued — Express 5, Tiptap 3, React
Router 7; the transitive review is pipeline work nobody has started; the criteria and the
quarterly review are decisions to write down rather than code to write; and the registry is
an ICTU infrastructure question before it is a repository one.

The CPSV Editor's triage row is not applicable because it has no open alerts — it is the only
one of the three that has none.

## What the guideline does not measure

The guideline scores how dependencies are managed. It says almost nothing about whether the
code works, and the same weeks hold a great deal of test work that barely registers in
the scores above — the test gates added on 20 August moved exactly one cell, in one
application.

<!-- ictu:tests -->

<!-- ictu:testgates -->

Read the columns as: test files · end-to-end specs · workflows running a suite, of the
workflows in the repository · a per-file coverage floor in the runner configuration.
From 27 September the Linked Data Explorer counts five workflows running a suite rather than
four: its promotion to `main` now runs the 24-check `promotion-targets` harness before it
deploys, and that harness is counted as a suite.

Three things are visible here that the ICTU scores hide. The CPSV Editor's suite grew more
than fourfold, from 15 files to 65, and gained its first end-to-end journeys. Every
repository's CI was running its suites by 23 August — the CPSV Editor's and the Linked Data
Explorer's for the first time. And the per-file 80%
branch floor arrived in all three at once, in the releases of 11 September — a gate that
fails a single file rather than an average, which is the harder promise to keep. Only the
last of these, and only indirectly, touches a cell on this page.

Counted from the tree at each weekly commit: files whose name ends in `.test.*` or `.spec.*`,
end-to-end specs under an `e2e/` directory, the workflows that run a suite, and the runner
configurations carrying a per-file floor. The published test *counts* — how many cases those
files hold — are measured per release on each application's testing page, not here.

## What was verified

Re-checked for this page on 27 September 2026, at the three commits in the stamp, rather than
carried over from the assessment:

- **`runs-on:` in every job of every workflow**: 9 in the CPSV Editor, 18 in the Linked Data
  Explorer, 20 in the RONL Business API — 47 in all — every one `ubuntu-24.04`, none
  `ubuntu-latest`. The remaining 3 and 4 jobs call a reusable workflow and have no `runs-on:`
  of their own. Each repository now has exactly one **`schedule:` trigger**, in
  `dependency-audit.yml`.
- **`skip_app_build`, the build steps and the deploy packaging**, from the workflow files at
  those commits, including both backends' staged `npm ci --omit=dev` — the Linked Data
  Explorer's and, since 21 September, the RONL Business API's.
- **The required status checks per branch**, from the rulesets API. On `acc`: `audit`, `scan`
  and `Build and deploy ACC` in the CPSV Editor; `audit`, `scan`, `deploy`,
  `Build and Deploy Frontend` and `Build and Deploy ROPA Site` in the Linked Data Explorer;
  `audit`, `scan`, `build` and the three ACC deploy checks in the RONL Business API. On
  `main`: `audit` and `scan` in the Linked Data Explorer, `audit` alone in the RONL Business
  API, and no required check at all in the CPSV Editor. None of them requires a branch to be
  up to date with `acc` before merging. See [Branch Protection](branch-protection.md).
- **Every `changes` job's pattern**, against `package-lock.json` specifically — which is how
  the RONL Business API gap above was found.
- **Open Dependabot alerts**: 0 in the CPSV Editor, 3 in the Linked Data Explorer (all
  medium), 5 in the RONL Business API (one high, in a development dependency); none of them
  dismissed with a reason.
- **Renovate pull requests merged in the preceding 30 days**: 23, 26 and 26.
- **The registry origin of every resolved package**: 566, 1,463 and 1,499 entries, every one
  `registry.npmjs.org`. No internal registry, no proxy, no provenance check — R5 stays 0.
- **That npm honours `min-release-age` only from 11.10**, and that Node 22.23.2 bundles npm
  10.9.8 while Node 24.20.0 and 24.21.0 bundle npm 11.19.0. With the Linked Data Explorer on
  24.21.0, that leaves one repository, the RONL Business API, whose own toolchain ignores the
  cooldown silently.
- **The daily audit and its runs**: `dependency-audit.yml`, cron `17 5 * * *`, auditing `acc`
  and `main` in each; scheduled runs on 25 and 26 September, passing in the CPSV Editor and the
  Linked Data Explorer and failing in the RONL Business API on the `adm-zip` high on `main`,
  which a promotion then removed.
- **The release SBOMs**: two per repository under `docs/sbom/` — the CPSV Editor's 2026.09.6
  and .7, the Linked Data Explorer's 2026.09.7 and .8, the RONL Business API's 2026.09.11 and
  .12.
- **The Renovate major rules**: `allowedVersions` excluding `X.0.0` for npm in all three; the
  `ubuntu` major disabled with a reason in all three, and Node 24 in the RONL Business API.
  Pending approval on each Dependency Dashboard: 0, 2 and 17, of which 0, 2 and 12 are majors.
- **Container images in the RONL Business API**: five in the root `docker-compose.yml`, each
  with a tag and a digest; three compose files under `deployment/vm/` with neither, one of them
  on `:latest`.

## What was not verified

- **The scores themselves.** They are a judgement on a 0–5 scale, and several of this week's
  cells are readings rather than facts; a stricter reading would score each one lower, and
  taking every one of them would give 29, 29 and 26 rather than 35, 33 and 31. R7 in all
  three, where the rule that skips `X.0.0` covers npm only and the approval tick leaves no
  written assessment — the RONL Business API still has twelve majors waiting on it, the Linked
  Data Explorer two. R10 in the CPSV Editor and the RONL Business API: two scheduled runs are
  a short record and nothing yet analyses the SBOMs, and the RONL Business API's five open
  alerts stay open without being accepted in writing. The Linked Data Explorer's R2, where
  `NODE|24-lts` still names no exact version and the recorded reason is a deviation rather
  than a pin. The RONL Business API's R3 and R4, where the break-glass scripts still install
  without a lockfile and the VM images carry no digest. R9 in the CPSV Editor and the Linked
  Data Explorer, where transitive changes go unreviewed and no ruleset requires a branch to be
  up to date with `acc` before it merges. The CPSV Editor's R8, the only 5 of the three on
  that recommendation. And, carried from last week, the CPSV Editor's R2, where the only
  unpinned thing left is a vendor container that no longer builds anything; R3 in the CPSV
  Editor and the Linked Data Explorer, where the manifests still hold caret ranges although no
  deploy path re-resolves them; and the RONL Business API's R6, whose own npm ignores the
  cooldown silently.
- **Whether a person reads release notes or checks maintenance** before merging or adding a
  dependency. Nothing in the repositories records it either way, so R1, R9 and R11 score only
  what is recorded.
- **Whether Semgrep Cloud re-evaluates a stored scan** against advisories published after it
  ran.
- **The published test counts and coverage percentages** shown on the applications' own
  testing pages. This page counts test *files* at each weekly commit, which is a different and
  cheaper measurement.
