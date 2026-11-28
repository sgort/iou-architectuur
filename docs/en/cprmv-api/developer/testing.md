---
component: CPRMV
---

# Testing

The CPRMV API has two test files in `serve_api/test/`, run with pytest: `test_serve.py` has seven active tests, four of them on `/health`, and ten more commented out since the method modules were introduced in 0.4.2; `test_ref.py` has 19 tests of `/ref`. The shell scripts of the pipeline and the VMs have 69 bats tests. The release SBOM script has its own pytest suite, `scripts/test/test_write_sbom.py`, which the Release SBOM workflow runs. The SHACL shapes are validated separately with a shell script that is not part of CI.

---

## At a glance

Measured on 28 November 2026 at `0c4d236`, the commit on `main` (release v2026.11.1), from a scratch export, on Windows with Python 3.14. The hash-locked `requirements-dev.txt` was installed with `--require-hashes` without `uvloop`, which does not build on Windows, and `pywin32`, `pywin32-ctypes` and `colorama` were added, which the Linux-compiled files omit. CI on Linux ran the same suite and the shell tests in the `test` job of [run 50](https://github.com/open-regels/cprmv/actions/runs/46040683051) at `0c4d236`, and passed; the Release SBOM workflow's [run 13](https://github.com/open-regels/cprmv/actions/runs/46040682565) on the same commit passed the SBOM script's tests.

| Check | Command | Result |
|---|---|---|
| Syntax check | `python -m py_compile src/serve.py` (from `serve_api/`) | Not run locally; passed in CI |
| Import check | `python -c "from src.serve import app"` (from `serve_api/`) | Not run separately (the tests import `app`); passed in CI |
| Unit tests | `pytest` (from `serve_api/`) | 26 collected, 19 in `test/test_ref.py` and 7 in `test/test_serve.py`; 26 passed in 6.99 s; 26 passed in CI in 1.45 s |
| Shell tests | `bats scripts/test deployment/vm/reconciler/test` (from the repository root) | Not run locally (bats not installed); 69 passed in CI, as read from the run's log |
| SBOM script tests | `python -m pytest scripts/test/test_write_sbom.py` (from the repository root) | 75 collected, 74 passed and 1 skipped in 1.62 s: the skipped test runs the real `cyclonedx-py`, which was not installed; 75 passed in the Release SBOM run, which installs `cyclonedx-bom` 8.0.1 |
| SHACL validation | `sh test.sh` (from `rdf/0.4.3/`) | Not measured |

---

## Running the tests

Install the dependencies as described in [Local Development](local-development.md#setup) (on Linux or WSL; on Windows, see the container command below), then run from `serve_api/`. The API loads `./data/` and `./respec/` relative to the working directory:

```bash
python -m py_compile src/serve.py
python -c "from src.serve import app; print('FastAPI app imported successfully')"
pytest
```

`make tests` runs `pytest test`. No active test needs network access: `test_ref.py` replaces CELLAR, and the references `test_serve.py` resolves never reach it (see [Test inventory](#test-inventory)).

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

`scripts/test/test_write_sbom.py` is not in this job: the Release SBOM workflow runs it, on pushes to `main`, by hand, and on pull requests that change the SBOM script or its inputs, so it does not run on a push to `acc` ([CI/CD](ci-cd.md#release-sbom-sbomyml)).

The rulesets require `test` on `acc` and `main`. The `build` job then starts the built image and requires its `/health` to report the commit; `publish` repeats that on the pushed image. See [CI/CD](ci-cd.md).

---

## Test inventory

### Active

In `test_serve.py`:

| Test | What it checks | Notes |
|---|---|---|
| `test_get_root` | `GET /` returns 200 and `{"CPRMV Rules Serve API": "0.4.3"}` | Uses FastAPI's `TestClient` |
| `test_health_reports_build_and_digest` | With `BUILD_SHA`, `BUILD_RUN`, `BUILD_RELEASE`, `CPRMV_IMAGE_DIGEST` and `CPRMV_ENVIRONMENT` set, `GET /health` returns them, with the keys in the order `status`, `version`, `environment`, `release`, `build`, `image` | |
| `test_health_reports_null_when_unset` | Unset, each of them is `null` | |
| `test_health_treats_empty_as_null` | An empty value is `null` too | |
| `test_health_reads_the_release_per_request` | Changing `BUILD_RELEASE` between two requests changes `release`: it is read per request | |
| `test_detect_cprmv_serve_reference_method_and_transform` | An empty reference resolves to `None`; a Juriconnect 1.31 reference with `z` and `g` and a 1.3 reference with `g` resolve to the expected `/rules/…` paths | Offline: none of these references reaches CELLAR, since `elifmx4` no longer queries it for a reference that is not an ELI |
| `test_detect_cprmv_serve_unknown_method` | `get_rules("UNKNOWN")` returns the "No supported publication repository…" error | |

In `test_ref.py`, 19 cases from six test functions, offline: every test that could reach CELLAR replaces the ELI method's `urlopen`, either with a fake CELLAR answer or with one that fails the test when called.

| Test | Cases | What it checks |
|---|---|---|
| `test_ref_redirect_does_not_echo_request_headers` | 1 | A Juriconnect reference sent with `x-api-key` and a custom header gets a `307` to `/rules/BWBR0015703_…` that carries neither header nor the key's value |
| `test_unrecognised_references_never_reach_cellar` | 8 | An empty string, plain text, an ELI on another host, and ELIs with a quote, a SPARQL injection, a closing `" . }`, angle brackets or a trailing newline resolve to `None` without a CELLAR query |
| `test_valid_eli_reference_queries_cellar` | 1 | A valid ELI queries CELLAR once, at `https://publications.europa.eu/webapi/rdf/sparql?`, and resolves to the item |
| `test_ref_redirects_to_a_cellar_item` | 1 | `/ref` redirects a valid ELI to the CELLAR item |
| `test_ref_refuses_to_redirect_elsewhere` | 7 | A target on another host, `//host`, `/\host`, with user info, on a look-alike host, `javascript:` or `ftp:` gets `200` with the *not a valid or supported reference* error and no `location` |
| `test_ref_refuses_a_cellar_answer_pointing_elsewhere` | 1 | A CELLAR answer that points to another host is refused the same way |

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

The pipeline's and the VMs' shell scripts have 69 bats tests in six files, run by CI's `test` job on a runner with git, jq, curl, `flock` and pip-audit; the reconciler's tests run against stubbed `docker` and `curl`. On Linux or WSL with those tools, run `bats scripts/test deployment/vm/reconciler/test` from the repository root. The `bats/bats:1.14.0` image lacks git, jq and curl, so in Docker only the tests that need none of them run, such as `scripts/test/ci-tier.bats`. What each file covers is on [VM Deployment](vm-deployment.md#what-the-tests-verify).

---

## SBOM script tests

`scripts/test/test_write_sbom.py` tests `scripts/write-sbom.py`, which writes the [release SBOM](ci-cd.md#release-sbom-sbomyml). Its 17 test functions make 75 cases, most of them from parametrising every mode of the script over eleven malformed release files. They run without network, in a temporary project, with the CycloneDX tool's output as a fixture. They check that:

- the file is named after the release, not the vocabulary version; a release file without a trailing newline is read; and the script validates the release with the same expression as `scripts/read-release.sh`;
- every mode fails, writing nothing, when `serve_api/RELEASE` is missing or malformed (no `v`, month 13, an unpadded month, a CRLF ending, two lines, a path, an empty file, two trailing newlines, a NUL byte, a leading space), and `--verify-release` then says that `main` has not been released with a release number;
- the output is normalised: volatile fields removed, components sorted whatever the input order or line numbers, a duplicate package rejected, and stable JSON with a trailing newline;
- `--check` passes on a fresh file, fails on a missing or stale one, and ignores the tool's version and timestamp; `--verify-release` fails only on a missing file; `--print-path` runs no tool;
- one test runs the real `cyclonedx-py` on a hashed requirements file. It is skipped where the tool is not installed; the Release SBOM workflow installs it.

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
- **`/methods`, `/0.4.3/methods`, `/raw` and `/respec`** have no endpoint test. `/ref` is tested for its headers and its redirect targets, with Juriconnect and ELI references; no test resolves a `cprmvapi` or `elinl` reference.
- **The new sources.** Nothing tests IOU Norms, ROO, DSO or the `x-api-key` pass-through.
- **MCP.** Nothing tests `/mcp/`. It answers on the hosts, but no test lists its tools.
- **The image's methods.** CI starts the built image and the pushed one and checks `/health`, but `/health` loads no method: an image without `methods/` would still pass, because the tests run against the source tree, where `methods/` exists (see [Deployment](deployment.md#docker-image)). The Dockerfile copies `methods/`, and nothing checks that it does.
- **The data files.** Nothing checks that `serve_api/data/` holds the files the API loads, or compares the committed `cprmvmethods.ttl` with what `make methods` generates — at v0.4.3 they are the same (see [Local Development](local-development.md#data-files)).
- **SHACL.** The shapes and the API's output are validated only when someone runs `test.sh` by hand.
- **Coverage.** No coverage is measured or required.

A design for a fuller test foundation — tests on recorded source responses, a per-file branch-coverage floor and end-to-end runs — is in review as a draft pull request ([open-regels/cprmv#29](https://github.com/open-regels/cprmv/pull/29)); none of it is in place.
