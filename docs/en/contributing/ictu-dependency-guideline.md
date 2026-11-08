---
scope: cross-cutting
verified:
  date: 2026-11-08
  against:
    CPSV Editor: "34a51b4"
    Linked Data Explorer: "4300700"
    RONL Business API: "c6cf3ac"
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
    — and the work that follows was tracked in
    [linked-data-explorer#119](https://github.com/sgort/linked-data-explorer/issues/119) until
    it closed on 3 October 2026, leaving three issues there. Two have closed since:
    [#248](https://github.com/sgort/linked-data-explorer/issues/248), for R9, on 6 October,
    and [#250](https://github.com/sgort/linked-data-explorer/issues/250), for R1 and R11, on
    10 October. [#249](https://github.com/sgort/linked-data-explorer/issues/249), for R5, is
    still open. The R10 triage is tracked per repository — in the RONL Business API by
    [#311](https://github.com/sgort/ronl-business-api/issues/311), and the risks it accepts in
    [#395](https://github.com/sgort/ronl-business-api/issues/395).

    Every assessment reads each repository's `acc`, the branch of record. The scores below
    were read at `34a51b4` (CPSV Editor), `4300700` (Linked Data Explorer) and `c6cf3ac`
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

**Four weeks carry most of it.** The week of 24–30 August, when Renovate, digest pinning,
zizmor and the first rulesets arrived together; the week of 14–20 September, spent on the
findings of the assessment itself; the week of 21–27 September, which brought monitoring;
and the week of 5–11 October, which gave the human half of the guideline a written trace.
One week went the other way: 19–25 October, when nothing from Renovate had merged for a
fortnight and two daily audits stayed red — the first scores in the series to fall. The other
weeks are cadence weeks: updates merging, deferrals written down, nothing structural.

## Scores

Scale: **0** absent or contradicted · **1** incidental only · **2** partly met, large gaps ·
**3** mostly met, a clear gap · **4** met, a small gap · **5** fully met, and enforced rather
than intended. The superscript is the change since the previous week.

<!-- ictu:scores -->

<!-- ictu:heatmap -->

**The pattern matters more than the ordering.** All three are strongest where tooling does
the work — digest-pinned actions verified by a blocking check, Renovate under a 14-day
cooldown, a build that ships what the tests ran on — and weakest where tooling does not reach
on its own: infrastructure that does not exist here (R5). Monitoring on a schedule (R10) was
such a place until the week of 21–27 September, and the human processes that leave a written
trace (R1, R11) until the week of 5–11 October. Each moved as soon as tooling reached it — a
script that gathers the evidence, then an issue or a comment that asks a person for the
judgement — which is the pattern, not an exception to it. R5 moved that week too, but only by
its provenance half: the registry it asks for is still ICTU's to provide.

## What moved this week

Four Sundays are new since the last pass: 18 and 25 October and 1 November, which had no pass
and were reconstructed afterwards, and 8 November, measured on the day. Between them six cells
moved — five down and one up — and the totals are 41, 39 and 39, against 42, 41 and 40 on
11 October. It is the first time the series has fallen.

- **R8 on 25 October: 5 → 4 in the CPSV Editor, 4 → 3 in the other two.** No Renovate pull
  request merged in any of the three between 10 and 29 October — 24 days in the CPSV Editor,
  whose last merge was on 5 October — and two security updates waited with the rest: `vite` in
  the CPSV Editor ([ttl-editor#214](https://github.com/sgort/ttl-editor/pull/214)) and the MCP
  SDK in the RONL Business API ([#391](https://github.com/sgort/ronl-business-api/pull/391)).
  The weekly merges came back on 29 October and have held since — 10, 7 and 11 in the 30 days
  to 8 November — but the cell has not. Lock-file maintenance, which refreshes the transitive
  tree and earned the CPSV Editor its 5, has not merged there since 1 October, nor in the other
  two since 6 October. Its three pull requests
  ([ttl-editor#196](https://github.com/sgort/ttl-editor/pull/196),
  [linked-data-explorer#301](https://github.com/sgort/linked-data-explorer/pull/301) and
  [ronl-business-api#387](https://github.com/sgort/ronl-business-api/pull/387)) are open, with
  every required check green.
- **R10 on 25 October: 4 → 3 in the Linked Data Explorer and the RONL Business API.** From
  21 October both daily audits failed every day on production highs, and opened
  [linked-data-explorer#305](https://github.com/sgort/linked-data-explorer/issues/305) and
  [ronl-business-api#389](https://github.com/sgort/ronl-business-api/issues/389). Neither had a
  fix or a written acceptance by the Sunday. They closed on 29 and 30 October, when one day's
  triage — a lockfile refresh for advisories, and Node 24.22.1 (22.23.4 in the RONL Business
  API) — cleared them; by then the Linked Data Explorer's audit listed 21 production advisories,
  a `dompurify` critical among them.
- **The RONL Business API's R10 on 8 November: 3 → 4.** A `follow-redirects` high turned both
  audits red again on 31 October. The RONL Business API fixed it on 6 November
  ([#410](https://github.com/sgort/ronl-business-api/issues/410), closed by
  [#417](https://github.com/sgort/ronl-business-api/pull/417)), and
  [#395](https://github.com/sgort/ronl-business-api/issues/395) records what the 29 October
  refresh could not clear — React Router 7's open redirect, accepted until the major, and four
  development-only advisories — the first written acceptance in the series. The Linked Data
  Explorer's [#313](https://github.com/sgort/linked-data-explorer/issues/313) is still open, and
  its audit has failed every day since 31 October.

Several things happened that moved no cell. The first new direct dependency since the
`lockfile-review` checklist arrived, `stylelint` in the RONL Business API
([#376](https://github.com/sgort/ronl-business-api/pull/376), 12 October), was listed with its
five checks and merged with none of them ticked. The VM's Postgres images are now pinned by
digest (`ee73c87`), while the engine-login work of 7 November added Operaton `1.0.0` and two
Caddy images without one. And all three moved Node: the CPSV Editor and the Linked Data
Explorer to 24.22.1, the RONL Business API to 22.23.4.

The cells that held, held for a reason:

- **Nothing moved back on 1 November.** The 29 October clean-up was a catch-up rather than a
  cadence, and two days later the audits were red again.
- **R11 stays 4 in all three.** The quarterly review has not yet run on its own schedule; the
  first slot is 2 January 2027.
- **R1 stays 3.** The checklist has been used once, and not followed — which gives the stricter
  reading a case rather than only an absence.
- **The RONL Business API's R6 stays 4**: its `.nvmrc` now names 22.23.4, which bundles npm
  10.9.9, and npm ignores the cooldown silently below 11.10.

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

The three Sundays of 18 October to 1 November, when no pass ran, were reconstructed the same
way on 8 November, reading each repository's `acc` along its first-parent line: a Renovate
commit dated before a Sunday but merged after it counts from the day it merged. Two sources
were added, because those were the weeks in which they moved: the Dependabot alerts with their
creation and fix dates, and the scheduled runs of the daily audit. Nothing reached any `acc`
between 13 and 29 October, so 18 and 25 October share their heads.

## The finding that was ranked first, and how it closed

The first assessment ranked one finding above the others: **the code that passed the tests
and the code that shipped were produced by different installs, on different Node versions,
inside a container the repository did not choose.** It decided R2, R3 and R4 together.

| | Tested with | Shipped with, on 13 September | Shipped with, today |
|---|---|---|---|
| CPSV Editor | `npm ci` on the runner | Oryx's `npm install`, Node 22.22.0 | the runner's build, Node 24.22.1 |
| Linked Data Explorer — frontend | `npm ci` on the runner | Oryx's `npm install`, Node 22.22.0 | the runner's build, Node 24.22.1 |
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

The starting position was 13 September 2026; the ticks below are today's. The checkboxes
lived in [linked-data-explorer#119](https://github.com/sgort/linked-data-explorer/issues/119)
until it closed on 3 October 2026; each open row now names the issue that carries it. This
table says where each item stands as of the latest assessment.

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
| Triage open Dependabot alerts: fix, or dismiss with a reason ([ronl-business-api#311](https://github.com/sgort/ronl-business-api/issues/311)) | R10 | ⬜ | ⬜ | ⬜ |
| Review transitive changes on dependency pull requests ([#248](https://github.com/sgort/linked-data-explorer/issues/248)) | R9 | ✅ | ✅ | ✅ |
| Pin container images by version and digest | R2, R4 | — | — | ✅¹ |
| Write down criteria for adding a dependency; review maintenance quarterly ([#250](https://github.com/sgort/linked-data-explorer/issues/250)) | R1, R11 | ✅ | ✅ | ✅ |
| Adopt a rule: wait for a major's first or second patch release | R7 | ✅ | ✅ | ✅ |
| Verify registry signatures and provenance in CI ([#249](https://github.com/sgort/linked-data-explorer/issues/249)) | R5 | ✅ | ✅ | ✅ |
| Decide on an internal registry or proxy ([#249](https://github.com/sgort/linked-data-explorer/issues/249)) | R5 | ⬜ | ⬜ | ⬜ |
| Decide on the floating App Service runtime (`NODE\|24-lts`, `NODE\|22-lts`) | R2 | — | ✅ | ✅ |
| Assess queued majors and record deferrals with reasons | R7 | ✅ | ✅ | ✅ |
| Scan what production runs, not only `acc` | R10 | ✅ | ✅ | ✅ |
| Generate SBOMs for releases | R10 | ✅ | ✅ | ✅ |

¹ The local stack: six images in the root `docker-compose.yml`, each with a tag and a digest.
The compose files under `deployment/vm/` are not all pinned, because nothing in the repository
applies them ([#196](https://github.com/sgort/ronl-business-api/issues/196), open). Skosmos
there has been pinned by digest on `:latest` since 30 September 2026 (`62c05a7`), and Postgres
since 6 November (`ee73c87`, from Renovate). Keycloak `23.0`, and the Operaton `1.0.0` and two
Caddy images added for the engine login on 7 November, carry no digest — one Caddy tag,
`2-alpine`, names only a major
([ronl-business-api#433](https://github.com/sgort/ronl-business-api/issues/433)). That holds the
RONL Business API's R3 and R4 back; a stricter reading holds back its R2 as well.

Sixteen of the eighteen rows are done, and none has closed since 11 October. What is left
divides cleanly. The Dependabot triage waits mostly on majors already queued — Tiptap 3 in the
Linked Data Explorer; React Router 7, accepted in
[#395](https://github.com/sgort/ronl-business-api/issues/395) until then, and, for the
development-only `minimatch` high, typescript-eslint v8 in the RONL Business API — and on
development-only mediums. The October criticals (`handlebars`, `shell-quote`) and the
`source-map-js` high were fixed on 29 October. The Linked Data Explorer also has a runtime
`follow-redirects` high open since 5 November. The registry is an ICTU infrastructure question
before it is a repository one.

The CPSV Editor's triage row stays open on one alert, a `minimatch` medium in development
dependencies that arrived on 5 November; its October alerts were fixed on 29 October.

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
deploys, and that harness is counted as a suite. From 11 October the count rises in all three
for the same reason: `dependency-review.yml`, `sbom.yml` and the `lockfile-review` job each
run their script's own tests before using it — tooling tests, not application suites.

Three things are visible here that the ICTU scores hide. The CPSV Editor's suite grew more
than fourfold, from 15 files to 72, and gained its first end-to-end journeys. Every
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

Re-checked for this page on 8 November 2026, at the three commits in the stamp, rather than
carried over from the assessment:

- **`runs-on:` in every job of every workflow**: 12 in the CPSV Editor, 21 in the Linked Data
  Explorer, 23 in the RONL Business API — 56 in all — every one `ubuntu-24.04`, none
  `ubuntu-latest`. The remaining 3 and 4 jobs call a reusable workflow and have no `runs-on:`
  of their own. Each repository has two **`schedule:` triggers**: `dependency-audit.yml`
  daily and `dependency-review.yml` quarterly.
- **`skip_app_build`, the build steps and the deploy packaging**, from the workflow files at
  those commits, including both backends' staged `npm ci --omit=dev` — the Linked Data
  Explorer's and, since 21 September, the RONL Business API's.
- **The required status checks per branch**, from the rulesets API. On `acc`: `audit`, `scan`,
  `Build and deploy ACC` and `lockfile-review` in the CPSV Editor; `audit`, `scan`, `deploy`,
  `Build and Deploy Frontend`, `Build and Deploy ROPA Site` and `lockfile-review` in the Linked
  Data Explorer; `audit`, `scan`, `build`, the three ACC deploy checks and `lockfile-review` in
  the RONL Business API — `lockfile-review` in all three since 6 October 2026. On `main`:
  `audit` and `scan` in all three. None of the six rulesets requires a branch to be up to date
  before merging, none requires an approving review, and no branch keeps classic branch
  protection. See [Branch Protection](branch-protection.md).
- **Every `changes` job's pattern**, against `package-lock.json` specifically. The RONL
  Business API's three Static Web App patterns have named it since `6f79e93` (6 October).
- **Open Dependabot alerts**: 1 in the CPSV Editor (a `minimatch` medium, development); 6 in
  the Linked Data Explorer (at runtime the `follow-redirects` high of 5 November and the
  `@tiptap/core` medium; in development dependencies three mediums and a low); 8 in the RONL
  Business API (two `react-router` mediums at runtime, accepted in
  [#395](https://github.com/sgort/ronl-business-api/issues/395); in development dependencies
  the `minimatch` high, four mediums and a low). None of them is dismissed with a reason.
- **Renovate pull requests merged in the preceding 30 days**, counted by author
  (`app/renovate`) and merge date since 9 October: 10, 7 and 11 — none of them between
  11 and 28 October.
- **The registry origin of every resolved package**: 552, 1,527 and 1,710 entries, every one
  `registry.npmjs.org` (besides 2 and 6 workspace links), none without an `integrity` hash.
  `npm audit signatures` runs in the required `audit` job in all three, through
  `scripts/audit-signatures.sh`. No internal registry and no proxy.
- **That npm honours `min-release-age` only from 11.10**, and that Node 24.22.1 bundles npm
  11.19.1. The CPSV Editor and the Linked Data Explorer pin 24.22.1; the RONL Business API's
  `.nvmrc` names 22.23.4, which bundles npm 10.9.9, so it is the one repository whose own
  toolchain ignores the cooldown silently.
- **The daily audit and its runs**: `dependency-audit.yml`, cron `17 5 * * *`, auditing `acc`
  and `main` in each. Every scheduled run of the CPSV Editor's since 10 October has passed. The
  Linked Data Explorer's failed from 21 to 28 October
  ([linked-data-explorer#305](https://github.com/sgort/linked-data-explorer/issues/305), closed
  29 October) and has failed every day again since 31 October
  ([linked-data-explorer#313](https://github.com/sgort/linked-data-explorer/issues/313), open,
  `follow-redirects`). The RONL Business API's failed from 21 to 29 October
  ([#389](https://github.com/sgort/ronl-business-api/issues/389), closed 30 October) and from
  31 October to 6 November ([#410](https://github.com/sgort/ronl-business-api/issues/410),
  closed by [#417](https://github.com/sgort/ronl-business-api/pull/417)).
- **The quarterly dependency review**: `dependency-review.yml`, cron `23 6 2 1,4,7,10 *`, run by
  hand on 10 October in all three
  ([ttl-editor#210](https://github.com/sgort/ttl-editor/issues/210),
  [linked-data-explorer#290](https://github.com/sgort/linked-data-explorer/issues/290),
  [ronl-business-api#362](https://github.com/sgort/ronl-business-api/issues/362)), each closed
  with an outcome for every flagged package. The schedule has not run yet: its first slot is
  2 January 2027.
- **The release SBOMs** under `docs/sbom/`: six in the CPSV Editor (2026.09.6, .09.7, .10.0,
  .10.1, .10.2 and .11.0), eight in the Linked Data Explorer (2026.09.7, .09.8, .10.0 to .10.3,
  .11.0 and .11.1) and twelve in the RONL Business API (2026.09.11 to .09.15, .10.0 to .10.4,
  .11.0 and .11.1). Since 10 October
  the production set is read from the lockfile, and the two checks in `sbom.yml` run before
  the generate step.
- **The Renovate major rules**: `allowedVersions` excluding `X.0.0` for npm in all three; the
  `ubuntu` major disabled with a reason in all three, and Node 24 in the RONL Business API.
  Pending approval on each Dependency Dashboard on 8 November: 1, 3 and 18, of which 1, 3 and
  13 are majors — Node 26 in the CPSV Editor and the Linked Data Explorer, and
  `react-router-dom` 7, `eslint` 10 and TypeScript 7 among them in the RONL Business API.
- **Container images in the RONL Business API**: six in the root `docker-compose.yml`, each
  with a tag and a digest; of the six compose files under `deployment/vm/`, Skosmos (on
  `:latest`) and Postgres are digest-pinned, as is the Operaton test harness's `curl`, while
  Keycloak `23.0`, Operaton `1.0.0` and Caddy (`2-alpine`, `2.10.2-alpine`) carry no digest.

## What was not verified

- **The scores themselves.** They are a judgement on a 0–5 scale, and several cells are
  readings rather than facts; a stricter reading would score each one lower, and taking every
  one of them would give 32, 31 and 29 rather than 41, 39 and 39. Three are new or sharper
  this week. R10 in all three: in the CPSV Editor, development-only highs waited three weeks
  for a fix the production-only gate did not ask for; in the Linked Data Explorer, the audit
  has been red since 31 October with a fix available, which a stricter reading scores 2; in
  the RONL Business API, the second failure took six days and its acceptance lives in an issue
  rather than on the alerts. The CPSV Editor's R8, where lock-file maintenance has waited 34
  days with every check green. And R1 in all three now has a case rather than an absence: the
  checklist's first new dependency merged with none of its boxes ticked. The rest are carried.
  R5 in all three, where only the provenance half is done and the registry question has not
  been put to ICTU on the record. R11 in all three, where the review ran once, by hand, and the
  schedule has not yet fired. R9 in all three, where no ruleset requires a branch to be up to
  date or a review to approve it. R7 in all three, where the rule that skips `X.0.0` covers npm
  only and the approval tick leaves no written assessment — the RONL Business API has thirteen
  majors waiting on it, the Linked Data Explorer three and the CPSV Editor one. The RONL
  Business API's R2: the Skosmos reference still spells `:latest`, and the new Caddy image
  names only a major. The Linked Data Explorer's R2, where `NODE|24-lts` still names no exact
  version and the recorded reason is a deviation rather than a pin. The RONL Business API's R3
  and R4, where the break-glass scripts still install without a lockfile and the VM's Keycloak,
  Operaton and Caddy images carry no digest. The CPSV Editor's R2, where the only unpinned
  thing left is a vendor container that no longer builds anything. R3 in the CPSV Editor and
  the Linked Data Explorer, where the manifests still hold caret ranges although no deploy path
  re-resolves them. And the RONL Business API's R6, whose own npm ignores the cooldown
  silently.
- **The generous readings not taken.** R9 at 5 in all three, on `lockfile-review` closing
  the transitive-review gap; R8 back at 5, 4 and 4, on the weekly merges that resumed on
  29 October; and the Linked Data Explorer's R10 at 4, on the one-day clean-up of 29 October.
  Taking every generous reading as well would give 43, 42 and 41.
- **Whether a person reads release notes or checks maintenance** before merging or adding a
  dependency. Nothing in the repositories records it either way, so R1, R9 and R11 score only
  what is recorded.
- **Whether Semgrep Cloud re-evaluates a stored scan** against advisories published after it
  ran.
- **The published test counts and coverage percentages** shown on the applications' own
  testing pages. This page counts test *files* at each weekly commit, which is a different and
  cheaper measurement.
