---
component: CPRMV
---

# CI/CD

---

## CI/CD pipeline

The `cprmv` repository uses GitLab CI (`.gitlab-ci.yml`) with three stages: `test`, `build`, `deploy`.

### Stages

**test-cprmv-api** (`python:3.14-bookworm`)

Runs on merge request pipelines and on pushes to `main` when files under `serve_api/` change:

1. Installs `libxml2-dev` and `libxslt-dev`.
2. Installs `requirements-dev.txt`.
3. Syntax-checks `src/serve.py` with `py_compile`.
4. Import-checks the FastAPI app (`python -c "from src.serve import app"`).
5. Checks that `data/cprmvmethods.ttl` and `data/cprmv.ttl` exist — warn only: a missing file prints a warning and the job continues.
6. Runs `pytest`.

See [Testing](testing.md) for what the tests cover.

**build-cprmv-api** (`docker:24.0.5` with DinD)

Runs on pushes to `main` and `develop` when files under `serve_api/` change:

- On `main`: builds and pushes `datafluisteraar/cprmv-api:latest` and `datafluisteraar/cprmv-api:{short-sha}`.
- On `develop`: builds and pushes `datafluisteraar/cprmv-api:{branch-slug}`. No test job runs on `develop` pushes, so these images are built without a test gate.

On `main`, the test stage runs first, so a failing test stops the build. No job starts the built image or requests an endpoint from it.

Required CI/CD variables: `DOCKER_HUB_USERNAME`, `DOCKER_HUB_TOKEN`.

**deploy-cprmv-api** (`alpine:latest`, `main` only)

Prints the `docker pull` commands for the new image tags and a reminder to update `docker-compose.yml`. It deploys nothing: each host is updated by pulling the image (see [Deployment](deployment.md#updating-to-a-new-image-version)).

### ReSpec publication

A separate job (`create-pages`, `node:lts-alpine`) runs on the default branch only. It installs Chromium, runs `npm ci` and `npm run build` in `html/`, and publishes `html/public` to GitLab Pages.
