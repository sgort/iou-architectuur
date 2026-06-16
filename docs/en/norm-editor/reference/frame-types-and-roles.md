# Frame Types & Roles

A reference for the frame catalogue: the types, their subtypes, the roles each relation
exposes, and the visual encoding used throughout the editor.

---

## Frame types

| Type id | Label | Class |
|---|---|---|
| `fact` | Fact | fact |
| `act` | Act | relation |
| `claim_duty` | Claim-duty | relation |

## Fact subtypes

A fact may carry **several** of these at once.

| Subtype id | Label |
|---|---|
| `agent` | Agent |
| `action` | Action |
| `object` | Object |
| `duty` | Duty |
| `condition` | Condition |

---

## Roles and the subtypes they accept

### Act

| Role | Cardinality | Accepts fact subtype(s) |
|---|---|---|
| `action` | one | action |
| `actor` | one | agent |
| `object` | one | object |
| `recipient` | one | agent |
| `precondition` | one tree | (boolean construct over facts) |
| `creates` | many | agent, action, object |
| `terminates` | many | agent, action, object |

The act label is auto-generated as `[action] [object] [actor] [recipient]`, with placeholders
`<action>`, `<obj>`, `<actor>`, `<rec>` for unfilled roles. Automatic labelling can be turned
off per act.

### Claim-duty

| Role | Cardinality | Accepts fact subtype(s) |
|---|---|---|
| `duty` | one | duty |
| `claimant` | one | agent |
| `holder` | one | agent |

When a role accepts exactly one subtype, the editor assigns that subtype to a fact created
into it from the source.

---

## Visual encoding

Each type/subtype has a consistent icon and colour across the list, editor, underlines, and
network view.

| Frame / subtype | Icon (MDI) | Underline colour | Network node colour |
|---|---|---|---|
| Fact | — | `#1976D2` | `#b3d9ff` |
| Agent | `mdi-account-switch` | `#F2C037` | `#ffdd80` |
| Action | `mdi-gesture-tap` | `#26A69A` | `#80fff3` |
| Object | `mdi-account-arrow-left-outline` | `#9C27B0` | `#f4b3ff` |
| Duty | `mdi-exclamation` | `#31CCEC` | `#80e9ff` |
| Condition | `mdi-circle-small` | `#21BA45` | `#a8ffbd` |
| Act | `mdi-autorenew` | `#311b92` | `#c0b3ff` |
| Claim-duty | `mdi-square` | `#311b92` | `#c0b3ff` |
| Multiple subtypes | — | `#c0ca33` | `#f9ffa1` |
| NLP indicator | `mdi-text-recognition` | — | — |

### Network node sizes

| Node | Size |
|---|---|
| Act / Claim-duty | 10 |
| Fact | 5 |
| Anonymous (boolean construct join-point) | 3 |

A fact with **more than one** subtype uses the *multiple* colour rather than any single
subtype colour.
