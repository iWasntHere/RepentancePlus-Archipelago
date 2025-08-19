from typing import TYPE_CHECKING

from BaseClasses import MultiWorld, CollectionState
from ..generic.Rules import CollectionRule

if TYPE_CHECKING:
    from . import TBOIWorld

def set_region_access_rule(mw: MultiWorld, player: int, region: str, rule: CollectionRule):
    for entrance in mw.get_region(region, player).entrances:
        entrance.access_rule = rule

def make_rules(world: "TBOIWorld"):
    ply = world.player
    mw = world.multiworld

    mw.completion_condition[ply] = lambda state: state.has("Victory", ply)
    mw.get_location("Victory (Baby Hunt)", ply).place_locked_item(world.create_item("Victory"))

    set_region_access_rule(mw, ply, "Cellar", lambda state: state.has("The Cellar", ply))
    set_region_access_rule(mw, ply, "Burning Basement", lambda state: state.has("Burning Basement", ply))

    set_region_access_rule(mw, ply, "Downpour", lambda state: state.has("A Secret Exit", ply))
    set_region_access_rule(mw, ply, "Dross", lambda state: state.has_all(["A Secret Exit", "Dross"],  ply))

    set_region_access_rule(mw, ply, "Catacombs", lambda state: state.has("The Catacombs", ply))
    set_region_access_rule(mw, ply, "Flooded Caves", lambda state: state.has("Flooded Caves", ply))

    set_region_access_rule(mw, ply, "Mines", lambda state: state.has("A Secret Exit", ply))
    set_region_access_rule(mw, ply, "Ashpit", lambda state: state.has_all(["A Secret Exit", "Ashpit"], ply))

    set_region_access_rule(mw, ply, "Necropolis", lambda state: state.has("The Necropolis", ply))
    set_region_access_rule(mw, ply, "Dank Depths", lambda state: state.has("Dank Depths", ply))

    set_region_access_rule(mw, ply, "Mausoleum", lambda state: state.has("A Secret Exit", ply))
    set_region_access_rule(mw, ply, "Gehenna", lambda state: state.has_all(["A Secret Exit", "Gehenna"], ply))

    set_region_access_rule(mw, ply, "Corpse", lambda state: state.has_all(["A Secret Exit"], ply))

    set_region_access_rule(mw, ply, "The Womb", lambda state: state.has("The Womb", ply))
    set_region_access_rule(mw, ply, "Utero", lambda state: state.has("The Womb", ply))
    set_region_access_rule(mw, ply, "Scarred Womb", lambda state: state.has_all(["The Womb", "Scarred Womb"], ply))

    set_region_access_rule(mw, ply, "Blue Womb", lambda state: state.has("Blue Womb", ply))

    set_region_access_rule(mw, ply, "Sheol", lambda state: state.has("It Lives!", ply))
    set_region_access_rule(mw, ply, "Cathedral", lambda state: state.has("It Lives!", ply))

    set_region_access_rule(mw, ply, "Dark Room", lambda state: state.has("The Negative", ply))
    set_region_access_rule(mw, ply, "The Chest", lambda state: state.has("The Polaroid", ply))

    set_region_access_rule(mw, ply, "Mega Satan", lambda state: state.has("Angels", ply))
    set_region_access_rule(mw, ply, "The Void", lambda state: state.has("New Area", ply))

    # Womb is required here because neither polaroid nor negative will properly drop without it
    set_region_access_rule(mw, ply, "Ascent", lambda state: state.has("A Strange Door", ply) and state.has_any(["The Polaroid", "The Negative"], ply) and state.has("The Womb", ply))

    set_region_access_rule(mw, ply, "Greedier Mode", lambda state: state.has("Greedier!", ply))
