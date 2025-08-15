"""
Generates Lua, Python files for the game mod and the AP World. Place the data files into sources and run this script
from its directory to generate into output.
"""

import csv
import re
import pathlib

directory = pathlib.Path(__file__).parent

starts_with_number_regex = re.compile(r"^[0-9]")

def de_string_integers(match):
    """
    Removes quotation marks around pure integer values in the string.
    """
    g = match.group(0)
    return (g[1:])[:-1]

def flip(tuple_list : list[tuple[any, any]]) -> list[tuple[any, any]]:
    """
    Reverses a tuple such that the first element is now the second, and the second is now the first.
    """
    return [(t[1], t[0]) for t in tuple_list]

def tuple_list_to_lua_table(tuple_list: list[tuple[any, any]]) -> str:
    """
    Converts a tuple list to a Lua table.
    """

    out_strings = []

    for item in tuple_list:
        item1 = item[0]
        item2 = item[1]

        item1_string = '["' + str(item1) + '"]'
        item2_string = '"' + str(item2) + '"'

        out_strings.append(item1_string + " = " + item2_string)

    return "{" + ",".join(out_strings) + "}"

def tuple_list_to_lua_enum(tuple_list: list[tuple[any, any]]) -> str:
    """
    Converts a tuple list to a Lua enum-style table.
    """

    out_strings = []

    for item in tuple_list:
        item1 = item[0]
        item2 = item[1]

        item1_string = str(item1)
        item2_string = '"' + str(item2) + '"'

        item1_string = item1_string \
            .replace("???", "bluebaby") \
            .replace("#", "num ") \
            .replace(">", "greater than ") \
            .replace("<", "less than ") \
            .replace("&", "and") \
            .replace("-", "_") \
            .replace(" ", "_") \
            .upper()

        item1_string = re.sub(r"[(),.?!':;$/]", "", item1_string)

        # If the enum starts with a number, prevent that
        if starts_with_number_regex.match(item1_string):
            item1_string = "_" + item1_string

        out_strings.append(item1_string + " = " + item2_string)

    return "{" + ",".join(out_strings) + "}"

def make_item_data_lua():
    """
    Create item_data.lua for the game mod.
    """

    name_to_code = []
    collectible_id_to_code = []
    trinket_id_to_code = []
    card_id_to_code = []
    pill_id_to_code = []
    character_id_to_code = []
    baby_id_to_code = []
    code_to_type = []

    with open(directory.joinpath("sources", "items_ap.csv").resolve(), "r") as input_file:
        reader = csv.reader(input_file)

        for row in reader:
            if row[0] == "AP ID": # Skip first row (these are headers)
                continue

            code = int(row[0])
            name = row[1]
            item_type = row[2]
            internal_id = row[3]
            classification = row[8]

            if classification == "EXCLUDE": # Exclude specific items
                continue

            name_to_code.append((name, code))
            code_to_type.append((code, item_type))

            if item_type == "Item":
                collectible_id_to_code.append((internal_id, code))

            if item_type == "Trinket":
                trinket_id_to_code.append((internal_id, code))

            if item_type in ["Tarot", "Suit", "Rune", "Special", "Object", "Reverse_Tarot"]:
                card_id_to_code.append((internal_id, code))

            if item_type == "Pill":
                pill_id_to_code.append((internal_id, code))

            if item_type == "Character" or item_type == "Tainted_Character":
                character_id_to_code.append((internal_id, code))

            if item_type == "Co-Op_Baby":
                baby_id_to_code.append((internal_id, code))

    out_string = ("return \n{{" +
                   "NAME_TO_CODE = {name_to_code},\n" +
                   "CODE_TO_NAME = {code_to_name},\n" +
                   "COLLECTIBLE_ID_TO_CODE = {collectible_to_code},\n" +
                   "TRINKET_ID_TO_CODE = {trinket_to_code},\n" +
                   "CARD_ID_TO_CODE = {card_to_code},\n" +
                   "PILL_ID_TO_CODE = {pill_to_code},\n" +
                   "CHARACTER_ID_TO_CODE = {character_to_code},\n" +
                   "BABY_ID_TO_CODE = {baby_to_code},\n" +
                   "CODE_TO_COLLECTIBLE_ID = {code_to_collectible},\n" +
                   "CODE_TO_TRINKET_ID = {code_to_trinket},\n" +
                   "CODE_TO_CARD_ID = {code_to_card},\n" +
                   "CODE_TO_PILL_ID = {code_to_pill},\n" +
                   "CODE_TO_CHARACTER_ID = {code_to_character},\n" +
                   "CODE_TO_BABY_ID = {code_to_baby},\n" +
                   "CODE_TO_TYPE = {code_to_type}}}").format(
        name_to_code=tuple_list_to_lua_table(name_to_code),
        code_to_name=tuple_list_to_lua_table(flip(name_to_code)),
        collectible_to_code=tuple_list_to_lua_table(collectible_id_to_code),
        trinket_to_code=tuple_list_to_lua_table(trinket_id_to_code),
        card_to_code=tuple_list_to_lua_table(card_id_to_code),
        pill_to_code=tuple_list_to_lua_table(pill_id_to_code),
        character_to_code=tuple_list_to_lua_table(character_id_to_code),
        baby_to_code=tuple_list_to_lua_table(baby_id_to_code),

        code_to_collectible=tuple_list_to_lua_table(flip(collectible_id_to_code)),
        code_to_trinket=tuple_list_to_lua_table(flip(trinket_id_to_code)),
        code_to_card=tuple_list_to_lua_table(flip(card_id_to_code)),
        code_to_pill=tuple_list_to_lua_table(flip(pill_id_to_code)),
        code_to_character=tuple_list_to_lua_table(flip(character_id_to_code)),
        code_to_baby=tuple_list_to_lua_table(flip(baby_id_to_code)),

        code_to_type=tuple_list_to_lua_table(code_to_type)
    )

    out_string = re.sub(r'"\d+"', de_string_integers, out_string)

    with open(directory.joinpath("output", "item_data.lua").resolve(), "w") as out_file:
        out_file.write(out_string)

