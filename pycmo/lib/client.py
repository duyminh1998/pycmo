import socket

host = "localhost"
port = 7777                   # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
data = "--script \n VP_RunSimulation() \n local unit = VP_GetUnit({side = 'United Nations', name = 'HMS Black Swan'}) \n file = io.open('C:\\\\Users\\\\Public\\\\Desktop\\\\test.txt', 'w') \n io.output(file) \n io.write(unit.name) \n io.close(file) \n VP_PauseSimulation()"
s.sendall(data.encode(encoding='UTF-8'))
data = s.recv(1024)
received = str(data, "utf-8")
s.close()
print(received)