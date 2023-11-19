# Author: Minh Hua
# Date: 10/21/2023
# Purpose: A sample agent to interact with the steam_demo scenario, demonstrating our ability to work with the Steam version of CMO.

import random

from pycmo.lib import actions
from pycmo.agents.base_agent import BaseAgent
from pycmo.lib.features import FeaturesFromSteam, Unit

class RandomAgent(BaseAgent):
    def __init__(self, player_side:str, ac_name:str):
        super().__init__(player_side)
        self.ac_name = ac_name

    def get_unit_info_from_observation(self, features: FeaturesFromSteam, unit_name:str) -> Unit:
        units = features.units
        for unit in units:
            if unit.Name == unit_name:
                return unit
        return None

    def action(self, features: FeaturesFromSteam, VALID_FUNCTIONS:actions.AvailableFunctions) -> str:
        action = ""
        ac = self.get_unit_info_from_observation(features=features, unit_name=self.ac_name)

        base_script = f"local side = '{self.player_side}'\nlocal sufa = ScenEdit_GetUnit({{side = side, name = '{self.ac_name}'}})\n"
        delta_longitude = (random.random() * 1) - 0.5
        delta_latitude = (random.random() * 1) - 0.5
        new_longitude = float(ac.Lon) + delta_longitude
        new_latitude = float(ac.Lat) + delta_latitude
        action = base_script + f'move_unit_to(side, sufa.name, {new_latitude}, {new_longitude})'

        return action
