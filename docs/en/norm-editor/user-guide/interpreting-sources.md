# Interpreting Sources

Step 3 is where the real work happens. The screen is split: **source text on the left**,
**frames on the right**. You highlight text, turn it into frames, and connect those frames
into acts and claim-duties.

---

## The layout

```
┌───────────────────────────┬──────────────────────────────────────┐
│  Sources                  │  Frames            [List | Network]   │
│  (selected sentences,     │  Add: Fact  Act  Claim-duty           │
│   with coloured           │  ┌──────────────────────────────────┐ │
│   underlines)             │  │ Frame editor panel               │ │
│                           │  │  (opens when a frame is selected) │ │
└───────────────────────────┴──────────────────────────────────────┘
```

The source panel can be collapsed with the arrow button between the two columns to give the
frames more room. The frames panel can be shown as a [list or a network](../features/visualisation.md).

---

## Creating a fact from text

1. Select a phrase in the source text.
2. A small panel appears next to your selection.
3. Click **Fact** (or **Act** / **Claim-duty**).
4. The frame is created, the text is underlined in the frame's colour, and the frame opens in
   the editor panel where you can give it a description, set subtypes, and add comments.

If you decide against it, click **Cancel** in the panel to discard the selection.

---

## Building an act

An act ties facts together into "who may do what". To build one:

1. Click **Act** to create an empty act. Its editor panel shows the roles: **action**,
   **actor**, **object**, **recipient**, plus **precondition**, **creates**, and
   **terminates**.
2. Click the **pencil** next to a role to make it active.
3. Fill the role in one of two ways:
    - **Highlight text** in the source — a fact of the correct subtype is created and dropped
      straight into the role.
    - **Click an existing fact chip** to reuse a fact already in the interpretation.
4. Repeat for the other roles.

As you fill the roles, the act's **label updates automatically** to
`[action] [object] [actor] [recipient]`. Unfilled roles show placeholders such as `<actor>`.
You can turn off automatic labelling and type your own label if you prefer.

To remove a fact from a role, click the small **×** next to its chip.

---

## Building a claim-duty

A claim-duty works the same way, with three roles:

- **Duty** — the obligation,
- **Claimant** — the party that can claim it, and
- **Holder** — the party that bears it.

Activate a role with its pencil, then fill it from the source or from an existing frame.

---

## Preconditions and fact subdivisions

An act's **precondition** and a fact's **subdivision** are
[boolean constructs](../features/boolean-constructs.md) — trees of **AND / OR / NOT**. In the
construct's tree view you can:

- add frames (by highlighting text or clicking existing chips),
- **subdivide** a node to nest conditions,
- switch a node between **AND** and **OR**,
- **negate** a node, and
- remove operands.

This is how you capture conditions such as *(resident OR citizen) AND NOT bankrupt*.

---

## Adding to an existing frame

If a phrase belongs to a frame you have already made, highlight it and choose **Add to
existing frame** in the panel, then click the target frame's chip. The new annotation is
attached to that frame, so one frame can be anchored to several places in the text.

---

## Reviewing and tidying up

- **Filter** frames by label using the search box, or by type/subtype in the network view.
- Click any chip to reopen its frame; several frames can be open in the editor at once, listed
  down the side of the panel.
- **Delete** a frame to remove it everywhere — every role and precondition that referenced it
  is cleaned up automatically, along with its annotations in the text.
- Use **scroll to source** to jump from a frame back to the sentence it came from.

When you are happy, save your work — see [Saving and loading](saving-and-loading.md).
