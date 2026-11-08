---
title: "8. Beveiliging en privacy"
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

# 8. Beveiliging en privacy

## Wat dit hoofdstuk in uw PSA vastlegt

Hoe toegang, autorisatie, vastlegging en gegevensbescherming zijn ingericht, welke
maatregelen IOU zelf meebrengt, en welke u treft. Dit hoofdstuk is de basis voor
uw risicoanalyse, uw BIO2-verantwoording en uw DPIA-afweging. Het is daar geen
vervanging van.

## Wat IOU beslist

**Inloggen en autorisatie**

- **Eén OIDC-uitgever voor alle backends** (AB-17). Medewerkers loggen in via de
  inlogvoorziening van uw organisatie, later inwoners via DigiD of eHerkenning,
  allemaal gekoppeld achter dezelfde uitgever. De backend controleert bij elk
  verzoek het token: handtekening, uitgever, bestemming en geldigheid. IOU kiest
  Keycloak als uitgever; dat is vervangbaar (AB-32).
- **Autorisatie per zaak, in de backend** (AB-18). Een medewerker ziet alleen zaken
  van de eigen organisatie, een inwoner alleen de eigen zaken. Het
  organisatielabel zet de server zelf; bij twijfel weigert hij. Het scherm is geen
  beveiligingsgrens.
- **Betrouwbaarheidsniveau per handeling** (AB-19). Een beslissing laten berekenen
  vraagt `basis`, een proces starten `midden`.
- **Elke schrijfactie geauthenticeerd, geautoriseerd en vastgelegd** (AB-20). De
  RONL Business API voldoet hieraan. De Linked Data Explorer, de CPSV Editor en de
  Norm Editor nog niet: wie hun backend kan bereiken, kan er schrijven
  (risico R-02).
- **De ontwerptools alleen voor medewerkers** (AB-21). Dat wordt pas afgedwongen
  als AB-20 is gerealiseerd. Tot dan schermt u ze zelf af.

**Afscherming**

- **De engine nooit van buitenaf bereikbaar** (AB-13). De portalen gaan via de
  RONL Business API, maar de engine zelf is nog van buitenaf bereikbaar, al vraagt wijzigen nu een login (risico R-01).
- **Een aparte publieke laag die alleen leest** (AB-22). Zonder inloggen, met een
  limiet op het aantal verzoeken. Waar de publieke site iets laat versturen, vraagt
  hij eerst een rekenkundige proef van de browser, tegen geautomatiseerd misbruik.
- **Beveiligingskoppen en een limiet op verzoeken** in de RONL Business API. CORS
  beperkt welke webpagina's een API mogen aanroepen, maar is geen toegangscontrole.

**Vastlegging en privacy**

- **Elk geauthenticeerd verzoek vastgelegd in een aparte auditopslag** (AB-23).
  Een bewaartermijn wordt nog niet toegepast (risico R-10).
- **Gegevens bij de bron** (AB-26): persoonsgegevens uit basisregistraties worden
  opgevraagd wanneer nodig, niet gekopieerd.
- **Verwerkingsregister per proces** (AB-27), openbaar zonder contactgegevens.
- **Een taalmodel-assistent is uw eigen keuze** (AB-31). De RONL Business API
  vraagt er nu in elke omgeving nog een sleutel voor (risico R-08). Gebruikt u hem,
  dan gaan gegevens naar een externe dienst; beoordeel dat op AVG en
  verwerkersovereenkomst.

**Bouwen en leveren**

- **Reproduceerbaar bouwen** (AB-28): alles wat een build ophaalt is vastgepind,
  elke release heeft een SBOM, en updates wachten een vaste periode af. Dat geldt
  voor de CPSV Editor, de Linked Data Explorer en de RONL Business API; nog niet
  voor CPRMV en de Norm Editor (risico R-07). IOU ondertekent zijn eigen releases
  niet; wel controleert het de handtekeningen van wat het binnenhaalt.

### Wat IOU niet regelt

- Geen meldpunt voor kwetsbaarheden: geen van de onderdelen heeft een
  `SECURITY.md` of `security.txt`.
- Geen penetratietest en geen dreigingsanalyse.
- Geen afbeelding op de BIO2 en geen DPIA.
- Geen sleutel- en geheimbeheer voor uw omgeving; dat hoort bij uw inrichting.

## Fasering

Gebaseerd op de faseringstabel van een compacte gemeentelijke PSA.

| Onderwerp | Fase 1: medewerkers | Nu voorbereiden | Fase 2: inwoners en ondernemers |
|---|---|---|---|
| Authenticatie | Inlogvoorziening van uw organisatie, achter de OIDC-uitgever | Uitgever los van de bedrijfslogica (AB-17, gerealiseerd voor de RONL Business API) | DigiD, eHerkenning, eventueel eIDAS |
| Autorisatie | Rollen en organisatie | Autorisatie per zaak in de backend (AB-18, gerealiseerd) | Alleen eigen zaken of zaken waarvoor een machtiging geldt |
| Netwerk | Interne toegang | Ontwerptools en engine afschermen (R-01, R-02) | Publieke toegang tot portalen en publieke site |
| Interface | Werkomgeving | Toegankelijkheid vanaf het begin | MijnOmgeving, getoetst op toegankelijkheid |
| Gegevens | Interne verwerking | Afscherming per zaak en identiteit | Inzage door de inwoner zelf |
| API's | Interne clients | Tokenvalidatie, autorisatie en limieten in de backend | Publieke client erbij |
| Vastlegging | Handelingen van medewerkers | Bewaartermijn vaststellen en toepassen (R-10) | Ook handelingen van inwoners, en misbruikdetectie |
| Privacy | Beoordeling van interne verwerking | DPIA-afweging vastleggen | Opnieuw beoordelen voor externe toegang |
| Toetsing | Risicoanalyse, BIO2-verantwoording | Dreigingsanalyse | Penetratietest en formele vrijgave vóór publieke ingebruikname |

## Wat u invult

- Uw risicoanalyse en BIO2-verantwoording, met de risico's uit
  [hoofdstuk 11](11-decisions-and-risks.md) als begin.
- De DPIA-afweging: is een DPIA nodig, en zo ja, wanneer.
- Hoe u de ontwerptools en de engine afschermt zolang IOU dat niet zelf doet.
- Het betrouwbaarheidsniveau per dienst in fase 2.
- Wie kwetsbaarheden meldt en oppakt, en hoe u IOU informeert.
- Sleutel- en geheimbeheer, inclusief het periodiek vervangen van sleutels en van
  de wachtwoorden van de accounts waarmee de backends de engine aanroepen.
- Of u een taalmodel-assistent gebruikt, en onder welke voorwaarden.

## Verder lezen

- [Authenticatie en toegangsbeheer](../ronl-business-api/features/authentication-iam.md)
- [Beveiliging en naleving van de RONL Business API](../ronl-business-api/features/security-compliance.md)
- [Standaarden en naleving](../ronl-business-api/reference/standards-compliance.md)
- [Due diligence van de CPSV Editor](../cpsv-editor/developer/due-diligence.md)
- [Vastpinnen van afhankelijkheden](../contributing/supply-chain.md) en
  [het scannen van afhankelijkheden](../contributing/dependency-scanning.md)
