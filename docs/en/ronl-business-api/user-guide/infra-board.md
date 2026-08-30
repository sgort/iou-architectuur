---
component: RONL Business API
---

# Infra-board

*portfolio · fases*

Infra-board is portfolio steering for infrastructure projects. It organises projects into phase swimlanes, from planning through delivery, with per-project status and RIP management.

On opening the board you see projects grouped by phase, with their status and RIP information, so the portfolio's progress is visible in one view.

<figure markdown style="width:100%; margin:0;">
  ![Screenshot: RONL Business API Infra-board showing phase swimlanes with per-project status](../../assets/screenshots/ronl-business-api-infra-board.png)
  <figcaption>Infra-board — portfolio steering for infrastructure projects</figcaption>
</figure>

## Signing a phase-exit approval

Some approval tasks are signed rather than merely ticked. Where a task carries a
signature requirement in its process model, the panel that normally shows a form
shows a **signing panel** instead — you sign the phase document without leaving
the board.

The flow, from a project leader's point of view:

1. **Claim the task.** An unclaimed task shows the claim button as usual.
2. **The signing panel replaces the form.** It prepares the document, then opens
   the signing ceremony in the panel itself.
3. **Sign.** The panel watches for completion on its own.
4. **The task completes.** The signed document and its evidence summary are
   archived to the project's eDOCS workspace, and the process moves on.

You do not complete the task by hand — it completes when the signature lands.

!!! note "If the panel looks stuck after you have signed"
    The panel polls for the result, and a signature can complete through either
    the platform's callback or a periodic sweep. If it has not resolved after a
    minute or so, reload the page: the status is read fresh, not held in the
    panel.

For how this works underneath — the signing platform, the environment locks, and
what happens if the callback never arrives — see
[ValidSign phase-approval signing](../developer/validsign-signing.md).

---

!!! note "Brief by design"
    This board is on the acceptance environment. The page covers what it is for
    and what you see; a full step-by-step guide follows when it reaches
    production. See [Getting Started](getting-started.md).
