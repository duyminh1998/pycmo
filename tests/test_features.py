import pytest
import os

from pycmo.configs.config import get_config
from pycmo.lib.features import FeaturesFromSteam, Game, Side, Weapon, Loadout, Mount, Unit, Contact
from pycmo.lib.tools import cmo_steam_observation_file_to_xml

config = get_config()

side = "Israel"
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
    assert meta.Time == "1519552951"
    assert meta.ZeroHour == "1519552800"
    assert meta.StartTime == "1519552800"
    assert meta.Duration == "21600"

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
    unit_xml = features.scen_dic["Scenario"]["ActiveUnits"]['Aircraft'][1]["Loadout"]["Loadout"]
    weapons = features.get_weapon('Loadout', unit_xml)
    assert len(weapons) == 3
    
    weapon = weapons[0]

    assert isinstance(weapon, Weapon)
    assert weapon.ID == 'E9MD86-0HMTL4284RD9I'
    assert weapon.WeaponID == '516'
    assert weapon.QuantRemaining == 4
    assert weapon.MaxQuant == 4

def test_features_from_steam_get_mount_weapon():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    unit_xml = features.scen_dic["Scenario"]["ActiveUnits"]['Aircraft'][1]["Mounts"]["Mount"][1]
    weapons = features.get_weapon('Mount', unit_xml)
    assert len(weapons) == 2
    
    weapon = weapons[0]

    assert isinstance(weapon, Weapon)
    assert weapon.ID == 'E9MD86-0HMTL4284RD8T'
    assert weapon.WeaponID == '564'
    assert weapon.QuantRemaining == 12
    assert weapon.MaxQuant == 12

def test_features_from_steam_get_loadout():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    unit_xml = features.scen_dic["Scenario"]["ActiveUnits"]['Aircraft'][1]
    loadout = features.get_loadout(unit_xml)
    
    assert isinstance(loadout, Loadout)
    assert loadout.ID == '18127'
    assert loadout.Name == 'A/A: Python 5, Light 004'
    assert loadout.Weapons == features.get_weapon('Loadout', unit_xml["Loadout"]["Loadout"])

def test_features_from_steam_get_loadout():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    unit_xml = features.scen_dic["Scenario"]["ActiveUnits"]['Aircraft'][1]
    mounts = features.get_mount(unit_xml)

    assert len(mounts) == 2

    mount = mounts[0]
    
    assert isinstance(mount, Mount)
    assert mount.ID == 'E9MD86-0HMTL4284RD8O'
    assert mount.Name == '20mm/85 M61A1 Vulcan [515 rnds]'
    assert mount.Weapons == features.get_weapon('Mount', unit_xml["Mounts"]["Mount"][0])

def test_features_from_steam_get_unit_fuel():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    sufa_aircraft = features.units[2]
    assert sufa_aircraft.Name == "Sufa #3"
    assert sufa_aircraft.CurrentFuel == 8450
    assert sufa_aircraft.MaxFuel == 8450

def test_features_from_steam_get_unit():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    sufa_aircraft = features.units[2]
    assert isinstance(sufa_aircraft, Unit)
    assert sufa_aircraft.Name == "Sufa #3"
    assert sufa_aircraft.Side == "Israel"
    assert sufa_aircraft.DBID == '4508'
    assert sufa_aircraft.Type == "Aircraft"
    assert sufa_aircraft.CH == '0.0'
    assert sufa_aircraft.CS == 350.0
    assert sufa_aircraft.CA == 55.0
    assert sufa_aircraft.Lon == 35.183342038182
    assert sufa_aircraft.Lat == 32.66746735647
    assert sufa_aircraft.CurrentFuel == 8450
    assert sufa_aircraft.MaxFuel == 8450
    assert len(sufa_aircraft.Mounts) > 0
    assert len(sufa_aircraft.Loadout) > 0

def test_features_from_steam_get_contacts():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    contacts = features.contacts
    assert len(contacts) > 0
    contact = contacts[0]
    assert isinstance(contact, Contact)
    assert contact.ID == "0HXVM6-0HMUTDCKTG4AA"
    assert contact.Name == "MacDill Runway Access Point (Very Large Aircraft)"
    assert contact.CS == 0.0
    assert contact.CA == 6.0
    assert contact.Lon == -82.516819017376
    assert contact.Lat == 27.852581555226