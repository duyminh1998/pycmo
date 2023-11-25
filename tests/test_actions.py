import pytest
import os

from pycmo.configs.config import get_config
from pycmo.lib.actions import *
from pycmo.lib.tools import cmo_steam_observation_file_to_xml

config = get_config()

observation_file_path = os.path.join(config['pycmo_path'], 'tests', "fixtures", 'test_steam_observation.inst')
scenario_xml = cmo_steam_observation_file_to_xml(observation_file_path)

side = "Israel"
tanker_name = "Chevron #6"
aircraft_name = "Sufa #1"
aircraft_ID = "6352f8eb-db07-4916-8da7-33ef013878a0"
weapon_ID = "4369"
weapon_qty = 4
mount_ID = "1256"
target_name = "Bogey #1"
target_ID = "0HXVM6-0HMUTDCKTG4A6"
launch_aircraft_test_parameters = [
    (side, aircraft_name, "true", f"ScenEdit_SetUnit({{side = '{side}', name = '{aircraft_name}', Launch = 'true'}})"),
    (side, aircraft_name, "false", f"ScenEdit_SetUnit({{side = '{side}', name = '{aircraft_name}', Launch = 'false'}})"),
]
manual_attack_contact_parameters = [
    (aircraft_ID, target_ID, weapon_ID, weapon_qty, mount_ID, f"ScenEdit_AttackContact('{aircraft_ID}', '{target_ID}' , {{mode='1', mount='{mount_ID}', weapon='{weapon_ID}', qty='{weapon_qty}'}})"),
    (aircraft_ID, target_ID, weapon_ID, weapon_qty, None, f"ScenEdit_AttackContact('{aircraft_ID}', '{target_ID}' , {{mode='1', weapon='{weapon_ID}', qty='{weapon_qty}'}})"),
]

def test_no_op():
    assert no_op() == ""

@pytest.mark.parametrize("side, aircraft_name, launch_yn, expected", launch_aircraft_test_parameters)
def test_launch_aircraft(side, aircraft_name, launch_yn, expected):
    assert launch_aircraft(side, aircraft_name, launch_yn) == expected

@pytest.mark.parametrize("attacker_id, contact_id, weapon_id, qty, mount_id, expected", manual_attack_contact_parameters)
def test_manual_attack_contact(attacker_id, contact_id, weapon_id, qty, mount_id, expected):
    assert manual_attack_contact(attacker_id, contact_id, weapon_id, qty, mount_id) == expected

def test_auto_attack_contact():
    assert auto_attack_contact(aircraft_ID, target_ID) == f"ScenEdit_AttackContact('{aircraft_ID}', '{target_ID}', {{mode='0'}})"

def test_refuel_unit():
    assert refuel_unit(side, aircraft_name, tanker_name) == f"ScenEdit_RefuelUnit({{side='{side}', unitname='{aircraft_name}', tanker='{tanker_name}'}})"

def test_auto_refuel_unit():
    assert auto_refuel_unit(side, aircraft_name) == f"ScenEdit_RefuelUnit({{side='{side}', unitname='{aircraft_name}'}})"

def test_rtb():
    assert rtb(side, aircraft_name) == f"ScenEdit_SetUnit({{side = '{side}', name = '{aircraft_name}', RTB = true}})"

features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
avail_funcs = AvailableFunctionsSteam(features=features)
unit_id = "05ba3413-d0cd-4a69-8513-2d7e55d28366"
mount_id = "286"
loadout_id = "18127"
mount_weapon_id = "1918"
loadout_weapon_id = "516"
def test_available_functions():
    assert isinstance(avail_funcs, AvailableFunctionsSteam)

def test_available_functions_sides():
    assert len(avail_funcs.sides) == 1
    assert avail_funcs.sides[0] == side

def test_available_functions_unit_ids():
    assert len(avail_funcs.unit_ids) == 9
    assert isinstance(avail_funcs.unit_ids[0], str)
    assert avail_funcs.unit_ids[0] == "8e2750c4-6c86-46a4-8dfa-16507c7f71e3"

def test_available_functions_contact_ids():
    assert len(avail_funcs.contact_ids) == 8
    assert isinstance(avail_funcs.contact_ids[0], str)
    assert avail_funcs.contact_ids[0] == "0HXVM6-0HMUTDCKTG4AA"

def test_available_functions_mount_ids():
    assert len(avail_funcs.mount_ids[unit_id]) == 2
    assert isinstance(avail_funcs.mount_ids[unit_id], list)
    assert avail_funcs.mount_ids[unit_id][0] == mount_id

def test_available_functions_loadout_ids():
    assert len(avail_funcs.loadout_ids[unit_id]) == 1
    assert isinstance(avail_funcs.loadout_ids[unit_id], list)
    assert avail_funcs.loadout_ids[unit_id][0] == loadout_id

def test_available_functions_mount_weapon_ids():
    key = f"{unit_id},{mount_id}"
    assert len(avail_funcs.weapon_ids) == 20
    assert isinstance(avail_funcs.weapon_ids[key], list)
    assert avail_funcs.weapon_ids[key][0] == mount_weapon_id

def test_available_functions_loadout_weapon_ids():
    key = f"{unit_id},{loadout_id}"
    assert len(avail_funcs.weapon_ids) == 20
    assert isinstance(avail_funcs.weapon_ids[key], list)
    assert avail_funcs.weapon_ids[key][0] == loadout_weapon_id

def test_available_functions_mount_weapon_qtys():
    key = f"{unit_id},{mount_id},{mount_weapon_id}"
    assert len(avail_funcs.weapon_qtys) == 45
    assert isinstance(avail_funcs.weapon_qtys[key], int)
    assert avail_funcs.weapon_qtys[key] == 5

def test_available_functions_loadout_weapon_qtys():
    key = f"{unit_id},{loadout_id},{loadout_weapon_id}"
    assert len(avail_funcs.weapon_qtys) == 45
    assert isinstance(avail_funcs.weapon_qtys[key], int)
    assert avail_funcs.weapon_qtys[key] == 4

def test_available_functions_valid_functions():
    manual_attack_fnc = avail_funcs.VALID_FUNCTIONS[3]
    assert isinstance(avail_funcs.VALID_FUNCTIONS, list)
    assert len(avail_funcs.VALID_FUNCTIONS) == 8
    assert isinstance(manual_attack_fnc, Function)
    assert manual_attack_fnc.id == 3
    assert manual_attack_fnc.name == "manual_attack_contact"
    assert manual_attack_fnc.corresponding_def == manual_attack_contact
    assert isinstance(manual_attack_fnc.args, list)
    weapon_id_args = manual_attack_fnc.args[2]
    assert isinstance(weapon_id_args, set)
    assert isinstance(list(weapon_id_args)[0], str)
    weapon_qty_args = manual_attack_fnc.args[3]
    assert isinstance(weapon_qty_args, set)
    assert isinstance(list(weapon_qty_args)[0], int)
    mount_id_args = manual_attack_fnc.args[4]
    assert isinstance(mount_id_args, set)
    assert isinstance(list(mount_id_args)[0], str)
