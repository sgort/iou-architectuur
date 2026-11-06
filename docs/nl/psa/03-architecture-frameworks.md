---
title: "3. Architectuurkaders"
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

# 3. Architectuurkaders

## Wat dit hoofdstuk in uw PSA vastlegt

Welke kaders en standaarden voor uw IOU-implementatie gelden, hoe de keuzes van
IOU zich daartoe verhouden, en wat u zelf nog moet doen. Niet elk kader is voor
elke organisatie verplicht; dit hoofdstuk legt vast welke voor u gelden en waar u
afwijkt.

Een PSA laat zien hoe aan kaders wordt gewerkt. Het is geen bewijs van naleving.
IOU heeft voor geen van onderstaande kaders een formele toets of certificering;
die doet uw organisatie voor haar eigen implementatie.

## Wat IOU beslist

**Open standaarden voor alles wat gedeeld wordt** (AB-03), **open source als
standaard** (AB-04), **API's volgens de API Design Rules** (AB-05) en **gegevens
bij de bron** (AB-26). Hoe dat uitpakt per kader:

| Kader | Hoe IOU zich ertoe verhoudt | Wat u nog doet |
|---|---|---|
| **NORA** | De keuzes voor open standaarden, open source, gegevens bij de bron en één toegang via API's sluiten aan op de NORA-principes. IOU heeft die aansluiting niet per principe uitgewerkt. | Leg per relevant NORA-principe vast hoe uw implementatie eraan voldoet. |
| **GEMMA** (gemeenten) of de referentiearchitectuur van uw bestuurslaag | IOU is niet afgebeeld op de referentiecomponenten van GEMMA of een andere referentiearchitectuur. | Beeld de IOU-onderdelen af op de referentiecomponenten die u gebruikt. Hoofdstuk 5 geeft de onderdelen en hun rol. |
| **Common Ground** | IOU scheidt proces, regels en gegevens: regels staan in de kennisgraaf, processen in de engine, gegevens blijven bij de bron (AB-26) en elk onderdeel beheert zijn eigen gegevens (AB-25). Beide besluiten zijn nog niet volledig gerealiseerd. | Bepaal welke Common Ground-componenten u al heeft en hoe IOU ze gebruikt. |
| **BIO2** | IOU heeft geen afbeelding van zijn maatregelen op de BIO2. Wel zijn er besluiten die BIO2-maatregelen ondersteunen: autorisatie per zaak (AB-18), vastlegging van verzoeken (AB-23), reproduceerbaar bouwen (AB-28). | Maak een risicoanalyse en een BIO2-verantwoording voor uw implementatie. [Hoofdstuk 8](08-security-and-privacy.md) en [hoofdstuk 11](11-decisions-and-risks.md) geven de bekende gaten. |
| **AVG en UAVG** | IOU verwerkt persoonsgegevens in zaken. Het verwerkingsregister kan per proces worden bijgehouden en gepubliceerd (AB-27). | Bepaal grondslag, doelen en bewaartermijnen per verwerking, en maak de afweging of een DPIA nodig is. Zie [hoofdstuk 8](08-security-and-privacy.md). |
| **Wet digitale overheid** | Regelt onder meer de inlogmiddelen voor digitale dienstverlening. IOU vraagt een betrouwbaarheidsniveau per handeling (AB-19) en is voorbereid op DigiD en eIDAS, maar die staan nog uit. | Bepaal per dienst het vereiste betrouwbaarheidsniveau en de inlogmiddelen, vóór fase 2. |
| **Digitale toegankelijkheid** (EN 301 549 met WCAG 2.1) | Voor de publieke site van de RONL Business API zijn er geautomatiseerde toegankelijkheidstests op WCAG-niveau A en AA. Dat is geen volledige toets. De andere onderdelen zijn niet op toegankelijkheid getoetst. | Laat elke interface die u in gebruik neemt toetsen, en publiceer een toegankelijkheidsverklaring. |
| **Archiefwet** | Een gepubliceerde dienstbeschrijving houdt geen geschiedenis bij (AB-10, risico R-06). Voor auditgegevens wordt nog geen bewaartermijn toegepast (AB-23). | Stel bewaartermijnen vast en richt archivering in. Houd rekening met MDTO (zie hieronder). |
| **Forum Standaardisatie** | Zie de tabel hieronder. | Neem de verplichte standaarden op in uw inkoop en leg afwijkingen vast. |

