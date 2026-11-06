---
title: "11. Architectuurbesluiten en risico's"
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

# 11. Architectuurbesluiten en risico's

Dit hoofdstuk is de ruggengraat van de gids. Het besluitenregister bevat alle
besluiten die IOU heeft genomen, met hun laag en hun status. De andere
hoofdstukken verwijzen ernaar met het nummer. Neem het register over in uw eigen
PSA, vul het aan met uw afwijkingen, en neem de risico's over die voor u gelden.

Wat de lagen en de statussen betekenen, staat op de pagina
[Over deze PSA](index.md#drie-lagen).

## Besluitenregister

| ID | Besluit | Laag | Status | Toelichting |
|---|---|---|---|---|
| AB-01 | Elke stap levert zijn product op in een open formaat; niets wordt overgetypt. | Kern | deels | Van dienstbeschrijving tot uitvoering klopt dit. De stap van juridische interpretatie (Norm Editor) naar dienstbeschrijving (CPSV Editor) gaat nog met de hand. |
| AB-02 | Gedeelde producten gebruiken CPSV-AP 3.2.0, CPRMV 0.4.2, BPMN 2.0, DMN 1.3, RDF/Turtle, SKOS/NL-SBB en ELI, BWB, CVDR en JuriConnect voor verwijzingen naar wetgeving. | Kern | deels | De CPSV Editor schrijft nog CPRMV 0.4.1. |
| AB-03 | Open source is de standaard (EUPL-1.2). Een gesloten product kan alleen achter een vervangbare koppeling. | Kern | deels | CPSV Editor, Linked Data Explorer, RONL Business API en CPRMV hebben EUPL-1.2; de Norm Editor heeft Apache-2.0. De RONL Business API vraagt in productie een gesloten taaldienst (zie AB-30). |
| AB-04 | API's volgen de API Design Rules en hebben een OpenAPI 3.1-beschrijving die automatisch wordt gecontroleerd. | Kern | deels | RONL Business API en Linked Data Explorer wel; CPRMV en de Norm Editor nog niet. |
| AB-05 | Publieke dienstverlening wordt beschreven en gepubliceerd met de CPSV Editor. | Kern | gerealiseerd | |
| AB-06 | Regels worden vastgelegd in CPRMV: een regelset hoort bij een publieke dienst, verwijst naar de wet waarop hij berust, en heeft een geldigheidsperiode. | Kern | deels | De CPSV Editor koppelt een regelset aan de wet met een andere relatie dan CPRMV voorschrijft. CPRMV is nog een eerste openbare werkversie. |
| AB-07 | Processen worden ontworpen in de Linked Data Explorer en alleen via zijn backend uitgerold, als één bundel van proces, formulieren en documentsjablonen. | Kern | gerealiseerd | |
| AB-08 | Beslismodellen worden gevonden met standaard SPARQL; regels worden afgenomen via de versie-2-API voor normen, met een vaste stabiliteitsbelofte. | Kern | gerealiseerd | De versie-1-API is uitgefaseerd en verdwijnt op 1 november 2028. |
| AB-09 | Elke gepubliceerde dienst staat in één eigen graaf per organisatie en dienst, op een vast adres. | Kern | gerealiseerd | Opnieuw publiceren overschrijft de graaf; er blijft geen geschiedenis bewaard (risico R-06). |
| AB-10 | Gedeelde producten worden vóór publicatie gevalideerd tegen de SHACL-shapes van CPSV-AP, CPRMV en RONL; een fout blokkeert publicatie. Tijdens het opstellen is de controle een advies. | Kern | nog niet | De controle bestaat, maar blokkeert nooit. |
| AB-11 | Juridische interpretatie wordt vastgelegd in FLINT, gekoppeld aan de brontekst. De Norm Editor is IOU's gereedschap daarvoor. | Vervangbaar | deels | Twee van de zes onderdelen van de Norm Editor zijn nog niet gebouwd, en geen ander onderdeel leest FLINT al in. |
| AB-12 | Een Business API staat tussen elk portaal en de procesengine; de engine is nooit van buitenaf bereikbaar. | Kern | deels | De portalen lopen via de RONL Business API. De engine zelf is nog direct bereikbaar. |
| AB-13 | Processen en beslissingen draaien op een engine met de Camunda 7 REST-API; IOU kiest Operaton. | Vervangbaar | gerealiseerd | Camunda 7 Enterprise past; Camunda 8 vraagt een herbouw. |
| AB-14 | De organisatie reist mee met elke uitrol en elke zaak. Een beslismodel wordt één keer uitgerold en gedeeld; verschillen per organisatie staan in de beslistabel zelf. | Kern | gerealiseerd | |
| AB-15 | Gepubliceerde producten staan in een SPARQL 1.1-triplestore; IOU kiest TriplyDB. | Vervangbaar | gerealiseerd | **Onder herziening**: IOU overweegt Apache Jena Fuseki. |
| AB-16 | Backends accepteren tokens van één OIDC-uitgever, die de inlogvoorzieningen voor medewerkers en inwoners achter zich koppelt. IOU kiest Keycloak, dat vervangbaar is. | Kern | deels | De RONL Business API wel. De ontwerptools controleren nog geen tokens (zie AB-19). |
| AB-17 | De backend bepaalt per zaak wie iets mag, en weigert bij twijfel: alleen de eigen organisatie of de aanvrager zelf. | Kern | gerealiseerd | In de RONL Business API. |
| AB-18 | Handelingen vragen een betrouwbaarheidsniveau: `basis` om een beslissing te laten berekenen, `midden` om een proces te starten. | Kern | deels | De controle werkt. DigiD en eIDAS zijn voorbereid maar uitgeschakeld; eHerkenning is er nog niet. |
| AB-19 | Elke schrijfactie in elk onderdeel is geauthenticeerd, geautoriseerd en vastgelegd. Publiceren gebeurt namens een bevoegde organisatie. | Kern | deels | De RONL Business API wel. Linked Data Explorer, CPSV Editor en Norm Editor nog niet. |
| AB-20 | De ontwerptools zijn alleen voor medewerkers; inwoners en ondernemers komen alleen bij de portalen en de publieke site. | Kern | deels | Inwoners krijgen de ontwerptools niet aangeboden, maar die tools dwingen dat nog niet af (zie AB-19). |
| AB-21 | Publieke catalogi worden live uit de kennisgraaf gelezen, via een aparte publieke laag die alleen leest, zonder inloggen en met een limiet op het aantal verzoeken. | Kern | gerealiseerd | |
| AB-22 | Elk geauthenticeerd verzoek wordt vastgelegd in een aparte auditopslag. De bewaartermijn bepaalt u zelf. | Kern | deels | De vastlegging werkt; een bewaartermijn wordt nog nergens toegepast. |
| AB-23 | Documenten blijven in het documentmanagementsysteem van de organisatie; de zaak bevat alleen een verwijzing. | Eigen keuze | gerealiseerd | |
| AB-24 | Elk onderdeel beheert zijn eigen gegevens; geen onderdeel leest de database van een ander. | Kern | deels | De RONL Business API leest nog rechtstreeks uit de database van de Linked Data Explorer. |
| AB-25 | Gegevens blijven bij de bron: basisregistraties worden bevraagd, niet gekopieerd. | Kern | deels | De BRP wordt bevraagd via de Haal Centraal-API, maar nog tegen een testvoorziening. Andere registraties zijn nog niet gekoppeld. |
| AB-26 | Het verwerkingsregister (AVG artikel 30) wordt per proces bijgehouden in de Linked Data Explorer en gepubliceerd. | Vervangbaar | gerealiseerd | U mag uw register ook elders bijhouden. |
| AB-27 | Elk IOU-onderdeel bouwt reproduceerbaar: niets wat een build ophaalt is ongepind, elke release heeft een CycloneDX-SBOM, updates wachten een vaste periode af, en de ICTU-richtlijn voor afhankelijkheden wordt wekelijks gemeten. | Kern | deels | CPSV Editor, Linked Data Explorer en RONL Business API wel; CPRMV en de Norm Editor nog niet. |
| AB-28 | Elk onderdeel heeft zelfstandige releases met kalenderversies; wijzigingen bereiken acceptatie en productie alleen via een pull request. | Kern | deels | CPSV Editor, Linked Data Explorer en RONL Business API wel. CPRMV volgt de versie van zijn specificatie; de Norm Editor kent alleen een productiebranch. |
| AB-29 | Productie wordt geleverd via een standaard leverstraat met een kwaliteitspoort. | Kern | nog niet | Alle onderdelen leveren nu via het spoor voor snelle prototypes. |
| AB-30 | Een taalmodel-assistent is optioneel en de keuze van de organisatie. | Eigen keuze | nog niet | De RONL Business API start in productie niet zonder sleutel voor een gesloten taaldienst. |

## Afwijkingen vastleggen

Van een besluit in de laag **Kern** wijkt u niet af. Van een besluit in de laag
**Vervangbaar** mag u afwijken; leg elke afwijking in uw eigen PSA vast in deze
vorm:

| ID | Wijkt af van | Reden | Strijdig met principe | Kosten | Weg terug |
|---|---|---|---|---|---|
| AFW-01 | AB-13: Operaton | Bestaand contract en kennis bij het team voor Camunda 7 Enterprise. | AB-03: open source is de standaard. | Licentiekosten, afhankelijkheid van één leverancier, verbeteringen in Operaton komen niet vanzelf mee. | Beide volgen de Camunda 7 REST-API; overstappen vraagt opnieuw uitrollen, geen herbouw. |

Een afwijking op een besluit in de laag **Eigen keuze** bestaat niet: daar legt u
gewoon uw keuze vast, in het hoofdstuk waar die hoort.

## Risico's

Elk besluit dat IOU deels of nog niet heeft gerealiseerd, staat hieronder als
risico. Daarnaast staan er risico's die geen besluit raken maar wel voor elke
implementatie gelden. Neem over wat voor u geldt, en vul aan.

| ID | Risico | Raakt | Wat u ondertussen doet | Issue |
|---|---|---|---|---|
| R-01 | De procesengine is direct bereikbaar, buiten de controles van de Business API om. | AB-12 | Plaats de engine in uw eigen netwerk zo dat alleen de backends hem bereiken. | [ronl-business-api#415](https://github.com/sgort/ronl-business-api/issues/415) |
| R-02 | De ontwerptools accepteren schrijfacties zonder dat vaststaat wie ze doet. | AB-16, AB-19, AB-20 | Maak de ontwerptools alleen bereikbaar binnen uw netwerk, achter de inlogvoorziening van uw organisatie. | [linked-data-explorer#163](https://github.com/sgort/linked-data-explorer/issues/163), [ttl-editor#234](https://github.com/sgort/ttl-editor/issues/234), [editor#2](https://git.open-regels.nl/regels/editor/-/issues/2) |
| R-03 | Toegang voor inwoners en ondernemers werkt nog niet echt: DigiD en eIDAS staan uit, eHerkenning ontbreekt, de BRP is een testvoorziening. | AB-18, AB-25 | Beperk de ingebruikname tot fase 1. Plan de aansluiting op DigiD, eHerkenning en de BRP als eigen project vóór fase 2. | — |
| R-04 | Wat de CPSV Editor schrijft, wijkt af van CPRMV 0.4.2; CPRMV zelf is nog een werkversie. | AB-02, AB-06 | Valideer gepubliceerde regels tegen de CPRMV-shapes en houd de ontwikkeling van de specificatie bij. | — |
| R-05 | SHACL-validatie geeft alleen advies; een product met fouten kan worden gepubliceerd. | AB-10 | Spreek af dat niemand publiceert zolang de validatie fouten meldt. | — |
| R-06 | Een gepubliceerde dienstbeschrijving houdt geen geschiedenis bij: opnieuw publiceren overschrijft de vorige versie. Dat raakt de Archiefwet. | AB-09 | Archiveer elke gepubliceerde versie zelf, met datum, in uw archiefvoorziening. | — |
| R-07 | Niet elk onderdeel voldoet aan de bouw- en API-afspraken, en er is nog geen standaard leverstraat. | AB-04, AB-27, AB-28, AB-29 | Neem CPRMV en de Norm Editor op in uw eigen acceptatietest; neem geen release in productie zonder die test. | — |
| R-08 | De RONL Business API vraagt in productie een gesloten taaldienst. | AB-03, AB-30 | Beoordeel de taaldienst op AVG en verwerkersovereenkomst, of wacht tot hij optioneel is. | — |
| R-09 | Eén onderdeel leest rechtstreeks de database van een ander; wijzigingen aan die database kunnen het breken. | AB-24 | Neem beide onderdelen altijd samen op in uw acceptatietest. | — |
| R-10 | Er wordt geen bewaartermijn toegepast op auditgegevens. | AB-22 | Stel uw bewaartermijn vast en richt het opschonen zelf in. | — |
| R-11 | De juridische interpretatie wordt met de hand overgenomen in de dienstbeschrijving, en de Norm Editor is nog niet compleet. | AB-01, AB-11 | Leg vast wie de overname controleert, en hoe. | — |
| R-12 | De procesengine heeft nog geen eigen productie-instantie: acceptatie en productie delen één engine. Voor de engine en de database van de Linked Data Explorer is geen back-up ingericht. | — | Richt in uw eigen omgeving een aparte engine per omgeving in, met een productiedatabase, back-up en een geteste herstelprocedure. | [ronl-business-api#349](https://github.com/sgort/ronl-business-api/issues/349) |
| R-13 | Overstappen naar een andere triplestore of hosting vraagt aanpassingen in de code; niet alle adressen zijn instelbaar. | AB-15 | Reken bij een andere triplestore of hosting op ontwikkelwerk, en neem dat op in de planning. | — |
| R-14 | Op test en acceptatie breekt de keten: de bestaande voorzieningen waaraan IOU koppelt (bijvoorbeeld documentbeheer, ondertekening, identiteitsbeheer, financiën) hebben vaak alleen een productieomgeving. Acceptatie toetst dan een nabootsing, of raakt productiegegevens. | — | Laat beheerders en leveranciers een test- en acceptatieomgeving inrichten voor elke gekoppelde voorziening (route 3 in [hoofdstuk 7](07-integration-architecture.md)). Tot die er is: toets met nabootsingen, en leg vast dat de echte koppeling pas in productie voor het eerst wordt gebruikt. | — |
