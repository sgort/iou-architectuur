---
scope: cross-cutting
---

# CI-posture over de repositories — presentatie

!!! info "Documentatie in ontwikkeling"
    De Nederlandse vertaling van deze pagina is nog niet beschikbaar.
    Raadpleeg de <a href="/contributing/ci-posture-deck/">Engelse versie</a> voor de huidige inhoud.
    De dia's zelf zijn Engelstalig.

---

**Status:** Concept  
**Engelstalige bron:** `contributing/ci-posture-deck.md`

---

Een presentatie van vijf dia's, *CPSV-Editor & Linked Data Explorer — Software Delivery
Decision*, opnieuw geëxporteerd op **12 september 2026**. De vraag erin is er één: goedkeuring
voor een **initiële schoonmaak** van beide applicaties en het inrichten van een standaard
leveringspijplijn daarachter, terwijl het huidige `acc`-en-`main`-spoor in gebruik blijft voor
rapid prototyping.

!!! abstract "Downloaden"
    [CI Posture Across Repos — presentatie (PDF, 138 KB)](../../assets/downloads/ci-posture-across-repos-deck.pdf)

!!! note "Deze versie telt vijf controles, de vorige vier"
    De vijfde is een **spiegelcontrole** die bij elke release draait en niet in CI kán
    draaien: de `gitlab`-remote staat in `.git/config` en geen enkel bestand in de
    repository noemt de host, dus een runner heeft die remote niet. De controle duwt zelf
    nooit — zij toont het commando en stopt.

---

## Twee sporen

<figure markdown style="width:100%; margin:0;">
  ![Dia 1 van 5: bovenin de band RAPID PROTOTYPING — accepteren op acc, promoveren naar main, elke merge bewaakt door GitHub Actions, waar vijf controles draaien: vier in CI en een vijfde bij elke release. Daaronder de nog te bouwen band STANDARD SOFTWARE DELIVERY met Wasstraat, CI/CD-pijplijn (build, test, deploy) en een productieklare oplevering; de initiële schoonmaak links is de gevraagde beslissing](../../assets/slides/ci-posture/slide-1-two-tracks.png)
  <figcaption>Alles gaat vandaag via het prototypingspoor; het spoor daaronder moet nog gebouwd worden</figcaption>
</figure>

---

## Wat GitHub Actions al bewaakt

<figure markdown style="width:100%; margin:0;">
  ![Dia 2 van 5: vier controles die in CI draaien — 01 build-herkomst ("welke build zie ik?"), 02 pin-waarheid ("klopt de pin?"), 03 code- en dependencyscan ("draait er iets met bekende kwetsbaarheden?") en 04 de dekkingsdrempel ("is deze code echt getest?", 80% van de beslispaden per bestand) — plus 05, de spiegelcontrole die géén CI-gate is. Onderaan een tabel per applicatie: verplichte checks op acc zijn audit en scan in beide, op main alleen bij de Explorer; de CPSV Editor heeft daar bewust geen verplichte checks](../../assets/slides/ci-posture/slide-2-what-ci-gates.png)
  <figcaption>De vijf controles als vragen, en waar elke repository ze verplicht stelt</figcaption>
</figure>

Elke controle heeft een eigen pagina — zie [Controles in één oogopslag](controls.md) voor het
overzicht, en [Build Provenance](build-provenance.md),
[Supply-Chain Pinning](supply-chain.md) en de [Coverage Floor](coverage-floor.md) voor de
mechaniek.

---

## Acht punten, alle gesloten

<figure markdown style="width:100%; margin:0;">
  ![Dia 3 van 5: acht afgevinkte punten uit de CI-posture-review, alle gesloten — laatste dekkingsuitzondering opgeheven, het pinregister loopt mee met de bumps, geen marge meer op de dekkingsdrempel, opmaak gecontroleerd op de gedeelde branch, productie-build-id's één keer met het oog bevestigd, code- en dependencyscanning blokkeert nu, de transitieve dependencyboom wordt eindelijk ververst, en de tweede kopie wordt bij elke release gecontroleerd](../../assets/slides/ci-posture/slide-3-what-was-delivered.png)
  <figcaption>Een opleverrapport in plaats van een backlog</figcaption>
</figure>

---

## De vraag

<figure markdown style="width:100%; margin:0;">
  ![Dia 4 van 5: de vraag — start de initiële schoonmaak van beide applicaties en richt de standaard leveringspijplijn in. Drie kolommen: wat het oplevert, wat het kost en wat het brengt. De kostenkolom noemt dat prototypewerk dan via een merge van zes maanden bij een deployment komt in plaats van op de dag dat het geschreven wordt](../../assets/slides/ci-posture/slide-4-the-decision.png)
  <figcaption>Wat het oplevert, wat het kost en wat het brengt — de middelste kolom is de eerlijke</figcaption>
</figure>

---

## Wat er tussen versies veranderde

<figure markdown style="width:100%; margin:0;">
  ![Dia 5 van 5: zeven wijzigingen ten opzichte van de vorige versie — van vier naar vijf controles, van zes naar acht opgeleverde punten, de scanbevindingen van de CPSV Editor naar nul nadat de dependencyboom voor het eerst werd ververst, de spiegel die nu bij elke release wordt gecontroleerd, waar de controles verplicht zijn, de verificatie van 12 september 2026, en de scope: een derde applicatie, de RONL Business API, draait nu dezelfde vijf controles maar valt buiten deze beslissing](../../assets/slides/ci-posture/slide-5-changelog.png)
  <figcaption>De presentatie draagt haar eigen correcties in plaats van de eerdere formulering stil te vervangen</figcaption>
</figure>

---

## Verwante pagina's

- [Controles in één oogopslag](controls.md)
- [Build Provenance](build-provenance.md)
- [Supply-Chain Pinning](supply-chain.md)
- [Coverage Floor](coverage-floor.md)
- [Code Standards](code-standards.md)
