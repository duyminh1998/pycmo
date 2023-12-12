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
local export_observations_every_seconds = '3'
local time_compression = 5 -- 0 = x1, 1 = x2, 2 = x5, 3 = x15, 4 = turbo, 5 = double turbo

-- Call script to setup observation export and agent action handler
ScenEdit_RunScript(pycmo_path .. 'lua/init.lua', true)
setup_observation_export_agent_action(lua_script_foldername, pycmo_lib_lua_filename, agent_action_lua_filename, export_observation_lua_filename, execute_agent_action_every_seconds, export_observations_every_seconds, time_compression)

-- Scenario specific events
local BLUE_side_id = '0HXVM6-0HMUSTB12FUD8'
local RED_side_id = '0HXVM6-0HMUSTB12FUDA'
-- When BLUE loses a unit, end the scenario
local scenario_ended_event_name = 'Teardown and end scenario'
local blue_unit_destroyed_trigger_name = 'BLUE unit destroyed'

local scenario_events = ScenEdit_GetEvents(1)
for i = 1, #scenario_events do
    local event = scenario_events[i]
    if event.description == scenario_ended_event_name then
        ScenEdit_SetTrigger({description = blue_unit_destroyed_trigger_name, mode = 'remove'})
    end
end

local scenario_ended_event = ScenEdit_GetEvent(scenario_ended_event_name)
ScenEdit_SetTrigger({mode = 'add', type = 'UnitDestroyed', TargetFilter = {TargetSide = BLUE_side_id}, name = blue_unit_destroyed_trigger_name})
ScenEdit_SetEventTrigger(scenario_ended_event.guid, {mode = 'add', name = blue_unit_destroyed_trigger_name})

-- Add points when BLUE destroys RED target
local blue_destroys_red_target_event_name = 'BLUE destroys RED target'
local blue_destroys_red_target_trigger_name = 'BLUE destroys RED target'
local blue_destroys_red_target_add_points_action_name = 'BLUE destroys RED target add points'
local points_to_add = '300'
local blue_destroys_red_target_end_scenario_action_name = 'BLUE destroys RED target end scenario'
local export_observation_event_name = 'Export observation'
local blue_destroys_red_target_end_scenario_action_script_text = "ScenEdit_RunScript('" .. pycmo_lib_lua_filename .. "', true)\nteardown_and_end_scenario('" .. export_observation_event_name .. "', true)"

local scenario_events = ScenEdit_GetEvents(1)
for i = 1, #scenario_events do
    local event = scenario_events[i]
    if event.description == blue_destroys_red_target_event_name then
        ScenEdit_SetEvent(event.description, {mode = 'remove'})
        ScenEdit_SetTrigger({description = blue_destroys_red_target_trigger_name, mode = 'remove'})
        ScenEdit_SetAction({description = blue_destroys_red_target_add_points_action_name, mode = 'remove'})
        ScenEdit_SetAction({description = blue_destroys_red_target_end_scenario_action_name, mode = 'remove'})
    end
end

local blue_destroys_red_target_event = ScenEdit_SetEvent(blue_destroys_red_target_event_name, {mode='add', IsRepeatable=true})
ScenEdit_SetTrigger({mode = 'add', type = 'UnitDestroyed', TargetFilter = {TargetSide = RED_side_id, TargetType = '8', TargetSubType = '11500', SpecificUnitClass = '181'}, name = blue_destroys_red_target_trigger_name})
ScenEdit_SetEventTrigger(blue_destroys_red_target_event.guid, {mode = 'add', name = blue_destroys_red_target_trigger_name})
ScenEdit_SetAction({mode = 'add',type = 'Points', name = blue_destroys_red_target_add_points_action_name, PointChange = points_to_add, SideID = BLUE_side_id})
ScenEdit_SetEventAction(blue_destroys_red_target_event.guid, {mode = 'add', name = blue_destroys_red_target_add_points_action_name})
ScenEdit_SetAction({mode = 'add',type = 'LuaScript', name = blue_destroys_red_target_end_scenario_action_name, ScriptText = blue_destroys_red_target_end_scenario_action_script_text})
ScenEdit_SetEventAction(blue_destroys_red_target_event.guid, {mode = 'add', name = blue_destroys_red_target_end_scenario_action_name})

-- Deduct points every timestep (?)
local deduct_points_every_timestep_event_name = 'Deduct points every timestep'
local deduct_points_every_timestep_trigger_name = 'Deduct points every timestep'
local deduct_points_every_timestep_action_name = 'Deduct points every timestep'
local deduct_points_every_seconds = export_observations_every_seconds
local points_to_deduct = '-1'

local scenario_events = ScenEdit_GetEvents(1)
for i = 1, #scenario_events do
    local event = scenario_events[i]
    if event.description == deduct_points_every_timestep_event_name then
        ScenEdit_SetEvent(event.description, {mode = 'remove'})
        ScenEdit_SetTrigger({description = deduct_points_every_timestep_trigger_name, mode = 'remove'})
        ScenEdit_SetAction({description = deduct_points_every_timestep_action_name, mode = 'remove'})
    end
end

local deduct_points_every_timestep_event = ScenEdit_SetEvent(deduct_points_every_timestep_event_name, {mode='add', IsRepeatable=true})
ScenEdit_SetTrigger({mode = 'add', type = 'RegularTime', Interval = deduct_points_every_seconds, name = deduct_points_every_timestep_trigger_name})
ScenEdit_SetEventTrigger(deduct_points_every_timestep_event.guid, {mode = 'add', name = deduct_points_every_timestep_trigger_name})
ScenEdit_SetAction({mode = 'add',type = 'Points', name = deduct_points_every_timestep_action_name, PointChange = points_to_deduct, SideID = BLUE_side_id})
ScenEdit_SetEventAction(deduct_points_every_timestep_event.guid, {mode = 'add', name = deduct_points_every_timestep_action_name})
