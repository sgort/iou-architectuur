---
name: iou-document-patch
description: Bring the IOU architecture documentation site into sync with the latest documented version of a linked component's code, in a controlled staged manner. Verifies the source clone is current, analyzes the component's changelog.json against what the docs currently record, plans per-perspective doc updates (developer / features / reference / user-guide), and — as a required stage, not optional tidying — updates the cross-cutting contributor documentation under docs/en/contributing/ (CI, git hooks, the supply-chain gate, the release process, the assistant's plugin set and its working boundaries in ~/.claude/), re-counting every counted claim against source. Also builds a required-screenshots manifest, updates the What's New card and repo-versions.json metadata, and keeps EN/NL in sync. Use when the user asks to sync/patch/update the docs to a component's latest version, or invokes /iou-document-patch.
---

# IOU Document Patch

Synchronise the documentation site (`iou-architectuur`) with the latest
**documented version** recorded in a linked component's source changelog. The
default component is the **CPSV Editor**, whose code lives in the sibling
`../ttl-editor` repo and whose per-release notes live in
`../ttl-editor/src/data/changelog.json`.

A sync has **two halves**, and both are required: the component's own pages
(four perspectives, EN/NL, screenshots, `repo-versions.json`), and the
cross-cutting contributor pages under `docs/en/contributing/` that describe the
tooling across *every* component at once. For a release made of CI,
supply-chain, release-process or tooling work, the second half is the larger
one.

The work is **staged**: analyse → present a plan + screenshot manifest → get the
user's approval and the `repo-versions.json` metadata → apply → verify. Never
skip straight to editing docs.

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
| Cross-cutting contributor docs | `docs/en/contributing/**` — **not component-scoped, and easy to miss.** These pages describe the tooling across *all* components at once: CI, git hooks, lint/format scripts, the repository table, the release process, the supply-chain gate, the assistant's plugin set and its working boundaries. A single component's release can falsify them, and they carry no `component:` front matter to flag them as in-scope. **Stage 2e is a required stage, not optional tidying** |
| Assistant-tooling sources of truth | `~/.claude/CLAUDE.md` (working boundaries), `~/.claude/plugins/installed_plugins.json` (what is installed, and at which scope), `~/.claude/settings.json` → `enabledPlugins` (what is actually on), `~/.claude/plugins/known_marketplaces.json`. These are the **only** authority for `development-workflow/skills-and-boundaries.md` and `working-with-claude-code.md` — never restate those pages from memory. See Stage 2e |
| Per-page metadata header | `component:` front matter on every edited/added component page; `scope: cross-cutting` on every `contributing/**` page (see below) |

### Known components beyond CPSV Editor

| Component | Source repo | Changelog | Notes |
|---|---|---|---|
| **Norm Editor** | sibling repo **`../editor`** (confirmed on the Windows workstation at `C:\Users\gorts01\Development\editor`; also seen at `/home/steven/Development/editor` on Linux) | `gui/public/changelog.json`, schema **`{versions: {<service>: <semver>, ...}, releases: [{version, date, changes: {<conventional-commit-type>: [commit, ...]}, commits: [...]}]}`** — git-log-derived, not curated. `version-gap.py` auto-detects this shape (a `releases` array) vs. the curated `versions` array and normalizes both to the same `sections`/`items` shape; it also drops the synthetic `"Unreleased"` pseudo-version. Pass `--changelog <path> --component "Norm Editor"` explicitly. | No `developer/changelog-roadmap.md` existed before the 2026.07.0 sync (create it + add the mkdocs.yml nav entry — don't assume the page is there). Docs currently have **zero** screenshots — don't force a manifest entry for that reason alone. `docs/nl/index.md` is a placeholder with no "What's New" section to mirror at all — check before assuming both `docs/en/index.md` and `docs/nl/index.md` need the card edit. Because the first tag can land long after the code it covers, don't backfill version numbers onto pre-existing features you can't date — only claim what genuinely changed inside the tagged commit range. |
| **Linked Data Explorer** | sibling repo `../linked-data-explorer` | `packages/frontend/src/changelog.json` — a dict with a **`versions`** array, same curated `format: "commits"` shape as the CPSV Editor, plus a per-entry `scope` field (`frontend` / `backend` / `both`, absent on most). **`version-gap.py` works against it unmodified** — pass `--changelog ../linked-data-explorer/packages/frontend/src/changelog.json --component "Linked Data Explorer"`. | Versions switched from SemVer to CalVer mid-history (…, 1.9.12, 1.9.13, 2026.07.0, …), so an ordered gap can span both schemes — the same transition the CPSV Editor made. `repo-versions.json` and the roadmap headings carry a `v` prefix; the changelog does not. **i18n differs from the CPSV Editor**: all 60 EN pages have an NL counterpart, and **three are real translations** — `developer/backend.md`, `reference/api-stability.md`, `user-guide/multilingualism.md` — so check each NL page before assuming it is a placeholder. A screenshot manifest already exists at `screenshot-manifest/linked-data-explorer-screenshots-todo.md`. There is no `developer/testing.md` yet (note `developer/test-cases.md` is a *feature* doc, not the test-suite page). |
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

Supporting infrastructure (already in place — do not rebuild it):

| File | Role |
|---|---|
| `hooks/repo_versions.py` | `on_config` hook loading `repo-versions.json` into `config.extra.repo_versions` |
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
command; `docs_built` = today; keep the existing environment/repo_url base) and
ask the user to confirm each field. The user is the authority on version,
environment, and the exact commit that was deployed.

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

### Stage 2e — Cross-cutting contributor documentation (REQUIRED)

Everything above is component-scoped. `docs/en/contributing/**` is not, and that
is exactly why it goes stale unnoticed: it describes the tooling across **all**
components at once, so a change in any one of them can falsify a sentence that
never mentions that component by name. These pages carry no `component:` front
matter, so nothing flags them as in-scope.

**This stage is not optional and not tidying.** It has been skipped before, with
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
   versions). Add rows to the **Completed** roadmap table for newly-shipped
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
7. **Cross-cutting contributor pages** — apply every correction found in
   Stage 2e, verifying each against the source (workflow YAML on `acc`,
   `.husky/*`, `package.json`, `gh api .../rulesets`, `~/.claude/CLAUDE.md`,
   `~/.claude/plugins/installed_plugins.json`) rather than against the prose
   being replaced.

    **Do this before the cosmetic steps below, not after.** It used to be step
    10 and was the step that got dropped when a run ran long — three consecutive
    syncs left these pages stale. If a new cross-cutting page is warranted
    (a topic that spans every component, such as the supply-chain gate), create
    it under `docs/en/contributing/`, add a `mkdocs.yml` nav entry, and add an
    NL placeholder with mirrored `##` headers. Cross-cutting pages get **no**
    `component:` front matter — the metadata header renders one component's
    version, which would be wrong on a page about all of them.

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
    `commit_date`/`environment`/`repo_url` and the top-level `docs_built` to the
    user-confirmed values.

