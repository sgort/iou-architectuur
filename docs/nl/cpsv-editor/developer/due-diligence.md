# CPSV Editor — Product- & Architectuuroverzicht

**Repository:** `ttl-editor` (publiek, GitLab — gespiegeld naar GitHub)

**Doel:** Een browsergebaseerde editor voor het aanmaken, importeren en exporteren van Nederlandse overheidsdienst­beschrijvingen als RDF/Turtle-bestanden, conform de EU CPSV-AP 3.2.0-standaard.

**Onderdeel van:** Het RONL-initiatief (regels.overheid.nl) — tooling voor machineleesbare metadata van overheidsregelgeving.

---

## Wat het doet

De editor stelt beleidsanalisten en regelmodelleurs in staat om een publieke dienst (bijv. Zorgtoeslag, WW-uitkering) te beschrijven via een gestructureerd formulier. Het formulier legt de dienst vast, de verantwoordelijke organisatie, de onderliggende wetgeving, temporele bedrijfsregels, parameters, kosten, outputs en gekoppelde concepten. De editor genereert in realtime een standaardconforme Turtle-bestand (.ttl) via een live voorbeeldvenster en kan eerder geëxporteerde .ttl-bestanden opnieuw importeren voor round-trip-bewerking.

---

## Functionele domeinen

De huidige applicatie bundelt vier onderscheiden functionele domeinen in één React-SPA. Elk domein zou in principe als onafhankelijke module of product kunnen functioneren zonder de overige te verstoren — mits ze hetzelfde RDF-datamodel als integratiecontract delen.

### 1 — Kerneditor (metadata-authoring)

Formuliergebaseerde authoring van CPSV-AP 3.2.0-conforme dienstbeschrijvingen. Tien tabbladen bestrijken het volledige datamodel:

| Tabblad | Wat het vastlegt | Belangrijkste standaarden |
|---|---|---|
| Dienst | Identificatie, naam, beschrijving, sector, thematisch gebied, trefwoorden | CPSV-AP, DCAT |
| Organisatie | Bevoegd gezag, homepage, geografische jurisdictie, logo | CV, FOAF, ORG |
| Juridisch | BWB/CVDR-wetgevingsreferentie, versie, RONL-analyse- & methodeconcepten | ELI, SKOS, RONL-vocabulaire |
| Regels | Temporele bedrijfsregels met geldigheidsperioden en betrouwbaarheidsniveaus | CPRMV 0.3.0 |
| CPRMV (Beleid) | Normatieve regels met ruleId, rulesetId, situatie, norm, definitie | CPRMV 0.3.0 |
| Parameters | Benoemde parameterwaarden (bedragen, percentages, looptijden) met temporele geldigheid | CPRMV, SKOS |
| Concepten | NL-SBB-conforme SKOS-concepten met labels, definities, notaties | SKOS, NL-SBB |
| Kosten / Output | Dienstkosten en outputbeschrijvingen (ingebed in het tabblad Dienst) | CV |
| Wijzigingslog | Versiegeschiedenis | Eigen formaat |

Aanvullende mogelijkheden: TTL-import met volledige round-trip trust (parseTTL_enhanced.js, ~770 regels), TTL-export met live voorbeeldweergave, formuliervalidatie, CPRMV JSON-import en een "alles wissen"-reset.

### 2 — Leveranciersintegratie

Het tabblad Leverancier biedt een multi-leverancier-architectuur waarmee organisaties leverancierspecifieke implementaties aan een dienstbeschrijving kunnen koppelen. Er bestaan momenteel twee integratietypes:

**Blueriq** — Legt contactinformatie vast, technische service-URL, licentietype, toegangsmodel en certificeringsstatus. Leveranciers worden geselecteerd uit de RONL-vocabulaire-dropdown (bij opstart opgehaald via SPARQL uit TriplyDB). Geserialiseerd als `ronl:VendorService`-triples in de output.

**iKnow** — Importeert Cognitatie/iKnow XML-annotatie-exports en mapt kennisdomein­concepten naar het datamodel van de editor via configureerbare mappingbestanden. Een eenrichtingsimportpad dat de tabbladen Dienst, Organisatie, Juridisch, Regels en Parameters vult vanuit de iKnow XML-structuur.

Beide integraties bevinden zich binnen hetzelfde tabblad Leverancier, wat het patroon demonstreert voor het onboarden van aanvullende leverancierstoolchains in de toekomst.

**Koppeling met kerneditor:** Laag. Gebruikt de RONL-vocabulaire­concepten (gedeeld met het tabblad Juridisch) en de dienst-identifier voor URI-generatie.

### 3 — Publicatie naar TriplyDB

