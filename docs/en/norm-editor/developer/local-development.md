---
component: Norm Editor
---

# Local Development

This page covers running the Norm Editor on your machine, both as a full stack and as a
frontend-only setup.

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose (for the full stack), or
- [Node.js](https://nodejs.org/) 20, 22, 24, 26 or 28 (the `engines` range in `gui/package.json`) for
  the frontend on its own; the frontend image and the pipeline build with Node 24.
- A **Triply API key** if you intend to read from or write to TriplyDB.

---

## Full stack with Docker Compose

1. Create a `.env` file in the project root:

   ```env
   TRIPLY_KEY_R=your-triply-api-key
   ```

2. Put the NLP model directories in `nlp_api/API_NLP/models/` — see
   [NLP models](#nlp-models).

3. Build and start every service:

   ```bash
   docker compose up --build
   ```

4. Open **http://localhost**.

All requests are proxied through nginx on port 80. For debugging, each service is also exposed
directly:

| Service | URL |
|---|---|
| backend | http://localhost:3000 |
| nlp-api | http://localhost:8081 |
| unwrap-api | http://localhost:5001 |
| wrap-up-api | http://localhost:5002 |

The Compose file sets the shared environment variables (Triply endpoints, the internal
service URLs and `MODEL_PATH`) on every service — see
[Environment Variables](../reference/environment-variables.md).

---

## NLP models

The model files are not in the repository and not in the `nlp-api` image. Compose sets
`MODEL_PATH=/mnt/models` and mounts `./nlp_api/API_NLP/models` at `/mnt/models` into both
`nlp-api` and `backend`. `nlp-api` loads each model from a directory of that name:

```
nlp_api/API_NLP/models/
├── bertje_2022_e4/              # the default model
└── legal-bert-dutch-english/
```

Without a model directory the stack still starts, but `/api/predict` for that model answers
`500` with `Model does not exist on filesystem.`

---

## Frontend only (hot reload)

When you are working on the UI with the Compose stack running:

```bash
cd gui
npm install
npm run dev
```

`npm run dev` runs `quasar dev`, which serves the app with hot reload on Quasar's default
port; pass `npm run dev -- --port 3333` for another one. `quasar.config.js` proxies `/api` to
`http://localhost:80`, the nginx of the running Compose stack, so the dev server talks to the
real services.

Build a production bundle with:

```bash
cd gui
npm run build
```

Other scripts: `npm run lint` (ESLint) and `npm run format` (Prettier).

---

## Running a single Python service

Each Python service runs on its own for focused work, with the same commands as its
Dockerfile — each pair from the repository root, in its own terminal:

```bash
cd unwrap_api && pip install -r requirements.txt
flask run --port=5001

cd wrap_up_api && pip install -r requirements.txt
flask --app=main run --port=5002

cd nlp_api/API_NLP && pip install -r requirements.txt
python app.py                   # port 8081; set MODEL_PATH to the models directory
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
