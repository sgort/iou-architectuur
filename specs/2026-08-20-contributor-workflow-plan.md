# Contributor Workflow & Homepage Restructure — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Document how this ecosystem is actually developed — the AI-assisted pipeline, the user/project skill split, and the boundaries a first-time contributor needs — and regroup the homepage around three questions so the new material has somewhere to land.

**Architecture:** Documentation only; no component code changes. Four new pages form a `contributing/development-workflow/` subsection, `code-standards.md` is written from re-measured facts, `contributing/index.md` gains a two-track fork, and the homepage groups its existing sections under three headings. Tasks are ordered so no task ever links to a page a later task creates — there are no dangling links at any point.

**Tech Stack:** MkDocs 1.6.1 + Material, `mkdocs-static-i18n` (folder structure, EN default), the repo's `hooks/repo_versions.py`.

**Spec:** `specs/2026-08-20-contributor-workflow-design.md`

## Global Constraints

- Build with the repo venv: `venv/Scripts/mkdocs.exe build`. **Never pipe its output through `grep` alone** — a fatal config error hides behind a warning filter. Read the tail AND check the exit code. **Do NOT use `--strict`.**
- The site is currently completely clean. **Expect exit 0 and ZERO warnings after every task.** Any warning means you broke something.
- After each task also run the absolute-link sweep, which MkDocs never performs. It must print nothing:
  ```
  grep -rhoE 'href="/[A-Za-z0-9/._-]+"' docs/en docs/nl | sed 's/href="//;s/"$//' | sort -u | while read u; do
    p="site${u}"; [ -f "$p" ] || [ -f "${p%/}/index.html" ] || echo "BROKEN: $u"
  done
  ```
- **No `component:` front matter on any page in this plan.** Verified 2026-08-20: no existing page under `docs/en/contributing/` carries it, and these are site-level pages, not component pages — they must show no version header.
- **Every new EN page needs an NL counterpart.** Verified 2026-08-20: every existing page under `docs/nl/contributing/` is a placeholder, none a real translation. So NL pages are placeholders in the house pattern — a "Documentatie in ontwikkeling" admonition, `**Status:** Concept`, `**Engelstalige bron:**`, and mirrored empty `##` headings. Copy the exact shape from `docs/nl/contributing/code-standards.md`. **Do NOT translate.**
- `mkdocs.yml` nav indentation — **the Contributing section is one level shallower than the component sections. Do not reuse component-section indentation here.** Verified 2026-08-20 with `cat -A`:
  - `  - 🤝 Contributing:` — **2 spaces**
  - `    - Overview:` / `    - Documentation Architecture:` / `    - Code Standards:` — **4 spaces**
  - a nested subgroup's leaves, e.g. under `Documentation Architecture:` — **6 spaces**

  Always confirm with `cat -A` on the live file rather than the diff. A mismatched anchor silently eats leading spaces and breaks the YAML — this exact error broke this repo's nav once already.
- **A nav entry pointing at a file that does not exist is a hard MkDocs ERROR**, not a warning. Each task adds only nav entries for pages it creates in that same task.
- **Stage only your own files. NEVER `git add -A`** — the working tree holds unrelated untracked and modified files that must not enter a commit.
- Commit messages carry **no** `Co-Authored-By` and **no** `Claude-Session` trailer.
- **Ask the user before every `git commit`.** No blanket approval has been given for this plan.
- Write British English, matching the surrounding site.

---

### Task 1: Development workflow — Overview

The subsection's entry point. A newcomer who reads only this page should understand the shape of how work happens here.

**Files:**
- Create: `docs/en/contributing/development-workflow/overview.md`
- Create: `docs/nl/contributing/development-workflow/overview.md` (placeholder)
- Modify: `mkdocs.yml` (new `Development Workflow` subgroup under Contributing, one leaf)

**Interfaces:**
- Produces: the path `contributing/development-workflow/overview.md`, which Tasks 5 and 6 link to, and the nav subgroup Tasks 2–3 add their leaves into.

- [ ] **Step 1: Read the surrounding material first**

Read `docs/en/contributing/index.md` for the section's voice, and the spec's "Design → 2" section for what this page owes. Read `docs/nl/contributing/code-standards.md` for the exact NL placeholder shape.

- [ ] **Step 2: Write the EN page**

