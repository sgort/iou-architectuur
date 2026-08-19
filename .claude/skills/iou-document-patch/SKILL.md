---
name: iou-document-patch
description: Bring the IOU architecture documentation site into sync with the latest documented version of a linked component's code, in a controlled staged manner. Analyzes the component's changelog.json against what the docs currently record, plans per-perspective doc updates (developer / features / reference / user-guide), builds a required-screenshots manifest, updates the What's New card and repo-versions.json metadata, and keeps EN/NL in sync. Use when the user asks to sync/patch/update the docs to a component's latest version, or invokes /iou-document-patch.
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

## Component map

Default target is the CPSV Editor. If the user names a different component,
adapt the paths — the same staging applies.

| Thing | Location |
|---|---|
| Source changelog | `../ttl-editor/src/data/changelog.json` (array of versions, newest first) |
| Documented version of record | `docs/repo-versions.json` → repository named **"CPSV Editor"** → `version` |
| Developer changelog page | `docs/en/cpsv-editor/developer/changelog-roadmap.md` |
| Four perspectives (EN) | `docs/en/cpsv-editor/{developer,features,reference,user-guide}/*.md` |
| Four perspectives (NL) | `docs/nl/cpsv-editor/{developer,features,reference,user-guide}/*.md` |
| Home "What's New" card | `docs/en/index.md` (and `docs/nl/index.md`) — CPSV Editor grid card |
| Screenshots referenced by docs | `../../assets/screenshots/cpsv-editor-*.png` → real files in `docs/assets/screenshots/` (language-neutral, served at site root) |
| Testing page | `docs/en/<component>/developer/testing.md` — the site is the **single source of truth** for test docs (see Stage 2d) |
| Per-page metadata header | `component:` front matter on every edited/added page (see below) |

### Known components beyond CPSV Editor

| Component | Source repo | Changelog | Notes |
|---|---|---|---|
| **Norm Editor** | not a sibling repo — ask the user for its path (seen at `/home/steven/Development/editor`) | `gui/public/changelog.json`, schema **`{versions: {<service>: <semver>, ...}, releases: [{version, date, changes: {<conventional-commit-type>: [commit, ...]}, commits: [...]}]}`** — git-log-derived, not curated. `version-gap.py` auto-detects this shape (a `releases` array) vs. the curated `versions` array and normalizes both to the same `sections`/`items` shape; it also drops the synthetic `"Unreleased"` pseudo-version. Pass `--changelog <path> --component "Norm Editor"` explicitly. | No `developer/changelog-roadmap.md` existed before the 2026.07.0 sync (create it + add the mkdocs.yml nav entry — don't assume the page is there). Docs currently have **zero** screenshots — don't force a manifest entry for that reason alone. `docs/nl/index.md` is a placeholder with no "What's New" section to mirror at all — check before assuming both `docs/en/index.md` and `docs/nl/index.md` need the card edit. Because the first tag can land long after the code it covers, don't backfill version numbers onto pre-existing features you can't date — only claim what genuinely changed inside the tagged commit range. |
| **RONL Business API** | sibling repo `../ronl-business-api` | `packages/frontend/src/pages/changelog-data.ts` — a **TypeScript file**, not JSON: unquoted object keys, mixed single/double-quoted strings, trailing commas, and a `ChangelogItem = string \| FeedbackItem` union mixed into `items` arrays. `version-gap.py`'s `json.loads()` cannot parse it directly, and no safe regex conversion exists (a colon inside changelog prose would get mangled by a naive `key:` → `"key":` transform). **Do not run `version-gap.py` against this component** — manually read the `versions` array in `changelog-data.ts` and compare against `repo-versions.json`'s `"RONL Business API"` entry / the top heading in `developer/changelog-roadmap.md` to compute the gap, until a Node-based `.ts`→JSON shim is built for it. | Version strings carry a `v` prefix in `repo-versions.json` and `changelog-roadmap.md` headings (`v3.9.1`) but not in `changelog-data.ts` itself (`'3.9.1'`) — normalize before comparing. |

### i18n rule (do not violate)

The site uses `mkdocs-static-i18n` with `docs_structure: folder`. EN is the
default with `fallback_to_default: true`. **Most `docs/nl/cpsv-editor/**` pages
are placeholders** (an "Documentatie in ontwikkeling" admonition + mirrored empty
`##` headers + `**Status:** Concept` + `**Engelstalige bron:**`). Only
`docs/nl/cpsv-editor/developer/due-diligence.md` is a full Dutch translation.

Consequences for this skill:
- Write substantive content in the **EN** page.
- Update the **NL** page only when it is a real translation (currently just
  `due-diligence.md`), or when its mirrored section headers must change to match
  a restructured EN page.
- The **What's New** card exists in both `docs/en/index.md` and
  `docs/nl/index.md` — update both.

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
7. **Front matter** — add `component: <Name>` to **every** page created or
   edited in this patch, EN and NL, placeholders included (see *Per-page
   metadata header*). Easiest as one sweep at the end over the file list.
8. **`screenshot-manifest/<component-slug>-screenshots-todo.md`** — write the
   manifest (root folder, **not** under `docs/`).
9. **`repo-versions.json`** — set the component's `version`/`commit`/
   `commit_date`/`environment`/`repo_url` and the top-level `docs_built` to the
   user-confirmed values.

## Stage 4 — Verify & report

1. Re-run `version-gap.py` — it should now report `in_sync` (roadmap top ==
   documented == latest).
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
5. Report a summary: gap closed, files changed grouped by perspective, the
   screenshot manifest path with NEW/REPLACE counts, and the metadata written.
   Explicitly list what still needs a human: capturing the screenshots and
   translating any NL pages left as placeholders.

## Guardrails

- **Staged, not one-shot.** Always present the Stage 2 plan and stop for
  approval before any edit.
- **Do not invent code behaviour.** Every doc claim must trace to a changelog
  entry (or, if verifying, to the actual `../ttl-editor` source). If a changelog
  item is ambiguous, read the referenced source file before writing.
- **Respect the i18n rule** — never turn an NL placeholder into a half-English
  page; leave placeholders as placeholders unless the user asks for translation.
- **repo-versions.json values come from the user**, not from guesses.
