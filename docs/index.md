# Informatie Architectuur Framework
## Lelystad-Zuid Ringweg Project

De statische demonstrator [https://iou.open-regels.nl/](https://iou.open-regels.nl/) visualiseert de voorgestelde informatiearchitectuur voor het Lelystad-Zuid Ringweg Project. De getoonde data is fictief, dient ter illustratie én is work in progress.

<div class="image-row">
  <figure>
    <img src="assets/screenshots/screenshot1.png" alt="Compliance Dashboard">
    <figcaption>Compliance Dashboard</figcaption>
  </figure>
  <figure>
    <img src="assets/screenshots/screenshot2.png" alt="Jurisdictionele Coördinatie">
    <figcaption>Jurisdictionele Coördinatie</figcaption>
  </figure>
</div>

Deze site bevat de documentatie van het Informatie Architectuur Framework voor dit Project.

## Over dit Framework

Dit framework definieert de informatiearchitectuur voor het beheren van regelgevende naleving, ruimtelijke ordening en projectgovernance voor het Lelystad-Zuid Ringweg project met behulp van semantische webtechnologieën en Nederlandse/EU-standaarden.

### Belangrijkste Kenmerken

- **Multi-layer ontologie**: Van juridisch tot implementatieniveau
- **MIM-compliant**: Volgt het Metamodel voor Informatiemodellering
- **Linked Data**: RDF/SKOS-gebaseerde kennisgraaf
- **Interoperabiliteit**: Gebaseerd op EU CPSV-AP en Nederlandse standaarden

## Framework Structuur

Het framework bestaat uit drie hoofddelen:

### [:material-file-document-outline: Deel 1 - Ontologische Architectuur](deel-1-ontologie.md)

Definieert de fundamentele semantische structuur:

- Namespace strategie en governance
- Kern ontologie klassen (Infrastructuur, Mitigerende Maatregelen, Naleving, Ruimtelijk)
- Properties en relaties
- Alignering met Nederlandse/EU vocabulaires

### [:material-cogs: Deel 2 - Implementatie Architectuur](deel-2-implementatie.md)

Praktische implementatie specificaties:

- Standaarden collectie en annotatie
- Begrippenkader (MIM Level 1)
- Informatiemodel (MIM Levels 2-3)
- Process Blueprint
- Rollen en toegangscontrole
- Demonstrator architectuur

### [:material-road-variant: Deel 3 - Roadmap en Evaluatie](deel-3-roadmap.md)

Implementatie planning en evaluatie:

- 16-weken implementatie roadmap
- Success metrics en KPI's
- ROI analyse
- Volgende stappen en besluitpunten

## Project Context

**Project**: Lelystad-Zuid Ringweg  
**Provincie**: Flevoland, Nederland  
**Componenten**:

- Provinciale sectie (Laan van Nieuw Land)
- Gemeentelijke sectie (Verlengde Westerdreef)

**Regelgevend Kader**:

- Omgevingswet
- Natuurbeschermingswet (NNN, Natura 2000)
- DSO/RTR (Digitaal Stelsel Omgevingswet)

## Technische Specificaties

### Standaarden

| Standaard | Doel |
|-----------|------|
| **MIM** | Metamodel voor Informatiemodellering (4 niveaus) |
| **NL-SBB** | SKOS-gebaseerde begrippenbeschrijving |
| **CPSV-AP** | EU Public Service Vocabulary |
| **CPRMV** | EU Core Public Records Management Vocabulary |
| **GeoSPARQL** | Ruimtelijke data integratie |

### Namespace Strategie

```turtle
@prefix flvl-sp: <https://data.flevoland.nl/def/spatial-planning/> .
@prefix flvl-eco: <https://data.flevoland.nl/def/ecology/> .
@prefix flvl-def: <https://data.flevoland.nl/def/> .
@prefix flvl-id: <https://data.flevoland.nl/id/> .
@prefix flvl-concept: <https://data.flevoland.nl/concept/> .
```

## Use Cases

Het framework ondersteunt drie primaire gebruikssituaties:

1. **Compliance Dashboard**: Real-time overzicht van regelgevende vereisten
2. **Jurisdictionele Coördinatie**: Beheer van provinciaal-gemeentelijke samenwerking
3. **Knowledge Graph Exploratie**: Semantische navigatie door projectgegevens

## Aan de Slag

### Voor Architecten
Begin met [Deel 1: Ontologische Architectuur](deel-1-ontologie.md) voor de semantische fundamenten.

### Voor Ontwikkelaars
Zie [Deel 2: Implementatie Architectuur](deel-2-implementatie.md) voor technische specificaties en SPARQL voorbeelden.

### Voor Projectmanagers
Raadpleeg [Deel 3: Roadmap en Evaluatie](deel-3-roadmap.md) voor implementatie planning en ROI analyse.

## Demonstrator

Een werkende demonstrator is beschikbaar op: [https://iou.open-regels.nl](https://iou.open-regels.nl)

De demonstrator toont:

- ✅ Compliance Dashboard met 19 requirements
- ✅ Interactieve kaart met jurisdictie-overlaps
- ✅ Knowledge Graph explorer met SPARQL queries

## Documentatie Versie

- **Versie**: 1.0
- **Datum**: November 2025
- **Status**: Voor stakeholder review
- **Volgende Review**: Q1 2026

## Contact

**Provincie Flevoland**  
Afdeling Infrastructuur & Omgeving

Voor vragen of feedback over dit framework, neem contact op via uw projectmanager.

---

!!! info "Over deze Documentatie"
    Deze documentatie is gegenereerd met [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) en gehost op Azure Static Web Apps. De bronbestanden zijn beschikbaar in GitLab CE.
<- applies consistent line endings for cross-platform Build: 1763106765 -->
