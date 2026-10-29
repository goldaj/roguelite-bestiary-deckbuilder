"""Headless starter choices and economy constraints on the real 90-card catalog."""
import random
import unittest

from core.starter_decks import ARCHETYPES, DESCRIPTIONS, starting_deck
from tests.test_card_reward_choice import load_game_module


class StarterDeckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = load_game_module()
        cls.catalogue = cls.module.create_all_cards()

    def test_real_catalogue_supports_all_three_affordable_archetypes(self):
        self.assertEqual(len(self.catalogue), 90)
        for kind in ARCHETYPES:
            for seed in range(40):
                deck = starting_deck(self.catalogue, kind, rng=random.Random(seed))
                self.assertEqual(len(deck), 12)
                self.assertEqual(len({card.id for card in deck}), 12)
                self.assertGreaterEqual(sum(card.cost <= 1 for card in deck), 4)
                self.assertGreaterEqual(sum(card.cost <= 2 for card in deck), 8)
                self.assertTrue(all(card.cost <= self.module.ENERGY_PER_TURN for card in deck))
                self.assertIn(kind, DESCRIPTIONS)

    def test_seed_reproduces_selection_without_resetting_global_random(self):
        a = [card.id for card in starting_deck(self.catalogue, "assaut", rng=random.Random(4))]
        b = [card.id for card in starting_deck(self.catalogue, "assaut", rng=random.Random(4))]
        c = [card.id for card in starting_deck(self.catalogue, "assaut", rng=random.Random(8))]
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_archetypes_yield_distinct_card_pools(self):
        rows = {
            archetype: {card.id for card in starting_deck(self.catalogue, archetype, rng=random.Random(5))}
            for archetype in ARCHETYPES
        }
        self.assertNotEqual(rows["assaut"], rows["rempart"])
        self.assertNotEqual(rows["equilibre"], rows["assaut"])

    def test_new_run_integrates_selected_template_clones(self):
        game = self.module.BestiaireGame.__new__(self.module.BestiaireGame)
        game.cards = self.catalogue
        game.max_stages = 10
        game.start_new_run("rempart")
        self.assertEqual(game.starter_archetype, "rempart")
        self.assertEqual(game.state, "combat")
        self.assertEqual(len(game.player_deck), 12)
        self.assertEqual(len(game.hand), 5)
        self.assertEqual(len(game.draw_pile), 7)
        self.assertEqual(len({id(c) for c in game.player_deck}), 12)
        self.assertTrue(all(c is not original for c in game.player_deck for original in game.cards))
        self.assertGreaterEqual(sum(c.cost <= 1 for c in game.player_deck), 4)

    def test_menu_mouse_selection_starts_requested_game(self):
        for index, kind in enumerate(ARCHETYPES):
            game = self.module.BestiaireGame.__new__(self.module.BestiaireGame)
            game.cards = self.catalogue
            game.max_stages = 10
            game.state = "menu"
            rect = game.starter_rect(index)
            game.handle_click((rect.x + 5, rect.y + 5))
            self.assertEqual(game.starter_archetype, kind)
            self.assertEqual(game.state, "combat")

    def test_invalid_or_too_small_catalogue_fails_closed(self):
        with self.assertRaises(ValueError):
            starting_deck(self.catalogue, "nonexistent")
        with self.assertRaises(ValueError):
            starting_deck(self.catalogue[:5], "equilibre")
        with self.assertRaises(ValueError):
            starting_deck(self.catalogue, "equilibre", size=True)


if __name__ == "__main__":
    unittest.main()
