# Author: Minh Hua
# Date: 04/25/2022
# Purpose: Value iteration algorithm.

from lib import *
import numpy as np
import pickle
import time
import random

def ValueIteration(
    map_name:str,
    map_folder:str,
    epsilon:float,
    discount:float,
    restart_policy:int,
    possible_actions:list=[-1, 0, 1],
    vmax:int=5,
    vmin:int=-5,
    prob_fail:float=0.2,
    prob_success:float=0.8,
    pickle_dest:str=None,
    training_dest:str=None
):
    """
    Description:
        Algorithm for Value Iteration.

    Args:
        map_name: the name of the track.
        map_folder: the folder containing the maps.
        epsilon: the threshold for convergence.
        discount: the discount factor.
        possible_actions: the list of possible actions, e.g values for accelerations.
        vmax: the maximum velocity.
        vmin: the minimum velocity.
        prob_fail: the probability that the action will fail.
        prob_success: the probability that the action will succeed.
        pickle_dest: the folder to save the pickle information.

    Return:
        None
    """    
    # get map
    map_src = map_folder + '/{}.txt'.format(map_name)
    base_map, base_map_info = get_map(map_src)

    # initialize parameters
    delta = epsilon + 1 # delta parameter to check for convergence
    epoch = 0
    # define boundaries of the map
    xmin, ymin = 0, 0
    xmax, ymax = base_map_info.Width - 1, base_map_info.Height - 1
    # clamp the changes down to +-5 if it exceeds it
    clamp = lambda n, minn, maxn: max(min(maxn, n), minn)
    training_time = int(time.time()) # time to mark training

    # initialize Q and V tables
    Q = np.random.uniform(-10, -9, size = (base_map_info.Width, base_map_info.Height, 11, 11, 3, 3)) # Q(s = (x, y, vx, vy), a = [-1, 0, 1] * 2) array
    V = np.random.uniform(-10, -9, size = (base_map_info.Width, base_map_info.Height, 11, 11)) # V(s = (x, y, vx, vy)) array

    # loop until convergence
    while delta >= epsilon:
        delta = 0
        # loop through each s in S
        for x_idx, x in enumerate(V):
            for y_idx, y in enumerate(V[x_idx]):
                for vx_idx, vx in enumerate(V[x_idx][y_idx]):
                    for vy_idx, vy in enumerate(V[x_idx][y_idx][vx_idx]):
                        # check if we are at a wall piece, if we are, then no action is available
                        if (x_idx, y_idx) not in base_map_info.WallLocs and (x_idx, y_idx) not in base_map_info.FinishLocs:
                            curV = V[x_idx][y_idx][vx_idx][vy_idx] # save the current V for comparison to check convergence
                            # we are not at a wall location, continue to update V
                            for ax_idx, ax in enumerate(possible_actions):
                                for ay_idx, ay in enumerate(possible_actions):
                                    # get successor state of successful velocity application
                                    new_vx = clamp(vx_idx + vmin + ax, vmin, vmax)
                                    new_vy = clamp(vy_idx + vmin + ay, vmin, vmax)
                                    new_x = clamp(x_idx + new_vx, xmin, xmax)
                                    new_y = clamp(y_idx + new_vy, ymin, ymax)
                                    new_vx = new_vx + vmax
                                    new_vy = new_vy + vmax
                                    # check if we collided, if we did, place at the location of collision
                                    success_game_status, success_last_X, success_last_Y = determine_win(base_map, x_idx, y_idx, new_x, new_y)
                                    if success_game_status == -1: # crashed, implement restart policy
                                        if restart_policy == 1: # place at crash location
                                            new_x = success_last_X
                                            new_y = success_last_Y
                                        else: # place at start location
                                            start_pos = base_map_info.StartLocs[random.randint(0, len(base_map_info.StartLocs) - 1)]
                                            new_x = start_pos[0]
                                            new_y = start_pos[1]
                                        new_vx = vmax # reset velocity
                                        new_vy = vmax # reset velocity
                                    
                                    # failure state is the same as the current state, except the position changes
                                    fail_x = clamp(x_idx + vx_idx + vmin, xmin, xmax)
                                    fail_y = clamp(y_idx + vy_idx + vmin, ymin, ymax)
                                    fail_vx = vx_idx
                                    fail_vy = vy_idx
                                    # check if we collided, if we did, place at the location of collision
                                    fail_game_status, fail_last_X, fail_last_Y = determine_win(base_map, x_idx, y_idx, fail_x, fail_y)
                                    if fail_game_status == -1: # crashed, implement restart policy
                                        if restart_policy == 1: # place at crash location
                                            fail_x = fail_last_X
                                            fail_y = fail_last_Y
                                        else: # place at start location
                                            start_pos = base_map_info.StartLocs[random.randint(0, len(base_map_info.StartLocs) - 1)]
                                            fail_x = start_pos[0]
                                            fail_y = start_pos[1]
                                        fail_vx = vmax # reset velocity
                                        fail_vy = vmax # reset velocity

                                    # check reward, reward only 0 at finish state, else it is -1
                                    old_reward, new_reward = -1, -1
                                    if (fail_x, fail_y) in base_map_info.FinishLocs:
                                        old_reward = 0
                                    if (new_x, new_y) in base_map_info.FinishLocs:
                                        new_reward = 0
                                    # check wether we crossed the finish line
                                    if success_game_status == 1:
                                        new_reward = 0
                                        new_x = success_last_X
                                        new_y = success_last_Y
                                    if fail_game_status == 1:
                                        old_reward = 0
                                        fail_x = fail_last_X
                                        fail_y = fail_last_Y
                                    
                                    # update Q value
                                    # Q(s, a) = E[r|s,a] + discount * Sum P(s'|s,a)V(s')
                                    expected_reward = old_reward * prob_fail + new_reward * prob_success
                                    new_state_value_sum = prob_fail * V[fail_x][fail_y][fail_vx][fail_vy] + prob_success * V[new_x][new_y][new_vx][new_vy]
                                    Q[x_idx][y_idx][vx_idx][vy_idx][ax_idx][ay_idx] = expected_reward + discount * new_state_value_sum
                            # update V(s)
                            V[x_idx][y_idx][vx_idx][vy_idx] = np.max(Q[x_idx][y_idx][vx_idx][vy_idx])
                            delta = max(delta, abs(curV - V[x_idx][y_idx][vx_idx][vy_idx]))
                        # if we are at a finish location, no transitions can be made
                        elif (x_idx, y_idx) in base_map_info.FinishLocs:
                            for ax_idx, ax in enumerate(possible_actions):
                                for ay_idx, ay in enumerate(possible_actions):
                                    expected_reward = 0
                                    new_state_value_sum = (prob_fail + prob_success) * V[x_idx][y_idx][vx_idx][vy_idx]
                                    Q[x_idx][y_idx][vx_idx][vy_idx][ax_idx][ay_idx] = expected_reward + discount * new_state_value_sum
                            V[x_idx][y_idx][vx_idx][vy_idx] = np.max(Q[x_idx][y_idx][vx_idx][vy_idx])
        # print debug info
        print("Epoch: {}, Maximum delta: {}".format(epoch, delta))
        # save training results
        if training_dest:
            with open(training_dest.format(map_name, restart_policy, training_time), 'a') as f:
                f.write("Epoch: {}, Maximum delta: {} \n".format(epoch, delta))
        epoch += 1

    # save V and Q tables
    if pickle_dest:
        with open(pickle_dest.format(map_name, restart_policy, 'Q', training_time), 'wb') as f:
            pickle.dump(Q, f)
        with open(pickle_dest.format(map_name, restart_policy, 'V', training_time), 'wb') as f:
            pickle.dump(V, f)

if __name__ == "__main__":
    test = 0

    map_name = 'R-track'
    map_folder = '../data'
    epsilon = 0.005
    discount = 0.9
    restart_policy = 0
    pickle_dest = 'pickle/ValueIteration/' + map_name + '/{}_restart_{}_{}_{}.pickle'
    training_dest = 'training/ValueIteration/' + map_name + '/{}_restart_{}_{}.txt'
    # test Value Iteration
    if test == 0:
        ValueIteration(map_name, map_folder, epsilon, discount, restart_policy, pickle_dest=pickle_dest, training_dest=training_dest)
    # read back V table
    elif test == 1:
        V_src = 'pickle/ValueIteration/' + map_name + '/' + map_name + '_restart_0_Q_1651374822.pickle'
        with open(V_src, 'rb') as f:
            V = pickle.load(f)
            print(np.min(V))
            test = V[1][1][5][5]
            print(test)
            optimal_action = np.unravel_index(np.argmax(test, axis=None), test.shape)
            vx, vy = optimal_action[0] - 1, optimal_action[1] - 1
            print(vx, vy)
    # read back Q table
    elif test == 2:
        pass