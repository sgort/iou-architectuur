# RONL Business API — documentation strategy redesign

**Date:** 2026-08-19
**Status:** awaiting review
**Scope:** restructure only. The overdue version sync (v3.9.1 → current) runs
separately afterwards.

> Placed at the repository root rather than under `docs/`, because `docs/` is the
> MkDocs source tree — a Markdown file there that is not in the `nav` produces a
> "not included in the nav configuration" warning on every build.

---

## Problem

The RONL Business API is developed in short cycles, in close collaboration with a
diverse group of users. Features move faster than User Guides can be written, and
keeping the guides current has proven to cost more effort than it returns. The
home page currently carries a callout apologising for the resulting gap: only the
Developer perspective was reconciled during the v3.0.8 → v3.9.1 pass, leaving
Features, Reference and User Guides behind.

The 12 existing guides now describe an application around **v2.9.1** (the highest
version they reference), against a documented version of **v3.9.1**.

The strategy changes rather than the effort increasing: document RBA to a depth
its cadence can sustain, and say so as policy instead of as an apology.

---

## Decisions

| # | Question | Decision |
|---|---|---|
| 1 | Scope of the new ACC guides | The four employee boards only. Citizen journeys are archived. |
| 2 | ACC-brief vs PROD-full mechanism | **Temporal.** One section; depth follows maturity. Brief while on ACC, expanded when a board reaches PROD. |
| 3 | Archive mechanics | Move to `user-guide/archive/`, nav subgroup, standard banner on each page. |
| 4 | Home page | Lead sentence + comparison table, then Documentation Status promoted directly beneath it. |
| 5 | This pass | Restructure only; version sync separately. |
| 6 | Public site | Its own brief page **and** covered in the intro. |
| 7 | Environments | All of RBA is ACC for now — every page is written at ACC depth. |
| 8 | Testhandleidingen | Not archived. Separate **Test guides** subgroup, kept current. |
| 9 | `references/` naming | Renamed to `reference/` in this pass, matching every other component. |

---

## Design

### 1. User Guides structure

```
docs/en/ronl-business-api/user-guide/
├── getting-started.md                  ← intro: both environments
├── caseworker.md                       ← board
├── pa-cockpit.md                       ← board
├── infra-board.md                      ← board
├── woo-dashboard.md                    ← board
├── public-site.md                      ← public site (ACC-only)
├── test-guides/                        ← kept current
│   ├── pa-cockpit-gebruikershandleiding.md
│   ├── dossierbeheer-testhandleiding.md
│   └── capaciteitsclaim-testhandleiding.md
└── archive/                            ← frozen
    ├── adding-municipality.md
    ├── assessing-income-support-schemes.md
    ├── caseworker-workflow.md
    ├── hr-onboarding.md
    ├── login-flow.md
    ├── rip-phase1-workflow.md
    ├── submitting-application.md
    ├── timeline-navigation.md
    └── zorgtoeslag-cross-org-journey.md
```

Mirrored under `docs/nl/`. `assessing-income-support-schemes.html` (a sibling
HTML artifact of the same-named guide) moves with it.

Nav shape — one **User Guides** group:

```
- User Guides:
  - Getting Started: .../getting-started.md
  - Caseworker: .../caseworker.md
  - PA-Cockpit: .../pa-cockpit.md
  - Infra-board: .../infra-board.md
  - Woo-dashboard: .../woo-dashboard.md
  - Public Site: .../public-site.md
  - Test guides:
    - ... (3 pages)
  - Archive:
    - ... (9 pages)
```

### 2. The six current pages

**Intro** — both environments in one place: the werkomgeving (login via
medewerkersaccount, four boards, role-based visibility) and the public knowledge
base (no login, no account, no personal data). Embeds both screenshots. Links out
to each of the five detail pages.

**Four board pages**, deliberately short — roughly half a screen each:

- what the board is for, and who uses it
- what you see on opening it
- a link to the matching Features page for depth
- a standing note that the full guide follows when the board reaches PROD

Content per the landing page: Caseworker (*werk · taken* — personal work queue
for case handlers, with a built-in assistant), PA-Cockpit (*kompas · issues* —
administrative overview weighing priority and momentum), Infra-board
(*portfolio · fases* — phase swimlanes and RIP management for infrastructure
projects), Woo-dashboard (*woo · compliance* — Wet open overheid compliance,
lead times and active publication).

