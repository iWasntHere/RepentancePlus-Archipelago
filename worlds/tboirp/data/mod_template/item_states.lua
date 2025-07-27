{% from "macros.lua" import dict_to_lua %}

return {{ dict_to_lua(item_states) }}