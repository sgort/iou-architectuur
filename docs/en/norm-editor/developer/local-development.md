# Local Development

This page covers running the Norm Editor on your machine, both as a full stack and as a
frontend-only setup.

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose (for the full stack), or
- [Node.js](https://nodejs.org/) v20+ (for the frontend on its own).
- A **Triply API key** if you intend to read from or write to TriplyDB.

---

## Full stack with Docker Compose

1. Create a `.env` file in the project root:

   ```env
   TRIPLY_KEY_R=your-triply-api-key
   ```

2. Build and start every service:

   ```bash
   docker compose up --build
   ```

3. Open **http://localhost**.

All requests are proxied through nginx on port 80. For debugging, each service is also exposed
directly:

| Service | URL |
|---|---|
| backend | http://localhost:3000 |
| nlp-api | http://localhost:8081 |
| unwrap-api | http://localhost:5001 |
| wrap-up-api | http://localhost:5002 |

The Compose file injects a `config.json` and shared environment variables (Triply endpoints
and the internal service URLs) into the relevant containers — see
[Environment Variables](../reference/environment-variables.md).

---

## Frontend only (hot reload)

When you are working on the UI against an already-running backend:

```bash
cd gui
npm install
npm run dev
```

Vite serves the app with hot reload (default port `5137`). Useful flags:

```bash
npm run dev -- --port=3333   # custom port
npm run dev -- --open        # open the browser automatically
```

Build a production bundle with:

```bash
cd gui
npm run build
```

Other scripts: `npm run lint` (ESLint) and `npm run format` (Prettier).

---

## Running a single Python service

Each Python service can run on its own for focused work. The pattern is the same for all
three:

```bash
cd unwrap_api          # or nlp_api/API_NLP, or wrap_up_api
pip install -r requirements.txt
python app.py
```

Or build and run its Docker image from the service directory. The NLP service additionally
ships an OpenAPI/Swagger UI at `/swagger`.

---

## Tests for the conversion services

The wrap-up and unwrap services come with fixture-based test suites:

```bash
cd wrap_up_api
python test_wrap_up.py
```

This dynamically generates a test for every `.json` fixture in `Tests/`, converts it to RDF,
and compares the result to the expected `.ttl` using RDFLib graph isomorphism, printing the
diff on failure. The fixtures double as worked examples of the
[Interpretation JSON Format](../reference/interpretation-json-format.md) and the
[FLINT Ontology](../reference/flint-ontology.md). Both services also include Jupyter notebooks
in which the conversion functions were developed and can be experimented with.
