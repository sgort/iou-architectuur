# Dossierbeheer — Testhandleiding

**Provincie Flevoland · versie 3.8.1**

---

## Inleiding

### Wat is de PA-Cockpit?

De PA-Cockpit is de werkomgeving voor Public Affairs-medewerkers van de provincie. Het draait om het **dossier**: een bundel van alles rondom één politiek-inhoudelijk thema — het Flevolands Kompas (prioriteitsscore), stakeholders, het lobby- en communicatieritme, frames en tegenframes, en een tijdlijn van gebeurtenissen. De cockpit verzamelt daarnaast automatisch **signalen** — relevante Kamerstukken, publicaties en berichten — via een **curatiepijplijn** die deze aan het juiste dossier koppelt. Signalen en de curatiepijplijn zijn **geen onderdeel van deze testronde**; ze worden hier alleen genoemd zodat de rol van een dossier duidelijk is: het is het anker waar al het andere aan gekoppeld wordt.

### Wat is Dossierbeheer?

Tot voor kort werden dossiers nog niet in de cockpit zelf beheerd. **Dossierbeheer** is het nieuwe scherm waarmee het kernteam dossiers **aanmaakt, bewerkt, publiceert, archiveert en verwijdert** — zonder tussenkomst van een ontwikkelaar. Het is te vinden onder **Beheer → Strategisch kompas → Dossierbeheer**.

Een dossier dat hier gepubliceerd wordt, verschijnt direct in de rest van de cockpit (Dossiers, Vandaag, Monitoring, Voortgang). Een dossier dat gearchiveerd of nog niet gepubliceerd is, blijft daar juist verborgen. Dossierbeheer is dus de bron — en deze testronde controleert of die bron zich betrouwbaar gedraagt.

### Doel van deze testronde

Deze handleiding test **alle functies** van Dossierbeheer: elke knop, elke actie, elke validatie. Het gaat **niet** om vormgeving, tekstkeuzes of gebruiksgemak — daar is later een aparte ronde voor. Meld een bevinding dus alleen als:

- een actie niet doet wat er beloofd wordt (of niets doet, of iets anders doet),
- een fout optreedt zonder duidelijke melding,
- de applicatie vastloopt, data verliest, of een verkeerde status laat zien,
- een rol méér of juist minder kan dan de tabel hieronder aangeeft.

Vind je de indeling onhandig, een knop onduidelijk benoemd, of een kleur verwarrend? Noteer het gerust apart, maar dat is voor nu geen testblokkade — dat werk komt in een volgende ronde.

---

## Voorbereiding

