# Local Development

This guide covers setting up the full local development environment: the Linked Data Explorer frontend and its backend. Both must run simultaneously because the frontend calls the backend for all SPARQL and Operaton operations.

---

## Prerequisites

- Node.js 20.0.0 or higher
- npm 10.0.0 or higher
- Git
- Access to the TriplyDB and Operaton remote services (no local setup needed — they are always available remotely)

---

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/sgort/linked-data-explorer.git
cd linked-data-explorer

# 2. Install all workspace dependencies
npm install
```

---

## Backend configuration

```bash
cd packages/backend
cp .env.example .env
```

Edit `.env`:

```env
# Server
NODE_ENV=development
PORT=3001
HOST=localhost

# CORS — must include both frontend dev ports
CORS_ORIGIN=http://localhost:3000,http://localhost:5173

# TriplyDB — default SPARQL endpoint
TRIPLYDB_ENDPOINT=https://api.open-regels.triply.cc/datasets/stevengort/DMN-discovery/services/DMN-discovery/sparql
TRIPLYDB_TIMEOUT=30000

# Operaton
OPERATON_BASE_URL=https://operaton.open-regels.nl/engine-rest
OPERATON_TIMEOUT=10000

# Logging
LOG_LEVEL=debug
LOG_FORMAT=json

# Performance
CHAIN_EXECUTION_TIMEOUT=5000
MAX_CHAIN_DEPTH=10
ENABLE_CACHING=false
```

---

## Frontend configuration

The frontend reads environment variables via Vite. The `packages/frontend/.env.development` file is pre-configured:

```env
VITE_API_BASE_URL=http://localhost:3001
VITE_OPERATON_BASE_URL=https://operaton.open-regels.nl/engine-rest
```

No changes needed for standard local development.

---

## Starting the services

Open three terminal windows.

**Terminal 1 — Backend:**

```bash
cd packages/backend
npm run dev
```

Expected output:
```
[INFO] Server started
[INFO] environment: development
[INFO] host: localhost
[INFO] port: 3001
[INFO] corsOrigin: http://localhost:3000,http://localhost:5173
[INFO] API available at: http://localhost:3001/v1
[INFO] Health check: http://localhost:3001/v1/health
```

**Terminal 2 — Frontend:**

```bash
cd packages/frontend
npm run dev
```

Expected output:
```
VITE v6.x ready in XXX ms
➜  Local:   http://localhost:5173/
```

The frontend runs at `http://localhost:5173`. The backend runs at `http://localhost:3001`.

---

## Verifying the setup

**Health check:**

```bash
curl http://localhost:3001/v1/health | jq '.'
```

Expected response:
```json
{
  "name": "Linked Data Explorer Backend",
  "version": "0.x.x",
  "environment": "development",
  "status": "healthy",
  "services": {
    "triplydb": { "status": "up", "latency": 150 },
    "operaton": { "status": "up", "latency": 120 }
  }
}
```

If either service shows `"status": "down"`, check your internet connection — both TriplyDB and Operaton are remote services.

**Browser check:**

1. Open `http://localhost:5173`
2. Click the GitBranch icon (Chain Builder)
3. DMN cards should load in the left panel within a few seconds
4. Open browser DevTools → Console: no CORS errors should appear

---

## Running backend tests

```bash
cd packages/backend
npm test                  # run all tests
npm run test:watch        # watch mode
npm run test:coverage     # with coverage report
```

---

## Code quality

```bash
# Lint and format (from repo root)
npm run lint              # lint all packages
npm run lint:fix          # auto-fix
npm run format            # prettier all packages
npm run check-format      # check without writing
```

Pre-commit hooks (husky + lint-staged) run lint and format automatically on staged files in `packages/frontend/`.

---

## Pushing to ACC

After local verification:

```bash
# From repo root
git add packages/backend/src/ packages/frontend/src/
git commit -m "feat: your description"
git push origin acc
```

Monitor the GitHub Actions run for the `acc` branch. The ACC frontend deploys to `https://acc.linkeddata.open-regels.nl` and the ACC backend to `https://acc.backend.linkeddata.open-regels.nl`. Verify the ACC deployment before opening a PR to `main`.
