# Author: Minh Hua
# Date: 04/19/2022
# Purpose: The main loop to run the environment with a Q Learning agent.

from lib import *
from car import *
from env import *
from QLearning import *
import pickle
import time

def run_Q_Learning_loop(
    map_src:str, 
    agent:QLearning, 
    discount:float, 
    epsilon:float, 
    epsilon_anneal_rate:float,
    eta_anneal_rate:float,
    min_epochs:int, 
    save_every:int, 
    pickle_dest:str,
    training_dest:str,
    restart_policy:int,
    custom_restart_loc:list,
    update_agent:bool=True,
    print_debug:bool=False
    ) -> None:
    """
    Description:
        Runs an reinforcement learning training loop for a Q Learning agent.

    Args:
        map_src: the path to the map.
        agent: the agent to make decisions. If not supplied then environment will initialize one.
        discount: the discount factor.
        epsilon: the epsilon parameter for epsilon-greedy search.
        epsilon:anneal_rate: the anneal rate for epsilon.
        eta_anneal_rate: the anneal rate for the learning rate.
        min_epochs: minimum amount of epochs before stopping training.
        save_every: save model information every few iterations.
        pickle_dest: the folder to save pickle information to.
        training_dest: the folder to save training information to.
        restart_policy: whether the car restarts at the start or at the location of crash.
        custom_restart_loc: custom restart locations to boost learning.
        update_agent: whether or not to update the Q values for the agent.
        print_debug: whether or not to print the state of the map at each time step for debug.

    Return:
        None
    """    
    # config

    # initialize agent
    if not agent:
        agent = QLearning(map_src, discount, eta, epsilon, epsilon_anneal_rate)

    # build Racetrack environment
    env = RacetrackEnv(map_src, None, restart_policy, custom_restart_loc)
    # if a custom restart location is passed in, initialize the car at that location
    if custom_restart_loc:
        env.restart(1, custom_restart_loc[random.randint(0, len(custom_restart_loc) - 1)])

    # initial variables and state
    step_id = 0
    current_reward = -1
    current_epoch = 0
    # average convergence steps
    average_steps_till_win = []

    # variable to see if we crossed the finish line
    has_game_ended = env.check_game_ended()[0]

    # pickle the state
    pickle_file_name = '{}_{}_restart_{}_custom_{}_{}'.format(map_src.split('/')[-1].split('.')[0], 'Q', restart_policy, custom_restart_loc[0], int(time.time()))
    model_pickle_dest = pickle_dest + pickle_file_name + '.pickle'
    model_training_dest = training_dest + pickle_file_name + '.txt'
    with open(model_training_dest, 'a') as f:
        f.write(pickle_file_name)

    # draw initial map
    if print_debug:
        print_game_info(env.map, step_id, env.car.x, env.car.y, env.car.vx, env.car.vy, env.car.ax, env.car.ay)

    # main loop
    # the condition to stop the loop is the win condition or the crash condition or max time step
    try:
        while agent.epsilon > 0 or current_epoch < min_epochs:
            # while loop constitutes one epoch
            while (has_game_ended != 1):
                # check for crash and implement restart strategy
                # if has_game_ended == -1:
                #     # restart environment
                #     if restart_policy == 1:                    
                #         env.restart(restart_policy, (last_X, last_Y))
                #     else:
                #         if custom_restart_loc:
                #             env.restart(1, custom_restart_loc[random.randint(0, len(custom_restart_loc) - 1)])
                #         else:
                #             env.restart(0, None)                        
                #     step_id = 0
                #     # draw restarted map
                #     if print_debug:
                #         print_game_info(env.map, step_id, env.car.x, env.car.y, env.car.vx, env.car.vy, env.car.ax, env.car.ay)
                #     # update loss count because we lost
                #     loss_count += 1
                
                # main loop
                # get old state
                old_state = env.TimeSteps[step_id]

                # call the agent to perform an action
                # action = input("Enter acceleration: ")
                # if action == "":
                #     action = [0, 0]
                # else:
                #     action = action.split(" ")
                action_idx = agent.get_action(old_state.observation)
                action = [acc - 1 for acc in action_idx]

                # send action to the environment
                step_id += 1
                new_state = env.step(step_id, action)
                current_reward = new_state.reward

                # draw new state
                if print_debug:
                    print_game_info(env.map, step_id, new_state.observation.X, new_state.observation.Y, new_state.observation.VX, new_state.observation.VY, action[0], action[1])

                # check whether game ended
                has_game_ended, last_X, last_Y = env.check_game_ended()

                # call agent to observe new state
                if update_agent:
                    agent.observe(action_idx, old_state.observation, new_state.observation, current_reward)
            
            # game has ended, save info
            current_epoch += 1
            # save model information
            if current_epoch % save_every == 0:
                with open(model_pickle_dest, 'wb') as f:
                    pickle.dump(agent, f)
            # save win count
            if has_game_ended == 1:
                average_steps_till_win.append(step_id)
                # call agent to update Q value for terminal state
                if update_agent:
                    old_state = CarState(last_X, last_Y, new_state.observation.VX, new_state.observation.VY)
                    agent.observe(action_idx, old_state, old_state, 0)
            # return metric of this epoch
            print("Epoch: {}, Epsilon: {}, Eta: {}, STW: {}, Average STW: {}".format(current_epoch, agent.epsilon, agent.eta, step_id, np.sum(average_steps_till_win) / len(average_steps_till_win))) 
            with open(model_training_dest, 'a') as f:
                f.write("Epoch: {}, Epsilon: {}, Eta: {}, STW: {}, Average STW: {}\n".format(current_epoch, agent.epsilon, agent.eta, step_id, np.sum(average_steps_till_win) / len(average_steps_till_win)))

            # draw final state
            if print_debug:
                print_game_info(env.map, step_id, new_state.observation.X, new_state.observation.Y, new_state.observation.VX, new_state.observation.VY, action[0], action[1])

            # restart agent annealing rate
            agent.epsilon = agent.epsilon - epsilon_anneal_rate
            agent.eta = agent.eta - eta_anneal_rate
            if agent.epsilon < 0:
                agent.epsilon = 0.0 # clamp epsilon if it gets too low
            if agent.eta < 0:
                agent.eta = 0.0 # clamp eta if it gets too low
            
            # restart the environment
            # place car at the custom location if passed in, else place at the start
            if custom_restart_loc:
                env.restart(1, custom_restart_loc[random.randint(0, len(custom_restart_loc) - 1)])
            else:
                env.restart(0, None)
            step_id = 0
            has_game_ended = env.check_game_ended()[0]  
            # draw restarted map
            if print_debug:
                print_game_info(env.map, step_id, env.car.x, env.car.y, env.car.vx, env.car.vy, env.car.ax, env.car.ay)
                       
    except KeyboardInterrupt:
        with open(model_pickle_dest, 'wb') as f:
            pickle.dump(agent, f)
    
    return model_pickle_dest

