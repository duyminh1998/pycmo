-- Reference: https://github.com/rjstone/cmano-lua-helpers/blob/master/README.md
-- Run this script in the in-game script console during the first load of the scenario to set up handlers for agent action and observation export
-- Save after running script and you will not have to run this script again

-- Edit these variables as needed
local scripts_path = 'E:/MyProjects/pycmo/scripts/'
local lua_script_foldername = 'steam_demo'
local pycmo_lib_lua_filename = 'pycmo_lib.lua'
local agent_action_lua_filename = 'move_unit_randomly.lua'
local export_observation_lua_filename = 'export_observation.lua'
local execute_agent_action_every_seconds = '0' -- '0' = 1 second, '1' = 5 seconds, '2' = 15 seconds
local export_observations_every_seconds = '1'

-- Should not need to edit anything else after this
local setup_script_text = "local scripts_path = '" .. scripts_path .. "'\nlocal lua_script_foldername = '" .. lua_script_foldername .. "/'\nScenEdit_RunScript(scripts_path .. '" .. pycmo_lib_lua_filename .. "', true)\n"

local agent_action_event_name = 'Execute agent action'
local agent_action_trigger_name = 'Execute agent action every seconds'
local agent_action_name = 'Agent action'
local agent_action_script_text = setup_script_text .. "ScenEdit_RunScript(scripts_path .. lua_script_foldername ..'" .. agent_action_lua_filename .. "', true)"

local execute_agent_action_event = ScenEdit_SetEvent(agent_action_event_name, {mode='add', IsRepeatable=true})
ScenEdit_SetTrigger({mode = 'add', type = 'RegularTime', Interval = execute_agent_action_every_seconds, name = agent_action_trigger_name})
ScenEdit_SetEventTrigger(execute_agent_action_event.guid, {mode = 'add', name = agent_action_trigger_name})
ScenEdit_SetAction({mode = 'add',type = 'LuaScript', name = agent_action_name, ScriptText = agent_action_script_text})
ScenEdit_SetEventAction(execute_agent_action_event.guid, {mode = 'add', name = agent_action_name})

local export_observation_event_name = 'Export observation'
local export_observation_trigger_name = 'Export observation every seconds'
local export_observation_action_name = 'Export observation'
local export_observation_action_script_text = setup_script_text .. "ScenEdit_RunScript(scripts_path .. lua_script_foldername ..'" .. export_observation_lua_filename .. "', true)"

local export_observation_action_event = ScenEdit_SetEvent(export_observation_event_name, {mode='add', IsRepeatable=true})
ScenEdit_SetTrigger({mode = 'add', type = 'RegularTime', Interval = export_observations_every_seconds, name = export_observation_trigger_name})
ScenEdit_SetEventTrigger(export_observation_action_event.guid, {mode = 'add', name = export_observation_trigger_name})
ScenEdit_SetAction({mode = 'add',type = 'LuaScript', name = export_observation_action_name, ScriptText = export_observation_action_script_text})
ScenEdit_SetEventAction(export_observation_action_event.guid, {mode = 'add', name = export_observation_action_name})