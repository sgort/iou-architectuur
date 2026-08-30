# RONL Business API — screenshots to capture

!!! success "Nothing outstanding"
    Every screenshot this manifest calls for has been captured. The file is
    retained as the record of what each image shows and why it was needed.

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
