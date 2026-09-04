---
component: CPSV Editor
---

# Deployment

---

## Environments

| Environment | URL | Branch |
|---|---|---|
| Production | https://cpsv-editor.open-regels.nl | `main` |
| Acceptance | https://acc.cpsv-editor.open-regels.nl | `acc` |

All changes go to `acc` first. After acceptance testing, they are merged to `main` for production deployment.

---

## CI/CD pipeline

Three workflows live in `.github/workflows/`. The two deploy workflows are
structurally identical, differing only in target branch, Azure token and
backend URL.

| Workflow name | File | Target | Purpose |
|---|---|---|---|
| **Deploy ACC (orange-beach)** | `azure-static-web-apps-orange-beach-0574c2a03.yml` | `acc` | Build, test and deploy acceptance |
| **Deploy PROD (white-sky)** | `azure-static-web-apps-white-sky-02b674303.yml` | `main` | Build, test and deploy production |
| **Supply-chain audit** | `zizmor.yml` | every PR; pushes to `acc`/`main` | Job name `audit` — the required status check |

Both deploy workflows were called `Azure Static Web Apps CI/CD` until v2026.09.0,
with both jobs named `Build and Deploy Job`. A production run was therefore
indistinguishable from an acceptance one in the Actions list and in `gh run list`.
They now say which environment they are. Renaming a job renames the check it
reports, so it was done before any deploy check is made required.

A deploy is also skipped entirely for documentation-only changes —
`paths-ignore` covers `docs/**`, `.claude/**` and `**/*.md`. That is a denylist
on purpose: an allowlist would mean enumerating every path that affects the
build, and anything forgotten from it would *silently skip a deploy*, which is
worse than one unnecessary preview.

A deploy workflow runs:

```
checkout (persist-credentials: false)
       ↓
setup-node 24  →  npm ci
       ↓
npm run lint  →  npm run test:ci        ← a failure here blocks the deploy
       ↓
Azure/static-web-apps-deploy (builds via Oryx inside its own container)
       ↓
https://cpsv-editor.open-regels.nl      (main)
https://acc.cpsv-editor.open-regels.nl  (acc)
```

Every `uses:` reference is pinned to a commit digest rather than a tag, each
job declares least-privilege `permissions:`, and the checkout step no longer
persists a git credential into the workspace. See
[Supply-Chain Pinning](../../contributing/supply-chain.md) for why, and for
what that hardening deliberately does not cover.

!!! warning "The build that ships is not the build that is tested"
    `npm ci` verifies every package against `package-lock.json`'s integrity
    hashes — but that install feeds lint and the test suite. The deploy action
    does not set `skip_app_build`, so Oryx performs its *own* install and build
    inside the Static Web Apps container to produce the deployed bundle. The
    lockfile governs what is tested, not what is shipped.

---

## Pull request workflow

`acc` is protected by the `acc supply-chain gate` ruleset: it requires a pull
request and a passing `audit` check, with no bypass actors. **A direct
`git push origin acc` is rejected outright** — including for releases, and
including for the repository owner.

1. Create a feature branch from `acc`.
2. Make changes and test locally (`npm run test:ci`, `npm run lint`, `npm run check-format`).
3. Push the branch and open a pull request targeting `acc`.
4. The pull request runs `audit` and `Build and Deploy`; the latter produces a
   Static Web Apps preview deployment. Both must be green to merge.
5. Merge — with a merge commit for a release pull request, never a squash,
   because changelog entries cite commits by SHA and squashing orphans every
   citation. Renovate's dependency pull requests are the opposite case and
   should be squashed.
6. Merging *is* the push to `acc`, which triggers the acceptance deploy. Verify
   behaviour on the ACC environment.
7. Open a pull request from `acc` to `main` for production release.

---

## Azure Static Web Apps

The application is deployed as a static site. No server-side rendering is involved. The build output is the `build/` directory produced by `npm run build` (Create React App).

There is no `staticwebapp.config.json` in the repository. Routing and CORS
therefore fall back to the Static Web Apps defaults, and the absence of that
file is also why Oryx builds the app inside the deploy container rather than
uploading a prebuilt artifact.

---

## Environment variables

The frontend has no required environment variables for basic operation. The TriplyDB base URL, account, dataset, and API token are entered by the user at runtime and stored in browser localStorage.

If the optional backend proxy is deployed, its URL can be configured — see the backend documentation in the Linked Data Explorer repository.