- Log in op de PA-Cockpit als **`test-pa-flevoland`** (wachtwoord `test123`). Deze gebruiker is een volwaardige **Beheerder** — daarmee kun je alle functies in deze handleiding uitvoeren.
- Rollenoverzicht, zodat je weet wat elke rol hoort te mogen (test dit gericht in [Testblok 7](#testblok-7-rolafhankelijke-functies)):

  | Rol           | Aanmaken | Bewerken | Sjablonen | Publiceren | Archiveren | Verwijderen |
  | ------------- | :------: | :------: | :-------: | :--------: | :--------: | :---------: |
  | **Auteur**    |    ✓     |    ✓     |           |            |            |             |
  | **Redacteur** |    ✓     |    ✓     |     ✓     |     ✓      |            |             |
  | **Beheerder** |    ✓     |    ✓     |     ✓     |     ✓      |     ✓      |      ✓      |

- Boven in Dossierbeheer zie je zes gekleurde chips die tonen welke van deze zes acties jouw rol toestaat. Klopt dat met de tabel? Dat is zelf ook een testpunt (zie Testblok 7).

---

## Mock versus live — wat je moet weten

Dossierbeheer kan op twee manieren data tonen, **wisselbaar tijdens het testen, zonder herladen van de applicatie**:

- **Mock-modus** — alles draait lokaal in de browser met voorbeelddossiers. Niets wordt bewaard; een pagina-herlaad zet alles terug naar de startset. Geschikt om de schermen zonder risico te verkennen.
- **Live-modus** — elke actie raakt echt de database. Wijzigingen blijven bestaan na herladen en zijn zichtbaar voor collega's.

Een gekleurde banner bovenaan het scherm toont de actieve modus en heeft een knop om te wisselen (**"Zet vlag om naar live →"** / **"↩ Terug naar mock"**). **Voor deze testronde is live-modus vereist** — alleen dan test je de echte opslag, versiegeschiedenis en publicatiestatus. Zet de vlag dus als eerste om.

> **Testblok 0 — De vlag zelf**
>
> | # | Actie | Verwacht resultaat |
> | - | ----- | ------------------- |
> | 0.1 | Open Dossierbeheer, controleer de banner | Toont de huidige modus (amber = mock, groen = live) |
> | 0.2 | Klik "Zet vlag om naar live →" | Banner wordt groen; lijst ververst met dossiers uit de database |
> | 0.3 | Navigeer weg (bijv. naar Dossiers) en terug | Live-modus blijft actief — de keuze overleeft navigatie |
> | 0.4 | Herlaad de pagina (F5) | Live-modus blijft actief — de keuze overleeft een herlaad |

---

## Testblok 1 — Overzicht

Open **Beheer → Dossierbeheer**.

| # | Actie | Verwacht resultaat |
| - | ----- | ------------------- |
| 1.1 | Bekijk de rolbalk bovenaan | Toont **Beheerder** met alle zes capability-chips groen, en "Keycloak: pa-admin" |
| 1.2 | Bekijk de tellers | Aantallen actief / sluimerend / gearchiveerd / gepubliceerd kloppen met wat je in de lijst eronder telt |
| 1.3 | Bekijk de groepering | Dossiers zijn gegroepeerd onder **Actief**, **Sluimerend** en **Gearchiveerd** — elk dossier staat in precies één groep, passend bij zijn status |
| 1.4 | Bekijk een gearchiveerd dossier in de lijst | Herkenbaar gemarkeerd (bijv. gestippelde kaart) met archiveringsgegevens zichtbaar |

---

## Testblok 2 — Navigatie

| # | Actie | Verwacht resultaat |
| - | ----- | ------------------- |
| 2.1 | Klik **Nieuw dossier** in de zijbalk | Opent het sjablonenoverzicht |
| 2.2 | Klik daarna **Dossierbeheer** in de zijbalk | Keert terug naar het overzicht — de lijst blijft correct |
| 2.3 | Herhaal een paar keer heen-en-weer | Beide schermen wisselen steeds correct, geen vastlopers, geen dubbele content, geen verdwenen dossiers |

---

## Testblok 3 — Een dossier aanmaken

| # | Actie | Verwacht resultaat |
| - | ----- | ------------------- |
| 3.1 | Klik **+ Nieuw dossier** → kies een sjabloon → **Doorgaan met dit sjabloon** | Opent de dossier-editor met het sjabloon als startpunt |
| 3.2 | Laat **Naam** en **Onderwerp** leeg | De opslaanknop is uitgeschakeld |
| 3.3 | Vul een Naam van 1–2 tekens in | Opslaanknop blijft uitgeschakeld (minimaal 3 tekens vereist) |
| 3.4 | Vul een geldige Naam (≥3 tekens) in, laat Onderwerp leeg | Opslaanknop blijft uitgeschakeld |
| 3.5 | Vul ook het Onderwerp in | Opslaanknop wordt actief |
| 3.6 | Typ in het Naam-veld | De URL-preview (`/pa/dossiers/{slug}`) werkt live mee met wat je typt |
| 3.7 | Klik de Kompas-criteria (0/1/2 per criterium) | Totaalscore en prioriteitsband werken direct bij elke klik |
| 3.8 | Open de Markdown-editor, wissel tussen **Schrijven / Split / Voorbeeld** | Alle drie tonen consistente content; Voorbeeld toont opgemaakte tekst met een "veilig gerenderd"-indicator |
| 3.9 | Selecteer tekst en gebruik een opmaakknop in de toolbar (bijv. vet) | De opmaak wordt correct om de selectie toegepast |
| 3.10 | Zet de cursor in een tekstveld, klik een snippet aan | Snippet-tekst verschijnt op de cursorpositie; datum-/gebruikersvariabelen zijn ingevuld met echte waarden, niet met placeholders |
| 3.11 | Klik **Dossier aanmaken** | Keert terug naar het overzicht; het nieuwe dossier staat bovenaan in de juiste groep |
| 3.12 | Herlaad de pagina | Het nieuwe dossier is nog steeds aanwezig (bevestigt opslag in live-modus) |

---

## Testblok 4 — Bewerken en versiebeheer

| # | Actie | Verwacht resultaat |
| - | ----- | ------------------- |
| 4.1 | Open een bestaand dossier via **Bewerken** | Editor opent met de huidige gegevens correct vooringevuld |
| 4.2 | Wijzig een veld, klik **Wijzigingen opslaan** | Terug naar overzicht; wijziging is zichtbaar bij opnieuw openen |
| 4.3 | Bekijk de Versiegeschiedenis | Toont een nieuwe versie-regel voor de zojuist opgeslagen wijziging |
| 4.4 | Wijzig nogmaals en sla nogmaals op | Versienummer loopt verder op (niet terug naar 1, niet overschreven) |

---

## Testblok 5 — Publiceren

| # | Actie | Verwacht resultaat |
| - | ----- | ------------------- |
| 5.1 | Open een concept-dossier, klik **Opslaan & publiceren** | Dossier krijgt status "gepubliceerd" |
| 5.2 | Ga naar **Dossiers** in de topnavigatie | Het zojuist gepubliceerde dossier is daar nu zichtbaar |
| 5.3 | Zet een gepubliceerd dossier terug (indien de functie dit toestaat) of maak een nieuw concept | Een dossier dat **niet** gepubliceerd is, verschijnt **niet** onder Dossiers |

> Publiceren is een Redacteur/Beheerder-functie — test het rol-effect in Testblok 7.

---

## Testblok 6 — Archiveren (Archiefwet)

| # | Actie | Verwacht resultaat |
| - | ----- | ------------------- |
| 6.1 | Open een actief dossier → **Archiveren (Archiefwet)…** | Vraagt om classificatie, bewaartermijn en een reden |
| 6.2 | Probeer te bevestigen zonder reden in te vullen | Actie wordt geblokkeerd totdat een reden is ingevuld |
| 6.3 | Vul alles in, bevestig | Dossier verdwijnt uit Actief/Sluimerend en verschijnt onder **Gearchiveerd** |
| 6.4 | Open het gearchiveerde dossier via **Bekijken** | Alle velden zijn **alleen-lezen** — geen bewerk- of publiceerknoppen aanwezig |
| 6.5 | Controleer of het dossier nog zichtbaar is onder **Dossiers** in de topnavigatie | Niet zichtbaar — archiveren verwijdert het dossier uit de actieve cockpit-weergave |
| 6.6 | Klik **Herstellen** (op de rij) of **Dearchiveren (herstellen)…** (in de editor) | Dossier keert terug als **concept**: status actief, maar **nog niet gepubliceerd** |
| 6.7 | Controleer of het herstelde dossier zichtbaar is onder Dossiers | Niet zichtbaar totdat je het opnieuw publiceert (zie Testblok 5) |
| 6.8 | Publiceer het herstelde dossier opnieuw | Verschijnt weer onder Dossiers |

---

## Testblok 7 — Rolafhankelijke functies

Log — indien mogelijk met hulp van een collega-tester of een tweede testaccount — in met een gebruiker met **minder rechten** dan `test-pa-flevoland` (bijvoorbeeld alleen Auteur- of Redacteur-rechten) en herhaal de relevante acties.

| # | Actie | Verwacht resultaat |
| - | ----- | ------------------- |
| 7.1 | Log in als Auteur-only, open Dossierbeheer | Capability-chips tonen alleen Aanmaken/Bewerken als actief; overige chips grijs/uit |
| 7.2 | Probeer als Auteur te publiceren, archiveren of verwijderen | Knoppen zijn niet klikbaar of tonen een duidelijke melding dat de rol ontbreekt — **geen** stille mislukking |
| 7.3 | Log in als Redacteur, herhaal publiceren | Publiceren werkt (Redacteur mag dit) |
| 7.4 | Log in als Redacteur, probeer te archiveren of verwijderen | Geblokkeerd — dit zijn Beheerder-only functies |
| 7.5 | Vergelijk elk resultaat met de rollentabel in de Voorbereiding | Alle rollen gedragen zich exact zoals de tabel voorschrijft — niet meer, niet minder |

---

## Testblok 8 — Verwijderen

⚠️ Test dit met een dossier dat je zelf hebt aangemaakt in Testblok 3 — niet met een van de bestaande voorbeelddossiers.

| # | Actie | Verwacht resultaat |
| - | ----- | ------------------- |
| 8.1 | Open het testdossier → **Definitief verwijderen…** | Vraagt om de exacte dossiernaam ter bevestiging |
| 8.2 | Typ een afwijkende of onvolledige naam | Bevestigingsknop blijft uitgeschakeld |
| 8.3 | Typ de exacte naam | Bevestigingsknop wordt actief |
| 8.4 | Bevestig | Dossier is direct weg uit alle groepen in het overzicht |
| 8.5 | Herlaad de pagina | Dossier blijft weg (bevestigt permanente verwijdering, geen "zombie" na refresh) |

---

## Testblok 9 — Doorwerking naar de rest van de cockpit

Dit testblok controleert of Dossierbeheer daadwerkelijk de bron is voor de rest van de applicatie.

| # | Actie | Verwacht resultaat |
| - | ----- | ------------------- |
| 9.1 | Publiceer een nieuw dossier (Testblok 3 + 5) | Verschijnt op **Vandaag**, **Dossiers**, **Voortgang** |
| 9.2 | Archiveer een gepubliceerd dossier (Testblok 6) | Verdwijnt direct van diezelfde schermen |
| 9.3 | Maak een concept aan maar publiceer niet | Verschijnt **nergens** buiten Dossierbeheer zelf |

---

## Terugzetten naar mock (optioneel, na afloop)

Klik **"↩ Terug naar mock"** op de banner om terug te schakelen naar de veilige oefenmodus. Dit heeft geen effect op wat je in live-modus al hebt opgeslagen.

---

## Buiten scope van deze testronde

- **Signalen en de curatiepijplijn** (Monitoring-scherm) — apart testtraject
- **Vormgeving, teksten, kleurgebruik** — aparte UX-ronde, later
- **Prestaties/snelheid** onder zware belasting

---

## Bevindingen melden

Gebruik **Feedback geven** in de **Beheer**-sectie van de topnavigatie. Vermeld het testblok- en stapnummer (bijv. "6.4") zodat de bevinding snel te herleiden is.
