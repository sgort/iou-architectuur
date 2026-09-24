---
component: Linked Data Explorer
---

# DSO Viewer APIs — Presentatie

!!! info "Documentatie in ontwikkeling"
    De Nederlandse vertaling van deze pagina is nog niet beschikbaar.
    Raadpleeg de <a href="/linked-data-explorer/features/dso-viewer-apis-deck/">Engelse versie</a> voor de huidige inhoud.
    De dia's zelf zijn Engelstalig.

Een technische presentatie van dertien dia's over de manier waarop de DSO Viewer in LDE met het
Digitaal Stelsel Omgevingswet communiceert: de proxylaag, de zes bovenliggende API's, welke
aanroepen elk tabblad doet, hoe het dossier van een activiteit wordt samengesteld, en de
openstaande punten. Zie [DSO-integratie](dso-integration.md) voor dezelfde stof in lopende
tekst.

!!! abstract "Downloaden"
    [DSO Viewer APIs Deck (PDF, 184 KB)](../../assets/downloads/dso-viewer-apis-deck.pdf)

    De presentatie is ontworpen op basis van `docs/dso-viewer-apis.md` in de
    `linked-data-explorer`-repository en als dia's geëxporteerd. Deze versie is die van
    **24 september 2026**, bij LDE v2026.09.6. Het is een momentopname, geen actuele weergave.

---

## Architectuur

<figure markdown style="width:100%; margin:0;">
  ![Dia 1 van 13, titeldia: DSO Viewer — API Reference, met onderaan drie kengetallen — 6 bovenliggende DSO-API's, 16 LDE-proxyendpoints, 2 omgevingen die met één header worden geschakeld](../../assets/slides/dso-viewer-apis/slide-01-title.png)
  <figcaption>Zes API's, zestien proxyendpoints, twee omgevingen</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Dia 2 van 13, het aanroeppad: DsoExplorer.tsx met vier tabbladen naar dsoService.ts naar de LDE-proxy op /v1/dso/* naar dso.service.ts naar het DSO, zes afzonderlijke publieke diensten — de frontend benadert het DSO nooit rechtstreeks](../../assets/slides/dso-viewer-apis/slide-02-call-path.png)
  <figcaption>Elk verzoek loopt via de LDE-backend</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Dia 3 van 13, wat de proxylaag oplevert: de API-sleutel blijft server-side, één header (X-Dso-Env) schakelt tussen pre-productie en productie, en HAL-antwoorden worden ongewijzigd doorgegeven binnen de success-data-envelop](../../assets/slides/dso-viewer-apis/slide-03-why-the-proxy.png)
  <figcaption>Sleutel, omgeving en payload — de drie redenen voor de proxy</figcaption>
</figure>

---

## De zes bovenliggende API's

<figure markdown style="width:100%; margin:0;">
  ![Dia 4 van 13, zes bovenliggende DSO-API's met hun paden, in een raster van drie bij twee: Stelselcatalogus, RTR Gegevens, Zoekinterface, Opvragen Werkzaamheden, Toepasbare Regels Uitvoeren Gegevens en Omgevingsdocumenten Presenteren (Ozon) voor regelingen zoeken, de annotatiegrafiek en documentonderdelen achter het activiteitendossier](../../assets/slides/dso-viewer-apis/slide-04-six-apis.png)
  <figcaption>De zes API's achter één <code>/v1/dso</code>-oppervlak — Ozon is de nieuwste</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Dia 5 van 13, vier tabbladen en zes API's: Concepts gebruikt API 1, Werkzaamheden gebruikt API 3 voor zoeken en suggesties en API 4 voor versiedetail, Activities gebruikt API 2 voor lijst en detail en API 5 voor het regelpaneel, en Quality Profile gebruikt API 2, 5 en 6 in één aanroep](../../assets/slides/dso-viewer-apis/slide-05-tabs-to-apis.png)
  <figcaption>Welk tabblad welke API aanroept — het vierde bereikt er drie in één aanroep</figcaption>
</figure>

---

## Het dossier en het kwaliteitsprofiel

