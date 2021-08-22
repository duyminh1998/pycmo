# Author: Minh Hua
# Date: 08/16/2021
# Purpose: Encodes the action space of the game.

# imports
import collections

available_functions = ["no_op", "ScenEdit_AddMission", "ScenEdit_AddReferencePoint", "ScenEdit_AssignUnitAsTarget", 
"ScenEdit_AssignUnitToMission", "ScenEdit_AttackContact", "ScenEdit_DeleteMission", "ScenEdit_DeleteReferencePoint",
"ScenEdit_RefuelUnit", "ScenEdit_RemoveUnitAsTarget", "ScenEdit_SetEMCON", "ScenEdit_SetLoadout", "ScenEdit_SetMission",
"ScenEdit_SetReferencePoint", "ScenEdit_SetUnit"]

def no_op():
  return "--script \nTool_EmulateNoConsole(true)"

def launch_aircraft(side, aircraft_name, launch_yn):
  return "--script \nTool_EmulateNoConsole(true) \nScenEdit_SetUnit({{side = '{}', name = '{}', Launch = '{}'}})".format(side, aircraft_name, launch_yn)

def set_unit_course(side, aircraft_name, latitude, longitude):
  data = "--script \nTool_EmulateNoConsole(true) \nScenEdit_SetUnit({{side = '{}', name = '{}', course = {{".format(side, aircraft_name)
  data += "{{longitude = '{}', latitude = '{}', TypeOf = 'ManualPlottedCourseWaypoint'}}".format(latitude, longitude)
  data += "}})"
  return data

def manual_attack_contact(attacker_id, contact_id, weapon_id, qty, mount_id=None):
  if mount_id == None:
    return "--script \nTool_EmulateNoConsole(true) \nScenEdit_AttackContact('{}', '{}' ,{{mode='1', weapon='{}', qty='{}'}})".format(attacker_id, contact_id, weapon_id, qty)
  else:
    return "--script \nTool_EmulateNoConsole(true) \nScenEdit_AttackContact('{}', '{}' ,{{mode='1', mount='{}', weapon='{}', qty='{}'}})".format(attacker_id, contact_id, mount_id, weapon_id, qty)

def auto_attack_contact(attacker_id, contact_id):
  return "--script \nTool_EmulateNoConsole(true) \nScenEdit_AttackContact('{}', '{}',{{mode='0'}})".format(attacker_id, contact_id)

def refuel_unit(side, unit_name, tanker_name):
  return "--script \nTool_EmulateNoConsole(true) \nScenEdit_RefuelUnit({{side='{}', unitname='{}', tanker='{}'}})".format(side, unit_name, tanker_name)

def auto_refuel(side, unit_name):
  return "--script \nTool_EmulateNoConsole(true) \nScenEdit_RefuelUnit({{side='{}', unitname='{}'}})".format(side, unit_name)

def rtb(side, aircraft_name):
  return "--script \nTool_EmulateNoConsole(true) \nScenEdit_SetUnit({{side = '{}', name = '{}', RTB = true}})".format(side, aircraft_name)

Function = collections.namedtuple("Function", ['id', 'name', 'corresponding_def', 'args', 'arg_types'])

class AvailableFunctions():
  def __init__(self, features):
    sides = [features.player_side]
    units = []
    contacts = []
    if features.units != None:
      units = [unit.ID for unit in features.units]
    if features.contacts != None:
      contacts = [contact.ID for contact in features.contacts]
    weapons = [weap.WeaponID for weap in features.avai_weapons]
    mounts = []
    for unit in features.units:
      if unit.Mounts != None:
        for mount in unit.Mounts:
          mounts.append(mount.DBID)
    VALID_FUNCTION_ARGS = {
      'no_op': [],
      'launch_aircraft': [sides, units, ["true", "false"]],
      'set_unit_course': [sides, units, [-90, 90], [-180, 180]],
      'manual_attack_contact': [units, contacts, weapons, [1], mounts],
      'auto_attack_contact': [units, contacts],
      'refuel_unit': [sides, units, units],
      'rtb': [sides, units],
      'auto_refuel': [sides, units]
    }
    ARG_TYPES = {
      'no_op': ['NoneChoice'],
      'launch_aircraft': ['EnumChoice', 'EnumChoice', 'EnumChoice'],
      'set_unit_course': ['EnumChoice', 'EnumChoice', 'Range', 'Range'],
      'manual_attack_contact': ['EnumChoice', 'EnumChoice', 'EnumChoice', 'EnumChoice', 'EnumChoice'],
      'auto_attack_contact': ['EnumChoice', 'EnumChoice'],
      'refuel_unit': ['EnumChoice', 'EnumChoice', 'EnumChoice'],
      'rtb': ['EnumChoice', 'EnumChoice'],
      'auto_refuel': ['EnumChoice', 'EnumChoice']
    }
    self.VALID_FUNCTIONS = [
      Function(0, "no_op", no_op, VALID_FUNCTION_ARGS['no_op'], ARG_TYPES['no_op']),
      Function(1, "launch_aircraft", launch_aircraft, VALID_FUNCTION_ARGS['launch_aircraft'], ARG_TYPES['launch_aircraft']),
      Function(2, 'set_unit_course', set_unit_course, VALID_FUNCTION_ARGS['set_unit_course'], ARG_TYPES['set_unit_course']),
      Function(3, "manual_attack_contact", manual_attack_contact, VALID_FUNCTION_ARGS['manual_attack_contact'], ARG_TYPES['manual_attack_contact']),
      Function(4, "auto_attack_contact", auto_attack_contact, VALID_FUNCTION_ARGS['auto_attack_contact'], ARG_TYPES['auto_attack_contact']),
      Function(5, 'refuel_unit', refuel_unit, VALID_FUNCTION_ARGS['refuel_unit'], ARG_TYPES['refuel_unit']),
      Function(6, 'rtb', rtb, VALID_FUNCTION_ARGS['rtb'], ARG_TYPES['rtb']),
      Function(7, 'auto_refuel', auto_refuel, VALID_FUNCTION_ARGS['auto_refuel'], ARG_TYPES['auto_refuel'])
    ]
