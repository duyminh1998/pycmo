# Author: Minh Hua
# Date: 06/21/2022
# Last Updated: 06/21/2022
# Purpose: Q-learning algorithm for track navigation.

# imports
import numpy as np
from pycmo.lib import tools

class QLearning:
    """Q Learning algorithm for track navigation."""
    def __init__(
        self,
        discount:float,
        eta:float,
        epsilon:float,
        epsilon_anneal_rate:float
    ):
        """
        Description:
            Initializes a Q Learning agent.

        Args:
            discount: the discount factor.
            eta: the learning rate.
            epsilon: the epsilon parameter for epsilon-greedy search.
            epsilon:anneal_rate: the anneal rate for epsilon.

        Return:
            None
        """    
        # initialize parameters
        self.discount = discount
        self.eta = eta
        self.epsilon = epsilon
        self.epsilon_anneal_rate = epsilon_anneal_rate

        # bookkeeping variables
        self.possible_actions = tools.discretize_2d_space(38.21, 40.63, -103.10, -97.63, 30, 25)
        # convert possible actions into a dictionary for easier indexing
        self.possible_actions_dict = {}
        dict_idx = 0
        for possible_action in self.possible_actions:
            self.possible_actions_dict[str(possible_action[0]) + '_' + str(possible_action[1])] = dict_idx
            dict_idx += 1

        # initialize Q table
        # Q(s = (x, y), a = [[x1, y1], [x2, y2], ..., [x750, y750]]) array
        self.Q = np.random.uniform(-10, -9, size = (len(self.possible_actions), len(self.possible_actions))) 

    def get_action(self, state:list) -> tuple:
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

    def observe(self, action:list, old_state:list, new_state:list, r:int) -> None:
        """
        Description:
            Updates the Q table using the reward from the action.

        Args:
            action: the action taken to get from old_state to new_state.
            old_state: the previous state.
            new_state: the current state.
            r: the reward received at the new_state.

        Return:
            None
        """
        old_state_query_str = str(old_state[0]) + "_" + str(old_state[1]) # the key to find the index of the old state
        new_state_query_str = str(new_state[0]) + "_" + str(new_state[1]) # the key to find the index of the new state
        action_query_str = str(action[0]) + "_" + str(action[1]) # the key to find the index of the action
        old_Q = self.Q[self.possible_actions_dict[old_state_query_str]][self.possible_actions_dict[action_query_str]] # Q(s, a) we are updating
        new_Q = self.Q[self.possible_actions_dict[new_state_query_str]] # reference to the new state
        max_action_for_new_state = np.max(new_Q)
        Q_update_val = old_Q + self.eta * (r + self.discount * max_action_for_new_state - old_Q)
        self.Q[self.possible_actions_dict[old_state_query_str]][self.possible_actions_dict[action_query_str]] = Q_update_val

    def epsilon_greedy(self, state:list) -> tuple:
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
            a_choice = np.random.randint(0, len(self.possible_actions))
        # exploit
        else:
            action_probabilities = self.softmax_actions(state) # get the action probabilities for the state
            a_choice = np.unravel_index(np.argmax(action_probabilities, axis=None), action_probabilities.shape)
            a_choice = a_choice[0]
        action = (self.possible_actions[a_choice][0], self.possible_actions[a_choice][1])
        # anneal epsilon
        # if self.epsilon - self.epsilon_anneal_rate >= 0:
        #     self.epsilon -= self.epsilon_anneal_rate
        # return action
        return action

    def softmax_actions(self, state:list) -> list:
        """
        Description:
            Turns actions into softmax probabilities.

        Args:
            state: the state of the environment at a timestep.

        Return:
            (tuple) the chosen action
        """
        state_query_str = str(state[0]) + "_" + str(state[1]) # the key to find the index of the state
        state_Q_array = self.Q[self.possible_actions_dict[state_query_str]] # the array of Q-values for the actions of a state
        action_probabilities = np.zeros(state_Q_array.shape) # store softmax probabilities for each action
        denom = np.sum(np.exp(state_Q_array)) # denominator of softmax
        for action_idx in range(len(self.possible_actions)):
            numerator = np.exp(state_Q_array[action_idx])
            action_probabilities[action_idx] = numerator / denom
        return action_probabilities

if __name__ == "__main__":
    test = 0

    discount = 0.9
    eta = 0.2
    epsilon = 0.1
    epsilon_anneal_rate = 0.00001

    # test Value Iteration
    if test == 0:
        agent = QLearning(discount, eta, epsilon, epsilon_anneal_rate)
        old_state = tools.get_nearest_point_from_location(40, -100, tools.discretize_2d_space(38.21, 40.63, -103.10, -97.63, 30, 25))
        new_state = tools.get_nearest_point_from_location(30, -105, tools.discretize_2d_space(38.21, 40.63, -103.10, -97.63, 30, 25))
        action = agent.get_action(old_state)
        agent.observe(action, old_state, new_state, -1)
        print(action)