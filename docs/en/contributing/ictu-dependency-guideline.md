---
scope: cross-cutting
verified:
  date: 2026-10-04
  against:
    CPSV Editor: "4cba989"
    Linked Data Explorer: "9e0d18e"
    RONL Business API: "5c6e716"
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
    it closed on 3 October 2026. What it still held is now three issues there:
    [#248](https://github.com/sgort/linked-data-explorer/issues/248) for R9,
    [#249](https://github.com/sgort/linked-data-explorer/issues/249) for R5 and
    [#250](https://github.com/sgort/linked-data-explorer/issues/250) for R1 and R11. The R10
    triage is tracked per repository — in the RONL Business API by
    [#311](https://github.com/sgort/ronl-business-api/issues/311).

    Every assessment reads each repository's `acc`, the branch of record. The scores below
    were read at `4cba989` (CPSV Editor), `9e0d18e` (Linked Data Explorer) and `5c6e716`
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
findings of the assessment itself; and the week of 21–27 September, which brought
monitoring. The
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
schedule (R10) was the third such place until the week of 21–27 September, and it moved as
soon as tooling reached it — and again the week after, once that tooling had caught something
— which is the pattern, not an exception to it.

## What moved this week

The week of 28 September – 4 October was the week the daily audit earned its place. It failed
on a production high in two of the three repositories, and both were fixed by shrinking the
production tree rather than by waiting for an upstream patch. Three cells moved, all upward:
the totals are 35, 34 and 33, against 35, 33 and 31 a week earlier.

- **The Linked Data Explorer's R10, 3 → 4.** The audit failed from 30 September on
  `brace-expansion` and `http-cache-semantics`, reached through `libxmljs2`'s `node-gyp`, and
  opened [#240](https://github.com/sgort/linked-data-explorer/issues/240). `http-cache-semantics`
  has no patched release, so only removing the chain could clear it: the weekly lockfile
  refresh (`7dcfdea`) and an override that gives `libxmljs2` `node-gyp` 13
  (`be5bc99`, [#251](https://github.com/sgort/linked-data-explorer/pull/251)) took it out of
  the production tree, and #240 closed on 3 October. The commit records the backend's
  production install falling from 349 packages to 271; the release SBOM fell from 416
  components (`2026.09.8`) to 370 (`2026.10.0`). It is the repository's first production
  finding caught by the schedule rather than by someone looking. It is not a 5:
  [alert #134](https://github.com/sgort/linked-data-explorer/security/dependabot/134), a
  `@tiptap/core` medium whose only fix is the Tiptap 3 major, has been open since
  2 September without a fix or a written acceptance.
- **The RONL Business API's R10, 3 → 4.** The audit opened
  [#303](https://github.com/sgort/ronl-business-api/issues/303) for a `braces` high at 10:24
  on 3 October, and it closed at 11:45 once
  [#305](https://github.com/sgort/ronl-business-api/pull/305) made `@tailwindcss/typography`
  the build-time devDependency it always was. A second issue,
  [#307](https://github.com/sgort/ronl-business-api/issues/307), held `main` from 11:49 until
  the promotion cleared it at 13:25. Eighty-one minutes from the alarm to a fix on `acc`. It is
  not a 5: four Dependabot alerts stay open — one high in a development dependency, two
  `react-router` mediums, one `dompurify` low — none dismissed with a reason; their triage is
  now tracked in [#311](https://github.com/sgort/ronl-business-api/issues/311).
- **The RONL Business API's R2, 3 → 4.** Skosmos on the VM, the last image in the repository
  that floated on a tag, now runs `quay.io/natlibfi/skosmos:latest@sha256:c5855698…`, pinned
  by Renovate in `62c05a7` ([#198](https://github.com/sgort/ronl-business-api/pull/198)). The
  two Keycloak compose files under `deployment/vm/` still run `quay.io/keycloak/keycloak:23.0`
  and `postgres:16-alpine` without a digest
  ([#196](https://github.com/sgort/ronl-business-api/issues/196), open) — but those tags name a
  version, so they count against R3 and R4, not here.

Several things happened that moved no cell. All three `main` branches now require `audit` and
`scan`: the RONL Business API's `main` ruleset gained `scan` on 29 September, and the CPSV
Editor's `main` gained its first ruleset on 30 September, the same day its `acc` ruleset was
narrowed to merge commits and began blocking deletion and force-pushes. The CPSV Editor moved
to Node 24.21.0 on 30 September, so the Node pinned in the audit, SBOM and zizmor workflows is
24.21.0 in all three, and so is every `.nvmrc` except the RONL Business API's, still 22.23.2.
And [linked-data-explorer#119](https://github.com/sgort/linked-data-explorer/issues/119), the
tracker the first assessment opened, closed on 3 October into three issues for what is left
([#248](https://github.com/sgort/linked-data-explorer/issues/248),
[#249](https://github.com/sgort/linked-data-explorer/issues/249),
[#250](https://github.com/sgort/linked-data-explorer/issues/250)).

The cells that held, held for a reason:

- **The CPSV Editor's R10 stays 4.** Every scheduled run of its audit has passed, which is the right result
  but not yet evidence of a catch, and nothing analyses the SBOMs.
- **The Linked Data Explorer's R8 stays 4.** Renovate's lockfile maintenance keeps merging —
  [#230](https://github.com/sgort/linked-data-explorer/pull/230) on 3 October was the fifth
  since 11 September — but a generous reading of 5 on the strength of it was not taken.
- **The RONL Business API's R11 stays 1.** Its local Redis is held at 7.2 for its licence
  ([#302](https://github.com/sgort/ronl-business-api/pull/302)) — a maintenance judgement, but
  a one-off: Renovate has enforced it since #313 (4 October), but the recommendation asks for a periodic review, which this is not.
- **The RONL Business API's R3, R4 and R9 stay 3, 4 and 3**: the VM's Keycloak and Postgres
  images carry no digest, the break-glass scripts still install without a lockfile, and the
  gap below is still open.
- **R1, R5 and R11 in all three** now have their own issues (#249, #250), but nothing is
  written down or decided yet.

!!! warning "One gap the week of 21–27 September introduced, still open"
    In the RONL Business API, the three Static Web App `changes` patterns do not match the root
    `package-lock.json` (`azure-frontend-acc.yml:79`, `azure-pa-demo-acc.yml:85`,
    `azure-publicsite-acc.yml:77` at `5c6e716`). A lock-file maintenance pull request changes
    nothing else, so all three jobs skip — and a skipped job reports success. The update that
    moves the entire transitive tree is therefore the one update that merges with three of its
    four required build checks never having run; the lockfile-only
    [#286](https://github.com/sgort/ronl-business-api/pull/286) of 30 September merged that way.
    The lockfile-sync step in `audit` does not close it: it proves the lockfile matches the
    manifests, not that the three apps build on it.

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
| CPSV Editor | `npm ci` on the runner | Oryx's `npm install`, Node 22.22.0 | the runner's build, Node 24.21.0 |
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
| Triage open Dependabot alerts: fix, or dismiss with a reason ([ronl-business-api#311](https://github.com/sgort/ronl-business-api/issues/311)) | R10 | — | ⬜ | ⬜ |
| Review transitive changes on dependency pull requests ([#248](https://github.com/sgort/linked-data-explorer/issues/248)) | R9 | ⬜ | ⬜ | ⬜ |
| Pin container images by version and digest | R2, R4 | — | — | ✅¹ |
| Write down criteria for adding a dependency; review maintenance quarterly ([#250](https://github.com/sgort/linked-data-explorer/issues/250)) | R1, R11 | ⬜ | ⬜ | ⬜ |
| Adopt a rule: wait for a major's first or second patch release | R7 | ✅ | ✅ | ✅ |
| Decide on an internal registry or proxy, and on provenance verification ([#249](https://github.com/sgort/linked-data-explorer/issues/249)) | R5 | ⬜ | ⬜ | ⬜ |
| Decide on the floating App Service runtime (`NODE\|24-lts`, `NODE\|22-lts`) | R2 | — | ✅ | ✅ |
| Assess queued majors and record deferrals with reasons | R7 | ✅ | ✅ | ✅ |
| Scan what production runs, not only `acc` | R10 | ✅ | ✅ | ✅ |
| Generate SBOMs for releases | R10 | ✅ | ✅ | ✅ |

¹ The local stack. The compose files under `deployment/vm/` are deliberately not pinned,
because nothing in the repository applies them
([#196](https://github.com/sgort/ronl-business-api/issues/196)). Skosmos there has been
pinned by digest on `:latest` since 30 September 2026 (`62c05a7`); the two Keycloak compose
files carry neither a digest nor a full version, which holds the RONL Business API's R3 and R4
back but no longer its R2.

Thirteen of the seventeen rows are done; none closed this week. What is left divides
cleanly: the Dependabot triage waits mostly on majors already queued — Tiptap 3 in the Linked
Data Explorer, React Router 7 and, for the development-only `minimatch` high, typescript-eslint
v8 in the RONL Business API — while the two `dompurify` lows need only the 3.4.16 patch; the
transitive review is pipeline work nobody has started; the criteria and the
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
than fourfold, from 15 files to 66, and gained its first end-to-end journeys. Every
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

Re-checked for this page on 4 October 2026, at the three commits in the stamp, rather than
carried over from the assessment:

- **`runs-on:` in every job of every workflow**: 9 in the CPSV Editor, 18 in the Linked Data
  Explorer, 20 in the RONL Business API — 47 in all — every one `ubuntu-24.04`, none
  `ubuntu-latest`. The remaining 3 and 4 jobs call a reusable workflow and have no `runs-on:`
  of their own. Each repository has exactly one **`schedule:` trigger**, in
  `dependency-audit.yml`.
- **`skip_app_build`, the build steps and the deploy packaging**, from the workflow files at
  those commits, including both backends' staged `npm ci --omit=dev` — the Linked Data
  Explorer's and, since 21 September, the RONL Business API's.
- **The required status checks per branch**, from the rulesets API. On `acc`: `audit`, `scan`
  and `Build and deploy ACC` in the CPSV Editor; `audit`, `scan`, `deploy`,
  `Build and Deploy Frontend` and `Build and Deploy ROPA Site` in the Linked Data Explorer;
  `audit`, `scan`, `build` and the three ACC deploy checks in the RONL Business API. On
  `main`: `audit` and `scan` in all three — in the RONL Business API since 29 September 2026,
  in the CPSV Editor since its `main` ruleset was created on 30 September. None of the six
  rulesets requires a branch to be up to date before merging, and no branch keeps classic
  branch protection. See [Branch Protection](branch-protection.md).
- **Every `changes` job's pattern**, against `package-lock.json` specifically — which is how
  the RONL Business API gap above was found.
- **Open Dependabot alerts**: 0 in the CPSV Editor; 2 in the Linked Data Explorer (a
  `@tiptap/core` medium and a `dompurify` low); 4 in the RONL Business API (a `minimatch` high
  in a development dependency, two `react-router` mediums and a `dompurify` low). None of them
  is dismissed with a reason.
- **Renovate pull requests merged in the preceding 30 days**, counted by author
  (`app/renovate`) and merge date since 4 September: 30, 20 and 23. Last week's 23, 26 and 26
  may have been counted differently, so the two weeks are not a trend.
- **The registry origin of every resolved package**: 566, 1,527 and 1,497 entries, every one
  `registry.npmjs.org` (besides 2 and 6 workspace links). No internal registry, no proxy, no
  provenance check — R5 stays 0.
- **That npm honours `min-release-age` only from 11.10**, and that Node 22.23.2 bundles npm
  10.9.8 while Node 24.21.0 bundles npm 11.19.0. With the CPSV Editor on 24.21.0 since
  30 September, joining the Linked Data Explorer, the RONL Business API — whose `.nvmrc` still
  names 22.23.2 — is the one repository whose own toolchain ignores the cooldown silently.
- **The daily audit and its runs**: `dependency-audit.yml`, cron `17 5 * * *`, auditing `acc`
  and `main` in each. Every scheduled run in the CPSV Editor has passed. The Linked Data
  Explorer's failed from 30 September until 3 October
  ([#240](https://github.com/sgort/linked-data-explorer/issues/240)); the RONL Business API's
  failed on 3 October, on `acc`
  ([#303](https://github.com/sgort/ronl-business-api/issues/303)) and on `main`
  ([#307](https://github.com/sgort/ronl-business-api/issues/307)), after its earlier catch, the
  `adm-zip` high on `main` of 25 and 26 September.
- **The release SBOMs** under `docs/sbom/`: three in the CPSV Editor (2026.09.6, .09.7 and
  .10.0), three in the Linked Data Explorer (2026.09.7, .09.8 and .10.0) and six in the RONL
  Business API (2026.09.11 to .09.15, and .10.0).
- **The Renovate major rules**: `allowedVersions` excluding `X.0.0` for npm in all three; the
  `ubuntu` major disabled with a reason in all three, and Node 24 in the RONL Business API.
  Pending approval on each Dependency Dashboard on 4 October: 1, 2 and 19, of which 1, 2 and
  14 are majors — among them `vitest` 5 in the CPSV Editor and `redis` 8 in the RONL Business
  API.
- **Container images in the RONL Business API**: five in the root `docker-compose.yml`, each
  with a tag and a digest; of the three compose files under `deployment/vm/`, Skosmos is
  digest-pinned on `:latest` and the two Keycloak files carry neither a digest nor a full
  version.

## What was not verified

- **The scores themselves.** They are a judgement on a 0–5 scale, and several cells are
  readings rather than facts; a stricter reading would score each one lower, and taking every
  one of them would give 29, 29 and 27 rather than 35, 34 and 33. R7 in all three, where the
  rule that skips `X.0.0` covers npm only and the approval tick leaves no written assessment —
  the RONL Business API has fourteen majors waiting on it, the Linked Data Explorer two. R10
  in all three: the CPSV Editor's audit has not yet caught anything and nothing analyses the
  SBOMs; the Linked Data Explorer's `@tiptap/core` medium
  ([alert #134](https://github.com/sgort/linked-data-explorer/security/dependabot/134)) has
  been open a month without a fix or a written acceptance; and the RONL Business API's four
  open alerts stay open, none dismissed, so a stricter reading keeps both of this week's R10
  moves at 3. The RONL Business API's R2, which a stricter reading keeps at 3: the Skosmos
  reference still spells `:latest`, and the VM's other images carry no digest. The Linked Data
  Explorer's R2, where `NODE|24-lts` still names no exact version and the recorded reason is a
  deviation rather than a pin. The RONL Business API's R3 and R4, where the break-glass
  scripts still install without a lockfile and the Keycloak VM images carry no digest. R9 in
  the CPSV Editor and the Linked Data Explorer, where transitive changes go unreviewed and no
  ruleset requires a branch to be up to date before it merges. The CPSV Editor's R8, the only
  5 of the three on that recommendation. And, carried from earlier weeks, the CPSV Editor's
  R2, where the only unpinned thing left is a vendor container that no longer builds
  anything; R3 in the CPSV Editor and the Linked Data Explorer, where the manifests still hold
  caret ranges although no deploy path re-resolves them; and the RONL Business API's R6,
  whose own npm ignores the cooldown silently.
- **The generous readings not taken.** The Linked Data Explorer's R8 at 5, on weekly lockfile
  maintenance that keeps merging; and the RONL Business API's R11 at 2, on the Redis 7.2
  licence hold, which no Renovate rule enforces yet. Taking every generous reading as well
  would give 35, 35 and 34.
- **Whether a person reads release notes or checks maintenance** before merging or adding a
  dependency. Nothing in the repositories records it either way, so R1, R9 and R11 score only
  what is recorded.
- **Whether Semgrep Cloud re-evaluates a stored scan** against advisories published after it
  ran.
- **The published test counts and coverage percentages** shown on the applications' own
  testing pages. This page counts test *files* at each weekly commit, which is a different and
  cheaper measurement.
