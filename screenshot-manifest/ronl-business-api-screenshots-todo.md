# RONL Business API — screenshots to capture

!!! warning "Two captures outstanding — reviewed 30 September 2026 for v2026.09.15"
    Rows 11 and 12 below, both on the Caseworker board and both behind sign-in, so
    maintainer steps. Row 12 is **NEW**: until it is captured a non-strict
    `mkdocs build` reports exactly one missing image, `ronl-business-api-caseworker-process-overlay.png`.
    Rows 9 and 10 from v2026.09.13 were replaced in `19fc36c` on 28 September 2026.

## Sync v2026.09.13 → v2026.09.15 — one REPLACE, one NEW

Reviewed on 30 September 2026 for **v2026.09.14** and **v2026.09.15**, both in
production. One change has a surface a figure already shows, and one adds a view
worth its own figure — both on the Caseworker board:

| # | Status | File | Embedding page | What it must show | Trigger |
|---|---|---|---|---|---|
| 11 | ⬜ **REPLACE** | `ronl-business-api-caseworker-board.png` | `user-guide/caseworker.md` | A task whose process is drawn in lanes and marked with `ronl:awbPhase`: the "Awb-fase" hint in the Taken list, *Waar sta ik* with the eight-phase stepper, the folded **Procesgegevens** bar, and *Processtappen per rol*. The current capture (19 August) shows the expanded Procesgegevens table and a flat English step list. | v2026.09.14 — the process view (`45a0a1c`, `5a6e418`, `0ae18b5`) |
| 12 | ⬜ **NEW** | `ronl-business-api-caseworker-process-overlay.png` | `user-guide/caseworker.md` | The process overview modal for the same task: full stepper, *Hoofdproces › Deelproces* breadcrumb, legend and the swimlane scrolled to the task's node. | v2026.09.14 — `ProcessOverlay` (`45a0a1c`) |

**Capture on acceptance, with a model that has lanes and markers.** The view only
appears for a process whose deployed BPMN is drawn in lanes, and the stepper
needs `ronl:awbPhase` markers. On 30 September 2026 such models exist on the Linked
Data Explorer's `acc` (`dec2359`) and not yet on its `main`, so production tasks
show the flat list. Deploy a marked model to acceptance first.

**Considered and not captured:** the citizen `StartFailureNotice` (an error state,
described in prose), the link-preview cards (they live in other apps' unfurls, not
on this site), and the `/v1/m2m` changes (no surface).

## Sync v2026.09.12 → v2026.09.13 — two REPLACE, no NEW

Reviewed on 28 September 2026 for **v2026.09.13**, an **acceptance** release. Of
the thirteen changelog entries, eleven have no product surface at all — a
provisioning script, a cache key, two npm scripts, a git hook and the end-to-end
harness. Two changes are visible, and both land inside a figure this site
already embeds.

**Neither row needs a new `<figure>` block.** Both files are already referenced
by their embedding page, so nothing has to be added to the docs during Stage 3 —
these are re-captures of existing figures, and the Stage 2b invariant (every
manifest entry maps to a real `<figure>`) is satisfied by the blocks already
there.

| # | Status | File | Embedding page | What it must show | Trigger |
|---|---|---|---|---|---|
| 9 | ✅ **REPLACE** (`19fc36c`) | `ronl-business-api-rip-phase-swimlane.png` | `user-guide/infra-board.md` | The same R2.2 *Voorlopig Ontwerp (VO)* swimlane, with **two** document badges under *Opstellen concept VO* — **Ontwerptoelichting** *and* **Objectenboom** | v2026.09.13 |
| 10 | ✅ **REPLACE** (`19fc36c`) | `ronl-business-api-landing-page.png` | `user-guide/getting-started.md` | The werkomgeving landing page with its hero's **primary button reading "Inloggen met uw Flevoland-account"**, *Bekijk de borden* beside it as the secondary action, and the note below reading *"Met het account waarmee u op uw werkplek bent aangemeld"* | v2026.09.13 |

