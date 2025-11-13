# Architecture Diagram

## System Architecture

```mermaid
graph TB
    subgraph "Content Creation"
        A[Markdown Files<br/>docs/nl/*.md<br/>docs/en/*.md]
        B[GitLab Repository<br/>git.open-regels.nl]
    end
    
    subgraph "CI/CD Pipeline"
        C[GitLab Runner]
        D[MkDocs Build]
        E[Static HTML Output<br/>site/]
    end
    
    subgraph "Azure Cloud"
        F[Azure Static Web Apps]
        G[CDN/Edge Network]
        H[SSL Certificate<br/>Let's Encrypt]
    end
    
    subgraph "DNS"
        I[DNS Provider]
        J[iou-architectuur.open-regels.nl]
    end
    
    subgraph "End Users"
        K[Web Browsers]
        L[Mobile Devices]
    end
    
    A -->|git push| B
    B -->|trigger| C
    C -->|build| D
    D -->|generate| E
    E -->|deploy| F
    F -->|serve via| G
    G -->|with| H
    I -->|CNAME| J
    J -->|points to| F
    G -->|deliver| K
    G -->|deliver| L
    
    style A fill:#e1f5ff
    style B fill:#ffe1e1
    style F fill:#e1ffe1
    style K fill:#ffe1ff
    style L fill:#ffe1ff
```

## Deployment Flow

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant GL as GitLab
    participant CI as CI/CD Pipeline
    participant AZ as Azure SWA
    participant User as End User
    
    Dev->>GL: 1. git push main
    GL->>CI: 2. Trigger pipeline
    CI->>CI: 3. Install dependencies
    CI->>CI: 4. mkdocs build
    CI->>AZ: 5. Deploy to Azure
    AZ->>AZ: 6. Distribute to CDN
    User->>AZ: 7. Request page
    AZ->>User: 8. Serve HTML/CSS/JS
    
    Note over Dev,User: Total time: ~2-3 minutes
```

## Content Structure

```mermaid
graph LR
    subgraph "Dutch Content"
        A[index.md] --> B[deel-1-ontologie.md]
        A --> C[deel-2-implementatie.md]
        A --> D[deel-3-roadmap.md]
    end
    
    subgraph "English Content"
        E[index.md] --> F[part-1-ontology.md]
        E --> G[part-2-implementation.md]
        E --> H[part-3-roadmap.md]
    end
    
    subgraph "Shared Assets"
        I[images/]
        J[diagrams/]
        K[stylesheets/]
    end
    
    B -.uses.-> I
    C -.uses.-> J
    F -.uses.-> I
    G -.uses.-> J
    
    style A fill:#ffd700
    style E fill:#ffd700
    style I fill:#e1e1ff
    style J fill:#e1e1ff
    style K fill:#e1e1ff
```

## Data Flow

```mermaid
flowchart TD
    A[Framework<br/>Markdown Files] -->|MkDocs| B[Static HTML]
    B -->|GitLab CI| C[Deployment Package]
    C -->|Azure CLI| D[Azure Storage]
    D -->|CDN| E[Edge Locations]
    
    F[User Request] -->|DNS Lookup| G[iou-architectuur.open-regels.nl]
    G -->|CNAME| H[Azure SWA Hostname]
    H -->|Route| E
    E -->|Serve| I[User Browser]
    
    J[SSL Certificate] -->|Secure| E
    
    style A fill:#e1f5ff
    style D fill:#e1ffe1
    style I fill:#ffe1ff
    style J fill:#ffe1e1
```

## Multilingual Structure

```mermaid
graph TB
    A[Root URL<br/>iou-architectuur.open-regels.nl] -->|redirect| B[/nl/]
    A -->|manual| C[/en/]
    
    B --> D[Nederlandse Inhoud]
    C --> E[English Content]
    
    F[Language Switcher] -.toggle.-> B
    F -.toggle.-> C
    
    style A fill:#ffd700
    style B fill:#ff9999
    style C fill:#9999ff
    style F fill:#99ff99
```

## CI/CD Pipeline Stages

```mermaid
graph LR
    A[Code Push] --> B[Build Stage]
    B --> C{Tests Pass?}
    C -->|Yes| D[Deploy Stage]
    C -->|No| E[Fail Build]
    D --> F{Deploy Success?}
    F -->|Yes| G[Production Live]
    F -->|No| H[Rollback]
    
    style A fill:#e1f5ff
    style G fill:#e1ffe1
    style E fill:#ffe1e1
    style H fill:#ffe1e1
```

## Monitoring & Observability

```mermaid
graph TB
    A[User Traffic] --> B[Azure Static Web Apps]
    B --> C[Application Insights]
    C --> D[Metrics]
    C --> E[Logs]
    C --> F[Traces]
    
    G[GitLab Pipeline] --> H[Build Logs]
    G --> I[Deploy Status]
    
    D --> J[Dashboard]
    E --> J
    F --> J
    H --> J
    I --> J
    
    style B fill:#e1ffe1
    style C fill:#ffe1ff
    style J fill:#ffd700
```

---

These diagrams show:

1. **System Architecture**: Complete overview of components
2. **Deployment Flow**: Step-by-step deployment process
3. **Content Structure**: How documentation is organized
4. **Data Flow**: Request routing and SSL
5. **Multilingual**: Language switching mechanism
6. **CI/CD Pipeline**: Build and deploy stages
7. **Monitoring**: Observability strategy
