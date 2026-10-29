"""Behavioral tests for the actual playable BestiaireGame, without a display."""
import importlib.util
from pathlib import Path
import random
import sys
import types
import unittest
from unittest.mock import Mock, patch

PATH = Path(__file__).resolve().parents[1] / "bestiaire_game.py"


class FakeRect:
    def __init__(self, x, y, w, h):
        self.x, self.y, self.width, self.height = x, y, w, h

    def collidepoint(self, point):
        x, y = point
        return self.x <= x < self.x + self.width and self.y <= y < self.y + self.height


def load_game_module():
    pygame = types.ModuleType("pygame")
    pygame.Rect = FakeRect
    spec = importlib.util.spec_from_file_location("bestiaire_reward_under_test", PATH)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {"pygame": pygame}):
        sys.modules[spec.name] = module
        try:
            spec.loader.exec_module(module)
        finally:
            sys.modules.pop(spec.name, None)
    return module


class RewardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_game_module()

    def setUp(self):
        random.seed(20261029)
        module = self.module
        self.game = module.BestiaireGame.__new__(module.BestiaireGame)
        self.game.cards = module.create_all_cards()
        self.game.player_deck = [self.game.cards[0].clone(), self.game.cards[1].clone()]
        self.game.stage = 1
        self.game.max_stages = 10
        self.game.state = "combat"
        self.game.reward_options = []
        self.game.combat_state = Mock()
        self.game.combat_state.is_combat_over.return_value = "victory"

    def test_victory_does_not_force_a_random_card(self):
        initial = len(self.game.player_deck)
        self.game.end_turn()
        self.assertEqual(self.game.stage, 2)
        self.assertEqual(self.game.state, "reward")
        self.assertEqual(len(self.game.player_deck), initial)
        self.assertEqual(len(self.game.reward_options), 3)
        self.assertEqual(len({card.id for card in self.game.reward_options}), 3)
        self.assertTrue(any(card.cost <= self.module.ENERGY_PER_TURN
                            for card in self.game.reward_options))

    def test_selecting_reward_adds_one_real_card_then_starts_combat(self):
        self.game.end_turn()
        chosen = self.game.reward_options[1]
        self.assertTrue(self.game.select_reward(1))
        self.assertEqual(self.game.state, "combat")
        self.assertEqual(len(self.game.player_deck), 3)
        self.assertEqual(self.game.player_deck[-1].id, chosen.id)
        self.assertEqual(self.game.stage, 2)
        self.assertEqual(self.game.reward_options, [])
        self.assertFalse(self.game.select_reward(0))
        self.assertIsNotNone(self.game.combat_state)
        self.assertGreater(len(self.game.hand), 0)

    def test_skip_is_valid_with_no_forced_reward(self):
        self.game.end_turn()
        self.assertTrue(self.game.select_reward(None))
        self.assertEqual(len(self.game.player_deck), 2)
        self.assertEqual(self.game.stage, 2)
        self.assertEqual(self.game.state, "combat")

    def test_invalid_choice_does_not_modify_state(self):
        self.game.end_turn()
        old = len(self.game.player_deck)
        for bad in (-1, 3, True, "1"):
            self.assertFalse(self.game.select_reward(bad))
        self.assertEqual(self.game.state, "reward")
        self.assertEqual(len(self.game.player_deck), old)

    def test_click_first_reward_and_skip_button(self):
        self.game.end_turn()
        card_id = self.game.reward_options[0].id
        self.game.handle_click((185, 220))
        self.assertEqual(self.game.player_deck[-1].id, card_id)
        self.assertEqual(self.game.state, "combat")
        self.game.combat_state = Mock()
        self.game.combat_state.is_combat_over.return_value = "victory"
        self.game.end_turn()
        self.assertEqual(self.game.state, "reward")
        before = len(self.game.player_deck)
        self.game.handle_click((self.module.SCREEN_WIDTH // 2, 540))
        self.assertEqual(len(self.game.player_deck), before)

    def test_final_boss_ends_run_without_extra_reward(self):
        self.game.stage = self.game.max_stages
        self.game.end_turn()
        self.assertEqual(self.game.state, "victory")
        self.assertEqual(self.game.stage, self.game.max_stages + 1)
        self.assertEqual(self.game.reward_options, [])


if __name__ == "__main__":
    unittest.main()
