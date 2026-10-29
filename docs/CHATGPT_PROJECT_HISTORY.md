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

## 2026-10-24 — Revue parallèle multi-dépôts (heure non disponible)

**Utilisateur (verbatim, message visible dans cette conversation)** :

> tu vois tout le boulot qu'on a fait sur la conversation Avancement projets codex ?
> Tu vas refaire la même chose sur TOUT mon repo git. Tu vas commencer par les projets les plus gros, regarder ce que tu peux faire dessus et le faire sur ta branch (même consignes que sur l'autre conversation).
> Tu vas ensuite me faire un rapport très succint des projets que t'as touché et de ce que t'as avancé dessus.
> Amuse toi !

**Assistant (résumé reconstruit, non verbatim)** : revue des gros dépôts et amélioration isolée sur `chatgpt/review-20261024`. Sauvegardes : import Tuple manquant, backup corrompu/effacé, checksum d'import recalculé et validé ; tests isolés et CI sans prétendre corriger les sept échecs existants.

**Validation et confiance** : confiance moyenne sur la portée du changement ; aucune exécution locale des tests ne peut être attestée depuis l'accès GitHub disponible. Consulter les statuts GitHub Actions de la PR avant intégration. Aucune modification de `main`/`develop`, aucun déploiement. Codex doit inspecter le diff, relancer les tests et choisir les commits à intégrer sans écraser son travail.

## 2026-10-24 — Bestiaire: correction et continuation du prototype jouable

**Utilisateur (verbatim, heure de message non attestée)** : « je crois que ça a planté. Reprends là où tu t'es arrêté »

**Utilisateur (résumé reconstruit, non verbatim)** : souhaite réduire les changements de structure et favoriser les corrections fonctionnelles et la poursuite des fonctions non terminées, dans des branches indépendantes que Codex peut choisir de reprendre ou non.

**Assistant (résumé reconstruit, non verbatim)** : Le prototype Pygame autonome `bestiaire_game.py` charge désormais les 90 cartes du catalogue, les compétences `on_attack` existantes (au lieu de statuts aléatoires), une pioche limitée et renouvelée à chaque tour, les blessures conservées entre combats et une carte capturée en récompense après victoire. Garde et Carapace agissent au combat. Le moteur `core/` a aussi les captures/boutiques/loot et déblocages corrigés dans cette branche. Certaines capacités hors `on_attack` restent volontairement à réaliser.

**Validation** : GitHub Actions du commit 7aca63801276c3410b8f57f5f6a79e5052e24fb8: 50 tests réussis le 24 octobre 2026, incluant des tests Pygame sans affichage. Aucun test humain approfondi d'équilibrage.

**Handoff Codex** : lire les changements sur `chatgpt/review-20261024`, poursuivre les éléments non terminés, puis choisir sélectivement les commits utiles. Aucun merge sur la branche principale.

## 2026-10-29 — trois récompenses de cartes au choix (résumé non verbatim)

- L'utilisateur attend une progression GitHub continue, fonctionnelle et documentée ; préférence antérieure pour l'équilibrage mesuré des jeux.
- Après consultation de la PR #1 Bestiaire et des branches, la nouvelle branche empilée `feat/meaningful-card-rewards-20261029` modifie réellement `bestiaire_game.py` : remplacer une carte automatiquement tirée et ajoutée au deck par trois choix distincts ou possibilité de passer, avec transition vers le combat suivant.
- Une option accessible au budget énergétique de base est garantie. Tests de la vraie classe sans GUI : effets de choix, skip, clics, progression et boss final. Workflow Python 3.10/3.12 ajouté ; succès à établir par ses journaux. Aucun test manuel graphique ou bilan statistique d'équilibrage n'a été réalisé.
- Lire `docs/REWARD_DRAFT.md` et ne pas fusionner dans `develop` avant la PR parent #1.


## CI complète du dépôt : régression puis correction

Premier run de la suite intégrale : 54 tests réussis, 2 échecs. L'ancien test `test_end_turn_refills_hand_and_captures_new_card` attendait une récompense automatique désormais supprimée ; il a été réécrit pour vérifier l'état `reward`, la décision du joueur et la carte réellement ajoutée. L'autre échec, `test_dead_cards_are_not_revived_on_next_stage`, a révélé des références persistantes à des créatures détruites dans `hand` et `draw_pile` pendant le nouvel écran. Le moteur vide désormais les piles du combat achevé avant le choix ; `start_combat` les reconstruit ensuite à partir du deck survivant. Les tests historiques ne sont pas désactivés. Recontrôler le nouveau run CI avant de fusionner.
