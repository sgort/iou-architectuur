---
title: "2. Context en scope"
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

# 2. Context en scope

## Wat dit hoofdstuk in uw PSA vastlegt

Wat IOU doet, voor wie, welke processen het ondersteunt en waar het ophoudt. Na
dit hoofdstuk weet een lezer van uw PSA welke plek IOU krijgt in uw
informatievoorziening, en welke bestaande systemen het raakt.

## Wat IOU beslist

**IOU brengt wet- en regelgeving in een keten van stappen naar de uitvoering.**
Elke stap levert een product op dat de volgende stap ongewijzigd overneemt, in een
open formaat (AB-02):

| Stap | Wat er gebeurt | Onderdeel | Product |
|---|---|---|---|
| 1. Interpreteren | Juristen en beleidsmedewerkers leggen vast wat een wettekst betekent: welke handelingen, feiten en plichten erin staan. | Norm Editor | Interpretatie in FLINT, gekoppeld aan de brontekst |
| 2. Beschrijven | De dienst wordt beschreven: wat hij is, welke organisatie bevoegd is, op welke wet hij berust en welke regels gelden. | CPSV Editor, met CPRMV | Dienstbeschrijving (CPSV-AP) met regelsets (CPRMV) |
| 3. Ontwerpen | Beslissingen worden uitgewerkt in beslistabellen, het werk in een procesmodel, met formulieren en documentsjablonen. | Linked Data Explorer | Beslismodellen (DMN) en een procesbundel (BPMN, formulieren, sjablonen) |
| 4. Uitvoeren | Medewerkers behandelen zaken; beslissingen worden berekend; later doen inwoners zelf een aanvraag. | RONL Business API, met een procesengine | Zaken, taken, besluiten, documenten |
| 5. Verantwoorden | Regels, processen en het verwerkingsregister worden openbaar gemaakt. | RONL Business API (publieke site), Linked Data Explorer | Publieke regelcatalogus, procesbibliotheek, verwerkingsregister |

Daarnaast haalt de CPRMV API de actuele tekst van wetten en regelingen op uit de
officiële publicatiebronnen, zodat die tekst niet wordt overgenomen.

**De ontwerptools zijn voor medewerkers; inwoners komen alleen bij de portalen en
de publieke site** (AB-21). Fase 2 opent de uitvoering voor inwoners en
ondernemers, niet het ontwerp.

**Wie IOU gebruikt:**

| Gebruiker | Werkt met | Fase |
|---|---|---|
| Jurist, beleidsmedewerker | Norm Editor | 1 |
| Regelanalist, eigenaar van een dienst | CPSV Editor | 1 |
| Procesontwerper, producteigenaar | Linked Data Explorer | 1 |
| Behandelaar, teamleider | Werkomgeving van de RONL Business API | 1 |
| Beheerder | Alle onderdelen, de procesengine, de inlogvoorziening | 1 |
| Inwoner, gemachtigde | MijnOmgeving | 2 |
| Ondernemer | MijnOmgeving | 2 |
| Iedereen, zonder inloggen | Publieke site: regelcatalogus, procesbibliotheek, verwerkingsregister | 1 en 2 |

**Waar IOU ophoudt.** IOU is geen documentmanagementsysteem, geen
identiteitsvoorziening, geen basisregistratie en geen financieel systeem. Het
koppelt aan de voorzieningen die uw organisatie daarvoor al heeft (zie
[hoofdstuk 7](07-integration-architecture.md)). IOU vervangt ook niet in één keer
bestaande zaaksystemen: u kiest per proces of het in IOU wordt uitgevoerd.

## Fasering

| | Fase 1: medewerkers | Nu voorbereiden | Fase 2: inwoners en ondernemers |
|---|---|---|---|
| Gebruikers | Medewerkers van de eigen organisatie | Rollen voor inwoner en gemachtigde bestaan al in de inlogvoorziening | Inwoners, gemachtigden en ondernemers |
| Processen | Interne behandeling, met of zonder aanvraag van buiten | Processen zo ontwerpen dat een aanvraag ook van een inwoner kan komen | Aanvragen via MijnOmgeving |
| Openbaarheid | Publieke site met regels en processen | Bepalen wat openbaar wordt | Ongewijzigd |

## Wat u invult

- Welke processen u als eerste in IOU uitvoert, en waarom die.
- Welke van de vijf stappen u gebruikt. Niet elke organisatie begint bij het
  interpreteren van wetgeving.
- Welke gebruikersgroepen u in fase 1 toelaat, en wanneer fase 2 begint.
- Welke bestaande systemen IOU raakt: zaaksystemen, documentbeheer,
  ondertekening, identiteitsbeheer, financiën, basisregistraties.
- Waar IOU overlapt met wat u al heeft, en hoe u die overlap oplost.

## Verder lezen

- [Architectuur van IOU in dia's](../iou-architecture-deck.md)
- [Norm Editor](../norm-editor/index.md)
- [CPSV Editor](../cpsv-editor/index.md)
- [Linked Data Explorer](../linked-data-explorer/index.md)
- [RONL Business API](../ronl-business-api/index.md) en het
  [overzicht van de functies](../ronl-business-api/features/overview.md)
- [CPRMV API](../cprmv-api/index.md)
