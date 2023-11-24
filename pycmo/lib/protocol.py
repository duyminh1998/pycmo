# Author: Minh Hua
# Date: 08/16/2021
# Last Update: 06/16/2022
# Purpose: Protocol library to communicate with a Command server.

# imports
import socket
import subprocess
import os
from typing import Callable, Tuple
from time import sleep

from pycmo.configs.config import get_config
from pycmo.lib.tools import process_exists, window_exists, send_key_press

# open config and set important files and folder paths
config = get_config()

class Server():
    """
    Wrapper for an instance of CommandCLI running a specified scenario. 
    This class acts as the "server" by starting a CLI instance of Command.
    This mode of execution relies on the CLI mode of the game. 
    The Server is not needed if the user intends to run the agent with the normal game (running the normal executable with the GUI).
    """
    def __init__(self, scenario: str) -> None:
        """
        Description:
            Initializes the server.

        Keyword Arguments:
            scenario: the path to the scenario (.scen) file

        Returns:
            None
        """
        self.scenario = scenario # the path to the scenario (.scen) file to start the game with

    def start_game(self) -> None:
        """
        Description:
            Starts the game with the loaded scenario in paused mode.
            This code should be ran in a terminal to act as a server.

        Keyword Arguments:
            None

        Returns:
            None
        """        
        try:
            prog_path = config['command_path'] # the path to the installation folder of Command
            command = "CommandCLI.exe -mode I -scenfile \"{}\" -outputfolder \"{}\"".format(self.scenario, config['command_cli_output_path']) # shell command to start an instance of the scenario with CommandCLI
            subprocess.call(command, shell=True, cwd = prog_path)
        except:
            print("ERROR: Failed to start game server.")

    def restart(self) -> None:
        """
        Description:
            Restarts the game by calling self.start_game().

        Keyword Arguments:
            None

        Returns:
            None
        """               
        self.start_game()

    def end_game(self):
        # TODO
        pass

class Client():
    """
    The Client connects to the Server (either the Server class or a GUI-instance of the game running) and sends actions to the game.
    Connection is via a TCP/IP port.
    See the Command Premium Edition manual for configuration. This functionality is only available in the Premium version of the game.
    """
    def __init__(self, host:str="localhost", port:int=7777) -> None:
        """
        Description:
            Initializes the client.

        Keyword Arguments:
            host: the IP host of the socket. Default is "localhost".
            port: the port on which the game is receiving instructions. Default is 7777.

        Returns:
            None
        """
        self.host = host
        self.port = port
        
    def connect(self) -> bool:
        """
        Description:
            Connect to the game.

        Keyword Arguments:
            host: the IP host of the socket. Default is "localhost".
            port: the port on which the game is receiving instructions. Default is 7777.

        Returns:
            (bool) connection successful or not
        """
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # open a socket to the game
            self.s.connect((self.host, self.port))
            return True
        except OSError:
            raise ConnectionError("No active instance of Command to connect to. Aborting.")

    def send(self, data:str, encoding:str="UTF-8") -> str:
        """
        Description:
            Send a command or an entire script to the game via data packets to the socket.

        Keyword Arguments:
            data: a string of commands to send to the game's Lua API. Refer to the documentation for formatting.
            encoding: different encoding types when connecting to Lua TCP socket.
                NOTE: This is determined by the CPE.ini file in the game's configuration files. Set these accordingly.
                For this code, we chose UTF-8 encoding.

        Returns:
            (str) return code of the send operation
        """
        try:
            self.s.sendall(data.encode(encoding=encoding))
            data = self.s.recv(1024)
            received = str(data, encoding)
            return received
        except OSError:
            raise ConnectionError("Failed to send data to CMO server.")

    def restart(self) -> bool:
        """
        Description:
            Restart the client's connection the game.

        Keyword Arguments:
            None

        Returns:
            (bool) connection successful or not
        """
        self.end_connection() # close the current connection
        return self.connect()

    def end_connection(self) -> bool:
        """
        Description:
            End the client's connection the game.

        Keyword Arguments:
            None

        Returns:
            (bool) connection end successful or not
        """
        try:
            self.s.close()
            return True
        except:
            raise ConnectionError("Failed to close client connection.")
        
