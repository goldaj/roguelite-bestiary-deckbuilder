"""Gameplay smoke tests for the actual Pygame launcher (headless SDL)."""
import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from bestiaire_game import (
    BestiaireGame, CombatState, BOARD_SLOTS,
    StatusEffect, create_all_cards,
)


@pytest.fixture
def game():
    instance = BestiaireGame()
    yield instance
    pygame.quit()


def test_launcher_loads_all_catalogue_cards(game):
    assert len(game.cards) == 90
    assert "forest_spine_frog" in {card.id for card in game.cards}
    assert "ruins_golem" in {card.id for card in game.cards}


def test_attacks_use_card_abilities_not_random_status(game):
    spider = next(card.clone() for card in game.cards if card.id == "forest_azure_spider")
    victim = next(card.clone() for card in game.cards if card.id == "forest_spine_frog")
    state = CombatState()
    state.add_unit(spider, 0, True)
    state.add_unit(victim, 0, False)
    state.attack(state.player_board[0], state.enemy_board[0])
    assert victim.permanent_statuses[StatusEffect.VENIN] == 1

    other = next(card.clone() for card in game.cards if card.id == "dunes_solar_fennec")
    state.add_unit(other, 1, True)
    previous = dict(victim.permanent_statuses)
    for _ in range(10):
        state.attack(state.player_board[1], state.enemy_board[0])
    assert victim.permanent_statuses == previous


def test_draw_pile_is_finite_and_card_instances_are_not_duplicated(game):
    game.start_new_run()
    assert len(game.player_deck) == 12
    assert len(game.hand) == 5
    assert len(game.draw_pile) == 7
    assert len({id(x) for x in game.hand + game.draw_pile}) == 12
    game.hand.pop()
    game.draw_cards(4)
    assert len(game.hand) == 5
    assert len(game.draw_pile) == 6
    game.draw_cards(100)
    assert len(game.hand) == 5
    assert len({id(x) for x in game.hand + game.draw_pile}) == 11


def test_end_turn_refills_hand_and_captures_new_card(game):
    game.start_new_run()
    game.hand.pop()
    game.combat_state.player_hp = 999
    game.combat_state.enemy_hp = 999
    game.end_turn()
    assert game.state == "combat"
    assert len(game.hand) == 5

    wounded = game.hand[0]
    wounded.current_dur -= 1
    before = len(game.player_deck)
    game.combat_state.enemy_hp = -1
    game.end_turn()
    assert game.stage == 2
    assert len(game.player_deck) == before + 1
    assert wounded in game.player_deck
    assert wounded.current_dur == wounded.base_dur - 1
    assert any("Carte capturée" in line for line in game.combat_state.combat_log)


def test_dead_cards_are_not_revived_on_next_stage(game):
    game.start_new_run()
    lost = game.hand[0]
    lost.current_dur = -1
    game.combat_state.player_hp = 999
    game.combat_state.enemy_hp = -1
    game.end_turn()
    assert lost not in game.player_deck
    assert all(card.current_dur > 0 for card in game.hand + game.draw_pile)


def test_defeat_ends_run_without_loot(game):
    game.start_new_run()
    before = len(game.player_deck)
    game.combat_state.player_hp = -200
    game.end_turn()
    assert game.state == "defeat"
    assert len(game.player_deck) == before
