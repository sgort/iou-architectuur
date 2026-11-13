---
component: CPSV Editor
---

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
| Dienst | Identificatie, naam, beschrijving, sector, thematisch gebied, trefwoorden, vereiste diensten (`dct:requires`) | CPSV-AP, DCAT |
| Organisatie | Bevoegd gezag, homepage, geografische jurisdictie, logo | CV, FOAF, ORG |
| Juridisch | BWB/CVDR-wetgevingsreferentie, versie, RONL-analyse- & methodeconcepten | ELI, SKOS, RONL-vocabulaire |
| Regels | Temporele bedrijfsregels met geldigheidsperioden en betrouwbaarheidsniveaus | CPRMV 0.4.1 |
| CPRMV (Beleid) | Normatieve regels met ruleId, rulesetId, situatie, norm, definitie; gegroepeerd in `cprmv:RuleSet`s | CPRMV 0.4.1 |
| Parameters | Benoemde parameterwaarden (bedragen, percentages, looptijden) met temporele geldigheid | CPRMV, SKOS |
| Concepten | NL-SBB-conforme SKOS-concepten met labels, definities, notaties | SKOS, NL-SBB |
| Kosten / Output | Dienstkosten en outputbeschrijvingen (ingebed in het tabblad Dienst) | CV |
| Wijzigingslog | Versiegeschiedenis | Eigen formaat |

Aanvullende mogelijkheden: TTL-import met volledige round-trip trust (`parseTTL.enhanced.js`, ~840 regels), TTL-export met live voorbeeldweergave, formuliervalidatie, CPRMV JSON-import en een "alles wissen"-reset.

### 2 — Leveranciersintegratie

Het tabblad Leverancier biedt een multi-leverancier-architectuur waarmee organisaties leverancierspecifieke implementaties aan een dienstbeschrijving kunnen koppelen. Er bestaan momenteel twee integratietypes:

**Blueriq** — Legt contactinformatie vast, technische service-URL, licentietype, toegangsmodel en certificeringsstatus. Leveranciers worden geselecteerd uit de RONL-vocabulaire-dropdown (bij opstart opgehaald via SPARQL uit TriplyDB). Geserialiseerd als `ronl:VendorService`-triples in de output.

**iKnow** — Importeert Cognitatie/iKnow XML-annotatie-exports en mapt kennisdomein­concepten naar het datamodel van de editor via configureerbare mappingbestanden. Een eenrichtingsimportpad dat de tabbladen Dienst, Organisatie, Juridisch, Regels en Parameters vult vanuit de iKnow XML-structuur.

Beide integraties bevinden zich binnen hetzelfde tabblad Leverancier, wat het patroon demonstreert voor het onboarden van aanvullende leverancierstoolchains in de toekomst.

**Koppeling met kerneditor:** Laag. Gebruikt de RONL-vocabulaire­concepten (gedeeld met het tabblad Juridisch) en de dienst-identifier voor URI-generatie.

### 3 — Publicatie naar TriplyDB

Een PublishDialog-component publiceert de gegenereerde TTL naar een TriplyDB-triplestore — sinds v2026.11.1 via de gedeelde Express-backend, als de ingelogde auteur, in één aanroep (`publishToTriplyDB` → `POST /v1/triplydb/publish`). De backend beheert het TriplyDB-account en -token, uploadt de Turtle naar een graph-IRI op basis van de organisatie- en dienst-identifiers, uploadt de logo's van organisatie en leverancier, herindexeert de SPARQL-service van de dataset en legt vast wie publiceerde. De dialoog toont de voortgang (valideren → TTL genereren → publiceren), controleert desgevraagd de dataset via de backend en bewaart alleen de datasetnaam in localStorage. Publiceren vereist de realmrol `lde-author`.

