from pycmo.lib import actions
from pycmo.lib.features import Features, FeaturesFromSteam

class BaseAgent:
    def __init__(self, player_side):
        self.player_side = player_side

    def action(self, observation: Features | FeaturesFromSteam, VALID_FUNCTIONS:actions.AvailableFunctions) -> str:
        ...

    def reset(self) -> None:
        ...