`# Development Workflow`, then the pipeline in order, one short section per stage, each linking onward:

1. **Design** — for medium-to-large features where fundamental UX is at stake, design comes first, in Claude Design. Small changes skip this entirely.
2. **Handoff** — the design leaves Claude Design as a handoff package: the design itself, standalone HTML, screenshots, a README and a PROMPT.
3. **Implementation** — Claude Code, with `claude-mem` capturing session memory by default, working either inline or through the `superpowers` plugin depending on the size of the change. Implementation follows **red/green TDD**: the failing test comes first.
4. **Release** — `/bump-release`, defined per repository.
5. **Documentation** — `/iou-document-patch`, defined once, in the documentation repository.

Close with a short "Where to go next" list pointing at the other pages in the subsection. Keep the whole page under roughly 60 lines — it is a map, not the territory.

Link only to pages that exist right now (`../index.md`, and the two skills described inline). **Do not link to `design-and-handoff.md`, `working-with-claude-code.md` or `skills-and-boundaries.md`** — they are created in Tasks 2 and 3, and linking early would produce a build warning.

- [ ] **Step 3: Write the NL placeholder**

House pattern, mirroring the EN `##` headings, `**Engelstalige bron:** contributing/development-workflow/overview.md`.

- [ ] **Step 4: Add the nav subgroup**

Under `- 🤝 Contributing:` in `mkdocs.yml`, after the `Overview` leaf, add:

```
    - Development Workflow:
      - Overview: contributing/development-workflow/overview.md
```

Group key at **4 spaces** to match its siblings (`- Documentation Architecture:`), its leaf at **6**. Confirm against the existing `Documentation Architecture` subgroup with `cat -A` before and after.

- [ ] **Step 5: Verify**

```bash
venv/Scripts/mkdocs.exe build 2>&1 | tail -15
```
Expected: exit 0, zero warnings. Then run the absolute-link sweep from Global Constraints — it must print nothing.

- [ ] **Step 6: Commit** (ask the user first)

```bash
git add docs/en/contributing/development-workflow/overview.md \
        docs/nl/contributing/development-workflow/overview.md mkdocs.yml
git commit -m "docs(contributing): add the development workflow overview"
```

---

### Task 2: Design & Handoff, and Working with Claude Code

Two pages covering the first half of the pipeline. Grouped because both describe tooling the reader meets before writing any code, and a reviewer would accept or reject them together.

**Files:**
- Create: `docs/en/contributing/development-workflow/design-and-handoff.md`
- Create: `docs/en/contributing/development-workflow/working-with-claude-code.md`
- Create: both NL placeholders
- Modify: `mkdocs.yml` (two leaves into the existing subgroup)

**Interfaces:**
- Consumes: the `Development Workflow` nav subgroup created in Task 1.
- Produces: both page paths, which Task 6's homepage summary may link to.

- [ ] **Step 1: Write `design-and-handoff.md`**

Two halves.

*When to use Claude Design* — medium-to-large features where fundamental UX is at stake. Say what that excludes: a bug fix, a copy change, or a new field on an existing form goes straight to implementation. The test is whether the shape of the interaction is in question, not whether the change is large in lines.

*The handoff package* — what it contains (the design, standalone HTML, screenshots, a README, a PROMPT) and how it is used. Two rules, both learned in practice, stated as rules with their reasons:

- **The handoff folder's files are the single source of truth** for that piece of work — not a same-named or similar-looking file already in the application. The two often share a shape and a plausible location, and mistaking one for the other means designing against the wrong data.
- **The handoff folder is briefing material, not repository content.** Port what it specifies into the real source files and leave the folder untracked, or remove it before the final commit.

- [ ] **Step 2: Write `working-with-claude-code.md`**

Three short sections.

*Session memory* — `claude-mem` runs by default and captures session memory; the viewer is at `http://localhost:37780`. State that the port is configurable via `CLAUDE_MEM_WORKER_PORT` in `~/.claude-mem/settings.json`. **Re-verify the port from that file before writing it** rather than copying it from this plan.

*Inline versus superpowers* — inline for small, well-understood changes; the `superpowers` plugin for multi-step work, where it provides brainstorming a design, writing a plan, and executing it with review between tasks. Frame the choice by the size and uncertainty of the work, not by preference.

