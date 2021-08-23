# Author: Minh Hua
# Date: 08/22/2021
# Purpose: Run an agent.

from pycmo.lib.run_loop import *
from pycmo.agents.random_agent import RandomAgent
from pycmo.agents.rule_based_agent import RuleBasedAgent
from pycmo.configs import config

def main(player_side: str, step_size: list, config, agent=None, max_steps=None, server=False, scen_file=None):
    """Run an agent."""
    run_loop(player_side, step_size, config=config, agent=agent)

if __name__ == "__main__":
    # open config
    config = config.get_config()

    # scenario file and player side
    scen_file = "C:\\ProgramData\\Command Professional Edition 2\\Scenarios\\Standalone Scenarios\\Wooden Leg, 1985.scen"
    player_side = "Israel"
    step_size = ["00", "05", "00"]

    # initalize agent
    player_agent = RuleBasedAgent('wooden_leg', player_side)
    # player_agent = RandomAgent('wooden_leg', player_side)
    main(player_side, step_size, config=config, agent=player_agent)