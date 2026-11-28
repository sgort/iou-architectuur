---
component: CPRMV
---

# Deployment

The CPRMV API runs as a Docker container. CI builds the image on every push to `acc` and `main` and publishes it to the GitHub Container Registry as `ghcr.io/open-regels/cprmv-api`, a public package; each tier's VM pulls it from there and runs it by digest. How the VMs deploy themselves is on [VM Deployment](vm-deployment.md).

---

## Docker image

`serve_api/Dockerfile`:

- Builds from `python:3.14-bookworm`, pinned by digest.
- Installs and sets the `nl_NL.UTF-8` locale (`LANG`, `LANGUAGE`, `LC_ALL`).
- Installs `requirements.txt` with `--require-hashes --no-deps`: every package must match its recorded hash, and nothing outside the file is resolved.
- Copies `src/`, `data/`, `respec/`, `methods/` and `certs/` into `/app`. `certs/` holds the certSIGN Web CA intermediate that `serve.py` adds to its SSL context, because `repository.officiele-overheidspublicaties.nl` omits it from its TLS handshake.
- Takes the commit, the CI run number and the release number as build arguments, `BUILD_SHA`, `BUILD_RUN` and `BUILD_RELEASE`, and keeps them in the environment, where `/health` reads them. Labels the image with its vocabulary version (`org.opencontainers.image.version`, `0.4.3`), source repository and revision; the release number is not a label.
- Creates a non-root `appuser` and runs as that user, on port `8000`.
- Health check: `GET http://localhost:8000/health` every 30 seconds.
- Command: `fastapi run src/serve.py --port 8000 --host 0.0.0.0`, which serves `app`, the API with the MCP server mounted at `/mcp`.

| Tag | Pushed by | Points at |
|---|---|---|
| `sha-<commit>` | every push to `acc` or `main` | that commit's build; what the VMs deploy |
| `acc` | every push to `acc` | the latest acceptance build |
| `stable` | every push to `main` | the latest stable build |
| `<version>`, the vocabulary version, e.g. `0.4.3` | every push to `main` | the latest stable build of that version |
| `vYYYY.MM.N`, the release, e.g. `v2026.11.0` | every push to `main` once there is a release | the latest stable build of that release |

The VMs never run a tag: they resolve `sha-<commit>` to its registry digest and run the digest. Each pushed digest carries a build provenance attestation and a BuildKit SBOM attestation. On 28 November 2026 `v2026.11.1`, `0.4.3` and `stable` named the same digest.

---

## Hosts

| Host | Tier | Branch | `/health` on 28 November 2026 |
|---|---|---|---|
| `https://cprmv.open-regels.nl/` | stable | `main` | `stable`, `v2026.11.1`, `0c4d236`, run 50 |
| `https://cprmv.open-rules.eu/` | stable (alias, same VM) | `main` | `stable`, `v2026.11.1`, `0c4d236`, run 50 |
| `https://acc.cprmv.open-regels.nl/` | acceptance | `acc` | `acceptance`, `v2026.11.1`, `ebf7def`, run 56 |

All three answer `{"CPRMV Rules Serve API":"0.4.3"}` on `/`, and `/mcp/` answers as an MCP endpoint; `/mcp` without the slash redirects to an `http://` address ([open-regels/cprmv#2](https://github.com/open-regels/cprmv/issues/2)). Each also serves `/deploy-status.json`, its VM's deployment status ([VM Deployment](vm-deployment.md#reading-deploy-statusjson)).

---

## Health check

`GET /health` reports the vocabulary version, the environment, the release and the build: the commit and CI run the image was built from, and the image digest ([API Endpoints](../reference/api-endpoints.md#get-health)). The image's own health check and the tier's Compose health check request it; CI and the reconciler go further and require `build.sha` to match the commit they expect ([VM Deployment](vm-deployment.md#what-health-proves)).

`/health` proves that the image a host runs was built from a given commit, not that every method loads. To check that methods load, request a rule, for example:

```
GET https://cprmv.open-regels.nl/rules/BWBR0015703_2025-07-01_0,Artikel%2020
```

---

## Running the image yourself

From the repository root:

```bash
docker build -t cprmv-api:local serve_api
docker run --rm -p 8000:8000 cprmv-api:local
```

or pull a published build, for instance `ghcr.io/open-regels/cprmv-api:stable`. A local build has no build arguments, so its `/health` reports `release`, `build.sha` and `build.run` as `null`; without a tier's Compose file, `environment` and `image.digest` are `null` too. The image carries its data: nothing needs to be mounted.
