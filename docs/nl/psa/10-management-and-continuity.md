---
title: "10. Beheer en continuïteit"
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

# 10. Beheer en continuïteit

## Wat dit hoofdstuk in uw PSA vastlegt

Wie IOU beheert, hoe nieuwe versies binnenkomen, hoe u merkt dat iets misgaat en
hoe u herstelt. Het belangrijkste onderscheid in dit hoofdstuk: wat u met de
software meekrijgt, wat het IOU-team doet, en wat u zelf regelt.

## Wat IOU beslist

**IOU neemt standaarden stap voor stap over en leert ervan** (AB-01). Onderdelen,
statussen en besluiten veranderen dus. Deze gids wordt elke week opnieuw
gecontroleerd tegen de vrijgegeven versies; de datum bovenaan elke pagina zegt
wanneer.

**Reproduceerbaar bouwen** (AB-28): vastgepinde afhankelijkheden, een SBOM bij elke
release, een wachttijd voor updates, en een wekelijkse meting tegen de
ICTU-richtlijn voor afhankelijkheden.

**Zelfstandige releases met kalenderversies; wijzigingen alleen via een pull
request** (AB-29). Elk onderdeel heeft zijn eigen versie en zijn eigen
releasemoment.

**Productie via een standaard leverstraat met een kwaliteitspoort** (AB-30). Die
is er nog niet: alle onderdelen leveren via het spoor voor snelle prototypes
(risico R-07).

### Wie doet wat

| Onderwerp | Meegeleverd met de software | Werkwijze van het IOU-team | Regelt u zelf |
|---|---|---|---|
| Afhankelijkheden | Vastgepind; SBOM per release | Updates via geautomatiseerde voorstellen, na een wachttijd; dagelijkse controle op kwetsbaarheden; driemaandelijkse review | De SBOM's die u in gebruik hebt opnieuw controleren op nieuwe kwetsbaarheden; eventueel een eigen pakketregister |
| Kwaliteit | Getest vóór elke release; minimale testdekking per bestand | Test- en controlepoorten op elke pull request | Uw eigen acceptatietest in uw eigen omgevingen |
| Versie-informatie | Elke webinterface en de backends tonen welke build draait | | Die informatie gebruiken in monitoring en bij incidenten |
| Licentie | EUPL-1.2 (Norm Editor: Apache-2.0) | | Licenties van uw eigen aanvullingen |
| Releases | Kalenderversies per onderdeel | Release en promotie naar productie via pull requests | Bepalen wanneer u een release overneemt |
| Broncode | Openbaar op GitHub; spiegel op GitLab | Spiegel bijgewerkt bij elke release | Bepalen welke bron u volgt |
| Hosting en omgevingen | | | Volledig ([hoofdstuk 9](09-technical-infrastructure.md)) |
| Monitoring en meldingen | Een gezondheidscontrole op de backends | | Volledig: wat u meet, wanneer u gewaarschuwd wordt |
| Incidenten | | | Volledig: melding, opvolging, communicatie |
| Back-up en herstel | | | Volledig, inclusief hersteltests |
| Kwetsbaarheden melden | Nog geen meldpunt | | Uw eigen meldproces; afspraken met IOU |

Dit geldt volledig voor de CPSV Editor, de Linked Data Explorer en de RONL
Business API. CPRMV en de Norm Editor worden op GitLab gebouwd, met een eigen,
lichter regime: CPRMV test vóór elke build op zijn hoofdbranch; de Norm Editor
heeft nog geen testdekking of controlepoorten.

## Fasering

| | Fase 1: medewerkers | Nu voorbereiden | Fase 2: inwoners en ondernemers |
|---|---|---|---|
| Ondersteuning | Interne servicedesk | Een uitbreidbaar incident- en ondersteuningsproces | Ondersteuning voor inwoners en ondernemers |
| Beschikbaarheid | Afgestemd op werktijden | Monitoring en waarschuwingen | Afspraken over beschikbaarheid buiten werktijd |
| Releases | Overnemen na eigen acceptatietest | Een vast ritme voor overname | Releases zonder onderbreking voor inwoners |

## Wat u invult

- De rollen: functioneel beheer, applicatiebeheer, technisch beheer, en wie
  beveiligingsupdates en incidenten afhandelt.
- Hoe u releases van IOU volgt en overneemt, en wie daarover beslist.
- Hoe u veranderingen in deze gids volgt: statussen, besluiten onder herziening,
  nieuwe versies van standaarden (AB-01).
- Monitoring, waarschuwingen en uw incidentproces.
- Back-up en herstel, en hoe vaak u herstel test.
- Hoe u bevindingen teruggeeft aan IOU, zodat IOU er ook van leert.

## Verder lezen

- [Overzicht van de controles](../contributing/controls.md)
- [De ontwikkelwerkwijze](../contributing/development-workflow/overview.md)
- [Bouwherkomst: welke build draait er](../contributing/build-provenance.md)
- [Twee sporen voor levering](../contributing/ci-posture-deck.md)
- [De spiegel op GitLab](../contributing/the-gitlab-mirror.md)
