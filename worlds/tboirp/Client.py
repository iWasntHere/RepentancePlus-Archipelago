import asyncio
import json
import os
import time

from CommonClient import get_base_parser, CommonContext, gui_enabled, server_loop, logger
from NetUtils import NetworkItem
from settings import get_settings
from worlds.tboirp.Settings import TBOISettings


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

    default_unlocked_items: list[int] # Item IDs of things that start unlocked (anything that isn't in the item pool)

    game_directory: str
    save_slot: int

    game_output_file_path: str # The file that will be scanned for outgoing messages from the game, then deleted (the primary mod)
    game_input_file_path: str # The file that will be written to pass data to the game (the supplemental mod)

    def __init__(self, server_address, password, game_directory: str, save_slot: int):
        super().__init__(server_address, password)

        self.game_directory = game_directory

        self.game_output_file_path = os.path.join(game_directory, "data", "archipelago", "save{slot}.dat".format(slot=save_slot))

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
            if "ap_data" not in data:
                logger.info("No Archipelago data in file! Is the supplemental mod installed?")
                continue

            ap_data = data["ap_data"]

            logger.info(ap_data)

            # Ensure the data is there
            if "seed_name" not in ap_data or "slot_name" not in ap_data:
                logger.info("Critical data missing from file!!")
                continue

            # All good!
            self.auth = ap_data["slot_name"]
            self.seed_name = ap_data["seed_name"] # Will automatically get disconnect if there is a mismatch


    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super().server_auth(password_requested)

        await self.get_username() # This comes from the connection to the game
        await self.send_connect()

async def progression_watcher(ctx: TBOIContext):
    while not ctx.exit_event.is_set():
        if not ctx.slot_name: # Game isn't connected yet
            await asyncio.sleep(5)
            continue

        # Set the input file path
        if ctx.game_input_file_path is None:
            ctx.game_input_file_path = os.path.join(ctx.game_directory, "mods", f"_AP-TBOIRP-{ctx.seed_name}-{ctx.slot_info[ctx.slot].name}", "incoming_ap_data.lua".format(slot=ctx.save_slot))

        send_locations = []
        hint_locations = []
        number = 0
        try:
            # We want to leave the file handle open as much as we can, so quickly read the file and drop the handle
            with open(ctx.game_output_file_path ,"r") as file:
                content = file.read()
                file.close()

            data = json.loads(content)

            logger.info(content)

            number = data["number"] if data["number"] else 0

            # Send any locations that need to be sent
            if "send_locations" in data:
                for location_id in data["send_locations"]:
                    send_locations.append(location_id)

            # Send any hints that need to be sent
            if "hint_locations" in data:
                for location_id in data["hint_locations"]:
                    hint_locations.append(location_id)
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

        try:
            # We need to convert the JSON to a lua string so we can import it properly in-game
            out_json = json.dumps({"number": number + 1}).replace('"', '\\\"')
            out_content = "jsonString=\"{json}\"".format(json=out_json) # All quotes need to be escaped

            # We want to leave the file handle open as much as we can, so quickly read the file and drop the handle
            with open(ctx.game_input_file_path ,"w") as file:
                content = file.write(out_content)
                file.close()
        finally:
            pass

        await asyncio.sleep(5)

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
