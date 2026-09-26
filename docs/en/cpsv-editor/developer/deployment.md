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

Seven workflows live in `.github/workflows/`. Two deploy the application; the
rest audit it, scan it, record what was released, or clean up after a pull
request.

| Workflow name | File | Job (check) | Runs on | Purpose |
|---|---|---|---|---|
| **Deploy ACC (orange-beach)** | `azure-static-web-apps-orange-beach-0574c2a03.yml` | `changes`, `Build and deploy ACC` | pushes to `acc`; pull requests into `acc` | Lint, test, build and deploy acceptance |
| **Deploy PROD (white-sky)** | `azure-static-web-apps-white-sky-02b674303.yml` | `Build and deploy PROD` | pushes to `main`; pull requests into `main` | Lint, test, build and deploy production |
| **Supply-chain audit** | `zizmor.yml` | `audit` | every pull request; pushes to `acc`/`main` | Workflow analysis, Renovate config, lockfile sync, formatting, pin truth |
| **Semgrep** | `semgrep.yml` | `scan` | every pull request; pushes to `acc`/`main` | Semgrep Code and Supply Chain over the source and the npm tree |
| **Close preview environments** | `close-preview-environments.yml` | `Close ACC staging environment`, `Close PROD staging environment` | every pull request closed into `acc` or `main` | Deletes the pull request's Static Web Apps preview |
| **Dependency audit** | `dependency-audit.yml` | `dependency-audit` | daily at 05:17 UTC; on demand; pull requests touching the audit itself | `npm audit` of both `acc` and `main` |
| **Release SBOM** | `sbom.yml` | `release-sbom` | pushes to `main`; on demand; pull requests touching the SBOM tooling | CycloneDX SBOM of the released version |

Every job runs on `ubuntu-24.04` rather than `ubuntu-latest`, so a change of
Ubuntu release arrives as a diff in this repository instead of silently under
every job at once. That label pins the *release*, not the image — GitHub
rebuilds `ubuntu-24.04` about weekly and a hosted runner cannot be pinned to a
digest — which the repository's `SECURITY-PIPELINE.md` records as an accepted
risk.

The deploy jobs are named for the environment they deploy. Required checks
match by job name, so `Build and deploy ACC` can be required on `acc` without
ambiguity, and renaming it means updating the ruleset in the same change. For
the same reason the daily audit's job is `dependency-audit`, not `audit`: a
second job called `audit` would make the required context ambiguous — one
passing and one failing check under one name, which no ruleset can satisfy.

### Which changes deploy

A push to `acc` or `main` that changes only documentation does not deploy.
`paths-ignore` on the push trigger covers `docs/**`, `.claude/**` and
`**/*.md`. That is a denylist on purpose: an allowlist would mean enumerating
every path that affects the build, and anything forgotten from it would
*silently skip a deploy*, which is worse than one unnecessary preview.

Pull requests are filtered differently in each deploy workflow:

- **ACC** has no path filter on its `pull_request` trigger. The workflow always
  starts, and a `changes` job matches the pull request's files against the same
  list; a documentation-only pull request skips the build. A workflow its
  trigger filters out never starts and reports no check at all, so a required
  check would wait forever — whereas a job skipped by its own `if:` reports
  success. The fallback is deliberately fail-safe: the build runs whenever
  `changes` did *not* succeed, so a failed lookup means a full build, never a
  free pass.
- **PROD** keeps `paths-ignore` on both triggers and has no `changes` job.
  Nothing is required on `main`, so a check that never reports blocks nothing.

### What a deploy runs

```
checkout (persist-credentials: false)
       ↓
setup-node (node-version-file: .nvmrc → 24.20.0)  →  npm ci
       ↓
npm run lint  →  npm run test:ci        ← a failure here blocks the deploy
       ↓
Build: npm run build
       with VITE_BACKEND_URL, VITE_BUILD_SHA, VITE_BUILD_RUN
       fails if dist/index.html is missing
       ↓
Azure/static-web-apps-deploy
       app_location: '/dist', skip_app_build: true   (uploads, builds nothing)
       ↓
https://cpsv-editor.open-regels.nl      (main)
https://acc.cpsv-editor.open-regels.nl  (acc)
```

**The install that is tested is the install that ships.** The bundle is built
on the runner, from the tree `npm ci` installed and on the Node the tests just
ran on, and the deploy action uploads `dist/` as it is. The `dist/index.html`
check exists because the deploy action, given an empty or wrong directory,
uploads it and reports success. Before v2026.09.7 the action built the bundle
itself, with Oryx inside its own container, on a Node the repository never
chose; production moved from Oryx's Node 22.22.0 to the `.nvmrc`-pinned 24.20.0
with this release. Renovate's `nvm` manager maintains `.nvmrc`.

Every `uses:` reference is pinned to a commit digest rather than a tag, each
job declares least-privilege `permissions:`, and the checkout step does not
persist a git credential into the workspace. See
[Supply-Chain Pinning](../../contributing/supply-chain.md) for why, and for
what that hardening deliberately does not cover. The deploy action's container
image, `staticappsclient:stable`, still floats and cannot be pinned; it now
only uploads, but still receives the deploy token and the built artifact.

### Dependency audit and release SBOM

Two workflows answer questions about dependencies rather than about a commit.

