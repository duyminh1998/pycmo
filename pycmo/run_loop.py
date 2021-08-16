"""A run loop for agent/environment interaction."""

from lib.features import Features
from lib.protocol import Client, Server
from agents.random_agent import RandomAgent
from cmo_env import CMOEnv
import threading, time
from lib.tools import *
import json
import os

def run_loop(scen_file, initial_xml, player_side, server=False, config=None, agent=None):
    # config and set up
    steps_path = config["steps_path"]
    for f in os.listdir(steps_path):
        os.remove(os.path.join(steps_path, f))
    
    # set up a Command TCP/IP socket if the game is not already running somewhere
    if server:
        server = Server(scen_file)
        x = threading.Thread(target=server.start_game)
        x.start()
        time.sleep(15)
    
    # build CMO environment
    env = CMOEnv(config["observation_path"], ["01", "00", "00"], player_side, config["scen_ended"])
    
    scen_end = False
    step_id = 0
    initial_state = env.reset()
    cur_time = ticks_to_unix(initial_state.observation.meta.Time)
    print(parse_datetime(int(initial_state.observation.meta.Time)))
    available_actions = env.action_spec(initial_state.observation)
    print(player_agent.get_action(available_actions.VALID_FUNCTIONS))

    # main loop
    while not (env.check_game_ended() or (step_id > 100)):
        # add randomness to agent's actions
        # agent.epsilon = 80 - counter_games

        # get old state
        step_id += 1
        state_old = env.step(cur_time, step_id)
        available_actions = env.action_spec(initial_state.observation)
        print(player_agent.get_action(available_actions.VALID_FUNCTIONS))
        # r_old = state_old.side_info.TotalScore
        # d_old = 0
        # ts_old = TimeStep(StepType(1), r_old, d_old, state_old)

        # perform random actions or choose the action
        # final_move = 
        # player1.do_move(final_move)

        # get new state and observation, rewards, discount
        # client.step_and_get_obs("01", "00", "00", xml_file)
        # env.TimeStep('step_type', 'reward', 'discount', 'observation')
        # new_state = Features(xml_file, player_side)

        # store new data into a long-term memory

        # reset loop
        #scen_end = True
        cur_time = ticks_to_unix(state_old.observation.meta.Time)
        print(parse_datetime(int(state_old.observation.meta.Time)))
    

if __name__ == '__main__':
    f = open("C:\\Users\\AFSOC A8XW ORSA\\Documents\\Python Proj\\AI\\pycmo\\pycmo\\configs\\config.json")
    config = json.load(f)

    scen_file = "C:\\ProgramData\\Command Professional Edition 2\\Scenarios\\Standalone Scenarios\\Wooden Leg, 1985.scen"
    xml_file = "C:\\Users\\AFSOC A8XW ORSA\\Documents\\Python Proj\\AI\\pycmo\\raw\\wooden_leg.xml"
    player_side = "Israel"

    player_agent = RandomAgent()
    run_loop(scen_file, xml_file, player_side, config=config, agent=player_agent)