import os
import numpy as np
from gymnasium import spaces

from pycmo.configs.config import get_config
from pycmo.lib.features import FeaturesFromSteam, Weapon, Loadout, Mount, Unit, Contact
from pycmo.lib.spaces import get_contact_space, get_weapon_space, get_loadout_space, get_mount_space, get_unit_space, add_loadout_space_to_unit_space, add_mount_space_to_unit_space
from pycmo.lib.tools import cmo_steam_observation_file_to_xml

config = get_config()

side = "Israel"
side_index = 0
sufa_aircraft_name = "Sufa #3"
sufa_aircraft_ID = "05ba3413-d0cd-4a69-8513-2d7e55d28366"
observation_file_path = os.path.join(config['pycmo_path'], 'tests', "fixtures", 'test_steam_observation.inst')
scenario_xml = cmo_steam_observation_file_to_xml(observation_file_path)

sample_int = np.array((51,), dtype=np.int64)
sample_float = np.array((51.,), dtype=np.float64)

def test_get_weapon_space():
    weapon_space = get_weapon_space()
    assert isinstance(weapon_space, spaces.Dict)
    for k in weapon_space.keys():
        assert k in Weapon._fields
    assert weapon_space["ID"].contains("0HXVM6-0HMUTDCKT5SCN")
    assert weapon_space["WeaponID"].contains(sample_int)
    assert weapon_space["QuantRemaining"].contains(sample_int)
    assert weapon_space["MaxQuant"].contains(sample_int)
    assert not weapon_space["WeaponID"].contains(51)

def test_get_contact_space():
    contact_space = get_contact_space()
    assert isinstance(contact_space, spaces.Dict)
    for k in contact_space.keys():
        assert k in Contact._fields
    assert contact_space["ID"].contains("0HXVM6-0HMUTDCKT5SCN")
    assert contact_space["Name"].contains("SAM Bn (SA-21a Growler [S-400 Triumf])")
    assert contact_space["CS"].contains(sample_float)
    assert contact_space["CA"].contains(sample_float)
    assert contact_space["Lon"].contains(sample_float)
    assert contact_space["Lat"].contains(sample_float)
    assert not contact_space["Lon"].contains(np.array((-510.,), dtype=np.float64))
    assert not contact_space["Lat"].contains(np.array((510.,), dtype=np.float64))

def test_get_mount_space():
    mount_space = get_mount_space()
    assert isinstance(mount_space, spaces.Dict)
    for k in mount_space.keys():
        assert k in Mount._fields
    assert "Weapons" not in mount_space.keys()   
    mount_space = get_mount_space(num_weapons=2)
    assert "Weapons" in mount_space.keys()
    assert mount_space["ID"].contains("0HXVM6-0HMUTDCKT5SCN")
    assert mount_space["Name"].contains("20mm/85 M61A1 Vulcan [512 rnds]")
    assert mount_space["DBID"].contains(sample_int)
    assert len(mount_space["Weapons"]) == 2

def test_get_loadout_space():
    loadout_space = get_loadout_space()
    assert isinstance(loadout_space, spaces.Dict)
    for k in loadout_space.keys():
        assert k in Loadout._fields
    assert "Weapons" not in loadout_space.keys()   
    loadout_space = get_loadout_space(num_weapons=2)
    assert "Weapons" in loadout_space.keys()
    assert loadout_space["ID"].contains(sample_int)
    assert loadout_space["Name"].contains("GBU-53/B SDB-II, Sniper XR Pod [FLIR], Heavy")
    assert loadout_space["DBID"].contains(sample_int)
    assert len(loadout_space["Weapons"]) == 2

def test_get_unit_space():
    unit_space = get_unit_space()
    assert isinstance(unit_space, spaces.Dict)
    for k in unit_space.keys():
        assert k in Unit._fields
    assert unit_space["ID"].contains("0HXVM6-0HMUTDCKT5SCN")
    assert unit_space["Name"].contains("Thunder #1")
    assert unit_space["Side"].contains("BLUE")
    assert unit_space["Type"].contains("Aircraft")
    assert unit_space["CH"].contains(sample_float)
    assert unit_space["CS"].contains(sample_float)
    assert unit_space["CA"].contains(sample_float)
    assert unit_space["Lon"].contains(sample_float)
    assert unit_space["Lat"].contains(sample_float)
    assert not unit_space["Lon"].contains(np.array((-510.,), dtype=np.float64))
    assert not unit_space["Lat"].contains(np.array((510.,), dtype=np.float64))
    assert unit_space["CurrentFuel"].contains(sample_float)
    assert unit_space["MaxFuel"].contains(sample_float)

def test_add_mount_space_to_unit_space():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    sufa = [unit for unit in features.units if unit.Name == sufa_aircraft_name][0]
    test_space = spaces.Dict({"KEY1": spaces.Discrete(1)})
    test_space = add_mount_space_to_unit_space(unit_space = test_space, mounts = sufa.Mounts)
    assert "Mounts" in test_space.keys()
    assert isinstance(test_space["Mounts"], spaces.Dict)
    assert len(test_space["Mounts"].keys()) == 2

def test_add_loadout_space_to_unit_space():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    sufa = [unit for unit in features.units if unit.Name == sufa_aircraft_name][0]
    test_space = spaces.Dict({"KEY1": spaces.Discrete(1)})
    test_space = add_loadout_space_to_unit_space(unit_space = test_space, loadout = sufa.Loadout)
    assert "Loadout" in test_space.keys()
    assert isinstance(test_space["Loadout"], spaces.Dict)
    assert len(test_space["Loadout"].keys()) == 4
    assert "Weapons" in test_space["Loadout"].keys()
    assert len(test_space["Loadout"]["Weapons"]) == 3
