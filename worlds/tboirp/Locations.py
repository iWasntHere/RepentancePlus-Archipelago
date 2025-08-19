from math import floor
from typing import TYPE_CHECKING

from BaseClasses import Location, Region, LocationProgressType
from .Locations_Data import locations_data, LocationData
from ..generic.Rules import CollectionRule

if TYPE_CHECKING:
    from . import TBOIWorld

class TBOILocation(Location):
    game = "The Binding of Isaac: Repentance+"
    data: LocationData

    def __init__(self, player: int, data: LocationData, region: Region):
        super().__init__(player, data.full_name(), data.code, region)
        self.access_rule = data.access_rule
        self.progress_type = data.progress_type

        self.data = data

def make_locations(world: "TBOIWorld") -> list[LocationData]:
    ply = world.player
    babies = world.options.max_babies
    baby_ratio = world.options.baby_ratio_required

    locations = locations_data(world)

    # Set location access rule for co-op baby victory
    set_location_access_rule(locations, [data for data in locations if data.name == "Victory (Baby Hunt)"][0],
                             lambda s: s.has_group("Co-Op Baby", ply, floor(babies * (baby_ratio / 100))))

     # Exclude some locations
    options = world.options
    greed_value = options.include_greed_mode.value
    challenge_value = options.include_challenges.value
    repetitious_value = options.include_repetitious.value
    bossanity_value = options.bossanity.value
    chapter_completionsanity_value = options.chapter_completionsanity.value
    char_exclusions = options.exclude_characters.get_excluded_characters()
    for location in locations:

        # Challenges!!!
        if "Challenge" in location.categories:
            if challenge_value == options.include_challenges.option_exclude: # Exclude
                exclude_location(locations, location)
            elif challenge_value == options.include_challenges.option_remove: # Remove
                remove_location(locations, location)

        # No Greed Mode? (Insert Megamind image)
        if greed_value != options.include_greed_mode.option_greed_and_greedier and (location.region in ["Greed Mode", "Greedier Mode"] or "All Marks" in location.categories):
            if location.region == "Greed Mode" and greed_value == options.include_greed_mode.option_greed_mode_only:
                continue

            if location.region == "Greedier Mode" and greed_value == options.include_greed_mode.option_greedier_mode_only:
                continue

            exclude_location(locations, location)

        # If we are excluding/removing repetitious locations
        if repetitious_value != options.include_repetitious.option_include and location.repetitions > 1:
            if repetitious_value == options.include_repetitious.option_exclude: # Exclude
                exclude_location(locations, location)
            elif repetitious_value == options.include_repetitious.option_remove: # Remove
                remove_location(locations, location)

        # Bossanity!
        if bossanity_value != options.bossanity.option_on and location.categories[0] == "Boss_Clear" and location.custom:
            if bossanity_value == options.bossanity.option_on_filler: # Exclude
                exclude_location(locations, location)
            elif bossanity_value == options.bossanity.option_on_filler: # Remove
                remove_location(locations, location)

        # Chapter Completionsanity!
        if chapter_completionsanity_value != options.chapter_completionsanity.option_on and location.categories[0] == "Stage_Clear" and location.custom:
            if chapter_completionsanity_value == options.chapter_completionsanity.option_on: # Exclude
                exclude_location(locations, location)
            elif chapter_completionsanity_value == options.chapter_completionsanity.option_on_filler: # Remove
                remove_location(locations, location)

        # Character exclusions
        if location.character in char_exclusions:
            exclude_location(locations, location)

    # Remove any superfluous AP locations
    remove_ap_locations(locations, "Shop Donation", options.shop_donations.value, 50)
    remove_ap_locations(locations, "Greed Donation", options.greed_donations.value, 50)
    remove_ap_locations(locations, "AP Consumable", options.consumable_locations.value, 50)

    return locations

"""
Removes all the AP locations of a type, after the given index
"""
def remove_ap_locations(locations: list[LocationData], starts_with: str, past: int, up_to: int):
    for i in range(up_to):
        index = i + 1
        if index < past:
            continue

        loc = [data for data in locations if
               data.name.startswith(starts_with) and data.name.endswith("({index}x)".format(index=index))][0]
        remove_location(locations, loc)

"""
Sets a location to "EXCLUDED" (Only filler)
"""
def exclude_location(locations: list[LocationData], data: LocationData):
    try:
        index = locations.index(data)

        locations[index] = LocationData(data.name, data.code, data.region, data.categories, data.repetitions, LocationProgressType.EXCLUDED, data.custom, data.character, data.access_rule)
    except ValueError:
        pass # This is fine, just means the location was removed

"""
Entirely removes a location
"""
def remove_location(locations: list[LocationData], data: LocationData):
    index = locations.index(data)

    locations[index] = LocationData(data.name, data.code, data.region, data.categories, data.repetitions, None, data.custom, data.character, data.access_rule)

"""
Sets a location's access rule
"""
def set_location_access_rule(locations: list[LocationData], data: LocationData, rule: CollectionRule):
    index = locations.index(data)

    locations[index] = LocationData(data.name, data.code, data.region, data.categories, data.repetitions, data.progress_type, data.custom, data.character, rule)