*Red/green test-driven development* — how implementation proceeds here, and a full section rather than an aside. The cycle: write the failing test first; **run it and watch it fail, for the reason you expect**; write the minimum that makes it pass; run it again; refactor with the test as the safety net.

Make the middle step's purpose explicit — it is the step most often skipped and the only one that proves anything. A test that has never been seen to fail proves nothing: it may assert something already true, or nothing at all. If a test passes before the implementation exists, it is testing something other than what it claims, and the fix is to correct the test, not to celebrate.

Note that the `superpowers` plugin structures work this way by default, so a contributor using it follows the cycle whether or not they think of it as TDD. Say plainly where it does not apply — a documentation change has no failing test to write, and pretending otherwise is cargo cult.

*What this means for a contributor* — the boundaries page (Task 3) covers the rules; here just note that the assistant works within recorded boundaries and point forward without linking yet.

**Do not link to `skills-and-boundaries.md`** — Task 3 creates it. Cross-link it in Task 3 instead.

- [ ] **Step 3: Write both NL placeholders**

House pattern, mirrored headings, correct `**Engelstalige bron:**` paths.

- [ ] **Step 4: Add both nav leaves**

Into the existing `Development Workflow` subgroup at **6 spaces**, after `Overview`:

```
      - Design & Handoff: contributing/development-workflow/design-and-handoff.md
      - Working with Claude Code: contributing/development-workflow/working-with-claude-code.md
```

- [ ] **Step 5: Verify**

Build (exit 0, zero warnings) and the absolute-link sweep (prints nothing).

- [ ] **Step 6: Commit** (ask the user first)

```bash
git add docs/en/contributing/development-workflow/ docs/nl/contributing/development-workflow/ mkdocs.yml
git commit -m "docs(contributing): document Claude Design handoff and working with Claude Code"
```

---

### Task 3: Skills & Boundaries

The first-time contributor explainer, and the page that does the most work in this plan.

**Files:**
- Create: `docs/en/contributing/development-workflow/skills-and-boundaries.md`
- Create: `docs/nl/contributing/development-workflow/skills-and-boundaries.md` (placeholder)
- Modify: `docs/en/contributing/development-workflow/overview.md` and `working-with-claude-code.md` (add the forward links held back in Tasks 1–2)
- Modify: `mkdocs.yml` (one leaf)

**Interfaces:**
- Consumes: the nav subgroup from Task 1; the two pages from Task 2.
- Produces: `skills-and-boundaries.md`, which Task 6's homepage summary links to.

- [ ] **Step 1: Re-verify the facts before writing them**

Do not copy these from the plan. Run:

```bash
ls ~/.claude/CLAUDE.md && grep -c '^## ' ~/.claude/CLAUDE.md
ls ~/.claude/plugins/cache/*/
for r in iou-architectuur ronl-business-api linked-data-explorer ttl-editor editor; do
  echo "$r: skills=[$(ls /c/Users/gorts01/Development/$r/.claude/skills 2>/dev/null | tr '\n' ' ')] commands=[$(ls /c/Users/gorts01/Development/$r/.claude/commands 2>/dev/null | sed 's/\.md//' | tr '\n' ' ')]"
done
```

Expected at the time of writing: 9 rules in `CLAUDE.md`; plugins `superpowers` and `claude-mem`; `iou-document-patch` a skill in the docs repo only; `bump-release` a command in three component repos; the Norm Editor repo has neither. **If what you find differs, document what you find and say so in your report.**

- [ ] **Step 2: Write the two-level explanation**

A table contrasting the levels — what lives at each, and what each applies to:

| Level | Location | Applies |
|---|---|---|
| User | `~/.claude/` | Every repository, every session |
| Project | `<repo>/.claude/` | That repository only |

Then the example that makes it concrete: **`/bump-release` exists three times**, once per repository, because each repository's changelog is genuinely different — one a JSON array, one a JSON object with a per-entry `scope` field, one a TypeScript module. Same command name, three implementations. **`/iou-document-patch` exists exactly once**, because there is one documentation site.

State the rule that follows: *a capability belongs at user level when it describes how you work, and stays at project level when it depends on what the repository is.*

Note that the user-level rules were promoted from project level on 2026-08-19, after the same rule had been independently re-learned in four separate repositories — that history is the argument for the rule.

- [ ] **Step 3: Write the boundaries section**

