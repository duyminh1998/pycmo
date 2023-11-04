# Author: Minh Hua
# Date: 10/21/2023
# Purpose: A sample agent to interact with the steam_demo scenario, demonstrating our ability to work with the Steam version of CMO.

import os

from pycmo.configs.config import get_config
from pycmo.lib.features import Unit
from pycmo.env.cmo_env import CMOEnv

# open config and set important files and folder paths
config = get_config()

# FUNCTIONS
def get_unit_from_observation(units, unit_name) -> Unit:
    for unit in units:
        if unit.Name == unit_name:
            return unit

def no_op():
    action = ''
    return action

# MAIN LOOP
# SIDE INFO
main_unit = "Lightning #1"

scenario_name = "floridistan"
scenario_script_folder_name = "floridistan"
player_side = "BLUE"
step_size = ['0', '0', '1']
command_version = config["command_mo_version"]
observation_path = os.path.join(config['steam_observation_folder_path'], f'{scenario_name}.inst')
action_path = os.path.join(config["scripts_path"], scenario_script_folder_name, "agent_action.lua")
scen_ended_path = config['scen_ended']

cmo_env = CMOEnv(
        scenario_name=scenario_name,
        player_side=player_side,
        step_size=step_size,
        observation_path=observation_path,
        action_path=action_path,
        scen_ended_path=scen_ended_path,
        command_version=command_version
)

# start the game
# scenario_started = cmo_env.client.start_scenario()
scenario_started = True

if scenario_started:
    scenario_ended = False
    old_state = cmo_env.reset()

    while not scenario_ended:
        observation = old_state.observation
        
        sufa_info = get_unit_from_observation(observation.units, main_unit)
        action = no_op()
        print(f"Action:\n{action}\n")
    
        new_state = cmo_env.step(action)
        print(f"New observation:\n{new_state}\n")

        # set old state as the previous new state
        old_state = new_state
