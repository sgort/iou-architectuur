#!/bin/bash

# Content Synchronization Script
# Extracts and converts content from CPSV Editor and Linked Data Explorer READMEs
# to IOU Architecture documentation structure

set -e

echo "📚 IOU Architecture Content Sync Tool"
echo "======================================"

# Configuration
DOCS_DIR="docs/en"
CPSV_README="/mnt/project/README-CPSV-Editor.md"
LDE_README="/mnt/project/README-Linked-Data-Explorer.md"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to extract section from README
extract_section() {
    local readme_file=$1
    local section_start=$2
    local section_end=$3
    local output_file=$4
    
    echo -e "${BLUE}Extracting ${section_start} from $(basename ${readme_file})...${NC}"
    
    # Use awk to extract content between headers
    awk "
        /^## ${section_start}/,/^## ${section_end}/ {
            if (/^## ${section_end}/) exit;
            if (/^## ${section_start}/) next;
            print
        }
    " "${readme_file}" > "${output_file}.tmp"
    
    # Add frontmatter
    {
        echo "# ${section_start}"
        echo ""
        cat "${output_file}.tmp"
    } > "${output_file}"
    
    rm "${output_file}.tmp"
    echo -e "${GREEN}  ✓ Created ${output_file}${NC}"
}

# Function to create feature overview
create_features_page() {
    local readme_file=$1
    local output_file=$2
    local app_name=$3
    
    echo -e "${BLUE}Creating features page for ${app_name}...${NC}"
    
    # Extract features section
    awk '
        /^## ✨ Features/,/^## / {
            if (/^## / && !/^## ✨ Features/) exit;
            print
        }
    ' "${readme_file}" > "${output_file}"
    
    echo -e "${GREEN}  ✓ Created ${output_file}${NC}"
}

# Main sync process
sync_content() {
    echo ""
    echo -e "${YELLOW}Starting content synchronization...${NC}"
    echo ""
    
    # ===== CPSV Editor =====
    echo -e "${BLUE}=== Syncing CPSV Editor Documentation ===${NC}"
    
    # Features
    create_features_page "${CPSV_README}" \
        "${DOCS_DIR}/cpsv-editor/features.md" \
        "CPSV Editor"
    
    # Architecture
    extract_section "${CPSV_README}" \
        "Architecture" \
        "Standards Compliance" \
        "${DOCS_DIR}/cpsv-editor/technical/architecture.md"
    
    # Standards
    extract_section "${CPSV_README}" \
        "Standards Compliance" \
        "Getting Started" \
        "${DOCS_DIR}/cpsv-editor/technical/standards-compliance.md"
    
    # Development
    extract_section "${CPSV_README}" \
        "Development" \
        "Deployment" \
        "${DOCS_DIR}/cpsv-editor/technical/development.md"
    
    echo ""
    
    # ===== Linked Data Explorer =====
    echo -e "${BLUE}=== Syncing Linked Data Explorer Documentation ===${NC}"
    
    # Features
    create_features_page "${LDE_README}" \
        "${DOCS_DIR}/linked-data-explorer/features.md" \
        "Linked Data Explorer"
    
    # Architecture
    extract_section "${LDE_README}" \
        "Architecture Overview" \
        "Overview" \
        "${DOCS_DIR}/linked-data-explorer/technical/architecture.md"
    
    # Development
    extract_section "${LDE_README}" \
        "Development" \
        "Code Quality" \
        "${DOCS_DIR}/linked-data-explorer/technical/development.md"
    
    # API Reference - extract from README
    cat > "${DOCS_DIR}/linked-data-explorer/technical/api-reference.md" << 'EOF'
# API Reference

## Overview

The Linked Data Explorer backend provides a RESTful API for DMN discovery, chain orchestration, and SPARQL querying.

**Base URLs:**
- Production: `https://backend.linkeddata.open-regels.nl`
- Acceptance: `https://acc.backend.linkeddata.open-regels.nl`

## Endpoints

### Health Check

```http
GET /v1/health
```

Returns service status and version information.

**Response:**
```json
{
  "name": "Linked Data Explorer Backend",
  "version": "0.1.0",
  "status": "running",
  "environment": "production"
}
```

### List DMNs

```http
GET /v1/dmns
GET /v1/dmns?endpoint={triplydb_endpoint}
```

Lists all available DMN models from TriplyDB.

**Query Parameters:**
- `endpoint` (optional): Custom TriplyDB SPARQL endpoint
- `refresh` (optional): Bypass cache (`refresh=true`)

**Response:**
```json
[
  {
    "id": "urn:dmn:svb-kinderalimentatie",
    "title": "SVB Kinderalimentatie Berekening",
    "description": "Berekent kinderalimentatie verplichtingen",
    "inputs": [...],
    "outputs": [...]
  }
]
```

### Execute Chain

```http
POST /v1/chains/execute
```

Executes a sequence of DMN models with automatic variable orchestration.

**Request Body:**
```json
{
  "dmnIds": ["urn:dmn:1", "urn:dmn:2"],
  "inputs": {
    "age": 25,
    "income": 35000
  }
}
```

**Response:**
```json
{
  "success": true,
  "results": [...],
  "intermediateResults": [...],
  "executionTime": 842
}
```

### SPARQL Query

```http
POST /v1/triplydb/query
```

Executes SPARQL queries against TriplyDB.

**Request Body:**
```json
{
  "query": "SELECT * WHERE { ?s ?p ?o } LIMIT 10",
  "endpoint": "https://api.open-regels.triply.cc/..."
}
```

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK` - Successful request
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error responses include:
```json
{
  "error": "Error message",
  "details": "Additional context"
}
```

## Rate Limiting

Currently no rate limiting is enforced. Future versions may implement:
- 100 requests per minute per IP
- Burst allowance of 20 requests

## Authentication

Currently no authentication required. Future versions will support:
- API keys
- OAuth 2.0
- JWT tokens

---

For complete API documentation with interactive testing, visit the [Swagger UI](https://backend.linkeddata.open-regels.nl/api-docs) (when available).
EOF
    echo -e "${GREEN}  ✓ Created API reference${NC}"
    
    echo ""
    
    # ===== Shared Backend =====
    echo -e "${BLUE}=== Creating Shared Backend Documentation ===${NC}"
    
    # API Documentation (already created above as part of LDE)
    
    # TriplyDB Integration
    cat > "${DOCS_DIR}/shared-backend/triplydb-integration.md" << 'EOF'
# TriplyDB Integration

## Overview

The shared backend integrates with TriplyDB for storing and querying semantic data using SPARQL.

## Configuration

```typescript
// Environment variables
TRIPLYDB_ENDPOINT=https://api.open-regels.triply.cc/datasets/...
```

## DMN Discovery

DMNs are discovered from TriplyDB using CPRMV vocabulary:

```sparql
PREFIX cprmv: <http://purl.org/vocab/cprmv#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?dmn ?title ?description WHERE {
  ?dmn a cprmv:DecisionModel ;
       dcterms:title ?title ;
       dcterms:description ?description .
}
```

## Caching Strategy

- **Cache Duration**: 5 minutes
- **Per-Endpoint Caching**: Each TriplyDB endpoint has separate cache
- **Cache Bypass**: Use `?refresh=true` parameter

## Publishing

CPSV Editor publishes TTL files to TriplyDB via backend proxy:

```http
POST /api/triplydb/publish
Content-Type: text/turtle

@prefix cpsv: <http://purl.org/vocab/cpsv#> .
...
```

## Error Handling

- Connection timeouts: 30 seconds
- Retry logic: 3 attempts with exponential backoff
- Fallback: CORS proxy for public endpoints

---

See [API Documentation](api-documentation.md) for endpoint details.
EOF
    echo -e "${GREEN}  ✓ Created TriplyDB integration docs${NC}"
    
    # Operaton Integration
    cat > "${DOCS_DIR}/shared-backend/operaton-integration.md" << 'EOF'
# Operaton Integration

## Overview

The backend integrates with Operaton (open-source Camunda fork) for DMN execution and BPMN process orchestration.

## Configuration

```typescript
// Environment variables
OPERATON_BASE_URL=https://operaton.open-regels.nl/engine-rest
```

## DMN Deployment

DMN models are deployed to Operaton:

```typescript
// Deploy DMN file
POST /deployment/create
Content-Type: multipart/form-data

deployment-name: my-dmn-model
deployment-source: linked-data-explorer
enable-duplicate-filtering: true
deploy-changed-only: true
data: [DMN XML file]
```

## Decision Evaluation

Evaluate decisions with input variables:

```typescript
POST /decision-definition/key/{decisionKey}/evaluate

{
  "variables": {
    "age": { "value": 25, "type": "Integer" },
    "income": { "value": 35000, "type": "Integer" }
  }
}
```

## Process Execution

Execute BPMN processes:

```typescript
POST /process-definition/key/{processKey}/start

{
  "variables": {
    "applicantName": { "value": "John Doe", "type": "String" }
  },
  "businessKey": "application-12345"
}
```

## Chain Orchestration

The backend orchestrates DMN chains by:

1. Executing first DMN with initial inputs
2. Mapping outputs to next DMN's inputs
3. Repeating for entire chain
4. Collecting all results

```mermaid
sequenceDiagram
    participant Client
    participant Backend
    participant Operaton
    
    Client->>Backend: POST /chains/execute
    Backend->>Operaton: Evaluate DMN 1
    Operaton-->>Backend: Result 1
    Backend->>Backend: Map outputs to inputs
    Backend->>Operaton: Evaluate DMN 2
    Operaton-->>Backend: Result 2
    Backend->>Backend: Map outputs to inputs
    Backend->>Operaton: Evaluate DMN 3
    Operaton-->>Backend: Result 3
    Backend-->>Client: All results + timing
```

## Error Handling

- DMN not found: 404 with clear message
- Invalid inputs: 400 with validation errors
- Execution errors: 500 with Operaton error details

---

See [API Documentation](api-documentation.md) for endpoint details.
EOF
    echo -e "${GREEN}  ✓ Created Operaton integration docs${NC}"
    
    # Deployment
    cat > "${DOCS_DIR}/shared-backend/deployment.md" << 'EOF'
# Backend Deployment

## Overview

The shared backend is deployed to Azure App Service with automated CI/CD via GitHub Actions.

## Environments

| Environment | URL | Branch | Approval |
|------------|-----|--------|----------|
| Production | [backend.linkeddata.open-regels.nl](https://backend.linkeddata.open-regels.nl) | `main` | ✅ Required |
| Acceptance | [acc.backend.linkeddata.open-regels.nl](https://acc.backend.linkeddata.open-regels.nl) | `acc` | ❌ Auto |

## Configuration

### Environment Variables

```bash
NODE_ENV=production
PORT=8080
HOST=0.0.0.0

CORS_ORIGIN=https://linkeddata.open-regels.nl,https://backend.linkeddata.open-regels.nl
TRIPLYDB_ENDPOINT=https://api.open-regels.triply.cc/...
OPERATON_BASE_URL=https://operaton.open-regels.nl/engine-rest

LOG_LEVEL=info
```

### Azure App Service Settings

Set via Azure Portal or Azure CLI:

```bash
az webapp config appsettings set \
  --name ronl-linkeddata-backend-prod \
  --resource-group RONL-Preproduction \
  --settings \
    NODE_ENV=production \
    PORT=8080 \
    CORS_ORIGIN="https://linkeddata.open-regels.nl"
```

## Deployment Process

### Automatic (GitHub Actions)

1. Push to `main` or `acc` branch
2. GitHub Actions builds TypeScript
3. Runs linting and tests
4. Packages for deployment
5. (Production only) Waits for manual approval
6. Deploys to Azure App Service
7. Runs health check verification

### Manual Deployment

```bash
# Build locally
npm run build

# Deploy to Azure (production)
az webapp up \
  --name ronl-linkeddata-backend-prod \
  --resource-group RONL-Preproduction \
  --runtime "NODE:22-lts"
```

## Health Checks

Verify deployment:

```bash
# Production
curl https://backend.linkeddata.open-regels.nl/v1/health

# Acceptance
curl https://acc.backend.linkeddata.open-regels.nl/v1/health
```

Expected response:
```json
{
  "name": "Linked Data Explorer Backend",
  "version": "0.1.0",
  "status": "running",
  "environment": "production"
}
```

## Monitoring

### Logs

View logs in Azure Portal or via CLI:

```bash
az webapp log tail \
  --name ronl-linkeddata-backend-prod \
  --resource-group RONL-Preproduction
```

### Metrics

Monitor in Azure Portal:
- Response times
- Request count
- Error rate
- CPU/Memory usage

## Rollback

If deployment fails:

1. Via Azure Portal: Deployment Center → Revert to previous version
2. Via GitHub: Rerun previous successful workflow
3. Via Git: Revert commit and push

---

See [Linked Data Explorer deployment](../linked-data-explorer/technical/development.md#deployment) for frontend deployment.
EOF
    echo -e "${GREEN}  ✓ Created deployment docs${NC}"
    
    echo ""
    echo -e "${GREEN}======================================"
    echo "✅ Content synchronization complete!"
    echo "======================================${NC}"
    echo ""
    echo "Synced content from:"
    echo "  - CPSV Editor README"
    echo "  - Linked Data Explorer README"
    echo ""
    echo "Created documentation for:"
    echo "  - CPSV Editor (features, architecture, standards, development)"
    echo "  - Linked Data Explorer (features, architecture, API, development)"
    echo "  - Shared Backend (API, TriplyDB, Operaton, deployment)"
    echo ""
    echo "Next steps:"
    echo "1. Review extracted content for accuracy"
    echo "2. Add Dutch translations to docs/nl/"
    echo "3. Create user guides based on README content"
    echo "4. Test build: mkdocs serve"
    echo ""
}

# Run sync
sync_content

echo "Done! 🎉"
