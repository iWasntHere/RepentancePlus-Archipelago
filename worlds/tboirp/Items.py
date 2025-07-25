from math import floor
from typing import Optional, NamedTuple, Dict, TYPE_CHECKING

from BaseClasses import ItemClassification, Item
from .Items_Data import ItemData, items_data

if TYPE_CHECKING:
    from . import TBOIWorld


class TBOIItem(Item):
    game = "The Binding of Isaac: Repentance+"

    def __init__(self, player: int, name: str, data: ItemData):
        super().__init__(name, data.classification, data.code, player)
        self.name = name

# For the option "starting character", the number corresponds to the entry in this table.
character_items = [
    "Isaac", "Magdalene", "Cain", "Judas", "???",
    "Eve", "Samson",
    "Azazel", "Lazarus", "Eden", "Lost",
    "Lilith", "Keeper",
    "Apollyon", "Forgotten",
    "Bethany", "Jacob and Esau",
    "The Broken", "The Dauntless", "The Hoarder", "The Deceiver", "The Soiled",
    "The Curdled", "The Savage",
    "The Benighted", "The Enigma", "The Capricious", "The Baleful",
    "The Harlot", "The Miser",
    "The Empty", "The Fettered",
    "The Zealot", "The Deserter"
]

"""
The way this works, is that we'll modify the existing items table(IDs are not changed), and then use that modified items table to specify
items. *These* items will actually be used in the Archipelago world (not unlocked by default).
"""
def generate_items_for_pool(world: "TBOIWorld", location_count: int, included_locations_count: int, exclude_items: list[str]) -> Dict[str, ItemData]:
    print("Need to generate {count} items".format(count=location_count))

    bup = location_count

    # If we're in Baby Hunt, pick some babies to make Progressive
    if world.options.game_mode.option_baby_hunt:
        for name in world.random.choices([name for name in items_data if "Co-Op_Baby" in items_data[name].categories]):
            set_item_classification(name, ItemClassification.progression_skip_balancing)

    # Set challenges to filler if they don't contribute anything
    if world.options.include_challenges == world.options.include_challenges.option_remove:
        for name in world.random.choices([name for name in items_data if "Challenge" in items_data[name].categories]):
            set_item_classification(name, ItemClassification.filler)

    # Filter out any of the 'excluded' items (as well as victory, and traps/fillers)
    filtered_items = {name: data for name, data in items_data.items() if name not in exclude_items and data.categories[0] not in ["Victory", "Trap", "Filler"]}

    # All of these MUST get added
    progression_items = [name for name, data in filtered_items.items() if data.classification in [ItemClassification.progression]]

    # If on Baby Hunt, select some babies to add
    if world.options.game_mode == world.options.game_mode.option_baby_hunt:
        all_babies = [name for name, data in items_data.items() if "Co-Op_Baby" in data.categories]
        world.random.shuffle(all_babies)

        # Set chosen babies to be progression & add them to the progression items list
        for baby in all_babies[:world.options.max_babies]:
            set_item_classification(baby, ItemClassification.progression_skip_balancing)
            progression_items.append(baby)

    # Items to add to the pool as filler
    shuffle_items = [name for name, data in filtered_items.items() if data.classification == ItemClassification.filler and "Co-Op_Baby" not in items_data[name].categories]

    # If we're locking only the standard unlockable items, then filter the default items out
    if not world.options.lock_all_items:
        shuffle_items = [name for name in shuffle_items if items_data[name].achievement is not None]

    # Select some higher-quality items to make progressive (they will contribute to the player's "Power")
    # Do this by selecting a number of high quality items, removing them from the shuffle pool and inserting them into
    # the progression pool
    higher_tier_items = [name for name in shuffle_items if items_data[name].quality is not None and items_data[name].quality >= 3]
    for name in world.random.choices(higher_tier_items, k=floor(included_locations_count / 4)):
        if not name in shuffle_items:
            continue # The item is actually a default item (and we're filtering them out), so we don't need to remove it here

        shuffle_items.remove(name)
        progression_items.append(name)

    # At this point, we simply select items from the filler until we max out the location count
    items_to_use = {name: items_data[name] for name in progression_items}

    location_count -= len(items_to_use.items()) # Since they are guaranteed to appear...
    world.random.shuffle(shuffle_items) # Shuffle the items, so we take a 'random' selection of them
    other_items_to_add = shuffle_items[:min(location_count, len(shuffle_items))]
    for name in other_items_to_add:
        items_to_use[name] = items_data[name]

    location_count -= len(other_items_to_add)

    # We still have unfilled locations, so let's get some random items and fill
    while location_count > 0:
        name = world.get_filler_item_name()
        add_count_to_item(name, 1) # Add a copy of the item
        location_count -= 1

        items_to_use[name] = items_data[name]

    # Ensure that this is all correct, I guess?
    total = 0
    for name, data in items_to_use.items():
        total += data.amount

    print(total)
    print(bup)
    print(bup - total)

    return items_to_use

"""
Just sets an item's classification in the items table.
"""
def set_item_classification(name: str, classification: ItemClassification):
    data = items_data[name]
    items_data[name] = ItemData(data.code, classification, data.categories, data.achievement, data.internal_id, data.amount, data.quality)

"""
Adds 1 copy of the item to the pool
"""
def add_count_to_item(name: str, amount_to_add: int):
    data = items_data[name]
    items_data[name] = ItemData(data.code, data.classification, data.categories, data.achievement, data.internal_id, data.amount + amount_to_add, data.quality)



trap_items = (
    "Fool Trap",
    "High Priestess Trap",
    "Tower Trap",
    "Emperor Trap",
    "Damocles Trap",
    "Chariot? Trap",
    "Stars? Trap",
    "Forget Me Now Trap",
    "TM Trainer Trap",
    "Clicker Trap",
    "Run",
    "Wheel of Fortune? Trap",
    "Cursed! Trap"
)

filler_items = (
    "Active Recharge",
    "Temporary Shield",
    "Three Coins",
    "Three Cards",
    "Three Runes",
    "Three Pills",
    "Three Hearts",
    "Three Bombs",
    "Three Keys"
)