---
component: Linked Data Explorer
---

# RIP Phase Ladder

*Flevoland's Regionaal Investeringsprogramma, modelled as deployable BPMN*

The RIP ladder is the sequence of phases a Flevoland infrastructure project passes
through, from project definition to discharge. Each phase is authored here as a BPMN
bundle — the process, its forms and its document templates — and deployed to Operaton
through the [BPMN Modeler](bpmn-modeler.md). The
[RONL Business API](../../ronl-business-api/user-guide/infra-board.md) adopts the
deployed definitions into its phase catalogue and draws the Infra-board from them.

Two phases have their own deep pages, written when they were the only ones modelled:
[R2.1](rip-phase1-bundle.md) and [R2.2](rip-r22-bundle.md). This page covers the ladder
as a whole.

---

## What is modelled

**Eleven of twelve phases**, as of v2026.09.1. Nine of them landed in that single
release; R2.1 and R2.2 preceded it.

!!! info "R5.3 is not in this release"
    R5.3 — *(vervroegde) Ingebruikname / Oplevering* — was still unmodelled at
    v2026.09.1 and was added to `acc` the following day. It is therefore **not** part
    of the version this page documents. The RONL Business API's Faseladder reads
    *eleven of twelve deelprocessen inzetbaar* against this release.

| Phase | Subject | Nodes | Flows | Lanes | Forms | Docs |
|---|---|--:|--:|--:|--:|--:|
| [R2.1](rip-phase1-bundle.md) | Projectdefinitie en voorbereiding VO | 19 | 21 | 9 | 12 | 3 |
| [R2.2](rip-r22-bundle.md) | Voorlopig ontwerp | 17 | 21 | 4 | 9 | 4 |
| R2.3 | VO-raming | 22 | 23 | 9 | 12 | 6 |
| R2.4 | DO en -raming | 29 | 33 | 6 | 18 | 9 |
| R3.1 | Opstellen bestek en tekeningen | 25 | 31 | 4 | 12 | 6 |
| R3.2 | Afronding bestek en tekeningen | 27 | 30 | 7 | 18 | 7 |
| R4.1 | Aanbestedingsproces | 25 | 27 | 7 | 17 | 7 |
| R5.1 | Voorbereiding op uitvoering | 25 | 30 | 8 | 19 | 10 |
| R5.2 | Directievoering en toezicht UAV | **56** | **67** | 7 | **36** | **11** |
| R5.4 | Oplevering en onderhoudsperiode | 39 | 46 | 6 | 26 | 8 |
| R6.1 | Projectdecharge | 28 | 32 | 6 | 21 | 4 |

!!! note "Counted from the BPMN, not from the release notes"
    Every figure above was derived by parsing the eleven `RipR*Process.bpmn` files at
    the v2026.09.1 release commit — flow nodes (tasks, events and gateways),
    `sequenceFlow` elements, `lane` elements, distinct `camunda:formRef`/`formKey`
    values, and distinct `ronl:documentRef`/`ronl:signatureRef` values.

    They agree with the release notes everywhere the notes state a figure, with one
    exception: **R2.3 has 22 flow nodes, where the notes say 21.** The file is the
    authority — 12 user tasks, 1 start event, 4 end events, 4 exclusive gateways and
    1 parallel gateway.

---

## Modelling decisions that recur

The phases were not laid out uniformly, and the differences are deliberate. Four
patterns are worth knowing before reading any individual diagram.

### Parallel splits where the source draws no order

Several phases fan out into streams that share no data and have no sequence in the
source sheet. R5.1 has five preparation streams — VISI, Better Performance, the
toezichtsplan, the besteksadministratie and the startoverleg — and R6.1 has three
(financial overview, transfer declaration, final evaluation) converging on the
dechargedossier. Where the sheet draws no order, **a parallel split and join is more
faithful than an arbitrary sequence**.

### A period, not a deliverable

R5.2 is the only phase whose subject is an ongoing period rather than a product, and
it is the densest in the ladder. It is modelled as a parallel split into the weekly
cycle, invoicing and the delivery request, joined before the phase exit.

The flat alternative was considered and rejected on a concrete failure: **one loop
containing every stream would force an invoice and a delivery request through every
week**, and deadlock a real instance on the parallel join. The repetition is confined
to the weekly branch, where the source sheet's own *Werk gereed* decision sits.

### Rework loops belong to the phase that owns the decision

Rework is modelled where the source puts the decision, not where it would be tidiest.
R2.4 carries the ladder's first rework loop; R5.2 carries three — weekstaat rejected,
AWR overview rejected, and work not finished. R4.1 runs two irregularity checks *in
sequence*, each with its own remedy: an unlawful tender is set aside and rejected on a
terminating path, while an unclear tender prompts a request for clarification that
loops back into the unit-price check.

### One exit per phase, so the phase end stays detectable

Every phase ends at a single end event, because the ladder's progression rule depends
on a completion being observable. Two phases needed work to preserve that:

- **R6.1's sheet draws two *Einde proces* markers**, one per closing action. They mean
  the same completion, so they are modelled as one end event behind a parallel join.
- **R5.1's BO13.1 branch is a round trip, not an exit.** On *ja* the installation part
  is handed to Beheer en Onderhoud, which communicates the handover back, so the leg
  rejoins the document check and the phase keeps its single R5.2 exit.

---

## Two traps the modelling surfaced

**An empty lane deploys as a lane no task can land in.** R5.4's source sheet draws an
*Aannemer* band carrying no activity — the contractor is written about in that phase
but never acts. The lane is omitted and the reason recorded in a text annotation on
the diagram, rather than deployed as a band that can never receive work. R5.1 is the
first phase in which the contractor genuinely occupies a lane.

**A start form on a programmatically started process leaves the instance stuck.** R2.3
was the first phase generated from the reusable BPMN toolchain rather than laid out by
hand, and it surfaced this: on a programmatic start the gating variable would be
unset, leaving the instance with no selectable outgoing flow. The start form was moved
into the first task.

---

## Forms bind to their own deployment

Since v2026.09.0 every form reference in these bundles uses
`camunda:formRefBinding="deployment"` rather than `"latest"`.

Tenanting a process definition made the process unambiguous and its forms ambiguous:
`"latest"` resolves a form key across the whole engine repository rather than within
the bundle, so deploying under tenant `flevoland` produced `ENGINE-03109` — the key
existing for multiple tenants. `"deployment"` resolves the form from the process
definition's own deployment, unique by construction, so tenanted and untenanted copies
coexist and no deployment history has to be destroyed.

91 of 109 references were converted. `thuisbatterij` and `ind` remain on `"latest"`
because their form keys resolve nowhere in the repository.

---

## Deploying a phase

The [BPMN Modeler](bpmn-modeler.md) deploy dialog refuses a bundle whose forms or
documents are missing from local storage — listing them by name and disabling Deploy
while any remain. That guard exists because its absence produced a failure three
components away: a phase deployed without its documents, and the RONL Business API's
phase-exit approval silently rendered an ordinary form instead of the signing panel.

!!! warning "Already-deployed definitions do not heal themselves"
    `public/examples` is seeded into `localStorage` and re-fetched only when its
    version rises. After a change to the seeded bundles you need a frontend deploy and
    a page load that re-seeds; the `e2e-fixtures` copies must be re-imported through
    the Modeler before an end-to-end run exercises them.
