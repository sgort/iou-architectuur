# Shared Backend

## Overview

The shared backend is a Node.js/Express API that provides TriplyDB integration and Operaton DMN execution for both CPSV Editor and Linked Data Explorer.

**Production API**: [backend.linkeddata.open-regels.nl](https://backend.linkeddata.open-regels.nl)  
**Acceptance API**: [acc.backend.linkeddata.open-regels.nl](https://acc.backend.linkeddata.open-regels.nl)

## Features

### TriplyDB Integration
- SPARQL query execution
- DMN metadata discovery
- Caching layer (5-minute TTL)
- Multiple endpoint support

### Operaton Integration
- DMN deployment
- Decision evaluation
- BPMN process execution

### Chain Orchestration
- Sequential DMN execution
- Variable mapping and passing
- Progress tracking
- Error handling

## API Endpoints

```
GET  /v1/health              - Health check
GET  /v1/dmns                - List all DMNs
POST /v1/chains/execute      - Execute DMN chain
POST /v1/triplydb/query      - SPARQL query
```

[View Full API Documentation →](api-documentation.md){ .md-button }

## Quick Links

- [API Documentation](api-documentation.md)
- [TriplyDB Integration](triplydb-integration.md)
- [Operaton Integration](operaton-integration.md)
- [Deployment Guide](deployment.md)

---

!!! warning "API Versioning"
    The API uses versioned endpoints (`/v1/`). Legacy endpoints (`/api/`) are deprecated.
