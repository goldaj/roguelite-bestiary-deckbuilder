"""Functional tests for the actual collectible catalogue and merchant/capture flow."""
import random
from collections import Counter

from core.entities import CardDatabase, Biome, Rarity, RunState, StatusEffect
from core.progression import MerchantSystem, EventSystem, MetaProgression


def test_complete_catalogue_is_playable():
    db = CardDatabase()
    assert len(db.cards) == 90
    assert len({db.cards[k]["biome"] for k in db.cards}) >= 6
    for card_id in db.cards:
        card = db.create_card(card_id)
        assert card.id == card_id
        assert card.base_dur > 0
    venom = db.create_card("forest_azure_spider")
    assert venom.on_attack[0]["effect"] == StatusEffect.VENIN
    assert db.create_card("forest_azure_spider") is not venom


def test_capture_is_not_a_permanent_placeholder(monkeypatch):
    db = CardDatabase()
    events = EventSystem(db)
    seen = {events._generate_random_card(3).id for _ in range(100)}
    assert len(seen) > 1
    assert seen.issubset(db.cards)
    run = RunState(current_deck=[])
    events.process_event("wounded_specimen", 0, run)
    assert run.current_deck[0].current_dur <= run.current_deck[0].base_dur
    with __import__("pytest").raises(ValueError):
        events.process_event("wounded_specimen", -1, run)


def test_merchants_sell_real_biome_cards():
    db = CardDatabase()
    merchant = MerchantSystem(db)
    for biome in (Biome.FORET, Biome.DUNES, Biome.FALAISES, Biome.FLEUVE):
        for act in (1, 2, 3):
            stock = merchant.generate_shop(act, biome, random.Random(42))
            assert len(stock["cards"]) >= 4
            for offer in stock["cards"]:
                assert offer["card_id"] in db.cards
                assert db.cards[offer["card_id"]]["biome"] == biome
                assert offer["rarity"] == db.cards[offer["card_id"]]["rarity"]


def test_first_victory_unlock_persists(tmp_path):
    meta = MetaProgression(tmp_path)
    state = RunState(current_deck=[], current_act=3, score=1500)
    meta.complete_run(state, victory=True)
    assert "first_victory" in meta.profile["achievements"]
    assert "variant_mist_scythe" in meta.profile["unlocked_cards"]
    assert MetaProgression(tmp_path).profile["achievements"] == ["first_victory"]
    meta.complete_run(state, victory=True)
    assert meta.profile["achievements"].count("first_victory") == 1