Bij het openen van de dialoog draait ook een **adviserende pre-publicatie SHACL-validatie** (`shaclHelper.js` → `POST /v1/shacl/validate`), met een gelaagd CPRMV 0.4.1 / CPSV-AP 3.2.0 / RONL-resultaat. Deze blokkeert publiceren nooit en valt terug op een neutrale amberstatus wanneer de backend onbereikbaar is. De validatie controleert de *opnieuw gegenereerde* output van de editor, die kan afwijken van een geïmporteerd bronbestand omdat import naar de 0.4.1-vocabulaire normaliseert.

**Koppeling met kerneditor:** Laag. Gebruikt uitsluitend de gegenereerde TTL-string en dienst-/organisatie-identifiers voor graph-naamgeving. De Express-backend (`VITE_BACKEND_URL`) wordt gedeeld met de Linked Data Explorer.

### 4 — DMN-integratie & Operaton-deployment

Het DMN-tabblad (`DMNTab.jsx`, ~1840 regels) behandelt de volledige levenscyclus van beslismodel­integratie. De workflow doorloopt vier stadia: valideren → deployen → testen → concepten genereren.

**Uploaden & Valideren.** Upload een `.dmn`-bestand of laad een ingebouwd voorbeeld. Bij upload parseert de editor de DMN-XML client-side (DOMParser) om de primaire beslissleutel te extraheren (met overslaan van `p_*`-constante parameters), detecteert alle testbare beslissingen in een DRD, en genereert automatisch een request-body vanuit `<inputData>`-elementen met slimme type-inferentie (datums krijgen willekeurige geboorte­datums, numerieke waarden standaard 0, booleans false). Tegelijkertijd roept de editor het gedeelde LDE-backend-endpoint `POST /v1/dmns/validate` aan voor vijflaagse syntactische validatie (`dmn-validation.service.ts`, ~950 regels, met libxmljs2):