### Why item 9 is a REPLACE and not a leave-alone

The existing capture was checked rather than assumed. It is the **R2.2** phase,
and its *Opstellen concept VO* node carries exactly **one** badge,
`Ontwerptoelichting`. That is precisely the task this release changes: the R2.2
model's `ronl:documentRef` became `rip-ontwerptoelichting,rip-objectenboom`, and
the board now renders one badge per document. The current image therefore shows
the pre-change state of the exact frame the release is about — the strongest
case a REPLACE row can have.

**Capture notes**

- **Same view, same framing.** `/dashboard/infra-board` → a project in R2.2 →
  the phase swimlane, at the width of the existing capture so the two read as
  one series on the page.
- **After the acceptance redeploy.** The fixture change reaches the engine with
  a redeploy; a capture taken from a stale definition will still show one badge,
  which is the defect rather than the fix.
- **The two badges must both be legible** at the page's rendered width. If they
  are not, crop to the *Ontwerper* lane rather than shrinking the whole diagram.
- It sits behind sign-in, so this is a maintainer step.

### Why item 10 is a REPLACE

The four board cards the caption names are unchanged — but the hero above them
is the page's primary control, and it now says something different. *Bekijk de
borden* went from the `btn-primary` anchor to a `btn-secondary` one; the new
`btn-primary` is a sign-in button; and the note beneath changed from *"Inloggen
vereist via medewerkersaccount"* to *"Met het account waarmee u op uw werkplek
bent aangemeld"*. A reader arriving at `getting-started.md` to find out how to
get in is looking straight at the part of the frame that is wrong.

**Capture notes**

- **Capture in Dutch.** The existing capture is Dutch — a known inconsistency
  with the English public-site capture, recorded further down this file — and
  the new button text is Dutch, so a re-shot in Dutch both matches the series
  and shows the string the prose quotes.
- **Capture from acceptance**, `https://acc.mijn.open-regels.nl`. v2026.09.13 is
  not promoted; production still serves v2026.09.12 and would show the old hero.
- **Include the hero and the four cards in one frame**, as the current capture
  does, so the caption still holds.
- **Sign out first.** The landing page is the signed-out view.

### Declined, and why

Recorded so the next review does not re-open them.

| Change | Why no figure |
|---|---|
| The Entra provisioning script (`8e36b93`) and the lower-casing fix (`328f502`) | Terminal output — a list of created mappers and a redirect URI. The runbook quotes both. |
| The `IOU_USERS` role mapping (`39176bd`) | A value in a table on two pages. Nothing spatial. |
| The Caseworker-card redirect fix (`1ae2b94`) | A routing outcome: the same card leads somewhere else. A still image of the card before and after is identical. |
| Deployed-BPMN caching by definition id (`36eb5a5`) | Invisible in the right direction — it makes a *correct* diagram appear where a stale one did. A still cannot show "after a redeploy". |
| `e2e:deploy-fixtures`, `check-swimlane-fixtures` (`b4c3176`, `71b76a9`, `4d0dc73`, `dfa325a`, `2bdff69` in part) | Terminal scripts and a git hook. |
| `check-previews` carriage returns (`80e34a2`) | A shell script's exit status. |

**The Keycloak login page's Flevoland button was considered and is not
requested.** It is a fallback path — the landing-page button is how an employee
actually signs in — and `ronl-keycloak-custom-theme.png` already shows that page
with its provider buttons. A second capture of it would document the route
nobody takes.

---

## Sync v2026.09.11 → v2026.09.12 — nothing to capture, one figure retired

Reviewed on 26 September 2026. The release's frontend changes are not visual — the
BSN dropped from a console message in `brp.api.ts`, a username instead of the claims
object in a `bsn.mapping.ts` log, a constant format string in `SectionErrorBoundary.tsx`,
and a `nosemgrep` comment in the public site's search. The OpenAPI description renders
live on the new API Specification page, so it needs no image. Tenant access, the SBOM,
the daily audit, the lockfile check and the pinned compose images have no surface.

