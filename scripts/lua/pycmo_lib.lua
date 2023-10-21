-- Convert a contacts table into a lua syntactically correct string
function contacts_table_to_string(tbl)
    local result = "{"
    for k, v in pairs(tbl) do
        -- Check the key type (ignore any numerical keys - assume its an array)
        if type(k) == "string" then
            result = result.."[\""..k.."\"]".."="
        end

        -- Check the value type
        if type(v) == "table" then
            result = result..table_to_string(v)
        elseif type(v) == "boolean" then
            result = result..tostring(v)
        else
            result = result.."\""..v.guid.."\""
        end
        result = result..","
    end
    -- Remove leading commas from the result
    if result ~= "{" then
        result = result:sub(1, result:len()-1)
    end
    return result.."}"
end

function move_unit_to(side, unit_name, latitude, longitude)
    print(latitude)
    if latitude >= -90 and latitude <= 90 and longitude >= -180 and longitude <= 180 then
        ScenEdit_SetUnit({side = side, unitname = unit_name, course = {{longitude = longitude, latitude = latitude, TypeOf = 'ManualPlottedCourseWaypoint'}}})
    end
end

function export_observation(side, units_guid, local_file_name, ingame_inst_name, comments)
    ScenEdit_ExportInst(side, units_guid, {filename = local_file_name, name = ingame_inst_name, comment = comments})
end