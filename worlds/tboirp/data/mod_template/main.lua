{% from "macros.lua" import list_to_lua %}

local json = require("json")
local Mod = RegisterMod("{{ mod_formal_name }}", 1)

-- Global var
ArchipelagoSlot = Mod

ArchipelagoSlot.SEED = "{{ seed_name }}"
ArchipelagoSlot.SLOT_NAME = "{{ slot_name }}"

ArchipelagoSlot.SHOP_DONATION_COUNT = {{ shop_donation_location_count }}
ArchipelagoSlot.GREED_DONATION_COUNT = {{ greed_donation_location_count }}
ArchipelagoSlot.CONSUMABLE_COUNT = {{ consumable_location_count }}
ArchipelagoSlot.TARGET_BABY_CODES = {{ list_to_lua(target_baby_codes) }}
ArchipelagoSlot.REQUIRED_BABY_COUNT = {{ required_baby_count }}

ArchipelagoSlot.HINT_FORTUNES = require("fortune_hints")

local itemStates = require("item_states")
local locationInfo = require("location_info")

local saveState = nil
local FOREIGN_ITEM = -100

-- Ensures that the save is loaded by lazy-loading, so the order of execution won't matter
local function ensureSaveIsLoaded()
	if saveState ~= nil then
		return -- Save already loaded, do nothing
	end

	if not Mod:HasData() then -- No save, so create an empty save
		saveState = {save = {}, processed_items = {}}
	else -- Save exists, so load it
		saveState = json.decode(Mod:LoadData())
	end

	-- Use items' state keys to mark them as unlocked
	for key, itemCode in pairs(saveState.processed_items) do
		if itemCode ~= FOREIGN_ITEM then -- Make sure this item is actually for us
			-- Mark item as unlocked (item codes are strings)
			itemStates[tostring(itemCode)] = true
		end
	end
end

-- For checking if an item is unlocked
function Mod:IsItemUnlocked(itemCode)
	ensureSaveIsLoaded()
	local state = itemStates[itemCode]

	if state == nil then
		Archipelago.util.Error("No such item code " .. tostring(itemCode))
	end

	return state
end

-- For checking what items exist at what location
function Mod:GetLocationInfo(locationCode)
    local info = locationInfo[locationCode]

    if info == nil then
         Archipelago.util.Error("No such location code " .. tostring(locationCode))
    end

    return info
end

-- For saving data persistently
function Mod:SaveKey(key, value)
	ensureSaveIsLoaded()

	saveState.save[key] = value
	Mod:SaveData(json.encode(saveState))
end

-- For loading data persistently!
function Mod:LoadKey(key, default)
    ensureSaveIsLoaded()

	local val = saveState.save[key]

	if val == nil then
		return default
	end

	return val
end

-- Stores the length of the last read of incoming_ap_data. The JSON is decoded only when the length changes.
local lastReadLength = 0

-- Load the input data file so we can get updated from the Archipelago server
Mod:AddCallback(ModCallbacks.MC_POST_UPDATE, function()
	if Isaac.GetFrameCount() % 60 ~= 0 then -- Only do this once every second
		return
	end

	ensureSaveIsLoaded()

	local incoming_data = ""
	local data = {}

	-- Catch any errors in case there's an issue with file handles
	if not pcall(function ()
		incoming_data = include("incoming_ap_data")

		-- Don't do anything if the file isn't changed
		local length = string.len(incoming_data)
		if length == lastReadLength then
			error("File is unchanged")
		end

		lastReadLength = length -- Record length for the next read
		data = json.decode(incoming_data)
	end) then
		return
	end

	local needsToSave = false

	-- Now, we compare the "new" data with the saved data.
	-- Diffs are acted upon and the save is updated
	for key, receive_data in pairs(data) do
		if not saveState.processed_items[key] then -- Item isn't processed
			if receive_data.is_for_me then -- We are receiving this item
				saveState.processed_items[key] = receive_data.item_code -- Mark it as so (by using its item code)

				-- Set the item as unlocked (item codes are strings)
				itemStates[tostring(receive_data.item_code)] = true

				Isaac.RunCallback(Archipelago.Callbacks.MC_ARCHIPELAGO_ITEM_RECEIVED, receive_data.item_name, receive_data.player_name, receive_data.location_name, false)
			else
				saveState.processed_items[key] = FOREIGN_ITEM -- Mark it as so (with the FOREIGN_ITEM value)

				Isaac.RunCallback(Archipelago.Callbacks.MC_ARCHIPELAGO_ITEM_SENT, receive_data.item_name, receive_data.player_name, receive_data.location_name, false)
			end

			-- Update the state table
			needsToSave = true
		end
	end

	-- Update the save
	if needsToSave then
		Mod:SaveData(json.encode(saveState))
	end

end)