# Operaton Deployment (VM)

Operaton is the BPMN/DMN execution engine. It runs as a single Docker container on the VM, shared between ACC and PROD (process definition version tags differentiate environments). It is exposed via Caddy at `https://operaton.open-regels.nl`.

## Repository structure

Operaton deployment is managed directly on the VM. There is no Operaton-specific folder in the `ronl-business-api` repository — Operaton's Docker image and configuration are maintained separately from the application code.

## Starting Operaton

```bash
ssh user@open-regels.nl

# Create the Operaton directory
mkdir -p ~/operaton
cd ~/operaton

# Create docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  operaton:
    image: operaton/operaton:latest
    container_name: operaton
    ports:
      - "127.0.0.1:8090:8080"
    environment:
      - DB_DRIVER=org.h2.Driver
      - DB_URL=jdbc:h2:./camunda-h2-databases/process-engine;TRACE_LEVEL_FILE=0;DB_CLOSE_ON_EXIT=FALSE
      - DB_USERNAME=sa
      - DB_PASSWORD=
    volumes:
      - operaton-data:/camunda
    restart: always
    networks:
      - npm-network

volumes:
  operaton-data:

networks:
  npm-network:
    external: true
EOF

docker compose up -d
```

## Verify

```bash
curl https://operaton.open-regels.nl/engine-rest/engine
# Expected: [{"name":"default"}]
```

The Operaton Cockpit UI is available at `https://operaton.open-regels.nl/app/cockpit/`.

## Deploying BPMN/DMN process definitions

Process definitions (`.bpmn` and `.dmn` files) are deployed to Operaton via its REST API. RONL ships with a `zorgtoeslag` process:

```bash
# Deploy zorgtoeslag BPMN
curl -X POST https://operaton.open-regels.nl/engine-rest/deployment/create \
  -F "deployment-name=zorgtoeslag" \
  -F "deploy-changed-only=true" \
  -F "zorgtoeslag.bpmn=@processes/zorgtoeslag.bpmn"
```

## Integration with the Business API

The backend connects to Operaton via `OPERATON_BASE_URL`:

```bash
OPERATON_BASE_URL=https://operaton.open-regels.nl/engine-rest
OPERATON_TIMEOUT=30000
```

`packages/backend/src/services/operaton.service.ts` handles all Operaton API calls. The service injects user context variables and maps Operaton responses to the Business API response format.

## Updating Operaton

```bash
cd ~/operaton
docker compose pull
docker compose up -d
docker compose logs -f operaton    # verify startup
```

Check the Operaton release notes before upgrading — BPMN/DMN deployment compatibility should be verified in the ACC environment first.
