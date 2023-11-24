import pytest
import os

from pycmo.configs.config import get_config
from pycmo.lib.actions import *

config = get_config()

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
