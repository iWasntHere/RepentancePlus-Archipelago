from BaseClasses import Item, Tutorial
from worlds.AutoWorld import World, WebWorld
from .Items import filler_items, trap_items, get_items_table, TBOIItem, ItemData, character_items
from .Locations import make_locations, LocationData
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

    item_name_to_id = {item[0]: item[1].code for item in get_items_table(None).items()}
    location_name_to_id = {location.name: location.code for location in make_locations(None)}

    item_name_groups = {
        "Co-Op Baby": [name for name, data in get_items_table(None).items() if data.category == "Co-Op Baby"]
    }

    def set_rules(self):
        make_rules(self)

    def create_item(self, name: str) -> Item:
        return TBOIItem(self.player, name, get_items_table(self)[name])

    def create_items(self):
        items: list[TBOIItem] = []

        excluded_items = [self.starting_character_item, "Victory"] # Filter some items out
        items_table: dict[str: ItemData] = {name: item for name, item in get_items_table(self).items() if name not in excluded_items}

        # Generate regular items
        for item_name in items_table.keys():
            items.append(TBOIItem(self.player, item_name, get_items_table(self)[item_name]))

        # Generate filler
        for _ in range(len(self.multiworld.get_unfilled_locations(self.player)) - len(items)):
            name = self.get_filler_item_name()
            items.append(TBOIItem(self.player, name, items_table[name]))

        self.multiworld.itempool += items

    def create_regions(self):
        make_regions(self, make_locations(self))

    def get_filler_item_name(self) -> str:
        if self.random.random() < 0.25:
            return self.multiworld.random.choice(trap_items)

        return self.multiworld.random.choice(filler_items)

    def generate_early(self) -> None:
        self.starting_character_item = character_items[self.options.starting_character.value]
        self.multiworld.push_precollected(self.create_item(self.starting_character_item))