Give each boundary its reason; a rule without one reads as arbitrary and gets worked around. Cover at minimum:

- Never start, stop or restart a dev server — the contributor owns those processes, and killing one can cascade into siblings under a shared runner.
- Ask before every commit — approval is per commit, never inferred from an earlier one.
- Never merge or force-push a shared branch unasked.
- Create a branch before implementing.
- No Claude attribution trailers in commit messages.

Point to `~/.claude/CLAUDE.md` as the authority rather than restating all nine in full — a copy here would drift.

- [ ] **Step 4: Describe the two custom skills**

`/bump-release` — cuts a release in the repository you are in. `/iou-document-patch` — brings this documentation site into sync with a component's latest release, in staged fashion. For each: what it is for, where it is defined, and that it is invoked by name. Do not document their internals; link to the skill files.

- [ ] **Step 5: Add the forward links held back earlier**

In `overview.md`'s "Where to go next", and in `working-with-claude-code.md`'s closing section, add the links to this page and to the Task 2 pages. Every target now exists.

- [ ] **Step 6: Write the NL placeholder, add the nav leaf** at **6 spaces**, after `Working with Claude Code`.

- [ ] **Step 7: Verify**

Build (exit 0, zero warnings) and the sweep (prints nothing). Also confirm every link added in Step 5 resolves — the build catches missing `.md` targets, but check anchors by eye.

- [ ] **Step 8: Commit** (ask the user first)

```bash
git add docs/en/contributing/development-workflow/ docs/nl/contributing/development-workflow/ mkdocs.yml
git commit -m "docs(contributing): explain user vs project skills and the working boundaries"
```

---

### Task 4: Code Standards

Replaces a 19-line "Coming Soon" stub with a page written from re-measured facts.

**Files:**
- Modify: `docs/en/contributing/code-standards.md`
- Modify: `docs/nl/contributing/code-standards.md` (mirror headings only)

**Interfaces:**
- Consumes: nothing. Its nav entry already exists — **do not add one**.

- [ ] **Step 1: Measure, do not copy**

The figures below were true on 2026-08-19 and are given only so you know what to look for. **Re-verify every one before writing it.** For each of `ronl-business-api`, `linked-data-explorer`, `ttl-editor` under `/c/Users/gorts01/Development/`:

```bash
cd /c/Users/gorts01/Development/<repo>
python -c "import json,io;d=json.load(io.open('package.json',encoding='utf-8'));print(json.dumps(d.get('scripts'),indent=1))"
cat .husky/pre-commit .husky/pre-push 2>/dev/null
```

**Do not run any test suite, dev server or container.** You are reading configuration, not executing it.

- [ ] **Step 2: Write the EN page**

Cover:

- **The commands**, per repository — lint, lint fix, format, and format-check. Note that the format-check command's *name differs between repositories* (`check-format` versus `format:check`); in one repository a root script that fanned out by name silently skipped a whole workspace because of exactly this.
- **What the git hooks actually gate.** Expect to find `pre-commit` running `lint-staged` and `pre-push` running lint and formatting. **State plainly whether any repository's hooks run the tests** — at the last measurement none did, and a contributor assuming otherwise will push a broken suite.
- **CI**, where it differs from the hooks. At the last measurement the RONL Business API's public-site package had a real test gate in CI while its frontend — the largest suite — had neither lint nor test.
- **Commit messages**, including the no-attribution-trailer rule.
- **Testing** — link to each component's own `developer/testing` page rather than repeating counts that go stale. The CPSV Editor, Linked Data Explorer and RONL Business API each have one. State the expectation that new code arrives with tests written red/green, and cross-link [Working with Claude Code](development-workflow/working-with-claude-code.md) for the cycle itself rather than restating it.

Remove the "Coming Soon" admonition entirely.

- [ ] **Step 3: Mirror the changed headings** into the NL placeholder. Do not translate.

- [ ] **Step 4: Verify**

Build (exit 0, zero warnings), sweep (prints nothing), and confirm each linked `developer/testing` page exists.

- [ ] **Step 5: Commit** (ask the user first)

```bash
git add docs/en/contributing/code-standards.md docs/nl/contributing/code-standards.md
git commit -m "docs(contributing): write code standards from measured per-repo facts"
```

---

### Task 5: Two tracks in the Contributing overview

