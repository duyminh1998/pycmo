# Author: Minh Hua
# Date: 08/16/2021
# Purpose: A random agent.

import random

class RandomAgent():
    def __init__(self):
        pass

    def get_action(self, VALID_FUNCTIONS):
        function = random.choice(VALID_FUNCTIONS)
        if function.id == 0: # no-op
            return ''
        args = [random.choice(arg) for arg in function.args if arg != []]
        return function.corresponding_def(*args)
