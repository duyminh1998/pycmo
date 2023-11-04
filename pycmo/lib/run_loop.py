# Author: Minh Hua
# Date: 08/16/2021
# Last Update: 06/16/2022
# Purpose: A run loop for agent/environment interaction.

# imports
from pycmo.lib.protocol import Server # Server to handle connection
from pycmo.env.cmo_env import CPEEnv # CPE environment, functions as the client that sends actions and receives observations
# agents
from pycmo.agents.rule_based_agent import RuleBasedAgent
from pycmo.agents.scripted_agent import ScriptedAgent
# auxiliary functions
import threading, time
from pycmo.lib.tools import *
from pycmo.configs import config

def run_loop(player_side:str, config:dict, step_size:list=['0', '0', '1'], agent=None, max_steps=None, server=False, scen_file=None) -> None:
    """
    Description:
        Generic function to run an observe-act loop.

    Keyword Arguments:
        player_side: the name of the player's side.
        config: a dictionary of configuration paths to important folders and files.
        step_size: a list containing the step size in the format ["h", "m", "s"]. Default is step size of 1 seconds.
        agent: an agent to control the game.
        max_steps: the maximum number of allowable steps.
        server: whether or not to initialize a server.
        scen_file: whether or not to use a custom scenario file.

    Returns:
        None
    """        
    # config and set up, clean up steps folder
    steps_path = config["observation_path"]
    clean_up_steps(steps_path)
    
    # set up a Command TCP/IP socket if the game is not already running somewhere
    if server:
        server = Server(scen_file)
        x = threading.Thread(target=server.start_game)
        x.start()
        time.sleep(10)
    
    # build CPE environment
    env = CPEEnv(steps_path, step_size, player_side, config["scen_ended"])
    
    # initial variables and state
    step_id = 0
    initial_state = env.reset()
    state_old = initial_state
    cur_time = ticks_to_unix(initial_state.observation.meta.Time)
    print(parse_datetime(int(initial_state.observation.meta.Time)))

    # Configure a limit for the maximum number of steps
    if max_steps == None:
        max_steps = 1000

    # main loop
    while not (env.check_game_ended() or (step_id > max_steps)):
        # get current time
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

        # set old state as the previous new state
        old_state = new_state

        if step_id % 10 == 0:
            clean_up_steps(steps_path)

# for debugging
if __name__ == "__main__":
    # open config
    config = config.get_config()

    # scenario file and player side
    # scen_file = "C:\\ProgramData\\Command Professional Edition 2\\Scenarios\\Standalone Scenarios\\Wooden Leg, 1985.scen"
    # scen_file = "C:\\ProgramData\\Command Professional Edition 2\\Scenarios\\Custom RCS Detection\\Lua Hook Sensor Detection Test.scen"
    scen_file = ""
    player_side = "US"
    step_size = ["00", "00", "01"]

    # initalize agent
    # player_agent = ScriptedAgent('wooden_leg', player_side)
    # player_agent = RandomAgent('wooden_leg', player_side)
    player_agent = None
    run_loop(player_side, config=config, step_size=step_size, agent=player_agent)