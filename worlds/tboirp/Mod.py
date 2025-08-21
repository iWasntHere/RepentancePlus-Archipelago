import os
import threading
import zipfile
from typing import TYPE_CHECKING, Optional, Union, Tuple, Callable, List, Any, Dict
import xml.etree.ElementTree as ET

import jinja2

import Utils
import worlds.Files
from BaseClasses import ItemClassification

template_load_lock = threading.Lock()

from . import ItemData, items_data, TBOIPoolEntry

if TYPE_CHECKING:
    from . import TBOIWorld

template_env: Optional[jinja2.Environment] = None

metadata_template: Optional[jinja2.Template] = None
mainlua_template: Optional[jinja2.Template] = None

class TBOIModFile(worlds.Files.APPlayerContainer):
    game = "The Binding of Isaac: Repentance+"
    patch_file_ending = ".zip"
    writing_tasks: List[Callable[[], Tuple[str, Union[str, bytes]]]]

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)

        self.writing_tasks = []

    def write_contents(self, opened_zipfile: zipfile.ZipFile) -> None:
        mod_dir = self.path[:-4]

        for root, dirs, files in os.walk(mod_dir):
            for file in files:
                filename = os.path.join(root, file)
                opened_zipfile.write(filename, os.path.relpath(filename, os.path.join(mod_dir, '..')))

        for task in self.writing_tasks:
            target, content = task()
            opened_zipfile.writestr(target, content)

        super(TBOIModFile, self).write_contents(opened_zipfile)

def make_item_states_table(world: "TBOIWorld"):
    unlocked = {data.code: True for name, data in world.default_items.items()}
    locked = {data.code: False for name, data in world.usable_items.items()}

    return {**unlocked, **locked}

def make_pools_xml(pool_values: Dict[str, list[TBOIPoolEntry]]) -> str:
    root = ET.Element("ItemPools")

    # Create pool tags
    for pool_name, pool_entries in pool_values.items():
        pool = ET.Element("Pool")
        pool.attrib["Name"] = pool_name

        # Create item tags
        for pool_entry in pool_entries:
            entry = ET.Element("Item")

            entry.attrib["Id"] = str(pool_entry.internal_item_id)
            entry.attrib["Weight"] = str(pool_entry.weight)
            entry.attrib["DecreaseBy"] = str(pool_entry.weight)
            entry.attrib["RemoveOn"] = "0.1" # I don't think this really matters

            pool.append(entry)

        root.append(pool)

    return ET.tostring(root, encoding="utf-8")

characters = [
    "Isaac", "Magdalene", "Cain", "Judas", "???",
    "Eve", "Samson",
    "Azazel", "Lazarus", "Eden", "Lost",
    "Lilith", "Keeper",
    "Apollyon", "Forgotten",
    "Bethany", "Jacob and Esau",

    "Tainted Isaac", "Tainted Magdalene", "Tainted Cain", "Tainted Judas", "Tainted ???",
    "Tainted Eve", "Tainted Samson",
    "Tainted Azazel", "Tainted Lazarus", "Tainted Eden", "Tainted Lost",
    "Tainted Lilith", "Tainted Keeper",
    "Tainted Apollyon", "Tainted Forgotten",
    "Tainted Bethany", "Tainted Jacob"
]

def item_classification_string(classification: ItemClassification):
    """
    Returns a string describing how useful the given classification of item is.
    """

    if classification == ItemClassification.useful:
        return "useful thing"
    elif classification == ItemClassification.progression:
        return "important thing"
    elif classification == ItemClassification.progression:
        return "\"important\" thing"

    return "thing"

def make_fortune_hints(world: "TBOIWorld") -> dict:
    """
    Creates the dict that holds all the player's Fortune Teller hints.
    """

    hints = {}
    specificity = world.options.hint_specificity

    # Items
    for hint_item in world.hint_items:
        hints.setdefault("Global", [])

        location = hint_item.location
        player_name = world.multiworld.get_player_name(location.player)

        text = "{item}|IS AT|{location}|FROM {finder}"

        # If the item is in our world, omit the player it's from
        if location.player == world.player:
            text = "{item} IS AT|{location}"

        item_name = hint_item.name

        # If on vague specificity, replace with classification
        if specificity.value == specificity.option_vague:
            item_name = item_classification_string(hint_item.classification)

        hints["Global"].append({
            "text": text.format(item = item_name, location = location.name, finder = player_name).upper(),
            "location": location.address
        })

    # Locations
    for hint_location in world.hint_locations:
        character = hint_location.data.character

        if character is None: # Any character can get this fortune
            character = "Global"

        hints.setdefault(character, [])

        item_name = hint_location.item.name if specificity.value != specificity.option_vague else item_classification_string(hint_location.item.classification)
        player_name = world.multiworld.get_player_name(hint_location.item.player) + "'S"

        # If the item is for this slot, then use "your" as the player's name
        if world.player == hint_location.item.player:
            player_name = "YOUR"

        full_name = "{player} {item}".format(player=player_name, item=item_name)

        if len(full_name) >= 24:  # Split the player and item name onto separate lines if together they're too long
            full_name = "{player}|{item}".format(player=player_name, item=item_name)

        if specificity.value == specificity.option_full: # Full hint
            text = "{name}|is at {location}".format(name = full_name, location = hint_location.name)
        else: # Immersive & Vague hint
            text = hint_location.data.as_hint().format(item = full_name)

        hints[character].append({
            "text": text.upper(),
            "location": hint_location.address
        })

    return hints

