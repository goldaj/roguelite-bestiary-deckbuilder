#!/usr/bin/env python3
"""
BESTIAIRE: Écorces & Échos
Jeu complet fonctionnel - Version intégrée
"""

import pygame
import random
import math
import json
from copy import deepcopy
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from pathlib import Path

# ============================================================================
# CONFIGURATION
# ============================================================================

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Couleurs
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_GRAY = (40, 40, 40)
MID_GRAY = (80, 80, 80)
LIGHT_GRAY = (160, 160, 160)
GREEN = (100, 200, 100)
RED = (200, 100, 100)
BLUE = (100, 100, 200)
GOLD = (255, 215, 0)
ORANGE = (255, 150, 50)
PURPLE = (150, 100, 200)

# Configuration gameplay
PLAYER_HP = 20
ENEMY_HP_BASE = 15
HAND_SIZE_INITIAL = 5
ENERGY_PER_TURN = 3
BOARD_SLOTS = 4


# ============================================================================
# MODÈLES DE DONNÉES
# ============================================================================

class StatusEffect(Enum):
    """Effets permanents"""
    VENIN = "venin"  # Dégâts au début du combat
    BRULURE = "brulure"  # Dégâts à la fin du combat
    SAIGNEMENT = "saignement"  # Dégâts quand attaque
    FRACTURE = "fracture"  # -1 ATQ permanent
    MALEDICTION = "malediction"  # -1 Vitesse au début
    EROSION = "erosion"  # -1 DUR à chaque nœud


class Keyword(Enum):
    """Mots-clés des cartes"""
    TIRAILLEUR = auto()  # +1 ATQ contre nouvelles invocations
    GARDE = auto()  # Protège la ligne arrière
    VOL = auto()  # Ignore effets de terrain
    PERCEE = auto()  # Traverse les boucliers
    BOND = auto()  # Cible le plus faible
    CARAPACE = auto()  # Réduit l'ATQ de l'attaquant
    ETHEREE = auto()  # Ne peut être ciblé au corps-à-corps


@dataclass
class Card:
    """Carte de créature"""
    id: str
    name: str
    cost: int
    base_atk: int
    base_dur: int
    base_spd: int
    keywords: List[Keyword] = field(default_factory=list)
    description: str = ""
    color: Tuple[int, int, int] = field(default_factory=lambda: (100, 100, 100))

    # État permanent durant la run
    current_dur: int = 0
    current_atk: int = 0
    current_spd: int = 0
    shields: int = 0
    permanent_statuses: Dict[StatusEffect, int] = field(default_factory=dict)
    on_attack: List[Dict] = field(default_factory=list)

    def __post_init__(self):
        if self.current_dur == 0:
            self.current_dur = self.base_dur
        if self.current_atk == 0:
            self.current_atk = self.base_atk
        if self.current_spd == 0:
            self.current_spd = self.base_spd

    def take_damage(self, amount: int) -> bool:
        """Applique des dégâts permanents"""
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

        if effect == StatusEffect.FRACTURE:
            self.current_atk = max(1, self.current_atk - value)

    def get_effective_atk(self) -> int:
        """Retourne l'ATQ effective"""
        return max(0, self.current_atk)

    def clone(self) -> 'Card':
        """Crée une copie de la carte"""
        new_card = Card(
            id=self.id,
            name=self.name,
            cost=self.cost,
            base_atk=self.base_atk,
            base_dur=self.base_dur,
            base_spd=self.base_spd,
            keywords=self.keywords.copy(),
            description=self.description,
            color=self.color
        )
        new_card.current_atk = self.current_atk
        new_card.current_dur = self.current_dur
        new_card.current_spd = self.current_spd
        new_card.shields = self.shields
        new_card.permanent_statuses = self.permanent_statuses.copy()
        new_card.on_attack = deepcopy(self.on_attack)
        return new_card


# ============================================================================
# CARTES DU JEU
# ============================================================================

