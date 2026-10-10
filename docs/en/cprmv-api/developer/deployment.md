---
component: CPRMV
---

# Deployment

The CPRMV API runs as a Docker container. GitLab CI builds the image and pushes it to Docker Hub (`datafluisteraar/cprmv-api`); the hosts run it from there.

---

## Docker image

`serve_api/Dockerfile` on `main` builds from `python:3.14-bookworm`:

- Installs and sets the `nl_NL.UTF-8` locale (`LANG`, `LANGUAGE`, `LC_ALL`).
- Installs `requirements.txt`.
- Copies `src/`, `data/`, `respec/` and `certs/` into `/app`. `certs/` holds the certSIGN Web CA intermediate that `serve.py` adds to its SSL context, because `repository.officiele-overheidspublicaties.nl` omits it from its TLS handshake.
- Creates a non-root `appuser` and runs as that user.
- Exposes port `8000`.
- Health check via `urllib.request.urlopen('http://localhost:8000/', timeout=5)`.
- Command: `fastapi run src/serve.py --port 8000 --host 0.0.0.0`.

!!! warning "The Dockerfile on `main` does not copy `methods/`"
    The method modules in `serve_api/methods/` are not copied into the image. `serve.py` then finds no methods at startup, so an image built from `main`'s Dockerfile cannot load any method: `/` answers, but `/rules` and `/ref` cannot resolve any publication or reference. The fix, which adds `COPY methods/ ./methods/`, is [standards/cprmv!20](https://git.open-regels.nl/standards/cprmv/-/merge_requests/20) and is not yet merged. The hosts currently run an image built with that fix.

---

## Hosts

| Host | Version on `/` |
|---|---|
| `https://cprmv.open-regels.nl/` | 0.4.2 |
| `https://cprmv.open-rules.eu/` | 0.4.2 |
| `https://acc.cprmv.open-regels.nl/` | 0.4.2 |

All three answer `{"CPRMV Rules Serve API":"0.4.2"}` on `/` (checked 10 October 2026). `/mcp` answers 404 on all three: MCP is not reachable in the current deployment ([standards/cprmv#31](https://git.open-regels.nl/standards/cprmv/-/work_items/31)).

---

## Running with Docker Compose

`serve_api/docker-compose.yml` runs the published image:

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

The `data/` volume mount replaces the image's `data/` folder, so the XSLT files and method TTLs can be updated without rebuilding the image — and the mounted folder must contain all of them.

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

`serve_api/README.md` documents building and running the image on a Synology NAS:

```bash
# Build locally
cd /volume2/development/cprmv/serve-api/
docker build -t cprmv-fastapi .

# Run
docker run -d --name cprmv-api -p 8000:8000 cprmv-fastapi
```

On Synology, the data volume is mounted from `/volume2/docker/cprmv/`.

---

## Updating to a new image version

Nothing deploys automatically. The CI `deploy-cprmv-api` job only prints pull hints; a host is updated by pulling the new image and recreating the container:

```bash
docker compose pull
docker compose up -d
```

The `IMAGE_TAG` environment variable pins a specific commit SHA from the CI build output.

---

## Health check

The container's built-in health check polls `http://localhost:8000/` every 30 seconds with a 30-second timeout, 3 retries, and a 5-second start period. The `/` endpoint returns `{"CPRMV Rules Serve API": "0.4.2"}`. The compose file defines its own health check on the same URL (10-second timeout, 40-second start period).

The health check only proves the application started: an image without `methods/` passes it. To check that methods load, request a rule, for example:

```
GET https://cprmv.open-regels.nl/rules/BWBR0015703_2025-07-01_0,Artikel%2020
```
