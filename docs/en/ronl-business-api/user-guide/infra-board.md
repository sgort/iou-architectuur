---
component: RONL Business API
---

# Infra-board

*portfolio · fases*

Infra-board is portfolio steering for infrastructure projects. It organises projects into phase swimlanes, from planning through delivery, with per-project status and RIP management.

On opening the board you see projects grouped by phase, with their status and RIP information, so the portfolio's progress is visible in one view.

**A project between two phases stays in view.** When a project has finished a phase and the next has not been started yet, the portfolio shows it at the phase it finished, marked *wachtend* and labelled *… afgerond · wacht op start van* the next phase — the same projects Beheer lists under *Starten*. The rail's **Wacht op start** counts them. A project that has finished R6.1 reads **RIP afgerond**. On the *Per fase* board a waiting card names the phase it waits for, and opening the project shows the finished phase and what comes next.

Since September 2026 the **Faseladder reads twelve of twelve deelprocessen inzetbaar** — every RIP phase from R2.1 through R6.1 is modelled and deployed, where previously only R2.1 was. Three things follow for you:

- **Finishing a phase readies the project for the next one.** A completed instance moves its project into the following phase's *Starten* list automatically, so you no longer start each phase from a standing position.
- **Every phase has a real diagram.** Opening a project shows the process drawn from the model actually deployed on the engine, not a hand-maintained sketch — including its rework loops, and coloured by what genuinely ran when you select a finished rung. It looks the same as the Caseworker's process overview: a legend that lists only what the diagram shows, the lanes you work in marked **jouw rol**, your own task marked **jouw taak** and a colleague's claimed task **geclaimd**, and a dashed outline on every task that is not yours. A decision is a diamond with a question mark and its question above it; a parallel split or join is a bar captioned *tegelijk* or *alles klaar*.
- **A task shows every document it carries.** Where a process step produces more than one deliverable, the diagram gives it one badge per document rather than naming only the first. R2.2's *Opstellen concept VO* is the clearest case: it yields both an **Ontwerptoelichting** and an **Objectenboom**, and both are named on the node. A document that a task links from eDOCS rather than generates is not drawn on the node — it is in the task's **Documenten bij deze taak** and the phase's **Documenten** panel (see [Documents at a task](#documents-at-a-task)) — so once R2.2's model declares the Ontwerptoelichting as linked, that node will name only the Objectenboom.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: a RIP phase swimlane diagram derived from the deployed BPMN, showing lanes, task states and a rework loop](../../assets/screenshots/ronl-business-api-rip-phase-swimlane.png)
  <figcaption>A phase diagram drawn from the BPMN Operaton has deployed — lanes, per-task state, and rework loops routed below the lane rows</figcaption>
</figure>

One number is deliberately absent: **R5.4 shows `—` rather than a Klaar figure.** Klaar is derived from the preceding phase's completions, and R5.3 has four possible endings — only one leads to R5.4, and one of the others lets a project legitimately complete R5.3 more than once. Any number there would overstate R5.4's candidates without the screen being able to show why, so none is given.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: RONL Business API Infra-board showing phase swimlanes with per-project status](../../assets/screenshots/ronl-business-api-infra-board.png)
  <figcaption>Infra-board — portfolio steering for infrastructure projects</figcaption>
</figure>

## Starting a project on a phase

Starting R2.1 from its phase page asks you for two things first: a
**Projectnummer** and a **Projectnaam**. Both are required — the *R2.1 starten*
button stays disabled until each holds something more than spaces — and both are
trimmed before they are sent.

Naming it here is what makes the project recognisable everywhere at once. The
number and name travel with the process from the moment it starts, so the
portfolio, the command palette and the phase page's WIP and Gereed tables all
show the project rather than a placeholder. The intake form that follows asks
for the same two fields and **opens already filled in with what you typed**, so
nothing is entered twice. The command palette (**Ctrl+K**) also finds projects
waiting between phases, as the portfolio lists them, and opens them the same way.

!!! note "A project started some other way is named by its state, not by a dash"
    An instance started outside this screen has no number or name until its
    intake form is submitted. Rather than showing a dash, the board says what it
    actually is: *"Nieuw R2.1-project · intake open"* for a nameless R2.1
    instance, shown next to the first characters of its instance id, and *"RIP
    R2.x project"* for one that has moved past R2.1.