def create_all_cards() -> List[Card]:
    """Construit les cartes jouables depuis le catalogue partagé de 90 cartes."""
    path = Path(__file__).resolve().parent / "data" / "cards.json"
    with path.open("r", encoding="utf-8") as handle:
        catalogue = json.load(handle)["cards"]

    palette = {
        "forest": (92, 145, 97),
        "dunes": (190, 145, 94),
        "cliffs": (118, 135, 177),
        "river": (77, 124, 170),
        "volcano": (178, 83, 84),
        "ruins": (141, 104, 153),
        "neutral": (128, 135, 135),
    }
    cards = []
    for card_id, data in catalogue.items():
        abilities = []
        for effect in data.get("on_attack", []):
            if isinstance(effect.get("effect"), str) and effect["effect"] in StatusEffect.__members__:
                abilities.append({"effect": StatusEffect[effect["effect"]],
                                  "value": effect.get("value", 1),
                                  "self": effect.get("self", False)})
        cards.append(Card(
            card_id, data["name"], data["cost"], data["atk"], data["dur"], data["spd"],
            [Keyword[name] for name in data.get("keywords", [])],
            data.get("description", ""),
            palette[data["biome"]],
            on_attack=abilities,
        ))
    return cards


# ============================================================================
# SYSTÈME DE COMBAT
# ============================================================================

@dataclass
class CombatUnit:
    """Unité sur le terrain"""
    card: Card
    position: int
    is_player: bool
    has_attacked: bool = False


class CombatState:
    """État du combat"""

    def __init__(self):
        self.player_board: List[Optional[CombatUnit]] = [None] * BOARD_SLOTS
        self.enemy_board: List[Optional[CombatUnit]] = [None] * BOARD_SLOTS
        self.player_hp = PLAYER_HP
        self.enemy_hp = ENEMY_HP_BASE
        self.turn = 1
        self.energy = ENERGY_PER_TURN
        self.combat_log: List[str] = []

    def add_unit(self, card: Card, position: int, is_player: bool) -> bool:
        """Ajoute une unité sur le terrain"""
        board = self.player_board if is_player else self.enemy_board
        if board[position] is None:
            # Carapace begins protected; the first incoming blow can blunt its attacker.
            if Keyword.CARAPACE in card.keywords and card.shields == 0:
                card.shields = 1
            board[position] = CombatUnit(card, position, is_player)
            return True
        return False

    def get_all_units(self) -> List[CombatUnit]:
        """Retourne toutes les unités vivantes"""
        units = []
        for unit in self.player_board + self.enemy_board:
            if unit and unit.card.current_dur > 0:
                units.append(unit)
        return units

    def resolve_combat_turn(self):
        """Résout un tour de combat"""
        units = self.get_all_units()
        # Trier par vitesse décroissante
        units.sort(key=lambda u: u.card.current_spd, reverse=True)

        for unit in units:
            if unit.card.current_dur <= 0:
                continue

            # Trouver une cible
            target = self.find_target(unit)
            if target:
                self.attack(unit, target)
            else:
                # Attaque directe au joueur/ennemi
                if unit.is_player:
                    self.enemy_hp -= unit.card.get_effective_atk()
                    self.combat_log.append(f"{unit.card.name} inflige {unit.card.get_effective_atk()} dégâts directs!")
                else:
                    self.player_hp -= unit.card.get_effective_atk()
                    self.combat_log.append(f"{unit.card.name} vous inflige {unit.card.get_effective_atk()} dégâts!")

        # Nettoyer les morts
        self.cleanup_dead_units()

        # Appliquer les effets de fin de tour
        self.apply_end_turn_effects()

        self.turn += 1
        self.energy = ENERGY_PER_TURN

    def find_target(self, attacker: CombatUnit) -> Optional[CombatUnit]:
        """Target opposing units; a front-row Guard intercepts attacks on the rear."""
        opposing = self.enemy_board if attacker.is_player else self.player_board
        living = [unit for unit in opposing if unit and unit.card.current_dur > 0]
        if not living:
            return None

        if Keyword.BOND in attacker.card.keywords:
            target = min(living, key=lambda unit: unit.card.current_dur)
        else:
            direct = opposing[attacker.position] if attacker.position < len(opposing) else None
            target = direct if direct and direct.card.current_dur > 0 else living[0]

        # Two front slots, two rear slots in the playable four-slot prototype.
        if target.position >= BOARD_SLOTS // 2 and Keyword.PERCEE not in attacker.card.keywords:
            guard = next((unit for unit in living
                          if unit.position < BOARD_SLOTS // 2
                          and Keyword.GARDE in unit.card.keywords), None)
            if guard:
                return guard
        return target

    def attack(self, attacker: CombatUnit, defender: CombatUnit):
        """Effectue une attaque"""
        damage = attacker.card.get_effective_atk()

        # Carapace uses a shield to blunt the attacking creature.
        if (Keyword.CARAPACE in defender.card.keywords
                and defender.card.shields > 0
                and Keyword.PERCEE not in attacker.card.keywords):
            defender.card.shields -= 1
            attacker.card.current_atk = max(1, attacker.card.current_atk - 1)
            self.combat_log.append(f"{defender.card.name} active Carapace !")
            return
        # Percée ignores shields, otherwise normal damage and shield absorption.
        if Keyword.PERCEE in attacker.card.keywords:
            defender.card.current_dur -= damage
        else:
            defender.card.take_damage(damage)

        self.combat_log.append(f"{attacker.card.name} attaque {defender.card.name} pour {damage} dégâts!")

        # Les effets ne sont pas arbitraires : ils suivent la fiche de la carte.
        for effect in attacker.card.on_attack:
            target = attacker.card if effect.get("self") else defender.card
            target.apply_status(effect["effect"], max(0, int(effect["value"])))
            self.combat_log.append(
                f"{target.name} reçoit {effect['effect'].value} ({effect['value']})!"
            )

    def cleanup_dead_units(self):
        """Enlève les unités mortes"""
        for i in range(BOARD_SLOTS):
            if self.player_board[i] and self.player_board[i].card.current_dur <= 0:
                self.combat_log.append(f"{self.player_board[i].card.name} est détruit!")
                self.player_board[i] = None
            if self.enemy_board[i] and self.enemy_board[i].card.current_dur <= 0:
                self.combat_log.append(f"{self.enemy_board[i].card.name} est détruit!")
                self.enemy_board[i] = None

    def apply_end_turn_effects(self):
        """Applique les effets de fin de tour"""
        for unit in self.get_all_units():
            # Brûlure
            if StatusEffect.BRULURE in unit.card.permanent_statuses:
                damage = unit.card.permanent_statuses[StatusEffect.BRULURE]
                unit.card.take_damage(damage)
                self.combat_log.append(f"{unit.card.name} brûle pour {damage} dégâts!")

    def is_combat_over(self) -> Optional[str]:
        """Vérifie si le combat est terminé"""
        if self.player_hp <= 0:
            return "defeat"
        if self.enemy_hp <= 0:
            return "victory"
        return None


