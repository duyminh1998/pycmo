# Author: Minh Hua
# Date: 08/16/2021
# Last Update: 06/16/2022
# Purpose: Library of helper functions.

# imports
from datetime import datetime, timedelta
import os
import numpy as np
import subprocess
import json
import win32gui

from pycmo.configs.config import get_config

config = get_config()

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

def parse_utc(utc:int) -> datetime:
    return datetime.fromtimestamp(utc)

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

def euclidean_distance(p1:np.array, p2:np.array) -> float:
    """
    Description:
        Returns the Euclidean distance between two points p1 and p2.

    Keyword Arguments:
        p1: array of coordinates of first point.
        p2: array of coordinates of second point.

    Returns:
        (float) Euclidean distance between p1 and p2
    """
    # convert arrays to np if not in np array format
    if type(p1) != np.array:
        p1 = np.array(p1)
    if type(p2) != np.array:
        p2 = np.array(p2)
    return np.linalg.norm(p1 - p2)

def discretize_2d_space(min_lat:float, max_lat:float, min_long:float, max_long:float, num_lat:int, num_long:int) -> list:
    """
    Description:
        Discretize a continuous 2D space by generating a fixed mesh of points.

    Keyword Arguments:
        min_lat: the minimum latitude value of the space.
        max_lat: the maximum latitude value of the space.
        min_long: the minimum longitude value of the space.
        max_long: the maximum longitude value of the space.
        num_lat: the number of points in the vertical direction to generate.
        num_long: the number of points in the horizontal direction to generate.
    """
    x = np.linspace(min_lat, max_lat, num_lat)
    y = np.linspace(min_long, max_long, num_long)
    xx, yy = np.meshgrid(x, y)
    discrete_points = []
    for i in range(len(xx)):
        for j in range(len(xx[i])):
            discrete_points.append([xx[i][j], yy[i][j]])
    # return
    return discrete_points

def get_nearest_point_from_location(raw_lat:float, raw_long:float, coords:list) -> list:
    """
    Description:
        Get the nearest discrete point from the unit's current position as a strategy to discretize the unit's position.

    Keyword Arguments:
        raw_lat: the current latitude of the unit.
        raw_long: the current longitude of the unit.
        coords: a list of discretized coordinates, e.g. coords = [[1, 0], [0, 1], [2, 0], ...]

    Returns:
        (list) the lat and long of the closest coordinate in coords to the unit's position.
    """
    min_dist = float('inf')
    closest_pt = None
    check_coord = [raw_lat, raw_long] # coordinate of the main point to check other points against
    for coord in coords:
        cur_dist = euclidean_distance(check_coord, coord)
        if cur_dist < min_dist:
            min_dist = cur_dist
            closest_pt = coord
    # return closest point
    return closest_pt

def process_exists(process_name):
    """Check whether a process exists. https://stackoverflow.com/questions/7787120/check-if-a-process-is-running-or-not-on-windows"""
    call = 'TASKLIST', '/FI', 'imagename eq %s' % process_name
    # use buildin check_output right away
    output = subprocess.check_output(call).decode()
    # check in last line for process name
    last_line = output.strip().split('\r\n')[-1]
    # because Fail message could be translated
    return last_line.lower().startswith(process_name.lower())

def win32gui_window_exists(window_name:str):
    ret = []
    def win_enum_handler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            txt = win32gui.GetWindowText(hwnd)
            if txt == window_name:
                ret.append((hwnd,txt))
    win32gui.EnumWindows(win_enum_handler, None)
    if len(ret) > 0: return True
    else: return False

def window_exists(window_name:str, fast:bool=True, script_path:str=None) -> bool:
    if fast:
        return win32gui_window_exists(window_name=window_name)
    else:
        try:
            if not script_path: script_path = os.path.join(config['scripts_path'], 'checkWindowExistsByTitle.ps1')
            window_exists_process = subprocess.run(['PowerShell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', script_path, window_name], capture_output=True, text=True)
            process_exists = bool(window_exists_process.stdout.strip())
            if process_exists: return True
            else: return False
        except FileNotFoundError:
            raise FileNotFoundError(f"Cannot find '{script_path}'.")
    
def cmo_steam_observation_file_to_xml(file_path:str) -> str or None:
    try:
        with open(file_path, 'r') as f:
            observation_file_contents = f.read()
    except FileNotFoundError:
        return None
    
    try:
        observation_file_json = json.loads(observation_file_contents)
    except json.decoder.JSONDecodeError:
        return None
    
    observation_xml = observation_file_json["Comments"]
    return observation_xml

def send_key_press(key:str, window_name:str, script_path:str=os.path.join(config['scripts_path'], 'nonsecureSendKeys.bat')) -> bool:
    try:
        send_key_process = subprocess.run([script_path, window_name, key])
        return True
    except FileNotFoundError:
        raise FileNotFoundError(f"Cannot find '{script_path}'.")
