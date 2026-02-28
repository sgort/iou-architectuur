# CI/CD & Changelog

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

---

## Changelog

### v0.4.0 — Current

- On-the-fly rule retrieval for BWB, CVDR, and EU CELLAR publications.
- Automatic `_latest` version resolution via SRU search.
- Seven output formats: `cprmv-json`, `json-ld`, `turtle`, `ttl`, `turtle2`, `n3`, `xml`.
- `unformat` parameter for structured definition extraction using `parse` patterns.
- `/ref/Juriconnect/{reference}` endpoint — `jci1.3` and `jci1.31` redirect to `/rules/` paths.
- `/methods` endpoint exposing the Methods KG in RDF.
- Static CPRMV specification served at `/respec/`.
- Docker image: `datafluisteraar/cprmv-api:latest`.
- Non-root container user, built-in health check.
- GitLab CI pipeline with test, build, and deploy stages.
- Dutch locale (`nl_NL.UTF-8`) installed in the container.
- DMN 1.3 / Operaton formalisation method (experimental).

### v0.1.0

- Browser-based prototype in `serve_api/cprmv-serve.html` using Pyodide/WebAssembly.
- Local file-based rule set loading from pre-converted Turtle files.
- Basic `/ruleset/{rulesetid}` and rule path traversal.