**The board notices a project started elsewhere.** If an instance is started
outside the board — by a script, or by someone else — the live rows pick it up
when you come back to the tab, and when you switch between Mijn dag, Portfolio
and Beheer. A page reload is no longer needed for it to appear. The phase counts
on the Faseladder refresh with them.

---

## Working on a task

In a task's panel the process variables, **Procesgegevens**, start folded: **Gegevens tonen** opens them. Claiming a task refreshes the project's open tasks at once, so the diagram's marks follow straight away.

---

## Documents at a task

Some documents of R2.1 to R2.4 are not made by the board but kept in eDOCS: a PSU-presentatie, an
Ontwerptoelichting, a Projectraming. The board calls them **B** documents, and **B+** when they also
carry key figures; a document the board makes itself is an **A** document. When a phase's model
declares that a task links such a document, the task shows **Documenten bij deze taak** above its
form, and you cannot complete the task until the block is complete.

!!! note "Not on the process engines yet"
    The R2.1–R2.4 models that declare these linked documents
    ([linked-data-explorer#362](https://github.com/sgort/linked-data-explorer/pull/362)) are not yet
    deployed on the ACC or the production process engines. Until they are, no task shows this block
    and the Documenten panel below has no B or B+ rows; both appear once those models are deployed.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: the Documenten bij deze taak block of an Infra-board task, with a document linked from the eDOCS projectmap, its key figures, the kredietcheck with its voorstel, and Taak voltooien disabled](../../assets/screenshots/ronl-business-api-infra-board-taak-documenten.png)
  <figcaption>A task's documents: linked from the eDOCS projectmap, with its key figures and the kredietcheck</figcaption>
</figure>

In those models, these tasks link a document:

| Phase | Task | Document | Kind |
|---|---|---|---|
| R2.1 | Uitvoeren PSU en aanvullen Projectplan 3. PSU-verslag | PSU-presentatie | B |
| R2.2 | Opstellen concept VO | Ontwerptoelichting | B |
| R2.2 | Bespreken concept VO | Bevindingenformulier | B |
| R2.2 | Opstellen definitief VO | Hoeveelheidsbepaling | B |
| R2.3 | (Laten) opstellen VO-raming | Projectraming VO | B+ |
| R2.3 | Opstellen SSK-raming | SSK-rekenmodel Provincie Flevoland UAV | B+ |
| R2.3 | Controleren Projectraming VO | — the kredietcheck | |
| R2.3 | Bepalen inkoopstrategie | Inkoopplan, only when one is written | B |
| R2.4 | Opstellen Projectraming DO | Projectraming DO, and the kredietcheck | B+ |
| R2.4 | Invullen ILS | ILS Flevoland | B |
| R2.4 | Samenstellen Verzamelmap V&G | Verzamelmap documenten V&G (a folder) | B |

**Link a document.** Under *Kiezen uit de projectmap in eDOCS* the block lists the project's eDOCS
projectmap, with each item's number, version, date and author; choose the document. For the V&G
collection you choose a folder instead (*Map kiezen*), and the block then lists the three documents that
folder must hold — *V&G-plan ontwerpfase*, *Risico-inventarisatie V&G*, *Aanstelling V&G-coördinator
ontwerpfase* — each **Aanwezig** or **Ontbreekt in de map**; put a missing one in the folder in eDOCS.
A linked document shows its eDOCS name.

**Or upload it.** **Bestand uploaden naar projectmap…** sends a file of at most 20 MB to eDOCS, files it
into the projectmap under the project number and links it. When the project has no projectmap yet, the
button reads **Bestand uploaden naar eDOCS…** and the file lands in eDOCS outside the projectmap.
A folder cannot be uploaded: make it in eDOCS and link it.

**When the projectmap is empty** the block says so and what to do — upload a file, or put it in the
projectmap in eDOCS — and **Opnieuw laden** reads it again.

**Key figures (B+).** Under the document, enter the figures from the spreadsheet: for a projectraming
the total excluding VAT, the part for the unforeseen, and the price level; for the SSK model the building
costs and the total. The board does not recalculate them; the spreadsheet stays the source. In R2.4 the
Projectraming DO opens with the figures of R2.3's Projectraming VO, to confirm or change.

**The kredietcheck.** Enter the *Beschikbaar projectkrediet* (R2.4 brings it from R2.3). The block shows
the estimate, the credit and the difference, and marks **Binnen** or **Buiten projectkrediet** as its
*voorstel*. You decide; when you choose against the suggestion, give a reason under *Reden voor afwijken
van het voorstel*. The answer is what the process branches on.

**Taak voltooien** stays disabled while anything is missing, and the block's last line says what: *Nog
nodig: …*, or *Alles compleet.* The platform checks the same when you complete, so a task cannot close
without its documents by any route through the board.

You link and upload as yourself, with your Flevoland account: eDOCS records your name and applies your
rights. Signed in with another account, the block says *eDOCS is alleen beschikbaar als u bent
ingelogd met uw Flevoland-account.* Only someone who may do the task — who holds one of its roles — can
link its documents, and only while the task is open.

Reading a task's documents also needs the caseworker role — for a Flevoland account, the Entra ID app
role `IOU_USERS`. Without it, a task panel shows *De documenten van deze taak konden niet worden
geladen.* above its form.

### The Documenten panel

A project page shows, under the phase diagram, a **Documenten** panel for the selected phase: every
document the phase's model declares, A, B or B+, with the task and role that produce it, its eDOCS
number, version and date, and its status — **Gekoppeld**, **Opgemaakt**, **Wordt opgemaakt bij
akkoord**, **Ontbreekt — taak wacht**, **Nog niet aan de beurt** or **Niet nodig — criteria voldaan**.
A B+ row shows its figures, and a phase with a kredietcheck has a *Beslispunt* under the table with the
estimate, the credit and the answer. **Taak openen** selects the task that has to produce a missing
document. The panel reads again after each task you complete.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: the Documenten panel of a RIP phase on a project page, listing A, B and B+ documents with their eDOCS number and status, and the kredietcheck Beslispunt](../../assets/screenshots/ronl-business-api-infra-board-documenten-panel.png)
  <figcaption>The Documenten panel of a phase: every document, its werkwijze and status</figcaption>