**Retired, not replaced:** `ronl-business-api-health-check.png` on
`developer/local-development.md` showed the pre-CalVer `/v1/health` shape
(`version: "1.0.0"`, a `services` block). The rewritten page shows the response as a
code block instead, which cannot drift from the text around it. The file stays in
`docs/assets/screenshots/` until nothing references it; the archived pages do not.

## Sync v2026.09.9 → v2026.09.11 — one NEW, several declined

Reviewed on 24 September 2026 for **v2026.09.10** and **v2026.09.11**. Of the
twenty-eight commits across the two releases, twenty-five have no user-visible
surface at all — they are CI, deployment, supply-chain and end-to-end-harness
work. One change is visible, and it earns a figure.

| # | Status | File | Embedding page | What it must show | Trigger |
|---|---|---|---|---|---|
| 8 | ⬜ **NEW** | `ronl-business-api-public-site-begrippen-io.png` | `user-guide/public-site.md` | A **rule's detail page** at `publiek.open-regels.nl`, scrolled to its concepts, with the chips **divided into two headed groups** — *Invoer — gegevens die de regels nodig hebben (n)* and *Uitvoer — wat de regels bepalen (n)* — each heading carrying its own count | v2026.09.11 |

### Why this one is worth capturing

The change is a *layout* claim, and layout is what a screenshot settles and a
sentence does not. Before v2026.09.11 a rule's concepts were one alphabetical
row of chips; now they are two labelled groups with counts. Prose can say that;
it cannot show a reader what to look for, or that the section heading and its
total are unchanged above the split.

### Capture notes

- **Pick a service with concepts on both sides.** A service whose concepts all
  fall on one side renders a single group, which is exactly the state this
  figure exists to distinguish from — and a reader comparing it with their own
  screen would conclude the feature had not shipped.
- **Capture from production**, `https://publiek.open-regels.nl`. Production was
  promoted to v2026.09.11 on 23 September 2026, so it serves this. The page
  carries no environment badge, so an acceptance capture cannot be told apart
  afterwards.
- **Include the section heading and its total**, not only the chips. The point
  is that the total is unchanged and the chips beneath it are now divided.
- Any concept the graph leaves undirected appears in a third group. That is
  correct behaviour and does not disqualify a capture — but a frame without one
  is the cleaner illustration.

### Declined, and why

These are recorded so the next review does not re-open them.

| Change | Why no figure |
|---|---|
| The promotion workflow (`3bc93f1`) | An Actions run is not product UI. A screenshot of it dates on the next run and says less than the ordering diagram already on `deployment/backend.md`. |
| The backend deploying over OIDC (`e3c7dd6`) | No surface. The one reader-visible artefact is `/v1/health`'s `build` block, which is a JSON payload and belongs in prose. |
| Preview opt-in by label (`32ddf67`) | The control is a GitHub label on a pull request, not part of either application. |
| `check-previews` / `set-secret.sh` (`ae83054`, `3636ecd`) | Terminal scripts. Their output is a list of names and a byte count. |
| The process-instance attribute on `TakenInbox` (`91195ac`) | Invisible by design — a `data-` attribute added so an end-to-end helper can resolve its own instances. It changes no pixel. |
| Everything in the end-to-end harness | Test infrastructure, covered by `developer/testing/e2e.md`. |

**No REPLACE rows.** Nothing in this gap alters a view an existing screenshot
shows: the public process listing, the four boards, the login and form captures
and the PA demo frames are all unaffected.

---

## Sync v2026.09.7 → v2026.09.9 — one NEW, one declined

Reviewed on 20 September 2026 for **v2026.09.8** and **v2026.09.9**. Most of the
thirty-two commits are CI, dependency and callback work with no surface at all;
two changes are visible, and only one of them earns a figure.

