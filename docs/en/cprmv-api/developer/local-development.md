---
component: CPRMV
---

# Local Development

---

## Prerequisites

- Python 3.14 — the Docker image and the CI test job both use `python:3.14-bookworm`
- `libxml2` and `libxslt` system libraries (required by lxml)

On Debian/Ubuntu:

```bash
sudo apt-get install libxml2-dev libxslt-dev
```

On macOS (Homebrew):

```bash
brew install libxml2 libxslt
```

!!! warning "Windows"
    `requirements.txt` and `requirements-dev.txt` pin `uvloop` (pulled in by `uvicorn[standard]`), which does not build on Windows. Install the requirements without that line.

---

## Setup

```bash
cd serve_api

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install runtime, dev and tool dependencies (what CI installs)
pip install -r requirements-dev.txt
```

`requirements-dev.txt` is compiled from `pyproject.toml` with the `dev` and `tools` extras, so it includes the runtime dependencies. `requirements.txt` holds the runtime dependencies only; it is what the Docker image installs.

The `Makefile` in `serve_api/` offers the same steps as targets:

| Target | Runs |
|---|---|
| `make install` | `pip install pip-tools`, `./pip-compile.sh`, `pip install -r requirements-dev.txt` |
| `make deps` | `./pip-compile.sh` — recompile both requirements files, keeping current pins |
| `make deps-upgrade` | `./pip-compile.sh --upgrade` — upgrade every pin |
| `make methods` | Regenerate `data/` from `rdf/0.4.2/` (see [Data files](#data-files)) |
| `make tests` | `pytest test` |

`pip-compile.sh` also takes `-P <package>` (repeatable) to upgrade a single package. Note that `make install` recompiles the requirements files before installing them.

---

## Running the development server

From the `serve_api/` directory:

```bash
fastapi dev src/serve.py
```

The server starts on `http://127.0.0.1:8000`. The Swagger UI is at `http://127.0.0.1:8000/docs`.

!!! note "Working directory"
    `serve.py` uses relative paths to load `./data/cprmvmethods.ttl`, `./data/cprmv.ttl` and `./respec/`, and `core_xml` reads its XSLT files from `./data/`. Start the server from `serve_api/`. The method modules are found relative to `src/`, in `serve_api/methods/`.

---

## Running tests

See [Testing](testing.md) for the commands, what they cover and what CI runs.

---

## Project dependencies

`pyproject.toml` declares the dependencies without versions; `pip-compile.sh` locks them into `requirements.txt` and `requirements-dev.txt`.

| Package | Locked version | Purpose |
|---|---|---|
| `fastapi[standard]` | 0.142.2 | Web framework, with Uvicorn and the `fastapi` CLI |
| `rdflib` | 7.6.0 | RDF graph storage and serialisation |
| `parse` | 1.22.2 | Pattern matching for ids, references and `unformat` |
| `lxml` | 6.1.3 | XSLT transform of publication XML |
| `ciso8601` | 2.3.3 | ISO 8601 date parsing |
| `fastmcp` | 4.0.10 | MCP server wiring (see [Architecture](architecture.md#mcp)) |

Dev extras: `pytest`, `pytest-cov`, `httpx`, `pre-commit`. Tool extras: `bandit`, `black`, `mypy`, `ruff`, `safety`, `vulture`.

---

## Data files

`serve_api/data/` holds what the API reads at runtime:

| File | Description |
|---|---|
| `cprmvmethods.ttl` | Methods registry — loaded at startup and served by `/methods` |
| `cprmv.ttl` | CPRMV vocabulary — merged into the methods knowledge graph at startup |
| `bwb2cprmv.xsl` | BWB XML → CPRMV |
| `cvdr2cprmv.xsl` | CVDR XML → CPRMV |
| `dmn13operaton2cprmv.xsl` | DMN 1.3 → CPRMV |
| `fmx42cprmv.xsl` | Formex 4 → CPRMV |

The files are committed and copied into the Docker image at build time.

`make methods` regenerates them from the specification: it copies `rdf/0.4.2/cprmv.ttl` and `rdf/0.4.2/cprmvmethods.ttl`, appends every `rdf/0.4.2/methods/*/method.ttl` to `cprmvmethods.ttl`, and copies the methods' `*.xsl` files. Run it after changing a method definition.

!!! warning "The committed `cprmvmethods.ttl` is not what `make methods` produces"
    At `0.4.2`, `serve_api/data/cprmvmethods.ttl` differs from the generated file: it still contains the removed NRML method, and its value lists use `cprmv:acknowledged`, which is the predicate the code reads. `rdf/0.4.2/cprmvmethods.ttl` writes those lists with `cprmvmethods:acknowledged`, so a regenerated file gives the code no acknowledged methods. The stale file is item 3 of [standards/cprmv#31](https://git.open-regels.nl/standards/cprmv/-/work_items/31).