Een PublishDialog-component verzorgt het uploaden van de gegenereerde TTL-inhoud naar een TriplyDB-triplestore. Twee uploadmethoden zijn geïmplementeerd: FormData-gebaseerde bestandsupload (`publishToTriplyDB`) en SPARQL UPDATE-insertie (`publishToTriplyDB_SPARQL`). De publicatieworkflow is een meerstapsproces met voortgangs­registratie: valideren → TTL genereren → uploaden naar TriplyDB → logo's uploaden (organisatie + leverancier) → SPARQL-service bijwerken → bevestigen. Ondersteunt configureerbaar account/dataset/token (opgeslagen in localStorage), verbindingstesten, graph-IRI-generatie op basis van organisatie- + dienst-identifiers, en SPARQL-service-herindexering (via de gedeelde Express-backend om CORS te vermijden).

**Koppeling met kerneditor:** Laag. Gebruikt uitsluitend de gegenereerde TTL-string en dienst-/organisatie-identifiers voor graph-naamgeving. De Express-backend (`REACT_APP_BACKEND_URL`) wordt gedeeld met de Linked Data Explorer.

### 4 — DMN-integratie & Operaton-deployment

Het DMN-tabblad (`DMNTab.jsx`, ~1520 regels) behandelt de volledige levenscyclus van beslismodel­integratie. De workflow doorloopt vier stadia: valideren → deployen → testen → concepten genereren.

**Uploaden & Valideren.** Upload een `.dmn`-bestand of laad een ingebouwd voorbeeld. Bij upload parseert de editor de DMN-XML client-side (DOMParser) om de primaire beslissleutel te extraheren (met overslaan van `p_*`-constante parameters), detecteert alle testbare beslissingen in een DRD, en genereert automatisch een request-body vanuit `<inputData>`-elementen met slimme type-inferentie (datums krijgen willekeurige geboorte­datums, numerieke waarden standaard 0, booleans false). Tegelijkertijd roept de editor het gedeelde LDE-backend-endpoint `POST /v1/dmns/validate` aan voor vijflaagse syntactische validatie (`dmn-validation.service.ts`, ~950 regels, met libxmljs2):

