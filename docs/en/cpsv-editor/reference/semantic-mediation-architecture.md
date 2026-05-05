# Semantic Mediation Reference Architecture

This page documents the reference architecture for semantic mediation between business domain models and citizen-centric vocabularies. The CPSV Editor is the authoring tool that produces artefacts for the semantic mediation layer.

---

## Visual overview

```
┌────────────────────────────────────────────────────────────────────────┐
│                          CITIZEN CONTEXT                               │
│                                                                        │
│   Citizen Services / Portals / Letters / Forms / Chatbots / Voice UX   │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │           CITIZEN VOCABULARY (Presentation Model)              │   │
│   │   • Plain-language wording                                     │   │
│   │   • Life-event concepts                                        │   │
│   │   • UX terminology                                             │   │
│   │   • Multilingual variants                                      │   │
│   └────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
                                   ↕  CONTEXTUAL TRANSLATION / MAPPING
┌────────────────────────────────────────────────────────────────────────┐
│                     SEMANTIC MEDIATION LAYER                           │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │  Concept Mapping & Rules                                       │   │
│   │  • Ontology alignment                                          │   │
│   │  • Term mappings (citizen ↔ canonical)                         │   │
│   │  • Context rules                                               │   │
│   │  • Meaning validation                                          │   │
│   │  • Simplification & transformation                             │   │
│   └────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
                                   ↕  CANONICAL ALIGNMENT
┌────────────────────────────────────────────────────────────────────────┐
│                       BUSINESS SEMANTIC CORE                           │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │          CANONICAL INFORMATION MODEL                           │   │
│   │   • Harmonised core concepts                                   │   │
│   │   • Legal definitions                                          │   │
│   │   • Controlled vocabularies                                    │   │
│   └────────────────────────────────────────────────────────────────┘   │
│                                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │              BUSINESS DOMAIN MODEL                             │   │
│   │   • Policy concepts                                            │   │
│   │   • Service rules                                              │   │
│   │   • Product structures                                         │   │
│   └────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────┘
                                   ↕  IMPLEMENTATION
┌────────────────────────────────────────────────────────────────────────┐
│                        APPLICATION & DATA LAYER                        │
│                                                                        │
│   • APIs / Microservices                                               │
│   • Schemas & Databases                                                │
│   • Workflow Engines                                                   │
│   • Legacy Systems                                                     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Semantic layers

| Layer | Description |
|---|---|
| Citizen Context | Interaction channels communicating in plain language |
| Citizen Vocabulary | Presentation model with citizen-friendly terms |
| Semantic Mediation | Mapping, contextualisation, transformation, and validation |
| Canonical Information Model | Logical, harmonised semantic data model |
| Business Domain Model | Policy and product conceptual models |
| Application & Data Layer | Technical implementations |

---

## Architecture purpose

This reference architecture describes how business domain models are translated into citizen-centric vocabularies through an explicit semantic mediation layer, enabling clear and understandable communication with citizens, cross-system semantic interoperability, and legal and policy meaning preservation.

---

## TOGAF ADM positioning

| ADM Phase | Concern |
|---|---|
| Architecture Vision | Citizen-centric semantic alignment |
| Business Architecture | Service concepts and citizen communication vocabulary |
| Data Architecture | Canonical models and controlled vocabularies |
| Application Architecture | Semantic mediation and translation services |
| Technology Architecture | API gateways, middleware, and integration platforms |

---

## TOGAF terminology mapping

| Reference Architecture Element | TOGAF Term |
|---|---|
| Citizen Vocabulary | Business Architecture — Stakeholder Viewpoints |
| Semantic Mediation Layer | Application Architecture — Integration Services |
| Canonical Information Model | Data Architecture — Logical Data Model |
| Business Domain Model | Business Architecture — Business Objects |
| Physical Schemas | Data Architecture — Physical Data Model |
| Citizen Channels | Business Architecture — Front-Stage Processes |

---

## ArchiMate terminology mapping

| Reference Architecture Element | ArchiMate Element |
|---|---|
| Citizen Vocabulary | Business Object + Representation |
| Semantic Mediation | Application Service + Application Component |
| Ontology Mapping | Application Function |
| Canonical Information Model | Data Object |
| Business Domain Model | Business Object |
| APIs | Application Interface |
| Systems | Application Component |

---

## Positioning of the CPSV Editor

The CPSV Editor operates at the **Business Domain Model** and **Canonical Information Model** levels. It produces CPSV-AP 3.2.0 compliant Turtle files that represent government services using standardised EU and Dutch vocabularies. These artefacts are the canonical representation that the semantic mediation layer uses to bridge to citizen-facing vocabulary.

The RPP architectural pattern (Rules–Policy–Parameters) further decomposes the Business Domain Model level into its governance layers, ensuring that the semantic chain from legislation to citizen communication is fully traceable.
