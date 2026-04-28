# DSO-integratie

!!! info "Documentatie in ontwikkeling"
    Deze pagina is nog niet vertaald. Raadpleeg voorlopig de [Engelse versie](../../features/dso-integration.md) voor de volledige inhoud.

    **Status:** Engelse versie compleet — Nederlandse vertaling staat gepland.

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

## BPMN-subproces koppelen aan een DSO-activiteit

Het footerpaneel van de BPMN Modeler bevat een DSO Activity-selector waarmee een URN wordt geverifieerd tegen de live DSO RTR en wordt opgeslagen als `ronl:dsoActiviteitUrn` op het BPMN-procesetlement.

## Verwante pagina's

- [DSO Explorer-gebruikershandleiding](../user-guide/dso-explorer.md)
- [DSO-integratie fasenplan](dso-integration-phase-plan.md)