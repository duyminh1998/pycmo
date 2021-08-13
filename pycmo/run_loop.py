"""A run loop for agent/environment interaction."""

from lib.features import Features
from lib.protocol import Client, Server
from cmo_env import CMOEnv
import threading, time
from lib.tools import *
import json
import os

def run_loop(scen_file, initial_xml, player_side, server=False, config=None):
    steps_path = config["steps_path"]
    for f in os.listdir(steps_path):
        os.remove(os.path.join(steps_path, f))
    
    if server:
        server = Server(scen_file)
        x = threading.Thread(target=server.start_game)
        x.start()
        time.sleep(15)
    
    env = CMOEnv()
    
    scen_end = False
    step_id = 0
    state_old = Features(initial_xml, player_side)
    cur_time = ticks_to_unix(state_old.meta.Time)

    while not (step_id > 10):
        # add randomness to agent's actions
        # agent.epsilon = 80 - counter_games

        # get old state
        env.step_and_get_obs("00", "00", "10", config["observation_path"], cur_time, step_id)
        xml_file = "C:\\Users\\AFSOC A8XW ORSA\\Documents\\Python Proj\\AI\\pycmo\\raw\\steps\\" + str(step_id) + ".xml"
        state_old = Features(xml_file, player_side)
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
        step_id += 1
        cur_time = ticks_to_unix(state_old.meta.Time)
        print(parse_datetime(int(state_old.meta.Time)))
    

if __name__ == '__main__':
    f = open("C:\\Users\\AFSOC A8XW ORSA\\Documents\\Python Proj\\AI\\pycmo\\pycmo\\configs\\config.json")
    config = json.load(f)

    scen_file = "C:\\ProgramData\\Command Professional Edition 2\\Scenarios\\Standalone Scenarios\\Wooden Leg, 1985.scen"
    xml_file = "C:\\Users\\AFSOC A8XW ORSA\\Documents\\Python Proj\\AI\\pycmo\\raw\\wooden_leg.xml"
    player_side = "Israel"

    run_loop(scen_file, xml_file, player_side, config=config)