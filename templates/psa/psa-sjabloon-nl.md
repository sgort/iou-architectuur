# Project Start Architectuur — [naam organisatie]

| | |
|---|---|
| Organisatie | […] |
| Versie | […] |
| Status | […] |
| Datum | […] |
| Auteur | […] |
| Vastgesteld door | […] |

Gebaseerd op de IOU PSA-gids, geverifieerd op 2026-11-06 tegen CPSV Editor 0412e9b, Linked Data Explorer 814c4bb, RONL Business API ff6c362, Norm Editor c47096b, CPRMV 8262d3e.

## Over dit sjabloon

Dit sjabloon bevat de besluiten die IOU al heeft genomen, per hoofdstuk. U vult alleen in wat uw organisatie zelf bepaalt: overal waar […] staat.

Besluiten in de laag **Kern** liggen vast. Van een besluit in de laag **Vervangbaar** mag u afwijken; leg dat vast in hoofdstuk 11 als afwijking (DEV-nn). Besluiten in de laag **Eigen keuze** vult u zelf in.

De status bij IOU geeft aan hoe ver IOU zelf is met een besluit, op de datum hierboven.

## 1. Managementsamenvatting

Toelichting in de gids: https://iou-architectuur.open-regels.nl/nl/psa/01-executive-summary/

IOU's eerste besluit, dat voor iedereen geldt: AB-01 — IOU neemt standaarden die nog in ontwikkeling zijn stap voor stap over, en geeft terug wat het daarbij leert. Een functie die een nieuwere versie nodig heeft, staat bewust uit tot die versie is uitgerold; de rest werkt door.

**Doel.** […]

**Aanleiding.** […]

**Belangrijkste architectuurkeuzes.** […]

**Fasering.** […]

## 2. Context en scope

Toelichting in de gids: https://iou-architectuur.open-regels.nl/nl/psa/02-context-and-scope/

### Besluiten van IOU

| ID | Besluit | Laag | Status bij IOU | Afwijken |
|---|---|---|---|---|
| AB-02 | Elke stap levert zijn product op in een open formaat; niets wordt overgetypt. | Kern | deels | niet open voor afwijking |
| AB-21 | De ontwerptools zijn alleen voor medewerkers; inwoners en ondernemers komen alleen bij de portalen en de publieke site. | Kern | deels | niet open voor afwijking |

