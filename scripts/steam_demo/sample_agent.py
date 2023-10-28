# Author: Minh Hua
# Date: 10/21/2023
# Purpose: A sample agent to interact with the steam_demo scenario, demonstrating our ability to work with the Steam version of CMO.

import os
import json
import subprocess
import random

from pycmo.configs.config import get_config
from pycmo.lib.protocol import SteamClient

# open config and set important files and folder paths
config = get_config()

# CONSTANTS
latitude_min = -90
latitude_max = 90
longitude_min = -180
longitude_max = 180

# INIT
def read_cmo_steam_observation_file(file_path:str=os.path.join(config['steam_observation_folder_path'], 'Israel_units.inst')) -> any or None:
    try:
        with open(file_path, 'r') as f:
            observation_file_contents = f.read()
    except FileNotFoundError:
        return None
    try:
        observation_file_json = json.loads(observation_file_contents)
    except json.decoder.JSONDecodeError:
        return None
    unit = observation_file_json["MemberRecords"][0]
    return unit

def filter_observation(observation):
    return {
        'guid': observation['Member_GUID'],
        'type': observation['MemberType'],
        'name': observation['MemberName'],
        'longitude': observation['Longitude'],
        'latitude': observation['Latitude'],
        'altitude': observation['Altitude'],
        'speed': observation['Speed'],
    }

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
side = "Israel"
sufa = "Sufa #1"

scenario_name = "Steam demo"
command_version = "Command v1.06 - Build 1328.10a"

observation_file_path = os.path.join(config['steam_observation_folder_path'], 'Israel_units.inst')
scripts_folder_path = config["scripts_path"]
agent_action_filename = os.path.join(scripts_folder_path, "steam_demo", "python_agent_action.lua")


client = SteamClient(scenario_name, agent_action_filename, command_version)

# start the game
scenario_started = client.start_scenario()

if scenario_started:
    scenario_ended = False
    current_raw_observation = read_cmo_steam_observation_file(observation_file_path)

    # reset agent action to nothing
    client.send("")

    while not scenario_ended:
        next_raw_observation = read_cmo_steam_observation_file(observation_file_path)

        if next_raw_observation and next_raw_observation != current_raw_observation:
            observation = filter_observation(next_raw_observation)
            print(f"New observation:\n{observation}")
            action = move_aircraft(side, sufa, observation['longitude'], observation['latitude'])
            print(f"Action:\n{action}")

            action_written = client.send(action)
            if action_written:
                scenario_started = client.start_scenario()
                
        current_raw_observation = next_raw_observation