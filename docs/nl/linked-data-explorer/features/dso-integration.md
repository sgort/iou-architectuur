# DSO-integratie

!!! info "Documentatie in ontwikkeling"
    De Nederlandse vertaling van deze pagina is nog niet beschikbaar.
    Raadpleeg de <a href="/linked-data-explorer/features/dso-integration/">Engelse versie</a> voor de huidige inhoud.

## Overzicht

LDE integreert met het Digitaal Stelsel Omgevingswet (DSO) zodat ontwerpers BPMN-subprocessen direct kunnen koppelen aan de gezaghebbende DSO-activiteit, de Stelselcatalogus en het werkzaamhedenregister vanuit LDE kunnen doorbladeren, en verwijzingen kunnen verifiëren tegen actuele DSO-gegevens.

## DSO-omgevingsschakelaar

Een schakelaar in Instellingen kiest tussen de pre-productie- en productie-DSO-omgeving, onafhankelijk van de LDE-omgeving.

## Concepts-tabblad

Volledige tekst zoeken in de Stelselcatalogus.

## Works-tabblad

Werkzaamheden zoeken via de Zoekinterface, met autocomplete en versiegeschiedenis per werkzaamheid.

## Activities-tabblad

RTR-activiteiten doorbladeren, gefilterd via OIN-presets (Lelystad, Flevoland) en datum.

## Toepasbare regels → LDE-assets (Fase 4)

De toepasbare regels van een activiteit exporteren naar LDE-assets — een deploy-klare DMN of een form-js-scaffold — of doorgeven aan de CPSV Editor om te publiceren (v1.9.3–v1.9.5).

## BPMN-subproces koppelen aan een DSO-activiteit

Het footerpaneel van de BPMN Modeler bevat een DSO Activity-selector waarmee een URN wordt geverifieerd tegen de live DSO RTR en wordt opgeslagen als `ronl:dsoActiviteitUrn` op het BPMN-procesetlement.

## Verwante pagina's

- [DSO Explorer-gebruikershandleiding](../user-guide/dso-explorer.md)
- [DSO-integratie fasenplan](dso-integration-phase-plan.md)