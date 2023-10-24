local side = "Israel"
local sufa = ScenEdit_GetUnit({side = side, name = "Sufa #1"})
local latitude = math.random() + math.random(-90, 91)
local longitude = math.random() + math.random(-180, 181)
move_unit_to(side, sufa.name, latitude, longitude)