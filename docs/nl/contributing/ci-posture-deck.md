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
Decision*, geëxporteerd op **9 september 2026**. De vraag erin is er één: goedkeuring voor een
**initiële schoonmaak** van beide applicaties en het inrichten van een standaard
leveringspijplijn daarachter, terwijl het huidige `acc`-en-`main`-spoor in gebruik blijft voor
rapid prototyping.

!!! abstract "Downloaden"
    [CI Posture Across Repos — presentatie (PDF, 82 KB)](../../assets/downloads/ci-posture-across-repos-deck.pdf)

---

## Twee sporen

<figure markdown style="width:100%; margin:0;">
  ![Dia 1 van 5: bovenin de band RAPID PROTOTYPING — accepteren op acc, promoveren naar main, elke merge bewaakt door GitHub Actions, waar alle drie de controles al draaien. Daaronder de nog te bouwen band STANDARD SOFTWARE DELIVERY met Wasstraat, CI/CD-pijplijn (build, test, deploy) en een productieklare oplevering; de initiële schoonmaak links is de gevraagde beslissing](../../assets/slides/ci-posture/slide-1-two-tracks.png)
  <figcaption>Alles gaat vandaag via het prototypingspoor; het spoor daaronder moet nog gebouwd worden</figcaption>
</figure>

---

## Wat GitHub Actions al bewaakt

<figure markdown style="width:100%; margin:0;">
  ![Dia 2 van 5: drie controles die in CI blokkeren — 01 build-herkomst ("welke build zie ik?"), 02 supply-chainverificatie ("klopt de pin?") en 03 de dekkingsdrempel ("is deze code echt getest?", 80% van de beslispaden per bestand). Onderaan een tabel met Ja voor zowel de CPSV Editor als de Linked Data Explorer](../../assets/slides/ci-posture/slide-2-what-ci-gates.png)
  <figcaption>De drie controles als vragen, en de tabel erachter</figcaption>
</figure>

Elke controle heeft een eigen pagina: [Build Provenance](build-provenance.md),
[Supply-Chain Pinning](supply-chain.md) en de [Coverage Floor](coverage-floor.md).

---

## Vijf punten, alle gesloten

<figure markdown style="width:100%; margin:0;">
  ![Dia 3 van 5: vijf afgevinkte punten uit de CI-posture-review — laatste dekkingsuitzondering opgeheven, het pinregister loopt mee met de bumps, marge op de dekkingsdrempel, opmaakcontrole in CI op de gedeelde branch, en productie-build-id's eenmalig bevestigd](../../assets/slides/ci-posture/slide-3-what-was-delivered.png)
  <figcaption>Een opleveringsverslag in plaats van een backlog</figcaption>
</figure>

---

## De vraag

<figure markdown style="width:100%; margin:0;">
  ![Dia 4 van 5: start de initiële schoonmaak — wat het oplevert, wat het kost en wat het brengt, met als kern dat prototypewerk pas bij een halfjaarlijkse merge in een oplevering terechtkomt in plaats van op de dag dat het geschreven is](../../assets/slides/ci-posture/slide-4-the-decision.png)
  <figcaption>Wat het oplevert, wat het kost, wat het brengt</figcaption>
</figure>

---

## Wat er tussen versies veranderde

<figure markdown style="width:100%; margin:0;">
  ![Dia 5 van 5: zes correcties ten opzichte van de eerste versie, waaronder dat het prototypingspoor wél degelijk een CI/CD-gang kent en dat alle vijf de punten inmiddels gesloten zijn](../../assets/slides/ci-posture/slide-5-changelog.png)
  <figcaption>De presentatie draagt haar eigen correcties</figcaption>
</figure>

---

## Verwante pagina's

- [Build Provenance](build-provenance.md)
- [Supply-Chain Pinning](supply-chain.md)
- [Coverage Floor](coverage-floor.md)
- [Code Standards](code-standards.md)
