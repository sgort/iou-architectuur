# Information Architecture Framework
## Lelystad-Zuid Ring Road Project

Welcome to the documentation of the Information Architecture Framework for the Lelystad-Zuid Ring Road Project.

## About this Framework

This framework defines the information architecture for managing regulatory compliance, spatial planning, and project governance for the Lelystad-Zuid Ring Road project using semantic web technologies and Dutch/EU standards.

### Key Features

- **Multi-layer ontology**: From legal to implementation level
- **MIM-compliant**: Follows the Metamodel for Information Modeling
- **Linked Data**: RDF/SKOS-based knowledge graph
- **Interoperability**: Based on EU CPSV-AP and Dutch standards

## Framework Structure

The framework consists of three main parts:

### [:material-file-document-outline: Part 1 - Ontological Architecture](part-1-ontology.md)

Defines the fundamental semantic structure:

- Namespace strategy and governance
- Core ontology classes (Infrastructure, Mitigation Measures, Compliance, Spatial)
- Properties and relationships
- Alignment with Dutch/EU vocabularies

### [:material-cogs: Part 2 - Implementation Architecture](part-2-implementation.md)

Practical implementation specifications:

- Standards collection and annotation
- Concept framework (MIM Level 1)
- Information model (MIM Levels 2-3)
- Process Blueprint
- Roles and access control
- Demonstrator architecture

### [:material-road-variant: Part 3 - Roadmap and Evaluation](part-3-roadmap.md)

Implementation planning and evaluation:

- 16-week implementation roadmap
- Success metrics and KPIs
- ROI analysis
- Next steps and decision points

## Project Context

**Project**: Lelystad-Zuid Ring Road  
**Province**: Flevoland, Netherlands  
**Components**: 
- Provincial section (Laan van Nieuw Land)
- Municipal section (Verlengde Westerdreef)

**Regulatory Framework**:
- Environment Act (Omgevingswet)
- Nature Conservation Act (NNN, Natura 2000)
- DSO/RTR (Digital System for the Environment Act)

## Technical Specifications

### Standards

| Standard | Purpose |
|----------|---------|
| **MIM** | Metamodel for Information Modeling (4 levels) |
| **NL-SBB** | SKOS-based concept description |
| **CPSV-AP** | EU Public Service Vocabulary |
| **CPRMV** | EU Core Public Records Management Vocabulary |
| **GeoSPARQL** | Spatial data integration |

### Namespace Strategy

```turtle
@prefix flvl-sp: <https://data.flevoland.nl/def/spatial-planning/> .
@prefix flvl-eco: <https://data.flevoland.nl/def/ecology/> .
@prefix flvl-def: <https://data.flevoland.nl/def/> .
@prefix flvl-id: <https://data.flevoland.nl/id/> .
@prefix flvl-concept: <https://data.flevoland.nl/concept/> .
```

## Use Cases

The framework supports three primary use cases:

1. **Compliance Dashboard**: Real-time overview of regulatory requirements
2. **Jurisdictional Coordination**: Management of provincial-municipal cooperation
3. **Knowledge Graph Exploration**: Semantic navigation through project data

## Getting Started

### For Architects
Start with [Part 1: Ontological Architecture](part-1-ontology.md) for the semantic foundations.

### For Developers
See [Part 2: Implementation Architecture](part-2-implementation.md) for technical specifications and SPARQL examples.

### For Project Managers
Consult [Part 3: Roadmap and Evaluation](part-3-roadmap.md) for implementation planning and ROI analysis.

## Demonstrator

A working demonstrator is available at:  
**https://iou.open-regels.nl**

The demonstrator shows:
- ✅ Compliance Dashboard with 19 requirements
- ✅ Interactive map with jurisdictional overlaps
- ✅ Knowledge Graph explorer with SPARQL queries

## Documentation Version

- **Version**: 1.0
- **Date**: November 2025
- **Status**: For stakeholder review
- **Next Review**: Q1 2026

## Contact

**Province of Flevoland**  
Department of Infrastructure & Environment

For questions or feedback about this framework, please contact your project manager.

---

!!! info "About this Documentation"
    This documentation is generated with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) and hosted on Azure Static Web Apps. Source files are available in GitLab CE.
