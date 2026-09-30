---
component: RONL Business API
---

# Caseworker

*werk · taken*

Caseworker is the personal work queue for case handlers. It brings together the tasks, claims and deadlines that belong to your cases, shows where each task stands in its process, and has a built-in assistant to help with quick assessment.

On opening the board you land on the **Taken** inbox in the **Werk** mode: your tasks on the left, the one you pick on the right, so you can take up the next piece of work without hunting for it across other boards.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: RONL Business API Caseworker Taken inbox with a task selected, its Awb-fase hint in the list, the Waar sta ik stepper, the folded Procesgegevens bar and the steps grouped per role](../../assets/screenshots/ronl-business-api-caseworker-board.png)
  <figcaption>Caseworker's Taken inbox — a task from a process drawn in lanes, with its Awb phase, the folded Procesgegevens bar and its steps per role</figcaption>
</figure>

---

## The task list

The inbox has three columns: filters, the list, and the selected task.

The filter column offers **Alle taken**, **Te laat**, **Vandaag**, **Deze week**, **Mijn claim** and **Openstaand**, each with the number of tasks it holds. **↺ Vernieuwen** reloads the list. The list is sorted by deadline, soonest first; tasks without a deadline come last.

Each task in the list shows its name, whether it is **Open** or **Geclaimd**, the key of the process it belongs to, and its deadline — **Deadline** followed by the date, or **Te laat —** followed by the date once it has passed. When the task's process is drawn in lanes and marks its Awb phases, the list also shows the phase the task sits in, for example **Awb-fase 4+5**.

## Opening a task

Selecting a task opens it on the right: the process key above its name, then **Aangemaakt**, **Deadline**, **Status** and **Taak ID**.

**Procesgegevens** — the process variables of the case — is a long table, so it starts folded. **Gegevens tonen ▼** opens it and **Gegevens verbergen ▲** closes it again. It folds back each time you select another task.

## Where the task stands

