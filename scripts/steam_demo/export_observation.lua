local side = "Israel"
local sufa = ScenEdit_GetUnit({side = side, name = "Sufa #1"})
export_observation(side, {sufa.guid}, side .. '_units.inst', side .. '_units', 'Extra data can go here')

-- pause the scenario
local msg_boix = ScenEdit_MsgBox('Scenario paused', 0)