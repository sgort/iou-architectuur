# CI/CD

## CI/CD pipeline

The `cprmv` repository uses GitLab CI (`.gitlab-ci.yml`) with three stages: `test`, `build`, `deploy`.

### Stages

**test-cprmv-api** (`python:3.12-bookworm`)

Runs on merge requests and pushes to `main` when `serve_api/**` files change:

1. Installs `libxml2-dev` and `libxslt-dev`.
2. Installs `requirements-dev.txt`.
3. Syntax-checks `src/serve.py` with `py_compile`.
4. Import-checks the FastAPI app.
5. Verifies `data/cprmvmethods.ttl` is present.
6. Runs `pytest`.

**build-cprmv-api** (`docker:24.0.5` with DinD)

Runs on pushes to `main` and `develop` when `serve_api/**` changes:

- On `main`: builds and pushes `datafluisteraar/cprmv-api:latest` and `datafluisteraar/cprmv-api:{commit-sha}`.
- On `develop`: builds and pushes `datafluisteraar/cprmv-api:{branch-slug}`.

Required CI/CD variables: `DOCKER_HUB_USERNAME`, `DOCKER_HUB_TOKEN`.

**deploy-cprmv-api**

Prints the new image tag and pull commands. Actual container restart is a manual step on the deployment host (run `docker compose pull && docker compose up -d`).

### ReSpec publication

A separate job (`create-pages`) builds the ReSpec HTML specification from `html/` using `node:lts` and publishes it to GitLab Pages at `html/public`.
