---
component: Norm Editor
---

# Testing

The Norm Editor is two languages in one repository — a Quasar/Vue frontend and a
Node backend on **Vitest**, three Flask services on **pytest** — and its CI runs on
**GitLab**, not GitHub Actions. Both facts make it the odd one out among the IOU
components, and both shape what follows.

The suite arrived in one release, v2026.07.3, together with the pipeline that runs
it. Before that the repository had no automated tests at all.

!!! info "Figures on this page are measured, not estimated"
    Every count below was produced by running each suite the way `.gitlab-ci.yml`
    runs it, against **2026.09.15-2** on **9 October 2026**, on `main` at `c47096b`:
    the two Vitest suites from their installed dependencies, each Python service in a
    fresh virtual environment of its own on Python 3.14.3 (Windows). Two tests fail
    there; see [Two failures in `wrap_up_api`](#two-failures-in-wrap_up_api).

**At a glance:** 16 test files · **127 tests: 125 passing, 2 failing**.

| Service | Language | Runner | Files | Tests | Result |
|---|---|---|--:|--:|---|
| `gui` | JavaScript (Quasar/Vue) | Vitest | 8 | **46** | all pass |
| `backend` | JavaScript (Fastify) | Vitest | 2 | **11** | all pass |
| `wrap_up_api` | Python (Flask) | pytest | 3 | **34** | **32 pass, 2 fail** |
| `unwrap_api` | Python (Flask) | pytest | 2 | **27** | all pass |
| `nlp_api` | Python (Flask) | pytest | 1 | **9** | all pass |

---

## Running the tests

The commands below are exactly what CI runs, from the repository root.

| Service | Command |
|---|---|
| `gui` | `cd gui && npm i && npm test` |
| `backend` | `cd backend && npm i && npm test` |
| `wrap_up_api` | `cd wrap_up_api && pip install -r requirements.txt -r requirements-dev.txt && pytest` |
| `unwrap_api` | `cd unwrap_api && pip install -r requirements.txt -r requirements-dev.txt && pytest` |
| `nlp_api` | `cd nlp_api/API_NLP && pip install -r requirements.txt -r requirements-dev.txt && pytest` |

Both `npm test` scripts are `vitest run` — the non-watching form, so they exit.

!!! warning "Use a virtual environment for the Python services"
    Each of the three has its own `requirements.txt` and pins versions
    independently, so installing them into one shared environment invites
    conflicts. Create a venv per service.

---

## Two failures in `wrap_up_api`

**`test_wrap_up.py::WrapTest::test_15` and `test_17` fail on a fresh install, and the
cause is not established.** Both compare the service's output with a gold-standard
Turtle fixture using `rdflib.compare.isomorphic`, and the printed difference is
rdflib's own bookkeeping rather than interpretation content: the generated graph
carries `[a rdfg:Graph; rdflib:storage [a rdflib:Store; rdfs:label 'Memory']]`
triples the fixture does not.

`rdflib` is pinned at 7.6.0 in both requirements files, so a library version
difference does not explain it, and `wrap_up_api` did not change between the
7 September measurement, which passed, and this one. Whether CI's
`test_wrap_up_api` job passes is not visible from outside the GitLab project. Until
that is known, read the two failures as unexplained, not as a conversion defect.

**`nlp_api` runs on Python 3.11 or later.** Its `requirements.txt` pins
`networkx==3.6.1`, which requires `>=3.11`. On older Pythons the install stops
before pytest is reached. The suite itself needs neither the model nor a GPU: it
imports `labeling.py` only, though installing `requirements.txt` still pulls the
transformer stack.

---

## What CI actually gates

`.gitlab-ci.yml` defines two stages, and the test stage runs first:

| Stage | Jobs |
|---|---|
| `test` | `test_gui`, `test_backend` on `node:24`; `test_wrap_up_api`, `test_unwrap_api`, `test_nlp_api` on `python:3.14.6` |
| `build` | One job per service — `backend`, `gui`, `nlp_api`, `unwrap_api`, `wrap_up_api`, `nginx` — each building a Docker image and pushing it to Azure Container Registry |

Every service with a test suite has a job, and the build stage runs after the test
stage, so **a failing test blocks the image build**. The build jobs are restricted
to `main`, `develop` and tags; the test jobs are not, so they run on every branch.

Images are tagged twice, with the commit SHA and with `latest`, and pushed to the
registry named by `ACR_REGISTRY_USERNAME`.

`build_gui` first regenerates the changelog the app displays:
`./scripts/generate-changelog.mjs && mv ./changelog.json gui/public`, then builds the
image.

!!! warning "That step needs Node, and the job's image has none"
    `build_gui` runs in `docker:latest`, an Alpine image with the Docker CLI and no
    Node, while the script starts with `#!/usr/bin/env node`. Unless the runner
    supplies Node some other way, the step fails and no GUI image is built. The
    pipeline runs are not visible from outside the GitLab project, so this is read
    from the source, not observed. Even where the step runs, the generator groups
    commits by git tag, and the only tags on the remote are `2026.07.0` and
    `2026.07.1`.

!!! note "This is the only IOU component on GitLab CI"
    The CPSV Editor, RONL Business API and Linked Data Explorer all run GitHub
    Actions, and the supply-chain policy documented in
    [Supply-Chain Pinning](../../contributing/supply-chain.md) is written against
    that shape — digest-pinned `uses:` references, a zizmor audit job, an `acc`
    branch ruleset. **None of it applies here**, because none of those mechanisms
    exists in GitLab CI in the same form. The Norm Editor's images are also built
    and pushed by its own pipeline rather than by a vendor action, so the container
    exception that dominates the other three does not arise either.

---

## Test inventory

### `gui` — 8 files, 46 tests

Domain logic only. The tests exercise the editor's in-memory model and its helper
functions, not Vue components.

| File | Covers |
|---|---|
| `test/unit/model/sentence.test.js` | Sentence structure |
| `test/unit/model/snippet.test.js` | Source snippets |
| `test/unit/model/booleanConstruct.test.js` | Boolean fact construction, including `isEmpty` until a frame is added at some level |
| `test/unit/model/vizNetwork.test.js` | The View interpretation network: a node per act and claim-duty but none for facts, and a link from an act to the acts that need what it creates |
| `test/unit/helpers/dateTimeFunctions.test.js` | Date and time handling |
| `test/unit/helpers/sourceFormatting.test.js` | Source text formatting |
| `test/unit/helpers/utilities.test.js` | Shared utilities |
| `test/unit/helpers/frameRelations.test.js` | Relations between frames: the frames inside a subdivision, every role of an act or claim-duty whether set or not, what a frame uses through its roles and conditions, and which acts use a fact |

### `backend` — 2 files, 11 tests

`test/unit/routes.test.js` and `test/unit/helpers.test.js`. Since v2026.07.4 the
route tests use **`light-my-request`**, which drives Fastify's routing in-process
rather than over a socket — faster, and with no port to collide on.

### `wrap_up_api` — 3 files, 34 tests

`test_wrap_up.py`, `test_routes.py` and `test_helpers.py`. The largest suite in the
repository, covering the service that assembles a finished interpretation. Two of its
gold-standard comparisons fail on a fresh install; see
[Two failures in `wrap_up_api`](#two-failures-in-wrap_up_api).

### `unwrap_api` — 2 files, 27 tests

`test_routes.py` and `test_helpers.py`, covering the inverse transformation.

### `nlp_api` — 1 file, 9 tests

`test_labeling.py`, and it is worth reading: every
test targets the **token-merging logic** rather than the model. It covers dropping
`[CLS]`/`[SEP]` specials, renaming raw labels to entity names, merging `##`
continuation tokens into the preceding word, a continuation inheriting the previous
token's label even when its own differs, a leading continuation with nothing before
it, chained continuations, a realistic mixed sentence, and empty input.

That is the right thing to test. The model's predictions are not deterministic
across versions and are not this repository's code; the reassembly of WordPiece
tokens into labelled words is both, and it is where an off-by-one silently
mislabels a word.

---

## What is not covered

- **No component tests.** The `gui` suite covers domain logic and helpers; nothing
  renders a Vue component.
- **No end-to-end tests.** There is no Playwright or Cypress suite, so no test
  exercises the editor through a browser.
- **No coverage measurement.** Neither Vitest run passes `--coverage`, no pytest
  run passes `--cov`, and no threshold is configured anywhere. Coverage percentages
  for this component do not exist — which is why this page reports counts only.
- **The NLP model itself is untested**, deliberately. See the `nlp_api` note above.
