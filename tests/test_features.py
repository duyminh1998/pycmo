import pytest
import os
import math

from pycmo.configs.config import get_config
from pycmo.lib.features import FeaturesFromSteam, Game, Side, Weapon, Loadout, Mount, Unit, Contact
from pycmo.lib.tools import cmo_steam_observation_file_to_xml

config = get_config()

side = "Israel"
side_index = 0
sufa_aircraft_name = "Sufa #3"
sufa_aircraft_ID = "05ba3413-d0cd-4a69-8513-2d7e55d28366"
observation_file_path = os.path.join(config['pycmo_path'], 'tests', "fixtures", 'test_steam_observation.inst')
scenario_xml = cmo_steam_observation_file_to_xml(observation_file_path)

def test_features_from_steam_init():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    assert isinstance(features, FeaturesFromSteam)
    scen_dic = features.scen_dic
    units = features.units
    assert len(scen_dic['Scenario']['ActiveUnits']['Aircraft']) == 8
    assert scen_dic['Scenario']['Title'] == 'Steam demo'
    assert len(scen_dic['Scenario']['Sides']['Side']) == 2
    assert len(units) == 9

def test_features_from_steam_get_meta():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    meta = features.get_meta()
    assert isinstance(meta, Game)
    assert meta.TimelineID is None
    assert meta.ScenarioName == "Steam demo"
    assert meta.Time == 1519552951
    assert meta.ZeroHour == 1519552800
    assert meta.StartTime == 1519552800
    assert meta.Duration == 21600
    assert meta.Sides == ["Israel", "Syria"]

def test_features_from_steam_get_sides():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    sides = features.get_sides()
    assert len(sides) == 2
    assert sides[0] == "Israel"
    assert sides[1] == "Syria"

def test_features_from_steam_get_side_properties():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    side_properties = features.get_side_properties(0)
    assert isinstance(side_properties, Side)
    assert side_properties.Name == "Israel"
    assert side_properties.ID == "c2fbbdf2-3db5-4160-af9d-01cd6e545232"
    assert side_properties.TotalScore == 0

def test_features_from_steam_get_loadout_weapon():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    loadout = features.scen_dic["Scenario"]["ActiveUnits"]['Aircraft'][1]["Loadout"]["Loadout"]
    weapons = features.get_loadout_or_mount_weapons('Loadout', loadout)
    assert len(weapons) == 3
    
    weapon = weapons[0]

    assert isinstance(weapon, Weapon)
    assert weapon.ID == 'E9MD86-0HMTL4284RD9I'
    assert weapon.WeaponID == 516
    assert weapon.QuantRemaining == 4
    assert weapon.MaxQuant == 4

def test_features_from_steam_get_mount_weapon():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    mount = features.scen_dic["Scenario"]["ActiveUnits"]['Aircraft'][1]["Mounts"]["Mount"][1]
    weapons = features.get_loadout_or_mount_weapons('Mount', mount)
    assert len(weapons) == 2
    
    weapon = weapons[0]

    assert isinstance(weapon, Weapon)
    assert weapon.ID == 'E9MD86-0HMTL4284RD8T'
    assert weapon.WeaponID == 564
    assert weapon.QuantRemaining == 12
    assert weapon.MaxQuant == 12

def test_features_from_steam_get_loadout():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    unit = features.scen_dic["Scenario"]["ActiveUnits"]['Aircraft'][1]
    loadout = features.get_loadout(unit)
    
    assert isinstance(loadout, Loadout)
    assert loadout.ID == 18127
    assert loadout.Name == 'A/A: Python 5, Light 004'
    assert loadout.DBID == 18127
    assert loadout.Weapons == features.get_loadout_or_mount_weapons('Loadout', unit["Loadout"]["Loadout"])

def test_features_from_steam_get_mount():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    unit = features.scen_dic["Scenario"]["ActiveUnits"]['Aircraft'][1]
    mounts = features.get_mount(unit)

    assert len(mounts) == 2

    mount = mounts[0]
    
    assert isinstance(mount, Mount)
    assert mount.ID == 'E9MD86-0HMTL4284RD8O'
    assert mount.Name == '20mm/85 M61A1 Vulcan [515 rnds]'
    assert mount.DBID == 286
    assert mount.Weapons == features.get_loadout_or_mount_weapons('Mount', unit["Mounts"]["Mount"][0])

