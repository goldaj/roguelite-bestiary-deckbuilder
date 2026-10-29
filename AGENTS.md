# AGENTS.md — Bestiaire

## Avant toute intervention
- Lire `README.md`, puis **`docs/CHATGPT_PROJECT_HISTORY.md`** pour les décisions de conception et les limites documentaires. Consulter ensuite les documents spécialisés cités par le README.
- Mission : Roguelite Python/Pygame de créatures, cartes, moteur de combats, progression persistante et sauvegardes.
- Invariants : Distinguer prototype jouable, docs d'ambition et travail restant. Les 7 tests de progression en échec cités dans le README ne doivent pas être présentés comme résolus sans mesure.

## Exécution
- `python -m pip install -r requirements.txt` ; `python bestiaire_game.py` ; `python -m pytest tests`.
- Préserver le travail préexistant, les versions anciennes et les fichiers non concernés. Valider uniquement ce qui peut être vérifié dans l'environnement disponible.

## Continuité du contexte
- Après toute modification de projet, consulter et enrichir `docs/CHATGPT_PROJECT_HISTORY.md` avec les échanges fournis, les décisions et le résultat de la validation.
- Distinguer `Utilisateur (verbatim)`, `Assistant (verbatim)` et `Résumé reconstruit (non verbatim)`. Donner date et heure uniquement si attestées, sinon noter qu'elles manquent.
- Ne pas inventer d'échanges ou de tests. Si une transcription n'est pas accessible, demander son export plutôt que supposer son contenu.
- Le dépôt peut être public : expurger secrets, données personnelles et contenus ne relevant pas du projet. Ne pas écraser les éléments historiques.

## Récompenses choisies (2026-10-29)

- Branche `feat/meaningful-card-rewards-20261029` construite **sur le commit de la PR #1** `chatgpt/review-20261024`, base PR empilée sur cette branche. Ne pas merger avant le parent ni modifier `develop` automatiquement.
- Dans le jeu autonome `bestiaire_game.py` : l'état `reward` propose trois cartes distinctes après les étapes 1 à 9 ; le joueur choisit 1 carte ou passe. Transition vers le combat suivant uniquement après le choix. Pas de récompense après la victoire finale.
- Le pool garantit au moins un coût <=3 si disponible. Ne pas confondre ce garde-fou avec une étude d'équilibrage du deck, qui manque.
- Lire `docs/REWARD_DRAFT.md`. Tests sans Pygame graphique : `python -m unittest discover -s tests -p 'test_card_reward_choice.py' -v`. Vérifier CI et UI vraie avant fusion.
- Conserver les fichiers historiques, les sauvegardes utilisateur et l'intégration précédente des 90 cartes/captures.
