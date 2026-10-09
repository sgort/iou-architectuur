---
component: Norm Editor
---

# Interpreting Sources

The **Interpret sources** tab is where the real work happens. The screen has three panes side
by side: the **source text**, the **frames** in the interpretation, and the **frame editor**.
You highlight text, turn it into frames, and connect those frames into acts and claim-duties.

---

## The layout

A status bar runs across the top; the three panes fill the height below it:

```
┌──────────────────────────────────────────────────────────────────────────┐
│ Status bar: what you can do next  (orange while choosing, with Cancel)   │
├─────────────────────┬────────────────────────┬───────────────────────────┤
│ Source text      «  │ Frames 12 [≡|net] +New │ [act ×] [fact ×] [ ... ]  │
│ (a tab per document │ [Filter on name     ]  │                           │
│  when there are     │ Act                    │ Form of the frame in the  │
│  several)           │ Claim-duty             │ active tab: name, roles,  │
│                     │ Fact                   │ conditions, comments,     │
│ selected sentences, │   Agent / Action /     │ delete and close          │
│ with coloured       │   Object / Duty /      │                           │
│ underlines          │   Condition            │                           │
└─────────────────────┴────────────────────────┴───────────────────────────┘
```

- **Status bar** — one line that tells you what you can do next, for example *Select a passage
  in the source text to create a frame, or click a frame to open it.* While you are choosing a
  fact for a role, a condition, or a frame to attach text to, it turns orange, names what you
  are choosing, and offers **Cancel**.
- **Source text** — the selected sentences of the displayed document, with a coloured underline
  for every annotation. With several sources, each document has its own tab; with one, its
  title appears under the pane heading. The **«** button (*Hide source text*) folds the pane
  into a narrow rail, and **»** (*Show source text*) brings it back. When no sentences are
  selected yet, the pane offers a **Collect sources** button.
- **Frames** — every frame in the interpretation, grouped by type (Act, Claim-duty, Fact) with a
  count per group; facts with a subtype are grouped further under Agent, Action, Object, Duty,
  and Condition. Typing two or more characters in **Filter on name** narrows the list. Two icon
  buttons switch between *Show as list* and *Show as network*; the pane widens in network mode
  (see [Frame visualisation](../features/visualisation.md)). The orange **New** button adds an
  empty Fact, Act, or Claim-duty.
- **Frame editor** — the frames you have opened, as browser-style tabs. Each tab shows the
  frame's colour and short name (or *Untitled act*, *Untitled fact*, and so on); its **×**
  closes the tab and keeps your changes. With nothing open, the pane shows a three-step guide
  to interpreting a source.

On narrow screens the panes stack on top of each other and the page scrolls.

---

## Creating a fact from text

1. Select a phrase in the source text.
2. A panel appears next to your selection, quoting the **Selected text**.
3. Under **Create a new frame**, click **Fact** (or **Act** / **Claim-duty**).
4. The frame is created, the text is underlined in the frame's colour, and the frame opens in
   the editor. A new fact takes the selected text as its short name; you can add a full name,
   choose its **Subtypes** (*What kind of fact is this? Choose one or more.*), and add comments.

If you decide against it, click **Cancel** in the panel to discard the selection.

---

## Building an act

An act ties facts together into "who may do what". Its form has three sections: **Roles**
(Action, Actor, Object, Recipient), **Precondition** (*What must be true before the act can be
performed.*), and **Postcondition** (Creates, Terminates). To build one:

1. Create the act from a selection in the source, or from scratch with **New → Act**.
2. Click **Select** next to a role. The role turns orange, shows *Select text in the source, or
   click a fact in the Frames list*, and its button becomes **Cancel**.
3. Fill the role in one of two ways:
    - **Highlight text** in the source — a fact is created and dropped straight into the role.
      Where the role accepts a single subtype (for example *Action*), the new fact gets it.
    - **Click an existing fact** in the Frames list to reuse it. While you are choosing, the
      facts you can pick are highlighted; other frames cannot be picked.
4. Repeat for the other roles. A filled role's button reads **Change**. **Creates** and
   **Terminates** can hold several facts and use **Add**. A role with nothing in it shows
   *Not set*.

The act's **Short name** is generated from its roles as `[action] [object] [actor] [recipient]`,
with placeholders such as `<actor>` for roles that are still empty; the field's hint reads
*Generated from the roles below until you type your own name*. Typing your own name stops the
generation; clearing the field starts it again.

To remove a fact from a role, click the small **×** next to its chip. Clicking the chip itself
opens that fact in the editor.

---

## Building a claim-duty

A claim-duty works the same way, with three roles:

- **Duty** — the obligation,
- **Claimant** — the party that can claim it, and
- **Duty holder** — the party that bears it.

Click **Select** next to a role, then fill it from the source or from an existing fact. A
claim-duty's short name is not generated; you type it yourself.

---

## Preconditions and fact subdivisions

An act's **Precondition** and a fact's **Subdivision** are
[boolean constructs](../features/boolean-constructs.md) — trees of conditions. In the
construct's tree you can:

- click an empty node to choose its condition — the status bar reads *Choosing a condition* —
  then highlight text in the source and pick a frame type, or click an existing fact in the
  Frames list,
- **subdivide** a node to nest conditions beneath it,
- use **Add child** to add another operand to a node that joins others,
- pick the function that joins a node's children (**AND** or **OR**) from *Pick a function*;
  picking **NOT** marks the node as negated, and
- remove a frame from a node, or remove the node itself, with its **×**.

This is how you capture conditions such as *(resident OR citizen) AND NOT bankrupt*.

---

## Adding to an existing frame

If a phrase belongs to a frame you have already made, highlight it and choose **Add to
existing frame** in the panel. The status bar asks you to click a frame in the **Frames** list;
the annotation is attached to the frame you click, so one frame can be anchored to several
places in the text.

---

## Reviewing and tidying up

- **Filter** frames by name in the list, or by frame type in the network view.
- Click any frame in the list, or a chip in a role, to open it. Several frames can be open at
  once, each in its own editor tab; open frames carry a pencil icon in the list. **Close** at
  the bottom of the form closes the tab — changes are saved as you type.
- **Show in source** at the top of the form brings the sentence the frame came from into view,
  switching to the right document first. It is disabled for a frame that is not linked to
  source text yet.
- **Delete** at the bottom of the form asks for confirmation (*Delete this act?* with **Keep**
  and **Delete**). Deleting a frame removes it from the interpretation together with its
  annotations in the text, and clears it from the roles, the *Creates* lists, the
  preconditions, and the subdivisions that referenced it. A fact listed under an act's
  *Terminates* stays listed there; remove it from that list by hand.
- The frame's identifier is shown at the bottom of the form, with a button to copy it.

When you are happy, save your work — see [Saving and loading](saving-and-loading.md).
