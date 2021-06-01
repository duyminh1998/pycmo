"""Protocol library to communicate with a Command server."""

import os
import socket

class Client():
    def __init__(self, side):
        self.host = "localhost"
        self.port = 7777                   # The same port as used by the server
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def get_observation(self):
        pass

    def send_action(self, data):
        self.s.connect((self.host, self.port))
        self.s.sendall(data.encode(encoding='UTF-8'))
        data = self.s.recv(1024)
        received = str(data, "utf-8")
        self.s.close()
        print(received)

    def step(self):
        pass

    def restart(self):
        pass

    def end_game(self):
        pass

blue = Client("United Nations")
blue.send_action(data = "--script \n VP_RunSimulation() \n local unit = VP_GetUnit({side = 'United Nations', name = 'HMS Black Swan'}) \n file = io.open('C:\\\\Users\\\\Public\\\\Desktop\\\\test.txt', 'w') \n io.output(file) \n io.write(unit.name) \n io.close(file) \n VP_PauseSimulation()")