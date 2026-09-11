---
scope: cross-cutting
verified:
  date: 2026-09-09
  against:
    CPSV Editor: "bbda389"
    Linked Data Explorer: "007b350"
    RONL Business API: "04e38c8"
---

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

!!! note "GitLab hosts code only — for the repositories on this page"
    The three application repositories covered here run all their CI/CD on GitHub
    Actions and contain no `.gitlab-ci.yml`, so "extend the policy to GitLab" is
    vacuous for them: their entire attack surface is the GitHub workflows.

    **The Norm Editor is the exception, and it is not covered by this page.** Its
    pipeline *is* GitLab CI, it builds and pushes its own Docker images to Azure
    Container Registry rather than handing a bundle to a vendor action, and none of
    the five mechanisms below exists there in the same form — there are no `uses:`
    references to digest-pin, no zizmor equivalent wired in, and no `acc` branch to
    protect, because `main` is its only integration branch. Extending the policy to
    it is a separate piece of work against a different CI system, not a fifth row in
    the table below.

---

## Adoption status

| Repository | Pinned workflows | `audit` gate | Renovate | `acc` ruleset |
|---|:---:|:---:|:---:|:---:|
| **CPSV Editor** (`ttl-editor`) — pilot | ✅ | ✅ | ✅ | ✅ `acc supply-chain gate` |
| **RONL Business API** | ✅ | ✅ | ✅ | ✅ `acc supply-chain gate` |
| **Linked Data Explorer** | ✅ | ✅ | ✅ | ✅ `acc supply-chain gate` |
| **IOU Architecture Docs** (this site) | ❌ | ❌ | ❌ | ❌ |

The CPSV Editor is the pilot, adopted in v2026.08.2; RONL Business API followed
within the same week, and Linked Data Explorer in v2026.08.7 — taking its
findings from **40 to 0** across twenty action references in six deployment
workflows. All three rulesets are named `acc supply-chain gate`, target
`refs/heads/acc`, are `active`, and carry **zero bypass actors**; each requires a
pull request and a passing `audit` check.

Adoption is not uniform, and the differences are worth knowing rather than
flattening:

| | CPSV Editor | RONL Business API | Linked Data Explorer |
|---|---|---|---|
| Action references pinned | 11 / 11 | 30 / 30 | 23 / 23 |
| Action majors | **v7** (since v2026.09.0) | **v7** | v4 (one v3) |
| Blocks deletion / non-fast-forward | no | no | **yes** |
| Merge method restricted *in the ruleset* | no — repository setting only | **yes** | **yes** |
| `skip_app_build` | not set | **set on all six deploy steps** | not set |
| Backend deployed by CI | n/a | **no** — script from a developer machine¹ | **yes** — `azure/webapps-deploy` |

¹ Not for want of trying, and **not for the reason long assumed**. The standing
theory was that `azure/webapps-deploy` authenticates over SCM basic auth, which
Azure now disables by default, and that the route forward was OIDC with a
federated credential. Tested against a real failed run in v2026.08.34, that was
**disproved — OIDC is not needed**, and the blocker is now open rather than
diagnosed. Worth stating, because a plausible-sounding cause that has been ruled
out is more useful written down than quietly dropped.

Two consequences follow from that table. **Where `skip_app_build` is not set,
Oryx builds the production bundle inside the floating vendor container**, so
lockfile integrity covers only what is tested — true for the CPSV Editor and the
Linked Data Explorer, but not for RONL Business API. And **the gate is enforced
on `acc` only, in every repository**: the ruleset targets `refs/heads/acc`
everywhere, so a production deploy is not covered by the guarantees an `acc`
pull request gets. The CPSV Editor is the only one that even carries the four
artifacts on `main` — but carrying the files is not the same as enforcing them,
and nothing enforces them there.

