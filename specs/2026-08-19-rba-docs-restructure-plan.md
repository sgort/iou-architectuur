# RBA Documentation Restructure — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the RONL Business API documentation so its depth matches its short development cycle — archive the stale User Guides, publish six brief ACC-level pages, promote Documentation Status on the home page, and align `references/` with every other component.

**Architecture:** Pure documentation and configuration change in the MkDocs site. No application code. Each task ends with a `mkdocs build` that must be warning-free plus a targeted `grep` proving the change landed. Files move with `git mv` so history follows them.

**Tech Stack:** MkDocs 1.6.1 + Material, `mkdocs-static-i18n` (folder structure, EN default), `git-revision-date-localized`, the repo's `hooks/repo_versions.py` metadata header.

**Spec:** `specs/2026-08-19-rba-docs-strategy-design.md`

## Global Constraints

- Build with the repo venv: `venv/Scripts/mkdocs.exe build`. **Never filter its output through `grep` alone** — a fatal config error can hide behind a warning filter. Read the tail and check the exit code.
- Every page created or edited gets YAML front matter `component: RONL Business API` as its first three lines.
- EN pages carry substantive content; NL counterparts are placeholders using the house pattern (`# Title`, *Documentatie in ontwikkeling* admonition, `**Status:** Concept`, `**Engelstalige bron:**`, mirrored empty `##` headers).
- Screenshots live in `docs/assets/screenshots/`, referenced from pages as `../../assets/screenshots/<file>.png` inside a `<figure markdown>` block.
- No file may be added under `docs/` without a matching `mkdocs.yml` nav entry — a loose file triggers "not included in the nav configuration".
- Commit messages carry **no** `Co-Authored-By` and **no** `Claude-Session` trailer.
- Ask the user before every `git commit`. The commit steps below are written out, but each still requires a fresh go-ahead.
- Existing indentation in `mkdocs.yml` for the RBA block is **4 spaces** for group keys and **6 spaces** for leaf entries. Match it exactly — a mismatched anchor silently eats indentation and breaks the YAML.

---

### Task 1: Rename `references/` to `reference/`

Aligns RBA with every other component. 20 files, 10 nav entries, 32 link occurrences across 30 files — two of them from Linked Data Explorer pages.

**Files:**
- Move: `docs/en/ronl-business-api/references/` → `docs/en/ronl-business-api/reference/` (10 files)
- Move: `docs/nl/ronl-business-api/references/` → `docs/nl/ronl-business-api/reference/` (10 files)
- Modify: `mkdocs.yml` (10 nav entries)
- Modify: 30 files containing inbound links

- [ ] **Step 1: Record the baseline that must reach zero**

```bash
grep -rn "ronl-business-api/references/\|\.\./references/\|\.\./\.\./references/" docs/ mkdocs.yml | wc -l
```

Expected: a non-zero count. Note it — this is the number that must become `0`.

- [ ] **Step 2: Move both folders with history**

```bash
git mv docs/en/ronl-business-api/references docs/en/ronl-business-api/reference
git mv docs/nl/ronl-business-api/references docs/nl/ronl-business-api/reference
```

- [ ] **Step 3: Rewrite every inbound link and nav entry**

```bash
grep -rl "ronl-business-api/references/\|\.\./references/\|\.\./\.\./references/" docs/ mkdocs.yml \
  | while read f; do
      sed -i 's|ronl-business-api/references/|ronl-business-api/reference/|g; s|\.\./references/|../reference/|g; s|\.\./\.\./references/|../../reference/|g' "$f"
    done
```

- [ ] **Step 4: Verify zero occurrences remain**

```bash
grep -rn "ronl-business-api/references/\|\.\./references/\|\.\./\.\./references/" docs/ mkdocs.yml | wc -l
```

Expected: `0`.

- [ ] **Step 5: Build and read the whole tail**

```bash
venv/Scripts/mkdocs.exe build 2>&1 | tail -15
```

