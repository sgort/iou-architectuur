---
scope: cross-cutting
verified:
  date: 2026-09-20
  against:
    CPSV Editor: "1868087"
    Linked Data Explorer: "0e7733e"
    RONL Business API: "6ca80f2"
---

# Supply-Chain Pinning

!!! info "Verification status"
    All three repositories' claims were re-checked on **20 September 2026**, against
    `1868087`, `0e7733e` and `6ca80f2`: every `uses:` reference listed and counted,
    rulesets read from the API, `.nvmrc`, `.npmrc` and every `runs-on:` read from the
    workflow files, and `renovate.json` read rule by rule.

    **A batch of supply-chain work landed on all three `acc` branches on 19 September
    2026**, and it falsified more of this page than any previous release: the static
    web apps are now built on the runner, every repository names its Node version once
    and exactly, every job runs on a pinned runner image, a package-manager cooldown
    exists, and the build checks are required on `acc`. The superseded reasoning is
    kept below rather than deleted — it explains why the fixes are shaped the way they
    are — but it is marked as history wherever it appears.

Nothing a pipeline downloads or executes may float. No `latest`, no empty
versions — a hash, digest or verified checksum wherever one exists.

This page describes how that policy is enforced for **GitHub Actions** — the
`uses:` references a workflow downloads and runs — why it is enforced *inside*
each repository rather than at the organisation level, and, just as importantly,
what it deliberately does not protect. It is cross-cutting: the mechanism is the
same in every repository that has adopted it, and the same four files are copied
into the next one.

Three neighbouring topics have pages of their own, because each is a control in its
own right rather than a part of this one:

| Page | What it covers |
|---|---|
| [Branch Protection](branch-protection.md) | The rulesets that turn these checks into a gate, and which checks each branch requires |
| [Dependency Scanning](dependency-scanning.md) | The other half of the supply chain — the npm tree, and the code, scanned by Semgrep |
| [The GitLab Mirror](the-gitlab-mirror.md) | The second copy no runner can reach, and the release-time check that watches it |

---

## Why in-repo rather than org-level

