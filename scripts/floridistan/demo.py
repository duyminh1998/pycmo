import os

from sample_agent import ScriptedAgent

from pycmo.configs.config import get_config
from pycmo.env.cmo_env import CMOEnv
from pycmo.lib.run_loop import run_loop_steam

config = get_config()

# MAIN LOOP
scenario_name = "floridistan"
scenario_script_folder_name = "floridistan"
player_side = "BLUE"
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
        pycmo_lua_lib_path=pycmo_lua_lib_path
)

attacker_name = "Thunder #1"
target_name = "BTR-82V"
strike_weapon_name = "GBU-53/B StormBreaker"

agent = ScriptedAgent(player_side=player_side, attacker_name=attacker_name, target_name=target_name, strike_weapon_name=strike_weapon_name)

run_loop_steam(env=cmo_env, agent=agent, max_steps=None)
