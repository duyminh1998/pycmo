import pytest
import os

from pycmo.configs.config import get_config
from pycmo.lib.features import FeaturesFromSteam, Game
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
    assert meta.ScenarioName == "Steam demo"
    assert meta.TimelineID is None

def test_features_from_steam_get_sides():
    features = FeaturesFromSteam(xml=scenario_xml, player_side=side)
    sides = features.get_sides()
    assert len(sides) == 2
    assert sides[0] == "Israel"
    assert sides[1] == "Syria"