# API Endpoints

All browser requests go through nginx, which routes by path prefix to one of the services
below. This page lists every endpoint the editor relies on.

---

## Routing summary

| Path (as seen by the browser) | Service |
|---|---|
| `/api/predict` | nlp-api |
| `/api/process_graph` | unwrap-api |
| `/api/process_and_save` | wrap-up-api |
| `/api/*` (everything else) | backend |
| `/*` | web (Quasar SSR) |

---

## backend

Base: the Node/Express service. Reads Triply credentials from environment variables.

### `GET /`

Health/welcome message.

### `GET /api/getSources`

Lists available source documents via SPARQL.

**Response**

```json
{ "message": "Sources retrieved!", "sources": { "head": {...}, "results": {...} } }
```

The `sources` body is a SPARQL JSON result with `iri`, `title`, `date`, and `editor` per
source, ordered newest first.

### `POST /api/getSource`

Exports one source graph as Turtle.

**Request** `{ "iri": "<source graph iri>" }`
**Response** `{ "message": "Source retreived!", "source": "<turtle string>" }`

### `POST /api/getTasksFromTriply`

Lists tasks via SPARQL.

**Request** `{ "endpoint": "TNO/editor/sparql" }`
**Response** `{ "message": "Tasks retrieved!", "tasks": { ...SPARQL JSON... } }` with `iri`,
`title`, `date`, `editor` per task.

### `POST /api/getTask`

Exports a task graph **and every graph it `calc:involves`** (interpretation + sources) as a
single TriG document.

**Request** `{ "iri": "<task iri>" }`
**Response** (JSON-encoded string) `{ "message": "Task retrieved!", "task": "<trig string>" }`

### `POST /api/saveTaskAtTriply`

Uploads a task to TriplyDB, skipping graphs that already exist online.

**Request** `{ "task": "<trig string>" }`
**Response** `{ "message": "Task saved!" }` on success (HTTP 200).

---

## nlp-api

### `POST /api/predict`

Predicts the constituents of an act frame for Dutch text.

**Request**

```json
{ "text": "de verwerkingsverantwoordelijke verwerkt persoonsgegevens" }
```

**Response**

```json
{
  "text": "...",
  "predicted_entities": [
    ["de", "None"],
    ["verwerkingsverantwoordelijke", "Actor"],
    ["verwerkt", "Action"],
    ["persoonsgegevens", "Object"]
  ]
}
```

Labels are `Action`, `Actor`, `Object`, `Recipient`, or `None`. A Swagger UI is available at
`/swagger`.

---

## unwrap-api

Converts FLINT RDF to editor JSON. The editor uses `/process_graph` (routed from
`/api/process_graph`); the others support its standalone download page.

| Method & path | Purpose |
|---|---|
| `GET /` | Renders the graph-picker page |
| `GET /get_graph_names` | List graph names from the Triply dataset |
| `GET /download_graph/<graph_iri>` | Download a graph as Turtle (gzip handled) |
| `POST /process_graph` | Convert posted Turtle (`Content-Type: text/turtle`) into editor JSON |
| `GET /process_and_download_graph/<graph_iri>` | Download a graph and return converted JSON |

**`POST /process_graph`** — body is a Turtle string; response is the editor JSON
interpretation.

---

## wrap-up-api

Converts an editor JSON interpretation to FLINT RDF and stores it.

| Method & path | Purpose |
|---|---|
| `POST /process_and_save` (routed) | Accepts an editor JSON interpretation, returns the FLINT RDF (Turtle/TriG) |

The editor calls this via `convertToRDF` before downloading a `.trig` file or saving to
TriplyDB.

---

## Notes

- The frontend sends an `X-API-KEY` header (from the `X_API_KEY` build variable) on the
  `predict` and `process_and_save` calls.
- CORS is enabled on the backend and the Python services.
- Error responses follow the usual HTTP status codes (`401`, `404`, `500`); the frontend
  surfaces them through an alert widget.
