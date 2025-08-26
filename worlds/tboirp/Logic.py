from BaseClasses import CollectionState
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import TBOIWorld

class TBOILogic:
    player: int
    easier_lost: bool # Whether the Lost needs its mantle to have its locations be in logic
    items_in_pool: list[str] # Items that exist in the pool

    normal_character_items = [
        "Isaac", "Magdalene", "Cain", "Judas", "???",
        "Eve", "Samson",
        "Azazel", "Lazarus", "Eden", "Lost",
        "Lilith", "Keeper",
        "Apollyon", "Forgotten",
        "Bethany", "Jacob and Esau"
    ]

    tainted_character_items = [
        "The Broken", "The Dauntless", "The Hoarder", "The Deceiver", "The Soiled",
        "The Curdled", "The Savage",
        "The Benighted", "The Enigma", "The Capricious", "The Baleful",
        "The Harlot", "The Miser",
        "The Empty", "The Fettered",
        "The Zealot", "The Deserter"
    ]

    def __init__(self, world: "TBOIWorld"):
        self.player = world.player
        self.easier_lost = world.options.lost_difficulty.value == world.options.lost_difficulty.option_hard
        self.items_in_pool = []

    def has_the_lost(self, state: CollectionState) -> bool:
        """
        'True' when Lost difficulty is set to Hard and the player has the Lost's Holy Mantle item.
        """
        if not self.easier_lost:
            return state.has("Lost", self.player)

        return state.has_all(["Lost", "Lost Holds Holy Mantle"], self.player)

    def has_all_normal_characters(self, state: CollectionState) -> bool:
        """
        'True' when the player has all non-tainted characters.
        """
        return state.has_all(self.normal_character_items, self.player) and self.has_the_lost(state)

    def has_all_characters(self, state: CollectionState) -> bool:
        """
        'True' when the player has all characters.
        """
        return state.has_all(self.normal_character_items + self.tainted_character_items, self.player) and self.has_the_lost(state)

    def can_reach_all_regions(self, state: CollectionState, regions: list[str]) -> bool:
        """
        'True' when the player is able to reach all the given regions.
        """
        for name in regions:
            if not state.can_reach_region(name, self.player):
                return False

        return True

    def can_reach_big4(self, state: CollectionState) -> bool:
        """
        'True' when the player can reach Isaac, Satan, ???, and The Lamb.
        """
        return self.can_reach_all_regions(state, ["Cathedral", "The Chest", "Sheol", "Dark Room"])

    def can_reach_br_hush(self, state: CollectionState) -> bool:
        """
        'True' when the player can reach Boss Rush and Hush.
        """
        return self.can_reach_all_regions(state, ["Chapter 3", "Blue Womb"])

    def can_reach_all_marks(self, state: CollectionState) -> bool:
        """
        'True' when the player is able to reach all marks as any character.
        """
        return self.can_reach_all_regions(state, [
            "Chapter 3", "Chapter 4",
            "Dark Room", "The Chest", "Mega Satan",
            "Blue Womb", "The Void",
            "Corpse", "Ascent",
            "Greed Mode", "Greedier Mode"
        ])

    def can_do_rescue(self, as_character: str, state: CollectionState) -> bool:
        """
        'True' when the player has the given character, and Cracked Key.
        """
        return state.has_all([as_character, "Cracked Key"], self.player)

    def has_quantum(self, name: str, state: CollectionState) -> bool:
        """
        'True' if the item is not in the pool (not randomized), or the player has collected it.
        """
        if name not in self.items_in_pool: # Item is not randomized
            return True

        return state.has(name, self.player)