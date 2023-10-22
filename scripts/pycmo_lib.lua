function move_unit_to(side, unit_name, latitude, longitude)
    if latitude >= -90 and latitude <= 90 and longitude >= -180 and longitude <= 180 then
        ScenEdit_SetUnit({side = side, unitname = unit_name, course = {{longitude = longitude, latitude = latitude, TypeOf = 'ManualPlottedCourseWaypoint'}}})
    end
end

function export_observation(side, units_guid, local_file_name, ingame_inst_name, comments)
    ScenEdit_ExportInst(side, units_guid, {filename = local_file_name, name = ingame_inst_name, comment = comments})
end