The rulesets are also not identical in shape, which the table's last two rows
record. Only the Linked Data Explorer's blocks branch deletion and
non-fast-forward pushes. And while all three end up allowing merge commits only,
two of them say so *in the ruleset* while the CPSV Editor relies on the
repository-level setting alone — see
[Merge method](#the-merge-method-is-a-setting-not-a-rule). All three reach the
same place; only two are belt *and* braces.

Ruleset shapes verified with `gh api repos/<repo>/rulesets` on 4 September 2026;
pin counts and majors read from the workflow files at CPSV Editor v2026.09.0.

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

Pins are taken at the **then-current major and not upgraded**, so *adopting* the
policy is behaviour-preserving. Version upgrades arrive separately, as reviewed
Renovate pull requests. That separation is what lets the first live run prove
the *pinning* worked, without a simultaneous upgrade muddying the result.

The separation then does its job: in the CPSV Editor, `actions/checkout` and
`actions/setup-node` have since moved from v3.7.0 and v4.4.0 to **v7.0.1**
(`3d3c42e…`) and **v7.0.0** (`820762…`), each as its own reviewed pull request
under the cooldown. The pin is not a freeze — it is a record of exactly which
bytes run, changed only by a diff someone approved.

Each workflow also declares least privilege — `permissions: contents: read` at
workflow level, with a deploy job adding only `pull-requests: write` for the
Static Web Apps action's PR comments, and a close-PR job taking an empty
`permissions: {}` block.

`actions/checkout` sets `persist-credentials: false`. Before this, a live
`GITHUB_TOKEN` was written into `.git/config` and mounted into a closed-source
third-party container on every run. That is a real hole closed, not a cosmetic
lint fix; the deploy action authenticates with explicitly passed tokens instead.

### 3. `.github/workflows/zizmor.yml` — the gate

Runs [zizmor](https://github.com/zizmorcore/zizmor) under job name **`audit`**,
on **every** pull request and on pushes to `acc` and `main`.

!!! danger "The `branches` filter had to go, and the reason is worth reading"
    Until September 2026 the audit triggered on `pull_request` only for `acc`
    and `main`. Combined with the ruleset making `audit` a required check on
    `acc`, that produced a pull request which could never merge — and which
    looked perfectly healthy while it did.

    A **stacked** pull request, based on a feature branch rather than on `acc`,
    matched no trigger and so accumulated no audit at all. Because the ruleset
    applies only while the base **is** `acc`, GitHub reported the pull request
    as **CLEAN with zero checks**. It read as ready and was not. The moment its
    parent merged, GitHub auto-retargeted it onto `acc`, the ruleset began
    applying, the required check was missing — and a retarget emits no
    `pull_request` event, so nothing ever backfilled it. Permanently blocked.
    (If one is ever stuck this way: `gh pr close <n> && gh pr reopen <n>`;
    `reopened` is in the default types set, and by then the base is `acc`.)

    A `paths` filter is the same hole in another dimension — it lets a pull
    request skip the gate by touching nothing watched, where a `branches`
    filter lets it skip by targeting an unwatched base. The audit carries
    neither. `push` stays filtered, because `acc` and `main` are the only
    branches whose post-merge state is worth re-auditing.

    **All three repositories now run the audit on every pull request** — the
    CPSV Editor in v2026.08.3, RONL Business API and the Linked Data Explorer
    following in early September, each independently reaching the same shape.
    It was not a theoretical fix in any of them: it cost four rounds of manual
    intervention in the Linked Data Explorer and blocked a pull request outright
    in RONL Business API before the filter came off.

    **Do not copy this shape into a deploy workflow.** Those fail in the
    opposite direction: an absent filter on the *audit* makes a required check
    silently missing, while an absent filter on a *deploy* silently exhausts a
    bounded pool of staging environments. The rule is **audit widely, deploy
    narrowly**.

Three zizmor inputs are deliberate:

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

#### The gate also validates `renovate.json`

The gate enforced that every action reference is a commit hash but had nothing
to say about the file that keeps those hashes current — and **pinning without
automated updates decays into an unpatched tree**, so a Renovate that has
silently stopped running is precisely the supply-chain failure this audit
exists to catch.

That is not hypothetical. In the Linked Data Explorer, five keys used as JSON
comments were rejected as invalid configuration and Renovate stopped opening
pull requests as a precaution. Nothing in CI noticed; the repository looked
green while half its policy was inert.

A second step now runs `renovate-config-validator`, with four deliberate
choices:

| Choice | Why |
|---|---|
| Runs in the existing `audit` job | It is therefore covered by the current required status check, with no ruleset change |
| `if: always()` | One run reports on **both** halves of the policy, rather than a zizmor failure hiding a config failure |
| `--strict` | Also fails on configuration Renovate would silently auto-migrate. That is how `baseBranches`, renamed upstream to `baseBranchPatterns`, was caught rather than living on as a deprecated key that still "worked" |
| No filename argument | Passing one switches the validator into *global config* mode, which applies different rules than the repository config the file actually is — it validates happily and tells you nothing useful |

The tool version is pinned inline like everything else here, and — like the
zizmor version — Renovate does **not** maintain it: it is an `npx` argument,
not a manifest entry, so it is bumped by hand.

A `Set up Node 24` step precedes both. Renovate declares
`engines.node ^24.11.0` while the runner defaults to Node 22; npm accepts that
mismatch with a warning rather than refusing, so the validator ran unsupported
and reported green — the kind of mismatch that keeps working right up until it
abruptly does not, at which point the gate fails for a reason unrelated to
anything anyone changed. It is placed *before* the zizmor step deliberately: a
step following a failed one is skipped, so putting it after would leave the
validator's `always()` condition running on whatever Node the runner defaulted
to.

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
- **`prConcurrentLimit: 5`** — a cap on how many dependency pull requests are
  open at once.

That last rule is the one most cooldown policies omit, and its absence is why
people disable such policies mid-incident: **without it the cooldown would delay
exactly the updates that must not wait.** It fires off GitHub's Dependabot
*alerts* feed, so those must be enabled — while Dependabot *security updates*
must stay **off**, or two bots race on the same manifests with only one of them
respecting the cooldown.

**The concurrency cap is not tidiness — it was a collision.** Renovate's default
`prConcurrentLimit` is ten, and the Static Web Apps staging ceiling is also ten.
The two numbers being equal meant a full Renovate queue consumed every staging
environment and the next pull request opened by a human was refused outright:
ten open dependency pull requests held all ten slots, and two unrelated pull
requests had their deploy fail on arrival. It self-perpetuated, too — merging
two freed two slots, and Renovate opened two new pull requests into them within
the minute. Capping at five leaves five permanently available for human work.
Deliberately *not* solved by paying for a higher tier: a bigger ceiling moves
the number at which the same collision happens rather than removing it.

#### What is exempted, and why each exemption is written down

| Dependency | Held | Reason |
|---|---|---|
| `Azure/static-web-apps-deploy` | Entirely | Renovate's `github-tags` datasource resolves `@v1` to the 2021 **tag** while the workflows pin the **branch**, so a routine-looking digest update would silently revert the production deploy step to 3.5-year-old code — and the cooldown offers no protection whatsoever, the target commit being years old |
| `tailwindcss` | Major only | v4 moves its PostCSS plugin into a separate package and requires the configuration rewritten. Doing that under Create React App is throwaway work, because the Vite setup replaces the PostCSS wiring rather than porting it. Left enabled, Renovate re-opened the same failing pull request every cycle — holding a staging slot each time |
| `typescript` | Major only | `react-scripts@5.0.1` peer-requires `typescript "^3.2.1 \|\| ^4"`, so npm cannot resolve v7 at all. The pull request shipped a `package.json` bump with **no lockfile**, because Renovate's lockfile generation failed against that peer constraint. The out-of-sync lockfile was the symptom; `react-scripts` is the cause, and nothing inside the pull request could fix it — `--legacy-peer-deps` would force through a real incompatibility rather than resolve it |

Two properties make those last two exemptions honest rather than convenient.
Only the **major** is held, so minor and patch updates keep flowing. And each
rule is written to be *removed* by a specific future event — the Vite migration,
which deletes `react-scripts` and unblocks both — rather than left as an
open-ended exception nobody revisits.

### 5. The `acc` ruleset — what makes it *enforcement*

A workflow that runs but cannot block is advice. The ruleset converts it into a
gate. In all three adopting repositories the ruleset is named **`acc
supply-chain gate`**, targets `refs/heads/acc`, and is `active` with **zero
bypass actors**:

- `required_status_checks` → context **`audit`**
- `pull_request` → `required_approving_review_count: 0`

Both rules are needed *together*. Requiring the check alone would still let a
direct push to `acc` bypass the gate entirely.

Approvals are `0` because these repositories have a single maintainer and GitHub
does not permit self-approval — requiring `1` would make `acc` unmergeable.
Raise it when a second reviewer exists.

### The merge method is a setting, not a rule

A changelog entry names each commit by its SHA, so any merge strategy that
rewrites hashes orphans every citation in it. The first version of this rule
said *never squash* — and missed that **rebase-and-merge rewrites hashes just as
thoroughly**, deceptively so, because it preserves the commit count while
replacing every hash. That gap surfaced only when someone looked at the actual
merge dropdown.

All three repositories now disable squash and rebase at repository level
(Settings → General → Pull Requests), leaving merge commits only, with
`delete_branch_on_merge` enabled:

```
allow_merge_commit: true    allow_squash_merge: false
allow_rebase_merge: false   delete_branch_on_merge: true
```

GitHub's default button is *Squash and merge*, so without the setting a single
absent-minded click would orphan a release's entire entry. The failure is now
impossible by construction rather than forbidden by prose — which is the general
shape worth copying: **a rule that depends on remembering is a rule that
eventually fails.**

A side effect is that Renovate's dependency pull requests land as merge commits
too. That costs nothing: `--no-merges` already excludes the merge commit from a
changelog range, and the underlying update commit is what an entry should name.

**A repository adopting this template must apply the setting too.** The rule
without it is one click from failing.

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

**The Static Web Apps container cannot be pinned**, and in the pilot it builds
what ships. `Azure/static-web-apps-deploy` is a three-line wrapper whose
`action.yml` declares `runs: using: docker, image: "Dockerfile"`, and that
Dockerfile is `FROM mcr.microsoft.com/appsvc/staticappsclient:stable`. Pinning
the action makes the wrapper immutable and leaves the payload floating.
Unreachable from our side; it would require Microsoft publishing digest-pinned
image references, or IOU forking the action.

!!! warning "How badly this bites depends on one flag, and the three repositories differ"
    **CPSV Editor and Linked Data Explorer set `skip_app_build` nowhere.** Oryx
    therefore runs *inside* that floating image and builds the production bundle
    there, making the image the **build toolchain that produces the deployed
    artifact**, not merely an upload step.

    **RONL Business API sets `skip_app_build: true` on all six deploy steps**,
    pointing `app_location` at an already-built `dist/`. The container uploads an
    artifact the pipeline built on pinned `setup-node` via `npm ci`. (Its other
    three references to the action are `action: 'close'` steps, which build
    nothing.)

    So for RBA's three static sites, lockfile integrity covers **what ships**;
    for the other two it covers only what is tested. The difference is one flag,
    and it is worth preserving deliberately as the rollout continues — the
    majority position is currently the weaker one.

**`npm ci` integrity covers what is tested, not necessarily what is shipped.**
`package-lock.json` carries a `sha512` per package and `npm ci` verifies it. In
the CPSV Editor and the Linked Data Explorer that install feeds lint and the
unit tests only, because Oryx
performs its own install inside the container to produce the deployed bytes;
where `skip_app_build` is set, the verified install is the one that produces
them.

**The Node version floats — in two of three repositories.** This was recorded as
a general gap, "reachable in principle". The Linked Data Explorer reached it in
v2026.09.1, which makes the remaining two a choice rather than a limitation:

| Repository | `node-version` in the deploy workflows |
|---|---|
| CPSV Editor | `'24'` — major only, so whichever 24.x patch is current at run time |
| RONL Business API | `'20'` — major only (its audit job pins `'24'`) |
| **Linked Data Explorer** | **`20.20.2`** frontend, **`22.23.2`** backend, **`24.19.0`** audit — exact patches, with the `engines` floors raised to match |

The Linked Data Explorer's pins landed alongside the workflow digest pins in the
same release, which is the natural moment: the runtime is one more thing the
pipeline downloads, and pinning the actions while leaving the interpreter
floating is half the job. Neither of the other two has an `.nvmrc` or an
`engines` field pinning a runtime.

Note that the CPSV Editor's audit job pins Node **24** for a different reason
entirely — Renovate's `engines.node`, not supply-chain policy — so its presence
there is not evidence the gap is closed.

**zizmor validates pin _format_, never pin _truth_.** A wrong or hostile digest
with a plausible `# v7.0.1` comment passes zizmor, Prettier and human review
alike. Nothing currently re-checks that a digest resolves to the tag it claims.

**The register drifts — and has.** Renovate updates workflow pins and never
touches `SECURITY-PIPELINE.md`, and nothing checks that the two agree. This was
written as a prediction in August 2026 and was true within a week: as of
v2026.09.0 the CPSV Editor's register still lists `actions/checkout` at
`a37ce91…` (v3.7.0) and `actions/setup-node` at `49933ea…` (v4.4.0), while the
workflows had moved to `3d3c42e…` (v7.0.1) and `820762…` (v7.0.0). Its
`node-version: '20'` exception was likewise stale the moment the workflows took
Node 24.

!!! warning "Where the digests on this page come from"
    The pins quoted here are read from the **workflow files**, not from any
    repository's register, precisely because the two are known to disagree.
    When they conflict, the workflow is what runs.

Those last two gaps were the motivation for the `check-supply-chain` preflight,
which **shipped in September 2026 and now runs in all three repositories** — see
[below](#6-check-supply-chain-the-preflight-zizmor-cannot-be).

!!! warning "It drifted, was caught by a documentation review, and was reconciled by hand"
    Between the v7 action upgrades and 30 August 2026, RONL Business API's
    register still listed the superseded v4 digests for `actions/checkout`,
    `actions/setup-node` and `actions/upload-artifact` — every gate green
    throughout. A quieter second drift came with it: `setup-node` had gone from
    ×8 to ×9 when a config-validator step was added, and the `renovate@44.50.3`
    pin that step introduced was missing from the table entirely. **A count is as
    easy to falsify as a digest**, and neither the audit nor review catches it.

    It was reconciled in v2026.08.34 and currently matches: 30 `uses:`
    references across nine workflows, digests agreeing. That reconciliation was
    manual and prompted by a docs review rather than by any check in the
    repository — which is the argument for the preflight, not against it. Until
    it exists, treat "the register matches the workflows" as an assumption.

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

**Do not give the audit a `branches` filter.** It is the obvious symmetry with
the deploy workflows and it is wrong — see
[the gate](#3-githubworkflowszizmoryml-the-gate). Stacked pull requests then
report CLEAN with zero checks and block permanently once GitHub retargets them.

**Set `prConcurrentLimit` below the staging ceiling.** Renovate's default is ten.
If the hosting tier also allows ten staging environments, a full dependency queue
consumes every one of them and human pull requests are refused. Leave headroom
deliberately; raising the tier only moves the number at which the collision
happens.

---

Once a change is ready to commit,
[Code Standards](code-standards.md) covers what lint, format, hooks and CI
enforce in each repository.


---

## 6. `check-supply-chain` — the preflight zizmor cannot be

The two gaps above — pin *truth* and register agreement — are now checked by a
script rather than left as known limitations. It shipped in the CPSV Editor in
v2026.09.1 and was adopted by the other two within days.

### What it checks

| Check | What it catches |
|---|---|
| **Pin truth** | Every digest is resolved against the GitHub API and compared with the version its trailing comment claims. Annotated tags are dereferenced to their commit |
| **Register agreement** | The `Pinned` table is compared with the workflows — digests, version strings, the `(×N)` multiplicities, and the *"N `uses:` references across M workflows"* headline |

The multiplicities are not decoration. In RONL Business API `setup-node` silently
went from ×8 to ×9 when the config-validator step was added, and the register
still said ×8 **with every gate green**. That is the drift this catches.

### Where it runs, and where it blocks

| Repository | State |
|---|---|
| CPSV Editor | ✅ blocking, in the `audit` job |
| Linked Data Explorer | ✅ blocking |
| RONL Business API | ⚠️ **non-blocking**, deliberately — see below |

**RONL Business API's is non-blocking for a stated reason, not out of caution.**
Renovate rewrites workflow pins and never touches `SECURITY-PIPELINE.md`, so
every action-bump pull request fails the register half until the register is
updated by hand. Blocking on that would fail a required check on routine
dependency updates — *which is how gates get resented and then bypassed*.
Promoting it is tracked as
[ronl-business-api#83](https://github.com/sgort/ronl-business-api/issues/83).

The Linked Data Explorer promoted its step to blocking in v2026.09.2 without
waiting for a tool change, because the problem is a habit rather than a defect.

### The habit the register depends on

Renovate rewrites a workflow's digest **and its version comment together**,
honestly and correctly. It was predicted that this made the register safe — the
pair moves as one, so pin truth still holds. **Pin truth does hold. Register
agreement does not**, and a real Renovate pull request said so:

```
[register] actions/checkout: workflow pins 3d3c42e5aac5… (v7.0.1) but
           SECURITY-PIPELINE.md records only 11d5960a3267… (v4.4.0), a37ce9120846… (v3.7.0)
```

The check is right and the register is stale — exactly the drift it exists to
catch, caught on the branch rather than after the merge. So each repository’s
`SECURITY-PIPELINE.md` records the rule — in RONL Business API’s case on `acc`,
where it has not yet been promoted to `main`:

!!! tip "When a Renovate pull request bumps an action, update the register on that pull request's branch — before merging it"
    **Not afterwards.** The check runs on the pull request, so a register fixed
    after the merge leaves that pull request red for its whole life. It also makes
    the step impossible to promote: if no bump can ever present a green result,
    blocking would mean no action ever gets updated.

The Linked Data Explorer exercised this twice — on the `checkout` v7.0.1 and
`setup-node` v7.0.0 bumps — before promoting its step. In both, the register moved
on the bump's own branch, the check went green there, and the pull request merged
green. That is the evidence the promotion rested on, and it is what RONL Business
API needs before #83 can close.

!!! danger "If it proves flaky the answer is `--offline`, never `continue-on-error`"
    The known cost is a network call inside a required job. `--offline` drops the
    pin-truth half and keeps register agreement blocking. `continue-on-error`
    looks equivalent and is not: it **rewrites the step's reported conclusion as
    well as the job's**, so a failing check reports success rather than reporting
    a failure that does not block. One is a narrower check; the other is a check
    that lies.

### It was proved by making it fail

A green run proves nothing about a check that might be silently inert. Acceptance
was a planted wrong digest carrying a plausible comment, a digest changed without
updating the register, and a transport failure with a deliberately invalid token —
which produced four API-error findings rather than silence.

**Its assumptions were also wrong in a way this repository could not show.** Run
against the other two before either adopted it, it reported findings that turned
out to be its own bugs: an action can legitimately be pinned at **two digests**
mid-upgrade, and a register may annotate a version cell (`v1 (branch head)`) where
a workflow comment cannot. Rows are now matched by digest and versions compared on
the leading token. Neither bug was visible in the repository that wrote the
script, which pins every action once and annotates nothing — the same shape as the
defect the script exists to catch.
