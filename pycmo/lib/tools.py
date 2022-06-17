# Author: Minh Hua
# Date: 08/16/2021
# Last Update: 06/16/2022
# Purpose: Library of helper functions.

# imports
from datetime import datetime, timedelta
import os

def parse_datetime(time_int:int) -> datetime:
    """
    Description:
        Parses Ticks time into a readable format.

    Keyword Arguments:
        time_int: time in Ticks format
    
    Returns:
        (datetime)
    """    
    n_ticks = time_int & 0x3fffffffffffffff
    secs = n_ticks / 1e7

    d1 = datetime(1, 1, 1)
    t1 = timedelta(seconds = secs)
    return d1 + t1

def ticks_to_unix(ticks:int) -> int:
    """
    Description:
        Converts time in Ticks format to UNIX format.

    Keyword Arguments:
        ticks: time in Ticks format
    
    Returns:
        (int) time in UNIX format
    """    
    return int((int(ticks)/10000000) - 621355968000000000/10000000)

def clean_up_steps(path:str) -> None:
    """
    Description:
        Delete all the steps file (.xml) in the steps folder.

    Keyword Arguments:
        path: the path to the folder containing the steps (.xml) files.

    Returns:
        None
    """
    try:
        for step in os.listdir(path):
            if step.endswith('.xml'):
                os.remove(os.path.join(path, step))
    except:
        raise ValueError("Failed to clean up steps folder.")

def print_env_information(step_id:int, current_time:datetime, final_move:str, current_score:int, current_reward:int) -> None:
    """
    Description:
        Prints debug information about the current time step.

    Keyword Arguments:
        step_id: the id of the current step.
        current_time: the current date and time.
        final_move: the last action that the agent took.
        current_score: the current score.
        current_reward: the reward at the current time step.

    Returns:
        None
    """    
    print("Step: {}".format(step_id))
    print("Current Time: {}".format(current_time))
    print("Action: {}".format(final_move))
    print("Current scenario score: {} \nCurrent reward: {}\n".format(current_score, current_reward))