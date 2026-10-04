---
scope: cross-cutting
verified:
  date: 2026-10-04
  against:
    CPSV Editor: "4cba989"
    Linked Data Explorer: "9e0d18e"
    RONL Business API: "5c6e716"
---

# Controls at a Glance

Seven pages stand between a change and a deployment: the five controls the
[CI posture deck](ci-posture-deck.md) counts, plus the standards a change is held to on the
way in and the branch rules that make any of it blocking. **One row here, one page** — and
every count, percentage and finding lives on the page that owns it, so there is one place
to correct when a number moves.

## What is enforced, where

| Page | What it answers | CPSV Editor | Linked Data Explorer | RONL Business API |
|---|---|---|---|---|
| [Code Standards](code-standards.md) | Is it linted and formatted before it lands? | hooks · `check-format` in `audit` | hooks · `check-format` in `audit` | hooks · `check-format` in `audit` |
| [Branch Protection](branch-protection.md) | What must pass before a merge can land? | `acc` and `main` | `acc` and `main` | `acc` and `main` |
| [Supply-Chain Pinning](supply-chain.md) | Is the pinned digest the version its comment claims? | required on `acc` and `main` | required on `acc` and `main` | required on `acc` and `main` |
| [Dependency Scanning](dependency-scanning.md) | Is a known-vulnerable package or pattern shipping? | required on `acc` and `main` | required on `acc` and `main` | required on `acc` and `main` |
| [Coverage Floor](coverage-floor.md) | Is every *file* tested, not just the package average? | enforced natively | enforced natively | enforced natively |
| [Build Provenance](build-provenance.md) | Which build is this environment serving? | in place | in place — frontend and backend | in place |
| [The GitLab Mirror](the-gitlab-mirror.md) | Does the second copy still match the one the gates run on? | at each release | at each release | at each release |

Read *required* strictly: it means the check is named in a branch ruleset, so the merge
button stays disabled until it reports green. A control that is merely *in place* or *runs*
does real work and blocks nothing by itself.

The deck numbers five of these rows as its controls — build provenance 01, action pin truth
02, the scan 03, the coverage floor 04 and the mirror check 05. The other two rows are not
controls in that sense: **Code Standards** is what a change is held to before any of them
run, and **Branch Protection** is what turns the rest from checks into gates.

## What the rulesets actually require

| | `acc` | `main` |
|---|---|---|
| **CPSV Editor** | pull request · `audit` · `scan` · `Build and deploy ACC` · no deletion · no force-push | pull request · `audit` · `scan` · no deletion · no force-push |
| **Linked Data Explorer** | pull request · `audit` · `scan` · `deploy` · `Build and Deploy Frontend` · `Build and Deploy ROPA Site` · no deletion · no force-push | pull request · `audit` · `scan` · no deletion · no force-push |
| **RONL Business API** | pull request · `audit` · `scan` · `build` · `Build and Deploy ACC Frontend` · `Build and Deploy ACC PA Demo` · `Build and Deploy ACC Public Site` · no deletion · no force-push | pull request · `audit` · `scan` · no deletion · no force-push |

Read from the API on 4 October 2026 with `gh api repos/<owner>/<repo>/rules/branches/<branch>`,
which reports the effective rules from every ruleset at once. Three things this table does
not say, and all three matter:

- **The test suites are in it now, on `acc`.** Each build and deploy check runs `npm ci`,
  the linter, the type check where one exists and the unit suites before it builds, so
  requiring the check requires everything in front of it. That changed on 19 September
  2026; until then no ruleset named them and a red suite stopped the deploy without
  blocking the merge. See
  [Coverage Floor — a floor only gates where the tests run before the merge](coverage-floor.md#a-floor-only-gates-where-the-tests-run-before-the-merge).
- **`main` did not move with `acc`.** Every repository requires strictly more on `acc`
  than on `main`, and a promotion pull request is held to less than the pull requests it
  carries. Read the table rather than assuming the two branches match.
- **`audit` is one check running several things.** zizmor itself, the `renovate.json`
  validator, lockfile-against-`package.json` agreement (since 25 September 2026),
  formatting, pin truth, the register and — in the RONL Business API — the
  declarations-only check on `@ronl/shared` all report through it. One red cross can mean
  any of them.

## Where each differs, and why

Two deliberate differences, each decided rather than drifted into:

- **No `main` requires a build check, in any of the three**, and in none would one report
  on every promotion. The CPSV Editor's production workflow keeps `paths-ignore` on its
  `pull_request` trigger; the Linked Data Explorer's two production site workflows keep a
  path-filtered `pull_request` preview trigger, and its backend has none; the RONL Business
  API's four have no `pull_request` trigger at all. Since 23 September 2026 in the RONL
  Business API and 26 September in the Linked Data Explorer, production deploys only
  through `promote-to-production.yml` on a push to `main`, which calls the production
  workflows and decides which to run in a script. A required check that never reports
  wedges a pull request forever — see
  [how a path-filtered workflow became requireable](branch-protection.md#how-a-path-filtered-workflow-became-requireable)
  for the mechanism that solved this on `acc` and was deliberately not applied to `main`.
  Until 30 September 2026 the CPSV Editor's `main` carried no required checks at all, on
  the same reasoning ([#131](https://github.com/sgort/ttl-editor/issues/131)). Since then
  it requires `audit` and `scan`, whose workflows run on every pull request with no path
  filter; the reasoning held for the deploy check and not for those two.
- **`require_extra_approval_for_unattributed_changes` is `true` on `acc` and `false` on
  `main`** in all three. A promotion carries commits under
  several author identities against a ruleset requiring zero approvals, so the flag would
  demand an approval nobody can give. Preserved rather than harmonised.

And one risk that came with the promotion workflow:

- **A broken promotion workflow deploys nothing, and says so nowhere.** In the two
  repositories that promote, the production deploy workflows no longer trigger on a push to
  `main`; `promote-to-production.yml` calls them, and it is not a required check. The
  source names the consequence itself: *"If THIS workflow breaks, nothing deploys —
  silently."* The escape hatch is `workflow_dispatch` on each deploy workflow — all four in
  the RONL Business API, and the backend in the Linked Data Explorer.

## The fourth and fifth components

The **Norm Editor** runs GitLab CI with its own hook directory and none of the controls
above; see
[Code Standards](code-standards.md#the-norm-editor-is-shaped-differently). The **CPRMV API**
is likewise outside this set. **This documentation repository** has a deliberately deferred
gap of its own: version floors with `>=` and no lockfile, recorded in
[Supply-Chain Pinning](supply-chain.md#what-this-does-not-protect).

## Measured against ICTU's guideline

ICTU's eleven recommendations for dependency management ask more than the controls above
deliver, and an assessment on 13 September 2026 says where. The scores live on
[ICTU Dependency Guideline](ictu-dependency-guideline.md); this is where each recommendation
is addressed, and what the controls do not yet reach:

| Recommendations | Addressed on | Not yet reached |
|---|---|---|
| R1, R11 — vet before adding; re-check maintenance quarterly | nowhere yet | a written criterion and a scheduled review, in all three — [linked-data-explorer#250](https://github.com/sgort/linked-data-explorer/issues/250) |
| R2–R4 — no floating tags, exact pins, hash pins and `npm ci` | [Supply-Chain Pinning](supply-chain.md#what-this-does-not-protect) | the RONL Business API's VM container images (`deployment/vm/`: the two Keycloak compose files, acceptance and production, still carry Keycloak and Postgres without a digest; Skosmos is digest-pinned, on `:latest` — [#196](https://github.com/sgort/ronl-business-api/issues/196)), and its break-glass deploy scripts, which still install without the lockfile. The App Service runtime is decided rather than open — the platform pins a major and nothing finer — and the RONL Business API's backend has deployed from the lockfile in CI since 20 September 2026. The runner image and **the build that ships** were on this list until 19 September 2026 |
| R5 — internal registry, verified origin | nowhere yet | an ICTU infrastructure question before a repository one — [linked-data-explorer#249](https://github.com/sgort/linked-data-explorer/issues/249) |
| R6 — a cooldown of at least 7 days | [Supply-Chain Pinning](supply-chain.md#the-cooldown-stops-at-the-manifest) | the cooldown now exists at the package-manager level too, but `npm ci` ignores it by design and npm older than 11.10 ignores it silently — which leaves the RONL Business API, whose `.nvmrc` names Node 22.23.2 and so npm 10.9.8, uncovered on its own toolchain |
| R7, R8 — assess majors; update on a schedule | [Dependency Scanning](dependency-scanning.md#renovate-maintains-dependencies-not-the-tree) | the first-patch rule exists since 25 September 2026 but covers npm alone — action, runner, Node and Docker majors wait on Dependency Dashboard approval, which, on the stricter reading of R7, leaves no written assessment |
| R9 — reviewed MR, whole pipeline green, no automerge | [Branch Protection](branch-protection.md#what-the-rulesets-still-do-not-require) | met on `acc` since 19 September 2026; no `main` requires a build or a test, and nothing reviews a lockfile diff — [linked-data-explorer#248](https://github.com/sgort/linked-data-explorer/issues/248) |
| R10 — daily audit, including released versions | [Dependency Scanning](dependency-scanning.md#what-nothing-watches-between-merges) | a daily audit of `acc` and `main` and a committed SBOM per release exist in all three since 24 and 26 September 2026, and the audit has caught real advisories in the Linked Data Explorer ([#240](https://github.com/sgort/linked-data-explorer/issues/240)) and the RONL Business API ([#303](https://github.com/sgort/ronl-business-api/issues/303)); still open are the alerts neither fixed nor dismissed with a reason, in the Linked Data Explorer and the RONL Business API, the audit passing moderates and development-only advisories, and nothing re-analysing a stored SBOM |

The finding the assessment ranked first has since been closed. In the CPSV Editor and the
Linked Data Explorer's frontend, **the build that passed the tests was not the build that
shipped** — a vendor container re-resolved the tree on a Node version neither repository
chose. Since 19 September 2026 all three build on the runner and upload the result with
`skip_app_build: true`, so the verified install is the one that produces the deployed
bytes. See [Supply-Chain Pinning](supply-chain.md#what-this-does-not-protect) for what
that leaves open, and
[ICTU Dependency Guideline](ictu-dependency-guideline.md#the-finding-that-was-ranked-first-and-how-it-closed)
for the scores and for what each of the five deployables ships with now. The work was tracked in
[linked-data-explorer#119](https://github.com/sgort/linked-data-explorer/issues/119), closed on
3 October 2026; what it left open continues in #248–#250, named in the table above.

## One page owns each number

Each page in the table above is the **only** place its figures live — the pin counts on
Supply-Chain Pinning, the percentages on the Coverage Floor, the findings on Dependency
Scanning, the run numbers on Build Provenance, the drift on The GitLab Mirror, and the scores
against ICTU's guideline on ICTU Dependency Guideline. This page
carries enforcement states and no counts at all, so a figure that moves is corrected once
rather than in two places that then disagree.

The [CI Posture Deck](ci-posture-deck.md) is the executive-length version of the same five
controls, and the decision they lead to.
