"""Three repeatable starting-deck profiles; no Pygame dependency.

The draw remains varied, but starting hands contain cards affordable with
the game's three-energy economy. Advice: balance *hypotheses*, not win-rate proof.
"""
from __future__ import annotations

import random

ARCHETYPES = ("equilibre", "assaut", "rempart")
DESCRIPTIONS = {
    "equilibre": "Équilibré : attaque et endurance",
    "assaut": "Assaut : privilégie attaque et vitesse",
    "rempart": "Rempart : privilégie endurance et protection",
}


def strength(card, archetype: str) -> float:
    attack = max(0, float(card.base_atk))
    durability = max(0, float(card.base_dur))
    speed = max(0, float(card.base_spd))
    cost = max(0, float(card.cost))
    keywords = {getattr(word, "name", str(word)) for word in getattr(card, "keywords", [])}
    guards = int("GARDE" in keywords) + int("CARAPACE" in keywords)
    if archetype == "assaut":
        return 2.5 * attack + 0.65 * speed + 0.15 * durability - 0.5 * cost
    if archetype == "rempart":
        return 1.75 * durability + 0.45 * attack + 1.4 * guards - 0.3 * cost
    return attack + 0.8 * durability + 0.25 * speed + 0.5 * guards - 0.35 * cost


def starting_deck(cards, archetype="equilibre", *, rng=None, size=12, energy=3):
    """Return distinct templates; caller clones them before play.

    For 12-card decks: at least 4 cards cost <=1 and 8 cost <=2; every
    card costs <=3. Fail rather than silently build a broken opening.
    """
    if archetype not in ARCHETYPES:
        raise ValueError("Unknown starter archetype")
    if type(size) is not int or not 1 <= size <= 30:
        raise ValueError("Unsupported deck size")
    if type(energy) is not int or energy < 2:
        raise ValueError("Unsupported energy budget")
    rng = rng if rng is not None else random
    unique = {card.id: card for card in cards}
    affordable = [card for card in unique.values() if 0 <= card.cost <= energy]
    if len(affordable) < size:
        raise ValueError("Not enough distinct affordable cards to form a starting deck")

    selected = []
    selected_ids = set()

    def choose(pool, count):
        choices = [card for card in pool if card.id not in selected_ids]
        if len(choices) < count:
            raise ValueError("Not enough affordable cards for starter curve")
        # Bias toward profile while retaining meaningful seed-driven variation.
        choices.sort(key=lambda card: (-strength(card, archetype), card.id))
        candidates = choices[:max(count, min(len(choices), count * 3))]
        for card in rng.sample(candidates, count):
            selected.append(card)
            selected_ids.add(card.id)

    cheap_needed = min(size, max(1, size // 3))
    medium_needed = min(size - cheap_needed, max(0, 2 * size // 3 - cheap_needed))
    choose([card for card in affordable if card.cost <= 1], cheap_needed)
    choose([card for card in affordable if card.cost <= min(2, energy)], medium_needed)
    choose(affordable, size - len(selected))
    rng.shuffle(selected)
    return selected
