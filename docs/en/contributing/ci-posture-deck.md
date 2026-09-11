---
scope: cross-cutting
verified:
  date: 2026-09-09
  against:
    CPSV Editor: "bbda389"
    Linked Data Explorer: "007b350"
    RONL Business API: "04e38c8"
---

# CI Posture Across Repos — Slide Deck

A five-slide executive brief, *CPSV-Editor & Linked Data Explorer — Software Delivery
Decision*, exported on **9 September 2026**. It asks for one thing: approval to start an
**initial clean** on both applications and to stand up a standard delivery pipeline behind
them, while today's `acc`-and-`main` track stays in service for rapid prototyping.

The deck is the executive-length version of what three pages here document mechanism by
mechanism — [Build Provenance](build-provenance.md),
[Supply-Chain Pinning](supply-chain.md) and the [Coverage Floor](coverage-floor.md). Those
pages say *how each control works and where it does not yet hold*. The deck says **what the
controls add up to, and what they still do not cover**, which is a different question and the
one a decision needs answered.

!!! abstract "Download"
    [CI Posture Across Repos — deck (PDF, 82 KB)](../../assets/downloads/ci-posture-across-repos-deck.pdf)

    Slides are English. Status in the deck was verified against the **`main`** branch of
    `ttl-editor` and `linked-data-explorer`, with `acc` and `main` in sync on both.

---

## Two tracks, one of which does not exist yet

<figure markdown style="width:100%; margin:0;">
  ![Slide 1 of 5: a wide navy band across the top labelled RAPID PROTOTYPING — fast, iterative experimentation with real CI, accept on acc, promote to main, every merge gated by GitHub Actions workflows, all three controls already run here. Below it, a lighter band labelled STANDARD SOFTWARE DELIVERY — PRODUCTION-READY DEPLOYMENT with an orange TO BE BUILT tag, containing three boxes left to right: Wasstraat, a quality gate before the pipeline; CI/CD Pipeline with Build, Test and Deploy in sequence; and Production-Ready, deployment of both applications. Four vertical arrows connect the two bands: Initial clean — the decision, both applications are rinsed and become the first releases through the standard pipeline; Every 6 months, functionality proven on acc and main is merged into the delivery pipeline; After 2 weeks or one sprint, the deployed release becomes the new rapid-prototyping baseline](../../assets/slides/ci-posture/slide-1-two-tracks.png)
  <figcaption>Everything ships on the prototyping track today; the delivery track below it is the thing being asked for</figcaption>
</figure>

The framing worth carrying away is that **the prototyping track is not ungoverned**. Every
merge to `acc` or `main` is gated by GitHub Actions, and all three controls run there. What is
missing is not CI — it is a release path that stops moving while a release is being made.

---

## What GitHub Actions already gates

<figure markdown style="width:100%; margin:0;">
  ![Slide 2 of 5, titled Three controls, gated in CI — with no standard software delivery aligned yet. Three cards: 01 Build provenance, "Which build am I looking at?" — every environment states the exact source and build it is serving, a hand-written version number never could; 02 Supply-chain verification, "Is the pin telling the truth?" — standard tooling only checks that a dependency is pinned to a fingerprint, we now re-resolve that fingerprint against source, a wrong or hostile one used to pass every review; 03 Test-coverage floor, "Is this code actually tested?" — 80% of decision paths tested in every file, so a well-tested utility can no longer pay for an untested screen. Below, two panels: IN PLACE — CI gating, GitHub Actions workflows block any merge, acc or main, when a control fails; and MISSING — delivery pipeline, both branches stay inside prototyping, no pipeline, no production-ready deployment beyond them. A table at the bottom answers Yes for both CPSV Editor and Linked Data Explorer on three rows: all three controls in place and blocking, tests run before a merge, formatting checked in CI](../../assets/slides/ci-posture/slide-2-what-ci-gates.png)
  <figcaption>The three controls as questions, and the Yes/Yes table behind them</figcaption>
</figure>

Each control has a page here, and the page is the place to go when the answer needs to be more
precise than *Yes*:

| Deck control | The question it answers | Documented in |
|---|---|---|
| 01 — Build provenance | Which build is this environment serving? | [Build Provenance](build-provenance.md) |
| 02 — Supply-chain verification | Is the pinned digest the version its comment claims? | [Supply-Chain Pinning](supply-chain.md) |
| 03 — Test-coverage floor | Is every *file* tested, not just the package average? | [Coverage Floor](coverage-floor.md) |

