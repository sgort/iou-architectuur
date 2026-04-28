# Meertaligheid

!!! info "Documentatie in ontwikkeling"
    Deze pagina is nog niet vertaald. Raadpleeg voorlopig de [Engelse versie](../../features/multilingualism.md) voor de volledige inhoud.

    **Status:** Engelse versie compleet — Nederlandse vertaling staat gepland.

## Overzicht

LDE ondersteunt het taggen van ontwerpartefacten (BPMN, formulieren, documenttemplates) met een taal en een organisatie. Daardoor kunnen bundels één keer worden ontworpen en in meerdere talen worden uitgerold zonder de onderliggende logica te splitsen.

## Wat kan worden getagd

BPMN-processen, Camunda-formulieren en documenttemplates dragen een ISO 639-1-taal (en, nl, de) en een organisatiesleutel. DMN's blijven taalonafhankelijk — variabele-sleutels blijven stabiel Engels.

## Toolbar in lijstpanelen

Elke editor heeft dezelfde toolbar: zoekveld, taalfilter en match-teller.

## Inklapbare organisatiegroepen

Artefacten zijn gegroepeerd onder organisatie-headers (FLEVOLAND, TOESLAGEN, BZK, …). Subprocessen volgen de organisatie van hun shell.

## Footerpaneel in editor

Het footerpaneel onder de lijst toont selectors voor Language, Organization en (alleen BPMN) RoPA en DSO Activity.

## Opslaan-bij-Save-model

Wijzigingen in het footerpaneel worden pas opgeslagen wanneer u op Save klikt. Bij het opslaan van een shell worden taal en organisatie atomair gepropageerd naar alle gekoppelde subprocessen.

## Bestandsnaam-inferentie bij import

Bestandsnamen als `capacity-claim-intake.nl.form` worden bij import automatisch getagd.

## Taalconsistentiecontrole bij deploy

De deploy-dialoog toont een amberkleurige waarschuwing als een bundel meerdere talen mengt.

## HR-capacity Nederlandse referentiebundel

`Beheer capaciteitsclaim — proces (Voorbeeld, NL)` — 1 BPMN, 8 formulieren, 2 documenten, allemaal getagd `language=nl`, `organization=flevoland`.

## Bekende beperking — form-js focusverlies

De form-js properties-panel verliest focus bij een korte pauze tijdens typen — upstream form-js issue #86, wontfix. Workaround: bewerk de `.form` JSON in een code-editor en importeer opnieuw.

## Verwante pagina's

- [Meertaligheid-gebruikershandleiding](../user-guide/multilingualism.md)
- [BPMN Modeler — taal en organisatie](bpmn-modeler.md#taal-en-organisatie)
- [Form Editor — taal en organisatie](form-editor.md#taal-en-organisatie)
- [Document Composer — taal en organisatie](document-composer.md#taal-en-organisatie)