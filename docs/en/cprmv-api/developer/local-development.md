---
component: CPRMV
---

# Local Development

---

## Prerequisites

- Python 3.14 — the Docker image builds from `python:3.14-bookworm`, pinned by digest, and CI's `test` job uses Python 3.14
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
    Both requirements files are compiled **for Linux** and carry hashes, so they do not install on Windows as they are: `uvloop` does not build there, platform-only packages such as `colorama` are missing, and pip refuses anything without a hash. On Windows, run the API and its tests in Docker, or use WSL. From Git Bash at the repository root:

    ```bash
    docker build -t cprmv-api:local serve_api
    docker run --rm -p 8000:8000 cprmv-api:local
    ```

    The container command for the tests is under [Testing](testing.md#running-the-tests).

---

## Setup

```bash
cd serve_api

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install runtime, dev and tool dependencies (what CI installs)
pip install --require-hashes -r requirements-dev.txt
```

`requirements-dev.txt` is compiled from `pyproject.toml` with the `dev` and `tools` extras, so it includes the runtime dependencies. `requirements.txt` holds the runtime dependencies only; it is what the Docker image installs.

The `Makefile` in `serve_api/` offers the same steps as targets:

| Target | Runs |
|---|---|
| `make install` | `pip install pip-tools==7.6.2`, then `pip install -r requirements-dev.txt` |
| `make deps` / `make deps-linux` | Recompile both requirements files, with hashes, in a `python:3.14-bookworm` container pinned by digest, as CI checks them; `ARGS=--upgrade` upgrades every pin |
| `make deps-upgrade` | `make deps-linux ARGS=--upgrade` |
| `make methods` | Regenerate `data/` from `rdf/0.4.3/` (see [Data files](#data-files)) |
| `make tests` | `pytest test` |

`pip-compile.sh` also takes `-P <package>` (repeatable) to upgrade a single package. `make install` does not recompile. CI's `audit` check recompiles both files on Linux and fails on any difference, so a file compiled on Windows is rejected. Windows has no `make`; `SECURITY-PIPELINE.md` in the repository gives the equivalent `docker run`.

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

`pyproject.toml` declares the dependencies without versions; `pip-compile.sh` locks them, with hashes, into `requirements.txt` and `requirements-dev.txt` (`--generate-hashes --allow-unsafe --strip-extras`).

| Package | Locked version | Purpose |
|---|---|---|
| `fastapi[standard]` | 0.142.2 | Web framework, with Uvicorn and the `fastapi` CLI |
| `rdflib` | 7.6.0 | RDF graph storage and serialisation |
| `parse` | 1.22.2 | Pattern matching for ids, references and `unformat` |
| `lxml` | 6.1.3 | XSLT transform of publication XML |
| `ciso8601` | 2.3.3 | ISO 8601 date parsing |
| `fastmcp` | 4.1.8 | MCP server wiring (see [Architecture](architecture.md#mcp)) |

Dev extras: `pytest`, `pytest-cov`, `httpx`, `pre-commit`. Tool extras: `bandit`, `black`, `mypy`, `ruff`, `vulture`.

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
| `sttr2cprmv.xsl` | STTR (DSO) → CPRMV |

The files are committed and copied into the Docker image at build time.

`make methods` regenerates them from the specification: it copies `rdf/0.4.3/cprmv.ttl` and `rdf/0.4.3/cprmvmethods.ttl`, appends every `rdf/0.4.3/methods/*/method.ttl` to `cprmvmethods.ttl`, and copies the methods' `*.xsl` files. Run it after changing a method definition. At v0.4.3 the committed files are exactly what `make methods` generates.
