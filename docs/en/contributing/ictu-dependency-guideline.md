---
scope: cross-cutting
verified:
  date: 2026-09-13
  against:
    CPSV Editor: "f5bae6a"
    Linked Data Explorer: "be6bc54"
    RONL Business API: "311d732"
---

# ICTU Dependency Guideline

*Eleven recommendations, and where the three applications stand*

ICTU publishes eleven recommendations for managing dependencies — for everything a build
pulls in, direct and indirect, including the images, hooks and pipeline definitions around
the code. On 13 September 2026 the three applications were assessed against them, and this
page records the result. It owns the **scores**. The mechanisms each recommendation touches
are documented on the control pages, and the
[controls index](controls.md#measured-against-ictus-guideline) maps each recommendation to
the page that covers it.

!!! info "Sources and scope"
    The guideline and the assessment live in the Linked Data Explorer repository —
    [`ICTU-dependencies-guideline.md`](https://github.com/sgort/linked-data-explorer/blob/acc/docs/ICTU-dependencies-guideline.md)
    and
    [`ICTU-dependencies-assessment.md`](https://github.com/sgort/linked-data-explorer/blob/acc/docs/ICTU-dependencies-assessment.md)
    — and the work that follows is tracked in
    [linked-data-explorer#119](https://github.com/sgort/linked-data-explorer/issues/119).
    The assessment read each repository's `acc` at `f7fe80f` (CPSV Editor), `1babd54`
    (Linked Data Explorer) and `28e1a9e` (RONL Business API); none carries a CI-relevant
    change beyond the commits this page is stamped against.

    The scores are the assessment's judgement and are reproduced here, not re-scored. The
    facts they rest on were re-checked for this page — see
    [What was verified](#what-was-verified). This documentation repository was not assessed;
    its own gap is recorded under
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

## Scores

Scale: **0** absent or contradicted · **1** incidental only · **2** partly met, large gaps ·
**3** mostly met, a clear gap · **4** met, a small gap · **5** fully met, and enforced rather
than intended.

| | Recommendation | CPSV Editor | Linked Data Explorer | RONL Business API |
|---|---|:-:|:-:|:-:|
| R1 | Vet maintenance before adding | 1 | 1 | 2 |
| R2 | No unpinned tags | 2 | 2 | 2 |
| R3 | Highest precision, no ranges | 2 | 2 | 2 |
| R4 | Hash pins, lockfile, `npm ci` | 3 | 2 | 3 |
| R5 | Internal registry; verified origin | 0 | 0 | 0 |
| R6 | Cooldown of at least 7 days | 3 | 3 | 3 |
| R7 | Assess majors; wait for a patch | 4 | 3 | 3 |
| R8 | Periodic, tool-driven updates | 5 | 4 | 3 |
| R9 | Reviewed MR, whole pipeline, no automerge | 3 | 3 | 2 |
| R10 | Daily audit, including releases | 2 | 2 | 1 |
| R11 | Quarterly maintenance check | 1 | 1 | 1 |
| | **Total, of 55** | **26** | **23** | **22** |

**None is close, and the ordering matters less than the pattern.** All three are strong
where tooling does the work — digest-pinned actions verified by a blocking check, Renovate
under a 14-day cooldown, majors behind approval — and weak in the three places tooling does
not reach on its own: infrastructure that does not exist here (R5), monitoring on a
schedule (R10), and a human process that leaves a written trace (R1, R11).

Where the CPSV Editor scores higher it is largely for writing things down: its
`renovate.json` defers Tailwind CSS 4 and ESLint 10 with reasons, which is the assessment
R7 asks for.

## What ships is not what was tested

The finding the assessment ranks first, and the one that decides R2, R3 and R4 together.
In the CPSV Editor and the Linked Data Explorer's frontend, **the code that passed the tests
and the code that ships are produced by different installs on different Node versions**,
and the shipped one is chosen by a floating container.

| | Tested with | Shipped with |
|---|---|---|
| CPSV Editor | `npm ci` on the runner, Node 24 | Oryx's `npm install` inside the Static Web Apps container, **Node 22.22.0** |
| Linked Data Explorer — frontend | `npm ci` on the runner, Node 20.20.2 | Oryx's `npm install` inside the Static Web Apps container, **Node 22.22.0** |
| Linked Data Explorer — backend | `npm ci` on the runner | `npm install --production --omit=dev` from `package.json`, **without the lockfile** |
| RONL Business API — frontends | `npm ci` on the runner, Node 22.22.0 | the same build, uploaded with `skip_app_build: true` |
| RONL Business API — backend | `npm ci` on the runner | a deploy script on a developer machine, `npm install` without the lockfile ([#34](https://github.com/sgort/ronl-business-api/issues/34)) |

Read from the deploy logs rather than the workflow files.
[Linked Data Explorer run 34612031473](https://github.com/sgort/linked-data-explorer/actions/runs/34612031473)
added 1,288 packages with `npm ci` on Node 20.20.2 for lint and tests, then its deploy step
logged `Oryx Version: 0.2.20260109.4`, `Downloading and extracting 'nodejs' version
'22.22.0'` and `Running 'npm install'`.
[CPSV Editor run 34622800899](https://github.com/sgort/ttl-editor/actions/runs/34622800899)
tested on Node 24 and shipped the same way. **Neither Node version is one the repository
chooses.**

`npm install` honours a lockfile that agrees with `package.json` and quietly re-resolves one
that does not, where `npm ci` would fail. The CPSV Editor's install matched its lockfile in
that run — `up to date, audited 542 packages` — which is the likely outcome rather than a
guaranteed one.

The fix is the one the RONL Business API already made: **build on the runner and deploy with
`skip_app_build: true`**. In one change it removes Oryx's install, ships on the Node version
the tests ran on, and takes the floating container out of the build path. The mechanism is
on [Supply-Chain Pinning](supply-chain.md#what-this-does-not-protect).

## The work, and where it starts

Each application's position on 13 September 2026, ordered by the assessment's own ranking
of leverage, with the issue's further items after. **The checkboxes live in
[linked-data-explorer#119](https://github.com/sgort/linked-data-explorer/issues/119)** — this
table is the dated starting point and is not kept current as items close, so that there is
one place to tick a box rather than two that disagree.

✅ already done · ⬜ open · — not applicable

| Work item | Serves | CPSV Editor | Linked Data Explorer | RONL Business API |
|---|---|:-:|:-:|:-:|
| Build static web apps on the runner, deploy with `skip_app_build: true` | R2–R4 | ⬜ | ⬜ | ✅ |
| Deploy backends from the lockfile with `npm ci --omit=dev` | R3, R4 | — | ⬜ | ⬜ |
| Add a cooldown at the package-manager level | R6 | ⬜ | ⬜ | ⬜ |
| Pin the runner image to `ubuntu-24.04` | R2 | ⬜ | ⬜ | ⬜ |
| Add a daily scheduled dependency audit | R10 | ⬜ | ⬜ | ⬜ |
| Triage open Dependabot alerts: fix, or dismiss with a reason | R10 | — | ⬜ | ⬜ |
| Require the build and test checks | R9 | ⬜ | ⬜ | ⬜ |
| Review transitive changes on dependency pull requests | R9 | ⬜ | ⬜ | ⬜ |
| Pin container images by version and digest | R2, R4 | — | — | ⬜ |
| Write down criteria for adding a dependency; review maintenance quarterly | R1, R11 | ⬜ | ⬜ | ⬜ |
| Adopt a rule: wait for a major's first or second patch release | R7 | ⬜ | ⬜ | ⬜ |
| Decide on an internal registry or proxy, and on provenance verification | R5 | ⬜ | ⬜ | ⬜ |
| Decide on the floating App Service runtime `NODE\|22-lts` | R2 | — | ⬜ | ⬜ |
| Pin Node exactly, in one place | R3 | ⬜ | ⬜ | ✅ |
| Assess queued majors and record deferrals with reasons | R7 | ✅ | ⬜ | ⬜ |
| Scan what production runs, not only `acc` | R10 | ⬜ | ⬜ | ⬜ |
| Generate SBOMs for releases | R10 | ⬜ | ⬜ | ⬜ |

The CPSV Editor's triage row is not applicable because it had no open alerts to triage; the
registry row is an ICTU infrastructure question before it is a repository one.

## What was verified

Re-checked for this page on 13 September 2026, rather than carried over from the assessment:

- **The Oryx toolchain and both installs**, from the job logs of the two deploy runs above.
- **`runs-on: ubuntu-latest` in every job** — 6 in the CPSV Editor, 12 in the Linked Data
  Explorer, 13 in the RONL Business API — and **no `schedule:` trigger** in any workflow.
- **`skip_app_build` and `app_build_command`** in each Static Web Apps workflow, and the
  Linked Data Explorer's backend deploy packaging, from the workflow files at the assessed
  commits.
- **Open and dismissed Dependabot alerts**, and each repository's default branch, from the
  GitHub API.
- **The registry origin of every resolved package** in each `package-lock.json`.
- **That Renovate does not apply `minimumReleaseAge` to lock-file maintenance**, from
  Renovate's own documentation.
- **The required status checks per branch**, from the rulesets API — see
  [Branch Protection](branch-protection.md).
- **The majors queued behind the RONL Business API's Dependency Dashboard**: 18 entries in its *Pending Approval* section, every one a major, covering 41 distinct packages once the grouped updates are unpacked. The assessment first gave 31, which matched neither count; it is corrected at source in [linked-data-explorer#120](https://github.com/sgort/linked-data-explorer/pull/120).

## What was not verified

- **The scores themselves.** They are a judgement on a 0–5 scale and are reproduced as the
  assessment gives them.
- **Whether the npm bundled with Node 22 supports `min-release-age` in `.npmrc`**, the setting
  the guideline names for R6. Establish it before relying on it.
- **Whether a person reads release notes or checks maintenance** before merging or adding a
  dependency. Nothing in the repositories records it either way, so R1, R9 and R11 score
  only what is recorded.
- **Whether Semgrep Cloud re-evaluates a stored scan** against advisories published after it
  ran.
