from typing import TYPE_CHECKING, NamedTuple, List, Optional, Dict

from BaseClasses import Region, LocationProgressType
from ..generic.Rules import CollectionRule
from .Locations import LocationData, TBOILocation

if TYPE_CHECKING:
    from . import TBOIWorld

class RegionExitData(NamedTuple):
    to: str
    rule: Optional[CollectionRule] = None

class TBOIRegionData(NamedTuple):
    to_regions: Optional[List[str]] = None
    locations: Optional[List[LocationData]] = []

def make_regions(world: "TBOIWorld", location_data: list[LocationData]):
    player = world.player
    multiworld = world.multiworld

    stages: Dict[str, TBOIRegionData] = {
        "Basement":                         TBOIRegionData(["Chapter 1"]),
        "Cellar":                           TBOIRegionData(["Chapter 1"]),
        "Burning Basement":                 TBOIRegionData(["Chapter 1"]),

        "Downpour":                         TBOIRegionData(["Chapter 1.5"]),
        "Dross":                            TBOIRegionData(["Chapter 1.5"]),

        "Caves":                            TBOIRegionData(["Chapter 2"]),
        "Catacombs":                        TBOIRegionData(["Chapter 2"]),
        "Flooded Caves":                    TBOIRegionData(["Chapter 2"]),

        "Mines":                            TBOIRegionData(["Chapter 2.5"]),
        "Ashpit":                           TBOIRegionData(["Chapter 2.5"]),

        "Depths":                           TBOIRegionData(["Chapter 3"]),
        "Necropolis":                       TBOIRegionData(["Chapter 3"]),
        "Dank Depths":                      TBOIRegionData(["Chapter 3"]),

        "Mausoleum":                        TBOIRegionData(["Chapter 3.5"]),
        "Gehenna":                          TBOIRegionData(["Chapter 3.5"]),

        "Corpse":                           TBOIRegionData(),

        "The Womb":                         TBOIRegionData(["Chapter 4"]),
        "Utero":                            TBOIRegionData(["Chapter 4"]),
        "Scarred Womb":                     TBOIRegionData(["Chapter 4"]),

        "Blue Womb":                        TBOIRegionData(["Sheol", "Cathedral", "The Void"]),

        "Sheol":                            TBOIRegionData(["Dark Room"]),
        "Cathedral":                        TBOIRegionData(["The Chest"]),

        "Dark Room":                        TBOIRegionData(["Chapter 6"]),
        "The Chest":                        TBOIRegionData(["Chapter 6"]),

        "Mega Satan":                       TBOIRegionData(),
        "The Void":                         TBOIRegionData(),
        "Ascent":                           TBOIRegionData()
    }

    chapters: Dict[str, TBOIRegionData] = {
        "Chapter 1":                        TBOIRegionData(["Caves", "Catacombs", "Flooded Caves", "Downpour", "Dross"]),
        "Chapter 1.5":                      TBOIRegionData(["Caves", "Catacombs", "Flooded Caves", "Mines", "Ashpit"]),
        "Chapter 2":                        TBOIRegionData(["Depths", "Necropolis", "Dank Depths", "Mines", "Ashpit"]),
        "Chapter 2.5":                      TBOIRegionData(["Depths", "Necropolis", "Dank Depths", "Mausoleum", "Gehenna"]),
        "Chapter 3":                        TBOIRegionData(["The Womb", "Utero", "Scarred Womb", "Mausoleum", "Gehenna", "Ascent"]),
        "Chapter 3.5":                      TBOIRegionData(["The Womb", "Utero", "Scarred Womb", "Corpse"]),
        "Chapter 4":                        TBOIRegionData(["Sheol", "Cathedral", "Blue Womb"]),
        "Chapter 6":                        TBOIRegionData(["Mega Satan"]),

        "Greed Mode":                       TBOIRegionData(),
        "Greedier Mode":                    TBOIRegionData(),
    }

    misc: Dict[str, TBOIRegionData] = {
        "Menu":                             TBOIRegionData([
            "Basement", "Cellar", "Burning Basement",
            "Greed Mode", "Greedier Mode",
        ]),
    }

    all_regions: Dict[str, TBOIRegionData] = {**stages, **chapters, **misc}

    # Set location data
    for location_datum in location_data:
        all_regions[location_datum.region].locations.append(location_datum)

    # Create regions and locations, add them to multiworld
    for region_name, region_data in all_regions.items():
        region = Region(region_name, player, multiworld)

        for location_datum in region_data.locations:
            if location_datum.region == region_name: # Location is at this region
                location = TBOILocation(player, location_datum, region)
                if location.progress_type == LocationProgressType.EXCLUDED:
                    pass
                region.locations.append(location)

        multiworld.regions.append(region)

    # Connect regions
    for region_name, region_data in all_regions.items():
        region = multiworld.get_region(region_name, player)

        if region_data.to_regions:
            region.add_exits(region_data.to_regions)