# test code
if __name__ == "__main__":
    test = 0

    # init config
    map_src = '../data/L-track.txt'
    epochs = 100000
    discount = 0.9
    eta = 0.2
    epsilon = 1
    epsilon_anneal_rate = 0.00001
    eta_anneal_rate = 0.000001
    save_every = epochs / 10
    pickle_dest = 'pickle/QLearning/L-track/'
    training_dest = 'training/QLearning/L-track/'
    restart_policy = 1
    update_agent = True
    print_debug = True

    # init agent
    # f = open('pickle/QLearning/L-track/L-track_Q_restart_1_custom_[35, 7]_1651344211.pickle', 'rb')
    f = open('pickle/QLearning/L-track/L-track_Q_restart_1_custom_[35, 1]_1651382394.pickle', 'rb')
    agent = pickle.load(f)
    f.close()
    agent.epsilon = epsilon
    agent = QLearning(map_src, discount, eta, epsilon, epsilon_anneal_rate)
    # init custom restart locations to speed up learning
    L_track_custom_starts = [
        [[35, 7], [34, 7], [33, 7], [32, 7]],
        [[35, 5], [34, 5], [33, 5], [32, 5]],
        [[35, 3], [34, 3], [33, 3], [32, 3]],
        [[35, 1], [34, 1], [33, 1], [32, 1]],
        [[31, 4], [31, 3], [31, 2], [31, 1]],
        [[29, 4], [29, 3], [29, 2], [29, 1]],
        [[27, 4], [27, 3], [27, 2], [27, 1]],
        [[25, 4], [25, 3], [25, 2], [25, 1]],
        [[23, 4], [23, 3], [23, 2], [23, 1]],
        [[20, 4], [20, 3], [20, 2], [20, 1]],
        [[18, 4], [18, 3], [18, 2], [18, 1]],
        [[16, 4], [16, 3], [16, 2], [16, 1]],
        [[14, 4], [14, 3], [14, 2], [14, 1]],
        [[12, 4], [12, 3], [12, 2], [12, 1]],
        [[10, 4], [10, 3], [10, 2], [10, 1]],
        [[8, 4], [8, 3], [8, 2], [8, 1]],
        [[6, 4], [6, 3], [6, 2], [6, 1]],
        [[4, 4], [4, 3], [4, 2], [4, 1]],
        [[2, 4], [2, 3], [2, 2], [2, 1]],
        [[1, 4], [1, 3], [1, 2], [1, 1]]
    ]
    custom_start_loc = L_track_custom_starts[0]
    
    # test run loop
    if test == 0:
        for custom_start_loc_idx in range(0, len(L_track_custom_starts)):
            custom_start_loc = L_track_custom_starts[custom_start_loc_idx]
            model_pickle_dest = run_Q_Learning_loop(map_src, agent, discount, epsilon, epsilon_anneal_rate, eta_anneal_rate, epochs, save_every, pickle_dest, training_dest, restart_policy, custom_start_loc, update_agent, print_debug)
            f = open(model_pickle_dest, 'rb')
            agent = pickle.load(f)
            f.close()
            agent.epsilon = 1
            agent.eta = 0.2