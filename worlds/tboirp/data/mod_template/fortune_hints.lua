{% from "macros.lua" import dict_to_lua %}

return {{ dict_to_lua(fortune_hints) }}