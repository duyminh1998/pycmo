# Author: Minh Hua
# Date: 08/16/2021
# Purpose: Protocol library to communicate with a Command server.

# imports
import socket
import subprocess
from pycmo.configs import config

# open config
config = config.get_config()

class Server():
    def __init__(self, scenario: str):
        """Wrapper for an instance of CommandCLI running the specified scenario"""
        self.scenario = scenario # the path to the scenario (.scen) file to start the game with

    def start_game(self):
        try:
            prog_path = config['command_path']
            command = "CommandCLI.exe -mode I -scenfile \"{}\" -outputfolder \"{}\"".format(self.scenario, config['command_cli_output_path'])
            subprocess.call(command, shell=True, cwd = prog_path)
        except:
            print("ERROR: Failed to start game server.")

    def restart(self):
        self.start_game()

    def end_game(self):
        pass

class Client():
    def __init__(self):
        """Wrapper for a client that can send commands to Command Modern Operations via a TCP/IP port."""
        self.host = "localhost"
        self.port = 7777
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def connect(self):
        """Connect to the game."""
        try:
            self.s.connect((self.host, self.port))
        except OSError:
            print("ERROR: No active instance of Command to connect to. Aborting.")
            raise

    def send(self, data: str):
        """Send a Lua command to the game."""
        try:
            self.s.sendall(data.encode(encoding='UTF-8'))
            data = self.s.recv(1024)
            received = str(data, "UTF-8")
        except OSError:
            print("ERROR: failed to send data to CMO server.")
            raise

    def restart(self):
        """Restart client connection to the game."""
        self.s.connect((self.host, self.port))

    def end_connection(self):
        """End client connection to the game."""
        try:
            self.s.close()
        except:
            print("ERROR: failed to close client connection.")