---
title: "4. Functionele architectuur"
scope: cross-cutting
verified:
  date: 2026-11-06
  against:
    CPSV Editor: "0412e9b"
    Linked Data Explorer: "814c4bb"
    RONL Business API: "ff6c362"
    Norm Editor: "c47096b"
    CPRMV: "8262d3e"
---

# 4. Functionele architectuur

## Wat dit hoofdstuk in uw PSA vastlegt

De hoofdfuncties van IOU, de rollen die ermee werken, en hoe IOU uw processen
ondersteunt. Schermen en volledige functionele eisen horen in een functioneel
ontwerp; dit hoofdstuk blijft op het niveau van functies.

## Wat IOU beslist

**Elke stap heeft één gereedschap, en de producten zijn gedeeld.** Diensten worden
beschreven met de CPSV Editor (AB-06), regels in CPRMV (AB-07), processen ontworpen
in de Linked Data Explorer (AB-08). Juridische interpretatie gebeurt in FLINT met
de Norm Editor; dat gereedschap is vervangbaar (AB-12).

**De organisatie reist mee met alles wat wordt uitgerold** (AB-15). Een beslismodel
wordt één keer uitgerold en door meerdere organisaties gebruikt; verschillen per
organisatie staan in de beslistabel zelf. Een proces en een zaak horen altijd bij
één organisatie.

### Hoofdfuncties

| Functie | Wat het doet | Onderdeel |
|---|---|---|
| Wettekst interpreteren | Brontekst ophalen, handelingen, feiten en plichten markeren (met suggesties uit taalanalyse), en de interpretatie opslaan in de kennisgraaf. | Norm Editor |
| Dienst beschrijven | Dienst, bevoegde organisatie en wettelijke grondslag vastleggen; regels scheiden in regels, beleid en parameters, elk met een eigen eigenaar. | CPSV Editor |
| Publiceren | De dienstbeschrijving met regels valideren en publiceren in de kennisgraaf. | CPSV Editor |
| Wettekst opvragen | De geldende tekst van een wet of regeling ophalen bij de officiële bron, op een gekozen datum. | CPRMV API |
| Beslissingen ontwerpen | Beslismodellen vinden, testen en aan elkaar koppelen tot een keten, ook over organisaties heen. | Linked Data Explorer |
| Processen ontwerpen | Een proces modelleren met fasen, rollen en taken; formulieren en documentsjablonen maken; het geheel als bundel uitrollen. | Linked Data Explorer |
| Kwaliteit bewaken | Beslismodellen en gedeelde producten valideren; vastleggen wie een product heeft gevalideerd of gecertificeerd. | Linked Data Explorer |
| Verwerkingsregister bijhouden | Per proces de verwerking van persoonsgegevens vastleggen en publiceren. | Linked Data Explorer |
| Zaken behandelen | Taken zien, oppakken, afhandelen; beslissingen laten berekenen; formulieren invullen; documenten maken en bewaren. | RONL Business API |
| Aanvragen doen (fase 2) | Een inwoner of gemachtigde start een dienst en volgt de eigen zaken. | RONL Business API (MijnOmgeving) |
| Openbaar maken | Regelcatalogus, procesbibliotheek en verwerkingsregister zonder inloggen raadplegen. | RONL Business API (publieke site), Linked Data Explorer |

### Rollen

De inlogvoorziening kent een paar vaste rollen, en daarnaast rollen per proces.

| Rol | Wat de rol mag | Laag |
|---|---|---|
| Inwoner | Eigen aanvragen doen en eigen zaken zien (fase 2) | Kern |
| Gemachtigde | Namens een ander optreden, binnen de machtiging (fase 2) | Kern |
| Behandelaar | Zaken van de eigen organisatie behandelen | Kern |
| Beheerder | Beheer van de eigen organisatie | Kern |
| Procesrollen | Taken binnen één proces, zoals indiener, jurist of ondertekenaar; in het procesmodel gekoppeld aan taken | Eigen keuze |

De ontwerptools kennen nog geen rollen: ze controleren niet wie ze gebruikt
(AB-20, risico R-02).

## Fasering

| | Fase 1: medewerkers | Nu voorbereiden | Fase 2: inwoners en ondernemers |
|---|---|---|---|
| Rollen | Behandelaar, beheerder, procesrollen | De rollen inwoner en gemachtigde bestaan al; ontwerp processen zo dat ze die kunnen gebruiken | Inwoner en gemachtigde actief |
| Processen | Gestart door een medewerker | Bepaal per proces of een inwoner het later zelf mag starten | Gestart door inwoner of gemachtigde |
| Beslissingen | Berekend voor de behandelaar | Beslissingen die een inwoner vooraf mag laten berekenen, vragen alleen niveau `basis` (AB-19) | Inwoner laat zelf berekenen |

## Wat u invult

- Welke hoofdfuncties u in fase 1 gebruikt.
- Welke processen u ondersteunt, en welke procesrollen daarbij horen.
- Hoe de rollen aansluiten op uw organisatie: wie mag behandelen, wie beheert,
  wie publiceert, wie mag uitrollen.
- Wie eigenaar is van elk gedeeld product: welke afdeling beschrijft een dienst,
  welke stelt regels vast, welke ontwerpt het proces.

## Verder lezen

- [Het FLINT-framemodel](../norm-editor/features/flint-frame-model.md)
- [Dienst, organisatie en wettelijke grondslag](../cpsv-editor/features/service-organisation-legal.md)
  en [regels, beleid en parameters](../cpsv-editor/reference/rpp-architecture.md)
- [De BPMN Modeler](../linked-data-explorer/features/bpmn-modeler.md) en
  [ketens van beslissingen](../linked-data-explorer/features/dmn-chain-building.md)
- [Taken](../ronl-business-api/features/tasks.md),
  [beslissingen uitvoeren](../ronl-business-api/features/business-rules-execution.md)
  en [rollen in de inlogvoorziening](../ronl-business-api/reference/keycloak-realm.md)