Expected: exit 0, no `WARNING` about unrecognised links, no "not included in the nav".

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "docs(ronl-business-api): rename references/ to reference/ to match every other component"
```

---

### Task 2: Rename the two RBA screenshots to the naming convention

Every other screenshot is lowercase, hyphenated and component-prefixed. Later tasks reference these files, so this comes first.

**Files:**
- Move: `docs/assets/screenshots/RBA-LandingPage.png` → `ronl-business-api-landing-page.png`
- Move: `docs/assets/screenshots/RBA-public-site.png` → `ronl-business-api-public-site.png`

- [ ] **Step 1: Confirm nothing references the old names yet**

```bash
grep -rn "RBA-LandingPage\|RBA-public-site" docs/ screenshot-manifest/ | wc -l
```

Expected: `0` (the files are new and not yet embedded).

- [ ] **Step 2: Rename**

```bash
cd docs/assets/screenshots
mv RBA-LandingPage.png ronl-business-api-landing-page.png
mv RBA-public-site.png ronl-business-api-public-site.png
cd ../../..
```

- [ ] **Step 3: Verify the convention holds**

```bash
ls docs/assets/screenshots/ | grep "^ronl-business-api-"
```

Expected: both new names listed; no capitals, no `RBA-` prefix anywhere.

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "docs: rename RBA screenshots to the lowercase component-prefixed convention"
```

---

### Task 3: Archive the nine superseded User Guides

**Files:**
- Create: `docs/en/ronl-business-api/user-guide/archive/` and the NL mirror
- Move: 9 EN `.md`, 9 NL `.md`, and `assessing-income-support-schemes.html`
- Modify: `mkdocs.yml` (Archive nav subgroup)

**Interfaces:**
- Produces: the path `docs/{en,nl}/ronl-business-api/user-guide/archive/`, which Task 10 writes into the skill as never-edit.

- [ ] **Step 1: Create the folders and move the nine guides plus the HTML sibling**

```bash
mkdir -p docs/en/ronl-business-api/user-guide/archive docs/nl/ronl-business-api/user-guide/archive
for f in adding-municipality assessing-income-support-schemes caseworker-workflow \
         hr-onboarding login-flow rip-phase1-workflow submitting-application \
         timeline-navigation zorgtoeslag-cross-org-journey; do
  git mv "docs/en/ronl-business-api/user-guide/$f.md" "docs/en/ronl-business-api/user-guide/archive/$f.md"
  git mv "docs/nl/ronl-business-api/user-guide/$f.md" "docs/nl/ronl-business-api/user-guide/archive/$f.md"
done
git mv docs/en/ronl-business-api/user-guide/assessing-income-support-schemes.html \
       docs/en/ronl-business-api/user-guide/archive/assessing-income-support-schemes.html
```

- [ ] **Step 2: Insert the archive banner at the top of all 18 pages**

The banner goes immediately after the front matter (or at the very top where there is none), before the `# Heading`. Exact EN text:

```markdown
!!! warning "Archived — not maintained"
    This guide is kept for reference and is no longer updated. It describes the
    application around **v2.9.1**; the current documented version is **v3.9.1**.
    For current documentation see [Getting Started](../getting-started.md).
```

Exact NL text:

```markdown
!!! warning "Gearchiveerd — niet onderhouden"
    Deze handleiding blijft beschikbaar ter referentie en wordt niet meer
    bijgewerkt. Zij beschrijft de applicatie rond **v2.9.1**; de huidige
    gedocumenteerde versie is **v3.9.1**. Zie
    [Getting Started](../getting-started.md) voor actuele documentatie.
```

Also prepend the front matter `---\ncomponent: RONL Business API\n---` to each of the 18 pages if absent.

- [ ] **Step 3: Verify every archived page carries the banner**

```bash
grep -L "Archived — not maintained" docs/en/ronl-business-api/user-guide/archive/*.md
grep -L "Gearchiveerd — niet onderhouden" docs/nl/ronl-business-api/user-guide/archive/*.md
```

Expected: no output from either (every file matched).

- [ ] **Step 4: Add the Archive nav subgroup**

Under `- User Guides:` in `mkdocs.yml`, replace the nine moved leaf entries with a nested group. Leaf entries use 6 spaces; the nested group's own leaves use 10. Entries, in this order: Logging In — Citizen & Caseworker; Submitting an Application; Zorgtoeslag via Commercial Org; Using Timeline Navigation; Caseworker Workflow; HR Onboarding; RIP Phase 1 Workflow; Adding a Municipality; Multiple interacting rules example — each pointing at `ronl-business-api/user-guide/archive/<file>.md`.

