import asyncio
import json
import os
import time
from typing import Optional, NamedTuple

from CommonClient import get_base_parser, CommonContext, gui_enabled, server_loop, logger
from NetUtils import NetworkItem
from settings import get_settings
from worlds.tboirp.Settings import TBOISettings

class SentNetworkItem(NamedTuple):
    """Represents an item that was sent from this game."""
    item: int
    location: int
    from_player: int
    to_player: int
    flags: int = 0

class TBOIContext(CommonContext):
    game = "The Binding of Isaac: Repentance+"
    items_handling = 0b111

    locations_checked = set[int] # Location IDs that have been checked locally
    locations_scouted = set[int] # Location IDs that have been scouted locally

    items_received: list[NetworkItem] # Items received from server
    missing_locations: set[int] # Unchecked locations from server
    checked_locations: set[int] # Checked locations from server
    server_locations: set[int] # All locations from server
    location_scout_info: dict[int, NetworkItem] # Location id to scouted item

    items_sent: list[SentNetworkItem] # Items sent to other players (this doesn't need persistence)

    default_unlocked_items: list[int] # Item IDs of things that start unlocked (anything that isn't in the item pool)

    game_directory: str
    save_slot: int

    game_output_file_path: str # The file that will be scanned for outgoing messages from the game, then deleted (the primary mod)
    game_input_file_path: Optional[str] # The file that will be written to pass data to the game (the supplemental mod)

    def __init__(self, server_address, password, game_directory: str, save_slot: int):
        super().__init__(server_address, password)

        self.game_directory = game_directory

        self.save_slot = save_slot
        self.game_output_file_path = os.path.join(game_directory, "data", "archipelago", "save{slot}.dat".format(slot=save_slot))
        self.game_input_file_path = None
        self.items_sent = []

    def run_gui(self):
        from kvui import GameManager

        class TBOIManager(GameManager):
            logging_pairs = [
                ("Client", "Archipelago")
            ]
            base_title = "Archipelago TBOI Client"

        self.ui = TBOIManager(self)
        self.ui_task = asyncio.create_task(self.ui.async_run(), name="UI")

    async def get_username(self):
        logger.info("Please start a run with the Archipelago mod and the supplemental mod installed.")

        while not self.auth:
            await asyncio.sleep(5)

            if not os.path.isfile(self.game_output_file_path): # File doesn't exist
                continue

            timestamp = os.path.getmtime(self.game_output_file_path)

            # File is too old, it needs to have been written to in the last minute for the game to be considered active
            if time.time() - timestamp > 60:
                continue

            # File is new enough, try to get the slot name from it
            contents: str
            with open(self.game_output_file_path, "r") as file:
                contents = file.read()
                file.close()

            # Ensure the ap-data object exists
            data = json.loads(contents)

            # Ensure the data is there
            if "seed_name" not in data or "slot_name" not in data:
                logger.info("No Archipelago data detected. Is the supplemental mod installed?")
                continue

            # All good!
            self.auth = data["slot_name"]
            self.seed_name = data["seed_name"] # Will automatically get disconnect if there is a mismatch


    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super().server_auth(password_requested)

        await self.get_username() # This comes from the connection to the game
        await self.send_connect()

    def on_package(self, cmd: str, args: dict):
        if cmd == "PrintJSON" and "type" in args and args["type"] == "ItemSend": # Log items that we've sent out
            item: NetworkItem = args["item"]
            receiving_slot = args["receiving"]

            # We didn't send this item, or this item is for us... we only care about things WE send OUT
            if item.player != self.slot or receiving_slot == self.slot:
                return

            self.items_sent.append(SentNetworkItem(
                item.item,
                item.location,
                item.player,
                receiving_slot,
                item.flags
            ))

async def handle_sending_locations(ctx: TBOIContext):
    if not os.path.isfile(ctx.game_output_file_path): # No output file, therefore, no locations to send
        return

    send_locations = []
    hint_locations = []
    try:
        # We want to leave the file handle open as much as we can, so quickly read the file and drop the handle
        with open(ctx.game_output_file_path, "r") as file:
            content = file.read()
            file.close()

        data = json.loads(content)

        # Send any locations that need to be sent
        if "location_checks" in data:
            for location_id in data["location_checks"]:
                send_locations.append(location_id)

        # Send any hints that need to be sent
        if "location_scouts" in data:
            for location_id in data["location_scouts"]:
                hint_locations.append(location_id)

        # Now we can nuke the file
        os.remove(ctx.game_output_file_path)
    except Exception as exc:
        logger.error(exc)
    finally:
        if len(send_locations) > 0:
            await ctx.send_msgs([{
                "cmd": "LocationChecks",
                "locations": send_locations,
            }])

        if len(hint_locations) > 0:
            await ctx.send_msgs([{
                "cmd": "LocationScouts",
                "locations": hint_locations,
                "create_as_hint": int(2)
            }])

async def handle_receiving_items(ctx: TBOIContext):
    # These are the items we are receiving
    incoming_items = {  # Python is truly a strange beast
        "{item_code}-{player}-{location_code}".format(item_code=data.item, player=data.player,
                                                      location_code=data.location): {
            "item_name": ctx.item_names.lookup_in_slot(data.item, ctx.slot),
            "player_name": ctx.player_names[data.player],
            "location_name": ctx.location_names.lookup_in_slot(data.location, data.player),
            "item_code": data.item,
            "is_for_me": True
        }
        for data
        in ctx.items_received
    }

    # These are the items that we just sent out. We need to "receive" them so the game can play the notification
    outgoing_items = {
        "{item_code}-{player}-{location_code}".format(item_code=data.item, player=data.to_player,
                                                      location_code=data.location): {
            "item_name": ctx.item_names.lookup_in_slot(data.item, data.to_player),
            "player_name": ctx.player_names[data.to_player],
            "location_name": ctx.location_names.lookup_in_slot(data.location, data.from_player),
            "item_code": data.item,
            "is_for_me": False
        }
        for data
        in ctx.items_sent
    }

    out_content = json.dumps({**incoming_items, **outgoing_items})

    try:
        with open(ctx.game_input_file_path, "w") as file:
            file.write('return "' + out_content.replace('"', '\\"') + '"')
            file.close()
    finally:
        pass  # We don't really care if this fails

async def progression_watcher(ctx: TBOIContext):
    while not ctx.exit_event.is_set():
        if not ctx.username: # Game isn't connected yet
            await asyncio.sleep(5)
            continue

        # Set the input file path
        if ctx.game_input_file_path is None:
            ctx.game_input_file_path = os.path.join(ctx.game_directory, "mods", f"_AP-TBOIRP-{ctx.seed_name}-{ctx.slot_info[ctx.slot].name}", "incoming_ap_data.lua".format(slot=ctx.save_slot))

        await handle_sending_locations(ctx)
        await handle_receiving_items(ctx)

        await asyncio.sleep(1)

settings: TBOISettings = get_settings().tboirp_options

def launch():
    async def main(args):
        ctx = TBOIContext(args.connect, args.password, settings.game_directory, save_slot=settings.save_slot)

        ctx.server_task = asyncio.create_task(
            server_loop(ctx), name="server loop")

        asyncio.create_task(
            progression_watcher(ctx), name="TBOIProgressionWatcher")

        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        await ctx.exit_event.wait()
        ctx.server_address = None

        await ctx.shutdown()

    import colorama

    parser = get_base_parser(description="Client for The Binding of Isaac: Repentance+")

    args, rest = parser.parse_known_args()
    colorama.just_fix_windows_console()
    asyncio.run(main(args))
    colorama.deinit()