| Laag | Scope | Voorbeeldcontroles |
|---|---|---|
| 1 — Basis-DMN | XML-welgevormdheid, root-element, DMN-namespace | BASE-PARSE, BASE-ROOT, BASE-NS |
| 2 — Bedrijfsregels | Beslistabelstructuur, hit policies, type refs, invoer-/uitvoerentries | BIZ-001 t/m BIZ-008+ |
| 3 — Uitvoeringsregels | CPRMV-extensieattributen (ruleType, confidence, validFrom/Until, BWB-ID's) | EXEC-001 t/m EXEC-006+ |
| 4 — Interactieregels | DRD-bedrading, informationRequirement-integriteit, verweesde inputData, zelfreferenties | INT-001 t/m INT-007 |
| 5 — Inhoud | Metadatakwaliteit — lege beschrijvingen, ontbrekende typeRefs, lege tekstannotaties | CON-001 t/m CON-005 |

Validatieresultaten (fouten, waarschuwingen, info per laag) worden inline weergegeven met inklapbaar detail per laag. Dit is dezelfde validatie-engine die wordt gebruikt door de drag-and-drop DMN-validator van de Linked Data Explorer voor meerdere bestanden. Als de backend onbereikbaar is, toont het paneel een aparte amberkleurige *"Syntax validation result not available"*-status (v1.9.5) in plaats van stil te falen — deployen en testen blijven werken; alleen de syntactische voorcontrole wordt overgeslagen.

**Deployen.** Eenkliksdeploy naar de Operaton-regelengine, via `POST /v1/dmns/deploy` op de gedeelde LDE-backend in plaats van een directe aanroep vanuit de browser (v2026.08.0 — die directe aanroep liep vast op CORS bij lokale ontwikkeling). Slaat het deployment-ID en tijdstempel op in de editor-state.

**Testen.** Drie testniveaus, alle via `POST /v1/dmns/evaluate/{key}` op de gedeelde LDE-backend (v2026.08.0), die Operaton server-to-server aanroept:

| Testmodus | Wat het doet |
|---|---|
| Enkele evaluatie (Postman-stijl) | Bewerkbare JSON-request-body, evalueer de primaire beslissing, bekijk de volledige respons inline. De request-body wordt automatisch gegenereerd uit DMN-inputData maar is volledig bewerkbaar. |
| Tussenliggende beslissingstests | Voor DRD's met meerdere beslissingen: evalueert elke deelbeslissing individueel met dezelfde request-body. Toont progressieve resultaten (ok / fout / onverwacht) per beslissing. Constante-parameterbeslissingen (`p_*`) worden automatisch gefilterd. |
| Testcases | Upload een `test-cases.json`-bestand (ondersteunt twee formaten: Toeslagen `{name, expected, requestBody}` en DUO `{testName, testResult, variables}`). Voert alle cases sequentieel uit tegen de primaire beslissing. Toont slaag/faal per case met uitklapbaar detail. |

**Conceptgeneratie.** Na elke geslaagde test genereert het tabblad automatisch NL-SBB-conforme SKOS-concepten uit de DMN-invoer-/uitvoervariabelen — inclusief URI, prefLabel, definitie, notatie en `skos:exactMatch` — en pusht deze naar het tabblad Concepten. Testcase-runs leiden invoerconcepten af uit de vereniging van de request-bodyvariabelen van álle geüploade cases (zodat alle invoer wordt gedekt, ook zonder geslaagde evaluatie) en voegen uitvoerconcepten toe uit de laatst geslaagde case (v1.10.2). Gegenereerde concept-URI's, `dct:subject` en `skos:exactMatch` worden IRI-veilig gemaakt (witruimte → `_`, ongeldige tekens percent-gecodeerd) zodat de export door een strikte SHACL-parser komt en schoon herimporteert.

De DMN-inhoud wordt ingebed in de TTL-output als `cprmv:DecisionModel`-triples, en het tabblad Organisatie ondersteunt validatiestatustracking (niet-gevalideerd / in-review / gevalideerd / afgewezen) met metadata over wie heeft gevalideerd en wanneer.

**Koppeling met kerneditor:** Gemiddeld. DMN-metadata (deploystatus, testresultaten, validatie) is onderdeel van de editor-state. De automatisch gegenereerde concepten voeden het tabblad Concepten. De TTL-export bevat DMN-blokken. De syntactische validatie is afhankelijk van het gedeelde LDE-backend (`POST /v1/dmns/validate`). Deployen en evalueren lopen ook via die backend (`/v1/dmns/deploy`, `/v1/dmns/evaluate/{key}`), zodat het tabblad niet meer rechtstreeks met Operaton communiceert. DMN XML-parsing (`dmnHelpers.js`) blijft een op zichzelf staande utility.

### 5 — DSO → DMN deep-link import

De `useDsoImport`-hook (`src/hooks/useDsoImport.js`, v1.9.6) verwerkt een deep-link-overdracht vanuit de Linked Data Explorer: `/?dsoImport=dmn&dmnId=…&env=…&activityName=…&authority=…&activityUrn=…&fsRef=…`. Bij mount haalt hij de standalone DMN-XML op van de gedeelde backend (`GET /v1/dso/toepasbare-regels/{dmnId}/dmn`, met `?env=prod` alleen wanneer `env=prod`) en vult de DMN-tab (interactief — *niet* de bewaard-geïmporteerde modus), de Service-tab (vanuit de DSO-activiteit) en de Organisatie-tab (vanuit de opgeloste autoriteit) voor. Daarna worden de importparameters via `history.replaceState` verwijderd, en een `consumedRef`-guard voorkomt een dubbele aanroep onder StrictMode. Deployen/testen/publiceren verlopen via de bestaande DMNTab + PublishDialog-flow.

**Koppeling met kerneditor:** Laag. De hook roept alleen de bestaande `setDmnData`/`setService`/`setOrganization`-setters en de gedeelde berichtenbanner aan.

---

## Technologiestack

| Laag | Technologie |
|---|---|
| Frontend | React 19, Vite, Tailwind CSS, Lucide-iconen, `keycloak-js` (inloggen) |
| Statusbeheer | React hooks (`useEditorState`, `useArrayHandlers`), geen externe state-library |
| Build & lint | Vite, ESLint, Prettier, Husky (pre-commit/pre-push), lint-staged |
| Testen | Vitest 5, `@testing-library/react`, Playwright — 858 tests in 70 bestanden, alle geslaagd (gemeten op 12 november 2026), met 91,35% statements, 89,29% branches, 82,15% functions en 92,03% lines; plus 4 end-to-end-journeys ([Testing](testing.md)) |
| TTL-parsing | Eigen handgeschreven parser (geen RDF-library-afhankelijkheid) |
| DMN-parsing | Browser DOMParser (XML) |
| Externe API's | Keycloak (OIDC-inloggen, realm `ronl`) rechtstreeks vanuit de browser; TriplyDB, Operaton (Camunda-compatibele REST), de RONL SPARQL-vocabulaire en de DSO-API's alleen via de gedeelde backend |
| Backend-afhankelijkheid | Gedeelde Express-server (Linked Data Explorer-repo) voor CORS-geproxyde SPARQL-queries (de RONL-vocabulaire en de lijst gepubliceerde diensten), TriplyDB-publicatie als de ingelogde auteur, DMN-syntactische validatie (libxmljs2), het deployen en evalueren van DMN's, de SHACL-validatie vóór publicatie en de DSO-import |
| Hosting | Azure Static Web Apps (acc-branch → acceptatie, main → productie) |
| CI/CD | GitHub Actions: lint, tests en de productiebuild op de runner (Node 24.22.2 uit `.nvmrc`), geüpload naar Azure Static Web Apps met `skip_app_build`; bij elke pull request een verplichte lockfile-review en controle van registry-handtekeningen en provenance-attestaties; een dagelijkse dependency-audit, een driemaandelijkse dependency-review en een SBOM per release van elk productiepakket ([Deployment](deployment.md)) |

---

## Advies voor het DevOps-team

**Wat goed is:** De applicatie werkt, is in actief gebruik, heeft real-world TTL-voorbeelden voor 12+ organisaties en bestrijkt een complexe EU-standaard. De vocabulaireconfiguratie is goed gestructureerd, de validatielaag is solide en de TTL round-trip import/export is volwassen.

**Wat te beoordelen:**

- **Geen RDF-library.** TTL-parsing en -generatie zijn volledig handgeschreven (een parser van ~840 regels en een generator van ~1660 regels). Dit werkt maar is fragiel voor randgevallen. Evalueer of het introduceren van een lichtgewicht RDF/JS-library (bijv. N3.js) de onderhoudslast zou verlagen versus de kosten van migratie.

- **App.jsx-orkestratie.** De hoofd-`App.jsx` (1190 regels) is gedeeltelijk gemodulariseerd: datastatus leeft in `useEditorState`, array-CRUD-operaties in `useArrayHandlers`, TTL-importlogica in `importHandler.js` en TTL-generatie in `ttlGenerator.js`. Wat in App.jsx overblijft is UI-orkestratie (tabweergave, bericht-/statusbeheer), de publicatieworkflow (~230 regels: formuliervalidatie, TTL-generatie en één backend-aanroep, met de voortgangs- en resultaatstatussen) en code die status aan child componenten koppelt. Verdere extractiedoelen: de publicatie-handler zou een custom hook kunnen worden (`usePublishWorkflow`), en de tabnavigatie + berichtensysteem kan worden gescheiden van de data wiring.

- **Geautomatiseerde tests — opgelost.** Dit werd hier oorspronkelijk aangemerkt als *"geen geautomatiseerde tests voor TTL-output"*: het enige testbestand was een CRA-stub en validatie gebeurde handmatig via voorbeeldbestanden. In v2026.07.0 is een gefaseerde testsuite opgeleverd, inclusief de hier voorgestelde round-trip-dekking — een echte referentie-export inlezen, opnieuw genereren, opnieuw inlezen en vergelijken — en die legde direct twee werkelijke defecten bloot, waarvan er één sinds een hernoeming van een predicaat stilzwijgend gegevens liet wegvallen bij herimport. Alle acht fasen, P0–P7, zijn afgerond: bij v2026.09.4 telt de suite **751 tests in 61 bestanden**, plus drie Playwright-journeys tegen een draaiende stack, en voor elk bestand geldt een **80%-branchdrempel die de testrunner zelf afdwingt**. De UI-laag die hier ooit als ongetest werd genoemd, is gedekt: `DMNTab.jsx` 98,34% branches, `importHandler.js` 100% statements, `ttlGenerator.js` 94,89% en `parseTTL.enhanced.js` 94,50% statements. De resterende zwakte is smaller en specifiek: `App.jsx` haalt de branchdrempel met 81,48%, maar komt op **53,70% functions** — complete handlers die geen test aanroept, en die een branchdrempel niet ziet. Zie [Testing](testing.md).

- **localStorage voor configuratie — opgelost.** TriplyDB-credentials werden opgeslagen in localStorage. Sinds v2026.11.1 bewaart de browser alleen de datasetnaam; het token staat in de backend van de Linked Data Explorer, en een token dat een oudere versie bewaarde wordt bij de eerste keer laden verwijderd.

- **Gedeelde backend.** De Express-backend is onderdeel van de Linked Data Explorer-repo. De CPSV Editor is ervan afhankelijk voor CORS-geproxyde SPARQL-queries (de RONL-vocabulaire en, sinds v2026.11.0, de publieke diensten die in de dataset zijn gepubliceerd), TriplyDB-publicatie (als de ingelogde auteur, sinds v2026.11.1), DMN-syntactische validatie (de vijflaagse validator gebruikt libxmljs2, dat een Node.js-runtime vereist), het deployen en evalueren van DMN's op Operaton, de SHACL-validatie vóór publicatie en de DSO-import. Wijzigingen aan de backend beïnvloeden de CPSV Editor. Verduidelijk eigenaarschap, versiebeheer (API v1-header is reeds aanwezig) en deploykoppeling.

- **Separatiemogelijkheid.** De vier domeinen (editor, leverancier, publicatie, DMN) zijn losjes gekoppeld via de gedeelde editor-state. Een modulaire architectuur — of als aparte routes/lazy-loaded modules binnen de SPA (Single Page Application), of als onafhankelijke micro-frontends die een TTL-datacontract delen — zou de onderhoudbaarheid verbeteren en onafhankelijke release-cycli mogelijk maken. Een eerste stap in die richting is gezet: sinds v2026.09.2 worden de vier zwaarste tabbladen — `ChangelogTab`, `CPRMVTab`, `DMNTab` en `VendorTab` — lazy geladen, waardoor de entry-chunk van 685,71 naar 392,74 kB ging.

- **Create React App — opgelost.** Deze review raadde migratie weg van CRA aan, dat het React-team op 14 februari 2025 als verouderd aanmerkte en dat geen nieuwe functies, prestatieverbeteringen of actieve beveiligingsupdates meer ontvangt. Die migratie naar **Vite is uitgevoerd in v2026.09.1**, in vier afzonderlijk terug te draaien fasen, met de P0–P4-suite als regressievangnet, precies zoals hier voorgesteld. `npm audit` daalde van 52 naar 10 kwetsbaarheden en productiebuilds van ongeveer 30 seconden naar minder dan twee. Zie [Testing](testing.md).

---

## Authenticatie & Autorisatie voor Productiepublicatie

Sinds v2026.11.1 kent de editor inloggen. Een gebruiker logt in bij Keycloak-realm `ronl`, de login die de Linked Data Explorer en de RONL Business API delen — client `ttl-editor`, de authorization-code-flow met PKCE — via Entra van Flevoland of met een medewerkerswachtwoord. Inloggen is optioneel: bewerken, importeren, valideren en downloaden werken zonder. De twee acties die gedeelde gegevens wijzigen vereisen de realmrol `lde-author`:

| Integratiepunt | Authenticatiemechanisme bij v2026.11.1 |
|---|---|
| TriplyDB-publicatie | Het bearer-token van de auteur naar `POST /v1/triplydb/publish` van de Linked Data Explorer-backend, die `lde-author` vereist en publiceert met een eigen TriplyDB-account en -token. De browser bewaart alleen de datasetnaam |
| Operaton-deployment & testen | Deployen stuurt het token van de auteur naar `POST /v1/dmns/deploy`. Zonder token maakt de backend er een testdeploy van naar tenant `TestOnly`, die na 48 uur wordt verwijderd — aan op acceptatie, uit op productie. Evalueren is open. De backend bereikt de engine met een eigen, optionele `OPERATON_API_KEY` |
| Gedeelde Express-backend (LDE) | Controleert Keycloak-tokens. Elke route waarmee de editor gedeelde gegevens wijzigt vereist `lde-author` — publish, test-connection, update-service, list-graphs — behalve deploy, dat zonder token een testdeploy is waar die aan staat. De routes die de editor alleen leest blijven open: de SPARQL-proxy, DMN- en SHACL-validatie, evaluate, `publish-target` en `deploy/options` |
| Azure Static Web Apps | Deployment-tokens in GitHub Secrets (alleen CI/CD, geen gebruikersauth) |

Daarmee staat vast **wie** de gebruiker is en dat die de gedeelde bibliotheek mag wijzigen. Niet vast staat **namens wie** die publiceert: de rol is één vlag, dus elke auteur kan een beschrijving voor elke organisatie publiceren in elke dataset van het TriplyDB-account van de backend. Een publicatie die het mandaat van een bevoegd gezag draagt, heeft die koppeling nodig.

**Advies voor het DevOps-team:**

- **Backend-gemedieerde publicatie — gerealiseerd.** Sinds v2026.11.1 heeft de browser nooit een TriplyDB-token. De backend beheert de servicecredentials en accepteert een publicatie alleen van een auteur; daarmee is ook het token uit localStorage verdwenen ([ttl-editor#234](https://github.com/sgort/ttl-editor/issues/234)).

- **Autorisatie per organisatie — open.** Koppel een auteur aan de organisaties waarvoor die mag publiceren — een tokenclaim of een Keycloak-groep — en laat de backend een publicatie weigeren waarvan de `organization` daar niet bij hoort; beperk eventueel ook de datasets.

- **Operaton-credentials — deels opgelost.** De editor bevat geen Operaton-credential: deployen en evalueren worden geproxyd door de backend van de Linked Data Explorer, die de engine server-naar-server aanroept met een eigen, optionele `OPERATON_API_KEY`. Deployen vereist nu een auteur, of blijft beperkt tot tenant `TestOnly`; evalueren staat nog open voor elke aanroeper.

- **Backend-authenticatie — gerealiseerd voor schrijfacties.** De gedeelde backend controleert Keycloak-tokens tegen de sleutels van de realm en vereist `lde-author` op de routes die schrijven. De leesroutes blijven open.

- **Audittrail — een logregel, nog geen registratie.** Elke publicatiepoging schrijft één logregel: wie, welke organisatie en dienst, welke graaf en dataset, en de uitkomst (`published`, `published-with-warning` of `failed`). Dat is het grondmateriaal voor een audittrail; een opslag met een bewaartermijn, die een mandaat nodig heeft, bestaat nog niet.

- **Scope.** De enige schrijfactie die een niet-ingelogde gebruiker kan doen is de testdeploy, en alleen waar `TEST_DEPLOY_ENABLED` van de backend `true` is: op 12 november 2026 antwoordde acceptatie `enabled: true` en productie `enabled: false` (`GET /v1/dmns/deploy/options`).