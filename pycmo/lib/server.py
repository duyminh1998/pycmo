"""Protocol library to communicate with Command."""

import socket
import os
import subprocess

class CommandProtocol():
    def __init__(self, side):
        self.side = side

    def start_game(self, scenario):
        try:
            prog_path = "C:\\Program Files (x86)\\Command Professional Edition"
            scen_path = scenario
            command = "CommandCLI.exe -mode I -scenfile \"{}\"".format(scen_path)
            print(command)
            subprocess.call(command, shell=True, cwd = prog_path)
            
        except:
            pass

    def get_observation(self):
        pass

    def send_action(self):
        pass

    def step(self):
        pass

    def restart(self):
        pass

    def end_game(self):
        pass

blue = CommandProtocol("United Nations")
blue.start_game("C:\\Program Files (x86)\\Command Professional Edition\\Scenarios\\Standalone Scenarios\\Battle of Chumonchin Chan, 1950.scen")