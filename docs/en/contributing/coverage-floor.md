---
scope: cross-cutting
verified:
  date: 2026-09-12
  against:
    CPSV Editor: "f5bae6a"
    Linked Data Explorer: "be6bc54"
    RONL Business API: "311d732"
---

# The Coverage Floor

!!! info "Re-verified for all three applications on 12 September 2026"
    Every claim on this page was re-checked against `f5bae6a`, `be6bc54` and
    `311d732`. The RONL Business API's figures were **measured rather than read**: all
    five of its suites were run with coverage on the tree `main` `311d732` publishes,
    which is byte-identical to `acc` `28e1a9e`.

    Its one remaining weakness on this page — a backend floor that gated nothing before
    a merge — closed in v2026.09.7.

*A per-file 80% branch-coverage floor, and what it took to enforce it in three
repositories*

All three application repositories hold new and changed code to **80% branch
coverage per file**. As of September 2026 all three enforce it **natively**, in
their test runners' own configuration, with no exemptions and no custom script.

That uniformity is recent, and the route each took is more instructive than the
destination.

---

## Why per file, and why branches

**Per file**, because a project average lets a well-tested utility pay for an
untested component. The branches that matter are precisely the ones nobody has
exercised, and an average is designed to hide them.

**Branches**, because statement and line coverage largely restate *"was this file
imported"*, and function coverage rewards splitting code into more functions. A
branch is a decision the code makes; an uncovered branch is a decision no test has
ever checked.

| Repository | Mechanism | State |
|---|---|---|
| CPSV Editor (`ttl-editor`) | Native thresholds in one runner | Clean, no exemptions |
| Linked Data Explorer | Native thresholds in both runners | Clean, no exemptions |
| RONL Business API | Native thresholds in all five runners | Clean, no exemptions |

---

## A functions floor is a separate decision

**80% functions is not a safe companion setting**, and this was measured rather
than assumed. In RONL Business API at the time the branch floor landed, adding a
functions floor at the same number would have failed **31 files**:

| Workspace | Files below 80% functions |
|---|--:|
| frontend | 11 |
| pa-cockpit | 10 |
| pa-demo | 7 |
| public-site | 3 |
| backend | 0 |

`public-site/TopBar.tsx` is the illustration: **100% branches, 66% functions**.
The two measure different things and are not interchangeable.

The asymmetry runs both ways. In the CPSV Editor, `ConceptsTab.jsx` reads 80.55%
on branches but **71.62% on statements and 63.33% on functions**, and `App.jsx`
reads 81.48% / 71.65% / **53.70%** — the uncovered code there is largely
branch-free, whole handlers no test calls, so a branch floor steps straight over
it. Worth knowing what the column you gate on does not see.

---

## Why one repository needed a script first

**Vitest cannot express a partial rollout of this policy.** Its `thresholds`
block accepts glob keys that look like per-file overrides, but they are
**additive** rather than overriding — from Vitest's own source, *"Global
threshold is for all files, even if they are included by glob patterns"*. A file
matching `'src/App.jsx': { branches: 34 }` is still measured against the global 80
as well, and the build fails anyway. `perFile: true` is all-or-nothing.

The CPSV Editor was not at 80% everywhere, so it carried
`scripts/check-branch-coverage.mjs` — a `DEBT` list working as a **ratchet that
tightened from both ends**:

| Condition | Result |
|---|---|
| Below its pin | Fail — a regression |
| More than 10 points above its pin | Fail, asking for the pin to be raised |
| At or above the floor | Fail, asking to be deleted |
| Naming a file that no longer exists | Fail |

