import pytest
import os

from pycmo.configs.config import get_config
from pycmo.env.cmo_env import CMOEnv
from pycmo.lib.features import FeaturesFromSteam

config = get_config()

# INPUT
scenario_name = "Steam demo"
player_side = "Israel"
step_size = ['0', '0', '1']
command_version = config["command_mo_version"]
observation_path = os.path.join(config['pycmo_path'], 'tests', "fixtures", "test_steam_observation.inst")
action_path = os.path.join(config['pycmo_path'], 'tests', "fixtures", "test_cmo_env.lua")
scen_ended_path = os.path.join(config['pycmo_path'], 'tests', "fixtures", "Steam demo_scen_has_ended.inst")
pycmo_lua_lib_path = os.path.join(config['pycmo_path'], 'lua', 'pycmo_lib.lua')

def init_cmo_env():
    return CMOEnv(
        scenario_name=scenario_name,
        player_side=player_side,
        step_size=step_size,
        command_version=command_version,
        observation_path=observation_path,
        action_path=action_path,
        scen_ended_path=scen_ended_path,
        pycmo_lua_lib_path=pycmo_lua_lib_path,
    )

def test_cmo_env_init():
    cmo_env = init_cmo_env()
    assert isinstance(cmo_env, CMOEnv)

def test_cmo_env_get_obs():
    cmo_env = init_cmo_env()
    observation = cmo_env.get_obs()
    scen_dic = observation.scen_dic
    units = observation.units
    aircrafts = scen_dic['Scenario']['ActiveUnits']['Aircraft']
    scenario_title = scen_dic['Scenario']['Title']
    sides = scen_dic['Scenario']['Sides']['Side']
    
    assert isinstance(observation, FeaturesFromSteam)
    assert len(aircrafts) == 8
    assert scenario_title == 'Steam demo'
    assert len(sides) == 2
    assert len(units) == 9

def test_cmo_env_check_game_ended():
    cmo_env = init_cmo_env()
    assert cmo_env.check_game_ended() == True
