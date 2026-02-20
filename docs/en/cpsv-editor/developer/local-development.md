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
git clone https://github.com/your-org/cpsv-editor.git
cd cpsv-editor
npm install
npm start
```

Opens at `http://localhost:3000`.

### Shared backend

```bash
git clone https://github.com/your-org/linked-data-explorer.git
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

## Pre-deployment checklist

Before pushing to ACC, verify:

- [ ] All verification tests pass locally
- [ ] Both CPSV Editor and Linked Data Explorer work correctly
- [ ] No CORS errors in the browser console
- [ ] Backend logs show no errors
- [ ] New features work as expected
- [ ] Existing features show no regression
- [ ] Git commit messages are clear and descriptive

---

## Deploying to ACC

```bash
# 1. Commit your changes
git add .
git commit -m "feat: your change description"

# 2. Push to ACC branch
git push origin acc

# 3. Monitor the GitHub Actions workflow
# https://github.com/your-org/cpsv-editor/actions

# 4. Verify the ACC deployment
curl https://acc.cpsv.open-regels.nl
```
