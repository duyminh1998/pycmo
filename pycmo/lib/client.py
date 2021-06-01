"""Protocol library to communicate with a Command server."""

import os
import socket

class Client():
    def __init__(self, side=None):
        self.host = "localhost"
        self.port = 7777
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((self.host, self.port))

    def get_raw_data(self, destination):
        data = "file = io.open({}, \"w\") \n".format(destination)
        data += "io.output(file) \n theXML = ScenEdit_ExportScenarioToXML() \n io.write(theXML) \n io.close(file)"
        self.send_action(data)

    def send_action(self, data):
        self.s.sendall(data.encode(encoding='UTF-8'))
        data = self.s.recv(1024)
        received = str(data, "utf-8")
        print(received)

    def step(self):
        pass

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
    blue = Client("United Nations")
    blue.send_action(data = "--script \n VP_RunSimulation() \n local unit = VP_GetUnit({side = 'United Nations', name = 'HMS Black Swan'}) \n file = io.open('C:\\\\Users\\\\Public\\\\Desktop\\\\test.txt', 'w') \n io.output(file) \n io.write(unit.name) \n io.close(file) \n VP_PauseSimulation()")