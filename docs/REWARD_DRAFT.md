# Bestiaire — choix de récompense entre les combats (29 octobre 2026)

## Fonctionnalité

Auparavant, chaque victoire ajoutait automatiquement une carte aléatoire à `player_deck`, puis ouvrait le combat suivant sans décision du joueur. L'amélioration affecte bien **`bestiaire_game.py`, le prototype lancé par le README**, et non seulement les classes du moteur `core/` parfois non utilisées dans cette interface.

Désormais, à la victoire d'un combat intermédiaire :

1. Les créatures détruites sont retirées du deck comme avant ; l'étape suivante est préparée.
2. La partie passe dans l'état `reward`, avec trois cartes distinctes proposées, leurs coûts, statistiques et descriptions.
3. Le joueur peut cliquer une carte, utiliser les touches **1/2/3**, ou **passer** avec le bouton, **S** ou **Échap**.
4. Choisir une carte en ajoute **une seule copie** au deck. Passer n'en ajoute aucune. Une sélection invalide est refusée, et les clics répétés après transition n'accordent pas de butin supplémentaire.
5. `start_combat` démarre ensuite réellement l'étape suivante. Après la victoire finale de l'étape 10, la run se termine directement, sans faux écran de récompense.

**Accessibilité initiale :** parmi les trois propositions, au moins une possède un coût de carte inférieur ou égal à l'énergie par tour de base (3), tant que le catalogue contient un tel exemplaire. Cela évite un écran composé uniquement de cartes impossibles à jouer dans la configuration initiale. Les 2 autres restent variées et peuvent inclure des choix coûteux, pour créer des objectifs de progression. Ce n'est pas encore un algorithme de draft équilibré sur plusieurs runs.

## Comment tester

```bash
python -m unittest discover -s tests -p 'test_card_reward_choice.py' -v
python -m py_compile bestiaire_game.py
```

La suite dédiée charge la **vraie classe `BestiaireGame`**, avec `pygame.Rect` simulé pour éviter le besoin d'un écran. Elle vérifie : pas de carte offerte automatiquement, trois récompenses différentes, au moins une accessible au budget, choix effectif, refus des doublons, skip, clics et transition vers le nouveau combat, fin directe après boss.

Un workflow GitHub exécute ces tests sous Python 3.10 et 3.12. **Le résultat doit être contrôlé**, pas présumé vert. Cette validation de règles ne remplace pas le test Pygame du rendu et de la souris dans une fenêtre.

Pour jouer visuellement :

```bash
python -m pip install -r requirements.txt
python bestiaire_game.py
```

## Reprise Codex et limites d'équilibrage

- Branche `feat/meaningful-card-rewards-20261029` dérivée du commit de la PR #1 `chatgpt/review-20261024` ; **PR empilée**. Ne pas fusionner avant #1 ni écraser les modifications antérieures.
- Lire `AGENTS.md`, `README.md`, `docs/CHATGPT_PROJECT_HISTORY.md` et ce document.
- Faire tester l'écran sous Pygame : clic sur les trois cartes, bouton Passer, clavier 1/2/3/S/Échap, rendu de noms longs et des descriptions.
- Simulation recommandée : mesurer sur 100+ graines le pourcentage de runs atteignant les combats 3, 5, 8 et 10 avec prise de carte automatique (ancien témoin), choix greedy, choix aléatoire et skip ; tenir compte des cartes mortes et des dégâts permanents. Ne pas déclarer le jeu équilibré à partir de tests de règles.
- Les récompenses sont actuellement un **draft simple** de 3 cartes sans filtre de rareté par étape. Ajouter ultérieurement des catégories de récompenses et des choix qui changent la stratégie, mais seulement avec des mesures et un cadre de difficulté documentés.
- Ne pas lire ni publier des sauvegardes personnelles ; aucune connexion réseau ni collection de données utilisateurs n'est introduite.

**État des preuves :** code et tests engagés, validation à constater via GitHub Actions. Aucun test graphique manuel certifié dans cette intervention.


## CI complète du dépôt : régression puis correction

Premier run de la suite intégrale : 54 tests réussis, 2 échecs. L'ancien test `test_end_turn_refills_hand_and_captures_new_card` attendait une récompense automatique désormais supprimée ; il a été réécrit pour vérifier l'état `reward`, la décision du joueur et la carte réellement ajoutée. L'autre échec, `test_dead_cards_are_not_revived_on_next_stage`, a révélé des références persistantes à des créatures détruites dans `hand` et `draw_pile` pendant le nouvel écran. Le moteur vide désormais les piles du combat achevé avant le choix ; `start_combat` les reconstruit ensuite à partir du deck survivant. Les tests historiques ne sont pas désactivés. Recontrôler le nouveau run CI avant de fusionner.
