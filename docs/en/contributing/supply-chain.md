# Supply-Chain Pinning

Nothing a pipeline downloads or executes may float. No `latest`, no empty
versions — a hash, digest or verified checksum wherever one exists.

This page describes how that policy is enforced, why it is enforced *inside*
each repository rather than at the organisation level, and — just as
importantly — what it deliberately does not protect. It is cross-cutting: the
mechanism is the same in every repository that has adopted it, and the same
four files are copied into the next one.

---

## Why in-repo rather than org-level

`github.com/ictu` already enforces hash-pinned GitHub Actions at the
organisation level. The IOU repositories are not in that organisation — they
live under `github.com/sgort`, with the
[open-regels.nl GitLab instance](https://git.open-regels.nl) as the code host —
so they inherit none of that enforcement.

The recorded decision is to build the controls **inside each repository**, where
they travel with the code regardless of which remote hosts it, rather than
migrating the repositories into the `ictu` organisation. Two alternatives were
considered and rejected: pinning and upgrading to the latest majors in one step
(which couples "make immutable" with "change runner behaviour", leaving a broken
deploy undiagnosable between the two), and forking the actions into an IOU-owned
namespace (disproportionate for a handful of actions, and it relocates the trust
problem rather than solving it).

!!! note "GitLab hosts code only"
    All IOU CI/CD runs on GitHub Actions. There is no `.gitlab-ci.yml` in these
    repositories, so "extend the policy to GitLab" is vacuous for them — the
    entire attack surface is the GitHub workflows.

---

## Adoption status

| Repository | Pinned workflows | `audit` gate | Renovate | `acc` ruleset |
|---|:---:|:---:|:---:|:---:|
| **CPSV Editor** (`ttl-editor`) — pilot | ✅ | ✅ | ✅ | ✅ `acc supply-chain gate` |
| **RONL Business API** | ✅ | ✅ | ✅ | ✅ `acc supply-chain gate` |
| **Linked Data Explorer** | ❌ | ❌ | ❌ | ❌ |
| **IOU Architecture Docs** (this site) | ❌ | ❌ | ❌ | ❌ |

The CPSV Editor is the pilot, adopted in v2026.08.2; RONL Business API followed
within the same week. Linked Data Explorer is next in the rollout order.

**This documentation repository is a known gap, deliberately deferred.** Its
`requirements.txt` uses `>=` floors for five of six packages and its workflow
runs `pip install --upgrade pip`, so both the dependencies and the installer
float, with no lockfile or hash file. It has looser dependency integrity than
any repository currently in scope. The decision to defer was taken on
2026-08-26 and recorded so it stays deliberate rather than forgotten; the fix,
when it is taken up, is a `requirements.in` compiled by
`pip-compile --generate-hashes` and installed with `pip install --require-hashes`.

---

## The concrete risk

A step written `uses: some/action@v1` executes whatever code that tag points at
*today*. Whoever controls the tag controls the pipeline — including the step
holding the deployment token.

`Azure/static-web-apps-deploy` illustrates the problem exactly. It publishes
`v1` as **both** a 2021 tag (`1a947af…`) and a 2024 branch head (`4d27395…`),
28 commits and 3.5 years apart, and GitHub does not document how it resolves an
ambiguous ref. So `@v1` was ambiguous *and* partly mutable.

For a two-environment setup the consequence is sharper than it first appears.
The acceptance and production workflows resolve the same ref **independently, at
their own run times**. A ref moving between an acc deploy and the later
production deploy sends *different action code to each environment from
identical repository content* — leaving no trace in git history. Acceptance
silently stops being a faithful rehearsal of production.

---

## The five pieces

Four files and one GitHub setting.

### 1. `.github/zizmor.yml` — the policy

```yaml
rules:
  unpinned-uses:
    config:
      policies:
        '*': hash-pin
```

A commit hash for **every** namespace, with no exemption for first-party
`actions/*`. zizmor 1.29.0 already enforces this by default, so today the file
changes no findings. It is committed deliberately: the policy belongs in the
repository rather than in a tool default that a future release could quietly
relax.

### 2. Pinned workflows

Every `uses:` is a 40-character commit SHA followed by a `# vX.Y.Z` comment. The
comment is **functional, not decorative** — Renovate parses it to know which
version a digest represents, and rewrites it on update.

Pins are taken at the **then-current major and not upgraded**, so adopting the
policy is behaviour-preserving. Version upgrades arrive separately, as reviewed
Renovate pull requests. That separation is what lets the first live run prove
the *pinning* worked, without a simultaneous upgrade muddying the result.

Each workflow also declares least privilege — `permissions: contents: read` at
workflow level, with a deploy job adding only `pull-requests: write` for the
Static Web Apps action's PR comments, and a close-PR job taking an empty
`permissions: {}` block.

`actions/checkout` sets `persist-credentials: false`. Before this, a live
`GITHUB_TOKEN` was written into `.git/config` and mounted into a closed-source
third-party container on every run. That is a real hole closed, not a cosmetic
lint fix; the deploy action authenticates with explicitly passed tokens instead.

### 3. `.github/workflows/zizmor.yml` — the gate

Runs [zizmor](https://github.com/zizmorcore/zizmor) on pull requests and pushes
to `acc` and `main`, under job name **`audit`**. Three inputs are deliberate:

| Input | Value | Why |
|---|---|---|
| `version` | `'1.29.0'` | The action defaults to `latest`. A supply-chain gate that pulls an unpinned tool on every run would defeat itself. The action resolves this through an internal digest table and runs a genuine container digest pin |
| `advanced-security` | `false` | The default uploads SARIF and requires `security-events: write`; this job is `contents: read` only. It also means fork PRs work, since there is no upload step to fail |
| `annotations` | `true` | Surfaces findings inline on the diff. Mutually exclusive with `advanced-security` — the action errors if both are true |

The gate lands **after** the tree already reports zero findings, so it arrives
green rather than red. Measured on the pilot: **16 findings → 0**, verified at
every intermediate step.

| Stage | `unpinned-uses` | `excessive-permissions` | `artipacked` | Total |
|---|---:|---:|---:|---:|
| Before | 8 | 6 | 2 | **16** |
| After digest pins + `persist-credentials: false` | 4 | 6 | 0 | **10** |
| After `permissions:` blocks | 4 | 0 | 0 | **4** |
| After pinning the deploy action | 0 | 0 | 0 | **0** |

### 4. `renovate.json` — keeping the pins alive

A pin that is never updated is a pin that rots. Renovate maintains the digests
under a cooldown:

- **`helpers:pinGitHubActionDigests`** — maintains digests *and* rewrites the
  version comment to match.
- **`minimumReleaseAge: "14 days"`** — the cooldown, giving vendors and
  researchers time to find problems before adoption.
- **`internalChecksFilter: "strict"`** — suppresses the pull request entirely
  until the age is genuinely met, rather than raising one that fails a check.
- **`vulnerabilityAlerts` with `minimumReleaseAge: null`** — the fast route for
  security advisories.

That last rule is the one most cooldown policies omit, and its absence is why
people disable such policies mid-incident: **without it the cooldown would delay
exactly the updates that must not wait.** It fires off GitHub's Dependabot
*alerts* feed, so those must be enabled — while Dependabot *security updates*
must stay **off**, or two bots race on the same manifests with only one of them
respecting the cooldown.

One dependency is exempted from Renovate entirely. Its `github-tags` datasource
resolves `Azure/static-web-apps-deploy@v1` to the 2021 **tag** while the
workflows pin the **branch**, so a routine-looking digest update would silently
revert the production deploy step to 3.5-year-old code — and the 14-day cooldown
offers no protection whatsoever, the target commit being years old.

### 5. The `acc` ruleset — what makes it *enforcement*

A workflow that runs but cannot block is advice. The ruleset converts it into a
gate. In both adopting repositories the ruleset is named **`acc supply-chain
gate`**, targets `refs/heads/acc`, and is `active` with **zero bypass actors**:

- `required_status_checks` → context **`audit`**
- `pull_request` → `required_approving_review_count: 0`

Both rules are needed *together*. Requiring the check alone would still let a
direct push to `acc` bypass the gate entirely.

Approvals are `0` because these repositories have a single maintainer and GitHub
does not permit self-approval — requiring `1` would make `acc` unmergeable.
Raise it when a second reviewer exists.

---

## What this means day to day

```
push to a feature branch   → nothing runs (workflows trigger on acc/main only)
open a PR against acc      → audit + Build and Deploy run
audit fails                → merge blocked by the ruleset
audit passes               → merge allowed
direct push to acc         → rejected: a pull request is required
```

Two consequences worth stating plainly:

**Releases go through a pull request.** Any release flow that lands on the
protected branch with `git checkout acc && git merge --ff-only` plus a direct
push is blocked — a locally created commit has never passed `audit`. Each
repository's `/bump-release` was changed accordingly; see
[Development Workflow](development-workflow/overview.md#4-release).

**Renovate's own pull requests are gated by the policy Renovate maintains.** The
bot raises them against `acc` like any contributor. Observed on the first ones:
`audit` passing in 11–13 seconds alongside `renovate/stability-days` reporting
that the minimum release age was met.

---

## What this does **not** protect

Each repository keeps a `SECURITY-PIPELINE.md` exceptions register. A register
that claims total coverage produces a permanent unfixable finding at the first
audit, and the predictable response is to weaken the gate — so the register is
what allows the gate to stay strict *honestly*.

**The Static Web Apps container cannot be pinned, and it builds what ships.**
`Azure/static-web-apps-deploy` is a three-line wrapper whose `action.yml`
declares `runs: using: docker, image: "Dockerfile"`, and that Dockerfile is
`FROM mcr.microsoft.com/appsvc/staticappsclient:stable`. Because `skip_app_build`
is not set, Oryx runs *inside* that floating image and builds the production
bundle there. The image is therefore the **build toolchain that produces the
deployed artifact**, not merely an upload step. Pinning the action makes the
wrapper immutable and leaves the payload floating. Unreachable from our side; it
would require Microsoft publishing digest-pinned image references, or IOU
forking the action.

**`npm ci` integrity covers what is tested, not what is shipped.**
`package-lock.json` carries a `sha512` per package and `npm ci` verifies it —
but that install feeds lint and the unit tests. Oryx performs its own install
inside the container to produce the deployed bytes.

**`node-version: '20'` floats** across all 20.x patches and is downloaded at run
time. Closing this is reachable in principle — an exact patch, or an `.nvmrc` —
but picking and then maintaining an exact Node version is a separate decision,
and it is recorded as a known gap rather than silently ignored.

**zizmor validates pin _format_, never pin _truth_.** A wrong or hostile digest
with a plausible `# v4.4.0` comment passes zizmor, Prettier and human review
alike. Nothing currently re-checks that a digest resolves to the tag it claims.

**The register will drift.** Renovate updates workflow pins and never touches
`SECURITY-PIPELINE.md`, and nothing checks that the two agree. Those last two
gaps are the motivation for a planned `check-supply-chain` preflight script.

---

## Evidence it works — and a cautionary tale

The gate caught a real breakage on its first live run, and the failure is more
instructive than the success.

During review, `token: ''` was added to the zizmor action as "optional
hardening" — the input defaults to `${{ github.token }}`, and zeroing it looked
consistent with the workflow's own least-privilege logic. Every local check
passed: zizmor reported zero findings, Prettier was clean, two independent
reviews approved. In CI it failed in seven seconds:

```
error: invalid value '' for '--gh-token <GH_TOKEN>': GitHub token cannot be empty
```

The action passes the input as an **environment variable**, and zizmor's
`--gh-token` is env-backed through clap — which distinguishes *unset* (fine)
from *set-but-empty* (rejected) at argument parsing, before any audit runs.
`online-audits: false` does not avoid it. The default was restored, with a
comment in the workflow recording the failure so the same hardening is not
retried.

Three lessons worth keeping:

1. **The only change with no functional justification was the one that broke
   it.** Everything load-bearing — digests, permissions,
   `persist-credentials: false` — worked first time.
2. **It was invisible to local tooling by construction.** zizmor validates
   format, Prettier validates syntax; neither executes the action. Only a real
   run could surface it.
3. **Verify against a real pipeline before declaring done.** Static analysis
   proved the configuration was well-formed, not that it ran.

---

## Replicating this in the next repository

Copy the four files, in this order:

1. `.github/zizmor.yml` — verbatim.
2. `renovate.json` — verbatim **except** the `packageRules` guard, which is
   specific to `Azure/static-web-apps-deploy`. Keep it only if that action is
   used.
3. `.github/workflows/zizmor.yml` — verbatim. Land it **after** the tree already
   reports zero findings, so the gate arrives green.
4. `SECURITY-PIPELINE.md` — as a *template*. Its exceptions are repository-
   specific and must be re-derived, not copied.

Then, in order:

1. Pin the existing workflows and add `permissions:` blocks until zizmor reports
   0 findings.
2. Merge to the default branch **before** installing Renovate — it reads config
   only from the default branch, and installing first makes it onboard with
   defaults: no cooldown, no digest pinning, no guard.
3. Install Renovate, scoped to that repository only.
4. Enable Dependabot **alerts** only.
5. Create the ruleset with **both** `required_status_checks` and `pull_request`.

### Two traps

**Audit scope differs between local and CI.** The gate passes neither `inputs:`
nor `collect:`, so it audits the whole repository using action defaults — wider
than the `.github/workflows/` scope typically used for a local baseline. That
made no difference in the pilot, which has no composite actions or
`dependabot.yml`. It will differ in a repository that does.

**The release command must be changed at the same time.** A `/bump-release` that
still fast-forwards `acc` locally and pushes will be blocked the first time it
runs after the ruleset lands. Change it in the same pass, not after the failure.

---

Once a change is ready to commit,
[Code Standards](code-standards.md) covers what lint, format, hooks and CI
enforce in each repository.
