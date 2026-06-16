# Defining a Task

A **task** is the container for one interpretation. It records who is doing the work and what
they are interpreting. This is step 1 of the workflow.

---

## Filling in the form

The task form has three fields, all required:

| Field | What to enter |
|---|---|
| **Editor** | The name of the person carrying out the interpretation |
| **Label** | A short title for the task |
| **Description** | A fuller explanation of what is being interpreted and why |

The **Continue** button stays disabled until all three fields are filled. Once they are, click
**Continue** to move to source collection.

---

## What happens behind the scenes

When you start a task, the editor creates a task with two stable identifiers:

- a **task IRI**, and
- an **interpretation IRI** linked to it.

These identifiers travel with the task through saving and loading, so a task you reopen from
TriplyDB keeps its identity rather than becoming a new one. You do not need to manage these
IRIs yourself — the editor handles them.

!!! tip "Reopening an existing task"
    If you want to continue earlier work rather than start fresh, skip this step and use the
    **load** banner (or the task retrieval panel) to open a saved task. Its editor, label, and
    description are restored automatically. See [Saving and loading](saving-and-loading.md).