Note two of the current entries carry a stray `en/` path prefix
(`en/ronl-business-api/user-guide/zorgtoeslag-cross-org-journey.md`). Drop the
prefix while moving them — it is inconsistent with every sibling.

- [ ] **Step 5: Build and read the whole tail**

```bash
venv/Scripts/mkdocs.exe build 2>&1 | tail -15
```

Expected: exit 0 and no "not included in the nav configuration". The banner's
`../getting-started.md` target does not exist yet, so expect **one warning per
archived page about that single missing target** (up to 18, EN + NL) — they all
clear in Task 5. Record the exact count you see; nothing *else* may warn.

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "docs(ronl-business-api): archive nine superseded user guides behind an archived banner"
```

---

### Task 4: Move the three Testhandleidingen into a Test guides subgroup

These are live test scripts for the user group, not stale guides — they stay current and must not read as abandoned.

**Files:**
- Move: 3 EN + 3 NL into `user-guide/test-guides/`
- Modify: `mkdocs.yml`

- [ ] **Step 1: Move them**

```bash
mkdir -p docs/en/ronl-business-api/user-guide/test-guides docs/nl/ronl-business-api/user-guide/test-guides
for f in pa-cockpit-gebruikershandleiding dossierbeheer-testhandleiding capaciteitsclaim-testhandleiding; do
  git mv "docs/en/ronl-business-api/user-guide/$f.md" "docs/en/ronl-business-api/user-guide/test-guides/$f.md"
  git mv "docs/nl/ronl-business-api/user-guide/$f.md" "docs/nl/ronl-business-api/user-guide/test-guides/$f.md"