# ============================================================================
# INTERFACE DE JEU
# ============================================================================

class BestiaireGame:
    """Classe principale du jeu"""

    def __init__(self):
        pygame.init()

        # Configuration de l'écran
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Bestiaire: Écorces & Échos")

        # Police
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 18)

        # Horloge
        self.clock = pygame.time.Clock()
        self.running = True

        # État du jeu
        self.state = "menu"  # menu, combat, victory, defeat, map
        self.cards = create_all_cards()

        # Deck et progression
        self.player_deck: List[Card] = []
        self.enemy_deck: List[Card] = []
        self.hand: List[Card] = []
        self.draw_pile: List[Card] = []
        self.combat_state: Optional[CombatState] = None
        self.stage = 1
        self.max_stages = 10
        self.reward_options: List[Card] = []

        # Variables UI
        self.selected_card: Optional[int] = None
        self.hover_slot: Optional[int] = None
        self.animation_timer = 0

        # Particules
        self.particles: List[Dict] = []

    def start_new_run(self):
        """Démarre une nouvelle run"""
        # Créer le deck du joueur (10 cartes aléatoires)
        self.player_deck = []
        for _ in range(12):
            card = random.choice(self.cards).clone()
            self.player_deck.append(card)

        self.stage = 1
        self.reward_options = []
        self.start_combat()

    def start_combat(self):
        """Démarre un nouveau combat"""
        self.state = "combat"
        self.combat_state = CombatState()

        # Ajuster la difficulté
        is_boss = (self.stage == self.max_stages)
        enemy_hp = ENEMY_HP_BASE + (self.stage - 1) * 3
        if is_boss:
            enemy_hp += 20
        self.combat_state.enemy_hp = enemy_hp

        # Placer des ennemis
        enemy_count = min(2 + self.stage // 3, BOARD_SLOTS)
        for i in range(enemy_count):
            enemy_card = random.choice(self.cards).clone()
            # Bonus de stats pour les ennemis
            enemy_card.current_atk += self.stage // 2
            enemy_card.current_dur += self.stage
            self.combat_state.add_unit(enemy_card, i, False)

        # Une créature n'est ni dupliquée par la pioche, ni ressuscitée
        # après sa destruction. Les cartes encore en main restent disponibles.
        self.hand = []
        self.draw_pile = [card for card in self.player_deck if card.current_dur > 0]
        random.shuffle(self.draw_pile)
        self.draw_cards(HAND_SIZE_INITIAL)

        # Log
        self.combat_state.combat_log.append(f"=== Combat {self.stage} {'(BOSS)' if is_boss else ''} ===")

    def handle_events(self):
        """Gère les événements"""
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "combat":
                        self.state = "menu"
                    elif self.state == "reward":
                        self.select_reward(None)
                    else:
                        self.running = False
                elif self.state == "reward" and event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                    self.select_reward(event.key - pygame.K_1)
                elif self.state == "reward" and event.key == pygame.K_s:
                    self.select_reward(None)

                elif event.key == pygame.K_SPACE:
                    if self.state == "menu":
                        self.start_new_run()
                    elif self.state in ["victory", "defeat"]:
                        self.state = "menu"

                elif event.key == pygame.K_RETURN and self.state == "combat":
                    self.end_turn()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Clic gauche
                    self.handle_click(mouse_pos)

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.selected_card is not None:
                    self.handle_card_drop(mouse_pos)

            elif event.type == pygame.MOUSEMOTION:
                self.handle_hover(mouse_pos)

    def handle_click(self, pos):
        """Gère les clics"""
        if self.state == "menu":
            # Bouton nouvelle partie
            new_game_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 300, 300, 60)
            if new_game_rect.collidepoint(pos):
                self.start_new_run()

        elif self.state == "reward":
            for index in range(len(self.reward_options)):
                if self.reward_rect(index).collidepoint(pos):
                    self.select_reward(index)
                    return
            if self.reward_skip_rect().collidepoint(pos):
                self.select_reward(None)
            return

        elif self.state == "combat":
            # Sélection de carte dans la main
            for i, card in enumerate(self.hand):
                card_rect = self.get_hand_card_rect(i)
                if card_rect.collidepoint(pos):
                    if self.combat_state.energy >= card.cost:
                        self.selected_card = i
                    return

            # Bouton fin de tour
            end_turn_rect = pygame.Rect(SCREEN_WIDTH - 180, SCREEN_HEIGHT - 80, 160, 50)
            if end_turn_rect.collidepoint(pos):
                self.end_turn()

    def handle_card_drop(self, pos):
        """Gère le drop d'une carte"""
        if self.selected_card is None or self.state != "combat":
            return

        # Vérifier si on drop sur un slot
        for i in range(BOARD_SLOTS):
            slot_rect = self.get_board_slot_rect(i, True)
            if slot_rect.collidepoint(pos):
                if self.combat_state.player_board[i] is None:
                    card = self.hand.pop(self.selected_card)
                    self.combat_state.add_unit(card, i, True)
                    self.combat_state.energy -= card.cost
                    self.add_particle_burst(slot_rect.centerx, slot_rect.centery, card.color)
                    self.combat_state.combat_log.append(f"Vous jouez {card.name}")
                break

        self.selected_card = None

    def handle_hover(self, pos):
        """Gère le survol"""
        self.hover_slot = None

        if self.state == "combat":
            for i in range(BOARD_SLOTS):
                slot_rect = self.get_board_slot_rect(i, True)
                if slot_rect.collidepoint(pos):
                    self.hover_slot = i
                    break

    def draw_cards(self, count: int):
        """Pioche uniquement les cartes encore disponibles dans ce combat."""
        while count > 0 and self.draw_pile and len(self.hand) < HAND_SIZE_INITIAL:
            self.hand.append(self.draw_pile.pop())
            count -= 1

    def end_turn(self):
        """Résout le combat, attribue le butin et remplit la main."""
        if self.state != "combat":
            return
        self.combat_state.resolve_combat_turn()
        result = self.combat_state.is_combat_over()
        if result == "victory":
            # Les blessures et destructions demeurent à l'étape suivante.
            self.player_deck = [card for card in self.player_deck if card.current_dur > 0]
            self.stage += 1
            if self.stage > self.max_stages:
                self.state = "victory"
            else:
                # Stop on a real player choice instead of forcing a random card.
                self.reward_options = self.generate_reward_options()
                # A resolved fight must not keep stale hand/draw references, in
                # particular creatures that have died and left the persistent deck.
                self.hand = []
                self.draw_pile = []
                self.selected_card = None
                self.state = "reward"
        elif result == "defeat":
            self.state = "defeat"
        else:
            self.draw_cards(HAND_SIZE_INITIAL - len(self.hand))

    def generate_reward_options(self) -> List[Card]:
        """One accessible card plus two distinct alternatives, no automatic grant."""
        affordable = [card for card in self.cards if card.cost <= ENERGY_PER_TURN]
        if not affordable:
            affordable = list(self.cards)
        if not affordable:
            return []
        first = random.choice(affordable)
        remaining = [card for card in self.cards if card.id != first.id]
        choices = [first] + random.sample(remaining, min(2, len(remaining)))
        random.shuffle(choices)
        return [card.clone() for card in choices]

    def select_reward(self, index: Optional[int]) -> bool:
        """Choose one card or skip; no mutation for invalid/duplicate selections."""
        if self.state != "reward":
            return False
        if index is not None and (type(index) is not int or not 0 <= index < len(self.reward_options)):
            return False
        if index is not None:
            self.player_deck.append(self.reward_options[index].clone())
        self.reward_options = []
        self.start_combat()
        return True

    @staticmethod
    def reward_rect(index: int) -> pygame.Rect:
        return pygame.Rect(175 + index * 310, 210, 270, 255)

    @staticmethod
    def reward_skip_rect() -> pygame.Rect:
        return pygame.Rect(SCREEN_WIDTH // 2 - 135, 525, 270, 52)

    def get_hand_card_rect(self, index: int) -> pygame.Rect:
        """Retourne le rectangle d'une carte dans la main"""
        card_width = 120
        card_height = 160
        spacing = 10
        total_width = len(self.hand) * (card_width + spacing) - spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        y = SCREEN_HEIGHT - card_height - 20
        x = start_x + index * (card_width + spacing)
        return pygame.Rect(x, y, card_width, card_height)

    def get_board_slot_rect(self, index: int, is_player: bool) -> pygame.Rect:
        """Retourne le rectangle d'un slot du plateau"""
        slot_width = 140
        slot_height = 180
        spacing = 20
        total_width = BOARD_SLOTS * (slot_width + spacing) - spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        x = start_x + index * (slot_width + spacing)
        y = 320 if is_player else 80
        return pygame.Rect(x, y, slot_width, slot_height)

    def add_particle_burst(self, x, y, color):
        """Ajoute une explosion de particules"""
        for _ in range(20):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 150)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 1.0,
                'color': color,
                'size': random.randint(2, 6)
            })

    def update_particles(self, dt):
        """Met à jour les particules"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx'] * dt
            particle['y'] += particle['vy'] * dt
            particle['life'] -= dt * 2
            particle['vy'] += 300 * dt  # Gravité

            if particle['life'] <= 0:
                self.particles.remove(particle)

    def draw_menu(self):
        """Dessine le menu principal"""
        self.screen.fill(DARK_GRAY)

        # Titre
        title = self.big_font.render("BESTIAIRE", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        subtitle = self.font.render("Écorces & Échos", True, LIGHT_GRAY)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(subtitle, subtitle_rect)

        # Bouton nouvelle partie
        button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, 300, 300, 60)
        pygame.draw.rect(self.screen, GREEN, button_rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, button_rect, 3, border_radius=10)

        button_text = self.font.render("NOUVELLE PARTIE", True, WHITE)
        button_text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, button_text_rect)

        # Instructions
        instructions = [
            "Chaque dégât est permanent pour toute la run",
            "Survivez à 10 combats pour gagner",
            "Le dernier combat est un BOSS",
            "",
            "ESC - Retour au menu",
            "ENTRÉE - Fin du tour"
        ]

        y = 450
        for line in instructions:
            text = self.small_font.render(line, True, LIGHT_GRAY)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, text_rect)
            y += 25

    def draw_combat(self):
        """Dessine le combat"""
        self.screen.fill(DARK_GRAY)

        # Infos du combat
        stage_text = f"Combat {self.stage}/{self.max_stages}"
        if self.stage == self.max_stages:
            stage_text += " (BOSS)"
            color = GOLD
        else:
            color = WHITE
        text = self.font.render(stage_text, True, color)
        self.screen.blit(text, (20, 20))

        # HP
        player_hp_text = f"Vos PV: {self.combat_state.player_hp}"
        enemy_hp_text = f"PV Ennemi: {self.combat_state.enemy_hp}"

        hp_color = GREEN if self.combat_state.player_hp > 10 else RED
        text = self.font.render(player_hp_text, True, hp_color)
        self.screen.blit(text, (20, 50))

        hp_color = GREEN if self.combat_state.enemy_hp > 10 else RED
        text = self.font.render(enemy_hp_text, True, hp_color)
        self.screen.blit(text, (20, 80))

        # Énergie
        energy_text = f"Énergie: {self.combat_state.energy}/{ENERGY_PER_TURN}"
        text = self.font.render(energy_text, True, BLUE)
        self.screen.blit(text, (20, 110))

        # Plateau ennemi
        for i in range(BOARD_SLOTS):
            rect = self.get_board_slot_rect(i, False)
            pygame.draw.rect(self.screen, MID_GRAY, rect, border_radius=10)
            pygame.draw.rect(self.screen, RED, rect, 2, border_radius=10)

            unit = self.combat_state.enemy_board[i]
            if unit:
                self.draw_unit_card(rect, unit.card, False)

        # Plateau joueur
        for i in range(BOARD_SLOTS):
            rect = self.get_board_slot_rect(i, True)

            # Highlight si hover avec carte
            if self.hover_slot == i and self.selected_card is not None:
                if self.combat_state.player_board[i] is None:
                    pygame.draw.rect(self.screen, GREEN, rect, border_radius=10)
                else:
                    pygame.draw.rect(self.screen, MID_GRAY, rect, border_radius=10)
            else:
                pygame.draw.rect(self.screen, MID_GRAY, rect, border_radius=10)

            pygame.draw.rect(self.screen, BLUE, rect, 2, border_radius=10)

            unit = self.combat_state.player_board[i]
            if unit:
                self.draw_unit_card(rect, unit.card, True)

        # Main du joueur
        for i, card in enumerate(self.hand):
            if i == self.selected_card:
                continue  # On la dessine après pour qu'elle soit au-dessus

            rect = self.get_hand_card_rect(i)
            self.draw_hand_card(rect, card)

        # Carte sélectionnée (suit la souris)
        if self.selected_card is not None:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            rect = pygame.Rect(mouse_x - 60, mouse_y - 80, 120, 160)
            self.draw_hand_card(rect, self.hand[self.selected_card])

        # Bouton fin de tour
        button_rect = pygame.Rect(SCREEN_WIDTH - 180, SCREEN_HEIGHT - 80, 160, 50)
        pygame.draw.rect(self.screen, GREEN, button_rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, button_rect, 3, border_radius=10)

        button_text = self.font.render("FIN DU TOUR", True, WHITE)
        button_text_rect = button_text.get_rect(center=button_rect.center)
        self.screen.blit(button_text, button_text_rect)

        # Journal de combat (derniers messages)
        y = SCREEN_HEIGHT - 250
        for message in self.combat_state.combat_log[-5:]:
            text = self.small_font.render(message, True, LIGHT_GRAY)
            self.screen.blit(text, (SCREEN_WIDTH - 400, y))
            y += 20

    def draw_unit_card(self, rect: pygame.Rect, card: Card, is_player: bool):
        """Dessine une carte unité sur le plateau"""
        # Fond
        color = card.color if is_player else tuple(c // 2 for c in card.color)
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=10)

        # Nom
        name = card.name[:12] + "..." if len(card.name) > 12 else card.name
        text = self.small_font.render(name, True, WHITE)
        text_rect = text.get_rect(centerx=rect.centerx, y=rect.y + 5)
        self.screen.blit(text, text_rect)

        # Stats
        stats_y = rect.y + 40

        # ATK
        atk_text = f"ATK: {card.get_effective_atk()}"
        color = RED if card.current_atk < card.base_atk else WHITE
        text = self.font.render(atk_text, True, color)
        self.screen.blit(text, (rect.x + 10, stats_y))

        # DUR
        dur_text = f"DUR: {card.current_dur}"
        color = RED if card.current_dur < card.base_dur else WHITE
        text = self.font.render(dur_text, True, color)
        self.screen.blit(text, (rect.x + 10, stats_y + 30))

        # SPD
        spd_text = f"SPD: {card.current_spd}"
        text = self.font.render(spd_text, True, WHITE)
        self.screen.blit(text, (rect.x + 10, stats_y + 60))

        # Boucliers
        if card.shields > 0:
            shield_text = f"🛡 {card.shields}"
            text = self.font.render(shield_text, True, LIGHT_GRAY)
            self.screen.blit(text, (rect.x + 10, stats_y + 90))

        # Statuts
        status_y = rect.bottom - 25
        status_x = rect.x + 5
        for status, value in card.permanent_statuses.items():
            if value > 0:
                # Icône de statut
                status_colors = {
                    StatusEffect.VENIN: GREEN,
                    StatusEffect.BRULURE: ORANGE,
                    StatusEffect.SAIGNEMENT: RED,
                    StatusEffect.FRACTURE: LIGHT_GRAY,
                    StatusEffect.MALEDICTION: PURPLE,
                    StatusEffect.EROSION: (100, 100, 50)
                }
                color = status_colors.get(status, WHITE)
                pygame.draw.circle(self.screen, color, (status_x, status_y), 8)

                # Valeur
                text = self.small_font.render(str(value), True, WHITE)
                self.screen.blit(text, (status_x - 3, status_y - 8))

                status_x += 20

    def draw_hand_card(self, rect: pygame.Rect, card: Card):
        """Dessine une carte dans la main"""
        # Fond
        color = card.color
        pygame.draw.rect(self.screen, color, rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, rect, 3, border_radius=10)

        # Coût
        cost_rect = pygame.Rect(rect.x + 5, rect.y + 5, 25, 25)
        pygame.draw.circle(self.screen, BLUE, (rect.x + 17, rect.y + 17), 12)
        cost_text = self.font.render(str(card.cost), True, WHITE)
        cost_text_rect = cost_text.get_rect(center=(rect.x + 17, rect.y + 17))
        self.screen.blit(cost_text, cost_text_rect)

        # Nom
        name = card.name[:10] + "..." if len(card.name) > 10 else card.name
        text = self.small_font.render(name, True, WHITE)
        text_rect = text.get_rect(centerx=rect.centerx, y=rect.y + 35)
        self.screen.blit(text, text_rect)

        # Stats
        stats_text = f"{card.get_effective_atk()}/{card.current_dur}/{card.current_spd}"
        text = self.font.render(stats_text, True, WHITE)
        text_rect = text.get_rect(centerx=rect.centerx, y=rect.y + 60)
        self.screen.blit(text, text_rect)

        # Description
        desc_lines = []
        if card.description:
            words = card.description.split()
            line = ""
            for word in words:
                if len(line + word) < 15:
                    line += word + " "
                else:
                    desc_lines.append(line.strip())
                    line = word + " "
            if line:
                desc_lines.append(line.strip())

        y = rect.y + 90
        for line in desc_lines[:3]:
            text = self.small_font.render(line, True, LIGHT_GRAY)
            text_rect = text.get_rect(centerx=rect.centerx, y=y)
            self.screen.blit(text, text_rect)
            y += 18

        # Si carte non jouable (pas assez d'énergie)
        if self.combat_state and card.cost > self.combat_state.energy:
            overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, rect)

    def draw_reward(self):
        """Offer an explicit choice of up to three cards, including skip."""
        self.screen.fill(DARK_GRAY)
        title = self.big_font.render(f"Victoire ! Étape {self.stage} : choisissez une carte", True, GOLD)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 90)))
        instruction = self.small_font.render("Cliquez une carte, utilisez 1/2/3 ou S pour passer.", True, WHITE)
        self.screen.blit(instruction, instruction.get_rect(center=(SCREEN_WIDTH // 2, 140)))
        for index, card in enumerate(self.reward_options):
            rect = self.reward_rect(index)
            pygame.draw.rect(self.screen, card.color, rect, border_radius=12)
            pygame.draw.rect(self.screen, GOLD, rect, 3, border_radius=12)
            fields = [
                (self.font, f"{index + 1}. {card.name[:23]}", 34),
                (self.font, f"Coût : {card.cost}", 84),
                (self.font, f"ATQ {card.current_atk} · DUR {card.current_dur} · VIT {card.current_spd}", 128),
                (self.small_font, card.description[:50], 180),
            ]
            for font, text, offset in fields:
                display = font.render(text, True, WHITE)
                self.screen.blit(display, display.get_rect(center=(rect.centerx, rect.y + offset)))
        skip = self.reward_skip_rect()
        pygame.draw.rect(self.screen, MID_GRAY, skip, border_radius=8)
        pygame.draw.rect(self.screen, WHITE, skip, 2, border_radius=8)
        label = self.font.render("Passer (S)", True, WHITE)
        self.screen.blit(label, label.get_rect(center=skip.center))

    def draw_victory(self):
        """Dessine l'écran de victoire"""
        self.screen.fill(DARK_GRAY)

        # Animation d'étoiles
        for i in range(50):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.circle(self.screen, WHITE, (x, y), 1)

        # Titre
        title = self.big_font.render("VICTOIRE!", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)

        subtitle = self.font.render("Vous avez survécu aux 10 combats!", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 260))
        self.screen.blit(subtitle, subtitle_rect)

        # Instructions
        text = self.font.render("Appuyez sur ESPACE pour retourner au menu", True, LIGHT_GRAY)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(text, text_rect)

    def draw_defeat(self):
        """Dessine l'écran de défaite"""
        self.screen.fill(DARK_GRAY)

        # Titre
        title = self.big_font.render("DÉFAITE", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)

        subtitle = self.font.render(f"Vous avez atteint le combat {self.stage}", True, WHITE)
        subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 260))
        self.screen.blit(subtitle, subtitle_rect)

        # Instructions
        text = self.font.render("Appuyez sur ESPACE pour retourner au menu", True, LIGHT_GRAY)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(text, text_rect)

    def draw_particles(self):
        """Dessine les particules"""
        for particle in self.particles:
            alpha = int(255 * particle['life'])
            color = (*particle['color'], alpha)
            size = int(particle['size'] * particle['life'])
            if size > 0:
                pygame.draw.circle(self.screen, particle['color'],
                                   (int(particle['x']), int(particle['y'])),
                                   size)

    def draw(self):
        """Dessine l'écran selon l'état"""
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "combat":
            self.draw_combat()
        elif self.state == "reward":
            self.draw_reward()
        elif self.state == "victory":
            self.draw_victory()
        elif self.state == "defeat":
            self.draw_defeat()

        # Particules par-dessus tout
        self.draw_particles()

        pygame.display.flip()

    def update(self, dt):
        """Met à jour la logique du jeu"""
        self.animation_timer += dt

        # Mettre à jour les particules
        self.update_particles(dt)

    def run(self):
        """Boucle principale du jeu"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════╗
    ║         BESTIAIRE: Écorces & Échos      ║
    ║              Version 1.0.0               ║
    ║                                          ║
    ║     Roguelite Deckbuilding Permanent    ║
    ╚══════════════════════════════════════════╝

    CONTRÔLES:
    - Drag & Drop les cartes de la main vers le plateau
    - ENTRÉE ou bouton : Fin du tour
    - ESPACE : Confirmer / Nouvelle partie
    - ESC : Retour au menu

    RÈGLES:
    - Les dégâts sont PERMANENTS pour toute la run
    - Survivez à 10 combats pour gagner
    - Le dernier combat est un BOSS
    """)

    game = BestiaireGame()
    game.run()