"""Protocol library to host a Command headless server."""

import os
import subprocess

class Server():
    def __init__(self, scenario):
        self.scenario = scenario

    def start_game(self):
        try:
            prog_path = "C:\\Program Files (x86)\\Command Professional Edition"
            command = "CommandCLI.exe -mode I -scenfile \"{}\"".format(self.scenario)
            print(command)
            subprocess.call(command, shell=True, cwd = prog_path)
        except:
            pass

    def restart(self):
        try:
            self.start_game()
        except:
            pass

    def end_game(self):
        pass

if __name__ == "__main__":
    blue = Server("C:\\Program Files (x86)\\Command Professional Edition\\Scenarios\\Standalone Scenarios\\Battle of Chumonchin Chan, 1950.scen")
    blue.start_game()