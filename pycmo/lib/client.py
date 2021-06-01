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
        data = "--script \nfile = io.open('{}', 'w') \n".format(destination)
        data += "io.output(file) \ntheXML = ScenEdit_ExportScenarioToXML()\nio.write(theXML) \nio.close(file)"
        self.send_action(data)

    def send_action(self, data):
        self.s.sendall(data.encode(encoding='UTF-8'))
        data = self.s.recv(1024)
        received = str(data, "utf-8")
        print(received)

    def step(self, h, m, s):
        self.send_action("--script VP_RunForTimeAndHalt({Time='" + str(h) + ":" + str(m) + ":" + str(s) + "'})")

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
    for i in range(5):
        blue.get_raw_data("C:\\\\Users\\\\Public\\\\Desktop\\\\scenario" + str(i) + ".xml")
        blue.step("01", "00", "00")