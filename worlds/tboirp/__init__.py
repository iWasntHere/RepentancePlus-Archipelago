from typing import Dict

from BaseClasses import Item, Tutorial, LocationProgressType
from worlds.AutoWorld import World, WebWorld
from .Items import filler_items, trap_items, TBOIItem, ItemData, character_items, generate_items_for_pool
from .Items_Data import items_data
from .Locations import make_locations, LocationData
from .Locations_Data import locations_data
from .Options import TBOIOptions
from .Regions import make_regions
from .Rules import make_rules


class TBOIWebWorld(WebWorld):
    theme = 'dirt'
    tutorials = [
        Tutorial(
            tutorial_name='Setup Guide',
            description='Setup guide',
            language='English',
            file_name='guide_en.md',
            link='guide/en',
            authors=['Vivian']
        )
    ]


class TBOIWorld(World):
    """
    A roguelike game with over 600 unlockable items and many, many endings.
    """
    game = "The Binding of Isaac: Repentance+"
    topology_present = False
    web = TBOIWebWorld()

    options_dataclass = TBOIOptions
    options: TBOIOptions

    starting_character_item: str

    item_name_to_id = {item[0]: item[1].code for item in items_data.items()}
    location_name_to_id = {location.name: location.code for location in locations_data(None)}

    usable_items: Dict[str, ItemData] # Items that will appear in the multiworld
    default_items: Dict[str, ItemData] # Items that start unlocked for the player

    item_name_groups = {
        "Co-Op Baby": [name for name, data in items_data.items() if "Co-Op_Baby" in data.categories]
    }

    def set_rules(self):
        make_rules(self)

    def create_item(self, name: str) -> Item:
        return TBOIItem(self.player, name, items_data[name])

    def create_items(self):
        items_table: dict[str: ItemData] = {name: item for name, item in self.usable_items.items()}

        # Now we can actually add some stuff!
        for name, data in items_table.items():
            for i in range(data.amount): # In case we have multiple copies
                self.multiworld.itempool.append(TBOIItem(self.player, name, data))

    def create_regions(self):
        make_regions(self, make_locations(self))

    def get_filler_item_name(self) -> str:
        if self.random.random() < 0.25:
            return self.multiworld.random.choice(trap_items)

        return self.multiworld.random.choice(filler_items)

    def generate_early(self) -> None:
        self.starting_character_item = character_items[self.options.starting_character.value]
        self.multiworld.push_precollected(self.create_item(self.starting_character_item))

        excluded_items = [self.starting_character_item]  # Filter some items out

        # Kind of a bad hack, but we need to know how many locations are going to be local so
        # we know how many items to add to the pool.
        locations = make_locations(self)

        self.usable_items = generate_items_for_pool(self, len(locations), len([data.name for data in locations if data.progress_type != LocationProgressType.EXCLUDED]), excluded_items)
        self.default_items = {name: data for name, data in items_data.items() if name not in self.usable_items}