---
name: iou-document-patch
description: Use when the user asks to sync, patch or update the IOU architecture documentation site (iou-architectuur) to a component's latest release — CPSV Editor / ttl-editor, Linked Data Explorer, RONL Business API, Norm Editor, CPRMV — or invokes /iou-document-patch; and use when the user asks for the weekly Sunday pass, the cross-cutting contributor pages under docs/en/contributing/, a new ICTU dependency-guideline assessment or score, or the test-posture figures behind its charts. The run has two modes that touch different files — a component sync edits that component's own pages and defers the cross-cutting half, while the weekly pass edits the contributing pages and docs/data/ictu-assessments.yml and reads no component changelog. Establish which mode before Stage 0.
---

# IOU Document Patch

Synchronise the documentation site (`iou-architectuur`) with the latest
**documented version** recorded in a linked component's source changelog. The
default component is the **CPSV Editor**, whose code lives in the sibling
`../ttl-editor` repo and whose per-release notes live in
`../ttl-editor/src/data/changelog.json`.

The work is **staged**: analyse → present a plan + screenshot manifest → get the
user's approval and the `repo-versions.json` metadata → apply → verify. Never
skip straight to editing docs.

## Establish the mode first

There are two halves to keeping this site true, and since 24 September 2026 they
run on **different cadences and in different files**. Decide which one you are in
before Stage 0, and say so in your first message.

| | **Component sync** | **Weekly pass** |
|---|---|---|
| Triggered by | a component and/or a version — "sync RBA", "patch the docs to v2026.09.9", `/iou-document-patch <component>` | "the Sunday pass", "the weekly pass", "a new assessment", "score the guideline", "the cross-cutting pages", `/iou-document-patch weekly` |
| Cadence | whenever a component ships | every Sunday, over all components at once |
| Reads | that component's changelog at its branch of record | the three repositories' `acc` heads, and the queue (below) |
| Edits | `docs/{en,nl}/<component>/**`, the What's New card, `repo-versions.json`, the screenshot manifest | `docs/{en,nl}/contributing/**`, `docs/data/ictu-assessments.yml` |
| Must not edit | **anything under `docs/{en,nl}/contributing/`**, and no `verified:` stamp | any component page, `repo-versions.json`, the What's New card |
| Stages | 0, 1, 2, 2b, 2c, 2d, 3, 4, 5 — **2e is deferred, not skipped** | 6 (which has its own staging) |

**Why they were split.** Until 20 September 2026 every component sync carried the
cross-cutting half with it, and that half is the larger one for a CI or
supply-chain release. Two things followed: a component sync became too big to
finish in one sitting, and the contributing pages were re-checked only when a
component happened to ship. They now move on a weekly rhythm of their own, which
is also what makes the ICTU score series comparable week to week — the scores are
read on the same weekday, at each repository's `acc` head.

!!! danger "Deferred means recorded. Skipped means the pages rot."
    Stage 2e was dropped by three consecutive runs of this skill before it was
    made mandatory, and making it *conditional* is exactly how that returns. In a
    component sync the stage does not disappear — it becomes two obligations:

    1. **Append to the queue** — `cross-cutting-queue.md` at the repository root
       (an operational artifact, never under `docs/`). One entry per cross-cutting
       fact the sync turned up, with the evidence: the changelog entry or the
       source file that establishes it, and which contributing page it bears on.
    2. **Say so in the report**, naming the queue file and the facts you put in it.

    A component sync that edits no contributing page and writes no queue entry
    has **skipped** the stage, not deferred it. If a release genuinely surfaced
    nothing cross-cutting, write that sentence in the queue file with the date —
    a silent no-op is indistinguishable from a forgotten step on the next run.

## Component map

Default target is the CPSV Editor. If the user names a different component,
adapt the paths — the same staging applies.

| Thing | Location |
|---|---|
| Source changelog | `../ttl-editor/src/data/changelog.json` — a **top-level object** `{versions: [...]}`, newest first. Not a bare array; `json.load()` gives you a dict, so index `["versions"]`. Entries carry `format` / `version` / `status` / `date` / `commits`, and there is **no** `scope` field (single-package repo). Read it as UTF-8 — it contains non-cp1252 bytes, so a bare `open()` fails on Windows. Two shapes coexist: legacy entries up to v1.10.6 use `sections`/`items`; everything from v1.10.7 uses `format: "commits"` with per-commit `sha`/`author`/`type`/`subject`/`details`. Recognised types include `ci` (added in v2026.08.2) alongside `feat`/`fix`/`test`/`docs`/`chore`/`refactor`/`other`. Versioning switched from SemVer to CalVer at v2026.07.0, so an ordered gap can span both schemes. Read the changelog from the **`acc`** branch — that is the branch of record. |
| Documented version of record | `docs/repo-versions.json` → repository named **"CPSV Editor"** → `version` |
| Developer changelog page | `docs/en/cpsv-editor/developer/changelog-roadmap.md` |
| Four perspectives (EN) | `docs/en/cpsv-editor/{developer,features,reference,user-guide}/*.md` |
| Four perspectives (NL) | `docs/nl/cpsv-editor/{developer,features,reference,user-guide}/*.md` |
| Home "What's New" card | `docs/en/index.md` (and `docs/nl/index.md`) — CPSV Editor grid card |
| Screenshots referenced by docs | `../../assets/screenshots/cpsv-editor-*.png` → real files in `docs/assets/screenshots/` (language-neutral, served at site root) |
| Testing page | `docs/en/<component>/developer/testing.md` — the site is the **single source of truth** for test docs (see Stage 2d) |
| Cross-cutting contributor docs | `docs/en/contributing/**` — **not component-scoped, and easy to miss.** These pages describe the tooling across *all* components at once: CI, git hooks, lint/format scripts, the repository table, the release process, the supply-chain gate, the assistant's plugin set and its working boundaries. A single component's release can falsify them, and they carry no `component:` front matter to flag them as in-scope. **Owned by the weekly pass (Stage 6); a component sync queues instead of editing them** |
| Cross-cutting queue | `cross-cutting-queue.md` at the repository root — what a component sync noticed and deferred. An operational artifact like the screenshot manifest, so never under `docs/`, where a file outside the nav warns on every build |
| ICTU assessment series | `docs/data/ictu-assessments.yml` — one entry per Sunday: the three `acc` heads, eleven scores per component, and a reason per moved cell. Every table and chart on `contributing/ictu-dependency-guideline.md` is generated from it; write the week's scores here and nowhere else |
| Assistant-tooling sources of truth | `~/.claude/CLAUDE.md` (working boundaries), `~/.claude/plugins/installed_plugins.json` (what is installed, and at which scope), `~/.claude/settings.json` → `enabledPlugins` (what is actually on), `~/.claude/plugins/known_marketplaces.json`. These are the **only** authority for `development-workflow/skills-and-boundaries.md` and `working-with-claude-code.md` — never restate those pages from memory. See Stage 2e |
| Per-page metadata header | `component:` front matter on every edited/added component page; `scope: cross-cutting` on every `contributing/**` page (see below) |

### Known components beyond CPSV Editor

