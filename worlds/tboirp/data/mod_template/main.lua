{% from "macros.lua" import dict_to_lua %}

local json = require("json")
local mod = RegisterMod("{{ mod_formal_name }}", 1)

AP_SUPP_MOD = mod

ARCHIPELAGO_SEED = "{{ seed_name }}"
ARCHIPELAGO_SLOT = "{{ slot_name }}"

SHOP_DONATION_LOCATION_COUNT = {{ shop_donation_location_count }}
GREED_DONATION_LOCATION_COUNT = {{ greed_donation_location_count }}
CONSUMABLE_LOCATION_COUNT = {{ consumable_location_count }}

mod.itemStates = require("item_states")

local saveState = nil
local FOREIGN_ITEM = -100

-- For saving data persistently
function mod:SaveKey(key, value)
	saveState.save[key] = value
end

-- For loading data persistently!
function mod:LoadKey(key, default)
	local val = saveState.save[key]

	if val == nil then
		return default
	end

	return val
end

-- Load the save file first, so we know what we've processed (or make a new save if we don't have one yet)
-- This is high priority so it runs before the base mod can remove items from the pool
mod:AddPriorityCallback(ModCallbacks.MC_POST_GAME_STARTED, CallbackPriority.IMPORTANT, function(continued)
	if not mod:HasData() then
		saveState = {save = {}, processed_items = {}}
		return
	end

	saveState = json.decode(mod:LoadData())

	-- Use items' state keys to mark them as unlocked
	for key, itemCode in pairs(saveState.processed_items) do
		if itemCode ~= FOREIGN_ITEM then -- Make sure this item is actually for us
			-- Mark item as unlocked (item codes are strings)
			mod.itemStates[tostring(itemCode)] = true
		end
	end
end)

-- Load the input data file so we can get updated from the Archipelago server
mod:AddCallback(ModCallbacks.MC_POST_UPDATE, function()
	if not saveState then
		return
	end

	if Isaac.GetFrameCount() % 60 ~= 0 then -- Only do this once every second
		return
	end

	local incoming_data = ""
	local data = {}

	-- Catch any errors in case there's an issue with file handles
	if not pcall(function ()
		incoming_data = include("incoming_ap_data")
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
				mod.itemStates[tostring(receive_data.item_code)] = true

				Isaac.RunCallback(ArchipelagoModCallbacks.MC_ARCHIPELAGO_ITEM_RECEIVED, receive_data.item_name, receive_data.player_name, receive_data.location_name, false)
			else
				saveState.processed_items[key] = FOREIGN_ITEM -- Mark it as so (with the FOREIGN_ITEM value)

				Isaac.RunCallback(ArchipelagoModCallbacks.MC_ARCHIPELAGO_ITEM_SENT, receive_data.item_name, receive_data.player_name, receive_data.location_name, false)
			end

			-- Update the state table
			needsToSave = true
		end
	end

	-- Update the save
	if needsToSave then
		mod:SaveData(json.encode(saveState))
	end

end)

AP_SUPP_MOD = mod