For a task whose process is drawn in lanes, the task shows where it stands in that process. Which processes do this is set by how their model is drawn — see [Which processes show the process view](#which-processes-show-the-process-view). For any other task, the steps appear as a plain list, as described under [Processtappen](#processtappen).

### Waar sta ik

Under the task's header, a compact stepper shows the eight Awb phases, with the phases already passed marked done and the current one highlighted. The line above it reads, for example:

```
Waar sta ik · Awb-fase 6 · stap 5 van 8
```

The first number is the legal phase, the second the position on the stepper. The two differ from phase 6 on because phases 4 and 5 — treatment and decision — are one step. The eight steps are:

| Step | Phase | Name |
|---|---|---|
| 1 | Fase 1 | Rechtsbetrekking |
| 2 | Fase 2 | Ontvangst |
| 3 | Fase 3 | Ontvankelijkheid |
| 4 | Fase 4+5 | Behandeling en besluit |
| 5 | Fase 6 | Bekendmaking |
| 6 | Fase 7 | Betaling |
| 7 | Fase 8 | Ketenproces |
| 8 | Archiefwet | Archivering |

Below the stepper, a caption names the current phase — **Fase 6 · Bekendmaking**, say — followed by **in deelproces** and the subprocess's name when the task runs in a subprocess, and by **beslistermijn tot** and a date when the process has set a decision deadline.

**Bekijk proces →** opens the [process overview](#the-process-overview) at the task's own phase. Clicking a step on the stepper opens it at that phase instead.

### Processtappen

**Processtappen** lists what has happened in the case and what comes next. For a process drawn in lanes, the steps are grouped per role:

- **Lane groups.** Consecutive steps in the same lane form a group, headed by a chip for the lane and its name. The lane you work in — one whose tasks go to a role you hold — is marked **jouw rol**. A group that runs in a subprocess is tagged **deelproces**, with its phase.
- **Handovers.** Between groups, a line says where the work goes: `↓` and the next lane, `↓ daarna:` where the future steps begin, `↘ deelproces` and a name where a subprocess starts, and `↗ terug in hoofdproces ·` and a lane where the work returns.
- **Step states.** A finished step shows when it ended and **Afgerond**, or **Afgebroken** when it was cancelled rather than completed. A running step shows **Loopt nog**; your own task shows **Jouw taak — loopt nog**; a subprocess that is still running shows **Deelproces loopt**. Each step also carries its type: **GEBRUIKERSTAAK**, **SERVICETAAK**, **SCRIPT**, **BESLISSING**, **KEUZE** or **CALLACTIVITY**.
- **Decisions and documents.** A step that evaluates a decision table shows **DMN** and the table's name; a step that works with a document shows the document's name.
- **Choices already made.** A choice point that has been passed shows the branch the case took, written out in words — a condition such as `${eligible != true}` reads as `eligible ≠ true`.
- **Hierna.** After the current step, up to three steps show what comes next, marked **Hierna**. The look-ahead stops at the first choice point, because its outcome depends on work not done yet: it lists the branches instead — **Hierna · splitst:** followed by each branch. When a subprocess ends, the look-ahead continues in the process that called it.

By default only the two groups before the current one are shown. **▸ *n* eerdere stappen tonen** brings back the earlier ones; the list folds again when you select another task.

**Hele proces als swimlane bekijken →** at the foot opens the process overview.

For a process that is not drawn in lanes, **Processtappen** is a plain list of the steps the case has passed, each with its type, its start time and **Afgerond**, **Afgebroken** or **Loopt nog**.

The view draws the most recently deployed version of the process. A step the case ran in an older version, which the current model no longer has, is left out.

## The process overview

The overview shows the whole process as a swimlane, in a window over the inbox.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: the Caseworker process overview, with the full Awb stepper, the Hoofdproces and Deelproces breadcrumb, the legend and the swimlane scrolled to the task](../../assets/screenshots/ronl-business-api-caseworker-process-overlay.png)
  <figcaption>The process overview — the whole process as a swimlane, opened from a task</figcaption>
</figure>

- **The full stepper.** Along the top runs the Awb stepper at full size, where it marks phases and moves between them: picking a phase shows the part of the process it belongs to.
- **Main process and subprocess.** Where the process calls a subprocess, a breadcrumb — **Hoofdproces › Deelproces fase** and the phase — switches between the two. A subprocess in the swimlane also has an **open ↘** button, which opens it in the same window.
- **Title and legend.** The process name and key sit above the swimlane, beside **Processtappen & rollen — procesmodel (live)**. The legend reads **Afgerond**, **Loopt**, **Jouw taak**, **Jouw rol** — followed by the roles you hold in this process — **Automatisch (script / DMN)** and **Nog niet / niet doorlopen**.
- **Your task.** The swimlane scrolls to your task, which is labelled *jouw taak*, and the lanes you work in are highlighted.

**Sluiten**, **Esc** or a click beside the window closes it. While it is open, the keyboard stays inside it; when it closes, the keyboard returns to where it was.

The overview can also be opened with the command palette: with a task selected, press **⌘K** (or **Ctrl+K**) and choose **Proces van deze taak bekijken**. The command is offered only for a task whose process is drawn in lanes.

## Claiming and completing a task

Under **Acties**, an open task offers **Taak claimen**. Once claimed, the confirmation **Taak geclaimd.** appears and the task's form opens in its place. Fill it in and choose **Taak voltooien**; **Taak voltooid.** confirms it and the task leaves your list. If saving fails, **Opslaan mislukt.** says so and the form stays open.

## The assistant

**Vraag de assistent**, at the side of the board, opens the **Assistent** panel beside your work. Closing and reopening it keeps the conversation, and so does reloading the page within the same browser session. The panel can be widened or narrowed by dragging its edge.

## Which processes show the process view

The process view — lane groups and the overview — appears only for a process whose deployed BPMN model is drawn in lanes, with the user tasks inside them. **jouw rol** needs, in addition, that a lane's tasks are assigned to a role by name. The **Waar sta ik** stepper and the **Awb-fase** hint in the list need the model to mark its steps with their Awb phase; a task in a subprocess without markers of its own takes the phase of the step that called the subprocess. A process with lanes but no phase markers shows its steps per role without the stepper; a process without lanes shows the plain list. Whether a given task shows the view therefore depends on how its process is modelled, not on the task. How a model is marked up for this is described in [BPMN Design Criteria](../reference/bpmn-design-criteria.md).

---

For how earlier versions of the board worked, see [Caseworker Dashboard](../features/archive/caseworker-dashboard.md) and [Caseworker Dashboard (V2)](../features/archive/caseworker-dashboard-v2.md).