| Component | Source repo | Changelog | Notes |
|---|---|---|---|
| **Norm Editor** | sibling repo **`../editor`** (confirmed on the Windows workstation at `C:\Users\gorts01\Development\editor`; also seen at `/home/steven/Development/editor` on Linux) | `gui/public/changelog.json`, schema **`{versions: {<service>: <semver>, ...}, releases: [{version, date, changes: {<conventional-commit-type>: [commit, ...]}, commits: [...]}]}`** — git-log-derived, not curated. `version-gap.py` auto-detects this shape (a `releases` array) vs. the curated `versions` array and normalizes both to the same `sections`/`items` shape; it also drops the synthetic `"Unreleased"` pseudo-version. Pass `--changelog <path> --component "Norm Editor"` explicitly. | No `developer/changelog-roadmap.md` existed before the 2026.07.0 sync (create it + add the mkdocs.yml nav entry — don't assume the page is there). Docs currently have **zero** screenshots — don't force a manifest entry for that reason alone. `docs/nl/index.md` is a placeholder with no "What's New" section to mirror at all — check before assuming both `docs/en/index.md` and `docs/nl/index.md` need the card edit. Because the first tag can land long after the code it covers, don't backfill version numbers onto pre-existing features you can't date — only claim what genuinely changed inside the tagged commit range. |
| **Linked Data Explorer** | sibling repo `../linked-data-explorer` | `packages/frontend/src/changelog.json` — a dict with a **`versions`** array, same curated `format: "commits"` shape as the CPSV Editor, plus a per-entry `scope` field (`frontend` / `backend` / `both`, absent on most). **`version-gap.py` works against it unmodified** — pass `--changelog ../linked-data-explorer/packages/frontend/src/changelog.json --component "Linked Data Explorer"`. | Versions switched from SemVer to CalVer mid-history (…, 1.9.12, 1.9.13, 2026.07.0, …), so an ordered gap can span both schemes — the same transition the CPSV Editor made. `repo-versions.json` and the roadmap headings carry a `v` prefix; the changelog does not. **i18n differs from the CPSV Editor**: nearly every EN page has an NL counterpart (64 and 63 on 24 September 2026 — count rather than trust the number, it moves every sync), and **three are real translations** — `developer/backend.md`, `reference/api-stability.md`, `user-guide/multilingualism.md` — so check each NL page before assuming it is a placeholder. A screenshot manifest already exists at `screenshot-manifest/linked-data-explorer-screenshots-todo.md`. `developer/testing.md` **exists** (507 lines as of v2026.09.5) — refresh it, never create a second one; note `developer/test-cases.md` is a *feature* doc, not the test-suite page. The repository has **no Playwright suite at all**, so the Stage 2d end-to-end sweep legitimately returns nothing here. |
| **RONL Business API** | sibling repo `../ronl-business-api` | `packages/frontend/src/pages/changelog-data.ts` — a **TypeScript file**, not JSON: unquoted object keys, mixed single/double-quoted strings, trailing commas, and a `ChangelogItem = string \| FeedbackItem` union mixed into `items` arrays. `version-gap.py`'s `json.loads()` cannot parse it directly, and no safe regex conversion exists (a colon inside changelog prose would get mangled by a naive `key:` → `"key":` transform). **Use the shim, not `version-gap.py`:** `node .claude/skills/iou-document-patch/scripts/ts-changelog.js <file.ts>`, with `--latest`, `--gap <version>` or `--json`. It slices off everything before the `export const changelog` assignment and evaluates the remaining object literal as a JavaScript expression in a throwaway `vm` context, so nothing regexes the content. Feed it a file read from a **ref**, not the working tree. If it reports that it cannot evaluate the literal, the data has grown a real TypeScript construct — say so rather than working around it. | Version strings carry a `v` prefix in `repo-versions.json` and `changelog-roadmap.md` headings (`v3.9.1`) but not in `changelog-data.ts` itself (`'3.9.1'`) — normalize before comparing. **Documentation convention for User Guides**: pages are **ACC-brief / PROD-full** — a page's depth follows the release maturity of what it documents, not a fixed template. The current set is Getting Started, four board pages (Caseworker, PA-Cockpit, Infra-board, Woo-dashboard), and Public Site. `user-guide/test-guides/` holds live Dutch test scripts that are **maintained, not archived** — never give them the archive banner or treat them as frozen. Promoting a board from ACC to PROD is the trigger to expand its brief page into a full guide. |

### i18n rule (do not violate)

The site uses `mkdocs-static-i18n` with `docs_structure: folder`. EN is the
default with `fallback_to_default: true`. **Most `docs/nl/cpsv-editor/**` pages
are placeholders** (an "Documentatie in ontwikkeling" admonition + mirrored empty
`##` headers + `**Status:** Concept` + `**Engelstalige bron:**`). Only
`docs/nl/cpsv-editor/developer/due-diligence.md` is a full Dutch translation.

Consequences for this skill:
- Write substantive content in the **EN** page.
- Update the **NL** page only when it is a real translation, or when its
  mirrored section headers must change to match a restructured EN page.
- **Which NL pages are real differs per component.** For the CPSV Editor it is
  only `developer/due-diligence.md`; the Linked Data Explorer has three (see the
  Known components table). Check before assuming — the reliable test is whether
  the page contains the "Documentatie in ontwikkeling" admonition:

  ```
  grep -L "Documentatie in ontwikkeling" docs/nl/<component>/**/*.md
  ```

  **That grep detects the banner, not the emptiness, and there is a third kind
  of page it misfiles.** `docs/nl/linked-data-explorer/features/dso-integration.md`
  carries the banner *and* 58 lines of substantive Dutch prose, some of it stale
  by a release. The grep calls it a placeholder; it is not. So make the test two
  parts — the banner, **and** no prose under the `##` headers:

  ```
  wc -l docs/nl/<component>/<page>.md      # a placeholder is ~20-40 lines of headers
  ```

  On a page of that third kind, **"Code is leading" still applies**: a claim the
  source contradicts is corrected **in Dutch**, in the narrowest edit that makes
  it true — the heading and the sentence that states the falsified fact, nothing
  else. That is not turning a placeholder into a half-English page; leaving a
  Dutch sentence asserting something untrue is the worse outcome. Prose that is
  merely *older* than this gap stays as it is, and goes in the report as a
  translation-pass finding.
- The **What's New** card exists in both `docs/en/index.md` and
  `docs/nl/index.md` — update both.

### Archived pages are frozen (do not violate)

`docs/{en,nl}/<component>/user-guide/archive/**` is **never edited by a sync** —
not reworded, not version-stamped, not given a new or altered metadata header, not relinked.
Archived pages describe an older release on purpose; "updating" one destroys the
only record of how the product behaved then.

If a sync's content belongs on an archived topic, write it on the current page
instead. The archive only ever grows: pages enter it when a restructure retires
them, and never leave.

**An archive banner must never name the component's current version.** Say what
the archived page describes ("describes the application around v2.9.1") and
where to go instead — never "the current documented version is vX". That clause
is stale the moment the next sync lands, and it cannot be corrected later
without editing frozen pages. The rendered metadata header is likewise
suppressed on any page under an `archive/` path segment, for the same reason:
the version is looked up globally at build time, so an archived page would
otherwise assert the current version directly above a banner describing an
older one.

This freeze governs *content*, not the mechanical link repair a move itself
makes necessary. When pages are moved into `archive/`, their relative links and
image paths have to be re-depthed or they resolve nowhere — that repair is a
consequence of the move, not a sync touching frozen content. A link that
resolves nowhere after a move is **broken**, not frozen; fix it. Rewording the
prose it sits in, or adding a version stamp, is not.

### Per-page metadata header (every page you touch)

Pages opt into a metadata header — rendered directly below the breadcrumbs,
carrying the git created/updated dates and the component's documented version
— by declaring the component name in YAML front matter:

```yaml
---
component: CPSV Editor
---
```

The name must match a `name` in `docs/repo-versions.json` exactly.

**Cross-cutting pages use the other key.** A page under
`docs/{en,nl}/contributing/**` describes every component at once, so no single
component's version is true of it. Those pages declare:

```yaml
---
scope: cross-cutting
---
```

which renders the same header with *"Applies to all components · docs built
&lt;date&gt;"* (Dutch: *"Geldt voor alle componenten · docs gebouwd …"*) in place
of a version badge. Never put a `component:` key on a contributing page — it
would stamp one arbitrary component's version onto a page that describes five.

The two keys exist because absence had become ambiguous: a page with no header
could mean either "no version applies here" or "not synced yet". Now the header
is present on every page a sync touches, and its right-hand fact says which
kind of page it is.

**Add this front matter to every page this patch edits or creates**, EN and NL
alike, including placeholders. It is deliberately opt-in: untouched pages keep
Material's default rendering, with the dates at the bottom of the page. Over
successive syncs the header spreads only as far as pages actually get revised.

#### The `verified` stamp — cross-cutting pages

A cross-cutting page may also say which commit of each component its claims were
last re-checked against. The header renders it as *"verified 2026-09-09 against
✏️ bbda389 · 🔍 007b350 · ⚙️ 04e38c8"*, each SHA linking to the commit in the
component's `ci_repo` — **GitHub** for the three applications, where the deploy
runs it triggered are listed; not the GitLab mirror, which has the same SHAs but
lags and shows no runs.
On a stamped page it replaces the site-wide *docs built* date, which only says a
sync happened somewhere:

```yaml
---
scope: cross-cutting
verified:
  date: 2026-09-09
  against:
    CPSV Editor: "bbda389"
    Linked Data Explorer: "007b350"
    RONL Business API: "04e38c8"
---
```

Rules — each one exists because the stamp is only worth something if it is true:

- **Write a component into the stamp only if you re-checked that component's
  claims *on this page*, today.** Touching a page is not re-checking it. Where
  you verified two components and not the third, the stamp names two. An old or
  partial stamp is information; a refreshed one that was not earned is a lie
  with a link on it.
- **The SHA is the commit you verified against** — the fetched
  `origin/<branch-of-record>` head, or the promoted `main` commit if that is
  what you read. Never the commit the docs happen to record in
  `repo-versions.json`, unless that is genuinely what you checked.
- **Prefer a SHA that triggered a deploy run on GitHub**, so the reader can follow
  it to a build. A commit that changed only CI configuration (`renovate.json`,
  `SECURITY-PIPELINE.md`, a non-deploy workflow) triggers none, because deploy
  workflows are path-filtered. If the head you read is one of those, stamp the most
  recent commit that did deploy — **but only if no CI-relevant commit sits between
  the two**; otherwise stamp the head and accept the script's warning.
- **Quote every SHA.** YAML parses an unquoted all-digit SHA as an integer, and
  one with a leading zero as octal: `0123456` becomes `42798`. The value is
  gone before the template sees it.
- **One date per page.** Components verified on other dates stay out of the
  stamp rather than borrowing this one.
- **Commits, not build ids.** Deploy workflows are path-filtered — in the Linked
  Data Explorer and RONL Business API the frontend build fires only on frontend
  paths — so most of what a contributing page describes (workflows,
  `SECURITY-PIPELINE.md`, runner configs) changes without producing a new build.
- **NL placeholders carry no stamp.** They contain no claims to have verified.

The site build never checks a stamp — it stays offline. `scripts/stamp-staleness.py`
does, in Stage 2e and Stage 4.

#### The `build` field — component pages

`repo-versions.json` may carry a `build` object per component, which the header
renders after the version and environment badge — *"v2026.09.2 PROD · build
007b350 · #39"*:

```json
"build": {
  "sha": "007b350",
  "run": 39,
  "run_url": "https://github.com/sgort/linked-data-explorer/actions/runs/34339996841"
}
```

`run_url` is the Actions run's `html_url`; the header links the build id there,
and the staleness script checks the run carries that SHA and run number. Each
component also records `ci_repo` — the repository its deploys run in, GitHub or
GitLab — which is where every commit link on the site points.

It is the **frontend build that was serving the recorded environment when the
recorded commit was current** — a different fact from `version`, because a new
build can reach ACC or PROD without a release bump, and the reader can compare
this string with the build line the running application prints. See Stage 2c for
how to derive it. Omit it for components with no build id (Norm Editor, CPRMV).

Supporting infrastructure (already in place — do not rebuild it):

| File | Role |
|---|---|
| `hooks/repo_versions.py` | `on_config` hook loading `repo-versions.json` into `config.extra.repo_versions`, deriving each component's `commit_base` from its `repo_url` so stamps can link any commit |
| `hooks/kpi_charts.py` | Renders `docs/data/ictu-assessments.yml` wherever a page leaves a `<!-- ictu:scores\|totals\|movement\|heatmap\|changes\|tests\|testgates -->` placeholder — tables and inline SVG, styled by the `.ictu-*` rules in `docs/stylesheets/extra.css`. Inline SVG rather than a chart library: no third-party script origin to add to the CSP work, and Material's palette carries into dark mode |
| `scripts/stamp-staleness.py` (in this skill) | Reports, per stamped page and component, the CI-relevant commits on the branch of record since the stamp; exits 1 on a malformed stamp |
| `overrides/partials/doc-meta.html` | Renders the header |
| `overrides/main.html` | `content` block override — renders the header first, suppresses the bottom `source-file.html` for opted-in pages |
| `docs/stylesheets/extra.css` | `.doc-meta*` rules |

The `content` block mirrors Material's own `partials/content.html`. If a
Material upgrade changes that file, re-check the override.

---

## Stage 0 — Locate inputs

1. Confirm the docs repo root is the current working directory and the component
   source repo is reachable (default `../ttl-editor`). If the user linked it
   elsewhere, ask for the path.
2. Confirm the changelog file exists.
3. **Confirm _this_ repository is not stale — before anything else.**
4. **Confirm the component clone is not stale.**

!!! danger "Fetch the documentation repository too — it is the one you are standing in"
    Stage 0 has always checked the *component* clone. It said nothing about
    `iou-architectuur` itself, and that is the gap that bit hardest, because a
    stale docs clone is invisible: every page reads plausibly, `mkdocs serve`
    renders happily, and `repo-versions.json` shows versions that look like
    findings rather than like your own staleness.

    **It has happened.** On 29 August 2026 an RBA sync ran from a clone **5
    commits behind `origin/acc`**. It missed a completed CPSV Editor sync to
    v2026.08.3, then *reported that component as two releases adrift* — a
    fabricated finding, defended twice, and only settled when the user compared
    the live site against localhost. The branch was cut from the stale `acc`, so
    the work also had to be rebased afterwards, resolving six conflicts in files
    that had been edited on both sides in the meantime.

    So, first command of the run, before reading a single page:

    ```bash
    git fetch --quiet origin
    git status -sb | head -1              # "behind N" ⇒ stale
    git log --oneline acc..origin/acc     # what you have not seen
    ```

    Where even a fetch is unwelcome — a dry run, or another agent mid-write in
    this tree — compare against the remote without writing a ref:

    ```bash
    git ls-remote origin refs/heads/acc refs/heads/main
    git rev-parse origin/acc origin/main   # differs ⇒ your refs are stale
    ```

    That is the same trick the component-staleness box below offers, and it is
    strictly better evidence: it reads the remote's live answer instead of one a
    fetch has just written.

    If it is behind, **stop and tell the user before pulling** — and branch from
    `origin/acc`, never from a stale local `acc`. Two failure modes follow from
    skipping this, and the second is the expensive one:

    - the sync duplicates work already done, and
    - **it silently reverts it.** The stale clone's `repo-versions.json` still
      carried the *old* CPSV version, so committing it would have rolled that
      component's recorded version backwards on the live site.

    A version on the front page that looks wrong is far more often this than a
    real gap. Rule out your own clone before reporting drift in anyone's repo.

!!! danger "A stale clone makes `version-gap.py` confidently wrong"
    The script reads the changelog from the **working tree**. If the local
    checkout is behind its remote, it compares the docs against an old changelog
    and reports `in_sync: true` for a component that is several releases ahead.
    This is silent: there is no error, no warning, and the JSON looks healthy.

    It has happened. In the v2026.08.3 sync the local `ttl-editor` checkout was
    **93 commits behind `origin/acc`** and still carried `1.10.6`, while the docs
    already recorded `v2026.08.1`. The script reported `in_sync: true`. Only the
    absurdity of `latest_version` being *older* than `documented_version` gave it
    away — and that tell will not always be there.

    So, always:

    ```bash
    git -C ../<component-repo> fetch --all --prune
    git -C ../<component-repo> status -sb | head -1     # "behind N" ⇒ stale
    ```

    If it is behind, **stop and ask the user before pulling** — a pull mutates a
    repository this skill does not own. Alternatively, read the changelog from the
    remote ref without touching the working tree, which is always safe:

    ```bash
    git -C ../<component-repo> show origin/acc:src/data/changelog.json > /tmp/changelog-acc.json
    ```

    `acc` is the branch of record for these components. Do not compute a gap
    against `main`.

    Sanity check regardless of what the script says: if `latest_version` is not
    newer than `documented_version`, something is wrong with the *inputs*, not
    with the docs.

## Stage 1 — Compute the version gap

Run the helper (deterministic, no judgement):

```
python .claude/skills/iou-document-patch/scripts/version-gap.py --json
```

It reports:
- `documented_version` — from `repo-versions.json`
- `roadmap_top_version` — cross-check from `changelog-roadmap.md`
- `latest_version` — newest in the source changelog
- `gap_versions` — ordered oldest→newest list of versions to document
- `gap_entries` — the full changelog `sections`/`items` for each gap version

If `in_sync` is true, tell the user the docs are already current and stop.

Sanity-check that `documented_version` and `roadmap_top_version` agree. If they
disagree, surface it — the docs may be internally inconsistent and the user
should decide the true baseline before proceeding.

## Stage 2 — Analyse & plan (present, then STOP)

For **each** gap version, read its `gap_entries` sections and classify every
change into the perspective(s) it belongs to. Use the section content, not just
the title — one changelog section can touch several perspectives.

**Perspective routing heuristics:**

- **developer** — always. Every gap version gets a new `### vX.Y.Z` entry at the
  top of `changelog-roadmap.md`, and the **Completed** roadmap table gains a row
  for any newly-shipped roadmap-level capability. Implementation-level changes
  (helper/function/file names, new tests, refactors) also update the relevant
  deep page: e.g. `dmn-implementation.md`, `vocabulary-configuration.md`,
  `triplydb-publish-implementation.md`, `project-structure.md`.
- **features** — a user-visible capability changed or was added. Map to the
  matching page: `dmn-orchestration.md`, `rules-policy-parameters.md`,
  `triplydb-publishing.md`, `import-export.md`, `service-organisation-legal.md`,
  `vendor-integration.md`, `dso-import.md`.
- **reference** — vocabulary / namespace / data-model / field-mapping / standards
  changed: `namespace-property-reference.md`, `data-model-diagrams.md`,
  `external-standards.md`, `field-mapping.md`, `rpp-architecture.md`,
  `ronl-ontology.md`, `semantic-mediation-architecture.md`. (E.g. a CPRMV
  version selector or shape change is a reference change.)
- **user-guide** — the how-to workflow a user follows changed: `dmn-workflow.md`,
  `dmn-testing.md`, `filling-in-the-tabs.md`, `publishing-to-triplydb.md`,
  `import-export-ttl.md`, `getting-started.md`, `dso-import.md`,
  `vendor-integration.md`.

**Detect prior partial documentation first.** Some gap versions may already be
*partly* documented — a dedicated deep page and/or a temporary "scoped callout"
on the home page can be added ahead of a full sync (e.g. `cprmv-dataset-generation.md`
plus a *"documented on three pages; the rest is not yet updated"* admonition on
`docs/en/index.md` + `docs/nl/index.md`). Before planning, grep the docs for the
gap version numbers and their key terms:

```
grep -rn "1\.10\.[3-6]\|<key-term>" docs/en/cpsv-editor docs/en/index.md
```

**Scope the grep to the component's own tree, as above — never to `docs/`.**
Under CalVer the version numbers collide: `2026.09.6` is a released version of
the CPSV Editor *and* of the Linked Data Explorer *and* of the RONL Business API.
A repository-wide grep for a gap version returns mostly other components'
releases — 19 hits, none of them relevant, in one real run — and reading those as
"prior partial documentation" leads to cross-linking another product's release
notes.

For each hit: **cross-link** to the existing deep page from the changelog entry
rather than duplicating it, and mark any temporary scoped callout for **removal**
in Stage 3 (its premise — "the rest isn't updated yet" — is exactly what this
patch invalidates).

Match the **existing voice** of each page (read it before planning an edit):
feature/reference/user-guide pages are prose in present tense describing current
behaviour, not a running changelog. Fold new behaviour into the description as if
it had always been there; the changelog-roadmap page is the only place that keeps
per-version history.

Produce a **change plan** as a table: `version → perspective → file → summary of
the edit`. Then build the **screenshot manifest** (Stage 2b). Present both, then
**stop and ask for approval and metadata** (Stage 2c). Do not edit yet.

### Stage 2b — Required-screenshots manifest

Screenshots are referenced as
`![Screenshot: <caption>](../../assets/screenshots/cpsv-editor-<slug>.png)` inside
a `<figure markdown>` block with a matching `<figcaption>`. The real files live
in `docs/assets/screenshots/` (language-neutral assets served at the site root;
**not** `docs/en/assets/screenshots/`, which holds unrelated placeholders).

Determine, for the gap:
- **NEW** — a change introduces UI the docs will describe but no screenshot yet
  exists for (a new tab control, dialog, panel, badge). Propose a filename slug
  and the page(s) that will embed it.
- **REPLACE** — an existing screenshot now shows stale UI because the change
  altered that view (e.g. a new toolbar control changes the DMN tab header, so
  `cpsv-editor-dmn-tab.png` must be re-shot).

Check which referenced files actually exist:

```
ls docs/assets/screenshots/
```

Write the manifest to **`screenshot-manifest/<component-slug>-screenshots-todo.md`**
(committed) with one row per screenshot: status (NEW/REPLACE), filename, embedding
page(s), caption, and the reason/version that triggered it. This is a deliverable
in its own right — the user captures these separately.

!!! important "Keep manifests out of `docs/`"
    The manifest is an operational artifact, **not** documentation content. Write
    it under the root `screenshot-manifest/` folder, never under `docs/` — any
    loose `.md` in the MkDocs source tree that isn't in the `nav` produces a
    "not included in the nav configuration" warning on `mkdocs serve`/`build`.
    The screenshots themselves still go in `docs/assets/screenshots/`.

!!! invariant "Every manifest entry must map to a real `<figure>`"
    A screenshot only belongs in the manifest if a page **embeds** it. So:

    - A **NEW** row obliges you to add a `<figure markdown>` block for it during
      Stage 3 (the `.png` won't exist yet — that's fine, the manifest tracks
      capture). Never document a NEW screenshot's change as prose-only *and*
      still list it: either add the figure, or drop the row.
    - A **REPLACE** row must name an existing embedding page.

    A NEW entry with no embedding page is a defect — it promises a screenshot the
    docs never ask for. Decide per change whether the UI warrants a figure at
    all; if not, cover it in prose and **omit it from the manifest**.

### Stage 2c — Ask for repo-versions.json metadata

`repo-versions.json` records what the home-page doc-status admonition shows. The
CPSV Editor entry needs: `version`, `commit` (short hash + `…`), `commit_date`
(ISO), `environment` (`acc`/`prod`), `repo_url` (full commit URL). The top-level
`docs_built` date also updates.

Auto-derive sensible defaults first, then ask the user to confirm or override:

```
git -C ../ttl-editor log -1 --format="%h %cd" --date=short
```

Present defaults (target version = newest gap version; commit + date from the
command; `docs_built` = today; keep the existing `repo_url` base) and ask the
user to confirm each field. The user is the authority on version, environment,
and the exact commit that was deployed.

!!! warning "`environment` is a fact to establish, not a field to carry over"
    Do not default it to whatever the entry already says. Check where the gap
    version actually is: `git -C ../<repo> rev-parse --short origin/main` against
    the branch the changelog was read from. **A gap version that exists only on
    `acc` cannot be recorded as `prod`** — carrying the old value forward
    publishes a false claim on the home page's status admonition. It is also a
    reason to ask whether to sync at all: the user may prefer to wait for the
    promotion, or to document it as `acc` and re-stamp after.

**Also derive the `build` field** for components that have a build id (CPSV
Editor, Linked Data Explorer, RONL Business API). It is the latest successful
*frontend deploy* push run on the environment's branch whose commit is the
recorded commit **or an ancestor of it**:

```bash
gh api "repos/sgort/<repo>/actions/runs?branch=<main|acc>&event=push&per_page=40" \
  --jq '.workflow_runs[] | select(.name|test("Frontend|PROD|static";"i"))
        | select(.conclusion=="success")
        | "\(.name) | #\(.run_number) | \(.head_sha[0:7]) | \(.html_url)"'
```

!!! danger "Do not put `status=success` in the URL — it answers from a stale page"
    Filter on `.conclusion` in the `jq` instead. On 24 September 2026 the URL
    form returned *Deploy Frontend to Acceptance* **#146 at `234a9ac`** — a build
    from 30 August — while the same query without `status=success` returned
    **#395 at `9c58737`**, the actual `acc` head. Following the URL form writes a
    month-old build id into `repo-versions.json`, which the header then links and
    `stamp-staleness.py` is asked to reconcile.

    Sanity-check the answer before recording it: the chosen `run_number` should
    be the **highest** for that workflow name, and its `head_sha` should be the
    recorded commit or an ancestor of it (`git merge-base --is-ancestor`).

Expect the build's SHA to differ from the recorded commit sometimes, and record
it anyway: the frontend workflow is path-filtered, so a commit that touched only
the backend or CI produces no build, and the environment keeps serving the older
one. Two workflows can share an environment branch (the CPSV Editor's acc and
prod Static Web Apps files) — pick the one that deploys the recorded environment.

### Stage 2d — Testing documentation

**Every component gets a `developer/testing.md` page.** A great deal of work
has gone into test coverage across these repositories, and the documentation
site is the **single source of truth** for it: repo-side test docs
(`docs/TESTS.md`, `docs/TESTING-GUIDE.md` and equivalents) are being retired.

Consequences:

- **Write the page self-contained.** Do not cross-link repo-side test docs as
  the authority, and do not send readers there for detail — they are going
  away. Fold in what is worth keeping.
- **Do not update the repo's own test docs.** They are out of scope.

!!! danger "Run every command; never copy figures from repo docs"
    Repo-side test docs drift badly — in the CPSV Editor sync they understated
    one file by 9 tests, omitted a whole 12-test suite, and claimed no coverage
    report existed. **Every number on the page must come from a command you
    actually ran in this session.**

    1. Run the full suite (e.g. `npm run test:ci`) and record suites, tests,
       pass/fail, and wall-clock time.
    2. Run **each** scoped/phase script individually and record its counts —
       this also proves the script works and its pattern still matches.
    3. Get authoritative per-file counts from the runner's own JSON reporter
       (e.g. `--json --outputFile=…`), not by grepping for `it(`, which
       miscounts multi-line and parameterised cases.
    4. Capture the coverage table if the runner produces one.
    5. Run the lint/format commands too, and read the git hooks
       (`.husky/*`) to state exactly what is gated — say so plainly if the
       hooks do **not** run the tests.

    State the version and date the figures were measured against, so a future
    reader knows how stale they are.

!!! danger "E2E coverage is derived from the spec directory, never from the changelog"
    Everything above concerns unit suites, which a release usually mentions. The
    end-to-end suites are different, and they have been documented wrongly three
    times: **a spec can be added in a release you are not syncing, and then no
    changelog entry will ever point at it.**

    **It has happened.** `infra-board-journey.spec.ts` and
    `rip-r21-journey.spec.ts` landed on 24 August 2026. Two subsequent syncs ran
    without noticing, and the docs recorded the Infra-board as having *"no
    end-to-end coverage at all"* in three separate places — while the second
    spec's own header read *"infra-board-journey covers the shell; this covers
    the work."* The second of those syncs even put the seven passing tests into
    one page's table and left the contradiction standing two files away. The user
    found it.

    So every run, list the directory rather than reasoning from the release:

    ```bash
    git -C ../<repo> ls-tree -r --name-only acc | grep 'e2e/.*\.spec\.ts'
    ```

    **An empty result is a legitimate answer, not a broken glob.** The Linked
    Data Explorer has no Playwright suite at all; its `e2e-fixtures/` hold BPMN,
    DMN and form bundles, not specs. Say so on the page rather than hunting for
    a directory that does not exist — and do not import the RONL Business API's
    per-board attribution rules into a component with nothing to attribute.

    Then **run the suites and count with the runner**, because a static count is
    wrong in both directions:

    - a single parameterised `test(` can run five cases —
      `login-redirect.spec.ts` does exactly that, so `grep -c` said 1 where the
      runner said 5;
    - a `test.skip(true, reason)` **inside a test body** is a runtime skip, not a
      skipped declaration, and a grep reads it as one.

    In the 30 August measurement a static grep gave **23** and the runner gave
    **27**, against docs claiming **19**.

**Attribute E2E tests per board or surface, and make one page own the table.**
A suite of cross-cutting specs (`login-redirect`, `protected-route`,
`tenant-isolation`, `smoke`) belongs to no single board, so a per-board sum will
not reach the total — and if each per-board page keeps its own figure, they drift
apart. Put one table on the E2E page, have every per-board page link to it, and
state the cross-cutting row explicitly so the arithmetic is legible. Caseworker
had been counting four cross-cutting specs towards itself, which is how twelve
became two with no test removed.

**Some suites need a stack this skill may not start.** Where a Playwright config
has no `webServer`, it needs services running, and the working rules forbid
starting them. Ask the user to bring the stack up rather than reporting the suite
as unmeasurable — one request turned two "not re-run" rows into measured ones.
Where a suite *does* declare `webServer`, check the ports are free first so
Playwright's own server cannot collide with one the user is running.

**A failing E2E suite is not a finding until you know what it needed.** Three of
six public-site tests failed on timeouts; all three needed search results, the
site's `VITE_API_URL` pointed at a backend that was not listening, and the same
specs passed 6/6 once it was up. Re-run serially first to rule out contention,
then check the suite's environment dependencies, and only then call it a defect.

Page structure that worked well:

| Section | Contents |
|---|---|
| At a glance | Suites, tests, pass state, runtime |
| Running the tests | Every command in a table with its measured counts, plus copyable examples and any gotchas (watch mode not exiting, coverage pinning) |
| Linting, formatting, git hooks | What each does and what is actually gated |
| Test inventory | Per-file: count, mocking style, what it covers — grouped by layer/phase |
| Coverage | Measured percentages by area and per module, with an honest reading of what the headline number means |
| Defects the tests found | Real bugs surfaced by writing them |
| Documented behaviour | Couplings locked in by assertions rather than silently patched |
| Adding tests | Conventions — colocation, splitting, phase scripts, where to mock |
| Roadmap | Remaining phases and what is deliberately out of scope |

### Stage 2e — Cross-cutting contributor documentation

**In a component sync, do not perform this stage — queue it** (see *Establish the
mode first*). Read the checks below anyway: they tell you what counts as a
cross-cutting fact, which is what the queue entry has to capture. Then leave
`docs/{en,nl}/contributing/**` untouched, leave every `verified:` stamp exactly as
it is, and write what you found into `cross-cutting-queue.md`.

**In the weekly pass this stage is the work itself** — Stage 6 runs it in full,
over all components at once.

Everything above is component-scoped. `docs/en/contributing/**` is not, and that
is exactly why it goes stale unnoticed: it describes the tooling across **all**
components at once, so a change in any one of them can falsify a sentence that
never mentions that component by name. These pages carry no `component:` front
matter, so nothing flags them as in-scope.

**The stage is not optional and not tidying.** It has been skipped before, with
consequences:

- The CI test gates added on 20 August 2026 — across three repositories, in
  three releases — invalidated every claim in `code-standards.md`'s CI section.
  Three consecutive runs of this skill updated the component pages correctly and
  left that section describing a world that no longer existed.
- In the v2026.08.3 sync, `code-standards.md` still said RONL Business API had
  **six** workflows when `acc` carried **nine**; `skills-and-boundaries.md` still
  said `~/.claude/CLAUDE.md` held **nine** rules when it held **ten**; and
  `working-with-claude-code.md` named **two** plugins when **six** were
  installed. None of those sentences mentions the component that falsified them.

!!! important "Some releases are *mostly* a contributing-docs change"
    Classify the gap before planning. A release made of CI, supply-chain,
    release-process, tooling or repository-policy work has almost no component
    surface — its real footprint is `docs/en/contributing/**`, and the component
    pages are the *smaller* half of the job. Do not let the four-perspective
    routing in Stage 2 make such a release look thin. If most changelog entries
    are typed `ci`, `chore` or `docs`, this stage is the main event.

#### Start from the stamps

Before reading any page, run the stamp report. It needs the clones fetched
(Stage 0 does that; or pass `--fetch`):

```bash
python .claude/skills/iou-document-patch/scripts/stamp-staleness.py
```

For every stamped cross-cutting page it lists, per component, the commits on the
branch of record that touched CI-relevant paths since the stamp — workflows,
hooks, `SECURITY-PIPELINE.md`, `renovate.json`, runner and lint configs. Those
commit subjects are the first evidence for the table below: a page with commits
against it is a page to re-read against source, and the subjects usually say
which claim moved (`docs: record that scan gates acc, in the three places that
claimed otherwise` is a page going stale in its own words).

Zero commits since a stamp means no CI-relevant path changed, **not** that the
page is right — it may have been wrong when stamped. And an unstamped page has no
baseline at all: read it in full.

#### The page-by-page staleness table

| Page | Goes stale when |
|---|---|
| `contributing/code-standards.md` | CI steps, git hooks, a lint/format/test script name, the number of workflows, or which packages are gated changes in **any** repo |
| `contributing/supply-chain.md` | A repository adopts (or has not yet adopted) digest pinning, the `audit` gate, Renovate or an `acc` ruleset; a pinned digest, a zizmor version or an exception in `SECURITY-PIPELINE.md` changes |
| `contributing/index.md` | A repository is added or renamed, or its issue tracker or local-development page moves; a branch gains protection that changes how a contributor lands work |
| `contributing/development-workflow/overview.md` | The pipeline's shape changes — a stage added, removed, or reordered; how a release lands changes |
| `contributing/development-workflow/working-with-claude-code.md` | **A plugin is installed, removed, enabled, disabled, or changes scope**; session-memory tooling or the TDD/subagent workflow changes |
| `contributing/development-workflow/skills-and-boundaries.md` | **A `~/.claude/CLAUDE.md` rule is added or promoted**, or a project-level command/skill is added, moved or removed, or a plugin changes scope. Note it states the rule **count** — re-count it, every time |
| `contributing/development-workflow/design-and-handoff.md` | The handoff package's shape or its route into the repo changes |
| `contributing/doc-architecture/*.md` | This site's own stack, hosting or build changes — those pages describe the documentation repository itself |

#### Required checks

**1. Read the sources, never the prose.** The CI section was rewritten by
enumerating all fourteen workflow files across the three repositories; doing that
surfaced three facts the old text never had. Editing the one sentence that looks
wrong will leave the four beside it that also are.

For repository tooling, read on the **`acc` branch of each repo**, not the local
working tree, which may be on a feature branch or stale:

```bash
git -C ../<repo> ls-tree -r --name-only acc | grep -E '^\.github/|renovate|SECURITY-PIPELINE|\.husky'
git -C ../<repo> show acc:.github/workflows/<file>.yml
git -C ../<repo> show acc:package.json
```

Where a claim is about a GitHub setting rather than a file — branch protection,
required checks, bypass actors — verify it with `gh`, not from prose:

```bash
gh api repos/<owner>/<repo>/rulesets --jq '.[] | "\(.name) \(.target) \(.enforcement)"'
gh api repos/<owner>/<repo>/rulesets/<id> --jq '[.rules[] | {type, checks:(.parameters.required_status_checks//null|if .==null then null else map(.context) end)}]'
```

**2. Re-derive the assistant-tooling pages from `~/.claude/`.** Two pages
describe the assistant itself, and both drift silently because nothing in a
component repository changes when the assistant's configuration does:

```bash
grep -c '^## ' ~/.claude/CLAUDE.md                      # the rule COUNT — the page states it
grep -n '^## ' ~/.claude/CLAUDE.md                      # which rules, in order
python3 -c "import json;d=json.load(open('$HOME/.claude/plugins/installed_plugins.json'));\
[print(k, e['scope'], e.get('version')) for k,v in d['plugins'].items() for e in v]"
python3 -c "import json;print(json.load(open('$HOME/.claude/settings.json')).get('enabledPlugins'))"
```

Three traps in that data, all of which have produced wrong documentation:

- **Installed ≠ enabled.** A plugin can be present in `installed_plugins.json`
  and absent from `enabledPlugins`. Document what is *enabled*.
- **Scope matters and can change.** The same plugin can appear twice — once
  `project`, once `user`. A promotion from project to user scope leaves the old
  project entry in place; the user entry is the one that governs. A scope change
  is itself worth documenting, because it is the concrete illustration of the
  user-versus-project rule the page is built around.
- **Enabled ≠ working.** A plugin may need an external binary. Check before
  claiming a capability — `typescript-lsp` needs `typescript-language-server` on
  the `PATH` and is inert without it.

**3. Two greps that have both caught real drift:**

```
grep -rniE "no test|not run|never run|only .* (has|one)|neither lint nor" docs/en/contributing/
grep -rniE "azure-[a-z-]+|Static Web Apps|pre-push|pre-commit|lint-staged|zizmor|renovate|ruleset" docs/en/contributing/
```

The second matters more than it looks: these pages name CI jobs and git hooks
without naming the component they belong to, so a component-scoped search never
surfaces them.

**4. Re-count every counted claim.** Where a page counts things — *all three
repositories*, *nine rules*, *six workflows*, *the two custom capabilities*, *the
only package that…* — count them again against the source. A release that adds a
fourth of something turns an exhaustive claim into a false one **without touching
a single word in the sentence**, which is why re-reading the prose never catches
it.

---

## Stage 3 — Apply (only after approval)

Work in this order so a failure leaves the docs in an obvious half-state:

1. **`changelog-roadmap.md`** — insert a `### vX.Y.Z — <headline> (<Month Year>)`
   block per gap version, newest first, above the current top entry. Use the
   existing entry style (bold lead-ins, backticked identifiers, `---` between
   versions). The heading level follows the page: `##` where the entries are
   top-level (RONL Business API), `###` where they sit under a `## Changelog`
   parent (Linked Data Explorer). Where the page has one — the CPSV Editor and
   the RONL Business API do, the Linked Data Explorer does not — add rows to the
   **Completed** roadmap table for newly-shipped
   roadmap-level items; if a Planned item shipped, remove/relocate it.
2. **feature / reference / user-guide pages** — apply the prose edits from the
   plan, matching each page's voice. Add or adjust `<figure>` blocks for
   screenshots per the manifest (the `.png` may not exist yet — the reference is
   correct and the manifest tracks capture).
3. **Retire stale scoped callouts** — remove any temporary "only partially
   documented / status table not yet updated" admonition on `docs/en/index.md`
   and `docs/nl/index.md` that this sync makes untrue (see Stage 2). Keep the
   deep pages they linked to.
4. **What's New card** — update the component's grid card in `docs/en/index.md`
   (version token in the `**<icon> <Name> — vX.Y.Z** · *Month Year*` heading, the
   date, the headline `**...**`, the summary paragraph, and links). Before touching
   `docs/nl/index.md` too, check it actually has a mirrored "What's New" section —
   a fully-placeholder NL home page may not carry that section at all, in which case
   there is nothing to sync there.
5. **NL pages** — for real translations (`due-diligence.md`) apply the
   corresponding edit; for placeholders, only sync mirrored section headers if
   the EN page structure changed.
6. **`developer/testing.md`** — create or refresh it from the figures measured
   in Stage 2d, and add a `mkdocs.yml` nav entry plus an NL placeholder if the
   page is new. Update any page that repeats a now-stale testing claim — the
   due-diligence review in particular tends to carry a "no automated tests"
   assessment that a coverage push invalidates.
7. **The cross-cutting queue** — in a component sync, this step is *not* editing
   the contributing pages. Append to `cross-cutting-queue.md` at the repository
   root, under a heading for this sync (date, component, version range), one
   bullet per cross-cutting fact: what changed, the evidence for it (the
   changelog entry, or the source file and what it says), and which page it bears
   on. Write the "nothing cross-cutting surfaced" sentence if that is the truth.
   Do not touch any `verified:` stamp: a stamp records a re-check, and there was
   none.

   **In the weekly pass (Stage 6) this step is the edit itself** — apply every
   correction found in Stage 2e, verifying each against the source (workflow YAML
   on `acc`, `.husky/*`, `package.json`, `gh api .../rulesets`,
   `~/.claude/CLAUDE.md`, `~/.claude/plugins/installed_plugins.json`) rather than
   against the prose being replaced.

    **Do this before the cosmetic steps below, not after.** It used to be step
    10 and was the step that got dropped when a run ran long — three consecutive
    syncs left these pages stale. If a new cross-cutting page is warranted
    (a topic that spans every component, such as the supply-chain gate), create
    it under `docs/en/contributing/`, add a `mkdocs.yml` nav entry, and add an
    NL placeholder with mirrored `##` headers. Cross-cutting pages get **no**
    `component:` front matter — the metadata header renders one component's
    version, which would be wrong on a page about all of them.

    **Then update each re-checked page's `verified` stamp** — today's date, and
    the commit you read for each component whose claims on that page you
    re-checked (see *The `verified` stamp* above). A page you edited without
    re-checking a component keeps that component's old entry, or none.

8. **Front matter** — add `component: <Name>` to **every** *component* page
   created or edited in this patch, EN and NL, placeholders included (see
   *Per-page metadata header*). Easiest as one sweep at the end over the file
   list. Skip `docs/en/contributing/**` and the home page.
9. **`screenshot-manifest/<component-slug>-screenshots-todo.md`** — write the
   manifest (root folder, **not** under `docs/`). If the gap warrants no
   screenshots at all, say so explicitly in the manifest with the reasoning,
   rather than leaving the file untouched — a silent no-op is indistinguishable
   from a forgotten step on the next run.
10. **`repo-versions.json`** — set the component's `version`/`commit`/
    `commit_date`/`environment`/`repo_url`, its `build` where it has one, and
    the top-level `docs_built` to the user-confirmed values.

## Stage 4 — Verify & report

1. Re-run `version-gap.py` — it should now report `in_sync` (roadmap top ==
   documented == latest). **For RONL Business API use
   `scripts/ts-changelog.js --latest` instead**, and compare the three by hand:
   `repo-versions.json`'s entry, the top version heading in
   `changelog-roadmap.md` (`##` or `###` — match the page, see Stage 3 step 1),
   and the shim's answer. All three must agree.
2. **Manifest consistency** — confirm every manifest filename is embedded in at
   least one page (enforces the Stage 2b invariant):

   ```
   for img in <slugs from the manifest>; do
     echo "$img -> $(grep -rl "$img" docs/en | wc -l) page(s)"
   done
   ```

   Every row must report ≥ 1. A `0` means a NEW entry has no `<figure>` — add the
   figure or drop the row.
3. **Metadata header** — confirm the header rendered and the bottom aside did
   not survive on an opted-in page, and that a page you did *not* touch still
   renders the stock bottom dates:

   ```
   grep -c 'aside class="doc-meta"' site/<component>/<some-edited-page>/index.html   # 1
   grep -c 'md-source-file'        site/<component>/<some-edited-page>/index.html   # 0
   grep -c 'md-source-file'        site/<component>/<untouched-page>/index.html     # 1
   ```

4. If `mkdocs` is available, offer a build check. Use a **non-strict** build and
   scan the warnings — do **not** use `--strict`, which fails on the NEW
   screenshots this patch intentionally references before they are captured:

   ```
   mkdocs build 2>&1 | grep -i warning
   ```

   The only image warnings should be exactly the **NEW** manifest files (the not-
   yet-captured `.png`s). Any warning about a missing `.md` target or an existing
   screenshot is a real broken link — fix it.
5. **Cross-cutting claims** — *weekly pass only; in a component sync you changed
   none of these pages, so verify instead that you changed none:*

   ```
   git status --short docs/en/contributing docs/nl/contributing   # must be empty
   ```

   An unexpected hit is almost always a stamp refreshed out of habit. Revert it:
   a stamp asserts a re-check that did not happen.

   In the weekly pass, re-read whatever you changed under
   `docs/en/contributing/` against the source one last time, and confirm no
   *neighbouring* sentence in the same section still describes the old state.
   The failure mode here is a half-corrected section, which reads as
   authoritative while being wrong.

   Then re-run the counted claims specifically, because these are the ones that
   survive a careful re-read:

   ```
   grep -rniE "\b(two|three|four|five|six|seven|eight|nine|ten)\b (repositor|workflow|rule|plugin|package|capabilit)" docs/en/contributing/
   ```

   Every hit must be re-verified against the source, not against your memory of
   having just edited nearby.

   Then re-run the stamp report. Every component you re-checked on a page must
   now show **0 CI-relevant commits since** its stamp, and the script must exit 0
   — a non-zero exit is a malformed stamp (unquoted SHA, unknown component,
   unresolvable commit) or a recorded `build` contradicting its GitHub run.
   Report every warning: *triggered no successful deploy run* means the stamp
   cannot be followed to a build; *not on any origin/\* branch* means the header
   link 404s until that commit is pushed.

   ```
   python .claude/skills/iou-document-patch/scripts/stamp-staleness.py
   ```

6. **Anchors and nav** — cross-references between contributing pages are
   deep-linked more often than component pages are. A non-strict `mkdocs build`
   reports a bad anchor only at INFO level, so grep the built HTML for each
   anchor you linked to:

   ```
   grep -c 'id="<anchor>"' site/contributing/<page>/index.html      # must be 1
   ```

   Any new page must appear in `mkdocs.yml`'s `nav`, or the build warns that it
   is not included.

7. Report a summary: gap closed, files changed grouped by perspective, the
   screenshot manifest path with NEW/REPLACE counts, and the metadata written.
   **Then the cross-cutting half**, in its own paragraph, worded for the mode you
   are in:

   - *Component sync*: what you queued in `cross-cutting-queue.md` — each fact
     and the page it bears on — or the explicit statement that this release
     surfaced nothing cross-cutting. Name the file, and say the pages themselves
     were deliberately not touched and no stamp was refreshed.
   - *Weekly pass*: what was corrected **and what was checked and found correct**
     — "verified, no change needed" is a result, and its absence from a report is
     how a skipped stage hides.

   Then list what still needs a human: capturing screenshots and translating any
   NL pages left as placeholders.
8. Run the **sibling drift check** below and report it, whatever it says.

---

## Stage 5 — Sibling drift check

A run is scoped to one component. `repo-versions.json` and the home page's
What's New grid are **not** — they show every component at once, so a sibling
that shipped since its own last sync sits on the front page displaying a stale
version, and nothing in a single-component run would notice.

Do this **only after Stage 0 has confirmed this clone is current.** Run against
a stale clone it reports fiction, and the fiction is convincing: it names real
components and plausible version numbers. That is exactly how the 29 August run
produced a false "CPSV Editor is two releases behind".

!!! danger "Fetch every sibling before reading it, and check what its remote is called"
    A sibling clone is stale far more often than the docs are wrong, so an
    unfetched read manufactures drift findings that look entirely real. **Two of
    the five produced a false reading in a single run** on 5 September 2026:

    - **CPRMV** reported as drifted. Its only remote is named **`gitlab`**, not
      `origin`, so `git fetch origin` was a silent no-op, `origin/main` was a
      months-old leftover ref, and the *recorded* commit did not exist locally at
      all — the recorded commit was **newer** than local `main`. After fetching
      `gitlab`, it was exactly in sync, 0 commits behind.
    - **Norm Editor** read as `2026.07.1` before the fetch and `2026.09.1` after
      — the drift was real but understated by two months.

    So, first:

    ```bash
    for r in ttl-editor linked-data-explorer ronl-business-api editor cprmv; do
      [ -d "../$r/.git" ] || continue
      echo "== $r: $(git -C ../$r remote | tr '\n' ' ')"
      git -C ../$r fetch --all --prune --quiet
    done
    ```

    Then read from a **remote-tracking ref** — `<remote>/acc`, not the local
    `acc`, and never `rev-parse main`, which reads whatever the local branch
    happens to point at. Substitute the remote name the loop printed; it is not
    `origin` everywhere.

| Component | Read the shipped version from |
|---|---|
| CPSV Editor | `git -C ../ttl-editor show origin/acc:package.json` → `version` |
| Linked Data Explorer | `git -C ../linked-data-explorer show origin/acc:packages/frontend/src/changelog.json` → first `versions[]` |
| RONL Business API | `git -C ../ronl-business-api show origin/acc:packages/frontend/src/pages/changelog-data.ts` → first `version:` — TypeScript, so use the shim in `scripts/ts-changelog.js` rather than `json.loads` |
| Norm Editor | `git -C ../editor show origin/main:gui/public/changelog.json` → first non-`Unreleased` `releases[]`. **Its releases live on `main`, not `acc`**, though `repo-versions.json` records the environment as `acc` — check both and say which you read |
| CPRMV | Its remote-tracking ref for `main`, against the recorded `commit`. **Read the remote's name first** (`git -C ../cprmv remote`) — it has been `gitlab` in one clone and `origin` in another, and the wrong name makes `rev-parse` fail or, worse, answer from a months-old leftover ref |

Read from a **ref**, never the working tree — a sibling repo is very often
parked on a feature branch, and its working tree will answer confidently and
wrongly. On Windows/Git Bash, `git show <ref>:<path>` needs `MSYS_NO_PATHCONV=1`
or the argument is mangled into a Windows path.

**Report, do not act.** A drifted sibling is a *finding*, not a licence to widen
the run: syncing it properly means its own changelog reading, per-perspective
plan, screenshot manifest and approval. Say which components have drifted and by
how many releases, and let the user decide.

Distinguish two cases, because they need different fixes: an entry merely
*behind*, versus one *wrong about its environment*. The Norm Editor is currently
the second kind.

## Stage 6 — The weekly pass (cross-cutting pages + the ICTU series)

Runs on **Sundays**, over all three applications at once, and reads no component
changelog. It has two deliverables that belong together: the contributing pages
re-checked against source, and one new point in the assessment series that the
same re-check produced.

**It edits `docs/{en,nl}/contributing/**` and `docs/data/ictu-assessments.yml`,
and nothing else** — with one exception, `docs_built` in `repo-versions.json`,
which dates the documentation rather than any component. A component's `version`,
`commit` or `build` never moves in this pass; that is a component sync's job.

### 6a — Inputs

1. Stage 0's freshness checks, for this repository and for **all three** clones
   (`../ttl-editor`, `../linked-data-explorer`, `../ronl-business-api`). Branch
   from `origin/acc`.
2. **Pin the heads and write them down**: `git -C ../<repo> rev-parse --short
   origin/acc` for each. Every score, every count and every stamp in this pass is
   read at those three commits, and they are what the page and the data file
   record. Never mix a head from the fetch with a figure read yesterday.
3. **Drain `cross-cutting-queue.md`** — the facts component syncs parked since the
   last pass. Each entry is a lead, not a finding: verify it against source now,
   then strike it from the file in this pass's commit. An entry you cannot verify
   stays, with a note saying why.

### 6b — Re-check the pages

Run **Stage 2e in full** — the stamp report first, then the page-by-page
staleness table, the required checks, the re-count of every counted claim, and the
re-derivation of the assistant-tooling pages from `~/.claude/`. That stage is
written for this pass; nothing here replaces it.

### 6c — Score the assessment

The scores live in `docs/data/ictu-assessments.yml` and every table and chart on
`docs/en/contributing/ictu-dependency-guideline.md` is generated from it by
`hooks/kpi_charts.py`. **Add one entry; never edit a published earlier entry**
except to correct a demonstrated error, and say so when you do.

The rubric and the interpretation of each recommendation come from the assessment
of record — `docs/ICTU-dependencies-assessment.md` on the Linked Data Explorer's
`acc`. Read it before scoring, so this week's judgement matches earlier weeks'.

Entry shape, all of it required:

```yaml
  - date: 2026-09-27          # the Sunday
    kind: measured            # or: reconstructed, for a backfilled week
    heads: {TTL: <sha>, LDE: <sha>, RBA: <sha>}
    note: >-
      One or two sentences on what the week was about.
    scores:
      TTL: [ ... 11 integers, R1..R11 ... ]
      LDE: [ ... ]
      RBA: [ ... ]
    changes:                  # one per cell that moved, in either direction
      - {component: LDE, recommendation: R9, from: 3, to: 4,
         why: "What changed, named concretely enough to check."}
```

Then refresh the `tests:` rows for the same Sunday — test files, end-to-end
specs, workflows running a suite, and whether a per-file coverage floor is
configured — counted from the tree at those same heads. These feed the companion
chart, which exists because the guideline scores dependency management and says
almost nothing about whether the code works.

**Score what the source enforces today, not what was worked on.** Configuration
that has not yet had its first scheduled run is configured, not enforced. A count
that grew is evidence for a cell, not a cell.

### 6d — Present, and stop

**The scores are judgement, and the user owns them.** Present, before editing the
data file:

- the per-component table: new score, last week's, the delta, per recommendation;
- one line of evidence per moved cell;
- **every cell where a stricter reading would score lower**, with both readings
  and what each would make the total. These are the cells the published page has
  to be honest about, and the user decides them.

Then stop for approval, as in Stage 2.

### 6e — Apply and verify

Apply the page corrections, the stamps (today's date, the three pinned heads,
naming only components you actually re-checked on that page), and the new entry.
Then, on top of Stage 4's checks:

```bash
venv/Scripts/python.exe - <<'PY'
import sys, yaml; sys.path.insert(0, "hooks")
import kpi_charts as k
d = yaml.safe_load(open("docs/data/ictu-assessments.yml", encoding="utf-8"))
order = [r["id"] for r in d["recommendations"]]
prev = None
for e in d["assessments"]:
    for c, s in e["scores"].items():
        assert len(s) == len(order), (e["date"], c, len(s))
    if prev:
        moved = {(c["component"], c["recommendation"]) for c in e.get("changes", [])}
        for c in e["scores"]:
            for i, rid in enumerate(order):
                delta = e["scores"][c][i] - prev["scores"][c][i]
                if delta and (c, rid) not in moved:
                    print("MISSING reason", e["date"], c, rid)
                if not delta and (c, rid) in moved:
                    print("SPURIOUS reason", e["date"], c, rid)
    prev = e
    print(e["date"], e["kind"], {c: sum(s) for c, s in e["scores"].items()})
for name in k.RENDERERS:
    k.RENDERERS[name](d)
print("all renderers ok")
PY
```

Every score that moved must carry its reason and every reason must correspond to
a move. Then build, and confirm the page holds the generated charts rather than
the placeholders:

```bash
grep -c 'class="ictu-chart"' site/contributing/ictu-dependency-guideline/index.html   # 4
grep -c 'ictu:'              site/contributing/ictu-dependency-guideline/index.html   # 0
```

A surviving `<!-- ictu:… -->` means the hook did not run — check `mkdocs.yml`'s
`hooks:` list. An admonition saying the data could not be read means the YAML is
malformed; the hook degrades rather than failing the build, deliberately.

### 6f — Report

The per-component totals and the week's deltas, what moved and why, which
judgement calls the user settled and how, what was corrected on the contributing
pages **and what was checked and found correct**, which queue entries were drained
and which remain, and the three heads everything was read at.

## Guardrails

- **Splice by index, never with a string replacement.** `String.prototype.replace`
  with a *string* as its second argument expands `$&`, `$'`, `` $` `` and a dollar sign followed by a
  digit in the text being inserted. (That last one is spelled out on purpose: this
  skill's own loader substitutes a literal dollar-digit with an argument, which is the
  same class of bug a third time.) On 11 September 2026 a changelog entry that *quoted* `$'` —
  it described exactly that bug in the Linked Data Explorer's BPMN modeler — pasted
  the rest of the document into itself, taking the page from 1,240 lines to 3,739.
  Slice at `indexOf` and concatenate, or pass a function (`() => text`), and compare
  line counts before and after every splice.

- **Staged, not one-shot.** Always present the Stage 2 plan and stop for
  approval before any edit.
- **Fetch this repository first, and branch from `origin/acc`.** A stale docs
  clone is silent, duplicates finished work, reverts `repo-versions.json`, and
  manufactures drift findings about components that are perfectly in sync. Rule
  out your own clone before reporting a gap in anyone's repo.
- **A run is scoped to one component; the home page is not.** Always finish with
  the Stage 5 sibling drift check, and report it even when clean.
- **Do not invent code behaviour.** Every doc claim must trace to a changelog
  entry (or, if verifying, to the actual `../ttl-editor` source). If a changelog
  item is ambiguous, read the referenced source file before writing.
- **Code is leading. Docs follow.** When an existing page asserts something the
  source does not support, the claim is **deleted** — not preserved out of
  deference to whoever wrote it, not softened into a hedge, and not carried
  forward through a rewrite just because it was already there. This applies
  with most force to security, compliance, privacy, and certification claims,
  where a reader may act on the statement: in one pass a component's Features
  pages claimed BSN encryption and compliance with named standards, neither
  supported by the source, and both were removed.
- **This licenses contradicting the brief.** If the source disagrees with an
  orientation note, an assumption, or an instruction given for the task, follow
  the source and say so — that is expected behaviour, not insubordination. In
  one pass three separate subagents correctly overrode orientation notes
  because the source said otherwise.
- **Respect the i18n rule** — never turn an NL placeholder into a half-English
  page; leave placeholders as placeholders unless the user asks for translation.
- **repo-versions.json values come from the user**, not from guesses.
- **Establish the mode before Stage 0, and stay inside it.** A component sync
  that edits a contributing page has widened itself; a weekly pass that edits a
  component page or bumps a component's version in `repo-versions.json` has done
  the same. Both make a reviewer read a diff that does not match its title. If
  the other half turns out to be needed urgently, say so and let the user decide
  — do not annex it.
- **A component sync is not finished at the component boundary; it is finished
  when the boundary is recorded.** The cross-cutting pages describe every
  component at once and carry no `component:` front matter to flag them as
  in-scope. They were left stale by three consecutive syncs of this skill, which
  is why deferral is only legitimate when it is written down: a queue entry per
  cross-cutting fact, or the sentence saying this release had none.
- **Never refresh a `verified:` stamp you did not earn this run.** A stamp says a
  human-checkable claim was re-read against a named commit on a named date. In a
  component sync you re-read none of them, so every stamp stays exactly as it is
  — including on a page you would swear is unaffected.
- **Verify the inputs before trusting the tooling.** `version-gap.py` is
  deterministic but only as good as the working tree it reads. A stale clone
  makes it report `in_sync` for a component that is releases ahead. Fetch first;
  read from the remote `acc` ref when in doubt.
- **The assistant's own configuration is documented content.** Plugins, their
  scopes, and the rules in `~/.claude/CLAUDE.md` are described on two pages of
  this site. They change without any component repository changing, so nothing
  else in this skill will surface the drift. Re-derive them from `~/.claude/`
  every run — never from the pages themselves, and never from memory.
