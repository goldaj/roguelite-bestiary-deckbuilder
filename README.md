# Bestiaire — roguelite de créatures et deckbuilding

Prototype Python/Pygame de roguelite et de deckbuilding autour de créatures, de combats et d'une progression persistante. Ce dépôt conserve les expérimentations existantes, le moteur de règles et ses tests.

## Essayer le prototype

Python 3.10 ou plus récent conseillé. Créer un environnement virtuel puis :

```bash
python -m pip install -r requirements.txt
python bestiaire_game.py
```

Le prototype autonome utilise le glisser-déposer des cartes, Entrée pour finir un tour, Espace pour confirmer et Échap pour revenir au menu. Il charge les 90 cartes du catalogue commun, repioche jusqu'à cinq cartes à chaque tour (dans la limite du deck restant), conserve les blessures des créatures entre les combats et ajoute une carte capturée à chaque victoire d'étape. Les effets `on_attack` du catalogue sont appliqués ; les autres compétences spéciales ne sont pas toutes intégrées à ce prototype. `main.py` contient un écran d'accueil expérimental distinct.

## Explorer le code

- `core/` : entités, résolution des combats, progression et sauvegardes.
- `bestiaire_game.py` : prototype autonome jouable.
- `tests/` : tests existants des entités, combats et progression.
- `docs/README.md` et `pitch_deck.html` : documentation de conception et ambitions du projet ; certaines descriptions ne sont pas encore réalisées dans le prototype.

Pour lancer les tests : `python -m pip install pytest hypothesis`, puis `python -m pytest tests`.

Historique : le 18 octobre 2026, la suite comptait 25 tests réussis et 7 échecs de progression. Après les correctifs sur `chatgpt/review-20261024`, **50 tests réussissent sur GitHub Actions le 24 octobre 2026**, incluant le lancement Pygame sans affichage, les boutiques, les récompenses et les sauvegardes. Il reste du travail sur la totalité des compétences, l'équilibrage et les parcours d'interface.

Le projet reste en développement. Les anciens documents de conception décrivent aussi des pistes futures et des exemples de distribution ; ils ne constituent pas une annonce de version publiée. Les environnements, caches, paramètres IDE et sauvegardes personnelles restent sur le poste et sont ignorés par Git.

## Situer ce prototype parmi les autres jeux

| Projet | Expérience explorée | Organisation du code |
| --- | --- | --- |
| [Moonrail](https://github.com/goldaj/moonrail-narrative-deckbuilder) | Deckbuilding narratif, collection et progression persistante | Projet distinct, avec sa direction de produit et ses personnages |
| [Bestiaire](https://github.com/goldaj/roguelite-bestiary-deckbuilder) | Créatures, cartes et attrition persistante au fil des combats | Prototype autonome, moteur `core/` et tests ; progression encore à corriger |
| [DeckLite](https://github.com/goldaj/decklite-roguelite-deckbuilder) | Construire son deck pendant une run, choisir des récompenses, événements et boutique méta | Prototype Pygame concentré dans `main.py` |
| [Exploration sur tuiles](https://github.com/goldaj/tilemap-exploration-roguelite) | Se déplacer sur une grille, rencontrer des ennemis, gérer objets et boutique | Modules monde/combat/interface, tuiles et sprites |
| [Chess Roguelite](https://github.com/goldaj/chess-roguelite) | Déplacer des pièces d'échecs et acquérir des améliorations entre les affrontements | Plateau, IA, progression et interface souris |
| [Idle Clicker](https://github.com/goldaj/idle-clicker-tkinter) | Clics, revenus et achats avec coût dynamique | Interface de bureau Tkinter/ttkbootstrap |

Ces dépôts conservent des expériences distinctes, à différents niveaux d'avancement.
