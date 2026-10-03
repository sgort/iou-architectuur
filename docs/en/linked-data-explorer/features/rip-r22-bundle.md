---
component: Linked Data Explorer
---

# RIP R2.2 VO Bundle

The **R2.2 bundle** is the second Regular Infrastructure Projects (RIP) process bundle shipped for the Province of Flevoland. It covers the *voorlopig ontwerp* (preliminary design) phase, picking up exactly where the [R2.1 bundle](rip-phase1-bundle.md)'s *"Fase 1 voltooid → R2.2"* end event leaves off.

It lives at `examples/organizations/flevoland/rip-phase-22/` and is deployed to Operaton in a single multipart request from the BPMN Modeler's Deploy modal, the same way every other bundle is.

The process was derived from `R2_2 - VO.pdf` (rev. 21-11-2024), one of the Flevoland phase specifications kept under `examples/organizations/flevoland/rip-phases-left/`.

---

## Process flow

`RipR22Process` has **four lanes and nine user tasks**.

| Lane | Responsible for |
|---|---|
| Projectleider | Overall progress and the client-requirements feedback loop |
| Ontwerper | The design itself — concept VO through definitive VO |
| RIP-team, Aandrager, Adviseur | Investigations, requirements gathering and review |
| Omgevingsmanager | Cables and pipelines, and the framework permit |

| Task id | Name |
|---|---|
| `Task_UitvoerenConditionerendeOnderzoeken` | Uitvoeren conditionerende onderzoeken |
| `Task_VerzamelenKlanteisen` | Verzamelen klanteisen |
| `Task_InventariserenKabelsLeidingen` | Inventariseren kabels en leidingen |
| `Task_AanvragenRaamvergunning` | Aanvragen raamvergunning |
| `Task_OpstellenConceptVO` | Opstellen concept VO |
| `Task_BesprekenConceptVO` | Bespreken concept VO |
| `Task_BesprekenKlanteisenKL` | Bespreken klanteisen en kabels en leidingen |
| `Task_TerugkoppelenKlanteisen` | Terugkoppelen klanteisen |
| `Task_OpstellenDefinitiefVO` | Opstellen definitief VO |

### The join gateway takes all five branches

All five branches of the opening parallel split rejoin the join gateway. **The source PDF does not draw it that way.** It shows *Inventariseren kabels en leidingen* and *Aanvragen raamvergunning* leaving the pool into CO1 and JU3.5 and never coming back — which, read as control flow, deadlocks at the join, because a parallel join waits for every incoming branch.

Those two hand-offs are modelled as `textAnnotation`s instead. A `callActivity` would have been the faithful alternative, but CO1 and JU3.5 do not exist as fixtures, so it would dangle at deploy time and fail the manifest's `calledElement` test. Both are referenced by several phases and belong in a shared bundle of their own.

!!! note "A deviation from the specification, on purpose"
    This is the one place where the bundle deliberately does not mirror the
    drawing. The annotation records the hand-off without asserting a flow that
    would not execute.

---

## Bundle contents

Fifteen files deploy together: one BPMN, nine forms and five document templates.

### Forms

One per user task, bound with `camunda:formRef`. Field types stay inside the eight the R2.1 bundle already uses — `text`, `textarea`, `textfield`, `checkbox`, `datetime`, `select`, `radio`, `button` — because nothing beyond those is exercised against this Camunda 7.21 stack.

| Form | Task |
|---|---|
| `rip-conditionerende-onderzoeken.form` | Uitvoeren conditionerende onderzoeken |
| `rip-verzamelen-klanteisen.form` | Verzamelen klanteisen |
| `rip-inventariseren-kabels-leidingen.form` | Inventariseren kabels en leidingen |
| `rip-aanvragen-raamvergunning.form` | Aanvragen raamvergunning |
| `rip-concept-vo.form` | Opstellen concept VO |
| `rip-bespreken-concept-vo.form` | Bespreken concept VO |
| `rip-bespreken-klanteisen-kl.form` | Bespreken klanteisen en kabels en leidingen |
| `rip-terugkoppelen-klanteisen.form` | Terugkoppelen klanteisen |
| `rip-definitief-vo.form` | Opstellen definitief VO |

Two modelling decisions are worth knowing:

- The specification's conditional *"LCC-raming (indien variantenafweging)"* is a checkbox plus a reference field on `rip-concept-vo.form` rather than an artifact of its own, since it exists only when a variant trade-off actually happened.
- `klicMeldingReferentie` is collected **only** on `rip-inventariseren-kabels-leidingen.form`. The concept-VO task reads the same information but does not also write it — two forms writing one process variable would mean whichever task completes last silently wins.

