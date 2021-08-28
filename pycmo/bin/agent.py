# Author: Minh Hua
# Date: 08/22/2021
# Purpose: Run an agent.

from pycmo.lib.run_loop import *
from pycmo.agents.random_agent import RandomAgent
from pycmo.agents.rule_based_agent import RuleBasedAgent
from pycmo.agents.scripted_agent import ScriptedAgent
from pycmo.configs import config
import argparse

def main(player_side: str, step_size: list, config, agent=None, max_steps=None, server=False, scen_file=None):
    """Run an agent."""
    run_loop(player_side, step_size, config=config, agent=agent)

if __name__ == "__main__":
    # open config
    config = config.get_config()

    # add args parser
    parser = argparse.ArgumentParser(description='Arguments for choosing agent and timestep size.')
    parser.add_argument('-agent', help='Select an agent. 0 for RandomAgent, 1 for ScriptedAgent, 2 for RuleBasedAgent.')
    parser.add_argument('-size', help='Size of a timestep, must be in "hh:mm:ss" format.')
    parser.add_argument('-scenario', help='The name of the scenario, used for ScriptedAgent and RuleBasedAgent. Usually the literal name of the .scen file.')
    parser.add_argument('-player', help="The name of player's side.")
    args = parser.parse_args()

    # scenario file and player side
    if args.scenario == None:
        scen_short_name = 'Wooden Leg, 1985'
    else:
        scen_short_name = args.scenario
    if args.player == None:
        player_side = "Israel"
    else:
        player_side = args.player
    # get step size
    if args.size == None:
        step_size = ["00", "01", "00"]
    else:
        step_size = args.size.split(":")
    # initalize agent, RandomAgent by default
    if args.agent == None:
        player_agent = RandomAgent(scen_short_name, player_side)
    else:
        agents = [RandomAgent, ScriptedAgent, RuleBasedAgent]
        player_agent = agents[int(args.agent)](scen_short_name, player_side)
    # run main loop
    main(player_side, step_size, config=config, agent=player_agent)