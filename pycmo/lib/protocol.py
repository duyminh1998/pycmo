"""Protocol library to communicate with a Command server."""

import socket
import subprocess
import json

f = open("C:\\Users\\AFSOC A8XW ORSA\\Documents\\Python Proj\\AI\\pycmo\\pycmo\\configs\\config.json")
config = json.load(f)

class Server():
    def __init__(self, scenario):
        self.scenario = scenario

    def start_game(self):
        try:
            prog_path = config['command_path']
            command = "CommandCLI.exe -mode I -scenfile \"{}\" -outputfolder \"C:\\ProgramData\\Command Professional Edition 2\\Analysis_Int\"".format(self.scenario)
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

class Client():
    def __init__(self, side=None):
        self.host = "localhost"
        self.port = 7777
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
    def connect(self):
        try:
            self.s.connect((self.host, self.port))
        except:
            print("No active instance of Command to connect to. Aborting.")
            return

    def send_action(self, data):
        self.s.sendall(data.encode(encoding='UTF-8'))
        data = self.s.recv(1024)
        received = str(data, "UTF-8")
        print(received)

    def restart(self):
        try:
            self.s.connect((self.host, self.port))
        except:
            pass

    def end_game(self):
        try:
            self.s.close()
        except:
            pass