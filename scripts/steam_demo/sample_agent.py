# Author: Minh Hua
# Date: 10/21/2023
# Purpose: A sample agent to interact with the steam_demo scenario, demonstrating our ability to work with the Steam version of CMO.

import os
import random

from pycmo.configs.config import get_config
from pycmo.lib.tools import cmo_steam_observation_file_to_xml
from pycmo.lib.protocol import SteamClient
from pycmo.lib.features import FeaturesFromSteam, Unit
from pycmo.env.cmo_env import CMOEnv

# open config and set important files and folder paths
config = get_config()

# FUNCTIONS
def get_unit_from_observation(units, unit_name) -> Unit:
    for unit in units:
        if unit.Name == unit_name:
            return unit

def move_aircraft(side:str, unit_name:str, initial_longitude:float, initial_latitude:float):
    base_script = f"local side = '{side}'\nlocal sufa = ScenEdit_GetUnit({{side = side, name = '{unit_name}'}})\n"
    delta_longitude = (random.random() * 1) - 0.5
    delta_latitude = (random.random() * 1) - 0.5
    new_longitude = float(initial_longitude) + delta_longitude
    new_latitude = float(initial_latitude) + delta_latitude
    action = base_script + f'move_unit_to(side, sufa.name, {new_latitude}, {new_longitude})'
    return action

def no_op():
    action = ''
    return action

# MAIN LOOP
# SIDE INFO
sufa = "Sufa #1"

scenario_name = "Steam demo"
scenario_script_folder_name = "steam_demo"
player_side = "Israel"
step_size = ['0', '0', '1']
command_version = config["command_mo_version"]
observation_path = os.path.join(config['steam_observation_folder_path'], f'{scenario_name}.inst')
action_path = os.path.join(config["scripts_path"], scenario_script_folder_name, "agent_action.lua")
scen_ended_path = os.path.join(config['steam_observation_folder_path'], f'{scenario_name}_scen_has_ended.inst')
pycmo_lua_lib_path = os.path.join(config['pycmo_path'], 'lua', 'pycmo_lib.lua')

cmo_env = CMOEnv(
        scenario_name=scenario_name,
        player_side=player_side,
        step_size=step_size,
        command_version=command_version,
        observation_path=observation_path,
        action_path=action_path,
        scen_ended_path=scen_ended_path,
        pycmo_lua_lib_path=pycmo_lua_lib_path,
)

# start the game
# scenario_started = cmo_env.client.start_scenario()
scenario_started = True

if scenario_started:
    old_state = cmo_env.reset()
    scenario_ended = cmo_env.check_game_ended()

    while not scenario_ended:
        observation = old_state.observation
        
        sufa_info = get_unit_from_observation(observation.units, sufa)
        action = move_aircraft(player_side, sufa, sufa_info.Lon, sufa_info.Lat)
        print(f"Action:\n{action}\n")
    
        new_state = cmo_env.step(action)
        print(f"New observation:\n{new_state}\n")

        # set old state as the previous new state
        old_state = new_state

        scenario_ended = cmo_env.check_game_ended()
