import collections

# pylint: disable=line-too-long
available_functions = ["no_op", "ScenEdit_AddMission", "ScenEdit_AddReferencePoint", "ScenEdit_AssignUnitAsTarget", 
"ScenEdit_AssignUnitToMission", "ScenEdit_AttackContact", "ScenEdit_DeleteMission", "ScenEdit_DeleteReferencePoint",
"ScenEdit_RefuelUnit", "ScenEdit_RemoveUnitAsTarget", "ScenEdit_SetEMCON", "ScenEdit_SetLoadout", "ScenEdit_SetMission",
"ScenEdit_SetReferencePoint", "ScenEdit_SetUnit"]

def no_op():
  return ""

def launch_aircraft(side, aircraft_name, launch_yn):
  return "ScenEdit_SetUnit({{side = '{}', name = '{}', Launch = '{}'}})".format(side, aircraft_name, launch_yn)

def set_unit_course(side, aircraft_name, latitude, longitude):
  data = "ScenEdit_SetUnit({{side = '{}', name = '{}', course = {{".format(side, aircraft_name)
  data += "{{longitude = '{}', latitude = '{}', TypeOf = 'ManualPlottedCourseWaypoint'}}".format(latitude, longitude)
  data += "}})"
  return data

def manual_attack_contact(attacker_id, contact_id, weapon_id, qty, mount_id=None):
  if mount_id == None:
    return "ScenEdit_AttackContact('{}', '{}' ,{{mode='1', weapon='{}', qty='{}'}})".format(attacker_id, contact_id, weapon_id, qty)
  else:
    return "ScenEdit_AttackContact('{}', '{}' ,{{mode='1', mount='{}', weapon='{}', qty='{}'}})".format(attacker_id, contact_id, mount_id, weapon_id, qty)

def auto_attack_contact(attacker_id, contact_id):
  return "ScenEdit_AttackContact('{}', '{}',{{mode='1'}})".format(attacker_id, contact_id)

def refuel_unit(side, unit_name, tanker_name):
  return "ScenEdit_RefuelUnit({{side='{}', unitname='{}', tanker='{}'}})".format(side, unit_name, tanker_name)

Function = collections.namedtuple("Function", ['id', 'name', 'corresponding_def', 'args'])

class AvailableFunctions():
  def __init__(self, features):
    sides = [features.player_side]
    units = []
    contacts = []
    if features.units != None:
      units = [unit.ID for unit in features.units]
    if features.contacts != None:
      contacts = [contact.ID for contact in features.contacts]
    weapons = []
    mounts = []
    for unit in features.units:
      if unit.Mounts != None:
        for mount in unit.Mounts:
          mounts.append(mount.DBID)
          if mount.Weapons != None:
            for weapon in mount.Weapons:
              weapons.append(weapon.WeaponID)
    VALID_FUNCTION_ARGS = {
      'no_op': [],
      'launch_aircraft': [sides, units, ["true", "false"]],
      'set_unit_course': [sides, units, [-90, 90], [-180, 180]],
      'manual_attack_contact': [units, contacts, weapons, [1], mounts],
      'auto_attack_contact': [units, contacts],
      'refuel_unit': [sides, units, units]
    }
    self.VALID_FUNCTIONS = [
      Function(0, "no_op", no_op, VALID_FUNCTION_ARGS['no_op']),
      Function(1, "launch_aircraft", launch_aircraft, VALID_FUNCTION_ARGS['launch_aircraft']),
      Function(2, 'set_unit_course', set_unit_course, VALID_FUNCTION_ARGS['set_unit_course']),
      Function(3, "manual_attack_contact", manual_attack_contact, VALID_FUNCTION_ARGS['manual_attack_contact']),
      Function(4, "auto_attack_contact", auto_attack_contact, VALID_FUNCTION_ARGS['auto_attack_contact']),
      Function(5, 'refuel_unit', refuel_unit, VALID_FUNCTION_ARGS['refuel_unit'])   
    ]
