# IOU Architecture Documentation

Welcome to the comprehensive documentation for the IOU Architecture Framework and the RONL ecosystem.

## What is IOU Architecture?

The Information Architecture Framework for IOU integrates semantic web technologies, decision models, and Dutch government standards into a unified system for managing regulatory compliance and spatial planning.

## Ecosystem Components

### ⚙️ RONL Business API

The core business API layer that provides secure authentication and process orchestration for Dutch government services.

**Key Features:**  
- OpenID Connect (OIDC) authentication with DigiD/eIDAS  
- Multi-tenant architecture (per municipality)  
- Integration with Keycloak IAM and Operaton BPMN  
- Full audit logging for compliance  

**Live App**: [mijn.open-regels.nl](https://mijn.open-regels.nl)

[View Documentation →](ronl-business-api/index.md){ .md-button }

### ✏️ CPSV Editor
React-based application for creating CPSV-AP 3.2.0 compliant RDF/Turtle files for Dutch government services.

**Live App**: [cpsv-editor.open-regels.nl](https://cpsv-editor.open-regels.nl)

[View Documentation →](cpsv-editor/index.md){ .md-button }

### 🔍 Linked Data Explorer
Web application for SPARQL queries and BPMN & DMN orchestration with TriplyDB integration.

**Live App**: [linkeddata.open-regels.nl](https://linkeddata.open-regels.nl)

[View Documentation →](linked-data-explorer/index.md){ .md-button }

## Architecture Overview

```mermaid
graph TB
    subgraph "IOU Architecture Ecosystem"
        A[Municipality Portal<br/>React] -->|OIDC/JWT| B[Keycloak IAM]
        B -->|Validated Token| C[Business API<br/>Node.js]
        C -->|REST| D[Operaton BPMN<br/>Business Rules]
        
        E[CPSV Editor<br/>React] -->|TTL| F[TriplyDB<br/>Knowledge Graph]
        E -->|DMN Files| D
        
        F -->|SPARQL| G[Orchestration Service<br/>Node.js]
        G -->|Deploy BPMN+DMN| D
        
        H[Linked Data Explorer<br/>React] -->|API Calls| G
        H -->|Direct SPARQL| F
    end
```

## Quick Links

| Resource | Link |
|----------|------|
| **CPSV Editor** | [cpsv-editor.open-regels.nl](https://cpsv-editor.open-regels.nl) |
| **Linked Data Explorer** | [linkeddata.open-regels.nl](https://linkeddata.open-regels.nl) |
| **Backend API** | [backend.linkeddata.open-regels.nl](https://backend.linkeddata.open-regels.nl) |
| **Operaton** | [operaton.open-regels.nl](https://operaton.open-regels.nl) |
| **Keycloak IAM** | [keycloak.open-regels.nl](https://keycloak.open-regels.nl) |

## Technology Stack

The IOU Architecture ecosystem is built entirely on **open source technologies**:

| Component | Technology | License |
|-----------|-----------|---------|
| **IAM** | Keycloak | Apache 2.0 |
| **BPMN Engine** | Operaton | Apache 2.0 |
| **Backend** | Node.js + Express | MIT |
| **Frontend** | React | MIT |
| **Database** | PostgreSQL | PostgreSQL License |
| **Cache** | Redis | BSD 3-Clause |
| **Reverse Proxy** | Caddy | Apache 2.0 |
| **Knowledge Graph** | TriplyDB | - |

## Standards Compliance

- **CPSV-AP 3.2.0** - EU Public Service Vocabulary
- **CPRMV** - Core Public Rule Management Vocabulary
- **RONL** - Dutch Rules Vocabulary
- **BIO** - Baseline Informatiebeveiliging Overheid
- **NEN 7510** - Healthcare information security
- **AVG/GDPR** - Data protection

## Contributing

We welcome contributions! See the [Contributing Guide](contributing/index.md) for details.

---

**Documentation Version**: 1.0  
**Last Updated**: February 2026  
**License**: EUPL v1.2