### Standaarden en hun status bij Forum Standaardisatie

Gecontroleerd op 6 november 2026 op forumstandaardisatie.nl. "Pas toe of leg uit"
betekent dat de standaard bij inkoop en ontwikkeling verplicht is, tenzij u
uitlegt waarom niet.

| Standaard | Waar IOU hem gebruikt | Status |
|---|---|---|
| BWB (Juriconnect-standaard voor verwijzingen naar wetgeving) | Verwijzingen naar landelijke wetgeving in dienstbeschrijvingen en regels | Pas toe of leg uit |
| JCDR (Juriconnect Decentrale Regelgeving) | Verwijzingen naar decentrale regelgeving | Pas toe of leg uit |
| SKOS en NL-SBB | Begrippen in dienstbeschrijvingen | Pas toe of leg uit |
| DCAT-AP-NL | Beschrijving van datasets, als u die publiceert | Pas toe of leg uit |
| OpenAPI Specification en REST-API Design Rules | Beschrijving en ontwerp van de API's (AB-05) | Pas toe of leg uit |
| Authenticatie-standaarden (OpenID.NLGov en SAML) | Inloggen via de OIDC-uitgever; DigiD werkt met SAML | Pas toe of leg uit |
| NL GOV Assurance profile for OAuth 2.0 | Tokens tussen portalen en backend | Pas toe of leg uit |
| HTTPS en HSTS, TLS | Al het verkeer | Pas toe of leg uit |
| Digitoegankelijk (EN 301 549 met WCAG 2.1) | Interfaces voor medewerkers en inwoners | Pas toe of leg uit |
| ODF | Documenten die u aanbiedt om te bewerken | Pas toe of leg uit |
| MDTO (metagegevens voor duurzaam toegankelijke overheidsinformatie) | Archivering | Pas toe of leg uit, per 1 januari 2027 |
| NEN-ISO/IEC 27001 en 27002 | Basis van de BIO2 | Pas toe of leg uit |
| RDF, RDFS, OWL, SHACL | Kennisgraaf en validatie (AB-11) | Aanbevolen |
| CPSV-AP 3.2.0 | Dienstbeschrijvingen (AB-06) | Niet op de lijst; Europese standaard |
| CPRMV 0.4.2 | Regels en hun methoden (AB-07) | Niet op de lijst; eerste openbare werkversie |
| ELI | Verwijzingen naar wetgeving | Niet op de lijst; Europese standaard |
| BPMN 2.0, DMN 1.3 | Proces- en beslismodellen | Niet op de lijst; internationale standaarden |
| SPARQL | Bevragen van de kennisgraaf | Niet op de lijst |

IOU heeft niet per verplichte standaard vastgesteld of elk onderdeel er volledig
aan voldoet. De tabel zegt waar de standaard van toepassing is, niet dat hij overal
correct is toegepast.

## Wat u invult

- Welke kaders voor uw organisatie gelden, en welke referentiearchitectuur u
  gebruikt.
- Per verplichte standaard: of uw implementatie eraan voldoet, en zo niet, uw
  uitleg.
- Uw eigen architectuurprincipes, beveiligingsrichtlijnen en technologiekeuzes, en
  hoe IOU daarbinnen past.
- Wie de BIO2-verantwoording, de DPIA-afweging en de toegankelijkheidstoets doet,
  en wanneer.

## Verder lezen

- [Standaarden en naleving van de RONL Business API](../ronl-business-api/reference/standards-compliance.md)
- [Externe standaarden in de CPSV Editor](../cpsv-editor/reference/external-standards.md)
- [CPRMV-vocabulaire](../cprmv-api/reference/cprmv-vocabulary.md)
- [ICTU-richtlijn voor afhankelijkheden](../contributing/ictu-dependency-guideline.md)