| Laag | Scope | Voorbeeldcontroles |
|---|---|---|
| 1 — Basis-DMN | XML-welgevormdheid, root-element, DMN-namespace | BASE-PARSE, BASE-ROOT, BASE-NS |
| 2 — Bedrijfsregels | Beslistabelstructuur, hit policies, type refs, invoer-/uitvoerentries | BIZ-001 t/m BIZ-008+ |
| 3 — Uitvoeringsregels | CPRMV-extensieattributen (ruleType, confidence, validFrom/Until, BWB-ID's) | EXEC-001 t/m EXEC-006+ |
| 4 — Interactieregels | DRD-bedrading, informationRequirement-integriteit, verweesde inputData, zelfreferenties | INT-001 t/m INT-007 |
| 5 — Inhoud | Metadatakwaliteit — lege beschrijvingen, ontbrekende typeRefs, lege tekstannotaties | CON-001 t/m CON-005 |

Validatieresultaten (fouten, waarschuwingen, info per laag) worden inline weergegeven met inklapbaar detail per laag. Dit is dezelfde validatie-engine die wordt gebruikt door de drag-and-drop DMN-validator van de Linked Data Explorer voor meerdere bestanden. Als de backend onbereikbaar is, faalt de validatie stil — het blokkeert de DMN-workflow niet.

**Deployen.** Eenkliksdeploy naar de Operaton-regelengine (`operaton.open-regels.nl/engine-rest/deployment/create`) via multipart-formulierupload. Slaat het deployment-ID en tijdstempel op in de editor-state.

**Testen.** Drie testniveaus, alle via directe aanroep van Operaton `/engine-rest/decision-definition/key/{key}/evaluate`-endpoint vanuit de browser:

| Testmodus | Wat het doet |
|---|---|
| Enkele evaluatie (Postman-stijl) | Bewerkbare JSON-request-body, evalueer de primaire beslissing, bekijk de volledige respons inline. De request-body wordt automatisch gegenereerd uit DMN-inputData maar is volledig bewerkbaar. |
| Tussenliggende beslissingstests | Voor DRD's met meerdere beslissingen: evalueert elke deelbeslissing individueel met dezelfde request-body. Toont progressieve resultaten (ok / fout / onverwacht) per beslissing. Constante-parameterbeslissingen (`p_*`) worden automatisch gefilterd. |
| Testcases | Upload een `test-cases.json`-bestand (ondersteunt twee formaten: Toeslagen `{name, expected, requestBody}` en DUO `{testName, testResult, variables}`). Voert alle cases sequentieel uit tegen de primaire beslissing. Toont slaag/faal per case met uitklapbaar detail. |

**Conceptgeneratie.** Na elke geslaagde test genereert het tabblad automatisch NL-SBB-conforme SKOS-concepten uit de DMN-invoer-/uitvoervariabelen — inclusief URI, prefLabel, definitie, notatie en `skos:exactMatch` — en pusht deze naar het tabblad Concepten. Testcase-runs genereren concepten uit de laatst geslaagde case.

De DMN-inhoud wordt ingebed in de TTL-output als `cprmv:DecisionModel`-triples, en het tabblad Organisatie ondersteunt validatiestatustracking (niet-gevalideerd / in-review / gevalideerd / afgewezen) met metadata over wie heeft gevalideerd en wanneer.

**Koppeling met kerneditor:** Gemiddeld. DMN-metadata (deploystatus, testresultaten, validatie) is onderdeel van de editor-state. De automatisch gegenereerde concepten voeden het tabblad Concepten. De TTL-export bevat DMN-blokken. De syntactische validatie is afhankelijk van het gedeelde LDE-backend (`POST /v1/dmns/validate`). De Operaton REST API-interactie en DMN XML-parsing (`dmnHelpers.js`) zijn echter op zichzelf staande utilities.

---

## Technologiestack

| Laag | Technologie |
|---|---|
| Frontend | React 19, Create React App (verouderd — zie hieronder), Tailwind CSS, Lucide-iconen |
| Statusbeheer | React hooks (`useEditorState`, `useArrayHandlers`), geen externe state-library |
| Build & lint | CRA, ESLint, Prettier, Husky (pre-commit/pre-push), lint-staged |
| TTL-parsing | Eigen handgeschreven parser (geen RDF-library-afhankelijkheid) |
| DMN-parsing | Browser DOMParser (XML) |
| Externe API's | TriplyDB REST + SPARQL, Operaton REST (Camunda-compatibel), RONL SPARQL-vocabulaire |
| Backend-afhankelijkheid | Gedeelde Express-server (Linked Data Explorer-repo) voor CORS-geproxyde SPARQL-queries, TriplyDB-service-updates en DMN-syntactische validatie (libxmljs2) |
| Hosting | Azure Static Web Apps (acc-branch → acceptatie, main → productie) |
| CI/CD | GitHub Actions → Azure SWA deploy |

---

## Advies voor het DevOps-team

**Wat goed is:** De applicatie werkt, is in actief gebruik, heeft real-world TTL-voorbeelden voor 12+ organisaties en bestrijkt een complexe EU-standaard. De vocabulaireconfiguratie is goed gestructureerd, de validatielaag is solide en de TTL round-trip import/export is volwassen.

**Wat te beoordelen:**

- **Geen RDF-library.** TTL-parsing en -generatie zijn volledig handgeschreven (~770 + ~200 regels). Dit werkt maar is fragiel voor randgevallen. Evalueer of het introduceren van een lichtgewicht RDF/JS-library (bijv. N3.js) de onderhoudslast zou verlagen versus de kosten van migratie.

- **App.js-orkestratie.** De hoofd-`App.js` (1143 regels) is gedeeltelijk gemodulariseerd: datastatus leeft in `useEditorState`, array-CRUD-operaties in `useArrayHandlers`, TTL-importlogica in `importHandler.js` en TTL-generatie in `ttlGenerator.js`. Wat in App.js overblijft is UI-orkestratie (tabweergave, bericht-/statusbeheer), de publicatieworkflow (~300 regels stap-voor-stap voortgangsregistratie) en code die status aan child componenten koppelt. Verdere extractiedoelen: de publicatie-handler zou een custom hook kunnen worden (`usePublishWorkflow`), en de tabnavigatie + berichtensysteem kan worden gescheiden van de data wiring.

- **Geen geautomatiseerde tests voor TTL-output.** Het testbestand (`App.test.js`) is een CRA-stub. De werkelijke validatie vindt handmatig plaats via voorbeeldbestanden. Een testsuite die gegenereerde TTL vergelijkt met de referentievoorbeelden zou zeer waardevol zijn.

- **localStorage voor configuratie.** TriplyDB-credentials worden opgeslagen in localStorage. Prima voor een prototype, maar voor een productietool die door meerdere teams wordt gebruikt, behoeft een andere secrets-/configuratiebeheer­aanpak.

- **Gedeelde backend.** De Express-backend is onderdeel van de Linked Data Explorer-repo. De CPSV Editor is ervan afhankelijk voor drie zaken: CORS-geproxyde SPARQL-queries (RONL-vocabulaire), TriplyDB-service-herindexering en DMN-syntactische validatie (de vijflaagse validator gebruikt libxmljs2, dat een Node.js-runtime vereist). Wijzigingen aan de backend beïnvloeden de CPSV Editor. Verduidelijk eigenaarschap, versiebeheer (API v1-header is reeds aanwezig) en deploykoppeling.

- **Separatiemogelijkheid.** De vier domeinen (editor, leverancier, publicatie, DMN) zijn losjes gekoppeld via de gedeelde editor-state. Een modulaire architectuur — of als aparte routes/lazy-loaded modules binnen de SPA (Single Page Application), of als onafhankelijke micro-frontends die een TTL-datacontract delen — zou de onderhoudbaarheid verbeteren en onafhankelijke release-cycli mogelijk maken.

- **Create React App.** Het React-team heeft CRA officieel als verouderd aangemerkt op 14 februari 2025. Het blijft werken in onderhoudsmodus (een definitieve versie is gepubliceerd met React 19-ondersteuning), maar het zal geen nieuwe functies, prestatieverbeteringen of actieve beveiligingsupdates ontvangen. Het React-team beveelt migratie aan naar een framework (Next.js, React Router) of een moderne build-tool (Vite, Parcel, Rsbuild). Aangezien de Linked Data Explorer reeds Vite gebruikt, zou migratie van de CPSV Editor naar Vite de tooling binnen het RONL-ecosysteem gelijktrekken en de afhankelijkheid van een niet meer onderhouden build-tool wegnemen.

---

## Authenticatie & Autorisatie voor Productiepublicatie

Het prototype heeft geen gebruikersauthenticatie. Een gebruiker die een overheidsdienst­beschrijving publiceert naar de productie-TriplyDB-instantie handelt namens een bevoegd gezag — dat is een formeel mandaat dat verifieerbaar moet zijn. De huidige codebase behandelt credentials als volgt:

| Integratiepunt | Huidig authenticatiemechanisme |
|---|---|
| TriplyDB-publicatie | Persoonlijk API-token, ingevoerd door de gebruiker, opgeslagen in browser-localStorage |
| Operaton-deployment & testen | Hardcoded Basic Auth (`demo:demo`) |
| Gedeelde Express-backend (LDE) | Geen authenticatie — endpoints zijn open |
| Azure Static Web Apps | Deployment-tokens in GitHub Secrets (alleen CI/CD, geen gebruikersauth) |

Geen van deze mechanismen stelt vast wie de gebruiker is, welke organisatie zij vertegenwoordigen, of zij geautoriseerd zijn om namens die organisatie te publiceren. Voor een productieomgeving is dit een vereiste, geen verbetering.

**Wat er moet veranderen.** De productiepublicatie­flow moet de gebruiker authenticeren via de IAM-infrastructuur die reeds bestaat voor Nederlandse overheidsorganisaties en ambtenaren. De gebruikelijke aanpak is integratie van een OpenID Connect (OIDC) identity provider — ofwel de eigen IdP van de organisatie (bijv. Microsoft Entra ID / Azure AD, waar de meeste overheidsorganisaties reeds over beschikken) ofwel een gefedereerde overheids-IdP. De authenticatie moet een verifieerbare identiteitsclaim opleveren (wie is deze persoon, bij welke organisatie hoort deze) die de backend kan gebruiken om de publicatieactie te autoriseren.

**Advies voor het DevOps-team:**

- **Backend-gemedieerde publicatie.** In productie mag de publicatieactie niet rechtstreeks vanuit de browser naar TriplyDB gaan met een door de gebruiker opgegeven API-token. In plaats daarvan moet de geauthenticeerde gebruiker publicatie aanvragen via de backend, die de TriplyDB-servicecredentials beheert en autorisatieregels kan afdwingen (heeft deze gebruiker het recht om namens deze organisatie te publiceren, naar deze dataset/graph?). Dit elimineert tevens het localStorage-tokenopslagprobleem.

- **Operaton-credentials.** De hardcoded `demo:demo` Basic Auth moet worden vervangen. In productie moet de backend Operaton-aanroepen proxyen met juiste servicecredentials, vergelijkbaar met hoe het reeds SPARQL-queries naar TriplyDB proxyt.

- **Backend-authenticatie.** De gedeelde Express-backend heeft momenteel geen authenticatie-middleware. Het toevoegen van een OIDC-tokenverificatie-middleware (die JWT-access-tokens van de IdP van de organisatie valideert) zou alle drie de backendfuncties (SPARQL-proxy, TriplyDB-publicatie, DMN-validatie) in één laag beschermen.

- **Audittrail.** Wanneer een publicatie het gewicht draagt van een mandaat van een bevoegd gezag, wordt een auditlog die vastlegt wie wat heeft gepubliceerd, wanneer en namens wie, essentieel. De backend is de natuurlijke plek hiervoor.

- **Scope.** Dit geldt specifiek voor de productieomgeving. De ontwikkel- en acceptatieomgevingen kunnen blijven werken met de huidige prototype-credentials ten behoeve van snelle iteratie.