## Stage 4 — Verify & report

1. Re-run `version-gap.py` — it should now report `in_sync` (roadmap top ==
   documented == latest). **For RONL Business API use
   `scripts/ts-changelog.js --latest` instead**, and compare the three by hand:
   `repo-versions.json`'s entry, the top `## vX.Y.Z` heading in
   `changelog-roadmap.md`, and the shim's answer. All three must agree.
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
5. **Cross-cutting claims** — re-read whatever you changed under
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

6. **Anchors and nav** — cross-references between contributing pages are
   deep-linked more often than component pages are. A non-strict `mkdocs build`
   reports a bad anchor only at INFO level, so grep the built HTML for each
   anchor you linked to:

   ```
   grep -c 'id="<anchor>"' site/contributing/<page>/index.html      # must be 1
   ```

   Any new page must appear in `mkdocs.yml`'s `nav`, or the build warns that it
   is not included.

7. Report a summary: gap closed, files changed grouped by perspective **and a
   separate cross-cutting group**, the screenshot manifest path with
   NEW/REPLACE counts, and the metadata written. State explicitly what was
   checked under `docs/en/contributing/` and found **correct**, not only what
   was changed — "verified, no change needed" is a result, and its absence from
   a report is how a skipped stage hides. Then list what still needs a human:
   capturing screenshots and translating any NL pages left as placeholders.
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
| CPRMV | `git -C ../cprmv rev-parse --short gitlab/main` against the recorded `commit`. **Its remote is `gitlab`** — `main` and `origin/main` are both stale in the usual clone |

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

## Guardrails

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
- **A component sync is not finished at the component boundary.** The
  cross-cutting pages under `docs/en/contributing/` describe every component at
  once and carry no `component:` front matter to flag them as in-scope. They
  have already been left stale by three consecutive syncs of this skill. Treat
  Stage 2e as part of the sync, not as optional tidying — and report on it
  explicitly, including where nothing needed changing.
- **Verify the inputs before trusting the tooling.** `version-gap.py` is
  deterministic but only as good as the working tree it reads. A stale clone
  makes it report `in_sync` for a component that is releases ahead. Fetch first;
  read from the remote `acc` ref when in doubt.
- **The assistant's own configuration is documented content.** Plugins, their
  scopes, and the rules in `~/.claude/CLAUDE.md` are described on two pages of
  this site. They change without any component repository changing, so nothing
  else in this skill will surface the drift. Re-derive them from `~/.claude/`
  every run — never from the pages themselves, and never from memory.
