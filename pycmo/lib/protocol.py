"""Protocol library to communicate with a Command server."""

import socket
import subprocess
import json
import time
import os

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
        self.s.connect((self.host, self.port))

    def get_raw_data(self, destination):
        data = "--script \nfile = io.open('{}', 'w') \n".format(destination)
        data += "io.output(file) \ntheXML = ScenEdit_ExportScenarioToXML()\nio.write(theXML) \nio.close(file)"
        self.send_action(data)

    def send_action(self, data):
        self.s.sendall(data.encode(encoding='UTF-8'))
        data = self.s.recv(1024)
        received = str(data, "UTF-8")
        print(received)

    def step(self, h, m, s):
        self.send_action("VP_RunForTimeAndHalt({Time='" + str(h) + ":" + str(m) + ":" + str(s) + "'})")

    def step_and_get_obs(self, h, m, s, destination, cur_time, step_id):
        self.send_action("\nVP_RunForTimeAndHalt({Time='" + str(h) + ":" + str(m) + ":" + str(s) + "'})")
        paused = False
        dur_in_secs = (int(h) * 3600) + (int(m) * 60) + int(s)
        while not paused:
            data = "--script \nlocal now = ScenEdit_CurrentTime() \nlocal elapsed = now - {} \nif elapsed >= {} then \nfile = io.open('{}' .. '\\\\steps\\\\' .. {} .. '.xml', 'w') \nio.output(file) \ntheXML = ScenEdit_ExportScenarioToXML()\nio.write(theXML) \nio.close(file) \nend".format(cur_time, dur_in_secs, destination, step_id)            
            self.send_action(data)
            path = str(step_id) + '.xml'
            if path in os.listdir(os.path.join(destination, "steps")):
                paused = True
                return
            time.sleep(0.1)

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

if __name__ == "__main__":
    blue = Server("C:\\Program Files (x86)\\Command Professional Edition 2\\Scenarios\\Standalone Scenarios\\Battle of Chumonchin Chan, 1950.scen")
    blue.start_game()