### Document templates

One per green *"Format …"* box in the specification. A Format there and a `.document` here are the same thing: a template with bindings. The blue outputs drawn beside them are instances of these templates rather than artifacts of their own.

| Template | Attached to |
|---|---|
| `rip-kes.document` | `Task_VerzamelenKlanteisen` |
| `rip-ontwerptoelichting.document` | `Task_OpstellenConceptVO` |
| `rip-bevindingenformulier.document` | `Task_BesprekenConceptVO` |
| `rip-hoeveelheidsbepaling.document` | `Task_OpstellenDefinitiefVO` |
| `rip-objectenboom.document` | `Task_OpstellenConceptVO` |

Zone keys are `signOff` and `contactInformation`, camelCase, from the start — unlike R2.1's templates, which shipped with `signoff` and `contactInfo`, keys `DocumentZones` never declares, leaving their signature blocks silently unrendered until v2026.08.4 repaired them.

!!! note "One task, two templates"
    `Task_OpstellenConceptVO` produces both the Ontwerptoelichting and the
    Objectenboom, and carries both:
    `ronl:documentRef="rip-ontwerptoelichting,rip-objectenboom"`. The attribute
    holds a comma-separated list, so the Modeler badge on that task reads
    **2 documents**, and the Deploy modal includes both templates in the
    bundle. See [BPMN Modeler → Document template linking](bpmn-modeler.md#document-template-linking).

---

## Deploying the bundle

Deployment is identical to any other bundle — see [Deploying the bundle](rip-phase1-bundle.md#deploying-the-bundle) on the R2.1 page. Open `RipR22Process.bpmn` in the BPMN Modeler and click **Deploy**; all fifteen resources go through the LDE backend to Operaton as one deployment.

---

## The mirrored copy

The R2.2 bundle files exist **twice** in this repository, and its BPMN a third time downstream:

| Path | Role |
|---|---|
| `examples/organizations/flevoland/rip-phase-22/` | the authored source |
| `e2e-fixtures/flevoland/` | the mirror that is imported and deployed for end-to-end testing |
| ronl-business-api `packages/backend/src/rip-swimlane/__fixtures__/` | parser fixtures for the RONL Business API's swimlane derivation (BPMN only) |

Two checks keep the copies in step:

- **The parity test** (`packages/backend/src/example-fixture-parity.test.ts`) asserts that every file in a mirrored bundle is byte-identical to its twin in `e2e-fixtures/`. A bundle opts in by adding an entry to `MIRRORED_BUNDLES`; R2.1 and R2.2 do.
- **`npm run check-rip-bpmn`** (`scripts/check-rip-bpmn-copies.mjs`) covers the BPMNs of all RIP phases. It compares each `e2e-fixtures/` copy byte for byte with its source, and checks every authoring BPMN against the sha256 fingerprints in `rip-bpmn-fingerprints.json`, a file committed identically in both repositories so the RONL Business API can enforce the same thing in its own CI. After an intended edit, `node scripts/check-rip-bpmn-copies.mjs --write` regenerates the fingerprints, refreshes the `e2e-fixtures/` copies, and names the command that refreshes the RONL Business API's fixtures. The pre-push hook runs this check; no CI workflow does.

!!! warning "A pull request that changes only bundle files runs no backend tests"
    The backend workflow runs on every pull request to `acc`, but its
    `changes` job skips the test job unless the pull request touches
    `packages/backend/`, the workflow file, `.nvmrc`, `package.json` or
    `package-lock.json`. `examples/`, `e2e-fixtures/` and
    `packages/frontend/public/examples/` are not in that pattern, so a pull
    request that edits only bundle files never runs the parity test. Edit both
    copies together, and run the backend suite and `npm run check-rip-bpmn`
    locally before opening the pull request.

---

## Related

- [RIP R2.1 Bundle](rip-phase1-bundle.md) — the phase this one follows
- [BPMN Modeler](bpmn-modeler.md) — the Deploy modal and the `ronl:*` attributes
- [Document Composer](document-composer.md) — how `.document` templates and their zones work
- [Testing](../developer/testing.md) — the fixture and parity suites
- [Besluitvorming onder gedelegeerde bevoegdheid](besluitvorming-gedelegeerd-bundle.md) — the delegated-decision bundle, which pairs a document with a signature
