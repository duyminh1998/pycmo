# Author: Minh Hua
# Date: 10/21/2023
# Purpose: A sample agent to interact with the steam_demo scenario, demonstrating our ability to work with the Steam version of CMO.

import os

from sample_agent import ScriptedAgent

from pycmo.configs.config import get_config
from pycmo.env.cmo_env import CMOEnv, StepType
from pycmo.lib.tools import print_env_information, parse_datetime

# open config and set important files and folder paths
config = get_config()

# MAIN LOOP
scenario_name = "floridistan"
player_side = "BLUE"
step_size = ['0', '0', '1']
scenario_script_folder_name = "floridistan" # name of folder containing the lua script that the agent will use

command_version = config["command_mo_version"]
observation_path = os.path.join(config['steam_observation_folder_path'], f'{scenario_name}.inst')
action_path = os.path.join(config["scripts_path"], scenario_script_folder_name, "agent_action.lua")
scen_ended_path = os.path.join(config['steam_observation_folder_path'], f'{scenario_name}_scen_has_ended.inst')
pycmo_lua_lib_path = os.path.join(config['pycmo_path'], 'lua', 'pycmo_lib.lua')

env = CMOEnv(
        scenario_name=scenario_name,
        player_side=player_side,
        step_size=step_size,
        command_version=command_version,
        observation_path=observation_path,
        action_path=action_path,
        scen_ended_path=scen_ended_path,
        pycmo_lua_lib_path=pycmo_lua_lib_path
)

attacker_name = "Thunder #1"
target_name = "BTR-82V"
strike_weapon_name = "GBU-53/B StormBreaker"

agent = ScriptedAgent(player_side=player_side, attacker_name=attacker_name, target_name=target_name, strike_weapon_name=strike_weapon_name)

# start the game
state = env.reset()
action = ''

stop_at_step = 25
iterations = 5

# main loop
for _ in range(stop_at_step * iterations):
    print_env_information(state.step_id, parse_datetime(int(state.observation.meta.Time)), action, state.reward, state.reward)

    if state.step_id > 0 and (state.step_id % stop_at_step) == 0:
        state = env.end_game()
        print("Ending game...")
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
        env.client.close_scenario_end_message()
        state = env.reset()
        action = ''
        agent.reset()