<figure markdown style="width:100%; margin:0;">
  ![Dia 6 van 13, één aanroep, drie API's, twee assen, geen totaalcijfer: links haalt GET /v1/dso/activiteiten/{urn}/dossier gegevens op bij API 2, API 5 en API 6 en levert de keten — juridische bron, annotaties en besliscriteria. Rechts het kwaliteitsprofiel met twee assen, leesbaarheid en herleidbaarheid, met twee kanttekeningen: de twee scores worden nooit tot één cijfer gecombineerd, en een ontbrekende regelset wordt als ontbrekend gerapporteerd en niet als nul](../../assets/slides/dso-viewer-apis/slide-06-dossier-quality-profile.png)
  <figcaption>Eén aanroep verbindt drie API's; het profiel scoort op twee assen en houdt het daarbij</figcaption>
</figure>

---

## Activiteiten en de fan-out

<figure markdown style="width:100%; margin:0;">
  ![Dia 7 van 13, activiteiten laden in twee modi: op datum (per 20 gepagineerd) of op bestuurslaag en bevoegd gezag, waarbij één aanroep de volledige set ophaalt zodat het naamfilter client-side werkt — 342 gemeenten, 12 provincies, 21 waterschappen en 12 ministeries. De RTR levert alleen een code zoals GM0995, dus de keuzelijst heeft een eigen namenlijst nodig; de RTR wil dd-MM-jjjj en Ozon JJJJ-MM-dd, dus de backend converteert per API](../../assets/slides/dso-viewer-apis/slide-07-two-load-modes.png)
  <figcaption>Twee laadmodi: op datum, of de hele set van één bevoegd gezag</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Dia 8 van 13, een activiteit openen kost 1 + N verzoeken: de RTR levert onderliggende activiteiten als kale links zonder omschrijving, dus het paneel vraagt elke onderliggende activiteit apart op — 24 aanroepen voor Bedrijfsactiviteiten met 23 kinderen, nu vijf tegelijk, en het detail wordt vijf minuten gecachet zodat opnieuw openen binnen dat venster niets kost](../../assets/slides/dso-viewer-apis/slide-08-child-fan-out.png)
  <figcaption>De zwaarste interactie in de viewer — <code>1 + N</code> aanroepen, vijf tegelijk</figcaption>
</figure>

---

## Toepasbare regels

<figure markdown style="width:100%; margin:0;">
  ![Dia 9 van 13, van regelbeheerobject naar regelbestand: geselecteerde activiteit, regelBeheerObjecten, functioneleStructuurRef en identifier — en daarna één upstream-endpoint met drie acties (STTR downloaden, DMN extraheren, formulierscaffold genereren)](../../assets/slides/dso-viewer-apis/slide-09-rule-objects.png)
  <figcaption>Eén STTR-download, drie verschillende bewerkingen</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Dia 10 van 13, vijf correcties maken STTR-uitvoer uitvoerbaar: DMN 1.2 naar 1.3, ontbrekende id's, FEEL-veilige variabelenamen, typeRef op ongetypeerde uitvoer en camunda:historyTimeToLive per beslissing](../../assets/slides/dso-viewer-apis/slide-10-dmn-fixes.png)
  <figcaption>Wat <code>normalizeDmnForOperaton</code> aanpast</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Dia 11 van 13, een DMN publiceren is een overdracht en geen opslag: LDE heeft geen eigen DMN-opslag, dus de deep link naar de CPSV Editor draagt alleen identificatoren en de CPSV Editor haalt de XML zelf op bij dezelfde backend](../../assets/slides/dso-viewer-apis/slide-11-cpsv-handoff.png)
  <figcaption>De deep link draagt identificatoren; de CPSV Editor haalt de XML zelf op</figcaption>
</figure>

---

## Status en vervolg

<figure markdown style="width:100%; margin:0;">
  ![Dia 12 van 13, bekende losse eindjes: zoeken op geometrie is gebouwd maar niet ontsloten in de UI, geldigOp op begripzoeken heeft geen invoerveld, en de App Service-runtime is alleen op een hoofdversie vast te zetten, zodat die en de vastgelegde Node-versie met de hand en in de juiste volgorde moeten worden verzet](../../assets/slides/dso-viewer-apis/slide-12-loose-ends.png)
  <figcaption>Drie bekende gaten: twee onbereikbare functies en één operationeel risico</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Dia 13 van 13, vervolgstappen: kaart- en puntselectie, geldigheidsdatum in de UI, en een eigen timeout en defaults voor productie](../../assets/slides/dso-viewer-apis/slide-13-roadmap.png)
  <figcaption>Drie vervolgstappen — twee van de vijf uit augustus zijn in v2026.09.6 opgeleverd</figcaption>
</figure>

---

## Verwante pagina's

- [DSO-integratie](dso-integration.md)
- [API Specification](../reference/api-specification.md)
- [DSO Explorer-handleiding](../user-guide/dso-explorer.md)
- [DSO-integratie fasenplan](dso-integration-phase-plan.md)
