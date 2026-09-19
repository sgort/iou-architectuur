---
component: CPSV Editor
---

# Local Development

This guide covers setting up and running the CPSV Editor — and the backend it depends on — locally for development and testing.

---

## When you need a local backend

The editor's frontend works standalone for form editing, TTL generation, import, and export. You need the shared backend running locally when making changes to:

- Backend API endpoints (new routes, modifications)
- Backend services (SPARQL, TriplyDB, Operaton integration)
- CORS configuration
- API versioning or the `/v1/*` endpoint structure

The backend serves both the CPSV Editor and the Linked Data Explorer. Breaking it in one context can affect the other.

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│  Local Development Environment                       │
├──────────────────────────────────────────────────────┤
│                                                      │
│  CPSV Editor              Linked Data Explorer       │
│  http://localhost:3000    http://localhost:5173      │
│  (React / CRA)            (React / Vite)             │
│           │                       │                  │
│           └──────────┬────────────┘                  │
│                      ↓                               │
│              Shared Backend                          │
│           http://localhost:3001                      │
│        (Node.js + Express + TypeScript)              │
│                      │                               │
│                      ↓                               │
│     External Services (always remote)                │
│     • TriplyDB — api.open-regels.triply.cc           │
│     • Operaton — operaton.open-regels.nl             │
└──────────────────────────────────────────────────────┘
```

External services do not need to be running locally. They are always accessed remotely.

---

## Prerequisites

- Node.js 20.x or higher (CI builds on Node 24 since v2026.09.0)
- npm 10.x or higher
- Git
- Access to the `cpsv-editor` and `linked-data-explorer` repositories

---

## Setup

### Frontend (CPSV Editor)

```bash
git clone https://github.com/sgort/ttl-editor.git
cd ttl-editor
npm ci
npm start
```

Opens at `http://localhost:3000`. Use `npm ci`, not `npm install`: it installs exactly the
committed lockfile instead of re-resolving version ranges. Since v2026.09.5 `npm start`
runs `npm run deps:check` first, and refuses to start Vite — naming `npm ci` as the fix —
when what is installed has fallen behind `package-lock.json`. A fast-forward brings
lockfile changes in and installs nothing; on 14 September 2026 one workstation had 53
packages at a different version and 86 missing.

### Shared backend

```bash
git clone https://github.com/sgort/linked-data-explorer.git
cd linked-data-explorer
npm ci
npm run dev:backend
```

Backend starts at `http://localhost:3001`.

### Linked Data Explorer (optional, for full regression testing)

```bash
cd linked-data-explorer
npm run dev:frontend
```

Opens at `http://localhost:5173`.

---

## Environment variables

Vite reads them per mode from the tracked `.env.development`, `.env.acceptance` and
`.env.production` files, so local development needs no `.env` of its own; `.env.example`
lists them. Only variables prefixed `VITE_` reach the browser — the `REACT_APP_` names
from before the v2026.09.1 Vite migration are no longer read.

| Variable | Purpose | `.env.development` | Fallback when unset |
|---|---|---|---|
| `VITE_BACKEND_URL` | The shared Linked Data Explorer backend — SPARQL proxy, TriplyDB publishing, and DMN validate/deploy/evaluate | `http://localhost:3001` | `http://localhost:3001` |
| `VITE_OPERATON_URL` | The Operaton base the DMN tab shows as its **Base URL**, and from which it builds the evaluate URL it **publishes** as `cprmv:implementedBy` | `http://localhost:8081` | `https://operaton.open-regels.nl` |
| `VITE_BUILD_SHA`, `VITE_BUILD_RUN` | Build provenance, injected by the deploy workflows — see [Build Provenance](../../contributing/build-provenance.md) | — | local build |

!!! warning "`VITE_OPERATON_URL` decides what a published DMN claims, not where it deploys"
    Deploy and evaluate both go through the Linked Data Explorer backend, which
    targets **its own** configured Operaton — so where a DMN lands in local
    development is decided by the local backend's `OPERATON_BASE_URL`, not by this
    variable. What this variable does decide is the evaluate endpoint the editor
    records for the decision and writes into the TTL as `cprmv:implementedBy`.
    Publishing from a local session therefore publishes a `localhost:8081`
    endpoint. Publish from acceptance or production, whose `.env` files name the
    shared engine.

---

## Running the tests

```bash
npm run test:ci      # everything, once, with coverage
npm test             # watch mode
npm run test:p2      # one layer in isolation
```

The full suite is 16 files and 257 tests. Note that the pre-push hook runs
`lint` and `check-format` **only** — it does not run the tests, so run
`test:ci` yourself before pushing. Since v2026.08.1 both deploy workflows do
run the suite and a failure blocks the deploy, and since v2026.08.2 a failing
pull request cannot be merged into `acc` at all — but the feedback arrives in
CI rather than on your machine.

See [Testing](testing.md) for the full command list and per-file inventory.

---

## Pre-deployment checklist

Before pushing to ACC, verify:

- [ ] `npm run test:ci` passes (16 suites, 257 tests)
- [ ] `npm run lint` and `npm run check-format` pass
- [ ] All verification tests pass locally
- [ ] Both CPSV Editor and Linked Data Explorer work correctly
- [ ] No CORS errors in the browser console
- [ ] Backend logs show no errors
- [ ] New features work as expected
- [ ] Existing features show no regression
- [ ] Git commit messages are clear and descriptive

---

## Deploying to ACC

!!! danger "`git push origin acc` no longer works"
    Since v2026.08.2, `acc` is protected by the `acc supply-chain gate`
    ruleset — it requires a pull request and a passing `audit` check, with no
    bypass actors. A direct push is rejected outright, for releases and for the
    repository owner alike. Deployment goes through a pull request.

```bash
# 1. Work on a branch, never on acc directly
git checkout -b feature/your-topic

# 2. Commit your changes
git add .
git commit -m "feat: your change description"

# 3. Push the branch and open a pull request against acc
git push -u origin feature/your-topic
gh pr create --base acc --title "feat: your change description"

# 4. Watch both required checks — `audit` and `Build and Deploy`
gh pr checks

# 5. Merge once green. Merging IS the push to acc, and triggers the deploy.
#    Use a merge commit for a release PR; squash a Renovate dependency PR.
gh pr merge <n> --merge --delete-branch

# 6. Verify the ACC deployment
curl https://acc.cpsv-editor.open-regels.nl
```

The pull request also produces a Static Web Apps preview deployment, so the
change can be checked before it reaches acceptance at all. See
[Deployment](deployment.md) for the pipeline itself and
[Supply-Chain Pinning](../../contributing/supply-chain.md) for the gate.
