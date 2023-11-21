# Author: Minh Hua
# Date: 08/16/2021
# Last Update: 06/16/2022
# Purpose: Protocol library to communicate with a Command server.

# imports
import socket
import subprocess
import os

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
                 restart_duration:int=10,
                 enter_scenario_max_retries:int=10) -> None:
        self.scenario_name = scenario_name
        self.agent_action_filename = agent_action_filename
        self.cmo_window_title = f"{scenario_name} - {command_version}"
        self.restart_duration = restart_duration
        self.enter_scenario_max_retries = enter_scenario_max_retries

    def connect(self, command_process_name:str="Command.exe") -> bool:
        return process_exists(command_process_name)

    def send(self, data:str) -> bool:
        try:
            with open(self.agent_action_filename, 'w') as f:
                f.write(data)
            return True
        except (PermissionError, FileNotFoundError):
            return False
    
    def start_scenario(self) -> bool:
        return self.send_key_press("{ }")
    
    def pause_scenario(self) -> bool:
        return self.send_key_press("{ }")
    
    def close_scenario_message(self) -> bool:
        return self.send_key_press("{ENTER}")
    
    def close_scenario_end_message(self) -> bool:
        try:
            os.chdir(config['scripts_path'])
            close_scenario_end_message_process = subprocess.run(['closeScenarioEndMessage.bat'])
            return True
        except FileNotFoundError:
            raise FileNotFoundError("Cannot find 'closeScenarioEndMessage.bat' script.")
            
    def send_key_press(self, key:str) -> bool:
        return send_key_press(key, self.cmo_window_title)
        
    def restart_scenario(self) -> bool:
        try:
            enter_scenario_window_name = "Side selection and briefing"
            os.chdir(config['scripts_path'])
            restart_process = subprocess.run(['restartScenario.bat', self.cmo_window_title, str(int(self.restart_duration / 2) * 1000)])
            # per issue #26, need to check here if the "Side selection and briefing" window is active, and if yes, call self.click_enter_scenario() again
            self.click_enter_scenario()
            retries = 0
            while window_exists(enter_scenario_window_name) and retries < self.enter_scenario_max_retries:
                print(f"Steam client was not able to enter scenario. Retrying... (Attempt {retries} of {self.enter_scenario_max_retries})")
                self.click_enter_scenario()
                retries += 1
            if window_exists(enter_scenario_window_name):
                raise ValueError("Steam client was not able to enter scenario properly. Please check protocol.py or the 'MoveMouseEnterScenario.ps1' script.")
            
            return True
        except FileNotFoundError:
            raise FileNotFoundError("Cannot find 'restartScenario.bat' script.")
        
    def click_enter_scenario(self) -> bool:
        try:
            os.chdir(config['scripts_path'])
            click_enter_scenario_process = subprocess.run(['PowerShell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', 'MoveMouseEnterScenario.ps1'])
            return True
        except FileNotFoundError:
            raise FileNotFoundError("Cannot find 'MoveMouseEnterScenario.ps1' script.")

    def close_popup(self, popup_type: str, window_name: str, closing_script_path: str, max_retries: int) -> bool:
        ...
        