# Author: Minh Hua
# Date: 10/21/2023
# Purpose: A sample agent to interact with the steam_demo scenario, demonstrating our ability to work with the Steam version of CMO.

import os
import json
import random

from pycmo.configs import config

# open config and set important files and folder paths
config = config.get_config()

# SIDE INFO
side = "Israel"
sufa = "Sufa #1"
observation_file_path = os.path.join(config['command_path'], 'ImportExport', 'Israel_units.inst')

# CONSTANTS
latitude_min = -90
latitude_max = 90
longitude_min = -180
longitude_max = 180

# INIT
def read_cmo_steam_observation_file(file_path:str=os.path.join(config['command_path'], 'ImportExport', 'Israel_units.inst')) -> any or None:
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

def parse_observation(observation):
    return {
        'guid': observation['Member_GUID'],
        'type': observation['MemberType'],
        'name': observation['MemberName'],
        'longitude': observation['Longitude'],
        'latitude': observation['Latitude'],
        'altitude': observation['Altitude'],
        'speed': observation['Speed'],
    }

# def take_action(observation:tuple):
#     unit_longitude = observation['longitude']
#     unit_latitude = observation['latitude']
#     delta_longitude = (random.random() * 2) - 1
#     delta_latitude = (random.random() * 2) - 1
#     return 

def move_randomly(side, unit_name, initial_longitude, initial_latitude):
    """
    local side = "Israel"\n
    local sufa = ScenEdit_GetUnit({side = side, name = "Sufa #1"})
    local latitude = math.random() + math.random(-90, 91)
    local longitude = math.random() + math.random(-180, 181)
    move_unit_to(side, sufa.name, latitude, longitude)
    """
    base_script = f"local side = '{side}'\nlocal sufa = ScenEdit_GetUnit({{side = side, name = '{unit_name}'}})\n"
    # delta_longitude = (random.random() * 2) - 1
    # delta_latitude = (random.random() * 2) - 1
    delta_longitude = 0.5
    delta_latitude = 0.5
    new_longitude = initial_longitude + delta_longitude
    new_latitude = initial_latitude + delta_latitude
    action = base_script + f'move_unit_to(side, sufa.name, {new_latitude}, {new_longitude})'
    return action

def no_op():
    action = ''
    return action

# MAIN LOOP
scenario_ended = False
raw_observation = read_cmo_steam_observation_file(observation_file_path)
agent_action_filename = os.path.join(".", "scripts", "steam_demo", "python_agent_action.lua")

while not scenario_ended:
    next_raw_observation = read_cmo_steam_observation_file(observation_file_path)
    if raw_observation and next_raw_observation != raw_observation:
        observation = parse_observation(raw_observation)
        action = move_randomly(side, sufa, observation['longitude'], observation['latitude'])
        print(action)

        try:
            with open(agent_action_filename, 'w') as f:
                f.write(action)
        except PermissionError:
            pass


    raw_observation = next_raw_observation