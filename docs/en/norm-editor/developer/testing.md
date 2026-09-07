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
    runs it, against **2026.09.1** on **7 September 2026**, on `main` at `46e44c8`.
    One exception is marked in the table and explained under
    [What could not be measured here](#what-could-not-be-measured-here).

**At a glance:** 14 test files · **110 measured tests, all passing** · plus 9 more
in a suite this machine cannot run.

| Service | Language | Runner | Files | Tests | |
|---|---|---|--:|--:|---|
| `gui` | JavaScript (Quasar/Vue) | Vitest | 6 | **38** | measured |
| `backend` | JavaScript (Fastify) | Vitest | 2 | **11** | measured |
| `wrap_up_api` | Python (Flask) | pytest | 3 | **34** | measured |
| `unwrap_api` | Python (Flask) | pytest | 2 | **27** | measured |
| `nlp_api` | Python (Flask) | pytest | 1 | 9 † | **not run here** |

† Counted from `def test_` declarations rather than from the runner. The file
contains no parameterised cases, so the static count and the runner's should agree
— but that is an inference, not a measurement.

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

## What could not be measured here

**`nlp_api`'s suite did not run on this machine, and the reason is the runtime, not
the code.** Its `requirements.txt` pins `networkx==3.6.1`, which declares
`requires_python !=3.14.1,>=3.11`. This machine has Python **3.10.12**, so pip
resolves no candidate and the install fails before pytest is reached:

```
ERROR: Could not find a version that satisfies the requirement networkx==3.6.1
ERROR: No matching distribution found for networkx==3.6.1
```

CI runs these jobs on `python:3.14.6`, where the pin resolves. **This is an
environment limitation on the measuring machine, not a defect in the repository**
— stated here so the 9 in the table is not mistaken for a measured figure, and so
nobody re-investigates it as a bug.

The other two Python services install and run cleanly on 3.10, because neither
depends on the transformer stack that pulls `networkx` in.

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

### `gui` — 6 files, 38 tests

Domain logic only. The tests exercise the editor's in-memory model and its helper
functions, not Vue components.

| File | Covers |
|---|---|
| `test/unit/model/sentence.test.js` | Sentence structure |
| `test/unit/model/snippet.test.js` | Source snippets |
| `test/unit/model/booleanConstruct.test.js` | Boolean fact construction |
| `test/unit/helpers/dateTimeFunctions.test.js` | Date and time handling |
| `test/unit/helpers/sourceFormatting.test.js` | Source text formatting |
| `test/unit/helpers/utilities.test.js` | Shared utilities |

### `backend` — 2 files, 11 tests

`test/unit/routes.test.js` and `test/unit/helpers.test.js`. Since v2026.07.4 the
route tests use **`light-my-request`**, which drives Fastify's routing in-process
rather than over a socket — faster, and with no port to collide on.

### `wrap_up_api` — 3 files, 34 tests

`test_wrap_up.py`, `test_routes.py` and `test_helpers.py`. The largest suite in the
repository, covering the service that assembles a finished interpretation.

### `unwrap_api` — 2 files, 27 tests

`test_routes.py` and `test_helpers.py`, covering the inverse transformation.

### `nlp_api` — 1 file, 9 tests

`test_labeling.py`, and it is worth reading even though it does not run here: every
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
