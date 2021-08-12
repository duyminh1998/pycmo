"""A run loop for agent/environment interaction."""

from lib.features import Features
from lib.protocol import Client, Server
#from env.environment import TimeStep, StepType
import threading
import time
import json
import os
from datetime import datetime, timedelta

f = open("C:\\Users\\AFSOC A8XW ORSA\\Documents\\Python Proj\\AI\\pycmo\\pycmo\\configs\\config.json")
config = json.load(f)

scen_file = "C:\\ProgramData\\Command Professional Edition 2\\Scenarios\\Standalone Scenarios\\Wooden Leg, 1985.scen"
xml_file = "C:\\Users\\AFSOC A8XW ORSA\\Documents\\Python Proj\\AI\\pycmo\\raw\\wooden_leg.xml"
player_side = "Israel"

for f in os.listdir("C:\\Users\\AFSOC A8XW ORSA\\Documents\\Python Proj\\AI\\pycmo\\raw\\steps"):
    os.remove(os.path.join("C:\\Users\\AFSOC A8XW ORSA\\Documents\\Python Proj\\AI\\pycmo\\raw\\steps\\", f))

""" server = Server(scen_file)
x = threading.Thread(target=server.start_game)
x.start()

time.sleep(15) """

client = Client()
client.connect()

def parse_datetime(time_int):
    n_ticks = time_int & 0x3fffffffffffffff
    secs = n_ticks / 1e7

    d1 = datetime(1, 1, 1)
    t1 = timedelta(seconds = secs)
    return d1 + t1

def ticks_to_unix(ticks):
    return int((int(ticks)/10000000) - 621355968000000000/10000000)

scen_end = False
step_id = 0
state_old = Features(xml_file, player_side)
cur_time = ticks_to_unix(state_old.meta.Time)

while not (step_id > 10):
    # add randomness to agent's actions
    # agent.epsilon = 80 - counter_games

    # get old state
    client.step_and_get_obs("00", "00", "10", config["observation_path"], cur_time, step_id)
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