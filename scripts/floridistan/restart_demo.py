# Author: Minh Hua
# Date: 11/19/2023
# Purpose: A sample agent to interact with the floridistan scenario, but the scenario restarts every 25 steps.

import os
import logging
logging.basicConfig(level=logging.INFO)

from sample_agent import ScriptedAgent

from pycmo.configs.config import get_config
from pycmo.env.cmo_env import CMOEnv, StepType
from pycmo.lib.protocol import SteamClientProps
from pycmo.lib.tools import print_env_information, parse_utc

# open config and set important files and folder paths
config = get_config()

# MAIN LOOP
scenario_name = "floridistan"
player_side = "BLUE"
scenario_script_folder_name = "floridistan" # name of folder containing the lua script that the agent will use

command_version = config["command_mo_version"]
observation_path = os.path.join(config['steam_observation_folder_path'], f'{scenario_name}.inst')
action_path = os.path.join(config["scripts_path"], scenario_script_folder_name, "agent_action.lua")
scen_ended_path = os.path.join(config['steam_observation_folder_path'], f'{scenario_name}_scen_has_ended.inst')
steam_client_props = SteamClientProps(scenario_name=scenario_name, agent_action_filename=action_path, command_version=command_version)

env = CMOEnv(
        player_side=player_side,
        steam_client_props=steam_client_props,
        observation_path=observation_path,
        action_path=action_path,
        scen_ended_path=scen_ended_path,
)

attacker_name = "Thunder #1"
target_name = "BTR-82V"
strike_weapon_name = "GBU-53/B StormBreaker"

agent = ScriptedAgent(player_side=player_side, attacker_name=attacker_name, target_name=target_name, strike_weapon_name=strike_weapon_name)

# start the game
state = env.reset(close_scenario_end_and_player_eval_messages=False)
action = ''

stop_at_step = 200
iteration = 0
max_iterations = 5

# main loop
while iteration < max_iterations:
    print_env_information(state.step_id, parse_utc(int(state.observation.meta.Time)), action, state.reward, state.reward)

    if state.step_id > 0 and (state.step_id % stop_at_step) == 0:
        state = env.end_game()
        iteration += 1
    else:
        if not env.check_game_ended():
            # perform random actions or choose the action
            available_actions = env.action_spec(state.observation)
            if agent:
                action = agent.action(state.observation, available_actions.VALID_FUNCTIONS)
            else:
                action = '' # No action if no agent is loaded

            # get new state and observation, rewards, discount
            state = env.step(action)

    if state.step_type == StepType(2) or env.check_game_ended():
        print_env_information(state.step_id, parse_utc(int(state.observation.meta.Time)), action, state.reward, state.reward)
        state = env.reset(close_scenario_end_and_player_eval_messages=True)
        action = ''
        agent.reset()
