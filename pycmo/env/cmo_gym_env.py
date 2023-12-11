from typing import Tuple
import gymnasium as gym
from gymnasium import spaces
import numpy as np

from pycmo.lib.features import FeaturesFromSteam
from pycmo.env.cmo_env import CMOEnv, StepType
from pycmo.lib.protocol import SteamClientProps

class BasePycmoGymEnv(gym.Env):
    metadata = {"render_modes": [None]}

    def __init__(
            self,
            player_side: str,
            steam_client_props:SteamClientProps,
            observation_path: str, 
            action_path: str,
            scen_ended_path: str,
            pycmo_lua_lib_path: str | None = None,
            max_resets: int = 20,
            render_mode=None,
    ):
        self.cmo_env = CMOEnv(
            player_side=player_side,
            steam_client_props=steam_client_props,
            observation_path=observation_path,
            action_path=action_path,
            scen_ended_path=scen_ended_path,
            pycmo_lua_lib_path=pycmo_lua_lib_path,
            max_resets=max_resets
        )

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode
        
    def _get_obs(self, observation:FeaturesFromSteam) -> dict:
        ...
    
    def _get_info(self) -> dict:
        ...
    
    def reset(self, seed:int=None, options:dict=None) -> Tuple[dict, dict]:
        state = self.cmo_env.reset(close_scenario_end_and_player_eval_messages=options['close_scenario_end_and_player_eval_messages'])
        observation = self._get_obs(observation=state.observation)
        info = self._get_info()
        
        return observation, info

    def step(self, action) -> Tuple[dict, int, bool, bool, dict]:
        state = self.cmo_env.step(action)
        terminated = self.cmo_env.check_game_ended() or state.step_type == StepType(2)
        truncated = False
        reward = state.reward
        observation = self._get_obs(observation=state.observation)
        info = self._get_info()

        return observation, reward, terminated, truncated, info

    def close(self) -> None:
        self.cmo_env.end_game()

class FloridistanPycmoGymEnv(BasePycmoGymEnv):
    def __init__(
            self,
            observation_space:spaces.Space,
            action_space:spaces.Space,
            player_side: str,
            steam_client_props:SteamClientProps,
            observation_path: str, 
            action_path: str,
            scen_ended_path: str,
            pycmo_lua_lib_path: str | None = None,
            max_resets: int = 20,
            render_mode=None,
    ):
        super().__init__(
            player_side=player_side,
            steam_client_props=steam_client_props,
            observation_path=observation_path,
            action_path=action_path,
            scen_ended_path=scen_ended_path,
            pycmo_lua_lib_path=pycmo_lua_lib_path,
            max_resets=max_resets,
            render_mode=render_mode
        )

        self.observation_space = observation_space
        self.action_space = action_space

    def _get_obs(self, observation:FeaturesFromSteam) -> dict:
        _observation = {}

        unit_name = "Thunder #1"
        for unit in observation.units:
            if unit.Name == unit_name:
                break
        _observation[unit_name] = {}

        for key in self.observation_space[unit_name].keys():
            obs_value = getattr(unit, key)
            if isinstance(obs_value, float):
                _observation[unit_name][key] = np.array((obs_value,), dtype=np.float64)
            else:
                _observation[unit_name][key] = obs_value        

        contact_name = "BTR-82V"
        for contact in observation.contacts:
            if contact.Name == contact:
                break
        _observation[contact_name] = {}

        for key in self.observation_space[contact_name].keys():
            obs_value = getattr(contact, key)
            if isinstance(obs_value, float):
                _observation[contact_name][key] = np.array((obs_value,), dtype=np.float64)
            else:
                _observation[contact_name][key] = obs_value
        
        return _observation        
    
    def _get_info(self) -> dict:
        return {}
