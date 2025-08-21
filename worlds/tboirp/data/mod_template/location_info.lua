{% from "macros.lua" import dict_to_lua %}

return {{ dict_to_lua(location_information) }}