The script's own header stated it was temporary and named its own deletion as the
last step of the work rather than an afterthought. That is what closed
[ttl-editor#103](https://github.com/sgort/ttl-editor/issues/103): `DMNTab.jsx`,
1855 lines and the largest file in the repository, went from 45.73% to **98.34%**
branch coverage, the last `DEBT` entry went with it, and the script was deleted in
favour of four lines of config.

Three things from that run are worth carrying:

- **The ratchet's upper bound fired for real**, once. An increment took
  `DMNTab.jsx` past its pin by more than the slack allowed, and the gate failed
  naming the new value. *A ratchet that only catches regressions decays into an
  exemption list* — this one did not.
- **Measure in isolation *and* in the full suite.** Both readings were identical,
  which is what proves no other file's tests were propping the number up. A
  per-file floor read only from a full run cannot tell the difference.
- **The last few branches are usually unreachable, and that is the honest place to
  stop.** Seven remain, all guards the UI cannot reach — `if (!uploadedFile)`
  under a button that only renders once a file exists, and three of the same
  shape.

---

## Reaching the floor has a load cost, and it lands somewhere else

Not a threshold mechanic, but it surfaced on the same change and would surface in
any repository pushed to this floor.

Bringing one file to 80% meant 56 new tests, 680 → 736. The suite then began
failing **intermittently, in unrelated files** — a different one each run, always
passing in isolation. Not a defect in the new tests and not one in the old:
Testing Library's `findBy*` gives up after one second by default, and under
coverage instrumentation with every file running in parallel, a control that
appears in tens of milliseconds on an idle machine can take longer than that on a
saturated one.

**Measured rather than assumed**, which is the only way to tell contention from a
real order dependency: three consecutive full runs clean with the new files moved
aside, one failure in three with them present.

Fixed at its own boundary — `asyncUtilTimeout: 5000` and `testTimeout: 15000`,
both commented as contention headroom. **Not by serialising the suite**, which
would diverge from CI, cost real time on every run, and hide the order
dependencies parallelism is good at exposing. Raising a wait is not a defect mask:
an element that is genuinely never rendered still fails, only later.

**The same shape at a much smaller dose.** The Linked Data Explorer added 31 tests
(1042 → 1073) and saw exactly one parallel-only failure: a `ShaclValidator` test
timing out at the 5000 ms default in a full run, passing **37 of 37 in isolation**,
in a file the change had not touched. It did not recur, and no timeout was raised
for it. Two readings, both worth carrying:

- **The effect scales with how loaded the run is, not with how many tests you
  added.** 31 was enough to surface it once.
- **A parallel-only failure is not a finding until it fails in isolation.** That
  one command is what separates contention from a real order dependency, and
  changing code on the strength of a full-run failure alone is how a healthy suite
  acquires defensive edits it never needed.

---

## Raising coverage without writing hollow tests

Writing tests *to raise a number* is the failure mode this whole policy exists to
avoid. Three mechanics kept the Linked Data Explorer's twelve-file push honest,
and all three transfer.

### Mutation-check every test — one written after the code cannot fail on its own merits

A test written against code that already exists **passes on its first run**, which
proves nothing about whether it *can* fail. So each new test had the branch it
targets deliberately broken in the production file, and had to fail before being
kept — then the file was restored. Cheap to automate: a shell loop over `sed`
one-liners, one file-scoped run each.

**That caught five of the thirty-one passing vacuously**, which would otherwise
have shipped as coverage with nothing behind it:

- **Two guard tests** used a response fixture with no `data` field at all, so
  `data ?? []` and the real `success && Array.isArray(data)` guard behaved
  identically. The fixture had to carry a payload that *survives* the guard's
  removal before the test could fail.
- **Four component tests** asserted *"nothing was added"* / *"nothing was saved"* —
  which stays true when the handler **throws** partway through.

!!! danger "On any React codebase, \"nothing happened\" is not a safe assertion"
    React surfaces an error thrown inside a click handler on `window`'s **`error`
    event** rather than rejecting the click, so an assertion on the DOM sees a
    successful no-op either way. The fix is a listener around the interaction that
    fails the test if anything was raised.

    This is the transferable one. A test that asserts an absence needs something
    watching for the throw, or it passes for the wrong reason.

### Some branches are unreachable, and leaving them is the honest move

Three guards sat behind a submit button already `disabled` on exactly the same
condition — `filename.trim() || chainName` under `disabled={!filename.trim()}`.
Covering them would mean invoking the handler directly, which tests nothing a user
can do, and is why two files stop at 98.08% and 94.44% rather than 100%.

**This is the same finding the CPSV Editor recorded** about `DMNTab.jsx`'s seven
remaining guards — reached independently, in a different codebase and a different
framework. Taken together they suggest a rule: *a per-file floor in the high
nineties is usually the ceiling, and the last few points are dead code asking to be
documented rather than tested.*

### Say which mutations a test does **not** catch

Two branches are covered but **behaviour-preserving**: a pair of
`if (!templates) return null` guards whose removal only produces a throw the
surrounding `try/catch` already swallows, and a `?? ''` feeding an `Array.join`
that coerces `undefined` anyway. Their mutations survive by construction. They are
worth keeping — they assert the returned contract — but a reader deserves to know
which mutations they do not catch, and the comments say so rather than implying
more.

### One file deliberately left at the bottom

`GraphView.tsx` stays at 82.26% — **51 of 62 branches**. The eleven uncovered ones
are inside d3's force-simulation tick and drag handlers: `d.x || 0` fallbacks that
need a node at the origin, and `if (!event.active)` guards that need synthesised
`D3DragEvent`s. Reaching them means standing up a d3 harness and asserting on d3's
mechanics rather than on the component.

It has **one branch of slack**, and that is worth stating numerically rather than
as a feeling: a twelfth uncovered branch still reads 80.95% and passes; the
thirteenth fails. The config comment records it, so whoever next meets the floor
there knows **the answer is to test their new branch rather than lower the
threshold**.

---

## Runner mechanics

- **Jest** takes a **glob key** (`'./src/**/*.ts'`), which it applies to each
  matching file individually.
- **Vitest** takes `thresholds: { branches: 80, perFile: true }`. It reports
  *"global threshold"* in its failure message **even in per-file mode** — that is
  its wording, not a misconfiguration. Naming the file rather than reporting the
  package average is what demonstrates per-file behaviour.

### How to verify a threshold actually bites

**Do not trust a green run.** Add a temporary file with a few uncovered branches
and confirm both that the run fails *and that it names the file*:

```
Jest:   ".../src/__threshold-probe.ts" coverage threshold for branches (80%) not met: 0%
Vitest: ERROR: Coverage for branches (0%) does not meet global threshold (80%) for src/__threshold-probe.ts
```

Naming the file is the part that matters — it proves the threshold is per-file
rather than being satisfied by a healthy package average. The CPSV Editor proved
its native threshold the equivalent way, by raising it to 99 and watching it name
eight files.

---

## Margins differ sharply, and "clean" means different things

All three were measured clean before enforcing. That word hides a lot:

| | Files measured | Lowest branch coverage |
|---|--:|---|
| RONL Business API backend | not derived | comfortable — 92.31% across the package |
| Linked Data Explorer backend | 38 of 44 | `sparql.service.ts` 82.85% |
| Linked Data Explorer frontend | 68 of 78 | `ChainBuilder/TestCasePanel.tsx` exactly 80.00% — **since raised to 100%** |
| CPSV Editor | 32 of 41 | `useDsoImport.js` 80.39% — **since raised to 92.15%** |

The RONL Business API's five workspaces were re-measured on 12 September 2026 and
every one passes the per-file floor, with these package averages on branches: backend
**92.31%**, frontend **89.78%**, `pa-cockpit` **88.52%**, `pa-demo` **95.65%**,
`public-site` **96.41%**. A package average is the number this page exists to distrust,
so read them only as *how much room the package has*, not as evidence any file is
covered; the floor is what speaks per file, and it passed in all five runners.

*"Files measured" counts files carrying at least one branch* — 68 of the 78 in
the Linked Data Explorer's frontend report, counted from `coverage-final.json`
rather than from the printed table, which elides rows. A file with no branches
cannot fail a branch threshold, so including it inflates the denominator without
telling you anything.

The Linked Data Explorer rows were re-measured at v2026.09.4. The frontend reads
**69 of 78**, one more file carrying a branch, with `GraphView.tsx` at 82.26% the
only one under 85%. The backend reads **38 of 44**, and its lowest file has not
moved. That backend row said **49** until 11 September 2026, copied from the comment
`jest.config.js` carries — *"measured clean when this landed — 49 files"* — and 49
is neither 38 nor the 44 files the report contains at all. It is the same class of
figure as the frontend's 64: quoted from a record rather than recounted under the
rule this table states. The CPSV Editor's row said **41**, which is the number of files
in its report; 32 of them carry a branch. Its lowest file has not moved.

!!! bug "This table named a file that does not exist, and the error travelled"
    Until 9 September 2026 the Linked Data Explorer row here read
    **`CaseworkerCasePanel.tsx`**. No such file has ever existed in that
    repository — the one sitting at exactly 80.00% was
    `ChainBuilder/TestCasePanel.tsx`. The wrong name reached a commit message, a
    config comment and a cross-repository record before anyone checked whether the
    file was real, and this page copied it from there rather than verifying it.

    The count was wrong too: **64** is not reproducible from any report, which is
    why the rule is now stated rather than the number quoted.

    Worth keeping as a caution about this page's own method. A margins table reads
    like measurement, so it invites transcription — but only the percentages had
    been measured, and the file names beside them had not.

Thresholds pass at `>= 80`, so a file at exactly 80.00% is green with **zero
margin** — the first uncovered branch added to it turns CI red on an otherwise
unrelated change.

**The Linked Data Explorer closed that gap in v2026.09.2**: twelve files raised,
package branches 90.59% → **92.88%**, files under 85% from fourteen to one, tests
1042 → 1073. **No production code changed** — test files only, plus the config
comment. The CPSV Editor has not yet, and arrived at the same position by a
different route: its three lowest files — `useDsoImport.js` 80.39%,
`ConceptsTab.jsx` 80.55%, `ChangelogTab.jsx` 80.70% — are each one uncovered
branch from failing, and the ratchet's pins that used to absorb a slip are gone.

**The first uncovered branch added to any of them turns CI red on an otherwise
unrelated change.** That is the floor working as designed, but it is worth meeting
in a config comment rather than in a surprising failure.

---

## A floor only gates where the tests run before the merge

A threshold enforced after a merge is a report, not a gate. This is where the
three diverge most:

| Repository | Tests on a pull request |
|---|---|
| CPSV Editor | ✅ both Static Web Apps workflows run `npm run test:ci` on `push` **and** `pull_request` — run, though not required; see below |
| Linked Data Explorer | ✅ backend and frontend, acc workflows — run, though not required; see below |
| RONL Business API | ✅ all five workspaces since v2026.09.7 — run, though not required; see below |

**All three now run their suites before the merge.** The RONL Business API was the last
to close that gap, and it had two halves. Its backend workflow triggered on `push`
alone, so its 2008 tests ran only *after* a merge and its backend branch threshold
gated nothing on a pull request
([#87](https://github.com/sgort/ronl-business-api/issues/87)). And `@ronl/pa-cockpit`,
a library with no deploy workflow of its own, **ran nowhere in CI at all** — its 476
tests were measured only on a developer's machine; both frontend workflows now run its
suite, placed before the frontend's own because the frontend imports it.

The backend trigger proved itself on the pull request that carried it: an `axios` 1.18
security bump broke the backend build there, with 1859 tests passing and one suite
failing to compile on a widened header type. Before the trigger existed, that lands on
`acc`.

The Linked Data Explorer had the same gap and **closed it in v2026.09.2**: its
backend suite — 1151 tests at v2026.09.4 — now runs on the pull request rather than
only after the merge. It is the worked example, because it had already let a genuine
defect sit on a pushed branch for days — no pull request ever ran the test that
caught it.

!!! note "Running before the merge is not the same as blocking it"
    The CPSV Editor's and the Linked Data Explorer's rulesets require two checks,
    `audit` and `scan`; the RONL Business API's require `audit` alone. The workflows
    that run the suites, and so enforce the floor, are not among them in any of the
    three. A pull request that drops a file below 80% therefore turns its checks red
    and **stops the deploy**, and the merge button stays available. That is a
    deliberate gap rather than an oversight only if someone decided it; making the
    test checks required is one ruleset change, provided each can report on every
    pull request — a path-filtered workflow that never runs would wedge the pull
    request instead.

!!! warning "The fix is not identical, and the difference matters before copying one into the other"
    The Linked Data Explorer's backend workflow **deploys to Azure**, so its
    `pull_request` trigger had to come with six deploy-side steps gated on the
    event — arranged as per-step conditions rather than a job split, so the check
    name stays stable and no ruleset entry changes.

    RONL Business API's backend workflow **does not deploy**: it ends at a
    deployment zip and an uploaded artifact, with the real deploy a manual script
    run from a clean `acc`. Nothing in that job has an external side effect, so
    there is nothing to gate — the change is the trigger alone.

!!! tip "A package outside the measurement is not covered — it is unmeasured"
    `@ronl/shared` has no test runner, deliberately: it holds types, constant data and
    re-exports, and there is nothing there to test. The consequence is sharper than an
    exemption, though. A function placed in that package is not *under-tested*; it is
    **outside the measurement entirely**, so no run fails and no reviewer sees a number
    move. That happened once — v2026.09.4 moved a branching label helper out of the
    package for exactly that reason, and it was caught by hand, by someone who happened
    to look.

    v2026.09.7 replaced the convention with a check
    ([#84](https://github.com/sgort/ronl-business-api/issues/84)): `check-shared` fails
    the `audit` job on a function, class, conditional or loop anywhere in the package.
    It parses with the TypeScript compiler API rather than matching text, because an
    arrow in an interface is a type and the same syntax assigned to a const is logic,
    and no regular expression separates the two. It runs in `audit` rather than a
    workspace suite because `audit` has no paths filter and is the required check — so
    every pull request reaches it, including the one that first adds a function to a
    package no filter yet watches.

    The general rule this leaves: **where a package cannot be measured, enforce what
    makes it unmeasurable** rather than measuring nothing and calling it covered.

**Production workflows are deliberately excluded from that treatment**, on
evidence rather than preference. In the Linked Data Explorer the `acceptance`
environment has no protection rules while `production` has required reviewers and
a branch policy — so a `pull_request` trigger on a production workflow would make
every pull request to `main` **wait on a human approval before the tests could
run**: an approval gate in front of the check meant to inform it. `main` is
promoted from `acc`, and those commits already ran the full suite there.

---

## Adopting this in a fourth application

1. **Measure before enforcing.** Native thresholds are all-or-nothing per file. A
   repository not yet at 80% everywhere needs the ratchet approach instead — and
   should treat that script as temporary from the day it is written. The CPSV
   Editor's carried one file and was deleted with it, which is the intended
   lifespan.
2. **Gate on branches only** until a functions floor has been measured
   separately. It is not a free companion setting.
3. **Check where the tests actually run.** A floor enforced only after the merge
   is retrospective.
4. **Prove the threshold by making it fail**, and confirm the failure names the
   file.
5. **Expect a load cost** when a large file is brought up, and fix it at its own
   boundary rather than by serialising the suite.

---

Related: [Supply-Chain Pinning](supply-chain.md) for what the `audit` job gates,
and [Build Provenance](build-provenance.md) for identifying which build a running
app is.
