function setup_observation_export_agent_action(lua_script_foldername, pycmo_lib_lua_filename, agent_action_lua_filename, export_observation_lua_filename, execute_agent_action_every_seconds, export_observations_every_seconds)
    local setup_script_text = "local lua_script_foldername = '" .. lua_script_foldername .. "'\nScenEdit_RunScript('" .. pycmo_lib_lua_filename .. "', true)\n"

    local agent_action_event_name = 'Execute agent action'
    local agent_action_trigger_name = 'Execute agent action every seconds'
    local agent_action_name = 'Agent action'
    local agent_action_script_text = setup_script_text .. "ScenEdit_RunScript(lua_script_foldername ..'" .. agent_action_lua_filename .. "', true)"
    
    -- Remove these events, triggers, and actions if they are already present
    local scenario_events = ScenEdit_GetEvents(1)
    for i = 1, #scenario_events do
        local event = scenario_events[i]
        if event.description == agent_action_event_name then
            ScenEdit_SetEvent(event.description, {mode = 'remove'})
            ScenEdit_SetTrigger({description = agent_action_trigger_name, mode = 'remove'})
            ScenEdit_SetAction({description = agent_action_name, mode = 'remove'})
        end
    end
    
    local execute_agent_action_event = ScenEdit_SetEvent(agent_action_event_name, {mode='add', IsRepeatable=true})
    ScenEdit_SetTrigger({mode = 'add', type = 'RegularTime', Interval = execute_agent_action_every_seconds, name = agent_action_trigger_name})
    ScenEdit_SetEventTrigger(execute_agent_action_event.guid, {mode = 'add', name = agent_action_trigger_name})
    ScenEdit_SetAction({mode = 'add',type = 'LuaScript', name = agent_action_name, ScriptText = agent_action_script_text})
    ScenEdit_SetEventAction(execute_agent_action_event.guid, {mode = 'add', name = agent_action_name})
    
    local export_observation_event_name = 'Export observation'
    local export_observation_trigger_name = 'Export observation every seconds'
    local export_observation_action_name = 'Export observation'
    local export_observation_action_script_text = setup_script_text .. "ScenEdit_RunScript(lua_script_foldername ..'" .. export_observation_lua_filename .. "', true)"
    
    -- Remove these events, triggers, and actions if they are already present
    local scenario_events = ScenEdit_GetEvents(1)
    for i = 1, #scenario_events do
        local event = scenario_events[i]
        if event.description == export_observation_event_name then
            ScenEdit_SetEvent(event.description, {mode = 'remove'})
            ScenEdit_SetTrigger({description = export_observation_trigger_name, mode = 'remove'})
            ScenEdit_SetAction({description = export_observation_action_name, mode = 'remove'})
        end
    end
    
    local export_observation_action_event = ScenEdit_SetEvent(export_observation_event_name, {mode='add', IsRepeatable=true})
    ScenEdit_SetTrigger({mode = 'add', type = 'RegularTime', Interval = export_observations_every_seconds, name = export_observation_trigger_name})
    ScenEdit_SetEventTrigger(export_observation_action_event.guid, {mode = 'add', name = export_observation_trigger_name})
    ScenEdit_SetAction({mode = 'add',type = 'LuaScript', name = export_observation_action_name, ScriptText = export_observation_action_script_text})
    ScenEdit_SetEventAction(export_observation_action_event.guid, {mode = 'add', name = export_observation_action_name})
    
    -- Set up an event to export the scenario when it is first loaded
    local export_observation_event_name = 'Export observation initially'
    local export_observation_trigger_name = 'Scenario is Loaded'
    local export_observation_action_name = 'Export observation initially'
    local export_observation_action_script_text = "ScenEdit_RunScript('" .. pycmo_lib_lua_filename .. "', true)\nScenEdit_ExportScenarioToXML()"
    
    -- Remove these events, triggers, and actions if they are already present
    local scenario_events = ScenEdit_GetEvents(1)
    for i = 1, #scenario_events do
        local event = scenario_events[i]
        if event.description == export_observation_event_name then
            ScenEdit_SetEvent(event.description, {mode = 'remove'})
            ScenEdit_SetTrigger({description = export_observation_trigger_name, mode = 'remove'})
            ScenEdit_SetAction({description = export_observation_action_name, mode = 'remove'})
        end
    end
    
    local export_observation_action_event = ScenEdit_SetEvent(export_observation_event_name, {mode='add', IsRepeatable=true})
    ScenEdit_SetTrigger({mode = 'add', type = 'ScenLoaded', name = export_observation_trigger_name})
    ScenEdit_SetEventTrigger(export_observation_action_event.guid, {mode = 'add', name = export_observation_trigger_name})
    ScenEdit_SetAction({mode = 'add',type = 'LuaScript', name = export_observation_action_name, ScriptText = export_observation_action_script_text})
    ScenEdit_SetEventAction(export_observation_action_event.guid, {mode = 'add', name = export_observation_action_name})
end