### Wat IOU beslist (overgenomen uit de IOU PSA-gids)

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
[hoofdstuk 7](https://iou-architectuur.open-regels.nl/nl/psa/07-integration-architecture/)). IOU vervangt ook niet in één keer
bestaande zaaksystemen: u kiest per proces of het in IOU wordt uitgevoerd.

### Fasering

| | Fase 1: medewerkers | Nu voorbereiden | Fase 2: inwoners en ondernemers |
|---|---|---|---|
| Gebruikers | Medewerkers van de eigen organisatie | Rollen voor inwoner en gemachtigde bestaan al in de inlogvoorziening | Inwoners, gemachtigden en ondernemers |
| Processen | Interne behandeling, met of zonder aanvraag van buiten | Processen zo ontwerpen dat een aanvraag ook van een inwoner kan komen | Aanvragen via MijnOmgeving |
| Openbaarheid | Publieke site met regels en processen | Bepalen wat openbaar wordt | Ongewijzigd |

### Onze invulling

1. Welke processen u als eerste in IOU uitvoert, en waarom die.

   […]

2. Welke van de vijf stappen u gebruikt. Niet elke organisatie begint bij het interpreteren van wetgeving.

   […]

3. Welke gebruikersgroepen u in fase 1 toelaat, en wanneer fase 2 begint.

   […]

4. Welke bestaande systemen IOU raakt: zaaksystemen, documentbeheer, ondertekening, identiteitsbeheer, financiën, basisregistraties.

   […]

5. Waar IOU overlapt met wat u al heeft, en hoe u die overlap oplost.

   […]

## 3. Architectuurkaders

Toelichting in de gids: https://iou-architectuur.open-regels.nl/nl/psa/03-architecture-frameworks/

### Besluiten van IOU

| ID | Besluit | Laag | Status bij IOU | Afwijken |
|---|---|---|---|---|
| AB-03 | Gedeelde producten gebruiken CPSV-AP 3.2.0, CPRMV 0.4.2, BPMN 2.0, DMN 1.3, RDF/Turtle, SKOS/NL-SBB en ELI, BWB, CVDR en JuriConnect voor verwijzingen naar wetgeving. | Kern | deels | niet open voor afwijking |
| AB-04 | Open source is de standaard (EUPL-1.2). Een gesloten product kan alleen achter een vervangbare koppeling. | Kern | deels | niet open voor afwijking |
| AB-05 | API's volgen de API Design Rules en hebben een OpenAPI 3.1-beschrijving die automatisch wordt gecontroleerd. | Kern | deels | niet open voor afwijking |
| AB-06 | Publieke dienstverlening wordt beschreven en gepubliceerd met de CPSV Editor. | Kern | gerealiseerd | niet open voor afwijking |
| AB-07 | Regels worden vastgelegd in CPRMV: een regelset hoort bij een publieke dienst, verwijst naar de wet waarop hij berust, en heeft een geldigheidsperiode. | Kern | deels | niet open voor afwijking |
| AB-10 | Elke gepubliceerde dienst staat in één eigen graaf per organisatie en dienst, op een vast adres. | Kern | gerealiseerd | niet open voor afwijking |
| AB-11 | Gedeelde producten worden vóór publicatie gevalideerd tegen de SHACL-shapes van CPSV-AP, CPRMV en RONL; een fout blokkeert publicatie. Tijdens het opstellen is de controle een advies. | Kern | nog niet | niet open voor afwijking |
| AB-18 | De backend bepaalt per zaak wie iets mag, en weigert bij twijfel: alleen de eigen organisatie of de aanvrager zelf. | Kern | gerealiseerd | niet open voor afwijking |
| AB-19 | Handelingen vragen een betrouwbaarheidsniveau: `basis` om een beslissing te laten berekenen, `midden` om een proces te starten. | Kern | deels | niet open voor afwijking |
| AB-23 | Elk geauthenticeerd verzoek wordt vastgelegd in een aparte auditopslag. De bewaartermijn bepaalt u zelf. | Kern | deels | niet open voor afwijking |
| AB-25 | Elk onderdeel beheert zijn eigen gegevens; geen onderdeel leest de database van een ander. | Kern | deels | niet open voor afwijking |
| AB-26 | Gegevens blijven bij de bron: basisregistraties worden bevraagd, niet gekopieerd. | Kern | deels | niet open voor afwijking |
| AB-27 | Het verwerkingsregister (AVG artikel 30) wordt per proces bijgehouden in de Linked Data Explorer en gepubliceerd. | Vervangbaar | gerealiseerd | mag; zie hieronder |
| AB-28 | Elk IOU-onderdeel bouwt reproduceerbaar: niets wat een build ophaalt is ongepind, elke release heeft een CycloneDX-SBOM, updates wachten een vaste periode af, en de ICTU-richtlijn voor afhankelijkheden wordt wekelijks gemeten. | Kern | deels | niet open voor afwijking |

### Wat IOU beslist (overgenomen uit de IOU PSA-gids)

**Open standaarden voor alles wat gedeeld wordt** (AB-03), **open source als
standaard** (AB-04), **API's volgens de API Design Rules** (AB-05) en **gegevens
bij de bron** (AB-26). Hoe dat uitpakt per kader:

| Kader | Hoe IOU zich ertoe verhoudt | Wat u nog doet |
|---|---|---|
| **NORA** | De keuzes voor open standaarden, open source, gegevens bij de bron en één toegang via API's sluiten aan op de NORA-principes. IOU heeft die aansluiting niet per principe uitgewerkt. | Leg per relevant NORA-principe vast hoe uw implementatie eraan voldoet. |
| **GEMMA** (gemeenten) of de referentiearchitectuur van uw bestuurslaag | IOU is niet afgebeeld op de referentiecomponenten van GEMMA of een andere referentiearchitectuur. | Beeld de IOU-onderdelen af op de referentiecomponenten die u gebruikt. Hoofdstuk 5 geeft de onderdelen en hun rol. |
| **Common Ground** | IOU scheidt proces, regels en gegevens: regels staan in de kennisgraaf, processen in de engine, gegevens blijven bij de bron (AB-26) en elk onderdeel beheert zijn eigen gegevens (AB-25). Beide besluiten zijn nog niet volledig gerealiseerd. | Bepaal welke Common Ground-componenten u al heeft en hoe IOU ze gebruikt. |
| **BIO2** | IOU heeft geen afbeelding van zijn maatregelen op de BIO2. Wel zijn er besluiten die BIO2-maatregelen ondersteunen: autorisatie per zaak (AB-18), vastlegging van verzoeken (AB-23), reproduceerbaar bouwen (AB-28). | Maak een risicoanalyse en een BIO2-verantwoording voor uw implementatie. [Hoofdstuk 8](https://iou-architectuur.open-regels.nl/nl/psa/08-security-and-privacy/) en [hoofdstuk 11](https://iou-architectuur.open-regels.nl/nl/psa/11-decisions-and-risks/) geven de bekende gaten. |
| **AVG en UAVG** | IOU verwerkt persoonsgegevens in zaken. Het verwerkingsregister kan per proces worden bijgehouden en gepubliceerd (AB-27). | Bepaal grondslag, doelen en bewaartermijnen per verwerking, en maak de afweging of een DPIA nodig is. Zie [hoofdstuk 8](https://iou-architectuur.open-regels.nl/nl/psa/08-security-and-privacy/). |
| **Wet digitale overheid** | Regelt onder meer de inlogmiddelen voor digitale dienstverlening. IOU vraagt een betrouwbaarheidsniveau per handeling (AB-19) en is voorbereid op DigiD en eIDAS, maar die staan nog uit. | Bepaal per dienst het vereiste betrouwbaarheidsniveau en de inlogmiddelen, vóór fase 2. |
| **Digitale toegankelijkheid** (EN 301 549 met WCAG 2.1) | Voor de publieke site van de RONL Business API zijn er geautomatiseerde toegankelijkheidstests op WCAG-niveau A en AA. Dat is geen volledige toets. De andere onderdelen zijn niet op toegankelijkheid getoetst. | Laat elke interface die u in gebruik neemt toetsen, en publiceer een toegankelijkheidsverklaring. |
| **Archiefwet** | Een gepubliceerde dienstbeschrijving houdt geen geschiedenis bij (AB-10, risico R-06). Voor auditgegevens wordt nog geen bewaartermijn toegepast (AB-23). | Stel bewaartermijnen vast en richt archivering in. Houd rekening met MDTO (zie hieronder). |
| **Forum Standaardisatie** | Zie de tabel hieronder. | Neem de verplichte standaarden op in uw inkoop en leg afwijkingen vast. |

#### Standaarden en hun status bij Forum Standaardisatie

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
| BPMN 2.0, DMN 1.3 | Proces- en beslismodellen | Niet op de lijst; internationale standaarden. Voor DMN stelt IOU een Nederlands toepassingsprofiel voor: [DMN-AP NL](https://github.com/sgort/ttl-editor/blob/main/docs/dmn-ap-nl-voorstel.md) |
| SPARQL | Bevragen van de kennisgraaf | Niet op de lijst |

IOU heeft niet per verplichte standaard vastgesteld of elk onderdeel er volledig
aan voldoet. De tabel zegt waar de standaard van toepassing is, niet dat hij overal
correct is toegepast.

### Onze invulling

1. Welke kaders voor uw organisatie gelden, en welke referentiearchitectuur u gebruikt.

   […]

2. Per verplichte standaard: of uw implementatie eraan voldoet, en zo niet, uw uitleg.

   […]

3. Uw eigen architectuurprincipes, beveiligingsrichtlijnen en technologiekeuzes, en hoe IOU daarbinnen past.

   […]

4. Wie de BIO2-verantwoording, de DPIA-afweging en de toegankelijkheidstoets doet, en wanneer.

   […]

Volgen wij IOU's keuze voor AB-27? [ja / nee — zie afwijking DEV-…]

## 4. Functionele architectuur

Toelichting in de gids: https://iou-architectuur.open-regels.nl/nl/psa/04-functional-architecture/

### Besluiten van IOU

| ID | Besluit | Laag | Status bij IOU | Afwijken |
|---|---|---|---|---|
| AB-06 | Publieke dienstverlening wordt beschreven en gepubliceerd met de CPSV Editor. | Kern | gerealiseerd | niet open voor afwijking |
| AB-07 | Regels worden vastgelegd in CPRMV: een regelset hoort bij een publieke dienst, verwijst naar de wet waarop hij berust, en heeft een geldigheidsperiode. | Kern | deels | niet open voor afwijking |
| AB-08 | Processen worden ontworpen in de Linked Data Explorer en alleen via zijn backend uitgerold, als één bundel van proces, formulieren en documentsjablonen. | Kern | deels | niet open voor afwijking |
| AB-12 | Juridische interpretatie wordt vastgelegd in FLINT, gekoppeld aan de brontekst. De Norm Editor is IOU's gereedschap daarvoor. | Vervangbaar | deels | mag; zie hieronder |
| AB-15 | De organisatie reist mee met elke uitrol en elke zaak. Een beslismodel wordt één keer uitgerold en gedeeld; verschillen per organisatie staan in de beslistabel zelf. | Kern | gerealiseerd | niet open voor afwijking |
| AB-19 | Handelingen vragen een betrouwbaarheidsniveau: `basis` om een beslissing te laten berekenen, `midden` om een proces te starten. | Kern | deels | niet open voor afwijking |
| AB-20 | Elke schrijfactie in elk onderdeel is geauthenticeerd, geautoriseerd en vastgelegd. Publiceren gebeurt namens een bevoegde organisatie. | Kern | deels | niet open voor afwijking |

### Wat IOU beslist (overgenomen uit de IOU PSA-gids)

**Elke stap heeft één gereedschap, en de producten zijn gedeeld.** Diensten worden
beschreven met de CPSV Editor (AB-06), regels in CPRMV (AB-07), processen ontworpen
in de Linked Data Explorer (AB-08). Juridische interpretatie gebeurt in FLINT met
de Norm Editor; dat gereedschap is vervangbaar (AB-12).

**De organisatie reist mee met alles wat wordt uitgerold** (AB-15). Een beslismodel
wordt één keer uitgerold en door meerdere organisaties gebruikt; verschillen per
organisatie staan in de beslistabel zelf. Een proces en een zaak horen altijd bij
één organisatie.

#### Hoofdfuncties

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

#### Rollen

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

### Fasering

| | Fase 1: medewerkers | Nu voorbereiden | Fase 2: inwoners en ondernemers |
|---|---|---|---|
| Rollen | Behandelaar, beheerder, procesrollen | De rollen inwoner en gemachtigde bestaan al; ontwerp processen zo dat ze die kunnen gebruiken | Inwoner en gemachtigde actief |
| Processen | Gestart door een medewerker | Bepaal per proces of een inwoner het later zelf mag starten | Gestart door inwoner of gemachtigde |
| Beslissingen | Berekend voor de behandelaar | Beslissingen die een inwoner vooraf mag laten berekenen, vragen alleen niveau `basis` (AB-19) | Inwoner laat zelf berekenen |

### Onze invulling

1. Welke hoofdfuncties u in fase 1 gebruikt.

   […]

2. Welke processen u ondersteunt, en welke procesrollen daarbij horen.

   […]

3. Hoe de rollen aansluiten op uw organisatie: wie mag behandelen, wie beheert, wie publiceert, wie mag uitrollen.

   […]

4. Wie eigenaar is van elk gedeeld product: welke afdeling beschrijft een dienst, welke stelt regels vast, welke ontwerpt het proces.

   […]

Volgen wij IOU's keuze voor AB-12? [ja / nee — zie afwijking DEV-…]

## 5. Applicatiearchitectuur

Toelichting in de gids: https://iou-architectuur.open-regels.nl/nl/psa/05-application-architecture/

### Besluiten van IOU

| ID | Besluit | Laag | Status bij IOU | Afwijken |
|---|---|---|---|---|
| AB-13 | Een Business API staat tussen elk portaal en de procesengine; de engine is nooit van buitenaf bereikbaar. | Kern | deels | niet open voor afwijking |
| AB-14 | Processen en beslissingen draaien op een engine met de Camunda 7 REST-API; IOU kiest Operaton. | Vervangbaar | gerealiseerd | mag; zie hieronder |
| AB-16 | Gepubliceerde producten staan in een SPARQL 1.1-triplestore; IOU kiest TriplyDB. | Vervangbaar | gerealiseerd | mag; zie hieronder |
| AB-17 | Backends accepteren tokens van één OIDC-uitgever, die de inlogvoorzieningen voor medewerkers en inwoners achter zich koppelt. Welk product de uitgever is, staat in AB-32. | Kern | deels | niet open voor afwijking |
| AB-18 | De backend bepaalt per zaak wie iets mag, en weigert bij twijfel: alleen de eigen organisatie of de aanvrager zelf. | Kern | gerealiseerd | niet open voor afwijking |
| AB-20 | Elke schrijfactie in elk onderdeel is geauthenticeerd, geautoriseerd en vastgelegd. Publiceren gebeurt namens een bevoegde organisatie. | Kern | deels | niet open voor afwijking |
| AB-21 | De ontwerptools zijn alleen voor medewerkers; inwoners en ondernemers komen alleen bij de portalen en de publieke site. | Kern | deels | niet open voor afwijking |
| AB-22 | Publieke catalogi worden live uit de kennisgraaf gelezen, via een aparte publieke laag die alleen leest, zonder inloggen en met een limiet op het aantal verzoeken. | Kern | gerealiseerd | niet open voor afwijking |
| AB-25 | Elk onderdeel beheert zijn eigen gegevens; geen onderdeel leest de database van een ander. | Kern | deels | niet open voor afwijking |
| AB-32 | IOU kiest Keycloak als OIDC-uitgever. | Vervangbaar | gerealiseerd | mag; zie hieronder |

### Wat IOU beslist (overgenomen uit de IOU PSA-gids)

**Eén API-laag tussen alle portalen en de procesengine** (AB-13). De werkomgeving,
MijnOmgeving en de publieke site praten alleen met de RONL Business API. Die
controleert wie iets mag, legt het vast, en praat met de engine. De engine zelf is
nog direct bereikbaar (risico R-01).

**De engine spreekt de Camunda 7 REST-API** (AB-14). IOU kiest Operaton. Een andere
engine met dezelfde API kan; een engine met een andere API (zoals Camunda 8)
betekent herbouw.

**Gedeelde producten staan in een SPARQL-triplestore** (AB-16). IOU kiest TriplyDB;
dat besluit is onder herziening.

**Eén OIDC-uitgever voor alle backends** (AB-17). IOU kiest Keycloak (AB-32, vervangbaar), dat de
inlogvoorziening van uw organisatie en later DigiD en eHerkenning achter zich
koppelt.

**Een aparte publieke laag die alleen leest** (AB-22), en **elk onderdeel beheert
zijn eigen gegevens** (AB-25).

#### Het landschap

Elk onderdeel staat bij de stap waar het hoort. Tussen haakjes staat de laag.


#### De onderdelen

| Onderdeel | Rol | Bestaat uit | Laag |
|---|---|---|---|
| Norm Editor | Juridische interpretatie in FLINT | Webinterface, backend, drie diensten voor tekst- en taalanalyse | Vervangbaar |
| CPSV Editor | Diensten en regels beschrijven en publiceren | Webinterface; gebruikt de backend van de Linked Data Explorer voor validatie en publicatie | Kern |
| CPRMV API | Wettekst en regels ophalen uit officiële bronnen | Eén API-dienst, zonder eigen opslag | Kern |
| Linked Data Explorer | Beslissingen en processen ontwerpen en uitrollen; verwerkingsregister | Webinterface, backend met eigen database, publieke site voor het verwerkingsregister | Kern |
| RONL Business API | Zaken uitvoeren; portalen voor medewerkers en inwoners; publieke site | Backend met auditopslag; webinterfaces voor werkomgeving en MijnOmgeving; publieke site | Kern |
| Procesengine | Processen en beslissingen uitvoeren | Operaton | Vervangbaar |
| Kennisgraaf | Gedeelde producten opslaan en bevraagbaar maken | TriplyDB | Vervangbaar |
| OIDC-uitgever | Inloggen, rollen, koppeling met andere inlogvoorzieningen | Keycloak | Vervangbaar |

#### Hoe ze communiceren

| Van | Naar | Waarvoor | Hoe |
|---|---|---|---|
| Webinterfaces | Hun eigen backend | Alle functies | HTTPS; de browser praat niet zelf met engine of kennisgraaf |
| CPSV Editor | Kennisgraaf | Publiceren | HTTPS, via de API van TriplyDB en de backend van de Linked Data Explorer |
| Norm Editor | Kennisgraaf | Interpretaties opslaan | HTTPS, via de API van TriplyDB |
| Linked Data Explorer | Kennisgraaf | Beslismodellen vinden, regels afnemen | SPARQL 1.1 |
| Linked Data Explorer | Procesengine | Procesbundels uitrollen; taken die het systeem zelf uitvoert | Camunda 7 REST-API |
| RONL Business API | Procesengine | Zaken starten, taken afhandelen, beslissingen berekenen | Camunda 7 REST-API |
| RONL Business API | Kennisgraaf | Regelcatalogus, procesbibliotheek | SPARQL 1.1, live gelezen |
| RONL Business API | Linked Data Explorer | Gepubliceerde procesbundels | REST; daarnaast nog rechtstreeks uit de database (AB-25, risico R-09) |
| RONL Business API | CPRMV API | Wettekst voor de assistent | Staat bewust uit zolang de uitgerolde versie van de CPRMV API de benodigde functie nog niet levert |
| Portalen | RONL Business API | Inloggen en handelingen | OIDC-tokens van de uitgever, gecontroleerd door de backend |

Een koppeling met een onderdeel dat nog in ontwikkeling is, gaat pas aan als de
uitgerolde versie levert wat de koppeling nodig heeft. Tot dan staat ze uit, en
werkt de rest gewoon door. Zo kan IOU een standaard stap voor stap overnemen
(zie [Over deze PSA](https://iou-architectuur.open-regels.nl/nl/psa/#hoe-iou-zich-ontwikkelt)).

De ontwerptools gebruiken nog geen tokens (AB-20, risico R-02). Waar de
webinterfaces van de Linked Data Explorer, de CPSV Editor en de Norm Editor met hun
backend praten, controleert die backend dus nog niet wie de gebruiker is.

### Fasering

| | Fase 1: medewerkers | Nu voorbereiden | Fase 2: inwoners en ondernemers |
|---|---|---|---|
| Portalen | Werkomgeving | MijnOmgeving bestaat al als onderdeel van de RONL Business API | MijnOmgeving open voor inwoners |
| API-laag | Interne clients | Alle autorisatie in de backend, niet in het scherm (AB-18) | Publieke clients als extra gebruiker van dezelfde API |
| Ontwerptools | Alleen medewerkers | Afschermen achter uw inlogvoorziening | Blijven alleen voor medewerkers (AB-21) |

### Onze invulling

1. Welke onderdelen u installeert, en welke u gedeeld afneemt.

   […]

2. Of u een vervangbaar onderdeel vervangt; zo ja, een afwijking in hoofdstuk 11.

   […]

3. Hoe u de IOU-onderdelen afbeeldt op uw referentiearchitectuur.

   […]

4. Welke van uw eigen systemen aan welke onderdelen koppelen (zie [hoofdstuk 7](https://iou-architectuur.open-regels.nl/nl/psa/07-integration-architecture/)).

   […]

Volgen wij IOU's keuze voor AB-14? [ja / nee — zie afwijking DEV-…]

Volgen wij IOU's keuze voor AB-16? [ja / nee — zie afwijking DEV-…]

Volgen wij IOU's keuze voor AB-32? [ja / nee — zie afwijking DEV-…]

## 6. Gegevensarchitectuur

Toelichting in de gids: https://iou-architectuur.open-regels.nl/nl/psa/06-data-architecture/

### Besluiten van IOU

| ID | Besluit | Laag | Status bij IOU | Afwijken |
|---|---|---|---|---|
| AB-10 | Elke gepubliceerde dienst staat in één eigen graaf per organisatie en dienst, op een vast adres. | Kern | gerealiseerd | niet open voor afwijking |
| AB-15 | De organisatie reist mee met elke uitrol en elke zaak. Een beslismodel wordt één keer uitgerold en gedeeld; verschillen per organisatie staan in de beslistabel zelf. | Kern | gerealiseerd | niet open voor afwijking |
| AB-18 | De backend bepaalt per zaak wie iets mag, en weigert bij twijfel: alleen de eigen organisatie of de aanvrager zelf. | Kern | gerealiseerd | niet open voor afwijking |
| AB-23 | Elk geauthenticeerd verzoek wordt vastgelegd in een aparte auditopslag. De bewaartermijn bepaalt u zelf. | Kern | deels | niet open voor afwijking |
| AB-24 | Documenten blijven in het documentmanagementsysteem van de organisatie; de zaak bevat alleen een verwijzing. | Eigen keuze | gerealiseerd | uw eigen keuze |
| AB-25 | Elk onderdeel beheert zijn eigen gegevens; geen onderdeel leest de database van een ander. | Kern | deels | niet open voor afwijking |
| AB-26 | Gegevens blijven bij de bron: basisregistraties worden bevraagd, niet gekopieerd. | Kern | deels | niet open voor afwijking |
| AB-27 | Het verwerkingsregister (AVG artikel 30) wordt per proces bijgehouden in de Linked Data Explorer en gepubliceerd. | Vervangbaar | gerealiseerd | mag; zie hieronder |

### Wat IOU beslist (overgenomen uit de IOU PSA-gids)

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

#### Gegevensobjecten

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
[hoofdstuk 8](https://iou-architectuur.open-regels.nl/nl/psa/08-security-and-privacy/)).

### Fasering

| | Fase 1: medewerkers | Nu voorbereiden | Fase 2: inwoners en ondernemers |
|---|---|---|---|
| Zaakgegevens | Zaken van de eigen organisatie | Autorisatie per zaak werkt al in de backend (AB-18) | Inwoners zien alleen hun eigen zaken |
| Persoonsgegevens | Verwerking door medewerkers | Grondslag, doel en bewaartermijn per verwerking vastleggen | Inzage door de inwoner zelf; opnieuw beoordelen |
| Auditgegevens | Handelingen van medewerkers | Bewaartermijn vaststellen en toepassen | Ook handelingen van inwoners |

### Onze invulling

1. Welke gegevens u in IOU verwerkt, met grondslag en doel per verwerking.

   […]

2. Bewaartermijnen per gegevensobject, afgeleid van uw selectielijst, en wie het opschonen uitvoert.

   […]

3. Hoe u eerdere versies van gepubliceerde dienstbeschrijvingen archiveert, zolang IOU dat niet doet.

   […]

4. Welk documentmanagementsysteem u koppelt, en waar uw verwerkingsregister staat.

   […]

5. Hoe u gegevens overdraagt als u stopt met IOU: de gedeelde producten staan in open formaten in de kennisgraaf; zaakgegevens moet u uit de procesengine halen.

   […]

Volgen wij IOU's keuze voor AB-27? [ja / nee — zie afwijking DEV-…]

## 7. Integratiearchitectuur

Toelichting in de gids: https://iou-architectuur.open-regels.nl/nl/psa/07-integration-architecture/

### Besluiten van IOU

| ID | Besluit | Laag | Status bij IOU | Afwijken |
|---|---|---|---|---|
| AB-05 | API's volgen de API Design Rules en hebben een OpenAPI 3.1-beschrijving die automatisch wordt gecontroleerd. | Kern | deels | niet open voor afwijking |
| AB-09 | Beslismodellen worden gevonden met standaard SPARQL; regels worden afgenomen via de versie-2-API voor normen, met een vaste stabiliteitsbelofte. | Kern | gerealiseerd | niet open voor afwijking |
| AB-13 | Een Business API staat tussen elk portaal en de procesengine; de engine is nooit van buitenaf bereikbaar. | Kern | deels | niet open voor afwijking |
| AB-17 | Backends accepteren tokens van één OIDC-uitgever, die de inlogvoorzieningen voor medewerkers en inwoners achter zich koppelt. Welk product de uitgever is, staat in AB-32. | Kern | deels | niet open voor afwijking |
| AB-22 | Publieke catalogi worden live uit de kennisgraaf gelezen, via een aparte publieke laag die alleen leest, zonder inloggen en met een limiet op het aantal verzoeken. | Kern | gerealiseerd | niet open voor afwijking |
| AB-24 | Documenten blijven in het documentmanagementsysteem van de organisatie; de zaak bevat alleen een verwijzing. | Eigen keuze | gerealiseerd | uw eigen keuze |
| AB-25 | Elk onderdeel beheert zijn eigen gegevens; geen onderdeel leest de database van een ander. | Kern | deels | niet open voor afwijking |
| AB-26 | Gegevens blijven bij de bron: basisregistraties worden bevraagd, niet gekopieerd. | Kern | deels | niet open voor afwijking |

### Wat IOU beslist (overgenomen uit de IOU PSA-gids)

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

#### API's van IOU

| API | Aangeboden door | Voor wie | Toegang |
|---|---|---|---|
| Zaken, taken, beslissingen, formulieren, documenten | RONL Business API | Werkomgeving en MijnOmgeving | Token van de OIDC-uitgever, met rol en organisatie |
| Publieke catalogi | RONL Business API | Iedereen | Zonder inloggen, alleen lezen, met een limiet op het aantal verzoeken (AB-22) |
| Normen, beslismodellen, procesbundels | Linked Data Explorer | Andere IOU-onderdelen, andere organisaties | Lezen openbaar; schrijven nog zonder controle (R-02) |
| Wettekst en verwijzingen | CPRMV API | Iedereen die wettekst nodig heeft | Openbaar |
| SPARQL | Kennisgraaf | IOU-onderdelen, andere organisaties | Lezen volgens de instelling van de dataset; schrijven met een token |

#### Koppelingen met uw voorzieningen

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

#### Test en acceptatie van koppelingen

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

### Fasering

| | Fase 1: medewerkers | Nu voorbereiden | Fase 2: inwoners en ondernemers |
|---|---|---|---|
| API's | Gebruikt door de werkomgeving | Tokenvalidatie, autorisatie per zaak en een limiet op verzoeken zitten al in de backend | MijnOmgeving als extra client van dezelfde API |
| Inlogmiddelen | Inlogvoorziening van uw organisatie | Aansluiting op DigiD en eHerkenning plannen | DigiD, eHerkenning, eventueel eIDAS |
| Koppelingen | Met nabootsing of echte voorziening, per route | Route 3 aanvragen bij beheerders en leveranciers | Echte voorzieningen, getoetst op acceptatie |

### Onze invulling

1. Welke voorzieningen u aan IOU koppelt, en welke route u per koppeling kiest. Kiest u niet voor route 3, leg dan uit waarom.

   […]

2. Welke systemen namens zichzelf aanroepen, en hoe ze zich bekendmaken.

   […]

3. Of u Digikoppeling nodig hebt voor de aansluiting op basisregistraties of andere overheidsorganisaties. IOU gebruikt het zelf niet.

   […]

4. Welke API's u openstelt voor andere organisaties.

   […]

## 8. Beveiliging en privacy

Toelichting in de gids: https://iou-architectuur.open-regels.nl/nl/psa/08-security-and-privacy/

### Besluiten van IOU

| ID | Besluit | Laag | Status bij IOU | Afwijken |
|---|---|---|---|---|
| AB-13 | Een Business API staat tussen elk portaal en de procesengine; de engine is nooit van buitenaf bereikbaar. | Kern | deels | niet open voor afwijking |
| AB-17 | Backends accepteren tokens van één OIDC-uitgever, die de inlogvoorzieningen voor medewerkers en inwoners achter zich koppelt. Welk product de uitgever is, staat in AB-32. | Kern | deels | niet open voor afwijking |
| AB-18 | De backend bepaalt per zaak wie iets mag, en weigert bij twijfel: alleen de eigen organisatie of de aanvrager zelf. | Kern | gerealiseerd | niet open voor afwijking |
| AB-19 | Handelingen vragen een betrouwbaarheidsniveau: `basis` om een beslissing te laten berekenen, `midden` om een proces te starten. | Kern | deels | niet open voor afwijking |
| AB-20 | Elke schrijfactie in elk onderdeel is geauthenticeerd, geautoriseerd en vastgelegd. Publiceren gebeurt namens een bevoegde organisatie. | Kern | deels | niet open voor afwijking |
| AB-21 | De ontwerptools zijn alleen voor medewerkers; inwoners en ondernemers komen alleen bij de portalen en de publieke site. | Kern | deels | niet open voor afwijking |
| AB-22 | Publieke catalogi worden live uit de kennisgraaf gelezen, via een aparte publieke laag die alleen leest, zonder inloggen en met een limiet op het aantal verzoeken. | Kern | gerealiseerd | niet open voor afwijking |
| AB-23 | Elk geauthenticeerd verzoek wordt vastgelegd in een aparte auditopslag. De bewaartermijn bepaalt u zelf. | Kern | deels | niet open voor afwijking |
| AB-26 | Gegevens blijven bij de bron: basisregistraties worden bevraagd, niet gekopieerd. | Kern | deels | niet open voor afwijking |
| AB-27 | Het verwerkingsregister (AVG artikel 30) wordt per proces bijgehouden in de Linked Data Explorer en gepubliceerd. | Vervangbaar | gerealiseerd | mag; zie hieronder |
| AB-28 | Elk IOU-onderdeel bouwt reproduceerbaar: niets wat een build ophaalt is ongepind, elke release heeft een CycloneDX-SBOM, updates wachten een vaste periode af, en de ICTU-richtlijn voor afhankelijkheden wordt wekelijks gemeten. | Kern | deels | niet open voor afwijking |
| AB-31 | Een taalmodel-assistent is optioneel en de keuze van de organisatie. | Eigen keuze | nog niet | uw eigen keuze |
| AB-32 | IOU kiest Keycloak als OIDC-uitgever. | Vervangbaar | gerealiseerd | mag; zie hieronder |

### Wat IOU beslist (overgenomen uit de IOU PSA-gids)

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
  RONL Business API, maar de engine zelf is nog direct bereikbaar (risico R-01).
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
  vraagt er nu in productie nog een sleutel voor (risico R-08). Gebruikt u hem,
  dan gaan gegevens naar een externe dienst; beoordeel dat op AVG en
  verwerkersovereenkomst.

**Bouwen en leveren**

- **Reproduceerbaar bouwen** (AB-28): alles wat een build ophaalt is vastgepind,
  elke release heeft een SBOM, en updates wachten een vaste periode af. Dat geldt
  voor de CPSV Editor, de Linked Data Explorer en de RONL Business API; nog niet
  voor CPRMV en de Norm Editor (risico R-07). IOU ondertekent zijn eigen releases
  niet; wel controleert het de handtekeningen van wat het binnenhaalt.

#### Wat IOU niet regelt

- Geen meldpunt voor kwetsbaarheden: geen van de onderdelen heeft een
  `SECURITY.md` of `security.txt`.
- Geen penetratietest en geen dreigingsanalyse.
- Geen afbeelding op de BIO2 en geen DPIA.
- Geen sleutel- en geheimbeheer voor uw omgeving; dat hoort bij uw inrichting.

### Fasering

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

### Onze invulling

1. Uw risicoanalyse en BIO2-verantwoording, met de risico's uit [hoofdstuk 11](https://iou-architectuur.open-regels.nl/nl/psa/11-decisions-and-risks/) als begin.

   […]

2. De DPIA-afweging: is een DPIA nodig, en zo ja, wanneer.

   […]

3. Hoe u de ontwerptools en de engine afschermt zolang IOU dat niet zelf doet.

   […]

4. Het betrouwbaarheidsniveau per dienst in fase 2.

   […]

5. Wie kwetsbaarheden meldt en oppakt, en hoe u IOU informeert.

   […]

6. Sleutel- en geheimbeheer, inclusief het periodiek vervangen van sleutels.

   […]

7. Of u een taalmodel-assistent gebruikt, en onder welke voorwaarden.

   […]

Volgen wij IOU's keuze voor AB-27? [ja / nee — zie afwijking DEV-…]

Volgen wij IOU's keuze voor AB-32? [ja / nee — zie afwijking DEV-…]

## 9. Technische infrastructuur

Toelichting in de gids: https://iou-architectuur.open-regels.nl/nl/psa/09-technical-infrastructure/

### Besluiten van IOU

| ID | Besluit | Laag | Status bij IOU | Afwijken |
|---|---|---|---|---|
| AB-13 | Een Business API staat tussen elk portaal en de procesengine; de engine is nooit van buitenaf bereikbaar. | Kern | deels | niet open voor afwijking |
| AB-14 | Processen en beslissingen draaien op een engine met de Camunda 7 REST-API; IOU kiest Operaton. | Vervangbaar | gerealiseerd | mag; zie hieronder |
| AB-16 | Gepubliceerde producten staan in een SPARQL 1.1-triplestore; IOU kiest TriplyDB. | Vervangbaar | gerealiseerd | mag; zie hieronder |
| AB-25 | Elk onderdeel beheert zijn eigen gegevens; geen onderdeel leest de database van een ander. | Kern | deels | niet open voor afwijking |

### Wat IOU beslist (overgenomen uit de IOU PSA-gids)

IOU beslist over de onderdelen, niet over waar ze draaien. Drie besluiten raken
de infrastructuur wel:

- **De engine is nooit van buitenaf bereikbaar** (AB-13). Uw netwerkontwerp moet
  dat afdwingen: alleen de backends bereiken de engine (risico R-01).
- **Een engine met de Camunda 7 REST-API** (AB-14) en **een SPARQL
  1.1-triplestore** (AB-16). Welke u kiest en waar die draait, is aan u.
- **Elk onderdeel heeft zijn eigen database** (AB-25).

#### De referentie-inrichting

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

#### Omgevingen (OTAP)

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

De laatste regel is het probleem uit [hoofdstuk 7](https://iou-architectuur.open-regels.nl/nl/psa/07-integration-architecture/#test-en-acceptatie-van-koppelingen):
uw bestaande voorzieningen hebben vaak alleen productie, dus op test en
acceptatie breekt de keten (risico R-14). **IOU raadt aan dat beheerders en
leveranciers voor elke gekoppelde voorziening een test- en acceptatieomgeving
inrichten** (route 3).

#### Back-up en herstel

Azure Database for PostgreSQL maakt automatisch back-ups. Voor de virtuele machine
met de engine en Keycloak beschrijft de referentie een back-upprocedure, maar die
is niet als vaste taak ingericht. Voor de engine en de database van de Linked Data
Explorer is geen herstel getest (risico R-12).

### Fasering

| | Fase 1: medewerkers | Nu voorbereiden | Fase 2: inwoners en ondernemers |
|---|---|---|---|
| Netwerk | Alles binnen uw netwerk | Scheiding tussen portalen, API-laag, engine, databases en interne systemen | Portalen en publieke site bereikbaar vanaf internet |
| Beschikbaarheid | Afgestemd op werktijden | Monitoring en herstel inrichten | Ruimere beschikbaarheid; schaalbaarheid toetsen |
| Bescherming | Interne afscherming | Bepalen waar een WAF en DDoS-bescherming komen | WAF en DDoS-bescherming actief |

### Onze invulling

1. Waar u elk onderdeel draait: eigen datacenter, overheidscloud, publieke cloud.

   […]

2. Uw netwerkontwerp, met zones voor portalen, API-laag, engine, databases en interne systemen.

   […]

3. Uw omgevingen per onderdeel, en per gekoppelde voorziening of route 3 er is.

   […]

4. Back-up en herstel per onderdeel: frequentie, bewaartermijn, hersteltijd en hoeveel gegevensverlies acceptabel is; en wanneer u herstel test.

   […]

5. Of u TriplyDB afneemt als dienst, zelf een triplestore draait, of een andere kiest (AB-16, onder herziening).

   […]

Volgen wij IOU's keuze voor AB-14? [ja / nee — zie afwijking DEV-…]

Volgen wij IOU's keuze voor AB-16? [ja / nee — zie afwijking DEV-…]

## 10. Beheer en continuïteit

Toelichting in de gids: https://iou-architectuur.open-regels.nl/nl/psa/10-management-and-continuity/

### Besluiten van IOU

| ID | Besluit | Laag | Status bij IOU | Afwijken |
|---|---|---|---|---|
| AB-01 | IOU neemt standaarden die nog in ontwikkeling zijn stap voor stap over, en geeft terug wat het daarbij leert. Een functie die een nieuwere versie nodig heeft, staat bewust uit tot die versie is uitgerold; de rest werkt door. | Kern | gerealiseerd | niet open voor afwijking |
| AB-28 | Elk IOU-onderdeel bouwt reproduceerbaar: niets wat een build ophaalt is ongepind, elke release heeft een CycloneDX-SBOM, updates wachten een vaste periode af, en de ICTU-richtlijn voor afhankelijkheden wordt wekelijks gemeten. | Kern | deels | niet open voor afwijking |
| AB-29 | Elk onderdeel heeft zelfstandige releases met kalenderversies; wijzigingen bereiken acceptatie en productie alleen via een pull request. | Kern | deels | niet open voor afwijking |
| AB-30 | Productie wordt geleverd via een standaard leverstraat met een kwaliteitspoort. | Kern | nog niet | niet open voor afwijking |

### Wat IOU beslist (overgenomen uit de IOU PSA-gids)

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

#### Wie doet wat

| Onderwerp | Meegeleverd met de software | Werkwijze van het IOU-team | Regelt u zelf |
|---|---|---|---|
| Afhankelijkheden | Vastgepind; SBOM per release | Updates via geautomatiseerde voorstellen, na een wachttijd; dagelijkse controle op kwetsbaarheden; driemaandelijkse review | De SBOM's die u in gebruik hebt opnieuw controleren op nieuwe kwetsbaarheden; eventueel een eigen pakketregister |
| Kwaliteit | Getest vóór elke release; minimale testdekking per bestand | Test- en controlepoorten op elke pull request | Uw eigen acceptatietest in uw eigen omgevingen |
| Versie-informatie | Elke webinterface en de backends tonen welke build draait | | Die informatie gebruiken in monitoring en bij incidenten |
| Licentie | EUPL-1.2 (Norm Editor: Apache-2.0) | | Licenties van uw eigen aanvullingen |
| Releases | Kalenderversies per onderdeel | Release en promotie naar productie via pull requests | Bepalen wanneer u een release overneemt |
| Broncode | Openbaar op GitHub; spiegel op GitLab | Spiegel bijgewerkt bij elke release | Bepalen welke bron u volgt |
| Hosting en omgevingen | | | Volledig ([hoofdstuk 9](https://iou-architectuur.open-regels.nl/nl/psa/09-technical-infrastructure/)) |
| Monitoring en meldingen | Een gezondheidscontrole op de backends | | Volledig: wat u meet, wanneer u gewaarschuwd wordt |
| Incidenten | | | Volledig: melding, opvolging, communicatie |
| Back-up en herstel | | | Volledig, inclusief hersteltests |
| Kwetsbaarheden melden | Nog geen meldpunt | | Uw eigen meldproces; afspraken met IOU |

Dit geldt volledig voor de CPSV Editor, de Linked Data Explorer en de RONL
Business API. CPRMV en de Norm Editor worden op GitLab gebouwd, met een eigen,
lichter regime: CPRMV test vóór elke build op zijn hoofdbranch; de Norm Editor
heeft nog geen testdekking of controlepoorten.

### Fasering

| | Fase 1: medewerkers | Nu voorbereiden | Fase 2: inwoners en ondernemers |
|---|---|---|---|
| Ondersteuning | Interne servicedesk | Een uitbreidbaar incident- en ondersteuningsproces | Ondersteuning voor inwoners en ondernemers |
| Beschikbaarheid | Afgestemd op werktijden | Monitoring en waarschuwingen | Afspraken over beschikbaarheid buiten werktijd |
| Releases | Overnemen na eigen acceptatietest | Een vast ritme voor overname | Releases zonder onderbreking voor inwoners |

### Onze invulling

1. De rollen: functioneel beheer, applicatiebeheer, technisch beheer, en wie beveiligingsupdates en incidenten afhandelt.

   […]

2. Hoe u releases van IOU volgt en overneemt, en wie daarover beslist.

   […]

3. Hoe u veranderingen in deze gids volgt: statussen, besluiten onder herziening, nieuwe versies van standaarden (AB-01).

   […]

4. Monitoring, waarschuwingen en uw incidentproces.

   […]

5. Back-up en herstel, en hoe vaak u herstel test.

   […]

6. Hoe u bevindingen teruggeeft aan IOU, zodat IOU er ook van leert.

   […]

## 11. Architectuurbesluiten en risico's

Toelichting in de gids: https://iou-architectuur.open-regels.nl/nl/psa/11-decisions-and-risks/

### Besluitenregister van IOU

| ID | Besluit | Laag | Status | Toelichting |
|---|---|---|---|---|
| AB-01 | IOU neemt standaarden die nog in ontwikkeling zijn stap voor stap over, en geeft terug wat het daarbij leert. Een functie die een nieuwere versie nodig heeft, staat bewust uit tot die versie is uitgerold; de rest werkt door. | Kern | gerealiseerd | IOU en CPRMV groeien zo samen; voor DMN stelt IOU een Nederlands toepassingsprofiel voor, [DMN-AP NL](https://github.com/sgort/ttl-editor/blob/main/docs/dmn-ap-nl-voorstel.md). Zie [Hoe IOU zich ontwikkelt](https://iou-architectuur.open-regels.nl/nl/psa/#hoe-iou-zich-ontwikkelt). |
| AB-02 | Elke stap levert zijn product op in een open formaat; niets wordt overgetypt. | Kern | deels | Van dienstbeschrijving tot uitvoering klopt dit. De stap van juridische interpretatie (Norm Editor) naar dienstbeschrijving (CPSV Editor) gaat nog met de hand. |
| AB-03 | Gedeelde producten gebruiken CPSV-AP 3.2.0, CPRMV 0.4.2, BPMN 2.0, DMN 1.3, RDF/Turtle, SKOS/NL-SBB en ELI, BWB, CVDR en JuriConnect voor verwijzingen naar wetgeving. | Kern | deels | De CPSV Editor schrijft nog CPRMV 0.4.1. |
| AB-04 | Open source is de standaard (EUPL-1.2). Een gesloten product kan alleen achter een vervangbare koppeling. | Kern | deels | CPSV Editor, Linked Data Explorer, RONL Business API en CPRMV hebben EUPL-1.2; de Norm Editor heeft Apache-2.0. De RONL Business API vraagt in productie een gesloten taaldienst (zie AB-31). |
| AB-05 | API's volgen de API Design Rules en hebben een OpenAPI 3.1-beschrijving die automatisch wordt gecontroleerd. | Kern | deels | RONL Business API en Linked Data Explorer wel; CPRMV en de Norm Editor nog niet. |
| AB-06 | Publieke dienstverlening wordt beschreven en gepubliceerd met de CPSV Editor. | Kern | gerealiseerd | |
| AB-07 | Regels worden vastgelegd in CPRMV: een regelset hoort bij een publieke dienst, verwijst naar de wet waarop hij berust, en heeft een geldigheidsperiode. | Kern | deels | De CPSV Editor koppelt een regelset aan de wet met een andere relatie dan CPRMV voorschrijft. CPRMV is nog een eerste openbare werkversie. |
| AB-08 | Processen worden ontworpen in de Linked Data Explorer en alleen via zijn backend uitgerold, als één bundel van proces, formulieren en documentsjablonen. | Kern | deels | Zo rolt de Linked Data Explorer uit. Maar zolang de engine direct bereikbaar is, kan een uitrol er ook omheen (zie AB-13). |
| AB-09 | Beslismodellen worden gevonden met standaard SPARQL; regels worden afgenomen via de versie-2-API voor normen, met een vaste stabiliteitsbelofte. | Kern | gerealiseerd | De versie-1-API is uitgefaseerd en verdwijnt op 1 november 2028. |
| AB-10 | Elke gepubliceerde dienst staat in één eigen graaf per organisatie en dienst, op een vast adres. | Kern | gerealiseerd | Opnieuw publiceren overschrijft de graaf; er blijft geen geschiedenis bewaard (risico R-06). |
| AB-11 | Gedeelde producten worden vóór publicatie gevalideerd tegen de SHACL-shapes van CPSV-AP, CPRMV en RONL; een fout blokkeert publicatie. Tijdens het opstellen is de controle een advies. | Kern | nog niet | De controle bestaat, maar blokkeert nooit. |
| AB-12 | Juridische interpretatie wordt vastgelegd in FLINT, gekoppeld aan de brontekst. De Norm Editor is IOU's gereedschap daarvoor. | Vervangbaar | deels | Twee van de zes onderdelen van de Norm Editor zijn nog niet gebouwd, en geen ander onderdeel leest FLINT al in. |
| AB-13 | Een Business API staat tussen elk portaal en de procesengine; de engine is nooit van buitenaf bereikbaar. | Kern | deels | De portalen lopen via de RONL Business API. De engine zelf is nog direct bereikbaar. |
| AB-14 | Processen en beslissingen draaien op een engine met de Camunda 7 REST-API; IOU kiest Operaton. | Vervangbaar | gerealiseerd | Camunda 7 Enterprise past; Camunda 8 vraagt een herbouw. |
| AB-15 | De organisatie reist mee met elke uitrol en elke zaak. Een beslismodel wordt één keer uitgerold en gedeeld; verschillen per organisatie staan in de beslistabel zelf. | Kern | gerealiseerd | |
| AB-16 | Gepubliceerde producten staan in een SPARQL 1.1-triplestore; IOU kiest TriplyDB. | Vervangbaar | gerealiseerd | **Onder herziening**: IOU overweegt Apache Jena Fuseki. |
| AB-17 | Backends accepteren tokens van één OIDC-uitgever, die de inlogvoorzieningen voor medewerkers en inwoners achter zich koppelt. Welk product de uitgever is, staat in AB-32. | Kern | deels | De RONL Business API wel. De ontwerptools controleren nog geen tokens (zie AB-20). |
| AB-18 | De backend bepaalt per zaak wie iets mag, en weigert bij twijfel: alleen de eigen organisatie of de aanvrager zelf. | Kern | gerealiseerd | In de RONL Business API. |
| AB-19 | Handelingen vragen een betrouwbaarheidsniveau: `basis` om een beslissing te laten berekenen, `midden` om een proces te starten. | Kern | deels | De controle werkt. DigiD en eIDAS zijn voorbereid maar uitgeschakeld; eHerkenning is er nog niet. |
| AB-20 | Elke schrijfactie in elk onderdeel is geauthenticeerd, geautoriseerd en vastgelegd. Publiceren gebeurt namens een bevoegde organisatie. | Kern | deels | De RONL Business API wel. Linked Data Explorer, CPSV Editor en Norm Editor nog niet. |
| AB-21 | De ontwerptools zijn alleen voor medewerkers; inwoners en ondernemers komen alleen bij de portalen en de publieke site. | Kern | deels | Inwoners krijgen de ontwerptools niet aangeboden, maar die tools dwingen dat nog niet af (zie AB-20). |
| AB-22 | Publieke catalogi worden live uit de kennisgraaf gelezen, via een aparte publieke laag die alleen leest, zonder inloggen en met een limiet op het aantal verzoeken. | Kern | gerealiseerd | |
| AB-23 | Elk geauthenticeerd verzoek wordt vastgelegd in een aparte auditopslag. De bewaartermijn bepaalt u zelf. | Kern | deels | De vastlegging werkt; een bewaartermijn wordt nog nergens toegepast. |
| AB-24 | Documenten blijven in het documentmanagementsysteem van de organisatie; de zaak bevat alleen een verwijzing. | Eigen keuze | gerealiseerd | |
| AB-25 | Elk onderdeel beheert zijn eigen gegevens; geen onderdeel leest de database van een ander. | Kern | deels | De RONL Business API leest nog rechtstreeks uit de database van de Linked Data Explorer. |
| AB-26 | Gegevens blijven bij de bron: basisregistraties worden bevraagd, niet gekopieerd. | Kern | deels | De BRP wordt bevraagd via de Haal Centraal-API, maar nog tegen een testvoorziening. Andere registraties zijn nog niet gekoppeld. |
| AB-27 | Het verwerkingsregister (AVG artikel 30) wordt per proces bijgehouden in de Linked Data Explorer en gepubliceerd. | Vervangbaar | gerealiseerd | U mag uw register ook elders bijhouden. |
| AB-28 | Elk IOU-onderdeel bouwt reproduceerbaar: niets wat een build ophaalt is ongepind, elke release heeft een CycloneDX-SBOM, updates wachten een vaste periode af, en de ICTU-richtlijn voor afhankelijkheden wordt wekelijks gemeten. | Kern | deels | CPSV Editor, Linked Data Explorer en RONL Business API wel; CPRMV en de Norm Editor nog niet. |
| AB-29 | Elk onderdeel heeft zelfstandige releases met kalenderversies; wijzigingen bereiken acceptatie en productie alleen via een pull request. | Kern | deels | CPSV Editor, Linked Data Explorer en RONL Business API wel. CPRMV volgt de versie van zijn specificatie; de Norm Editor kent alleen een productiebranch. |
| AB-30 | Productie wordt geleverd via een standaard leverstraat met een kwaliteitspoort. | Kern | nog niet | Alle onderdelen leveren nu via het spoor voor snelle prototypes. |
| AB-31 | Een taalmodel-assistent is optioneel en de keuze van de organisatie. | Eigen keuze | nog niet | De RONL Business API start in productie niet zonder sleutel voor een gesloten taaldienst. |
| AB-32 | IOU kiest Keycloak als OIDC-uitgever. | Vervangbaar | gerealiseerd | Een andere uitgever die OIDC-tokens uitgeeft en de inlogvoorzieningen koppelt, kan; bijvoorbeeld Entra ID. |

### Onze afwijkingen

| ID | Wijkt af van | Reden | Strijdig met principe | Kosten | Weg terug |
|---|---|---|---|---|---|
| DEV-01 | […] | […] | […] | […] | […] |

### Risico's

| ID | Risico | Raakt | Wat u ondertussen doet | Issue | Geldt voor ons? | Onze maatregel |
|---|---|---|---|---|---|---|
| R-01 | De procesengine is direct bereikbaar, buiten de controles van de Business API om. | AB-08, AB-13 | Plaats de engine in uw eigen netwerk zo dat alleen de backends hem bereiken. | Gemeld bij het onderdeel; link volgt na herstel | […] | […] |
| R-02 | De ontwerptools accepteren schrijfacties zonder dat vaststaat wie ze doet. | AB-17, AB-20, AB-21 | Maak de ontwerptools alleen bereikbaar binnen uw netwerk, achter de inlogvoorziening van uw organisatie. | Gemeld bij het onderdeel; link volgt na herstel | […] | […] |
| R-03 | Toegang voor inwoners en ondernemers werkt nog niet echt: DigiD en eIDAS staan uit, eHerkenning ontbreekt, de BRP is een testvoorziening. | AB-19, AB-26 | Beperk de ingebruikname tot fase 1. Plan de aansluiting op DigiD, eHerkenning en de BRP als eigen project vóór fase 2. | — | […] | […] |
| R-04 | Wat de CPSV Editor schrijft, wijkt af van CPRMV 0.4.2, en CPRMV is zelf nog een werkversie. Dat hoort bij hoe IOU en CPRMV samen groeien, maar het betekent dat gedeelde regels tussen versies kunnen verschillen. | AB-03, AB-07 | Valideer gepubliceerde regels tegen de CPRMV-shapes, volg de ontwikkeling van CPRMV, en geef wat u tegenkomt terug aan IOU. | — | […] | […] |
| R-05 | SHACL-validatie geeft alleen advies; een product met fouten kan worden gepubliceerd. | AB-11 | Spreek af dat niemand publiceert zolang de validatie fouten meldt. | — | […] | […] |
| R-06 | Een gepubliceerde dienstbeschrijving houdt geen geschiedenis bij: opnieuw publiceren overschrijft de vorige versie. Dat raakt de Archiefwet. | AB-10 | Archiveer elke gepubliceerde versie zelf, met datum, in uw archiefvoorziening. | — | […] | […] |
| R-07 | Niet elk onderdeel voldoet aan de bouw- en API-afspraken, en er is nog geen standaard leverstraat. | AB-05, AB-28, AB-29, AB-30 | Neem CPRMV en de Norm Editor op in uw eigen acceptatietest; neem geen release in productie zonder die test. | — | […] | […] |
| R-08 | De RONL Business API vraagt in productie een gesloten taaldienst. | AB-04, AB-31 | Beoordeel de taaldienst op AVG en verwerkersovereenkomst, of wacht tot hij optioneel is. | — | […] | […] |
| R-09 | Eén onderdeel leest rechtstreeks de database van een ander; wijzigingen aan die database kunnen het breken. | AB-25 | Neem beide onderdelen altijd samen op in uw acceptatietest. | — | […] | […] |
| R-10 | Er wordt geen bewaartermijn toegepast op auditgegevens. | AB-23 | Stel uw bewaartermijn vast en richt het opschonen zelf in. | — | […] | […] |
| R-11 | De juridische interpretatie wordt met de hand overgenomen in de dienstbeschrijving, en de Norm Editor is nog niet compleet. | AB-02, AB-12 | Leg vast wie de overname controleert, en hoe. | — | […] | […] |
| R-12 | De procesengine heeft nog geen eigen productie-instantie: acceptatie en productie delen één engine. Voor de engine en de database van de Linked Data Explorer is geen back-up ingericht. | — | Richt in uw eigen omgeving een aparte engine per omgeving in, met een productiedatabase, back-up en een geteste herstelprocedure. | Gemeld bij het onderdeel; link volgt na herstel | […] | […] |
| R-13 | Overstappen naar een andere triplestore of hosting vraagt aanpassingen in de code; niet alle adressen zijn instelbaar. | AB-16 | Reken bij een andere triplestore of hosting op ontwikkelwerk, en neem dat op in de planning. | — | […] | […] |
| R-14 | Op test en acceptatie breekt de keten: de bestaande voorzieningen waaraan IOU koppelt (bijvoorbeeld documentbeheer, ondertekening, identiteitsbeheer, financiën) hebben vaak alleen een productieomgeving. Acceptatie toetst dan een nabootsing, of raakt productiegegevens. | — | Laat beheerders en leveranciers een test- en acceptatieomgeving inrichten voor elke gekoppelde voorziening (route 3 in [hoofdstuk 7](https://iou-architectuur.open-regels.nl/nl/psa/07-integration-architecture/)). Tot die er is: toets met nabootsingen, en leg vast dat de echte koppeling pas in productie voor het eerst wordt gebruikt. | — | […] | […] |
| R-15 | Een beslismodel kan alle controles doorstaan en toch nooit de juiste uitkomst geven: DMN eist niet dat een model aantoont dat het werkt, en zegt niet hoe het naar de wet verwijst. | AB-03 | Test elk beslismodel met testgevallen vóór uitrol, ook op de uitkomsten die het moet kunnen geven. Volg de ontwikkeling van [DMN-AP NL](https://github.com/sgort/ttl-editor/blob/main/docs/dmn-ap-nl-voorstel.md). | — | […] | […] |
