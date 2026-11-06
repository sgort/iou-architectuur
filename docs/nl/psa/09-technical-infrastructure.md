---
title: "9. Technische infrastructuur"
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

# 9. Technische infrastructuur

## Wat dit hoofdstuk in uw PSA vastlegt

Waar IOU draait: hosting, containers, databases, netwerk, omgevingen en back-up.
Hosting is uw eigen keuze. IOU laat één referentie-inrichting zien als voorbeeld,
niet als voorschrift.

## Wat IOU beslist

IOU beslist over de onderdelen, niet over waar ze draaien. Drie besluiten raken
de infrastructuur wel:

- **De engine is nooit van buitenaf bereikbaar** (AB-13). Uw netwerkontwerp moet
  dat afdwingen: alleen de backends bereiken de engine (risico R-01).
- **Een engine met de Camunda 7 REST-API** (AB-14) en **een SPARQL
  1.1-triplestore** (AB-16). Welke u kiest en waar die draait, is aan u.
- **Elk onderdeel heeft zijn eigen database** (AB-25).

### De referentie-inrichting

| Onderdeel | Draait in de referentie op | In een container |
|---|---|---|
| Webinterfaces (CPSV Editor, Linked Data Explorer, RONL Business API) | Azure Static Web Apps | Nee |
| Backends van de Linked Data Explorer en de RONL Business API | Azure App Service (Node.js) | Nee |
| Databases van de Linked Data Explorer en de RONL Business API | Azure Database for PostgreSQL, één server per onderdeel | Nee |
| Procesengine (Operaton) en OIDC-uitgever (Keycloak) | Virtuele machine met Docker, achter een reverse proxy | Ja |
| Norm Editor | Azure Container Apps, ingericht met Bicep | Ja |
| CPRMV API | Container, op eigen servers | Ja |
| Kennisgraaf (TriplyDB) | Dienst van de leverancier | Niet van toepassing |

Gevolg voor u: CPRMV, de Norm Editor, de engine en Keycloak kunt u als container
overal draaien. Voor de Linked Data Explorer en de RONL Business API bestaan geen
containerbeschrijvingen of infrastructuur-als-code; draaien buiten Azure vraagt
eigen werk (risico R-13).

### Omgevingen (OTAP)

De IOU-onderdelen kennen vier omgevingen. Ontwikkeling en test draaien bij de
ontwikkelaar; acceptatie en productie zijn gedeelde omgevingen.

| Onderdeel | Ontwikkeling | Test | Acceptatie | Productie |
|---|---|---|---|---|
| CPSV Editor | lokaal | lokaal | ACC | PROD |
| Linked Data Explorer | lokaal | lokaal | ACC | PROD |
| RONL Business API | lokaal | lokaal | ACC | PROD |
| Operaton (platform) | lokaal | lokaal | ACC | nog niet: deelt de engine van ACC (R-12) |
| Keycloak (platform) | lokaal | lokaal | ACC | PROD |
| PostgreSQL (platform) | lokaal | lokaal | ACC | PROD |
| TriplyDB (linked data) | dataset O | dataset T | dataset A | eigen instantie |
| Documentmanagement, ondertekening, identiteitsbeheer, financiën (uw voorzieningen) | nabootsing | meestal geen | meestal geen | PROD |

De laatste regel is het probleem uit [hoofdstuk 7](07-integration-architecture.md#test-en-acceptatie-van-koppelingen):
uw bestaande voorzieningen hebben vaak alleen productie, dus op test en
acceptatie breekt de keten (risico R-14). **IOU raadt aan dat beheerders en
leveranciers voor elke gekoppelde voorziening een test- en acceptatieomgeving
inrichten** (route 3).

### Back-up en herstel

Azure Database for PostgreSQL maakt automatisch back-ups. Voor de virtuele machine
met de engine en Keycloak beschrijft de referentie een back-upprocedure, maar die
is niet als vaste taak ingericht. Voor de engine en de database van de Linked Data
Explorer is geen herstel getest (risico R-12).

## Fasering

| | Fase 1: medewerkers | Nu voorbereiden | Fase 2: inwoners en ondernemers |
|---|---|---|---|
| Netwerk | Alles binnen uw netwerk | Scheiding tussen portalen, API-laag, engine, databases en interne systemen | Portalen en publieke site bereikbaar vanaf internet |
| Beschikbaarheid | Afgestemd op werktijden | Monitoring en herstel inrichten | Ruimere beschikbaarheid; schaalbaarheid toetsen |
| Bescherming | Interne afscherming | Bepalen waar een WAF en DDoS-bescherming komen | WAF en DDoS-bescherming actief |

## Wat u invult

- Waar u elk onderdeel draait: eigen datacenter, overheidscloud, publieke cloud.
- Uw netwerkontwerp, met zones voor portalen, API-laag, engine, databases en
  interne systemen.
- Uw omgevingen per onderdeel, en per gekoppelde voorziening of route 3 er is.
- Back-up en herstel per onderdeel: frequentie, bewaartermijn, hersteltijd en
  hoeveel gegevensverlies acceptabel is; en wanneer u herstel test.
- Of u TriplyDB afneemt als dienst, zelf een triplestore draait, of een andere
  kiest (AB-16, onder herziening).

## Verder lezen

- [Overzicht van de inrichting van de RONL Business API](../ronl-business-api/developer/deployment/overview.md),
  met [Operaton](../ronl-business-api/developer/deployment/operaton.md) en
  [Keycloak](../ronl-business-api/developer/deployment/keycloak.md)
- [Inrichting van de Linked Data Explorer](../linked-data-explorer/developer/deployment.md)
- [Inrichting van de CPSV Editor](../cpsv-editor/developer/deployment.md)
- [Inrichting van de CPRMV API](../cprmv-api/developer/deployment.md)
- [Inrichting van de Norm Editor](../norm-editor/developer/deployment.md)