| # | Status | File | Embedding page | What it must show | Trigger |
|---|---|---|---|---|---|
| 7 | ✅ captured 20 Sep 2026 | `ronl-business-api-public-site-processen.png` | `user-guide/public-site.md` | The **public process library listing** at `publiek.open-regels.nl`, with **several processes visible** and each one carrying its **status label** (`example` / `wip` / `e2e`) beside its name. The listing view, not a detail page — the label appearing in the list is the whole point | v2026.09.9 |

### Why this one is worth capturing

It is the only genuinely new piece of visible interface in the gap, and it
carries two claims at once that prose states less convincingly than an image
does. First, the library **is no longer empty**: until v2026.09.9 it filtered on
a status value the underlying catalogue cannot hold, so production listed
nothing at all — a reader who remembers an empty page needs to see a populated
one. Second, the status label now sits **in the listing**, not only on a
process's own page, which is exactly the kind of "where on the screen" claim a
screenshot settles and a sentence does not.

### Capture notes

- **Capture from production**, `https://publiek.open-regels.nl`, not from a dev
  server or from acceptance. Production is the tier that showed nothing before,
  and the page carries no environment badge, so an acceptance capture would be
  indistinguishable and would understate the fix.
- **Show the listing with more than one row**, so the labels read as a column of
  states rather than as a one-off badge.
- **Mixed status values are better than uniform ones** if the data offers them —
  the point is that the label distinguishes, so two identical labels prove less
  than two different ones.
- Use the site's **English** setting, via the NL/EN toggle, to match
  `ronl-business-api-public-site.png` on the same page.
- Match the framing and width of `ronl-business-api-public-site.png`, which sits
  directly above it on the page.
- No sign-in is needed. This is a public, unauthenticated surface, so it does not
  need to be handed to the maintainer the way the board captures did.

### Declined, with the reason rather than silence

**The R2.1 start fields** (v2026.09.8) — *R2.1 starten* on the Infra-board phase
page now asks for **Projectnummer** and **Projectnaam** before it will start a
process. This was considered and **is not requested**, for three reasons taken
together rather than any one of them alone:

- The interface is **two labelled text inputs above a button**. There is nothing
  spatial, no state to disambiguate, and no layout a reader could misconstrue —
  `user-guide/infra-board.md` names both fields, says both are required, and
  says the button stays disabled until they are filled. An image would restate
  that and add nothing.
- It sits **behind sign-in** on acceptance, so capturing it costs a maintainer's
  authenticated session — a real price, worth paying for something prose cannot
  carry, and not for this.
- `user-guide/infra-board.md` already carries **two figures** for a page that is
  ACC-brief by convention. A third, of a form, would outweigh the text around
  it.

If it is ever added, the state worth showing is the button **disabled with one
field filled**, since the disabled-until-both-filled behaviour is the only part
of it a reader could be surprised by.

**Everything else in these two releases is invisible.** The ValidSign callback
now accepts `Basic` as well as `Bearer`; `deps:check` parses the lockfile rather
than comparing mtimes; `.nvmrc`, `.npmrc`, `ubuntu-24.04`, the `changes` jobs and
the five new required checks are workflow YAML and a ruleset. The board's live
rows refreshing on tab-focus (v2026.09.8) is a *timing* change — the same rows,
sooner — and a still image cannot show "without a page reload".

**Nothing needs a REPLACE.** `ronl-business-api-public-site.png` shows the
landing page with its combined search and five source cards, none of which
moved; the process library is a section reached *from* it.
`ronl-business-api-infra-board.png` shows the board overview, while the start
fields are on a phase detail page; and `ronl-business-api-rip-phase-swimlane.png`
is untouched by either release.

---

## Sync v2026.09.5 → v2026.09.7 — nothing to capture

Reviewed on 12 September 2026 for **v2026.09.6** and **v2026.09.7**. Eleven of the
nineteen commits are CI work, and the rest change what a view *says* rather than how it
looks:

- **The CI alignment** — the `acc` ruleset's two new rules, `check-supply-chain` blocking,
  formatting in the `audit` job, Semgrep, Renovate's lock-file maintenance, `.nvmrc`, the
  mirror check — is workflow YAML, `renovate.json`, a ruleset and two scripts. Nothing on
  screen.
