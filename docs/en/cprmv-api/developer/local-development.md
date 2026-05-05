# Local Development

---

## Prerequisites

- Python 3.12
- `libxml2` and `libxslt` system libraries (required by lxml)

On Debian/Ubuntu:

```bash
sudo apt-get install libxml2-dev libxslt-dev
```

On macOS (Homebrew):

```bash
brew install libxml2 libxslt
```

---

## Setup

```bash
cd serve_api

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install runtime dependencies
pip install -r requirements.txt

# Install dev dependencies (pytest, httpx, etc.)
pip install -r requirements-dev.txt
```

---

## Running the development server

From the `serve_api/` directory:

```bash
fastapi dev src/serve.py
```

The server starts on `http://127.0.0.1:8000`. The Swagger UI is at `http://127.0.0.1:8000/docs`.

!!! note "Working directory"
    `serve.py` uses relative paths to load `./data/cprmvmethods.ttl`, `./data/cprmv.ttl`, and `./respec/`. The server must be started from `serve_api/`.

---

## Running tests

```bash
python -m pytest -vv
```

The CI pipeline also runs a compile check and import check before pytest:

```bash
python -m py_compile src/serve.py
python -c "from src.serve import app; print('FastAPI app imported successfully')"
```

---

## Project dependencies

Declared in `pyproject.toml`:

| Package | Version | Purpose |
|---|---|---|
| `fastapi[standard]` | 0.116.1 | Web framework + Uvicorn server |
| `rdflib` | 7.1.4 | RDF graph storage and serialisation |
| `parse` | 1.20.2 | Pattern matching for unformat and ID detection |
| `lxml` | 6.0.0 | XSLT transform of publication XML |
| `ciso8601` | 2.3.3 | Fast ISO 8601 date parsing |

Dev extras: `pytest`, `pytest-cov`, `httpx`, `pre-commit`.

---

## Data files

`serve_api/data/` must contain:

| File | Required | Description |
|---|---|---|
| `cprmvmethods.ttl` | Yes | Methods registry — loaded at startup |
| `cprmv.ttl` | Yes | CPRMV vocabulary — merged into Methods KG at startup |
| `bwb2cprmv.xsl` | Yes | BWB XML → CPRMV XSLT |
| `cvdr2cprmv.xsl` | Yes | CVDR XML → CPRMV XSLT |
| `dmn13operaton2cprmv.xsl` | Yes | DMN 1.3 → CPRMV XSLT |
| `fmx4cellar2cprmv.xsl` | Yes | EU CELLAR Formex v4 → CPRMV XSLT |

These files are included in the repository and copied into the Docker image at build time.
