# Bestiaire : Écorces & Échos

Prototype Python/Pygame de roguelite et de deckbuilding autour de créatures, de combats et d'une progression persistante. Ce dépôt conserve les expérimentations existantes, le moteur de règles et ses tests.

## Essayer le prototype

Python 3.10 ou plus récent conseillé. Créer un environnement virtuel puis :

```bash
python -m pip install -r requirements.txt
python bestiaire_game.py
```

Le prototype autonome utilise le glisser-déposer des cartes, Entrée pour finir un tour, Espace pour confirmer et Échap pour revenir au menu. `main.py` contient un écran d'accueil expérimental distinct.

## Explorer le code

- `core/` : entités, résolution des combats, progression et sauvegardes.
- `bestiaire_game.py` : prototype autonome jouable.
- `tests/` : tests existants des entités, combats et progression.
- `docs/README.md` et `pitch_deck.html` : documentation de conception et ambitions du projet ; certaines descriptions ne sont pas encore réalisées dans le prototype.

Pour lancer les tests : `python -m pip install pytest hypothesis`, puis `python -m pytest tests`.

Vérification du 18 octobre 2026 : le prototype autonome s'initialise avec le pilote vidéo Pygame de test ; la suite existante compte 25 tests réussis et 7 échecs dans les systèmes de progression. Ces échecs restent à corriger ; le dépôt présente donc un travail en cours.

Le projet reste en développement. Les anciens documents de conception décrivent aussi des pistes futures et des exemples de distribution ; ils ne constituent pas une annonce de version publiée. Les environnements, caches, paramètres IDE et sauvegardes personnelles restent sur le poste et sont ignorés par Git.
