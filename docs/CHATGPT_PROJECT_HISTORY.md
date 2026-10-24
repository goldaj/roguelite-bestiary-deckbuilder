# Contexte de projet ChatGPT : Bestiaire

> Journal pour Codex créé le 2026-10-24. **Partiel**, car les exports complets de toutes les conversations ChatGPT ne sont pas accessibles dans cette session. Les résumés ci-dessous ne sont pas des citations.

## Périmètre et état vérifiables
- Dépôt : `goldaj/roguelite-bestiary-deckbuilder`.
- Objet d'après le README : Roguelite Python/Pygame de créatures, cartes, moteur de combats, progression persistante et sauvegardes.
- Invariants : Distinguer prototype jouable, docs d'ambition et travail restant. Les 7 tests de progression en échec cités dans le README ne doivent pas être présentés comme résolus sans mesure.
- Entrée de vérification : `python -m pip install -r requirements.txt` ; `python bestiaire_game.py` ; `python -m pytest tests`.

## Échanges et références retrouvés

2026-10-18 — Assistant, résumé non verbatim : séparation des prototypes de jeux et comparaison avec Moonrail sans fusion de leurs univers.

2026-10-18 13:24:13 UTC — Utilisateur (extrait exact) : « N'écrase aucun repo existant. »

2026-10-24 — Utilisateur (verbatim, heure indisponible) : « je te demande de lire mes repo git où tu es le dernier utilisateur, de rajouter un AGENTS.md pertinent s’il n’y en a pas. Mais en plus, tu rajoutera un document repérable par codex [...] où tu mets l’intégralité de nos échanges liés à ce projet. Mes questions, tes réponses [...] et les horodatages si tu les as. » (extrait avec ellipses signalées, donc non intégral).

## À compléter avec les transcriptions sources
**Manquent :** questions/réponses intégrales de chaque session de conception, horaires individuels de certains messages et échanges Codex non publiés. Ne jamais reconstituer un dialogue en prétendant citer des propos exacts.

Lorsque des exports ChatGPT authentiques sont fournis, les archiver par session, avec date ISO/fuseau, rôles et texte intégral en préservant leur ordre. Revoir toute donnée sensible avant de pousser sur GitHub. Après chaque modification, ajouter les échanges exacts nouvellement disponibles, puis actualiser les décisions et l'état vérifié.
