function move_unit_to(side, unit_name, latitude, longitude)
    if latitude >= -90 and latitude <= 90 and longitude >= -180 and longitude <= 180 then
        ScenEdit_SetUnit({side = side, unitname = unit_name, course = {{longitude = longitude, latitude = latitude, TypeOf = 'ManualPlottedCourseWaypoint'}}})
    end
end

-- Functions to emulate ScenEdit_ExportScenarioToXML()
function ScenEdit_ExportScenarioToXML()
    local scenario_xml = "<?xml version='1.0' encoding='utf-8'?><Scenario>"

    local scenario = VP_GetScenario()

    scenario_xml = scenario_xml .. WrapInXML(scenario.Title, 'Title')
    scenario_xml = scenario_xml .. WrapInXML(scenario.FileName, 'FileName')
    scenario_xml = scenario_xml .. WrapInXML(scenario.CurrentTimeNum, 'Time')
    scenario_xml = scenario_xml .. WrapInXML(scenario.StartTimeNum, 'StartTime')
    scenario_xml = scenario_xml .. WrapInXML(scenario.StartTimeNum, 'ZeroHour')
    scenario_xml = scenario_xml .. WrapInXML(scenario.DurationNum, 'Duration')
    scenario_xml = scenario_xml .. WrapInXML(scenario.SaveVersion, 'SaveVersion')
    scenario_xml = scenario_xml .. WrapInXML(scenario.CampaignScore, 'CampaignScore')
    scenario_xml = scenario_xml .. WrapInXML(scenario.HasStarted, 'HasStarted')
    scenario_xml = scenario_xml .. WrapInXML(scenario.Status, 'Status')
    scenario_xml = scenario_xml .. WrapInXML(scenario.TimeCompression, 'TimeCompression')
    scenario_xml = scenario_xml .. WrapInXML(scenario.GameStatus, 'GameStatus')

    scenario_xml = scenario_xml .. WrapInXML(ExportSidesToXML(), 'Sides')
    scenario_xml = scenario_xml .. WrapInXML(ExportUnitsToXML(), 'ActiveUnits')

    scenario_xml = scenario_xml .. '</Scenario>'

    WriteData(scenario_xml, scenario.Title .. '.inst')
end

function ExportSidesToXML()
    local sides_xml = ""

    local sides = VP_GetSides()

    for side_idx = 1, #sides do
        local side = sides[side_idx]

        sides_xml = sides_xml .. "<Side>"

        sides_xml = sides_xml .. WrapInXML(side.guid, 'ID')
        sides_xml = sides_xml .. WrapInXML(side.name, 'Name')
        sides_xml = sides_xml .. WrapInXML(ScenEdit_GetScore(side.name), 'TotalScore')
        sides_xml = sides_xml .. WrapInXML('', 'Missions')
        sides_xml = sides_xml .. WrapInXML('', 'Prof')
        sides_xml = sides_xml .. WrapInXML('', 'Doctrine')

        sides_xml = sides_xml .. "</Side>"
    end

    return sides_xml
end

function ExportUnitsToXML()
    local units_xml = ""

    local sides = VP_GetSides()

    for side_idx = 1, #sides do
        local side = sides[side_idx]
        local side_units = side.units

        for side_unit_idx = 1, #side_units do
            local side_unit = side_units[side_unit_idx]
            units_xml = units_xml .. ExportUnitToXML(side_unit.guid)
        end
    end

    return units_xml
end

function ExportUnitToXML(guid)
    local unit_xml = ""

    local unit = ScenEdit_GetUnit({guid = guid})

    if unit.type == 'Facility' then -- there is a limit to the length of the comment that we can export
        return ''
    end

    unit_xml = unit_xml .. WrapInXML(unit.guid, 'ID')
    unit_xml = unit_xml .. WrapInXML(unit.dbid, 'DBID')
    unit_xml = unit_xml .. WrapInXML(unit.name, 'Name')
    unit_xml = unit_xml .. WrapInXML(unit.side, 'Side')
    unit_xml = unit_xml .. WrapInXML(unit.classname, 'ClassName')
    unit_xml = unit_xml .. WrapInXML(unit.proficiency, 'Proficiency')
    unit_xml = unit_xml .. WrapInXML(unit.latitude, 'Lat')
    unit_xml = unit_xml .. WrapInXML(unit.longitude, 'Lon')
    unit_xml = unit_xml .. WrapInXML(unit.altitude, 'CA')
    unit_xml = unit_xml .. WrapInXML(unit.heading, 'CH')
    unit_xml = unit_xml .. WrapInXML(unit.speed, 'CS')
    unit_xml = unit_xml .. WrapInXML(unit.throttle, 'Thr')
    unit_xml = unit_xml .. WrapInXML(unit.fuelstate, 'FuelState')
    unit_xml = unit_xml .. WrapInXML(unit.weaponstate, 'WeaponState')
    if unit.loadoutdbid ~= nil then
        unit_xml = unit_xml .. WrapInXML(ExportUnitLoadoutToXML(unit.name), 'Loadout')
    end
    unit_xml = unit_xml .. WrapInXML('', 'Doctrine')
    unit_xml = unit_xml .. WrapInXML('', 'Sensors')
    unit_xml = unit_xml .. WrapInXML('', 'Comms')
    unit_xml = unit_xml .. WrapInXML('', 'Propulsion')
    unit_xml = unit_xml .. WrapInXML('', 'Fuel')
    
    return WrapInXML(unit_xml, unit.type)
end

function ExportUnitLoadoutToXML(unitname)
    local loadout_xml = ""

    local unit_loadout = ScenEdit_GetLoadout({unitname = unitname})

    loadout_xml = loadout_xml .. WrapInXML(unit_loadout.dbid, 'ID')
    loadout_xml = loadout_xml .. WrapInXML(unit_loadout.dbid, 'DBID')
    loadout_xml = loadout_xml .. WrapInXML(unit_loadout.name, 'Name')
    loadout_xml = loadout_xml .. WrapInXML(ExportUnitLoadoutWeaponsToXML(unitname), 'Weaps')

    return WrapInXML(loadout_xml, "Loadout")
end

function ExportUnitLoadoutWeaponsToXML(unitname)
    local weapon_xml = ""

    local loadout_weapons = ScenEdit_GetLoadout({unitname = unitname}).weapons

    if #loadout_weapons == 0 then return '' end

    for weapon_idx = 1, #loadout_weapons do
        local loadout_weapon = loadout_weapons[weapon_idx]

        weapon_xml = weapon_xml .. "<WRec>"

        weapon_xml = weapon_xml .. WrapInXML(loadout_weapon.wpn_guid, 'ID')
        weapon_xml = weapon_xml .. WrapInXML(loadout_weapon.wpn_dbid, 'WeapID')
        if loadout_weapon.wpn_current ~= nil then weapon_xml = weapon_xml .. WrapInXML(loadout_weapon.wpn_current, 'CL') end
        if loadout_weapon.wpn_maxcap ~= nil then  weapon_xml = weapon_xml .. WrapInXML(loadout_weapon.wpn_maxcap, 'ML') end

        weapon_xml = weapon_xml .. "</WRec>"
    end

    return weapon_xml
end

function WrapInXML(data, tag)
    return '<' .. tag .. '>' .. tostring(data) .. '</' .. tag .. '>'
end

function WriteData(data, filename)
    -- must have a valid side for ScenEdit_ExportInst to work
    local sides = VP_GetSides() -- use random side to export data because we do not care about what side we use
    ScenEdit_ExportInst(sides[1].name, {}, {filename = filename, comment = data})
end