---
title: "1. Managementsamenvatting"
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

# 1. Managementsamenvatting

**Doel.** IOU brengt wet- en regelgeving in een doorlopende keten naar de
uitvoering: van de interpretatie van een wettekst, via de beschrijving van een
dienst en zijn regels, naar het ontwerp en de uitvoering van het proces. Elke stap
levert een product op in een open formaat, dat de volgende stap ongewijzigd
overneemt en dat organisaties met elkaar delen. Een beslissing is zo terug te
voeren op het wetsartikel waarop ze rust.

**Aanleiding.** Organisaties die IOU invoeren, moeten een PSA schrijven. Deze gids
geeft daarvoor de basis: wat IOU heeft besloten, hoe bindend dat is, hoe ver IOU er
zelf mee is, en wat u invult.

**De belangrijkste architectuurkeuzes:**

- **IOU neemt standaarden in ontwikkeling stap voor stap over en leert ervan**
  (AB-01). Dit is het eerste besluit: het verklaart waarom statussen veranderen en
  waarom sommige besluiten onder herziening staan. Zo groeien CPRMV en het
  voorgestelde Nederlandse profiel voor DMN (DMN-AP NL) samen met IOU.
- **Gedeelde producten in open standaarden, gemaakt met vaste gereedschappen**:
  CPSV-AP en CPRMV met de CPSV Editor, BPMN en DMN met de Linked Data Explorer
  (AB-03, AB-06, AB-07, AB-08). Hier wijkt u niet van af.
- **Eén API-laag tussen alle portalen en de engine, met autorisatie per zaak in de
  backend** (AB-13, AB-18). Daardoor kunnen inwoners later toegang krijgen zonder
  verbouwing.
- **Eén OIDC-uitgever voor alle backends** (AB-17), waarachter u uw eigen
  inlogvoorziening en later DigiD en eHerkenning koppelt.
- **Engine, triplestore, inlogvoorziening en de Norm Editor zijn vervangbaar**
  (AB-12, AB-14, AB-16, AB-32), mits u de afwijking vastlegt.
- **Hosting, omgevingen, bewaartermijnen en beheer zijn uw eigen keuze.**

**Waar IOU nu staat.** IOU is als referentie nog niet af. De grootste open punten:
de engine is nog direct bereikbaar (R-01), de ontwerptools controleren nog niet wie
ze gebruikt (R-02), DigiD en eHerkenning zijn nog niet actief (R-03), en er is nog
geen standaard leverstraat (R-07). Op test en acceptatie breekt de keten naar uw
eigen voorzieningen (R-14); IOU raadt aan daar test- en acceptatieomgevingen voor
in te richten.

**Fasering.** Fase 1 is voor medewerkers en kan nu, mits u de ontwerptools en de
engine zelf afschermt. Fase 2 opent de uitvoering voor inwoners en ondernemers en
vraagt eerst aansluiting op DigiD en eHerkenning, een dreigingsanalyse, een
penetratietest en een formele vrijgave.
