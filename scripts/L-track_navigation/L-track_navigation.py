# Author: Minh Hua
# Date: 06/21/2022
# Last Update: 06/16/2022
# Purpose: Demonstration of an agent navigating an aircraft through an L-shaped track.

# imports
from pycmo.lib.protocol import Server # Server to handle connection
from pycmo.env import cmo_env
from pycmo.lib import tools
from pycmo.lib import actions
from QLearning import QLearning
from pycmo.configs import config
import pickle
import threading, time

def run_Q_Learning_loop(
    player_side:str,
    agent:QLearning, 
    discount:float, 
    epsilon:float, 
    epsilon_anneal_rate:float,
    eta:float,
    eta_anneal_rate:float,
    min_epochs:int, 
    save_every:int, 
    pickle_dest:str,
    training_dest:str,
    step_size:list=['0', '0', '1'],
    update_agent:bool=True,
    print_debug:bool=False,
    server:bool=False,
    scen_file:str=None
    ) -> None:
    """
    Description:
        Runs an reinforcement learning training loop for a Q Learning agent.

    Args:
        player_side: the side of the player that the agent is controlling.
        agent: the agent to make decisions. If not supplied then environment will initialize one.
        discount: the discount factor.
        epsilon: the epsilon parameter for epsilon-greedy search.
        epsilon:anneal_rate: the anneal rate for epsilon.
        eta: the learning rate.
        eta_anneal_rate: the anneal rate for the learning rate.
        min_epochs: minimum amount of epochs before stopping training.
        save_every: save model information every few iterations.
        pickle_dest: the folder to save pickle information to.
        training_dest: the folder to save training information to.
        step_size: a list containing the step size in the format ["h", "m", "s"]. Default is step size of 1 seconds.
        update_agent: whether or not to update the Q values for the agent.
        print_debug: whether or not to print the state of the map at each time step for debug.
        server: whether or not to initialize a server.
        scen_file: whether or not to use a custom scenario file.

    Return:
        None
    """
    # set up a Command TCP/IP socket if the game is not already running somewhere
    if server:
        server = Server(scen_file)
        x = threading.Thread(target=server.start_game)
        x.start()
        time.sleep(10)

    # open config
    config_file = config.get_config()
    # config and set up, clean up steps folder
    steps_path = config_file["observation_path"]
    tools.clean_up_steps(steps_path)

    # initialize agent
    if not agent:
        agent = QLearning(discount, eta, epsilon, epsilon_anneal_rate)

    # initialize environment
    env = cmo_env.CPEEnv(steps_path, step_size, player_side, config_file["scen_ended"])

    # initial variables and state
    step_id = 0
    initial_state = env.reset()
    old_state = initial_state
    current_reward = -1
    current_epoch = 0
    cur_time = tools.ticks_to_unix(initial_state.observation.meta.Time)
    print(tools.parse_datetime(int(initial_state.observation.meta.Time)))

    # pickle information
    model_pickle_dest = pickle_dest + 'L-track-model.pickle'

    # variable to see if we crossed the finish line
    has_game_ended = env.check_game_ended()

    # main loop
    try:
        while agent.epsilon > 0 or current_epoch < min_epochs:
            # while loop constitutes one epoch
            while not has_game_ended:
                # get current time
                cur_time = tools.ticks_to_unix(old_state.observation.meta.Time)

                # perform random actions or choose the action
                # extract unit lat and long and discretize location
                old_state_coord = (old_state.observation.units[0].Lat, old_state.observation.units[0].Lon)
                desired_waypoint = agent.get_action(old_state)
                action = actions.set_unit_course(player_side, 'MC-130J', desired_waypoint[1], desired_waypoint[0])
                old_state_coord = tools.get_nearest_point_from_location(old_state.observation.units[0].Lat, old_state.observation.units[0].Lon, agent.possible_actions)
                
                # send action to the environment
                step_id += 1
                new_state = env.step(cur_time, step_id, action)
                new_state_coord = tools.get_nearest_point_from_location(new_state.observation.units[0].Lat, new_state.observation.units[0].Lon, agent.possible_actions)
                current_reward = new_state.reward - 1
                current_score = new_state.observation.side_.TotalScore
                # print debug info
                tools.print_env_information(step_id, tools.parse_datetime(int(old_state.observation.meta.Time)), action, current_score, current_reward)

                # check whether game ended
                has_game_ended = env.check_game_ended()

                # call agent to observe new state
                if update_agent:
                    agent.observe(desired_waypoint, old_state_coord, new_state_coord, current_reward)
                
                # set old state as new state
                old_state = new_state

    except KeyboardInterrupt:
        with open(model_pickle_dest, 'wb') as f:
            pickle.dump(agent, f)

if __name__ == "__main__":
    # define an array of discrete latitude and longitude coordinates
    # points = tools.discretize_2d_space(38.21, 40.63, -103.10, -97.63, 30, 25)
    # print(len(points))

    # init config
    epochs = 100000
    discount = 0.9
    eta = 0.2
    epsilon = 1
    epsilon_anneal_rate = 0.00001
    eta_anneal_rate = 0.000001
    save_every = epochs / 10
    # open config
    config_file = config.get_config()
    pickle_dest = config_file["pickle_path"]
    update_agent = True
    print_debug = True
    scen_file = "C:\\Users\\AFSOC A8XW ORSA\\Documents\\Python Proj\\AI\\pycmo\\scen\\L-track.scen"

    run_Q_Learning_loop('A', None, discount, epsilon, epsilon_anneal_rate, eta, eta_anneal_rate, epochs, save_every, pickle_dest, None, ['0', '15', '0'], update_agent, print_debug, True, scen_file)