---
component: CPRMV
---

# Testing

The CPRMV API has one test file, `serve_api/test/test_serve.py`, run with pytest. Three tests are active; ten more are commented out since the method modules were introduced in 0.4.2, and v0.4.3 changed only the version the active ones expect. The SHACL shapes are validated separately with a shell script that is not part of CI.

---

## At a glance

Measured on 24 November 2026 at `d597671` (v0.4.3), from a scratch export, on Windows with Python 3.14.3, after installing the pinned `requirements-dev.txt` without `uvloop` (it does not build on Windows; uvicorn uses it only when serving), plus `pywin32` and `colorama`, which pip-compile's Linux pin set omits. CI on Linux (`python:3.14-bookworm`, pipeline #824 at `d597671`) ran the same suite and passed.

| Check | Command (from `serve_api/`) | Result |
|---|---|---|
| Syntax check | `python -m py_compile src/serve.py` | Not run locally; passed in CI |
| Import check | `python -c "from src.serve import app"` | Not run separately (the tests import `app`); passed in CI |
| Unit tests | `pytest` | 3 collected in `test/test_serve.py`, 3 passed in 6.68 s; passed in CI |
| SHACL validation | `sh test.sh` (from `rdf/0.4.3/`) | Not measured |

---

## Running the tests

Install the dependencies as described in [Local Development](local-development.md#setup), then run from `serve_api/` — the API loads `./data/` and `./respec/` relative to the working directory:

```bash
python -m py_compile src/serve.py
python -c "from src.serve import app; print('FastAPI app imported successfully')"
pytest
```

`make tests` runs `pytest test`. One active test needs network access (see [Test inventory](#test-inventory)).

---

## What CI runs

The `test-cprmv-api` job (`python:3.14-bookworm`) runs on merge request pipelines and on pushes to `main`, in both cases only when files under `serve_api/` change. It installs `libxml2-dev`, `libxslt-dev` and `requirements-dev.txt`, then runs:

1. `python -m py_compile src/serve.py`
2. `python -c "from src.serve import app; ..."`
3. `test -f ./data/cprmvmethods.ttl || echo "Warning ..."` and the same for `./data/cprmv.ttl` — these only print a warning; a missing file does not fail the job
4. `pytest`

Pushes to `develop` build and push an image (`datafluisteraar/cprmv-api:{branch-slug}`) without any test job. Changes outside `serve_api/` — including `rdf/` — do not trigger the test job. See [CI/CD](ci-cd.md).

---

## Test inventory

### Active

| Test | What it checks | Notes |
|---|---|---|
| `test_get_root` | `GET /` returns 200 and `{"CPRMV Rules Serve API": "0.4.3"}` | Uses FastAPI's `TestClient` |
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
- **The Docker image.** CI builds and pushes the image but never starts it or requests an endpoint from it. An image without `methods/` would pass: the tests run against the source tree, where `methods/` exists, and the image's health check only requests `/` (see [Deployment](deployment.md#docker-image)). The Dockerfile copies `methods/`, but nothing checks that it does.
- **The data files.** The CI check only warns when a file is missing, and nothing compares the committed `serve_api/data/cprmvmethods.ttl` with what `make methods` generates — at v0.4.3 they are the same (see [Local Development](local-development.md#data-files)).
- **SHACL.** The shapes and the API's output are validated only when someone runs `test.sh` by hand.
