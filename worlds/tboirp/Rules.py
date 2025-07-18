from typing import TYPE_CHECKING

from BaseClasses import MultiWorld, CollectionState
from ..generic.Rules import CollectionRule

if TYPE_CHECKING:
    from . import TBOIWorld

def can_reach_bluebaby_and_lamb(player: int, state: CollectionState):
    return can_reach_all_regions(player, state, ["Dark Room", "The Chest"])

def can_reach_all_marks(player: int, state: CollectionState):
    return can_reach_all_regions(player, state, [
        "Chapter 3", "Chapter 4",
        "Dark Room", "The Chest", "Mega Satan",
        "Blue Womb", "The Void",
        "Corpse", "Ascent",
        "Greed Mode", "Greedier Mode"
    ])

normal_character_items = [
    "Magdalene", "Cain", "Judas", "???",
    "Eve", "Samson",
    "Azazel", "Lazarus", "Eden", "Lost",
    "Lilith", "Keeper",
    "Apollyon", "Forgotten",
    "Bethany", "Jacob and Esau"
]

tainted_character_tems = [
    "The Broken", "The Dauntless", "The Hoarder", "The Deceiver", "The Soiled",
    "The Curdled", "The Savage",
    "The Benighted", "The Enigma", "The Capricious", "The Baleful",
    "The Harlot", "The Miser",
    "The Empty", "The Fettered",
    "The Zealot", "The Deserter"
]

def has_all_normal_characters(player: int, state: CollectionState):
    return state.has_all(normal_character_items, player)

def has_all_characters(player: int, state: CollectionState):
    return state.has_all(normal_character_items + tainted_character_tems, player)

def can_reach_all_regions(player: int, state: CollectionState, regions: list[str]):
    for name in regions:
        if not state.can_reach_region(name, player):
            return False

    return True

def set_region_access_rule(mw: MultiWorld, player: int, region: str, rule: CollectionRule):
    for entrance in mw.get_region(region, player).entrances:
        entrance.access_rule = rule

def make_rules(world: "TBOIWorld"):
    ply = world.player
    mw = world.multiworld

    mw.completion_condition[ply] = lambda state: state.has("Victory", ply)

    mw.get_location("All Co-Op Babies Found", ply).place_locked_item(world.create_item("Victory"))

    set_region_access_rule(mw, ply, "Cellar", lambda state: state.has("Cellar", ply))
    set_region_access_rule(mw, ply, "Burning Basement", lambda state: state.has("Burning Basement", ply))

    set_region_access_rule(mw, ply, "Downpour", lambda state: state.has("A Secret Exit", ply))
    set_region_access_rule(mw, ply, "Dross", lambda state: state.has_all(["A Secret Exit", "Dross"], ply))

    set_region_access_rule(mw, ply, "Catacombs", lambda state: state.has("Catacombs", ply))
    set_region_access_rule(mw, ply, "Flooded Caves", lambda state: state.has("Flooded Caves", ply))

    set_region_access_rule(mw, ply, "Mines", lambda state: state.has("A Secret Exit", ply))
    set_region_access_rule(mw, ply, "Ashpit", lambda state: state.has_all(["A Secret Exit", "Ashpit"], ply))

    set_region_access_rule(mw, ply, "Necropolis", lambda state: state.has("Necropolis", ply))
    set_region_access_rule(mw, ply, "Dank Depths", lambda state: state.has("Dank Depths", ply))

    set_region_access_rule(mw, ply, "Mausoleum", lambda state: state.has("A Secret Exit", ply))
    set_region_access_rule(mw, ply, "Gehenna", lambda state: state.has_all(["A Secret Exit", "Gehenna"], ply))

    set_region_access_rule(mw, ply, "Corpse", lambda state: state.has_all(["A Secret Exit"], ply))

    set_region_access_rule(mw, ply, "The Womb", lambda state: state.has("The Womb", ply))
    set_region_access_rule(mw, ply, "Scarred Womb", lambda state: state.has_all(["The Womb", "Scarred Womb"], ply))

    set_region_access_rule(mw, ply, "Blue Womb", lambda state: state.has("Blue Womb", ply))

    set_region_access_rule(mw, ply, "Sheol", lambda state: state.has("It Lives!", ply))
    set_region_access_rule(mw, ply, "Cathedral", lambda state: state.has("It Lives!", ply))

    set_region_access_rule(mw, ply, "Dark Room", lambda state: state.has("The Negative", ply))
    set_region_access_rule(mw, ply, "The Chest", lambda state: state.has("The Polaroid", ply))

    set_region_access_rule(mw, ply, "Mega Satan", lambda state: state.has("Angels", ply))
    set_region_access_rule(mw, ply, "The Void", lambda state: state.has("The Void", ply))
    set_region_access_rule(mw, ply, "Ascent", lambda state: state.has("A Strange Door", ply) and state.has_any(["The Polaroid", "The Negative"], ply))

    set_region_access_rule(mw, ply, "Greedier Mode", lambda state: state.has("Greedier!", ply))
