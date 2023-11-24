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
from dataclasses import dataclass

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
        
@dataclass
class SteamClientProps:
    scenario_name: str
    agent_action_filename : str = "agent_action.lua"
    command_version : str = config["command_mo_version"]

    send_key_delay_start_scenario : float = 0.1
    send_key_delay_pause_scenario : float = 0.1
    send_key_delay_close_scenario_paused_popup : float = 0.1
    send_key_delay_close_scenario_end_popup : float = 0.5
    send_key_delay_close_player_evaluation_popup : float = 0.5

    check_window_delay_scenario_paused_popup : float = 0.1
    check_window_delay_scenario_end_popup : float = 1
    check_window_delay_player_evaluation_popup : float = 1
    check_window_delay_side_selection_popup : float = 1

    max_retries_enter_scenario : int = 20
    max_retries_send_action : int = 100
    max_retries_close_scenario_paused_popup : int = 50
    max_retries_close_scenario_end_popup : int = 20
    max_retries_wait_for_side_selection_popup : int = 20

    wait_for_close_scenario_end_messages_completion_seconds : int = 2    

class SteamClient():
    """The Client connects to the Steam edition of the game and sends actions to the game."""
    def __init__(self, props:SteamClientProps) -> None:
        self.props = props

        self.cmo_window_title = f"{self.props.scenario_name} - {self.props.command_version}"
        self.scenario_paused_popup_name = "Incoming message"
        self.scenario_end_popup_name = "Scenario End"
        self.player_evaluation_popup_name = "Player Evaluation"
        self.side_selection_popup_name = "Side selection and briefing"

        self.shell = win32com.client.Dispatch("WScript.Shell") 

    def connect(self, command_process_name:str="Command.exe") -> bool:
        return process_exists(command_process_name)

    def send(self, data:str) -> bool:
        retries = 0
        while retries < self.props.max_retries_send_action:
            try:
                with open(self.props.agent_action_filename, 'w') as f:
                    f.write(data)
                return True
            except PermissionError:
                logging.debug(f"Failed to send agent action. Retrying... (Attempt {retries + 1} of {self.props.max_retries_send_action})")
                retries += 1
            except FileNotFoundError:
                raise FileNotFoundError(f"Unable to find {self.props.agent_action_filename} to write agent action to.")
        raise PermissionError(f"Failed to send agent action after {retries} attempts.")
    
    def send_key_press(self, key:str, window_name:str, delay:float=None) -> bool:
        if delay: 
            logging.debug(f"Sleeping for {delay} seconds before sending {key} key to {window_name}.")
            sleep(delay)
        self.shell.AppActivate(window_name)
        self.shell.SendKeys(key)
        return True
    
    def window_exists(self, window_name:str, delay:float=None) -> bool:
        if window_name == self.scenario_paused_popup_name:
            return window_exists(window_name=window_name, delay=delay if delay else self.props.check_window_delay_scenario_paused_popup)
        elif window_name == self.scenario_end_popup_name:
            return window_exists(window_name=window_name, delay=delay if delay else self.props.check_window_delay_scenario_end_popup)
        elif window_name == self.player_evaluation_popup_name:
            return window_exists(window_name=window_name, delay=delay if delay else self.props.check_window_delay_player_evaluation_popup)
        elif window_name == self.side_selection_popup_name:
            return window_exists(window_name=window_name, delay=delay if delay else self.props.check_window_delay_side_selection_popup)
        else:
            raise ValueError(f"window_name must be one of {', '.join([self.scenario_paused_popup_name, self.scenario_end_popup_name, self.player_evaluation_popup_name, self.side_selection_popup_name])}.")

    def close_popup(self, popup_name:str, 
                    close_popup_action: Callable[[], bool], 
                    close_popup_action_params: dict = {}, 
                    max_retries:int=20) -> Tuple[bool, int]:
        retries = 0
        if self.window_exists(window_name=popup_name):
            close_popup_action(**close_popup_action_params)
            while self.window_exists(window_name=popup_name) and retries < max_retries:
                logging.debug(f"Steam client was not able to close '{popup_name}' popup. Retrying... (Attempt {retries + 1} of {max_retries})")
                close_popup_action(**close_popup_action_params)
                retries += 1
            if retries >= max_retries and self.window_exists(window_name=popup_name):
                raise TimeoutError(f"Steam client was not able to close '{popup_name}' popup.")        
        
        return True, retries
        
    def start_scenario(self) -> bool:
        return self.send_key_press(key="{ }", window_name=self.cmo_window_title, delay=self.props.send_key_delay_start_scenario)
    
    def pause_scenario(self) -> bool:
        return self.send_key_press(key="{ }", window_name=self.cmo_window_title, delay=self.props.send_key_delay_pause_scenario)
    
    def close_scenario_paused_message(self) -> bool:
        try:
            close_popup_result, _ = self.close_popup(popup_name=self.scenario_paused_popup_name, 
                                    close_popup_action=self.send_key_press, 
                                    close_popup_action_params=dict(key="{ENTER}", window_name=self.cmo_window_title, delay=self.props.send_key_delay_close_scenario_paused_popup),
                                    max_retries=self.props.max_retries_close_scenario_paused_popup)
            return close_popup_result
        except TimeoutError:
            logging.debug(f"Timed out trying to close '{self.scenario_paused_popup_name}' popup.")
            return False
    
    def close_scenario_end_message(self) -> bool:
        try:
            close_popup_result, _ = self.close_popup(popup_name=self.scenario_end_popup_name, 
                            close_popup_action=self.send_key_press, 
                            close_popup_action_params=dict(key="{ENTER}", window_name=self.scenario_end_popup_name, delay=self.props.send_key_delay_close_scenario_end_popup))
            return close_popup_result
        except TimeoutError:
            logging.debug(f"Timed out trying to close '{self.scenario_end_popup_name}' popup.")
            return False
    
    def close_player_evaluation(self) -> bool:
        try:
            close_popup_result, _ = self.close_popup(popup_name=self.player_evaluation_popup_name, 
                                    close_popup_action=self.send_key_press, 
                                    close_popup_action_params=dict(key="{ESC}", window_name=self.player_evaluation_popup_name, delay=self.props.send_key_delay_close_player_evaluation_popup)) 
            return close_popup_result   
        except TimeoutError:
            logging.debug(f"Timed out trying to close '{self.player_evaluation_popup_name}' popup.")
            return False
    
    def close_scenario_end_and_player_eval_messages(self) -> bool:
        retries = 0

        while not self.window_exists(window_name=self.scenario_end_popup_name): ...
        
        logging.info(f"Attempting to close '{self.scenario_end_popup_name}', '{self.scenario_paused_popup_name}', and '{self.player_evaluation_popup_name}' popups...")
        while True:
            self.close_scenario_end_message()

            if self.window_exists(self.scenario_paused_popup_name):
                if self.close_scenario_paused_message(): 
                    self.pause_scenario() # weird bug where if we have to close more than one "Incoming message" popup the game will resume, so we need to pause it

            self.close_player_evaluation()
            
            logging.info(f"Waiting {self.props.wait_for_close_scenario_end_messages_completion_seconds} seconds to see if there are still any popups...")
            sleep(self.props.wait_for_close_scenario_end_messages_completion_seconds)
            if self.window_exists(window_name=self.scenario_end_popup_name) or \
                self.window_exists(window_name=self.scenario_paused_popup_name) or \
                    self.window_exists(window_name=self.player_evaluation_popup_name):
                retries += 1
                if retries >= self.props.max_retries_close_scenario_end_popup:
                    raise TimeoutError(f"Timed out trying to close '{self.scenario_end_popup_name}', '{self.scenario_paused_popup_name}', and '{self.player_evaluation_popup_name}' popups.")
                logging.debug(f"Re-attempting to close '{self.scenario_end_popup_name}', '{self.scenario_paused_popup_name}', and '{self.player_evaluation_popup_name}' popups... (Attempt {retries + 1} of {self.props.max_retries_close_scenario_end_popup})")
            else:
                logging.info("No more scenario end popups.")
                break

        return True
    
    def restart_scenario(self) -> bool:
        logging.info("Restarting scenario...")
        self.shell.AppActivate(self.cmo_window_title)
        sleep(1)
        self.shell.SendKeys("%f")
        sleep(1)
        self.shell.SendKeys("{DOWN}")
        sleep(0.5)
        self.shell.SendKeys("{DOWN}")
        sleep(0.5)
        self.shell.SendKeys("{DOWN}") 
        sleep(0.5)
        self.shell.SendKeys("{RIGHT}") 
        sleep(1)
        self.shell.SendKeys("{ENTER}") 

        logging.info(f"Waiting for '{self.side_selection_popup_name}' popup to show.")
        retries = 0
        while not self.window_exists(window_name=self.side_selection_popup_name):
            retries += 1
            if retries >= self.props.max_retries_wait_for_side_selection_popup: raise TimeoutError(f"Waited too long for '{self.side_selection_popup_name}' to appear but it did not.")
        
        logging.info("Entering scenario...")
        close_popup_result, _ = self.close_popup(popup_name=self.side_selection_popup_name, 
                                close_popup_action=self.click_enter_scenario, 
                                max_retries=self.props.max_retries_enter_scenario)
        return close_popup_result   
        
    def click_enter_scenario(self) -> bool:
        try:
            enter_scenario_script_name = 'MoveMouseEnterScenario.ps1'
            _ = subprocess.run(['PowerShell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', os.path.join(config['scripts_path'], enter_scenario_script_name)])
            return True
        except FileNotFoundError:
            raise FileNotFoundError(f"Cannot find {enter_scenario_script_name} script.")
