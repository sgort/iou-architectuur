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

- Node.js 20.x or higher
- npm 10.x or higher
- Git
- Access to the `cpsv-editor` and `linked-data-explorer` repositories

---

## Setup

### Frontend (CPSV Editor)

```bash
git clone https://github.com/sgort/cpsv-editor.git
cd cpsv-editor
npm install
npm start
```

Opens at `http://localhost:3000`.

### Shared backend

```bash
git clone https://github.com/sgort/linked-data-explorer.git
cd linked-data-explorer
npm install
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

Set these in a `.env` file at the CPSV Editor repository root.

| Variable | Purpose | Fallback when unset |
|---|---|---|
| `REACT_APP_BACKEND_URL` | The shared Linked Data Explorer backend — SPARQL proxy, TriplyDB publishing, and DMN validate/deploy/evaluate | — |
| `REACT_APP_OPERATON_URL` | The Operaton engine the backend should target for DMN deploy and evaluate | The shared production instance |

!!! warning "Set `REACT_APP_OPERATON_URL` when running a local engine"
    Without it, the DMN tab's Base URL falls back to the shared production
    Operaton instance — so local development would deploy to, and evaluate
    against, shared infrastructure rather than your container.

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