- **The build id** now appears under the changelog heading and in the public site's footer.
  It is one line of monospace text whose value differs per deployment, so a screenshot
  would date instantly and prove nothing a quoted string does not. Both pages quote it.
- **The prerendered seed fix** changes *when* the numbers on the public site are correct,
  not what the page looks like. A capture of the wrong counts would be a capture of the
  defect, which the docs describe rather than depict.
- **The unmodelled-phase removal** deletes an error path that no input could reach any
  more. The Faseladder already reads `12 / 12 deelprocessen inzetbaar`, and
  `ronl-business-api-infra-board.png` was recaptured for exactly that in the last sync.
- **`@ronl/pa-cockpit` running in CI** and the backend suite's pull-request trigger are
  pipeline facts.

`ronl-business-api-public-site.png` still shows the site accurately: the footer gained a
build id, which sits below the fold of that capture and is quoted in the text beside it.

## Sync v2026.08.36 → v2026.09.5 — one NEW, one REPLACE (both captured)

Reviewed on 5 September 2026 for the six-version gap covering **v2026.09.0**
through **v2026.09.5**. Unlike the two preceding entries, this release does
change what a reader sees, so there are rows — **both captured the same day**,
and a non-strict `mkdocs build` now reports no missing-image warning at all.

| # | Status | File | Embedding page | What it must show | Trigger |
|---|---|---|---|---|---|
| 1 | ✅ **DONE** (was NEW) | `ronl-business-api-rip-phase-swimlane.png` | `user-guide/infra-board.md` | A phase diagram **derived from deployed BPMN** — lanes with their names, per-task colouring (todo / active / done), and at least one **rework loop** routed in its own band below the lane rows. Ideally a phase other than R2.1, since R2.1 is the one phase whose diagram looked correct before this work | v2026.09.4 |
| 2 | ✅ **DONE** (was REPLACE) | `ronl-business-api-infra-board.png` | `user-guide/infra-board.md` | The board with the **Faseladder reading `12 / 12 deelprocessen inzetbaar`**. The current capture predates the ladder being complete and shows the old count | v2026.09.3 |

**Why item 1 is worth capturing and the signing panel was not.** The previous
entry declined a screenshot because the feature could not be photographed
without firing a real signature against a production-only licence. This one has
the opposite property: the diagram is the whole point of the release, it renders
from data already on ACC, and prose describes it poorly — "lanes, columns, and
rework loops drawn as returns rather than forward steps" is a picture's job.

**Why item 2 is a REPLACE rather than a leave-alone.** The existing capture is
not wrong about anything the board still does; it is wrong about one number that
happens to be the release's headline. The Faseladder badge went from **1 / 12**
to **12 / 12** over v2026.09.0–.3, and that badge is visible in the current
image.

**Not requested, deliberately:**

- **The Ongefilterd segment** (v2026.09.1). It is a third tab beside Gecureerd
  and Inbox on the PA cockpit, and `user-guide/pa-cockpit.md` carries one figure
  of the board. A segment control is legible in prose, and the page is
  ACC-brief by convention — a second figure there would outweigh the text
  around it.
- **The disabled-button fix** (v2026.09.0). A `:disabled` rule so a disabled
  button stops looking live. Real, and not worth an image.
- **Everything in v2026.09.2 and v2026.09.5.** Coverage, a feed-source
  migration, request fan-out and caching — none of it visible.

---

## 2026-08-19 — User Guides restructure (complete)

Generated for the User Guides restructure of 2026-08-19, which split the RONL
Business API user guide into per-board pages. Four new board pages each embed a
screenshot. **All four were captured on 2026-08-19 and are in place.** This
section is retained as the record of what each image shows and why it was
needed.

Real screenshot files live in **`docs/assets/screenshots/`** (language-neutral,
served at the site root). Docs reference them as
`../../assets/screenshots/<file>` inside a `<figure markdown>` block. Capture
each image below at the same framing/width as the existing set and drop it in
that folder — the doc references are already in place.

