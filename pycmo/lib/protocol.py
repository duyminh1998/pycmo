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
import logging
import win32com.client

from pycmo.configs.config import get_config
from pycmo.lib.tools import process_exists, window_exists

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
        self.send_max_retries = 100
        self.close_scenario_paused_max_retries = 50
        self.close_scenario_end_messages_max_retries = 10
        self.wait_for_side_selection_max_retries = 20

        self.start_scenario_send_key_delay = 0.05
        self.pause_scenario_send_key_delay = 0.1
        self.close_scenario_paused_send_key_delay = 0.1
        self.close_scenario_end_send_key_delay = 0.1
        self.close_player_evaluation_send_key_delay = 0.1
        
        self.scenario_paused_popup_name = "Incoming message"
        self.scenario_end_popup_name = "Scenario End"
        self.player_evaluation_popup_name = "Player Evaluation"

        self.shell = win32com.client.Dispatch("WScript.Shell") 

    def connect(self, command_process_name:str="Command.exe") -> bool:
        return process_exists(command_process_name)

    def send(self, data:str) -> bool:
        retries = 0
        while retries < self.send_max_retries:
            try:
                with open(self.agent_action_filename, 'w') as f:
                    f.write(data)
                return True
            except PermissionError:
                logging.info(f"Failed to send agent action. Retrying... (Attempt {retries + 1} of {self.send_max_retries})")
                retries += 1
            except FileNotFoundError:
                raise FileNotFoundError(f"Unable to find {self.agent_action_filename} to write agent action to.")
        raise PermissionError(f"Failed to send agent action after {retries} attempts.")
    
    def send_key_press(self, key:str, window_name:str, delay:float=None) -> bool:
        if delay: sleep(delay)
        self.shell.AppActivate(window_name)
        self.shell.SendKeys(key)
        return True

    def close_popup(self, popup_name:str, 
                    close_popup_action: Callable[[], bool], 
                    close_popup_action_params: dict = {}, 
                    max_retries:int=20,
                    delay_check_window_exists:float=None) -> Tuple[bool, int]:
        retries = 0
        if window_exists(window_name=popup_name, delay=delay_check_window_exists):
            close_popup_action(**close_popup_action_params)
            while window_exists(window_name=popup_name, delay=delay_check_window_exists) and retries < max_retries:
                logging.info(f"Steam client was not able to close '{popup_name}' popup. Retrying... (Attempt {retries + 1} of {max_retries})")
                close_popup_action(**close_popup_action_params)
                retries += 1
            if retries >= max_retries and window_exists(window_name=popup_name, delay=delay_check_window_exists):
                raise TimeoutError(f"Steam client was not able to close '{popup_name}' popup.")        
        
        return True, retries
        
    def start_scenario(self) -> bool:
        return self.send_key_press(key="{ }", window_name=self.cmo_window_title, delay=self.start_scenario_send_key_delay)
    
    def pause_scenario(self) -> bool:
        return self.send_key_press(key="{ }", window_name=self.cmo_window_title, delay=self.pause_scenario_send_key_delay)
    
    def close_scenario_paused_message(self) -> Tuple[bool, int]:
        try:
            close_popup_result, retries = self.close_popup(popup_name=self.scenario_paused_popup_name, 
                                    close_popup_action=self.send_key_press, 
                                    close_popup_action_params=dict(key="{ENTER}", window_name=self.cmo_window_title, delay=self.close_scenario_paused_send_key_delay),
                                    max_retries=self.close_scenario_paused_max_retries,
                                    delay_check_window_exists=0.1)
            return close_popup_result, retries
        except TimeoutError:
            return False, self.close_scenario_paused_max_retries
    
    def close_scenario_end_message(self) -> bool:
        try:
            close_popup_result, _ = self.close_popup(popup_name=self.scenario_end_popup_name, 
                            close_popup_action=self.send_key_press, 
                            close_popup_action_params=dict(key="{ENTER}", window_name=self.cmo_window_title, delay=self.close_scenario_end_send_key_delay),
                            delay_check_window_exists=1)
            return close_popup_result
        except TimeoutError:
            return False
    
    def close_player_evaluation(self) -> bool:
        try:
            close_popup_result, _ = self.close_popup(popup_name=self.player_evaluation_popup_name, 
                                    close_popup_action=self.send_key_press, 
                                    close_popup_action_params=dict(key="{ESC}", window_name=self.player_evaluation_popup_name, delay=self.close_player_evaluation_send_key_delay),
                                    delay_check_window_exists=1) 
            return close_popup_result   
        except TimeoutError:
            return False
    
    def close_scenario_end_and_player_eval_messages(self) -> bool:
        wait_for_completion_seconds = 3
        retries = 0
        delay_check_window_exists = 1

        while not window_exists(window_name=self.scenario_end_popup_name, delay=0.1): ...

        while True:
            if not self.close_scenario_end_message():
                logging.info(f"Timed out trying to close '{self.scenario_end_popup_name}' popup. Moving on to close '{self.scenario_paused_popup_name}' popup.")

            if window_exists(self.scenario_paused_popup_name, delay=delay_check_window_exists):
                if not self.close_scenario_paused_message():
                    logging.info(f"Timed out trying to close '{self.scenario_paused_popup_name}' popup. Moving on to close '{self.player_evaluation_popup_name}' popup.")
                else:
                    self.pause_scenario() # weird bug where if we have to close more than one "Incoming message" popup the game will resume, so we need to pause it

            if not self.close_player_evaluation():
                logging.info(f"Timed out trying to close '{self.player_evaluation_popup_name}' popup. Retrying entire sequence of closing actions.")
            
            logging.info(f"Waiting {wait_for_completion_seconds} seconds to see if there are still any popups...")
            sleep(wait_for_completion_seconds)
            if window_exists(window_name=self.scenario_end_popup_name, delay=delay_check_window_exists) or window_exists(window_name=self.scenario_paused_popup_name, delay=delay_check_window_exists) or window_exists(window_name=self.player_evaluation_popup_name, delay=delay_check_window_exists):
                retries += 1
                if retries > self.close_scenario_end_messages_max_retries:
                    raise TimeoutError(f"Timed out trying to close '{self.scenario_end_popup_name}', '{self.scenario_paused_popup_name}', and '{self.player_evaluation_popup_name}' popups.")
                logging.info(f"Re-attempting to close '{self.scenario_end_popup_name}', '{self.scenario_paused_popup_name}', and '{self.player_evaluation_popup_name}' popups... (Attempt {retries + 1} of {self.close_scenario_end_messages_max_retries})")
            else:
                logging.info("No more scenario end popups!")
                break

        return True
    
    def restart_scenario(self) -> bool:
        try:
            self.shell.AppActivate(self.cmo_window_title)
            sleep(1)
            self.shell.SendKeys("%f")
            sleep(1)
            self.shell.SendKeys("{DOWN}")
            sleep(0.5)
            self.shell.SendKeys("{DOWN}")
            sleep(0.5)
            self.shell.SendKeys("{DOWN}") 
            sleep(1)
            self.shell.SendKeys("{RIGHT}") 
            sleep(1)
            self.shell.SendKeys("{ENTER}") 
            
            popup_name = "Side selection and briefing"
            logging.info(f"Waiting for '{popup_name}' popup to show.")
            retries = 0
            while not window_exists(window_name=popup_name, delay=0.1):
                retries += 1
                if retries > self.wait_for_side_selection_max_retries: raise TimeoutError(f"Waited too long for '{popup_name}' to appear but it did not.")
            logging.info("Entering scenario...")

            close_popup_result, _ = self.close_popup(popup_name=popup_name, 
                                    close_popup_action=self.click_enter_scenario, 
                                    max_retries=self.enter_scenario_max_retries,
                                    delay_check_window_exists=1)
            return close_popup_result   
        except FileNotFoundError:
            raise FileNotFoundError("Cannot find 'restartScenario.bat' script.")
        
    def click_enter_scenario(self) -> bool:
        try:
            _ = subprocess.run(['PowerShell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(config['scripts_path'], 'MoveMouseEnterScenario.ps1')])
            return True
        except FileNotFoundError:
            raise FileNotFoundError("Cannot find 'MoveMouseEnterScenario.ps1' script.")
