# Deployment

The CPRMV API runs as a Docker container. The image is built and pushed by GitLab CI to Docker Hub (`datafluisteraar/cprmv-api`).

---

## Docker image

The `serve_api/Dockerfile` builds from `python:3.12-bookworm`:

- Installs `nl_NL.UTF-8` locale.
- Copies `src/`, `data/`, and `respec/` into the image.
- Creates a non-root `appuser` for security.
- Exposes port `8000`.
- Health check via `urllib.request.urlopen('http://localhost:8000/', timeout=5)`.
- Entrypoint: `fastapi run src/serve.py --port 8000 --host 0.0.0.0`.

---

## Running with Docker Compose

`serve_api/docker-compose.yml` provides a production-ready configuration:

```yaml
services:
  cprmv-api:
    image: datafluisteraar/cprmv-api:${IMAGE_TAG:-latest}
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    environment:
      - PYTHONUNBUFFERED=1
```

The `data/` volume mount allows updating the XSLT files and method TTLs without rebuilding the image.

**Start:**

```bash
docker compose up -d
```

**Use a specific image version:**

```bash
IMAGE_TAG=abc1234 docker compose up -d
```

**Logs:**

```bash
docker compose logs -f cprmv-api
```

**Stop:**

```bash
docker compose down
```

---

## Synology NAS deployment

The original deployment target documented in `serve_api/README.md` is a Synology NAS:

```bash
# Build locally
cd /volume2/development/cprmv/serve-api/
docker build -t cprmv-fastapi .

# Run
docker run -d --name cprmv-api -p 8000:8000 cprmv-fastapi
```

On Synology, the data volume should be mounted from `/volume2/docker/cprmv/`.

---

## Updating to a new image version

After CI pushes a new image to Docker Hub:

```bash
docker compose pull
docker compose up -d
```

The `IMAGE_TAG` environment variable can pin to a specific commit SHA from the CI build output.

---

## Health check

The container's built-in health check polls `http://localhost:8000/` every 30 seconds with a 30-second timeout, 3 retries, and a 5-second start period. The `/` endpoint returns `{"CPRMV Rules Serve API": "0.4.0"}`.

External monitoring can poll:

```
GET https://cprmv.open-regels.nl/
GET https://acc.cprmv.open-regels.nl/
```
