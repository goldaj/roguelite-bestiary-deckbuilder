# core/entities.py
"""Entités du jeu - Cartes, Créatures, États permanents"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any
from enum import Enum, auto
import json
import random
from copy import deepcopy
from pathlib import Path


class Rarity(Enum):
    COMMON = "C"
    UNCOMMON = "U"
    RARE = "R"
    EPIC = "E"
    LEGENDARY = "L"


class Biome(Enum):
    FORET = "forest"
    DUNES = "dunes"
    FALAISES = "cliffs"
    FLEUVE = "river"
    VOLCAN = "volcano"
    RUINES = "ruins"
    NEUTRE = "neutral"


class Keyword(Enum):
    TIRAILLEUR = auto()
    GARDE = auto()
    VOL = auto()
    PERCEE = auto()
    BOND = auto()
    CARAPACE = auto()
    ETHEREE = auto()


class StatusEffect(Enum):
    VENIN = "venin"
    BRULURE = "brulure"
    SAIGNEMENT = "saignement"
    FRACTURE = "fracture"
    MALEDICTION = "malediction"
    EROSION = "erosion"
    OFFENSE_EMOUSSEE = "offense_emoussee"


@dataclass
class Card:
    """Représente une carte de créature avec état permanent"""
    id: str
    name: str
    biome: Biome
    rarity: Rarity
    cost: int
    base_atk: int
    base_dur: int
    base_spd: int
    keywords: Set[Keyword] = field(default_factory=set)

    # État permanent durant la run
    current_dur: int = 0
    current_atk: int = 0
    current_spd: int = 0
    shields: int = 0
    permanent_statuses: Dict[StatusEffect, int] = field(default_factory=dict)

    # Capacités
    on_deploy: List[Dict] = field(default_factory=list)
    on_attack: List[Dict] = field(default_factory=list)
    on_hit: List[Dict] = field(default_factory=list)
    on_death: List[Dict] = field(default_factory=list)

    def __post_init__(self):
        if self.current_dur == 0:
            self.current_dur = self.base_dur
        if self.current_atk == 0:
            self.current_atk = self.base_atk
        if self.current_spd == 0:
            self.current_spd = self.base_spd

    def take_damage(self, amount: int) -> bool:
        """Applique des dégâts permanents. Retourne True si la carte survit."""
        while amount > 0 and self.shields > 0:
            self.shields -= 1
            amount -= 1

        self.current_dur -= amount
        return self.current_dur > 0

    def apply_status(self, effect: StatusEffect, value: int):
        """Applique une altération permanente"""
        if effect not in self.permanent_statuses:
            self.permanent_statuses[effect] = 0
        self.permanent_statuses[effect] += value

        # Effets immédiats de certains statuts
        if effect == StatusEffect.FRACTURE:
            self.current_atk = max(1, self.current_atk - value)
        elif effect == StatusEffect.OFFENSE_EMOUSSEE:
            self.current_atk = min(self.current_atk, 1)

    def process_start_combat(self):
        """Effets au début du combat"""
        if StatusEffect.VENIN in self.permanent_statuses:
            self.take_damage(self.permanent_statuses[StatusEffect.VENIN])
        if StatusEffect.MALEDICTION in self.permanent_statuses:
            self.current_spd = max(1, self.current_spd - 1)

    def process_end_combat(self):
        """Effets à la fin du combat"""
        if StatusEffect.BRULURE in self.permanent_statuses:
            self.take_damage(self.permanent_statuses[StatusEffect.BRULURE])

    def process_node_transition(self):
        """Effets entre les nœuds"""
        if StatusEffect.EROSION in self.permanent_statuses:
            self.take_damage(1)

    def get_effective_atk(self) -> int:
        """Retourne l'ATQ effective avec tous les modificateurs"""
        atk = self.current_atk
        if StatusEffect.OFFENSE_EMOUSSEE in self.permanent_statuses:
            atk = 1
        return max(1, atk)

    def to_dict(self) -> Dict:
        """Sérialisation pour sauvegarde"""
        return {
            'id': self.id,
            'name': self.name,
            'biome': self.biome.value,
            'rarity': self.rarity.value,
            'cost': self.cost,
            'base_stats': {'atk': self.base_atk, 'dur': self.base_dur, 'spd': self.base_spd},
            'current_stats': {'atk': self.current_atk, 'dur': self.current_dur, 'spd': self.current_spd},
            'shields': self.shields,
            'keywords': [k.name for k in self.keywords],
            'statuses': {s.value: v for s, v in self.permanent_statuses.items()}
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Card':
        """Désérialisation depuis sauvegarde"""
        card = cls(
            id=data['id'],
            name=data['name'],
            biome=Biome(data['biome']),
            rarity=Rarity(data['rarity']),
            cost=data['cost'],
            base_atk=data['base_stats']['atk'],
            base_dur=data['base_stats']['dur'],
            base_spd=data['base_stats']['spd']
        )

        card.current_atk = data['current_stats']['atk']
        card.current_dur = data['current_stats']['dur']
        card.current_spd = data['current_stats']['spd']
        card.shields = data.get('shields', 0)

        for k in data.get('keywords', []):
            card.keywords.add(Keyword[k])

        for status, value in data.get('statuses', {}).items():
            card.permanent_statuses[StatusEffect(status)] = value

        return card

    def clone(self) -> 'Card':
        """Crée une copie profonde de la carte"""
        return deepcopy(self)


@dataclass
class CombatState:
    """État d'un combat en cours"""
    player_field: List[Optional[Card]] = field(default_factory=lambda: [None] * 6)
    enemy_field: List[Optional[Card]] = field(default_factory=lambda: [None] * 6)
    turn: int = 1
    energy: int = 3
    hand: List[Card] = field(default_factory=list)
    deck: List[Card] = field(default_factory=list)
    discard: List[Card] = field(default_factory=list)

    terrain_modifiers: Dict[str, Any] = field(default_factory=dict)

    def get_presence(self, is_player: bool) -> int:
        """Calcule la présence totale d'un camp"""
        field = self.player_field if is_player else self.enemy_field
        return sum(c.current_dur for c in field if c)

    def is_combat_over(self) -> Optional[bool]:
        """Vérifie si le combat est terminé. Retourne True si victoire, False si défaite."""
        if self.get_presence(False) == 0:
            return True
        if self.get_presence(True) == 0:
            return False
        return None


@dataclass
class RunState:
    """État d'une run complète"""
    current_deck: List[Card]
    current_node: int = 0
    current_act: int = 1
    fragments: int = 0
    genes: int = 0
    eggs: int = 0
    trophies: int = 0

    unlocked_cards: Set[str] = field(default_factory=set)
    visited_nodes: List[str] = field(default_factory=list)
    score: int = 0

    def process_node_rewards(self, rewards: Dict):
        """Traite les récompenses d'un nœud"""
        self.fragments += rewards.get('fragments', 0)
        self.genes += rewards.get('genes', 0)
        self.eggs += rewards.get('eggs', 0)

        for card_id in rewards.get('cards', []):
            # Ajouter la carte au deck
            pass

    def save_to_dict(self) -> Dict:
        """Sauvegarde l'état de la run"""
        return {
            'deck': [c.to_dict() for c in self.current_deck],
            'node': self.current_node,
            'act': self.current_act,
            'resources': {
                'fragments': self.fragments,
                'genes': self.genes,
                'eggs': self.eggs,
                'trophies': self.trophies
            },
            'unlocked': list(self.unlocked_cards),
            'score': self.score
        }


class CardDatabase:
    """Base de données des cartes du jeu"""

    def __init__(self):
        self.cards: Dict[str, Dict] = {}
        self.load_cards()

    def load_cards(self):
        """Charge le catalogue réel plutôt qu'un échantillon codé en dur."""
        catalog_path = Path(__file__).resolve().parents[1] / "data" / "cards.json"
        with catalog_path.open("r", encoding="utf-8") as handle:
            source = json.load(handle)["cards"]

        self.cards = {}
        for card_id, raw in source.items():
            data = raw.copy()
            data["biome"] = Biome(raw["biome"])
            data["rarity"] = Rarity(raw["rarity"])
            data["keywords"] = [Keyword[name] for name in raw.get("keywords", [])]
            for field_name in ("on_attack", "on_deploy", "on_hit", "on_death"):
                # Les effets du JSON utilisent leurs noms, le moteur attend l'Enum.
                data[field_name] = []
                for raw_effect in raw.get(field_name, []):
                    effect = raw_effect.copy()
                    if isinstance(effect.get("effect"), str):
                        effect_name = effect["effect"]
                        if effect_name in StatusEffect.__members__:
                            effect["effect"] = StatusEffect[effect_name]
                    data[field_name].append(effect)
            self.cards[card_id] = data

    def create_card(self, card_id: str) -> Card:
        """Crée une instance de carte depuis l'ID"""
        if card_id not in self.cards:
            raise ValueError(f"Carte inconnue: {card_id}")

        data = self.cards[card_id]
        card = Card(
            id=card_id,
            name=data["name"],
            biome=data["biome"],
            rarity=data["rarity"],
            cost=data["cost"],
            base_atk=data["atk"],
            base_dur=data["dur"],
            base_spd=data["spd"],
            keywords=set(data.get("keywords", []))
        )

        card.on_attack = deepcopy(data.get("on_attack", []))
        card.on_deploy = deepcopy(data.get("on_deploy", []))
        card.on_hit = deepcopy(data.get("on_hit", []))
        card.on_death = deepcopy(data.get("on_death", []))

        return card

    def get_starter_deck(self) -> List[Card]:
        """Retourne le deck de départ pour une nouvelle run"""
        starter_ids = [
            "forest_spine_frog", "forest_spine_frog",
            "forest_azure_spider", "forest_azure_spider",
            "dunes_solar_fennec", "dunes_solar_fennec",
            # Ajouter plus de cartes de départ
        ]

        deck = []
        for card_id in starter_ids[:12]:  # 12 cartes de départ
            if card_id in self.cards:
                deck.append(self.create_card(card_id))

        return deck