**Dependency audit** runs daily, because a new advisory lands against code that
has not changed. It audits **both `acc` and `main`** — Dependabot watches only
the default branch, `acc` — reading each branch's lockfile with
`npm audit --package-lock-only`, so it installs nothing. It fails on a **high or
critical advisory in production dependencies**; moderate, low and dev-only
advisories are listed but do not fail it. `scripts/audit-tree.mjs` groups the
report by advisory rather than by package, because one advisory on a widely used
package otherwise reads as dozens of findings. It exits `2` when the audit could
not run at all, and that is handled with the same weight as a finding, never as
a clean tree. Results go to the run summary and to **one tracking issue** the
workflow opens, updates and closes.

**Release SBOM** covers the fact that a promotion to `main` *is* a release here
— there are no tags. `scripts/write-sbom.mjs` writes
`docs/sbom/<name>-<version>.cdx.json`: CycloneDX, production dependencies only,
from the lockfile alone. It has three modes: write (`npm run sbom`, a release
step), `--check` (strict, where the release is cut) and `--verify-release`
(what a promotion asserts: a missing document fails, drift only warns). The
workflow uploads the document as an artifact, kept 90 days — the maximum on a
public repository — so the committed copy is the durable one.

### Supply-chain guards around the install

- **Lockfile sync.** The `audit` job runs a step named *Lockfile matches
  package.json* — `npm ci --dry-run --ignore-scripts` — so a lockfile that
  disagrees with `package.json` fails under its own name. Its stated limit: it
  checks the pull request's merge commit against *that* base, so a pull request
  green against a stale base and merged into a moved one is not caught. Merge
  dependency pull requests one at a time, rebasing each onto the merged `acc`.
- **Cooldown.** The root `.npmrc` sets `min-release-age=14`, so npm will not
  resolve a version published less than 14 days ago — covering lock-file
  maintenance and workstation installs, which Renovate's own 14-day cooldown
  cannot reach. npm 11.10 or newer honours it (Node 24.20.0 bundles 11.19);
  `npm ci` ignores it by design, so CI is neither blocked nor protected by it.
- **Majors.** Renovate never offers an npm package's `X.0.0`, so the earliest a
  major can arrive is its first patch, and majors wait for Dependency Dashboard
  approval. The Ubuntu 26.04 runner major is deferred by a Renovate rule that
  records its reason: `ubuntu-latest` still resolves to 24.04.

---

## Pull request workflow

`acc` is protected by the `acc supply-chain gate` ruleset: it requires a pull
request and three passing checks — `audit`, `scan` and `Build and deploy ACC` —
with no bypass actors. **A direct `git push origin acc` is rejected outright** —
including for releases, and including for the repository owner. `main` requires
a pull request but no status checks, as decided in #131.

1. Create a feature branch from `acc`.
2. Make changes and test locally (`npm run test:ci`, `npm run lint`, `npm run check-format`).
3. Push the branch and open a pull request targeting `acc`.
4. The pull request runs `audit`, `scan` and `Build and deploy ACC`; the last
   produces a Static Web Apps preview deployment, or is skipped — and passes —
   when the pull request changes only documentation. All three must be green to
   merge.
5. Merge with a merge commit. It is the only merge method the repository
   allows: changelog entries cite commits by SHA, and squashing or rebasing
   would orphan every citation.
6. Merging *is* the push to `acc`, which triggers the acceptance deploy. Verify
   behaviour on the ACC environment.
7. Open a pull request from `acc` to `main` for production release.

---

## Azure Static Web Apps

The application is deployed as a static site. No server-side rendering is involved. The build output is the `dist/` directory produced by `npm run build` (Vite), built on the runner and uploaded as-is with `skip_app_build: true`. It was `build/` under Create React App until v2026.09.1 — the deploy workflows and the build changed in the same commit, because that rename cannot be half-applied.

There is no `staticwebapp.config.json` in the repository, so routing and CORS
fall back to the Static Web Apps defaults.

---

## Environment variables

Vite exposes only `VITE_`-prefixed variables to the bundle. `vite build` runs in
production mode, so it loads `.env.production` — for both environments.

| Variable | Set by | Value |
|---|---|---|
| `VITE_BACKEND_URL` | The Build step, per environment, overriding `.env.production` | `https://acc.backend.linkeddata.open-regels.nl` (ACC), `https://backend.linkeddata.open-regels.nl` (PROD) |
| `VITE_OPERATON_URL` | `.env.production` | `https://operaton.open-regels.nl` — the same engine for both environments |
| `VITE_BUILD_SHA`, `VITE_BUILD_RUN` | The Build step, from `github.sha` and `github.run_number` | Build provenance shown in the Changelog tab |

`.env.acceptance` exists but is loaded by nothing: only `--mode acceptance`
would read it, and no workflow passes that. Locally, `npm start` uses
`.env.development` (`localhost:3001` for the Linked Data Explorer backend,
`localhost:8081` for Operaton).

The build provenance is passed in rather than derived from git at build time,
so the build id has exactly one source. The release version identifies a
release, not a build of it: ACC and PROD can serve different builds of the same
version, and the SHA and run number tell them apart.

The TriplyDB base URL, account, dataset and API token are entered by the user at runtime and stored in browser localStorage.