def test_features_from_steam_get_unit_fuel():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    sufa_aircraft = features.units[2]
    assert sufa_aircraft.Name == sufa_aircraft_name
    assert sufa_aircraft.CurrentFuel == 8450
    assert sufa_aircraft.MaxFuel == 8450

def test_features_from_steam_get_unit():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    unit_type = "Aircraft"
    active_units = features.scen_dic["Scenario"]["ActiveUnits"][unit_type]
    active_unit = active_units[1]
    sufa_aircraft = features.get_unit(active_unit, 0, unit_type, side)
    assert isinstance(sufa_aircraft, Unit)
    assert sufa_aircraft.Name == sufa_aircraft_name
    assert sufa_aircraft.ID == sufa_aircraft_ID
    assert sufa_aircraft.Side == "Israel"
    assert sufa_aircraft.DBID == 4508
    assert sufa_aircraft.Type == "Aircraft"
    assert math.isclose(sufa_aircraft.CH, 0.0)
    assert math.isclose(sufa_aircraft.CS, 350.0)
    assert math.isclose(sufa_aircraft.CA, 55.0)
    assert math.isclose(sufa_aircraft.Lon, 35.183342038182)
    assert math.isclose(sufa_aircraft.Lat, 32.66746735647)
    assert math.isclose(sufa_aircraft.CurrentFuel, 8450.0)
    assert math.isclose(sufa_aircraft.MaxFuel, 8450.0)
    assert len(sufa_aircraft.Mounts) > 0
    assert isinstance(sufa_aircraft.Mounts[0], Mount)
    assert isinstance(sufa_aircraft.Loadout, Loadout)

def test_features_from_steam_get_unit_fail():
    with pytest.raises(KeyError):
        features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
        unit_type = "Aircraft"
        _ = features.get_unit({}, 0, unit_type, side)

def test_features_from_steam_get_side_units():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    sufa_aircraft = features.units[2]
    assert isinstance(sufa_aircraft, Unit)
    assert sufa_aircraft.Name == sufa_aircraft_name
    assert sufa_aircraft.ID == sufa_aircraft_ID
    assert sufa_aircraft.Side == "Israel"
    assert sufa_aircraft.DBID == 4508
    assert sufa_aircraft.Type == "Aircraft"
    assert math.isclose(sufa_aircraft.CH, 0.0)
    assert math.isclose(sufa_aircraft.CS, 350.0)
    assert math.isclose(sufa_aircraft.CA, 55.0)
    assert math.isclose(sufa_aircraft.Lon, 35.183342038182)
    assert math.isclose(sufa_aircraft.Lat, 32.66746735647)
    assert math.isclose(sufa_aircraft.CurrentFuel, 8450.0)
    assert math.isclose(sufa_aircraft.MaxFuel, 8450.0)
    assert len(sufa_aircraft.Mounts) > 0
    assert isinstance(sufa_aircraft.Mounts[0], Mount)
    assert isinstance(sufa_aircraft.Loadout, Loadout)

def test_features_from_steam_get_side_contacts():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    contacts = features.contacts
    assert len(contacts) > 0
    contact = contacts[0]
    assert isinstance(contact, Contact)
    assert contact.ID == "0HXVM6-0HMUTDCKTG4AA"
    assert contact.Name == "MacDill Runway Access Point (Very Large Aircraft)"
    assert math.isclose(contact.CS, 0.0)
    assert math.isclose(contact.CA, 6.0)
    assert math.isclose(contact.Lon, -82.516819017376)
    assert math.isclose(contact.Lat, 27.852581555226)

def test_features_from_steam_get_contact():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    contacts = features.scen_dic["Scenario"]["Sides"]["Side"][side_index]["Contacts"]["Contact"]
    contact_xml = contacts[0]
    contact = features.get_contact(contact=contact_xml, contact_idx=0)
    assert isinstance(contact, Contact)
    assert contact.ID == "0HXVM6-0HMUTDCKTG4AA"
    assert contact.Name == "MacDill Runway Access Point (Very Large Aircraft)"
    assert math.isclose(contact.CS, 0.0)
    assert math.isclose(contact.CA, 6.0)
    assert math.isclose(contact.Lon, -82.516819017376)
    assert math.isclose(contact.Lat, 27.852581555226)
