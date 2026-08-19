# RONL Business API — screenshots to capture (2026-08-19 User Guides restructure)

Generated for the User Guides restructure of 2026-08-19, which split the RONL
Business API user guide into per-board pages. Four new board pages each embed a
screenshot. **All four were captured on 2026-08-19 and are in place — nothing is
outstanding.** The file is retained as the record of what each image shows and
why it was needed.

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
