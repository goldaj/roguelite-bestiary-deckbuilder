from core.entities import CardDatabase, RunState, CombatState
from core.combat import CombatResolver
import pytest


def test_combat_rewards_really_expand_deck():
    db = CardDatabase()
    card_ids = ["forest_spine_frog", "dunes_solar_fennec"]
    state = RunState(current_deck=[], fragments=2)
    state.process_node_rewards({"fragments": 20, "genes": 1, "cards": card_ids})
    assert state.fragments == 22
    assert state.genes == 1
    assert [card.id for card in state.current_deck] == card_ids
    assert state.current_deck[0] is not db.create_card(card_ids[0])


def test_invalid_reward_card_cannot_partially_credit_run():
    state = RunState(current_deck=[], fragments=7)
    with pytest.raises(ValueError):
        state.process_node_rewards({"fragments": 25, "cards": ["unknown_card"]})
    assert state.fragments == 7
    assert not state.current_deck


def test_generated_loot_is_real_and_seeded():
    db = CardDatabase()
    a = CombatResolver(CombatState(), rng_seed=91)
    b = CombatResolver(CombatState(), rng_seed=91)
    ids = [a._generate_reward_card() for _ in range(20)]
    assert ids == [b._generate_reward_card() for _ in range(20)]
    assert len(set(ids)) > 1
    assert all(card in db.cards for card in ids)