def make_location_info(world: "TBOIWorld") -> dict:
    locations = world.get_locations()

    return {location.address: {
        "player_name": world.multiworld.get_player_name(location.item.player),
        "item_name": world.multiworld.worlds[location.item.player].item_id_to_name[location.item.code]
    } for location in locations}

def generate_mod(world: "TBOIWorld", output_directory: str):
    player = world.player
    mw = world.multiworld

    # Load templates
    global metadata_template, mainlua_template
    with template_load_lock:
        if not metadata_template:
            def load_template(name: str):
                import pkgutil
                data = pkgutil.get_data(__name__, "data/mod_template/" + name).decode()
                return data, name, lambda: False

            template_env = jinja2.Environment(loader=jinja2.FunctionLoader(load_template))

            metadata_template = template_env.get_template("metadata.xml")
            mainlua_template = template_env.get_template("main.lua")
            itemstateslua_template = template_env.get_template("item_states.lua")
            fortune_hintslua_template = template_env.get_template("fortune_hints.lua")
            location_info_lua_template = template_env.get_template("location_info.lua")

    # Set template data
    mod_name = f"_Archipelago ({mw.get_file_safe_player_name(player)}) ({mw.seed_name})"
    dir_name = f"_AP-TBOIRP-{mw.seed_name}-{mw.get_file_safe_player_name(player)}"

    template_data = {
        "mod_formal_name": mod_name,
        "mod_dir_name": dir_name,
        "seed_name": mw.seed_name,
        "slot_name": mw.get_player_name(player),
        "item_states": make_item_states_table(world),
        "shop_donation_location_count": world.options.shop_donations.value,
        "greed_donation_location_count": world.options.greed_donations.value,
        "consumable_location_count": world.options.consumable_locations.value,
        "target_baby_codes": world.babies,
        "fortune_hints": make_fortune_hints(world),
        "location_information": make_location_info(world)
    }

    # Create the .zip
    zip_path = os.path.join(output_directory, f"{dir_name}.zip")
    mod = TBOIModFile(zip_path, player=player, player_name=world.player_name)
    
    if world.zip_path:
        with zipfile.ZipFile(world.zip_path) as zf:
            for file in zf.infolist():
                if not file.is_dir() and "/data/mod/" in file.filename:
                    path_part = Utils.get_text_after(file.filename, "/data/mod/")
                    mod.writing_tasks.append(lambda arcpath=dir_name+"/"+path_part, content=zf.read(file):
                                             (arcpath, content))
    else:
        basepath = os.path.join(os.path.dirname(__file__), "data", "mod")
        for dirpath, dirnames, filenames in os.walk(basepath):
            base_arc_path = (dir_name+"/"+os.path.relpath(dirpath, basepath)).rstrip("/.\\")
            for filename in filenames:
                mod.writing_tasks.append(lambda arcpath=base_arc_path+"/"+filename,
                                                file_path=os.path.join(dirpath, filename):
                                         (arcpath, open(file_path, "rb").read()))

    # All files go in the root of the zip
    mod.writing_tasks.append(lambda: ("main.lua", mainlua_template.render(**template_data)))
    mod.writing_tasks.append(lambda: ("item_states.lua", itemstateslua_template.render(**template_data)))
    mod.writing_tasks.append(lambda: ("incoming_ap_data.lua", ""))
    mod.writing_tasks.append(lambda: ("metadata.xml", metadata_template.render(**template_data)))
    mod.writing_tasks.append(lambda: ("fortune_hints.lua", fortune_hintslua_template.render(**template_data)))
    mod.writing_tasks.append(lambda: ("location_info.lua", location_info_lua_template.render(**template_data)))

    # If we're doing pool rando, generate an itempools.xml
    if world.options.pool_rando.value != world.options.pool_rando.option_off:
        mod.writing_tasks.append(lambda: ("resources/itempools.xml", make_pools_xml(world.pool_rando)))

    mod.write()