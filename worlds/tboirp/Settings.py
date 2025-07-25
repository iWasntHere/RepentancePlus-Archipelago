import typing

import settings

class TBOISettings(settings.Group):
    class GameDirectory(settings.UserFolderPath):
        """
        The directory where isaac-ng.exe is located.
        """

    class SaveSlot(settings.IntEnum):
        """
        The save slot to use. The game *must* be played on this slot.
        """
        SLOT_1 = 1
        SLOT_2 = 2
        SLOT_3 = 3

    game_directory: GameDirectory = GameDirectory("C:\\Program Files (x86)\\Steam\\steamapps\\common\\The Binding of Isaac Rebirth")

    save_slot: SaveSlot = SaveSlot.SLOT_1