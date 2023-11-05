-- Reference: https://github.com/rjstone/cmano-lua-helpers/blob/master/README.md
-- Run this script in the in-game script console during the first load of the scenario to set up handlers for agent action and observation export
-- Save after running script and you will not have to run this script again

-- Edit these variables as needed
local pycmo_path = 'E:/MyProjects/pycmo/'
local lua_script_foldername = pycmo_path .. 'scripts/floridistan/'
local pycmo_lib_lua_filename = pycmo_path .. 'lua/pycmo_lib.lua'
local agent_action_lua_filename = 'agent_action.lua'
local export_observation_lua_filename = 'export_observation.lua'
local execute_agent_action_every_seconds = '0' -- '0' = 1 second, '1' = 5 seconds, '2' = 15 seconds, '3' = 30 seconds, '4' = 1 minute, '5' = 5 minutes, '6' = 15 minutes, '7' = 30 minutes, '8' = 1 hour
local export_observations_every_seconds = '2'
local time_compression = 3 -- 0 = x1, 1 = x2, 2 = x5, 3 = x15, 4 = turbo, 5 = double turbo

-- Call script to setup observation export and agent action handler
ScenEdit_RunScript(pycmo_path .. 'lua/init.lua', true)
setup_observation_export_agent_action(lua_script_foldername, pycmo_lib_lua_filename, agent_action_lua_filename, export_observation_lua_filename, execute_agent_action_every_seconds, export_observations_every_seconds, time_compression)
