---
title: "7. Integratiearchitectuur"
scope: cross-cutting
verified:
  date: 2026-11-08
  against:
    CPSV Editor: "84886c9"
    Linked Data Explorer: "189435e"
    RONL Business API: "35fb3a8"
    Norm Editor: "c47096b"
    CPRMV: "8262d3e"
---

# 7. Integratiearchitectuur

## Wat dit hoofdstuk in uw PSA vastlegt

Welke API's IOU aanbiedt, welke koppelingen het met uw bestaande voorzieningen
heeft, en hoe systemen zich tegenover elkaar bekendmaken. Volledige
API-specificaties staan op de pagina's waarnaar dit hoofdstuk verwijst.

## Wat IOU beslist

**API's volgen de API Design Rules en hebben een OpenAPI-beschrijving die
automatisch wordt gecontroleerd** (AB-05). Dat geldt nu voor de RONL Business API
en de Linked Data Explorer.

**Regels worden afgenomen via een API met een vaste stabiliteitsbelofte** (AB-09).
De versie-2-API voor normen van de Linked Data Explorer is die afspraak; de
versie-1-API verdwijnt op 1 november 2028.

**Alle portalen praten met één API-laag, nooit rechtstreeks met de engine**
(AB-13).

**Backends vertrouwen tokens van één OIDC-uitgever** (AB-17). Een gebruiker
logt daar in; de backend controleert het token bij elk verzoek. Systemen die
namens zichzelf aanroepen, staan bij naam op een lijst van toegestane clients.

**Componenten koppelen via hun API, niet via elkaars database** (AB-25).

### API's van IOU

| API | Aangeboden door | Voor wie | Toegang |
|---|---|---|---|
| Zaken, taken, beslissingen, formulieren, documenten | RONL Business API | Werkomgeving en MijnOmgeving | Token van de OIDC-uitgever, met rol en organisatie |
| Publieke catalogi | RONL Business API | Iedereen | Zonder inloggen, alleen lezen, met een limiet op het aantal verzoeken (AB-22) |
| Normen, beslismodellen, procesbundels | Linked Data Explorer | Andere IOU-onderdelen, andere organisaties | Lezen openbaar; schrijven nog zonder controle (R-02) |
| Wettekst en verwijzingen | CPRMV API | Iedereen die wettekst nodig heeft | Openbaar |
| SPARQL | Kennisgraaf | IOU-onderdelen, andere organisaties | Lezen volgens de instelling van de dataset; schrijven met een token |

### Koppelingen met uw voorzieningen

IOU koppelt aan voorzieningen die uw organisatie al heeft. Welke dat zijn, is uw
keuze; de referentie-inrichting laat de volgende zien:

| Soort voorziening | Voorbeeld in de referentie | Koppeling |
|---|---|---|
| Inlogvoorziening voor medewerkers | Entra ID | Gekoppeld achter de OIDC-uitgever (AB-17) |
| Inlogmiddelen voor inwoners en ondernemers | DigiD, eIDAS, eHerkenning | DigiD en eIDAS voorbereid maar uitgeschakeld; eHerkenning is er nog niet (R-03) |
| Documentmanagement | eDOCS | De zaak bewaart een verwijzing (AB-24); de backend handelt namens de gebruiker |
| Ondertekening | ValidSign | Vanuit een taak in het proces |
| Berichtenbox | Doccle | Vanuit een taak in het proces |
| Basisregistratie personen | BRP via Haal Centraal | Bevragen, niet kopiëren (AB-26); nu nog een testvoorziening |

### Test en acceptatie van koppelingen

Hier zit een structureel probleem. De IOU-onderdelen hebben een ontwikkel-, test-,
acceptatie- en productieomgeving. Veel voorzieningen waaraan IOU koppelt, hebben
alleen een productieomgeving. Op test en acceptatie breekt de keten dan
(risico R-14). Er zijn drie routes:

| Route | Wat het is | Gevolg |
|---|---|---|
| 1. Nabootsingen doortrekken | Test en acceptatie gebruiken een nagebootste koppeling. | Acceptatie toetst een nabootsing. De echte koppeling wordt pas in productie voor het eerst gebruikt. |
| 2. Acceptatie op productie aansluiten | De acceptatieomgeving van IOU praat met de productievoorziening. | Echte documenten, handtekeningen en identiteiten komen in een testtraject. Het productieregime wordt doorbroken. |
| 3. Test en acceptatie laten inrichten | Beheerders en leveranciers richten een test- en acceptatieomgeving in voor elke gekoppelde voorziening. | Structureel; een besluit buiten IOU, met kosten bij de beheerder of leverancier. |

**IOU raadt route 3 aan.** Alleen daarmee toetst acceptatie de echte koppeling
zonder productiegegevens te raken. Route 1 is een tijdelijke uitweg zolang route 3
er niet is; route 2 is af te raden.

## Fasering

| | Fase 1: medewerkers | Nu voorbereiden | Fase 2: inwoners en ondernemers |
|---|---|---|---|
| API's | Gebruikt door de werkomgeving | Tokenvalidatie, autorisatie per zaak en een limiet op verzoeken zitten al in de backend | MijnOmgeving als extra client van dezelfde API |
| Inlogmiddelen | Inlogvoorziening van uw organisatie | Aansluiting op DigiD en eHerkenning plannen | DigiD, eHerkenning, eventueel eIDAS |
| Koppelingen | Met nabootsing of echte voorziening, per route | Route 3 aanvragen bij beheerders en leveranciers | Echte voorzieningen, getoetst op acceptatie |

## Wat u invult

- Welke voorzieningen u aan IOU koppelt, en welke route u per koppeling kiest. Kiest
  u niet voor route 3, leg dan uit waarom.
- Welke systemen namens zichzelf aanroepen, en hoe ze zich bekendmaken.
- Of u Digikoppeling nodig hebt voor de aansluiting op basisregistraties of andere
  overheidsorganisaties. IOU gebruikt het zelf niet.
- Welke API's u openstelt voor andere organisaties.

## Verder lezen

- [API-ontwerp van de RONL Business API](../ronl-business-api/features/api-design.md)
  en [authenticatie](../ronl-business-api/features/authentication-iam.md)
- [Stabiliteit van de API van de Linked Data Explorer](../linked-data-explorer/reference/api-stability.md)
- [Endpoints van de CPRMV API](../cprmv-api/reference/api-endpoints.md)
- [Documenten](../ronl-business-api/features/documents.md),
  [ondertekenen met ValidSign](../ronl-business-api/developer/validsign-signing.md)