def make_item_data_python():
    """
    Create item_data.lua for the AP world.
    """

    lines = []

    with open(directory.joinpath("sources", "items_ap.csv").resolve(), "r") as input_file:
        reader = csv.reader(input_file)

        for row in reader:
            if row[0] == "AP ID": # Header data
                continue

            classification = row[8]

            if classification == "EXCLUDE": # Excluded
                continue

            type_ = row[2]
            tags = row[7]
            pool_data = row[9]

            pools = []
            if pool_data != "":
                for pool in pool_data.split(" "):
                    pool_name, weight = pool.split(":")
                    pools.append('Pool("{name}", {weight})'.format(name=pool_name, weight=weight))

            item_pools = '[{pools}]'.format(pools=", ".join(pools))

            lines.append(
                '{name}:ItemData({code}, {classification}, {categories}, {achievement}, {internal_id}, {amount}, {quality}, {pools})'.format(
                    code=row[0],
                    name='"{n}"'.format(n=row[1]).ljust(32),
                    classification="ItemClassification.{clas}".format(clas=classification.lower()),
                    categories=((type_ + " " + tags).strip()).split(" "),
                    achievement=row[4] if row[4] != "" else "None",
                    quality=row[6] if row[6] != "" else "None",
                    amount=row[10],
                    internal_id=row[3] if row[3] != "" else "None",
                    pools=item_pools
                ))

    with open(directory.joinpath("output", "items_data.py").resolve(), "w") as out_file:
        out_file.write(",\n".join(lines))


def make_location_data_lua():
    """
    Create location_data.lua for the game mod.
    """

    name_to_code = []

    with open(directory.joinpath("sources", "locations_ap.csv").resolve(), "r") as input_file:
        reader = csv.reader(input_file)

        for row in reader:
            if row[0] == "AP ID":  # Skip first row (these are headers)
                continue

            name = row[1]
            count = row[2]

            if count != "":
                name += " ({count}x)".format(count = count)

            name_to_code.append((name, row[0]))

    out_string = (
        "return {{\n" +
        "NAME_TO_CODE = {name_to_code},\n" +
        "--- @enum Location\n" +
        "LOCATIONS = {enum_to_code}}}"
    ).format(
        name_to_code = tuple_list_to_lua_table(name_to_code),
        enum_to_code = tuple_list_to_lua_enum(name_to_code),
    )
    out_string = re.sub(r'"\d+"', de_string_integers, out_string)

    with open(directory.joinpath("output", "location_data.lua").resolve(), "w") as out_file:
        out_file.write(out_string)

def make_location_data_python():
    """
    Create location_data.lua for the AP world.
    """

    lines = []

    with open(directory.joinpath("sources", "locations_ap.csv").resolve(), "r") as input_file:
        reader = csv.reader(input_file)

        for row in reader:
            if row[0] == "AP ID":  # Skip first row (these are headers)
                continue

            code = row[0]
            name = row[1]
            region = row[3]
            repeats = row[2] if row[2] != "" else "1"
            categories = row[4]
            split_cats = categories.split(" ")
            custom = row[6] == "Yes"
            progress = "LocationProgressType.{i}".format(i="DEFAULT")
            rule = "lambda s: {rule}"

            rule_value = row[5]

            if rule_value == "":
                rule = "lambda s: True"
            else:
                if rule_value.startswith("$"):
                    rule = rule.format(rule=rule_value[1:])
                    rule = rule.replace("has(", "s.has(")
                    rule = rule.replace("has_any(", "s.has_any(")
                    rule = rule.replace("has_all(", "s.has_all(")
                else:
                    rule = rule.format(rule='s.has("{val}", p)'.format(val=rule_value))

            line = 'LocationData("{name}", {code}, "{region}", {categories}, {repeats}, {progress_type}, {custom}, {rule})'.format(
                name=name,
                code=code,
                region=region,
                repeats=repeats,
                categories=split_cats,
                custom=custom,
                progress_type=progress,
                rule=rule
            )

            lines.append(line)

    with open(directory.joinpath("output", "location_data.py").resolve(), "w") as out_file:
        out_file.write(",\n".join(lines))

make_item_data_lua()
make_item_data_python()
make_location_data_lua()
make_location_data_python()