Legend: **NEW** = no file exists yet · **REPLACE** = file exists but now shows
stale UI.

| # | Status | File | Embedding page | What it must show |
|---|---|---|---|---|
| 1 | ✅ **DONE** (was NEW) | `ronl-business-api-caseworker-board.png` | `user-guide/caseworker.md` | The Caseworker board after sign-in — the personal task list with claims and deadlines |
| 2 | ✅ **DONE** (was NEW) | `ronl-business-api-pa-cockpit-board.png` | `user-guide/pa-cockpit.md` | The PA-Cockpit board — dossier and issue overview showing priority and momentum |
| 3 | ✅ **DONE** (was NEW) | `ronl-business-api-infra-board.png` | `user-guide/infra-board.md` | The Infra-board — phase swimlanes with per-project status |
| 4 | ✅ **DONE** (was NEW) | `ronl-business-api-woo-dashboard-board.png` | `user-guide/woo-dashboard.md` | The Woo-dashboard — compliance figures, traffic lights and the "Woo in cijfers" benchmark |

**Nothing outstanding.** All four were captured by the maintainer on
2026-08-19, while the restructure was still running. Each board sits behind
sign-in, so capture was necessarily a human step — this manifest was the
handover for it, and that handover is complete.

## Notes

- **All four required an authenticated session.** They sit behind sign-in on
  their respective boards and could not be captured headlessly, which is why
  they were handed over rather than automated.
- **The landing-page and public-site captures are already in place.**
  `ronl-business-api-landing-page.png` (embedded in
  `user-guide/getting-started.md`) and `ronl-business-api-public-site.png`
  (embedded in `user-guide/public-site.md`) are both present in
  `docs/assets/screenshots/`.
- **Known inconsistency to flag:** the werkomgeving landing-page capture is in
  **Dutch**, while the public-site capture is in **English**. An English
  werkomgeving re-shot would be preferable for consistency on an English
  page, *if* that interface offers an English mode — the public site has an
  NL/EN toggle, but it is not known whether the werkomgeving does. Do not
  assume it does; confirm before attempting an English re-shot.
- **Expected `mkdocs build` state:** until these four are captured,
  `venv/Scripts/mkdocs.exe build` reports exactly **four** missing-image
  warnings and nothing else. That is the expected steady state for this
  round — any **fifth** warning means something else is genuinely broken and
  should be investigated as such.
- **The archived guides under `user-guide/archive/` need no re-capturing.**
  They keep their own historical screenshots documenting the interface as it
  was at the time; nothing there is affected by this restructure.

## Verification

```bash
for i in caseworker-board pa-cockpit-board infra-board woo-dashboard-board; do
  echo "ronl-business-api-$i -> $(grep -rl "ronl-business-api-$i" docs/en | wc -l) page(s)"
done
```

Each line must report `1`. Confirmed on 2026-08-19:

```
ronl-business-api-caseworker-board -> 1 page(s)
ronl-business-api-pa-cockpit-board -> 1 page(s)
ronl-business-api-infra-board -> 1 page(s)
ronl-business-api-woo-dashboard-board -> 1 page(s)
```

## 2026-08-19 — v2026.08.19 docs sync: no new screenshots needed

This pass (bringing the RONL Business API docs from `v3.9.1` to
`v2026.08.19`) requires **no new screenshots**, by design rather than
oversight:

- The Features pages were rewritten as functional capability descriptions,
  under a rule that they describe capabilities and never name a use case.
  They embed no screenshots at all — a screenshot of a running system
  inherently shows one particular case. Verified directly:
  `grep -rn "\.png" docs/en/ronl-business-api/features/*.md` returns zero
  matches.
- The case-specific screenshots that used to appear on Features pages now
  live only in `features/archive/` and `user-guide/archive/`, alongside the
  pages that reference them. Archived pages keep their historical imagery
  and need no re-capture.
