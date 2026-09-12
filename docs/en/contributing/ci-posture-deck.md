---
scope: cross-cutting
verified:
  date: 2026-09-12
  against:
    CPSV Editor: "f5bae6a"
    Linked Data Explorer: "be6bc54"
    RONL Business API: "311d732"
---

# CI Posture Across Repos — Slide Deck

A five-slide executive brief, *CPSV-Editor & Linked Data Explorer — Software Delivery
Decision*, in the version re-exported on **12 September 2026**. It asks for one thing:
approval to start an **initial clean** on both applications and to stand up a standard
delivery pipeline behind them, while today's `acc`-and-`main` track stays in service for
rapid prototyping.

The deck is the executive-length version of what the [control pages](controls.md) document
mechanism by mechanism. Those pages say *how each control works and where it does not yet
hold*. The deck says **what the controls add up to, and what they still do not cover**,
which is a different question and the one a decision needs answered.

!!! abstract "Download"
    [CI Posture Across Repos — deck (PDF, 138 KB)](../../assets/downloads/ci-posture-across-repos-deck.pdf)

    Slides are English. The deck states it was re-verified on 12 September 2026 with rulesets
    read from the API, thresholds from the config that declares them and mirror state from
    `ls-remote` against both remotes. This page re-checked those claims independently — see
    [Verified against the repositories](#verified-against-the-repositories).

!!! note "This export counts five controls, where the last one counted four"
    A release-time **mirror check** joins the four CI controls. It is not a CI gate and
    cannot be: the `gitlab` remote lives in `.git/config` and no tracked file names the
    host, so a runner has no such remote and no route to it. It runs where the push happens,
    at each release, and it never pushes — it prints the command and stops. The deck carries
    the change as one of seven corrections on its closing slide rather than renumbering
    silently.

---

## Two tracks, one of which does not exist yet

<figure markdown style="width:100%; margin:0;">
  ![Slide 1 of 5, titled CPSV-Editor & Linked Data Explorer, subtitle both apps run on the rapid-prototyping track — acc and main, checked by GitHub Actions; standard delivery pipeline does not exist yet. A wide navy band labelled RAPID PROTOTYPING reads: fast, iterative experimentation with real CI, accept on acc, promote to main, every merge checked by GitHub Actions workflows; five controls run here — four in CI, and a fifth at each release. Below it a lighter band labelled STANDARD SOFTWARE DELIVERY — PRODUCTION-READY DEPLOYMENT with an orange TO BE BUILT tag, holding three boxes left to right: Wasstraat, a quality gate before the pipeline; CI/CD Pipeline with Build, Test and Deploy in sequence; and Production-Ready, deployment of both applications. Vertical arrows connect the bands: Initial clean — the decision, both applications are rinsed and become the first releases through the standard pipeline; Every 6 months, functionality proven on acc and main is merged into the delivery pipeline; After 2 weeks or one sprint, the deployed release becomes the new rapid-prototyping baseline](../../assets/slides/ci-posture/slide-1-two-tracks.png)
  <figcaption>Everything ships on the prototyping track today; the delivery track below it is the thing being asked for</figcaption>
</figure>

The framing worth carrying away is that **the prototyping track is not ungoverned**. Four of
the five controls run there on every pull request, and the fifth runs at every release. What
is missing is not CI — it is a release path that stops moving while a release is being made.

---

## What GitHub Actions already gates

<figure markdown style="width:100%; margin:0;">
  ![Slide 2 of 5, titled Five controls in force — with no standard software delivery aligned yet. Four cards across the top: 01 Build provenance, "Which build am I looking at?" — every environment states the exact source and build it is serving, a hand-written version number never could, confirmed by eye in production in both; 02 Action pin truth, "Is the pin telling the truth?" — standard tooling only checks that a build step is pinned to a fingerprint, and the pin is re-resolved against source because a wrong or hostile pin passes every review; 03 Code and dependency scan, "Is anything known-vulnerable shipping?" — the other half of the supply chain, the package tree and our own code, scanned on every merge, with the CPSV Editor at zero findings and the Explorer at four; 04 Test-coverage floor, "Is this code actually tested?" — 80% of decision paths tested in every file, so a well-tested utility can no longer pay for an untested screen, standard tooling in both and no exemptions left. Below them three panels: IN PLACE — CI GATING, the audit and the scan are required checks on acc in both and on main in the Explorer, and the test suites stop the deploy when they fail; 05 — MIRROR CHECK, NOT A CI GATE, both apps are mirrored to a second host no runner can reach, checked at every release instead, the one control that cannot run in CI; and MISSING — DELIVERY PIPELINE, both branches stay inside prototyping with no production-ready deployment beyond them. A table headed GATED IN CI TODAY compares the CPSV Editor and the Linked Data Explorer: all five controls in place, Yes and Yes; required checks on acc, audit and scan in both; required checks on main, None — decided, issue 131, for the Editor and audit and scan for the Explorer; tests run before a merge, Yes and Yes; formatting checked in CI, Yes and Yes; production build id confirmed by eye, Yes — 9 Sep in both; scan findings at the last run, 0 for the Editor and 4, one real and tracked, for the Explorer; mirror in sync at the last check, Yes on both branches in both](../../assets/slides/ci-posture/slide-2-what-ci-gates.png)
  <figcaption>The five controls as questions, and exactly where each repository requires them</figcaption>
</figure>

Each control has a page here, and the page is where to go when the answer needs to be more
precise than *Yes*:

| Deck control | The question it answers | Documented in |
|---|---|---|
| 01 — Build provenance | Which build is this environment serving? | [Build Provenance](build-provenance.md) |
| 02 — Action pin truth | Is the pinned digest the version its comment claims? | [Supply-Chain Pinning — `check-supply-chain`](supply-chain.md#6-check-supply-chain-the-preflight-zizmor-cannot-be) |
| 03 — Code and dependency scan | Is a known-vulnerable package or pattern shipping? | [Supply-Chain Pinning — the npm tree](supply-chain.md#7-the-other-supply-chain-the-npm-tree) |
| 04 — Test-coverage floor | Is every *file* tested, not just the package average? | [Coverage Floor](coverage-floor.md) |
| 05 — Mirror check | Does the second copy still match the one the gates run on? | [Supply-Chain Pinning — the GitLab mirror](supply-chain.md#the-gitlab-mirror) |

The [controls index](controls.md) carries the same five rows across all three applications.

!!! warning "The Yes/Yes table is scoped to two applications, and that scoping matters"
    The deck covers the **CPSV Editor** and the **Linked Data Explorer**, which is where the
    decision applies. Two qualifications belong with it:

    - **The RONL Business API now runs the same five controls**, as of 12 September 2026,
      and the deck says so on its closing slide while keeping it out of scope for the
      decision. It differs in one respect worth knowing: its `scan` **runs on every pull
      request and is deliberately not a required check** while its first scan's 435 findings
      are triaged, so `audit` is the only required check on either of its branches. See the
      [controls index](controls.md).
    - **The Norm Editor is shaped differently** again — GitLab CI, its own hook directory,
      and none of these controls. See
      [Code Standards](code-standards.md#the-norm-editor-is-shaped-differently).

    Reading the table as *"all applications, all green"* is the one misreading this page
    exists to prevent.

---

## Eight items, all closed

<figure markdown style="width:100%; margin:0;">
  ![Slide 3 of 5, titled Eight items, all closed: every item raised in the CI posture review is closed in both repositories, acc and main are in sync, and two further controls landed in the same period; nothing on the prototyping track is holding this decision up. A highlighted box reads "The prototyping track is finished work, not work in progress — the remaining gap is the graded release path above it, the thing you are asked to approve." Eight ticked rows, each tagged with the repository it belongs to: Last coverage exemption cleared, CPSV, issue 103 — the largest file went from 45.7% to 98.3% branch coverage, the last exemption went with it and the bespoke script is retired; Pin register kept in step with the bumps, both — bumps now update the pins and the register recording them on the same branch, a mechanism rather than a habit; Zero margin on the coverage floor, Explorer — twelve files raised without touching production code, package average 92.9%, one file remains under 85%; Formatting checked on the shared branch, CPSV — checked in CI rather than only by a hook on a developer's machine; Production build ids confirmed once, both — read off the running application, because the failure mode is a successful-looking deploy of the wrong thing; Code and dependency scanning made blocking, both, new — required on acc in both and on main in the Explorer, which went from 76 findings to 4 in a day; The dependency tree itself now refreshed, both, new — the bot only updated what we name directly while everything underneath sat still, and the Editor's last seven findings went to zero on the first refresh; The second copy is checked at each release, both, new — a release-time check now distinguishes behind from diverged, the first being one command and the second surgery](../../assets/slides/ci-posture/slide-3-what-was-delivered.png)
  <figcaption>A delivery report rather than a backlog — the eight items, and where each landed</figcaption>
</figure>

All eight are recorded here in their own right:

| Deck item | Where it is documented |
|---|---|
| Last coverage exemption cleared | [Coverage Floor — why one repository needed a script first](coverage-floor.md#why-one-repository-needed-a-script-first) |
| Pin register kept in step with the bumps | [Supply-Chain Pinning — the habit the register depends on](supply-chain.md#the-habit-the-register-depends-on) |
| Zero margin on the coverage floor | [Coverage Floor — raising coverage without writing hollow tests](coverage-floor.md#raising-coverage-without-writing-hollow-tests) |
| Formatting checked on the shared branch | [Code Standards](code-standards.md) |
| Production build ids confirmed once | [Build Provenance](build-provenance.md) |
| Code and dependency scanning made blocking | [Supply-Chain Pinning — the npm tree](supply-chain.md#7-the-other-supply-chain-the-npm-tree) |
| The dependency tree itself now refreshed | [Supply-Chain Pinning — Renovate maintains dependencies, not the tree](supply-chain.md#renovate-maintains-dependencies-not-the-tree) |
| The second copy is checked at each release | [Supply-Chain Pinning — the GitLab mirror](supply-chain.md#the-gitlab-mirror) |

The last two are the ones that were not on the original review list: the dependency refresh
and the mirror check both came out of the work the review triggered, which is the usual
shape of an honest delivery report.

---

## The ask

<figure markdown style="width:100%; margin:0;">
  ![Slide 4 of 5, headed ASK — Start the initial clean: rinse the CPSV-Editor and the Linked Data Explorer, and stand up the standard delivery pipeline behind them — a Wasstraat quality gate, then build, test and deploy to a production-ready release; today's acc-and-main track, with its five controls, stays in service for rapid prototyping. Three columns. What it buys: a delivery path separate from experimentation, so a release stops moving every time someone tries something; the five controls become gates on a deployment, not only on a merge between prototyping branches; a quality gate, the Wasstraat, that nothing reaches users without passing. What it costs: building the delivery pipeline and the Wasstraat gate, a one-off engineering investment; one clean-up pass on each application before it can be the first pipeline release; prototype work then reaches a deployment on a six-month merge, not the day it is written. What it delivers: production-ready, graded applications deployed through a pipeline rather than promoted between prototyping branches; the five controls stop being the last word and become the entry condition for a release; rapid prototyping keeps its speed on acc and main, staying the track where things are tried rather than the track that ships. A footnote reads: re-verified 12 September 2026 — main at f5bae6a and be6bc54 for v2026.09.4, acc at f7fe80f and daa4816; rulesets read from the API, thresholds from the config that declares them, mirror state from both remotes — not written from memory](../../assets/slides/ci-posture/slide-4-the-decision.png)
  <figcaption>What it buys, what it costs, what it delivers — the cost column is the honest one</figcaption>
</figure>

The trade the middle column names is the substance of the decision: **prototype work would
reach a deployment on a six-month merge rather than the day it is written.** Speed on the
prototyping track is preserved precisely by not letting that track be the thing that ships.

The middle row of *What it buys* reads more sharply next to slide 2's table: **the five
controls becoming gates on a deployment** is precisely what the CPSV Editor's `main` does
not have today, by decision — and the delivery pipeline is where that decision would be
revisited.

---

## What changed between deck versions

<figure markdown style="width:100%; margin:0;">
  ![Slide 5 of 5, titled What changed in this version — seven changes since the last version, so nothing in the earlier framing is carried forward silently. A three-column table of topic, previous version and this version: Number of controls, from four — build provenance, pin truth, scanning, coverage floor — to five, plus a release-time mirror check, the one control that cannot run in CI at all; Delivered items, from six all closed to eight all closed, lock-file maintenance and the mirror check joining them; Scan findings, from the Explorer 76 down to 4 with the Editor's last seven put down to needing an upstream release, to that was wrong — nothing had ever refreshed the transitive tree, and enabling it took the Editor to zero; The mirror, from not mentioned, outside every gate and unwatched, to checked at each release in both and in sync on both branches as of 12 September; Where the controls are required, from "acc or main" in both to acc in both and main in the Explorer only, the CPSV Editor's main ungated by decision, issue 131; Status verification, from the main branch of both with no commits named, to re-verified 12 September 2026 with main at f5bae6a and be6bc54 and acc at f7fe80f and daa4816; Scope, from two applications to still two — a third, the RONL Business API, now runs the same five controls but is out of scope here](../../assets/slides/ci-posture/slide-5-changelog.png)
  <figcaption>The deck carries its own corrections rather than quietly replacing the earlier framing</figcaption>
</figure>

Two rows are worth reading closely, because both are cases of a claim being *revised
downward in confidence* rather than upward in scope.

**Scan findings.** The previous version reported the CPSV Editor's last seven findings as
waiting on an upstream release. That was wrong, and the deck says so in those words: nothing
had ever refreshed the transitive tree, because Renovate maintains declared dependencies and
not what they resolve to. One refresh took the scan to zero. The earlier explanation was
plausible, was believed, and would have justified doing nothing indefinitely.

**The mirror.** The previous version did not mention it. The narrower true statement is that
the release check closes *the observation half* of the problem, not the drift: the mirror is
still pushed by hand, it still falls behind on every merge, and what changed is that a
release now notices.

---

## Verified against the repositories

The deck's status claims were re-checked on **12 September 2026** rather than taken on trust:

- **The rulesets were read from the API**, per branch, with
  `gh api repos/<owner>/<repo>/rules/branches/<branch>`, which reports the effective rules
  from every ruleset at once rather than one ruleset in isolation:

    | | `acc` | `main` |
    |---|---|---|
    | CPSV Editor | pull request, `audit` + `scan` | no ruleset rules — a pull request only, by decision ([#131](https://github.com/sgort/ttl-editor/issues/131)) |
    | Linked Data Explorer | pull request, `audit` + `scan`, deletion, non-fast-forward | the same four |
    | RONL Business API | pull request, `audit`, deletion, non-fast-forward | the same four |

- **The pin counts were re-derived** by counting `uses:` references on each `acc` head rather
  than read from a register: the CPSV Editor 12 of 12 across four workflows, the Linked Data
  Explorer 24 of 24 across eight, the RONL Business API 31 of 31 across ten. All are fully
  digest-pinned.
- **`acc` and `main` carry the same code in both applications the deck covers.** The deck's
  footnote says exactly that, and the promotion commits it names — `f5bae6a` and `be6bc54` —
  are the ones this page is stamped against.
- **Production has run in both**: the CPSV Editor's *Deploy PROD* at `f5bae6a` as run 94, the
  Linked Data Explorer's *Deploy Frontend to Production* at `be6bc54` as run 44. The deck's
  *"confirmed by eye — 9 Sep"* refers to the first builds, `#88` and `#39`.

One claim on slide 2 is **not** verifiable from here and is reported as the deck states it:
the scan-findings figures, 0 and 4, are the last run's results in the Semgrep dashboard,
which this documentation cannot read.

---

## Related pages

- [Controls at a Glance](controls.md) — the five controls across all three applications
- [Build Provenance](build-provenance.md) — control 01, in full
- [Supply-Chain Pinning](supply-chain.md) — controls 02, 03 and 05, in full
- [Coverage Floor](coverage-floor.md) — control 04, in full
- [Code Standards](code-standards.md) — formatting, hooks, and where the Norm Editor differs
- [Development Workflow](development-workflow/overview.md) — how a change reaches `acc` today
