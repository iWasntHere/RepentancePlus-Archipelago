import os
import threading
import zipfile
from typing import TYPE_CHECKING, Optional, Union, Tuple, Callable, List, Any, Dict
import xml.etree.ElementTree as ET

import jinja2

import Utils
import worlds.Files

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

def get_item_key(name: str, data: ItemData) -> str:
    """
    Returns a key for an item when it is unlocked by default.
    Items that have an internal id for quick lookup (collectibles, trinkets, etc)
    will be in the format Type-InternalID
    Items that lack an internal ID will just be the name of the item (e.g. The Cellar)
    """

    if data.internal_id is not None:
        cat = data.categories[0]

        if cat in ["Tarot", "Suit", "Rune", "Reverse", "Special", "Object"]:
            cat = "Card"

        return f"{cat}-{data.internal_id}"

    return name

def make_item_states_table(world: "TBOIWorld"):
    unlocked = {get_item_key(name, data): True for name, data in world.default_items.items()}
    locked = {get_item_key(name, data): False for name, data in world.usable_items.items()}

    return {**unlocked, **locked}

def make_code_to_state_table():
    table = {}
    for name, data in items_data.items():
        table[data.code] = get_item_key(name, data)

    return table

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

    # Set template data
    mod_name = f"_Archipelago ({mw.get_file_safe_player_name(player)}) ({mw.seed_name})"
    dir_name = f"_AP-TBOIRP-{mw.seed_name}-{mw.get_file_safe_player_name(player)}"

    template_data = {
        "mod_formal_name": mod_name,
        "mod_dir_name": dir_name,
        "seed_name": mw.seed_name,
        "slot_name": mw.get_player_name(player),
        "item_states": make_item_states_table(world),
        "item_code_to_item_state_key": make_code_to_state_table(),
        "shop_donation_location_count": world.options.shop_donations.value,
        "greed_donation_location_count": world.options.greed_donations.value,
        "consumable_location_count": world.options.consumable_locations.value
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
    mod.writing_tasks.append(lambda: ("incoming_ap_data.lua", ""))
    mod.writing_tasks.append(lambda: ("metadata.xml", metadata_template.render(**template_data)))

    # If we're doing pool rando, generate an itempools.xml
    if world.options.pool_rando.value != world.options.pool_rando.option_off:
        mod.writing_tasks.append(lambda: ("resources/itempools.xml", make_pools_xml(world.pool_rando)))

    mod.write()