import os
import gymnasium

from sample_agent import ScriptedAgent

from pycmo.configs.config import get_config
from pycmo.lib.protocol import SteamClientProps

# open config and set important files and folder paths
config = get_config()

scenario_name = "floridistan"
player_side = "BLUE"
scenario_script_folder_name = "floridistan" # name of folder containing the lua script that the agent will use

command_version = config["command_mo_version"]
observation_path = os.path.join(config['steam_observation_folder_path'], f'{scenario_name}.inst')
action_path = os.path.join(config["scripts_path"], scenario_script_folder_name, "agent_action.lua")
scen_ended_path = os.path.join(config['steam_observation_folder_path'], f'{scenario_name}_scen_has_ended.inst')
steam_client_props = SteamClientProps(scenario_name=scenario_name, agent_action_filename=action_path, command_version=command_version)

env = gymnasium.make('CMOGymEnv-v0',
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

observation, info = env.reset(close_scenario_end_and_player_eval_messages=False, seed=42)
for _ in range(282):
    action = agent.action(observation, env.unwrapped.valid_cmo_actions)
    observation, reward, terminated, truncated, info = env.step(action=action)

    if terminated or truncated:
        observation, info = env.reset(close_scenario_end_and_player_eval_messages=True)
        action = ''
        agent.reset()

env.close()
