# DSO-integratie

!!! info "Documentatie in ontwikkeling"
    De Nederlandse vertaling van deze pagina is nog niet beschikbaar.
    Raadpleeg de <a href="/linked-data-explorer/features/dso-integration/">Engelse versie</a> voor de huidige inhoud.

## Overzicht

LDE integreert met het Digitaal Stelsel Omgevingswet (DSO) zodat ontwerpers BPMN-subprocessen direct kunnen koppelen aan de gezaghebbende DSO-activiteit, de Stelselcatalogus en het werkzaamhedenregister vanuit LDE kunnen doorbladeren, en verwijzingen kunnen verifiëren tegen actuele DSO-gegevens.

De presentatie [DSO Viewer APIs](dso-viewer-apis-deck.md) vat dit samen in twaalf dia's en is
als PDF te downloaden.

## De vijf DSO-API's achter de viewer

De frontend benadert het DSO nooit rechtstreeks. Elk verzoek loopt via de LDE-backend, die de
DSO-proxy op `/v1/dso` aanbiedt en de `x-api-key` server-side toevoegt. Vijf afzonderlijke
DSO-API's voeden de viewer: Stelselcatalogus (begrippen), RTR Gegevens (activiteiten),
Zoekinterface (zoeken naar werkzaamheden), Opvragen Werkzaamheden (versiedetail) en Toepasbare
Regels Uitvoeren Gegevens (regelmetadata en STTR-bestanden).

## DSO-omgevingsschakelaar

Een schakelaar in Instellingen kiest tussen de pre-productie- en productie-DSO-omgeving, onafhankelijk van de LDE-omgeving.

## Concepts-tabblad

Volledige tekst zoeken in de Stelselcatalogus.

## Works-tabblad

Werkzaamheden zoeken via de Zoekinterface, met autocomplete; het detailpaneel met
versiegeschiedenis komt van een andere API, Opvragen Werkzaamheden.

## Activities-tabblad

RTR-activiteiten doorbladeren in twee modi: op datum, of op bevoegd gezag via de OIN-presets
(Lelystad, Flevoland, Ede en Gelderland — de laatste twee sinds v2026.08.0). Zoeken op
geometrie bestaat wel in de backend, maar wordt door geen enkel scherm gebruikt.

### Onderliggende activiteiten — één klik, `1 + N` verzoeken

De RTR levert onderliggende activiteiten als kale links zonder omschrijving. Het detailpaneel
haalt daarom elke onderliggende activiteit apart op — parallel, één verzoek per kind, bovenop
het verzoek voor de activiteit zelf. Zonder cache en zonder limiet op het aantal gelijktijdige
verzoeken.

## Toepasbare regels → LDE-assets (Fase 4)

De toepasbare regels van een activiteit exporteren naar LDE-assets — een deploy-klare DMN of een form-js-scaffold — of doorgeven aan de CPSV Editor om te publiceren (v1.9.3–v1.9.5).

## BPMN-subproces koppelen aan een DSO-activiteit

Het footerpaneel van de BPMN Modeler bevat een DSO Activity-selector waarmee een URN wordt geverifieerd tegen de live DSO RTR en wordt opgeslagen als `ronl:dsoActiviteitUrn` op het BPMN-procesetlement.

## Verwante pagina's

- [DSO Explorer-gebruikershandleiding](../user-guide/dso-explorer.md)
- [DSO-integratie fasenplan](dso-integration-phase-plan.md)