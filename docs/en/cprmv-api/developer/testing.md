---
component: CPRMV
---

# Testing

The CPRMV API has one test file, `serve_api/test/test_serve.py`, run with pytest. Six tests are active, three of them on `/health`; ten more are commented out since the method modules were introduced in 0.4.2. The shell scripts of the pipeline and the VMs have 54 bats tests. The SHACL shapes are validated separately with a shell script that is not part of CI.

---

## At a glance

Measured on 26 November 2026 at `189cadc`, whose code and tests equal `8f01b2b`, the commit on `main`, from a scratch export, on Windows with Python 3.14. The hash-locked `requirements-dev.txt` was installed with `--require-hashes` without `uvloop`, which does not build on Windows, and `pywin32`, `pywin32-ctypes` and `colorama` were added, which the Linux-compiled files omit. CI on Linux ran the same suite and the shell tests in the `test` job of [run 13](https://github.com/open-regels/cprmv/actions/runs/45892291396) at `8f01b2b`, and passed.

| Check | Command | Result |
|---|---|---|
| Syntax check | `python -m py_compile src/serve.py` (from `serve_api/`) | Not run locally; passed in CI |
| Import check | `python -c "from src.serve import app"` (from `serve_api/`) | Not run separately (the tests import `app`); passed in CI |
| Unit tests | `pytest` (from `serve_api/`) | 6 collected in `test/test_serve.py`, 6 passed in 9.63 s; 6 passed in CI in 1.83 s |
| Shell tests | `bats scripts/test deployment/vm/reconciler/test` (from the repository root) | Not run locally (bats not installed); 54 passed in CI, as read from the run's log |
| SHACL validation | `sh test.sh` (from `rdf/0.4.3/`) | Not measured |

---

## Running the tests

Install the dependencies as described in [Local Development](local-development.md#setup) (on Linux or WSL; on Windows, see the container command below), then run from `serve_api/`. The API loads `./data/` and `./respec/` relative to the working directory:

```bash
python -m py_compile src/serve.py
python -c "from src.serve import app; print('FastAPI app imported successfully')"
pytest
```

`make tests` runs `pytest test`. One active test needs network access (see [Test inventory](#test-inventory)).

In a container, from the repository root in Git Bash, as the repository's README gives it:

```bash
MSYS_NO_PATHCONV=1 docker run --rm -e PIP_ROOT_USER_ACTION=ignore -e PIP_DISABLE_PIP_VERSION_CHECK=1 -v "$PWD/serve_api:/s" -w /s python:3.14-bookworm sh -c "pip install -q --require-hashes -r requirements-dev.txt && pytest"
```

---

## What CI runs

The `test` job of the CI workflow runs on every pull request into `acc` or `main` and on every push to them, whatever the files changed. On `ubuntu-24.04` with Python 3.14 it installs `requirements-dev.txt` with `--require-hashes`, then runs:

1. `python -m py_compile src/serve.py`
2. `python -c "from src.serve import app"`
3. `pytest`, from `serve_api/`
4. shellcheck over every tracked `*.sh` outside `rdf/` and over the reconciler's test stubs
5. the bats suites in `scripts/test` and `deployment/vm/reconciler/test`

The rulesets require `test` on `acc` and `main`. The `build` job then starts the built image and requires its `/health` to report the commit; `publish` repeats that on the pushed image. See [CI/CD](ci-cd.md).

---

## Test inventory

### Active

| Test | What it checks | Notes |
|---|---|---|
| `test_get_root` | `GET /` returns 200 and `{"CPRMV Rules Serve API": "0.4.3"}` | Uses FastAPI's `TestClient` |
| `test_health_reports_build_and_digest` | With `BUILD_SHA`, `BUILD_RUN`, `CPRMV_IMAGE_DIGEST` and `CPRMV_ENVIRONMENT` set, `GET /health` returns them, with the keys in the order `status`, `version`, `environment`, `build`, `image` | |
| `test_health_reports_null_when_unset` | Unset, each of them is `null` | |
| `test_health_treats_empty_as_null` | An empty value is `null` too | |
| `test_detect_cprmv_serve_reference_method_and_transform` | An empty reference resolves to `None`; a Juriconnect 1.31 reference with `z` and `g` and a 1.3 reference with `g` resolve to the expected `/rules/…` paths | Needs network: the `elifmx4` reference method queries the EU CELLAR SPARQL endpoint |
| `test_detect_cprmv_serve_unknown_method` | `get_rules("UNKNOWN")` returns the "No supported publication repository…" error | |

### Commented out

Commit `0661a0d` ("disable failing tests, need to be recreated after all the modularisation changes in serve.py") commented out ten tests:

| Test | What it covered |
|---|---|
| `test_get_mapping` | The Juriconnect reference mapping read from the methods knowledge graph |
| `test_transform_jci_reference` | Juriconnect reference parts to a `/rules` path |
| `test_detect_cprmv_serve_acknowledged_method_unknown_identifier` | An unknown rule set id matches no method |
| `test_detect_cprmv_serve_acknowledged_method_DMN_identifier` | DMN 1.3 id detection and method settings |
| `test_detect_cprmv_serve_acknowledged_method_BWB_identifier` | BWB id detection and method settings |
| `test_detect_cprmv_serve_acknowledged_method_BWB_identifier_with_latest` | `…_latest` resolved through an SRU response fixture |
| `test_detect_cprmv_serve_acknowledged_method_BWB_identifier_with_implicit_latest` | A bare BWB id resolved to the version in force today |
| `test_detect_cprmv_serve_acknowledged_method_CVDR_identifier` | CVDR id detection and method settings |
| `test_detect_cprmv_serve_acknowledged_method_FMX4_identifier` | Formex 4 (CELLAR) id detection and method settings |
| `test_get_rules` | `/rules` end to end on a fixture publication, with rule path matching and `unformat` |

They call functions that 0.4.2 removed or moved into method modules (`detect_cprmv_serve_acknowledged_method`, `get_mapping`, `transform_jci_reference`), and they rely on method settings that changed.

### Fixtures

`serve_api/test/` holds `cprmvmethods.test.ttl` (a methods registry with a `test001bwb` method pointing at local files), `TEST001BWB_Publication.xml` and `TEST001BWB_Publication_Versioning.xml`. Only the commented-out tests use them, and `cprmvmethods.test.ttl` still uses pre-0.4.2 settings such as `cprmv-serve:frbr-repository-sru-url`, which 0.4.2 replaced with `frbr-sru:url`. The active tests use the committed `serve_api/data/` files.

---

## Shell tests

The pipeline's and the VMs' shell scripts have 54 bats tests in five files, run by CI's `test` job on a runner with git, jq, curl, `flock` and pip-audit; the reconciler's tests run against stubbed `docker` and `curl`. On Linux or WSL with those tools, run `bats scripts/test deployment/vm/reconciler/test` from the repository root. The `bats/bats:1.14.0` image lacks git, jq and curl, so in Docker only the tests that need none of them run, such as `scripts/test/ci-tier.bats`. What each file covers is on [VM Deployment](vm-deployment.md#what-the-tests-verify).

---

## SHACL validation

`rdf/0.4.3/test.sh` validates against `cprmv.shacl.ttl`, with `cprmv.ttl` as ontology and inference set to `both`:

1. `test.ttl` — the basic example data.
2. Every `methods/*/method.ttl` — all method definitions.
3. `testbwb.ttl`, `testcvdr.ttl`, `testdmn.ttl`, `testfmx4.ttl` — saved API output for the four implemented serialisations.

Run it from `rdf/0.4.3/`. It requires pyshacl (`pip install pyshacl`), which is not in `requirements-dev.txt`. The script is manual: CI does not run it. It was not run for the figures above.

---

## What is not covered

- **`/rules`.** No active test fetches a rule set or follows a rule path; `test_get_rules` is commented out.
- **The method modules.** No test calls a publication, serialisation or reference method directly, and no test checks which methods `load_methods()` loads. `test_detect_cprmv_serve_unknown_method` passes even when no method is loaded.
- **`/ref`, `/methods`, `/0.4.3/methods`, `/raw` and `/respec`** have no endpoint test.
- **The new sources.** Nothing tests IOU Norms, ROO, DSO or the `x-api-key` pass-through.
- **MCP.** Nothing tests `/mcp/`. It answers on the hosts, but no test lists its tools.
- **The image's methods.** CI starts the built image and the pushed one and checks `/health`, but `/health` loads no method: an image without `methods/` would still pass, because the tests run against the source tree, where `methods/` exists (see [Deployment](deployment.md#docker-image)). The Dockerfile copies `methods/`, and nothing checks that it does.
- **The data files.** Nothing checks that `serve_api/data/` holds the files the API loads, or compares the committed `cprmvmethods.ttl` with what `make methods` generates — at v0.4.3 they are the same (see [Local Development](local-development.md#data-files)).
- **SHACL.** The shapes and the API's output are validated only when someone runs `test.sh` by hand.
- **Coverage.** No coverage is measured or required.

A design for a fuller test foundation — tests on recorded source responses, a per-file branch-coverage floor and end-to-end runs — is in review as a draft pull request ([open-regels/cprmv#29](https://github.com/open-regels/cprmv/pull/29)); none of it is in place.
