import pytest
import os

from pycmo.configs.config import get_config
from pycmo.lib.features import FeaturesFromSteam, Game, Side, Weapon, Loadout
from pycmo.lib.tools import cmo_steam_observation_file_to_xml

config = get_config()

side = "Israel"
observation_file_path = os.path.join(config['pycmo_path'], 'tests', "fixtures", 'test_steam_observation.inst')
scenario_xml = cmo_steam_observation_file_to_xml(observation_file_path)

def test_features_from_steam_init():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    assert isinstance(features, FeaturesFromSteam)
    scen_dic = features.scen_dic
    assert len(scen_dic['Scenario']['ActiveUnits']['Aircraft']) == 8
    assert scen_dic['Scenario']['Title'] == 'Steam demo'
    assert len(scen_dic['Scenario']['Sides']['Side']) == 2

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

def test_features_from_steam_get_weapon_loadout():
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

def test_features_from_steam_get_loadout():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    unit_xml = features.scen_dic["Scenario"]["ActiveUnits"]['Aircraft'][1]
    loadout = features.get_loadout(unit_xml)
    
    assert isinstance(loadout, Loadout)
    assert loadout.ID == '18127'
    assert loadout.Name == 'A/A: Python 5, Light 004'
    assert loadout.Weapons == features.get_weapon('Loadout', unit_xml["Loadout"]["Loadout"])