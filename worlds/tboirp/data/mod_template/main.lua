{% from "macros.lua" import dict_to_lua %}

local mod = RegisterMod("{{ mod_formal_name }}", 1)

ARCHIPELAGO_SEED = "{{ seed_name }}"
ARCHIPELAGO_SLOT = "{{ slot_name }}"

CODE_TO_STATE = {{ dict_to_lua(item_code_to_item_state_key) }}

SHOP_DONATION_LOCATION_COUNT = {{ shop_donation_location_count }}
GREED_DONATION_LOCATION_COUNT = {{ greed_donation_location_count }}
CONSUMABLE_LOCATION_COUNT = {{ consumable_location_count }}

ITEM_STATES = {{ dict_to_lua(item_states) }}

mod:AddPriorityCallback(ModCallbacks.MC_POST_GAME_STARTED, CallbackPriority.IMPORTANT, function(continued)
    include("incoming_ap_data")
    end)