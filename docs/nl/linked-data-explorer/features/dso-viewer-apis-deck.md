---
component: Linked Data Explorer
---

# DSO Viewer APIs — Presentatie

!!! info "Documentatie in ontwikkeling"
    De Nederlandse vertaling van deze pagina is nog niet beschikbaar.
    Raadpleeg de <a href="/linked-data-explorer/features/dso-viewer-apis-deck/">Engelse versie</a> voor de huidige inhoud.
    De dia's zelf zijn Engelstalig.

Een technische presentatie van twaalf dia's over de manier waarop de DSO Viewer in LDE met het
Digitaal Stelsel Omgevingswet communiceert: de proxylaag, de vijf bovenliggende API's, welke
aanroepen elk tabblad doet, en de openstaande punten. Zie
[DSO-integratie](dso-integration.md) voor dezelfde stof in lopende tekst.

!!! abstract "Downloaden"
    [DSO Viewer APIs Deck (PDF, 121 KB)](../../assets/downloads/dso-viewer-apis-deck.pdf)

    De presentatie wordt gegenereerd in de `linked-data-explorer`-repository (`docs/`) en hier
    gekopieerd. Deze versie is die van **24 augustus 2026**, bij LDE v2026.08.3.

---

## Architectuur

<figure markdown style="width:100%; margin:0;">
  ![Dia 1 van 12, titeldia: DSO Viewer — API Reference, met onderaan drie kengetallen — 5 bovenliggende DSO-API's, 12 LDE-proxyendpoints, 2 omgevingen die met één header worden geschakeld](../../assets/slides/dso-viewer-apis/slide-01-title.png)
  <figcaption>Vijf API's, twaalf proxyendpoints, twee omgevingen</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Dia 2 van 12, het aanroeppad: DsoExplorer.tsx naar dsoService.ts naar de LDE-proxy op /v1/dso/* naar dso.service.ts naar het DSO — de frontend benadert het DSO nooit rechtstreeks](../../assets/slides/dso-viewer-apis/slide-02-call-path.png)
  <figcaption>Elk verzoek loopt via de LDE-backend</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Dia 3 van 12, wat de proxylaag oplevert: de API-sleutel blijft server-side, één header (X-Dso-Env) schakelt tussen pre-productie en productie, en HAL-antwoorden worden ongewijzigd doorgegeven binnen de success-data-envelop](../../assets/slides/dso-viewer-apis/slide-03-why-the-proxy.png)
  <figcaption>Sleutel, omgeving en payload — de drie redenen voor de proxy</figcaption>
</figure>

---

## De vijf bovenliggende API's

<figure markdown style="width:100%; margin:0;">
  ![Dia 4 van 12, vijf bovenliggende DSO-API's met hun paden: Stelselcatalogus, RTR Gegevens, Zoekinterface, Opvragen Werkzaamheden en Toepasbare Regels Uitvoeren Gegevens](../../assets/slides/dso-viewer-apis/slide-04-five-apis.png)
  <figcaption>De vijf API's achter één <code>/v1/dso</code>-oppervlak</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Dia 5 van 12, drie tabbladen en vijf API's: Concepts gebruikt API 1, Werkzaamheden gebruikt API 3 voor zoeken en suggesties en API 4 voor versiedetail, Activities gebruikt API 2 voor lijst en detail en API 5 voor het regelpaneel](../../assets/slides/dso-viewer-apis/slide-05-tabs-to-apis.png)
  <figcaption>Welk tabblad welke API aanroept — Werkzaamheden gebruikt er twee</figcaption>
</figure>

---

## Activiteiten en de fan-out

<figure markdown style="width:100%; margin:0;">
  ![Dia 6 van 12, activiteiten laden in twee modi: op datum (per 20 gepagineerd) of op bevoegd gezag via de OIN-presets, waarbij één aanroep met pageSize=200 de volledige set ophaalt zodat het naamfilter client-side werkt](../../assets/slides/dso-viewer-apis/slide-06-two-load-modes.png)
  <figcaption>Twee laadmodi: op datum, of de hele set van één bevoegd gezag</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Dia 7 van 12, een activiteit openen kost 1 + N verzoeken: de RTR levert onderliggende activiteiten als kale links zonder omschrijving, dus het paneel vraagt elke onderliggende activiteit apart op — 24 aanroepen voor Bedrijfsactiviteiten met 23 kinderen, zonder cache en zonder limiet op gelijktijdigheid](../../assets/slides/dso-viewer-apis/slide-07-child-fan-out.png)
  <figcaption>De zwaarste interactie in de viewer — <code>1 + N</code> aanroepen, alleen voor namen</figcaption>
</figure>

---

## Toepasbare regels

<figure markdown style="width:100%; margin:0;">
  ![Dia 8 van 12, van regelbeheerobject naar regelbestand: geselecteerde activiteit, regelBeheerObjecten, functioneleStructuurRef en identifier — en daarna één upstream-endpoint met drie acties (STTR downloaden, DMN extraheren, formulierscaffold genereren)](../../assets/slides/dso-viewer-apis/slide-08-rule-objects.png)
  <figcaption>Eén STTR-download, drie verschillende bewerkingen</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Dia 9 van 12, vijf correcties maken STTR-uitvoer uitvoerbaar: DMN 1.2 naar 1.3, ontbrekende id's, FEEL-veilige variabelenamen, typeRef op ongetypeerde uitvoer en camunda:historyTimeToLive per beslissing](../../assets/slides/dso-viewer-apis/slide-09-dmn-fixes.png)
  <figcaption>Wat <code>normalizeDmnForOperaton</code> aanpast</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Dia 10 van 12, een DMN publiceren is een overdracht en geen opslag: LDE heeft geen eigen DMN-opslag, dus de deep link naar de CPSV Editor draagt alleen identificatoren en de CPSV Editor haalt de XML zelf op bij dezelfde backend](../../assets/slides/dso-viewer-apis/slide-10-cpsv-handoff.png)
  <figcaption>De deep link draagt identificatoren; de CPSV Editor haalt de XML zelf op</figcaption>
</figure>

---

## Status en vervolg

<figure markdown style="width:100%; margin:0;">
  ![Dia 11 van 12, bekende losse eindjes: zoeken op geometrie is gebouwd maar niet ontsloten in de UI, geldigOp op begripzoeken heeft geen invoerveld, en de fan-out heeft geen cache](../../assets/slides/dso-viewer-apis/slide-11-loose-ends.png)
  <figcaption>Drie bekende gaten: twee onbereikbare functies en één prestatierisico</figcaption>
</figure>

<figure markdown style="width:100%; margin:0;">
  ![Dia 12 van 12, vervolgstappen: kaart- en puntselectie, de fan-out memoïseren, meer bevoegde gezagen dan de vier presets, geldigheidsdatum in de UI, en een eigen timeout en defaults voor productie](../../assets/slides/dso-viewer-apis/slide-12-roadmap.png)
  <figcaption>Vijf vervolgstappen, in de volgorde die de presentatie voorstelt</figcaption>
</figure>

---

## Verwante pagina's

- [DSO-integratie](dso-integration.md)
- [API-referentie — DSO Integration](../reference/api-reference.md#dso-integration)
- [DSO Explorer-handleiding](../user-guide/dso-explorer.md)
- [DSO-integratie fasenplan](dso-integration-phase-plan.md)
