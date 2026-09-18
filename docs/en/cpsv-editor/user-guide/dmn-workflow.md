---
component: CPSV Editor
---

# DMN to Linked Data Workflow

*From a legal body's DMN export to a tested decision service, published as linked data*

A DMN model delivered by the body that did the legal analysis is rarely something a
decision engine can run as it stands. This page is the route from that export to a
decision service that **executes, is tested rule by rule, and is published as
machine-readable law with its legal basis attached** — a nine-stage workflow, run three
times, for Amsterdam, SZW and Den Haag.

The CPSV Editor is where two of the stages happen: deploying and testing a model in
[the DMN tab](dmn-tab.md), and publishing it as part of a service in Turtle. The rest of
the workflow is about what to do *around* the editor, and where a person — not a
pipeline — has to decide. The page closes on
[three questions](#three-questions-for-the-standard) that neither the editor nor the
bodies that own the regulations can answer, because they belong to the standard.

!!! abstract "Download the slides"
    [DMN to Linked Data Workflow — deck (PDF, 261 KB)](../../assets/downloads/dmn-to-linked-data-workflow.pdf)

    Nine slides. The first eight are built from the workflow brief in the CPSV Editor
    repository,
    [`docs/dmn-to-linked-data-workflow.md`](https://github.com/sgort/ttl-editor/blob/main/docs/dmn-to-linked-data-workflow.md);
    the ninth closes the deck for a standardisation body, and draws its figures from
    the same passes. The headline figures were re-counted for this page from the
    example models at v2026.09.4 — decisions, rules, inputs and test cases per pass
    all agree with the slides.

---

## The result, and the two caveats that stay with it

<figure markdown style="width:100%; margin:0;">
  ![Slide 1 of 9, titled Three regulations, modelled by lawyers, turned into executable law — decision services that can be executed, tested rule by rule and published as machine-readable law, run three times for Amsterdam, SZW and Den Haag. Five figures: 3 government bodies, 34 decisions published, 179 rules with one test case each, 286 test cases against the live engine, 0 failures today. A dark panel, The problem this closes: an export that opens in a modeller is not a model a computer can execute; all three delivered exports failed to deploy or failed to answer, and every one now runs, is tested rule by rule, and is published as linked data with its legal basis attached. A second panel, Two caveats that stay attached: the 179 rules are the published models, and two of the three grew during derivation (Den Haag 44 to 55, SZW 17 to 25), so this is not a count of what legal analysis delivered; and "0 failures" means every case passes against the live engine today, not that the models are legally correct — four decisions await the responsible body, plus one flagged assumption](../../assets/slides/dmn-workflow/slide-01-legal-model-to-decision-service.png)
  <figcaption>Three bodies · 34 decisions · 179 rules · 286 test cases · 0 failures — with its caveats</figcaption>
</figure>

**All three exports that arrived failed to deploy or failed to answer.** Every one now
runs. That is the whole problem the workflow exists to close: an export that opens in a
modeller is not a model a computer can execute.

!!! warning "Do not quote the totals without the caveats"
    - **179 rules is the published count, not what legal analysis delivered.** Two of the
      three models grew during derivation — Den Haag from 44 rules to 55, SZW from 17 to
      25 — so the total counts the published models.
    - **"0 failures" means every case passes against the live engine today.** It does
      not mean the models are legally correct. Four decisions await the responsible
      body, plus one flagged assumption — see
      [What is still open](#what-is-still-open-and-who-owns-it).

---

## The nine stages

<figure markdown style="width:100%; margin:0;">
  ![Slide 2 of 9, titled Six stages execute. Three need a person. One sends you back. Nine cards in two rows, the three human stages shaded. 01 Receive — a DMN export arrives from the body that did the legal analysis, nothing is assumed about it. 02 Survey — does it deploy, does it answer, what does the validator say, does the answer look right. 03 Decide (human) — the derivation strategy, needing a domain expert; the temptation is to make it run by quietly changing what it decides. 04 Derive (human) — produce the patched model, every difference from the original listed in the changelog. 05 Deploy — push to the decision engine, which versions rather than replaces, so a deployment is additive and reversible. 06 Test — one case per rule, each routed to the decision whose rule it exercises, run live against the engine. 07 Publish — attach to a public service in the CPSV Editor, export Turtle, validate against the SHACL shapes. 08 Inspect (human) — read the published file, the stage most likely to be skipped, where four findings appeared only. 09 Record — three documents per pass: changelog, validation write-up, and a runner anyone can execute. An arrow from 08 back to 06 is labelled: what publishing reveals sends you back to the suite](../../assets/slides/dmn-workflow/slide-02-the-workflow-nine-stages.png)
  <figcaption>Six stages execute, three need a person, and stage 8 sends you back to stage 6</figcaption>
</figure>

The slide reads as one continuous path: the top row left to right, the bottom row right
to left. Of the three stages that need a person, stage 3 asks the most — a domain expert
who can say whether an answer is *right*, not only whether it runs.

| # | Stage | Who | Where |
|--:|---|---|---|
| 1 | **Receive** the export from the body that did the legal analysis | — | Nothing is assumed about it |
| 2 | **Survey** — does it deploy, does it answer, what does the validator say, does the answer look right? | — | [The DMN tab](dmn-tab.md) |
| 3 | **Decide** the derivation strategy | **A domain expert** | — |
| 4 | **Derive** the patched model, listing every difference from the original | **A person** | The pass's `CHANGELOG.md` |
| 5 | **Deploy** to the decision engine | — | [The DMN tab — deploy](dmn-tab.md#step-4-deploy-to-operaton) |
| 6 | **Test** — one case per rule, routed to the decision whose rule it exercises | — | [DMN Testing](dmn-testing.md) |
| 7 | **Publish** — attach to a public service, export Turtle, validate against SHACL | — | [Import & Export TTL](import-export-ttl.md), [Publishing to TriplyDB](publishing-to-triplydb.md) |
| 8 | **Inspect** the published file | **A person** | The exported `.ttl` |
| 9 | **Record** — changelog, validation write-up, and a runner anyone can execute | — | The pass's `testCases/` |

Two properties of the engine make stages 5 and 6 cheap to repeat. **A deployment is
additive**: the engine versions a model rather than replacing it, so deploying is
reversible. And **the loop runs backwards**: stage 8 is the most likely to be skipped,
and it is where four findings appeared that no model and no green suite could show —
each of which sent the pass back to stage 6.

---

## Three passes, side by side

<figure markdown style="width:100%; margin:0;">
  ![Slide 3 of 9, titled One workflow absorbed three very different models — every number measured from the repository, arrows reading before to after derivation. Three cards: Amsterdam, wide — 25 shallow decisions on income schemes, the problem was volume and repetition; SZW, deep — two decisions, one emitting 20 bijstandsnorm amounts and the other picking one per peildatum, a chained lookup over time; Den Haag, structural — written against an object model no decision engine can navigate, the problem was translation. A measured table for Amsterdam, SZW and Den Haag: source tool iKnow export, Camunda Modeler, Camunda over an object model; decisions 25, 2, 9 to 7; rules 99, 17 to 25, 44 to 55; declared inputs 52, 2, 2 to 26; test cases and decisions covered 100 covering 25 of 25, 121 covering 2 of 2, 65 covering 7 of 7; legal links in the source 48 sources and 99 links, none, 11 sources and 12 links; cell-level legal grounding 1 rule and 6 cells as a proof of concept, 80 cells, none available; published as Digital-Twin-Inkomensregelingen.ttl, Normenbrief---Informatie-voor-gemeenten.ttl, Aanvraag-LevensOnderhoud-ALO.ttl](../../assets/slides/dmn-workflow/slide-03-three-passes-side-by-side.png)
  <figcaption>Wide, deep and structural — the same workflow absorbed all three</figcaption>
</figure>

The three are deliberately different in shape, and the same workflow absorbed all three.
**Amsterdam** is wide — 25 shallow decisions, where the problem was volume and
repetition. **SZW** is deep — two decisions, one emitting twenty amounts and the other
picking one per reference date: a chained lookup over time. **Den Haag** is structural —
written against an object model no decision engine can navigate, so the problem was
translation, and the model had to be re-derived rather than patched.

On the slide, arrows read before to after derivation. Den Haag went from 9 decisions to
7 while its rules went from 44 to 55 — **not because the scope grew**, but because rules
the source could not reach were restored.

SZW's 80 grounded cells are the largest application in these three passes of
[cell-level legislative grounding](../developer/cell-level-grounding.md). Den Haag has no
published sources to ground against, so it has none — grounding against inferred
citations was rejected.

---

## What kept going wrong

<figure markdown style="width:100%; margin:0;">
  ![Slide 4 of 9, titled A defect catalogue that grows across the passes — Amsterdam discovered most of it, by Den Haag the same checks were run up front, and fifteen recurring defect families are now looked for before a model is even deployed. Two panels: the C-level summary, every one of these is invisible until the model is executed and several are invisible even then, which is what the test suite is for; and Not a validation tool, the validator passed all three exports as valid while none of them could run correctly, so passing validation is a weak signal, not a tick. A table of defect, effect and where found: unreachable approval rules, the model could not grant entitlement at all, Den Haag; amounts copied into the wrong cell, wrong benefit paid, SZW over two half-years; outputs no input could reach, 7 of 20 amounts unobtainable, SZW; two inputs mapped to one output, two situations answered identically, SZW; malformed conditions, silently resolving to the wrong thing, Amsterdam 56 times; output column with a label but no name, a blank unlogged error that hides behind any other defect, Amsterdam and Den Haag 6 of 9; empty input expression, an invalid model that works and fails later when something unrelated changes, SZW and Den Haag; value type contradicting its own cells, right answer wrong type no warning, SZW; object-model navigation, no decision engine can follow it, Den Haag in 3 decisions; empty placeholder rules, matching everything not caught earlier and returning nothing, Den Haag 3; wildcard default under the wrong hit policy, two rules matching where one must, Amsterdam. Plus multi-word bare names, a missing history setting, unescaped ampersands in URLs (48) and n/a used as a condition (10)](../../assets/slides/dmn-workflow/slide-04-what-kept-going-wrong.png)
  <figcaption>Fifteen defect families, now checked before a model is deployed</figcaption>
</figure>

This catalogue is the workflow's real asset. By the third pass most of these defects
were **checked for rather than discovered** — the return on running the workflow three
times, and the argument for a fourth.

**The validator passed all three exports as valid while none of them could run
correctly.** Passing validation is a weak signal, not a tick — which is why stage 2 asks
whether the model deploys and *answers*, and why stage 6 exists at all. Every one of
these defects is invisible until the model is executed, and several are invisible even
then: an output column with a label but no name fails with a blank, unlogged error, and
an empty placeholder rule quietly matches everything nothing else caught.

The defects the editor meets directly — the ones that block a deployment or an
evaluation in the DMN tab — are listed with their fixes under
[The DMN Tab — authoring pitfalls](dmn-tab.md#authoring-pitfalls).

---

## Where a person decides

<figure markdown style="width:100%; margin:0;">
  ![Slide 5 of 9, titled Eight judgements no pipeline can make for you — three stages need a human, one needs a domain expert who can say whether an answer is right. A table of decision, the real choice, and what was chosen and why: which file is the deliverable, patch the original or derive a new one — derive, so the original stays as the auditable record of what legal analysis delivered; a wrong amount, correct it or leave and report — report, corrected only once a second published source confirmed it; a missing reason code, invent one or leave the rule untestable — invent, and flag it as the only value in the model with no source; an unreachable output, extend the model or record the gap — extended where the vocabulary was mechanical (SZW), recorded where it was policy (Den Haag); a rule that matches nothing, fix the logic or record it — record, because what a mixed household is entitled to is policy, not transcription; disconnected decisions, wire them in or leave them — leave, because wiring them in would decide when a hardheidsclausule applies; unknown facts, a second boolean or a third value — a third value, so the answer can say which fact is missing; legal grounding, ground against inferred citations or don't — ground only where published sources exist (SZW), Den Haag has none so no grounding. A closing panel quotes: "We fix what is provably broken. We report what is arguably wrong." — a model that runs but decides something nobody authorised is worse than one that does not run; the pipeline reports questions to the responsible body, it does not answer them](../../assets/slides/dmn-workflow/slide-05-where-humans-decide.png)
  <figcaption>"We fix what is provably broken. We report what is arguably wrong."</figcaption>
</figure>

The nine stages drawn as boxes and arrows suggest a process that could be automated.
It cannot: these eight are the decisions actually taken across the three passes. The
rule behind all eight: **a model that runs but decides something nobody authorised
is worse than one that does not run.** The temptation at stage 3 is to make an export
run by quietly changing what it decides. The workflow resists it by deriving a new model
and keeping the original as the auditable record of what legal analysis delivered —
and by reporting questions to the responsible body rather than answering them.

What the workflow *declined* to do matters as much. Den Haag's three disconnected
decisions were not wired in, because connecting them would decide when a
hardheidsclausule applies — and that is policy, not transcription.

---

## What is still open, and who owns it

<figure markdown style="width:100%; margin:0;">
  ![Slide 6 of 9, titled Four decisions awaiting the responsible body, plus one flagged assumption — each a question for a government body about its own regulation. Four open cards: 01 SZW, which article is the basis for JO/JOK — Art. 20 lid 1 c rather than lid 2 c; both carry the lid 2 c amount in all five termijnen, the amount is confirmed by a second source but the citation is not, nor whether an 18–20-year-old with an AOW-age partner and no child gets the with-children norm. 02 Den Haag, what is the correct reden code — the source has a literal ??? for the ongeoorloofd-onbetaald-verlof rule, and "04" was adopted so it could be tested, the only value in any of the three models with no source. 03 Den Haag, what is a mixed household entitled to — one person refused and the other entitled; today the model matches no rule and returns nothing, and any answer adds a rule whose choice is policy. 04 Den Haag, should the three standalone decisions be wired in — TekortSchieten, DringendeReden, HardheidsclausuleToepassen; connecting them decides when a hardship clause applies, so they were left standalone and reported. A dark panel: all four belong to two of the three passes, Amsterdam contributes none — its 99 rules were legally coherent once the technical defects were fixed, while Den Haag's had genuine policy holes; that is a broken export versus an unfinished regulation, and only executing the model reveals which you have. A flagged assumption: Den Haag's unknown-voorliggende-voorzieningen rule reported an informatiebehoefte naming a different fact than its own column, and was changed and flagged. Three lanes, three addressees: 4 plus 1 for the regulation, to the government body; 2 for the standard, to the CPRMV spec owner — identifier stability and ruleType; 1 for the tooling, to us — the legal-source layer never reaches the file. Amsterdam adds an observation, not a question: 2 of its 99 legal links do not resolve against the annotations file](../../assets/slides/dmn-workflow/slide-06-what-is-still-open.png)
  <figcaption>Four decisions for the responsible bodies, one flagged assumption, and three lanes</figcaption>
</figure>

It is four decisions **plus** one flagged assumption, not a bare four. The fifth sits
inside a finding already marked fixed, so it blocks nothing — but it is still
unanswered. Each of the four cards is a question for a government body about its own
regulation.

Open items sit in **three lanes with different addressees**. Mixing them up sends a
question to someone who cannot answer it, and folding them into one number is what
produces overclaiming:

| Lane | Count | Addressed to |
|---|--:|---|
| The regulation | 4 + 1 | The government body — the four decisions above, plus the flagged assumption |
| The standard | 2 | The CPRMV specification owner — identifier stability and `ruleType` |
| The tooling | 1 | The CPSV Editor itself — the DMN legal-source layer never reaches the published file |

**Amsterdam contributes none of the four.** Its 99 rules were legally coherent once the
technical defects were fixed; Den Haag's had genuine policy holes — a household it could
not decide, three decisions connected to nothing. That is the difference between a
broken export and an unfinished regulation, and only executing the model tells you which
one you have.

---

## Two ideas worth keeping

<figure markdown style="width:100%; margin:0;">
  ![Slide 7 of 9, Two ideas worth a panel of their own. Idea one, "Unknown" is a third value, not a second flag: three states, rood for refused, oranje for information needed, groen for entitled. Den Haag's source model tracked, for each of six facts per person, whether it was true, false or not yet established, and when a fact was missing it said which one; an earlier attempt collapsed all six into a single "information incomplete" flag. Collapsed: "Something is missing." Restored: "We need the residence permit." Both versions run and both are correct; collapsing discarded the model's most useful answer while appearing to simplify, and restoring it turned 1 rule back into 6, per person. Idea two, Publishing is a discovery step, not the last step: none of these findings was visible from the model or a green test suite, only from the published artefact. Published outputs were silently empty whenever evaluation returned no rows, found by republishing Amsterdam; the generator overwrote a legal rule's real identifier with its own web address in 12 places in one file, found by inspecting the SZW artefact, fixed; the test runner treated a false answer as no answer, found by mutation-testing the runner, fixed; the editor reads no part of DMN's legal-source layer so 23 provenance links never reach the published file, found by inspecting the Den Haag artefact, open; an intermediate decision's output — the colour the entire model turns on — was absent from the published vocabulary, found by inspecting the Den Haag artefact after a second publish. Every test case had been routed through the top-level decision, so nothing asked the middle one directly; three editor improvements and two defects came out of the three passes](../../assets/slides/dmn-workflow/slide-07-two-ideas.png)
  <figcaption>"Unknown" is a third value — and publishing is where the last defects surface</figcaption>
</figure>

**"Unknown" is a third value, not a second flag.** Den Haag's model tracked six facts
per person as true, false or not yet established, and said which one was missing. A
model that can say *refused*, *entitled* or *information needed* — and, for the last,
*which* information — gives an applicant a next step. Collapsing the six facts into one
"information incomplete" flag still runs and is still correct; it only throws away the
model's most useful answer. Only the restored model can tell a caseworker *we need the
residence permit* — and restoring it turned 1 rule back into 6, per person.

**Publishing is a discovery step, not the last step.** Each finding in the table on the
slide surfaced only by reading the published artefact — including two defects in tooling
that had been in use for weeks. Each changed the editor or the suite:

- The generator minted a citation stub over rules the document already published, giving
  them a second, contradictory `cprmv:id` — fixed in v2026.09.3; see
  [Cell-Level Legislative Grounding](../developer/cell-level-grounding.md).
- An intermediate decision's output, the one the Den Haag model turns on, was missing
  from the published vocabulary because every test case went through the top-level
  decision — closed by cases that name the middle decision directly.
- The DMN legal-source layer is not read by the editor, so its provenance links never
  reach the published file. **That one is open**, and it is the tooling lane above.

---

## Why the testing is evidence

<figure markdown style="width:100%; margin:0;">
  ![Slide 8 of 9, titled A green run is evidence, not reassurance — four practices, in increasing order of how much they surprise people. 01 Coverage, one case per rule — not per feature or happy path; 100, 121 and 65 cases for 99, 25 and 55 rules. 02 Independence, the suite does not trust the model — each generator holds its own copy of the expected answers and emits nothing if that copy disagrees; a suite generated from the thing under test proves nothing. 03 Self-check, the runner is tested too — deliberately broken expectations confirm each is reported as a failure, which found a real defect in the comparison logic. 04 Both paths, two verdict paths both exercised — the command-line runner and the editor's own pass/fail logic read the expectations differently, so both run against the live engine. What comes out, per pass: the original DMN untouched, the patched DMN that actually runs, the published TTL as the linked-data service, CHANGELOG.md with what changed, when and why, and testCases/ with the suite, the reasoning and a runner anyone can execute — and live, a deployed, versioned decision on the engine callable over HTTP with a documented request body. A task panel, Run it a fourth time: Amsterdam discovered the defect catalogue, by Den Haag the same checks were run up front; a fourth pass costs less than the third and returns the same artefacts. Not fully automated, not finished at publish, not a legal opinion — four decisions plus one flagged assumption stay open with the responsible bodies](../../assets/slides/dmn-workflow/slide-08-why-the-testing-is-evidence.png)
  <figcaption>One case per rule, a suite that does not trust the model, and a runner that is tested too</figcaption>
</figure>

Whether "all tests pass" means anything is the first question a board asks. Four
practices make the answer yes:

1. **Coverage** — one case per rule, not per feature or happy path: 100, 121 and 65 cases
   for 99, 25 and 55 rules.
2. **Independence** — the one that surprises people most. A suite generated from the
   thing under test proves nothing, so each generator holds its own independent copy of
   the expected answers and refuses to emit a case if that copy disagrees with the model.
3. **Self-check** — the runner is tested too. Deliberately broken expectations confirm
   each is reported as a failure, which found a real defect in the comparison logic.
4. **Both paths** — the command-line runner and the editor's own pass/fail logic read the
   expectations differently, so both run against the live engine.

Together they make a green run evidence rather than reassurance.

**What comes out of every pass:**

| Artefact | What it is |
|---|---|
| `<original>.dmn` | The export, untouched — the auditable record of what legal analysis delivered |
| `<original>-patched.dmn` | What actually runs |
| `<published>.ttl` | The linked-data service, exported from the CPSV Editor |
| `CHANGELOG.md` | What changed, when, and why |
| `testCases/` | The suite, the reasoning behind it, and a runner anyone can execute |

And live: a deployed, versioned decision on the engine, callable over HTTP with a
documented request body.

A fourth pass costs less than the third — Amsterdam discovered the defect catalogue, and
by Den Haag the same checks were run before anything was deployed. It is still **not
fully automated, not finished at publish, and not a legal opinion**.

---

## Three questions for the standard

<figure markdown style="width:100%; margin:0;">
  ![Slide 9 of 9, titled Three things only a standardisation body can settle — slide 06 split the open items into three lanes; these are the two in the standard lane, plus the one the other two keep producing. Three cards. 01 Identifiers: who owns the convention for naming a rule inside an article? Legislation attaches at three levels — whole decision, whole rule, single cell — and none is authoritative; in one file the generator minted its own web address over a rule's real identifier 12 times; 2 of Amsterdam's 99 links still do not resolve. Deliver: persistent identifiers at rule granularity, lined up with Juriconnect/BWB and ELI rather than alongside them. Support: a standards-management home for CPRMV, or a route to one. 02 Conformance: can conformant mean it executes, not just it validates? The validator passed all three exports as valid; none of them could run correctly, 15 defect families deep, and 23 provenance links were lost at the DMN-to-profile boundary with the file still validating clean. Deliver: a Dutch application profile of DMN whose test is it deploys and it answers — allowed subset, the defect catalogue as shared checks, one case per rule, legal source required. Support: the intake; we contribute the catalogue and the cases. 03 Outcomes: must a decision service say which fact is missing? "Information incomplete" and "we need the residence permit" both run and both pass structural validation; six per-person facts collapse into one flag with no rule broken, so today the weaker model is conformant. Deliver: a required third outcome — information needed, naming the fact — as an interoperability agreement, not a per-body choice. Support: the motivation argument under Awb. A dark panel, What we are not asking for: a study. We are asking for an owner and a conformance rule. All three questions were produced by running the models, not by reading them — which is also the offer: a fourth pass, on a regulation you choose, as the evidence base. And one gap we cannot close alone: findings land with three different addressees (slide 06), with no agreed route back. What we bring to the table: 179 rules published as executable, citable linked data; 286 test cases, one per rule, running against a live engine; 3 passes documented end to end — changelog, validation, runner. The defect catalogue on slide 04 is reusable as a conformance checklist by anyone adopting the profile](../../assets/slides/dmn-workflow/slide-09-three-questions-for-the-standard.png)
  <figcaption>Identifiers, conformance and outcomes — an owner and a conformance rule, not a study</figcaption>
</figure>

The [three lanes](#what-is-still-open-and-who-owns-it) exist so that each open item
reaches someone who can answer it. Two of them — the regulation and the tooling — have an
owner. The **standard** lane does not yet, and every question in it is one neither the
CPSV Editor nor a municipality can settle. The deck closes on three, written for a
standardisation body such as Forum Standaardisatie: the two standard-lane items from
slide 06, plus the one the other two lanes keep producing.

| | Question | What the passes showed | Deliver | Support |
|--:|---|---|---|---|
| 1 | **Identifiers** — who owns the convention for naming a rule inside an article? | Legislation attaches at [three levels](../developer/cell-level-grounding.md) — whole decision, whole rule, single cell — and none is authoritative. In one file the generator minted its own web address over a rule's real identifier 12 times (since fixed); 2 of Amsterdam's 99 legal links still do not resolve | Persistent identifiers at rule granularity, lined up with Juriconnect/BWB and ELI rather than alongside them | A standards-management home for CPRMV, or a route to one |
| 2 | **Conformance** — can conformant mean *it executes*, not just *it validates*? | The validator passed all three exports; none could run correctly, [15 defect families](#what-kept-going-wrong) deep. DMN carries a legal-source layer and the linked-data profile carries provenance, but no normative mapping connects them — 23 provenance links were lost at that boundary, and the file still validated clean | A Dutch application profile of DMN whose test is *it deploys and it answers* — an allowed subset, the defect catalogue as shared checks, one case per rule, legal source required | The intake — the workflow contributes the catalogue and the cases |
| 3 | **Outcomes** — must a decision service say *which* fact is missing? | "Information incomplete" and "we need the residence permit" both run and both pass structural validation. [Six per-person facts](#two-ideas-worth-keeping) collapse into one flag with no rule broken — so today the weaker model is conformant | A required third outcome — *information needed*, naming the fact — as an interoperability agreement, not a per-body choice | The motivation argument under the Awb |

**What is asked for is an owner and a conformance rule, not a study.** All three
questions came from running the models rather than reading them, and that is also the
offer: a fourth pass, on a regulation the standardisation body chooses, as the evidence
base. What comes with it is what this page describes — 179 rules published as
executable, citable linked data, 286 test cases against a live engine, three passes
documented end to end, and a defect catalogue that anyone adopting the profile can use as
a conformance checklist.

One gap cannot be closed from this side alone: findings land with three different
addressees, and there is **no agreed route back** to any of them.

---

## Where to look in the repository

Each pass is recorded in full in the CPSV Editor repository:

| For | Read |
|---|---|
| The workflow brief this page and slides 1–8 are built from | [`docs/dmn-to-linked-data-workflow.md`](https://github.com/sgort/ttl-editor/blob/main/docs/dmn-to-linked-data-workflow.md) |
| A worked example, the largest | [Amsterdam `CHANGELOG.md`](https://github.com/sgort/ttl-editor/blob/main/examples/organizations/amsterdam/CHANGELOG.md) and [its validation write-up](https://github.com/sgort/ttl-editor/blob/main/examples/organizations/amsterdam/testCases/test-cases-validation-hva.md) |
| Cell-level legal grounding at scale | [SZW validation write-up](https://github.com/sgort/ttl-editor/blob/main/examples/organizations/szw/testCases/test-cases-validation-pw.md) |
| A model that had to be re-derived, not patched | [Den Haag validation write-up](https://github.com/sgort/ttl-editor/blob/main/examples/organizations/den%20haag/testCases/test-cases-validation-alo.md) |

---

## Related pages

- [The DMN Tab](dmn-tab.md) — uploading, validating, deploying and testing a model in the editor
- [DMN Testing](dmn-testing.md) — test cases, intermediate decisions and the pass/fail verdicts
- [Import & Export TTL](import-export-ttl.md) — the Turtle export stage 7 produces
- [Cell-Level Legislative Grounding](../developer/cell-level-grounding.md) — how a decision cell is tied to the norm it implements
