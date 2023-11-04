# Author: Minh Hua
# Date: 06/16/2022
# Last Update: 06/16/2022
# Purpose: Tests for cmo_env.py.

# imports
from pycmo.env import cmo_env
from pycmo.configs import config
from pycmo.lib.tools import *

# open config and set important files and folder paths
config = config.get_config()

# test CPEEnv class
# init
step_size = ['0', '0', '1']
side = 'US'
env = cmo_env.CPEEnv(config['observation_path'], step_size, side, config['scen_ended'])

# reset
step = env.reset()

# step
# step = env.step(1655215428, 1)

# end connection
print(env.close())