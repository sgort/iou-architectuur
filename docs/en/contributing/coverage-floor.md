---
scope: cross-cutting
---

# The Coverage Floor

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

The asymmetry runs both ways. In the CPSV Editor, `ConceptsTab.jsx` reads 80.56%
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
| RONL Business API backend | — | comfortable |
| Linked Data Explorer backend | 49 | `sparql.service.ts` 82.85% |
| Linked Data Explorer frontend | 64 | **`CaseworkerCasePanel.tsx` exactly 80.00%** |
| CPSV Editor | 41 | `useDsoImport.js` 80.39% |

Thresholds pass at `>= 80`, so that Linked Data Explorer file is green with **zero
margin**, and thirteen more sit between 80 and 85. The CPSV Editor arrived in the
same position by a different route: its three lowest files — `useDsoImport.js`
80.39%, `ConceptsTab.jsx` 80.56%, `ChangelogTab.jsx` 80.70% — are each **one
uncovered branch** from failing, and now that the ratchet's pins are gone there is
nothing to absorb a regression.

**The first uncovered branch added to any of them turns CI red on an otherwise
unrelated change.** That is the floor working as designed, but it is worth meeting
in a config comment rather than in a surprising failure.

---

## A floor only gates where the tests run before the merge

A threshold enforced after a merge is a report, not a gate. This is where the
three diverge most:

| Repository | Tests on a pull request |
|---|---|
| CPSV Editor | ✅ both Static Web Apps workflows run `npm run test:ci` on `push` **and** `pull_request` |
| Linked Data Explorer | ✅ backend and frontend, acc workflows |
| RONL Business API | ⚠️ **frontend, pa-demo and public-site only** |

**RONL Business API's backend workflow triggers on `push` alone**
([ronl-business-api#87](https://github.com/sgort/ronl-business-api/issues/87)). Its
2008 tests run only *after* a merge, so its backend branch threshold gates nothing
on a pull request — it would fail on `acc`, after the fact, rather than on the
branch that caused it. **The floor is real in four of its five workspaces and
retrospective in the fifth.**

That is the same gap the Linked Data Explorer closed, where it had let a genuine
defect sit on a pushed branch for days because no pull request ever ran the test
that caught it.

!!! warning "The fix is not identical, and the difference matters before copying one into the other"
    The Linked Data Explorer's backend workflow **deploys to Azure**, so its
    `pull_request` trigger had to come with six deploy-side steps gated on the
    event — arranged as per-step conditions rather than a job split, so the check
    name stays stable and no ruleset entry changes.

    RONL Business API's backend workflow **does not deploy**: it ends at a
    deployment zip and an uploaded artifact, with the real deploy a manual script
    run from a clean `acc`. Nothing in that job has an external side effect, so
    there is nothing to gate — the change is the trigger alone.

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
