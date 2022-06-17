# Author: Minh Hua
# Date: 04/26/2022
# Purpose: Sarsa algorithm.

from lib import *
from env import CarState
import numpy as np

class Sarsa:
    """Sarsa algorithm"""
    def __init__(
        self,
        map_src:str,
        discount:float,
        eta:float,
        epsilon:float,
        epsilon_anneal_rate:float
    ):
        """
        Description:
            Initializes a Sarsa agent.

        Args:
            map_src: the path to the map. Defines the size of the Q table.
            discount: the discount factor.
            eta: the learning rate.
            epsilon: the epsilon parameter for epsilon-greedy search.
            epsilon:anneal_rate: the anneal rate for epsilon.

        Return:
            None
        """    
        # get map
        self.base_map, self.base_map_info = get_map(map_src)

        # initialize parameters
        self.discount = discount
        self.eta = eta
        self.epsilon = epsilon
        self.epsilon_anneal_rate = epsilon_anneal_rate
        # bookkeeping variables
        self.possible_actions = [-1, 0, 1]
        self.vmin = -5
        self.vmax = 5

        # initialize Q table
        self.Q = np.random.uniform(-10, -9, size = (self.base_map_info.Width, self.base_map_info.Height, 11, 11, 3, 3)) # Q(s = (x, y, vx, vy), a = [-1, 0, 1] * 2) array
        # initialize terminal state to be 0
        for terminal_state in self.base_map_info.FinishLocs:
            x = terminal_state[0]
            y = terminal_state[1]
            for vx_idx, _ in enumerate(self.Q[x][y]):
                for vy_idx, _ in enumerate(self.Q[x][y][vx_idx]):
                    for ax_idx, _ in enumerate(self.possible_actions):
                        for ay_idx, _ in enumerate(self.possible_actions):
                            self.Q[x][y][vx_idx][vy_idx][ax_idx][ay_idx] = 0

    def get_action(self, state:CarState) -> tuple:
        """
        Description:
            Get a corresponding action for a state

        Args:
            state: the state of the environment at a timestep.

        Return:
            None
        """
        # action changes depending on the policy
        return self.epsilon_greedy(state)

    def observe(self, old_action:list, new_action:list, old_state:CarState, new_state:CarState, r:int) -> None:
        """
        Description:
            Updates the Q table using the reward from the action.

        Args:
            old_action: the action taken to get from old_state to new_state.
            new_action: the best action at the new state.
            old_state: the previous state.
            new_state: the current state.
            r: the reward received at the new_state.

        Return:
            None
        """        
        old_Q = self.Q[old_state.X][old_state.Y][old_state.VX + self.vmax][old_state.VY + self.vmax][old_action[0]][old_action[1]] # Q(s, a) we are updating
        new_Q = self.Q[new_state.X][new_state.Y][new_state.VX + self.vmax][new_state.VY + self.vmax][new_action[0]][new_action[1]] # reference to the new state
        Q_update_val = old_Q + self.eta * (r + self.discount * new_Q - old_Q)
        self.Q[old_state.X][old_state.Y][old_state.VX + self.vmax][old_state.VY + self.vmax][old_action[0]][old_action[1]] = Q_update_val

    def epsilon_greedy(self, state:CarState) -> tuple:
        """
        Description:
            Epsilon-greedy policy for taking an action.

        Args:
            state: the state of the environment at a timestep.

        Return:
            (tuple) the chosen action
        """        
        explore_or_exploit = np.random.choice([0, 1], p=[self.epsilon, 1 - self.epsilon]) # whether we explore or exploit
        # explore
        if explore_or_exploit == 0:
            ax_choice = np.random.randint(0, 3)
            ay_choice = np.random.randint(0, 3)
            action = (ax_choice, ay_choice)
        # exploit
        else:
            action_probabilities = self.softmax_actions(state) # get the action probabilities for the state
            action = np.unravel_index(np.argmax(action_probabilities, axis=None), action_probabilities.shape)
        # anneal epsilon
        # if self.epsilon - self.epsilon_anneal_rate >= 0:
        #     self.epsilon -= self.epsilon_anneal_rate
        # return action
        return action

    def softmax_actions(self, state:CarState) -> list:
        """
        Description:
            Turns actions into softmax probabilities.

        Args:
            state: the state of the environment at a timestep.

        Return:
            (tuple) the chosen action
        """        
        action_probabilities = np.zeros(self.Q[state.X][state.Y][state.VX + self.vmax][state.VY + self.vmax].shape) # store softmax probabilities for each action
        denom = np.sum(np.exp(self.Q[state.X][state.Y][state.VX + self.vmax][state.VY + self.vmax])) # denominator of softmax
        for ax_idx, _ in enumerate(self.possible_actions):
            for ay_idx, _ in enumerate(self.possible_actions):
                numerator = np.exp(self.Q[state.X][state.Y][state.VX + self.vmax][state.VY + self.vmax][ax_idx][ay_idx])
                action_probabilities[ax_idx][ay_idx] = numerator / denom
        return action_probabilities

if __name__ == "__main__":
    test = 0

    map_name = 'L-track'
    map_folder = '../data'
    discount = 0.9
    eta = 0.2
    pickle_dest = 'pickle/QLearning/{}_{}_{}.pickle'
    # test Value Iteration
    if test == 0:
        agent = Sarsa(map_name, map_folder, discount, eta, pickle_dest=pickle_dest)