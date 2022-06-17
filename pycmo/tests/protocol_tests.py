# Author: Minh Hua
# Date: 06/16/2022
# Last Update: 06/16/2022
# Purpose: Tests for protocol.py.

# imports
from pycmo.lib import protocol

# test Client class
# init
client = protocol.Client()

# connection
res = client.connect()
print(res)

# send data
data = "--script \n VP_RunSimulation()"
rec = client.send(data)
print(rec)

# restart
res = client.restart()
print(res)

# end connection
res = client.end_connection()
print(res)