done
```

- [ ] **Step 2: Confirm no archive banner leaked onto them**

```bash
grep -l "Archived — not maintained\|Gearchiveerd" docs/*/ronl-business-api/user-guide/test-guides/*.md
```

Expected: no output. These pages are current.

- [ ] **Step 3: Add the Test guides nav subgroup**

Replace the three moved leaf entries under `- User Guides:` with a nested `- Test guides:` group holding: PA-Cockpit Testen; Dossierbeheer Testhandleiding; Capaciteitsclaim Testhandleiding — each pointing at `ronl-business-api/user-guide/test-guides/<file>.md`. Place it above the Archive group.

- [ ] **Step 4: Build**

```bash
venv/Scripts/mkdocs.exe build 2>&1 | tail -15
```

Expected: exit 0; still only the 18 `getting-started.md` warnings from Task 3.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "docs(ronl-business-api): group the Testhandleidingen under Test guides, kept current"
```

---

### Task 5: Write the Getting Started page

Covers both environments and clears the 18 dangling banner links.

**Files:**
- Create: `docs/en/ronl-business-api/user-guide/getting-started.md`
- Create: `docs/nl/ronl-business-api/user-guide/getting-started.md` (placeholder)
- Modify: `mkdocs.yml`

**Interfaces:**
- Produces: `user-guide/getting-started.md`, the link target every archived page's banner points at, and the hub linking to the five detail pages created in Tasks 6–7.

- [ ] **Step 1: Write the EN page**

Front matter `component: RONL Business API`, then `# Getting Started`, then content covering:

- One paragraph framing RBA as two environments: the **werkomgeving** (sign in with a medewerkersaccount; four boards; which boards you see depends on your role and authorisations) and the **public knowledge base** (no login, no account, no personal data).
- A `<figure markdown>` embedding `../../assets/screenshots/ronl-business-api-landing-page.png` with a caption naming the four boards.
- A table of the four boards — Caseworker (*werk · taken*), PA-Cockpit (*kompas · issues*), Infra-board (*portfolio · fases*), Woo-dashboard (*woo · compliance*) — each linking to its page from Task 6.
- A short public-site paragraph with a `<figure markdown>` embedding `../../assets/screenshots/ronl-business-api-public-site.png`, linking to `public-site.md`, and stating it is **ACC-only** at `acc.publiek.open-regels.nl`.
- A closing admonition:

```markdown
!!! info "Documentation depth follows release maturity"
    The RONL Business API is developed in short cycles with a diverse user
    group. While a board is on the acceptance environment it is documented at
    this level — what it is for and what you see. Full step-by-step guides
    follow when a board reaches production. Guides describing earlier versions
    are kept under [Archive](archive/login-flow.md).
```

- [ ] **Step 2: Write the NL placeholder**

House pattern, mirroring the EN `##` headers, `**Engelstalige bron:** ronl-business-api/user-guide/getting-started.md`.

- [ ] **Step 3: Add both nav entries**

`- Getting Started: ronl-business-api/user-guide/getting-started.md` as the **first** entry under `- User Guides:`.

- [ ] **Step 4: Build — the 18 warnings must now be gone**

```bash
venv/Scripts/mkdocs.exe build 2>&1 | tail -15
```

Expected: exit 0 and **zero** warnings about `getting-started.md`. The two screenshot references resolve, because Task 2 renamed the files.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "docs(ronl-business-api): add Getting Started covering the werkomgeving and public site"
```

---

### Task 6: Write the four board pages

**Files:**
- Create: `caseworker.md`, `pa-cockpit.md`, `infra-board.md`, `woo-dashboard.md` under `docs/en/ronl-business-api/user-guide/`
- Create: the four NL placeholders
- Modify: `mkdocs.yml`

**Interfaces:**
- Consumes: `getting-started.md` from Task 5 (each board page links back to it).
- Produces: the four page paths that Task 5's board table links to, and the four screenshot slots Task 9 records in the manifest.

Each EN page follows the same shape: front matter; `# <Board>`; what it is for and who uses it; what you see on opening it; a `<figure markdown>` for its screenshot; and the shared closing note. Per-board content:

- **Caseworker** — `werk · taken`. Personal work queue for case handlers: tasks, claims and deadlines per case, with a built-in assistant for quick assessment. Cross-links to [Caseworker Dashboard](../features/caseworker-dashboard.md) and [Caseworker Dashboard (V2)](../features/caseworker-dashboard-v2.md). Figure: `../../assets/screenshots/ronl-business-api-caseworker-board.png`.
- **PA-Cockpit** — `kompas · issues`. Administrative overview of dossiers and issues: a compass weighing priority and momentum so the executive can steer in time. Figure: `../../assets/screenshots/ronl-business-api-pa-cockpit-board.png`.
- **Infra-board** — `portfolio · fases`. Portfolio steering for infrastructure projects: phase swimlanes, per-project status and RIP management, from planning through delivery. Figure: `../../assets/screenshots/ronl-business-api-infra-board.png`.
- **Woo-dashboard** — `woo · compliance`. Steering on the Wet open overheid: compliance, lead times, process bottlenecks and active publication, with traffic lights and a "Woo in cijfers" benchmark. Figure: `../../assets/screenshots/ronl-business-api-woo-dashboard-board.png`.

**Only Caseworker gets Features cross-links** — PA-Cockpit, Infra-board and Woo-dashboard have no Features page. Do not invent links to pages that do not exist.

Shared closing note on all four:

```markdown
!!! note "Brief by design"
    This board is on the acceptance environment. The page covers what it is for
    and what you see; a full step-by-step guide follows when it reaches
    production. See [Getting Started](getting-started.md).
```

- [ ] **Step 1: Write the four EN pages** using the content above.

- [ ] **Step 2: Write the four NL placeholders** in the house pattern.

- [ ] **Step 3: Add the four nav entries** after Getting Started, in landing-page order: Caseworker, PA-Cockpit, Infra-board, Woo-dashboard.

- [ ] **Step 4: Build**

```bash
venv/Scripts/mkdocs.exe build 2>&1 | tail -20
```

Expected: exit 0. **Exactly four image warnings** — the four board screenshots, which do not exist yet and are captured by a human via Task 9's manifest. No `.md` link warnings at all; a link warning here means a cross-link points somewhere real pages do not go.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "docs(ronl-business-api): add brief ACC-level pages for the four boards"
```

---

### Task 7: Write the public site page

**Files:**
- Create: `docs/en/ronl-business-api/user-guide/public-site.md`
- Create: the NL placeholder
- Modify: `mkdocs.yml`

- [ ] **Step 1: Write the EN page**

Front matter; `# Public Site`; then:

- What it is: **Open Regels Nederland — Public knowledge base, Province of Flevoland**. Publishes public information only; processes no personal data; needs no login or account. Every piece of public information a Flevoland civil servant sees is published here too.
- A `<figure markdown>` embedding `../../assets/screenshots/ronl-business-api-public-site.png`.
- The combined search: one query across all five sources.
- A table of the five sources — Announcements (official announcements from the Province of Flevoland), News (national news from the Dutch central government), Products & Services (permits, notifications and grants for residents and businesses), Rule catalogue (public services and the rules used to execute them, including validity dates and source), Process library (how an application moves through the organisation, step by step).
- Two further sections in the site's own navigation: Data dictionary and Provenance.
- An NL/EN language toggle, and a **Staff login** route across to the werkomgeving.
- Accountability links: Accessibility statement (WCAG 2.1 AA) and Open data & API.
- An ACC-only admonition:

```markdown
!!! warning "Acceptance environment only"
    The public site currently runs on the acceptance environment at
    `acc.publiek.open-regels.nl` (v2026.08.19). There is no production
    deployment yet; a full guide follows when one exists.
```

- [ ] **Step 2: Write the NL placeholder.**

- [ ] **Step 3: Add the nav entry** `- Public Site: ronl-business-api/user-guide/public-site.md` after the four boards.

- [ ] **Step 4: Build**

```bash
venv/Scripts/mkdocs.exe build 2>&1 | tail -20
```

Expected: exit 0; still exactly the four board-screenshot warnings and nothing new. The public-site screenshot resolves — Task 2 renamed it.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "docs(ronl-business-api): add the public knowledge base page, flagged ACC-only"
```

---

### Task 8: Restructure the home page

**Files:**
- Modify: `docs/en/index.md`

`docs/nl/index.md` has no Documentation Status section and no What's New — **leave it untouched**.

- [ ] **Step 1: Remove the superseded RBA callout**

Delete the whole `!!! note "RONL Business API: only the Developer docs are current to v3.9.1"` admonition and its indented body. Its premise is replaced by the new section.

- [ ] **Step 2: Insert the new section directly after the intro line**

```markdown
## 📘 How this documentation is maintained

Components differ in how fast they change, so they are documented to different depths.

| Component | Cadence | User Guides |
|---|---|---|
| **RONL Business API** | Short-cycle, co-designed with users | Landing page and a brief page per board on ACC; full guides when a board reaches PROD |
| **CPSV Editor** | Release-tagged | Full |
| **Linked Data Explorer** | Release-tagged | Full |
| **Norm Editor** | Release-tagged | Full |
| **CPRMV API** | Spec-driven | Full |

Features, Developer Docs and References follow the same pattern for every component.
```

- [ ] **Step 3: Move the Documentation Status block up**

Cut `## Documentation Status` together with its `<div id="doc-status"> … </div>` and its trailing `---`, and paste directly beneath the new section — above `## 🆕 What's New`. `doc-status.js` finds the div by id, so position does not affect it.

- [ ] **Step 4: Verify the resulting order**

```bash
grep -nE "^## " docs/en/index.md | head -6
```

Expected, in order: `## 📘 How this documentation is maintained`, `## Documentation Status`, `## 🆕 What's New`, then the rest unchanged.

- [ ] **Step 5: Confirm the old callout is gone and the div survived exactly once**

```bash
grep -c "only the Developer docs are current" docs/en/index.md   # expect 0
grep -c 'id="doc-status"' docs/en/index.md                        # expect 1
```

- [ ] **Step 6: Build**

```bash
venv/Scripts/mkdocs.exe build 2>&1 | tail -15
```

Expected: exit 0, no new warnings.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "docs: promote Documentation Status and explain per-component documentation depth"
```

---

### Task 9: Write the screenshot manifest

**Files:**
- Modify: `screenshot-manifest/ronl-business-api-screenshots-todo.md` (create if absent)

- [ ] **Step 1: Write the manifest**

Header naming this as the restructure pass of 2026-08-19. Four **NEW** rows, one per board, each with its embedding page and what it must show:

| # | Status | File | Embedding page | What it must show |
|---|---|---|---|---|
| 1 | NEW | `ronl-business-api-caseworker-board.png` | `user-guide/caseworker.md` | The Caseworker board after sign-in — task list with claims and deadlines |
| 2 | NEW | `ronl-business-api-pa-cockpit-board.png` | `user-guide/pa-cockpit.md` | The PA-Cockpit board — dossier and issue overview with priority/momentum |
| 3 | NEW | `ronl-business-api-infra-board.png` | `user-guide/infra-board.md` | The Infra-board — phase swimlanes with per-project status |
| 4 | NEW | `ronl-business-api-woo-dashboard-board.png` | `user-guide/woo-dashboard.md` | The Woo-dashboard — compliance figures, traffic lights, "Woo in cijfers" |

Note in the manifest that all four need an authenticated session, so capture is a human step, and that the landing-page and public-site captures are already in place. Record that the werkomgeving capture is Dutch while the public-site capture is English, and an English werkomgeving re-shot would be preferable if that interface exists.

- [ ] **Step 2: Verify every manifest row maps to a real figure**

```bash
for i in caseworker-board pa-cockpit-board infra-board woo-dashboard-board; do
  echo "ronl-business-api-$i -> $(grep -rl "ronl-business-api-$i" docs/en | wc -l) page(s)"
done
```

Expected: each reports `1`. A `0` means Task 6 omitted a figure — fix Task 6, not the manifest.

- [ ] **Step 3: Commit**

```bash
git add -A
git commit -m "docs: add RBA screenshot manifest for the four board captures"
```

---

### Task 10: Update the iou-document-patch skill

Without this, the next sync will treat the archive as ordinary pages and undo the restructure.

**Files:**
- Modify: `.claude/skills/iou-document-patch/SKILL.md`

- [ ] **Step 1: Add a hard archive rule** to the skill, in the same voice as the existing i18n rule:

```markdown
### Archived pages are frozen (do not violate)

`docs/{en,nl}/<component>/user-guide/archive/**` is **never edited by a sync** —
not reworded, not version-stamped, not given a metadata header, not relinked.
Archived pages describe an older release on purpose; "updating" one destroys the
only record of how the product behaved then.

If a sync's content belongs on an archived topic, write it on the current page
instead. The archive only ever grows: pages enter it when a restructure retires
them, and never leave.
```

- [ ] **Step 2: Record RBA's documentation convention** in the Known-components table: User Guides are ACC-brief / PROD-full; the current set is Getting Started, four board pages and the public site; `user-guide/test-guides/` is maintained, not archived; promoting a board to PROD is the trigger to expand its page into a full guide.

- [ ] **Step 3: Drop the stale `references/` note** — Task 1 renamed it, so every component now uses `reference/`. Leaving the note would send a future sync to a path that no longer exists.

- [ ] **Step 4: Verify the skill states all three**

```bash
grep -c "user-guide/archive\|ACC-brief\|test-guides" .claude/skills/iou-document-patch/SKILL.md  # expect >= 3
grep -c "uses \`references/\`" .claude/skills/iou-document-patch/SKILL.md                        # expect 0
```

- [ ] **Step 5: Commit**

```bash
git add .claude/skills/iou-document-patch/SKILL.md
git commit -m "docs(skill): freeze archived pages and record RBA's ACC-brief documentation convention"
```

---

## Final verification

- [ ] `venv/Scripts/mkdocs.exe build 2>&1 | tail -20` — exit 0; the **only** warnings are the four uncaptured board screenshots.
- [ ] `grep -rn "ronl-business-api/references/" docs/ mkdocs.yml | wc -l` → `0`.
- [ ] `ls docs/en/ronl-business-api/user-guide/*.md | wc -l` → `6`.
- [ ] `ls docs/en/ronl-business-api/user-guide/archive/*.md | wc -l` → `9`.
- [ ] `ls docs/en/ronl-business-api/user-guide/test-guides/*.md | wc -l` → `3`.
- [ ] Every archived page shows the banner; no test guide does.
- [ ] Home page section order: How this documentation is maintained → Documentation Status → What's New.
- [ ] No commit in this series carries a `Co-Authored-By` or `Claude-Session` trailer.