**Files:**
- Modify: `docs/en/contributing/index.md`

- [ ] **Step 1: Add the fork**

`index.md` currently has `## How to Contribute for Users` and `## How to Contribute for Developers`, the latter a six-step fork-and-MR process. Add a short paragraph immediately before the developer section sending the reader one of two ways:

- **Maintainers and core contributors** → the [Development Workflow](development-workflow/overview.md) subsection.
- **Outside contributors** → the six-step process that follows, unchanged.

- [ ] **Step 2: Do not disparage either route**

The fork-and-MR path is the correct route for anyone without this toolchain and must not read as a lesser option or a consolation. Do not edit the six steps themselves — they are accurate and stay as written.

- [ ] **Step 3: Verify**

Build (exit 0, zero warnings) and sweep (prints nothing).

- [ ] **Step 4: Commit** (ask the user first)

```bash
git add docs/en/contributing/index.md
git commit -m "docs(contributing): signpost the maintainer and outside-contributor routes"
```

---

### Task 6: Homepage — three questions

Last, so every link it makes points at a page that already exists.

**Files:**
- Modify: `docs/en/index.md`

- [ ] **Step 1: Group the existing sections under three headings**

Insert three `##` group headings and demote the current `##` sections beneath them to `###`, in this order:

| Group heading | Sections beneath it |
|---|---|
| `## What is this?` | What is IOU Architecture · Architecture Overview · Ecosystem Components · Technology Stack · Standards Compliance |
| `## What is the state of it?` | Documentation Status · What's New · How this documentation is maintained |
| `## How do I work on it?` | **Development workflow** *(new)* · Contributing · Quick Links |

**Nothing is deleted.** Every existing section survives with its content intact; only its heading level and position change.

Two things to preserve carefully:
- The `<div id="doc-status">` block must move intact — `docs/javascripts/doc-status.js` finds it by that id and injects the status table at page load. A duplicated or corrupted div breaks the homepage silently, with no build error.
- The `.whats-new-cards` container and its card list must stay structurally unchanged; the same script decorates those cards with environment badges.

- [ ] **Step 2: Write the new Development workflow section**

Under `## How do I work on it?`, roughly eight lines: one sentence per pipeline stage (design → handoff → implementation → release → documentation), then a link to [Development Workflow](contributing/development-workflow/overview.md). It summarises; it does not duplicate the subsection.

- [ ] **Step 3: Do not add front matter**

`docs/en/index.md` is the site home page and carries no `component:` key. Leave it that way.

- [ ] **Step 4: Leave `docs/nl/index.md` alone**

It has no matching structure to mirror. Verify this yourself before deciding, then leave it untouched.

- [ ] **Step 5: Verify**

```bash
grep -nE "^## " docs/en/index.md
```
Expected: exactly three `##` headings, in the order above, with everything else now `###`.

```bash
grep -c 'id="doc-status"' docs/en/index.md   # expect exactly 1
grep -c 'whats-new-cards' docs/en/index.md    # expect exactly 1
```

Then build (exit 0, zero warnings) and the sweep (prints nothing).

- [ ] **Step 6: Check the rendered page**

Open `site/index.html` and confirm the doc-status div and the What's New cards both survived the move intact, and that the three group headings render in the intended order.

- [ ] **Step 7: Commit** (ask the user first)

```bash
git add docs/en/index.md
git commit -m "docs: group the homepage around three questions and summarise the development workflow"
```

---

## Final verification

- [ ] `venv/Scripts/mkdocs.exe build` — exit 0, **zero** warnings.
- [ ] The absolute-link sweep prints nothing.
- [ ] `ls docs/en/contributing/development-workflow/*.md | wc -l` → `4`.
- [ ] `ls docs/nl/contributing/development-workflow/*.md | wc -l` → `4`.
- [ ] No page created by this plan carries `component:` front matter.
- [ ] `grep -c "Coming Soon" docs/en/contributing/code-standards.md` → `0`.
- [ ] The red/green TDD cycle is documented in `working-with-claude-code.md`, including why the failing run matters, and referenced from both the overview pipeline and `code-standards.md`.
- [ ] The homepage has exactly three `##` headings and one `id="doc-status"`.
- [ ] No commit in this series carries a `Co-Authored-By` or `Claude-Session` trailer.