- The four board screenshots captured during the earlier restructure (see
  above) remain in place; nothing outstanding.

---

## 2026-08-29 — v2026.08.33 docs sync: two screenshots, both captured

This pass (bringing the RONL Business API docs from `v2026.08.23` to
`v2026.08.33`) added the public **PA-Cockpit demo** to the User Guides. Both
captures were taken on 2026-08-29 and are in place.

| # | Status | File | Embedding page | What it shows |
|---|---|---|---|---|
| 5 | ✅ **DONE** (was NEW) | `ronl-business-api-pa-demo-plato.png` | `user-guide/pa-demo.md` | The demo cockpit as a visitor first sees it at `acc.plato.open-regels.nl` — the full rail and a populated board, with no sign-in prompt anywhere |
| 6 | ✅ **DONE** (was NEW) | `ronl-business-api-pa-demo-rollen.png` | `user-guide/pa-demo.md` | **Beheer → Rollen & rechten** — the four selectable role positions and the capability table beside them |

### These two are different from every earlier entry

**No authenticated session is needed.** Every previous screenshot in this
manifest sat behind sign-in, which is why they had to be handed to the
maintainer. These two are on a public, unauthenticated site — anyone with the
URL can capture them, and they can be re-shot later without arranging access.

### Capture notes

- **Capture from acceptance**, `https://acc.plato.open-regels.nl`, not from a
  local dev server. The footer carries an `ACCEPTATIEOMGEVING` badge and the
  acceptance hostname; that is the honest state of this surface today, since
  production is not yet stood up.
- **Use the default role.** The demo opens on the broadest of the four
  positions deliberately, and screenshot 5 should show what a visitor actually
  lands on.
- **Screenshot 6 should show a role that is *not* the default selected**, so the
  capability table visibly differs from the landing state — that is the point
  the surrounding prose makes.
- Match the framing and width of the existing board captures
  (`ronl-business-api-pa-cockpit-board.png` is the closest comparator).

### `mkdocs build` state

With both captured, a non-strict build reports **zero** warnings. Any warning at
all now means something is genuinely broken.

### Verification

```bash
for i in pa-demo-plato pa-demo-rollen; do
  echo "ronl-business-api-$i -> $(grep -rl "ronl-business-api-$i" docs/en | wc -l) page(s)"
done
```

Each line must report `1`.

### Nothing needed a REPLACE

The `@ronl/pa-cockpit` extraction was deliberately pixel-preserving — converted
styles use the literal computed values rather than the nearest design token,
precisely so the rendered result did not move. `ronl-business-api-pa-cockpit-board.png`
therefore still shows the current UI, and the other three board captures were
untouched by this release.

---

## 2026-08-30 — v2026.08.36 docs sync: no new screenshots

This pass (v2026.08.33 → v2026.08.36) adds the ValidSign phase-approval signing
feature and requires **no new or replaced captures**, deliberately:

- **The signing panel cannot be photographed usefully without signing
  something.** A representative screenshot would need a real ceremony in flight,
  which on a live tier means a real signature request against a production-only
  licence that cannot be recalled. In stub mode it shows a stand-in ceremony that
  is not what a reader would meet in production, so the image would misrepresent
  the feature either way.
- **The page it lands on is a developer page.** `developer/validsign-signing.md`
  documents routes, guards, configuration and failure modes — none of which is
  visual. The existing developer pages in this section embed no figures either.
- **The Infra-board capture still holds.** `ronl-business-api-infra-board.png`
  shows the board's phase swimlanes, which the signing work did not change. The
  panel replaces a form *inside* a task, not the board view the figure shows.
- **The remaining releases are pipeline and dependency work.** v2026.08.34 and
  v2026.08.35 ship no UI at all.

**If one screenshot were to be added later**, the candidate is the three-way
actions section — claim button, signing panel, ordinary form — since that
distinction is the one thing prose describes less efficiently than an image.
It is deliberately not requested here, because capturing the middle state needs
a claimed signature-bearing task in a state a reader can be shown safely.