!!! warning "The Yes/Yes table is scoped to two applications, and that scoping matters"
    The deck covers the **CPSV Editor** and the **Linked Data Explorer**, which is where the
    decision applies. Across the wider set the same rows are not all green:

    - **RONL Business API's `check-supply-chain` is non-blocking**, deliberately and for a
      stated reason — see [Supply-Chain Pinning](supply-chain.md#the-habit-the-register-depends-on).
    - **Its backend workflow triggers on `push` alone**, so its branch floor gates nothing on
      a pull request. The Linked Data Explorer closed exactly that gap in v2026.09.2.
    - **The Norm Editor is shaped differently** again — GitLab CI, its own hook directory, and
      none of these three controls. See
      [Code Standards](code-standards.md#the-norm-editor-is-shaped-differently).

    Reading the table as *"all applications, all green"* is the one misreading this page
    exists to prevent.

---

## Five items, all closed

<figure markdown style="width:100%; margin:0;">
  ![Slide 3 of 5, titled Five items, all closed: every item raised in the CI posture review is closed in both repositories, and acc and main are in sync — nothing on the prototyping track is holding this decision up. A highlighted box reads "The prototyping track is finished work, not work in progress; the remaining gap is the graded release path above it — the thing you are asked to approve." Five ticked rows on the right: Last coverage exemption cleared (CPSV, issue 103) — the last legacy file below the 80% floor is covered, so the bespoke script is retired in favour of standard tooling; Pin register kept in step with the bumps (both) — automated dependency bumps now update the pins and the register that records them on the same branch, a mechanism not a habit; Zero margin on the coverage floor (Explorer) — files at or just above the 80% line have been given headroom, so an unrelated change no longer turns CI red; Formatting checked on the shared branch (CPSV) — now checked in CI in both repositories, not only by a hook on a developer's machine; Production build ids confirmed once (both) — each branch's build reports the exact commit it was made from](../../assets/slides/ci-posture/slide-3-what-was-delivered.png)
  <figcaption>A delivery report rather than a backlog — the five review items, and where each landed</figcaption>
</figure>

All five are recorded here in their own right:

| Deck item | Where it is documented |
|---|---|
| Last coverage exemption cleared | [Coverage Floor — why one repository needed a script first](coverage-floor.md#why-one-repository-needed-a-script-first) |
| Pin register kept in step with the bumps | [Supply-Chain Pinning — the habit the register depends on](supply-chain.md#the-habit-the-register-depends-on) |
| Zero margin on the coverage floor | [Coverage Floor — raising coverage without writing hollow tests](coverage-floor.md#raising-coverage-without-writing-hollow-tests) |
| Formatting checked on the shared branch | [Code Standards](code-standards.md) |
| Production build ids confirmed once | [Build Provenance](build-provenance.md) |

---

## The ask

<figure markdown style="width:100%; margin:0;">
  ![Slide 4 of 5, headed ASK — Start the initial clean: rinse the CPSV-Editor and the Linked Data Explorer, and stand up the standard delivery pipeline behind them — a Wasstraat quality gate, then build, test and deploy to a production-ready release; today's acc-and-main track stays in service for rapid prototyping. Three columns. What it buys: a delivery path separate from experimentation so a release stops moving every time someone tries something; the three controls become gates on a deployment, not only on a merge between prototyping branches; a quality gate, the Wasstraat, that nothing reaches users without passing. What it costs: building the delivery pipeline and the Wasstraat gate, a one-off engineering investment; one clean-up pass on each application before it can be the first pipeline release; prototype work then reaches a deployment on a six-month merge, not the day it is written. What it delivers: production-ready, graded applications deployed through a pipeline rather than promoted between prototyping branches; the three CI controls stop being the last word and become the entry condition for a release; rapid prototyping keeps its speed on acc and main](../../assets/slides/ci-posture/slide-4-the-decision.png)
  <figcaption>What it buys, what it costs, what it delivers — the cost column is the honest one</figcaption>
</figure>

The trade the middle column names is the substance of the decision: **prototype work would
reach a deployment on a six-month merge rather than the day it is written.** Speed on the
prototyping track is preserved precisely by not letting that track be the thing that ships.

---

## What changed between deck versions

<figure markdown style="width:100%; margin:0;">
  ![Slide 5 of 5, titled What changed in this version — six corrections, so nothing in the earlier framing is carried forward silently. A three-column table of topic, first version and updated version: Branch model, acc and main split across the two tracks, now acc and main are both rapid prototyping, accept on acc and promote to main; Prototyping track, framed as running with no pipeline behind it, now framed accurately as real CI/CD with every merge gated by GitHub Actions; What is missing, a CI/CD pipeline of any kind, now the standard delivery pipeline beyond prototyping ending in a production-ready deployment; Open items, five items three closed, now five items all closed, a delivery report rather than a backlog; Slide 4 third column, "If we do nothing", now "What it delivers" — graded applications without losing prototyping speed; Status verification, acceptance-branch commit per repository, now the main branch of both repositories with acc and main in sync](../../assets/slides/ci-posture/slide-5-changelog.png)
  <figcaption>The deck carries its own corrections rather than quietly replacing the earlier framing</figcaption>
</figure>

The two corrections worth noticing are the same class of error this documentation keeps
finding in itself. The first version said the prototyping track ran *"with no pipeline behind
it"* and that a CI/CD pipeline of any kind was missing. Both were **false and easy to believe**
— the applications deploy from `acc` and `main` through GitHub Actions, with three blocking
controls, and had done so for weeks. What is genuinely missing is narrower and harder to
state: a release path *above* prototyping.

Overstating a gap is not a safe error. It invites building something that already exists, and
it makes the real gap look like a detail.

---

## Verified against the repositories, on the day of export

The deck's status claims were re-checked here rather than taken on trust:

- **`acc` and `main` in sync on both applications** — `ttl-editor` at `bbda389`,
  `linked-data-explorer` at `007b350`, each carrying v2026.09.2.
- **Three controls blocking in both** — no `continue-on-error` key appears in either
  repository's audit job; both carry per-file branch thresholds in their runner configs.
- **Production has now run in both** — the CPSV Editor's *Deploy PROD* workflow at `bbda389`
  (run 88) and the Linked Data Explorer's at `007b350` (run 39), so the build id each serves
  is derivable as `build bbda389 · #88` and `build 007b350 · #39`. RONL Business API's
  production workflow last ran in July, before the feature existed, so it remains wired and
  unexercised.

---

## Related pages

- [Build Provenance](build-provenance.md) — control 01, in full
- [Supply-Chain Pinning](supply-chain.md) — control 02, in full
- [Coverage Floor](coverage-floor.md) — control 03, in full
- [Code Standards](code-standards.md) — formatting, hooks, and where the Norm Editor differs
- [Development Workflow](development-workflow/overview.md) — how a change reaches `acc` today
