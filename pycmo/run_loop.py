"""A run loop for agent/environment interaction."""

from lib.features import Features
from lib.protocol import Client, Server
from env.environment import TimeStep, StepType
import threading
import time
import json

f = open("C:\\Users\\AFSOC A8XW ORSA\\Documents\\Python Proj\\AI\\pycmo\\pycmo\\configs\\config.json")
config = json.load(f)

scen_file = "C:\\ProgramData\\Command Professional Edition 2\\Scenarios\\Standalone Scenarios\\Wooden Leg, 1985.scen"
xml_file = "C:\\Users\\AFSOC A8XW ORSA\\Documents\\Python Proj\\AI\\pycmo\\raw\\wooden_leg.xml"
player_side = "Israel"

server = Server(scen_file)
x = threading.Thread(target=server.start_game)
x.start()

time.sleep(15)

client = Client()
client.connect()
""" for i in range(5):
    #client.get_raw_data(config["observation_path"] + str(i) + ".xml")
    client.step_and_get_obs("01", "00", "00", config["observation_path"] + str(i) + ".xml") """

scen_end = False

while not scen_end:
    # add randomness to agent's actions
    # agent.epsilon = 80 - counter_games

    # get old state
    state_old = Features(xml_file, player_side)
    r_old = state_old.side_info.TotalScore
    d_old = 0
    ts_old = TimeStep(StepType(1), r_old, d_old, state_old)

    # perform random actions or choose the action
    # final_move = 
    # player1.do_move(final_move)

    # get new state and observation, rewards, discount
    # client.step_and_get_obs("01", "00", "00", xml_file)
    # env.TimeStep('step_type', 'reward', 'discount', 'observation')
    # new_state = Features(xml_file, player_side)

    # store new data into a long-term memory

    # reset loop
    scen_end = True