**Public site page** — the five combined-search sources (Announcements, News,
Products & Services, Rule catalogue, Process library), plus Data dictionary and
Provenance, the NL/EN toggle, the "Staff login" route across to the
werkomgeving, and the accessibility statement (WCAG 2.1 AA) and Open data & API
links. States plainly that it publishes public information only, processes no
personal data and needs no login. Explicitly flagged **ACC-only**
(`acc.publiek.open-regels.nl`, v2026.08.19), unlike the boards.

### 3. Archive banner

One admonition at the top of each of the nine archived pages:

> !!! warning "Archived — not maintained"
>     This guide is kept for reference and is no longer updated. It describes the
>     application around **v2.9.1**; the current documented version is **v3.9.1**.
>     For current documentation see [Getting Started](../getting-started.md).

The version claim is anchored to what the guides actually reference, not to a
reconciliation date that cannot be evidenced.

### 4. Home page

Order becomes:

1. Title and intro
2. **`## 📘 How this documentation is maintained`** — lead sentence + table
3. **`## Documentation Status`** — the existing `#doc-status` block, moved up
4. `## 🆕 What's New` — unchanged
5. everything below — unchanged

The existing RBA callout is **removed**: its premise ("not yet reflected") is
replaced by the new section stating the depth as deliberate policy.

Table content as approved: RBA — short-cycle, co-designed — landing plus
per-board summaries on ACC, full guides on PROD; CPSV Editor, Linked Data
Explorer and Norm Editor — release-tagged — full; CPRMV API — spec-driven — full.

### 5. Skill changes (`iou-document-patch`)

So the structure survives future syncs:

- Component map records RBA's ACC-brief / PROD-full convention.
- **Hard rule: never edit `**/user-guide/archive/**`.** A sync must not update,
  reword or version-stamp an archived page.
- Test-guide subgroup is maintained, not archived.
- Promotion of a board to PROD is the trigger to expand its page.
- Drop the note about RBA's odd `references/` path — it is renamed in this pass, so every component now uses `reference/`.

### 6. `references/` → `reference/`

RBA is the only component using `references/`; every other uses `reference/`.
Renamed in this pass so a path that works elsewhere stops failing here.

| What | Count |
|---|---|
| Files moved | 10 EN + 10 NL = 20 |
| `mkdocs.yml` nav entries | 10 |
| Inbound link occurrences | 32, across 30 files |

Two of those inbound links come from **Linked Data Explorer** pages
(`features/bpmn-modeler.md`, `features/form-editor.md`), so the rename reaches
outside RBA's own tree — a good reason to do it in one deliberate pass rather
than discovering it piecemeal later.

!!! warning "This changes published URLs"
    `/ronl-business-api/references/<page>/` becomes
    `/ronl-business-api/reference/<page>/`. Any external bookmark or inbound link
    to the old path breaks. Accepted deliberately: the inconsistency is a
    standing trap for every future sync, and the cost only grows with more pages.

Verification is mechanical — after the rename, zero occurrences of
`ronl-business-api/references/` may remain anywhere in `docs/` or `mkdocs.yml`,
and `mkdocs build` must report no broken links.

### 7. i18n

Per the standing rule: EN substantive, NL placeholders for the six new pages.
Archived and test-guide pages keep whatever they are today — the four real Dutch
translations stay real, they simply move. `component: RONL Business API` front
matter goes on every page this pass creates or edits.

### 8. Screenshots

Two existing files are renamed to match the convention (lowercase, hyphenated,
component-prefixed):

- `RBA-LandingPage.png` → `ronl-business-api-landing-page.png`
- `RBA-public-site.png` → `ronl-business-api-public-site.png`

The public-site capture was replaced with the **English** version of the
interface on 2026-08-19, so the page uses English source names throughout. The
werkomgeving capture is still Dutch — the boards may not offer an English
interface. Not blocking; worth an English re-shot later if one exists, for
consistency on an English page.

Manifest gains four **NEW** rows — one screenshot per board — each with its
`<figure>` in place. The boards require a login, so capture is a human step.

---

## Out of scope

- The version sync from v3.9.1 (runs separately, via the skill).
- Features / Developer Docs / References content — unchanged in this pass; they
  keep the usual per-component pattern.
- Rewriting archived content.

---

## Verification

- `mkdocs build` clean: no broken links, no missing images, no "not included in
  the nav" warnings.
- Every moved page reachable from the nav; no orphaned files under `docs/`.
- Each of the four manifest rows embedded in at least one page.
- Zero remaining occurrences of `ronl-business-api/references/` in `docs/` or
  `mkdocs.yml`.
- Metadata header renders on every touched page, EN and NL.

---

## Open items

None blocking. Screenshot capture for the four boards is a human step and is
tracked in the manifest rather than blocking this pass.
