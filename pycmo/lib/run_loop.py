# Author: Minh Hua
# Date: 08/16/2021
# Purpose: A run loop for agent/environment interaction.

from pycmo.lib.protocol import Server
from pycmo.env.cmo_env import CMOEnv
from pycmo.agents.rule_based_agent import RuleBasedAgent
import threading, time
from pycmo.lib.tools import *
import os
from pycmo.configs import config

def clean_up_steps(path: str):
    """Delete all the steps file (.xml) in the steps folder"""
    try:
        for step in os.listdir(path):
            if step.endswith('.xml'):
                os.remove(os.path.join(path, step))
    except:
        print("ERROR: failed to clean up steps folder.")

def print_env_information(step_id, current_time, final_move, current_score, current_reward):
    """Prints information about the current time step"""
    print("Step: {}".format(step_id))
    print("Current Time: {}".format(current_time))
    print("Action: {}".format(final_move))
    print("Current scenario score: {} \nCurrent reward: {}\n".format(current_score, current_reward))

def run_loop(player_side: str, step_size: list, config, agent=None, max_steps=None, server=False, scen_file=None):
    # config and set up, clean up steps folder
    steps_path = config["observation_path"]
    clean_up_steps(steps_path)
    
    # set up a Command TCP/IP socket if the game is not already running somewhere
    if server:
        server = Server(scen_file)
        x = threading.Thread(target=server.start_game)
        x.start()
        time.sleep(10)
    
    # build CMO environment
    env = CMOEnv(steps_path, step_size, player_side, config["scen_ended"])
    
    # initial variables and state
    step_id = 0
    current_score = 0
    current_reward = 0
    initial_state = env.reset()
    cur_time = ticks_to_unix(initial_state.observation.meta.Time)
    print(parse_datetime(int(initial_state.observation.meta.Time)))

    # Configure a limit for the maximum number of steps
    if max_steps == None:
        max_steps = 1000

    # main loop
    while not (env.check_game_ended() or (step_id > max_steps)):
        # get old state
        state_old = env.get_timestep(step_id)
        cur_time = ticks_to_unix(state_old.observation.meta.Time)

        # perform random actions or choose the action
        available_actions = env.action_spec(state_old.observation)
        if agent != None:
            final_move = agent.get_action(state_old.observation, available_actions.VALID_FUNCTIONS)
        else:
            final_move = '--script \nTool_EmulateNoConsole(true)' # No action if no agent is loaded

        # get new state and observation, rewards, discount
        step_id += 1
        new_state = env.step(cur_time, step_id, action=final_move)
        current_score = new_state.observation.side_.TotalScore
        current_reward = new_state.reward
        print_env_information(step_id, parse_datetime(int(state_old.observation.meta.Time)), final_move, current_score, current_reward)

        # store new data into a long-term memory

        if step_id % 10 == 0:
            clean_up_steps(steps_path)
    #clean_up_steps(steps_path)

# for debugging
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
    run_loop(player_side, step_size, config=config, agent=player_agent)