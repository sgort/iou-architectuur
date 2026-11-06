---
title: "6. Gegevensarchitectuur"
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

# 6. Gegevensarchitectuur

## Wat dit hoofdstuk in uw PSA vastlegt

Welke gegevens IOU gebruikt en maakt, waar ze staan, wie eigenaar is en hoe lang
ze bewaard worden. Een volledig gegevensmodel hoort in het technisch ontwerp; dit
hoofdstuk legt de hoofdlijnen en de verantwoordelijkheden vast.

## Wat IOU beslist

**Gedeelde producten staan in de kennisgraaf, elk in een eigen graaf per
organisatie en dienst** (AB-10). Opnieuw publiceren overschrijft die graaf, dus
eerdere versies blijven niet bewaard (risico R-06).

**De organisatie reist mee met alles** (AB-15). Elke uitrol en elke zaak hoort
bij één organisatie. Wie bij welke zaak mag, bepaalt de backend aan de hand van
een organisatielabel dat de server zelf zet (AB-18).

**Elk geauthenticeerd verzoek wordt vastgelegd in een aparte auditopslag**
(AB-23). De bewaartermijn bepaalt u; IOU past er nog geen toe (risico R-10).

**Documenten blijven in uw documentmanagementsysteem; de zaak bewaart alleen een
verwijzing** (AB-24).

**Elk onderdeel beheert zijn eigen gegevens** (AB-25) en **gegevens blijven bij de
bron** (AB-26): basisregistraties worden bevraagd, niet gekopieerd. De RONL
Business API leest nog rechtstreeks uit de database van de Linked Data Explorer
(risico R-09).

**Het verwerkingsregister kan per proces in de Linked Data Explorer worden
bijgehouden** (AB-27). Dat is vervangbaar: u mag uw bestaande register gebruiken.

### Gegevensobjecten

| Gegevens | Waar ze staan | Eigenaar | Bewaartermijn |
|---|---|---|---|
| Interpretaties van wetgeving (FLINT) | Kennisgraaf | De organisatie die interpreteert | Eigen keuze |
| Dienstbeschrijvingen en regelsets | Kennisgraaf, één graaf per organisatie en dienst | De bevoegde organisatie | Eigen keuze; geen geschiedenis (R-06) |
| Beslismodellen (DMN) | Procesengine; vindbaar via de kennisgraaf | De organisatie die ze vaststelt | Eigen keuze |
| Procesbundels: proces, formulieren, documentsjablonen | Database van de Linked Data Explorer; uitgerold in de procesengine | De organisatie die het proces ontwerpt | Eigen keuze |
| Verwerkingsregister | Database van de Linked Data Explorer; openbaar zonder contactgegevens | De verwerkingsverantwoordelijke | Zolang de verwerking bestaat |
| Zaken: procesgegevens en beslissingen | Procesengine | De organisatie van de zaak | Eigen keuze; IOU stelt geen termijn in |
| Documenten | Uw documentmanagementsysteem | De organisatie van de zaak | Volgens uw selectielijst |
| Auditgegevens | Aparte database van de RONL Business API | Uw organisatie | Eigen keuze; nog niet toegepast (R-10) |
| Persoonsgegevens uit basisregistraties | Bij de bron; opgevraagd wanneer nodig | De bronhouder | Niet gekopieerd |
| Wettekst | Officiële publicatiebronnen; opgevraagd via de CPRMV API | De wetgever | Niet gekopieerd |

Twee kleinere opslagplekken: de Linked Data Explorer bewaart testgevallen en
sjablonen voor ketens in de browser van de gebruiker, en de CPSV Editor bewaart
daar het TriplyDB-token waarmee wordt gepubliceerd (zie
[hoofdstuk 8](08-security-and-privacy.md)).

## Fasering

| | Fase 1: medewerkers | Nu voorbereiden | Fase 2: inwoners en ondernemers |
|---|---|---|---|
| Zaakgegevens | Zaken van de eigen organisatie | Autorisatie per zaak werkt al in de backend (AB-18) | Inwoners zien alleen hun eigen zaken |
| Persoonsgegevens | Verwerking door medewerkers | Grondslag, doel en bewaartermijn per verwerking vastleggen | Inzage door de inwoner zelf; opnieuw beoordelen |
| Auditgegevens | Handelingen van medewerkers | Bewaartermijn vaststellen en toepassen | Ook handelingen van inwoners |

## Wat u invult

- Welke gegevens u in IOU verwerkt, met grondslag en doel per verwerking.
- Bewaartermijnen per gegevensobject, afgeleid van uw selectielijst, en wie het
  opschonen uitvoert.
- Hoe u eerdere versies van gepubliceerde dienstbeschrijvingen archiveert, zolang
  IOU dat niet doet.
- Welk documentmanagementsysteem u koppelt, en waar uw verwerkingsregister staat.
- Hoe u gegevens overdraagt als u stopt met IOU: de gedeelde producten staan in
  open formaten in de kennisgraaf; zaakgegevens moet u uit de procesengine halen.

## Verder lezen

- [Publiceren naar TriplyDB](../cpsv-editor/features/triplydb-publishing.md)
- [Opslag van procesbundels](../linked-data-explorer/developer/asset-storage.md)
  en de [database van de Linked Data Explorer](../linked-data-explorer/developer/deployment-postgresql.md)
- [Het verwerkingsregister](../linked-data-explorer/features/ropa-records.md)
- [Zaken en organisaties](../ronl-business-api/features/processes.md) en
  [documenten](../ronl-business-api/features/documents.md)
