---
scope: cross-cutting
verified:
  date: 2026-11-22
  against:
    CPSV Editor: "3ba847f"
    Linked Data Explorer: "fe841f9"
    RONL Business API: "be0a1f0"
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
    were read at `3ba847f` (CPSV Editor), `fe841f9` (Linked Data Explorer) and `be0a1f0`
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

One Sunday is new since the last pass, 22 November, measured on the day. No cell moved, and
the totals stay 42, 40 and 40.

Several things happened that moved no cell. The RONL Business API cleared most of its
Dependabot alerts by hand: on 17 November
[#469](https://github.com/sgort/ronl-business-api/pull/469) fixed the seven runtime `hono` and
`@hono/node-server` alerts and the `fast-xml-parser` low, two development mediums
(`postcss-selector-parser` and `minimatch`) were dismissed on the alert as a tolerable risk with
a written reason, and [#470](https://github.com/sgort/ronl-business-api/pull/470) gave its
`SECURITY-PIPELINE.md` a register, *Semgrep findings we accept, and why*, with a reason and a
revisit trigger for each of the three alerts it keeps open. Its fourteen open alerts of
15 November are three. `tsx` entered the Linked Data Explorer's backend, replacing `ts-node`,
listed by `lockfile-review` with its checks and merged with none of them ticked. The Linked
Data Explorer's daily audit went red once, on 18 November, on a `picomatch` high whose advisory
GitHub withdrew that afternoon; the next run closed
[linked-data-explorer#345](https://github.com/sgort/linked-data-explorer/issues/345) with no
commit in between. The CPSV Editor and the Linked Data Explorer took `zizmor-action` v0.8.1,
which installs zizmor from hash-locked wheels; that is inside the action, and Semgrep's
`pip install` still has no `--require-hashes`, so R4 does not move. The RONL Business API's own
bump ([ronl-business-api#461](https://github.com/sgort/ronl-business-api/pull/461)) is held by
the register check until its row is updated — the gate working, evidence for R9 rather than a
move.

The cells that held, held for a reason:

- **R8 holds in all three, and is the cell to watch.** Lock-file maintenance opened again on
  Monday 16 November ([ttl-editor#253](https://github.com/sgort/ttl-editor/pull/253),
  [linked-data-explorer#343](https://github.com/sgort/linked-data-explorer/pull/343) and
  [ronl-business-api#458](https://github.com/sgort/ronl-business-api/pull/458)), and all three
  were still open on the Sunday, six days old: every required check green, only Renovate's own
  `stability-days` status pending, which no ruleset requires. The CPSV Editor merged a weekly
  batch of six other Renovate pull requests on 21 November and the Linked Data Explorer four on
  22 November; the RONL Business API merged none, its last on 12 November. If nothing from
  Renovate merges there by about 26 November, the precedent of 25 October — more than a
  fortnight with nothing merged — applies, and its R8 falls to 3.
- **The RONL Business API's R10 stays 4.** Each alert it had on 15 November is now fixed,
  dismissed with a reason or accepted in writing, and every scheduled audit from 15 to 21 November passed. But
  three alerts, one of them high, stay open on purpose, and nothing checks the register against
  the open alerts: the acceptance is written, not enforced.
- **The Linked Data Explorer's R10 stays 3.** Its one red run was on an advisory withdrawn the
  same day, but its three open alerts are neither dismissed nor accepted in writing.
- **R11 stays 4 in all three.** The quarterly review has not yet run on its own schedule; the
  first slot is 2 January 2027.
- **R1 stays 3.** The checklist has now been used for seven new direct dependencies, in four
  pull requests, and not followed in any: none of its thirty-five boxes is ticked — which gives
  the stricter reading a growing case rather than only an absence.
- **The RONL Business API's R6 stays 4**: its `.nvmrc` still names 22.23.4, which bundles npm
  10.9.9, and npm ignores the cooldown silently below 11.10. The move to 24.22.2 reached its
  tooling workflows only.

The table gives the reasons for the cells that moved in the last three passes, newest first.
Weeks without a pass, reconstructed afterwards, are left out; their moves are described above,
and every reason for every week stays in `docs/data/ictu-assessments.yml`.

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
| CPSV Editor | `npm ci` on the runner | Oryx's `npm install`, Node 22.22.0 | the runner's build, Node 24.22.2 |
| Linked Data Explorer — frontend | `npm ci` on the runner | Oryx's `npm install`, Node 22.22.0 | the runner's build, Node 24.22.2 |
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
The compose files under `deployment/vm/` are applied by hand on the VMs, not by any workflow
([#196](https://github.com/sgort/ronl-business-api/issues/196), open). Skosmos there has been
pinned by digest on `:latest` since 30 September 2026 (`62c05a7`), Postgres since 6 November
(`ee73c87`) and the production Operaton `1.0.0` since 12 November (`568b23f`), all three from
Renovate, and Caddy since 14 November, as `2.11.9-alpine` (`a3a4db6`,
[ronl-business-api#433](https://github.com/sgort/ronl-business-api/issues/433)). Keycloak
`23.0`, in both Keycloak compose files, still carries no digest, nor does the Operaton
`1.0.0` in the engine-rest test harness. That holds the RONL Business API's R3 and R4 back;
a stricter reading holds back its R2 as well, on Skosmos's `:latest`.

Sixteen of the eighteen rows are done, and none has closed since 11 October. What is left
divides cleanly. The Dependabot triage waits mostly on majors already queued — Tiptap 3 in the
Linked Data Explorer; React Router 7, accepted in
[#395](https://github.com/sgort/ronl-business-api/issues/395) until then, and, for the
development-only `minimatch` high, typescript-eslint v8 in the RONL Business API — and on
development-only mediums. In the RONL Business API the seven runtime `hono` and
`@hono/node-server` alerts of 13 November and the `fast-xml-parser` low were fixed on
17 November ([#469](https://github.com/sgort/ronl-business-api/pull/469)), and two development
mediums were dismissed that day with a written reason; its `SECURITY-PIPELINE.md` now records
why each accepted Semgrep finding is accepted. Its row stays open all the same: the three
alerts it keeps — the two `react-router` mediums and the `minimatch` high — are accepted in
writing there, each with a revisit trigger, but neither fixed nor dismissed. The Linked Data
Explorer's `fast-xml-parser` low, with a patched release, is still open. The October criticals
(`handlebars`, `shell-quote`) and the `source-map-js` high were fixed on 29 October. The Linked
Data Explorer's runtime `follow-redirects` high, open from 5 November, was fixed on
12 November. The registry is an ICTU infrastructure question
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
From 15 November the RONL Business API counts one more for the same reason:
`upstream-certs.yml` runs its check script's tests before it checks the certificates.

Three things are visible here that the ICTU scores hide. The CPSV Editor's suite grew more
than fivefold, from 15 files to 83, and gained its first end-to-end journeys. Every
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

Re-checked for this page on 22 November 2026, at the three commits in the stamp, rather than
carried over from the assessment:

- **`runs-on:` in every job of every workflow**: 12 in the CPSV Editor, 21 in the Linked Data
  Explorer, 24 in the RONL Business API — 57 in all — every one `ubuntu-24.04`, none
  `ubuntu-latest`. The remaining 3 and 4 jobs call a reusable workflow and have no `runs-on:`
  of their own. Each repository has two **`schedule:` triggers** — `dependency-audit.yml`
  daily and `dependency-review.yml` quarterly — and the RONL Business API a third since
  13 November, `upstream-certs.yml` daily, which checks upstream certificates rather than
  dependencies.
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
- **Open Dependabot alerts**: 1 in the CPSV Editor (a `minimatch` medium, development); 3 in
  the Linked Data Explorer (at runtime the `@tiptap/core` medium and a `fast-xml-parser` low of
  12 November; in development dependencies a `minimatch` medium); 3 in the RONL Business API
  (at runtime two `react-router` mediums, accepted in
  [#395](https://github.com/sgort/ronl-business-api/issues/395); in development dependencies
  the `minimatch` high). Every one has a patched release, and none of them is dismissed with a
  reason. The RONL Business API's other alerts went on 17 November: eight fixed by
  [#469](https://github.com/sgort/ronl-business-api/pull/469), and two development mediums
  dismissed with a written reason and a condition for revisiting them; its
  `SECURITY-PIPELINE.md` gives the three it keeps open a reason and a revisit trigger each. The
  development `deepmerge` low in both monorepos left the API when GitHub withdrew its advisory
  on 16 November.
- **Renovate pull requests merged in the preceding 30 days**, counted by author
  (`app/renovate`) and merge date since 23 October: 22, 14 and 15 — the RONL Business API's
  last on 12 November. On the Sunday two were open in the CPSV Editor, one in the Linked Data
  Explorer and three in the RONL Business API, among them the three lock-file refreshes of
  16 November.
- **The registry origin of every resolved package**: 556, 1,573 and 1,527 entries, every one
  `registry.npmjs.org` (besides 2 and 6 workspace links), none without an `integrity` hash.
  `npm audit signatures` runs in the required `audit` job in all three, through
  `scripts/audit-signatures.sh`. No internal registry and no proxy.
- **That npm honours `min-release-age` only from 11.10**, and that Node 24.22.2 bundles npm
  11.19.1. The CPSV Editor and the Linked Data Explorer pin 24.22.2; the RONL Business API's
  `.nvmrc` names 22.23.4, which bundles npm 10.9.9, so it is the one repository whose own
  toolchain ignores the cooldown silently.
- **The daily audit and its runs**: `dependency-audit.yml`, cron `17 5 * * *`, auditing `acc`
  and `main` in each. Every scheduled run of the CPSV Editor's since 10 October has passed. The
  Linked Data Explorer's failed from 21 to 28 October
  ([linked-data-explorer#305](https://github.com/sgort/linked-data-explorer/issues/305), closed
  29 October) and from 31 October to 12 November
  ([linked-data-explorer#313](https://github.com/sgort/linked-data-explorer/issues/313), closed
  13 November, `follow-redirects`), and once more on 18 November, on a `picomatch` high whose
  advisory GitHub withdrew that afternoon
  ([linked-data-explorer#345](https://github.com/sgort/linked-data-explorer/issues/345), closed
  by the next run on 19 November). The RONL Business API's failed from
  21 to 29 October ([#389](https://github.com/sgort/ronl-business-api/issues/389), closed
  30 October) and from 31 October to 6 November
  ([#410](https://github.com/sgort/ronl-business-api/issues/410), closed by
  [#417](https://github.com/sgort/ronl-business-api/pull/417)). Every scheduled run from 7 to
  21 November passed in the CPSV Editor and the RONL Business API.
- **The quarterly dependency review**: `dependency-review.yml`, cron `23 6 2 1,4,7,10 *`, run by
  hand on 10 October in all three
  ([ttl-editor#210](https://github.com/sgort/ttl-editor/issues/210),
  [linked-data-explorer#290](https://github.com/sgort/linked-data-explorer/issues/290),
  [ronl-business-api#362](https://github.com/sgort/ronl-business-api/issues/362)), each closed
  with an outcome for every flagged package. The schedule has not run yet: its first slot is
  2 January 2027.
- **The release SBOMs** under `docs/sbom/`: eight in the CPSV Editor (2026.09.6, .09.7, .10.0,
  .10.1, .10.2, .11.0, .11.1 and .11.2), ten in the Linked Data Explorer (2026.09.7, .09.8, .10.0
  to .10.3 and .11.0 to .11.3) and sixteen in the RONL Business API (2026.09.11 to .09.15,
  .10.0 to .10.4 and .11.0 to .11.5). Since 10 October
  the production set is read from the lockfile, and the two checks in `sbom.yml` run before
  the generate step. Since 22 November the Linked Data Explorer's strict check compares
  content only, leaving out the npm that wrote the file
  ([linked-data-explorer#354](https://github.com/sgort/linked-data-explorer/pull/354)); the
  other two follow in [ttl-editor#269](https://github.com/sgort/ttl-editor/issues/269) and
  [ronl-business-api#481](https://github.com/sgort/ronl-business-api/issues/481), both open.
- **The Renovate major rules**: `allowedVersions` excluding `X.0.0` for npm in all three; the
  `ubuntu` major disabled with a reason in all three, and Node 24 in the RONL Business API.
  Pending approval on each Dependency Dashboard on 22 November: 2, 3 and 19, of which 2, 3 and
  14 are majors by title — Node 26 and `keycloak-js` 26 in the CPSV Editor, Node 26 and the
  backend and frontend major groups in the Linked Data Explorer, and React Router 7,
  `operaton/operaton` v2.2.1 and the Vitest 5 monorepo among them in the RONL Business API.
- **Container images in the RONL Business API**: six in the root `docker-compose.yml`, each
  with a tag and a digest; of the six compose files under `deployment/vm/`, Skosmos (on
  `:latest`), Postgres, the production Operaton and Caddy (`2.11.9-alpine`, in the VM's file
  and the test harness) are digest-pinned, as is the harness's `curl`, while Keycloak `23.0`
  and the harness's Operaton `1.0.0` carry no digest.

## What was not verified

- **The scores themselves.** They are a judgement on a 0–5 scale, and several cells are
  readings rather than facts; a stricter reading would score each one lower, and taking every
  one of them would give 33, 31 and 30 rather than 42, 40 and 40. The RONL Business API's
  strict total rises from 29 because last week's strict case for its R10 is answered: its
  fourteen open alerts are three, each accepted in writing with a revisit trigger, two others
  were dismissed with a reason on the alert, and every audit was green. R8 in all three still
  waits on its condition: lock-file maintenance merged once, on 12 November, after 38, 31 and
  24 days open — the same "a catch-up is not a cadence" argument that held the cell on
  1 November — and a stricter reading waits for a refresh to merge within its week; none has,
  the refreshes of 16 November
  ([ttl-editor#253](https://github.com/sgort/ttl-editor/pull/253),
  [linked-data-explorer#343](https://github.com/sgort/linked-data-explorer/pull/343),
  [ronl-business-api#458](https://github.com/sgort/ronl-business-api/pull/458)) being open
  after six days, and the RONL Business API merged no Renovate pull request at all this week.
  R1 in all three, sharper: seven new direct dependencies have now passed the checklist with
  none of its thirty-five boxes ticked, `tsx` this week among them, and the Linked Data
  Explorer's listed a transitive `limiter` 1.1.5 with no licence recorded. The rest are carried.
  R10 in the CPSV Editor, where a development `minimatch` medium has been open since
  5 November, neither fixed nor dismissed; and in the Linked Data Explorer, where three open
  alerts have nothing accepted in writing and the audit went red once this week, though on a
  withdrawn advisory, which a stricter reading scores 2. R5 in all three, where only the provenance half
  is done and the registry question has not been put to ICTU on the record. R11 in all three,
  where the review ran once, by hand, and the schedule has not yet fired. R9 in all three,
  where no ruleset requires a branch to be up to date or a review to approve it — the
  refreshes waiting on a pending Renovate status that no ruleset requires is this week's
  illustration. R7 in all
  three, where the rule that skips `X.0.0` covers npm only and the approval tick leaves no
  written assessment — the RONL Business API has fourteen majors waiting on it, the Linked Data
  Explorer three and the CPSV Editor two, `keycloak-js` 26 among them, for a dependency added
  three majors behind. The RONL Business API's R2: the Skosmos reference still spells
  `:latest`, and the VM's Keycloak tag, `23.0`, names no patch. The Linked Data Explorer's R2,
  where `NODE|24-lts` still names no exact version and the recorded reason is a deviation
  rather than a pin. The RONL Business API's R3 and R4, where the break-glass scripts still
  install without a lockfile and the VM's Keycloak images and the test harness's Operaton
  carry no digest. The CPSV Editor's R2, where the only unpinned
  thing left is a vendor container that no longer builds anything. R3 in the CPSV Editor and
  the Linked Data Explorer, where the manifests still hold caret ranges although no deploy path
  re-resolves them. And the RONL Business API's R6, whose own npm ignores the cooldown
  silently.
- **The generous readings not taken.** R9 at 5 in all three, on `lockfile-review` closing
  the transitive-review gap, with the RONL Business API's
  [#461](https://github.com/sgort/ronl-business-api/pull/461), held by the register check, as
  further evidence of the gate; R8 at 5 in the Linked Data Explorer, where a weekly batch merged
  and only the lock-file pull request is open; the Linked Data Explorer's R10 at 4, on an audit
  green apart from one run on an advisory GitHub withdrew that day, which the audit then closed
  by itself; the RONL Business API's R10 at 5, where every alert is fixed, dismissed with a
  reason or accepted in writing with a revisit trigger, and the daily audit was green every
  day; and R6 at 5 in the CPSV Editor and the Linked Data Explorer, where the refresh Renovate
  cannot cool down was shown on 15 November to respect the 14 days at package level — 68 and
  143 versions changed, the youngest 15.5 and 15.7 days old — and was not re-measured, this
  week's refreshes being unmerged. Taking every generous reading as well would give 44, 44
  and 42; the RONL Business API's 42 is now made of R9 and R10 rather than R9 and R8, its R8
  having lost last week's generous case of none open on the Sunday.
- **Whether a person reads release notes or checks maintenance** before merging or adding a
  dependency. Nothing in the repositories records it either way, so R1, R9 and R11 score only
  what is recorded.
- **Whether Semgrep Cloud re-evaluates a stored scan** against advisories published after it
  ran.
- **The published test counts and coverage percentages** shown on the applications' own
  testing pages. This page counts test *files* at each weekly commit, which is a different and
  cheaper measurement.
