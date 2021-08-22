# Author: Minh Hua
# Date: 08/16/2021
# Purpose: A random agent.

import random

class RandomAgent():
    def __init__(self, scenario, player_side):
        self.scenario = scenario
        self.player_side = player_side

    def get_action(self, observation, VALID_FUNCTIONS):
        function = random.choice(VALID_FUNCTIONS)
        if function.id == 0: # no-op
            return '--script \nTool_EmulateNoConsole(true)'
        args = []
        for arg, arg_type in zip(function.args, function.arg_types):
            if arg_type == "EnumChoice":
                args.append(random.choice(arg))
            elif arg_type == "Range":
                args.append(random.uniform(arg[0], arg[-1]))
        try:
            return function.corresponding_def(*args)
        except: # no-op
            return "--script \nTool_EmulateNoConsole(true)"