</figure>

On a phase page, the WIP table gains an **eDOCS** column — *2/3 gekoppeld*, or *1 ontbreekt* — and the
blockade names what a project is waiting for, such as *Wacht op koppeling Projectraming VO*.

---

## Signing a phase-exit approval

Some approval tasks are signed rather than merely ticked. Where a task carries a
signature requirement in its process model, the panel that normally shows a form
shows a **signing panel** instead — you sign the phase document without leaving
the board.

The flow, from a project leader's point of view:

1. **Claim the task.** An unclaimed task shows the claim button as usual.
2. **The board checks whether the task is signed.** For a moment it shows
   *Ondertekening controleren…* instead of a form, so a task that must be signed
   is never offered the ordinary approval form.
3. **The signing panel replaces the form.** It reads *Deze taak vereist een
   digitale handtekening.* Choose **Onderteken nu** to open the signing
   ceremony in the panel itself, or **Stuur per e-mail** to have the request
   emailed to you and sign elsewhere, for example on your phone.
4. **Sign.** The panel watches for completion on its own.
5. **The task completes.** The signed document and its evidence summary are
   archived in eDOCS, and the process moves on. Their titles in eDOCS end in
   "— namens" followed by your name and e-mail address, so the archive shows
   whom they were signed for.

You do not complete the task by hand — it completes when the signature lands.

**Declining also completes the task.** If you decline in the ceremony, the
panel says *De ondertekenaar is niet akkoord gegaan met dit document.*, the
task is completed for you as not approved, the board refreshes its list, and
the process follows its "niet akkoord" path.

Your account needs an email address to sign. Without one the panel says so and
offers no retry: only an administrator can add it.

If your account is the one ValidSign sends its requests from, you cannot sign
with it. The panel says *U bent de afzender van ValidSign-verzoeken en kunt
daarom niet zelf ondertekenen.* and offers no retry: let a colleague sign.

!!! note "If the panel looks stuck after you have signed"
    The panel polls for the result, and a signature can complete through either
    the platform's callback or a periodic sweep. If it has not resolved after a
    minute or so, reload the page: the status is read fresh, not held in the
    panel. When the status cannot be read three times in a row, the panel says
    so itself — *De status van de ondertekening kon niet worden opgehaald.* —
    and asks you to reload.

For how this works underneath — the signing platform, the environment locks, and
what happens if the callback never arrives — see
[ValidSign signing](../developer/validsign-signing.md). The same panel appears in
the caseworker task inbox for a task that must be signed — see
[Caseworker](caseworker.md).

---

!!! note "Brief for now"
    This page covers what the board is for and what you see; a fuller
    step-by-step guide will follow. See [Getting Started](getting-started.md).