`github.com/ictu` already enforces hash-pinned GitHub Actions at the
organisation level. The IOU repositories are not in that organisation — they
live under `github.com/sgort`, where their pull requests, issues and every gate on
this page run, and are mirrored to the
[open-regels.nl GitLab instance](https://git.open-regels.nl) — so they inherit none
of that enforcement.

The recorded decision is to build the controls **inside each repository**, where
they travel with the code regardless of which remote hosts it, rather than
migrating the repositories into the `ictu` organisation. Two alternatives were
considered and rejected: pinning and upgrading to the latest majors in one step
(which couples "make immutable" with "change runner behaviour", leaving a broken
deploy undiagnosable between the two), and forking the actions into an IOU-owned
namespace (disproportionate for a handful of actions, and it relocates the trust
problem rather than solving it).

!!! note "GitLab holds a mirror only — for the repositories on this page"
    The three application repositories covered here run all their CI/CD on GitHub
    Actions and contain no `.gitlab-ci.yml`, so "extend the policy to GitLab" is
    vacuous for them: their entire attack surface is the GitHub workflows.

    The corollary is that **the mirror is outside every gate on this page** — see
    [The GitLab Mirror](the-gitlab-mirror.md).

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
| **RONL Business API** | ✅ | ✅ | ✅ | ✅ `acc supply-chain gate`, and `main promotion gate` on `main` |
| **Linked Data Explorer** | ✅ | ✅ | ✅ | ✅ `acc supply-chain gate`, and `main promotion gate` on `main` |
| **IOU Architecture Docs** (this site) | ❌ | ❌ | ❌ | ❌ |

The CPSV Editor is the pilot, adopted in v2026.08.2; RONL Business API followed
within the same week, and Linked Data Explorer in v2026.08.7 — taking its
findings from **40 to 0** across twenty action references in six deployment
workflows. All three rulesets are named `acc supply-chain gate`, target
`refs/heads/acc`, are `active`, and carry **zero bypass actors**; each requires a
pull request, a passing `audit` check, a passing `scan` — the Semgrep job described in
[Dependency Scanning](dependency-scanning.md), required in the CPSV Editor and the
Linked Data Explorer since v2026.09.3 and in the RONL Business API since 19 September
2026 — and, since that same date, each repository's build and deploy checks. The full
per-branch list is on [Branch Protection](branch-protection.md#what-blocks-a-merge).

Adoption is not uniform, and the differences are worth knowing rather than
flattening:

| | CPSV Editor | RONL Business API | Linked Data Explorer |
|---|---|---|---|
| Action references pinned | 12 / 12 | 31 / 31 | 24 / 24 |
| Workflows carrying them | 5 | 10 | 8 |
| Action majors | **v7** (since v2026.09.0) | **v7** | **v7** (since v2026.09.2) |
| Blocks deletion / non-fast-forward | no | **yes** (since v2026.09.7) | **yes** |
| Merge method restricted *in the ruleset* | no — repository setting only | **yes** | **yes** |
| `skip_app_build` | **set on both deploy steps** | **set on all six deploy steps** | **set on both frontend deploy steps** |
| Backend deployed by CI | n/a | **no** — script from a developer machine¹ | **yes** — `azure/webapps-deploy` |

¹ Not for want of trying, and **not for the reason long assumed**. The standing
theory was that `azure/webapps-deploy` authenticates over SCM basic auth, which
Azure now disables by default, and that the route forward was OIDC with a
federated credential. Tested against a real failed run in v2026.08.34, that was
**disproved — OIDC is not needed**, and the blocker is now open rather than
diagnosed. Worth stating, because a plausible-sounding cause that has been ruled
out is more useful written down than quietly dropped.

**All three now set `skip_app_build`, and the row above is the one that moved on
19 September 2026.** Until then the CPSV Editor and the Linked Data Explorer set it
nowhere, and the consequence was the sharpest gap on this page: where the flag is unset,
Oryx builds the production bundle inside the floating vendor container, so lockfile
integrity covers only what is tested. The RONL Business API had already closed it; the
other two followed. The two `ropa-site` workflows are the remaining exception and
correctly so — that package is a static `index.html` plus a `staticwebapp.config.json`,
with nothing to build.

**Two of the three gate `main` as well.** The Linked Data Explorer's
`main promotion gate` ruleset was created on 9 September 2026, before the first promotion
pull request was opened: deletion and non-fast-forward blocked, a pull request with merge
commits only, `audit` and `scan` required, zero bypass actors. It mirrored the `acc`
ruleset exactly, save for one parameter, deliberately:
`require_extra_approval_for_unattributed_changes` is `true` on `acc` and
`false` on `main`, where GitHub's default of `true` — stored when the parameter
was *omitted* from the create call — would have required an approval no
single-maintainer repository can give, and deadlocked the promotion. **Read a
ruleset back after writing it**; the create response's shape does not show the
defaults it filled in.

**That mirroring ended on 19 September 2026.** The build and deploy checks were added to
`acc` and not to `main`, so `acc` now requires strictly more in both repositories, and a
promotion pull request is held to less than the pull requests it carries. That is
deliberate rather than an oversight: the production deploy workflows kept their
trigger-level path filters, and a required check that never reports wedges a pull request
permanently — see
[how a path-filtered workflow became requireable](branch-protection.md#how-a-path-filtered-workflow-became-requireable).

The RONL Business API created its own `main promotion gate` on 12 September 2026, on
the same pattern and for a sharper reason: until that day `main` carried only classic
protection — a pull request required, **zero** required status checks,
`allow_force_pushes` on and `enforce_admins` off — so the branch that deploys production
was the *less* protected of its two. It requires `audit` and **still not `scan`**, which
its `acc` ruleset has required since 19 September 2026. The original reason — that every
deploy workflow there was push-only, and a required check that never reports on a pull
request wedges it permanently — now holds only for the `*-prod` pair; its four `*-acc`
workflows do trigger on `pull_request`, and their checks are required.

That leaves the CPSV Editor as the one repository whose ruleset targets
`refs/heads/acc` only, so its `main` is not covered by the guarantees an `acc` pull
request gets. That is a decision rather than a gap: its `main` requires a pull request but no status checks,
weighed and kept on 11 September 2026
([ttl-editor#131](https://github.com/sgort/ttl-editor/issues/131)). The argument against
it stands, and is worth keeping in view — the promotion pull request is the one carrying
changes into production, and *"already checked on `acc`"* is true of the commits, not of
the merge. If it is revisited, `audit` and `scan` are the two that could be required
today: both trigger on every pull request, so neither can go missing on any base. The
deploy check cannot, as `main` stands — `Deploy PROD (white-sky)` keeps `paths-ignore`
on its `pull_request` trigger, so a documentation-only promotion never starts it, and a
required check that never reports wedges the pull request. **That constraint is no longer
structural, only unapplied**: the `changes`-job pattern that made the `acc` deploy checks
requireable on 19 September 2026 would work here too, and was simply not extended to the
production workflows. See
[how a path-filtered workflow became requireable](branch-protection.md#how-a-path-filtered-workflow-became-requireable).

The rulesets are also not identical in shape, which the table's last two rows
record. The CPSV Editor's is now the only one that does not block branch deletion and
non-fast-forward pushes; the RONL Business API's `acc` gained both on 12 September 2026,
a month after its `main` got them — two rulesets in one repository differing in a way
nobody had decided. And while all three end up allowing merge commits only,
two of them say so *in the ruleset* while the CPSV Editor relies on the
repository-level setting alone — see
[Merge method](branch-protection.md#the-merge-method-is-a-setting-not-a-rule). All three reach the
same place; only two are belt *and* braces.

Ruleset shapes re-verified on 20 September 2026 for all three, with
`gh api repos/<owner>/<repo>/rules/branches/<branch>` — which reports the effective rules
from every ruleset at once, where reading one ruleset, or the classic protection endpoint
alone, gives the wrong answer. Pin counts were re-derived the same day by listing `uses:`
references on each `acc` head.

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

## The four files

Four files, copied into each repository in this order. The GitHub setting that turns
them from checks into a gate — the branch ruleset — is the fifth piece, and it lives on
[Branch Protection](branch-protection.md).

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

The tool version is pinned inline like everything else here, and Renovate does
**not** maintain it: it is an `npx` argument, not a manifest entry, so it is bumped
by hand.

**The zizmor version is the opposite case**, although this page and all three
repositories' own records described it the same way until mid-September 2026. It is
the `version:` input of `zizmorcore/zizmor-action` — `1.29.0` in the Linked Data
Explorer — and Renovate's github-actions manager maps that input to the Docker image
`ghcr.io/zizmorcore/zizmor`, so Renovate **does** maintain it. It normally moves in
the same *github actions* group pull request as the action bump it depends on, and it
has to: the action only runs zizmor versions in its own digest table, so zizmor
1.30.1 needs zizmor-action v0.6.4. The two clear the cooldown separately, though, so
a group branch can carry the image update alone for a while — and the audit fails
until the action catches up. That failure is correct, not a flake.

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
- **`prConcurrentLimit: 5`** — a cap on how many dependency pull requests are
  open at once.
- **`vulnerabilityAlerts` with `minimumReleaseAge: null`** — the fast route for
  security advisories.

Three rules followed from the RONL Business API's fixes of 14 September. The Linked
Data Explorer carries all three since v2026.09.5; the CPSV Editor carries the first,
since its own v2026.09.5:

- **Lock-file maintenance is exempt from the pull-request limits** —
  `prConcurrentLimit: 0` and `prHourlyLimit: 0` on its rule alone. Holding majors
  behind approval was meant to keep a slot free for it, and could not: the concurrent
  count includes every open Renovate pull request, security ones included.
- **Minor updates of pre-1.0 packages wait for approval, like majors.** Semver gives
  `0.x` no compatibility promise, but Renovate classifies 0.4 → 0.5 as minor.
- **`engines` floors are widened, not bumped.** `rangeStrategy: "bump"` had rewritten
  `engines.node` to the newest release three times; the floor is a minimum the
  repository chooses, not a version to chase.

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

#### The cooldown stops at the manifest

`minimumReleaseAge` holds back the updates Renovate *proposes*. It does not reach the
transitive tree, and Renovate's own
[documentation](https://docs.renovatebot.com/key-concepts/minimum-release-age/) says why:
for `lockFileMaintenance` it is *"not possible, as we delegate to the package manager to
perform the required changes"*. All three repositories run lock-file maintenance weekly, so
until 19 September 2026 **a weekly refresh could pull in a transitive version published
that morning**, and so could any `npm install` a developer ran locally.

Renovate's recommendation, and ICTU's guideline, is to configure the cooldown in the package
manager as well — for npm, `min-release-age` in `.npmrc`. **All three repositories now carry
a root `.npmrc` setting `min-release-age=14`**, matching the 14 days `minimumReleaseAge`
already holds Renovate to. Renovate reads it, and for its own update pull requests applies
whichever cutoff is stricter.

What it covers is narrower than it looks, and each limit was measured rather than assumed:

| Limit | Consequence |
|---|---|
| **`npm ci` ignores it by design** ([npm/cli#9281](https://github.com/npm/cli/issues/9281)) | CI only ever runs `npm ci`, so **CI cannot fail on the cooldown** — and cannot enforce it either. The setting governs `npm install`, `npm update` and lock-file maintenance |
| **npm older than 11.10 ignores it silently** | No warning, no error, no effect. Whether a repository is covered therefore depends on which npm its Node bundles |
| **Node 22.23.2 bundles npm 10.9.8** | So the **Linked Data Explorer and the RONL Business API are not covered by their own setting** on a machine following `.nvmrc` |
| **Node 24.20.0 bundles npm 11.19** | So the **CPSV Editor is** covered |
| `scripts/check-deps.sh` warns on npm below 11.10 | At every dev-server start and every push, in all three — the gap is surfaced rather than left to be discovered |

The cooldown may be skipped for an urgent security fix, as the guideline allows: set the
flag to zero days on that one command line, never in the file, and say why in the pull
request. See [ICTU Dependency Guideline](ictu-dependency-guideline.md), recommendation R6.

#### What is exempted, and why each exemption is written down

| Dependency | Held | Reason |
|---|---|---|
| `Azure/static-web-apps-deploy` | Entirely | Renovate's `github-tags` datasource resolves `@v1` to the 2021 **tag** while the workflows pin the **branch**, so a routine-looking digest update would silently revert the production deploy step to 3.5-year-old code — and the cooldown offers no protection whatsoever, the target commit being years old |
| `tailwindcss` | Major only | **Still held after the Vite migration, for a different reason.** It originally blamed `react-scripts`, and v4 now resolves cleanly. What blocks it is `postcss.config.js` declaring `tailwindcss` as a PostCSS plugin — v4 moved that plugin into `@tailwindcss/postcss`, which is what the failing pull request could not compile. Under Vite the idiomatic setup is the `@tailwindcss/vite` plugin rather than a ported PostCSS pipeline, so it is a piece of work with its own acceptance run, and the rule is removed as part of it |
| `eslint` | Major only | eslint 10 **resolves and passes** — npm prints *"ERESOLVE overriding peer dependency"* and installs anyway — while three plugins run outside their declared peer range (`eslint-plugin-react` caps at `^9.7`, `jsx-a11y` and `import` at `^9`). A green build is not evidence here, which is exactly why it needs a rule. Re-checked when `eslint-plugin-react` names `^10` in its peers |

Two properties make these exemptions honest rather than convenient. Only the **major**
is held, so minor and patch updates keep flowing. And each rule is written to be
*removed* by a specific future event rather than left as an open-ended exception nobody
revisits. **One already has been**: `typescript` was held because `react-scripts`
peer-required `^3.2.1 || ^4`, so Renovate could not even generate a lockfile for v7 — and
the rule went with `react-scripts` in the Vite migration, exactly as it said it would.
`tailwindcss` is the instructive case the other way: its original reason went too, and
it stayed held **for a new reason, written down as a new reason** rather than left
standing on a stale one.

## What this means day to day

```
push to a feature branch   → nothing runs (workflows trigger on acc/main only)
open a PR against acc      → audit + scan + Build and Deploy run
audit fails                → merge blocked by the ruleset
scan fails                 → merge blocked, in all three since 19 Sep 2026
build or tests fail        → merge blocked on acc, in all three since 19 Sep 2026
all required checks pass   → merge allowed
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

**The Static Web Apps container still cannot be pinned** — what changed on 19 September
2026 is that it no longer builds what ships, only uploads it.
`Azure/static-web-apps-deploy` is a three-line wrapper whose
`action.yml` declares `runs: using: docker, image: "Dockerfile"`, and that
Dockerfile is `FROM mcr.microsoft.com/appsvc/staticappsclient:stable`. Pinning
the action makes the wrapper immutable and leaves the payload floating.
Unreachable from our side; it would require Microsoft publishing digest-pinned
image references, or IOU forking the action.

!!! success "One flag decided how badly this bit, and all three now set it"
    **`skip_app_build: true` points `app_location` at an already-built `dist/`**, so the
    container uploads an artifact the pipeline built itself on a pinned `setup-node` via
    `npm ci`. The RONL Business API set it on all six of its deploy steps first; the CPSV
    Editor and the Linked Data Explorer followed on 19 September 2026, each adding an
    explicit build step to their workflows. (References to the action carrying
    `action: 'close'` build nothing and are unaffected.)

    **Until then, the CPSV Editor and the Linked Data Explorer set it nowhere**, and the
    consequence is worth keeping on record because it is the failure mode any repository
    adopting Static Web Apps inherits by default: Oryx ran *inside* the floating image and
    built the production bundle there, making the image the **build toolchain that
    produced the deployed artifact**, not merely an upload step. Lockfile integrity
    covered only what was tested, in two of the three — the majority position was the
    weaker one.

    The two `ropa-site` workflows still do not set the flag. That is correct: the package
    is static files with no build, so there is no install for Oryx to re-resolve.

**`npm ci` integrity now covers what ships.** `package-lock.json` carries a `sha512` per
package and `npm ci` verifies it; where `skip_app_build` is set, the verified install is
the one that produces the deployed bytes, and since 19 September 2026 that is every
deployable in all three repositories.

!!! note "What it looked like when it did not — and how to recognise it"
    The install that produced the deployed bytes was not `npm ci`. Oryx ran
    `npm install`, which honours a lockfile that agrees with `package.json` and quietly
    re-resolves one that does not, where `npm ci` would fail. The CPSV Editor's matched its
    lockfile in the deploy run examined on 13 September 2026 — `up to date, audited 542
    packages` — which was the likely outcome rather than a guaranteed one.

    The tell in a deploy log is a line reading `Oryx Version: …` followed by
    `Downloading and extracting 'nodejs' version '…'` and `Running 'npm install'`. If
    those appear, the artifact was not built by the job that tested it, whatever the
    workflow file says about `setup-node`.

**Each repository now names its Node version once, exactly, in a file every deploy
workflow reads.** This was a general gap until 19 September 2026, and it had two halves:
the version the tests ran on, and the version that shipped. Both are closed.

| Repository | `.nvmrc` | Read by | The shipped bundle is built on |
|---|---|---|---|
| **CPSV Editor** | **`24.20.0`** | both Static Web Apps workflows, via `node-version-file` | the same — built on the runner, uploaded with `skip_app_build: true` |
| **Linked Data Explorer** | **`22.23.2`** | all six deploy workflows | the same |
| **RONL Business API** | **`22.23.2`** | all eight deploy workflows | the same |

`setup-node` decides only what the *runner* uses, so the pin is worth having only once
the runner is what builds. Both halves landed together, which is the right order: pinning
the interpreter while a vendor container re-chose it would have been ceremony.

!!! note "What the pins were before, and why the shape changed"
    The CPSV Editor read a bare `'24'` — a major, so whichever 24.x patch was current at
    run time — governing lint and tests only, while Oryx built the shipped bundle on a
    Node it chose itself (22.22.0, in run 34622800899). The Linked Data Explorer carried
    **three** exact literals in three workflow files — `20.20.2` frontend, `22.23.2`
    backend, `24.19.0` audit — with nothing keeping them in step, which its own
    [#113](https://github.com/sgort/linked-data-explorer/issues/113) recorded; its
    frontend shipped on Oryx's 22.22.0 rather than the 20.20.2 its tests ran on
    ([run 34612031473](https://github.com/sgort/linked-data-explorer/actions/runs/34612031473)).
    The RONL Business API was first to the file, at `22.22.0`, since bumped to `22.23.2`.

    **One file beats three literals**, and that is the maintainable half rather than a
    stylistic preference: Renovate's `node` manager parses `.nvmrc`, so the file stays
    current as a reviewed pull request, where hand-written literals rot silently and
    separately. Prefer the file.

    One trap came with it. A `paths:` filter that does not name `.nvmrc` means a Node bump
    builds and deploys **nothing** — the version changes and no artifact moves. Every
    deploy workflow's filter in all three repositories now lists `.nvmrc` for exactly that
    reason.

The RONL Business API's case also shows what the gap actually costs. Both its App Service
plans run `NODE|22-lts`, while eight workflows built the deployed artifact on Node 20 —
so the artifact was built on one major and served by another, silently, until
[#36](https://github.com/sgort/ronl-business-api/issues/36) closed. Its `engines.node`
moved to `>=22` in the same change, because a floor of `>=20.13.0` permits precisely the
mismatch being removed.

**One deliberate exception in each, and it is not the shared file.** Every `zizmor.yml`
sets its own `node-version: '24.20.0'` — an exact literal, deliberately separate from
`.nvmrc` — because its `renovate-config-validator` step needs Node 24 whatever the
application runs on. `renovate` declares `engines.node ^24.11.0`, and npm accepts a
mismatch with a warning rather than refusing, so the validator had been running
unsupported and green. That pin is load-bearing and must not be swept into the shared
file; in the CPSV Editor it happens to equal `.nvmrc` today, which is coincidence rather
than coupling. Renovate's `node` manager maintains both.

**Two things still float, and neither is a `uses:` reference for zizmor to see.** Checked
on 20 September 2026 at each repository's `acc` head:

- **The App Service runtime.** Both backends are hosted on `NODE|22-lts`, which floats within
  the major — the RONL Business API's recorded in
  [#36](https://github.com/sgort/ronl-business-api/issues/36), the Linked Data Explorer's in
  the assessment. Whether the platform allows an exact pin is not yet established.
- **Container images.** The RONL Business API's local `docker-compose.yml` uses
  `operaton/operaton:latest` and `alpine:latest`, and its Skosmos deployment uses
  `quay.io/natlibfi/skosmos:latest`. Its other images carry versions — `postgres:16-alpine`,
  `redis:7-alpine`, `keycloak:23.0` — and none carries a digest.

Two more were on that list until 19 September 2026 and are now closed:

- **The runner image**, which ran on `ubuntu-latest` in every job — 6 in the CPSV Editor,
  12 in the Linked Data Explorer, 13 in the RONL Business API — and moved whenever GitHub
  moved it. **Every job in all three now names `ubuntu-24.04`**: 7, 15 and 17 jobs
  respectively, the counts having grown with the `changes` jobs that made the build checks
  requireable. The only surviving `ubuntu-latest` string in any of them is a comment in
  `semgrep.yml` explaining why its Python install needs a venv.
- **The Linked Data Explorer's backend deploy package**, which copied `package.json` into
  the deploy directory **without `package-lock.json`** and ran
  `npm install --production --omit=dev` there, so the backend that shipped re-resolved
  every caret range at deploy time — after `npm ci` had tested the locked tree. Both
  backend workflows now stage the package and run
  `npm ci --omit=dev --workspace=@linked-data-explorer/backend --no-audit --no-fund`
  against the workspace root's lockfile, which is the only lockfile there is.

**The RONL Business API's backend is the one that did not move.** Its deploy scripts still
install from a developer machine without the lockfile
([#34](https://github.com/sgort/ronl-business-api/issues/34)), and its own `.npmrc` records
a second reason the cooldown does not reach it: npm reads a project `.npmrc` only from the
project root, and that install runs in a separate `deploy/` folder.

[ICTU Dependency Guideline](ictu-dependency-guideline.md) records these against the
recommendations they miss, and
[linked-data-explorer#119](https://github.com/sgort/linked-data-explorer/issues/119) tracks
the work.

**zizmor validates pin _format_, never pin _truth_.** A wrong or hostile digest
with a plausible `# v7.0.1` comment passes zizmor, Prettier and human review
alike. Nothing re-checked that a digest resolves to the tag it claims — until
`check-supply-chain`, below.

**The register drifts — and has.** Renovate updates workflow pins and never
touches `SECURITY-PIPELINE.md`, and nothing checks that the two agree. This was
written as a prediction in August 2026 and was true within a week: as of
v2026.09.0 the CPSV Editor's register still listed `actions/checkout` at
`a37ce91…` (v3.7.0) and `actions/setup-node` at `49933ea…` (v4.4.0), while the
workflows had moved to `3d3c42e…` (v7.0.1) and `820762…` (v7.0.0). Its
`node-version: '20'` exception was likewise stale the moment the workflows took
Node 24. The register has since been reconciled in all three repositories, and
`check-supply-chain` now fails the audit in each of them if it drifts again.

!!! warning "Where the digests on this page come from"
    The pins quoted here are read from the **workflow files**, not from any
    repository's register, precisely because the two are known to disagree.
    When they conflict, the workflow is what runs.

Those last two gaps were the motivation for the `check-supply-chain` preflight,
which **shipped in September 2026 and now runs in all three repositories** — see
[below](#check-supply-chain-the-preflight-zizmor-cannot-be).

!!! warning "It drifted, was caught by a documentation review, and was reconciled by hand"
    Between the v7 action upgrades and 30 August 2026, RONL Business API's
    register still listed the superseded v4 digests for `actions/checkout`,
    `actions/setup-node` and `actions/upload-artifact` — every gate green
    throughout. A quieter second drift came with it: `setup-node` had gone from
    ×8 to ×9 when a config-validator step was added, and the `renovate@44.50.3`
    pin that step introduced was missing from the table entirely. **A count is as
    easy to falsify as a digest**, and neither the audit nor review catches it.

    It was reconciled in v2026.08.34 and matches today at **31 `uses:`
    references across ten workflows**, digests agreeing — re-counted on 12 September
    2026, the Semgrep workflow having added one reference since. That first
    reconciliation was manual and prompted by a docs review rather than by any check
    in the repository, which is the argument for the preflight rather than against it.
    The preflight now exists and blocks in all three, so "the register matches the
    workflows" is checked on every pull request rather than assumed.

    One inconsistency survives inside that register, in prose rather than in the
    table: its *Keeping this register true* section still quotes the old
    `30 uses: references across 9 workflows` headline. The check reads the first
    match in the file and so still binds on the real headline and stays green — but
    two numbers in one document disagree, and that is worth fixing in the repository
    rather than here.

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

## `check-supply-chain` — the preflight zizmor cannot be

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
| Linked Data Explorer | ✅ blocking, since v2026.09.2 |
| RONL Business API | ✅ blocking, since v2026.09.7 |

**All three block.** The RONL Business API's ran non-blocking from adoption until 12
September 2026, for a stated reason rather than out of caution: Renovate rewrites workflow
pins and never touches `SECURITY-PIPELINE.md`, so every action-bump pull request fails the
register half until the register is updated by hand, and blocking on that would fail a
required check on routine dependency updates — *which is how gates get resented and then
bypassed*.

What retired that argument was evidence, not a tool change
([#83](https://github.com/sgort/ronl-business-api/issues/83)): its own `zizmor-action`
v0.6.2 → v0.6.4 bump had the register fixed on Renovate's branch and the check green there
before the merge, which is the habit below. The Linked Data Explorer had promoted its step
on the same evidence in v2026.09.2.

**The same pull request supplied the argument against waiting longer**, and it is the more
interesting half. Before the register was fixed, the check reported a real finding — the
workflow pinning v0.6.4 while the register recorded only v0.6.2 — while the step, the job
and the checks list all read *success*. `continue-on-error` rewrites the step's reported
conclusion as well as the job's, and the honest outcome is not exposed by the REST API at
all, so nothing outside that one log knew. A check nobody can see fail is a check that has
to be remembered, which is the condition the register drifted in to begin with.

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
catch, caught on the branch rather than after the merge. So each repository's
`SECURITY-PIPELINE.md` records the rule:

!!! tip "When a Renovate pull request bumps an action, update the register on that pull request's branch — before merging it"
    **Not afterwards.** The check runs on the pull request, so a register fixed
    after the merge leaves that pull request red for its whole life. It also makes
    the step impossible to promote: if no bump can ever present a green result,
    blocking would mean no action ever gets updated.

The Linked Data Explorer exercised this twice — on the `checkout` v7.0.1 and
`setup-node` v7.0.0 bumps — before promoting its step. In both, the register moved
on the bump's own branch, the check went green there, and the pull request merged
green. That is the evidence its promotion rested on, and the RONL Business API's
`zizmor-action` v0.6.4 bump supplied the same evidence there on 12 September 2026.

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

---