class SteamClient():
    """The Client connects to the Steam edition of the game and sends actions to the game."""
    def __init__(self, 
                 scenario_name:str,
                 agent_action_filename:str="python_agent_action.lua",
                 command_version:str=config["command_mo_version"],
                 enter_scenario_max_retries:int=10) -> None:
        self.scenario_name = scenario_name
        self.agent_action_filename = agent_action_filename
        self.cmo_window_title = f"{scenario_name} - {command_version}"
        self.enter_scenario_max_retries = enter_scenario_max_retries
        self.scenario_paused_popup_name = "Incoming message"
        self.scenario_end_popup_name = "Scenario End"
        self.player_evaluation_popup_name = "Player Evaluation"

    def connect(self, command_process_name:str="Command.exe") -> bool:
        return process_exists(command_process_name)

    def send(self, data:str) -> bool:
        retries = 0
        max_send_retries = 100
        while retries < max_send_retries:
            try:
                with open(self.agent_action_filename, 'w') as f:
                    f.write(data)
                return True
            except PermissionError:
                print(f"Failed to send agent action. Retrying... (Attempt {retries + 1} of {max_send_retries})")
                retries += 1
            except FileNotFoundError:
                raise FileNotFoundError(f"Unable to find {self.agent_action_filename} to write agent action to.")
        raise PermissionError(f"Failed to send agent action after {retries} attempts.")
    
    def send_key_press_to_game(self, key:str) -> bool:
        return send_key_press(key, self.cmo_window_title)

    def close_popup(self, popup_name:str, 
                    close_popup_action: Callable[[], bool], 
                    close_popup_action_params: dict = {},
                    check_window_exists_fast: bool = True, 
                    max_retries:int=20, 
                    wait_for_popup_init_seconds:float | int=-1) -> Tuple[bool, int]:
        if wait_for_popup_init_seconds >= 0:
            sleep(wait_for_popup_init_seconds)
        
        retries = 0
        if window_exists(window_name=popup_name, fast=check_window_exists_fast):
            close_popup_action(**close_popup_action_params)
            while window_exists(window_name=popup_name, fast=check_window_exists_fast) and retries < max_retries:
                print(f"Steam client was not able to close '{popup_name}' popup. Retrying... (Attempt {retries + 1} of {max_retries})")
                close_popup_action(**close_popup_action_params)
                retries += 1
            if retries >= max_retries and window_exists(window_name=popup_name, fast=check_window_exists_fast):
                raise TimeoutError(f"Steam client was not able to close '{popup_name}' popup.")        
        
        return True, retries
        
    def start_scenario(self) -> bool:
        return self.send_key_press_to_game("{ }")
    
    def pause_scenario(self) -> bool:
        return self.send_key_press_to_game("{ }")
    
    def close_scenario_paused_message(self) -> Tuple[bool, int]:
        close_popup_result, retries = self.close_popup(popup_name=self.scenario_paused_popup_name, 
                                close_popup_action=self.send_key_press_to_game, 
                                close_popup_action_params=dict(key="{ENTER}"),
                                check_window_exists_fast=False,
                                max_retries=50)
        return close_popup_result, retries
    
    def close_scenario_end_message(self) -> bool:
        close_popup_result, _ = self.close_popup(popup_name=self.scenario_end_popup_name, 
                         close_popup_action=self.send_key_press_to_game, 
                         close_popup_action_params=dict(key="{ENTER}"),
                         check_window_exists_fast=False)
        return close_popup_result
    
    def close_player_evaluation(self) -> bool:
        close_popup_result, _ = self.close_popup(popup_name=self.player_evaluation_popup_name, 
                                close_popup_action=send_key_press, 
                                close_popup_action_params=dict(key="{ESC}", window_name=self.player_evaluation_popup_name),
                                check_window_exists_fast=False) 
        return close_popup_result   
    
    def close_scenario_end_and_player_eval_messages(self) -> bool:
        while not window_exists(window_name=self.scenario_end_popup_name, fast=True): ...

        wait_for_completion_seconds = 3
        close_scenario_end_messages_retries = 0
        max_retries = 10

        while True:
            try:
                self.close_scenario_end_message()
            except TimeoutError:
                print("Timed out trying to close 'Scenario End' popup. Moving on to close 'Incoming message' popup.")

            if window_exists(self.scenario_paused_popup_name, fast=False):
                try:
                    self.close_scenario_paused_message()
                    self.pause_scenario() # weird bug where if we have to close more than one "Incoming message" popup the game will resume, so we need to pause it
                except TimeoutError:
                    print("Timed out trying to close 'Incoming message' popup. Moving on to close 'Player Evaluation' popup.")   

            try:
                self.close_player_evaluation() 
            except TimeoutError:
                print("Timed out trying to close 'Player Evaluation' popup. Retrying entire sequence of closing actions.")
            
            print(f"Waiting {wait_for_completion_seconds} seconds to see if there are still any popups...")
            sleep(wait_for_completion_seconds)
            if window_exists(window_name=self.scenario_end_popup_name, fast=False) or window_exists(window_name=self.scenario_paused_popup_name, fast=False) or window_exists(window_name=self.player_evaluation_popup_name, fast=False):
                close_scenario_end_messages_retries += 1
                if close_scenario_end_messages_retries > max_retries:
                    raise TimeoutError("Timed out trying to close 'Scenario End', 'Incoming message', and 'Player Evaluation' popups.")
                else:
                    print(f"Retrying to close 'Scenario End', 'Incoming message', and 'Player Evaluation' popups. (Attempt {close_scenario_end_messages_retries + 1} of {max_retries})")
            else:
                print("No more scenario end popups!")
                break

        return True
    
    def restart_scenario(self) -> bool:
        try:
            restart_process = subprocess.run([os.path.join(config['scripts_path'], 'restartScenario.bat'), self.cmo_window_title])
            
            popup_name = "Side selection and briefing"
            print(f"Waiting for '{popup_name}' popup to show.")
            retries = 0
            max_retries = 100
            while not window_exists(window_name=popup_name, fast=False):
                retries += 1
                if retries > max_retries: raise TimeoutError(f"Waited too long for '{popup_name} to appear but it did not.")
            print("Entering scenario...")

            close_popup_result, _ = self.close_popup(popup_name=popup_name, 
                                    close_popup_action=self.click_enter_scenario, 
                                    check_window_exists_fast=False,
                                    max_retries=self.enter_scenario_max_retries)
            return close_popup_result   
        except FileNotFoundError:
            raise FileNotFoundError("Cannot find 'restartScenario.bat' script.")
        
    def click_enter_scenario(self) -> bool:
        try:
            click_enter_scenario_process = subprocess.run(['PowerShell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(config['scripts_path'], 'MoveMouseEnterScenario.ps1')])
            return True
        except FileNotFoundError:
            raise FileNotFoundError("Cannot find 'MoveMouseEnterScenario.ps1' script.")
