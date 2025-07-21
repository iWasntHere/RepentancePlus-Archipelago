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

def has_all_normal_characters(player: int, state: CollectionState, world: "TBOIWorld"):
    return has_all(normal_character_items, state, world, player)

def has_all_characters(player: int, state: CollectionState, world: "TBOIWorld"):
    return has_all(normal_character_items + tainted_character_tems, state, world, player)

def can_reach_all_regions(player: int, state: CollectionState, regions: list[str]):
    for name in regions:
        if not state.can_reach_region(name, player):
            return False

    return True

def set_region_access_rule(mw: MultiWorld, player: int, region: str, rule: CollectionRule):
    for entrance in mw.get_region(region, player).entrances:
        entrance.access_rule = rule

def has(name: str, state: CollectionState, world: "TBOIWorld", player: int):
    return name in world.default_items or state.has(name, player)

def has_all(names: list[str], state: CollectionState, world: "TBOIWorld", player: int):
    for name in names:
        if not has(name, state, world, player):
            return False
    
    return True

def has_any(names: list[str], state: CollectionState, world: "TBOIWorld", player: int):
    for name in names:
        if has(name, state, world, player):
            return True

    return False

def make_rules(world: "TBOIWorld"):
    ply = world.player
    mw = world.multiworld

    mw.completion_condition[ply] = lambda state: state.has("Victory", ply)
    mw.get_location("All Co-Op Babies Found", ply).place_locked_item(world.create_item("Victory"))

    set_region_access_rule(mw, ply, "Cellar", lambda state: has("The Cellar", state, world, ply))
    set_region_access_rule(mw, ply, "Burning Basement", lambda state: has("Burning Basement", state, world, ply))

    set_region_access_rule(mw, ply, "Downpour", lambda state: has("A Secret Exit", state, world, ply))
    set_region_access_rule(mw, ply, "Dross", lambda state: has_all(["A Secret Exit", "Dross"], state, world, ply))

    set_region_access_rule(mw, ply, "Catacombs", lambda state: has("The Catacombs", state, world, ply))
    set_region_access_rule(mw, ply, "Flooded Caves", lambda state: has("Flooded Caves", state, world, ply))

    set_region_access_rule(mw, ply, "Mines", lambda state: has("A Secret Exit", state, world, ply))
    set_region_access_rule(mw, ply, "Ashpit", lambda state: has_all(["A Secret Exit", "Ashpit"], state, world, ply))

    set_region_access_rule(mw, ply, "Necropolis", lambda state: has("The Necropolis", state, world, ply))
    set_region_access_rule(mw, ply, "Dank Depths", lambda state: has("Dank Depths", state, world, ply))

    set_region_access_rule(mw, ply, "Mausoleum", lambda state: has("A Secret Exit", state, world, ply))
    set_region_access_rule(mw, ply, "Gehenna", lambda state: has_all(["A Secret Exit", "Gehenna"], state, world, ply))

    set_region_access_rule(mw, ply, "Corpse", lambda state: has_all(["A Secret Exit"], state, world, ply))

    set_region_access_rule(mw, ply, "The Womb", lambda state: has("The Womb", state, world, ply))
    set_region_access_rule(mw, ply, "Scarred Womb", lambda state: has_all(["The Womb", "Scarred Womb"], state, world, ply))

    set_region_access_rule(mw, ply, "Blue Womb", lambda state: has("Blue Womb", state, world, ply))

    set_region_access_rule(mw, ply, "Sheol", lambda state: has("It Lives!", state, world, ply))
    set_region_access_rule(mw, ply, "Cathedral", lambda state: has("It Lives!", state, world, ply))

    set_region_access_rule(mw, ply, "Dark Room", lambda state: has("The Negative", state, world, ply))
    set_region_access_rule(mw, ply, "The Chest", lambda state: has("The Polaroid", state, world, ply))

    set_region_access_rule(mw, ply, "Mega Satan", lambda state: has("Angels", state, world, ply))
    set_region_access_rule(mw, ply, "The Void", lambda state: has("New Area", state, world, ply))
    set_region_access_rule(mw, ply, "Ascent", lambda state: has("A Strange Door", state, world, ply) and has_any(["The Polaroid", "The Negative"], state, world, ply))

    set_region_access_rule(mw, ply, "Greedier Mode", lambda state: has("Greedier!", state, world, ply))
